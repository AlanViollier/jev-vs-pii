.PHONY: help install install-dev hooks format lint lint-slop typecheck docstrings test check format-check ci audit clean bench-free bench-tune bench

help:
	@echo "Targets:"
	@echo "  install      - Install package"
	@echo "  install-dev  - Install package with dev dependencies"
	@echo "  hooks        - Install pre-commit + pre-push hooks"
	@echo "  format       - Format code with ruff"
	@echo "  lint         - Run ruff checks"
	@echo "  lint-slop    - Grep for separator comments + .keywords blocklist"
	@echo "  typecheck    - Run mypy"
	@echo "  docstrings   - Run interrogate (docstring coverage gate, ≥60%)"
	@echo "  test         - Run pytest"
	@echo "  check        - Run format check, lint, lint-slop, typecheck, docstrings, and tests"
	@echo "  ci           - Mirror of GitHub CI: pre-commit run --all-files + pip-audit"
	@echo "  audit        - Scan dependencies for known CVEs (network; not in 'check')"
	@echo "  clean        - Remove caches and build artefacts"
	@echo "  bench-free   - Free lanes (floor, regex, Presidio, local models) on the three test sets"
	@echo "  bench-tune   - Every lane on 20 dev docs per dataset (the pilot), then decoder tuning"
	@echo "  bench        - The full benchmark: free lanes, tuning, every paid lane, scores, chart"

install:
	uv sync

install-dev:
	uv sync --extra dev

hooks:
	uv run pre-commit install
	uv run pre-commit install --hook-type pre-push

format:
	uv run ruff format .

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

check: format-check lint lint-slop typecheck docstrings test

## Mirror of GitHub CI — runs every pre-commit hook + pip-audit locally.
## Use this before pushing when you want to see what CI will see, without
## committing or installing the hooks (Tier 0 workflow).
ci:
	uv run pre-commit run --all-files --show-diff-on-failure
	uv run pip-audit --skip-editable --ignore-vuln PYSEC-2022-42969

format-check:
	uv run ruff format --check .

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

## The benchmark. Paid lanes stop before any call that would pass the budget cap in
## config. A lane whose provider keeps failing is skipped and reported; every dataset still
## runs, and rerunning the target retries only what's missing (responses are cached).
RUN ?= runs/test
DEV ?= runs/dev
DATASETS := ai4privacy tab nemotron
comma := ,
space := $(empty) $(empty)
FREE_LANES := mask_all,regex,presidio,privacy_filter,gliner_pii
JEV_LANES := jev_words,jev_typed
MODELS := qwen3-30b qwen3-235b gpt4.1-nano deepseek-v4-flash deepseek-v4-flash-think haiku4.5
LLM_LANES := $(subst $(space),$(comma),$(foreach model,$(MODELS),llm_sayback:$(model)))
## Dev pilot only, each settled by it: the answer-format study (offsets and tagged rewrites
## loop to the output cap, hours on full test sets), jev_bio (no gain over jev_words at twice
## the cost) and Llama 3.1 8B (loops under a strict schema on up to 60% of docs).
PILOT_ONLY := llm_offsets:qwen3-30b,llm_tagged:qwen3-30b,jev_bio,llm_sayback:llama3-8b
TEST_LANES := $(FREE_LANES),$(JEV_LANES),$(LLM_LANES)
PILOT_LANES := $(TEST_LANES),$(PILOT_ONLY)

bench-free:
	for dataset in $(DATASETS); do \
	  uv run pii-bench run --lanes $(FREE_LANES) --dataset $$dataset --tier full --out $(RUN) || exit 1; \
	done

## Every lane on 20 dev docs per dataset: the pilot, and the data every decoder is tuned on.
bench-tune:
	status=0; for dataset in $(DATASETS); do \
	  uv run pii-bench run --lanes $(PILOT_LANES) --dataset $$dataset --split dev --tier pilot --out $(DEV) || status=1; \
	done; exit $$status
	uv run pii-bench tune $(DEV)
	uv run pii-bench score $(DEV)

bench: bench-tune
	status=0; for dataset in $(DATASETS); do \
	  uv run pii-bench run --lanes $(TEST_LANES) --dataset $$dataset --tier full --out $(RUN) || status=1; \
	done; exit $$status
	uv run pii-bench score $(RUN)
	uv run pii-bench report $(RUN)
