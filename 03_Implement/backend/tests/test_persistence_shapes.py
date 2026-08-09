from sqlalchemy import String, Text
from sqlalchemy.dialects import mysql
from sqlalchemy.schema import CreateTable

from kj_atlas_api.models import Base
from kj_atlas_api.persistence_shapes import (
    OIDC_AUDIENCE_MAX_CHARS,
    OIDC_ISSUER_MAX_CHARS,
    DataShape,
    PERSISTENT_TEXT_SPECS,
)


def test_every_persistent_string_column_has_an_explicit_data_shape() -> None:
    actual = {
        f"{table.name}.{column.name}"
        for table in Base.metadata.sorted_tables
        for column in table.columns
        if isinstance(column.type, String)
    }

    assert PERSISTENT_TEXT_SPECS.keys() == actual


def test_only_content_objects_are_unbounded_by_character_count() -> None:
    unbounded = {
        name for name, spec in PERSISTENT_TEXT_SPECS.items() if spec.proposed_max_chars is None
    }

    assert unbounded == {
        "documents.payload_json",
        "inquiry_bundles.payload_json",
        "merge_decision_logs.payload_json",
    }
    assert all(
        spec.shape is DataShape.CONTENT_OBJECT
        for name, spec in PERSISTENT_TEXT_SPECS.items()
        if name in unbounded
    )


def test_identifier_and_bounded_text_proposals_have_positive_limits() -> None:
    for spec in PERSISTENT_TEXT_SPECS.values():
        if spec.shape is not DataShape.CONTENT_OBJECT:
            assert spec.proposed_max_chars is not None
            assert spec.proposed_max_chars > 0


def test_catalog_drives_physical_bounded_types_without_bounding_content() -> None:
    for qualified_name, spec in PERSISTENT_TEXT_SPECS.items():
        table_name, column_name = qualified_name.split(".", 1)
        column_type = Base.metadata.tables[table_name].columns[column_name].type
        if spec.shape is DataShape.CONTENT_OBJECT:
            assert isinstance(column_type, Text)
            assert column_type.length is None
        else:
            assert isinstance(column_type, String)
            assert not isinstance(column_type, Text)
            assert column_type.length == spec.proposed_max_chars


def test_journey_identifier_preserves_the_existing_api_limit() -> None:
    assert PERSISTENT_TEXT_SPECS["inquiry_bundles.journey_id"].proposed_max_chars == 256


def test_oidc_lookup_key_bounds_fit_mysql_utf8mb4_composite_index() -> None:
    assert (
        PERSISTENT_TEXT_SPECS["identity_providers.issuer"].proposed_max_chars
        == OIDC_ISSUER_MAX_CHARS
    )
    assert (
        PERSISTENT_TEXT_SPECS["identity_providers.audience"].proposed_max_chars
        == OIDC_AUDIENCE_MAX_CHARS
    )
    assert (OIDC_ISSUER_MAX_CHARS + OIDC_AUDIENCE_MAX_CHARS) * 4 <= 3072


def test_mysql_uses_longtext_only_for_content_objects() -> None:
    documents_ddl = str(
        CreateTable(Base.metadata.tables["documents"]).compile(dialect=mysql.dialect())
    )
    assert "payload_json LONGTEXT" in documents_ddl
    assert "tenant_id VARCHAR(128)" in documents_ddl
    assert (
        PERSISTENT_TEXT_SPECS["inquiry_bundle_deletion_audit_events.journey_id"].proposed_max_chars
        == 256
    )
