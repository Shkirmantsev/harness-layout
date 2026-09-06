# Migration from the previous bridge-based layout

Removed runtime concepts:

- `project-dev` mandatory project container;
- project HTTP/file bridge;
- session/project binding database and `make hermes-bind`;
- remote `harness_project` MCP for repository reads/writes;
- local `hermes-bridge` / attachment relay;
- local Hermes-control container;
- global `/workspace` project symlink;
- Firecrawl API/browser/Redis/RabbitMQ/PostgreSQL/MCP ecosystem.

Replacement:

- Hermes native SSH/file/vision tools operate on the project through a dedicated main-PC account;
- every request supplies the absolute `PROJECT_ROOT`;
- Tailscale SSH is the recommended keyless transport;
- OpenCode uses the native Hermes OpenAI API directly;
- Claude uses a small MCP **on the remote Hermes host** that only controls native `/v1/runs` lifecycle;
- Codex receives no Hermes transport in this phase;
- Crawl4AI handles crawl/render/extract; SearXNG and Playwright remain optional orthogonal tools.

Do not deploy old project-binding/attachment sidecars after migration.
