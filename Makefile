.PHONY: help install install-dev hooks lint lint-slop typecheck docstrings test check ci audit clean

help:
	@echo "Targets:"
	@echo "  install      - Install package"
	@echo "  install-dev  - Install package with dev dependencies"
	@echo "  hooks        - Install pre-commit + pre-push hooks"
	@echo "  lint         - Run ruff checks"
	@echo "  lint-slop    - Grep for separator comments + .keywords blocklist"
	@echo "  typecheck    - Run mypy"
	@echo "  docstrings   - Run interrogate (docstring coverage gate, ≥60%)"
	@echo "  test         - Run pytest"
	@echo "  check        - Run lint, lint-slop, typecheck, docstrings, and tests"
	@echo "  ci           - Mirror of GitHub CI: pre-commit run --all-files + pip-audit"
	@echo "  audit        - Scan dependencies for known CVEs (network; not in 'check')"
	@echo "  clean        - Remove caches and build artefacts"

install:
	uv sync

install-dev:
	uv sync --extra dev

hooks:
	uv run pre-commit install
	uv run pre-commit install --hook-type pre-push

lint:
	uv run ruff check .

## Visual separator comments are forbidden by STYLE.md. Ruff has no built-in
## rule, so grep enforces it. Patterns caught:
##   # ──────   (bare horizontal separators)
##   # ── text ──   (named with separator wings — also slop per STYLE.md)
##   # ====   # ----   (ASCII variants)
## Regex requires 2+ consecutive [─═=-] chars anywhere after the leading `#`.
## Excludes .venv and cache dirs.
##
## Second pass: if `.keywords` exists (gitignored, one regex per line; `#` and
## blank lines skipped), grep every tracked file for any term in it and fail.
## Use for project-local blocklists — names, internal terms, etc.
lint-slop:
	@result=$$(grep -rnE '^[[:space:]]*#+[[:space:]]*[─═=-]{2,}' --include='*.py' \
	  --exclude-dir=.venv --exclude-dir=.mypy_cache --exclude-dir=.ruff_cache \
	  --exclude-dir=.pytest_cache --exclude-dir=__pycache__ --exclude-dir=.git \
	  . 2>/dev/null || true); \
	if [ -n "$$result" ]; then \
	  echo ""; \
	  echo "  ✗ Visual separator comment lines found (forbidden by STYLE.md):"; \
	  echo ""; \
	  echo "$$result" | sed 's/^/    /'; \
	  echo ""; \
	  echo "  Use '## Section name' headers instead."; \
	  exit 1; \
	fi
	@if [ -f .keywords ] && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then \
	  patterns=$$(grep -vE '^[[:space:]]*(#|$$)' .keywords | paste -sd '|' -); \
	  if [ -n "$$patterns" ]; then \
	    result=$$(git ls-files -z | xargs -0 grep -inIE "($$patterns)" 2>/dev/null || true); \
	    if [ -n "$$result" ]; then \
	      echo ""; \
	      echo "  ✗ Forbidden keyword found (.keywords blocklist):"; \
	      echo ""; \
	      echo "$$result" | sed 's/^/    /'; \
	      echo ""; \
	      echo "  Remove the term or update .keywords."; \
	      exit 1; \
	    fi; \
	  fi; \
	fi

typecheck:
	uv run mypy .

docstrings:
	uv run interrogate .

test:
	uv run pytest || test $$? -eq 5

check: lint lint-slop typecheck docstrings test

## Mirror of GitHub CI — runs every pre-commit hook + pip-audit locally.
## Use this before pushing when you want to see what CI will see, without
## committing or installing the hooks (Tier 0 workflow).
ci:
	uv run pre-commit run --all-files --show-diff-on-failure
	uv run pip-audit --skip-editable --ignore-vuln PYSEC-2022-42969

## CVE scan via pip-audit. Kept out of `check` because it needs network and
## fails on transient PyPI advisory-DB hiccups. Runs in CI on every push.
##
## --skip-editable: don't try to audit our own placeholder package on PyPI.
## --ignore-vuln PYSEC-2022-42969: the `py` library is abandoned with no fix;
##   add new ignores here (with a comment) as you discover known-unfixable vulns.
audit:
	uv run pip-audit --skip-editable --ignore-vuln PYSEC-2022-42969

clean:
	@rm -rf .mypy_cache .ruff_cache .pytest_cache dist build *.egg-info
	@find . -not -path './.venv/*' -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@find . -not -path './.venv/*' -type f -name '*.py[co]' -delete 2>/dev/null || true
