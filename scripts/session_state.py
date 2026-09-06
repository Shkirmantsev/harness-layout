#!/usr/bin/env python3
"""Crash-safe, evidence-oriented session checkpoints for the harness."""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
import re
import secrets
import sys
from pathlib import Path

from common import ROOT


SCHEMA_VERSION = "1.0"
STATE_ROOT = ROOT / "tmp" / "local" / "sessions"
RUNTIME_CONFIG = ROOT / ".harness" / "runtime.json"
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,79}$")
STATUSES = {"planning", "executing", "verifying", "reviewing", "blocked", "complete"}
TRANSITIONS = {
    "planning": {"executing", "verifying", "reviewing", "blocked"},
    "executing": {"verifying", "blocked"},
    "verifying": {"executing", "reviewing", "blocked"},
    "reviewing": {"executing", "complete", "blocked"},
    "blocked": {"planning", "executing", "verifying", "reviewing"},
    "complete": set(),
}


class StateError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def default_max_steps() -> int:
    try:
        value = int(
            json.loads(RUNTIME_CONFIG.read_text(encoding="utf-8"))["goal_loop"][
                "max_steps"
            ]
        )
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise StateError("invalid_runtime_config", str(exc)) from exc
    if value < 1:
        raise StateError("invalid_runtime_config", "goal_loop.max_steps must be positive")
    return value


def runtime_limits() -> dict[str, int]:
    try:
        loop = json.loads(RUNTIME_CONFIG.read_text(encoding="utf-8"))["goal_loop"]
        limits = {
            "max_repeated_failure": int(loop["max_repeated_failure"]),
            "max_no_progress_windows": int(loop["max_no_progress_windows"]),
        }
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise StateError("invalid_runtime_config", str(exc)) from exc
    if any(value < 1 for value in limits.values()):
        raise StateError("invalid_runtime_config", "runtime limits must be positive")
    return limits


def progress_fingerprint(payload: dict) -> str:
    evidence = {
        "progress": payload["progress"],
        "decisions": payload["decisions"],
        "verification": payload["verification"],
        "working_set": payload["working_set"],
    }
    encoded = json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def session_id(value: str | None) -> str:
    if value is None:
        value = f"SESSION-{dt.datetime.now(dt.timezone.utc):%Y%m%d-%H%M%S}-{secrets.token_hex(2).upper()}"
    if not ID_PATTERN.fullmatch(value):
        raise StateError("invalid_session_id", "session id must be 3-80 safe characters")
    return value


def directory(identifier: str) -> Path:
    return STATE_ROOT / session_id(identifier)


def state_path(identifier: str) -> Path:
    return directory(identifier) / "state.json"


@contextlib.contextmanager
def locked(identifier: str):
    target = directory(identifier)
    target.mkdir(parents=True, exist_ok=True)
    lock_path = target / "state.lock"
    with lock_path.open("a", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def read(identifier: str) -> dict:
    path = state_path(identifier)
    if not path.exists():
        raise StateError("session_not_found", f"checkpoint does not exist: {identifier}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StateError("invalid_checkpoint", str(exc)) from exc
    if data.get("schema_version") != SCHEMA_VERSION:
        raise StateError("unsupported_schema", "checkpoint schema is not supported")
    return data


def atomic_write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        with temporary.open("wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    finally:
        temporary.unlink(missing_ok=True)


def project_file(raw: str) -> tuple[Path, str]:
    candidate = Path(raw).expanduser()
    resolved = candidate.resolve() if candidate.is_absolute() else (ROOT / candidate).resolve()
    try:
        relative = resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise StateError("path_outside_project", f"working file is outside project: {raw}") from exc
    if not resolved.is_file():
        raise StateError("file_not_found", f"working file does not exist: {relative}")
    digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
    return relative, digest


def start(args: argparse.Namespace) -> dict:
    identifier = session_id(args.id)
    steps_max = args.steps_max if args.steps_max is not None else default_max_steps()
    if steps_max < 1:
        raise StateError("invalid_budget", "steps_max must be positive")
    with locked(identifier):
        path = state_path(identifier)
        if path.exists() and not args.replace:
            raise StateError("session_exists", f"checkpoint already exists: {identifier}")
        timestamp = now()
        payload = {
            "schema_version": SCHEMA_VERSION,
            "session": {
                "id": identifier,
                "project": ROOT.name,
                "created_at": timestamp,
                "updated_at": timestamp,
            },
            "task": {
                "goal": args.goal,
                "acceptance": args.acceptance or [],
                "status": "planning",
            },
            "progress": {"done": [], "todo": [], "blocked": []},
            "decisions": [],
            "verification": {"passed": [], "pending": []},
            "working_set": [],
            "budgets": {"steps_used": 0, "steps_max": steps_max},
            "resume": {"next_action": "", "prerequisites": []},
            "runtime": {
                "no_progress_windows": 0,
                "last_failure_fingerprint": "",
                "repeated_failure_count": 0,
                "next_decision": "continue",
            },
        }
        atomic_write(path, payload)
    return payload


def checkpoint(args: argparse.Namespace) -> dict:
    identifier = session_id(args.id)
    with locked(identifier):
        payload = read(identifier)
        before = progress_fingerprint(payload)
        if args.status and args.status != payload["task"]["status"]:
            current = payload["task"]["status"]
            if args.status not in TRANSITIONS.get(current, set()):
                raise StateError(
                    "invalid_transition", f"cannot transition from {current} to {args.status}"
                )
            payload["task"]["status"] = args.status
        for key in ("done", "todo", "blocked"):
            value = getattr(args, key)
            if value is not None:
                payload["progress"][key] = value
        if args.decision is not None:
            payload["decisions"] = args.decision
        if args.verified is not None:
            payload["verification"]["passed"] = args.verified
        if args.pending_verification is not None:
            payload["verification"]["pending"] = args.pending_verification
        if payload["task"]["status"] == "complete" and (
            not payload["verification"]["passed"]
            or payload["verification"]["pending"]
        ):
            raise StateError(
                "verification_required",
                "completion requires recorded verification and no pending checks",
            )
        if args.file is not None:
            working_set = []
            for raw in args.file:
                relative, digest = project_file(raw)
                working_set.append({"path": relative.as_posix(), "sha256": digest})
            payload["working_set"] = sorted(working_set, key=lambda item: item["path"])
        if args.steps_used is not None:
            if args.steps_used < payload["budgets"]["steps_used"]:
                raise StateError("invalid_budget", "steps_used may not decrease")
            if args.steps_used > payload["budgets"]["steps_max"]:
                raise StateError("budget_exceeded", "steps_used exceeds steps_max")
            payload["budgets"]["steps_used"] = args.steps_used
        if args.next_action is not None:
            payload["resume"]["next_action"] = args.next_action
        if args.prerequisite is not None:
            payload["resume"]["prerequisites"] = args.prerequisite

        runtime = payload.setdefault(
            "runtime",
            {
                "no_progress_windows": 0,
                "last_failure_fingerprint": "",
                "repeated_failure_count": 0,
                "next_decision": "continue",
            },
        )
        after = progress_fingerprint(payload)
        runtime["no_progress_windows"] = (
            0 if after != before else runtime["no_progress_windows"] + 1
        )
        if args.clear_failure:
            runtime["last_failure_fingerprint"] = ""
            runtime["repeated_failure_count"] = 0
        elif args.failure_fingerprint:
            if args.failure_fingerprint == runtime["last_failure_fingerprint"]:
                runtime["repeated_failure_count"] += 1
            else:
                runtime["last_failure_fingerprint"] = args.failure_fingerprint
                runtime["repeated_failure_count"] = 1

        limits = runtime_limits()
        if (
            runtime["repeated_failure_count"] >= limits["max_repeated_failure"]
            or runtime["no_progress_windows"] >= limits["max_no_progress_windows"]
        ):
            runtime["next_decision"] = "escalate"
        elif runtime["no_progress_windows"]:
            runtime["next_decision"] = "reflect"
        else:
            runtime["next_decision"] = "continue"
        payload["session"]["updated_at"] = now()
        atomic_write(state_path(identifier), payload)
    return payload


def resume(identifier: str) -> tuple[dict, bool]:
    payload = read(session_id(identifier))
    changed: list[dict[str, str]] = []
    missing: list[str] = []
    for item in payload.get("working_set", []):
        path = (ROOT / item["path"]).resolve()
        if not path.is_file():
            missing.append(item["path"])
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != item["sha256"]:
            changed.append({"path": item["path"], "expected": item["sha256"], "actual": actual})
    drifted = bool(changed or missing)
    compact = {
        "schema_version": payload["schema_version"],
        "session": payload["session"],
        "task": payload["task"],
        "progress": payload["progress"],
        "decisions": payload["decisions"],
        "verification": payload["verification"],
        "budgets": payload["budgets"],
        "resume": payload["resume"],
        "runtime": payload.get("runtime", {}),
        "integrity": {
            "status": "drifted" if drifted else "clean",
            "changed": changed,
            "missing": missing,
        },
    }
    return compact, drifted


def show(identifier: str) -> dict:
    return read(session_id(identifier))


def list_sessions() -> dict:
    items = []
    if STATE_ROOT.exists():
        for path in sorted(STATE_ROOT.glob("*/state.json")):
            try:
                state = json.loads(path.read_text(encoding="utf-8"))
                items.append({
                    "id": state["session"]["id"],
                    "status": state["task"]["status"],
                    "updated_at": state["session"]["updated_at"],
                    "goal": state["task"]["goal"],
                })
            except (KeyError, OSError, json.JSONDecodeError):
                items.append({"id": path.parent.name, "status": "invalid"})
    return {"schema_version": SCHEMA_VERSION, "sessions": items}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    create = commands.add_parser("start")
    create.add_argument("--id")
    create.add_argument("--goal", required=True)
    create.add_argument("--acceptance", action="append")
    create.add_argument("--steps-max", type=int)
    create.add_argument("--replace", action="store_true")

    update = commands.add_parser("checkpoint")
    update.add_argument("--id", required=True)
    update.add_argument("--status", choices=sorted(STATUSES))
    update.add_argument("--done", action="append")
    update.add_argument("--todo", action="append")
    update.add_argument("--blocked", action="append")
    update.add_argument("--decision", action="append")
    update.add_argument("--verified", action="append")
    update.add_argument("--pending-verification", action="append")
    update.add_argument("--file", action="append")
    update.add_argument("--next-action")
    update.add_argument("--prerequisite", action="append")
    update.add_argument("--steps-used", type=int)
    update.add_argument("--failure-fingerprint")
    update.add_argument("--clear-failure", action="store_true")

    for name in ("show", "resume"):
        command = commands.add_parser(name)
        command.add_argument("--id", required=True)
    commands.add_parser("list")
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "start":
            payload = start(args)
            status = 0
        elif args.command == "checkpoint":
            payload = checkpoint(args)
            status = 0
        elif args.command == "show":
            payload = show(args.id)
            status = 0
        elif args.command == "resume":
            payload, drifted = resume(args.id)
            status = 3 if drifted else 0
        else:
            payload = list_sessions()
            status = 0
    except StateError as exc:
        payload = {"error": exc.code, "message": str(exc)}
        status = 2
    print(json.dumps(payload, indent=2, sort_keys=True))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
