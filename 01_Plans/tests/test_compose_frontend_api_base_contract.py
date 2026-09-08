from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COMPOSE_PATH = ROOT / "03_Implement/deploy/docker-compose.yml"
NGINX_PATH = ROOT / "03_Implement/deploy/nginx.conf"
FRONTEND_DOCKERFILE_PATH = ROOT / "03_Implement/frontend/Dockerfile"


def _service_section(compose_text: str, service_name: str) -> str:
    lines = compose_text.splitlines()
    start = next(
        (index for index, line in enumerate(lines) if line == f"  {service_name}:"),
        None,
    )
    if start is None:
        raise AssertionError(f"compose service is missing: {service_name}")
    section: list[str] = []
    for line in lines[start + 1 :]:
        if re.match(r"^  [A-Za-z0-9_.-]+:\s*$", line):
            break
        section.append(line)
    return "\n".join(section)


class ComposeFrontendApiBaseContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        compose_text = COMPOSE_PATH.read_text(encoding="utf-8")
        cls.web_section = _service_section(compose_text, "web")
        cls.nginx_text = NGINX_PATH.read_text(encoding="utf-8")
        cls.frontend_dockerfile = FRONTEND_DOCKERFILE_PATH.read_text(encoding="utf-8")

    def test_standard_compose_pins_frontend_api_base_to_nginx_proxy_path(self) -> None:
        self.assertIn("KJ_ATLAS_FRONTEND_API_BASE: /api", self.web_section)
        self.assertNotIn("${KJ_ATLAS_FRONTEND_API_BASE", self.web_section)
        self.assertIn("location /api/ {", self.nginx_text)
        self.assertIn("proxy_pass http://api:8000/;", self.nginx_text)

    def test_direct_frontend_build_keeps_custom_path_contract(self) -> None:
        self.assertIn("ARG KJ_ATLAS_FRONTEND_API_BASE=/api", self.frontend_dockerfile)
        self.assertIn(
            "ENV KJ_ATLAS_FRONTEND_API_BASE=${KJ_ATLAS_FRONTEND_API_BASE}",
            self.frontend_dockerfile,
        )


if __name__ == "__main__":
    unittest.main()
