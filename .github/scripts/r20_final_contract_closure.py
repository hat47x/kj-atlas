from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replace_text(path: str, old: str, new: str, *, count: int = 1) -> None:
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise SystemExit(f"{path}: expected {count} occurrence(s), found {actual}: {old[:100]!r}")
    p.write_text(text.replace(old, new, count), encoding="utf-8", newline="")


def replace_bytes(path: str, old: bytes, new: bytes, *, count: int = 1) -> None:
    p = ROOT / path
    data = p.read_bytes()
    actual = data.count(old)
    if actual != count:
        raise SystemExit(f"{path}: expected {count} occurrence(s), found {actual}: {old[:100]!r}")
    p.write_bytes(data.replace(old, new, count))


# External-agent merge candidates must carry an explicit method; never infer it.
replace_text(
    "03_Implement/frontend/src/import/agent_response_import.ts",
    'import { AGENT_TASK_KINDS, type AgentTaskCorrelation } from "../export/agent_task_export";\n',
    'import { AGENT_TASK_KINDS, type AgentTaskCorrelation } from "../export/agent_task_export";\nimport { isMergeMethod, type MergeMethod } from "../domain/merge_method";\n',
)
replace_text(
    "03_Implement/frontend/src/import/agent_response_import.ts",
    'export type AgentResponseProposalContent = {\n  title?: string;\n  text?: string;\n  mergedText?: string;\n};',
    'export type AgentResponseProposalContent = {\n  title?: string;\n  text?: string;\n  mergedText?: string;\n  mergeMethod?: MergeMethod;\n};',
)
replace_text(
    "03_Implement/frontend/src/import/agent_response_import.ts",
    '  return {\n    title: sanitizeString(value.title),\n    text: sanitizeString(value.text),\n    mergedText: sanitizeString(value.mergedText),\n  };',
    '  return {\n    title: sanitizeString(value.title),\n    text: sanitizeString(value.text),\n    mergedText: sanitizeString(value.mergedText),\n    mergeMethod: isMergeMethod(value.mergeMethod) ? value.mergeMethod : undefined,\n  };',
)
replace_text(
    "03_Implement/frontend/src/import/agent_response_import.ts",
    '  let patch: PatchV1 | undefined;\n  let patchHasDeleteOps = false;\n',
    '  const content = parseContent(value.content);\n  if (kind === "merge_candidate" && !content.mergeMethod) {\n    return { errors: ["proposal.merge_candidate_missing_or_invalid_merge_method"], warnings };\n  }\n\n  let patch: PatchV1 | undefined;\n  let patchHasDeleteOps = false;\n',
)
replace_text(
    "03_Implement/frontend/src/import/agent_response_import.ts",
    '    targetRef: parseTargetRef(value.targetRef),\n    content: parseContent(value.content),\n',
    '    targetRef: parseTargetRef(value.targetRef),\n    content,\n',
)

replace_text(
    "03_Implement/frontend/src/export/agent_task_export.ts",
    '    case "merge_candidates":\n      return `文脈に含まれるカードの中で、統合（マージ）できそうな組を${desiredCount}件程度、提案してください。対象範囲: ${scopeLabel}。`;\n',
    '    case "merge_candidates":\n      return `文脈に含まれるカードの中で、統合（マージ）できそうな組を${desiredCount}件程度、提案してください。対象範囲: ${scopeLabel}。近い記述を整理する場合は near_duplicate、完全な重複ではない複数カードから共通の意味核を立てる場合は kernel_fusion とし、各 merge_candidate の content.mergeMethod に必ず明示してください。`;\n',
)
replace_text(
    "03_Implement/frontend/src/export/agent_task_export.ts",
    '        content: { title: "string?", text: "string?", mergedText: "string?" },\n',
    '        content: { title: "string?", text: "string?", mergedText: "string?", mergeMethod: "near_duplicate | kernel_fusion (kind=merge_candidate のとき必須)" },\n',
)

# Preserve App.tsx CRLF bytes.
replace_bytes(
    "03_Implement/frontend/src/App.tsx",
    b'          const mergedText = review.content.mergedText ?? review.content.text;\r\n          if (cardIds.length < 2 || !mergedText) break;\r\n',
    b'          const mergedText = review.content.mergedText ?? review.content.text;\r\n          const mergeMethod = review.content.mergeMethod;\r\n          if (cardIds.length < 2 || !mergedText || !mergeMethod) break;\r\n',
)
replace_bytes(
    "03_Implement/frontend/src/App.tsx",
    b'              groupId: `agent-response-${review.proposalId}`,\r\n              targetCardId,\r\n',
    b'              groupId: `agent-response-${review.proposalId}`,\r\n              mergeMethod,\r\n              targetCardId,\r\n',
)

# Every NEW decision producer must supply the method.
replace_text(
    "03_Implement/frontend/src/domain/stream_b_contract_handoff.ts",
    'import { appendMergeSuggestionDecision, type MergeSuggestionDecision } from "./merge_suggestion_decisions";\n',
    'import { appendMergeSuggestionDecision, type MergeSuggestionDecision } from "./merge_suggestion_decisions";\nimport type { MergeMethod } from "./merge_method";\n',
)
replace_text(
    "03_Implement/frontend/src/domain/stream_b_contract_handoff.ts",
    'type ValidateDecisionLogInput = {\n  groupId: string;\n  decision: MergeSuggestionDecision;\n',
    'type ValidateDecisionLogInput = {\n  groupId: string;\n  mergeMethod: MergeMethod;\n  decision: MergeSuggestionDecision;\n',
)
replace_text(
    "03_Implement/frontend/src/domain/stream_b_contract_handoff.ts",
    '    entry?.snapshotVersion === STREAM_B_CONTRACTS.decisionLog.contractId &&\n    entry.action === input.decision &&\n',
    '    entry?.snapshotVersion === STREAM_B_CONTRACTS.decisionLog.contractId &&\n    entry.mergeMethod === input.mergeMethod &&\n    entry.action === input.decision &&\n',
)
replace_text(
    "03_Implement/frontend/src/domain/merge_suggestion_apply.test.ts",
    '      groupId: "g1",\n      decision,\n',
    '      groupId: "g1",\n      mergeMethod: "near_duplicate",\n      decision,\n',
)
replace_text(
    "03_Implement/frontend/src/domain/stream_b_mock_validation.test.ts",
    '          groupId: "g1",\n          decision: action,\n',
    '          groupId: "g1",\n          mergeMethod: "near_duplicate",\n          decision: action,\n',
)
replace_text(
    "03_Implement/frontend/src/domain/stream_b_contract_handoff.test.ts",
    '        groupId: "g1",\n        decision: "partial",\n',
    '        groupId: "g1",\n        mergeMethod: "near_duplicate",\n        decision: "partial",\n',
)
replace_bytes(
    "03_Implement/frontend/src/ui/MergeSuggestionsPanel.test.ts",
    b'        groupId: "heuristic-risk-a-b",\r\n',
    b'        groupId: "heuristic-risk-a-b",\r\n        mergeMethod: "near_duplicate",\r\n',
)

# Persisted DocumentV1: old entries may omit the method, but known new values must round-trip.
replace_bytes(
    "03_Implement/frontend/src/domain/types.ts",
    b'  rationale?: string;\r\n  /**\r\n   * R3-tier-1',
    b'  rationale?: string;\r\n  mergeMethod?: "near_duplicate" | "kernel_fusion";\r\n  /**\r\n   * R3-tier-1',
)
replace_text(
    "03_Implement/frontend/src/domain/validate_doc.ts",
    '"snapshotVersion", "rationale", "representativeCardId",',
    '"snapshotVersion", "rationale", "mergeMethod", "representativeCardId",',
)
replace_text(
    "03_Implement/frontend/src/domain/validate_doc.ts",
    '  if (item.rationale !== undefined && typeof item.rationale !== "string") {\n    errors.push(`${path}.rationale: must be a string when provided`);\n    valid = false;\n  }\n  if (item.representativeCardId !== undefined',
    '  if (item.rationale !== undefined && typeof item.rationale !== "string") {\n    errors.push(`${path}.rationale: must be a string when provided`);\n    valid = false;\n  }\n  if (item.mergeMethod !== undefined && item.mergeMethod !== "near_duplicate" && item.mergeMethod !== "kernel_fusion") {\n    errors.push(`${path}.mergeMethod: must be \'near_duplicate\' | \'kernel_fusion\' when provided`);\n    valid = false;\n  }\n  if (item.representativeCardId !== undefined',
)
replace_text(
    "03_Implement/frontend/src/domain/validate.ts",
    '      ...(typeof item.rationale === "string" ? { rationale: item.rationale } : {}),\n      ...(typeof item.representativeCardId === "string" ? { representativeCardId: item.representativeCardId } : {}),',
    '      ...(typeof item.rationale === "string" ? { rationale: item.rationale } : {}),\n      ...(item.mergeMethod === "near_duplicate" || item.mergeMethod === "kernel_fusion"\n        ? { mergeMethod: item.mergeMethod }\n        : {}),\n      ...(typeof item.representativeCardId === "string" ? { representativeCardId: item.representativeCardId } : {}),',
)

replace_text(
    "03_Implement/frontend/src/domain/validate_doc.test.ts",
    '  it("rejects merge suggestion decisions with invalid status", () => {',
    '''  it("preserves known merge methods, accepts legacy omissions, and rejects unknown methods", () => {
    const known = validateDocumentV1Strict({
      ...validDocument,
      mergeSuggestionDecisions: [{
        id: "decision-method", groupId: "merge-a-b", decision: "accept", decidedAt: now,
        cardIds: ["c1", "c2"], mergedTextDraft: "A", editedText: "A", mergeMethod: "kernel_fusion",
      }],
    });
    expect(known.ok).toBe(true);
    if (known.ok) expect(known.document.mergeSuggestionDecisions?.[0]?.mergeMethod).toBe("kernel_fusion");

    const legacy = validateDocumentV1Strict({
      ...validDocument,
      mergeSuggestionDecisions: [{
        id: "decision-legacy", groupId: "merge-a-b", decision: "defer", decidedAt: now,
        cardIds: ["c1", "c2"], mergedTextDraft: "A", editedText: "A",
      }],
    });
    expect(legacy.ok).toBe(true);

    const unknown = validateDocumentV1Strict({
      ...validDocument,
      mergeSuggestionDecisions: [{
        id: "decision-unknown", groupId: "merge-a-b", decision: "accept", decidedAt: now,
        cardIds: ["c1", "c2"], mergedTextDraft: "A", editedText: "A", mergeMethod: "semantic_fusion",
      }],
    });
    expect(unknown.ok).toBe(false);
    if (!unknown.ok) expect(unknown.errors).toContain(
      "mergeSuggestionDecisions[0].mergeMethod: must be 'near_duplicate' | 'kernel_fusion' when provided",
    );
  });

  it("rejects merge suggestion decisions with invalid status", () => {''',
)
replace_text(
    "03_Implement/frontend/src/domain/validate.test.ts",
    'describe("validateImportedDocument", () => {\n',
    '''describe("validateImportedDocument", () => {
  it("preserves a known mergeMethod and does not infer one for legacy decisions", () => {
    const result = validateImportedDocument({
      version: 1,
      id: "doc_merge_method",
      createdAt: "2026-09-04T00:00:00.000Z",
      updatedAt: "2026-09-04T00:00:00.000Z",
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [{ id: "c1", text: "A", x: 0, y: 0 }],
      edges: [], islands: [],
      mergeSuggestionDecisions: [
        { id: "d1", groupId: "g1", decision: "accept", decidedAt: "2026-09-04T00:01:00.000Z", cardIds: ["c1", "c2"], mergedTextDraft: "A", editedText: "A", mergeMethod: "near_duplicate" },
        { id: "d2", groupId: "g2", decision: "defer", decidedAt: "2026-09-04T00:02:00.000Z", cardIds: ["c1", "c2"], mergedTextDraft: "A", editedText: "A" },
      ],
    });
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.document.mergeSuggestionDecisions?.[0]?.mergeMethod).toBe("near_duplicate");
    expect(result.document.mergeSuggestionDecisions?.[1]?.mergeMethod).toBeUndefined();
  });
''',
)

# External-agent regressions.
replace_text(
    "03_Implement/frontend/src/import/agent_response_import.test.ts",
    '  it("rejects an unsupported schemaVersion", () => {',
    '''  it("requires an explicit known mergeMethod for merge_candidate proposals", () => {
    for (const mergeMethod of ["near_duplicate", "kernel_fusion"] as const) {
      const proposal = { proposalId: `merge-${mergeMethod}`, kind: "merge_candidate", targetRef: { cardIds: ["c1", "c2"] }, content: { mergedText: "統合候補", mergeMethod }, rationale: "統合方式を明示する" };
      const result = parseAgentResponse(buildValidResponseJson({ proposals: [proposal] }), "strict");
      expect(result.ok).toBe(true);
      if (result.ok) expect(result.response.proposals[0]?.content.mergeMethod).toBe(mergeMethod);
    }
  });

  it("does not guess a missing or unknown mergeMethod for merge_candidate proposals", () => {
    for (const content of [{ mergedText: "統合候補" }, { mergedText: "統合候補", mergeMethod: "unknown_method" }]) {
      const proposal = { proposalId: "merge-invalid", kind: "merge_candidate", targetRef: { cardIds: ["c1", "c2"] }, content, rationale: "方式が不正" };
      const lenient = parseAgentResponse(buildValidResponseJson({ proposals: [proposal] }), "lenient");
      expect(lenient.ok).toBe(true);
      if (lenient.ok) {
        expect(lenient.response.proposals).toHaveLength(0);
        expect(lenient.warnings.some((warning) => warning.includes("merge_candidate_missing_or_invalid_merge_method"))).toBe(true);
      }
      const strict = parseAgentResponse(buildValidResponseJson({ proposals: [proposal] }), "strict");
      expect(strict.ok).toBe(false);
      if (!strict.ok) expect(strict.errors[0]).toContain("merge_candidate_missing_or_invalid_merge_method");
    }
  });

  it("rejects an unsupported schemaVersion", () => {''',
)
replace_text(
    "03_Implement/frontend/src/export/agent_task_export.test.ts",
    '    expect(output.taskSheetMd).toContain(output.correlation.bundleHash);\n    expect(output.taskJson).toBe(JSON.stringify(output.correlation, null, 2));\n',
    '    expect(output.taskSheetMd).toContain(output.correlation.bundleHash);\n    expect(output.taskSheetMd).toContain("content.mergeMethod に必ず明示してください");\n    expect(output.taskSheetMd).toContain("near_duplicate | kernel_fusion (kind=merge_candidate のとき必須)");\n    expect(output.taskJson).toBe(JSON.stringify(output.correlation, null, 2));\n',
)
replace_text(
    "03_Implement/frontend/tests/fixtures/agent_task/agent_task_island_titles.md",
    '        "mergedText": "string?"\n',
    '        "mergedText": "string?",\n        "mergeMethod": "near_duplicate | kernel_fusion (kind=merge_candidate のとき必須)"\n',
)
replace_text(
    "02_Architecture/external_agent_collaboration_spec.html",
    '      "content": { "title": "string?", "text": "string?", "mergedText": "string?" },\n',
    '      "content": { "title": "string?", "text": "string?", "mergedText": "string?", "mergeMethod": "near_duplicate | kernel_fusion?" },\n',
)
replace_text(
    "02_Architecture/external_agent_collaboration_spec.html",
    '<tr><td><code>merge_candidate</code></td><td>MergeSuggestions（既存の採否・監査 <code>merge-decision-logs</code>）</td></tr>',
    '<tr><td><code>merge_candidate</code></td><td>MergeSuggestions（既存の採否・監査 <code>merge-decision-logs</code>）。<code>content.mergeMethod</code> は <code>near_duplicate</code> / <code>kernel_fusion</code> のいずれかを必須とし、欠落・未知値は推測せず取り込まない。</td></tr>',
)

print("R20 final contract closure patch applied")
