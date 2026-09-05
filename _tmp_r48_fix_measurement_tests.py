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

# The main patch adds the settings dependency; place it with the rest of the
# kj_atlas_api imports instead of between models and models_ai.
measure_path = Path('03_Implement/backend/scripts/measure_ai_route_provider_tokens.py')
measure = measure_path.read_text()
old = '''from kj_atlas_api.models import SuggestLayoutRequest
from kj_atlas_api.settings import settings
from kj_atlas_api.models_ai import (
'''
new = '''from kj_atlas_api.models import SuggestLayoutRequest
from kj_atlas_api.models_ai import (
'''
assert measure.count(old) == 1
measure = measure.replace(old, new, 1)
old = '''    SuggestCardGroupsRequest,
)
from kj_atlas_api.routes.ai import (
'''
new = '''    SuggestCardGroupsRequest,
)
from kj_atlas_api.routes.ai import (
'''
assert measure.count(old) == 1
# settings sorts after routes.ai as a top-level module path.
measure = measure.replace(old, new, 1)
route_end = '''    _suggest_layout_ir,
)

# `python -m scripts.measure_ai_route_provider_tokens`'''
route_new = '''    _suggest_layout_ir,
)
from kj_atlas_api.settings import settings

# `python -m scripts.measure_ai_route_provider_tokens`'''
assert measure.count(route_end) == 1
measure_path.write_text(measure.replace(route_end, route_new, 1))
