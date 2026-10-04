# OpenCode compatibility policy

## Default

`OPENCODE_CONFIG_GENERATION=v1`

V1 is the harness default because OpenCode 2 is currently beta and has intentionally breaking configuration/plugin/server changes.

The V1 generator uses the production documentation schema:

- `provider`
- `permission`
- MCP server names directly under `mcp`
- `enabled` on MCP entries

## Optional V2 beta

Set:

```dotenv
OPENCODE_CONFIG_GENERATION=v2
```

Then run:

```bash
python harness.py client-config
```

Native V2 generation uses:

- `providers`
- `package` + `settings`
- ordered `permissions` rules
- MCP entries under `mcp.servers`
- `disabled` instead of V1 `enabled`

The two formats are generated independently. The harness never creates a mixed V1/V2 configuration.

## Automatic routing and team discovery

Run `python harness.py client-config` after updating the harness or changing
enabled models, then restart OpenCode. No manual worker mention is required:

- V1 loads `.generated/opencode-routing.md` through `instructions` and discovers
  `harness_route` from `.opencode/tools/harness.js`. This tool runs the existing
  skill router with task text on stdin, without shell evaluation.
- Enabled `LOCAL_MODEL_1..4` entries become described
  `.opencode/agents/generated-<alias>-worker.md` subagents only when
  `LITELLM_ENABLED=true`. They use `harness/<alias>`, the same provider/model
  catalog as the client configuration, and cannot recursively delegate.
- The startup roster directs the parent to choose workers for independent
  bounded tasks, supply scope and acceptance criteria, reuse returned IDs for
  follow-up and reconcile evidence. Simple/dependent work stays with the parent.
- Hermes appears only when enabled and keeps its native `hermes_*` transport
  and explicit approval rule; it is never a local model-backed subagent.
- V2 uses native Markdown `permissions` and `subagent` actions. Its beta ambient
  `instructions` field is not currently injected, so root `AGENTS.md` directs
  intake to the generated roster. Routing uses the Python command; the V1 router
  custom tool is removed when switching to V2. Existing Hermes beta adapter
  compatibility still needs verification with the selected V2 runtime.

Generation refreshes harness-owned workers/tools while preserving personal
agents and tools. Built-in `explore` and `general` remain available when local
models are disabled. Discovery and instructions guide model choices; they do
not guarantee a particular model will delegate every eligible task.

Native references: [V1 agents](https://opencode.ai/docs/agents/),
[V1 configuration](https://opencode.ai/docs/config/),
[V2 agents](https://opencode.ai/v2/docs/agents), and
[V2 instructions](https://opencode.ai/v2/docs/instructions).

## Side-by-side use

OpenCode's V2 documentation states that the beta uses the `opencode2` binary and does not replace the V1 `opencode` binary. To test both against one repository:

1. keep V1 selected for normal work;
2. set V2 in `.env`, regenerate and test with `opencode2`;
3. switch back to V1 and regenerate before using `opencode` again.

Because both generations use the same project config path, do not assume one generated file is simultaneously native to both generations.
