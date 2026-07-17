#!/usr/bin/env python3
"""Deterministic documentation-contract checks used by the docs-check entrypoint."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
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

    if findings:
        print("documentation contract validation failed:")
        for finding in findings:
            print(f"- {finding.render()}")
        return 1

    print(f"ok: checked {len(markdown_paths)} tracked Markdown files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
