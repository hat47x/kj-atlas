from __future__ import annotations

from typing import Protocol

from kj_atlas_api.models_context import (
    ContextBundleRequest,
    ContextBundleResponse,
    ContextQuery,
    _canonical_bundle_hash_payload,
    _canonical_query_hash_payload,
    _sha256_canonical,
    build_bundle,
)


class ContextFoundationAdapter(Protocol):
    """Adapter boundary for CE foundation contract operations."""

    def validate_query(self, query: ContextQuery) -> str: ...

    def build_bundle(self, request: ContextBundleRequest) -> ContextBundleResponse: ...

    def verify_bundle_determinism(self, response: ContextBundleResponse) -> bool: ...


class MockContextFoundationAdapter:
    """Mock-first adapter for frozen ContextQuery/ContextBundle v1 contracts."""

    def validate_query(self, query: ContextQuery) -> str:
        return _sha256_canonical(_canonical_query_hash_payload(query))

    def build_bundle(self, request: ContextBundleRequest) -> ContextBundleResponse:
        return build_bundle(request)

    def verify_bundle_determinism(self, response: ContextBundleResponse) -> bool:
        expected_bundle_hash = _sha256_canonical(_canonical_bundle_hash_payload(response))
        return response.bundleHash == expected_bundle_hash


CONTEXT_FOUNDATION_ADAPTER: ContextFoundationAdapter = MockContextFoundationAdapter()
