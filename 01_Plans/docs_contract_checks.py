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

    if findings:
        print("documentation contract validation failed:")
        for finding in findings:
            print(f"- {finding.render()}")
        return 1

    print(f"ok: checked {len(markdown_paths)} tracked Markdown files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
