# Recall Match

## Problem statement

How might households, repair shops, schools, libraries, and small resellers compare the products they already own against official recall data without uploading an inventory or trusting an opaque matching API?

## Recommended direction

Build a zero-runtime-dependency Python CLI that accepts an inventory CSV and a locally downloaded CPSC recall JSON dataset. It produces transparent, review-oriented matches with the exact fields that caused each candidate: UPC, model, brand, and product-name similarity. Strong identifier evidence is separated from fuzzy review candidates.

The useful product is the evidence trail, not a search box. A user can keep a simple inventory, periodically download official data, rerun one command, archive the JSON/Markdown report, and see which product labels to inspect. The CLI never claims that an unmatched item is safe and never replaces confirmation on the official recall page.

## Key assumptions to validate

- [x] Official machine-readable data exists. CPSC publishes recall data in JSON/XML and encourages third-party applications.
- [x] The local workspace has no owned-product recall matcher. The closest projects address maintenance manuals or product-passport readiness, not recall matching.
- [x] Current commercial services expose catalog/CSV recall matching, which validates demand, while research found no clear zero-dependency offline open-source CLI with explainable evidence tiers.
- [ ] Users will maintain enough identifiers (especially UPC/model) for high-confidence matches. The example and documentation must make identifier capture easy.
- [ ] Other jurisdictions will provide stable exports. The first release deliberately supports only CPSC JSON instead of promising generic multi-agency coverage.

## MVP scope

- Inventory CSV loader.
- Raw CPSC JSON loader.
- Exact UPC and brand-plus-model matching.
- Conservative model-only and product-name review candidates.
- Text summary plus JSON and Markdown evidence reports.
- Source freshness warnings, deterministic ordering, bounded input size, and stable exit codes.
- Real fixtures, negative/corrupt fixtures, CI, wheel/sdist, and a release repair runbook.

## Not doing (and why)

- Live API synchronization in v0.1.0 — offline inputs make runs reproducible and avoid silently trusting a changing service.
- A web dashboard — the core value is automation and auditable matching, not another interface shell.
- OCR or receipt scanning — identifier extraction is a separate product and would weaken a focused first release.
- Food, drug, vehicle, or international presets — each source has different semantics and needs source-specific validation before support is claimed.
- Safety certification or legal advice — recall records change and fuzzy matching can be wrong; every candidate links back to its source.
- Notifications or cloud accounts — users can schedule the CLI with their existing automation.
