from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from kj_atlas_api.llm.provider import (
    LLMCallMetadata,
    ProviderDisabledError,
    ProviderRequestError,
)
from kj_atlas_api.models import AIProposalDecisionStateRow, Base, DocumentV1
from kj_atlas_api.models_ai import (
    CheckNarrativeRequest,
    DetectContradictionRequest,
    ExternalProposalReference,
)
from kj_atlas_api.proposal_decision_repository import (
    ProposalSystemHoldReceipt,
    hold_external_proposal_for_final_judgement_failure,
    record_proposal_decision,
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


def _metadata(trace_id: str = "system-hold-test") -> LLMCallMetadata:
    return LLMCallMetadata(
        provider_kind="large-scale",
        provider_name="provider-final",
        model_id="final-model",
        transport="http",
        requested_at="2026-09-06T00:00:00Z",
        trace_id=trace_id,
    )


def _request(dispatcher=None):
    state = SimpleNamespace(audit_dispatcher=dispatcher)
    return SimpleNamespace(app=SimpleNamespace(state=state))


def _register_external(db: Session, *, proposal_id: str = "proposal-ext-1") -> DocumentV1:
    doc = _doc()
    register_external_agent_task(
        db,
        tenant=TENANT,
        task_id="task-ext-1",
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
        proposal_id=proposal_id,
        proposal_kind="narrative_draft",
        source_bundle_hash=HASH_A,
        task_id="task-ext-1",
        base_doc_signature=f"{doc.id}:base",
        query_canonical_hash=HASH_B,
        proposal_fingerprint=("c" if proposal_id.endswith("1") else "d") * 64,
    )
    db.commit()
    return doc


def _state(db: Session, doc_id: str, proposal_id: str = "proposal-ext-1"):
    return db.get(AIProposalDecisionStateRow, (TENANT.tenant_id, doc_id, proposal_id))


def test_repository_system_hold_is_proposed_only_and_idempotent() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        doc = _register_external(db)
        first = hold_external_proposal_for_final_judgement_failure(
            db,
            tenant=TENANT,
            doc_id=doc.id,
            proposal_id="proposal-ext-1",
            source_bundle_hash=HASH_A,
        )
        db.commit()
        assert first.transitioned is True
        assert first.status == "held"
        assert _state(db, doc.id).status == "held"

        second = hold_external_proposal_for_final_judgement_failure(
            db,
            tenant=TENANT,
            doc_id=doc.id,
            proposal_id="proposal-ext-1",
            source_bundle_hash=HASH_A,
        )
        assert second.transitioned is False
        assert second.status == "held"


def test_system_hold_never_rolls_back_human_accepted_decision() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        doc = _register_external(db)
        record_proposal_decision(
            db,
            tenant=TENANT,
            doc_id=doc.id,
            proposal_id="proposal-ext-1",
            source_bundle_hash=HASH_A,
            idempotency_key="human-adopt",
            decision="adopt",
            reviewer_ref="human-reviewer",
            reason=None,
            expected_origin="external_agent",
        )
        db.commit()

        receipt = hold_external_proposal_for_final_judgement_failure(
            db,
            tenant=TENANT,
            doc_id=doc.id,
            proposal_id="proposal-ext-1",
            source_bundle_hash=HASH_A,
        )
        assert receipt.transitioned is False
        assert receipt.status == "accepted"
        assert _state(db, doc.id).status == "accepted"


def test_recovery_uses_new_proposal_without_reopening_held() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        doc = _register_external(db)
        hold_external_proposal_for_final_judgement_failure(
            db,
            tenant=TENANT,
            doc_id=doc.id,
            proposal_id="proposal-ext-1",
            source_bundle_hash=HASH_A,
        )
        db.commit()
        assert _state(db, doc.id).status == "held"

        register_external_agent_proposal(
            db,
            tenant=TENANT,
            doc_id=doc.id,
            proposal_id="proposal-ext-2",
            proposal_kind="narrative_draft",
            source_bundle_hash=HASH_A,
            task_id="task-ext-1",
            base_doc_signature=f"{doc.id}:base",
            query_canonical_hash=HASH_B,
            proposal_fingerprint="d" * 64,
        )
        db.commit()
        assert _state(db, doc.id, "proposal-ext-1").status == "held"
        assert _state(db, doc.id, "proposal-ext-2") is None


class _CaptureDispatcher:
    def __init__(self) -> None:
        self.events = []

    def emit(self, event):
        self.events.append(event)


def test_linked_unavailable_holds_once_and_emits_system_audit(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        doc = _register_external(db)
        dispatcher = _CaptureDispatcher()
        request = _request(dispatcher)
        payload = CheckNarrativeRequest(
            doc=doc,
            narrativeText="draft",
            externalProposalRef=ExternalProposalReference(
                proposalId="proposal-ext-1", sourceBundleHash=HASH_A
            ),
        )
        monkeypatch.setattr(ai, "_resolve_audit_tenant", lambda *_args, **_kwargs: TENANT)
        monkeypatch.setattr(ai, "_validate_check_narrative_input", lambda _payload: None)
        monkeypatch.setattr(ai, "_reject_unreviewed_text", lambda *_args, **_kwargs: None)
        monkeypatch.setattr(
            ai,
            "generate_with_fallback",
            lambda _request: (_ for _ in ()).throw(
                ProviderDisabledError("final provider disabled", _metadata())
            ),
        )

        with pytest.raises(HTTPException) as exc:
            ai.check_narrative(payload, request, db)
        assert exc.value.status_code == 503
        assert _state(db, doc.id).status == "held"
        assert len(dispatcher.events) == 1
        event = dispatcher.events[0]
        assert event.eventType == "proposal"
        assert event.actorRefHash is None
        assert event.metadata["proposalId"] == "proposal-ext-1"
        assert event.metadata["previousStatus"] == "proposed"
        assert event.metadata["newStatus"] == "held"
        assert event.metadata["transitionSource"] == "final_judgement_unavailable"
        assert event.metadata["routingStage"] == "final_judgement"
        assert event.metadata["failureCode"] == "provider_unavailable"
        assert event.metadata["trace_id"] == "system-hold-test"

        with pytest.raises(HTTPException):
            ai.check_narrative(payload, request, db)
        assert len(dispatcher.events) == 1


def test_linked_timeout_holds_but_provider_validation_does_not(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        doc = _register_external(db)
        request = _request(_CaptureDispatcher())
        payload = CheckNarrativeRequest(
            doc=doc,
            narrativeText="draft",
            externalProposalRef={"proposalId": "proposal-ext-1", "sourceBundleHash": HASH_A},
        )
        monkeypatch.setattr(ai, "_resolve_audit_tenant", lambda *_args, **_kwargs: TENANT)
        monkeypatch.setattr(ai, "_validate_check_narrative_input", lambda _payload: None)
        monkeypatch.setattr(ai, "_reject_unreviewed_text", lambda *_args, **_kwargs: None)
        monkeypatch.setattr(
            ai,
            "generate_with_fallback",
            lambda _request: (_ for _ in ()).throw(
                ProviderRequestError.timeout("timeout", _metadata("timeout-trace"))
            ),
        )
        with pytest.raises(HTTPException) as exc:
            ai.check_narrative(payload, request, db)
        assert exc.value.status_code == 504
        assert _state(db, doc.id).status == "held"

    engine2 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine2)
    with Session(engine2) as db:
        doc = _register_external(db)
        request = _request(_CaptureDispatcher())
        payload = CheckNarrativeRequest(
            doc=doc,
            narrativeText="draft",
            externalProposalRef={"proposalId": "proposal-ext-1", "sourceBundleHash": HASH_A},
        )
        monkeypatch.setattr(
            ai,
            "generate_with_fallback",
            lambda _request: (_ for _ in ()).throw(
                ProviderRequestError.validation("bad response", _metadata("validation-trace"))
            ),
        )
        with pytest.raises(HTTPException) as exc:
            ai.check_narrative(payload, request, db)
        assert exc.value.status_code == 422
        assert _state(db, doc.id) is None


def test_standalone_unavailable_is_state_neutral(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = CheckNarrativeRequest(doc=_doc(), narrativeText="draft")
    monkeypatch.setattr(ai, "_validate_check_narrative_input", lambda _payload: None)
    monkeypatch.setattr(ai, "_reject_unreviewed_text", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        ai,
        "hold_external_proposal_for_final_judgement_failure",
        lambda *_args, **_kwargs: pytest.fail("standalone failure must not touch proposal state"),
    )
    monkeypatch.setattr(
        ai,
        "generate_with_fallback",
        lambda _request: (_ for _ in ()).throw(
            ProviderDisabledError("disabled", _metadata())
        ),
    )
    with pytest.raises(HTTPException) as exc:
        ai.check_narrative(payload, _request(), object())  # type: ignore[arg-type]
    assert exc.value.status_code == 503


def test_system_hold_retries_first_state_insert_race(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeDb:
        def __init__(self) -> None:
            self.commits = 0
            self.rollbacks = 0
        def commit(self) -> None:
            self.commits += 1
        def rollback(self) -> None:
            self.rollbacks += 1

    calls = 0
    def persist(*_args, **_kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise IntegrityError("insert", {}, Exception("concurrent first decision"))
        return ProposalSystemHoldReceipt(
            proposal_id="proposal-ext-1",
            status="accepted",
            transitioned=False,
            recorded_at="2026-09-06T00:00:01Z",
        )

    db = FakeDb()
    monkeypatch.setattr(ai, "_resolve_audit_tenant", lambda *_args, **_kwargs: TENANT)
    monkeypatch.setattr(ai, "hold_external_proposal_for_final_judgement_failure", persist)
    ai._hold_linked_external_proposal_after_final_judgement_failure(
        ExternalProposalReference(proposalId="proposal-ext-1", sourceBundleHash=HASH_A),
        doc_id="doc-1",
        request=_request(_CaptureDispatcher()),
        db=db,  # type: ignore[arg-type]
        exc=ProviderDisabledError("disabled", _metadata()),
    )
    assert calls == 2
    assert db.rollbacks == 1
    assert db.commits == 1


def test_detect_contradiction_linked_unavailable_holds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        doc = _register_external(db)
        cards = doc.cards[:2]
        payload = DetectContradictionRequest(
            cardA={"id": cards[0].id, "text": cards[0].text, "textReviewed": True},
            cardB={"id": cards[1].id, "text": cards[1].text, "textReviewed": True},
            doc=doc,
            externalProposalRef={
                "proposalId": "proposal-ext-1",
                "sourceBundleHash": HASH_A,
            },
        )
        monkeypatch.setattr(ai, "_resolve_audit_tenant", lambda *_args, **_kwargs: TENANT)
        monkeypatch.setattr(ai, "_reject_unreviewed_cards", lambda *_args, **_kwargs: None)
        monkeypatch.setattr(ai, "_detect_contradiction_ir", lambda _payload: {})
        monkeypatch.setattr(ai, "adjudicated_contradiction", lambda *_args, **_kwargs: None)
        monkeypatch.setattr(
            ai,
            "generate_with_fallback",
            lambda _request: (_ for _ in ()).throw(
                ProviderRequestError.unavailable(
                    "final provider unavailable", _metadata("detect-unavailable")
                )
            ),
        )

        with pytest.raises(HTTPException) as exc:
            ai.detect_contradiction(payload, _request(_CaptureDispatcher()), db)
        assert exc.value.status_code == 503
        assert _state(db, doc.id).status == "held"
