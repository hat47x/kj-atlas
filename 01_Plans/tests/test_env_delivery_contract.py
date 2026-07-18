import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SETTINGS_PATH = REPO_ROOT / "03_Implement" / "backend" / "src" / "kj_atlas_api" / "settings.py"
REGISTRY_PATH = REPO_ROOT / "02_Architecture" / "runtime_parameter_registry.md"
COMPOSE_PATH = REPO_ROOT / "03_Implement" / "deploy" / "docker-compose.yml"
COMPOSE_OVERLAY_PATH = REPO_ROOT / "03_Implement" / "deploy" / "docker-compose.llm-stub.yml"
FRONTEND_DOCKERFILE_PATH = REPO_ROOT / "03_Implement" / "frontend" / "Dockerfile"

VALIDATION_ALIAS_RE = re.compile(r'validation_alias="(KJ_ATLAS_[A-Z0-9_]+)"')
# Key | Default | Purpose | Delivery surface | Secret | Probe -- captures the
# first 4 cells; Secret/Probe aren't needed for this drift check.
BACKEND_SETTINGS_ROW_RE = re.compile(
    r"^\|\s*`(KJ_ATLAS_[A-Z0-9_]+)`\s*\|([^|]*)\|([^|]*)\|([^|]*)\|",
    re.MULTILINE,
)
COMPOSE_ENV_LIST_ITEM_RE = re.compile(r"^\s{6}-\s*(KJ_ATLAS_[A-Z0-9_]+)(?:=.*)?\s*$")
COMPOSE_ENV_MAP_ITEM_RE = re.compile(r"^\s{6}(KJ_ATLAS_[A-Z0-9_]+):\s*.*$")


def _settings_validation_alias_keys() -> set[str]:
    return set(VALIDATION_ALIAS_RE.findall(SETTINGS_PATH.read_text(encoding="utf-8")))


def _backend_settings_section(registry_text: str) -> str:
    start = registry_text.index("## Backend settings")
    end = registry_text.index("## Compose and frontend build keys", start)
    return registry_text[start:end]


def _registry_backend_keys() -> dict[str, str]:
    """Return {key: delivery_surface_cell_text} for every Backend settings row."""
    section = _backend_settings_section(REGISTRY_PATH.read_text(encoding="utf-8"))
    result: dict[str, str] = {}
    for match in BACKEND_SETTINGS_ROW_RE.finditer(section):
        key, _default, _purpose, delivery_surface = match.groups()
        result[key] = delivery_surface.strip()
    return result


def _service_environment_block(compose_text: str, service_name: str) -> str:
    """Return the raw lines of a top-level (2-space-indented) service block."""
    lines = compose_text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line == f"  {service_name}:":
            start = i
            break
    if start is None:
        return ""
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if re.match(r"^  \S", lines[i]):
            end = i
            break
    return "\n".join(lines[start:end])


def _environment_keys_from_service_block(service_block: str) -> set[str]:
    """Return KJ_ATLAS_* keys from a service block's `environment:` list or map form."""
    keys: set[str] = set()
    in_env = False
    for line in service_block.splitlines():
        if re.match(r"^\s{4}environment:\s*$", line):
            in_env = True
            continue
        if not in_env:
            continue
        if re.match(r"^\s{0,4}\S", line):
            in_env = False
            continue
        list_match = COMPOSE_ENV_LIST_ITEM_RE.match(line)
        if list_match:
            keys.add(list_match.group(1))
            continue
        map_match = COMPOSE_ENV_MAP_ITEM_RE.match(line)
        if map_match:
            keys.add(map_match.group(1))
    return keys


class EnvDeliveryContractTest(unittest.TestCase):
    """ENV-COMPOSE-01: settings.py, the runtime parameter registry, and the
    Compose files must agree on which KJ_ATLAS_* keys exist and which
    delivery surface actually forwards them. A drift here is exactly the
    class of bug this issue exists to prevent: a document/registry claim
    about delivery that the real Compose file doesn't back up.
    """

    def test_settings_keys_match_registry_backend_settings_keys(self):
        settings_keys = _settings_validation_alias_keys()
        registry_keys = set(_registry_backend_keys().keys())
        self.assertEqual(
            settings_keys,
            registry_keys,
            "settings.py's validation_alias keys and the registry's Backend "
            "settings table must be the exact same key set",
        )

    def test_base_compose_delivered_keys_match_registry_delivery_surface(self):
        registry = _registry_backend_keys()
        registry_base_compose_keys = {key for key, surface in registry.items() if "base Compose" in surface}
        api_block = _service_environment_block(COMPOSE_PATH.read_text(encoding="utf-8"), "api")
        compose_delivered_keys = _environment_keys_from_service_block(api_block)
        self.assertEqual(
            registry_base_compose_keys,
            compose_delivered_keys,
            "keys the registry marks as base-Compose-delivered must exactly match "
            "docker-compose.yml's api.environment, in both directions",
        )

    def test_llm_stub_overlay_keys_are_a_subset_of_overlay_delivered_keys(self):
        registry = _registry_backend_keys()
        registry_overlay_keys = {key for key, surface in registry.items() if "llm-stub overlay" in surface}
        api_block = _service_environment_block(COMPOSE_OVERLAY_PATH.read_text(encoding="utf-8"), "api")
        overlay_delivered_keys = _environment_keys_from_service_block(api_block)
        self.assertTrue(
            registry_overlay_keys.issubset(overlay_delivered_keys),
            f"registry llm-stub-overlay keys {registry_overlay_keys} must all appear in "
            f"docker-compose.llm-stub.yml's api.environment {overlay_delivered_keys}",
        )

    def test_runtime_profile_is_identical_for_api_and_frontend_build(self):
        compose_text = COMPOSE_PATH.read_text(encoding="utf-8")
        api_block = _service_environment_block(compose_text, "api")
        web_block = _service_environment_block(compose_text, "web")
        profile_expression = "${KJ_ATLAS_RUNTIME_PROFILE:-evaluation}"

        self.assertIn(
            f"KJ_ATLAS_RUNTIME_PROFILE={profile_expression}",
            api_block,
        )
        self.assertIn(
            f"KJ_ATLAS_RUNTIME_PROFILE: {profile_expression}",
            web_block,
        )

        frontend_dockerfile = FRONTEND_DOCKERFILE_PATH.read_text(encoding="utf-8")
        self.assertIn("ARG KJ_ATLAS_RUNTIME_PROFILE=local-dev", frontend_dockerfile)
        self.assertIn(
            "ENV KJ_ATLAS_RUNTIME_PROFILE=${KJ_ATLAS_RUNTIME_PROFILE}",
            frontend_dockerfile,
        )


if __name__ == "__main__":
    unittest.main()
