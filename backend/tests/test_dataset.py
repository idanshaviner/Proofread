"""Invented evaluation split integrity; these are not AI-quality assertions."""
import copy
import json

import pytest

from evaluation import runner
from evaluation.runner import fingerprint, load_dataset

BASELINE_SHA256 = "43b7db226e15424b5ed0ce5012e522addcad64f3426dbd17ae49eeaed906a80f"


def test_v2_keeps_original_baseline_content_and_order():
    dataset = load_dataset()
    assert dataset["version"] == "synthetic-v2"
    assert len(dataset["cases"]) == 8
    baseline = dataset["cases"][:4]
    assert all(case["split"] == "baseline" for case in baseline)
    assert fingerprint([{key: value for key, value in case.items() if key != "split"}
                        for case in baseline]) == BASELINE_SHA256


def test_both_splits_have_generate_and_rewrite_and_declared_provenance():
    dataset = load_dataset()
    assert dataset["synthetic_only"] is True
    assert dataset["used_for_tuning"] is False
    assert set(dataset["split_policy"]) == {"baseline", "held_out_stress", "style_examples"}
    for split in ("baseline", "held_out_stress"):
        cases = [case for case in dataset["cases"] if case["split"] == split]
        assert len(cases) == 4
        assert [case["request"]["mode"] for case in cases].count("generate") == 2
        assert [case["request"]["mode"] for case in cases].count("rewrite") == 2
    for case in dataset["cases"][4:]:
        assert "Relevance:" in case["review_guidance"]
        assert "Intent:" in case["review_guidance"]
        assert "context" not in case["request"]


def test_live_first_generate_and_rewrite_inputs_stay_exact():
    dataset = load_dataset()
    first = [next(case for case in dataset["cases"] if case["request"]["mode"] == mode)
             for mode in ("generate", "rewrite")]
    assert [case["id"] for case in first] == ["generate-friend-plan", "rewrite-friend-decline"]
    assert first[0]["request"] == {"mode": "generate", "incoming_message": "Want to get lunch on Saturday?",
                                   "relationship": "friend", "goal": "Accept and ask what time."}
    assert first[1]["request"] == {"mode": "rewrite", "incoming_message": "Movie night at mine?",
                                   "relationship": "friend", "goal": "Decline warmly without inventing a reason.",
                                   "draft": "can't make it tonight but have fun"}


@pytest.mark.parametrize("mutation", ["unknown_split", "duplicate_id", "missing_split_mode", "real_data",
                                      "tuned", "no_policy", "blank_guidance", "blank_style", "draft_leak", "new_field"])
def test_loader_rejects_invalid_provenance_splits_or_scenario_integrity(tmp_path, monkeypatch, mutation):
    dataset = copy.deepcopy(json.loads(runner.DATASET_PATH.read_text()))
    first = dataset["cases"][0]
    if mutation == "unknown_split":
        first["split"] = "training"
    elif mutation == "duplicate_id":
        dataset["cases"][1]["id"] = first["id"]
    elif mutation == "missing_split_mode":
        # Global mode coverage remains valid; per-split mode coverage must fail.
        for case in dataset["cases"]:
            case["split"] = "baseline" if case["request"]["mode"] == "generate" else "held_out_stress"
    elif mutation == "real_data":
        dataset["synthetic_only"] = False
    elif mutation == "tuned":
        dataset["used_for_tuning"] = True
    elif mutation == "no_policy":
        dataset["split_policy"] = {}
    elif mutation == "blank_guidance":
        first["review_guidance"] = "  "
    elif mutation == "blank_style":
        first["style_examples"] = ["  "]
    elif mutation == "draft_leak":
        draft = next(case["request"]["draft"] for case in dataset["cases"] if case["request"]["mode"] == "rewrite")
        first["style_examples"] = ["  " + draft.upper() + "  "]
    else:
        first["request"]["context"] = "An undeclared API field."
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(dataset))
    monkeypatch.setattr(runner, "DATASET_PATH", path)
    with pytest.raises(ValueError):
        load_dataset()
