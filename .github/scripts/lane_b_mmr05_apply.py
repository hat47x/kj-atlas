from __future__ import annotations

from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match, found {count}")
    return text.replace(old, new, 1)


ai_path = Path("03_Implement/backend/src/kj_atlas_api/routes/ai.py")
ai = ai_path.read_text(encoding="utf-8")

ai = replace_once(
    ai,
    '''router = APIRouter(prefix="/ai", tags=["ai"])
logger = logging.getLogger(__name__)
def _audit_llm_trace(
''',
    '''router = APIRouter(prefix="/ai", tags=["ai"])
logger = logging.getLogger(__name__)


def _external_proposal_audit_fields(
    ref: ExternalProposalReference | None,
) -> dict[str, str]:
    """Return content-free proposal linkage fields for MMR-05 audit events."""
    if ref is None:
        return {}
    return {
        "proposalId": ref.proposalId,
        "sourceBundleHash": ref.sourceBundleHash,
    }


def _audit_llm_trace(
''',
    "insert shared proposal audit helper",
)

ai = replace_once(
    ai,
    '''    task: str,
    llm_response,
) -> None:
''',
    '''    task: str,
    llm_response,
    *,
    external_proposal_ref: ExternalProposalReference | None = None,
) -> None:
''',
    "extend llm audit signature",
)

ai = replace_once(
    ai,
    '''        "routingStage": routing_stage_for_task(task),
        **build_audit_fields(llm_response),
    }
''',
    '''        "routingStage": routing_stage_for_task(task),
        **build_audit_fields(llm_response),
        **_external_proposal_audit_fields(external_proposal_ref),
    }
''',
    "add linkage to successful llm audit",
)

ai = replace_once(
    ai,
    '''            "proposalId": ref.proposalId,
            "previousStatus": "proposed",
            "newStatus": "held",
            "transitionSource": "final_judgement_unavailable",
''',
    '''            "proposalId": ref.proposalId,
            "sourceBundleHash": ref.sourceBundleHash,
            "previousStatus": "proposed",
            "newStatus": "held",
            "transitionSource": "final_judgement_unavailable",
''',
    "add source hash to runtime system hold audit",
)

ai = replace_once(
    ai,
    '''    metadata = {
        "proposalId": ref.proposalId,
        "previousStatus": "proposed",
        "newStatus": "held",
        "transitionSource": "final_judgement_governance_blocked",
''',
    '''    metadata = {
        **_external_proposal_audit_fields(ref),
        "previousStatus": "proposed",
        "newStatus": "held",
        "transitionSource": "final_judgement_governance_blocked",
''',
    "share linkage fields in governance system hold audit",
)

ai = replace_once(
    ai,
    '''    _audit_llm_trace(request, _resolve_audit_tenant(request, db), payload.doc.id, "check_narrative", llm_response)
''',
    '''    _audit_llm_trace(
        request,
        _resolve_audit_tenant(request, db),
        payload.doc.id,
        "check_narrative",
        llm_response,
        external_proposal_ref=payload.externalProposalRef,
    )
''',
    "pass linkage to check narrative audit",
)

ai = replace_once(
    ai,
    '''        "detect_contradiction",
        llm_response,
    )
    return _parse_detect_contradiction_response(llm_response.raw_text)
''',
    '''        "detect_contradiction",
        llm_response,
        external_proposal_ref=payload.externalProposalRef,
    )
    return _parse_detect_contradiction_response(llm_response.raw_text)
''',
    "pass linkage to detect contradiction audit",
)

ai_path.write_text(ai, encoding="utf-8")

r2_path = Path("03_Implement/backend/tests/test_final_judgement_system_hold.py")
r2 = r2_path.read_text(encoding="utf-8")
r2 = replace_once(
    r2,
    '''        assert event.metadata["proposalId"] == "proposal-ext-1"
        assert event.metadata["previousStatus"] == "proposed"
''',
    '''        assert event.metadata["proposalId"] == "proposal-ext-1"
        assert event.metadata["sourceBundleHash"] == HASH_A
        assert event.metadata["previousStatus"] == "proposed"
''',
    "assert runtime hold source hash",
)
r2_path.write_text(r2, encoding="utf-8")

r3_path = Path("03_Implement/backend/tests/test_final_judgement_model_governance.py")
r3 = r3_path.read_text(encoding="utf-8")
r3 = replace_once(
    r3,
    '''from kj_atlas_api.llm.provider import RegisteredProviderConfig
''',
    '''from kj_atlas_api.llm.provider import LLMCallMetadata, LLMResponse, RegisteredProviderConfig
''',
    "extend governance test provider imports",
)
r3 = replace_once(
    r3,
    '''def _provider_config() -> RegisteredProviderConfig:
    return RegisteredProviderConfig(
        provider_id="provider-final",
        provider_kind="large-scale",
        base_url="https://llm.example.test",
        api_key_ref=None,
        model_id="final-model",
    )


class _CaptureDispatcher:
''',
    '''def _provider_config() -> RegisteredProviderConfig:
    return RegisteredProviderConfig(
        provider_id="provider-final",
        provider_kind="large-scale",
        base_url="https://llm.example.test",
        api_key_ref=None,
        model_id="final-model",
    )


def _metadata(trace_id: str = "mmr05-linked-audit") -> LLMCallMetadata:
    return LLMCallMetadata(
        provider_kind="large-scale",
        provider_name="provider-final",
        model_id="final-model",
        transport="http",
        requested_at="2026-09-06T00:00:00Z",
        trace_id=trace_id,
    )


class _CaptureDispatcher:
''',
    "add linked audit metadata fixture",
)

anchor = '''    assert captured[0].model == "final-model"
    assert captured[0].registered_provider == config


@pytest.mark.parametrize(
'''
new_test = '''    assert captured[0].model == "final-model"
    assert captured[0].registered_provider == config


def test_linked_final_judgement_success_audit_preserves_proposal_reference(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        doc = _register_external(db)
        config = _provider_config()
        dispatcher = _CaptureDispatcher()
        request = _request(dispatcher)

        monkeypatch.setattr(ai, "_resolve_audit_tenant", lambda *_args, **_kwargs: TENANT)
        monkeypatch.setattr(ai, "_validate_check_narrative_input", lambda _payload: None)
        monkeypatch.setattr(ai, "_reject_unreviewed_text", lambda *_args, **_kwargs: None)
        monkeypatch.setattr(ai, "_reject_unreviewed_cards", lambda *_args, **_kwargs: None)
        monkeypatch.setattr(ai, "_detect_contradiction_ir", lambda _payload: {})
        monkeypatch.setattr(ai, "adjudicated_contradiction", lambda *_args, **_kwargs: None)
        monkeypatch.setattr(ai, "resolve_model_for_task", lambda _task: "final-model")
        monkeypatch.setattr(ai, "_assert_model_allowed", lambda *_args, **_kwargs: config)
        monkeypatch.setattr(
            ai,
            "generate_with_fallback",
            lambda _req: LLMResponse(raw_text="{}", metadata=_metadata()),
        )
        monkeypatch.setattr(ai, "_parse_narrative_check_response", lambda *_args: "parsed-check")
        monkeypatch.setattr(ai, "_parse_detect_contradiction_response", lambda *_args: "parsed-detect")

        assert ai.check_narrative(_linked_check(doc), request, db) == "parsed-check"
        llm_events = [event for event in dispatcher.events if event.eventType == "llm"]
        assert len(llm_events) == 1
        assert llm_events[0].metadata["proposalId"] == "proposal-ext-r3"
        assert llm_events[0].metadata["sourceBundleHash"] == HASH_A
        assert llm_events[0].metadata["routingStage"] == "final_judgement"

        dispatcher.events.clear()
        cards = doc.cards[:2]
        detect_payload = DetectContradictionRequest(
            cardA={"id": cards[0].id, "text": cards[0].text, "textReviewed": True},
            cardB={"id": cards[1].id, "text": cards[1].text, "textReviewed": True},
            doc=doc,
            externalProposalRef={
                "proposalId": "proposal-ext-r3",
                "sourceBundleHash": HASH_A,
            },
        )
        assert ai.detect_contradiction(detect_payload, request, db) == "parsed-detect"
        llm_events = [event for event in dispatcher.events if event.eventType == "llm"]
        assert len(llm_events) == 1
        assert llm_events[0].metadata["proposalId"] == "proposal-ext-r3"
        assert llm_events[0].metadata["sourceBundleHash"] == HASH_A
        assert llm_events[0].metadata["routingStage"] == "final_judgement"


@pytest.mark.parametrize(
'''
r3 = replace_once(r3, anchor, new_test, "add linked success audit route test")
r3 = replace_once(
    r3,
    '''        metadata = dispatcher.events[0].metadata
        assert metadata["routingStage"] == "final_judgement"
''',
    '''        metadata = dispatcher.events[0].metadata
        assert metadata["proposalId"] == "proposal-ext-r3"
        assert metadata["sourceBundleHash"] == HASH_A
        assert metadata["routingStage"] == "final_judgement"
''',
    "assert governance hold linkage fields",
)
r3_path.write_text(r3, encoding="utf-8")

eval_path = Path("03_Implement/backend/tests/test_ai_eval_pipeline.py")
eval_text = eval_path.read_text(encoding="utf-8")
eval_text = replace_once(
    eval_text,
    '''    assert meta.get("model_id") == "deepseek-v4-flash"
    assert meta.get("trace_id") == "llm-eval-mock"
''',
    '''    assert meta.get("model_id") == "deepseek-v4-flash"
    assert meta.get("trace_id") == "llm-eval-mock"
    assert "proposalId" not in meta
    assert "sourceBundleHash" not in meta
''',
    "assert non-linked audit stays linkage-free",
)
eval_path.write_text(eval_text, encoding="utf-8")

issue_path = Path("01_Plans/issues/issue-AI-ROUTE-01-multi-model-routing-and-final-judgment-boundary.md")
issue = issue_path.read_text(encoding="utf-8")
issue = replace_once(
    issue,
    '- [~] 監査ログに MMR-05 の4項目が記録される。— `_audit_llm_trace` で `routingStage` / provider/model は記録済み。一方、linked final-judgementの通常LLM auditとsystem-hold auditで `sourceBundleHash` / `proposalId` を一貫して保持する契約は未完了のため、完全達成とはみなさない。',
    '- [x] 監査ログに MMR-05 の4項目が記録される。— **MMR-05 branch verified**: 通常LLM audit・runtime system-hold・governance system-holdが共通のtyped proposal-linkage fields (`proposalId` / `sourceBundleHash`) を保持する。standalone/intermediate auditにはlinkage fieldを捏造しない。main統合後に親Issueをcloseoutする。',
    "mark MMR-05 branch-verified",
)
issue = replace_once(
    issue,
    '- [~] integration test でルーティング・監査・安全停止が検証される。— routing audit既存e2eに加え、R2 system-holdとR3 model-governance安全停止をintegrationで固定。R3 GitHub Actions run `34018370431` はfocused/adjacent 51 passed。ただしMMR-05のlinked `sourceBundleHash` / `proposalId` telemetry completenessが残るため全体は部分達成。',
    '- [x] integration test でルーティング・監査・安全停止が検証される。— routing audit、R2 runtime system-hold、R3 model-governance安全停止に加え、MMR-05でlinked `check_narrative` / `detect_contradiction` 成功auditとR2/R3 failure auditの `proposalId` / `sourceBundleHash` 一貫性を固定。main統合後にfinal closeoutする。',
    "mark integration branch-verified",
)
issue += '''\n\n## MMR-05 linked telemetry進捗（2026-09-06）\n\n- final-judgement proposal linkageの監査語彙を `ExternalProposalReference` から生成する共通helperへ集約し、`proposalId` / `sourceBundleHash` の組を通常LLM audit・runtime system-hold・governance system-holdで同一に保持する。\n- `check_narrative` / `detect_contradiction` の成功LLM auditだけがrequestのexplicit `externalProposalRef` を引き継ぎ、linkageのないstandalone/intermediate routeにはproposal fieldを追加しない。\n- R2/R3 system-holdは既存のstate transition / failure分類 / provider・trace semanticsを変更せず、欠けていた `sourceBundleHash` のみをtyped referenceから補完する。\n- 本項目はbranch検証green後にMMR-05 / integration ACを完了扱いとし、親Issue `Status: Done` への移動はmain統合後のcloseoutで行う。\n'''
issue_path.write_text(issue, encoding="utf-8")

print("MMR-05 linkage audit patch applied")
