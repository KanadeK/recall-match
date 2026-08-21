Recall Match v0.1.0 is the first public release of an offline, explainable owned-product recall matcher.

### Highlights

- Reads a simple inventory CSV and raw CPSC recall JSON without network access.
- Separates exact UPC or brand/model evidence from fuzzy review candidates.
- Generates terminal, versioned JSON, and escaped Markdown reports.
- Preserves source URLs, hazards, remedies, scores, and human-readable reasons.
- Provides stable exit codes for scheduled checks and CI.
- Ships with a synthetic CPSC-shaped example, 90%+ test coverage, and a clean-wheel smoke gate.

### Safety boundary

Recall Match is a screening aid, not a safety certification. A missing candidate does not prove that a product is safe or not recalled. Confirm candidates against the official source notice and the label on the product.

### Try the release

Download the wheel asset, then:

```bash
python -m pip install recall_match-0.1.0-py3-none-any.whl
recall-match --version
```

The README contains the runnable example and complete acceptance commands.

