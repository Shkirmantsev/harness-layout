# Context and impact

## Affected boundaries

| Boundary | Current problem | Intended impact |
|---|---|---|
| OpenCode → Hermes `/v1/runs` | status can wait without a pending resolver | capability gate and exact-run approval metadata |
| Hermes worker runtime | API sessions bypass resolver under unattended policy | scoped compatibility fix plus guarded probe |
| Claude client → Hermes MCP | caller chooses any absolute root | canonical server-side allowlist |
| Harness filesystem writes | chmod follows content write | private atomic replacement |
| State writers | direct `fcntl` import | portable shared lock |
| Skill publication | remove then copy without serialization | locked staged publication |
| Verification | local-only, non-strict, stale manifest | CI, strict specs, reproducible integrity checks |

## Compatibility

- Existing safe Hermes workers continue to work after advertising and passing the
  resolver capability probe.
- Older or affected workers stop before task creation with an upgrade/patch
  instruction instead of creating a permanently stuck run.
- Existing project-root callers must use a configured allowed root.
- Operator checks retain secret validation; delegated checks intentionally do not.
- Generated OpenCode configuration gains a harness-owned package declaration.

## Security impact

The change removes three privilege-expansion paths: unattended auto-approval as a
tempting workaround, client-controlled filesystem roots, and permissive
intermediate secret files. No new secret access is granted to Hermes.

## Operational impact

Worker rollout adds a capability/probe health check and may require upgrading or
applying the scoped Hermes compatibility patch. CI becomes a required signal.
Manifest changes must be regenerated intentionally.

## Documentation impact

Update native Hermes setup, security guidance, QA evidence, skill links, and the
audit report's resolution table. Durable architecture documentation should name
the resolver-capability and server-enforced-root boundaries.
