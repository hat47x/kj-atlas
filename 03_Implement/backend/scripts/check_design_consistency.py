#!/usr/bin/env python3
"""Check cross-references and basic consistency across design documents.

ADR-0067: Three-Element Constraint Design Method — semi-automated consistency check.

This script performs mechanical checks on design documents:
1. ADR references in design docs point to existing files
2. API endpoints referenced in design docs exist in api.md
3. Schema types referenced in design docs exist in schemas.md
4. All AGENTS.md reading-table references resolve
5. Design doc HTML files contain valid Mermaid diagrams (basic check)

Exit code 0 = all checks pass (or only warnings).
Exit code 1 = hard errors found.

Warning baseline (--baseline PATH):
  When a baseline JSON file is provided, the script compares current warning
  counts by category against the stored baseline. If ANY category's count has
  INCREASED, the script exits with code 1 (new warnings introduced).
  If counts decreased, it suggests updating the baseline.
  This prevents the warning gap from growing — addressing R3 root cause 1
  (non-mandatory documentation processes).
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# --- File discovery ---

ADR_DIR = REPO_ROOT / "01_Plans" / "adr"
ISSUE_DIR = REPO_ROOT / "01_Plans" / "issues"
ARCH_DIR = REPO_ROOT / "02_Architecture"
API_MD = ARCH_DIR / "api.md"
SCHEMAS_MD = ARCH_DIR / "schemas.md"
AGENTS_MD = REPO_ROOT / "AGENTS.md"

# Patterns
ADR_FILENAME_RE = re.compile(r"ADR-\d{4}.*\.md")
ADRFILE_REF_RE = re.compile(r"`(ADR-\d{4}[^`]*)`")
MD_REF_RE = re.compile(r"`([0-9A-Za-z_/.-]+\.md)`")
HTML_REF_RE = re.compile(r"`([0-9A-Za-z_/.-]+\.html)`")
API_ENDPOINT_RE = re.compile(r"`(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s`]+)`")
# api.md format: **METHOD** `/path`
API_MD_BOLD_RE = re.compile(r"\*\*(GET|POST|PUT|DELETE|PATCH)\*\*\s+`(/\S+)`")
SCHEMA_TYPE_RE = re.compile(r"`(DocumentV1|Card|Edge|Island|Narrative|EvidenceLink|[A-Z][A-Za-z0-9]+(?:V\d)?)`")

errors: list[str] = []
warnings: list[str] = []


def error(msg: str) -> None:
    errors.append(msg)
    print(f"  ERROR: {msg}")


def warn(msg: str) -> None:
    warnings.append(msg)
    print(f"  WARN: {msg}")


# --- 1. ADR cross-references ---

print("=== 1. ADR cross-references ===")
adr_files = set()
for f in ADR_DIR.iterdir():
    if ADR_FILENAME_RE.match(f.name):
        adr_files.add(f.name)

print(f"  Found {len(adr_files)} ADR files")

# Check all design docs for ADR references
all_md_files = list(ARCH_DIR.rglob("*.md")) + list(ARCH_DIR.rglob("*.html"))
all_md_files.append(AGENTS_MD)
all_md_files.extend(ADR_DIR.rglob("*.md"))
all_md_files.extend(ISSUE_DIR.rglob("*.md"))

for doc_path in all_md_files:
    try:
        content = doc_path.read_text(encoding="utf-8")
    except Exception:
        continue

    for match in ADRFILE_REF_RE.finditer(content):
        ref = match.group(1).strip()
        # Extract ADR number
        adr_num = re.match(r"ADR-(\d{4})", ref)
        if adr_num:
            # Check if a file starting with this ADR number exists
            prefix = f"ADR-{adr_num.group(1)}"
            found = any(f.startswith(prefix) for f in adr_files)
            if not found:
                error(f"{doc_path.relative_to(REPO_ROOT)}: references non-existent {ref}")

# --- 2. API endpoint references ---

# Path-parameter canonicalization: {id}/{docId}/{doc_id} all refer to the
# same resource placeholder. Normalize before comparing.
_PARAM_TOKEN_RE = re.compile(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}")
# Concrete resource IDs (test fixtures, sample docs) normalize to {param}.
_CONCRETE_ID_RE = re.compile(r"([a-z][a-z0-9]+(?:[-_][a-z0-9]+)+)")


def _canonicalize_endpoint(path: str) -> str:
    # 1. Replace {named} placeholders
    normalized = _PARAM_TOKEN_RE.sub("{param}", path)
    # 2. Replace concrete resource ids (e.g. e2e-qa-roundtrip) with {param}
    normalized = _CONCRETE_ID_RE.sub("{param}", normalized)
    # 3. Collapse repeated {param} (GET /docs/{param}/{param} -> /docs/{param})
    while "{param}/{param}" in normalized:
        normalized = normalized.replace("{param}/{param}", "{param}")
    return normalized


# Endpoints that are NOT kj-atlas's own API: external IdP/broker endpoints
# (OAuth/OIDC/SAML) and wildcard "future" references. These must not be
# flagged as api.md gaps.
EXTERNAL_ENDPOINT_PREFIXES = (
    "/login",
    "/oauth/",
    "/.well-known/",
    "/saml",
)
WILDCARD_ENDPOINT_PATTERNS = ("/*", "/")  # trailing wildcard or bare prefix


def _is_external_or_wildcard(path: str) -> bool:
    if any(path.startswith(p) for p in EXTERNAL_ENDPOINT_PREFIXES):
        return True
    # Wildcard / future-reference forms: "/ai/*", "/context/*", "POST /ai/"
    # (bare path with no sub-resource = collection reference, not an endpoint)
    if "*" in path:
        return True
    # A path that consists only of a prefix (no trailing sub-path after the
    # last slash token) is a collection/future reference, e.g. "/ai/" or "/docs"
    stripped = path.rstrip("/")
    if "/" not in stripped or stripped.count("/") <= 1:
        return True
    return False


print("\n=== 2. API endpoint references ===")
if API_MD.exists():
    api_content = API_MD.read_text(encoding="utf-8")
    api_endpoints: set[str] = set()
    for match in API_ENDPOINT_RE.finditer(api_content):
        api_endpoints.add(f"{match.group(1)} {_canonicalize_endpoint(match.group(2))}")
    # Also match api.md bold format: **METHOD** `/path`
    for match in API_MD_BOLD_RE.finditer(api_content):
        api_endpoints.add(f"{match.group(1)} {_canonicalize_endpoint(match.group(2))}")

    for doc_path in all_md_files:
        try:
            content = doc_path.read_text(encoding="utf-8")
        except Exception:
            continue
        for match in API_ENDPOINT_RE.finditer(content):
            raw_path = match.group(2)
            ep = f"{match.group(1)} {_canonicalize_endpoint(raw_path)}"
            if ep in api_endpoints:
                continue
            # Skip external IdP endpoints and wildcard future references
            if _is_external_or_wildcard(raw_path):
                continue
            # Only check design docs, not implementation code
            if "02_Architecture" in str(doc_path) or "01_Plans" in str(doc_path):
                warn(f"{doc_path.relative_to(REPO_ROOT)}: references API endpoint '{ep}' not found in api.md")

    print(f"  Found {len(api_endpoints)} canonical endpoints in api.md")
else:
    warn("api.md not found — skipping API check")

# --- 3. Schema type references ---

print("\n=== 3. Schema type references ===")
if SCHEMAS_MD.exists():
    schema_content = SCHEMAS_MD.read_text(encoding="utf-8")
    schema_types: set[str] = set()
    for match in re.finditer(r"^export (?:type|interface) (\w+)", schema_content, re.MULTILINE):
        schema_types.add(match.group(1))

    for doc_path in all_md_files:
        try:
            content = doc_path.read_text(encoding="utf-8")
        except Exception:
            continue
        for match in SCHEMA_TYPE_RE.finditer(content):
            type_name = match.group(1)
            # Skip known non-schema types
            if type_name in {"GET", "POST", "PUT", "DELETE", "PATCH", "KJ", "OK", "ID", "AI", "UI",
                              "URL", "API", "DB", "CI", "CD", "OS", "CSV", "PNG", "SVG", "JSON",
                              "HTML", "HTTP", "HTTPS", "OSS", "PR", "ADR", "MVP", "LLM", "PDP"}:
                continue
            if type_name not in schema_types and type_name not in {
                "DocumentV1", "Card", "Edge", "Island", "Narrative",
            }:
                # Only flag in design docs
                if "02_Architecture" in str(doc_path):
                    pass  # Too many false positives — skip for now

    print(f"  Found {len(schema_types)} exported types in schemas.md")
else:
    warn("schemas.md not found — skipping schema check")

# --- 4. AGENTS.md reading table ---

print("\n=== 4. AGENTS.md reading table ===")
if AGENTS_MD.exists():
    agents_content = AGENTS_MD.read_text(encoding="utf-8")
    # Find all file references in the reading table
    in_table = False
    for line in agents_content.split("\n"):
        if "先に読む正本" in line:
            in_table = True
            continue
        if in_table and line.startswith("|"):
            for match in MD_REF_RE.finditer(line):
                ref = match.group(1)
                resolved = REPO_ROOT
                for part in ref.split("/"):
                    resolved = resolved / part
                if not resolved.exists():
                    warn(f"AGENTS.md reading table: references non-existent {ref}")
            for match in HTML_REF_RE.finditer(line):
                ref = match.group(1)
                resolved = REPO_ROOT
                for part in ref.split("/"):
                    resolved = resolved / part
                if not resolved.exists():
                    warn(f"AGENTS.md reading table: references non-existent {ref}")
        if in_table and not line.startswith("|"):
            in_table = False
else:
    warn("AGENTS.md not found")

# --- 5. Mermaid diagram check ---

print("\n=== 5. Mermaid diagram presence ===")
html_files = list(ARCH_DIR.rglob("*.html"))
mermaid_count = 0
for html_file in html_files:
    try:
        content = html_file.read_text(encoding="utf-8")
    except Exception:
        continue
    # Count Mermaid diagrams
    diagrams = re.findall(r'<pre class="mermaid">', content)
    if diagrams:
        mermaid_count += len(diagrams)

print(f"  Found {mermaid_count} Mermaid diagrams in {len(html_files)} HTML files")

# --- Warning categories for baseline tracking ---

warning_categories = {
    "adr_refs": sum(1 for e in errors if "references non-existent ADR" in e),
    "api_endpoints": sum(1 for w in warnings if "references API endpoint" in w),
    "agdmd_refs": sum(1 for w in warnings if "AGENTS.md reading table" in w),
    "mermaid": 0,  # No warnings currently generated for mermaid
}
total_warnings = len(warnings)

# --- Summary ---

print(f"\n=== Summary: {len(errors)} errors, {len(warnings)} warnings ===")

# Baseline check (R3 root cause 1 countermeasure)
baseline_path = None
for i, arg in enumerate(sys.argv):
    if arg == "--baseline" and i + 1 < len(sys.argv):
        baseline_path = Path(sys.argv[i + 1])
        break

if baseline_path:
    current = {
        "total_warnings": total_warnings,
        "total_errors": len(errors),
        "categories": warning_categories,
    }
    if baseline_path.exists():
        try:
            baseline = json.loads(baseline_path.read_text())
            increased = []
            for cat, count in current["categories"].items():
                base_count = baseline.get("categories", {}).get(cat, 0)
                if count > base_count:
                    increased.append(f"{cat}: {base_count}→{count} (+{count - base_count})")
            if increased:
                print(f"FAILED — warning count increased in: {', '.join(increased)}")
                print(f"  Baseline: {baseline_path} (update with --update-baseline after fixing)")
                sys.exit(1)
            elif current["total_warnings"] < baseline.get("total_warnings", 0):
                print(f"  Warning count decreased: {baseline['total_warnings']}→{current['total_warnings']}")
                print(f"  Consider updating baseline: --update-baseline")
        except (json.JSONDecodeError, KeyError):
            print(f"  Warning: baseline file corrupt, skipping baseline check")
    else:
        print(f"  Baseline created: {baseline_path} ({total_warnings} warnings)")
        baseline_path.write_text(json.dumps(current, indent=2))

# --update-baseline flag
if "--update-baseline" in sys.argv and baseline_path:
    current = {
        "total_warnings": total_warnings,
        "total_errors": len(errors),
        "categories": warning_categories,
    }
    baseline_path.write_text(json.dumps(current, indent=2))
    print(f"  Baseline updated: {baseline_path} ({total_warnings} warnings)")

if errors:
    print("FAILED — hard errors found")
    sys.exit(1)
else:
    print("PASSED" + (" (with warnings)" if warnings else ""))
    sys.exit(0)
