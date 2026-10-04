# Design

V1 loads a generated instruction file and a project-local `harness_route` custom tool wrapping the existing Python router with stdin, no shell, a timeout and Python interpreter fallback. Enabled LiteLLM workers are native subagents with descriptions, model aliases and leaf permissions. Generator ownership is confined to its own outputs.

V2 uses native `agents`, `system`, `permissions` and `subagent` fields. Root AGENTS directs OpenCode to the generated roster because beta ambient `instructions` are not currently injected. V2 routing uses the Python command rather than claiming legacy custom-tool discovery. Hermes keeps its existing native Runs API adapter.

Descriptions guide automatic selection; delegation is appropriate for independent bounded tasks, not every action. Parent supplies acceptance criteria, file ownership and evidence and reuses child/session IDs. No worker writes parent checkpoint state or recursively dispatches agents.
