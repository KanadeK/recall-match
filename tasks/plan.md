# Implementation plan: Recall Match v0.1.0

## Overview

Build the smallest complete offline path first: validated input -> deterministic evidence tiers -> terminal/JSON/Markdown reports -> packaged CLI. The highest-risk behavior is false confidence, so match-tier and negative-control tests precede implementation.

## Architecture decisions

- Loaders own untrusted-data validation and return immutable domain models.
- The matcher is pure and cannot access the filesystem, clock, or network.
- Report renderers consume one versioned report model.
- Runtime has no third-party packages; development tools are locked.

## Phase 1: Foundation

- [x] Task 1: Add packaging metadata, package skeleton, and CLI contract.
- [x] Task 2: Write failing loader/model tests and implement bounded inventory plus recall loaders.

### Checkpoint: Foundation

- [x] Inputs validate on Windows and malformed fixtures fail closed.
- [x] Lint, type check, and focused tests pass.

## Phase 2: Matching vertical slice

- [x] Task 3: Write failing tier/false-positive tests and implement normalization plus deterministic matching.
- [x] Task 4: Write failing report tests and implement provenance, freshness, JSON, Markdown, and text output.
- [x] Task 5: Wire the CLI and verify all exit-code modes end to end.

### Checkpoint: Core flow

- [x] Example produces identifier, review, and no-candidate outcomes.
- [x] Full tests and 90% line/branch coverage pass.

## Phase 3: Delivery

- [x] Task 6: Add examples, README, security policy, contributing guide, and failure-repair runbook.
- [x] Task 7: Add wheel/sdist packaging, release gate, and clean-install smoke.
- [x] Task 8: Add a focused GitHub Actions CI workflow.

### Checkpoint: Release ready

- [x] Dedicated correctness/security review has no unresolved required findings.
- [x] Local release gate passes from the release candidate checkout.
- [x] Public repository, CI, tag, Release, assets, contributor history, and Gmail notification are verified.

## Risks and mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Fuzzy match creates false confidence | High | Fuzzy evidence can only be `review_candidate`; reports repeat the confirmation warning. |
| Official fields are sparse or inconsistent | High | Search descriptive fields only with explicit reason labels; keep raw provenance and source links. |
| Huge/malicious input exhausts resources | Medium | A 50 MiB cap per file; no decompression, URL fetching, templating, or execution. |
| Report ordering changes across platforms | Medium | NFKC/casefold comparison keys and explicit total ordering. |

## Open questions

None for v0.1.0.
