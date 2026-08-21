# ADR-0001: Offline core with zero runtime dependencies

## Status

Accepted

## Date

2026-08-12

## Context

Recall Match processes potentially sensitive household inventory and safety-related public data. The first release needs to run from a clone, a wheel, or a single zipapp on common Python installations. Matching and parsing do not require a framework.

## Decision

Use Python 3.10+ and the standard library for all runtime behavior. All recall data is supplied as a local file. Network synchronization, OCR, and a web UI are outside v0.1.0.

The public interface is one audit CLI command and a versioned JSON report schema. Matching is a deterministic pure-logic layer behind validated dataclass inputs.

## Alternatives considered

### Hosted web application

- Pros: approachable interface and scheduled monitoring.
- Cons: uploads sensitive inventory, requires operations and accounts, and risks becoming an interface shell.
- Rejected: conflicts with the privacy and reproducibility goals.

### Third-party fuzzy matching library

- Pros: faster and potentially richer similarity metrics.
- Cons: supply-chain and packaging cost for a small, explainable matching ladder.
- Rejected: the standard library is sufficient for conservative review candidates.

### Live CPSC client in the core command

- Pros: freshest data with one command.
- Cons: non-reproducible runs, network failures, and an external-response trust boundary mixed into matching.
- Rejected for v0.1.0: users download official data separately, and reports hash the exact input.

## Consequences

- Installation and release artifacts stay small and cross-platform.
- Offline audits are reproducible and private.
- Data freshness is visible but not automatically repaired.
- New agency integrations require an additive loader/preset and source-specific tests rather than a generic promise.
