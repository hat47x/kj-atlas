from __future__ import annotations

import argparse
import json
import time
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

from benchmark_generation_codec import benchmark_git
from kj_atlas_api.generation_codec import (
    EncodedGenerationBlob,
    canonical_json_bytes,
    encode_generation,
    restore_generation,
)

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_DIR = BACKEND_DIR.parents[1]
REAL_FIXTURE = REPOSITORY_DIR / "03_Implement/frontend/tests/fixtures/agent_task/doc.fixture.json"


def _fixture_history(generations: int = 40) -> tuple[list[object], list[int | None]]:
    document = json.loads(REAL_FIXTURE.read_text(encoding="utf-8"))
    history: list[object] = []
    for generation in range(generations):
        value = deepcopy(document)
        value["updatedAt"] = f"2026-08-10T00:{generation:02d}:00.000Z"
        cards = value.setdefault("cards", [])
        if cards:
            target = cards[generation % len(cards)]
            target["text"] = f"{target.get('text', '')} / observation {generation}"
            target["x"] = int(target.get("x", 0)) + generation
        history.append(value)
        document = value
    return history, [None, *range(generations - 1)]


def _stable_noise(index: int, length: int) -> str:
    chunks: list[str] = []
    counter = 0
    while sum(map(len, chunks)) < length:
        chunks.append(sha256(f"card:{index}:chunk:{counter}".encode()).hexdigest())
        counter += 1
    return "".join(chunks)[:length]


def _large_history(generations: int = 20) -> tuple[list[object], list[int | None]]:
    cards: list[dict[str, object]] = [
        {
            "id": f"large-card-{index:04d}",
            "text": f"観察 {index}: {_stable_noise(index, 1200)}",
            "x": (index % 30) * 40,
            "y": (index // 30) * 30,
            "claimType": "unknown",
        }
        for index in range(900)
    ]
    history: list[object] = []
    for generation in range(generations):
        for offset in range(8):
            index = (generation * 17 + offset * 101) % len(cards)
            cards[index] = {
                **cards[index],
                "text": f"世代 {generation} 更新 {offset}: {_stable_noise(index + generation, 1200)}",
            }
        history.append(
            {
                "version": 1,
                "id": "large-generation-benchmark",
                "updatedAt": f"2026-08-10T01:{generation:02d}:00.000Z",
                "transform": {"panX": 0, "panY": 0, "zoom": 1},
                "cards": deepcopy(cards),
                "edges": [],
                "islands": [],
            }
        )
    return history, [None, *range(generations - 1)]


def _branch_merge_history() -> tuple[list[object], list[int | None]]:
    base = json.loads(REAL_FIXTURE.read_text(encoding="utf-8"))
    branch_a = deepcopy(base)
    branch_a["title"] = "Branch A synthesis"
    branch_a["cards"][0]["text"] += " / branch A"
    branch_b = deepcopy(base)
    branch_b["title"] = "Branch B synthesis"
    branch_b["cards"][-1]["text"] += " / branch B"
    merged = deepcopy(branch_a)
    merged["title"] = "Merged synthesis"
    merged["cards"][-1] = deepcopy(branch_b["cards"][-1])
    return [base, branch_a, branch_b, merged], [None, 0, 0, 1]


def benchmark_scenario(
    name: str,
    values: list[object],
    parent_indexes: list[int | None],
    *,
    include_git: bool,
) -> dict[str, object]:
    canonical = [canonical_json_bytes(value) for value in values]
    blobs: list[EncodedGenerationBlob] = []
    started = time.perf_counter()
    for index, value in enumerate(values):
        parent_index = parent_indexes[index]
        parent_blob = blobs[parent_index] if parent_index is not None else None
        blobs.append(
            encode_generation(
                value,
                base_bytes=canonical[parent_index] if parent_index is not None else None,
                base_digest=(parent_blob.content_digest if parent_blob else None),
                base_delta_depth=(parent_blob.delta_depth if parent_blob else 0),
            )
        )
    encode_ms = (time.perf_counter() - started) * 1000

    restore_started = time.perf_counter()
    for index, blob in enumerate(blobs):
        parent_index = parent_indexes[index]
        restored = restore_generation(
            blob,
            base_bytes=canonical[parent_index] if parent_index is not None else None,
        )
        assert restored == canonical[index]
    restore_ms = (time.perf_counter() - restore_started) * 1000
    result: dict[str, object] = {
        "name": name,
        "generations": len(values),
        "minimumGenerationBytes": min(map(len, canonical)),
        "maximumGenerationBytes": max(map(len, canonical)),
        "rawBytes": sum(map(len, canonical)),
        "storedBytes": sum(len(blob.stored_bytes) for blob in blobs),
        "fullCount": sum(blob.representation == "gzip_json" for blob in blobs),
        "deltaCount": sum(blob.representation == "gzip_delta" for blob in blobs),
        "maxDeltaDepth": max(blob.delta_depth for blob in blobs),
        "encodeMs": round(encode_ms, 2),
        "restoreMs": round(restore_ms, 2),
    }
    if name == "branch_merge":
        alternate = encode_generation(
            values[-1],
            base_bytes=canonical[2],
            base_digest=blobs[2].content_digest,
            base_delta_depth=blobs[2].delta_depth,
        )
        result["mergePrimaryParentStoredBytes"] = len(blobs[-1].stored_bytes)
        result["mergeAlternateParentStoredBytes"] = len(alternate.stored_bytes)
    if include_git:
        result["git"] = benchmark_git(canonical)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--include-git",
        action="store_true",
        help="also create and aggressively pack one Git history per scenario",
    )
    args = parser.parse_args()
    scenarios = (
        ("fixture_derived", *_fixture_history()),
        ("branch_merge", *_branch_merge_history()),
        ("large_1mib", *_large_history()),
    )
    result = {
        "fixture": str(REAL_FIXTURE.relative_to(REPOSITORY_DIR)),
        "scenarios": [
            benchmark_scenario(name, values, parents, include_git=args.include_git)
            for name, values, parents in scenarios
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
