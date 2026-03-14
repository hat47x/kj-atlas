from __future__ import annotations

import pytest
from pydantic import ValidationError

from kj_atlas_api.models import PolygonHandoffContractVerificationResponse


def test_polygon_handoff_response_accepts_consistent_ok_payload() -> None:
    response = PolygonHandoffContractVerificationResponse.model_validate(
        {
            "status": "ok",
            "rollbackRequired": False,
            "failureReasons": [],
            "verificationKey": "a" * 64,
        }
    )

    assert response.status == "ok"
    assert response.rollbackRequired is False


def test_polygon_handoff_response_rejects_rollback_flag_mismatch() -> None:
    with pytest.raises(ValidationError, match="rollbackRequired must match status"):
        PolygonHandoffContractVerificationResponse.model_validate(
            {
                "status": "ok",
                "rollbackRequired": True,
                "failureReasons": [],
                "verificationKey": "b" * 64,
            }
        )


def test_polygon_handoff_response_rejects_failure_reason_status_mismatch() -> None:
    with pytest.raises(
        ValidationError,
        match="failureReasons must be non-empty iff status is rollback_required",
    ):
        PolygonHandoffContractVerificationResponse.model_validate(
            {
                "status": "rollback_required",
                "rollbackRequired": True,
                "failureReasons": [],
                "verificationKey": "c" * 64,
            }
        )
