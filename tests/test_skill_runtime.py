import json
import pathlib
import shutil
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ROUTER = ROOT / "scripts" / "skill_router.py"
SESSIONS = ROOT / "scripts" / "session_state.py"


def run_json(script: pathlib.Path, *args: str, check: bool = True):
    result = subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode:
        raise AssertionError(
            f"command failed ({result.returncode}): {result.stderr or result.stdout}"
        )
    payload = json.loads(result.stdout) if result.stdout.strip() else None
    return result, payload


class SkillRouterTests(unittest.TestCase):
    def route(self, task: str, profile: str = "balanced"):
        _, payload = run_json(
            ROUTER, "--task", task, "--profile", profile, "--format", "json"
        )
        return payload

    def test_explicit_optional_skill_name_wins_without_loading_unrelated_skills(self):
        plan = self.route("Use the humanizer skill on this product announcement")
        names = [item["name"] for item in plan["required_skills"]]
        self.assertIn("humanizer", names)
        self.assertNotIn("graphify", names)
        self.assertLessEqual(len(plan["required_skills"]), 5)

    def test_alias_resolves_duplicate_grill_skill_to_one_canonical_skill(self):
        plan = self.route("Please use grill me to stress-test this product plan")
        names = [item["name"] for item in plan["required_skills"]]
        self.assertEqual(names.count("grilling"), 1)
        self.assertNotIn("grill-me", names)

    def test_bug_fix_routes_debugging_and_verification_but_not_every_workflow(self):
        plan = self.route(
            "Fix an intermittent Python session restore bug and add a regression test"
        )
        names = [item["name"] for item in plan["required_skills"]]
        self.assertIn("systematic-debugging", names)
        self.assertIn("verification", names)
        self.assertNotIn("obsidian-cli", names)
        self.assertNotIn("last30days", names)

    def test_local_small_profile_has_a_strict_activation_cap_and_simple_contract(self):
        plan = self.route(
            "Investigate, fix, refactor, review and verify a flaky Python migration",
            profile="local-small",
        )
        self.assertLessEqual(len(plan["required_skills"]), 4)
        self.assertEqual(plan["execution_contract"]["max_steps"], 8)
        self.assertTrue(plan["execution_contract"]["require_verification"])

    def test_equivalent_request_is_serialized_deterministically(self):
        first = self.route("Review this code change for regressions")
        second = self.route("Review this code change for regressions")
        self.assertEqual(first, second)

    def test_ordinary_search_does_not_activate_graphify(self):
        plan = self.route("Find the exact definition of configure_opencode in this repo")
        names = [item["name"] for item in plan["required_skills"]]
        self.assertNotIn("graphify", names)

    def test_hermes_delegation_keeps_transitive_context_dependencies_under_cap(self):
        plan = self.route(
            "Delegate to Hermes with a bounded context pack", profile="local-small"
        )
        names = [item["name"] for item in plan["required_skills"]]
        self.assertEqual(
            set(names),
            {"hermes-delegation", "delegation", "harness-project-access", "context-builder"},
        )
        self.assertLessEqual(len(names), 4)

    def test_only_small_core_is_directly_discoverable(self):
        exposed = sorted(
            p.parent.name
            for p in (ROOT / ".agents" / "skills").glob("*/SKILL.md")
        )
        self.assertEqual(
            exposed,
            ["project-safety", "session-checkpoint", "skill-router", "verification"],
        )
        library = ROOT / ".agents" / "skills" / "catalog"
        self.assertGreaterEqual(len(list(library.glob("*/SKILL.md"))), 39)

    def test_local_sync_exposes_only_core_and_removes_stale_catalog_skills(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "sync_skills.py"), "local"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        exposed = sorted(
            p.parent.name for p in (ROOT / ".claude" / "skills").glob("*/SKILL.md")
        )
        self.assertEqual(
            exposed,
            ["project-safety", "session-checkpoint", "skill-router", "verification"],
        )
        self.assertFalse((ROOT / ".claude" / "skills" / "catalog").exists())


class SessionStateTests(unittest.TestCase):
    session_id = "TEST-SKILL-RUNTIME"

    def setUp(self):
        self.session_dir = ROOT / "tmp" / "local" / "sessions" / self.session_id
        self.fixture = ROOT / "tmp" / "local" / "session-state-fixture.txt"
        self.fixture.parent.mkdir(parents=True, exist_ok=True)
        self.fixture.write_text("v1\n", encoding="utf-8")
        shutil.rmtree(self.session_dir, ignore_errors=True)

    def tearDown(self):
        shutil.rmtree(self.session_dir, ignore_errors=True)
        self.fixture.unlink(missing_ok=True)

    def test_checkpoint_round_trip_and_resume_hash_validation(self):
        _, started = run_json(
            SESSIONS,
            "start",
            "--id",
            self.session_id,
            "--goal",
            "Prove resumable state",
            "--acceptance",
            "resume validates working files",
        )
        self.assertEqual(started["task"]["status"], "planning")

        _, checkpoint = run_json(
            SESSIONS,
            "checkpoint",
            "--id",
            self.session_id,
            "--status",
            "verifying",
            "--done",
            "router implemented",
            "--todo",
            "run tests",
            "--verified",
            "router unit tests passed",
            "--file",
            str(self.fixture.relative_to(ROOT)),
            "--next-action",
            "Run the focused unit test",
            "--steps-used",
            "3",
        )
        self.assertEqual(checkpoint["progress"]["done"], ["router implemented"])
        self.assertEqual(checkpoint["budgets"]["steps_used"], 3)

        result, resumed = run_json(SESSIONS, "resume", "--id", self.session_id)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(resumed["integrity"]["status"], "clean")
        self.assertNotIn("reasoning", json.dumps(resumed).lower())

        self.fixture.write_text("v2\n", encoding="utf-8")
        result, resumed = run_json(
            SESSIONS, "resume", "--id", self.session_id, check=False
        )
        self.assertEqual(result.returncode, 3)
        self.assertEqual(resumed["integrity"]["status"], "drifted")

    def test_checkpoint_rejects_working_files_outside_project(self):
        run_json(
            SESSIONS,
            "start",
            "--id",
            self.session_id,
            "--goal",
            "Reject escaped paths",
        )
        result, payload = run_json(
            SESSIONS,
            "checkpoint",
            "--id",
            self.session_id,
            "--file",
            "/etc/hosts",
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(payload["error"], "path_outside_project")

    def test_checkpoint_rejects_completion_that_skips_verification_and_review(self):
        run_json(
            SESSIONS,
            "start",
            "--id",
            self.session_id,
            "--goal",
            "Enforce the goal state machine",
        )
        result, payload = run_json(
            SESSIONS,
            "checkpoint",
            "--id",
            self.session_id,
            "--status",
            "complete",
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(payload["error"], "invalid_transition")

    def test_no_progress_and_repeated_failure_counters_trigger_escalation(self):
        run_json(
            SESSIONS,
            "start",
            "--id",
            self.session_id,
            "--goal",
            "Stop unproductive loops",
        )
        _, first = run_json(SESSIONS, "checkpoint", "--id", self.session_id)
        self.assertEqual(first["runtime"]["no_progress_windows"], 1)
        self.assertEqual(first["runtime"]["next_decision"], "reflect")
        _, second = run_json(SESSIONS, "checkpoint", "--id", self.session_id)
        self.assertEqual(second["runtime"]["no_progress_windows"], 2)
        self.assertEqual(second["runtime"]["next_decision"], "escalate")

        _, progressed = run_json(
            SESSIONS,
            "checkpoint",
            "--id",
            self.session_id,
            "--done",
            "new evidence collected",
            "--failure-fingerprint",
            "same-test-failure",
        )
        self.assertEqual(progressed["runtime"]["no_progress_windows"], 0)
        _, repeated = run_json(
            SESSIONS,
            "checkpoint",
            "--id",
            self.session_id,
            "--failure-fingerprint",
            "same-test-failure",
        )
        self.assertEqual(repeated["runtime"]["repeated_failure_count"], 2)
        self.assertEqual(repeated["runtime"]["next_decision"], "escalate")

    def test_completion_requires_recorded_verification_and_no_pending_checks(self):
        run_json(
            SESSIONS,
            "start",
            "--id",
            self.session_id,
            "--goal",
            "Require evidence before completion",
        )
        run_json(
            SESSIONS,
            "checkpoint",
            "--id",
            self.session_id,
            "--status",
            "reviewing",
        )
        result, payload = run_json(
            SESSIONS,
            "checkpoint",
            "--id",
            self.session_id,
            "--status",
            "complete",
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(payload["error"], "verification_required")

        _, completed = run_json(
            SESSIONS,
            "checkpoint",
            "--id",
            self.session_id,
            "--status",
            "complete",
            "--verified",
            "focused tests passed",
        )
        self.assertEqual(completed["task"]["status"], "complete")


if __name__ == "__main__":
    unittest.main()
