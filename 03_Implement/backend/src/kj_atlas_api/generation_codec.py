from __future__ import annotations

import base64
import gzip
import json
from dataclasses import dataclass
from hashlib import sha256

from kj_atlas_api.generation_policy import GenerationRetentionPolicy


class GenerationCodecError(ValueError):
    pass


@dataclass(frozen=True)
class EncodedGenerationBlob:
    content_digest: str
    byte_size: int
    stored_bytes: bytes
    representation: str
    base_digest: str | None
    delta_depth: int


def canonical_json_bytes(value: object) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise GenerationCodecError("generation content is not canonical JSON") from error


def _gzip(data: bytes) -> bytes:
    return gzip.compress(data, compresslevel=6, mtime=0)


def _delta(base: bytes, current: bytes) -> bytes:
    prefix = 0
    limit = min(len(base), len(current))
    while prefix < limit and base[prefix] == current[prefix]:
        prefix += 1
    suffix = 0
    suffix_limit = limit - prefix
    while suffix < suffix_limit and base[-1 - suffix] == current[-1 - suffix]:
        suffix += 1
    middle_end = len(current) - suffix if suffix else len(current)
    envelope = {
        "v": 1,
        "prefix": prefix,
        "suffix": suffix,
        "middle": base64.b64encode(current[prefix:middle_end]).decode("ascii"),
    }
    return _gzip(canonical_json_bytes(envelope))


def encode_generation(
    value: object,
    *,
    base_bytes: bytes | None = None,
    base_digest: str | None = None,
    base_delta_depth: int = 0,
    policy: GenerationRetentionPolicy | None = None,
) -> EncodedGenerationBlob:
    policy = policy or GenerationRetentionPolicy()
    policy.validate()
    canonical = canonical_json_bytes(value)
    digest = sha256(canonical).hexdigest()
    full = _gzip(canonical)
    if (
        base_bytes is not None
        and base_digest is not None
        and sha256(base_bytes).hexdigest() == base_digest
        and base_delta_depth < policy.delta_chain_max_depth
    ):
        delta = _delta(base_bytes, canonical)
        if len(delta) <= len(full) * policy.full_snapshot_delta_ratio:
            return EncodedGenerationBlob(
                digest, len(canonical), delta, "gzip_delta", base_digest, base_delta_depth + 1
            )
    return EncodedGenerationBlob(digest, len(canonical), full, "gzip_json", None, 0)


def restore_generation(blob: EncodedGenerationBlob, *, base_bytes: bytes | None = None) -> bytes:
    try:
        decoded = gzip.decompress(blob.stored_bytes)
    except (OSError, EOFError) as error:
        raise GenerationCodecError("generation blob compression is invalid") from error
    if blob.representation == "gzip_json":
        restored = decoded
    elif blob.representation == "gzip_delta":
        if base_bytes is None or blob.base_digest != sha256(base_bytes).hexdigest():
            raise GenerationCodecError("generation delta base does not match")
        try:
            envelope = json.loads(decoded)
            prefix = envelope["prefix"]
            suffix = envelope["suffix"]
            middle = base64.b64decode(envelope["middle"], validate=True)
            restored = base_bytes[:prefix] + middle + (base_bytes[len(base_bytes) - suffix :] if suffix else b"")
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            raise GenerationCodecError("generation delta is invalid") from error
    else:
        raise GenerationCodecError("generation representation is unsupported")
    if len(restored) != blob.byte_size or sha256(restored).hexdigest() != blob.content_digest:
        raise GenerationCodecError("restored generation failed integrity verification")
    return restored
