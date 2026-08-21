"""Conservative, explainable product-to-recall matching."""

import re
import unicodedata
from collections.abc import Iterable
from difflib import SequenceMatcher

from recall_match.models import Candidate, InventoryItem, ItemResult, Recall


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(re.findall(r"[\w]+", normalized, flags=re.UNICODE))


def normalize_code(value: str) -> str:
    return "".join(character for character in normalize_text(value) if character.isalnum())


def normalize_upc(value: str) -> str:
    return "".join(character for character in value if character.isdigit())


def _contains_token_sequence(text: str, phrase: str) -> bool:
    text_tokens = normalize_text(text).split()
    phrase_tokens = normalize_text(phrase).split()
    if not phrase_tokens:
        return False
    width = len(phrase_tokens)
    return any(
        text_tokens[index : index + width] == phrase_tokens for index in range(len(text_tokens))
    )


def _name_similarity(item_name: str, recall: Recall) -> float:
    item_key = normalize_text(item_name)
    names = (*recall.product_names, recall.title)
    return max(
        (SequenceMatcher(None, item_key, normalize_text(name)).ratio() for name in names),
        default=0.0,
    )


def _shared_significant_tokens(left: str, right: str) -> int:
    left_tokens = {token for token in normalize_text(left).split() if len(token) >= 3}
    right_tokens = {token for token in normalize_text(right).split() if len(token) >= 3}
    return len(left_tokens & right_tokens)


def _candidate(item: InventoryItem, recall: Recall) -> Candidate | None:
    item_upc = normalize_upc(item.upc)
    recall_upcs = {normalize_upc(upc) for upc in recall.upcs}
    if item_upc and item_upc in recall_upcs:
        return Candidate(recall, "identifier_match", 100, (f"exact UPC {item_upc}",))

    model_matches = bool(item.model) and (
        normalize_code(item.model) in {normalize_code(model) for model in recall.models}
        or _contains_token_sequence(recall.searchable_text, item.model)
    )
    brand_present = bool(item.brand) and _contains_token_sequence(
        recall.searchable_text, item.brand
    )
    if model_matches and brand_present:
        return Candidate(
            recall,
            "identifier_match",
            96,
            (f"exact model {item.model.upper()}", f"brand {item.brand.title()} present"),
        )
    if model_matches:
        suffix = "brand not confirmed" if item.brand else "no brand provided"
        return Candidate(
            recall,
            "review_candidate",
            88,
            (f"exact model {item.model}; {suffix}",),
        )

    similarity = _name_similarity(item.name, recall)
    closest_name = max(
        (*recall.product_names, recall.title),
        key=lambda name: SequenceMatcher(
            None, normalize_text(item.name), normalize_text(name)
        ).ratio(),
    )
    if brand_present and similarity >= 0.55:
        return Candidate(
            recall,
            "review_candidate",
            min(79, round(60 + similarity * 20)),
            (f"brand {item.brand} present", f"product name similarity {similarity:.2f}"),
        )
    if similarity >= 0.72 and _shared_significant_tokens(item.name, closest_name) >= 2:
        return Candidate(
            recall,
            "review_candidate",
            min(69, round(50 + similarity * 20)),
            (f"product name similarity {similarity:.2f}",),
        )
    return None


def match_inventory(items: Iterable[InventoryItem], recalls: Iterable[Recall]) -> list[ItemResult]:
    """Return deterministic candidate lists for each inventory item."""
    recall_list = list(recalls)
    results: list[ItemResult] = []
    for item in items:
        candidates = [
            candidate
            for recall in recall_list
            if (candidate := _candidate(item, recall)) is not None
        ]
        candidates.sort(
            key=lambda candidate: (
                -candidate.score,
                -(candidate.recall.recall_date.toordinal() if candidate.recall.recall_date else 0),
                candidate.recall.recall_id,
            )
        )
        results.append(ItemResult(item, tuple(candidates)))
    return results
