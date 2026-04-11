from __future__ import annotations

import logging

from fastapi import APIRouter, Body, HTTPException
from pydantic import ValidationError

from kj_atlas_api.models_context import (
    ContextBundleRequest,
    ContextBundleResponse,
    ContextQuery,
    ContextQueryValidationResponse,
    build_bundle,
)

router = APIRouter(prefix="/context", tags=["context"])
logger = logging.getLogger(__name__)


def _validate_payload(model_type, payload: object):
    try:
        return model_type.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=exc.errors()) from exc


@router.post("/query", response_model=ContextQueryValidationResponse)
def validate_context_query(payload: object = Body(...)) -> ContextQueryValidationResponse:
    query = _validate_payload(ContextQuery, payload)
    preview = {
        "scope": query.scope,
        "depth": query.depth,
        "reviewFilter": "reviewed_only" if query.reviewedOnly else "all",
        "safeMode": query.safeMode,
        "targetCount": len(query.targetCardIds),
    }
    return ContextQueryValidationResponse(query=query, preview=preview)


@router.post("/bundle", response_model=ContextBundleResponse)
def build_context_bundle(payload: object = Body(...)) -> ContextBundleResponse:
    request = _validate_payload(ContextBundleRequest, payload)
    response = build_bundle(request)
    for item in response.bundle.excludedReasons:
        logger.info(
            "context_bundle_excluded",
            extra={
                "queryId": request.query.queryId,
                "bundleHash": response.bundleHash,
                "excludedReason": item["reason"],
                "cardId": item["cardId"],
            },
        )
    return response
