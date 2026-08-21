# Contributing

Thanks for improving Recall Match. Changes should preserve its conservative evidence boundary and zero-dependency runtime.

## Setup

```bash
git clone https://github.com/KanadeK/recall-match.git
cd recall-match
python -m venv .venv
python -m pip install -e ".[dev]"
```

Activate the virtual environment using the command appropriate for your shell, then run:

```bash
python -m ruff check .
python -m ruff format --check .
python -m mypy src
python -m pytest --cov=recall_match --cov-report=term-missing --cov-fail-under=90
```

## Change contract

- Add or change a test before changing matching, input, report, or exit-code behavior.
- Keep fuzzy evidence in `review_candidate`; never promote it to an identifier match.
- Validate only at input, filesystem, and other external boundaries.
- Do not add network access or a runtime dependency without an accepted ADR.
- Preserve deterministic ordering and source evidence.
- Do not claim an unmatched product is safe.

Pull requests should describe the user-visible change, the commands run, and any report/CLI compatibility impact. Keep unrelated cleanup out of the change.

