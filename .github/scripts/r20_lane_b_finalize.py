from pathlib import Path
import subprocess

BRANCH = "dogfood/r20-merge-method-traceability-20260904"


def run(*args: str, cwd: str | None = None) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


run("git", "fetch", "origin", "main")
run("git", "merge", "--no-edit", "origin/main")

# ---------------------------------------------------------------------------
# Frontend: MergeSuggestion/decision contract seams that were still outside
# the smaller R20 patch.  Keep edits surgical and fail if anchors drift.
# ---------------------------------------------------------------------------

path = Path("03_Implement/frontend/src/domain/types.ts")
text = read_text(path)
old = "  rationale?: string;\r\n  representativeCardId?: string;"
new = "  rationale?: string;\r\n  mergeMethod?: \"near_duplicate\" | \"kernel_fusion\";\r\n  representativeCardId?: string;"
if new not in text:
    if text.count(old) != 1:
        raise SystemExit("types.ts: MergeSuggestionDecisionEntry anchor mismatch")
    text = text.replace(old, new, 1)
write_text(path, text)

path = Path("03_Implement/frontend/src/App.tsx")
text = read_text(path)
old = (
    "          const cardIds = review.content.cardIds.filter((id) => cardsById.has(id));\r\n"
    "          const mergedText = review.content.mergedTextDraft.trim();\r\n"
    "          if (cardIds.length < 2 || !mergedText) break;\r\n"
)
new = (
    "          const cardIds = review.content.cardIds.filter((id) => cardsById.has(id));\r\n"
    "          const mergedText = review.content.mergedTextDraft.trim();\r\n"
    "          const mergeMethod = review.content.mergeMethod;\r\n"
    "          if (cardIds.length < 2 || !mergedText || !mergeMethod) break;\r\n"
)
if new not in text:
    if text.count(old) != 1:
        raise SystemExit("App.tsx: external merge review guard anchor mismatch")
    text = text.replace(old, new, 1)
old = (
    "              groupId: review.content.groupId,\r\n"
    "              cardIds,\r\n"
    "              mergedTextDraft: mergedText,\r\n"
)
new = (
    "              groupId: review.content.groupId,\r\n"
    "              cardIds,\r\n"
    "              mergedTextDraft: mergedText,\r\n"
    "              mergeMethod,\r\n"
)
if new not in text:
    if text.count(old) != 1:
        raise SystemExit("App.tsx: external merge review proposal anchor mismatch")
    text = text.replace(old, new, 1)
write_text(path, text)

path = Path("03_Implement/frontend/src/ui/MergeSuggestionsPanel.test.ts")
text = read_text(path)
old = "        mergedTextDraft: \"Merged\",\r\n        rationale: \"Because\","
new = "        mergedTextDraft: \"Merged\",\r\n        mergeMethod: \"near_duplicate\" as const,\r\n        rationale: \"Because\","
if new not in text:
    if text.count(old) != 1:
        raise SystemExit("MergeSuggestionsPanel.test.ts: suggestion fixture anchor mismatch")
    text = text.replace(old, new, 1)
write_text(path, text)

# Stream-B export/import: the common contract must carry mergeMethod and reject
# missing/unknown values rather than silently widening or dropping it.
path = Path("03_Implement/frontend/src/domain/stream_b_contract_handoff.ts")
text = read_text(path)
old = (
    "    content: {\n"
    "      groupId: suggestion.groupId,\n"
    "      cardIds: [...suggestion.cardIds],\n"
    "      mergedTextDraft: suggestion.mergedTextDraft,\n"
    "      rationale: suggestion.rationale,\n"
    "    },\n"
)
new = (
    "    content: {\n"
    "      groupId: suggestion.groupId,\n"
    "      cardIds: [...suggestion.cardIds],\n"
    "      mergedTextDraft: suggestion.mergedTextDraft,\n"
    "      mergeMethod: suggestion.mergeMethod,\n"
    "      rationale: suggestion.rationale,\n"
    "    },\n"
)
if new not in text:
    if text.count(old) != 1:
        raise SystemExit("stream_b_contract_handoff.ts: merge review content anchor mismatch")
    text = text.replace(old, new, 1)
write_text(path, text)

path = Path("03_Implement/frontend/src/import/agent_response.ts")
text = read_text(path)
if 'import { isMergeMethod } from "../domain/merge_method";' not in text:
    anchor = 'import type { DocumentV1 } from "../domain/types";\n'
    if text.count(anchor) != 1:
        raise SystemExit("agent_response.ts: import anchor mismatch")
    text = text.replace(anchor, anchor + 'import { isMergeMethod } from "../domain/merge_method";\n', 1)
old = (
    '      mergedTextDraft: asString(contentRaw.mergedTextDraft, "review.content.mergedTextDraft"),\n'
    '      rationale: asOptionalString(contentRaw.rationale, "review.content.rationale"),\n'
)
new = (
    '      mergedTextDraft: asString(contentRaw.mergedTextDraft, "review.content.mergedTextDraft"),\n'
    '      mergeMethod: isMergeMethod(contentRaw.mergeMethod)\n'
    '        ? contentRaw.mergeMethod\n'
    '        : (() => { throw new Error("review.content.mergeMethod must be near_duplicate or kernel_fusion"); })(),\n'
    '      rationale: asOptionalString(contentRaw.rationale, "review.content.rationale"),\n'
)
if new not in text:
    if text.count(old) != 1:
        raise SystemExit("agent_response.ts: merge review parser anchor mismatch")
    text = text.replace(old, new, 1)
write_text(path, text)

# Add focused regression tests for Stream-B import and Document persistence.
path = Path("03_Implement/frontend/src/import/agent_response_merge_method.test.ts")
write_text(path, '''import { describe, expect, it } from "vitest";\nimport { parseAgentResponseJson } from "./agent_response";\n\nfunction raw(method?: string) {\n  const content: Record<string, unknown> = {\n    groupId: "g",\n    cardIds: ["a", "b"],\n    mergedTextDraft: "merged",\n  };\n  if (method !== undefined) content.mergeMethod = method;\n  return JSON.stringify({\n    version: "1",\n    kind: "agent-response",\n    taskId: "t",\n    baseDocSignature: "sig",\n    generatedAt: "2026-09-04T00:00:00.000Z",\n    reviews: [{ id: "r", kind: "merge-suggestion", content }],\n  });\n}\n\ndescribe("agent response mergeMethod", () => {\n  it("preserves kernel_fusion", () => {\n    const parsed = parseAgentResponseJson(raw("kernel_fusion"));\n    expect(parsed.reviews[0]?.kind).toBe("merge-suggestion");\n    if (parsed.reviews[0]?.kind === "merge-suggestion") {\n      expect(parsed.reviews[0].content.mergeMethod).toBe("kernel_fusion");\n    }\n  });\n\n  it("preserves near_duplicate", () => {\n    const parsed = parseAgentResponseJson(raw("near_duplicate"));\n    if (parsed.reviews[0]?.kind === "merge-suggestion") {\n      expect(parsed.reviews[0].content.mergeMethod).toBe("near_duplicate");\n    }\n  });\n\n  it("rejects a missing method", () => {\n    expect(() => parseAgentResponseJson(raw())).toThrow(/mergeMethod/);\n  });\n\n  it("rejects an unknown method", () => {\n    expect(() => parseAgentResponseJson(raw("semantic_similarity"))).toThrow(/mergeMethod/);\n  });\n});\n''')

path = Path("03_Implement/frontend/src/domain/merge_method_persistence.test.ts")
write_text(path, '''import { describe, expect, it } from "vitest";\nimport { validateDocument } from "./validate";\n\nfunction baseDoc() {\n  return {\n    version: 1,\n    id: "d",\n    title: "test",\n    createdAt: "2026-09-04T00:00:00.000Z",\n    updatedAt: "2026-09-04T00:00:00.000Z",\n    transform: { panX: 0, panY: 0, zoom: 1 },\n    cards: [],\n    edges: [],\n    islands: [],\n    evidenceLinks: [],\n    readingOrder: [],\n    narratives: [],\n  };\n}\n\ndescribe("mergeMethod persistence", () => {\n  it("preserves near_duplicate on a new decision", () => {\n    const raw = { ...baseDoc(), mergeSuggestionDecisions: [{\n      id: "m", groupId: "g", decision: "accept", decidedAt: "2026-09-04T00:00:00.000Z",\n      cardIds: ["a", "b"], mergedTextDraft: "x", editedText: "x", mergeMethod: "near_duplicate",\n    }] };\n    const doc = validateDocument(raw);\n    expect(doc.mergeSuggestionDecisions?.[0]?.mergeMethod).toBe("near_duplicate");\n  });\n\n  it("preserves kernel_fusion on a new decision", () => {\n    const raw = { ...baseDoc(), mergeSuggestionDecisions: [{\n      id: "m", groupId: "g", decision: "accept", decidedAt: "2026-09-04T00:00:00.000Z",\n      cardIds: ["a", "b"], mergedTextDraft: "x", editedText: "x", mergeMethod: "kernel_fusion",\n    }] };\n    const doc = validateDocument(raw);\n    expect(doc.mergeSuggestionDecisions?.[0]?.mergeMethod).toBe("kernel_fusion");\n  });\n\n  it("keeps legacy decisions readable without inferring a method", () => {\n    const raw = { ...baseDoc(), mergeSuggestionDecisions: [{\n      id: "legacy", groupId: "g", decision: "accept", decidedAt: "2026-09-04T00:00:00.000Z",\n      cardIds: ["a", "b"], mergedTextDraft: "x", editedText: "x",\n    }] };\n    const doc = validateDocument(raw);\n    expect(doc.mergeSuggestionDecisions?.[0]).not.toHaveProperty("mergeMethod");\n  });\n\n  it("rejects an unknown method instead of widening it", () => {\n    const raw = { ...baseDoc(), mergeSuggestionDecisions: [{\n      id: "m", groupId: "g", decision: "accept", decidedAt: "2026-09-04T00:00:00.000Z",\n      cardIds: ["a", "b"], mergedTextDraft: "x", editedText: "x", mergeMethod: "semantic_similarity",\n    }] };\n    expect(() => validateDocument(raw)).toThrow();\n  });\n});\n''')

# SafeMode field policy is applied by the workflow shim immediately before this
# script runs, because the file is LF and independently edited by other lanes.

# ---------------------------------------------------------------------------
# Backend: dedicated old/new decision persistence test is created by the
# workflow shim; provider parse tests already live in the branch.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Documentation seams used by external-agent collaboration and Stream B.
# ---------------------------------------------------------------------------
path = Path("02_Architecture/external_agent_collaboration_spec.html")
text = read_text(path)
old = (
    '<code>groupId</code> / <code>cardIds</code> / <code>mergedTextDraft</code> / '
    '<code>rationale?</code>'
)
new = (
    '<code>groupId</code> / <code>cardIds</code> / <code>mergedTextDraft</code> / '
    '<code>mergeMethod</code> (<code>near_duplicate</code> | <code>kernel_fusion</code>) / '
    '<code>rationale?</code>'
)
if new not in text:
    if text.count(old) != 1:
        raise SystemExit("external_agent_collaboration_spec.html: response content schema anchor mismatch")
    text = text.replace(old, new, 1)
write_text(path, text)

# Validation gate: no push unless all targeted contracts and typechecks pass.
frontend = "03_Implement/frontend"
run("npm", "ci", cwd=frontend)
run(
    "npx", "vitest", "run",
    "src/api/client.test.ts",
    "src/domain/merge_candidates.test.ts",
    "src/domain/merge_suggestion_decisions.test.ts",
    "src/domain/merge_suggestion_apply.test.ts",
    "src/domain/stream_b_mock_validation.test.ts",
    "src/domain/stream_b_contract_handoff.test.ts",
    "src/domain/merge_method_persistence.test.ts",
    "src/import/agent_response_import.test.ts",
    "src/import/agent_response_merge_method.test.ts",
    "src/ui/MergeSuggestionsPanel.test.ts",
    "src/ui/MergeSuggestionsPanel.merge_method.test.ts",
    "src/ui/merge_method_label.test.ts",
    cwd=frontend,
)
run("npm", "run", "typecheck", cwd=frontend)

run("python", "-m", "pip", "install", "-e", "./03_Implement/backend[test]")
run(
    "python", "-m", "pytest",
    "tests/test_ai_merge_ir.py",
    "tests/test_ai_merge_semantics.py",
    "tests/test_models_backward_compat.py",
    "-q",
    cwd="03_Implement/backend",
)
run("python", "01_Plans/issues/validate_active_issue_memos.py")
run("python", "01_Plans/dogfood/validate_dogfood_docs.py")
run("git", "-c", "core.whitespace=cr-at-eol", "diff", "--check")

# Remove one-shot machinery before recording the validated product change.
for temp in [
    ".github/workflows/r20-lane-b-finalize.yml",
    ".github/scripts/r20_lane_b_finalize.py",
]:
    Path(temp).unlink(missing_ok=True)

run("git", "config", "user.name", "github-actions[bot]")
run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
run("git", "add", "-A")
run("git", "-c", "core.whitespace=cr-at-eol", "diff", "--cached", "--check")
run("git", "commit", "-m", "fix: mergeMethodの契約継ぎ目と永続化を閉じる")
run("git", "push", "origin", f"HEAD:{BRANCH}")
