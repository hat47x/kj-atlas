from pathlib import Path

path = Path('03_Implement/backend/tests/test_ai_route_provider_token_measurement.py')
text = path.read_text()
old = '''                requested_at="2026-09-05T00:00:00+00:00",
                trace_id=f"trace-{len(self.calls)}",
            ),'''
new = '''                requested_at="2026-09-05T00:00:00+00:00",
                trace_id=f"trace-{len(self.calls)}",
                thinking_mode="disabled",
            ),'''
assert text.count(old) == 1
text = text.replace(old, new, 1)

# Only the six tests that actually execute measurement rows need the explicit
# DeepSeek mode. Keep the provider-name mismatch test focused on its earlier
# fail-fast boundary.
marker = '\ndef test_provider_name_mismatch_fails_before_any_request_is_sent() -> None:\n'
prefix, suffix = text.split(marker, 1)
needle = '''        provider=provider,
'''
count = prefix.count(needle)
assert count == 6, count
prefix = prefix.replace(
    needle,
    '''        provider=provider,
        expected_deepseek_thinking_mode="disabled",
''',
)
path.write_text(prefix + marker + suffix)
