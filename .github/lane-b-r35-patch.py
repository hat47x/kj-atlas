from pathlib import Path

measure_path = Path("03_Implement/backend/scripts/measure_ai_route_provider_tokens.py")
s = measure_path.read_text(encoding="utf-8")

needle = '''        "provider_reported": {\n            "input_tokens": None,\n            "output_tokens": None,\n        },\n        "status": "dry-run",\n'''
replacement = '''        "provider_call": None,\n        "provider_reported": {\n            "input_tokens": None,\n            "output_tokens": None,\n        },\n        "status": "dry-run",\n'''
assert s.count(needle) == 1
s = s.replace(needle, replacement, 1)

needle = '''        "prompt_fingerprint": {"algorithm": "sha256", "encoding": "utf-8"},\n        "executed": execute,\n'''
replacement = '''        "prompt_fingerprint": {"algorithm": "sha256", "encoding": "utf-8"},\n        "provider_call_provenance": {"version": 1},\n        "executed": execute,\n'''
assert s.count(needle) == 1
s = s.replace(needle, replacement, 1)

needle = '''        row["actual_provider"] = response.metadata.provider_name\n        row["actual_provider_kind"] = response.metadata.provider_kind\n        row["actual_model"] = response.metadata.model_id\n        row["provider_reported"] = {\n'''
replacement = '''        row["actual_provider"] = response.metadata.provider_name\n        row["actual_provider_kind"] = response.metadata.provider_kind\n        row["actual_model"] = response.metadata.model_id\n        row["provider_call"] = response.metadata.as_audit_fields()\n        row["provider_reported"] = {\n'''
assert s.count(needle) == 1
s = s.replace(needle, replacement, 1)
measure_path.write_text(s, encoding="utf-8")

analyzer_path = Path("03_Implement/backend/scripts/analyze_ai_route_provider_measurement.py")
a = analyzer_path.read_text(encoding="utf-8")

needle = '''PROMPT_FINGERPRINT = {"algorithm": "sha256", "encoding": "utf-8"}\nCORE_ROUTE_TASKS = {\n'''
replacement = '''PROMPT_FINGERPRINT = {"algorithm": "sha256", "encoding": "utf-8"}\nPROVIDER_CALL_PROVENANCE = {"version": 1}\nCORE_ROUTE_TASKS = {\n'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)

needle = '''    if row.get("actual_model") != expected_model:\n        errors.append(f"model-mismatch:{name}")\n        return None\n    token = _int_token(row)\n'''
replacement = '''    if row.get("actual_model") != expected_model:\n        errors.append(f"model-mismatch:{name}")\n        return None\n\n    provider_call = row.get("provider_call")\n    if not isinstance(provider_call, dict):\n        errors.append(f"provider-call-metadata-missing:{name}")\n        return None\n    if provider_call.get("provider") != expected_provider:\n        errors.append(f"provider-call-provider-mismatch:{name}")\n        return None\n    if provider_call.get("provider_kind") != row.get("actual_provider_kind"):\n        errors.append(f"provider-call-kind-mismatch:{name}")\n        return None\n    if provider_call.get("model_id") != expected_model:\n        errors.append(f"provider-call-model-mismatch:{name}")\n        return None\n    for field in ("transport", "requested_at", "trace_id"):\n        value = provider_call.get(field)\n        if not isinstance(value, str) or not value.strip():\n            errors.append(f"provider-call-{field}-missing:{name}")\n            return None\n    if provider_call.get("fallback_to_none") is not False:\n        errors.append(f"provider-call-fallback-detected:{name}")\n        return None\n    if provider_call.get("execution_path") != "primary":\n        errors.append(f"provider-call-non-primary-path:{name}")\n        return None\n\n    token = _int_token(row)\n'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)

needle = '''    if report.get("prompt_fingerprint") != PROMPT_FINGERPRINT:\n        errors.append("unsupported-or-missing-prompt-fingerprint")\n\n    expected_provider = report.get("expected_provider")\n'''
replacement = '''    if report.get("prompt_fingerprint") != PROMPT_FINGERPRINT:\n        errors.append("unsupported-or-missing-prompt-fingerprint")\n    if report.get("provider_call_provenance") != PROVIDER_CALL_PROVENANCE:\n        errors.append("unsupported-or-missing-provider-call-provenance")\n\n    expected_provider = report.get("expected_provider")\n'''
assert a.count(needle) == 1
a = a.replace(needle, replacement, 1)
analyzer_path.write_text(a, encoding="utf-8")

test_path = Path("03_Implement/backend/tests/test_ai_route_provider_measurement_analysis.py")
t = test_path.read_text(encoding="utf-8")
needle = '''        "actual_provider": "named-provider",\n        "actual_provider_kind": "test",\n        "actual_model": "named-model",\n        "status": "measured",\n'''
replacement = '''        "actual_provider": "named-provider",\n        "actual_provider_kind": "test",\n        "actual_model": "named-model",\n        "provider_call": {\n            "provider": "named-provider",\n            "provider_kind": "test",\n            "model_id": "named-model",\n            "transport": "http",\n            "requested_at": "2026-09-05T00:00:00+00:00",\n            "trace_id": "trace-fixture",\n            "fallback_to_none": False,\n            "execution_path": "primary",\n        },\n        "status": "measured",\n'''
assert t.count(needle) == 1
t = t.replace(needle, replacement, 1)
needle = '''        "prompt_fingerprint": analysis.PROMPT_FINGERPRINT.copy(),\n        "routes": {\n'''
replacement = '''        "prompt_fingerprint": analysis.PROMPT_FINGERPRINT.copy(),\n        "provider_call_provenance": analysis.PROVIDER_CALL_PROVENANCE.copy(),\n        "routes": {\n'''
assert t.count(needle) == 1
t = t.replace(needle, replacement, 1)
test_path.write_text(t, encoding="utf-8")
