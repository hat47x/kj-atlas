from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from kj_atlas_api.llm.provider import LLMCallMetadata, LLMResponse
from kj_atlas_api.models import Base, DocumentV1
from kj_atlas_api.models_ai import (
    CheckNarrativeRequest,
    DetectContradictionRequest,
    ExternalProposalReference,
)
from kj_atlas_api.proposal_decision_repository import (
    ProposalDecisionConflict,
    ProposalNotRegistered,
    register_ai_proposal,
    register_external_agent_proposal,
    register_external_agent_task,
    validate_external_proposal_reference,
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


def _ref() -> ExternalProposalReference:
    return ExternalProposalReference(proposalId="proposal-ext-1", sourceBundleHash=HASH_A)


def _metadata() -> LLMCallMetadata:
    return LLMCallMetadata(
        provider_kind="local",
        provider_name="local",
        model_id="default",
        transport="http",
        requested_at="2026-09-06T00:00:00Z",
        trace_id="linkage-test",
    )


def test_final_judgement_request_linkage_is_optional_and_typed() -> None:
    doc = _doc()
    standalone = CheckNarrativeRequest(doc=doc, narrativeText="draft")
    assert standalone.externalProposalRef is None

    linked = CheckNarrativeRequest(
        doc=doc,
        narrativeText="draft",
        externalProposalRef={"proposalId": "proposal-ext-1", "sourceBundleHash": HASH_A},
    )
    assert linked.externalProposalRef == _ref()

    with pytest.raises(Exception):
        ExternalProposalReference(
            proposalId="proposal-ext-1",
            sourceBundleHash="not-a-sha256",
        )


def test_repository_validates_external_proposal_by_doc_and_source() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        register_external_agent_task(
            db,
            tenant=TENANT,
            task_id="task-ext-1",
            doc_id="doc-1",
            base_doc_signature="doc-1:2026-09-06T00:00:00Z",
            source_bundle_hash=HASH_A,
            query_canonical_hash=HASH_B,
            task_kind="narrative_draft",
        )
        register_external_agent_proposal(
            db,
            tenant=TENANT,
            doc_id="doc-1",
            proposal_id="proposal-ext-1",
            proposal_kind="narrative_draft",
            source_bundle_hash=HASH_A,
            task_id="task-ext-1",
            base_doc_signature="doc-1:2026-09-06T00:00:00Z",
            query_canonical_hash=HASH_B,
            proposal_fingerprint="c" * 64,
        )
        db.commit()

        row = validate_external_proposal_reference(
            db,
            tenant=TENANT,
            doc_id="doc-1",
            proposal_id="proposal-ext-1",
            source_bundle_hash=HASH_A,
        )
        assert row.origin == "external_agent"

        with pytest.raises(ProposalNotRegistered):
            validate_external_proposal_reference(
                db,
                tenant=TENANT,
                doc_id="doc-other",
                proposal_id="proposal-ext-1",
                source_bundle_hash=HASH_A,
            )
        with pytest.raises(ProposalDecisionConflict):
            validate_external_proposal_reference(
                db,
                tenant=TENANT,
                doc_id="doc-1",
                proposal_id="proposal-ext-1",
                source_bundle_hash="d" * 64,
            )


def test_repository_rejects_internal_proposal_as_external_reference() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        register_ai_proposal(
            db,
            tenant=TENANT,
            doc_id="doc-1",
            proposal_id="proposal-internal-1",
            proposal_kind="island_summary",
            source_bundle_hash=HASH_A,
        )
        db.commit()
        with pytest.raises(ProposalDecisionConflict):
            validate_external_proposal_reference(
                db,
                tenant=TENANT,
                doc_id="doc-1",
                proposal_id="proposal-internal-1",
                source_bundle_hash=HASH_A,
            )


def test_check_narrative_invalid_linkage_stops_before_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = CheckNarrativeRequest(
        doc=_doc(), narrativeText="draft", externalProposalRef=_ref()
    )
    monkeypatch.setattr(ai, "_validate_check_narrative_input", lambda _payload: None)
    monkeypatch.setattr(ai, "_reject_unreviewed_text", lambda *_args, **_kwargs: None)

    def reject_link(*_args, **_kwargs):
        raise HTTPException(status_code=409, detail="linkage mismatch")

    monkeypatch.setattr(ai, "_validate_final_judgement_external_proposal", reject_link)
    monkeypatch.setattr(
        ai,
        "generate_with_fallback",
        lambda _request: pytest.fail("provider must not be called after linkage rejection"),
    )

    with pytest.raises(HTTPException) as exc:
        ai.check_narrative(payload, None, None)  # type: ignore[arg-type]
    assert exc.value.status_code == 409


def test_check_narrative_standalone_does_not_validate_repository_linkage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = CheckNarrativeRequest(doc=_doc(), narrativeText="draft")
    monkeypatch.setattr(ai, "_validate_check_narrative_input", lambda _payload: None)
    monkeypatch.setattr(ai, "_reject_unreviewed_text", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        ai,
        "validate_external_proposal_reference",
        lambda *_args, **_kwargs: pytest.fail(
            "standalone call must not query proposal linkage"
        ),
    )
    monkeypatch.setattr(
        ai,
        "generate_with_fallback",
        lambda _request: LLMResponse(raw_text='{"issues": []}', metadata=_metadata()),
    )
    monkeypatch.setattr(ai, "_resolve_audit_tenant", lambda *_args, **_kwargs: TENANT)
    monkeypatch.setattr(ai, "_audit_llm_trace", lambda *_args, **_kwargs: None)

    response = ai.check_narrative(payload, None, None)  # type: ignore[arg-type]
    assert response.issues == []


def test_detect_contradiction_linkage_requires_document_before_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = DetectContradictionRequest(
        cardA={"id": "a", "text": "A", "textReviewed": True},
        cardB={"id": "b", "text": "B", "textReviewed": True},
        externalProposalRef=_ref(),
    )
    monkeypatch.setattr(ai, "_reject_unreviewed_cards", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        ai,
        "generate_with_fallback",
        lambda _request: pytest.fail(
            "provider must not be called without linkage document"
        ),
    )

    with pytest.raises(HTTPException) as exc:
        ai.detect_contradiction(payload, None, None)  # type: ignore[arg-type]
    assert exc.value.status_code == 422
    assert exc.value.detail["code"] == "external_proposal_document_required"
