# Design

Use the harness's resolved repository directory as the sole configured boundary.
Compare copied root values lexically before following any foreign symlinks or
inspecting external directories. All common root consumers inherit rejection;
client generation also validates before writes even when MCP is disabled, and
Hermes client renderers use the same resolver. Standalone MCP defaults to cwd;
only an explicit --root selects another project.

Explicit privacy repair anonymizes private provenance, including one old archive.
A state CLI forget operation removes only completed historical records and
protects the current pointer and unfinished tasks. Existing Git history is not
rewritten. Existing downstream copies must receive the patch, use PROJECT_ROOT=auto
and regenerate local configs/caches; no unknown project is modified automatically.

Regression proof covers no foreign path inspection, setup/config rejection,
current/auto roots, private workspace path absence and protected handoff deletion.
