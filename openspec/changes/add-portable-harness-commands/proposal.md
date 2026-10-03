# Complete portable harness commands

## Why

The donor has operator commands for MCP lifecycle that were excluded from the
initial adoption. The user explicitly requests them and a complete setup/Wiki
workflow. Existing client-managed stdio is usable but does not expose the manual
lifecycle commands. The donor's background stdio process has no client transport.

## What Changes

- Add run/stop/status/logs/clean MCP commands and donor aliases via Make and Python.
- Give the background process a usable loopback Streamable HTTP endpoint.
- Retain default client-managed stdio; allow explicit HTTP client configuration.
- Add non-destructive Wiki init, init-mcp and harness-* aliases.
- Remove Bash/awk dependencies from core Make recipes and help.

## Capabilities

### New Capabilities

- `2026-10-04-harness-command-lifecycle`: portable commands and owned MCP lifecycle.

### Modified Capabilities

None. Existing client-managed stdio and project initialization behavior are retained.

## Impact

Harness CLI, Make targets, optional MCP transport, generated client settings,
focused lifecycle tests and workflow documentation. No product business code,
Java/POM files, external MCP lifecycle or global client configuration changes.
