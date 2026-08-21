from datetime import date

from recall_match.matching import match_inventory
from recall_match.models import InventoryItem, Recall


def recall(**overrides):
    values = {
        "recall_id": "100",
        "title": "Acme recalls folding high chairs",
        "url": "https://www.cpsc.gov/Recalls/2026/example",
        "recall_date": date(2026, 1, 2),
        "product_names": ("Acme Folding High Chair",),
        "models": ("HC-200",),
        "upcs": ("012345678905",),
        "hazard": "Fall hazard",
        "remedy": "Stop use",
        "searchable_text": "Acme folding high chair model HC-200",
    }
    values.update(overrides)
    return Recall(**values)


def test_exact_upc_is_an_identifier_match():
    item = InventoryItem("chair", "High chair", upc="0 12345 67890 5")

    result = match_inventory([item], [recall()])[0]

    assert result.candidates[0].tier == "identifier_match"
    assert result.candidates[0].score == 100
    assert result.candidates[0].reasons == ("exact UPC 012345678905",)


def test_exact_model_and_brand_is_an_identifier_match():
    item = InventoryItem("chair", "High chair", brand="ACME", model="hc 200")

    candidate = match_inventory([item], [recall(upcs=())])[0].candidates[0]

    assert candidate.tier == "identifier_match"
    assert candidate.score == 96
    assert "exact model HC 200" in candidate.reasons
    assert "brand Acme present" in candidate.reasons


def test_model_without_brand_agreement_requires_review():
    item = InventoryItem("chair", "High chair", brand="Other", model="HC-200")

    candidate = match_inventory([item], [recall(upcs=())])[0].candidates[0]

    assert candidate.tier == "review_candidate"
    assert candidate.score == 88
    assert candidate.reasons == ("exact model HC-200; brand not confirmed",)


def test_similar_product_name_with_brand_requires_review():
    item = InventoryItem("chair", "Folding high chair", brand="Acme")

    candidate = match_inventory([item], [recall(models=(), upcs=())])[0].candidates[0]

    assert candidate.tier == "review_candidate"
    assert candidate.score <= 79
    assert any("product name similarity" in reason for reason in candidate.reasons)


def test_similar_name_never_becomes_identifier_match():
    item = InventoryItem("chair", "Acme folding high chairs")

    candidate = match_inventory([item], [recall(models=(), upcs=())])[0].candidates[0]

    assert candidate.tier == "review_candidate"
    assert candidate.score <= 69


def test_unrelated_product_has_no_candidates():
    item = InventoryItem("lamp", "Desk lamp", brand="BrightCo", model="L-9")

    result = match_inventory([item], [recall()])[0]

    assert result.candidates == ()


def test_short_generic_codes_never_create_identifier_matches():
    item = InventoryItem("light", "Desk light", brand="A", model="1", upc="1")
    generic = recall(
        title="A recalls model 1 desk lights",
        product_names=("Desk light",),
        models=("1",),
        upcs=("1",),
        searchable_text="A desk light model 1",
    )

    candidates = match_inventory([item], [generic])[0].candidates

    assert all(candidate.tier != "identifier_match" for candidate in candidates)


def test_candidates_have_stable_score_then_date_order():
    item = InventoryItem("chair", "High chair", brand="Acme", model="HC-200")
    older = recall(recall_id="older", recall_date=date(2025, 1, 1), upcs=())
    newer = recall(recall_id="newer", recall_date=date(2026, 1, 1), upcs=())

    candidates = match_inventory([item], [older, newer])[0].candidates

    assert [candidate.recall.recall_id for candidate in candidates] == ["newer", "older"]
