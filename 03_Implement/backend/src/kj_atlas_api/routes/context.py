from __future__ import annotations

import logging

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import ValidationError

from kj_atlas_api.context_adapter import CONTEXT_FOUNDATION_ADAPTER
from kj_atlas_api.models_context import (
    Ce4ResolveBundleRequest,
    Ce4ResolveBundleResponse,
    ContextBundleRequest,
    ContextBundleResponse,
    ContextQuery,
    ContextQueryValidationResponse,
    build_ce4_resolved_bundle,
)
from kj_atlas_api.tenant_session_precondition import (
    require_tenant_scoped_api_precondition,
)

router = APIRouter(
    prefix="/context",
    tags=["context"],
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
logger = logging.getLogger(__name__)


def _validate_payload(model_type, payload: object):
    try:
        return model_type.model_validate(payload)
    except ValidationError as exc:
        errors = exc.errors(
            include_url=False,
            include_context=False,
            include_input=False,
        )
        if any(error.get("type") == "extra_forbidden" for error in errors):
            raise HTTPException(status_code=400, detail={"code": "unknown_contract_key"}) from exc
        if any("constraints" in error.get("loc", ()) for error in errors):
            raise HTTPException(status_code=400, detail={"code": "invalid_constraints"}) from exc
        raise HTTPException(status_code=400, detail=errors) from exc


@router.post("/query", response_model=ContextQueryValidationResponse)
def validate_context_query(payload: object = Body(...)) -> ContextQueryValidationResponse:
    query = _validate_payload(ContextQuery, payload)
    if not query.previewConfirmed:
        raise HTTPException(status_code=422, detail={"code": "preview_required"})

    query_hash = CONTEXT_FOUNDATION_ADAPTER.validate_query(query)
    return ContextQueryValidationResponse(accepted=True, queryCanonicalHash=query_hash)


@router.post("/bundle", response_model=ContextBundleResponse)
def build_context_bundle(payload: object = Body(...)) -> ContextBundleResponse:
    request = _validate_payload(ContextBundleRequest, payload)
    try:
        response = CONTEXT_FOUNDATION_ADAPTER.build_bundle(request)
    except ValueError as exc:
        if str(exc) == "preview_required":
            raise HTTPException(status_code=422, detail={"code": "preview_required"}) from exc
        logger.warning("context_bundle_build_failed", extra={"error": str(exc)}, exc_info=True)
        raise HTTPException(
            status_code=400, detail={"code": "invalid_context_bundle_request"}
        ) from exc

    if not CONTEXT_FOUNDATION_ADAPTER.verify_bundle_determinism(response):
        raise HTTPException(status_code=409, detail={"code": "nondeterministic_bundle"})

    logger.info(
        "context_bundle_generated",
        extra={
            "queryId": request.query.queryId,
            "bundleHash": response.bundleHash,
            "queryCanonicalHash": response.queryCanonicalHash,
            "excludedReason": response.excludedReason,
        },
    )
    return response


def _resolve_ce4_bundle_contract(payload: object = Body(...)) -> Ce4ResolveBundleResponse:
    request = _validate_payload(Ce4ResolveBundleRequest, payload)
    try:
        response = build_ce4_resolved_bundle(request)
    except ValueError as exc:
        code = str(exc)
        if code == "safe_mode_required":
            raise HTTPException(status_code=422, detail={"code": "safe_mode_required"}) from exc
        logger.warning("ce4_bundle_resolve_failed", extra={"error": code}, exc_info=True)
        raise HTTPException(status_code=400, detail={"code": "invalid_ce4_bundle_request"}) from exc

    if not (response.equivalenceKey and response.bundleHash):
        raise HTTPException(
            status_code=422, detail={"code": "equivalence_and_bundle_hash_required"}
        )

    if not response.queryCanonicalHash:
        raise HTTPException(status_code=422, detail={"code": "query_canonical_hash_required"})

    required_events = {
        "query": response.auditChain.query,
        "bundle": response.auditChain.bundle,
        "proposal": response.auditChain.proposal,
        "apply": response.auditChain.apply,
    }
    if any(not event.strip() for event in required_events.values()):
        raise HTTPException(status_code=422, detail={"code": "audit_chain_incomplete"})

    return response


@router.post("/bundles:resolve", response_model=Ce4ResolveBundleResponse)
def resolve_ce4_bundle(payload: object = Body(...)) -> Ce4ResolveBundleResponse:
    return _resolve_ce4_bundle_contract(payload)


@router.post("/v1/bundles:resolve", response_model=Ce4ResolveBundleResponse)
def resolve_ce4_bundle_v1(payload: object = Body(...)) -> Ce4ResolveBundleResponse:
    return _resolve_ce4_bundle_contract(payload)
