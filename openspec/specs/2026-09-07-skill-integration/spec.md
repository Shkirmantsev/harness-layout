# skill-integration Specification

## Purpose

Define how harness-owned core skills coexist safely with workflow skills that
external coding-tool integrations generate in the same discovery directories.

## Requirements

### Requirement: tool-owned skills coexist with harness core skills

The harness MUST distinguish its fixed directly discoverable core skills from
skills generated and owned by an integrated coding tool, even when both occupy
the top level of `.agents/skills/`.

#### Scenario: OpenSpec initializes Codex skills

Given the four harness core skills are installed
When OpenSpec initializes its Codex integration under `.agents/skills/`
Then all OpenSpec workflow skills remain directly discoverable
And the harness still identifies exactly its four named skills as harness core.

### Requirement: local skill sync preserves integration-owned outputs

Local skill synchronization MUST copy only harness-owned core skills to the
project-local Claude Code and OpenCode skill directories and MUST NOT delete or
overwrite tool-owned OpenSpec or unrelated personal skills. Codex MUST continue
using canonical `.agents/skills/` discovery without writes to global skill paths.

#### Scenario: sync after multi-client OpenSpec initialization

- **GIVEN** OpenSpec skills exist in canonical and client-specific directories
- **WHEN** local harness skill synchronization runs
- **THEN** the four harness core skills are refreshed in both project-local mirrors
- **AND** the OpenSpec-generated and personal skills remain present and tool-owned
- **AND** no user-global Codex directory is modified.

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
