import copy
import json
import sys

import pytest

from app.provider import MockProvider, ProviderFailure
from evaluation.__main__ import main
from evaluation.runner import blind_comparison, evaluate, fingerprint, load_dataset, verify_report


def test_dataset_has_reproducible_synthetic_generate_and_rewrite_cases():
    dataset = load_dataset()
    assert fingerprint(dataset) == fingerprint(json.loads(json.dumps(dataset)))
    assert len(dataset["cases"]) == 4
    assert {case["request"]["mode"] for case in dataset["cases"]} == {"generate", "rewrite"}
    assert all(case["style_examples"] for case in dataset["cases"])


@pytest.mark.asyncio
async def test_mock_report_has_contract_evidence_without_quality_claim():
    report = await evaluate(MockProvider())
    assert verify_report(report) == report
    assert report["system"]["mock"] is True
    assert report["summary"]["contract_pass"] == 4
    assert report["summary"]["quality"] == "unmeasured"
    assert report["summary"]["authenticity_superiority"] == "not_established"
    assert all(record["latency_ms"] >= 0 for record in report["records"])
    edited = copy.deepcopy(report)
    edited["records"][0]["response"]["candidates"][0]["text"] = "altered"
    with pytest.raises(ValueError, match="integrity"):
        verify_report(edited)


@pytest.mark.asyncio
async def test_contract_failure_is_separate_from_provider_failure_and_quality():
    class InvalidProvider:
        async def generate(self, request):
            return {"provider": "invalid", "candidates": []}

    class FailingProvider:
        async def generate(self, request):
            raise ProviderFailure("untrusted sensitive upstream detail")

    invalid = await evaluate(InvalidProvider())
    failed = await evaluate(FailingProvider())
    assert invalid["summary"]["contract_failure"] == 4
    assert failed["summary"]["provider_failure"] == 4
    assert invalid["summary"]["quality"] == failed["summary"]["quality"] == "unmeasured"
    assert "upstream detail" not in json.dumps(failed)
    assert invalid["system"]["mock"] is False
    review, key = blind_comparison(invalid, failed)
    assert review["cases"] == []
    assert len(key["cases"]) == 4


@pytest.mark.asyncio
async def test_review_is_reproducible_and_keeps_system_mapping_separate():
    left = await evaluate(MockProvider(), system_name="secret-left")
    right = await evaluate(MockProvider(), system_name="secret-right")
    review, key = blind_comparison(left, right, seed=42)
    assert (review, key) == blind_comparison(left, right, seed=42)
    assert "secret-left" not in json.dumps(review)
    assert "secret-right" not in json.dumps(review)
    assert key["systems"]["left"]["name"] == "secret-left"
    assert len(review["cases"]) == 4
    for case, mapping in zip(review["cases"], key["cases"]):
        assert set(case["options"]) == {"A", "B"}
        assert set((mapping["A"], mapping["B"])) == {"left", "right"}
        assert all(value is None for value in case["preferences"].values())


@pytest.mark.asyncio
async def test_mismatched_dataset_rejected_even_with_valid_report_digest():
    report = await evaluate(MockProvider())
    report["dataset_sha256"] = "old-dataset"
    report["report_sha256"] = fingerprint({key: value for key, value in report.items() if key != "report_sha256"})
    with pytest.raises(ValueError, match="dataset"):
        verify_report(report)


def test_cli_ignores_live_provider_environment_and_preserves_existing_output(tmp_path, monkeypatch):
    monkeypatch.setenv("PROOFREAD_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    output = tmp_path / "report.json"
    monkeypatch.setattr(sys, "argv", ["evaluation", "run", "--output", str(output)])
    assert main() == 0
    assert json.loads(output.read_text())["system"]["mock"] is True
    original = output.read_bytes()
    with pytest.raises(FileExistsError):
        main()
    assert output.read_bytes() == original


@pytest.mark.parametrize("value", [None, [], {}, "not-a-report"])
def test_malformed_report_has_consistent_value_error(value):
    with pytest.raises(ValueError, match="schema"):
        verify_report(value)


@pytest.mark.asyncio
@pytest.mark.parametrize("path,value,error", [
    (("schema_version",), 2, "schema"),
    (("records", 0, "status"), "semantic_success", "schema"),
    (("records", 0, "response"), None, "schema"),
    (("records", 0, "response", "candidates"), [], "schema"),
    (("records", 0, "latency_ms"), -1, "schema"),
    (("records", 0, "case_id"), "wrong-id", "case IDs"),
    (("records",), [], "case IDs"),
    (("summary", "cases"), 3, "summary counts"),
    (("summary", "contract_pass"), 0, "summary counts"),
    (("system", "mock"), "true", "schema"),
])
async def test_valid_digest_does_not_bypass_schema_or_consistency_checks(path, value, error):
    report = await evaluate(MockProvider())
    target = report
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = value
    report["report_sha256"] = fingerprint({key: value for key, value in report.items() if key != "report_sha256"})
    with pytest.raises(ValueError, match=error):
        verify_report(report)


@pytest.mark.asyncio
async def test_missing_case_id_is_reported_as_schema_error():
    report = await evaluate(MockProvider())
    del report["records"][0]["case_id"]
    report["report_sha256"] = fingerprint({key: value for key, value in report.items() if key != "report_sha256"})
    with pytest.raises(ValueError, match="schema"):
        verify_report(report)


def test_compare_cli_reports_malformed_input_without_writing_artifacts(tmp_path, monkeypatch, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text("{}")
    output, key = tmp_path / "review.json", tmp_path / "key.json"
    monkeypatch.setattr(sys, "argv", ["evaluation", "compare", str(bad), str(bad),
                                     "--output", str(output), "--key", str(key)])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    assert "Invalid evaluation report schema" in capsys.readouterr().err
    assert not output.exists() and not key.exists()
