"""Versioned JSON, Markdown, and terminal reports."""

import html
import json
import os
import re
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from recall_match import __version__
from recall_match.models import ItemResult, Recall

Status = Literal["identifier_match", "review_candidate", "no_candidate"]


@dataclass(frozen=True)
class Summary:
    items_with_identifier_match: int
    items_with_review_candidate: int
    items_without_candidates: int


@dataclass(frozen=True)
class AuditReport:
    as_of: date
    inventory_path: Path
    recalls_path: Path
    recall_count: int
    latest_recall_date: date | None
    summary: Summary
    warnings: tuple[str, ...]
    results: tuple[ItemResult, ...]


def _status(result: ItemResult) -> Status:
    if any(candidate.tier == "identifier_match" for candidate in result.candidates):
        return "identifier_match"
    if result.candidates:
        return "review_candidate"
    return "no_candidate"


def build_report(
    results: Iterable[ItemResult],
    recalls: Iterable[Recall],
    *,
    inventory_path: Path,
    recalls_path: Path,
    as_of: date,
    max_data_age_days: int,
) -> AuditReport:
    """Build a report without reading the clock or filesystem."""
    result_list = tuple(results)
    recall_list = tuple(recalls)
    statuses = tuple(_status(result) for result in result_list)
    dated_recalls = [recall.recall_date for recall in recall_list if recall.recall_date]
    latest_recall_date = max(dated_recalls, default=None)

    warnings: list[str] = []
    if latest_recall_date is None:
        warnings.append("Recall data has no dated records; freshness cannot be checked.")
    else:
        age_days = (as_of - latest_recall_date).days
        if age_days > max_data_age_days:
            warnings.append(
                f"Recall data may be stale: latest record is {age_days} days old "
                f"(limit {max_data_age_days})."
            )

    return AuditReport(
        as_of=as_of,
        inventory_path=inventory_path,
        recalls_path=recalls_path,
        recall_count=len(recall_list),
        latest_recall_date=latest_recall_date,
        summary=Summary(
            items_with_identifier_match=statuses.count("identifier_match"),
            items_with_review_candidate=statuses.count("review_candidate"),
            items_without_candidates=statuses.count("no_candidate"),
        ),
        warnings=tuple(warnings),
        results=result_list,
    )


def _as_dict(report: AuditReport) -> dict[str, object]:
    return {
        "schema_version": "1",
        "tool_version": __version__,
        "as_of": report.as_of.isoformat(),
        "inputs": {
            "inventory": {
                "path": str(report.inventory_path),
                "records": len(report.results),
            },
            "recalls": {
                "path": str(report.recalls_path),
                "records": report.recall_count,
                "latest_recall_date": (
                    report.latest_recall_date.isoformat() if report.latest_recall_date else None
                ),
            },
        },
        "summary": {
            "items_with_identifier_match": report.summary.items_with_identifier_match,
            "items_with_review_candidate": report.summary.items_with_review_candidate,
            "items_without_candidates": report.summary.items_without_candidates,
        },
        "warnings": list(report.warnings),
        "results": [
            {
                "item": {
                    "item_id": result.item.item_id,
                    "name": result.item.name,
                    "brand": result.item.brand,
                    "model": result.item.model,
                    "upc": result.item.upc,
                },
                "status": _status(result),
                "candidates": [
                    {
                        "tier": candidate.tier,
                        "score": candidate.score,
                        "reasons": list(candidate.reasons),
                        "recall_id": candidate.recall.recall_id,
                        "title": candidate.recall.title,
                        "recall_date": (
                            candidate.recall.recall_date.isoformat()
                            if candidate.recall.recall_date
                            else None
                        ),
                        "source_url": candidate.recall.url,
                        "hazard": candidate.recall.hazard,
                        "remedy": candidate.recall.remedy,
                    }
                    for candidate in result.candidates
                ],
            }
            for result in report.results
        ],
    }


def render_json(report: AuditReport) -> str:
    return json.dumps(_as_dict(report), ensure_ascii=False, indent=2) + "\n"


def _markdown_text(value: str) -> str:
    escaped_html = html.escape(value.replace("\r", " ").replace("\n", " "))
    return re.sub(r"([\\`*{}\[\]()#+\-.!_|>])", r"\\\1", escaped_html)


def _http_url(value: str) -> str | None:
    parsed = urlsplit(value)
    if (
        parsed.scheme in {"http", "https"}
        and parsed.netloc
        and not any(character.isspace() for character in value)
    ):
        return value.replace("(", "%28").replace(")", "%29")
    return None


def render_markdown(report: AuditReport) -> str:
    summary = report.summary
    lines = [
        "# Recall Match report",
        "",
        f"Audit date: `{report.as_of.isoformat()}`",
        "",
        "> Candidate screening only. A missing candidate is not proof that a product is safe.",
        "",
        "## Summary",
        "",
        "| Identifier matches | Review candidates | Without candidates |",
        "| ---: | ---: | ---: |",
        (
            f"| {summary.items_with_identifier_match} | "
            f"{summary.items_with_review_candidate} | {summary.items_without_candidates} |"
        ),
    ]
    if report.warnings:
        lines.extend(("", "## Warnings", ""))
        lines.extend(f"- {_markdown_text(warning)}" for warning in report.warnings)

    lines.extend(("", "## Results", ""))
    for result in report.results:
        lines.extend(
            (
                f"### {_markdown_text(result.item.name)} "
                f"(item ID: {_markdown_text(result.item.item_id)})",
                "",
                f"Status: `{_status(result)}`",
                "",
            )
        )
        if not result.candidates:
            lines.extend(
                (
                    "No candidate found. This is not proof that the product is safe "
                    "or not recalled.",
                    "",
                )
            )
            continue

        lines.extend(
            (
                "| Tier | Score | Recall | Why | Hazard | Remedy |",
                "| --- | ---: | --- | --- | --- | --- |",
            )
        )
        for candidate in result.candidates:
            title = _markdown_text(candidate.recall.title)
            url = _http_url(candidate.recall.url)
            recall_label = f"[{title}]({url})" if url else title
            lines.append(
                f"| `{candidate.tier}` | {candidate.score} | {recall_label} | "
                f"{_markdown_text('; '.join(candidate.reasons))} | "
                f"{_markdown_text(candidate.recall.hazard)} | "
                f"{_markdown_text(candidate.recall.remedy)} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _count_phrase(count: int, singular: str, plural: str | None = None) -> str:
    return f"{count} {singular if count == 1 else plural or singular + 's'}"


def render_text(report: AuditReport) -> str:
    summary = report.summary
    first_line = "; ".join(
        (
            _count_phrase(len(report.results), "item"),
            _count_phrase(summary.items_with_identifier_match, "identifier match"),
            _count_phrase(summary.items_with_review_candidate, "review candidate"),
            _count_phrase(
                summary.items_without_candidates, "without candidates", "without candidates"
            ),
        )
    )
    lines = [f"Recall Match: {first_line}."]
    lines.extend(f"Warning: {warning}" for warning in report.warnings)
    return "\n".join(lines) + "\n"


def write_text_atomic(path: Path, content: str) -> None:
    """Replace one report only after its full content has been written."""
    file_descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8", newline="\n") as temporary_file:
            temporary_file.write(content)
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)
