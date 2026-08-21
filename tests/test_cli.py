import json

import pytest

from recall_match.cli import main


def write_inputs(tmp_path, inventory_row):
    inventory = tmp_path / "inventory.csv"
    inventory.write_text(
        "item_id,name,brand,model,upc\n" + inventory_row + "\n",
        encoding="utf-8",
    )
    recalls = tmp_path / "recalls.json"
    recalls.write_text(
        json.dumps(
            [
                {
                    "RecallID": 10461,
                    "RecallDate": "2026-01-01T00:00:00",
                    "Title": "Acme recalls folding high chairs",
                    "URL": "https://www.cpsc.gov/Recalls/2026/example",
                    "Products": [{"Name": "Acme Folding High Chair", "Model": "HC-200"}],
                    "ProductUPCs": [{"UPC": "012345678905"}],
                    "Hazards": [{"Name": "Fall hazard"}],
                    "Remedies": [{"Name": "Stop use"}],
                    "Manufacturers": [{"Name": "Acme"}],
                }
            ]
        ),
        encoding="utf-8",
    )
    return inventory, recalls


def test_audit_writes_reports_and_honors_never_threshold(tmp_path, capsys):
    inventory, recalls = write_inputs(tmp_path, "chair,High chair,Acme,HC-200,012345678905")
    json_out = tmp_path / "report.json"
    markdown_out = tmp_path / "report.md"

    exit_code = main(
        [
            "audit",
            str(inventory),
            "--recalls",
            str(recalls),
            "--json-out",
            str(json_out),
            "--markdown-out",
            str(markdown_out),
            "--as-of",
            "2026-01-02",
            "--fail-on",
            "never",
        ]
    )

    assert exit_code == 0
    assert json.loads(json_out.read_text(encoding="utf-8"))["schema_version"] == "1"
    assert "identifier_match" in markdown_out.read_text(encoding="utf-8")
    assert "1 identifier match" in capsys.readouterr().out


def test_default_threshold_fails_only_on_identifier_matches(tmp_path):
    exact_inventory, recalls = write_inputs(tmp_path, "chair,High chair,Acme,HC-200,012345678905")
    assert main(["audit", str(exact_inventory), "--recalls", str(recalls)]) == 1

    review_inventory, recalls = write_inputs(tmp_path, "chair,Acme folding high chairs,,,")
    assert main(["audit", str(review_inventory), "--recalls", str(recalls)]) == 0
    assert (
        main(
            [
                "audit",
                str(review_inventory),
                "--recalls",
                str(recalls),
                "--fail-on",
                "review",
            ]
        )
        == 1
    )


def test_invalid_input_returns_two_with_one_line_error(tmp_path, capsys):
    inventory, _ = write_inputs(tmp_path, "chair,High chair,Acme,HC-200,")
    recalls = tmp_path / "broken.json"
    recalls.write_text("not json", encoding="utf-8")

    exit_code = main(["audit", str(inventory), "--recalls", str(recalls)])

    assert exit_code == 2
    error = capsys.readouterr().err
    assert error.startswith("error: ")
    assert "invalid JSON" in error
    assert len(error.splitlines()) == 1


def test_version_is_available(capsys):
    with pytest.raises(SystemExit) as result:
        main(["--version"])

    assert result.value.code == 0
    assert capsys.readouterr().out.strip() == "recall-match 0.1.0"
