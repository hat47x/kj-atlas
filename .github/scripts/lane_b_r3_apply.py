from __future__ import annotations

from pathlib import Path


AI_PATH = Path("03_Implement/backend/src/kj_atlas_api/routes/ai.py")
SYSTEM_HOLD_TEST = Path("03_Implement/backend/tests/test_final_judgement_system_hold.py")
LINKAGE_TEST = Path("03_Implement/backend/tests/test_final_judgement_proposal_linkage.py")
R3_TEST = Path("03_Implement/backend/tests/test_final_judgement_model_governance.py")


def replace_once(text: str, old: str, new: str, *, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor, found {count}")
    return text.replace(old, new, 1)


ai = AI_PATH.read_text(encoding="utf-8")
if "_FINAL_JUDGEMENT_GOVERNANCE_FAILURE_CODES" in ai:
    raise SystemExit("R3 source patch already present")

helper = r'''

_FINAL_JUDGEMENT_GOVERNANCE_FAILURE_CODES = {
    "model_not_allowed": "policy_rejected",
    "model_not_registered": "provider_unavailable",
    "model_provider_unavailable": "provider_unavailable",
}


def _final_judgement_governance_failure_code(
    exc: HTTPException,
) -> tuple[str, str] | None:
    """Map only the narrow model-governance failures admitted by R3.

    The HTTP response keeps its existing, specific governance code. Proposal
    audit uses the stable externalization reason vocabulary so policy rejection
    and execution unavailability remain distinguishable without treating an
    arbitrary 4xx/5xx as a system hold.
    """
    detail = exc.detail
    governance_code = detail.get("code") if isinstance(detail, dict) else None
    if not isinstance(governance_code, str):
        return None
    failure_code = _FINAL_JUDGEMENT_GOVERNANCE_FAILURE_CODES.get(governance_code)
    if failure_code is None:
        return None
    return failure_code, governance_code


def _hold_linked_external_proposal_after_final_judgement_governance_failure(
    ref: ExternalProposalReference | None,
    *,
    doc_id: str,
    request: Request,
    db: Session,
    exc: HTTPException,
    model_id: str,
) -> None:
    """Record R3 pre-provider governance/routing failure as a system hold.

    State transition remains explicit-link-only. Because provider dispatch has
    not happened yet, audit records the selected model and governance code but
    deliberately does not fabricate provider or trace metadata.
    """
    mapped = _final_judgement_governance_failure_code(exc)
    if ref is None or mapped is None:
        return
    failure_code, governance_code = mapped
    tenant = _resolve_audit_tenant(request, db)

    def _persist():
        return hold_external_proposal_for_final_judgement_failure(
            db,
            tenant=tenant,
            doc_id=doc_id,
            proposal_id=ref.proposalId,
            source_bundle_hash=ref.sourceBundleHash,
        )

    try:
        receipt = _persist()
        db.commit()
    except IntegrityError:
        db.rollback()
        try:
            receipt = _persist()
            db.commit()
        except ProposalNotRegistered as retry_exc:
            db.rollback()
            raise HTTPException(status_code=404, detail=str(retry_exc)) from retry_exc
        except (IntegrityError, ProposalDecisionConflict) as retry_exc:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "proposal_system_hold_conflicted",
                    "message": "Proposal state changed while recording final-judgement hold.",
                },
            ) from retry_exc
    except ProposalNotRegistered as hold_exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(hold_exc)) from hold_exc
    except ProposalDecisionConflict as hold_exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(hold_exc)) from hold_exc

    if not receipt.transitioned:
        return

    metadata = {
        "proposalId": ref.proposalId,
        "previousStatus": "proposed",
        "newStatus": "held",
        "transitionSource": "final_judgement_governance_blocked",
        "routingStage": "final_judgement",
        "failureCode": failure_code,
        "governanceCode": governance_code,
        "requestedModelId": model_id,
    }
    logger.warning(
        "proposal_system_held",
        extra={
            "proposalId": ref.proposalId,
            "failureCode": failure_code,
            "governanceCode": governance_code,
        },
    )
    dispatcher = getattr(request.app.state, "audit_dispatcher", None)
    if dispatcher is not None:
        dispatcher.emit(
            build_event(
                event_type="proposal",
                tenant_id=tenant.tenant_id,
                doc_id=doc_id,
                safe_mode=False,
                metadata=metadata,
            )
        )
'''
ai = replace_once(
    ai,
    "\ndef _assert_model_allowed(\n",
    helper + "\n\ndef _assert_model_allowed(\n",
    label="insert governance hold helper",
)

old_check = '''    try:\n        llm_response = generate_with_fallback(\n            LLMRequest(\n                task="check_narrative",\n                prompt=_build_narrative_check_prompt(payload),\n            )\n        )\n'''
new_check = '''    model_id = resolve_model_for_task("check_narrative")\n    try:\n        provider_config = _assert_model_allowed(request, db, model_id)\n    except HTTPException as exc:\n        _hold_linked_external_proposal_after_final_judgement_governance_failure(\n            payload.externalProposalRef,\n            doc_id=payload.doc.id,\n            request=request,\n            db=db,\n            exc=exc,\n            model_id=model_id,\n        )\n        raise\n\n    try:\n        llm_response = generate_with_fallback(\n            LLMRequest(\n                task="check_narrative",\n                prompt=_build_narrative_check_prompt(payload),\n                model=model_id,\n                registered_provider=provider_config,\n            )\n        )\n'''
ai = replace_once(ai, old_check, new_check, label="check_narrative governance")

old_detect = '''    try:\n        llm_response = generate_with_fallback(\n            LLMRequest(\n                task="detect_contradiction",\n                prompt=_build_detect_contradiction_prompt(payload, ir),\n                inputs=ir,\n            )\n        )\n'''
new_detect = '''    model_id = resolve_model_for_task("detect_contradiction")\n    try:\n        provider_config = _assert_model_allowed(request, db, model_id)\n    except HTTPException as exc:\n        _hold_linked_external_proposal_after_final_judgement_governance_failure(\n            payload.externalProposalRef,\n            doc_id=payload.doc.id if payload.doc is not None else "(no-doc)",\n            request=request,\n            db=db,\n            exc=exc,\n            model_id=model_id,\n        )\n        raise\n\n    try:\n        llm_response = generate_with_fallback(\n            LLMRequest(\n                task="detect_contradiction",\n                prompt=_build_detect_contradiction_prompt(payload, ir),\n                inputs=ir,\n                model=model_id,\n                registered_provider=provider_config,\n            )\n        )\n'''
ai = replace_once(ai, old_detect, new_detect, label="detect_contradiction governance")
AI_PATH.write_text(ai, encoding="utf-8")

# R2 tests intentionally exercise provider-runtime failure after governance has
# already succeeded. Keep that boundary explicit so R3 does not turn those
# tests into accidental registry-fixture tests.
system_hold = SYSTEM_HOLD_TEST.read_text(encoding="utf-8")
fixture_anchor = '''def _request(dispatcher=None):\n    state = SimpleNamespace(audit_dispatcher=dispatcher)\n    return SimpleNamespace(app=SimpleNamespace(state=state))\n\n\n'''
fixture = '''def _request(dispatcher=None):\n    state = SimpleNamespace(audit_dispatcher=dispatcher)\n    return SimpleNamespace(app=SimpleNamespace(state=state))\n\n\n@pytest.fixture(autouse=True)\ndef _r2_provider_failure_tests_start_after_governance(monkeypatch: pytest.MonkeyPatch) -> None:\n    monkeypatch.setattr(ai, "resolve_model_for_task", lambda _task: "final-model")\n    monkeypatch.setattr(ai, "_assert_model_allowed", lambda *_args, **_kwargs: None)\n\n\n'''
system_hold = replace_once(
    system_hold,
    fixture_anchor,
    fixture,
    label="R2 system-hold governance fixture",
)
SYSTEM_HOLD_TEST.write_text(system_hold, encoding="utf-8")

linkage = LINKAGE_TEST.read_text(encoding="utf-8")
linkage_anchor = '''TENANT = TenantContext(\n    tenant_id="local-default",\n    membership_id=None,\n    resolved_by="single_tenant_adapter",\n)\n\n\n'''
linkage_fixture = linkage_anchor + '''@pytest.fixture(autouse=True)\ndef _linkage_tests_do_not_own_model_governance(monkeypatch: pytest.MonkeyPatch) -> None:\n    monkeypatch.setattr(ai, "resolve_model_for_task", lambda _task: "final-model")\n    monkeypatch.setattr(ai, "_assert_model_allowed", lambda *_args, **_kwargs: None)\n\n\n'''
linkage = replace_once(
    linkage,
    linkage_anchor,
    linkage_fixture,
    label="proposal-linkage governance fixture",
)
LINKAGE_TEST.write_text(linkage, encoding="utf-8")

R3_TEST.write_text(r'''from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from kj_atlas_api.llm.provider import RegisteredProviderConfig
from kj_atlas_api.models import AIProposalDecisionStateRow, Base, DocumentV1
from kj_atlas_api.models_ai import CheckNarrativeRequest, DetectContradictionRequest
from kj_atlas_api.proposal_decision_repository import (
    register_external_agent_proposal,
    register_external_agent_task,
)
from kj_atlas_api.routes import ai
from kj_atlas_api.tenant_context import TenantContext


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "ai_eval_kj_document.json"
HASH_A = "a" * 64
HASH_B = "b" * 64
TENANT = TenantContext(
    tenant_id="local-default",
    membership_id=None,
    resolved_by="single_tenant_adapter",
)


def _doc() -> DocumentV1:
    return DocumentV1.model_validate(json.loads(FIXTURE_PATH.read_text(encoding="utf-8")))


def _request(dispatcher=None):
    return SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(audit_dispatcher=dispatcher)))


def _provider_config() -> RegisteredProviderConfig:
    return RegisteredProviderConfig(
        provider_id="provider-final",
        provider_kind="large-scale",
        base_url="https://llm.example.test",
        api_key_ref=None,
        model_id="final-model",
    )


class _CaptureDispatcher:
    def __init__(self) -> None:
        self.events = []

    def emit(self, event) -> None:
        self.events.append(event)


def _register_external(db: Session) -> DocumentV1:
    doc = _doc()
    register_external_agent_task(
        db,
        tenant=TENANT,
        task_id="task-ext-r3",
        doc_id=doc.id,
        base_doc_signature=f"{doc.id}:base",
        source_bundle_hash=HASH_A,
        query_canonical_hash=HASH_B,
        task_kind="narrative_draft",
    )
    register_external_agent_proposal(
        db,
        tenant=TENANT,
        doc_id=doc.id,
        proposal_id="proposal-ext-r3",
        proposal_kind="narrative_draft",
        source_bundle_hash=HASH_A,
        task_id="task-ext-r3",
        base_doc_signature=f"{doc.id}:base",
        query_canonical_hash=HASH_B,
        proposal_fingerprint="c" * 64,
    )
    db.commit()
    return doc


def _state(db: Session, doc_id: str):
    return db.get(AIProposalDecisionStateRow, (TENANT.tenant_id, doc_id, "proposal-ext-r3"))


def _linked_check(doc: DocumentV1) -> CheckNarrativeRequest:
    return CheckNarrativeRequest(
        doc=doc,
        narrativeText="draft",
        externalProposalRef={
            "proposalId": "proposal-ext-r3",
            "sourceBundleHash": HASH_A,
        },
    )


def test_check_narrative_governance_pins_selected_model_and_registered_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = CheckNarrativeRequest(doc=_doc(), narrativeText="draft")
    config = _provider_config()
    captured = []
    monkeypatch.setattr(ai, "_validate_check_narrative_input", lambda _payload: None)
    monkeypatch.setattr(ai, "_reject_unreviewed_text", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(ai, "resolve_model_for_task", lambda task: "final-model")
    monkeypatch.setattr(ai, "_assert_model_allowed", lambda _request, _db, model_id: config)
    monkeypatch.setattr(
        ai,
        "generate_with_fallback",
        lambda req: captured.append(req) or SimpleNamespace(raw_text="{}"),
    )
    monkeypatch.setattr(ai, "_audit_llm_trace", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(ai, "_parse_narrative_check_response", lambda *_args: "parsed")

    assert ai.check_narrative(payload, _request(), object()) == "parsed"  # type: ignore[arg-type]
    assert len(captured) == 1
    assert captured[0].model == "final-model"
    assert captured[0].registered_provider == config


def test_detect_contradiction_governance_pins_selected_model_and_registered_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    doc = _doc()
    cards = doc.cards[:2]
    payload = DetectContradictionRequest(
        cardA={"id": cards[0].id, "text": cards[0].text, "textReviewed": True},
        cardB={"id": cards[1].id, "text": cards[1].text, "textReviewed": True},
        doc=doc,
    )
    config = _provider_config()
    captured = []
    monkeypatch.setattr(ai, "_reject_unreviewed_cards", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(ai, "_detect_contradiction_ir", lambda _payload: {})
    monkeypatch.setattr(ai, "adjudicated_contradiction", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(ai, "resolve_model_for_task", lambda task: "final-model")
    monkeypatch.setattr(ai, "_assert_model_allowed", lambda _request, _db, model_id: config)
    monkeypatch.setattr(
        ai,
        "generate_with_fallback",
        lambda req: captured.append(req) or SimpleNamespace(raw_text="{}"),
    )
    monkeypatch.setattr(ai, "_audit_llm_trace", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(ai, "_parse_detect_contradiction_response", lambda *_args: "parsed")

    assert ai.detect_contradiction(payload, _request(), object()) == "parsed"  # type: ignore[arg-type]
    assert len(captured) == 1
    assert captured[0].model == "final-model"
    assert captured[0].registered_provider == config


@pytest.mark.parametrize(
    ("governance_code", "status_code", "failure_code"),
    [
        ("model_not_allowed", 403, "policy_rejected"),
        ("model_not_registered", 403, "provider_unavailable"),
        ("model_provider_unavailable", 503, "provider_unavailable"),
    ],
)
def test_linked_governance_failure_holds_before_provider_without_fake_trace(
    monkeypatch: pytest.MonkeyPatch,
    governance_code: str,
    status_code: int,
    failure_code: str,
) -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        doc = _register_external(db)
        dispatcher = _CaptureDispatcher()
        monkeypatch.setattr(ai, "_resolve_audit_tenant", lambda *_args, **_kwargs: TENANT)
        monkeypatch.setattr(ai, "_validate_check_narrative_input", lambda _payload: None)
        monkeypatch.setattr(ai, "_reject_unreviewed_text", lambda *_args, **_kwargs: None)
        monkeypatch.setattr(ai, "resolve_model_for_task", lambda _task: "final-model")
        monkeypatch.setattr(
            ai,
            "_assert_model_allowed",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(
                HTTPException(status_code=status_code, detail={"code": governance_code})
            ),
        )
        monkeypatch.setattr(
            ai,
            "generate_with_fallback",
            lambda _req: pytest.fail("governance failure must stop before provider dispatch"),
        )

        with pytest.raises(HTTPException) as exc:
            ai.check_narrative(_linked_check(doc), _request(dispatcher), db)
        assert exc.value.status_code == status_code
        assert _state(db, doc.id).status == "held"
        assert len(dispatcher.events) == 1
        metadata = dispatcher.events[0].metadata
        assert metadata["routingStage"] == "final_judgement"
        assert metadata["failureCode"] == failure_code
        assert metadata["governanceCode"] == governance_code
        assert metadata["requestedModelId"] == "final-model"
        assert "provider" not in metadata
        assert "trace_id" not in metadata


def test_standalone_governance_failure_is_state_neutral_and_provider_is_not_called(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = CheckNarrativeRequest(doc=_doc(), narrativeText="draft")
    monkeypatch.setattr(ai, "_validate_check_narrative_input", lambda _payload: None)
    monkeypatch.setattr(ai, "_reject_unreviewed_text", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(ai, "resolve_model_for_task", lambda _task: "final-model")
    monkeypatch.setattr(
        ai,
        "_assert_model_allowed",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            HTTPException(status_code=403, detail={"code": "model_not_allowed"})
        ),
    )
    monkeypatch.setattr(
        ai,
        "hold_external_proposal_for_final_judgement_failure",
        lambda *_args, **_kwargs: pytest.fail("standalone governance failure must not mutate proposal state"),
    )
    monkeypatch.setattr(
        ai,
        "generate_with_fallback",
        lambda _req: pytest.fail("governance rejection must stop before provider dispatch"),
    )

    with pytest.raises(HTTPException) as exc:
        ai.check_narrative(payload, _request(), object())  # type: ignore[arg-type]
    assert exc.value.status_code == 403
    assert exc.value.detail["code"] == "model_not_allowed"


def test_non_governance_http_error_is_not_classified_for_system_hold() -> None:
    assert ai._final_judgement_governance_failure_code(
        HTTPException(status_code=422, detail={"code": "unreviewed_text_not_allowed"})
    ) is None
    assert ai._final_judgement_governance_failure_code(
        HTTPException(status_code=409, detail="linkage mismatch")
    ) is None
''', encoding="utf-8")

print("R3 patch applied")
