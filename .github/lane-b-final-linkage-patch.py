from pathlib import Path

root = Path('.')
models = root / '03_Implement/backend/src/kj_atlas_api/models_ai.py'
repo = root / '03_Implement/backend/src/kj_atlas_api/proposal_decision_repository.py'
route = root / '03_Implement/backend/src/kj_atlas_api/routes/ai.py'
api_doc = root / '02_Architecture/api.md'
schemas_doc = root / '02_Architecture/schemas.md'
issue = root / '01_Plans/issues/issue-AI-ROUTE-HELD-LINKAGE-01-link-final-judgement-failure-to-proposal-state.md'


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'marker not found in {path}: {old[:120]!r}')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'marker not unique in {path}: count={count} {old[:120]!r}')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')


replace_once(
    models,
    'class CheckNarrativeRequest(BaseModel):\n',
    '''class ExternalProposalReference(BaseModel):
    """Explicit identity for a registered external-agent proposal.

    Document identity is deliberately not carried here. Final-judgement routes
    bind this reference to the request document and validate the tuple
    server-side, so proposalId never becomes an implicit document lookup key.
    """

    model_config = ConfigDict(extra="forbid")

    proposalId: str = Field(min_length=1, max_length=128)
    sourceBundleHash: str = Field(pattern=SOURCE_BUNDLE_HASH_PATTERN)


class CheckNarrativeRequest(BaseModel):
''',
)
replace_once(
    models,
    '    basedOnReadingOrder: list[str] | None = None\n    # SEC-AI-SAFEMODE-01',
    '    basedOnReadingOrder: list[str] | None = None\n    # AI-ROUTE-HELD-LINKAGE-01 R1: optional explicit external proposal identity.\n    externalProposalRef: ExternalProposalReference | None = None\n    # SEC-AI-SAFEMODE-01',
)
replace_once(
    models,
    '''class DetectContradictionRequest(BaseModel):
    """Request to detect contradiction between two KJ-method cards."""

    model_config = ConfigDict(extra="forbid")

    cardA: _CardRef
    cardB: _CardRef
    # AI-IR-PROJECTION-01 (ADR-0069): optional canvas context. When supplied the
    # route builds the LLM input IR (`llm_input_ir_spec.md`) from it, so the
    # model finally sees `edges`, `islands`, `evidenceLinks` and
    # `contradictionState` instead of two bare texts. Optional on purpose: the
    # two-card request shape that shipped before stays valid (AC-11).
    doc: DocumentV1 | None = None
    # SEC-AI-SAFEMODE-01 (ADR-0068 D1=C/D3=A): optional, fail-closed relaxation.
    allowUnreviewedText: bool | None = None
''',
    '''class DetectContradictionRequest(BaseModel):
    """Request to detect contradiction between two KJ-method cards."""

    model_config = ConfigDict(extra="forbid")

    cardA: _CardRef
    cardB: _CardRef
    # AI-IR-PROJECTION-01 (ADR-0069): optional canvas context. When supplied the
    # route builds the LLM input IR (`llm_input_ir_spec.md`) from it, so the
    # model finally sees `edges`, `islands`, `evidenceLinks` and
    # `contradictionState` instead of two bare texts. Optional on purpose: the
    # two-card request shape that shipped before stays valid (AC-11).
    doc: DocumentV1 | None = None
    # AI-ROUTE-HELD-LINKAGE-01 R1: linkage requires doc so the server never
    # infers document identity from proposalId.
    externalProposalRef: ExternalProposalReference | None = None
    # SEC-AI-SAFEMODE-01 (ADR-0068 D1=C/D3=A): optional, fail-closed relaxation.
    allowUnreviewedText: bool | None = None
''',
)

replace_once(
    repo,
    '\n\ndef record_proposal_decision(\n',
    '''

def validate_external_proposal_reference(
    db: Session,
    *,
    tenant: TenantContext,
    doc_id: str,
    proposal_id: str,
    source_bundle_hash: str,
) -> AIProposalRow:
    """Resolve an external proposal only by its explicit document-local identity.

    This is intentionally read-only. MMR-06 state transitions are a later
    contract; R1 only proves which proposal a final-judgement call refers to.
    """
    apply_database_tenant_context(db=db, tenant=tenant)
    proposal = db.get(AIProposalRow, (tenant.tenant_id, doc_id, proposal_id))
    if proposal is None:
        raise ProposalNotRegistered("external proposal is not registered for this document")
    if proposal.origin != "external_agent":
        raise ProposalDecisionConflict("proposal is not an external-agent proposal")
    if proposal.source_bundle_hash != source_bundle_hash:
        raise ProposalDecisionConflict("external proposal source bundle does not match")
    return proposal


def record_proposal_decision(
''',
)

replace_once(
    route,
    '    ExternalAgentProposalDecisionRequest,\n',
    '    ExternalAgentProposalDecisionRequest,\n    ExternalProposalReference,\n',
)
replace_once(
    route,
    '    record_proposal_decision as persist_proposal_decision,\n',
    '    record_proposal_decision as persist_proposal_decision,\n    validate_external_proposal_reference,\n',
)
replace_once(
    route,
    '\n\ndef _assert_model_allowed(\n',
    '''

def _validate_final_judgement_external_proposal(
    ref: ExternalProposalReference | None,
    *,
    doc_id: str,
    request: Request,
    db: Session,
) -> None:
    """Reject an invalid explicit proposal link before provider execution."""
    if ref is None:
        return
    tenant = _resolve_audit_tenant(request, db)
    try:
        validate_external_proposal_reference(
            db,
            tenant=tenant,
            doc_id=doc_id,
            proposal_id=ref.proposalId,
            source_bundle_hash=ref.sourceBundleHash,
        )
    except ProposalNotRegistered as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProposalDecisionConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


def _assert_model_allowed(
''',
)
replace_once(
    route,
    '''    _validate_check_narrative_input(payload)
    _reject_unreviewed_text(payload.doc, payload.allowUnreviewedText)

    try:
''',
    '''    _validate_check_narrative_input(payload)
    _reject_unreviewed_text(payload.doc, payload.allowUnreviewedText)
    _validate_final_judgement_external_proposal(
        payload.externalProposalRef,
        doc_id=payload.doc.id,
        request=request,
        db=db,
    )

    try:
''',
)
replace_once(
    route,
    '''    _reject_unreviewed_cards([payload.cardA, payload.cardB], payload.allowUnreviewedText)

    # AI-IR-PROJECTION-01 (stage 1''',
    '''    _reject_unreviewed_cards([payload.cardA, payload.cardB], payload.allowUnreviewedText)

    if payload.externalProposalRef is not None:
        if payload.doc is None:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "external_proposal_document_required",
                    "message": "doc is required when externalProposalRef is supplied.",
                },
            )
        _validate_final_judgement_external_proposal(
            payload.externalProposalRef,
            doc_id=payload.doc.id,
            request=request,
            db=db,
        )

    # AI-IR-PROJECTION-01 (stage 1''',
)

api_marker = '## Final-judgement external proposal linkage (AI-ROUTE-HELD-LINKAGE-01 R1)'
api_text = api_doc.read_text(encoding='utf-8')
if api_marker not in api_text:
    api_doc.write_text(
        api_text.rstrip()
        + '\n\n'
        + api_marker
        + '''

`POST /ai/check-narrative` and `POST /ai/detect-contradiction` MAY carry `externalProposalRef`:

```json
{"proposalId":"<registered external proposal id>","sourceBundleHash":"<64-char sha256>"}
```

The field is optional so standalone final-judgement calls remain backward-compatible. When supplied, the server MUST bind it to the request document ID and validate `(tenantId, docId, proposalId)`, `origin=external_agent`, and `sourceBundleHash` before any provider request. The server MUST NOT infer a proposal or document from latest-created order, document similarity, or proposal content. `detect-contradiction` therefore requires `doc` whenever `externalProposalRef` is present. Missing registration returns 404; identity/source conflict returns 409; linkage without a document returns 422. R1 is read-only and does not itself transition proposal state.
''',
        encoding='utf-8',
    )

schema_marker = '## ExternalProposalReference（AI-ROUTE-HELD-LINKAGE-01 R1）'
schema_text = schemas_doc.read_text(encoding='utf-8')
if schema_marker not in schema_text:
    schemas_doc.write_text(
        schema_text.rstrip()
        + '\n\n'
        + schema_marker
        + '''

```text
ExternalProposalReference {
  proposalId: string(1..128)
  sourceBundleHash: sha256-hex(64)
}
```

`CheckNarrativeRequest.externalProposalRef` と `DetectContradictionRequest.externalProposalRef` は optional。参照自体に `docId` を持たせず、route payload の `doc.id` と server-side proposal row を照合する。これにより proposal ID を document lookup key として扱わない。
''',
        encoding='utf-8',
    )

issue_text = issue.read_text(encoding='utf-8')
old_ac = '- [ ] external proposal flowとfinal judgementの対象proposalを、推測なしで一意に結ぶtyped linkageをAPI/schemaへ固定する。'
new_ac = '- [x] external proposal flowとfinal judgementの対象proposalを、推測なしで一意に結ぶtyped linkageをAPI/schemaへ固定する。— R1: optional `externalProposalRef` + server-side `(tenant, doc, proposal, sourceBundleHash, origin)` validationを追加。'
if old_ac not in issue_text:
    raise SystemExit('linkage AC marker not found')
issue_text = issue_text.replace(old_ac, new_ac, 1)
issue_text = issue_text.rstrip() + '''

## R1 実装履歴（2026-09-06）

- `ExternalProposalReference` (`proposalId` + `sourceBundleHash`) を追加し、`check-narrative` / `detect-contradiction` に optional linkage として接続。
- serverはrequestの `doc.id` と登録済みproposal rowを照合し、external-agent origin / source hashまで一致した場合だけprovider処理へ進む。
- `detect-contradiction` でlinkageだけを渡してdocumentを省略することは禁止（422）。proposal IDからdocumentを逆引きしない。
- standalone呼出しのrequest shape/処理は維持。
- 本R1はread-only identity gateのみ。system `held` 遷移、failure class、system audit、recoveryは未実装であり、MMR-06は未完了のまま。
'''
issue.write_text(issue_text, encoding='utf-8')
