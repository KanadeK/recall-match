# Failure repair runbook

Work from the first failing command. Do not skip a failed gate and do not interpret finding exit code `1` as a software crash.

## 1. Establish the environment

```bash
python --version
python -m pip install -e ".[dev]"
recall-match --version
```

Required result: Python 3.10+ and `recall-match 0.1.0`.

If the command is not found, run `python -m recall_match --version`. If that works, the active environment's script directory is not on `PATH`; activating the environment or reinstalling the wheel fixes the entry point. If the module also fails, rerun the install command and fix its first error.

## 2. Isolate an input failure

Run without report paths first:

```bash
recall-match audit inventory.csv --recalls recalls.json --fail-on never
```

Common repairs:

- `expected UTF-8 text`: export both files as UTF-8; a UTF-8 BOM is accepted.
- `input exceeds the 50 MiB limit`: request a narrower official export or split the inventory and audit each part; do not raise the limit blindly.
- `missing required columns`: the CSV must contain `item_id,name` exactly.
- `duplicate item_id`: assign a stable unique ID to each inventory row.
- `comparison limit`: split the inventory into smaller CSV files and audit each against the same recall export.
- `top-level JSON value must be an array`: supply the raw CPSC array, not an object wrapping the array.
- `RecallID/Title/URL is required`: the file is not a supported raw CPSC record set or contains a damaged record; re-export it from the source.
- Exit `1` with a completed summary: open the candidate report; a configured finding threshold was reached. Rerun with `--fail-on never` only if automation should record rather than fail on findings.

## 3. Isolate an output failure

If an audit succeeds without `--json-out`/`--markdown-out` but fails with them, the destination parent directory must already exist and be writable. Output paths must differ from each other and from both input paths. Create the intended narrow directory, then rerun. Each report file is atomically replaced only after its complete content is written.

## 4. Repair a development gate

Run the exact failed command printed by the release gate:

```bash
python -m ruff check .
python -m ruff format --check .
python -m mypy src
python -m pytest --cov=recall_match --cov-report=term-missing --cov-fail-under=90
python -m build
```

- Ruff check failure: fix the listed file and line; use `python -m ruff format .` only for formatting findings.
- Mypy failure: correct the reported type contract rather than adding a blanket ignore.
- Pytest failure: rerun the named test with `-q`, fix the first behavioral mismatch, then rerun the full suite.
- Coverage failure: add a behavior test for the uncovered contract; do not exclude working code merely to reach the number.
- Build failure: confirm `README.md`, `LICENSE`, `src/recall_match`, and `pyproject.toml` exist, then reinstall development dependencies.

Finally rerun:

```bash
python scripts/release_gate.py
```

The gate deletes and recreates only its own `dist/` and `.release-venv/` outputs.
