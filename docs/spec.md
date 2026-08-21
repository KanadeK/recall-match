# Spec: Recall Match v0.1.0

## Objective

Recall Match compares a user's owned-product inventory with a local recall dataset and emits auditable candidates. It is designed for households and small organizations that want a private, scriptable check without a cloud account.

Success means a user can run the documented example, see a true exact model match and a fuzzy review candidate, understand why each appeared, receive no unsafe "all clear" claim, and reproduce the same ordered findings on Windows, macOS, and Linux.

## Tech stack

- Python 3.10+.
- Standard-library runtime only.
- `setuptools==84.0.0` build backend.
- Development tools: pytest, pytest-cov, ruff, mypy, and build.

## Public commands

```text
recall-match audit INVENTORY --recalls RECALLS [--json-out PATH] [--markdown-out PATH]
                   [--fail-on match|review|never] [--as-of YYYY-MM-DD]
                   [--max-data-age-days DAYS]
recall-match --version
```

Exit codes:

- `0`: command completed and the configured `--fail-on` threshold was not reached.
- `1`: audit completed and the configured finding threshold was reached.
- `2`: invalid arguments, unreadable input, unsupported schema, or a safety limit was exceeded.

`--fail-on match` is the default. `review` fails on either an identifier match or a review candidate. `never` returns zero for every successfully completed audit.

## Input contracts

### Inventory CSV

Required headers: `item_id,name`.

Optional headers: `brand,model,upc`.

### Recall data

The recall file is raw CPSC JSON: a top-level array with fields such as `RecallID`, `Products`, and `ProductUPCs`.

External text is normalized with Unicode NFKC plus case-folding. Files larger than 50 MiB, missing required fields, duplicate inventory IDs, or malformed top-level data fail fast with exit code 2.

An audit is limited to 5,000,000 inventory-to-recall comparisons. Output paths must be distinct and cannot replace either input file.

## Match contract

Findings are ordered by inventory item, tier, descending score, recall date, and recall ID.

- `identifier_match`, score 100: exact normalized 8–14 digit UPC in a structured UPC field.
- `identifier_match`, score 96: exact model of at least four normalized characters plus a brand phrase of at least two characters.
- `review_candidate`, score up to 88: exact sufficiently-specific model without brand agreement.
- `review_candidate`, score up to 79: brand agreement plus product-name similarity above the documented threshold.
- `review_candidate`, score up to 69: high product-name similarity with at least two significant tokens.
- `no_candidate`: no retained candidate. This must never be rendered as "safe" or "not recalled."

Every retained candidate contains `tier`, `score`, `reasons`, the official/source URL, and the relevant hazard/remedy fields. Fuzzy text alone can never produce `identifier_match`.

## Report contract

JSON reports use `schema_version: "1"` and contain:

- tool version and deterministic `as_of` date;
- input paths and record counts;
- recall source metadata and inferred latest record date;
- summary counts and freshness warnings;
- one result per inventory item, including zero or more ordered candidates.

Markdown escapes user/source-controlled table text and uses links only when the source URL is HTTP(S). Text output is a concise terminal summary. Reports are written atomically so a failed command cannot leave a partial success artifact.

## Project structure

```text
src/recall_match/       application package
tests/                  unit, integration, CLI, and security-limit tests
examples/               runnable inventory and recall fixtures
docs/                   research, specification, ADRs, and repair runbook
scripts/                release gate and deterministic packaging helpers
tasks/                  implementation plan and completion checklist
.github/workflows/      CI automation
```

## Code style

```python
def normalize_model(value: str) -> str:
    """Return a conservative comparison key without guessing aliases."""
    return "".join(character for character in normalize_text(value) if character.isalnum())
```

- Descriptive snake_case names, typed public functions, immutable dataclasses where practical.
- Pure matching functions; filesystem and clock access stay at boundaries.
- Structured domain errors are converted to one-line CLI messages without tracebacks by default.

## Testing strategy

- Unit tests cover normalization, schemas, match tiers, ordering, and false-positive controls.
- Integration tests load real-shaped CPSC fixtures and produce JSON/Markdown reports.
- CLI tests verify stdout, files, exit codes, corrupt inputs, and `--fail-on` modes.
- Security tests enforce the file cap, weak-identifier rejection, and Markdown escaping.
- Coverage gate: at least 90% lines and branches for `recall_match`.
- Release gate runs quality checks, builds wheel and sdist once, and smoke-tests the installed wheel.

## Boundaries

- Always: validate input at loaders, retain provenance, explain matches, link to the source, and run all gates before a release.
- Ask first: add runtime dependencies, network access, new agency presets, or breaking report/CLI changes.
- Never: execute input, fetch input URLs, upload inventories, infer legal status, or present a missing candidate as proof of safety.

## Success criteria

- The example audit yields at least one `identifier_match`, one `review_candidate`, and one `no_candidate` item.
- A deliberately malformed file fails with exit code 2 and a repair-oriented message.
- Reordering recall input does not change report finding order.
- The full test, lint, format, type, build, and clean-install smoke gates pass locally and in GitHub Actions.
- GitHub has a public repository, green CI, annotated `v0.1.0` tag, Release notes, and wheel/sdist assets.
- README contains exact acceptance commands and a failure-repair table.

## Open questions

None block v0.1.0. Other recall sources and live synchronization are explicitly deferred.
