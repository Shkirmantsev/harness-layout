---
name: session-checkpoint
description: Create or restore compact, crash-safe project task checkpoints. Use for long or interrupted work, phase boundaries, handoffs, context compaction, explicit resume requests, or before stopping with meaningful work unfinished.
compatibility: Linux/Python 3; project scripts/session_state.py
---

# Session Checkpoint

Persist verified operational state, not conversation history or hidden
reasoning.

## Workflow

Start a checkpoint:

```bash
python3 scripts/session_state.py start \
  --goal "<goal>" \
  --acceptance "<observable condition>"
```

At a meaningful phase boundary, use the returned session ID:

```bash
python3 scripts/session_state.py checkpoint \
  --id <SESSION-ID> \
  --status verifying \
  --done "<verified result>" \
  --todo "<remaining result>" \
  --file path/inside/project \
  --next-action "<one safe next action>"
```

When a command or hypothesis fails, pass a compact stable fingerprint with
`--failure-fingerprint`. Repeated fingerprints and evidence-free checkpoints
are counted by the host-side runtime; `runtime.next_decision` becomes `reflect`
and then `escalate` at the configured limits. A status change or a rewritten
plan is not evidence of progress by itself.

Restore and validate file hashes before continuing:

```bash
python3 scripts/session_state.py resume --id <SESSION-ID>
```

Exit code `3` means the recorded working set drifted. Re-inspect changed or
missing files before acting. Exit code `2` means the checkpoint request itself
is invalid.

## Store

- goal and observable acceptance conditions;
- done/todo/blocked state;
- verified decisions and verification results;
- project-relative file paths with SHA-256 hashes;
- bounded step use and the next safe action.

Do not store raw chats, chain-of-thought, credentials, copied source trees, or
large command output. Put bulky artifacts elsewhere and store only a path/hash.
Checkpoints are ignored under `tmp/local/sessions/` and written atomically.

## Safety

The script rejects working-set files outside the repository. A checkpoint does
not authorize writes, network access, delegation, or continuation past an
approval boundary.
