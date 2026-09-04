from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BACKEND_TESTS = REPO / "03_Implement" / "backend" / "tests"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"patch anchor mismatch: {path}: {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


# DOC-CI-DRIFT-01 already established that permanent GitHub Actions workflows are
# optional. Keep the database declaration checks strong when ci.yml exists, and
# explicitly bind the workflow-absent path to the current release contract.
db_test = BACKEND_TESTS / "test_database_support_declarations.py"
replace_once(
    db_test,
    'BACKEND_ROOT = REPO_ROOT / "03_Implement" / "backend"\n',
    'BACKEND_ROOT = REPO_ROOT / "03_Implement" / "backend"\n'
    'CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"\n'
    'RELEASE_DOC = REPO_ROOT / "04_Documentation" / "release.md"\n\n\n'
    'def _optional_ci_workflow_text() -> str | None:\n'
    '    if CI_WORKFLOW.is_file():\n'
    '        return CI_WORKFLOW.read_text(encoding="utf-8")\n'
    '    release = RELEASE_DOC.read_text(encoding="utf-8")\n'
    '    assert "常設CIは現在無効" in release\n'
    '    return None\n',
)
replace_once(
    db_test,
    '''def test_driver_extras_markers_tests_and_ci_stay_synchronized() -> None:\n    pyproject = (BACKEND_ROOT / "pyproject.toml").read_text(encoding="utf-8")\n    workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(\n        encoding="utf-8"\n    )\n    test_sources = "\\n".join(\n        path.read_text(encoding="utf-8")\n        for path in (BACKEND_ROOT / "tests").glob("test_*.py")\n    )\n    dependencies = {\n        support.optional_dependency\n        for support in registered_database_support()\n        if support.optional_dependency is not None\n    }\n    markers = {\n        support.test_marker\n        for support in registered_database_support()\n        if support.test_marker is not None\n    }\n\n    for dependency in dependencies:\n        assert re.search(rf"(?m)^{re.escape(dependency)}\\s*=\\s*\\[", pyproject)\n        assert re.search(rf'pip install -e "\\.\\[[^\\]]*\\b{re.escape(dependency)}\\b', workflow)\n    for marker in markers:\n        assert f'"{marker}: tests that require ' in pyproject\n        assert f"@pytest.mark.{marker}" in test_sources\n        assert re.search(rf"pytest -m ['\\\"]?{re.escape(marker)}(?:['\\\"]|\\s|$)", workflow)\n''',
    '''def test_driver_extras_markers_tests_and_optional_ci_stay_synchronized() -> None:\n    pyproject = (BACKEND_ROOT / "pyproject.toml").read_text(encoding="utf-8")\n    workflow = _optional_ci_workflow_text()\n    test_sources = "\\n".join(\n        path.read_text(encoding="utf-8")\n        for path in (BACKEND_ROOT / "tests").glob("test_*.py")\n    )\n    dependencies = {\n        support.optional_dependency\n        for support in registered_database_support()\n        if support.optional_dependency is not None\n    }\n    markers = {\n        support.test_marker\n        for support in registered_database_support()\n        if support.test_marker is not None\n    }\n\n    for dependency in dependencies:\n        assert re.search(rf"(?m)^{re.escape(dependency)}\\s*=\\s*\\[", pyproject)\n        if workflow is not None:\n            assert re.search(\n                rf'pip install -e "\\.\\[[^\\]]*\\b{re.escape(dependency)}\\b',\n                workflow,\n            )\n    for marker in markers:\n        assert f'"{marker}: tests that require ' in pyproject\n        assert f"@pytest.mark.{marker}" in test_sources\n        if workflow is not None:\n            assert re.search(\n                rf"pytest -m ['\\\"]?{re.escape(marker)}(?:['\\\"]|\\s|$)",\n                workflow,\n            )\n''',
)
replace_once(
    db_test,
    '''def test_every_external_verified_backend_ci_image_matches_registry() -> None:\n    workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(\n        encoding="utf-8"\n    )\n\n    for support in registered_database_support():\n        if support.ci_image is not None:\n            assert workflow.count(support.ci_image) == 1, support.backend\n''',
    '''def test_every_external_verified_backend_ci_image_contract_is_unambiguous() -> None:\n    workflow = _optional_ci_workflow_text()\n    images = [\n        support.ci_image\n        for support in registered_database_support()\n        if support.ci_image is not None\n    ]\n    assert len(images) == len(set(images))\n\n    if workflow is not None:\n        for support in registered_database_support():\n            if support.ci_image is not None:\n                assert workflow.count(support.ci_image) == 1, support.backend\n''',
)

settings_test = BACKEND_TESTS / "test_settings_env_prefix_migration.py"
replace_once(
    settings_test,
    'CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"\n',
    'CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"\n'
    'RELEASE_DOC = REPO_ROOT / "04_Documentation" / "release.md"\n',
)
replace_once(
    settings_test,
    '''def test_backend_ci_uses_canonical_database_test_keys() -> None:\n    workflow = CI_WORKFLOW.read_text(encoding="utf-8")\n\n    assert not re.search(r"^\\s+(?:DATABASE_URL|RUN_PG_TESTS):", workflow, re.MULTILINE)\n    assert workflow.count("KJ_ATLAS_DATABASE_URL:") == 5\n    assert workflow.count("KJ_ATLAS_RUN_PG_TESTS:") == 1\n''',
    '''def test_backend_ci_uses_canonical_database_test_keys_when_present() -> None:\n    if not CI_WORKFLOW.is_file():\n        release = RELEASE_DOC.read_text(encoding="utf-8")\n        assert "常設CIは現在無効" in release\n        return\n\n    workflow = CI_WORKFLOW.read_text(encoding="utf-8")\n    assert not re.search(r"^\\s+(?:DATABASE_URL|RUN_PG_TESTS):", workflow, re.MULTILINE)\n    assert workflow.count("KJ_ATLAS_DATABASE_URL:") == 5\n    assert workflow.count("KJ_ATLAS_RUN_PG_TESTS:") == 1\n''',
)

provider_test = BACKEND_TESTS / "test_llm_provider.py"
provider_text = provider_test.read_text(encoding="utf-8")
old_payload = '{\\"suggestions\\":[{\\"groupId\\":\\"g1\\",\\"cardIds\\":[\\"c1\\",\\"c2\\"],\\"mergedTextDraft\\":\\"merged\\"}]}'
new_payload = '{\\"suggestions\\":[{\\"groupId\\":\\"g1\\",\\"cardIds\\":[\\"c1\\",\\"c2\\"],\\"mergedTextDraft\\":\\"merged\\",\\"mergeMethod\\":\\"near_duplicate\\"}]}'
count = provider_text.count(old_payload)
if count != 2:
    raise SystemExit(f"provider fixture anchor mismatch: {count}")
provider_text = provider_text.replace(old_payload, new_payload)
assert_anchor = '        assert list(local_response.json().keys()) == ["suggestions"]\n'
if provider_text.count(assert_anchor) != 1:
    raise SystemExit("provider assertion anchor mismatch")
provider_text = provider_text.replace(
    assert_anchor,
    assert_anchor
    + '        assert local_response.json()["suggestions"][0]["mergeMethod"] == "near_duplicate"\n',
    1,
)
provider_test.write_text(provider_text, encoding="utf-8")

print("patched backend full-suite contract drift")
