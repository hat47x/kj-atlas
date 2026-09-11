from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"{label} target block drifted")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


store = Path("03_Implement/backend/src/kj_atlas_api/database_content_store.py")
replace_once(
    store,
    '''    def list_by_group(
        self, *, tenant: TenantContext, doc_id: str, group_id: str
    ) -> list[AppendOnlyLogContent]:
        rows = self._list(
            tenant=tenant,
            clauses=(
                MergeDecisionLogRow.doc_id == doc_id,
                MergeDecisionLogRow.group_id == group_id,
            ),
        )
        return [
            AppendOnlyLogContent(row=row, content=ContentBlob.from_text(row.payload_json))
            for row in rows
        ]

    def list_by_snapshot(
        self, *, tenant: TenantContext, doc_id: str, snapshot_version: str
    ) -> list[AppendOnlyLogContent]:
        rows = self._list(
            tenant=tenant,
            clauses=(
                MergeDecisionLogRow.doc_id == doc_id,
                MergeDecisionLogRow.snapshot_version == snapshot_version,
            ),
        )
        return [
            AppendOnlyLogContent(row=row, content=ContentBlob.from_text(row.payload_json))
            for row in rows
        ]

    def _list(
        self, *, tenant: TenantContext, clauses: tuple[object, ...]
    ) -> list[MergeDecisionLogRow]:
        apply_database_tenant_context(db=self._db, tenant=tenant)
        return list(
            self._db.scalars(
                select(MergeDecisionLogRow)
                .where(MergeDecisionLogRow.tenant_id == tenant.tenant_id, *clauses)
                .order_by(MergeDecisionLogRow.id.asc())
            ).all()
        )
''',
    '''    def list_by_group(
        self,
        *,
        tenant: TenantContext,
        doc_id: str,
        group_id: str,
        cursor: int | None = None,
        limit: int = 100,
    ) -> tuple[list[AppendOnlyLogContent], bool]:
        rows, has_more = self._list(
            tenant=tenant,
            clauses=(
                MergeDecisionLogRow.doc_id == doc_id,
                MergeDecisionLogRow.group_id == group_id,
            ),
            cursor=cursor,
            limit=limit,
        )
        return (
            [
                AppendOnlyLogContent(row=row, content=ContentBlob.from_text(row.payload_json))
                for row in rows
            ],
            has_more,
        )

    def list_by_snapshot(
        self,
        *,
        tenant: TenantContext,
        doc_id: str,
        snapshot_version: str,
        cursor: int | None = None,
        limit: int = 100,
    ) -> tuple[list[AppendOnlyLogContent], bool]:
        rows, has_more = self._list(
            tenant=tenant,
            clauses=(
                MergeDecisionLogRow.doc_id == doc_id,
                MergeDecisionLogRow.snapshot_version == snapshot_version,
            ),
            cursor=cursor,
            limit=limit,
        )
        return (
            [
                AppendOnlyLogContent(row=row, content=ContentBlob.from_text(row.payload_json))
                for row in rows
            ],
            has_more,
        )

    def _list(
        self,
        *,
        tenant: TenantContext,
        clauses: tuple[object, ...],
        cursor: int | None = None,
        limit: int = 100,
    ) -> tuple[list[MergeDecisionLogRow], bool]:
        """Return one bounded page in append order.

        SEC-DOC-BOUND-05: ``MergeDecisionLogRow.id`` is the server-owned,
        monotonic append key. ``cursor`` is the last id returned by the
        previous page. Reading ``limit + 1`` rows lets the route advertise a
        next cursor without an unbounded count query.
        """
        apply_database_tenant_context(db=self._db, tenant=tenant)
        query = select(MergeDecisionLogRow).where(
            MergeDecisionLogRow.tenant_id == tenant.tenant_id, *clauses
        )
        if cursor is not None:
            query = query.where(MergeDecisionLogRow.id > cursor)
        rows = list(
            self._db.scalars(
                query.order_by(MergeDecisionLogRow.id.asc()).limit(limit + 1)
            ).all()
        )
        has_more = len(rows) > limit
        return rows[:limit], has_more
''',
    "append-only store",
)

repo = Path("03_Implement/backend/src/kj_atlas_api/document_repository.py")
replace_once(
    repo,
    '''def list_merge_decision_logs_by_group(
    db: Session,
    *,
    tenant: TenantContext,
    doc_id: str,
    group_id: str,
) -> Sequence[MergeDecisionLogRow]:
    return [
        stored.row
        for stored in DatabaseAppendOnlyLogContentStore(db).list_by_group(
            tenant=tenant,
            doc_id=doc_id,
            group_id=group_id,
        )
    ]


def list_merge_decision_logs_by_snapshot(
    db: Session,
    *,
    tenant: TenantContext,
    doc_id: str,
    snapshot_version: str,
) -> Sequence[MergeDecisionLogRow]:
    return [
        stored.row
        for stored in DatabaseAppendOnlyLogContentStore(db).list_by_snapshot(
            tenant=tenant,
            doc_id=doc_id,
            snapshot_version=snapshot_version,
        )
    ]
''',
    '''def list_merge_decision_logs_by_group(
    db: Session,
    *,
    tenant: TenantContext,
    doc_id: str,
    group_id: str,
    cursor: int | None = None,
    limit: int = 100,
) -> tuple[list[MergeDecisionLogRow], bool]:
    stored_rows, has_more = DatabaseAppendOnlyLogContentStore(db).list_by_group(
        tenant=tenant,
        doc_id=doc_id,
        group_id=group_id,
        cursor=cursor,
        limit=limit,
    )
    return [stored.row for stored in stored_rows], has_more


def list_merge_decision_logs_by_snapshot(
    db: Session,
    *,
    tenant: TenantContext,
    doc_id: str,
    snapshot_version: str,
    cursor: int | None = None,
    limit: int = 100,
) -> tuple[list[MergeDecisionLogRow], bool]:
    stored_rows, has_more = DatabaseAppendOnlyLogContentStore(db).list_by_snapshot(
        tenant=tenant,
        doc_id=doc_id,
        snapshot_version=snapshot_version,
        cursor=cursor,
        limit=limit,
    )
    return [stored.row for stored in stored_rows], has_more
''',
    "document repository",
)

routes = Path("03_Implement/backend/src/kj_atlas_api/routes/docs.py")
replace_once(
    routes,
    '''def list_merge_decision_logs_by_group(
    doc_id: str,
    group_id: str,
    request: Request,
    x_read_only: str | None = Header(default=None, alias="X-Read-Only"),
    db: Session = Depends(get_db),
) -> list[MergeDecisionRecord]:
''',
    '''def list_merge_decision_logs_by_group(
    doc_id: str,
    group_id: str,
    request: Request,
    response: Response,
    cursor: int | None = Query(default=None, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    x_read_only: str | None = Header(default=None, alias="X-Read-Only"),
    db: Session = Depends(get_db),
) -> list[MergeDecisionRecord]:
''',
    "group route signature",
)
replace_once(
    routes,
    '''    rows = list_merge_log_rows_by_group(
        db,
        tenant=tenant,
        doc_id=doc_id,
        group_id=group_id,
    )
    return [MergeDecisionRecord.model_validate(json.loads(row.payload_json)) for row in rows]
''',
    '''    rows, has_more = list_merge_log_rows_by_group(
        db,
        tenant=tenant,
        doc_id=doc_id,
        group_id=group_id,
        cursor=cursor,
        limit=limit,
    )
    if has_more and rows:
        response.headers["X-Next-Cursor"] = str(rows[-1].id)
    return [MergeDecisionRecord.model_validate(json.loads(row.payload_json)) for row in rows]
''',
    "group route body",
)
replace_once(
    routes,
    '''def restore_merge_decision_logs(
    doc_id: str,
    snapshot_version: str,
    request: Request,
    x_read_only: str | None = Header(default=None, alias="X-Read-Only"),
    db: Session = Depends(get_db),
) -> list[MergeDecisionRecord]:
''',
    '''def restore_merge_decision_logs(
    doc_id: str,
    snapshot_version: str,
    request: Request,
    response: Response,
    cursor: int | None = Query(default=None, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    x_read_only: str | None = Header(default=None, alias="X-Read-Only"),
    db: Session = Depends(get_db),
) -> list[MergeDecisionRecord]:
''',
    "snapshot route signature",
)
replace_once(
    routes,
    '''    rows = list_merge_log_rows_by_snapshot(
        db,
        tenant=tenant,
        doc_id=doc_id,
        snapshot_version=snapshot_version,
    )
    return [MergeDecisionRecord.model_validate(json.loads(row.payload_json)) for row in rows]
''',
    '''    rows, has_more = list_merge_log_rows_by_snapshot(
        db,
        tenant=tenant,
        doc_id=doc_id,
        snapshot_version=snapshot_version,
        cursor=cursor,
        limit=limit,
    )
    if has_more and rows:
        response.headers["X-Next-Cursor"] = str(rows[-1].id)
    return [MergeDecisionRecord.model_validate(json.loads(row.payload_json)) for row in rows]
''',
    "snapshot route body",
)

Path("03_Implement/backend/tests/test_merge_decision_log_pagination.py").write_text(
    '''from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import Base


@pytest.fixture()
def client(tmp_path) -> Iterator[TestClient]:
    engine = create_engine(f"sqlite:///{tmp_path / 'merge-log-pagination.sqlite3'}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def _get_test_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_test_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _document(doc_id: str) -> dict:
    return {
        "version": 1,
        "id": doc_id,
        "title": "merge log pagination",
        "createdAt": "2026-09-10T00:00:00Z",
        "updatedAt": "2026-09-10T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [
            {"id": "card-1", "text": "alpha", "x": 0, "y": 0},
            {"id": "card-2", "text": "beta", "x": 100, "y": 0},
        ],
        "edges": [],
        "islands": [],
    }


def _record(index: int) -> dict:
    return {
        "decisionId": f"decision-page-{index}",
        "groupId": "group-page",
        "action": "defer",
        "selectedCardIds": ["card-1", "card-2"],
        "note": f"decision {index}",
        "decidedBy": "reviewer:opaque-1",
        "decidedAt": f"2026-09-10T00:0{index}:00Z",
        "snapshotVersion": "snap-page",
    }


def _seed(client: TestClient) -> str:
    doc_id = "doc-merge-log-pagination"
    response = client.put(f"/docs/{doc_id}", json=_document(doc_id))
    assert response.status_code == 200
    for index in range(1, 6):
        response = client.post(
            f"/docs/{doc_id}/merge-decision-logs",
            json={"record": _record(index)},
        )
        assert response.status_code == 201
    return doc_id


def _collect_three_pages(client: TestClient, url: str) -> list[str]:
    first = client.get(url, params={"limit": 2})
    assert first.status_code == 200
    assert [item["decisionId"] for item in first.json()] == [
        "decision-page-1",
        "decision-page-2",
    ]
    cursor1 = first.headers.get("x-next-cursor")
    assert cursor1 is not None

    second = client.get(url, params={"limit": 2, "cursor": cursor1})
    assert second.status_code == 200
    assert [item["decisionId"] for item in second.json()] == [
        "decision-page-3",
        "decision-page-4",
    ]
    cursor2 = second.headers.get("x-next-cursor")
    assert cursor2 is not None
    assert int(cursor2) > int(cursor1)

    third = client.get(url, params={"limit": 2, "cursor": cursor2})
    assert third.status_code == 200
    assert [item["decisionId"] for item in third.json()] == ["decision-page-5"]
    assert "x-next-cursor" not in third.headers

    return [
        *[item["decisionId"] for item in first.json()],
        *[item["decisionId"] for item in second.json()],
        *[item["decisionId"] for item in third.json()],
    ]


def test_by_group_keyset_pagination_is_bounded_and_gap_free(client: TestClient) -> None:
    doc_id = _seed(client)
    ids = _collect_three_pages(
        client, f"/docs/{doc_id}/merge-decision-logs/by-group/group-page"
    )
    assert ids == [f"decision-page-{index}" for index in range(1, 6)]
    assert len(ids) == len(set(ids))


def test_restore_keyset_pagination_is_bounded_and_gap_free(client: TestClient) -> None:
    doc_id = _seed(client)
    ids = _collect_three_pages(
        client, f"/docs/{doc_id}/merge-decision-logs/restore/snap-page"
    )
    assert ids == [f"decision-page-{index}" for index in range(1, 6)]
    assert len(ids) == len(set(ids))


def test_pagination_limits_are_validated_and_default_shape_stays_a_list(
    client: TestClient,
) -> None:
    doc_id = _seed(client)
    url = f"/docs/{doc_id}/merge-decision-logs/by-group/group-page"

    default_response = client.get(url)
    assert default_response.status_code == 200
    assert isinstance(default_response.json(), list)
    assert len(default_response.json()) == 5
    assert "x-next-cursor" not in default_response.headers

    assert client.get(url, params={"limit": 0}).status_code == 422
    assert client.get(url, params={"limit": 501}).status_code == 422
    assert client.get(url, params={"cursor": -1}).status_code == 422
''',
    encoding="utf-8",
)
