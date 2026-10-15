import asyncio
import json
import sys

import pytest

from app.provider import MockProvider
from evaluation.__main__ import main
from evaluation.runner import blind_comparison, evaluate


@pytest.fixture
def artifacts(tmp_path):
    left = asyncio.run(evaluate(MockProvider(), system_name="left-identity"))
    right = asyncio.run(evaluate(MockProvider(), system_name="right-identity"))
    review, key = blind_comparison(left, right, seed=42)
    paths = {}
    for name, value in (("left", left), ("right", right), ("review", review), ("key", key)):
        paths[name] = tmp_path / f"{name}.json"
        paths[name].write_text(json.dumps(value))
    return paths


def command(paths, output, *, key=False):
    args = ["evaluation", "summarize", str(paths["review"]), str(paths["left"]),
            str(paths["right"]), "--seed", "42", "--output", str(output)]
    if key:
        args.extend(["--key", str(paths["key"])])
    return args


def test_cli_counts_unrated_reviews_without_unblinding(artifacts, tmp_path, monkeypatch):
    output = tmp_path / "summary.json"
    monkeypatch.setattr(sys, "argv", command(artifacts, output))
    assert main() == 0
    summary = json.loads(output.read_text())
    assert summary["status"] == "unrated"
    assert summary["included_cases"] == 4
    assert summary["dimensions"]["authenticity"] == {"A": 0, "B": 0, "tie": 0, "missing": 4}
    assert summary["authenticity_superiority"] == "not_established"
    assert "system_preferences" not in summary and "systems" not in summary
    assert "left-identity" not in output.read_text()


def test_cli_summarizes_validated_ratings_and_preserves_output(artifacts, tmp_path, monkeypatch):
    review = json.loads(artifacts["review"].read_text())
    for case in review["cases"]:
        case["preferences"] = {"authenticity": "A", "helpfulness": "B", "intent_preservation": "tie"}
        case["notes"] = "synthetic reviewer note"
    artifacts["review"].write_text(json.dumps(review))
    output = tmp_path / "summary.json"
    monkeypatch.setattr(sys, "argv", command(artifacts, output, key=True))
    assert main() == 0
    original = output.read_bytes()
    summary = json.loads(original)
    assert summary["status"] == "complete"
    assert summary["dimensions"]["authenticity"]["A"] == 4
    assert summary["dimensions"]["helpfulness"]["B"] == 4
    assert summary["system_preferences"]["intent_preservation"]["tie"] == 4
    assert "synthetic reviewer note" not in original.decode()
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    assert output.read_bytes() == original


def test_cli_rejects_edited_candidate_without_writing_summary(artifacts, tmp_path, monkeypatch, capsys):
    review = json.loads(artifacts["review"].read_text())
    review["cases"][0]["options"]["A"][0]["text"] = "synthetic edited candidate"
    artifacts["review"].write_text(json.dumps(review))
    output = tmp_path / "summary.json"
    monkeypatch.setattr(sys, "argv", command(artifacts, output))
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    assert not output.exists()
    assert "synthetic edited candidate" not in capsys.readouterr().err


def test_cli_rejects_explicit_null_key_instead_of_silently_keeping_blind_mode(artifacts, tmp_path, monkeypatch):
    artifacts["key"].write_text("null")
    output = tmp_path / "summary.json"
    monkeypatch.setattr(sys, "argv", command(artifacts, output, key=True))
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    assert not output.exists()


def test_compare_cli_rolls_back_review_when_key_creation_fails(artifacts, tmp_path, monkeypatch):
    output = tmp_path / "new-review.json"
    key = tmp_path / "missing-parent" / "key.json"
    monkeypatch.setattr(sys, "argv", ["evaluation", "compare", str(artifacts["left"]),
                                     str(artifacts["right"]), "--output", str(output), "--key", str(key)])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    assert not output.exists() and not key.exists()
