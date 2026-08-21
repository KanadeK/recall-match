# Security policy

## Supported version

Security fixes are provided for the latest published release.

## Reporting a vulnerability

Use [GitHub private vulnerability reporting](https://github.com/KanadeK/recall-match/security/advisories/new). Include the affected version, reproduction steps, impact, and the smallest useful sample input. Do not open a public issue for an undisclosed vulnerability or include real household inventory in a report.

## Security boundaries

Recall Match reads local UTF-8 CSV/JSON files up to 50 MiB. It does not execute input, fetch source URLs, open browsers, upload inventories, or use templates. Markdown escapes external text and links only validated HTTP(S) URLs. Output destinations remain under the user's control.

Matching output is not a safety certification. Users must verify candidates and product labels against the official source notice.

