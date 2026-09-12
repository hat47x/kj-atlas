#!/usr/bin/env python3
"""Bounded subprocess transport for associative cognition providers.

The transport owns process isolation concerns only. It does not reinterpret
provider output, rank candidates, or grant semantic authority. The formal
request/response meaning remains in associative_channel.py.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from collections.abc import Mapping, Sequence
from typing import Any

from associative_channel import (
    D2AssociativeError,
    build_associative_request,
    normalize_associative_response,
)
from query_engine import D0Network


class AssociativeProviderProcessError(RuntimeError):
    pass


DEFAULT_TIMEOUT_SECONDS = 2.0
DEFAULT_MAX_REQUEST_BYTES = 4 * 1024 * 1024
DEFAULT_MAX_RESPONSE_BYTES = 4 * 1024 * 1024
DEFAULT_MAX_DIAGNOSTIC_BYTES = 16 * 1024


def _validate_argv(argv: Sequence[str]) -> tuple[str, ...]:
    if isinstance(argv, (str, bytes)) or not isinstance(argv, Sequence):
        raise AssociativeProviderProcessError("provider argv must be a sequence of strings")
    normalized = tuple(argv)
    if not normalized:
        raise AssociativeProviderProcessError("provider argv must not be empty")
    for value in normalized:
        if not isinstance(value, str) or not value:
            raise AssociativeProviderProcessError("provider argv entries must be non-empty strings")
        if "\x00" in value:
            raise AssociativeProviderProcessError("provider argv must not contain NUL")
    return normalized


def _encode_request(request: Mapping[str, Any], max_bytes: int) -> bytes:
    if not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or max_bytes < 1:
        raise AssociativeProviderProcessError("max_request_bytes must be a positive integer")
    try:
        payload = json.dumps(
            request,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise AssociativeProviderProcessError(f"request is not JSON serializable: {exc}") from exc
    if len(payload) > max_bytes:
        raise AssociativeProviderProcessError("provider request exceeds configured byte limit")
    return payload


def _strict_json_object(data: bytes) -> dict[str, Any]:
    def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise AssociativeProviderProcessError(
                    f"provider response contains duplicate JSON key: {key}"
                )
            result[key] = value
        return result

    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=no_duplicates)
    except AssociativeProviderProcessError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AssociativeProviderProcessError(f"provider stdout is not one valid UTF-8 JSON value: {exc}") from exc
    if not isinstance(value, dict):
        raise AssociativeProviderProcessError("provider response must be a JSON object")
    return value


def _diagnostic_text(stream: Any, max_bytes: int) -> str:
    stream.seek(0, os.SEEK_END)
    size = stream.tell()
    stream.seek(0)
    data = stream.read(min(size, max_bytes))
    text = data.decode("utf-8", errors="replace").replace("\x00", "")
    if size > max_bytes:
        text += "…[truncated]"
    return text.strip()


def invoke_associative_provider(
    request: Mapping[str, Any],
    argv: Sequence[str],
    *,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    max_request_bytes: int = DEFAULT_MAX_REQUEST_BYTES,
    max_response_bytes: int = DEFAULT_MAX_RESPONSE_BYTES,
    max_diagnostic_bytes: int = DEFAULT_MAX_DIAGNOSTIC_BYTES,
    cwd: str | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Invoke one provider process without a shell and return one JSON object.

    stdout/stderr are directed to temporary files rather than captured pipes so
    a misbehaving provider cannot grow the Python process memory without bound.
    The response is read into memory only after its byte size has been checked.
    """

    command = _validate_argv(argv)
    if not isinstance(timeout_seconds, (int, float)) or isinstance(timeout_seconds, bool) or timeout_seconds <= 0:
        raise AssociativeProviderProcessError("timeout_seconds must be positive")
    for value, name in (
        (max_response_bytes, "max_response_bytes"),
        (max_diagnostic_bytes, "max_diagnostic_bytes"),
    ):
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise AssociativeProviderProcessError(f"{name} must be a positive integer")

    payload = _encode_request(request, max_request_bytes)
    child_env = None if env is None else dict(env)

    with tempfile.TemporaryFile() as stdout_file, tempfile.TemporaryFile() as stderr_file:
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=stdout_file,
                stderr=stderr_file,
                cwd=cwd,
                env=child_env,
                shell=False,
                close_fds=True,
            )
        except OSError as exc:
            raise AssociativeProviderProcessError(f"provider process could not start: {exc}") from exc

        try:
            process.communicate(input=payload, timeout=float(timeout_seconds))
        except subprocess.TimeoutExpired as exc:
            process.kill()
            process.communicate()
            raise AssociativeProviderProcessError("provider process timed out") from exc

        if process.returncode != 0:
            diagnostic = _diagnostic_text(stderr_file, max_diagnostic_bytes)
            suffix = f": {diagnostic}" if diagnostic else ""
            raise AssociativeProviderProcessError(
                f"provider process exited with code {process.returncode}{suffix}"
            )

        stdout_file.seek(0, os.SEEK_END)
        response_size = stdout_file.tell()
        if response_size > max_response_bytes:
            raise AssociativeProviderProcessError("provider response exceeds configured byte limit")
        stdout_file.seek(0)
        response_data = stdout_file.read()

    return _strict_json_object(response_data)


def execute_associative_channel_via_process(
    network: D0Network,
    argv: Sequence[str],
    *,
    request_id: str,
    intent: str,
    anchor_refs: Sequence[str],
    scope_refs: Sequence[str] | None = None,
    candidate_limit: int = 8,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Build formal request -> invoke provider -> validate formal response."""

    request = build_associative_request(
        network,
        request_id=request_id,
        intent=intent,
        anchor_refs=anchor_refs,
        scope_refs=scope_refs,
        candidate_limit=candidate_limit,
    )
    response = invoke_associative_provider(
        request,
        argv,
        timeout_seconds=timeout_seconds,
    )
    try:
        return normalize_associative_response(request, response)
    except D2AssociativeError as exc:
        raise AssociativeProviderProcessError(
            f"provider response violates associative contract: {exc}"
        ) from exc
