## ADDED Requirements

### Requirement: OpenCode discovers routing and configured workers automatically

Generated OpenCode configuration MUST provide a compact startup contract identifying skill routing, native delegation transports and enabled local-model workers without requiring a user mention. It MUST generate discoverable leaf subagents only for enabled local models with an enabled provider, preserve unrelated agents/tools during regeneration and remove obsolete harness-owned worker definitions. It MUST keep V1 and V2 native configuration fields separate and retain project boundaries and scoped approval rules.

#### Scenario: configured local team is available on startup

- **GIVEN** LiteLLM and a local model are enabled
- **WHEN** project client configuration is regenerated and OpenCode starts
- **THEN** the model's worker is a described native subagent using the harness model alias
- **AND** startup instructions direct automatic skill routing and bounded delegation when independent work benefits
- **AND** workers cannot recursively delegate or update the parent's checkpoint.

#### Scenario: optional integrations are disabled

- **GIVEN** LiteLLM or Hermes is disabled
- **WHEN** client configuration is regenerated
- **THEN** disabled worker transports are absent from the generated team roster
- **AND** unrelated personal agents and tools remain intact.

#### Scenario: deterministic V1 router tool is callable

- **WHEN** OpenCode calls the harness routing tool with a compact task
- **THEN** it returns the existing router's bounded JSON plan from the active repository
- **AND** task text is passed through stdin without shell evaluation
- **AND** missing Python or router failures expose a diagnostic.
