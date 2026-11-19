.PHONY: lint typecheck test check-all

UV ?= uv
RUFF ?= $(UV) run --group dev ruff
TY ?= $(UV) run --group dev ty
PYTEST ?= $(UV) run --group dev pytest

lint:
	$(RUFF) check src tests

typecheck:
	$(TY) check --extra-search-path src src tests

test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTEST)

check-all: lint typecheck test
