from datetime import date
from pathlib import Path

from recall_match.loaders import load_cpsc_recalls, load_inventory
from recall_match.matching import match_inventory
from recall_match.reporting import build_report


def test_bundled_example_covers_all_user_visible_outcomes():
    project_root = Path(__file__).parents[1]
    inventory_path = project_root / "examples" / "inventory.csv"
    recalls_path = project_root / "examples" / "cpsc-recalls.json"
    inventory = load_inventory(inventory_path)
    recalls = load_cpsc_recalls(recalls_path)

    report = build_report(
        match_inventory(inventory, recalls),
        recalls,
        inventory_path=inventory_path,
        recalls_path=recalls_path,
        as_of=date(2026, 8, 21),
        max_data_age_days=30,
    )

    assert report.summary.items_with_identifier_match == 1
    assert report.summary.items_with_review_candidate == 1
    assert report.summary.items_without_candidates == 1
    assert report.warnings == ()
