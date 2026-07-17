from __future__ import annotations

from typing import Any
from urllib import request as urllib_request


class _RejectRedirectHandler(urllib_request.HTTPRedirectHandler):
    """Leave redirects to the default error handler instead of forwarding secrets."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001, ANN201, ARG002
        return None


def open_trusted_http(
    request: urllib_request.Request,
    *,
    timeout_seconds: float,
) -> Any:
    """Open one validated endpoint without following redirects."""
    opener = urllib_request.build_opener(_RejectRedirectHandler())
    return opener.open(request, timeout=timeout_seconds)  # noqa: S310
