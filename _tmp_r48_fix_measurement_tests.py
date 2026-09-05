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
needle = '''        provider=provider,
'''
count = text.count(needle)
assert count == 6, count
text = text.replace(
    needle,
    '''        provider=provider,
        expected_deepseek_thinking_mode="disabled",
''',
)
path.write_text(text)
