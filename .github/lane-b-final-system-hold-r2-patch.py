from pathlib import Path

root = Path('.')
repo = root / '03_Implement/backend/src/kj_atlas_api/proposal_decision_repository.py'
route = root / '03_Implement/backend/src/kj_atlas_api/routes/ai.py'
issue = root / '01_Plans/issues/issue-AI-ROUTE-HELD-LINKAGE-01-link-final-judgement-failure-to-proposal-state.md'
api_doc = root / '02_Architecture/api.md'
test = root / '03_Implement/backend/tests/test_final_judgement_system_hold.py'


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'marker count={count} in {path}: {old[:120]!r}')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')


replace_once(
    repo,
    '''@dataclass(frozen=True, slots=True)\nclass ProposalDecisionReceipt:\n    event_id: str\n    proposal_id: str\n    status: str\n    recorded_at: str\n\n\n_DECISION_STATUS''',
    '''@dataclass(frozen=True, slots=True)\nclass ProposalDecisionReceipt:\n    event_id: str\n    proposal_id: str\n    status: str\n    recorded_at: str\n\n\n@dataclass(frozen=True, slots=True)\nclass ProposalSystemHoldReceipt:\n    proposal_id: str\n    status: str\n    transitioned: bool\n    recorded_at: str\n\n\n_DECISION_STATUS''',
)

replace_once(
    repo,
    '''\n\ndef record_proposal_decision(\n    db: Session,''',
    '''\n\ndef hold_external_proposal_for_final_judgement_failure(\n    db: Session,\n    *,\n    tenant: TenantContext,\n    doc_id: str,\n    proposal_id: str,\n    source_bundle_hash: str,\n) -> ProposalSystemHoldReceipt:\n    \"\"\"Atomically hold one explicitly linked external proposal.\n\n    Absence of a decision-state row is the canonical `proposed` state.  System\n    failure may create only `held`; it never rewrites an accepted/rejected row\n    and never fabricates a human decision event.  A concurrent first decision\n    can surface as IntegrityError on insert; the route retries after rollback so\n    the winning state is observed rather than overwritten.\n    \"\"\"\n    proposal = validate_external_proposal_reference(\n        db,\n        tenant=tenant,\n        doc_id=doc_id,\n        proposal_id=proposal_id,\n        source_bundle_hash=source_bundle_hash,\n    )\n    state = db.scalar(\n        select(AIProposalDecisionStateRow)\n        .where(\n            AIProposalDecisionStateRow.tenant_id == tenant.tenant_id,\n            AIProposalDecisionStateRow.doc_id == doc_id,\n            AIProposalDecisionStateRow.proposal_id == proposal_id,\n        )\n        .with_for_update()\n    )\n    if state is not None:\n        if state.source_bundle_hash != source_bundle_hash:\n            raise ProposalDecisionConflict(\"proposal source bundle does not match\")\n        if state.status not in {\"accepted\", \"rejected\", \"held\"}:\n            raise ProposalDecisionConflict(\"proposal has an unsupported decision state\")\n        return ProposalSystemHoldReceipt(\n            proposal_id=proposal.proposal_id,\n            status=state.status,\n            transitioned=False,\n            recorded_at=state.updated_at,\n        )\n\n    recorded_at = datetime.now(timezone.utc).isoformat()\n    db.add(\n        AIProposalDecisionStateRow(\n            tenant_id=tenant.tenant_id,\n            doc_id=doc_id,\n            proposal_id=proposal_id,\n            source_bundle_hash=source_bundle_hash,\n            status=\"held\",\n            version=1,\n            updated_at=recorded_at,\n        )\n    )\n    db.flush()\n    return ProposalSystemHoldReceipt(\n        proposal_id=proposal_id,\n        status=\"held\",\n        transitioned=True,\n        recorded_at=recorded_at,\n    )\n\n\ndef record_proposal_decision(\n    db: Session,''',
)

replace_once(
    route,
    '''    register_external_agent_task,\n    record_proposal_decision as persist_proposal_decision,\n    validate_external_proposal_reference,\n)''',
    '''    register_external_agent_task,\n    hold_external_proposal_for_final_judgement_failure,\n    record_proposal_decision as persist_proposal_decision,\n    validate_external_proposal_reference,\n)''',
)

replace_once(
    route,
    '''\n\ndef _assert_model_allowed(\n    request: Request,''',
    '''\n\n_FINAL_JUDGEMENT_SYSTEM_HOLD_FAILURES = frozenset({\n    \"provider_unavailable\",\n    \"provider_timeout\",\n})\n\n\ndef _final_judgement_system_hold_failure_code(\n    exc: ProviderDisabledError | ProviderRequestError,\n) -> str | None:\n    if isinstance(exc, ProviderDisabledError):\n        return \"provider_unavailable\"\n    if exc.code in _FINAL_JUDGEMENT_SYSTEM_HOLD_FAILURES:\n        return exc.code\n    return None\n\n\ndef _hold_linked_external_proposal_after_final_judgement_failure(\n    ref: ExternalProposalReference | None,\n    *,\n    doc_id: str,\n    request: Request,\n    db: Session,\n    exc: ProviderDisabledError | ProviderRequestError,\n) -> None:\n    \"\"\"Persist proposed->held before returning an availability failure.\n\n    The route has already validated the explicit linkage before provider use.\n    This helper re-validates inside the state transition transaction, retries a\n    first-state insert race once, and emits a content-free system audit event\n    only when this call actually changed proposed -> held.\n    \"\"\"\n    failure_code = _final_judgement_system_hold_failure_code(exc)\n    if ref is None or failure_code is None:\n        return\n\n    tenant = _resolve_audit_tenant(request, db)\n\n    def _persist():\n        return hold_external_proposal_for_final_judgement_failure(\n            db,\n            tenant=tenant,\n            doc_id=doc_id,\n            proposal_id=ref.proposalId,\n            source_bundle_hash=ref.sourceBundleHash,\n        )\n\n    try:\n        receipt = _persist()\n        db.commit()\n    except IntegrityError:\n        db.rollback()\n        try:\n            receipt = _persist()\n            db.commit()\n        except ProposalNotRegistered as retry_exc:\n            db.rollback()\n            raise HTTPException(status_code=404, detail=str(retry_exc)) from retry_exc\n        except (IntegrityError, ProposalDecisionConflict) as retry_exc:\n            db.rollback()\n            raise HTTPException(\n                status_code=409,\n                detail={\n                    \"code\": \"proposal_system_hold_conflicted\",\n                    \"message\": \"Proposal state changed while recording final-judgement hold.\",\n                },\n            ) from retry_exc\n    except ProposalNotRegistered as hold_exc:\n        db.rollback()\n        raise HTTPException(status_code=404, detail=str(hold_exc)) from hold_exc\n    except ProposalDecisionConflict as hold_exc:\n        db.rollback()\n        raise HTTPException(status_code=409, detail=str(hold_exc)) from hold_exc\n\n    if not receipt.transitioned:\n        return\n\n    metadata = build_audit_fields(exc)\n    metadata.update(\n        {\n            \"proposalId\": ref.proposalId,\n            \"previousStatus\": \"proposed\",\n            \"newStatus\": \"held\",\n            \"transitionSource\": \"final_judgement_unavailable\",\n            \"routingStage\": \"final_judgement\",\n            \"failureCode\": failure_code,\n        }\n    )\n    logger.warning(\n        \"proposal_system_held\",\n        extra={\n            \"proposalId\": ref.proposalId,\n            \"failureCode\": failure_code,\n            \"traceId\": metadata.get(\"trace_id\"),\n        },\n    )\n    dispatcher = getattr(request.app.state, \"audit_dispatcher\", None)\n    if dispatcher is not None:\n        dispatcher.emit(\n            build_event(\n                event_type=\"proposal\",\n                tenant_id=tenant.tenant_id,\n                doc_id=doc_id,\n                safe_mode=False,\n                metadata=metadata,\n            )\n        )\n\n\ndef _assert_model_allowed(\n    request: Request,''',
)

replace_once(
    route,
    '''    except ProviderDisabledError as exc:\n        _raise_llm_http_error(exc)\n    except ProviderRequestError as exc:\n        _raise_llm_http_error(exc)\n\n    _audit_llm_trace(request, _resolve_audit_tenant(request, db), payload.doc.id, \"check_narrative\", llm_response)''',
    '''    except ProviderDisabledError as exc:\n        _hold_linked_external_proposal_after_final_judgement_failure(\n            payload.externalProposalRef,\n            doc_id=payload.doc.id,\n            request=request,\n            db=db,\n            exc=exc,\n        )\n        _raise_llm_http_error(exc)\n    except ProviderRequestError as exc:\n        _hold_linked_external_proposal_after_final_judgement_failure(\n            payload.externalProposalRef,\n            doc_id=payload.doc.id,\n            request=request,\n            db=db,\n            exc=exc,\n        )\n        _raise_llm_http_error(exc)\n\n    _audit_llm_trace(request, _resolve_audit_tenant(request, db), payload.doc.id, \"check_narrative\", llm_response)''',
)

replace_once(
    route,
    '''    except ProviderDisabledError as exc:\n        _raise_llm_http_error(exc)\n    except ProviderRequestError as exc:\n        _raise_llm_http_error(exc)\n    # Unchanged for the two-card request shape (\"(no-doc)\"); a supplied document\n    # is now attributable in the audit trail.''',
    '''    except ProviderDisabledError as exc:\n        _hold_linked_external_proposal_after_final_judgement_failure(\n            payload.externalProposalRef,\n            doc_id=payload.doc.id if payload.doc is not None else \"(no-doc)\",\n            request=request,\n            db=db,\n            exc=exc,\n        )\n        _raise_llm_http_error(exc)\n    except ProviderRequestError as exc:\n        _hold_linked_external_proposal_after_final_judgement_failure(\n            payload.externalProposalRef,\n            doc_id=payload.doc.id if payload.doc is not None else \"(no-doc)\",\n            request=request,\n            db=db,\n            exc=exc,\n        )\n        _raise_llm_http_error(exc)\n    # Unchanged for the two-card request shape (\"(no-doc)\"); a supplied document\n    # is now attributable in the audit trail.''',
)

replace_once(issue, '- Status: Draft', '- Status: In Progress')
replace_once(
    issue,
    '- [ ] linkageなしのstandalone `check_narrative` / `detect_contradiction` failureがproposal stateを変更しないことを固定する。',
    '- [x] linkageなしのstandalone `check_narrative` / `detect_contradiction` failureがproposal stateを変更しないことを固定する。— R2 integration testでrepository非参照を固定。',
)
replace_once(
    issue,
    '- [ ] MMR-06対象failure classを列挙し、明示的にlinkされた `proposed` proposalだけをsystem `held` へatomic遷移させる。',
    '- [x] MMR-06対象failure classを列挙し、明示的にlinkされた `proposed` proposalだけをsystem `held` へatomic遷移させる。— `provider_unavailable` / `provider_timeout` / `ProviderDisabledError` のみ。`provider_validation`・policy/input/parse failureは対象外。',
)
replace_once(
    issue,
    '- [ ] system holdがhuman decisionと区別できるaudit/event contractを持つ。',
    '- [x] system holdがhuman decisionと区別できるaudit/event contractを持つ。— human decision rowを作らず `eventType=proposal` / `transitionSource=final_judgement_unavailable` のcontent-free auditを実遷移時だけ発行。',
)
replace_once(
    issue,
    '- [ ] `accepted` / `rejected` を巻き戻さず、既存 `held` / concurrent decisionを安全に扱う。',
    '- [x] `accepted` / `rejected` を巻き戻さず、既存 `held` / concurrent decisionを安全に扱う。— terminal/current stateはno-op、初回state insert競合はrollback後に再読。',
)
replace_once(
    issue,
    '- [ ] `held` 後の明示的recovery contractを選択・実装し、成功してもauto-accept / auto-publishしない。',
    '- [x] `held` 後の明示的recovery contractを選択・実装し、成功してもauto-accept / auto-publishしない。— 自動reopenは行わず、再試行は新しいproposal IDで登録する（選択肢3）。既存の認証済みhuman decisionによるheld→accepted/rejectedは維持。',
)
replace_once(
    issue,
    '- [ ] integration testで少なくとも provider unavailable、timeout、standalone call、already-decided race、recoveryを検証する。',
    '- [x] integration testで少なくとも provider unavailable、timeout、standalone call、already-decided race、recoveryを検証する。— R2 focused suiteで固定。',
)
issue.write_text(
    issue.read_text(encoding='utf-8').rstrip()
    + '''\n\n## R2 実装履歴（2026-09-06）\n\n- system hold対象を availability failure に限定: `ProviderDisabledError`, `provider_unavailable`, `provider_timeout`。`provider_validation` と入力/policy/parse failureはholdしない。\n- 明示link済みexternal proposalのstate rowが存在しない（=`proposed`）場合だけ `held` rowを作成する。accepted/rejected/heldはno-opで巻き戻さない。\n- proposedからの初回state insertがhuman decisionと競合した場合はIntegrityError後にtransactionをrollbackして再読し、勝ったstateを尊重する。\n- system holdはhuman `AIProposalDecisionEventRow` を作らず、`proposal` audit eventに `previousStatus`, `newStatus`, `transitionSource`, `routingStage`, provider/model/trace, failure codeをcontent-freeで記録する。既存heldへの反復failureでは重複system transition eventを出さない。\n- recoveryは「heldを自動reopenしない。再試行は新しいproposalを登録する」を採用する。既存human endpointがheldをaccepted/rejectedへ明示判断する能力は変更しない。\n- MMR-06親項目はcloseout/evidence同期が完了するまで未完了のままとする。\n''',
    encoding='utf-8',
)

api_text = api_doc.read_text(encoding='utf-8')
marker = '## Final-judgement system hold (AI-ROUTE-HELD-LINKAGE-01 R2)'
if marker not in api_text:
    api_doc.write_text(
        api_text.rstrip()
        + '''\n\n## Final-judgement system hold (AI-ROUTE-HELD-LINKAGE-01 R2)\n\nAn explicitly linked external proposal is changed from implicit `proposed` (no decision-state row) to `held` only when final judgement fails with `ProviderDisabledError`, `provider_unavailable`, or `provider_timeout`. `provider_validation`, request/policy rejection, and response parse/schema failure do not trigger system hold. A standalone final-judgement call without `externalProposalRef` never changes proposal state.\n\nThe state transition re-validates `(tenantId, docId, proposalId, sourceBundleHash, origin=external_agent)` inside the transaction. Existing `accepted`, `rejected`, or `held` state wins and is never overwritten. A concurrent first human decision is resolved by the decision-state primary key plus rollback/re-read; system failure cannot roll an accepted/rejected proposal back to held.\n\nSystem hold does not create a human proposal-decision event. On an actual `proposed -> held` transition, the audit dispatcher receives a content-free `eventType=proposal` event with `previousStatus=proposed`, `newStatus=held`, `transitionSource=final_judgement_unavailable`, `routingStage=final_judgement`, failure code, and available provider/model/transport/trace metadata. Repeated failure against an already-held proposal is idempotent and emits no second transition event.\n\nRecovery does not automatically reopen `held`. A retry that needs a fresh proposed lifecycle registers a new proposal ID; existing authenticated human decision behavior for a held proposal remains unchanged. Availability recovery alone never accepts or publishes a proposal.\n''',
        encoding='utf-8',
    )


test.write_text(r'''from __future__ import annotations

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
from kj_atlas_api.models_ai import CheckNarrativeRequest, ExternalProposalReference
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
''', encoding='utf-8')
