from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEWLINES: dict[str, str] = {}


def read(path: str) -> str:
    with (ROOT / path).open("r", encoding="utf-8", newline="") as handle:
        raw = handle.read()
    if "\r\n" in raw:
        newline = "\r\n"
    else:
        newline = "\n"
    NEWLINES[path] = newline
    return raw.replace("\r\n", "\n")


def write(path: str, text: str) -> None:
    newline = NEWLINES.get(path, "\n")
    normalized = text.replace("\r\n", "\n")
    rendered = normalized if newline == "\n" else normalized.replace("\n", "\r\n")
    with (ROOT / path).open("w", encoding="utf-8", newline="") as handle:
        handle.write(rendered)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def match_brace(text: str, start: int) -> int:
    if text[start] != "{":
        raise ValueError("start is not an opening brace")
    depth = 0
    quote: str | None = None
    escaped = False
    i = start
    while i < len(text):
        ch = text[i]
        if quote is not None:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            i += 1
            continue
        if ch in {'"', "'", "`"}:
            quote = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError("unclosed brace")


def second_argument_object_start(text: str, call_start: int) -> int | None:
    open_paren = text.index("(", call_start)
    paren = 1
    brace = 0
    bracket = 0
    quote: str | None = None
    escaped = False
    i = open_paren + 1
    while i < len(text):
        ch = text[i]
        if quote is not None:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            i += 1
            continue
        if ch in {'"', "'", "`"}:
            quote = ch
        elif ch == "(":
            paren += 1
        elif ch == ")":
            paren -= 1
        elif ch == "{":
            brace += 1
        elif ch == "}":
            brace -= 1
        elif ch == "[":
            bracket += 1
        elif ch == "]":
            bracket -= 1
        elif ch == "," and paren == 1 and brace == 0 and bracket == 0:
            j = i + 1
            while j < len(text) and text[j].isspace():
                j += 1
            return j if j < len(text) and text[j] == "{" else None
        i += 1
    return None


def add_merge_method_to_append_literals(text: str) -> tuple[str, int]:
    needle = "appendMergeSuggestionDecision("
    positions: list[tuple[int, int]] = []
    cursor = 0
    while True:
        call = text.find(needle, cursor)
        if call < 0:
            break
        obj_start = second_argument_object_start(text, call)
        if obj_start is not None:
            obj_end = match_brace(text, obj_start)
            body = text[obj_start : obj_end + 1]
            if "mergeMethod:" not in body:
                positions.append((obj_start, obj_end))
        cursor = call + len(needle)

    added = 0
    for obj_start, obj_end in reversed(positions):
        body = text[obj_start : obj_end + 1]
        marker = "groupId:"
        marker_pos = body.find(marker)
        if marker_pos < 0:
            raise SystemExit("append input object without groupId")
        line_end = body.find("\n", marker_pos)
        if line_end < 0:
            raise SystemExit("groupId line without newline")
        line_start = body.rfind("\n", 0, marker_pos) + 1
        indent = body[line_start:marker_pos]
        insertion = f"\n{indent}mergeMethod: \"near_duplicate\"," 
        body = body[:line_end] + insertion + body[line_end:]
        text = text[:obj_start] + body + text[obj_end + 1 :]
        added += 1
    return text, added


# App.tsx: stale re-merge inserted mergeMethod twice in the same suggestion literal.
path = "03_Implement/frontend/src/App.tsx"
text = read(path)
text = replace_once(
    text,
    "              mergedTextDraft: mergedText,\n              mergeMethod,\n              rationale: review.rationale,",
    "              mergedTextDraft: mergedText,\n              rationale: review.rationale,",
    "App duplicate mergeMethod",
)
write(path, text)

# Stream B source: keep exactly one import, input field and comparison.
path = "03_Implement/frontend/src/domain/stream_b_contract_handoff.ts"
text = read(path)
text = replace_once(
    text,
    'import type { MergeMethod } from "./merge_method";\nimport type { DocumentV1 } from "./types";\nimport type { MergeMethod } from "./merge_method";',
    'import type { MergeMethod } from "./merge_method";\nimport type { DocumentV1 } from "./types";',
    "Stream B duplicate import",
)
text = replace_once(
    text,
    "  mergedTextDraft: string;\n  editedText: string;\n  mergeMethod: MergeMethod;\n};",
    "  mergedTextDraft: string;\n  editedText: string;\n};",
    "Stream B duplicate input field",
)
text = replace_once(
    text,
    "    entry.mergeMethod === input.mergeMethod &&\n    entry.action === input.decision &&\n    entry.mergeMethod === input.mergeMethod &&",
    "    entry.mergeMethod === input.mergeMethod &&\n    entry.action === input.decision &&",
    "Stream B duplicate comparison",
)
write(path, text)

# Stream B tests: remove only the duplicated second property.
for path in [
    "03_Implement/frontend/src/domain/stream_b_contract_handoff.test.ts",
    "03_Implement/frontend/src/domain/stream_b_mock_validation.test.ts",
]:
    text = read(path)
    lines = text.splitlines(keepends=True)
    seen_in_object = False
    out: list[str] = []
    removed = 0
    for line in lines:
        if 'groupId: "g1"' in line:
            seen_in_object = True
        if seen_in_object and "mergeMethod: \"near_duplicate\"" in line:
            if any("mergeMethod: \"near_duplicate\"" in prior for prior in out[-8:]):
                removed += 1
                continue
        out.append(line)
        if seen_in_object and line.lstrip().startswith("},"):
            seen_in_object = False
    if removed != 1:
        raise SystemExit(f"{path}: expected one duplicated mergeMethod property, removed {removed}")
    write(path, "".join(out))

# External-agent import: restore the single validated parser block from PR #2869.
path = "03_Implement/frontend/src/import/agent_response_import.ts"
text = read(path)
text = replace_once(
    text,
    'import { isMergeMethod, type MergeMethod } from "../domain/merge_method";\nimport type { AgentResponseProvenance } from "../storage/agent_task_ledger";\nimport { isMergeMethod, type MergeMethod } from "../domain/merge_method";',
    'import { isMergeMethod, type MergeMethod } from "../domain/merge_method";\nimport type { AgentResponseProvenance } from "../storage/agent_task_ledger";',
    "agent import duplicate mergeMethod import",
)
text = replace_once(
    text,
    '\n  const content = parseContent(value.content);\n  if (kind === "merge_candidate" && !isMergeMethod(content.mergeMethod)) {\n    return { errors: ["proposal.merge_candidate_missing_or_invalid_merge_method"], warnings };\n  }\n\n  const proposal: ParsedAgentProposal = {',
    '\n  const proposal: ParsedAgentProposal = {',
    "agent import duplicate content parser",
)
write(path, text)

# Decision tests: new append inputs must explicitly carry mergeMethod; legacy stored decisions remain untouched.
path = "03_Implement/frontend/src/domain/merge_suggestion_decisions.test.ts"
text = read(path)
text, added = add_merge_method_to_append_literals(text)
if added != 7:
    raise SystemExit(f"decision tests: expected 7 missing literal mergeMethod inputs, added {added}")
text = replace_once(
    text,
    "        rationale: undefined,\n        representativeCardId:",
    "        rationale: undefined,\n        mergeMethod: \"near_duplicate\",\n        representativeCardId:",
    "decision exact expectation mergeMethod",
)
# The shared partial-invalid fixture is passed by variable rather than object literal.
text = replace_once(
    text,
    '      groupId: "g-partial",\n      decision: "partial" as const,',
    '      groupId: "g-partial",\n      mergeMethod: "near_duplicate" as const,\n      decision: "partial" as const,',
    "decision shared partial fixture",
)
write(path, text)

# UI fixture: all derived suggestion cases inherit this required field.
path = "03_Implement/frontend/src/ui/MergeSuggestionsPanel.test.ts"
text = read(path)
text = replace_once(
    text,
    '        groupId: "heuristic-risk-a-b",\n        targetCardId:',
    '        groupId: "heuristic-risk-a-b",\n        mergeMethod: "near_duplicate" as const,\n        targetCardId:',
    "MergeSuggestionsPanel base fixture mergeMethod",
)
write(path, text)

print(f"patched append inputs: {added}")
