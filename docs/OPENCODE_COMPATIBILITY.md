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

## Side-by-side use

OpenCode's V2 documentation states that the beta uses the `opencode2` binary and does not replace the V1 `opencode` binary. To test both against one repository:

1. keep V1 selected for normal work;
2. set V2 in `.env`, regenerate and test with `opencode2`;
3. switch back to V1 and regenerate before using `opencode` again.

Because both generations use the same project config path, do not assume one generated file is simultaneously native to both generations.
