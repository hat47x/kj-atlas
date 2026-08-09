from dataclasses import replace

import pytest

from kj_atlas_api.generation_codec import (
    GenerationCodecError,
    canonical_json_bytes,
    encode_generation,
    restore_generation,
)
from kj_atlas_api.generation_policy import GenerationRetentionPolicy


def test_canonical_json_is_order_independent_and_rejects_nan() -> None:
    assert canonical_json_bytes({"b": 2, "a": "KJ"}) == canonical_json_bytes(
        {"a": "KJ", "b": 2}
    )
    with pytest.raises(GenerationCodecError, match="canonical JSON"):
        canonical_json_bytes({"value": float("nan")})


def test_small_change_uses_reversible_delta() -> None:
    base_value = {"cards": [{"id": str(i), "text": "observation" * 20} for i in range(100)]}
    base_bytes = canonical_json_bytes(base_value)
    base = encode_generation(base_value)
    changed = {"cards": list(base_value["cards"])}
    changed["cards"][50] = {"id": "50", "text": "changed"}

    encoded = encode_generation(
        changed,
        base_bytes=base_bytes,
        base_digest=base.content_digest,
        base_delta_depth=0,
    )

    assert encoded.representation == "gzip_delta"
    assert restore_generation(encoded, base_bytes=base_bytes) == canonical_json_bytes(changed)


def test_chain_limit_forces_full_snapshot() -> None:
    base = {"cards": ["a" * 1000]}
    base_bytes = canonical_json_bytes(base)
    encoded = encode_generation(
        {"cards": ["a" * 999 + "b"]},
        base_bytes=base_bytes,
        base_digest=encode_generation(base).content_digest,
        base_delta_depth=2,
        policy=GenerationRetentionPolicy(delta_chain_max_depth=2),
    )
    assert encoded.representation == "gzip_json"
    assert encoded.delta_depth == 0


def test_restore_fails_closed_for_wrong_base_and_tampering() -> None:
    base_value = {"cards": [{"id": str(i), "text": "observation" * 20} for i in range(100)]}
    changed = {"cards": list(base_value["cards"])}
    changed["cards"][50] = {"id": "50", "text": "changed"}
    base = canonical_json_bytes(base_value)
    encoded = encode_generation(
        changed,
        base_bytes=base,
        base_digest=__import__("hashlib").sha256(base).hexdigest(),
    )
    assert encoded.representation == "gzip_delta"
    with pytest.raises(GenerationCodecError):
        restore_generation(encoded, base_bytes=b"wrong")
    with pytest.raises(GenerationCodecError):
        restore_generation(replace(encoded, content_digest="0" * 64), base_bytes=base)
