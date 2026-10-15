"""One-time, synthetic-only integration check; blocked without reviewed evidence.

No default pricing assumptions and no network requests without explicit execution.
Reservations are durable before inference and never refunded, including failures.
"""
import argparse
import asyncio
from contextlib import contextmanager
from datetime import date
from decimal import Decimal
import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from typing import Literal
from uuid import UUID

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.main import ReplyRequest
from app.provider import OpenAIProvider, ProviderFailure
from .runner import fingerprint, load_dataset

APPROVAL_ID = "proofread-2026-10-15-gpt-5.4-mini-usd2-once"
MODEL = "gpt-5.4-mini"
BUDGET_USD = Decimal("2.00")
OUTPUT_TOKEN_CAP = 512
LEDGER_PATH = Path("/workspace/.proofread/live-budget.json")


class LiveBlocked(ValueError):
    """An unmet execution prerequisite; no sensitive provider details."""


class VerifiedModelSpec(BaseModel):
    """Reviewed official evidence, not inferred facts or automatically trusted data.

    There is deliberately no committed spec for the approved model. An owner or
    engineer must review current official sources before supplying this artifact.
    All pricing fields must be maxima across applicable input-length tiers, with
    no cached/batch/priority discounts. Context is the full model context maximum.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)
    model: Literal["gpt-5.4-mini"]
    verified_on: date
    reviewed_by: str = Field(min_length=1, max_length=200)
    official_sources: list[str] = Field(min_length=1)
    allowed_response_models: list[str] = Field(min_length=1)
    context_max_tokens: int = Field(gt=0, strict=True)
    maximum_input_usd_per_million: Decimal = Field(gt=0, allow_inf_nan=False)
    maximum_output_usd_per_million: Decimal = Field(gt=0, allow_inf_nan=False)
    structured_json_schema_supported: Literal[True]
    max_completion_tokens_caps_all_billed_output: Literal[True]
    maximum_rates_cover_all_applicable_tiers: Literal[True]
    default_service_tier_supported: Literal[True]

    @field_validator("structured_json_schema_supported", "max_completion_tokens_caps_all_billed_output",
                     "maximum_rates_cover_all_applicable_tiers", "default_service_tier_supported", mode="before")
    @classmethod
    def require_verified_true(cls, value):
        if value is not True:
            raise ValueError("Compatibility facts require explicit true evidence")
        return value

    def reservation_per_call(self):
        # Full context bounds every accepted input, including provider framing and
        # schema overhead. Output is additionally reserved even if context already
        # includes it. Unsupported/oversized requests may still fail and cost money.
        return (Decimal(self.context_max_tokens) * self.maximum_input_usd_per_million
                + Decimal(OUTPUT_TOKEN_CAP) * self.maximum_output_usd_per_million) / Decimal(1_000_000)


def validate_spec(spec):
    if spec is None:
        raise LiveBlocked("Reviewed official pricing, context and compatibility evidence is missing")
    try:
        spec = VerifiedModelSpec.model_validate(spec)
    except ValidationError as exc:
        raise LiveBlocked("Reviewed model evidence is invalid") from exc
    if spec.verified_on != date.today():
        raise LiveBlocked("Model evidence must be reviewed on the execution date")
    if any(not source.startswith(("https://developers.openai.com/", "https://platform.openai.com/",
                                  "https://openai.com/")) for source in spec.official_sources):
        raise LiveBlocked("Model evidence must cite official OpenAI sources")
    if any(model != MODEL and not re.fullmatch(re.escape(MODEL) + r"-\d{4}-\d{2}-\d{2}", model)
           for model in spec.allowed_response_models):
        raise LiveBlocked("Response model aliases must be verified approved-model snapshots")
    if spec.reservation_per_call() * 2 > BUDGET_USD:
        raise LiveBlocked("Two conservative context-window reservations exceed the approved $2 budget")
    return spec


@contextmanager
def _locked_ledger(path):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    flags = os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW
    descriptor = os.open(str(path) + ".lock", flags, 0o600)
    with os.fdopen(descriptor, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def _instance_fingerprint():
    try:
        if sys.platform == "darwin":
            boot_id = subprocess.run(["/usr/sbin/sysctl", "-n", "kern.bootsessionuuid"],
                                     capture_output=True, text=True, check=True, timeout=5).stdout.strip()
        elif sys.platform.startswith("linux"):
            boot_id = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
        else:
            raise LiveBlocked("Campaign instance identity is unsupported on this platform")
        boot_id = str(UUID(boot_id))
        hostname = os.uname().nodename
        if not hostname:
            raise ValueError("Missing hostname")
        return fingerprint({"hostname": hostname, "boot_id": boot_id})
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        raise LiveBlocked("Cannot verify the local campaign instance identity") from exc


def _write_ledger(path, ledger):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as handle:
            temporary = handle.name
            json.dump(ledger, handle)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def _initial_ledger():
    return {"approval_id": APPROVAL_ID, "model": MODEL, "budget_usd": str(BUDGET_USD),
            "campaign_instance": _instance_fingerprint(), "state": "available",
            "reserved_usd": "0", "calls_reserved": 0}


def initialize_approval_ledger(*, _ledger_path=LEDGER_PATH):
    """Explicit one-time approval provisioning, never called by CLI or startup.

    Only the currently approved campaign owner may invoke this once. Missing
    state on another task is a blocker, not authorization to create new credit.
    """
    path = Path(_ledger_path)
    try:
        with _locked_ledger(path):
            if path.exists() or path.is_symlink():
                raise LiveBlocked("Approval ledger already exists; initialization cannot overwrite it")
            ledger = _initial_ledger()
            _write_ledger(path, ledger)
            return ledger
    except OSError as exc:
        raise LiveBlocked("Cannot initialize the approved campaign ledger") from exc


def reserve_once(spec, *, _ledger_path=LEDGER_PATH):
    """Consume the whole one-time approval atomically; no reset/refund operation.

    The private path parameter exists for isolated tests. CLI always uses the
    fixed outside-repository ledger. File permissions are not a tamper-proof
    accounting system; this guard covers concurrent/repeated cooperative runs.
    """
    path = Path(_ledger_path)
    reservation = spec.reservation_per_call() * 2
    try:
        with _locked_ledger(path):
            if not path.is_file() or path.is_symlink():
                raise LiveBlocked("Approved campaign ledger is missing or unsafe; no automatic initialization")
            try:
                existing = json.loads(path.read_text())
            except (ValueError, OSError) as exc:
                raise LiveBlocked("Campaign ledger is unreadable; no reset is supported") from exc
            if existing != _initial_ledger():
                raise LiveBlocked("Campaign ledger is reserved, corrupt or belongs to another instance; no reset is supported")
            ledger = {
                "approval_id": APPROVAL_ID, "model": MODEL, "budget_usd": str(BUDGET_USD),
                "campaign_instance": existing["campaign_instance"], "state": "reserved",
                "reserved_usd": str(reservation), "calls_reserved": 2,
                "spec_sha256": fingerprint(spec.model_dump(mode="json")),
                "reservation_policy": "Never refund failed, interrupted or unknown outcomes",
                "outcomes": [],
            }
            _write_ledger(path, ledger)
            return ledger
    except OSError as exc:
        raise LiveBlocked("Cannot durably reserve the one-time budget") from exc


def _preserve_outcome(record, path):
    """Preserve completed/unknown outcomes before another paid operation."""
    try:
        with _locked_ledger(path):
            ledger = json.loads(path.read_text())
            if (ledger.get("approval_id") != APPROVAL_ID or ledger.get("state") != "reserved"
                    or ledger.get("campaign_instance") != _instance_fingerprint()):
                raise LiveBlocked("Cannot preserve outcome in the approved campaign ledger")
            ledger["outcomes"].append(record)
            _write_ledger(path, ledger)
    except (OSError, ValueError, KeyError, AttributeError) as exc:
        raise LiveBlocked("Cannot durably preserve outcome; further calls blocked") from exc


async def run_live(*, execute=False, spec=None, transport=None, _ledger_path=LEDGER_PATH):
    """At most two paid POSTs, never retried. Default invocation does no network IO."""
    if not execute:
        raise LiveBlocked("Explicit --execute is required")
    key = (os.getenv("PROOFREAD_OPENAI_API_KEY", "").strip()
           or os.getenv("OPENAI_API_KEY", "").strip())
    if not key:
        raise LiveBlocked("Configure the approved key securely in environment settings")
    spec = validate_spec(spec)
    try:
        async with httpx.AsyncClient(timeout=15, transport=transport, follow_redirects=False) as client:
            preflight = await client.get(f"https://api.openai.com/v1/models/{MODEL}",
                                         headers={"Authorization": f"Bearer {key}"})
            preflight.raise_for_status()
            if preflight.json().get("id") != MODEL:
                raise LiveBlocked("Approved model availability was not confirmed")
    except (httpx.HTTPError, ValueError, AttributeError) as exc:
        raise LiveBlocked("Approved model availability was not confirmed") from exc
    # Reserve BOTH requests before the first paid operation. A crash cannot make
    # the second slot available to a repeat invocation.
    ledger = reserve_once(spec, _ledger_path=_ledger_path)
    provider = OpenAIProvider(key, MODEL, transport=transport,
                              max_completion_tokens=OUTPUT_TOKEN_CAP)
    dataset = load_dataset()
    cases = [next(case for case in dataset["cases"] if case["request"]["mode"] == mode)
             for mode in ("generate", "rewrite")]
    records = []
    for case in cases:
        stop_after_outcome = False
        started = time.perf_counter()
        record = {"case_id": case["id"], "contextual_relevance": "human_review_required",
                  "quality": "unmeasured", "reserved_usd": str(spec.reservation_per_call())}
        try:
            answer, usage = await provider.generate_with_metadata(ReplyRequest.model_validate(case["request"]))
            record.update(status="contract_pass", schema_and_distinctness="passed",
                          response=answer.model_dump(), token_usage=usage.model_dump())
            violation = None
            if usage.prompt_tokens > spec.context_max_tokens or usage.completion_tokens > OUTPUT_TOKEN_CAP:
                violation = "accounting_bound_violation"
            elif usage.model not in spec.allowed_response_models or usage.service_tier != "default":
                violation = "accounting_evidence_mismatch"
            if violation:
                record.update(status=violation, actual_cost_usd="unknown")
                record["latency_ms"] = round((time.perf_counter() - started) * 1000, 3)
                _preserve_outcome(record, Path(_ledger_path))
                records.append(record)
                # A violation contradicts verified evidence. Stop before any more spend.
                break
            cost = (usage.prompt_tokens * spec.maximum_input_usd_per_million
                    + usage.completion_tokens * spec.maximum_output_usd_per_million) / Decimal(1_000_000)
            record["reported_usage_cost_upper_bound_usd"] = str(cost)
        except ProviderFailure:
            record.update(status="provider_or_contract_failure", token_usage="unknown",
                          schema_and_distinctness="unverified")
            # Invalid output can conceal model/tier/accounting evidence. Unknown
            # outcomes consume the reservation and stop further paid operations.
            stop_after_outcome = True
        record["latency_ms"] = round((time.perf_counter() - started) * 1000, 3)
        _preserve_outcome(record, Path(_ledger_path))
        records.append(record)
        if stop_after_outcome:
            break
    return {
        "approval_id": APPROVAL_ID, "model": MODEL, "synthetic_only": True,
        "personalization": "not_evaluated", "dataset_sha256": fingerprint(dataset),
        "spec": spec.model_dump(mode="json"),
        "budget": {key: value for key, value in ledger.items() if key != "outcomes"}, "records": records,
        "unrun_cases": [{"case_id": case["id"], "mode": case["request"]["mode"],
                         "reason": "Stopped after prior uncertain outcome; reservation retained"}
                        for case in cases[len(records):]],
        "authenticity_superiority": "not_established",
    }


def main():
    parser = argparse.ArgumentParser(description="One-time approved synthetic live integration; no defaults permit spend")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--reviewed-spec", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; overwrite is not supported")
    try:
        spec = json.loads(args.reviewed_spec.read_text()) if args.reviewed_spec else None
        with args.output.open("x") as output:
            # Prove the exclusive destination is writable before any possible
            # inference; completed outcomes also persist in the budget ledger.
            output.flush()
            os.fsync(output.fileno())
            try:
                report = asyncio.run(run_live(execute=args.execute, spec=spec))
            except LiveBlocked as exc:
                json.dump({"status": "blocked", "reason": str(exc)}, output)
                raise
            json.dump(report, output, indent=2)
            output.write("\n")
    except (LiveBlocked, OSError, ValueError) as exc:
        # Never include raw provider errors, HTTP response bodies or credentials.
        parser.error(str(exc) if isinstance(exc, LiveBlocked) else "Invalid evidence or output configuration")
    return int(any(record["status"] != "contract_pass" for record in report["records"]))


if __name__ == "__main__":
    raise SystemExit(main())
