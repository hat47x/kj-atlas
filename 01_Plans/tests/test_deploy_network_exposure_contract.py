import re
import unittest
from pathlib import Path

COMPOSE_PATH = Path(__file__).resolve().parents[2] / "03_Implement" / "deploy" / "docker-compose.yml"


def _web_service_block() -> str:
    lines = COMPOSE_PATH.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == "web:")
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i] and not lines[i].startswith(" "):
            end = i
            break
    return "\n".join(lines[start:end])


def _web_port_mapping() -> str:
    match = re.search(r'-\s+"([^"]+)"', _web_service_block())
    assert match is not None, "expected a quoted host:container port mapping under web.ports"
    return match.group(1)


class DeployNetworkExposureContractTest(unittest.TestCase):
    """DEPLOY-NET-01: the standard evaluation Compose must stay loopback-only.

    Omitting the host IP in a Docker port mapping binds 0.0.0.0, exposing this
    unauthenticated evaluation stack to the whole LAN. SafeMode and
    KJ_ATLAS_API_KEY do not control network reachability -- this loopback bind
    is the only thing that does.
    """

    def test_web_port_binds_loopback_only(self):
        mapping = _web_port_mapping()
        self.assertTrue(
            mapping.startswith("127.0.0.1:"),
            f"web port mapping must bind loopback only (127.0.0.1:<port>:80), got: {mapping!r}",
        )
        self.assertNotIn("0.0.0.0", mapping)

    def test_web_port_env_var_only_changes_port_not_bind_address(self):
        mapping = _web_port_mapping()
        self.assertIn(
            "${KJ_ATLAS_WEB_PORT",
            mapping,
            "KJ_ATLAS_WEB_PORT must remain the only user-facing port override",
        )
        # Collapse the ${VAR:-default} substitution to one token before counting
        # separators, since its own ":-" would otherwise be miscounted as a
        # host:port:container_port separator.
        collapsed = re.sub(r"\$\{[^}]*\}", "PORT", mapping)
        self.assertEqual(
            collapsed.count(":"),
            2,
            f"expected host_ip:port:container_port shape, got: {mapping!r}",
        )


if __name__ == "__main__":
    unittest.main()
