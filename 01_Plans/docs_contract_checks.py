#!/usr/bin/env python3
"""Deterministic documentation-contract checks used by the docs-check entrypoint."""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit

RELATIVE_LINK_RULE_ID = "DC-LNK-001"
CURRENT_ONLY_RULE_ID = "DC-CUR-001"
HISTORY_RULE_ID = "DC-HIS-001"
ROUTE_RULE_ID = "DC-RTE-001"
PUBLIC_RULE_ID = "DC-PUB-001"
FORMAT_RULE_ID = "DC-FMT-001"
SAFETY_RULE_ID = "DC-SAF-001"
FENCE_RE = re.compile(r"^[ \t]{0,3}(?P<fence>`{3,}|~{3,})")
INLINE_CODE_RE = re.compile(r"(?P<ticks>`+)[^\r\n]*?(?P=ticks)")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]\r\n]*\]\((?P<target><[^>\r\n]+>|[^)\r\n]+)\)")
MARKDOWN_HEADING_RE = re.compile(r"^(?P<hashes>#{1,6})[ \t]+(?P<title>.+?)\s*$", re.MULTILINE)
HISTORY_HEADING_RE = re.compile(
    r"(?i)(?:\bstream\b|\bfreeze\b|\bfrozen\b|\brerun\b|\bre-run\b|"
    r"\bexecution[ -]log\b|\bcheckpoint\b|\breaffirmation\b|"
    r"実行ログ|再実行|凍結|チェックポイント|過去件数|解消済み(?:queue|キュー))"
)
HISTORY_METADATA_PATTERNS = {
    "Status": re.compile(r"^Status:[ \t]*(?P<value>.+?)\s*$", re.MULTILINE),
    "Source document": re.compile(r"^Source document:[ \t]*(?P<value>.+?)\s*$", re.MULTILINE),
    "Source anchors": re.compile(r"^Source anchors:[ \t]*(?P<value>.+?)\s*$", re.MULTILINE),
    "Covered period": re.compile(r"^Covered period:[ \t]*(?P<value>.+?)\s*$", re.MULTILINE),
    "Snapshot / source revision": re.compile(
        r"^Snapshot / source revision:[ \t]*(?P<value>.+?)\s*$", re.MULTILINE
    ),
    "Retention reason": re.compile(r"^Retention reason:[ \t]*(?P<value>.+?)\s*$", re.MULTILINE),
    "Current normative anchors": re.compile(
        r"^Current normative anchors:[ \t]*(?P<value>.*?)\s*$", re.MULTILINE
    ),
}
PUBLIC_CATALOG_FORBIDDEN_RE = re.compile(
    r"00_Prompt|01_Plans|ADR-[0-9]{4}|issue-[A-Za-z0-9]|UX-NAV|UX-COMPLEXITY|Claude Design"
)
PUBLIC_CATALOG_REQUIRED = (
    "対象読者:",
    "確認対象revision",
    "最終確認日",
    "表示条件",
    "画像検証",
    "公開状態",
    "SafeMode",
)
SCREENSHOT_LEDGER_REQUIRED = (
    "Capture ID:",
    "Source revision:",
    "Captured at:",
    "Fixture:",
    "Locale / viewport / provider / SafeMode:",
    "Script / command:",
    "Result:",
    "Manual review:",
    "Stale triggers checked:",
)
SAFETY_INVARIANT_PATTERNS = (
    (
        "SafeMode default ON",
        (
            re.compile(r"SafeModeは既定ON", re.IGNORECASE),
            re.compile(r"SafeMode[ \t]*の既定ON", re.IGNORECASE),
        ),
    ),
    (
        "AI output remains proposal-only",
        (
            re.compile(r"AI出力はproposal-onlyで、自動適用しない", re.IGNORECASE),
            re.compile(r"02_Architecture/schemas\.md"),
        ),
    ),
    (
        "human_reviewed is human-only",
        (
            re.compile(r"`?human_reviewed`?[ \t]*は人間だけが設定する", re.IGNORECASE),
            re.compile(r"02_Architecture/schemas\.md"),
        ),
    ),
    (
        "provider=none retains core value",
        (
            re.compile(
                r"`?KJ_ATLAS_LLM_PROVIDER=none`?[ \t]*でも主要価値が成立する",
                re.IGNORECASE,
            ),
            re.compile(r"KJ_ATLAS_LLM_PROVIDER=none", re.IGNORECASE),
        ),
    ),
    (
        "share/export prevents unintended disclosure",
        (
            re.compile(
                r"share/exportで未レビュー情報や秘密情報を意図せず共有しない",
                re.IGNORECASE,
            ),
            re.compile(r"漏洩防止（share/export）", re.IGNORECASE),
        ),
    ),
)


def tracked_markdown_paths(root: Path) -> list[Path]:
    """Return relative paths of git-tracked markdown files under *root*."""
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--", "*.md"],
        capture_output=True, text=True, check=True,
    )
    return [
        Path(p) for p in result.stdout.split("\0") if p
    ]


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


@dataclass(frozen=True)
class RequiredRoute:
    source: Path
    target: Path
    reference: str
    markdown_link: bool


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


def check_current_only_headings(root: Path, markdown_paths: list[Path]) -> list[DocsCheckFinding]:
    """Return DC-CUR-001 findings for execution-history headings in current-only docs."""
    repository_root = root.resolve()
    findings: list[DocsCheckFinding] = []

    for supplied_path in sorted(markdown_paths, key=lambda path: path.as_posix()):
        source = supplied_path if supplied_path.is_absolute() else repository_root / supplied_path
        source = source.resolve()
        source_label = source.relative_to(repository_root).as_posix()
        text = _without_fenced_code(source.read_text(encoding="utf-8"))

        for match in MARKDOWN_HEADING_RE.finditer(text):
            title = INLINE_CODE_RE.sub("", match.group("title")).strip().rstrip("#").strip()
            if not HISTORY_HEADING_RE.search(title):
                continue
            line = text.count("\n", 0, match.start()) + 1
            findings.append(
                DocsCheckFinding(
                    rule_id=CURRENT_ONLY_RULE_ID,
                    path=source_label,
                    line=line,
                    target=title,
                    message=f"execution-history heading appears in a current-only document: {title}",
                    fix_hint="Move the execution record to the appropriate history document and keep only the current contract or procedure here.",
                )
            )

    return findings


def _markdown_destinations(text: str) -> list[str]:
    return [
        destination
        for match in MARKDOWN_LINK_RE.finditer(_without_code(text))
        if (destination := _link_destination(match.group("target")))
        and not _is_external_or_anchor(destination)
    ]


def _resolved_repository_target(repository_root: Path, source: Path, destination: str) -> Path | None:
    parsed = urlsplit(destination)
    relative_target = unquote(parsed.path)
    if not relative_target:
        return None
    target = (
        repository_root / relative_target.lstrip("/")
        if relative_target.startswith("/")
        else source.parent / relative_target
    ).resolve()
    try:
        target.relative_to(repository_root)
    except ValueError:
        return None
    return target


def check_history_documents(
    root: Path,
    history_paths: list[Path],
    history_index_path: Path,
) -> list[DocsCheckFinding]:
    """Return DC-HIS-001 findings for history metadata and bidirectional routing."""
    repository_root = root.resolve()
    findings: list[DocsCheckFinding] = []
    index = history_index_path if history_index_path.is_absolute() else repository_root / history_index_path
    index = index.resolve()

    if not index.exists():
        return [
            DocsCheckFinding(
                rule_id=HISTORY_RULE_ID,
                path=index.relative_to(repository_root).as_posix(),
                line=1,
                target="history index",
                message="history index does not exist",
                fix_hint="Restore the history README and list every retained history document.",
            )
        ]

    index_targets = {
        target
        for destination in _markdown_destinations(index.read_text(encoding="utf-8"))
        if (target := _resolved_repository_target(repository_root, index, destination)) is not None
    }

    for supplied_path in sorted(history_paths, key=lambda path: path.as_posix()):
        source = supplied_path if supplied_path.is_absolute() else repository_root / supplied_path
        source = source.resolve()
        source_label = source.relative_to(repository_root).as_posix()
        text = source.read_text(encoding="utf-8")
        metadata: dict[str, re.Match[str]] = {}

        for field, pattern in HISTORY_METADATA_PATTERNS.items():
            match = pattern.search(text)
            if match and (field == "Current normative anchors" or match.group("value").strip()):
                metadata[field] = match
                continue
            findings.append(
                DocsCheckFinding(
                    rule_id=HISTORY_RULE_ID,
                    path=source_label,
                    line=1,
                    target=field,
                    message=f"required history metadata is missing or empty: {field}",
                    fix_hint=f"Add a non-empty '{field}:' field using the history README contract.",
                )
            )

        status = metadata.get("Status")
        if status and status.group("value").strip() != "Informative history":
            line = text.count("\n", 0, status.start()) + 1
            findings.append(
                DocsCheckFinding(
                    rule_id=HISTORY_RULE_ID,
                    path=source_label,
                    line=line,
                    target=status.group("value").strip(),
                    message="history Status must be exactly 'Informative history'",
                    fix_hint="Use the canonical non-normative history status.",
                )
            )

        source_document: Path | None = None
        source_meta = metadata.get("Source document")
        if source_meta:
            source_destinations = _markdown_destinations(source_meta.group("value"))
            if source_destinations:
                source_document = _resolved_repository_target(
                    repository_root, source, source_destinations[0]
                )
            if source_document is None or not source_document.exists() or "history" in source_document.parts:
                line = text.count("\n", 0, source_meta.start()) + 1
                findings.append(
                    DocsCheckFinding(
                        rule_id=HISTORY_RULE_ID,
                        path=source_label,
                        line=line,
                        target=source_meta.group("value").strip(),
                        message="Source document must link to an existing current document",
                        fix_hint="Link Source document to the current normative source outside history/.",
                    )
                )
                source_document = None

        anchors_meta = metadata.get("Current normative anchors")
        if anchors_meta:
            anchors_end = len(text)
            next_heading = re.search(r"^#{1,6}[ \t]+", text[anchors_meta.end() :], re.MULTILINE)
            if next_heading:
                anchors_end = anchors_meta.end() + next_heading.start()
            anchor_block = text[anchors_meta.end() : anchors_end]
            anchor_targets = [
                target
                for destination in _markdown_destinations(anchor_block)
                if (target := _resolved_repository_target(repository_root, source, destination)) is not None
                and target.exists()
                and "history" not in target.parts
            ]
            if not anchor_targets:
                line = text.count("\n", 0, anchors_meta.start()) + 1
                findings.append(
                    DocsCheckFinding(
                        rule_id=HISTORY_RULE_ID,
                        path=source_label,
                        line=line,
                        target="Current normative anchors",
                        message="Current normative anchors must contain a link to an existing current document",
                        fix_hint="Add at least one current normative Markdown link before the first history heading.",
                    )
                )

        if source_document is not None:
            reverse_targets = {
                target
                for destination in _markdown_destinations(source_document.read_text(encoding="utf-8"))
                if (target := _resolved_repository_target(repository_root, source_document, destination))
                is not None
            }
            if source not in reverse_targets:
                findings.append(
                    DocsCheckFinding(
                        rule_id=HISTORY_RULE_ID,
                        path=source_document.relative_to(repository_root).as_posix(),
                        line=1,
                        target=source_label,
                        message="current source document does not link back to its retained history",
                        fix_hint=f"Add an informative link from the current source to {source_label}.",
                    )
                )

        if source not in index_targets:
            findings.append(
                DocsCheckFinding(
                    rule_id=HISTORY_RULE_ID,
                    path=index.relative_to(repository_root).as_posix(),
                    line=1,
                    target=source_label,
                    message="history document is missing from the history index",
                    fix_hint=f"Add {source.name} to the retained-history table.",
                )
            )

    return findings


def check_required_routes(root: Path, requirements: list[RequiredRoute]) -> list[DocsCheckFinding]:
    """Return DC-RTE-001 findings for missing contributor and public-document routes."""
    repository_root = root.resolve()
    findings: list[DocsCheckFinding] = []

    for requirement in sorted(
        requirements,
        key=lambda item: (item.source.as_posix(), item.target.as_posix(), item.reference),
    ):
        source = (repository_root / requirement.source).resolve()
        target = (repository_root / requirement.target).resolve()
        source_label = requirement.source.as_posix()
        target_label = requirement.target.as_posix()

        if not source.exists():
            findings.append(
                DocsCheckFinding(
                    rule_id=ROUTE_RULE_ID,
                    path=source_label,
                    line=1,
                    target=target_label,
                    message="route source document does not exist",
                    fix_hint=f"Restore {source_label} and route readers to {target_label}.",
                )
            )
            continue

        text = source.read_text(encoding="utf-8")
        if requirement.markdown_link:
            linked_targets = {
                resolved
                for destination in _markdown_destinations(text)
                if (resolved := _resolved_repository_target(repository_root, source, destination))
                is not None
            }
            route_exists = target in linked_targets
        else:
            route_exists = requirement.reference in text

        if route_exists and target.exists():
            continue

        line = text.count("\n", 0, text.find(requirement.reference)) + 1 if requirement.reference in text else 1
        detail = (
            "route target does not exist"
            if route_exists and not target.exists()
            else "required repository route is missing"
        )
        route_kind = "Markdown link" if requirement.markdown_link else "command/path reference"
        findings.append(
            DocsCheckFinding(
                rule_id=ROUTE_RULE_ID,
                path=source_label,
                line=line,
                target=target_label,
                message=f"{detail}: {target_label}",
                fix_hint=f"Add a {route_kind} from {source_label} using '{requirement.reference}'.",
            )
        )

    return findings


def check_public_ui_catalog(
    root: Path,
    catalog_path: Path,
    screenshot_ledger_path: Path,
) -> list[DocsCheckFinding]:
    """Return DC-PUB-001 findings for UI catalog boundaries and screenshot provenance."""
    repository_root = root.resolve()
    catalog = catalog_path if catalog_path.is_absolute() else repository_root / catalog_path
    ledger = (
        screenshot_ledger_path
        if screenshot_ledger_path.is_absolute()
        else repository_root / screenshot_ledger_path
    )
    catalog = catalog.resolve()
    ledger = ledger.resolve()
    findings: list[DocsCheckFinding] = []

    for document, required_labels, purpose in (
        (catalog, PUBLIC_CATALOG_REQUIRED, "public UI catalog"),
        (ledger, SCREENSHOT_LEDGER_REQUIRED, "screenshot provenance ledger"),
    ):
        label = document.relative_to(repository_root).as_posix()
        if not document.exists():
            findings.append(
                DocsCheckFinding(
                    rule_id=PUBLIC_RULE_ID,
                    path=label,
                    line=1,
                    target=purpose,
                    message=f"required {purpose} does not exist",
                    fix_hint=f"Restore {label} before publishing UI documentation.",
                )
            )
            continue
        text = document.read_text(encoding="utf-8")
        for required_label in required_labels:
            if required_label in text:
                continue
            findings.append(
                DocsCheckFinding(
                    rule_id=PUBLIC_RULE_ID,
                    path=label,
                    line=1,
                    target=required_label,
                    message=f"required {purpose} evidence is missing: {required_label}",
                    fix_hint=f"Add and populate the '{required_label}' field in {label}.",
                )
            )

    if catalog.exists():
        catalog_text = _without_fenced_code(catalog.read_text(encoding="utf-8"))
        for match in PUBLIC_CATALOG_FORBIDDEN_RE.finditer(catalog_text):
            line = catalog_text.count("\n", 0, match.start()) + 1
            findings.append(
                DocsCheckFinding(
                    rule_id=PUBLIC_RULE_ID,
                    path=catalog.relative_to(repository_root).as_posix(),
                    line=line,
                    target=match.group(0),
                    message=f"internal planning reference appears in the public UI catalog: {match.group(0)}",
                    fix_hint="Move internal issue/ADR/design handoff detail to 02_Architecture/design and keep only verified user-facing facts here.",
                )
            )

    return findings


def check_conflict_markers(root: Path, markdown_paths: list[Path]) -> list[DocsCheckFinding]:
    """Return DC-FMT-001 findings for unresolved Git conflict boundaries."""
    repository_root = root.resolve()
    findings: list[DocsCheckFinding] = []
    marker_re = re.compile(r"^(?P<marker><{7,}|>{7,})(?:[ \t].*)?$", re.MULTILINE)

    for supplied_path in sorted(markdown_paths, key=lambda path: path.as_posix()):
        source = supplied_path if supplied_path.is_absolute() else repository_root / supplied_path
        source = source.resolve()
        source_label = source.relative_to(repository_root).as_posix()
        text = _without_fenced_code(source.read_text(encoding="utf-8"))
        for match in marker_re.finditer(text):
            marker = match.group("marker")
            line = text.count("\n", 0, match.start()) + 1
            findings.append(
                DocsCheckFinding(
                    rule_id=FORMAT_RULE_ID,
                    path=source_label,
                    line=line,
                    target=marker,
                    message="unresolved Git conflict marker appears in Markdown",
                    fix_hint="Resolve the conflict, remove all conflict boundaries, and rerun git diff --check.",
                )
            )

    return findings


def check_safety_invariant_route(root: Path, entry_path: Path) -> list[DocsCheckFinding]:
    """Return DC-SAF-001 findings when the AI entry loses a safety invariant route."""
    repository_root = root.resolve()
    entry = entry_path if entry_path.is_absolute() else repository_root / entry_path
    entry = entry.resolve()
    entry_label = entry.relative_to(repository_root).as_posix()

    if not entry.exists():
        return [
            DocsCheckFinding(
                rule_id=SAFETY_RULE_ID,
                path=entry_label,
                line=1,
                target="safety invariant entry",
                message="AI safety entry document does not exist",
                fix_hint="Restore AGENTS.md with the five non-regression safety invariants.",
            )
        ]

    text = entry.read_text(encoding="utf-8")
    findings: list[DocsCheckFinding] = []
    for label, patterns in SAFETY_INVARIANT_PATTERNS:
        if any(pattern.search(text) for pattern in patterns):
            continue
        findings.append(
            DocsCheckFinding(
                rule_id=SAFETY_RULE_ID,
                path=entry_label,
                line=1,
                target=label,
                message=f"safety invariant is no longer reachable from the AI entry: {label}",
                fix_hint="Restore the explicit non-regression invariant in the AGENTS.md safety section.",
            )
        )
    return findings
