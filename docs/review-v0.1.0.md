# v0.1.0 release review

Review date: 2026-08-21

## Scope and trust model

Reviewed the complete v0.1.0 source, tests, examples, packaging, release gate, and CI workflow against the specification.

Trust boundaries:

- Inventory CSV and CPSC JSON are untrusted local files.
- Output paths are user-controlled filesystem destinations.
- Recall URLs and all report text are untrusted data; the program never fetches them.
- Build tools and GitHub Actions are development/release dependencies; the installed CLI has no third-party runtime dependency.

Assets at risk are the user's input files and inventory privacy, the integrity of candidate tiers and reports, and local CPU/disk availability.

## Required findings and resolution

| Finding | Risk | Resolution | Regression evidence |
| --- | --- | --- | --- |
| Outputs could replace an input or each other | Source-file loss or silently missing report | Resolve paths before loading; reject collisions with exit `2` | `test_outputs_cannot_replace_inputs_or_each_other` |
| Markdown special characters could change report structure | Misleading rendered evidence | Escape Markdown and HTML-controlled text; link only valid HTTP(S) URLs | `test_markdown_escapes_external_text_and_does_not_link_non_http_urls` |
| File-size limits did not bound matching work | Local denial of service | Reject audits above 5,000,000 item-to-recall comparisons | `test_audit_rejects_excessive_comparison_work` |

No critical finding remains.

## Five-axis result

- Correctness: public exit codes, input mappings, evidence tiers, ordering, reports, examples, and installed entry point are covered and pass.
- Readability: modules have one responsibility; no speculative adapters, UI, network client, or runtime dependency was added.
- Architecture: filesystem/clock access stays at the CLI/report boundary and matching remains deterministic pure logic.
- Security: inputs are size/schema bounded, workload and destination collisions are blocked, external text is escaped, source URLs are never fetched, and a targeted committed-file secret scan had no match.
- Performance: matching remains O(inventory × recalls), now with a 5,000,000-comparison ceiling. Large legitimate inventories must be split deliberately.

## Verification evidence

`python scripts/release_gate.py` passed on Windows with Python 3.12.10:

- Ruff check and format check: passed.
- Mypy strict check: passed.
- Pytest: 23 passed.
- Line/branch coverage: 91.35% (90% required).
- Build: `recall_match-0.1.0-py3-none-any.whl` and `recall_match-0.1.0.tar.gz`.
- Clean wheel install: `recall-match 0.1.0` and the three-outcome example passed.

## Residual trade-offs

- Official records can omit identifiers; false negatives and fuzzy false leads remain possible, so reports never claim safety.
- Data freshness is visible but remains the user's responsibility because v0.1.0 intentionally has no network access.
- The comparison ceiling favors predictable local behavior over one-shot processing of very large inventories.

## Verdict

Approved for v0.1.0 publication once the same commit passes the public GitHub Actions Python 3.10 release gate. Rollback/withdrawal steps are in [release.md](release.md).

