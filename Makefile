SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help
PYTHON ?= python3
STACK := $(PYTHON) scripts/stack.py

.PHONY: help init init-mcp env-sync runtime check wiki-index wiki-validate openspec-check mcp-install \
        config plan pull build up start stop restart down status ps logs client-config \
        skills-sync-local skills-sync-remote skills-check manifest-generate manifest-check hermes-host-setup hermes-host-revoke \
        hermes-sidecar-copy hermes-remote-instructions hermes-check hermes-import verify verify-models test clean

help: ## Show all harness commands.
	@printf "\nHarness Layout v4 — portable core + optional integrations\n\n"
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "  \033[36m%-28s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@printf "\nPortable equivalent on any OS: python harness.py <command>\n"
	@printf "Typical: make init -> edit .env if needed -> make mcp-install -> make client-config -> make check\n\n"

init: ## Portable core init; also disables telemetry when OpenSpec is installed.
	@$(PYTHON) harness.py init

init-mcp: ## Init core (including OpenSpec opt-out) and install project-context MCP.
	@$(PYTHON) harness.py init --install-mcp

env-sync: ## Add new .env.example variables without overwriting existing values.
	@$(PYTHON) scripts/bootstrap_env.py

runtime: ## Refresh auto identities and generated client files.
	@$(PYTHON) scripts/bootstrap_env.py
	@$(PYTHON) harness.py client-config

check: ## Validate config, Wiki, OpenSpec structure, and run core tests.
	@$(PYTHON) harness.py check

wiki-index: ## Rebuild disposable SQLite FTS index from canonical Markdown Wiki.
	@$(PYTHON) harness.py index

wiki-validate: ## Validate Wiki stable IDs and links.
	@$(PYTHON) harness.py wiki-validate

openspec-check: ## Validate production-sdd structure; invoke OpenSpec CLI when installed.
	@$(PYTHON) harness.py openspec-check

manifest-generate: ## Regenerate the deterministic source artifact manifest.
	@$(PYTHON) harness.py manifest-generate

manifest-check: ## Verify the deterministic source artifact manifest.
	@$(PYTHON) harness.py manifest-check

mcp-install: ## Install project-context MCP into tmp/local/project-context/venv.
	@$(PYTHON) harness.py mcp-install

client-config: ## Generate Claude/OpenCode/Codex configs; OpenCode V1 stable is default, V2 beta is opt-in.
	@$(PYTHON) harness.py client-config

config: ## Render Docker Compose configuration for enabled optional LOCAL features.
	@$(STACK) config

plan: ## Show enabled optional local services and remote Hermes status.
	@$(STACK) plan

pull: ## Pull images for enabled optional local features.
	@$(STACK) pull

build: ## Build local harness images for enabled optional local features.
	@$(STACK) build

up: check client-config ## Reconcile and start enabled optional LOCAL features.
	@$(STACK) up

start: ## Start already-created optional containers.
	@$(STACK) start

stop: ## Stop ALL harness containers, including old profiles.
	@$(STACK) stop

restart: ## Reconcile and restart enabled optional local stack.
	@$(MAKE) --no-print-directory down
	@$(MAKE) --no-print-directory up

down: ## Stop/remove ALL harness containers/network.
	@$(STACK) down

status: ## Show ALL harness containers.
	@$(STACK) status

ps: status ## Alias for status.

logs: ## Show recent logs for ALL harness containers; ARGS='-f' follows.
	@$(STACK) logs $(ARGS)

skills-sync-local: ## Sync directly discoverable routed core skills into .claude/skills.
	@$(PYTHON) scripts/sync_skills.py local

skills-sync-remote: ## Rsync routed core skills to optional remote Hermes profile.
	@$(PYTHON) scripts/sync_skills.py remote

skills-check: ## Verify Claude skill exposure and catalog isolation.
	@$(PYTHON) scripts/sync_skills.py check

hermes-host-setup: ## Optional: configure unprivileged main-PC Hermes access.
	@$(PYTHON) scripts/hermes_host_setup.py $(if $(filter 1 true yes,$(ENABLE_TAILSCALE_SSH)),--yes-enable-tailscale-ssh,)

hermes-host-revoke: ## Optional: remove this project's ACL from dedicated Hermes user.
	@$(PYTHON) scripts/hermes_host_setup.py --revoke

hermes-sidecar-copy: ## Optional: copy Claude-specific Hermes MCP sidecar source to remote host.
	@$(PYTHON) scripts/copy_remote_sidecar.py

hermes-remote-instructions: ## Optional: generate remote Hermes setup instructions.
	@$(PYTHON) scripts/render_hermes_remote_setup.py

hermes-check: ## Optional: verify remote Hermes control paths without paid inference.
	@$(PYTHON) scripts/verify.py --only-hermes

hermes-import: ## Optional: stage external file into PROJECT_ROOT/.harness/inbox. FILE=/path/file
	@test -n "$(FILE)" || (echo "Usage: make hermes-import FILE=/path/to/file"; exit 2)
	@$(PYTHON) scripts/hermes_import.py "$(FILE)"

verify: ## Verify enabled optional services; remote inference is NOT RUN by default.
	@$(PYTHON) scripts/verify.py

verify-models: ## Verify configured optional local/LiteLLM model aliases.
	@$(PYTHON) scripts/verify_models.py

test: ## Run core tests without requiring Docker/Tailscale.
	@$(PYTHON) harness.py test

clean: ## Remove generated clients/index/runtime state; preserve .env and source.
	@$(PYTHON) harness.py clean
