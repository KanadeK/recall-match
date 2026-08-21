# Recall Match

[![CI](https://github.com/KanadeK/recall-match/actions/workflows/ci.yml/badge.svg)](https://github.com/KanadeK/recall-match/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/KanadeK/recall-match)](https://github.com/KanadeK/recall-match/releases/latest)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Offline, explainable matching of products you own against official CPSC recall data.

Recall Match turns a small inventory CSV and a downloaded CPSC JSON file into terminal, JSON, and Markdown evidence reports. Exact identifiers are kept separate from fuzzy review candidates, every finding explains why it appeared, and your inventory never leaves your machine.

```text
Recall Match: 3 items; 1 identifier match; 1 review candidate; 1 without candidates.
```

> Recall Match is a screening tool. A missing candidate is not proof that a product is safe or not recalled; confirm findings on the linked source page.

<details>
<summary>中文简介</summary>

Recall Match 是一个离线、零运行时依赖的产品召回匹配 CLI。它读取自有物品 CSV 和本地 CPSC JSON，将精确 UPC/品牌型号证据与模糊复核候选严格分层，并输出可归档的 JSON/Markdown 报告。它不会上传清单，也不会把“未找到候选”误写成“安全”。

</details>

## Why this exists

Official recall data is machine-readable, but comparing it with labels on products already in a home, school, repair shop, library, or small resale inventory still takes manual work. Hosted catalog APIs exist, but they require sending inventory to a service and usually hide the matching logic.

Recall Match is deliberately narrow:

- offline after you obtain the source JSON;
- zero runtime dependencies;
- strong evidence only for a valid UPC or sufficiently specific brand-plus-model match;
- fuzzy text can only create a `review_candidate`;
- stable exit codes work in scheduled jobs and CI;
- source URLs, hazards, remedies, and reasons stay in the report.

## Quick start

Python 3.10 or newer is required.

```bash
python -m pip install .
recall-match audit examples/inventory.csv \
  --recalls examples/cpsc-recalls.json \
  --json-out report.json \
  --markdown-out report.md \
  --as-of 2026-08-21 \
  --fail-on never
```

The bundled data is synthetic but follows the CPSC JSON shape. It produces one identifier match, one review candidate, and one item without a candidate. Generated reference reports are in [`examples/expected`](examples/expected).

To use current data, obtain a JSON array through the [official CPSC Recall API](https://www.cpsc.gov/Recalls/CPSC-Recalls-Application-Program-Interface-API-Information), save it locally, and pass that file to `--recalls`. Recall Match never fetches URLs itself.

## Inventory format

CSV headers:

| Header | Required | Meaning |
| --- | --- | --- |
| `item_id` | yes | Stable unique ID chosen by you |
| `name` | yes | Human-readable product name |
| `brand` | no | Brand printed on the product |
| `model` | no | Model printed on the label |
| `upc` | no | UPC/GTIN digits; spaces and punctuation are ignored |

```csv
item_id,name,brand,model,upc
chair-01,Convertible High Chair,Harppa,BHC001,012345678905
```

## Evidence tiers

| Result | Evidence | Meaning |
| --- | --- | --- |
| `identifier_match` / 100 | Exact normalized 8–14 digit UPC | Strong candidate; verify the official notice and label |
| `identifier_match` / 96 | Exact model of at least four characters plus brand phrase | Strong candidate; verify variants and dates |
| `review_candidate` / up to 88 | Model without brand agreement | Inspect the label manually |
| `review_candidate` / up to 79 | Brand plus similar product name | Fuzzy lead only |
| `review_candidate` / up to 69 | High name similarity with shared significant words | Fuzzy lead only |
| `no_candidate` | Nothing retained | Not an all-clear |

## Command and exit codes

```text
recall-match audit INVENTORY --recalls RECALLS [--json-out PATH] [--markdown-out PATH]
                   [--fail-on match|review|never] [--as-of YYYY-MM-DD]
                   [--max-data-age-days DAYS]
recall-match --version
```

- `--fail-on match` (default): exit `1` when any item has an identifier match.
- `--fail-on review`: exit `1` for either an identifier match or review candidate.
- `--fail-on never`: exit `0` after any successful audit.
- Invalid arguments or input return `2`. A finding exit (`1`) is not a crash.

## Verify from source

```bash
python -m pip install -e ".[dev]"
python -m ruff check .
python -m ruff format --check .
python -m mypy src
python -m pytest --cov=recall_match --cov-report=term-missing --cov-fail-under=90
python scripts/release_gate.py
```

The release gate repeats the quality checks, builds the wheel and source distribution once, installs the wheel into a clean virtual environment, and runs the bundled example through the installed command.

## If a command fails

| Symptom | Meaning | Fix |
| --- | --- | --- |
| `recall-match` is not recognized | The package or scripts directory is not active | Run `python -m recall_match ...` from a clone, or reinstall the wheel in the active environment |
| `missing required columns` | Inventory headers are incomplete | Add `item_id,name`; keep optional headers spelled as shown above |
| `invalid JSON` or `top-level ... must be an array` | The recall download is not raw CPSC array JSON | Re-download/export JSON; do not wrap it in `{ "recalls": ... }` |
| Exit code `1` | The selected finding threshold was reached | Open the report, inspect the label, and confirm against the source URL; use `--fail-on never` only when findings should not fail automation |
| `Recall data may be stale` | Latest dated record is older than the configured limit | Obtain a newer official export or set a deliberate `--max-data-age-days` value |
| Release gate stops at a named command | That named gate failed | Run the printed command alone, fix the first error, then rerun `python scripts/release_gate.py` |

See the full [failure repair runbook](docs/repair.md) when the short table is not enough.

## Architecture

Loaders validate the two untrusted files, immutable domain objects cross into a pure matcher, and one report model feeds all renderers. Filesystem access and the clock stay at the CLI boundary. See [architecture](docs/architecture.md), [specification](docs/spec.md), and [ADR-0001](docs/decisions/0001-offline-zero-runtime-dependencies.md).

## Limits

- v0.1.0 supports inventory CSV and raw CPSC recall JSON only.
- It does not download data, scan receipts, perform OCR, monitor continuously, or cover food, drugs, vehicles, or non-U.S. agencies.
- Name similarity is intentionally conservative and may miss products or surface false leads.
- Input files are limited to 50 MiB each and one audit is limited to 5,000,000 inventory-to-recall comparisons. Split a large inventory into smaller files when needed.

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) for the development contract. Report vulnerabilities through [GitHub private vulnerability reporting](https://github.com/KanadeK/recall-match/security/advisories/new); see [SECURITY.md](SECURITY.md).

MIT licensed. CPSC is the source of the supported public recall schema; this project is not affiliated with or endorsed by CPSC.
