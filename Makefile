# Test and validation entry points for The Art Bin.
#
# JOBS sets the workers for the parallel targets. The suite is 27 read-only
# tests, 7 of which each spawn their own stdio server subprocess, so they
# parallelise cleanly. Measured on a 24-core box: 3.8s serial, 1.9s at 4-8
# workers, 2.5s at `auto` (24) -- past 8 the worker startup cost outweighs
# the suite.
JOBS        ?= 8
PYTEST_ARGS ?=

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@grep -hE '^[a-z0-9-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk -F':.*?## ' '{printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Sync the dev environment (pytest, pytest-asyncio)
	uv sync

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

.PHONY: clean
clean: ## Remove pytest and bytecode caches
	rm -rf .pytest_cache
	find src tests -name __pycache__ -type d -exec rm -rf {} +
