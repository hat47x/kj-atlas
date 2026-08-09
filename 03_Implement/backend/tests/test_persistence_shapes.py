from sqlalchemy import Text

from kj_atlas_api.models import Base
from kj_atlas_api.persistence_shapes import DataShape, PERSISTENT_TEXT_SPECS


def test_every_persistent_text_column_has_an_explicit_data_shape() -> None:
    actual = {
        f"{table.name}.{column.name}"
        for table in Base.metadata.sorted_tables
        for column in table.columns
        if isinstance(column.type, Text)
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
