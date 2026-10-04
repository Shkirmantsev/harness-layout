# Why

OpenCode configuration advertises MCP endpoints but neither a startup team/routing contract nor enabled local-model workers. Agents discover delegation only after user reminders.

# What Changes

Load a compact generated routing/team roster at startup, expose the deterministic router as a V1 custom tool, and register enabled LiteLLM local workers as leaf subagents. Keep native Hermes optional and approval scoped. Preserve separate V1/V2 formats and personal agents/tools.

# Capabilities

- Modified: `2026-09-07-skill-integration` — automatic OpenCode routing and configured team discovery.

# Impact

Client generator, OpenCode templates, regression tests, compatibility docs and explanatory Wiki. No business logic or external project access.
