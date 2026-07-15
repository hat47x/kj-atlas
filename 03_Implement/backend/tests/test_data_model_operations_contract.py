from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DATA_MODEL_OVERVIEW = ROOT / "02_Architecture/data_model_operations_overview.md"
SCHEMAS = ROOT / "02_Architecture/schemas.md"
API = ROOT / "02_Architecture/api.md"
ADR_0033 = ROOT / "01_Plans/adr/ADR-0033-mvp-data-support-and-maintenance-boundary.md"
DATA_MODEL_ISSUE = (
    ROOT
    / "01_Plans/issues/"
    / "issue-DATA-MODEL-OPS-01-mvp-data-model-overview-and-crud-boundary.md"
)

SUPPORT_LEVELS = {"L1", "L1.5", "L2", "L2.5", "L3", "L0"}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _table_rows(text: str, required_header: str) -> list[list[str]]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("|") and required_header in line:
            rows: list[list[str]] = []
            for row in lines[index + 2 :]:
                if not row.startswith("|"):
                    break
                cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
                rows.append(cells)
            if rows:
                return rows
    raise AssertionError(f"missing markdown table: {required_header}")


def _find_row(rows: list[list[str]], label: str) -> list[str]:
    for row in rows:
        if label in row[0]:
            return row
    raise AssertionError(f"missing table row: {label}")


def test_crud_support_table_keeps_support_levels_and_owners() -> None:
    text = _read(DATA_MODEL_OVERVIEW)
    rows = _table_rows(text, "データ領域 | Support level")

    assert len(rows) >= 10
    for row in rows:
        assert len(row) >= 8
        data_area, support_level, create, read, update, delete, owner, note = row[:8]
        assert data_area
        assert support_level in SUPPORT_LEVELS
        assert create
        assert read
        assert update
        assert delete
        assert owner
        assert note

    expected_levels = {
        "Documentスナップショット": "L1",
        "Card / Edge": "L2",
        "EvidenceLink": "L2",
        "ReviewAttribution": "L2.5",
        "MergeDecisionRecord": "L1.5",
        "SimilarCandidateGroup": "L3",
        "ContextQuery / ContextBundle": "L2.5",
        "Export / Context audit event": "L3",
        "User / UserIdentity": "L1",
        "Import/Review Pack artifact": "L3",
    }
    for label, support_level in expected_levels.items():
        assert _find_row(rows, label)[1] == support_level


def test_document_v2_field_table_keeps_embedded_and_contract_boundaries() -> None:
    text = _read(DATA_MODEL_OVERVIEW)
    rows = _table_rows(text, "フィールド | Support level")

    expected_levels = {
        "`version` / `id` / `createdAt` / `updatedAt` / `transform`": "L1",
        "`cards[]`": "L2",
        "`edges[]`": "L2",
        "`islands[]`": "L2",
        "`evidenceLinks`": "L2",
        "`patchApplyLog`": "L2",
        "`mergeSuggestionDecisions`": "L2",
        "`critiqueInputs` / `reproposalDiffs`": "L2.5",
        "`reviewAttribution`": "L2.5",
        "`deterministicTieBreak`": "L2.5",
    }
    for label, support_level in expected_levels.items():
        row = _find_row(rows, label)
        assert row[1] == support_level
        assert row[4]
        assert row[5]


def test_data_model_contract_references_are_wired_across_design_docs() -> None:
    overview = _read(DATA_MODEL_OVERVIEW)
    schemas = _read(SCHEMAS)
    api = _read(API)
    adr = _read(ADR_0033)
    issue = _read(DATA_MODEL_ISSUE)

    for text in (overview, schemas, adr, issue):
        for support_level in SUPPORT_LEVELS:
            assert support_level in text

    for text in (schemas, api):
        assert "data_model_operations_overview.md" in text

    for token in (
        "個別CRUD",
        "型がある",
        "version gate",
        "`PUT /docs/{doc_id}`",
        "DATA-MAINT-01",
        "DATA-CONTRACT-01",
    ):
        assert token in overview

    assert "POST** `/docs`" in api
    assert "DATA-CONTRACT-01" in api
    assert "本書の型定義単体で運用保証を主張しない" in schemas
