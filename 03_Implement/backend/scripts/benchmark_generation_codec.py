from __future__ import annotations

import json
import time

from kj_atlas_api.generation_codec import canonical_json_bytes, encode_generation, restore_generation


def document(cards: list[dict[str, object]], generation: int) -> dict[str, object]:
    return {
        "id": "generation-benchmark",
        "version": 1,
        "updatedAt": f"2026-08-10T00:{generation % 60:02d}:00Z",
        "cards": cards,
        "edges": [],
        "islands": [],
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
    }


def main() -> None:
    cards: list[dict[str, object]] = [
        {
            "id": f"card-{index:04d}",
            "text": (f"観察内容 {index} ") * 18,
            "x": (index % 30) * 40,
            "y": (index // 30) * 30,
            "claimType": "unknown",
        }
        for index in range(300)
    ]
    blobs = []
    canonical_generations = []
    base = None
    base_digest = None
    depth = 0
    encode_started = time.perf_counter()
    for generation in range(100):
        for offset in range(5):
            index = (generation * 7 + offset * 31) % len(cards)
            cards[index] = {
                **cards[index],
                "text": f"世代{generation} 更新{offset} " + str(cards[index]["text"])[-160:],
            }
        value = document(cards, generation)
        canonical = canonical_json_bytes(value)
        blob = encode_generation(
            value,
            base_bytes=base,
            base_digest=base_digest,
            base_delta_depth=depth,
        )
        blobs.append(blob)
        canonical_generations.append(canonical)
        base, base_digest, depth = canonical, blob.content_digest, blob.delta_depth
    encode_ms = (time.perf_counter() - encode_started) * 1000

    restore_started = time.perf_counter()
    restored = None
    for index, blob in enumerate(blobs):
        restored = restore_generation(blob, base_bytes=canonical_generations[index - 1] if index else None)
    restore_ms = (time.perf_counter() - restore_started) * 1000
    assert restored == canonical_generations[-1]
    result = {
        "cards": 300,
        "generations": 100,
        "rawBytes": sum(map(len, canonical_generations)),
        "storedBytes": sum(len(blob.stored_bytes) for blob in blobs),
        "fullCount": sum(blob.representation == "gzip_json" for blob in blobs),
        "deltaCount": sum(blob.representation == "gzip_delta" for blob in blobs),
        "maxDeltaDepth": max(blob.delta_depth for blob in blobs),
        "encodeMs": round(encode_ms, 2),
        "restoreMs": round(restore_ms, 2),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
