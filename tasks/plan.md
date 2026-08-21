# Implementation plan: Recall Match v0.1.0

## Overview

Build the smallest complete offline path first: validated input -> deterministic evidence tiers -> terminal/JSON/Markdown reports -> packaged CLI. The highest-risk behavior is false confidence, so match-tier and negative-control tests precede implementation.

## Architecture decisions

- Loaders own untrusted-data validation and return immutable domain models.
- The matcher is pure and cannot access the filesystem, clock, or network.
- Report renderers consume one versioned report model.
- Runtime has no third-party packages; development tools are locked.

## Phase 1: Foundation

- [ ] Task 1: Add packaging metadata, package skeleton, and CLI contract.
- [ ] Task 2: Write failing loader/model tests and implement bounded inventory plus recall loaders.

### Checkpoint: Foundation

- [ ] Inputs validate on Windows and malformed fixtures fail closed.
- [ ] Lint, type check, and focused tests pass.

## Phase 2: Matching vertical slice

- [ ] Task 3: Write failing tier/false-positive tests and implement normalization plus deterministic matching.
- [ ] Task 4: Write failing report tests and implement provenance, freshness, JSON, Markdown, and text output.
- [ ] Task 5: Wire the CLI and verify all exit-code modes end to end.

### Checkpoint: Core flow

- [ ] Example produces identifier, review, and no-candidate outcomes.
- [ ] Full tests and 90% line/branch coverage pass.

## Phase 3: Delivery

- [ ] Task 6: Add examples, README, security policy, contributing guide, and failure-repair runbook.
- [ ] Task 7: Add wheel/sdist packaging, release gate, and clean-install smoke.
- [ ] Task 8: Add CI/release workflows and Dependabot.

### Checkpoint: Release ready

- [ ] Independent correctness/security review has no unresolved required findings.
- [ ] Local release gate passes from a clean Git checkout.
- [ ] Public repository, CI, tag, Release, assets, contributor history, and Gmail notification are verified.

## Risks and mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Fuzzy match creates false confidence | High | Fuzzy evidence can only be `review_candidate`; reports repeat the confirmation warning. |
| Official fields are sparse or inconsistent | High | Search descriptive fields only with explicit reason labels; keep raw provenance and source links. |
| Huge/malicious input exhausts resources | Medium | File, record, field, and candidate limits; no decompression, URL fetching, templating, or execution. |
| Report ordering changes across platforms | Medium | NFKC/casefold comparison keys and explicit total ordering. |

## Open questions

None for v0.1.0.
