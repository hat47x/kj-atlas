from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

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


def tree_size(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def benchmark_git(generations: list[bytes]) -> dict[str, object]:
    if shutil.which("git") is None:
        return {"available": False}
    with tempfile.TemporaryDirectory(prefix="kj-generation-git-") as directory:
        repository = Path(directory)
        subprocess.run(["git", "init", "-q", str(repository)], check=True)
        subprocess.run(
            ["git", "-C", str(repository), "config", "user.email", "benchmark@example.invalid"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(repository), "config", "user.name", "KJ benchmark"],
            check=True,
        )
        commit_ids: list[str] = []
        started = time.perf_counter()
        for index, generation in enumerate(generations):
            (repository / "document.json").write_bytes(generation)
            subprocess.run(
                ["git", "-C", str(repository), "add", "document.json"], check=True
            )
            subprocess.run(
                ["git", "-C", str(repository), "commit", "-q", "-m", f"generation {index}"],
                check=True,
            )
            commit_ids.append(
                subprocess.check_output(
                    ["git", "-C", str(repository), "rev-parse", "HEAD"], text=True
                ).strip()
            )
        subprocess.run(
            ["git", "-C", str(repository), "gc", "--aggressive", "--prune=now"],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        write_ms = (time.perf_counter() - started) * 1000
        restore_started = time.perf_counter()
        for index in (0, len(generations) // 2, len(generations) - 1):
            restored = subprocess.check_output(
                ["git", "-C", str(repository), "show", f"{commit_ids[index]}:document.json"]
            )
            assert restored == generations[index]
        restore_ms = (time.perf_counter() - restore_started) * 1000
        return {
            "available": True,
            "repositoryBytes": tree_size(repository / ".git"),
            "writeAndGcMs": round(write_ms, 2),
            "restoreThreeGenerationsMs": round(restore_ms, 2),
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
        "git": benchmark_git(canonical_generations),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
