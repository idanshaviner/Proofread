"""All provider traffic is injected MockTransport, never real inference."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from decimal import Decimal
import json
import sys
import traceback
from types import SimpleNamespace

import httpx
import pytest

from evaluation.live import (APPROVAL_ID, MODEL, OUTPUT_TOKEN_CAP, LiveBlocked,
                             initialize_approval_ledger, main, reserve_once,
                             run_live, validate_spec)


@pytest.fixture
def evidence():
    # Invented rates/context for offline control tests. NOT approved model facts.
    return {
        "model": MODEL, "verified_on": date.today().isoformat(),
        "reviewed_by": "synthetic-test-fixture-only",
        "official_sources": ["https://developers.openai.com/synthetic-test-fixture"],
        "allowed_response_models": [MODEL],
        "context_max_tokens": 1000,
        "maximum_input_usd_per_million": "1.00",
        "maximum_output_usd_per_million": "2.00",
        "structured_json_schema_supported": True,
        "max_completion_tokens_caps_all_billed_output": True,
        "maximum_rates_cover_all_applicable_tiers": True,
        "default_service_tier_supported": True,
    }


@pytest.fixture
def ledger(tmp_path):
    path = tmp_path / "budget.json"
    initialize_approval_ledger(_ledger_path=path)
    return path


def completion(*, usage=True):
    result = {
        "model": MODEL, "service_tier": "default",
        "choices": [{"finish_reason": "stop", "message": {"content": json.dumps({"candidates": [
            {"text": "Yes, what time works?", "label": "Natural"},
            {"text": "I'm in. When?", "label": "Direct"},
            {"text": "Lunch sounds great! What time?", "label": "Playful"},
        ]})}}],
    }
    if usage:
        result["usage"] = {"prompt_tokens": 100, "completion_tokens": 60, "total_tokens": 160}
    return result


@pytest.mark.asyncio
@pytest.mark.parametrize("blocker", ["opt_in", "key", "evidence", "expensive", "compatibility", "stale"])
async def test_prerequisites_prevent_all_network(blocker, evidence, ledger, monkeypatch):
    monkeypatch.setenv("PROOFREAD_OPENAI_API_KEY", "fake-test-key")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    execute = True
    if blocker == "opt_in":
        execute = False
    if blocker == "key":
        monkeypatch.delenv("PROOFREAD_OPENAI_API_KEY")
    if blocker == "evidence":
        evidence = None
    if blocker == "expensive":
        evidence["maximum_input_usd_per_million"] = "10000"
    if blocker == "compatibility":
        evidence["structured_json_schema_supported"] = False
    if blocker == "stale":
        evidence["verified_on"] = (date.today() - timedelta(days=1)).isoformat()
    def no_network(request):
        pytest.fail("Blocked prerequisite must not make any request")
    with pytest.raises(LiveBlocked):
        await run_live(execute=execute, spec=evidence, transport=httpx.MockTransport(no_network), _ledger_path=ledger)
    assert json.loads(ledger.read_text())["state"] == "available"


@pytest.mark.asyncio
async def test_preflight_failure_never_posts_or_reserves(evidence, ledger, monkeypatch):
    monkeypatch.setenv("PROOFREAD_OPENAI_API_KEY", "fake-test-key")
    calls = []
    def handler(request):
        calls.append(request.method)
        return httpx.Response(404)
    with pytest.raises(LiveBlocked, match="availability"):
        await run_live(execute=True, spec=evidence, transport=httpx.MockTransport(handler), _ledger_path=ledger)
    assert calls == ["GET"]
    assert json.loads(ledger.read_text())["state"] == "available"


@pytest.mark.asyncio
async def test_two_calls_reserved_before_first_post_and_cannot_repeat(evidence, ledger, monkeypatch):
    monkeypatch.setenv("PROOFREAD_OPENAI_API_KEY", "fake-test-key")
    calls, modes = [], []
    def handler(request):
        calls.append(request.method)
        if request.method == "GET":
            return httpx.Response(200, json={"id": MODEL})
        saved = json.loads(ledger.read_text())
        assert saved["state"] == "reserved" and saved["calls_reserved"] == 2
        payload = json.loads(request.content)
        assert payload["model"] == MODEL
        assert payload["max_completion_tokens"] == OUTPUT_TOKEN_CAP
        assert payload["service_tier"] == "default"
        modes.append(json.loads(payload["messages"][1]["content"])["mode"])
        return httpx.Response(200, json=completion())
    transport = httpx.MockTransport(handler)
    report = await run_live(execute=True, spec=evidence, transport=transport, _ledger_path=ledger)
    assert calls == ["GET", "POST", "POST"]
    assert modes == ["generate", "rewrite"]
    assert all(record["status"] == "contract_pass" for record in report["records"])
    assert report["records"][0]["reported_usage_cost_upper_bound_usd"] == "0.00022"
    assert report["records"][0]["contextual_relevance"] == "human_review_required"
    assert report["budget"]["approval_id"] == APPROVAL_ID
    assert Decimal(report["budget"]["reserved_usd"]) == Decimal("0.004048")
    before = ledger.read_bytes()
    with pytest.raises(LiveBlocked, match="reserved"):
        await run_live(execute=True, spec=evidence, transport=transport, _ledger_path=ledger)
    assert calls.count("POST") == 2
    assert ledger.read_bytes() == before
    assert "fake-test-key" not in json.dumps(report) + ledger.read_text()


@pytest.mark.asyncio
@pytest.mark.parametrize("outcome", ["missing_usage", "http_error", "invalid_candidates", "timeout"])
async def test_unknown_outcomes_never_refund(evidence, ledger, monkeypatch, outcome):
    monkeypatch.setenv("PROOFREAD_OPENAI_API_KEY", "fake-test-key")
    posts = 0
    def handler(request):
        nonlocal posts
        if request.method == "GET":
            return httpx.Response(200, json={"id": MODEL})
        posts += 1
        if outcome == "timeout":
            raise httpx.ReadTimeout("secret upstream payload", request=request)
        if outcome == "http_error":
            return httpx.Response(500, text="fake-test-key sensitive provider error")
        result = completion(usage=outcome != "missing_usage")
        if outcome == "invalid_candidates":
            result["choices"][0]["message"]["content"] = '{"candidates":[]}'
        return httpx.Response(200, json=result)
    report = await run_live(execute=True, spec=evidence, transport=httpx.MockTransport(handler), _ledger_path=ledger)
    assert all(record["status"] == "provider_or_contract_failure" for record in report["records"])
    assert all(record["token_usage"] == "unknown" for record in report["records"])
    assert posts == 1
    assert len(report["unrun_cases"]) == 1
    assert report["unrun_cases"][0]["mode"] == "rewrite"
    assert json.loads(ledger.read_text())["calls_reserved"] == 2
    assert Decimal(json.loads(ledger.read_text())["reserved_usd"]) > 0
    assert "sensitive provider error" not in json.dumps(report)


def test_missing_corrupt_and_existing_ledgers_never_mint_allowance(evidence, tmp_path, ledger):
    spec = validate_spec(evidence)
    missing = tmp_path / "missing.json"
    with pytest.raises(LiveBlocked, match="missing"):
        reserve_once(spec, _ledger_path=missing)
    assert not missing.exists()
    ledger.write_text("truncated")
    with pytest.raises(LiveBlocked, match="unreadable"):
        reserve_once(spec, _ledger_path=ledger)
    with pytest.raises(LiveBlocked, match="already exists"):
        initialize_approval_ledger(_ledger_path=ledger)
    assert ledger.read_text() == "truncated"


def test_concurrent_reservations_share_one_approval(evidence, ledger):
    spec = validate_spec(evidence)
    def attempt():
        try:
            reserve_once(spec, _ledger_path=ledger)
            return "reserved"
        except LiveBlocked:
            return "blocked"
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: attempt(), range(2)))
    assert sorted(results) == ["blocked", "reserved"]


def test_copied_ledger_from_another_instance_is_rejected(evidence, ledger):
    saved = json.loads(ledger.read_text())
    saved["campaign_instance"] = "different-instance"
    ledger.write_text(json.dumps(saved))
    with pytest.raises(LiveBlocked, match="another instance"):
        reserve_once(validate_spec(evidence), _ledger_path=ledger)


def test_cli_has_no_reset_or_ledger_override_and_preserves_output(tmp_path, monkeypatch):
    output = tmp_path / "report.json"
    output.write_text("existing")
    monkeypatch.setattr(sys, "argv", ["live", "--output", str(output)])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    assert output.read_text() == "existing"
    monkeypatch.setattr(sys, "argv", ["live", "--reset", "--output", str(output)])
    with pytest.raises(SystemExit):
        main()


@pytest.mark.asyncio
async def test_accounting_bound_violation_stops_second_paid_call(evidence, ledger, monkeypatch):
    monkeypatch.setenv("PROOFREAD_OPENAI_API_KEY", "fake-test-key")
    calls = []
    def handler(request):
        calls.append(request.method)
        if request.method == "GET":
            return httpx.Response(200, json={"id": MODEL})
        response = completion()
        response["usage"] = {"prompt_tokens": 1001, "completion_tokens": 60, "total_tokens": 1061}
        return httpx.Response(200, json=response)
    report = await run_live(execute=True, spec=evidence, transport=httpx.MockTransport(handler), _ledger_path=ledger)
    assert calls == ["GET", "POST"]
    assert report["records"][0]["status"] == "accounting_bound_violation"
    saved = json.loads(ledger.read_text())
    assert saved["calls_reserved"] == 2
    assert saved["outcomes"] == report["records"]


@pytest.mark.asyncio
async def test_completed_outcome_is_durable_before_second_post(evidence, ledger, monkeypatch):
    monkeypatch.setenv("PROOFREAD_OPENAI_API_KEY", "fake-test-key")
    posts = 0
    def handler(request):
        nonlocal posts
        if request.method == "GET":
            return httpx.Response(200, json={"id": MODEL})
        assert len(json.loads(ledger.read_text())["outcomes"]) == posts
        posts += 1
        return httpx.Response(200, json=completion())
    report = await run_live(execute=True, spec=evidence, transport=httpx.MockTransport(handler), _ledger_path=ledger)
    assert json.loads(ledger.read_text())["outcomes"] == report["records"]


@pytest.mark.asyncio
@pytest.mark.parametrize("field,value", [("model", "other-model"), ("model", None),
                                        ("service_tier", "priority"), ("service_tier", None)])
async def test_unverified_response_model_or_tier_stops_second_call(evidence, ledger, monkeypatch, field, value):
    monkeypatch.setenv("PROOFREAD_OPENAI_API_KEY", "fake-test-key")
    posts = 0
    def handler(request):
        nonlocal posts
        if request.method == "GET":
            return httpx.Response(200, json={"id": MODEL})
        posts += 1
        result = completion()
        result[field] = value
        return httpx.Response(200, json=result)
    report = await run_live(execute=True, spec=evidence, transport=httpx.MockTransport(handler), _ledger_path=ledger)
    assert posts == 1
    assert report["records"][0]["status"] == "accounting_evidence_mismatch"
    assert json.loads(ledger.read_text())["calls_reserved"] == 2


def test_cli_unwritable_output_parent_prevents_execution(tmp_path, monkeypatch):
    from evaluation import live
    monkeypatch.setattr(sys, "argv", ["live", "--execute", "--output", str(tmp_path / "missing" / "out.json")])
    def forbidden(*args, **kwargs):
        pytest.fail("Execution must not start without writable output")
    monkeypatch.setattr(live.asyncio, "run", forbidden)
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2


def test_boot_identity_failure_is_safe(tmp_path, monkeypatch):
    from evaluation import live
    monkeypatch.setattr(live.sys, "platform", "linux")
    monkeypatch.setattr(live.Path, "read_text", lambda *args, **kwargs: "invalid-boot-id")
    with pytest.raises(LiveBlocked, match="identity"):
        initialize_approval_ledger(_ledger_path=tmp_path / "ledger.json")


def test_darwin_boot_identity_uses_bounded_sysctl(monkeypatch):
    from evaluation import live
    monkeypatch.setattr(live.sys, "platform", "darwin")
    def fake_sysctl(command, **kwargs):
        assert command == ["/usr/sbin/sysctl", "-n", "kern.bootsessionuuid"]
        assert kwargs["check"] and kwargs["timeout"] == 5
        return SimpleNamespace(stdout="12345678-1234-1234-1234-123456789abc\n")
    monkeypatch.setattr(live.subprocess, "run", fake_sysctl)
    assert len(live._instance_fingerprint()) == 64


@pytest.mark.asyncio
@pytest.mark.parametrize("field,value", [("model", "other-model"), ("service_tier", "priority")])
async def test_malformed_candidates_cannot_hide_mismatched_accounting(evidence, ledger, monkeypatch, field, value):
    monkeypatch.setenv("PROOFREAD_OPENAI_API_KEY", "fake-test-key")
    posts = 0
    def handler(request):
        nonlocal posts
        if request.method == "GET":
            return httpx.Response(200, json={"id": MODEL})
        posts += 1
        result = completion()
        result[field] = value
        result["choices"][0]["message"]["content"] = '{"candidates":[]}'
        return httpx.Response(200, json=result)
    report = await run_live(execute=True, spec=evidence, transport=httpx.MockTransport(handler), _ledger_path=ledger)
    assert posts == 1
    assert report["records"][0]["status"] == "provider_or_contract_failure"
    assert len(report["unrun_cases"]) == 1
    assert json.loads(ledger.read_text())["calls_reserved"] == 2


@pytest.mark.asyncio
async def test_preflight_total_deadline_cancels_slow_stream_without_reservation(evidence, monkeypatch):
    from evaluation import live
    monkeypatch.setenv("PROOFREAD_OPENAI_API_KEY", "fake-test-key")
    monkeypatch.setattr(live, "_PREFLIGHT_TIMEOUT_SECONDS", 0.01)
    monkeypatch.setattr(live, "reserve_once", lambda *args, **kwargs: pytest.fail("Preflight must not reserve"))
    state = {"cancelled": False, "closed": False, "methods": []}

    class SlowMetadata(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b'{"id":'
            try:
                await asyncio.sleep(0.05)
            except asyncio.CancelledError:
                state["cancelled"] = True
                raise
            yield b'"wrong-model"}'

        async def aclose(self):
            state["closed"] = True

    def handler(request):
        state["methods"].append(request.method)
        return httpx.Response(200, stream=SlowMetadata())

    with pytest.raises(LiveBlocked, match="availability"):
        await run_live(execute=True, spec=evidence, transport=httpx.MockTransport(handler))
    assert state == {"cancelled": True, "closed": True, "methods": ["GET"]}


@pytest.mark.asyncio
async def test_preflight_oversized_body_stops_early_without_reservation(evidence, monkeypatch):
    from evaluation import live
    monkeypatch.setenv("PROOFREAD_OPENAI_API_KEY", "fake-test-key")
    monkeypatch.setattr(live, "reserve_once", lambda *args, **kwargs: pytest.fail("Preflight must not reserve"))
    state = {"chunks": 0, "closed": False, "methods": []}

    class OversizedMetadata(httpx.AsyncByteStream):
        async def __aiter__(self):
            for _ in range(100):
                state["chunks"] += 1
                yield b"x" * 4096

        async def aclose(self):
            state["closed"] = True

    def handler(request):
        state["methods"].append(request.method)
        return httpx.Response(200, stream=OversizedMetadata())

    with pytest.raises(LiveBlocked, match="availability"):
        await run_live(execute=True, spec=evidence, transport=httpx.MockTransport(handler))
    assert state["chunks"] == 17  # 64 KiB allowed; stop at the first excess chunk.
    assert state["closed"] and state["methods"] == ["GET"]


@pytest.mark.asyncio
async def test_preflight_refuses_compression_before_decoding_without_reservation(evidence, monkeypatch):
    from evaluation import live
    monkeypatch.setenv("PROOFREAD_OPENAI_API_KEY", "fake-test-key")
    monkeypatch.setattr(live, "reserve_once", lambda *args, **kwargs: pytest.fail("Preflight must not reserve"))
    state = {"read": False, "closed": False, "accept_encoding": None}

    class CompressedMetadata(httpx.AsyncByteStream):
        async def __aiter__(self):
            state["read"] = True
            yield b"invalid compressed bytes"

        async def aclose(self):
            state["closed"] = True

    def handler(request):
        assert request.method == "GET"
        state["accept_encoding"] = request.headers.get("accept-encoding")
        return httpx.Response(200, headers={"content-encoding": "gzip"}, stream=CompressedMetadata())

    with pytest.raises(LiveBlocked, match="availability"):
        await run_live(execute=True, spec=evidence, transport=httpx.MockTransport(handler))
    assert state == {"read": False, "closed": True, "accept_encoding": "identity"}


@pytest.mark.asyncio
@pytest.mark.parametrize("excess", [0, 1])
async def test_preflight_exact_size_boundary_before_reservation(evidence, monkeypatch, excess):
    from evaluation import live
    monkeypatch.setenv("PROOFREAD_OPENAI_API_KEY", "fake-test-key")
    reservations = []
    def reserve(*args, **kwargs):
        reservations.append(True)
        raise LiveBlocked("Reservation boundary reached")
    monkeypatch.setattr(live, "reserve_once", reserve)
    body = json.dumps({"id": MODEL}).encode()
    body += b" " * (65536 + excess - len(body))
    calls = []
    def handler(request):
        calls.append(request.method)
        return httpx.Response(200, content=body)
    message = "Reservation boundary" if excess == 0 else "availability"
    with pytest.raises(LiveBlocked, match=message):
        await run_live(execute=True, spec=evidence, transport=httpx.MockTransport(handler))
    assert len(reservations) == (1 if excess == 0 else 0)
    assert calls == ["GET"]


@pytest.mark.asyncio
async def test_preflight_transport_errors_do_not_expose_diagnostics_or_reserve(evidence, monkeypatch):
    from evaluation import live
    monkeypatch.setenv("PROOFREAD_OPENAI_API_KEY", "fake-test-key")
    monkeypatch.setattr(live, "reserve_once", lambda *args, **kwargs: pytest.fail("Preflight must not reserve"))
    def handler(request):
        raise httpx.ConnectError("fake-test-key upstream-secret-diagnostic", request=request)
    with pytest.raises(LiveBlocked, match="availability") as error:
        await run_live(execute=True, spec=evidence, transport=httpx.MockTransport(handler))
    rendered = "".join(traceback.format_exception(error.value))
    assert "upstream-secret-diagnostic" not in rendered
    assert "fake-test-key" not in rendered
