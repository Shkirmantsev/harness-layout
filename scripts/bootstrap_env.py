#!/usr/bin/env python3
from __future__ import annotations
import os, shutil
from pathlib import Path
from common import ROOT, ENV, parse_env, update_env, random_token, tailscale_identity

EXAMPLE = ROOT / ".env.example"
GENERATED_KEYS = ("LITELLM_MASTER_KEY", "SEARXNG_SECRET", "CRAWL4AI_API_TOKEN")

def sync_missing() -> None:
    if not ENV.exists():
        shutil.copy2(EXAMPLE, ENV)
        print("Created .env from .env.example")
        return
    current = parse_env(ENV); example = parse_env(EXAMPLE)
    updates = {k:v for k,v in example.items() if k not in current}
    if updates:
        with ENV.open("a") as f:
            f.write("\n# Added by make env-sync\n")
            for k,v in updates.items(): f.write(f"{k}={v}\n")
        print(f"Added {len(updates)} missing variables to .env")

def main() -> int:
    sync_missing(); env = parse_env()
    updates: dict[str,str] = {}
    if env.get("PROJECT_ROOT", "auto") in {"auto", ".", "CHANGE_ME_ABSOLUTE_PROJECT_ROOT"}:
        updates["PROJECT_ROOT"] = str(ROOT.resolve())
    if env.get("MAIN_UID","auto") == "auto": updates["MAIN_UID"] = str(os.getuid())
    if env.get("MAIN_GID","auto") == "auto": updates["MAIN_GID"] = str(os.getgid())
    for key in GENERATED_KEYS:
        if env.get(key,"AUTO_GENERATE") == "AUTO_GENERATE":
            prefix = "sk-harness-" if key == "LITELLM_MASTER_KEY" else ""
            updates[key] = random_token(prefix)
    host = env.get("MAIN_TAILSCALE_HOST","auto"); ip = env.get("MAIN_TAILSCALE_IP","auto")
    if host == "auto" or ip == "auto":
        try:
            dns, ts_ip = tailscale_identity()
            if host == "auto": updates["MAIN_TAILSCALE_HOST"] = dns
            if ip == "auto": updates["MAIN_TAILSCALE_IP"] = ts_ip
        except Exception:
            print("WARN: Tailscale identity not resolved; leave auto or set MAIN_TAILSCALE_HOST/IP manually.")
    if updates: update_env(updates)
    try: os.chmod(ENV, 0o600)
    except OSError: pass
    (ROOT / ".generated").mkdir(exist_ok=True)
    print("Environment initialized. Edit .env, then run `make check`.")
    return 0
if __name__ == "__main__": raise SystemExit(main())
