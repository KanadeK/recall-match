import json
from datetime import date
from pathlib import Path

from recall_match.matching import match_inventory
from recall_match.models import InventoryItem, Recall
from recall_match.reporting import build_report, render_json, render_markdown, render_text


def make_recall(**overrides):
    values = {
        "recall_id": "10461",
        "title": "Acme recalls high chairs",
        "url": "https://www.cpsc.gov/Recalls/2026/example",
        "recall_date": date(2026, 1, 1),
        "product_names": ("Acme High Chair",),
        "models": ("HC-200",),
        "upcs": ("012345678905",),
        "hazard": "Fall hazard",
        "remedy": "Stop use",
        "searchable_text": "Acme high chair HC-200",
    }
    values.update(overrides)
    return Recall(**values)


def test_report_has_versioned_provenance_summary_and_freshness_warning():
    recall = make_recall()
    items = [
        InventoryItem("chair", "High chair", upc="012345678905"),
        InventoryItem("lamp", "Desk lamp"),
    ]
    results = match_inventory(items, [recall])

    report = build_report(
        results,
        [recall],
        inventory_path=Path("inventory.csv"),
        recalls_path=Path("recalls.json"),
        as_of=date(2026, 3, 15),
        max_data_age_days=30,
    )
    payload = json.loads(render_json(report))

    assert payload["schema_version"] == "1"
    assert payload["tool_version"] == "0.1.0"
    assert payload["as_of"] == "2026-03-15"
    assert payload["inputs"]["inventory"] == {"path": "inventory.csv", "records": 2}
    assert payload["inputs"]["recalls"]["latest_recall_date"] == "2026-01-01"
    assert payload["summary"] == {
        "items_with_identifier_match": 1,
        "items_with_review_candidate": 0,
        "items_without_candidates": 1,
    }
    assert "73 days old" in payload["warnings"][0]
    assert payload["results"][0]["candidates"][0]["source_url"].startswith("https://")

    markdown = render_markdown(report)
    assert "[Acme recalls high chairs](https://www.cpsc.gov/Recalls/2026/example)" in markdown
    assert "No candidate found. This is not proof" in markdown


def test_markdown_escapes_external_text_and_does_not_link_non_http_urls():
    recall = make_recall(
        title="Acme | <chair>",
        url="javascript:alert(1)",
        hazard="Fall | trap",
    )
    item = InventoryItem("chair", "Chair | <deluxe>\nline", upc="012345678905")
    report = build_report(
        match_inventory([item], [recall]),
        [recall],
        inventory_path=Path("inventory.csv"),
        recalls_path=Path("recalls.json"),
        as_of=date(2026, 1, 2),
        max_data_age_days=30,
    )

    markdown = render_markdown(report)

    assert "Chair \\| &lt;deluxe&gt; line" in markdown
    assert "Fall \\| trap" in markdown
    assert "javascript:" not in markdown
    assert "No candidate found" not in markdown


def test_text_report_is_a_concise_summary():
    recall = make_recall()
    report = build_report(
        match_inventory([InventoryItem("chair", "High chair", upc="012345678905")], [recall]),
        [recall],
        inventory_path=Path("inventory.csv"),
        recalls_path=Path("recalls.json"),
        as_of=date(2026, 1, 2),
        max_data_age_days=30,
    )

    assert render_text(report).splitlines()[0] == (
        "Recall Match: 1 item; 1 identifier match; 0 review candidates; 0 without candidates."
    )
