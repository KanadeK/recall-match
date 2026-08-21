# Opportunity research

Research date: 2026-08-12 (America/Los_Angeles)

## Decision

Build **Recall Match**, an offline owned-product-to-recall evidence matcher.

The selection followed a read-only inventory of roughly 131 local project directories plus web, GitHub, official-source, and community research. Star potential is not guaranteed; the product is optimized for discoverability through a crisp safety-related problem, a one-command demo, no account, no runtime dependencies, and reports that are useful in CI or by hand.

## Why this is a defensible gap

- The U.S. Consumer Product Safety Commission publishes decades of recall data through a public REST API in JSON or XML and explicitly encourages developers to build applications from it.
- The raw data includes fields such as recall IDs, dates, product descriptions, product models, UPCs, hazards, remedies, manufacturers, and source URLs.
- Current search results surfaced commercial matching APIs and mobile/web trackers. Their existence validates catalog-screening demand, but they require a service and do not provide this project's offline, inspectable evidence contract.
- Exact identifiers are often sparse. That creates a real technical need for a conservative ladder: exact UPC, brand plus exact model, model-only review, then explainable name similarity.

Official sources:

- CPSC Recall API information: https://www.cpsc.gov/Recalls/CPSC-Recalls-Application-Program-Interface-API-Information
- CPSC API programmer guide: https://www.cpsc.gov/s3fs-public/RecallRetrievalWebServicesProgrammersGuide20180917.pdf
- CPSC public data overview: https://www.cpsc.gov/Data
- Live JSON endpoint example: https://www.saferproducts.gov/RestWebServices/Recall?ProductName=Toddler&format=json

## Ideas rejected after overlap/competition checks

### Generic backup restore validator

Rejected despite strong community demand. It overlaps the local `export-checkup`, `exitpreflight`, `exitlint`, and `archive-parallax` family, plus adjacent `ShipReceipt` and `path-passport`. Building it would be recombination, not a new project.

### AI-agent diff guard

Rejected as crowded. Research found multiple near-exact policy/diff gates covering scope, secrets, workflows, dependency changes, and missing test evidence.

### Cross-platform path portability linter

Rejected. The workspace already contains `path-passport`, and GitHub has filename validators, case-conflict tools, normalization tools, and recent repository portability auditors.

### ISP outage evidence compiler

Rejected after finding current products and an open-source project that already combine monitoring, outage evidence, and complaint/PDF generation.

### Warranty/return docket

Rejected as newly crowded: several offline apps and a mature self-hosted open-source warranty tracker already cover receipts, serials, expirations, claims, and exports.

## Research limitations

- GitHub authenticated repository search hit its rate limit late in the research session. Earlier GitHub results, web indexes, official sources, community results, and the exhaustive local inventory were still sufficient to reject the crowded concepts and select the final direction.
- "No one has built this" cannot be proven over all public and private software. The defensible claim is narrower: no direct, mature open-source match was found for the exact offline, zero-runtime-dependency, evidence-tiered CLI defined here.
