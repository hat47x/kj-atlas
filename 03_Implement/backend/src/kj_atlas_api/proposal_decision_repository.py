from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from uuid import uuid4

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from kj_atlas_api.models import (
    AIProposalDecisionEventRow,
    AIProposalDecisionStateRow,
    AIProposalRow,
    ExternalAgentTaskRow,
)
from kj_atlas_api.tenant_context import TenantContext
from kj_atlas_api.tenant_db_guard import apply_database_tenant_context


class ProposalDecisionConflict(RuntimeError):
    pass


class ProposalNotRegistered(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ProposalDecisionReceipt:
    event_id: str
    proposal_id: str
    status: str
    recorded_at: str


_DECISION_STATUS = {"adopt": "accepted", "reject": "rejected", "hold": "held"}


def register_external_agent_task(
    db: Session,
    *,
    tenant: TenantContext,
    task_id: str,
    doc_id: str,
    base_doc_signature: str,
    source_bundle_hash: str,
    query_canonical_hash: str,
    task_kind: str,
) -> None:
    apply_database_tenant_context(db=db, tenant=tenant)
    existing = db.get(ExternalAgentTaskRow, (tenant.tenant_id, task_id))
    expected = {
        "doc_id": doc_id,
        "base_doc_signature": base_doc_signature,
        "source_bundle_hash": source_bundle_hash,
        "query_canonical_hash": query_canonical_hash,
        "task_kind": task_kind,
        "provenance_level": "user_presented_unsigned",
    }
    if existing is not None:
        if any(getattr(existing, field) != value for field, value in expected.items()):
            raise ProposalDecisionConflict("external task id was already used")
        return
    db.add(
        ExternalAgentTaskRow(
            tenant_id=tenant.tenant_id,
            task_id=task_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            **expected,
        )
    )
    db.flush()


def register_ai_proposal(
    db: Session,
    *,
    tenant: TenantContext,
    doc_id: str,
    proposal_id: str,
    proposal_kind: str,
    source_bundle_hash: str,
) -> None:
    apply_database_tenant_context(db=db, tenant=tenant)
    db.add(
        AIProposalRow(
            tenant_id=tenant.tenant_id,
            doc_id=doc_id,
            proposal_id=proposal_id,
            proposal_kind=proposal_kind,
            source_bundle_hash=source_bundle_hash,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
    )
    db.flush()


def register_external_agent_proposal(
    db: Session,
    *,
    tenant: TenantContext,
    doc_id: str,
    proposal_id: str,
    proposal_kind: str,
    source_bundle_hash: str,
    task_id: str,
    base_doc_signature: str,
    query_canonical_hash: str,
    proposal_fingerprint: str,
) -> None:
    apply_database_tenant_context(db=db, tenant=tenant)
    task = db.get(ExternalAgentTaskRow, (tenant.tenant_id, task_id))
    if task is None:
        raise ProposalNotRegistered("external task is not registered")
    task_expected = {
        "doc_id": doc_id,
        "base_doc_signature": base_doc_signature,
        "source_bundle_hash": source_bundle_hash,
        "query_canonical_hash": query_canonical_hash,
    }
    if any(getattr(task, field) != value for field, value in task_expected.items()):
        raise ProposalDecisionConflict("external proposal does not match registered task")
    existing = db.get(AIProposalRow, (tenant.tenant_id, doc_id, proposal_id))
    expected = {
        "origin": "external_agent",
        "proposal_kind": proposal_kind,
        "source_bundle_hash": source_bundle_hash,
        "task_id": task_id,
        "base_doc_signature": base_doc_signature,
        "query_canonical_hash": query_canonical_hash,
        "proposal_fingerprint": proposal_fingerprint,
        "provenance_level": "user_presented_unsigned",
    }
    if existing is not None:
        if any(getattr(existing, field) != value for field, value in expected.items()):
            raise ProposalDecisionConflict("external proposal registration does not match")
        return
    db.add(
        AIProposalRow(
            tenant_id=tenant.tenant_id,
            doc_id=doc_id,
            proposal_id=proposal_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            **expected,
        )
    )
    db.flush()


def record_proposal_decision(
    db: Session,
    *,
    tenant: TenantContext,
    doc_id: str,
    proposal_id: str,
    source_bundle_hash: str,
    idempotency_key: str,
    decision: str,
    reviewer_ref: str,
    reason: str | None,
    expected_origin: str = "internal",
) -> ProposalDecisionReceipt:
    apply_database_tenant_context(db=db, tenant=tenant)
    status = _DECISION_STATUS[decision]
    reason_bytes = (reason or "").encode("utf-8")
    reason_digest = sha256(reason_bytes).hexdigest() if reason is not None else None

    proposal = db.get(AIProposalRow, (tenant.tenant_id, doc_id, proposal_id))
    if proposal is None:
        raise ProposalNotRegistered("proposal is not registered for this document")
    if proposal.origin != expected_origin:
        raise ProposalDecisionConflict("proposal origin does not match endpoint")
    if proposal.source_bundle_hash != source_bundle_hash:
        raise ProposalDecisionConflict("proposal source bundle does not match")

    existing = db.scalar(
        select(AIProposalDecisionEventRow).where(
            AIProposalDecisionEventRow.tenant_id == tenant.tenant_id,
            AIProposalDecisionEventRow.doc_id == doc_id,
            AIProposalDecisionEventRow.idempotency_key == idempotency_key,
        )
    )
    if existing is not None:
        if (
            existing.proposal_id != proposal_id
            or existing.source_bundle_hash != source_bundle_hash
            or existing.decision != status
            or existing.reviewer_ref != reviewer_ref
            or existing.reason_sha256 != reason_digest
            or existing.reason_utf8_bytes != len(reason_bytes)
        ):
            raise ProposalDecisionConflict("idempotency key was already used for another decision")
        return ProposalDecisionReceipt(
            event_id=existing.event_id,
            proposal_id=existing.proposal_id,
            status=existing.decision,
            recorded_at=existing.recorded_at,
        )

    state = db.scalar(
        select(AIProposalDecisionStateRow)
        .where(
            AIProposalDecisionStateRow.tenant_id == tenant.tenant_id,
            AIProposalDecisionStateRow.doc_id == doc_id,
            AIProposalDecisionStateRow.proposal_id == proposal_id,
        )
        .with_for_update()
    )
    if state is not None:
        if state.source_bundle_hash != source_bundle_hash:
            raise ProposalDecisionConflict("proposal source bundle does not match")
        if state.status in {"accepted", "rejected"}:
            raise ProposalDecisionConflict("proposal already has a terminal decision")
        if status == "held":
            raise ProposalDecisionConflict("proposal is already held")

    recorded_at = datetime.now(timezone.utc).isoformat()
    if state is None:
        db.add(
            AIProposalDecisionStateRow(
                tenant_id=tenant.tenant_id,
                doc_id=doc_id,
                proposal_id=proposal_id,
                source_bundle_hash=source_bundle_hash,
                status=status,
                version=1,
                updated_at=recorded_at,
            )
        )
    else:
        result = db.execute(
            update(AIProposalDecisionStateRow)
            .where(
                AIProposalDecisionStateRow.tenant_id == tenant.tenant_id,
                AIProposalDecisionStateRow.doc_id == doc_id,
                AIProposalDecisionStateRow.proposal_id == proposal_id,
                AIProposalDecisionStateRow.version == state.version,
            )
            .values(
                status=status,
                version=state.version + 1,
                updated_at=recorded_at,
            )
        )
        if result.rowcount != 1:
            raise ProposalDecisionConflict("proposal decision changed concurrently")

    event_id = f"proposal-decision-{uuid4()}"
    db.add(
        AIProposalDecisionEventRow(
            event_id=event_id,
            tenant_id=tenant.tenant_id,
            doc_id=doc_id,
            proposal_id=proposal_id,
            source_bundle_hash=source_bundle_hash,
            idempotency_key=idempotency_key,
            decision=status,
            reviewer_ref=reviewer_ref,
            proposal_origin=proposal.origin,
            provenance_level=proposal.provenance_level,
            reason_sha256=reason_digest,
            reason_utf8_bytes=len(reason_bytes),
            recorded_at=recorded_at,
        )
    )
    db.flush()
    return ProposalDecisionReceipt(
        event_id=event_id,
        proposal_id=proposal_id,
        status=status,
        recorded_at=recorded_at,
    )
