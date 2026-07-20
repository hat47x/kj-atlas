import re
from pathlib import Path

from kj_atlas_api.models import DeterministicTieBreak, PolygonHandoffInputContract


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
FRONTEND_TYPES_PATH = REPOSITORY_ROOT / "03_Implement" / "frontend" / "src" / "domain" / "types.ts"
FRONTEND_VALIDATOR_PATH = REPOSITORY_ROOT / "03_Implement" / "frontend" / "src" / "domain" / "validate_doc.ts"
SCHEMAS_PATH = REPOSITORY_ROOT / "02_Architecture" / "schemas.md"


def _quoted_values(block: str) -> tuple[str, ...]:
    return tuple(re.findall(r'"([a-z_]+)"', block))


def _frontend_order() -> tuple[str, ...]:
    source = FRONTEND_TYPES_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"export const DOCUMENT_DETERMINISTIC_TIE_BREAK_ORDER = \[(?P<values>.*?)\] as const;",
        source,
        re.DOTALL,
    )
    assert match is not None
    return _quoted_values(match.group("values"))


def _schema_order() -> tuple[str, ...]:
    source = SCHEMAS_PATH.read_text(encoding="utf-8")
    match = re.search(r"deterministicTieBreakOrder: \[(?P<values>.*?)\];", source, re.DOTALL)
    assert match is not None
    return _quoted_values(match.group("values"))


def test_document_tie_break_order_stays_in_sync_across_contract_boundaries() -> None:
    frontend_order = _frontend_order()
    schema_order = _schema_order()
    document_model_order = tuple(DeterministicTieBreak.model_fields["order"].default)
    handoff_model_order = tuple(PolygonHandoffInputContract.model_fields["deterministicTieBreakOrder"].default)

    assert frontend_order == schema_order == document_model_order == handoff_model_order


def test_frontend_validator_consumes_the_shared_document_order() -> None:
    source = FRONTEND_VALIDATOR_PATH.read_text(encoding="utf-8")

    assert "DOCUMENT_DETERMINISTIC_TIE_BREAK_ORDER.length" in source
    assert "DOCUMENT_DETERMINISTIC_TIE_BREAK_ORDER.forEach" in source
    assert "const DETERMINISTIC_TIE_BREAK_ORDER" not in source
