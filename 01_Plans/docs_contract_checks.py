#!/usr/bin/env python3
"""Deterministic documentation-contract checks used by the docs-check entrypoint."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

RELATIVE_LINK_RULE_ID = "DC-LNK-001"
CURRENT_HISTORY_RULE_ID = "DC-CUR-001"
HISTORY_METADATA_RULE_ID = "DC-HIS-001"
ARCHITECTURE_BASELINE_RULE_ID = "DC-ARC-001"
PUBLIC_BOUNDARY_RULE_ID = "DC-PUB-001"
SAFETY_ROUTE_RULE_ID = "DC-SAF-001"
NPM_SCRIPT_COMMAND_RULE_ID = "DC-CMD-001"
DOCUMENT_TYPE_RE = re.compile(r"export type (Document\w*)\s*=\s*\{\s*\r?\n\s*version:\s*([^;]+);")
FENCE_RE = re.compile(r"^[ \t]{0,3}(?P<fence>`{3,}|~{3,})")
INLINE_CODE_RE = re.compile(r"(?P<ticks>`+)[^\r\n]*?(?P=ticks)")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]\r\n]*\]\((?P<target><[^>\r\n]+>|[^)\r\n]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(?P<title>.+)$", re.MULTILINE)
HISTORY_HEADING_RE = re.compile(
    r"(?:(?<![A-Za-z])stream(?![A-Za-z])|rerun|checkpoint|reaffirmation|execution\s+(?:log|record)|"
    r"phase\s+verification\s+log|fixed\s+execution\s+scope)",
    re.IGNORECASE,
)
CURRENT_ONLY_PATHS = (
    Path("01_Plans/project-progress-dashboard.md"),
    Path("01_Plans/issues/README.md"),
    Path("01_Plans/documentation_quality.md"),
    Path("02_Architecture/architecture.md"),
    Path("02_Architecture/api.md"),
    Path("02_Architecture/schemas.md"),
    Path("02_Architecture/data_model_operations_overview.md"),
    Path("03_Implement/frontend/docs/e2e_testing.md"),
)
HISTORY_REQUIRED_LABELS = (
    "Status: Informative history",
    "Source document:",
    "Source anchors:",
    "Covered period:",
    "Snapshot / source revision:",
    "Retention reason:",
    "Current normative anchors:",
)
SOURCE_DOCUMENT_RE = re.compile(
    r"^Source document:\s+\[[^\]]+\]\((?P<target>[^)#]+)(?:#[^)]+)?\)",
    re.MULTILINE,
)
CURRENT_ANCHOR_RE = re.compile(
    r"^Current normative anchors:\s*$[\s\S]*?^-\s+\[[^\]]+\]\((?:\.\./|/)[^)]+\)",
    re.MULTILINE,
)
PUBLIC_ENTRY_PATH = Path("04_Documentation/public_index.md")
PUBLIC_UI_CATALOG_PATH = Path("04_Documentation/ui_catalog.md")
SCREENSHOT_LEDGER_PATH = Path("04_Documentation/assets/screenshots/README.md")
PUBLIC_ENTRY_FORBIDDEN_TERMS = (
    "04_Documentation",
    "00_Prompt",
    "01_Plans",
    "AGENTS.md",
    "PUBLICATION_MANIFEST",
    "内部管理",
    "文書保守者",
    "Issue/ADR",
    "作業ログ",
)
PUBLIC_UI_CATALOG_FORBIDDEN_TERMS = (
    "00_Prompt",
    "01_Plans",
    "ADR-",
    "issue-",
    "UX-NAV",
    "UX-COMPLEXITY",
    "Claude Design",
)
PUBLIC_UI_CATALOG_REQUIRED_TERMS = (
    "確認対象revision",
    "最終確認日",
    "表示条件",
    "画像検証",
    "公開状態",
)
SCREENSHOT_LEDGER_REQUIRED_TERMS = (
    "source revision",
    "撮影日",
    "fixture",
    "locale",
    "viewport",
    "生成スクリプト",
    "検証結果",
)
AGENT_ENTRY_PATH = Path("AGENTS.md")
AGENT_SAFETY_REQUIRED_TERMS = (
    "SafeModeは既定ON",
    "AI出力はproposal-only",
    "`human_reviewed` は人間だけが設定する",
    "`KJ_ATLAS_LLM_PROVIDER=none` でも主要価値が成立する",
    "share/exportで未レビュー情報や秘密情報を意図せず共有しない",
    "import/zip/markdownは不正入力を安全側で拒否または無害化する",
)
AGENT_SAFETY_REQUIRED_ROUTES = (
    "THREAT_MODEL.md",
    "02_Architecture/architecture.md",
    "04_Documentation/public_index.md",
)
PUBLIC_SAFETY_ROUTES = {
    "data_handling.md": ("SafeMode", "未レビュー", "共有"),
    "security.md": ("SafeMode", "共有"),
    "ce2_low_risk_ai_assist.md": ("proposal-only", "human_reviewed"),
    "configuration.md": ("KJ_ATLAS_LLM_PROVIDER=none",),
}
NPM_SCRIPT_RE = re.compile(r"npm run\s+([\w:-]+)")
FRONTEND_PACKAGE_JSON_PATH = Path("03_Implement/frontend/package.json")
# DC-CMD-001 only scans the current/public surface a user or fresh-clone
# contributor would copy commands from -- not 00_Prompt/01_Plans process
# memos, which record historical verification commands (run against
# whatever the script set was at the time) rather than a live copy target.
CURRENT_PUBLIC_DOC_ROOTS = (
    Path("README.md"),
    Path("CONTRIBUTING.md"),
    Path("04_Documentation"),
    Path("03_Implement/frontend/docs/e2e_testing.md"),
)
# Only these subcommands take a service-name argument in current/public docs
# (up/down/ps/config operate on the whole project or take no service arg here).
COMPOSE_SERVICE_SUBCOMMANDS = ("logs", "exec", "restart", "stop", "start", "run", "kill", "pause", "unpause", "top")
COMPOSE_SERVICE_COMMAND_RE = re.compile(
    r"docker compose\s+(" + "|".join(COMPOSE_SERVICE_SUBCOMMANDS) + r")\s+(?:-\S+\s+)*([\w-]+)"
)
COMPOSE_FILE_PATH = Path("03_Implement/deploy/docker-compose.yml")
RUNTIME_PARAMETER_KEY_RE = re.compile(r"KJ_ATLAS_[A-Z0-9_]+")
RUNTIME_PARAMETER_REGISTRY_PATH = Path("02_Architecture/runtime_parameter_registry.md")
RUNTIME_PARAMETER_REGISTRY_ROW_RE = re.compile(r"^\|\s*`(KJ_ATLAS_[A-Z0-9_]+)`[^|]*\|", re.MULTILINE)
REPOSITORY_PATH_PREFIX_RE = re.compile(r"^(00_Prompt|01_Plans|02_Architecture|03_Implement|04_Documentation|\.github)/")
REPOSITORY_PATH_FORBIDDEN_CHARS = frozenset(" <>*{|")
BACKTICK_TOKEN_RE = re.compile(r"`([^`\r\n]+)`")
TRAILING_LINE_REF_RE = re.compile(r":\d+$")
# Build-output directory names that legitimately don't exist in a fresh
# checkout (gitignored, created only by running the build) -- an explicit
# allowlist rather than parsing .gitignore, since `git check-ignore` only
# recognizes a directory-only pattern like `dist/` when the path already
# exists on disk to prove it's a directory, which defeats checking a path
# that's *expected* to be absent until built (e.g. release.md's reference
# to the frontend-build CI artifact's contents).
REPOSITORY_PATH_BUILD_OUTPUT_LEAF_NAMES = frozenset({"dist", "node_modules", "build", "__pycache__", ".venv"})
CLI_OPTION_COMMAND_RE = re.compile(r"python3?\s+([\w./-]+\.py)((?:\s+--[\w-]+(?:[= ][^\s`]+)?)*)")
CLI_OPTION_FLAG_RE = re.compile(r"--[\w-]+")
CLI_OPTION_ADD_ARGUMENT_RE = re.compile(r"add_argument\(\s*[\"'](--[\w-]+)")
LOCALHOST_PROBE_RE = re.compile(r"https?://localhost[:/][\w./:?=&-]*")
# Every entry must carry a provenance comment tracing it to an actual route
# (nginx.conf proxy_pass target, a backend route, or a documented dev-server
# port) -- audited against current/public docs on 2026-07-18 per the issue's
# Sonnet execution plan (issue-DX-DOC-04...) 区分6.
LOCALHOST_PROBE_ALLOWLIST_EXACT = frozenset(
    {
        "http://localhost:8080/api/healthz",  # nginx `location /api/` -> `api:8000`'s `/healthz`
        "http://localhost:8000/healthz",  # backend started directly (no nginx/Compose)
        "http://localhost:8001/generate",  # local LLM provider HTTP contract endpoint
        "http://localhost:8001",  # mock adapter / local LLM base URL example
        "http://localhost:4173/api/healthz",  # vite preview server, e2e_testing.md
        "http://localhost:8080",  # web entry point (nginx-fronted SPA)
    }
)
LOCALHOST_PROBE_ALLOWLIST_PREFIX = (
    "http://localhost:8080/api/docs/",  # document API GET examples; doc id varies per example
)


@dataclass(frozen=True)
class DocsCheckFinding:
    rule_id: str
    path: str
    line: int
    target: str
    message: str
    fix_hint: str

    def render(self) -> str:
        return f"{self.rule_id} {self.path}:{self.line}: {self.message} Fix: {self.fix_hint}"


def _without_fenced_code(text: str) -> str:
    """Replace fenced-code content with blank lines while preserving line numbers."""
    output: list[str] = []
    fence_char = ""
    fence_length = 0

    for line in text.splitlines(keepends=True):
        match = FENCE_RE.match(line)
        if not fence_char:
            if match:
                marker = match.group("fence")
                fence_char = marker[0]
                fence_length = len(marker)
                output.append("\n" if line.endswith(("\n", "\r")) else "")
            else:
                output.append(line)
            continue

        if match:
            marker = match.group("fence")
            if marker[0] == fence_char and len(marker) >= fence_length:
                fence_char = ""
                fence_length = 0
        output.append("\n" if line.endswith(("\n", "\r")) else "")

    return "".join(output)


def _without_code(text: str) -> str:
    return INLINE_CODE_RE.sub("", _without_fenced_code(text))


def _link_destination(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<"):
        closing = target.find(">")
        return target[1:closing] if closing >= 0 else target
    return target.split(maxsplit=1)[0] if target else ""


def _is_external_or_anchor(destination: str) -> bool:
    if not destination or destination.startswith("#") or destination.startswith("//"):
        return True
    return bool(urlsplit(destination).scheme)


def check_relative_links(root: Path, markdown_paths: list[Path]) -> list[DocsCheckFinding]:
    """Return DC-LNK-001 findings for missing or out-of-repository targets."""
    repository_root = root.resolve()
    findings: list[DocsCheckFinding] = []

    for supplied_path in sorted(markdown_paths, key=lambda path: path.as_posix()):
        source = supplied_path if supplied_path.is_absolute() else repository_root / supplied_path
        source = source.resolve()
        source_label = source.relative_to(repository_root).as_posix()
        text = _without_code(source.read_text(encoding="utf-8"))

        for match in MARKDOWN_LINK_RE.finditer(text):
            destination = _link_destination(match.group("target"))
            if _is_external_or_anchor(destination):
                continue

            parsed = urlsplit(destination)
            relative_target = unquote(parsed.path)
            if not relative_target:
                continue

            if relative_target.startswith("/"):
                resolved_target = (repository_root / relative_target.lstrip("/")).resolve()
            else:
                resolved_target = (source.parent / relative_target).resolve()

            line = text.count("\n", 0, match.start()) + 1
            try:
                resolved_target.relative_to(repository_root)
            except ValueError:
                findings.append(
                    DocsCheckFinding(
                        rule_id=RELATIVE_LINK_RULE_ID,
                        path=source_label,
                        line=line,
                        target=destination,
                        message=f"relative target escapes the repository: {destination}",
                        fix_hint="Point the link to a tracked repository document.",
                    )
                )
                continue

            if not resolved_target.exists():
                findings.append(
                    DocsCheckFinding(
                        rule_id=RELATIVE_LINK_RULE_ID,
                        path=source_label,
                        line=line,
                        target=destination,
                        message=f"relative target does not exist: {destination}",
                        fix_hint=f"Update the target relative to {source.parent.relative_to(repository_root).as_posix()} or add the referenced file.",
                    )
                )

    return findings


def check_current_history_headings(
    root: Path, markdown_paths: tuple[Path, ...] = CURRENT_ONLY_PATHS
) -> list[DocsCheckFinding]:
    """Return DC-CUR-001 findings when execution-history headings enter current docs."""
    findings: list[DocsCheckFinding] = []
    for relative_path in markdown_paths:
        source = root / relative_path
        text = _without_code(source.read_text(encoding="utf-8"))
        for match in HEADING_RE.finditer(text):
            title = match.group("title").strip()
            if not HISTORY_HEADING_RE.search(title):
                continue
            findings.append(
                DocsCheckFinding(
                    rule_id=CURRENT_HISTORY_RULE_ID,
                    path=relative_path.as_posix(),
                    line=text.count("\n", 0, match.start()) + 1,
                    target=title,
                    message=f"execution-history heading appears in a current-only document: {title}",
                    fix_hint="Move formation or execution history to 02_Architecture/history or Git history.",
                )
            )
    return findings


def check_document_contract_baseline(
    root: Path,
    schemas_path: Path = Path("02_Architecture/schemas.md"),
    api_path: Path = Path("02_Architecture/api.md"),
    data_model_path: Path = Path("02_Architecture/data_model_operations_overview.md"),
) -> list[DocsCheckFinding]:
    """Return DC-ARC-001 findings when the single-DocumentV1 baseline (ADR-0058) regresses.

    Checks the raw text (not `_without_code`) since the Document type definition
    and its version live inside fenced ```ts blocks.
    """
    findings: list[DocsCheckFinding] = []

    schemas_text = (root / schemas_path).read_text(encoding="utf-8")
    document_types = list(DOCUMENT_TYPE_RE.finditer(schemas_text))
    if len(document_types) != 1:
        line = schemas_text.count("\n", 0, document_types[-1].start()) + 1 if document_types else 1
        findings.append(
            DocsCheckFinding(
                rule_id=ARCHITECTURE_BASELINE_RULE_ID,
                path=schemas_path.as_posix(),
                line=line,
                target="Document",
                message=f"expected exactly one persistent Document type definition, found {len(document_types)}",
                fix_hint="Consolidate all Document type definitions into a single DocumentV1 (version: 1) per ADR-0058.",
            )
        )
    else:
        type_name = document_types[0].group(1)
        version_literal = document_types[0].group(2).strip()
        if type_name != "DocumentV1" or version_literal != "1":
            findings.append(
                DocsCheckFinding(
                    rule_id=ARCHITECTURE_BASELINE_RULE_ID,
                    path=schemas_path.as_posix(),
                    line=schemas_text.count("\n", 0, document_types[0].start()) + 1,
                    target=type_name,
                    message=f"the sole Document type must be `DocumentV1` with `version: 1`, found `{type_name}` with version {version_literal}",
                    fix_hint="Rename the type to DocumentV1 and set version to the literal 1, per ADR-0058.",
                )
            )

    if "DocumentV2" in schemas_text:
        offset = schemas_text.find("DocumentV2")
        findings.append(
            DocsCheckFinding(
                rule_id=ARCHITECTURE_BASELINE_RULE_ID,
                path=schemas_path.as_posix(),
                line=schemas_text.count("\n", 0, offset) + 1,
                target="DocumentV2",
                message="obsolete DocumentV2 name reappeared in the current contract",
                fix_hint="Rename to DocumentV1 (version: 1), or move the historical mention to 02_Architecture/history.",
            )
        )

    if "Legacy" in schemas_text:
        offset = schemas_text.find("Legacy")
        findings.append(
            DocsCheckFinding(
                rule_id=ARCHITECTURE_BASELINE_RULE_ID,
                path=schemas_path.as_posix(),
                line=schemas_text.count("\n", 0, offset) + 1,
                target="Legacy",
                message="legacy version-normalization language reappeared; only version: 1 is accepted (fail-closed)",
                fix_hint="Remove the Legacy normalization note — unknown or old versions must be rejected outright, not normalized.",
            )
        )

    for label, path in (("api.md", api_path), ("data_model_operations_overview.md", data_model_path)):
        text = (root / path).read_text(encoding="utf-8")
        if "DocumentV2" in text:
            offset = text.find("DocumentV2")
            findings.append(
                DocsCheckFinding(
                    rule_id=ARCHITECTURE_BASELINE_RULE_ID,
                    path=path.as_posix(),
                    line=text.count("\n", 0, offset) + 1,
                    target="DocumentV2",
                    message=f"{label} still references the obsolete DocumentV2 name",
                    fix_hint="Update the reference to DocumentV1.",
                )
            )
        if "DocumentV1" not in text:
            findings.append(
                DocsCheckFinding(
                    rule_id=ARCHITECTURE_BASELINE_RULE_ID,
                    path=path.as_posix(),
                    line=1,
                    target="DocumentV1",
                    message=f"{label} does not reference DocumentV1 anywhere",
                    fix_hint="Add or restore a DocumentV1 reference (API I/F or support-level table).",
                )
            )

    return findings


def check_history_metadata(
    root: Path, history_paths: list[Path] | None = None
) -> list[DocsCheckFinding]:
    """Return DC-HIS-001 findings for incomplete history metadata or reverse links."""
    if history_paths is None:
        history_paths = sorted(
            path.relative_to(root)
            for path in (root / "02_Architecture" / "history").glob("*.md")
            if path.name != "README.md"
        )

    findings: list[DocsCheckFinding] = []
    for relative_path in history_paths:
        source = root / relative_path
        text = source.read_text(encoding="utf-8")
        for label in HISTORY_REQUIRED_LABELS:
            if label in text:
                continue
            findings.append(
                DocsCheckFinding(
                    rule_id=HISTORY_METADATA_RULE_ID,
                    path=relative_path.as_posix(),
                    line=1,
                    target=label,
                    message=f"history metadata is missing: {label}",
                    fix_hint="Add the required Informative history metadata near the document heading.",
                )
            )

        if "Current normative anchors:" in text and not CURRENT_ANCHOR_RE.search(text):
            anchor_offset = text.find("Current normative anchors:")
            findings.append(
                DocsCheckFinding(
                    rule_id=HISTORY_METADATA_RULE_ID,
                    path=relative_path.as_posix(),
                    line=text.count("\n", 0, anchor_offset) + 1,
                    target="Current normative anchors",
                    message="history document has no current normative anchor link",
                    fix_hint="Add at least one link from Current normative anchors to a current contract.",
                )
            )

        source_match = SOURCE_DOCUMENT_RE.search(text)
        if not source_match:
            continue
        current_path = (source.parent / source_match.group("target")).resolve()
        if not current_path.exists():
            continue
        backlink = relative_path.relative_to(current_path.parent.relative_to(root)).as_posix()
        current_text = current_path.read_text(encoding="utf-8")
        if backlink not in current_text:
            findings.append(
                DocsCheckFinding(
                    rule_id=HISTORY_METADATA_RULE_ID,
                    path=relative_path.as_posix(),
                    line=1,
                    target=current_path.relative_to(root).as_posix(),
                    message="source document does not link back to its formation history",
                    fix_hint=f"Add a link to {backlink} from the source document.",
                )
            )
    return findings


def check_public_boundary(
    root: Path,
    entry_path: Path = PUBLIC_ENTRY_PATH,
    catalog_path: Path = PUBLIC_UI_CATALOG_PATH,
    ledger_path: Path = SCREENSHOT_LEDGER_PATH,
) -> list[DocsCheckFinding]:
    """Return DC-PUB-001 findings for public-entry leakage and missing UI provenance."""
    findings: list[DocsCheckFinding] = []
    entry_text = (root / entry_path).read_text(encoding="utf-8")
    catalog_text = (root / catalog_path).read_text(encoding="utf-8")
    ledger_text = (root / ledger_path).read_text(encoding="utf-8")

    for path, text, forbidden_terms in (
        (entry_path, entry_text, PUBLIC_ENTRY_FORBIDDEN_TERMS),
        (catalog_path, catalog_text, PUBLIC_UI_CATALOG_FORBIDDEN_TERMS),
    ):
        for term in forbidden_terms:
            offset = text.find(term)
            if offset < 0:
                continue
            findings.append(
                DocsCheckFinding(
                    rule_id=PUBLIC_BOUNDARY_RULE_ID,
                    path=path.as_posix(),
                    line=text.count("\n", 0, offset) + 1,
                    target=term,
                    message=f"internal project-management marker appears in a public document: {term}",
                    fix_hint="Remove the internal marker and describe only the user-facing behavior or procedure.",
                )
            )

    linked_destinations = {
        urlsplit(_link_destination(match.group("target"))).path
        for match in MARKDOWN_LINK_RE.finditer(_without_code(entry_text))
    }
    if "ui_catalog.md" not in linked_destinations:
        findings.append(
            DocsCheckFinding(
                rule_id=PUBLIC_BOUNDARY_RULE_ID,
                path=entry_path.as_posix(),
                line=1,
                target="ui_catalog.md",
                message="the public entry has no route to the current UI catalog",
                fix_hint="Add a purpose-oriented link to ui_catalog.md from public_index.md.",
            )
        )

    for path, text, required_terms in (
        (catalog_path, catalog_text, PUBLIC_UI_CATALOG_REQUIRED_TERMS),
        (ledger_path, ledger_text, SCREENSHOT_LEDGER_REQUIRED_TERMS),
    ):
        for term in required_terms:
            if term in text:
                continue
            findings.append(
                DocsCheckFinding(
                    rule_id=PUBLIC_BOUNDARY_RULE_ID,
                    path=path.as_posix(),
                    line=1,
                    target=term,
                    message=f"public UI evidence is missing required provenance: {term}",
                    fix_hint="Restore the provenance field and record the current verified value.",
                )
            )

    return findings


def check_safety_routes(
    root: Path,
    agent_entry_path: Path = AGENT_ENTRY_PATH,
    public_entry_path: Path = PUBLIC_ENTRY_PATH,
) -> list[DocsCheckFinding]:
    """Return DC-SAF-001 findings when agent or public safety routes are incomplete."""
    findings: list[DocsCheckFinding] = []
    agent_text = (root / agent_entry_path).read_text(encoding="utf-8")
    public_text = (root / public_entry_path).read_text(encoding="utf-8")

    for term in AGENT_SAFETY_REQUIRED_TERMS:
        if term in agent_text:
            continue
        findings.append(
            DocsCheckFinding(
                rule_id=SAFETY_ROUTE_RULE_ID,
                path=agent_entry_path.as_posix(),
                line=1,
                target=term,
                message=f"the AI entrypoint is missing a safety invariant: {term}",
                fix_hint="Restore the invariant in AGENTS.md without weakening its fail-safe meaning.",
            )
        )

    for route in AGENT_SAFETY_REQUIRED_ROUTES:
        if route in agent_text and (root / route).exists():
            continue
        findings.append(
            DocsCheckFinding(
                rule_id=SAFETY_ROUTE_RULE_ID,
                path=agent_entry_path.as_posix(),
                line=1,
                target=route,
                message=f"the AI entrypoint has no valid route to a safety source: {route}",
                fix_hint="Restore the repository-relative path in AGENTS.md and ensure the target exists.",
            )
        )

    public_destinations = {
        urlsplit(_link_destination(match.group("target"))).path
        for match in MARKDOWN_LINK_RE.finditer(_without_code(public_text))
    }
    for destination, required_terms in PUBLIC_SAFETY_ROUTES.items():
        target_path = public_entry_path.parent / destination
        if destination not in public_destinations or not (root / target_path).exists():
            findings.append(
                DocsCheckFinding(
                    rule_id=SAFETY_ROUTE_RULE_ID,
                    path=public_entry_path.as_posix(),
                    line=1,
                    target=destination,
                    message=f"the public entry has no valid route to a safety guide: {destination}",
                    fix_hint=f"Add or restore a Markdown link to {destination} from public_index.md.",
                )
            )
            continue

        target_text = (root / target_path).read_text(encoding="utf-8")
        for term in required_terms:
            if term in target_text:
                continue
            findings.append(
                DocsCheckFinding(
                    rule_id=SAFETY_ROUTE_RULE_ID,
                    path=target_path.as_posix(),
                    line=1,
                    target=term,
                    message=f"the routed safety guide is missing its required boundary: {term}",
                    fix_hint=f"Restore the {term} explanation in {destination} or route to the current guide.",
                )
            )

    return findings


def _is_current_public_doc(relative_path: Path) -> bool:
    for scoped_root in CURRENT_PUBLIC_DOC_ROOTS:
        if relative_path == scoped_root or scoped_root in relative_path.parents:
            return True
    return False


def check_npm_script_commands(
    root: Path,
    markdown_paths: list[Path],
    package_json_path: Path = FRONTEND_PACKAGE_JSON_PATH,
) -> list[DocsCheckFinding]:
    """Return DC-CMD-001 findings for `npm run <script>` examples with no matching script.

    A copyable `npm run <script>` example is a user-facing interface, not
    prose; if the script was renamed or removed, the documented command fails
    the moment someone actually runs it. Scoped to current/public
    documentation only -- see CURRENT_PUBLIC_DOC_ROOTS.

    Returns no findings (rather than raising) when package_json_path doesn't
    exist under root -- callers that only need the repository's other
    contract checks (e.g. isolated fixture directories in this module's own
    tests) aren't required to also provide a frontend package.json.
    """
    repository_root = root.resolve()
    resolved_package_json = repository_root / package_json_path
    if not resolved_package_json.exists():
        return []
    scripts = set(json.loads(resolved_package_json.read_text(encoding="utf-8")).get("scripts", {}).keys())

    findings: list[DocsCheckFinding] = []
    for supplied_path in sorted(markdown_paths, key=lambda path: path.as_posix()):
        relative_path = supplied_path if not supplied_path.is_absolute() else supplied_path.relative_to(repository_root)
        if not _is_current_public_doc(relative_path):
            continue

        source = repository_root / relative_path
        text = source.read_text(encoding="utf-8")
        for match in NPM_SCRIPT_RE.finditer(text):
            script_name = match.group(1)
            if script_name in scripts:
                continue
            line = text.count("\n", 0, match.start()) + 1
            findings.append(
                DocsCheckFinding(
                    rule_id=NPM_SCRIPT_COMMAND_RULE_ID,
                    path=relative_path.as_posix(),
                    line=line,
                    target=f"npm run {script_name}",
                    message=f"npm script '{script_name}' does not exist in {package_json_path.as_posix()}",
                    fix_hint="Use an existing script name from package.json's scripts, or add the script if it is genuinely new.",
                )
            )

    return findings


def _extract_compose_services(compose_text: str) -> set[str]:
    """Return the top-level `services:` child keys from a Compose file's text.

    Deliberately not a full YAML parser -- kj-atlas's own compose files use a
    flat, consistently 2-space-indented `services:` block, so a line-based
    scan is enough and avoids adding a YAML dependency for one deterministic
    check.
    """
    services: set[str] = set()
    in_services_block = False
    for line in compose_text.splitlines():
        if re.match(r"^services:\s*$", line):
            in_services_block = True
            continue
        if not in_services_block:
            continue
        if re.match(r"^\S", line):
            break
        match = re.match(r"^  ([\w-]+):\s*$", line)
        if match:
            services.add(match.group(1))
    return services


def check_compose_service_commands(
    root: Path,
    markdown_paths: list[Path],
    compose_file_path: Path = COMPOSE_FILE_PATH,
) -> list[DocsCheckFinding]:
    """Return DC-CMD-001 findings for `docker compose <cmd> <service>` examples
    referencing a service absent from the standard Compose file.

    Only checks subcommands that take a service-name argument in current
    usage (COMPOSE_SERVICE_SUBCOMMANDS); `up`/`down`/`ps`/`config` are not
    scanned since current/public docs use them project-wide, not per-service.
    Scoped to current/public documentation only -- see CURRENT_PUBLIC_DOC_ROOTS.

    Returns no findings when compose_file_path doesn't exist under root, for
    the same reason check_npm_script_commands tolerates a missing
    package.json: isolated fixture directories in this module's own tests
    aren't required to also provide a real Compose file.
    """
    repository_root = root.resolve()
    resolved_compose_file = repository_root / compose_file_path
    if not resolved_compose_file.exists():
        return []
    services = _extract_compose_services(resolved_compose_file.read_text(encoding="utf-8"))

    findings: list[DocsCheckFinding] = []
    for supplied_path in sorted(markdown_paths, key=lambda path: path.as_posix()):
        relative_path = supplied_path if not supplied_path.is_absolute() else supplied_path.relative_to(repository_root)
        if not _is_current_public_doc(relative_path):
            continue

        source = repository_root / relative_path
        text = source.read_text(encoding="utf-8")
        for match in COMPOSE_SERVICE_COMMAND_RE.finditer(text):
            subcommand, service_name = match.group(1), match.group(2)
            if service_name in services:
                continue
            line = text.count("\n", 0, match.start()) + 1
            findings.append(
                DocsCheckFinding(
                    rule_id=NPM_SCRIPT_COMMAND_RULE_ID,
                    path=relative_path.as_posix(),
                    line=line,
                    target=f"docker compose {subcommand} {service_name}",
                    message=f"Compose service '{service_name}' does not exist in {compose_file_path.as_posix()}",
                    fix_hint="Use an existing service name from docker-compose.yml's services, or add the service if it is genuinely new.",
                )
            )

    return findings


def _extract_registry_keys(registry_text: str) -> set[str]:
    """Return every `KJ_ATLAS_*` key documented as a table row's first cell.

    A single regex over the whole file (rather than per-table parsing) is
    enough: the Private adapter boundary table's first-cell values (e.g.
    `POSTGRES_DB`) don't start with `KJ_ATLAS_`, so they're excluded by the
    pattern itself without needing to track which section a row is in.
    """
    return set(RUNTIME_PARAMETER_REGISTRY_ROW_RE.findall(registry_text))


def check_runtime_parameter_key_commands(
    root: Path,
    markdown_paths: list[Path],
    registry_path: Path = RUNTIME_PARAMETER_REGISTRY_PATH,
) -> list[DocsCheckFinding]:
    """Return DC-CMD-001 findings for `KJ_ATLAS_*` keys absent from the registry.

    Excludes prefix mentions (e.g. `KJ_ATLAS_AUDIT_*`), which the greedy
    `KJ_ATLAS_[A-Z0-9_]+` match reduces to a trailing-underscore token (e.g.
    `KJ_ATLAS_AUDIT_`) since `*` isn't in the character class -- those are
    documentation shorthand for "this key family", not a single copyable key,
    so they're skipped rather than treated as an unknown key.
    Scoped to current/public documentation only -- see CURRENT_PUBLIC_DOC_ROOTS.

    Returns no findings when registry_path doesn't exist under root, for the
    same reason the npm-script and Compose-service checks tolerate a missing
    canonical source: isolated fixture directories in this module's own tests
    aren't required to also provide a real registry document.
    """
    repository_root = root.resolve()
    resolved_registry = repository_root / registry_path
    if not resolved_registry.exists():
        return []
    registry_keys = _extract_registry_keys(resolved_registry.read_text(encoding="utf-8"))

    findings: list[DocsCheckFinding] = []
    for supplied_path in sorted(markdown_paths, key=lambda path: path.as_posix()):
        relative_path = supplied_path if not supplied_path.is_absolute() else supplied_path.relative_to(repository_root)
        if not _is_current_public_doc(relative_path):
            continue

        source = repository_root / relative_path
        text = source.read_text(encoding="utf-8")
        for match in RUNTIME_PARAMETER_KEY_RE.finditer(text):
            key = match.group(0)
            if key.endswith("_"):
                continue
            if match.end() < len(text) and text[match.end()] == "*":
                continue
            if key in registry_keys:
                continue
            line = text.count("\n", 0, match.start()) + 1
            findings.append(
                DocsCheckFinding(
                    rule_id=NPM_SCRIPT_COMMAND_RULE_ID,
                    path=relative_path.as_posix(),
                    line=line,
                    target=key,
                    message=f"Runtime parameter key '{key}' does not exist in {registry_path.as_posix()}",
                    fix_hint="Use an existing key from runtime_parameter_registry.md, or add the new key to the registry first.",
                )
            )

    return findings


def check_repository_path_commands(
    root: Path,
    markdown_paths: list[Path],
) -> list[DocsCheckFinding]:
    """Return DC-CMD-001 findings for inline-code repository paths that don't exist.

    Scans backtick-delimited tokens (not Markdown links -- those are
    DC-LNK-001's job) that start with a known repository root
    (00_Prompt/, 01_Plans/, 02_Architecture/, 03_Implement/,
    04_Documentation/, .github/) and contain none of the characters that
    mark a placeholder or shell-glob rather than a literal copyable path
    (space, <, >, *, {, |). A trailing `:N` line reference is stripped
    before existence is checked.

    Checks filesystem existence directly under `root` rather than
    replicating tracked_markdown_paths()'s `git ls-files` call: every
    path this check can match lives inside the same working tree being
    linted, so on-disk existence and tracked existence coincide here.
    This also means Path.exists() alone covers "token matches a
    directory that contains tracked files" -- exactly the directory-
    prefix case the issue's plan calls out -- with no extra logic
    needed, since Path.exists() is true for directories too.

    A path whose final segment is a known build-output directory name
    (REPOSITORY_PATH_BUILD_OUTPUT_LEAF_NAMES) is accepted without
    existing, provided its parent directory exists, since such paths
    are legitimately absent until a build actually runs (e.g. release.md
    describing what `03_Implement/frontend/dist` contains as a CI
    artifact).
    Scoped to current/public documentation only -- see CURRENT_PUBLIC_DOC_ROOTS.
    """
    repository_root = root.resolve()

    findings: list[DocsCheckFinding] = []
    for supplied_path in sorted(markdown_paths, key=lambda path: path.as_posix()):
        relative_path = supplied_path if not supplied_path.is_absolute() else supplied_path.relative_to(repository_root)
        if not _is_current_public_doc(relative_path):
            continue

        source = repository_root / relative_path
        text = source.read_text(encoding="utf-8")
        for match in BACKTICK_TOKEN_RE.finditer(text):
            token = match.group(1)
            if not REPOSITORY_PATH_PREFIX_RE.match(token):
                continue
            if any(ch in REPOSITORY_PATH_FORBIDDEN_CHARS for ch in token):
                continue
            normalized = TRAILING_LINE_REF_RE.sub("", token)
            target_path = repository_root / normalized
            if target_path.exists():
                continue
            if PurePosixPath(normalized).name in REPOSITORY_PATH_BUILD_OUTPUT_LEAF_NAMES and target_path.parent.exists():
                continue
            line = text.count("\n", 0, match.start()) + 1
            findings.append(
                DocsCheckFinding(
                    rule_id=NPM_SCRIPT_COMMAND_RULE_ID,
                    path=relative_path.as_posix(),
                    line=line,
                    target=token,
                    message=f"Repository path '{normalized}' does not exist",
                    fix_hint="Fix the path, or if it is genuinely new, add the file/directory first.",
                )
            )

    return findings


def check_cli_option_commands(
    root: Path,
    markdown_paths: list[Path],
) -> list[DocsCheckFinding]:
    """Return DC-CMD-001 findings for `python <script>.py --option` examples
    where `--option` isn't in the script's own argparse definition.

    Only scripts that both exist under `root` (a missing script path is
    check_repository_path_commands's finding, not duplicated here) and
    contain the literal string "ArgumentParser" are checked; scripts
    without argparse are treated as unverifiable and skipped rather than
    guessed at, per the issue's fixed condition that this check never
    executes the scripts it inspects -- only their source text is read.
    Scoped to current/public documentation only -- see CURRENT_PUBLIC_DOC_ROOTS.
    """
    repository_root = root.resolve()

    findings: list[DocsCheckFinding] = []
    for supplied_path in sorted(markdown_paths, key=lambda path: path.as_posix()):
        relative_path = supplied_path if not supplied_path.is_absolute() else supplied_path.relative_to(repository_root)
        if not _is_current_public_doc(relative_path):
            continue

        source = repository_root / relative_path
        text = source.read_text(encoding="utf-8")
        for match in CLI_OPTION_COMMAND_RE.finditer(text):
            script_rel, options_tail = match.group(1), match.group(2)
            script_path = repository_root / script_rel
            if not script_path.exists():
                continue
            script_text = script_path.read_text(encoding="utf-8")
            if "ArgumentParser" not in script_text:
                continue
            known_options = set(CLI_OPTION_ADD_ARGUMENT_RE.findall(script_text))

            options_tail_start = match.start(2)
            for opt_match in CLI_OPTION_FLAG_RE.finditer(options_tail):
                option = opt_match.group(0)
                if option in known_options:
                    continue
                line = text.count("\n", 0, options_tail_start + opt_match.start()) + 1
                findings.append(
                    DocsCheckFinding(
                        rule_id=NPM_SCRIPT_COMMAND_RULE_ID,
                        path=relative_path.as_posix(),
                        line=line,
                        target=f"{script_rel} {option}",
                        message=f"CLI option '{option}' does not exist in {script_rel}",
                        fix_hint="Use an existing option from the script's argparse definition, or add the option if it is genuinely new.",
                    )
                )

    return findings


def check_localhost_probe_commands(
    root: Path,
    markdown_paths: list[Path],
) -> list[DocsCheckFinding]:
    """Return DC-CMD-001 findings for localhost URLs absent from the probe allowlist.

    Catches the recurrence shape of a past real bug (`/api/health` missing
    the trailing `z`) by requiring every `http(s)://localhost...` example in
    current/public docs to be an explicitly allowlisted, provenance-commented
    route rather than accepted by pattern alone. A newly-legitimate URL is
    added to LOCALHOST_PROBE_ALLOWLIST_EXACT/_PREFIX only after confirming it
    against nginx.conf or the backend route it names -- never guessed.
    Scoped to current/public documentation only -- see CURRENT_PUBLIC_DOC_ROOTS.
    """
    repository_root = root.resolve()

    findings: list[DocsCheckFinding] = []
    for supplied_path in sorted(markdown_paths, key=lambda path: path.as_posix()):
        relative_path = supplied_path if not supplied_path.is_absolute() else supplied_path.relative_to(repository_root)
        if not _is_current_public_doc(relative_path):
            continue

        source = repository_root / relative_path
        text = source.read_text(encoding="utf-8")
        for match in LOCALHOST_PROBE_RE.finditer(text):
            url = match.group(0)
            if url in LOCALHOST_PROBE_ALLOWLIST_EXACT:
                continue
            if any(url.startswith(prefix) for prefix in LOCALHOST_PROBE_ALLOWLIST_PREFIX):
                continue
            line = text.count("\n", 0, match.start()) + 1
            findings.append(
                DocsCheckFinding(
                    rule_id=NPM_SCRIPT_COMMAND_RULE_ID,
                    path=relative_path.as_posix(),
                    line=line,
                    target=url,
                    message=f"Localhost URL '{url}' is not in the probe allowlist",
                    fix_hint="Confirm the route against nginx.conf/backend routes, then add it to LOCALHOST_PROBE_ALLOWLIST_EXACT/_PREFIX with a provenance comment.",
                )
            )

    return findings


def tracked_markdown_paths(root: Path) -> list[Path]:
    """Return tracked Markdown paths so generated and dependency files stay out of scope."""
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--", "*.md"],
        check=True,
        capture_output=True,
    )
    return [Path(raw.decode("utf-8")) for raw in result.stdout.split(b"\0") if raw]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate tracked Markdown contracts.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root (defaults to the parent of 01_Plans)",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    markdown_paths = tracked_markdown_paths(root)
    findings = check_relative_links(root, markdown_paths)
    findings.extend(check_current_history_headings(root))
    findings.extend(check_document_contract_baseline(root))
    findings.extend(check_history_metadata(root))
    findings.extend(check_public_boundary(root))
    findings.extend(check_safety_routes(root))
    findings.extend(check_npm_script_commands(root, markdown_paths))
    findings.extend(check_compose_service_commands(root, markdown_paths))
    findings.extend(check_runtime_parameter_key_commands(root, markdown_paths))
    findings.extend(check_repository_path_commands(root, markdown_paths))
    findings.extend(check_cli_option_commands(root, markdown_paths))
    findings.extend(check_localhost_probe_commands(root, markdown_paths))

    if findings:
        print("documentation contract validation failed:")
        for finding in findings:
            print(f"- {finding.render()}")
        return 1

    print(f"ok: checked {len(markdown_paths)} tracked Markdown files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
