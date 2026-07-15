#!/usr/bin/env python3
"""Deterministic documentation-contract checks used by the docs-check entrypoint."""
from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit

RELATIVE_LINK_RULE_ID = "DC-LNK-001"
CURRENT_HISTORY_RULE_ID = "DC-CUR-001"
HISTORY_METADATA_RULE_ID = "DC-HIS-001"
ARCHITECTURE_BASELINE_RULE_ID = "DC-ARC-001"
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

    if findings:
        print("documentation contract validation failed:")
        for finding in findings:
            print(f"- {finding.render()}")
        return 1

    print(f"ok: checked {len(markdown_paths)} tracked Markdown files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
