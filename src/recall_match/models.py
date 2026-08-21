"""Typed domain objects shared by loaders, matching, and reports."""

from dataclasses import dataclass
from datetime import date
from typing import Literal


@dataclass(frozen=True)
class InventoryItem:
    item_id: str
    name: str
    brand: str = ""
    model: str = ""
    upc: str = ""


@dataclass(frozen=True)
class Recall:
    recall_id: str
    title: str
    url: str
    recall_date: date | None
    product_names: tuple[str, ...]
    models: tuple[str, ...]
    upcs: tuple[str, ...]
    hazard: str
    remedy: str
    searchable_text: str


@dataclass(frozen=True)
class Candidate:
    recall: Recall
    tier: Literal["identifier_match", "review_candidate"]
    score: int
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ItemResult:
    item: InventoryItem
    candidates: tuple[Candidate, ...]
