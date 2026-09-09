#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MCP_ROOT = ROOT / "tools/mcp/project-context-mcp"
sys.path.insert(0, str(MCP_ROOT))


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    print("+", " ".join(cmd))
    return subprocess.run(cmd, cwd=ROOT, check=check)


def ensure_env() -> None:
    env = ROOT / ".env"
    if not env.exists():
        shutil.copy2(ROOT / ".env.example", env)
        print("Created .env from .env.example")
    run([sys.executable, "scripts/bootstrap_env.py"])


def cmd_mcp_install() -> None:
    target = ROOT / "tmp/local/project-context/venv"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        print(f"Creating local MCP virtual environment: {target.relative_to(ROOT)}")
        venv.EnvBuilder(with_pip=True).create(target)
    py = target / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    run([str(py), "-m", "pip", "install", "--disable-pip-version-check", "--retries", "1", "--timeout", "15", "-e", str(MCP_ROOT)])


def cmd_index() -> None:
    from project_context_mcp.core import build_index
    print(json.dumps(build_index(ROOT), indent=2))


def cmd_wiki_validate() -> None:
    from project_context_mcp.core import validate
    result = validate(ROOT)
    print(json.dumps(result, indent=2))
    if not result["ok"]:
        raise SystemExit(1)


def cmd_openspec_check() -> None:
    import re
    path = ROOT / "openspec/schemas/production-sdd/schema.yaml"
    text = path.read_text(encoding="utf-8")
    required = ["proposal", "specs", "design", "context-impact", "tasks"]
    missing = [x for x in required if not re.search(rf"(?m)^\s*- id: {re.escape(x)}\s*$", text)]
    template_dir = path.parent / "templates"
    missing_templates = [f for f in ["proposal.md","spec.md","design.md","context-impact.md","tasks.md"] if not (template_dir/f).exists()]
    if missing or missing_templates:
        print({"missingArtifacts": missing, "missingTemplates": missing_templates})
        raise SystemExit(1)
    print("OpenSpec project schema structure: PASS")
    if shutil.which("openspec"):
        run(["openspec", "schema", "validate", "production-sdd"])
        run(["openspec", "validate", "--all", "--strict"])
    else:
        raise SystemExit(
            "OpenSpec CLI validation: FAIL (install OpenSpec 1.12.0 or newer)"
        )


def configure_openspec() -> None:
    if not shutil.which("openspec"):
        print("OpenSpec telemetry: NOT RUN (openspec executable not installed)")
        return
    run(["openspec", "config", "set", "telemetry.enabled", "false"])


def cmd_client_config() -> None:
    run([sys.executable, "scripts/configure_clients.py"])


def cmd_test() -> None:
    # Run repository test modules in isolated processes. Several tests intentionally
    # mutate generated local state, so module isolation avoids order-dependent state.
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        module = f"tests.{path.stem}"
        run([sys.executable, "-m", "unittest", module, "-v"])
    env = os.environ.copy(); env["PYTHONPATH"] = str(MCP_ROOT)
    print("+ project-context core tests")
    installed_python = ROOT / "tmp/local/project-context/venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    python = str(installed_python) if installed_python.exists() else sys.executable
    subprocess.run([python, "-m", "unittest", "discover", "-s", str(MCP_ROOT / "tests"), "-p", "test_*.py", "-v"], cwd=ROOT, check=True, env=env)


def cmd_check(*, delegated: bool = False) -> None:
    if not delegated:
        run([sys.executable, "scripts/check_config.py"])
    else:
        print("Config/secret validation: SKIPPED (delegated secret-free profile)")
    run([sys.executable, "scripts/session_state.py", "verify"])
    cmd_wiki_validate()
    cmd_openspec_check()
    cmd_test()
    run([sys.executable, "scripts/artifact_manifest.py", "verify"])
    print("Harness core checks: PASS")


def cmd_init(args) -> None:
    ensure_env()
    configure_openspec()
    cmd_index()
    run([sys.executable, "scripts/sync_skills.py", "local"])
    if args.install_mcp:
        cmd_mcp_install()
    cmd_client_config()
    print("Initialization complete. Edit .env only if you want optional integrations, then run: python harness.py check")


def cmd_clean() -> None:
    for p in [ROOT / ".generated", ROOT / ".mcp.json", ROOT / "opencode.json", ROOT / ".codex/config.toml", ROOT / ".claude/settings.local.json"]:
        if p.is_dir(): shutil.rmtree(p, ignore_errors=True)
        elif p.exists(): p.unlink()
    for pattern in [ROOT / ".claude/agents", ROOT / ".opencode/agents"]:
        if pattern.exists():
            for p in pattern.glob("generated-*.md"): p.unlink()
    tool_dir=ROOT/'.opencode/tools'
    if tool_dir.exists():
        for p in list(tool_dir.glob('generated-hermes.*'))+[tool_dir/'hermes.js']:
            if p.exists(): p.unlink()
    shutil.rmtree(ROOT / "tmp/local/project-context", ignore_errors=True)
    print("Generated client/runtime/index state removed; source and .env preserved.")


def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(description="Cross-platform management CLI for harness-layout")
    sub=p.add_subparsers(dest="command", required=True)
    init=sub.add_parser("init", help="create .env, build Wiki index and generate client configs")
    init.add_argument("--install-mcp", action="store_true", help="also create local venv and install project-context MCP dependencies")
    sub.add_parser("check", help="validate config, Wiki, OpenSpec structure and run tests")
    sub.add_parser("check-delegated", help="secret-free repository gate for CI and restricted workers")
    sub.add_parser("test", help="run unit/static tests")
    sub.add_parser("index", help="rebuild local Markdown Wiki SQLite FTS index")
    sub.add_parser("wiki-validate", help="validate Wiki IDs and links")
    sub.add_parser("openspec-check", help="validate local OpenSpec schema and use CLI if installed")
    sub.add_parser("mcp-install", help="install project-context MCP into tmp/local virtualenv")
    sub.add_parser("client-config", help="generate Claude/OpenCode/Codex client configs from .env")
    sub.add_parser("manifest-generate", help="regenerate ARTIFACT_MANIFEST.sha256")
    sub.add_parser("manifest-check", help="verify ARTIFACT_MANIFEST.sha256")
    sub.add_parser("clean", help="remove generated local state without deleting .env")
    return p


def main() -> None:
    p=parser(); args=p.parse_args()
    {
      "init": lambda: cmd_init(args), "check": cmd_check, "test": cmd_test, "index": cmd_index,
      "check-delegated": lambda: cmd_check(delegated=True),
      "wiki-validate": cmd_wiki_validate, "openspec-check": cmd_openspec_check,
      "mcp-install": cmd_mcp_install, "client-config": cmd_client_config, "clean": cmd_clean,
      "manifest-generate": lambda: run([sys.executable, "scripts/artifact_manifest.py", "generate"]),
      "manifest-check": lambda: run([sys.executable, "scripts/artifact_manifest.py", "verify"]),
    }[args.command]()

if __name__ == "__main__": main()
