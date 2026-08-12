"""DX-DESIGN-CHECK-01: capability canary for check_design_consistency.py.

This does not test that the checker reports few warnings -- a checker that
reports nothing would pass such a test. It tests that the checker can still
tell distinct endpoints apart, which is the property that a warning count is
only meaningful on top of.

The defect this guards against: an earlier canonicalization rewrote every
kebab/snake path segment into a shared placeholder, so all ten /ai/* endpoints
became one token. The warning count fell, but so did the checker's ability to
notice a design document referencing an endpoint that api.md never documented.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "03_Implement" / "backend" / "scripts" / "check_design_consistency.py"


#: Names lifted out of the script for testing. Located by AST node name, so
#: inserting or reordering definitions in the script does not break this -- an
#: earlier text-slicing version broke the moment a helper was added between
#: two of these.
_WANTED = (
    "_PARAM_TOKEN_RE",
    "_strip_api_prefix",
    "_endpoint_segments",
    "endpoint_matches_documented",
)


def _load_matcher():
    """Load the pure matching helpers without running the script body.

    The script performs its checks at import time and calls sys.exit, so it
    cannot simply be imported. Its relevant definitions are selected from the
    parsed AST by name and compiled on their own.
    """
    tree = ast.parse(SCRIPT_PATH.read_text(encoding="utf-8"))
    selected: list[ast.stmt] = [ast.Import(names=[ast.alias(name="re", asname=None)])]
    found: set[str] = set()
    for node in tree.body:
        name = None
        if isinstance(node, ast.FunctionDef):
            name = node.name
        elif isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                name = target.id
        if name in _WANTED:
            selected.append(node)
            found.add(name)

    missing = set(_WANTED) - found
    assert not missing, (
        f"check_design_consistency.py no longer defines {sorted(missing)}. If these were "
        "renamed, update _WANTED -- do not delete this test, since it is what keeps the "
        "checker's discriminating power from regressing (DX-DESIGN-CHECK-01)."
    )

    module = ast.fix_missing_locations(ast.Module(body=selected, type_ignores=[]))
    namespace: dict[str, object] = {}
    exec(compile(module, str(SCRIPT_PATH), "exec"), namespace)  # noqa: S102 - our own repo script
    return namespace["endpoint_matches_documented"], namespace["_endpoint_segments"]


ENDPOINT_MATCHES, ENDPOINT_SEGMENTS = _load_matcher()


# Every AI endpoint defined in routes/ai.py. These are the ten that previously
# collapsed into a single token.
AI_ENDPOINTS = [
    "/ai/refine-card-text",
    "/ai/suggest-card-groups",
    "/ai/detect-contradiction",
    "/ai/assess-card-importance",
    "/ai/suggest-layout",
    "/ai/suggest-merges",
    "/ai/suggest-island-summary",
    "/ai/generate-narrative",
    "/ai/check-narrative",
    "/ai/suggest-document-title",
]


@pytest.mark.parametrize("endpoint", AI_ENDPOINTS)
def test_ai_endpoint_matches_only_itself(endpoint: str) -> None:
    """Each /ai/* endpoint must match itself and no sibling."""
    assert ENDPOINT_MATCHES(endpoint, endpoint)
    for other in AI_ENDPOINTS:
        if other != endpoint:
            assert not ENDPOINT_MATCHES(endpoint, other), (
                f"{endpoint} was treated as equivalent to {other}: the checker can no longer "
                "distinguish sibling AI endpoints, so a design document referencing an "
                "undocumented one would be silently accepted"
            )


def test_admin_and_bundle_reads_stay_distinct() -> None:
    """A tenant-admin access-control read must not look like an inquiry read.

    These two previously both degraded to a bare single placeholder, because
    every segment of each was kebab-case.
    """
    admin = "/tenant-admin/document-access/{doc_id}"
    inquiry = "/inquiry-bundles/{journey_id}"
    assert not ENDPOINT_MATCHES(admin, inquiry)
    assert not ENDPOINT_MATCHES(inquiry, admin)


def test_concrete_id_still_matches_a_declared_placeholder() -> None:
    """The false-positive suppression this replaced must still hold.

    A design document naming a concrete fixture document still has to match the
    documented parameterized route -- that is why the shape-guessing existed,
    and dropping it must not reintroduce those warnings.
    """
    assert ENDPOINT_MATCHES("/docs/e2e-qa-roundtrip", "/docs/{docId}")
    assert ENDPOINT_MATCHES("/docs/{doc_id}", "/docs/{docId}")
    assert ENDPOINT_MATCHES("/docs/doc-1/export-audit", "/docs/{docId}/export-audit")


def test_different_shapes_do_not_match() -> None:
    assert not ENDPOINT_MATCHES("/docs", "/docs/{docId}")
    assert not ENDPOINT_MATCHES("/docs/{docId}/export-audit", "/docs/{docId}")


def test_api_proxy_prefix_is_stripped_before_comparison() -> None:
    """The frontend's /api proxy prefix must not defeat matching.

    Added on main while this rewrite was in flight; kept here so the structural
    matcher cannot silently drop it.
    """
    assert ENDPOINT_MATCHES("/api/docs/{docId}", "/docs/{docId}")
    assert ENDPOINT_MATCHES("/api/ai/refine-card-text", "/ai/refine-card-text")
    # Stripping the prefix must not make distinct endpoints equal.
    assert not ENDPOINT_MATCHES("/api/ai/refine-card-text", "/ai/check-narrative")


def test_single_segment_endpoint_is_in_scope() -> None:
    """A one-segment path is a real collection endpoint, not a family prefix.

    The previous exclusion dropped anything with at most one slash, which took
    real endpoints out of the check entirely.
    """
    assert ENDPOINT_SEGMENTS("/docs") == ["docs"]
    assert ENDPOINT_MATCHES("/docs", "/docs")
    assert not ENDPOINT_MATCHES("/docs", "/query")
