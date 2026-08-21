import json

import pytest

from recall_match.loaders import InputError, load_cpsc_recalls, load_inventory


def test_load_inventory_reads_required_and_optional_columns(tmp_path):
    inventory = tmp_path / "inventory.csv"
    inventory.write_text(
        "item_id,name,brand,model,upc\nchair-1,Convertible High Chair,Harppa,BHC001,012345678905\n",
        encoding="utf-8",
    )

    items = load_inventory(inventory)

    assert len(items) == 1
    assert items[0].item_id == "chair-1"
    assert items[0].model == "BHC001"
    assert items[0].upc == "012345678905"


def test_load_inventory_rejects_duplicate_item_ids(tmp_path):
    inventory = tmp_path / "inventory.csv"
    inventory.write_text(
        "item_id,name\nitem-1,First product\nitem-1,Second product\n",
        encoding="utf-8",
    )

    with pytest.raises(InputError, match="duplicate item_id 'item-1'"):
        load_inventory(inventory)


def test_load_inventory_rejects_missing_required_header(tmp_path):
    inventory = tmp_path / "inventory.csv"
    inventory.write_text("item_id,brand\nitem-1,Acme\n", encoding="utf-8")

    with pytest.raises(InputError, match="missing required columns: name"):
        load_inventory(inventory)


def test_load_cpsc_recalls_maps_nested_official_fields(tmp_path):
    recalls_file = tmp_path / "recalls.json"
    recalls_file.write_text(
        json.dumps(
            [
                {
                    "RecallID": 10461,
                    "RecallNumber": "26061",
                    "RecallDate": "2025-10-30T00:00:00",
                    "Title": "Harppa recalls convertible high chairs",
                    "Description": "Only model BHC001 from batch 202408 is included.",
                    "URL": "https://www.cpsc.gov/Recalls/2026/example",
                    "Products": [
                        {
                            "Name": "Harppa 5-in-1 Convertible High Chair",
                            "Model": "BHC001",
                        }
                    ],
                    "ProductUPCs": [{"UPC": "012345678905"}],
                    "Hazards": [{"Name": "Fall and entrapment hazard"}],
                    "Remedies": [{"Name": "Stop use and request a replacement"}],
                    "Importers": [{"Name": "Harppa"}],
                    "Images": [{"Caption": "Model number BHC001 on the label"}],
                }
            ]
        ),
        encoding="utf-8",
    )

    recalls = load_cpsc_recalls(recalls_file)

    assert len(recalls) == 1
    assert recalls[0].recall_id == "10461"
    assert recalls[0].models == ("BHC001",)
    assert recalls[0].upcs == ("012345678905",)
    assert recalls[0].hazard == "Fall and entrapment hazard"
    assert "Harppa" in recalls[0].searchable_text


def test_load_cpsc_recalls_rejects_non_array_document(tmp_path):
    recalls_file = tmp_path / "recalls.json"
    recalls_file.write_text('{"recalls": []}', encoding="utf-8")

    with pytest.raises(InputError, match="top-level JSON value must be an array"):
        load_cpsc_recalls(recalls_file)
