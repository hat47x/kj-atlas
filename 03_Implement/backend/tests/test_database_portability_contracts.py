from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from kj_atlas_api.models import Base, DocumentRow, TenantRow
from tests.database_portability_contracts import TIMESTAMP, verify_revision_dag_contract


def test_revision_dag_portability_contract_on_sqlite(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'revision-portability.sqlite3'}")
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as db:
            for tenant_id in ("tenant-a", "tenant-b"):
                db.add(
                    TenantRow(
                        id=tenant_id,
                        display_name=tenant_id,
                        lifecycle_state="active",
                        created_at=TIMESTAMP,
                        updated_at=TIMESTAMP,
                    )
                )
                db.add(
                    DocumentRow(
                        tenant_id=tenant_id,
                        id="shared",
                        version=1,
                        updated_at=TIMESTAMP,
                        payload_json="{}",
                    )
                )
            db.commit()

        verify_revision_dag_contract(engine)
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()
