from __future__ import annotations

import logging

from fastapi import APIRouter, Body, HTTPException
from pydantic import ValidationError

from kj_atlas_api.models_context import (
    Ce4ResolveBundleRequest,
    Ce4ResolveBundleResponse,
    ContextBundleRequest,
    ContextBundleResponse,
    ContextQuery,
    ContextQueryValidationResponse,
    _canonical_bundle_hash_payload,
    _canonical_query_hash_payload,
    _sha256_canonical,
    build_ce4_resolved_bundle,
    build_bundle,
)

router = APIRouter(prefix="/context", tags=["context"])
logger = logging.getLogger(__name__)


def _validate_payload(model_type, payload: object):
    try:
        return model_type.model_validate(payload)
    except ValidationError as exc:
        if any(error.get("type") == "extra_forbidden" for error in exc.errors()):
            raise HTTPException(status_code=400, detail={"code": "unknown_contract_key"}) from exc
        raise HTTPException(status_code=400, detail=exc.errors()) from exc


@router.post("/query", response_model=ContextQueryValidationResponse)
def validate_context_query(payload: object = Body(...)) -> ContextQueryValidationResponse:
    query = _validate_payload(ContextQuery, payload)
    if not query.previewConfirmed:
        raise HTTPException(status_code=422, detail={"code": "preview_required"})

    query_hash = _sha256_canonical(_canonical_query_hash_payload(query))
    return ContextQueryValidationResponse(accepted=True, queryCanonicalHash=query_hash)


@router.post("/bundle", response_model=ContextBundleResponse)
def build_context_bundle(payload: object = Body(...)) -> ContextBundleResponse:
    request = _validate_payload(ContextBundleRequest, payload)
    try:
        response = build_bundle(request)
    except ValueError as exc:
        if str(exc) == "preview_required":
            raise HTTPException(status_code=422, detail={"code": "preview_required"}) from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    expected_bundle_hash = _sha256_canonical(_canonical_bundle_hash_payload(response))
    if response.bundleHash != expected_bundle_hash:
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
        if code == "dry_run_requires_no_side_effect":
            raise HTTPException(status_code=422, detail={"code": "dry_run_requires_no_side_effect"}) from exc
        raise HTTPException(status_code=400, detail=code) from exc

    if not (response.equivalenceKey and response.bundleHash):
        raise HTTPException(status_code=422, detail={"code": "equivalence_and_bundle_hash_required"})

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

    if request.dryRun and response.sideEffect != "none":
        raise HTTPException(status_code=422, detail={"code": "dry_run_requires_no_side_effect"})

    return response


@router.post("/bundles:resolve", response_model=Ce4ResolveBundleResponse)
def resolve_ce4_bundle(payload: object = Body(...)) -> Ce4ResolveBundleResponse:
    return _resolve_ce4_bundle_contract(payload)


@router.post("/v1/bundles:resolve", response_model=Ce4ResolveBundleResponse)
def resolve_ce4_bundle_v1(payload: object = Body(...)) -> Ce4ResolveBundleResponse:
    return _resolve_ce4_bundle_contract(payload)
