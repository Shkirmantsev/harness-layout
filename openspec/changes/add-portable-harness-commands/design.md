# Design

## Context

Donor scripts/project_mcp.py keeps a detached stdio child alive but redirects its
protocol output into a log. Its os.kill(pid, 0) liveness probe is unsafe on Windows,
where that API may terminate the target. Import the command surface with corrected
transport and ownership rather than preserving those defects.

## Decisions

Use the already installed MCP SDK's Streamable HTTP server bound only to 127.0.0.1.
Default client transport stays stdio; HTTP is selected explicitly in .env and all
client renderers reuse their existing remote-server support. Default port is 18883.
A detached supervisor owns its Popen child. Stop is an instance-scoped local file
request; the supervisor terminates its own child handle, never a PID from disk.
Readiness verifies the server instance and PID over loopback without system proxies.
Windows liveness uses OpenProcess/GetExitCodeProcess; POSIX uses signal zero.
Runtime state/log/control files stay ignored under tmp/local/mcp and are cleaned
only after shutdown. Whole-runtime clean refuses while the owned MCP is active.
A process lock serializes operator commands; process-specific worker state is
written atomically. Missing install, unresponsive workers and port conflicts fail
with actionable messages. A daemon reaper retains the supervisor Popen handle.

Make uses Python for help and core commands, with OS-specific interpreter defaults;
Python commands remain usable when GNU Make is absent. Wiki init validates and
indexes the existing canonical Wiki, without rewriting authored Markdown.

## Verification and rollback

Exercise a real HTTP initialize/list/call sequence, duplicate starts, port conflicts,
stop/clean, native process probes and existing stdio handshake on Linux/Windows.
No new third-party dependency is required. Revert transport to stdio and regenerate
clients to roll back shared HTTP use; stop-mcp removes only the owned background
process. Lifecycle clean preserves Wiki, .env, installed venv and unrelated files.
