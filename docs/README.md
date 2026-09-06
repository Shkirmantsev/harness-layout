# Documentation map

[Project home](../README.md) · [Wiki index](../.ai/wiki/INDEX.md) · [Structure and ownership](PROJECT_STRUCTURE.md)

## Setup and daily work

- [Quick start](QUICKSTART.md): initialize, install MCP, and validate.
- [Usage](USAGE_EN.md): daily commands and workflows.
- [Configuration](CONFIGURATION.md): supported settings and client generation.
- [OpenCode compatibility](OPENCODE_COMPATIBILITY.md): selecting a configuration generation.
- [Engineering conventions](conventions/README.md): task-specific design, implementation, testing, and review defaults.
- [OpenSpec workflow](../openspec/README.md): artifact dependencies and adoption.
- [Skills](SKILLS.md): routing and reusable procedures.
- [Security](SECURITY.md): credentials and project boundaries.
- [Troubleshooting](TROUBLESHOOTING.md): configuration and service diagnostics.
- [QA report](../QA_REPORT.md): executed checks and limitations.

## Optional infrastructure

- [Web stack](WEB_STACK.md): SearXNG, Crawl4AI, and Playwright.
- [Hermes native setup](HERMES_NATIVE_SETUP.md): client transports and deployment.
- [Hermes remote instructions](HERMES_REMOTE_AGENT_INSTRUCTION.md): worker operating contract.
- [Hermes deployment runbook](HERMES_TAILSCALE_WORKER_FINALIZE_v3_NATIVE.md): detailed native-worker setup; the filename retains its architecture version.

## Migration, provenance, and historical context

These explain prior decisions and upgrades; use current configuration and source for current behavior.

- [Upgrade to v4](migration/UPGRADE_TO_V4.md).
- [Upgrade 3.1.1 to 3.2.0](UPGRADE_3_1_1_TO_3_2_0.md).
- [Migration from bridge architecture](../MIGRATION_FROM_BRIDGE.md).
- [Recommendation matrix](REPORT_RECOMMENDATION_MATRIX.md).
- [Adaptive skill runtime plan](superpowers/plans/2026-09-05-adaptive-skill-runtime.md).
- [Third-party skills](THIRD_PARTY_SKILLS.md) and [licenses](THIRD_PARTY_LICENSES.md).
