"""`generate-narrative` の論理骨格を方式Bで保護する際の数値境界を固定する。

ここで確認するのは、現在の定数に対する決定論的なcharacterizationだけである。
プロバイダーが報告するトークン数や、方式Bを採用すべきかどうかは判定しない。
"""

from scripts.measure_ai_narrative_required_endpoint_pressure import measure


def _scenario(name: str) -> dict[str, object]:
    return next(item for item in measure()["scenarios"] if item["name"] == name)


def test_measurement_is_deterministic() -> None:
    assert measure() == measure()


def test_sparse_logical_skeleton_is_within_current_numeric_caps() -> None:
    result = _scenario("sparse-10-joints")

    assert result["logical_relation_count"] == 10
    assert result["required_endpoint_card_count"] == 20
    assert result["representative_text_chars"] == 920
    assert result["within_current_numeric_caps"] is True


def test_two_hundred_unique_endpoints_are_the_current_card_boundary() -> None:
    result = _scenario("card-cap-boundary-100-disjoint-joints")

    assert result["logical_relation_count"] == 100
    assert result["required_endpoint_card_count"] == 200
    assert result["representative_text_chars"] == 9200
    assert result["required_cards_fit"] is True
    assert result["required_relations_fit"] is True
    assert result["representative_text_fit"] is True


def test_two_hundred_two_unique_endpoints_exceed_the_current_card_cap() -> None:
    result = _scenario("card-cap-exceeded-101-disjoint-joints")

    assert result["logical_relation_count"] == 101
    assert result["required_endpoint_card_count"] == 202
    assert result["required_cards_fit"] is False
    assert result["required_relations_fit"] is True
    assert result["representative_text_fit"] is True
    assert result["within_current_numeric_caps"] is False


def test_relation_cap_can_fail_even_when_required_endpoints_fit() -> None:
    result = _scenario("relation-cap-exceeded-with-200-endpoints")

    assert result["required_endpoint_card_count"] == 200
    assert result["logical_relation_count"] == 401
    assert result["required_cards_fit"] is True
    assert result["required_relations_fit"] is False
    assert result["representative_text_fit"] is True
    assert result["within_current_numeric_caps"] is False


def test_document_wide_chain_exceeds_card_and_representative_text_caps() -> None:
    result = _scenario("document-wide-300-card-chain")

    assert result["logical_relation_count"] == 299
    assert result["required_endpoint_card_count"] == 300
    assert result["representative_text_chars"] == 13800
    assert result["required_cards_fit"] is False
    assert result["required_relations_fit"] is True
    assert result["representative_text_fit"] is False
    assert result["within_current_numeric_caps"] is False
