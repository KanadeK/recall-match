"""Command-line interface for offline recall matching."""

import argparse
import sys
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from recall_match import __version__
from recall_match.loaders import InputError, load_cpsc_recalls, load_inventory
from recall_match.matching import match_inventory
from recall_match.reporting import (
    build_report,
    render_json,
    render_markdown,
    render_text,
    write_text_atomic,
)


def _iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("expected YYYY-MM-DD") from error


def _nonnegative_integer(value: str) -> int:
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return number


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="recall-match",
        description="Match an owned-product inventory against local CPSC recall data.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)
    audit = subparsers.add_parser("audit", help="audit an inventory CSV")
    audit.add_argument("inventory", type=Path)
    audit.add_argument("--recalls", type=Path, required=True)
    audit.add_argument("--json-out", type=Path)
    audit.add_argument("--markdown-out", type=Path)
    audit.add_argument("--fail-on", choices=("match", "review", "never"), default="match")
    audit.add_argument("--as-of", type=_iso_date, default=date.today())
    audit.add_argument("--max-data-age-days", type=_nonnegative_integer, default=30)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        inventory = load_inventory(args.inventory)
        recalls = load_cpsc_recalls(args.recalls)
        report = build_report(
            match_inventory(inventory, recalls),
            recalls,
            inventory_path=args.inventory,
            recalls_path=args.recalls,
            as_of=args.as_of,
            max_data_age_days=args.max_data_age_days,
        )
        if args.json_out:
            write_text_atomic(args.json_out, render_json(report))
        if args.markdown_out:
            write_text_atomic(args.markdown_out, render_markdown(report))
    except (InputError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(render_text(report), end="")
    if args.fail_on == "match":
        return int(report.summary.items_with_identifier_match > 0)
    if args.fail_on == "review":
        return int(
            report.summary.items_with_identifier_match > 0
            or report.summary.items_with_review_candidate > 0
        )
    return 0
