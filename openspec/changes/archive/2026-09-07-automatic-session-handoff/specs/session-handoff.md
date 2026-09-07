# Specification delta

## Requirement: durable active-task handoff

The harness must persist non-secret operational task state in a project-visible
structured handoff and automatically regenerate a concise current-task view when
a task starts or advances.

### Scenario: resume from an empty dialog

Given a non-complete task has been started
When an agent begins a new session without the previous conversation
Then it can discover and validate the active task without knowing a session ID
And recover the goal, acceptance criteria, completed work, remaining work,
decisions, verification state, working files, and next action.

### Scenario: update a task

Given an active task exists
When the checkpoint command records a lifecycle update
Then the structured handoff and `.ai/state/CURRENT.md` describe the same updated
state.

### Scenario: legacy local checkpoint

Given a compatible checkpoint exists only under `tmp/local/sessions/`
When it is resumed or updated by ID
Then it remains readable
And it is promoted into the durable handoff store.
