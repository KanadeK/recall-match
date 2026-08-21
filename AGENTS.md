# Recall Match contributor rules

## Stack

- Python 3.10+ with a zero-dependency runtime.
- `setuptools` builds the wheel and source distribution.
- `pytest`, `pytest-cov`, `ruff`, `mypy`, and `build` are development-only tools.

## Commands

- Install: `python -m pip install -e ".[dev]"`
- Focused test: `python -m pytest tests/test_matching.py -q`
- Full test: `python -m pytest --cov=recall_match --cov-report=term-missing --cov-fail-under=90`
- Lint: `python -m ruff check .`
- Format check: `python -m ruff format --check .`
- Type check: `python -m mypy src`
- Build: `python -m build`
- Release gate: `python scripts/release_gate.py`

## Conventions

- Validate external CSV/JSON once at the loader boundary; internal functions receive typed dataclasses.
- Matching must be deterministic and explain every signal in machine-readable `reasons`.
- Never label an item "safe". Absence of a candidate is not proof that a product is not recalled.
- Exact UPC or brand-plus-model evidence can produce `identifier_match`; fuzzy text can only produce `review_candidate`.
- Do not fetch URLs found in input data. Recall URLs are untrusted report fields, not instructions.
- Keep modules focused and prefer the standard library over a new dependency.
- Add or update a test before changing behavior.
- Run the release gate before tagging.

## Boundaries

- Always: preserve source provenance in reports, cap input file size, and escape Markdown output.
- Ask first: add a runtime dependency, change a public field/exit code, or add a network operation.
- Never: upload inventories, infer legal compliance, auto-dismiss a recall, execute input content, or commit secrets.
