from __future__ import annotations

from pathlib import Path
import subprocess

BRANCH = "dogfood/r20-merge-method-traceability-20260904"


def run(*args: str, cwd: str | None = None) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.read()


def write_text(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def newline_of(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def replace_exact(path: str, old: str, new: str, expected: int = 1) -> None:
    text = read_text(path)
    count = text.count(old)
    if count != expected:
        raise SystemExit(f"{path}: expected {expected} occurrence(s), found {count}: {old[:100]!r}")
    write_text(path, text.replace(old, new, expected))


def update_region(path: str, start_marker: str, end_marker: str, updater) -> None:
    text = read_text(path)
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"{path}: start marker not found: {start_marker}")
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f"{path}: end marker not found: {end_marker}")
    region = text[start:end]
    updated = updater(region, newline_of(text))
    if updated == region:
        raise SystemExit(f"{path}: updater made no change")
    write_text(path, text[:start] + updated + text[end:])


# Verify against latest main, not the PR's original base.
run("git", "fetch", "origin", "main")
run("git", "merge", "--no-edit", "origin/main")

# 1. Persisted DocumentV1 type: new decisions write mergeMethod, old decisions may omit it.
def patch_types(region: str, nl: str) -> str:
    if "mergeMethod?:" in region:
        return region
    needle = f"  rationale?: string;{nl}"
    if region.count(needle) != 1:
        raise SystemExit("types.ts: rationale anchor mismatch in MergeSuggestionDecisionEntry")
    return region.replace(
        needle,
        needle + f'  mergeMethod?: "near_duplicate" | "kernel_fusion";{nl}',
        1,
    )

update_region(
    "03_Implement/frontend/src/domain/types.ts",
    "export type MergeSuggestionDecisionEntry = {",
    "export type PatchConflictMeta =",
    patch_types,
)

# 2. Strict validator: optional field for backward compatibility, known values only.
def patch_validate_doc(region: str, nl: str) -> str:
    if '"mergeMethod"' not in region:
        needle = '"rationale", "representativeCardId"'
        if region.count(needle) != 1:
            raise SystemExit("validate_doc.ts: merge decision allowed-key anchor mismatch")
        region = region.replace(needle, '"rationale", "mergeMethod", "representativeCardId"', 1)
    if ".mergeMethod:" not in region:
        anchor = f'  if (item.representativeCardId !== undefined && typeof item.representativeCardId !== "string") {{{nl}'
        if region.count(anchor) != 1:
            raise SystemExit("validate_doc.ts: representativeCardId validation anchor mismatch")
        validation = (
            f'  if ({nl}'
            f'    item.mergeMethod !== undefined{nl}'
            f'    && item.mergeMethod !== "near_duplicate"{nl}'
            f'    && item.mergeMethod !== "kernel_fusion"{nl}'
            f'  ) {{{nl}'
            f'    errors.push(`${{path}}.mergeMethod: must be \'near_duplicate\' | \'kernel_fusion\' when provided`);{nl}'
            f'    valid = false;{nl}'
            f'  }}{nl}'
        )
        region = region.replace(anchor, validation + anchor, 1)
    return region

update_region(
    "03_Implement/frontend/src/domain/validate_doc.ts",
    "function validateMergeSuggestionDecisionEntry(",
    "// DOMAIN-EXPR-04",
    patch_validate_doc,
)

# 3. Lenient normalizer: preserve known method, never guess/retain unknown values.
def patch_validate(region: str, nl: str) -> str:
    if "mergeMethod: item.mergeMethod" in region:
        return region
    needle = f'      ...(typeof item.rationale === "string" ? {{ rationale: item.rationale }} : {{}}),{nl}'
    if region.count(needle) != 1:
        raise SystemExit("validate.ts: rationale normalization anchor mismatch")
    addition = (
        needle
        + f'      ...((item.mergeMethod === "near_duplicate" || item.mergeMethod === "kernel_fusion"){nl}'
        + f'        ? {{ mergeMethod: item.mergeMethod }}{nl}'
        + f'        : {{}}),{nl}'
    )
    return region.replace(needle, addition, 1)

update_region(
    "03_Implement/frontend/src/domain/validate.ts",
    "function parseMergeSuggestionDecisions(",
    "function isContradictionSignalReviewStatus(",
    patch_validate,
)

# 4. Stream B contract handoff must carry and validate the method.
path = "03_Implement/frontend/src/domain/stream_b_contract_handoff.ts"
text = read_text(path)
nl = newline_of(text)
if 'import type { MergeMethod } from "./merge_method";' not in text:
    anchor = f'import {{ appendMergeSuggestionDecision, type MergeSuggestionDecision }} from "./merge_suggestion_decisions";{nl}'
    if text.count(anchor) != 1:
        raise SystemExit("stream_b_contract_handoff.ts: import anchor mismatch")
    text = text.replace(anchor, anchor + f'import type {{ MergeMethod }} from "./merge_method";{nl}', 1)
if "  mergeMethod: MergeMethod;" not in text:
    anchor = f"  groupId: string;{nl}  decision: MergeSuggestionDecision;"
    if text.count(anchor) != 1:
        raise SystemExit("stream_b_contract_handoff.ts: input anchor mismatch")
    text = text.replace(anchor, f"  groupId: string;{nl}  mergeMethod: MergeMethod;{nl}  decision: MergeSuggestionDecision;", 1)
if "entry.mergeMethod === input.mergeMethod" not in text:
    anchor = f"    entry?.snapshotVersion === STREAM_B_CONTRACTS.decisionLog.contractId &&{nl}    entry.action === input.decision &&"
    if text.count(anchor) != 1:
        raise SystemExit("stream_b_contract_handoff.ts: validation anchor mismatch")
    text = text.replace(
        anchor,
        f"    entry?.snapshotVersion === STREAM_B_CONTRACTS.decisionLog.contractId &&{nl}    entry.mergeMethod === input.mergeMethod &&{nl}    entry.action === input.decision &&",
        1,
    )
write_text(path, text)

# 5. External-agent merge candidates participate in the same common contract.
path = "03_Implement/frontend/src/import/agent_response_import.ts"
text = read_text(path)
nl = newline_of(text)
if 'from "../domain/merge_method";' not in text:
    anchor = f'import {{ AGENT_TASK_KINDS, type AgentTaskCorrelation }} from "../export/agent_task_export";{nl}'
    if text.count(anchor) != 1:
        raise SystemExit("agent_response_import.ts: merge-method import anchor mismatch")
    text = text.replace(anchor, anchor + f'import {{ isMergeMethod, type MergeMethod }} from "../domain/merge_method";{nl}', 1)
if "  mergeMethod?: MergeMethod;" not in text:
    anchor = f"  mergedText?: string;{nl}"
    if text.count(anchor) != 1:
        raise SystemExit("agent_response_import.ts: content type anchor mismatch")
    text = text.replace(anchor, anchor + f"  mergeMethod?: MergeMethod;{nl}", 1)
if "mergeMethod: isMergeMethod(value.mergeMethod)" not in text:
    anchor = f"    mergedText: sanitizeString(value.mergedText),{nl}"
    if text.count(anchor) != 1:
        raise SystemExit("agent_response_import.ts: parseContent anchor mismatch")
    text = text.replace(anchor, anchor + f"    mergeMethod: isMergeMethod(value.mergeMethod) ? value.mergeMethod : undefined,{nl}", 1)
if "merge_candidate_missing_or_invalid_merge_method" not in text:
    anchor = f"  let patch: PatchV1 | undefined;{nl}"
    if text.count(anchor) != 1:
        raise SystemExit("agent_response_import.ts: proposal patch anchor mismatch")
    guard = (
        f"  const content = parseContent(value.content);{nl}"
        f'  if (kind === "merge_candidate" && !content.mergeMethod) {{{nl}'
        f'    return {{ errors: ["proposal.merge_candidate_missing_or_invalid_merge_method"], warnings }};{nl}'
        f"  }}{nl}{nl}"
    )
    text = text.replace(anchor, guard + anchor, 1)
    old = f"    content: parseContent(value.content),{nl}"
    if text.count(old) != 1:
        raise SystemExit("agent_response_import.ts: proposal content anchor mismatch")
    text = text.replace(old, f"    content,{nl}", 1)
write_text(path, text)

# 6. External task sheet explicitly requests the method instead of relying on inference.
path = "03_Implement/frontend/src/export/agent_task_export.ts"
text = read_text(path)
nl = newline_of(text)
old = f'    case "merge_candidates":{nl}      return `文脈に含まれるカードの中で、統合（マージ）できそうな組を${{desiredCount}}件程度、提案してください。対象範囲: ${{scopeLabel}}。`;{nl}'
if "content.mergeMethod に必ず明示してください" not in text:
    if text.count(old) != 1:
        raise SystemExit("agent_task_export.ts: merge task instruction anchor mismatch")
    new = f'    case "merge_candidates":{nl}      return `文脈に含まれるカードの中で、統合（マージ）できそうな組を${{desiredCount}}件程度、提案してください。対象範囲: ${{scopeLabel}}。近い記述を整理する場合は near_duplicate、完全な重複ではない複数カードから共通の意味核を立てる場合は kernel_fusion とし、各 merge_candidate の content.mergeMethod に必ず明示してください。`;{nl}'
    text = text.replace(old, new, 1)
if "near_duplicate | kernel_fusion (kind=merge_candidate のとき必須)" not in text:
    old_schema = 'content: { title: "string?", text: "string?", mergedText: "string?" },'
    if text.count(old_schema) != 1:
        raise SystemExit("agent_task_export.ts: response schema anchor mismatch")
    text = text.replace(
        old_schema,
        'content: { title: "string?", text: "string?", mergedText: "string?", mergeMethod: "near_duplicate | kernel_fusion (kind=merge_candidate のとき必須)" },',
        1,
    )
write_text(path, text)

# 7. App converts imported merge proposals only when the explicit method survived validation.
path = "03_Implement/frontend/src/App.tsx"
text = read_text(path)
nl = newline_of(text)
if "const mergeMethod = review.content.mergeMethod;" not in text:
    anchor = f"          const mergedText = review.content.mergedText ?? review.content.text;{nl}          if (cardIds.length < 2 || !mergedText) break;"
    if text.count(anchor) != 1:
        raise SystemExit("App.tsx: external merge candidate anchor mismatch")
    text = text.replace(
        anchor,
        f"          const mergedText = review.content.mergedText ?? review.content.text;{nl}          const mergeMethod = review.content.mergeMethod;{nl}          if (cardIds.length < 2 || !mergedText || !mergeMethod) break;",
        1,
    )
if "              mergeMethod," not in text:
    anchor = f"              groupId: `agent-response-${{review.proposalId}}`,{nl}              targetCardId,"
    if text.count(anchor) != 1:
        raise SystemExit("App.tsx: imported suggestion group anchor mismatch")
    text = text.replace(anchor, f"              groupId: `agent-response-${{review.proposalId}}`,{nl}              mergeMethod,{nl}              targetCardId,", 1)
write_text(path, text)

# 8. Existing test fixtures must satisfy the newly-required proposal/decision contract.
path = "03_Implement/frontend/src/domain/merge_suggestion_apply.test.ts"
text = read_text(path)
nl = newline_of(text)
anchor = f'      editedText: "待ち時間は利用継続の負担になる",{nl}'
if "mergeMethod: \"near_duplicate\"" not in text:
    if text.count(anchor) != 1:
        raise SystemExit("merge_suggestion_apply.test.ts: decision fixture anchor mismatch")
    text = text.replace(anchor, anchor + f'      mergeMethod: "near_duplicate",{nl}', 1)
write_text(path, text)

for test_path, old, new in [
    (
        "03_Implement/frontend/src/domain/stream_b_mock_validation.test.ts",
        '          groupId: "g1",\n          decision: action,',
        '          groupId: "g1",\n          mergeMethod: "near_duplicate",\n          decision: action,',
    ),
    (
        "03_Implement/frontend/src/domain/stream_b_contract_handoff.test.ts",
        '        groupId: "g1",\n        decision: "partial",',
        '        groupId: "g1",\n        mergeMethod: "near_duplicate",\n        decision: "partial",',
    ),
]:
    text = read_text(test_path)
    nl = newline_of(text)
    old_n = old.replace("\n", nl)
    new_n = new.replace("\n", nl)
    if 'mergeMethod: "near_duplicate"' not in text:
        if text.count(old_n) != 1:
            raise SystemExit(f"{test_path}: Stream B fixture anchor mismatch")
        text = text.replace(old_n, new_n, 1)
    write_text(test_path, text)

path = "03_Implement/frontend/src/ui/MergeSuggestionsPanel.test.ts"
text = read_text(path)
nl = newline_of(text)
if 'mergeMethod: "near_duplicate" as const' not in text:
    anchor = f'        groupId: "heuristic-risk-a-b",{nl}'
    if text.count(anchor) < 1:
        raise SystemExit("MergeSuggestionsPanel.test.ts: shared fixture anchor mismatch")
    text = text.replace(anchor, anchor + f'        mergeMethod: "near_duplicate" as const,{nl}', 1)
write_text(path, text)

# 9. Add focused regression evidence for persistence and external-agent fail-closed behavior.
persistence_test = Path("03_Implement/frontend/src/domain/merge_method_persistence.test.ts")
if not persistence_test.exists():
    persistence_test.write_text(
        '''import { describe, expect, it } from "vitest";\n\nimport { validateDocument } from "./validate";\nimport { validateDocumentV1Strict } from "./validate_doc";\n\nconst baseDocument = {\n  version: 1,\n  id: "doc-merge-method",\n  createdAt: "2026-09-04T00:00:00.000Z",\n  updatedAt: "2026-09-04T00:00:00.000Z",\n  transform: { panX: 0, panY: 0, zoom: 1 },\n  cards: [],\n  edges: [],\n  islands: [],\n};\n\nfunction decision(mergeMethod?: unknown) {\n  return {\n    id: "d1",\n    groupId: "g1",\n    decision: "accept",\n    decidedAt: "2026-09-04T00:01:00.000Z",\n    cardIds: ["c1", "c2"],\n    mergedTextDraft: "統合案",\n    editedText: "統合案",\n    ...(mergeMethod === undefined ? {} : { mergeMethod }),\n  };\n}\n\ndescribe("mergeMethod persisted decision compatibility", () => {\n  it.each(["near_duplicate", "kernel_fusion"] as const)("strictly accepts and preserves %s", (mergeMethod) => {\n    const raw = { ...baseDocument, mergeSuggestionDecisions: [decision(mergeMethod)] };\n    const strict = validateDocumentV1Strict(raw);\n    expect(strict.ok).toBe(true);\n    const normalized = validateDocument(raw);\n    expect(normalized.ok).toBe(true);\n    if (normalized.ok) expect(normalized.document.mergeSuggestionDecisions?.[0]?.mergeMethod).toBe(mergeMethod);\n  });\n\n  it("keeps legacy decisions without guessing a method", () => {\n    const raw = { ...baseDocument, mergeSuggestionDecisions: [decision()] };\n    const strict = validateDocumentV1Strict(raw);\n    expect(strict.ok).toBe(true);\n    const normalized = validateDocument(raw);\n    expect(normalized.ok).toBe(true);\n    if (normalized.ok) expect(normalized.document.mergeSuggestionDecisions?.[0]?.mergeMethod).toBeUndefined();\n  });\n\n  it("rejects unknown methods strictly and drops them in lenient normalization", () => {\n    const raw = { ...baseDocument, mergeSuggestionDecisions: [decision("unknown_method")] };\n    const strict = validateDocumentV1Strict(raw);\n    expect(strict.ok).toBe(false);\n    const normalized = validateDocument(raw);\n    expect(normalized.ok).toBe(true);\n    if (normalized.ok) expect(normalized.document.mergeSuggestionDecisions?.[0]?.mergeMethod).toBeUndefined();\n  });\n});\n''',
        encoding="utf-8",
    )

external_test = Path("03_Implement/frontend/src/import/agent_response_merge_method.test.ts")
if not external_test.exists():
    external_test.write_text(
        '''import { describe, expect, it } from "vitest";\n\nimport { parseAgentResponse } from "./agent_response_import";\n\nfunction payload(content: Record<string, unknown>) {\n  return JSON.stringify({\n    schemaVersion: "agent-response.v1",\n    taskId: "task-1",\n    proposals: [{\n      proposalId: "p1",\n      kind: "merge_candidate",\n      targetRef: { cardIds: ["c1", "c2"] },\n      content,\n      rationale: "意味を保って統合する",\n    }],\n  });\n}\n\ndescribe("external merge candidate mergeMethod", () => {\n  it.each(["near_duplicate", "kernel_fusion"] as const)("keeps explicit %s", (mergeMethod) => {\n    const result = parseAgentResponse(payload({ mergedText: "統合案", mergeMethod }), "lenient");\n    expect(result.ok).toBe(true);\n    if (result.ok) expect(result.response.proposals[0]?.content.mergeMethod).toBe(mergeMethod);\n  });\n\n  it.each([undefined, "unknown_method"])("does not infer %s", (mergeMethod) => {\n    const content = mergeMethod === undefined ? { mergedText: "統合案" } : { mergedText: "統合案", mergeMethod };\n    const result = parseAgentResponse(payload(content), "lenient");\n    expect(result.ok).toBe(true);\n    if (result.ok) {\n      expect(result.response.proposals).toHaveLength(0);\n      expect(result.warnings.some((warning) => warning.includes("merge_candidate_missing_or_invalid_merge_method"))).toBe(true);\n    }\n  });\n});\n''',
        encoding="utf-8",
    )

# 10. Keep the human-facing external-agent contract in sync.
path = "02_Architecture/external_agent_collaboration_spec.html"
text = read_text(path)
if 'merge_candidate</code></td><td>MergeSuggestions' in text and 'content.mergeMethod' not in text:
    old = '<tr><td><code>merge_candidate</code></td><td>MergeSuggestions（既存の採否・監査 <code>merge-decision-logs</code>）</td></tr>'
    new = '<tr><td><code>merge_candidate</code></td><td>MergeSuggestions（既存の採否・監査 <code>merge-decision-logs</code>）。<code>content.mergeMethod</code> は <code>near_duplicate</code> / <code>kernel_fusion</code> のいずれかを必須とし、欠落・未知値は推測せず取り込まない。</td></tr>'
    if text.count(old) != 1:
        raise SystemExit("external_agent_collaboration_spec.html: merge_candidate row anchor mismatch")
    text = text.replace(old, new, 1)
if '"mergedText": "string?"' in text and '"mergeMethod": "near_duplicate | kernel_fusion?"' not in text:
    old = '"content": { "title": "string?", "text": "string?", "mergedText": "string?" },'
    new = '"content": { "title": "string?", "text": "string?", "mergedText": "string?", "mergeMethod": "near_duplicate | kernel_fusion?" },'
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
run("git", "diff", "--cached", "--check")
run("git", "commit", "-m", "fix: mergeMethodの契約継ぎ目と永続化を閉じる")
run("git", "push", "origin", f"HEAD:{BRANCH}")
