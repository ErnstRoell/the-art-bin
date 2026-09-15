# Entry points for The Art Bin: install the server, add a smell, run the checks.
#
# JOBS sets the workers for the parallel targets. The suite is 38 read-only
# tests, 7 of which each spawn their own stdio server subprocess, so they
# parallelise cleanly. Measured on a 24-core box: 3.8s serial, 1.9s at 4-8
# workers, 2.5s at `auto` (24) -- past 8 the worker startup cost outweighs
# the suite.
#
# ARGS is forwarded to install-mcp and new-smell, both of which are thin
# wrappers over a script with its own --help.
JOBS        ?= 8
PYTEST_ARGS ?=
ARGS        ?=
SLUG        ?=

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@grep -hE '^[a-z0-9-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk -F':.*?## ' '{printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Sync the dev environment (pytest, pytest-asyncio)
	uv sync

.PHONY: install-mcp
install-mcp: ## Register the MCP server with a client (ARGS='--client desktop', --help for more)
	./install.sh $(ARGS)

.PHONY: new-smell
new-smell: ## Scaffold a new smell (SLUG=my-smell, or no SLUG to be asked for everything)
	uv run new_smell.py $(SLUG) $(ARGS)

.PHONY: test
test: ## Run the whole suite serially (what CI runs)
	uv run pytest -q $(PYTEST_ARGS)

.PHONY: test-parallel
test-parallel: ## Run the whole suite in parallel (JOBS workers, default 8)
	uv run --with pytest-xdist pytest -q -n $(JOBS) $(PYTEST_ARGS)

.PHONY: test-unit
test-unit: ## Run the reading-layer tests only (fast, no subprocesses)
	uv run pytest -q tests/test_corpus.py $(PYTEST_ARGS)

.PHONY: test-e2e
test-e2e: ## Run the stdio end-to-end tests in parallel
	uv run --with pytest-xdist pytest -q -n $(JOBS) tests/test_server_e2e.py $(PYTEST_ARGS)

.PHONY: validate
validate: ## Validate the corpus and check catalog.json is fresh
	uv run validate.py

.PHONY: catalog
catalog: ## Regenerate catalog.json from snippets/
	uv run validate.py --write-catalog

.PHONY: check
check: validate test ## Validate the corpus, then run the suite (both CI jobs)

# The wheel carries a copy of the corpus (see pyproject force-include), so the installed
# binary serves a snapshot taken at build time rather than reading this checkout. Run
# `make catalog` first if you have added smells, or the snapshot ships a stale catalog.
.PHONY: build
build: ## Build the wheel and sdist into dist/
	uv build

.PHONY: install-tool
install-tool: ## Install art-bin-server on PATH as a standalone tool
	uv tool install --force .

.PHONY: uninstall-tool
uninstall-tool: ## Remove the installed art-bin-server tool
	uv tool uninstall art-bin-server

.PHONY: clean
clean: ## Remove build artifacts, pytest and bytecode caches
	rm -rf .pytest_cache dist
	find src tests -name __pycache__ -type d -exec rm -rf {} +
