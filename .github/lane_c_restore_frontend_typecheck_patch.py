from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    with (ROOT / path).open("r", encoding="utf-8", newline="") as handle:
        return handle.read()


def write(path: str, text: str) -> None:
    with (ROOT / path).open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def sub_once(text: str, pattern: str, repl, label: str) -> str:
    updated, count = re.subn(pattern, repl, text, count=1, flags=re.M)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return updated


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
            if "groupId:" in body and "mergeMethod:" not in body:
                positions.append((obj_start, obj_end))
        cursor = call + len(needle)

    added = 0
    for obj_start, obj_end in reversed(positions):
        body = text[obj_start : obj_end + 1]
        marker_pos = body.find("groupId:")
        line_end = body.find("\n", marker_pos)
        if line_end < 0:
            raise SystemExit("groupId line without newline")
        line_start = body.rfind("\n", 0, marker_pos) + 1
        indent = body[line_start:marker_pos]
        newline = "\r\n" if line_end > 0 and body[line_end - 1] == "\r" else "\n"
        insert_pos = line_end + 1
        insertion = f"{indent}mergeMethod: \"near_duplicate\",{newline}"
        body = body[:insert_pos] + insertion + body[insert_pos:]
        text = text[:obj_start] + body + text[obj_end + 1 :]
        added += 1
    return text, added


# App: remove only the duplicated property and preserve the local line endings.
path = "03_Implement/frontend/src/App.tsx"
text = read(path)
text = sub_once(
    text,
    r'(?P<a>              mergedTextDraft: mergedText,)(?P<nl>\r?\n)              mergeMethod,(?P=nl)(?P<b>              rationale: review\.rationale,)',
    lambda m: m.group("a") + m.group("nl") + m.group("b"),
    "App duplicate mergeMethod",
)
write(path, text)

# Stream B handoff: collapse stale duplicate insertions and carry the current partial subset contract.
path = "03_Implement/frontend/src/domain/stream_b_contract_handoff.ts"
text = read(path)
text = sub_once(
    text,
    r'import type \{ MergeMethod \} from "\./merge_method";(?P<nl>\r?\n)import type \{ DocumentV1 \} from "\./types";(?P=nl)import type \{ MergeMethod \} from "\./merge_method";',
    lambda m: 'import type { MergeMethod } from "./merge_method";' + m.group("nl") + 'import type { DocumentV1 } from "./types";',
    "Stream B duplicate import",
)
text = sub_once(
    text,
    r'  mergedTextDraft: string;(?P<nl>\r?\n)  editedText: string;(?P=nl)  mergeMethod: MergeMethod;(?P=nl)\};',
    lambda m: '  mergedTextDraft: string;' + m.group("nl") + '  editedText: string;' + m.group("nl") + '};',
    "Stream B duplicate input field",
)
text = sub_once(
    text,
    r'  decision: MergeSuggestionDecision;(?P<nl>\r?\n)  cardIds: string\[\];(?P=nl)  mergedTextDraft: string;',
    lambda m: '  decision: MergeSuggestionDecision;' + m.group("nl") + '  cardIds: string[];' + m.group("nl") + '  selectedCardIds?: string[];' + m.group("nl") + '  mergedTextDraft: string;',
    "Stream B partial selectedCardIds handoff",
)
text = sub_once(
    text,
    r'    entry\.mergeMethod === input\.mergeMethod &&(?P<nl>\r?\n)    entry\.action === input\.decision &&(?P=nl)    entry\.mergeMethod === input\.mergeMethod &&',
    lambda m: '    entry.mergeMethod === input.mergeMethod &&' + m.group("nl") + '    entry.action === input.decision &&',
    "Stream B duplicate comparison",
)
write(path, text)

# Stream B handoff fixture: partial is a strict subset, not an implicit full-group selection.
path = "03_Implement/frontend/src/domain/stream_b_contract_handoff.test.ts"
text = read(path)
text = sub_once(
    text,
    r'        groupId: "g1",(?P<nl>\r?\n)        mergeMethod: "near_duplicate",(?P=nl)        decision: "partial",(?P=nl)        cardIds: \["c2", "c1"\],(?P=nl)        mergedTextDraft: "risk mitigation",(?P=nl)        editedText: "risk mitigation \(reviewed\)",(?P=nl)        mergeMethod: "near_duplicate",',
    lambda m: (
        '        groupId: "g1",' + m.group("nl")
        + '        mergeMethod: "near_duplicate",' + m.group("nl")
        + '        decision: "partial",' + m.group("nl")
        + '        cardIds: ["c2", "c1", "c3"],' + m.group("nl")
        + '        selectedCardIds: ["c2", "c1"],' + m.group("nl")
        + '        mergedTextDraft: "risk mitigation",' + m.group("nl")
        + '        editedText: "risk mitigation (reviewed)",'
    ),
    "Stream B partial fixture",
)
write(path, text)

# Stream B mock fixture: only partial carries an explicit strict subset.
path = "03_Implement/frontend/src/domain/stream_b_mock_validation.test.ts"
text = read(path)
text = sub_once(
    text,
    r'          groupId: "g1",(?P<nl>\r?\n)          mergeMethod: "near_duplicate",(?P=nl)          decision: action,(?P=nl)          cardIds: \["c2", "c1"\],(?P=nl)          mergedTextDraft: "risk mitigation",(?P=nl)          editedText: `risk mitigation \(\$\{action\}\)`,(?P=nl)          mergeMethod: "near_duplicate",',
    lambda m: (
        '          groupId: "g1",' + m.group("nl")
        + '          mergeMethod: "near_duplicate",' + m.group("nl")
        + '          decision: action,' + m.group("nl")
        + '          cardIds: action === "partial" ? ["c2", "c1", "c3"] : ["c2", "c1"],' + m.group("nl")
        + '          selectedCardIds: action === "partial" ? ["c2", "c1"] : undefined,' + m.group("nl")
        + '          mergedTextDraft: "risk mitigation",' + m.group("nl")
        + '          editedText: `risk mitigation (${action})`,'
    ),
    "Stream B mock partial fixture",
)
write(path, text)

# External-agent import: restore the single parser path validated in PR #2869.
path = "03_Implement/frontend/src/import/agent_response_import.ts"
text = read(path)
text = sub_once(
    text,
    r'import \{ isMergeMethod, type MergeMethod \} from "\.\./domain/merge_method";(?P<nl>\r?\n)import type \{ AgentResponseProvenance \} from "\.\./storage/agent_task_ledger";(?P=nl)import \{ isMergeMethod, type MergeMethod \} from "\.\./domain/merge_method";',
    lambda m: 'import { isMergeMethod, type MergeMethod } from "../domain/merge_method";' + m.group("nl") + 'import type { AgentResponseProvenance } from "../storage/agent_task_ledger";',
    "agent import duplicate mergeMethod import",
)
text = sub_once(
    text,
    r'(?P<nl>\r?\n)  const content = parseContent\(value\.content\);(?P=nl)  if \(kind === "merge_candidate" && !isMergeMethod\(content\.mergeMethod\)\) \{(?P=nl)    return \{ errors: \["proposal\.merge_candidate_missing_or_invalid_merge_method"\], warnings \};(?P=nl)  \}(?P=nl)(?P=nl)  const proposal: ParsedAgentProposal = \{',
    lambda m: m.group("nl") + '  const proposal: ParsedAgentProposal = {',
    "agent import duplicate content parser",
)
write(path, text)

# New decision inputs require mergeMethod; persisted legacy decision fixtures intentionally remain without it.
path = "03_Implement/frontend/src/domain/merge_suggestion_decisions.test.ts"
text = read(path)
text, added = add_merge_method_to_append_literals(text)
if added != 7:
    raise SystemExit(f"decision tests: expected 7 missing literal mergeMethod inputs, added {added}")
text = sub_once(
    text,
    r'        rationale: undefined,(?P<nl>\r?\n)        representativeCardId:',
    lambda m: '        rationale: undefined,' + m.group("nl") + '        mergeMethod: "near_duplicate",' + m.group("nl") + '        representativeCardId:',
    "decision exact expectation mergeMethod",
)
text = sub_once(
    text,
    r'      groupId: "g-partial",(?P<nl>\r?\n)      decision: "partial" as const,',
    lambda m: '      groupId: "g-partial",' + m.group("nl") + '      mergeMethod: "near_duplicate" as const,' + m.group("nl") + '      decision: "partial" as const,',
    "decision shared partial fixture",
)
write(path, text)

# UI test fixture carries the same required method as production suggestions.
path = "03_Implement/frontend/src/ui/MergeSuggestionsPanel.test.ts"
text = read(path)
text = sub_once(
    text,
    r'        groupId: "heuristic-risk-a-b",(?P<nl>\r?\n)        targetCardId:',
    lambda m: '        groupId: "heuristic-risk-a-b",' + m.group("nl") + '        mergeMethod: "near_duplicate" as const,' + m.group("nl") + '        targetCardId:',
    "MergeSuggestionsPanel base fixture mergeMethod",
)
write(path, text)

print(f"patched append inputs: {added}")
