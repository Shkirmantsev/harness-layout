SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help
STACK := python3 scripts/stack.py

.PHONY: help init env-sync runtime check config plan pull build up start stop restart down status ps logs \
        client-config skills-sync-local skills-sync-remote skills-check \
        hermes-host-setup hermes-host-revoke hermes-sidecar-copy hermes-remote-instructions hermes-check hermes-import \
        verify verify-models test clean

help: ## Show all harness commands.
	@printf "\nHarness Layout — Makefile is the management API\n\n"
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "  \033[36m%-28s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@printf "\nTypical: make init -> edit .env -> make check -> make client-config -> make up -> make verify\n"
	@printf "Hermes once: make hermes-host-setup ENABLE_TAILSCALE_SSH=1 -> make hermes-sidecar-copy -> make hermes-remote-instructions -> apply remote runbook -> make hermes-check\n\n"

init: ## Create/sync .env, generate local secrets, skills, and client configs.
	@python3 scripts/bootstrap_env.py
	@$(MAKE) --no-print-directory skills-sync-local
	@$(MAKE) --no-print-directory client-config

env-sync: ## Add new .env.example variables without overwriting existing values.
	@python3 scripts/bootstrap_env.py

runtime: ## Refresh auto Tailscale identity and generated client files.
	@python3 scripts/bootstrap_env.py
	@$(MAKE) --no-print-directory client-config

check: ## Fail fast on unsafe/incomplete configuration.
	@python3 scripts/check_config.py

config: ## Render Docker Compose configuration for enabled LOCAL features.
	@$(STACK) config

plan: ## Show exactly which local services `make up` will run and remote Hermes status.
	@$(STACK) plan

pull: ## Pull images for all currently enabled local features.
	@$(STACK) pull

build: ## Build local harness images for all enabled local features.
	@$(STACK) build

up: check client-config ## Reconcile old containers and start exactly all enabled LOCAL features.
	@$(STACK) up

start: ## Start already-created containers for enabled local features.
	@$(STACK) start

stop: ## Stop ALL harness containers, including previously-enabled profiles.
	@$(STACK) stop

restart: ## Fully reconcile and restart the enabled local harness stack.
	@$(MAKE) --no-print-directory down
	@$(MAKE) --no-print-directory up

down: ## Stop/remove ALL harness containers/network regardless of current flags.
	@$(STACK) down

status: ## Show ALL harness containers, including stopped/old-profile containers.
	@$(STACK) status

ps: status ## Alias for status.

logs: ## Show recent logs for ALL harness containers. Add ARGS='-f' to follow.
	@$(STACK) logs $(ARGS)

client-config: ## Generate Claude/OpenCode/Codex configs: Claude->remote MCP, OpenCode->native Hermes Runs API tools.
	@python3 scripts/configure_clients.py

skills-sync-local: ## Sync four routed core skills into .claude/skills.
	@python3 scripts/sync_skills.py local

skills-sync-remote: ## Rsync routed core skills to the remote Hermes profile over SSH/Tailscale.
	@python3 scripts/sync_skills.py remote

skills-check: ## Verify Claude exposes the canonical core and no catalog skills.
	@python3 scripts/sync_skills.py check

hermes-host-setup: ## Create/reuse unprivileged main-PC Hermes user + project ACL. Set ENABLE_TAILSCALE_SSH=1 to enable Tailscale SSH.
	@python3 scripts/hermes_host_setup.py $(if $(filter 1 true yes,$(ENABLE_TAILSCALE_SSH)),--yes-enable-tailscale-ssh,)

hermes-host-revoke: ## Remove this project's ACL from the dedicated Hermes user (keeps account).
	@python3 scripts/hermes_host_setup.py --revoke

hermes-sidecar-copy: ## Copy the Claude-specific MCP sidecar source to the remote Hermes host (no secrets).
	@python3 scripts/copy_remote_sidecar.py

hermes-remote-instructions: ## Generate concrete Markdown instructions for the existing remote Hermes profile + Claude MCP sidecar.
	@python3 scripts/render_hermes_remote_setup.py

hermes-check: ## Verify native remote Hermes API and Claude-specific remote MCP sidecar without paid inference.
	@python3 scripts/verify.py --only-hermes

hermes-import: ## Copy an external file into PROJECT_ROOT/.harness/inbox. Usage: make hermes-import FILE=/path/file.pdf
	@test -n "$(FILE)" || (echo "Usage: make hermes-import FILE=/path/to/file"; exit 2)
	@python3 scripts/hermes_import.py "$(FILE)"

verify: ## Verify every enabled service; remote inference is NOT RUN by default.
	@python3 scripts/verify.py

verify-models: ## Verify configured LM Studio/LiteLLM model aliases.
	@python3 scripts/verify_models.py

test: ## Run local static/unit QA without requiring Docker/Tailscale.
	@python3 -m unittest discover -s tests -p 'test_*.py' -v

clean: ## Remove generated client secrets/config artifacts (keeps .env and Docker images).
	@rm -rf .generated
	@rm -f .mcp.json opencode.json .codex/config.toml
	@rm -f .claude/agents/generated-*.md
	@rm -f .opencode/agents/generated-*.md
	@rm -f .opencode/tools/generated-hermes.* .opencode/tools/hermes.js
	@echo "Generated files removed."
