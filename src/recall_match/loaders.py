"""Boundary validation for inventory CSV and official CPSC JSON files."""

import csv
import io
import json
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import Any

from recall_match.models import InventoryItem, Recall

MAX_INPUT_BYTES = 50 * 1024 * 1024


class InputError(ValueError):
    """An input file cannot be safely interpreted by Recall Match."""


def _read_text(path: Path) -> str:
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise InputError(f"{path}: input exceeds the 50 MiB limit")
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as error:
        raise InputError(f"{path}: expected UTF-8 text") from error


def load_inventory(path: Path) -> list[InventoryItem]:
    """Load and validate the user-owned product inventory CSV."""
    reader = csv.DictReader(io.StringIO(_read_text(path)))
    if reader.fieldnames is None:
        raise InputError(f"{path}: inventory CSV has no header")
    reader.fieldnames = [field.strip() for field in reader.fieldnames]
    missing = sorted({"item_id", "name"} - set(reader.fieldnames))
    if missing:
        raise InputError(f"{path}: missing required columns: {', '.join(missing)}")

    items: list[InventoryItem] = []
    seen_ids: set[str] = set()
    for row_number, row in enumerate(reader, start=2):
        item_id = (row.get("item_id") or "").strip()
        name = (row.get("name") or "").strip()
        if not item_id or not name:
            raise InputError(f"{path}:{row_number}: item_id and name must not be blank")
        if item_id in seen_ids:
            raise InputError(f"{path}:{row_number}: duplicate item_id '{item_id}'")
        seen_ids.add(item_id)
        items.append(
            InventoryItem(
                item_id=item_id,
                name=name,
                brand=(row.get("brand") or "").strip(),
                model=(row.get("model") or "").strip(),
                upc=(row.get("upc") or "").strip(),
            )
        )
    return items


def _nested_values(
    record: Mapping[str, Any], collection_name: str, field_name: str, row_number: int
) -> tuple[str, ...]:
    collection = record.get(collection_name) or []
    if not isinstance(collection, list):
        raise InputError(f"recall {row_number}: {collection_name} must be an array")
    values: list[str] = []
    for entry in collection:
        if not isinstance(entry, dict):
            raise InputError(f"recall {row_number}: {collection_name} entries must be objects")
        value = entry.get(field_name)
        if isinstance(value, str) and value.strip():
            values.append(value.strip())
    return tuple(values)


def _required_text(record: Mapping[str, Any], field: str, row_number: int) -> str:
    value = record.get(field)
    if not isinstance(value, str | int) or not str(value).strip():
        raise InputError(f"recall {row_number}: {field} is required")
    return str(value).strip()


def _optional_date(record: Mapping[str, Any], row_number: int) -> date | None:
    value = record.get("RecallDate")
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise InputError(f"recall {row_number}: RecallDate must be a string")
    try:
        return date.fromisoformat(value[:10])
    except ValueError as error:
        raise InputError(f"recall {row_number}: invalid RecallDate '{value}'") from error


def load_cpsc_recalls(path: Path) -> list[Recall]:
    """Load the raw JSON array returned by the official CPSC Recall API."""
    try:
        document = json.loads(_read_text(path))
    except json.JSONDecodeError as error:
        raise InputError(f"{path}:{error.lineno}: invalid JSON: {error.msg}") from error
    if not isinstance(document, list):
        raise InputError(f"{path}: top-level JSON value must be an array")

    recalls: list[Recall] = []
    for row_number, record in enumerate(document, start=1):
        if not isinstance(record, dict):
            raise InputError(f"recall {row_number}: entry must be an object")
        product_names = _nested_values(record, "Products", "Name", row_number)
        models = _nested_values(record, "Products", "Model", row_number)
        upcs = _nested_values(record, "ProductUPCs", "UPC", row_number)
        hazards = _nested_values(record, "Hazards", "Name", row_number)
        remedies = _nested_values(record, "Remedies", "Name", row_number)
        companies = sum(
            (
                _nested_values(record, collection, "Name", row_number)
                for collection in ("Manufacturers", "Importers", "Distributors")
            ),
            (),
        )
        captions = _nested_values(record, "Images", "Caption", row_number)
        title = _required_text(record, "Title", row_number)
        description_value = record.get("Description")
        description = description_value if isinstance(description_value, str) else ""
        searchable_parts = (title, description, *product_names, *models, *companies, *captions)

        recalls.append(
            Recall(
                recall_id=_required_text(record, "RecallID", row_number),
                title=title,
                url=_required_text(record, "URL", row_number),
                recall_date=_optional_date(record, row_number),
                product_names=product_names,
                models=models,
                upcs=upcs,
                hazard="; ".join(hazards),
                remedy="; ".join(remedies),
                searchable_text=" ".join(part for part in searchable_parts if part),
            )
        )
    return recalls
