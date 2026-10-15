"""Contract evidence and blinded human review, separate from semantic quality."""
import hashlib
from copy import deepcopy
import json
import random
import time
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from app.main import ReplyRequest
from app.provider import MockProvider, ProviderFailure, ReplyResponse

DATASET_PATH = Path(__file__).with_name("cases.json")


class _Artifact(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class _System(_Artifact):
    name: str = Field(min_length=1)
    adapter: str = Field(min_length=1)
    model: str | None
    mock: bool


class _Record(_Artifact):
    case_id: str = Field(min_length=1)
    quality: Literal["unmeasured"]
    status: Literal["contract_pass", "contract_failure", "provider_failure"]
    latency_ms: float = Field(ge=0, allow_inf_nan=False)
    response: ReplyResponse | None = None

    @model_validator(mode="after")
    def check_response(self):
        if (self.status == "contract_pass") != (self.response is not None):
            raise ValueError("Only passing records must contain a valid response")
        return self


class _Summary(_Artifact):
    cases: int = Field(ge=0)
    contract_pass: int = Field(ge=0)
    contract_failure: int = Field(ge=0)
    provider_failure: int = Field(ge=0)
    quality: Literal["unmeasured"]
    authenticity_superiority: Literal["not_established"]


class _Report(_Artifact):
    schema_version: Literal[1]
    dataset_version: str
    dataset_sha256: str
    report_sha256: str
    system: _System
    records: list[_Record]
    summary: _Summary


def fingerprint(value):
    """Stable content digest, independent of JSON formatting and key order."""
    canonical = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def load_dataset():
    dataset = json.loads(DATASET_PATH.read_text())
    if (not isinstance(dataset, dict) or not isinstance(dataset.get("version"), str)
            or not dataset["version"].strip() or not isinstance(dataset.get("provenance"), str)
            or not dataset["provenance"].strip() or dataset.get("synthetic_only") is not True
            or dataset.get("used_for_tuning") is not False):
        raise ValueError("Evaluation requires versioned synthetic-only, untuned provenance")
    policies = dataset.get("split_policy")
    if (not isinstance(policies, dict) or set(policies) != {"baseline", "held_out_stress", "style_examples"}
            or any(not isinstance(value, str) or not value.strip() for value in policies.values())):
        raise ValueError("Evaluation requires explicit split and review-example policies")
    if not isinstance(dataset.get("cases"), list) or not dataset["cases"]:
        raise ValueError("Evaluation requires nonempty cases")
    if any(not isinstance(case, dict) or not isinstance(case.get("id"), str) or not case["id"].strip()
           for case in dataset["cases"]):
        raise ValueError("Evaluation cases require nonblank IDs")
    ids = [case["id"] for case in dataset["cases"]]
    if len(ids) != len(set(ids)) or not ids:
        raise ValueError("Evaluation cases require unique IDs")
    scenario_texts = set()
    style_texts = set()
    normalize = lambda text: " ".join(text.split()).casefold()
    split_modes = {"baseline": set(), "held_out_stress": set()}
    for case in dataset["cases"]:
        if not isinstance(case.get("split"), str) or case["split"] not in split_modes:
            raise ValueError("Evaluation case has an unknown split")
        request = case.get("request")
        if not isinstance(request, dict) or not set(request) <= set(ReplyRequest.model_fields):
            raise ValueError("Evaluation requests must use the existing API fields")
        validated = ReplyRequest.model_validate(request)
        split_modes[case["split"]].add(validated.mode)
        scenario_texts.update(normalize(text) for text in (validated.incoming_message, validated.draft) if text and text.strip())
        examples = case.get("style_examples")
        if (not isinstance(examples, list) or not examples
                or any(not isinstance(example, str) or not example.strip() for example in examples)
                or not isinstance(case.get("review_guidance"), str) or not case["review_guidance"].strip()):
            raise ValueError("Each case requires invented review examples and guidance")
        style_texts.update(normalize(example) for example in examples)
    if any(modes != {"generate", "rewrite"} for modes in split_modes.values()):
        raise ValueError("Each evaluation split must include generate and rewrite")
    if scenario_texts & style_texts:
        raise ValueError("Review style examples must not duplicate scenario messages or drafts")
    return dataset


async def evaluate(provider, system_name="generic-mock", model=None):
    """Run committed synthetic cases using an explicitly supplied adapter.

    CLI callers always supply MockProvider. Supplying another adapter is an
    explicit integration decision; this runner never selects from environment.
    Style examples remain review context and are not sent by the generic runner.
    """
    dataset = load_dataset()
    records = []
    for case in dataset["cases"]:
        started = time.perf_counter()
        record = {"case_id": case["id"], "quality": "unmeasured"}
        try:
            answer = await provider.generate(ReplyRequest.model_validate(case["request"]))
            if isinstance(answer, ReplyResponse):
                answer = answer.model_dump()
            answer = ReplyResponse.model_validate(answer)
            record.update(status="contract_pass", response=answer.model_dump())
        except ValidationError:
            record["status"] = "contract_failure"
        except ProviderFailure:
            # ProviderFailure can wrap invalid upstream model output. It is not
            # evidence of low semantic quality and its raw exception is omitted.
            record["status"] = "provider_failure"
        record["latency_ms"] = round((time.perf_counter() - started) * 1000, 3)
        records.append(record)
    report = {
        "schema_version": 1,
        "dataset_version": dataset["version"],
        "dataset_sha256": fingerprint(dataset),
        "system": {"name": system_name, "adapter": type(provider).__name__,
                   "model": model, "mock": isinstance(provider, MockProvider)},
        "records": records,
        "summary": {"cases": len(records), **{
            status: sum(record["status"] == status for record in records)
            for status in ("contract_pass", "contract_failure", "provider_failure")
        }, "quality": "unmeasured", "authenticity_superiority": "not_established"},
    }
    report["report_sha256"] = fingerprint(report)
    return report


def verify_report(report):
    """Reject edited/mismatched artifacts before matching or human review."""
    try:
        validated = _Report.model_validate(report)
    except ValidationError as exc:
        raise ValueError("Invalid evaluation report schema") from exc
    unsigned = {key: value for key, value in report.items() if key != "report_sha256"}
    if report.get("report_sha256") != fingerprint(unsigned):
        raise ValueError("Report integrity check failed")
    dataset = load_dataset()
    if (validated.dataset_sha256 != fingerprint(dataset)
            or validated.dataset_version != dataset["version"]):
        raise ValueError("Report does not match the current synthetic dataset")
    expected_ids = [case["id"] for case in dataset["cases"]]
    if [record.case_id for record in validated.records] != expected_ids:
        raise ValueError("Report case IDs do not match the dataset")
    expected_counts = {"cases": len(validated.records), **{
        status: sum(record.status == status for record in validated.records)
        for status in ("contract_pass", "contract_failure", "provider_failure")
    }}
    if any(getattr(validated.summary, field) != count for field, count in expected_counts.items()):
        raise ValueError("Report summary counts do not match records")
    return report


def blind_comparison(left, right, seed=0):
    """Return a review sheet and separate unblinding key; never assign scores.

    Reviewers see synthetic writing exemplars and candidates but no system names.
    Blinding cannot hide recognizable mock text; treat mock reviews as rehearsal.
    """
    verify_report(left)
    verify_report(right)
    rng = random.Random(seed)
    review = {"dataset_sha256": left["dataset_sha256"], "cases": []}
    key = {"seed": seed, "systems": {"left": left["system"], "right": right["system"]},
           "reports": {"left": left["report_sha256"], "right": right["report_sha256"]}, "cases": []}
    for case, first, second in zip(load_dataset()["cases"], left["records"], right["records"]):
        if first["status"] != "contract_pass" or second["status"] != "contract_pass":
            key["cases"].append({"case_id": case["id"], "excluded": "contract/provider failure"})
            continue
        order = ["left", "right"]
        rng.shuffle(order)
        records = {"left": first, "right": second}
        review["cases"].append({
            **case,
            "options": {label: records[side]["response"]["candidates"] for label, side in zip(("A", "B"), order)},
            "preferences": {"authenticity": None, "helpfulness": None, "intent_preservation": None},
            "notes": "",
        })
        key["cases"].append({"case_id": case["id"], **dict(zip(("A", "B"), order))})
    # Reviewers edit returned artifacts; those edits must not mutate the verified
    # source reports (or vice versa) through shared candidate/system dictionaries.
    return deepcopy(review), deepcopy(key)
