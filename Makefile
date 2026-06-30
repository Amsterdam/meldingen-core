.PHONY: help build push up rebuild lint typecheck typecheck-sync test test-coverage

REGISTRY ?= localhost:5000
VERSION ?= latest
INSTALL_DEV ?= false
UID:=$(shell id --user)
GID:=$(shell id --group)
TEST ?= # used to add testpath as argument to pytest, e.g. TEST=tests/api/v1/endpoints/test_melding.py

dc = docker compose
core = $(dc) run --rm --user=root meldingen-core

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

### DEV ###

build: ## Build Docker Compose stack
	$(dc) build

up: ## Start Docker Compose stack (detached)
	$(dc) up -d

rebuild: ## Rebuild and start Docker Compose stack (detached)
	$(dc) up -d --build

format: ## Auto-fix formatting (black + isort)
	$(core) uv run black .
	$(core) uv run isort .

typecheck: ## Run mypy type checking
	$(core) sh -c "rm -rf .mypy_cache && uv run mypy --strict ."

typecheck-sync: ## Run mypy type checking and update baseline
	$(core) sh -c "rm -rf .mypy_cache && uv run mypy --strict ."

test: ## Run pytest (optional: make test TEST=tests/...)
	$(core) pytest -v $(TEST)

test-pdb: ## Run pytest with python debugger on failure (optional: make test-pdb TEST=tests/...)
	$(core) pytest -v --pdb $(TEST)

test-coverage: ## Run pytest with coverage and enforce minimum threshold
	$(core) pytest -v --cov --cov-fail-under=100 --cov-report=html -v $(TEST)

update: ## Update dependencies (poetry.lock) and rebuild Docker Compose stack
	$(core) uv lock --upgrade

check-all: ## Run all checks (format, typecheck, test)
	$(MAKE) format
	$(MAKE) typecheck
	$(MAKE) test