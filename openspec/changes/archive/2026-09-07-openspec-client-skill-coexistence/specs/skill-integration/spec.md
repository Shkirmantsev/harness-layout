# Skill integration specification delta

## ADDED Requirements

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

Local skill synchronization MUST copy only harness-owned core skills to Claude
Code and must not delete or overwrite tool-owned OpenSpec skills.

#### Scenario: sync after multi-client OpenSpec initialization

Given OpenSpec skills exist in `.agents/skills/` and `.claude/skills/`
When local harness skill synchronization runs
Then the four harness core skills are refreshed in `.claude/skills/`
And the OpenSpec-generated Claude skills remain present and tool-owned.
