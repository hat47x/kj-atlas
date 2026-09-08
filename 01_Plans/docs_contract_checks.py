#!/usr/bin/env python3
"""Deterministic documentation-contract checks used by the docs-check entrypoint."""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

RELATIVE_LINK_RULE_ID = "DC-LNK-001"
CODE_SPAN_CITATION_RULE_ID = "DC-LNK-002"
CURRENT_HISTORY_RULE_ID = "DC-CUR-001"
HISTORY_METADATA_RULE_ID = "DC-HIS-001"
ARCHITECTURE_BASELINE_RULE_ID = "DC-ARC-001"
API_RESPONSE_MODEL_RULE_ID = "DC-API-001"
PUBLIC_BOUNDARY_RULE_ID = "DC-PUB-001"
SAFETY_ROUTE_RULE_ID = "DC-SAF-001"
NPM_SCRIPT_COMMAND_RULE_ID = "DC-CMD-001"
RUNTIME_PARAMETER_DEFAULT_RULE_ID = "DC-CFG-001"
ADR_ID_UNIQUENESS_RULE_ID = "DC-ADR-001"
ADR_TRACEABILITY_PATH_RULE_ID = "DC-ADR-002"
CI_JOB_TIMEOUT_RULE_ID = "DC-CI-001"
ADR_FILENAME_RE = re.compile(r"^ADR-(?P<id>\d{4})-[^.]+\.md$")
ADR_TRACEABILITY_PATH_RE = re.compile(
    r"^- (?:Supersedes|Superseded by|Derived-from):\s+`(?P<target>01_Plans/adr/[^`]+)`",
    re.MULTILINE,
)
CI_WORKFLOW_PATHS = (
    Path(".github/workflows/ci.yml"),
    Path(".github/workflows/release.yml"),
)
CI_JOB_HEADER_RE = re.compile(r"^  (?P<job>[A-Za-z0-9_-]+):\s*$")
CI_JOB_TIMEOUT_RE = re.compile(r"^    timeout-minutes:\s*(?P<minutes>\d+)\s*$")
DOCUMENT_TYPE_RE = re.compile(r"export type (Document\w*)\s*=\s*\{\s*\r?\n\s*version:\s*([^;]+);")
FENCE_RE = re.compile(r"^[ \t]{0,3}(?P<fence>`{3,}|~{3,})")
INLINE_CODE_RE = re.compile(r"(?P<ticks>`+)[^\r\n]*?(?P=ticks)")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]\r\n]*\]\((?P<target><[^>\r\n]+>|[^)\r\n]+)\)")
HTML_SUFFIXES = frozenset({".html", ".htm"})
# HTML is scanned only where it is documentation. Unlike Markdown, HTML is also
# a runtime artifact in this repository: 03_Implement/frontend/index.html carries
# src="/src/main.tsx", which is root-relative to the dev server, not to the
# repository, and would be a false positive for the repository-relative link
# rule. Documentation roots keep the two apart.
DOCUMENTATION_HTML_ROOTS = (
    Path("00_Prompt"),
    Path("01_Plans"),
    Path("02_Architecture"),
    Path("04_Documentation"),
)
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
    Path("02_Architecture/architecture.html"),
    Path("02_Architecture/api.md"),
    Path("02_Architecture/schemas.md"),
    Path("02_Architecture/data_model_operations_overview.html"),
    Path("03_Implement/frontend/docs/e2e_testing.md"),
)
DOCUMENTED_RESPONSE_MODEL_REQUIRED_TERMS = {
    Path("02_Architecture/api.md"): (
        "/admin/provision/hil-rs/a2a3-gate:validate",
        "A2A3GateValidationResponse",
        "/docs/{doc_id}/similar-candidate-groups",
        "CandidateListViewModel",
        "/ai/provider-status",
        "ProviderStatusResponse",
    ),
    Path("02_Architecture/schemas.md"): (
        "A2A3GateValidationResponse",
        "CandidateListViewModel",
        "SimilarCandidateGroup",
        "generatedAt",
        "totalGroupCount",
        "ProviderStatusResponse",
        "providerKind",
    ),
}
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
    "02_Architecture/architecture.html",
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
# DC-LNK-002. `01_Plans/` Traceability/Scope/Related fields cite other documents
# as backtick code spans, not as `[text](path)` links, so DC-LNK-001 never saw
# them. A citation is only recognised as a path (rather than prose in backticks)
# when it ends in one of these suffixes -- the extension is what separates a file
# reference from an environment-variable name or a configuration key.
CITATION_SUFFIXES = frozenset({".md", ".html", ".py", ".ts", ".tsx"})
# Documents and modules that no longer exist anywhere in the repository and are
# cited deliberately, as history, by the record that retired them. Verified
# individually (DX-DOC-09); every entry names why the target is permanently
# absent, in the same provenance-comment style as
# LOCALHOST_PROBE_ALLOWLIST_EXACT above.
#
# Keyed by target path, not by (source, target) pair: "this document was removed
# from the repository" is a fact about the repository, so every citation of it is
# equally historical, and a pair-keyed list would be four times the size for no
# extra signal. The residual cost is that a *new* document genuinely intended to
# be created under one of these names would not be flagged as missing.
#
# Intent is stated here rather than inferred from the citing text, which is the
# lesson DX-CANON-INTENT-01 recorded: no wording heuristic separates "this file
# was deleted on purpose and the record says so" from "this citation rotted".
#
# Every entry below is a target that survived DX-DOC-09's mechanical passes:
# 446 of the 508 citations the rule first reported were repointed at files that
# had merely moved or been renamed. What remains is the residue that cannot be
# repointed, because there is nothing to point at.
RETIRED_CITATION_TARGETS: frozenset[str] = frozenset(
    {
        # Pre-ADR planning documents, all deleted in 906e8bbf ("docs: make
        # 01_Plans README a navigable ADR index") when the phase-plan format was
        # replaced by ADRs. Cited only from the `Replaces:` / `Source:` /
        # `Supersedes:` / `Migrated-from:` traceability fields of ADR-0000
        # through ADR-0009 -- the ADRs that retired them. Naming the retired
        # document is the entire purpose of those fields, so these are
        # historical citations, not rot.
        "01_Plans/roadmap.md",
        "01_Plans/value_to_requirements.md",
        "01_Plans/phase0_bootstrap.md",
        "01_Plans/phase1_canvas_mvp.md",
        "01_Plans/phase2_qualitative_integration.md",
        "01_Plans/phase3_review_governance.md",
        "01_Plans/phaseX_future_backlog.md",
        "01_Plans/phaseX_cli_tool.md",
        "01_Plans/phaseX_local_llm_integration.md",
        # Renamed away in 29fcffcc; cited by a done issue's audit record.
        "01_Plans/future_backlog.md",
        # ADR-0020 `Replaces:` -- a pre-ADR draft never tracked in git.
        "04_Documentation/auth_oidc_saml_mock_idp.md",
        # Modules deleted by the very issue that cites them. The citation names
        # what was removed; repointing it would falsify the record.
        "03_Implement/frontend/src/domain/merge/p2b_decision_log_mock.ts",  # DX-CLEANUP-01
        "03_Implement/frontend/src/domain/p2a_stream_d/mock_validation_stream_d.ts",  # DX-CLEANUP-01
        "03_Implement/frontend/src/domain/policy/access_control_metadata.ts",  # DX-CLEANUP-02
        "03_Implement/frontend/src/ui/DiffPanel.tsx",  # DX-CLEANUP-06 (8ab456f8)
        "03_Implement/frontend/src/ui/DiffPanel.test.ts",  # DX-CLEANUP-06 (8ab456f8)
        "03_Implement/backend/tests/test_settings_env_migration.py",  # ENV-ARCH-02
        # Replaced by the tabized work-mode surface in fbd1ff46 (UX-NAV-02).
        "03_Implement/frontend/src/ui/HilRsWorkflowPanel.tsx",
        # Proposed in a done issue's "next action" list and never adopted; the
        # content landed in the existing 04_Documentation/canonicalization.md.
        "02_Architecture/canonicalization_workflow.md",
        # Planned module for EXT-CONN-03, not yet built. schemas.md and the
        # issue describe the contract it will implement.
        "03_Implement/frontend/src/export/agent_constraints_export.ts",
        # Illustrative paths, not references: an example filename inside an
        # acceptance criterion, a probe path in a check's own test description,
        # and a dated-filename template placeholder.
        "01_Plans/xxx/result-analysis.md",
        "02_Architecture/_probe.md",
        "01_Plans/dogfood-log-2026-08-XX.md",
        # The filename DOGFOOD-07 reports as unstageable. The file exists under
        # the corrected name (dogfood-analysis-synthesis-2026-08-12.md); the old
        # name is the defect being recorded.
        "01_Plans/dogfood/result-analysis-synthesis-2026-08-12.md",
        # Static publish artifact, produced by `npm run publish:static -- --out
        # ../deploy/public` (03_Implement/README.md). Absent until a build runs,
        # like the REPOSITORY_PATH_BUILD_OUTPUT_LEAF_NAMES cases below.
        "03_Implement/deploy/public/index.html",
    }
)
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
        # SEC-ADMIN-PLANE-01 / ADR-0072 D1: control-plane bootstrap example in
        # 04_Documentation/security.md. Verified against nginx.conf
        # (location /api/ -> proxy_pass http://api:8000/, which strips /api) and
        # routes/admin.py (APIRouter prefix="/admin/provision" + "/identity-providers").
        "http://localhost:8080/api/admin/provision/identity-providers",
        # OPS-OBSERV-01: readiness probe documented in observability.md and
        # diagnostics.md. Verified against nginx.conf (location /api/ ->
        # proxy_pass http://api:8000/) and main.py's @app.get("/readyz").
        "http://localhost:8080/api/readyz",
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


class _HtmlToMarkdownish(HTMLParser):
    """Translate HTML into the Markdown shapes the contract checks already scan.

    The checks below are written against Markdown syntax (MARKDOWN_LINK_RE,
    BACKTICK_TOKEN_RE, and the fenced/inline code strippers). Rather than
    forking each check for HTML, HTML is normalized into the equivalent
    Markdown text once and fed through the existing checks unchanged:

    - `<a href="X">label</a>` becomes `[label](X)`, so link checking works.
    - `<code>Y</code>` becomes a backticked token, so `_without_code()` can
      strip it for link checking while path checking can still see it.
    - `<h1>`..`<h6>` become `#`-prefixed headings, so `HEADING_RE` works.
    - `<script>` / `<style>` bodies are dropped; they are never documentation.

    Newlines are preserved for every construct that is dropped or rewritten,
    because findings report a line number computed from the scanned text. A
    normalizer that collapsed lines would report positions that do not exist
    in the file the reader opens.

    Known limitation: end tags are assumed not to span lines (`</a>` etc.),
    which holds for generated and hand-written HTML in this repository.
    """

    _DROP_BODY_TAGS = frozenset({"script", "style"})
    _HEADING_TAGS = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._drop_depth = 0
        self._anchor_href: str | None = None
        self._anchor_label: list[str] | None = None
        self._code_depth = 0

    # -- emission helpers ------------------------------------------------
    def _emit(self, text: str) -> None:
        if self._anchor_label is not None:
            self._anchor_label.append(text)
        else:
            self._parts.append(text)

    def _emit_newlines_only(self, raw: str) -> None:
        # Always lands in the top-level buffer: line structure is a property of
        # the file, not of the anchor label being accumulated.
        self._parts.append("\n" * raw.count("\n"))

    def _open_heading(self, level: int) -> None:
        # HEADING_RE anchors on `^#`, so the marker has to reach line start.
        # Indentation already emitted for this line is swapped for it, which
        # keeps the newline count -- and reported line numbers -- unchanged.
        while self._parts:
            tail = self._parts[-1]
            if not tail:
                self._parts.pop()
                continue
            trimmed = tail.rstrip(" \t")
            if trimmed == tail:
                break
            if trimmed:
                self._parts[-1] = trimmed
                break
            self._parts.pop()
        self._parts.append("#" * level + " ")

    # -- HTMLParser hooks ------------------------------------------------
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._emit_newlines_only(self.get_starttag_text() or "")
        if tag in self._DROP_BODY_TAGS:
            self._drop_depth += 1
            return
        if self._drop_depth:
            return
        if tag == "a":
            href = next((value for name, value in attrs if name == "href"), None)
            self._anchor_href = href
            self._anchor_label = []
            return
        if tag == "code":
            self._code_depth += 1
            return
        if tag in self._HEADING_TAGS:
            self._open_heading(self._HEADING_TAGS[tag])

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._emit_newlines_only(self.get_starttag_text() or "")

    def handle_endtag(self, tag: str) -> None:
        if tag in self._DROP_BODY_TAGS:
            self._drop_depth = max(0, self._drop_depth - 1)
            return
        if self._drop_depth:
            return
        if tag == "a" and self._anchor_label is not None:
            label = "".join(self._anchor_label)
            href = self._anchor_href
            self._anchor_label = None
            self._anchor_href = None
            self._parts.append(f"[{label}]({href})" if href is not None else label)
            return
        if tag == "code" and self._code_depth:
            self._code_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._drop_depth:
            self._emit_newlines_only(data)
            return
        self._emit(f"`{data}`" if self._code_depth else data)

    def handle_comment(self, data: str) -> None:
        self._emit_newlines_only(data)

    def result(self) -> str:
        # An unclosed anchor still contributes its label text.
        if self._anchor_label is not None:
            self._parts.append("".join(self._anchor_label))
            self._anchor_label = None
        return "".join(self._parts)


def html_to_markdownish(raw: str) -> str:
    """Return `raw` HTML rewritten into the Markdown shapes the checks scan."""
    parser = _HtmlToMarkdownish()
    parser.feed(raw)
    parser.close()
    return parser.result()


def contract_source_text(root: Path, relative_path: Path) -> str:
    """Return the text a contract check should scan for `relative_path`.

    Markdown is returned as-is; documentation HTML is normalized first. Each
    check keeps applying its own filter on top (for example `_without_code()`).
    """
    raw = (root / relative_path).read_text(encoding="utf-8")
    if relative_path.suffix.lower() in HTML_SUFFIXES:
        return html_to_markdownish(raw)
    return raw


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
        text = _without_code(contract_source_text(repository_root, Path(source_label)))

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


def check_code_span_citations(root: Path, documentation_paths: list[Path]) -> list[DocsCheckFinding]:
    """Return DC-LNK-002 findings for backtick path citations that resolve to nothing.

    `01_Plans/` cites other documents by convention as a code span --
    `` `01_Plans/issues/done/issue-X.md` `` -- in Traceability, Scope, Related
    ADR/Spec and prose, not as a Markdown `[text](path)` link. DC-LNK-001 only
    scans MARKDOWN_LINK_RE, so it never covered the shape that carries almost
    every cross-reference in the planning layer: a citation could name a file
    that had been renamed, moved to `issues/done/`, or converted to HTML
    (AGENTS.md section 3) and nothing failed.

    Scope is the same corpus DC-LNK-001 checks -- tracked Markdown plus
    documentation HTML -- rather than DC-CMD-001's current/public subset,
    because the planning layer is precisely where this citation style is used.
    The two rules do not overlap: DC-LNK-001 reads Markdown link syntax,
    DC-CMD-001 reads any repository path in a public document (directories
    included), and this rule reads code-span citations of files anywhere in the
    documentation corpus.

    A token is treated as a citation only when it starts at a repository root
    (REPOSITORY_PATH_PREFIX_RE), ends in a known documentation or source suffix
    (CITATION_SUFFIXES), and contains no placeholder or glob character
    (REPOSITORY_PATH_FORBIDDEN_CHARS). The suffix requirement is what keeps
    environment-variable names, configuration keys and prose out of the rule.
    A trailing `:N` line reference is stripped before resolution, as in
    DC-CMD-001.

    Fenced code blocks are excluded -- a fence holds an example, not a citation.
    Inline spans are deliberately *not* excluded: `_without_fenced_code` is used
    rather than `_without_code`, since inline code spans are the thing being
    checked. Documentation HTML reaches the same path because
    `contract_source_text` renders `<code>` as a backtick span.
    """
    repository_root = root.resolve()
    findings: list[DocsCheckFinding] = []

    for supplied_path in sorted(documentation_paths, key=lambda path: path.as_posix()):
        relative_path = (
            supplied_path
            if not supplied_path.is_absolute()
            else supplied_path.relative_to(repository_root)
        )
        text = _without_fenced_code(contract_source_text(repository_root, relative_path))

        for match in BACKTICK_TOKEN_RE.finditer(text):
            token = match.group(1)
            if not REPOSITORY_PATH_PREFIX_RE.match(token):
                continue
            if any(character in REPOSITORY_PATH_FORBIDDEN_CHARS for character in token):
                continue
            normalized = TRAILING_LINE_REF_RE.sub("", token)
            if PurePosixPath(normalized).suffix.lower() not in CITATION_SUFFIXES:
                continue
            if normalized in RETIRED_CITATION_TARGETS:
                continue
            if (repository_root / normalized).is_file():
                continue
            findings.append(
                DocsCheckFinding(
                    rule_id=CODE_SPAN_CITATION_RULE_ID,
                    path=relative_path.as_posix(),
                    line=text.count("\n", 0, match.start()) + 1,
                    target=token,
                    message=f"cited path does not exist: {normalized}",
                    fix_hint=(
                        "Cite the file's current path -- an issue that closed now lives under "
                        "01_Plans/issues/done/, an ADR keeps its number but not its slug, and a "
                        "design document converted per AGENTS.md section 3 is .html. If the target "
                        "was deliberately removed and this citation records that, add it to "
                        "RETIRED_CITATION_TARGETS with the reason."
                    ),
                )
            )

    return findings


def check_adr_id_uniqueness(root: Path, markdown_paths: list[Path]) -> list[DocsCheckFinding]:
    """Reject duplicate ADR numbers even when their descriptive slugs differ."""
    repository_root = root.resolve()
    paths_by_id: dict[str, list[Path]] = {}

    for supplied_path in markdown_paths:
        relative_path = supplied_path if not supplied_path.is_absolute() else supplied_path.relative_to(repository_root)
        if relative_path.parent != Path("01_Plans/adr"):
            continue
        match = ADR_FILENAME_RE.match(relative_path.name)
        if match:
            paths_by_id.setdefault(match.group("id"), []).append(relative_path)

    findings: list[DocsCheckFinding] = []
    for adr_id, paths in sorted(paths_by_id.items()):
        ordered_paths = sorted(paths, key=lambda path: path.as_posix())
        if len(ordered_paths) < 2:
            continue
        path_list = ", ".join(path.as_posix() for path in ordered_paths)
        findings.append(
            DocsCheckFinding(
                rule_id=ADR_ID_UNIQUENESS_RULE_ID,
                path=ordered_paths[1].as_posix(),
                line=1,
                target=f"ADR-{adr_id}",
                message=f"ADR-{adr_id} is assigned to multiple files: {path_list}",
                fix_hint="Keep the established ADR number and rename the newer decision to the next unused ADR number, then update its references.",
            )
        )
    return findings


#: Constitution-layer identifiers (DOC-NORM-01). Definitions are headings or
#: top-level list items; anything else mentioning the token is a reference.
NORM_ID_RE = re.compile(r"\b(?:(?:DOM|KJT|AKP|WIR|VC|CQ)-[A-Z]*-?\d{2}|CHK-[BDFXK]\d)\b")
NORM_ID_DEFINITION_RE = re.compile(
    r"^(?:#{2,4}\s+|-\s+\*\*)((?:DOM|KJT|AKP|WIR|VC|CQ)-[A-Z]*-?\d{2})\b", re.M
)
#: The three-element checklist (02_Architecture, HTML). Its items are the gate a
#: design decision must pass, so they are citable the same way norms are. The
#: per-ADR three-element tables are deliberately NOT given identifiers: those are
#: reasoning that produced a decision, and 234+ reasoning cells would reproduce
#: the exists-but-unreferenced failure at scale.
THREE_ELEMENT_CHECKLIST_PATH = Path("02_Architecture/three-element-constraint-checklist.html")
CHECKLIST_ID_DEFINITION_RE = re.compile(r"<td>(CHK-[BDFXK]\d)</td>")

#: A line-number reference into the constitution layer, e.g. a doc path with a
#: trailing colon and digits.
#: These rot the moment the file is edited, which is why identifiers exist.
NORM_LINE_REFERENCE_RE = re.compile(r"00_Prompt/[A-Za-z0-9_.-]+\.md:\d+")

NORM_ID_UNIQUENESS_RULE_ID = "DC-NORM-001"
NORM_ID_RESOLUTION_RULE_ID = "DC-NORM-002"
NORM_LINE_REFERENCE_RULE_ID = "DC-NORM-003"


def _collect_norm_definitions(root: Path) -> dict[str, Path]:
    """Map every constitution-layer identifier to the file that defines it."""
    definitions: dict[str, Path] = {}
    duplicates: list[tuple[str, Path, Path]] = []
    prompt_dir = root / "00_Prompt"
    if not prompt_dir.is_dir():
        return definitions
    for source in sorted(prompt_dir.rglob("*.md")):
        relative = source.relative_to(root)
        try:
            text = source.read_text(encoding="utf-8")
        except OSError:
            continue
        for identifier in NORM_ID_DEFINITION_RE.findall(text):
            if identifier in definitions and definitions[identifier] != relative:
                duplicates.append((identifier, definitions[identifier], relative))
            else:
                definitions.setdefault(identifier, relative)
    checklist = root / THREE_ELEMENT_CHECKLIST_PATH
    if checklist.is_file():
        try:
            checklist_text = checklist.read_text(encoding="utf-8")
        except OSError:
            checklist_text = ""
        for identifier in CHECKLIST_ID_DEFINITION_RE.findall(checklist_text):
            definitions.setdefault(identifier, THREE_ELEMENT_CHECKLIST_PATH)

    _collect_norm_definitions.duplicates = duplicates  # type: ignore[attr-defined]
    return definitions


#: Controlled Status vocabulary for 00_Prompt (DOC-NORM-01).
#: Normative  = states rules that bind
#: Informative = orientation and rationale; binding rules live elsewhere
#: On-demand  = read only when the situation calls for it
#: Superseded = retained for history; do not follow
PROMPT_STATUS_VALUES = ("Normative", "Informative", "On-demand", "Superseded")
PROMPT_STATUS_RE = re.compile(r"^- Status:[ \t]*(?P<value>.+?)[ \t]*$", re.M)
PROMPT_STATUS_RULE_ID = "DC-NORM-004"


def check_prompt_status_vocabulary(root: Path) -> list[DocsCheckFinding]:
    """Every 00_Prompt document declares exactly one controlled Status.

    A parenthetical such as `Normative（ADR-0057 Accepted、…で追跡）` is rejected:
    a status is a controlled value, and a tracking pointer is a different fact.
    Put the pointer in `- Tracked-by:`.
    """
    repository_root = root.resolve()
    prompt_dir = repository_root / "00_Prompt"
    if not prompt_dir.is_dir():
        return []

    findings: list[DocsCheckFinding] = []
    for source in sorted(prompt_dir.glob("*.md")):
        relative = source.relative_to(repository_root)
        try:
            text = source.read_text(encoding="utf-8")
        except OSError:
            continue

        matches = list(PROMPT_STATUS_RE.finditer(text))
        if not matches:
            findings.append(
                DocsCheckFinding(
                    rule_id=PROMPT_STATUS_RULE_ID,
                    path=relative.as_posix(),
                    line=1,
                    target="Status",
                    message="00_Prompt document has no `- Status:` field",
                    fix_hint=(
                        "Add `- Status: " + " | ".join(PROMPT_STATUS_VALUES) + "` below the title."
                    ),
                )
            )
            continue

        if len(matches) > 1:
            second = text[: matches[1].start()].count("\n") + 1
            findings.append(
                DocsCheckFinding(
                    rule_id=PROMPT_STATUS_RULE_ID,
                    path=relative.as_posix(),
                    line=second,
                    target="Status",
                    message="00_Prompt document declares Status more than once",
                    fix_hint="Keep exactly one Status field.",
                )
            )

        value = matches[0].group("value").strip()
        if value not in PROMPT_STATUS_VALUES:
            line_number = text[: matches[0].start()].count("\n") + 1
            findings.append(
                DocsCheckFinding(
                    rule_id=PROMPT_STATUS_RULE_ID,
                    path=relative.as_posix(),
                    line=line_number,
                    target=value,
                    message=(
                        f"Status {value!r} is not one of {'/'.join(PROMPT_STATUS_VALUES)}"
                    ),
                    fix_hint=(
                        "Use a controlled value. Move tracking information (ADR numbers, "
                        "implementing issues) to a separate `- Tracked-by:` line."
                    ),
                )
            )
    return findings

def check_norm_identifier_uniqueness(root: Path) -> list[DocsCheckFinding]:
    """An identifier must name exactly one norm, forever."""
    repository_root = root.resolve()
    _collect_norm_definitions(repository_root)
    duplicates = getattr(_collect_norm_definitions, "duplicates", [])
    findings: list[DocsCheckFinding] = []
    for identifier, first, second in duplicates:
        findings.append(
            DocsCheckFinding(
                rule_id=NORM_ID_UNIQUENESS_RULE_ID,
                path=second.as_posix(),
                line=1,
                target=identifier,
                message=(
                    f"{identifier} is defined in both {first.as_posix()} and {second.as_posix()}"
                ),
                fix_hint=(
                    "Identifiers are append-only and are never reused. Give the newer norm the "
                    "next unused number in its prefix."
                ),
            )
        )
    return findings


def check_norm_identifier_resolution(
    root: Path, markdown_paths: list[Path]
) -> list[DocsCheckFinding]:
    """A reference to a norm must resolve to a norm that exists.

    This is the rule the whole identifier scheme exists for. Without it, plans
    can cite norms that were renamed or never existed, and the constitution
    cannot be changed with any knowledge of what depends on it.
    """
    repository_root = root.resolve()
    definitions = _collect_norm_definitions(repository_root)
    if not definitions:
        return []

    findings: list[DocsCheckFinding] = []
    for supplied_path in sorted(markdown_paths, key=lambda p: p.as_posix()):
        relative = (
            supplied_path
            if not supplied_path.is_absolute()
            else supplied_path.relative_to(repository_root)
        )
        source = repository_root / relative
        try:
            text = source.read_text(encoding="utf-8")
        except OSError:
            continue

        if relative == THREE_ELEMENT_CHECKLIST_PATH:
            continue
        defined_here = set(NORM_ID_DEFINITION_RE.findall(text))
        for line_number, line in enumerate(text.splitlines(), start=1):
            for match in NORM_ID_RE.finditer(line):
                token = match.group(0)
                if token in definitions or token in defined_here:
                    continue
                findings.append(
                    DocsCheckFinding(
                        rule_id=NORM_ID_RESOLUTION_RULE_ID,
                        path=relative.as_posix(),
                        line=line_number,
                        target=token,
                        message=f"{token} does not resolve to any norm defined in 00_Prompt",
                        fix_hint=(
                            "Cite an identifier that exists, or define it in the owning "
                            "00_Prompt document. Do not invent per-document identifiers."
                        ),
                    )
                )
    return findings


def check_norm_line_references(
    root: Path, markdown_paths: list[Path]
) -> list[DocsCheckFinding]:
    """Line-number citations into 00_Prompt rot on the next edit."""
    repository_root = root.resolve()
    findings: list[DocsCheckFinding] = []
    for supplied_path in sorted(markdown_paths, key=lambda p: p.as_posix()):
        relative = (
            supplied_path
            if not supplied_path.is_absolute()
            else supplied_path.relative_to(repository_root)
        )
        source = repository_root / relative
        try:
            text = source.read_text(encoding="utf-8")
        except OSError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for match in NORM_LINE_REFERENCE_RE.finditer(line):
                findings.append(
                    DocsCheckFinding(
                        rule_id=NORM_LINE_REFERENCE_RULE_ID,
                        path=relative.as_posix(),
                        line=line_number,
                        target=match.group(0),
                        message=(
                            f"{match.group(0)} cites 00_Prompt by line number, which breaks on edit"
                        ),
                        fix_hint=(
                            "Cite the norm identifier (e.g. DOM-CORE-02) instead. If the passage "
                            "has no identifier, add one in the owning document."
                        ),
                    )
                )
    return findings


#: `domain.md` §5 declares retired vocabulary in this exact shape, so the rule
#: below reads its terms from the document that owns them rather than hardcoding
#: a list that could drift from the norm it enforces.
RETIRED_TERM_DECLARATION_RE = re.compile(r"^- `([^`]+)` は旧称です", re.M)

#: A block a document explicitly marks as a historical or prohibition note.
#: Guessing intent from wording was tried and failed: the rename record in
#: ADR-0028 D11 and the prohibition statement in architecture.html both name the
#: retired term legitimately, and no keyword heuristic separated them from the
#: contract prose that had to change. An explicit marker states the intent
#: instead of inferring it -- the lesson DX-CANON-INTENT-01 recorded.
RETIRED_VOCAB_EXEMPT_OPEN = "retired-vocabulary: historical"
RETIRED_VOCAB_EXEMPT_CLOSE = "/retired-vocabulary"

#: Inline naming-as-retired, e.g. `Consensus Graph（旧称: Core Graph）`. Wrapping
#: every parenthetical in block markers would be worse than the problem.
RETIRED_INLINE_MARKERS = ("旧称", "旧 ", "legacy", "旧称:")

#: Scope. `02_Architecture` is where contract vocabulary lives, so that is where
#: reintroduction does damage. Deliberately NOT scoped to `01_Plans/issues`:
#: those carry execution records of the rename itself (over 80 occurrences in
#: `issue-CE0-core-graph-repositioning.md` alone) where the old name is correct.
#: The rule therefore protects less than `domain.md` §5 states. That gap is real
#: and is recorded in `issue-DOC-VOCAB-01`.
RETIRED_VOCAB_SCOPE = ("02_Architecture",)
RETIRED_VOCAB_RULE_ID = "DC-VOCAB-001"


def _retired_terms(root: Path) -> list[str]:
    domain = root / "00_Prompt" / "domain.md"
    try:
        text = domain.read_text(encoding="utf-8")
    except OSError:
        return []
    return RETIRED_TERM_DECLARATION_RE.findall(text)


def check_retired_vocabulary(root: Path) -> list[DocsCheckFinding]:
    """A term `domain.md` retired must not reappear as contract vocabulary."""
    repository_root = root.resolve()
    terms = _retired_terms(repository_root)
    if not terms:
        return []

    findings: list[DocsCheckFinding] = []
    for scope in RETIRED_VOCAB_SCOPE:
        base = repository_root / scope
        if not base.is_dir():
            continue
        for source in sorted(base.rglob("*")):
            if source.suffix not in {".md", ".html"} or not source.is_file():
                continue
            try:
                text = source.read_text(encoding="utf-8")
            except OSError:
                continue
            relative = source.relative_to(repository_root).as_posix()
            exempt = False
            for line_number, line in enumerate(text.splitlines(), start=1):
                if RETIRED_VOCAB_EXEMPT_OPEN in line:
                    exempt = True
                    continue
                if RETIRED_VOCAB_EXEMPT_CLOSE in line:
                    exempt = False
                    continue
                if exempt:
                    continue
                for term in terms:
                    if term not in line:
                        continue
                    if any(marker in line for marker in RETIRED_INLINE_MARKERS):
                        continue
                    findings.append(
                        DocsCheckFinding(
                            rule_id=RETIRED_VOCAB_RULE_ID,
                            path=relative,
                            line=line_number,
                            target=term,
                            message=(
                                f"{term!r} is retired vocabulary (00_Prompt/domain.md §5) but is "
                                "used here as contract vocabulary"
                            ),
                            fix_hint=(
                                "Use the canonical term. If this line is a historical note or the "
                                f"prohibition itself, wrap it in <!-- {RETIRED_VOCAB_EXEMPT_OPEN} --> "
                                f"... <!-- {RETIRED_VOCAB_EXEMPT_CLOSE} --> so the intent is stated "
                                "rather than guessed."
                            ),
                        )
                    )
    return findings

def check_current_history_headings(
    root: Path, markdown_paths: tuple[Path, ...] = CURRENT_ONLY_PATHS
) -> list[DocsCheckFinding]:
    """Return DC-CUR-001 findings when execution-history headings enter current docs."""
    findings: list[DocsCheckFinding] = []
    for relative_path in markdown_paths:
        text = _without_code(contract_source_text(root, relative_path))
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
    data_model_path: Path = Path("02_Architecture/data_model_operations_overview.html"),
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

    for label, path in (
        ("api.md", api_path),
        ("data_model_operations_overview.html", data_model_path),
    ):
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


def check_adr_traceability_paths(root: Path, markdown_paths: list[Path]) -> list[DocsCheckFinding]:
    """Reject traceability fields that point to a nonexistent ADR file."""
    repository_root = root.resolve()
    findings: list[DocsCheckFinding] = []

    for supplied_path in markdown_paths:
        relative_path = supplied_path if not supplied_path.is_absolute() else supplied_path.relative_to(repository_root)
        if relative_path.parent != Path("01_Plans/adr") or not ADR_FILENAME_RE.match(relative_path.name):
            continue
        source = repository_root / relative_path
        text = source.read_text(encoding="utf-8")
        for match in ADR_TRACEABILITY_PATH_RE.finditer(text):
            target = match.group("target")
            if (repository_root / target).is_file():
                continue
            findings.append(
                DocsCheckFinding(
                    rule_id=ADR_TRACEABILITY_PATH_RULE_ID,
                    path=relative_path.as_posix(),
                    line=text.count("\n", 0, match.start()) + 1,
                    target=target,
                    message=f"ADR traceability target does not exist: {target}",
                    fix_hint="Remove the false traceability claim or point it to the tracked ADR that records the decision.",
                )
            )

    return findings


def check_ci_job_timeouts(
    root: Path,
    workflow_paths: tuple[Path, ...] = CI_WORKFLOW_PATHS,
) -> list[DocsCheckFinding]:
    """Require bounded timeouts in each maintained workflow that exists.

    A configured path identifies a workflow to inspect when present. It does
    not require GitHub Actions itself to be enabled, so an absent workflow has
    no jobs for this rule to inspect.
    """
    findings: list[DocsCheckFinding] = []
    for relative_path in workflow_paths:
        source = root / relative_path
        if not source.is_file():
            continue
        lines = source.read_text(encoding="utf-8").splitlines()
        jobs_index = lines.index("jobs:")
        job_headers = [
            (index, match.group("job"))
            for index, line in enumerate(lines[jobs_index + 1 :], start=jobs_index + 1)
            if (match := CI_JOB_HEADER_RE.match(line))
        ]
        for position, (start_index, job_name) in enumerate(job_headers):
            end_index = job_headers[position + 1][0] if position + 1 < len(job_headers) else len(lines)
            timeout_match = next(
                (CI_JOB_TIMEOUT_RE.match(line) for line in lines[start_index + 1 : end_index] if CI_JOB_TIMEOUT_RE.match(line)),
                None,
            )
            if timeout_match and 1 <= int(timeout_match.group("minutes")) <= 360:
                continue
            findings.append(
                DocsCheckFinding(
                    rule_id=CI_JOB_TIMEOUT_RULE_ID,
                    path=relative_path.as_posix(),
                    line=start_index + 1,
                    target=job_name,
                    message=f"workflow job `{job_name}` is missing a valid timeout-minutes value",
                    fix_hint="Set timeout-minutes to an integer from 1 through 360 at the job level.",
                )
            )
    return findings


def check_documented_response_models(root: Path) -> list[DocsCheckFinding]:
    """Keep implemented auxiliary response contracts visible in both API docs."""
    findings: list[DocsCheckFinding] = []
    for path, required_terms in DOCUMENTED_RESPONSE_MODEL_REQUIRED_TERMS.items():
        text = (root / path).read_text(encoding="utf-8")
        for term in required_terms:
            if term in text:
                continue
            findings.append(
                DocsCheckFinding(
                    rule_id=API_RESPONSE_MODEL_RULE_ID,
                    path=path.as_posix(),
                    line=1,
                    target=term,
                    message=f"implemented response contract marker is missing: {term}",
                    fix_hint="Restore the endpoint/model contract and its response fields from the backend response_model definition.",
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
        # relpath, not relative_to: the source document need not be an ancestor
        # of its history directory (a doc nested one level deeper than
        # 02_Architecture/history/ would break relative_to's assumption).
        backlink = os.path.relpath(root / relative_path, current_path.parent).replace(os.sep, "/")
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




def _normalize_documented_runtime_default(raw: str) -> object:
    value = raw.strip().strip("`").strip()
    if "（" in value:
        value = value.split("（", 1)[0].strip()
    if value == "未設定":
        return None
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    numeric = value.replace(",", "").replace("_", "")
    if re.fullmatch(r"-?\d+", numeric):
        return int(numeric)
    if re.fullmatch(r"-?\d+\.\d+", numeric):
        return float(numeric)
    return value


def _extract_profile_implementation_defaults(registry_text: str) -> dict[str, tuple[object, int]]:
    marker = "### Profile default vs recommendation"
    if marker not in registry_text:
        return {}
    prefix, remainder = registry_text.split(marker, 1)
    section = remainder.split("\n## ", 1)[0]
    first_line = prefix.count("\n") + 1
    defaults: dict[str, tuple[object, int]] = {}
    for offset, line in enumerate(section.splitlines(), start=1):
        if not line.lstrip().startswith("| `KJ_ATLAS_"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        key = cells[0].strip("`")
        defaults[key] = (_normalize_documented_runtime_default(cells[1]), first_line + offset)
    return defaults


def _extract_settings_literal_defaults(settings_text: str) -> dict[str, object]:
    tree = ast.parse(settings_text)
    settings_class = next(
        (node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Settings"),
        None,
    )
    if settings_class is None:
        return {}
    defaults: dict[str, object] = {}
    for statement in settings_class.body:
        if not isinstance(statement, ast.AnnAssign) or not isinstance(statement.target, ast.Name):
            continue
        value = statement.value
        default_node: ast.AST | None = None
        if isinstance(value, ast.Call):
            func_name = value.func.id if isinstance(value.func, ast.Name) else None
            if func_name != "Field":
                continue
            default_keyword = next((keyword for keyword in value.keywords if keyword.arg == "default"), None)
            if default_keyword is None:
                continue
            default_node = default_keyword.value
        elif value is not None:
            default_node = value
        if default_node is None:
            continue
        try:
            defaults[statement.target.id] = ast.literal_eval(default_node)
        except (ValueError, TypeError):
            # computed/default_factory values are intentionally outside this static gate
            continue
    return defaults


def check_runtime_parameter_default_values(
    root: Path,
    registry_path: Path = RUNTIME_PARAMETER_REGISTRY_PATH,
    settings_path: Path = Path("03_Implement/backend/src/kj_atlas_api/settings.py"),
) -> list[DocsCheckFinding]:
    """Reject static Settings defaults that drift from the registry's implementation-default table."""
    repository_root = root.resolve()
    registry_file = repository_root / registry_path
    settings_file = repository_root / settings_path
    if not registry_file.exists() or not settings_file.exists():
        return []

    documented = _extract_profile_implementation_defaults(registry_file.read_text(encoding="utf-8"))
    implemented = _extract_settings_literal_defaults(settings_file.read_text(encoding="utf-8"))
    findings: list[DocsCheckFinding] = []
    for key, (documented_default, line) in sorted(documented.items()):
        field_name = key.removeprefix("KJ_ATLAS_").lower()
        if field_name not in implemented:
            continue
        implementation_default = implemented[field_name]
        if implementation_default == documented_default:
            continue
        findings.append(
            DocsCheckFinding(
                rule_id=RUNTIME_PARAMETER_DEFAULT_RULE_ID,
                path=registry_path.as_posix(),
                line=line,
                target=key,
                message=(
                    f"documented implementation default {documented_default!r} does not match "
                    f"Settings.{field_name} default {implementation_default!r}"
                ),
                fix_hint="Update the registry Implementation default or the Settings literal default in the same change.",
            )
        )
    return findings

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

    findings.extend(check_runtime_parameter_default_values(root, registry_path=registry_path))
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
    """Return tracked Markdown paths that are present in the working tree."""
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--", "*.md"],
        check=True,
        capture_output=True,
    )
    paths = [Path(raw.decode("utf-8")) for raw in result.stdout.split(b"\0") if raw]
    return [path for path in paths if (root / path).is_file()]


def tracked_documentation_html_paths(root: Path) -> list[Path]:
    """Return tracked HTML paths under the documentation roots.

    HTML design views live beside their Markdown source (see AGENTS.md section 3
    "文書の形式"). They are scanned so that a document does not escape link
    validation by being written as HTML. Application and build HTML is excluded
    on purpose -- see DOCUMENTATION_HTML_ROOTS.
    """
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--", "*.html", "*.htm"],
        check=True,
        capture_output=True,
    )
    paths = [Path(raw.decode("utf-8")) for raw in result.stdout.split(b"\0") if raw]
    return [
        path
        for path in paths
        if (root / path).is_file()
        and any(path == doc_root or doc_root in path.parents for doc_root in DOCUMENTATION_HTML_ROOTS)
    ]


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
    link_paths = markdown_paths + tracked_documentation_html_paths(root)
    findings = check_relative_links(root, link_paths)
    findings.extend(check_code_span_citations(root, link_paths))
    findings.extend(check_adr_id_uniqueness(root, markdown_paths))
    findings.extend(check_adr_traceability_paths(root, markdown_paths))
    findings.extend(check_ci_job_timeouts(root))
    findings.extend(check_current_history_headings(root))
    findings.extend(check_document_contract_baseline(root))
    findings.extend(check_documented_response_models(root))
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
