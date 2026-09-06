# Third-party licensing notes

This is an engineering summary, not legal advice. Review licenses with your organization's compliance process.

Project-level Agent Skill sources, pinned audit revisions, adaptations, and retained notices are listed in [THIRD_PARTY_SKILLS.md](THIRD_PARTY_SKILLS.md).

## Crawl4AI

Pinned default: `0.9.2`.

Repository license: Apache License 2.0 plus the repository's explicit attribution requirement. Preserve required notices when distributing/publicly using a product based on it.

Required attribution text from the upstream license:

> This product includes software developed by UncleCode (https://x.com/unclecode) as part of the Crawl4AI project (https://github.com/unclecode/crawl4ai).

This is the main reason Crawl4AI is the default crawler in this layout: it is free to self-host and has a substantially simpler enterprise compliance posture than the removed Firecrawl stack.

## SearXNG

SearXNG is AGPL-3.0. It is optional and runs as a separate service. Enterprise/commercial use is permitted, but modifications/network deployment can create source-sharing obligations. If your organization prohibits AGPL software, leave `WEB_SEARCH_ENABLED=false` and use an approved search service/native agent web search instead.

## Firecrawl

Not included. Firecrawl core is AGPL-3.0 and its full self-hosted architecture was also materially heavier than required for this layout.
