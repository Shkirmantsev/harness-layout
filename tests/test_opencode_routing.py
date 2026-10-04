import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tests.test_clients_and_skills import load_generator

ROOT = pathlib.Path(__file__).resolve().parents[1]


class OpenCodeRoutingTests(unittest.TestCase):
    def generate(self, root, env):
        gen = load_generator()
        (root / "templates/opencode").mkdir(parents=True, exist_ok=True)
        for name in ("harness.js", "hermes.js"):
            shutil.copyfile(ROOT / "templates/opencode" / name, root / "templates/opencode" / name)
        with patch.object(gen, "ROOT", root), patch.object(gen, "GEN", root / ".generated"):
            gen.configure_opencode(env, {})
        return json.loads((root / "opencode.json").read_text(encoding="utf-8"))

    def test_v1_startup_exposes_router_and_enabled_worker(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            config = self.generate(root, {"LITELLM_ENABLED": "true", "LOCAL_MODEL_1_ENABLED": "true", "LOCAL_MODEL_1_ALIAS": "small"})
            self.assertEqual([".generated/opencode-routing.md"], config["instructions"])
            self.assertEqual("allow", config["permission"]["harness_route"])
            roster = (root / config["instructions"][0]).read_text(encoding="utf-8")
            self.assertIn("generated-small-worker", roster)
            self.assertIn("without waiting for a user mention", roster)
            worker = (root / ".opencode/agents/generated-small-worker.md").read_text(encoding="utf-8")
            header = json.loads(worker.split("---")[1])
            self.assertEqual("subagent", header["mode"])
            self.assertEqual("harness/small", header["model"])
            self.assertIn("small", config["provider"]["harness"]["models"])
            self.assertEqual("deny", header["permission"]["task"])
            self.assertTrue((root / ".opencode/tools/harness.js").is_file())

    def test_regeneration_removes_disabled_workers_and_preserves_personal_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            self.generate(root, {"LITELLM_ENABLED": "true", "LOCAL_MODEL_1_ENABLED": "true"})
            personal = root / ".opencode/agents/reviewer.md"
            personal.write_text("personal agent", encoding="utf-8")
            personal_tool = root / ".opencode/tools/custom.js"
            personal_tool.write_text("personal tool", encoding="utf-8")
            self.generate(root, {"LOCAL_MODEL_1_ENABLED": "true"})
            self.assertEqual([], list((root / ".opencode/agents").glob("generated-*-worker.md")))
            self.assertEqual("personal agent", personal.read_text(encoding="utf-8"))
            self.assertEqual("personal tool", personal_tool.read_text(encoding="utf-8"))
            self.assertIn("Hermes is disabled", (root / ".generated/opencode-routing.md").read_text(encoding="utf-8"))

    def test_v2_uses_native_worker_permissions_and_shell_routing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            self.generate(root, {})
            config = self.generate(root, {"OPENCODE_CONFIG_GENERATION": "v2", "LITELLM_ENABLED": "true", "LOCAL_MODEL_2_ENABLED": "true"})
            self.assertNotIn("permission", config)
            self.assertNotIn("instructions", config)
            worker = next((root / ".opencode/agents").glob("generated-*-worker.md"))
            header = json.loads(worker.read_text(encoding="utf-8").split("---")[1])
            self.assertNotIn("permission", header)
            self.assertEqual("subagent", header["permissions"][0]["action"])
            self.assertFalse((root / ".opencode/tools/harness.js").exists())
            self.assertIn("scripts/skill_router.py", (root / ".generated/opencode-routing.md").read_text(encoding="utf-8"))

    def test_enabled_hermes_roster_names_native_tools_and_approval_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            self.generate(root, {"HERMES_ENABLED": "true", "HERMES_REMOTE_HOST": "localhost"})
            roster = (root / ".generated/opencode-routing.md").read_text(encoding="utf-8")
            for name in ("hermes_delegate", "hermes_status", "hermes_approve"):
                self.assertIn(name, roster)
            self.assertIn("explicit user authorization", roster)
            self.assertEqual([], list((root / ".opencode/agents").glob("generated-hermes*.md")))

    @unittest.skipUnless(shutil.which("node"), "Node is an optional OpenCode dependency")
    def test_router_tool_executes_real_plan_without_shell_evaluating_task(self):
        # Replace only the plugin schema helper, preserving the actual adapter code.
        source = (ROOT / "templates/opencode/harness.js").read_text(encoding="utf-8")
        source = source.replace('import { tool } from "@opencode-ai/plugin"',
                                'const schema = { describe() { return this }, optional() { return this } }; const tool = Object.assign(x => x, {schema: {string: () => schema, enum: () => schema}})')
        (ROOT / "tmp/local").mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "tmp/local") as directory:
            adapter = pathlib.Path(directory) / "routing.mjs"
            adapter.write_text(source, encoding="utf-8")
            runner = pathlib.Path(directory) / "test.mjs"
            marker = pathlib.Path(directory) / "should-not-exist"
            task = f"fix a regression $(touch {marker}) `touch {marker}`"
            runner.write_text('import { route } from "./routing.mjs";\n' +
                              f'const context = {{worktree: {json.dumps(str(ROOT))}}};\n' +
                              f'console.log(await route.execute({{task: {json.dumps(task)}}}, context));\n' +
                              'try { await route.execute({task: ""}, context); process.exit(1) } catch (error) { if (error.message !== "task is required") throw error }\n', encoding="utf-8")
            result = subprocess.run([shutil.which("node"), str(runner)], capture_output=True, text=True, timeout=40)
            self.assertEqual(0, result.returncode, result.stderr)
            plan = json.loads(result.stdout)
            self.assertIn("surgical-patch", [skill["name"] for skill in plan["required_skills"]])
            self.assertFalse(marker.exists())
