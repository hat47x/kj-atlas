from pathlib import Path
import json

ROOT = Path(".")


def read(path: str) -> str:
    with open(ROOT / path, "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def write(path: str, text: str) -> None:
    with open(ROOT / path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def adapt(text: str, newline: str) -> str:
    return text.replace("\n", newline)


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    newline = "\r\n" if "\r\n" in text else "\n"
    old_native = adapt(old, newline)
    new_native = adapt(new, newline)
    count = text.count(old_native)
    if count != 1:
        raise SystemExit(f"{path}: expected one anchor, found {count}: {old!r}")
    write(path, text.replace(old_native, new_native, 1))


def replace_in_block(path: str, start_marker: str, end_marker: str, old: str, new: str) -> None:
    text = read(path)
    newline = "\r\n" if "\r\n" in text else "\n"
    start = text.index(adapt(start_marker, newline))
    end = text.index(adapt(end_marker, newline), start)
    block = text[start:end]
    old_native = adapt(old, newline)
    new_native = adapt(new, newline)
    count = block.count(old_native)
    if count != 1:
        raise SystemExit(f"{path}: expected one block anchor, found {count}: {old!r}")
    write(path, text[:start] + block.replace(old_native, new_native, 1) + text[end:])


def append_json_entries(path: str, entries: list[tuple[str, str]]) -> None:
    text = read(path)
    newline = "\r\n" if "\r\n" in text else "\n"
    for key, _ in entries:
        if f'"{key}"' in text:
            raise SystemExit(f"{path}: translation key already exists: {key}")
    closing_index = text.rfind(newline + "}")
    if closing_index < 0:
        raise SystemExit(f"{path}: JSON closing brace not found")
    before = text[:closing_index]
    after = text[closing_index:]
    stripped = before.rstrip()
    whitespace = before[len(stripped):]
    separator = "" if stripped.endswith(",") else ","
    lines = []
    for index, (key, value) in enumerate(entries):
        comma = "," if index < len(entries) - 1 else ""
        lines.append(f"  {json.dumps(key, ensure_ascii=False)}: {json.dumps(value, ensure_ascii=False)}{comma}")
    write(path, stripped + separator + newline + newline.join(lines) + whitespace + after)


# ---------------------------------------------------------------------------
# Backend: new provider proposals require an explicit method. Historical
# Document decisions keep the field optional for backward compatibility.
# ---------------------------------------------------------------------------
replace_in_block(
    "03_Implement/backend/src/kj_atlas_api/models.py",
    "class MergeSuggestionDecision(BaseModel):\n",
    "\n\nclass MergeDecisionRecord(BaseModel):\n",
    "    rationale: str | None = Field(default=None, exclude_if=lambda value: value is None)\n",
    "    rationale: str | None = Field(default=None, exclude_if=lambda value: value is None)\n"
    "    mergeMethod: Literal[\"near_duplicate\", \"kernel_fusion\"] | None = Field(\n"
    "        default=None, exclude_if=lambda value: value is None\n"
    "    )\n",
)
replace_in_block(
    "03_Implement/backend/src/kj_atlas_api/models.py",
    "class MergeSuggestion(BaseModel):\n",
    "\n\nclass SuggestMergesRequest(BaseModel):\n",
    "    mergedTextDraft: str = Field(max_length=MERGE_DRAFT_MAX_LENGTH)\n    rationale: str | None = None\n",
    "    mergedTextDraft: str = Field(max_length=MERGE_DRAFT_MAX_LENGTH)\n"
    "    mergeMethod: Literal[\"near_duplicate\", \"kernel_fusion\"]\n"
    "    rationale: str | None = None\n",
)
replace_once(
    "03_Implement/backend/src/kj_atlas_api/routes/ai.py",
    "            \"Use this exact schema:\",\n"
    "            '{\"suggestions\":[{\"groupId\":string,\"cardIds\":[string,...],\"mergedTextDraft\":string,\"rationale\":string?}]}',\n"
    "            \"Each suggestion must include at least 2 cardIds.\",\n",
    "            \"Use this exact schema:\",\n"
    "            '{\"suggestions\":[{\"groupId\":string,\"cardIds\":[string,...],\"mergedTextDraft\":string,\"mergeMethod\":\"near_duplicate\"|\"kernel_fusion\",\"rationale\":string?}]}',\n"
    "            \"mergeMethod is required: use near_duplicate for 04-step-like consolidation and kernel_fusion for kernel-fusion-style integration.\",\n"
    "            \"Each suggestion must include at least 2 cardIds.\",\n",
)

# Backend tests: normal fixtures identify a method, and missing/unknown values
# are rejected by the same production Pydantic contract used by the route.
replace_once(
    "03_Implement/backend/tests/test_ai_merge_semantics.py",
    '                    "mergedTextDraft": f"merged {group_id}",\n                    "rationale": "candidate only",\n',
    '                    "mergedTextDraft": f"merged {group_id}",\n'
    '                    "mergeMethod": "near_duplicate",\n'
    '                    "rationale": "candidate only",\n',
)
replace_once(
    "03_Implement/backend/tests/test_ai_merge_semantics.py",
    '    assert "Similarity alone is not enough" in prompt\n',
    '    assert "Similarity alone is not enough" in prompt\n'
    '    assert "mergeMethod" in prompt\n'
    '    assert "near_duplicate" in prompt\n'
    '    assert "kernel_fusion" in prompt\n',
)
semantics_path = "03_Implement/backend/tests/test_ai_merge_semantics.py"
semantics = read(semantics_path)
newline = "\r\n" if "\r\n" in semantics else "\n"
addition = adapt('''

def test_merge_parser_rejects_missing_merge_method() -> None:
    payload = _payload([_card("c1", "alpha"), _card("c2", "alpha again")])
    raw = '{"suggestions":[{"groupId":"m1","cardIds":["c1","c2"],"mergedTextDraft":"draft"}]}'

    with pytest.raises(HTTPException) as exc_info:
        _parse_merge_suggestions(raw, payload)

    assert exc_info.value.status_code == 422


def test_merge_parser_rejects_unknown_merge_method() -> None:
    payload = _payload([_card("c1", "alpha"), _card("c2", "alpha again")])
    raw = '{"suggestions":[{"groupId":"m1","cardIds":["c1","c2"],"mergedTextDraft":"draft","mergeMethod":"summarize"}]}'

    with pytest.raises(HTTPException) as exc_info:
        _parse_merge_suggestions(raw, payload)

    assert exc_info.value.status_code == 422
''', newline)
if "test_merge_parser_rejects_missing_merge_method" in semantics:
    raise SystemExit("backend merge method semantic tests already exist")
write(semantics_path, semantics.rstrip("\r\n") + addition + newline)

replace_once(
    "03_Implement/backend/tests/test_ai_merge_ir.py",
    '    assert "person@example.com" not in prompt\n',
    '    assert "person@example.com" not in prompt\n'
    '    assert "mergeMethod" in prompt\n'
    '    assert "near_duplicate" in prompt\n'
    '    assert "kernel_fusion" in prompt\n',
)
replace_once(
    "03_Implement/backend/tests/test_ai_merge_ir.py",
    "            '{\"suggestions\":[{\"groupId\":\"m1\",\"cardIds\":[\"c1\",\"c4\"],\"mergedTextDraft\":\"draft\"}]}',\n",
    "            '{\"suggestions\":[{\"groupId\":\"m1\",\"cardIds\":[\"c1\",\"c4\"],\"mergedTextDraft\":\"draft\",\"mergeMethod\":\"near_duplicate\"}]}',\n",
)

# ---------------------------------------------------------------------------
# Frontend common vocabulary and strict new-proposal decoder.
# ---------------------------------------------------------------------------
method_path = ROOT / "03_Implement/frontend/src/domain/merge_method.ts"
if method_path.exists():
    raise SystemExit("merge_method.ts already exists")
method_path.write_text(
    '''export const MERGE_METHODS = ["near_duplicate", "kernel_fusion"] as const;\n\n'''
    '''export type MergeMethod = (typeof MERGE_METHODS)[number];\n\n'''
    '''export function isMergeMethod(value: unknown): value is MergeMethod {\n'''
    '''  return typeof value === "string" && MERGE_METHODS.includes(value as MergeMethod);\n'''
    '''}\n''',
    encoding="utf-8",
)

replace_once(
    "03_Implement/frontend/src/api/client.ts",
    'import type { Card, Document, DocumentV1, Island, KnownEdgeType } from "../domain/types";\n',
    'import type { Card, Document, DocumentV1, Island, KnownEdgeType } from "../domain/types";\n'
    'import { isMergeMethod, type MergeMethod } from "../domain/merge_method";\n',
)
replace_once(
    "03_Implement/frontend/src/api/client.ts",
    'export type MergeSuggestion = {\n  groupId: string;\n  cardIds: string[];\n  mergedTextDraft: string;\n  rationale?: string;\n};\n',
    'export type MergeSuggestion = {\n'
    '  groupId: string;\n'
    '  cardIds: string[];\n'
    '  mergedTextDraft: string;\n'
    '  mergeMethod: MergeMethod;\n'
    '  rationale?: string;\n'
    '};\n',
)
replace_once(
    "03_Implement/frontend/src/api/client.ts",
    '    && isNonEmptyString(suggestion.mergedTextDraft)\n    && (suggestion.rationale === undefined || isNonEmptyString(suggestion.rationale))\n',
    '    && isNonEmptyString(suggestion.mergedTextDraft)\n'
    '    && isMergeMethod(suggestion.mergeMethod)\n'
    '    && (suggestion.rationale === undefined || isNonEmptyString(suggestion.rationale))\n',
)

replace_once(
    "03_Implement/frontend/src/domain/merge_candidates.ts",
    '        cardIds,\n        mergedTextDraft,\n        rationale: `heuristic:${group.reason}`,\n',
    '        cardIds,\n'
    '        mergedTextDraft,\n'
    '        mergeMethod: "near_duplicate",\n'
    '        rationale: `heuristic:${group.reason}`,\n',
)
replace_once(
    "03_Implement/frontend/src/domain/merge_candidates.test.ts",
    '    expect(result[0]?.mergedTextDraft).toBe("Needs   follow-up");\n',
    '    expect(result[0]?.mergedTextDraft).toBe("Needs   follow-up");\n'
    '    expect(result[0]?.mergeMethod).toBe("near_duplicate");\n',
)

# Historical decision persistence may omit method; new append calls require it.
replace_once(
    "03_Implement/frontend/src/domain/types.ts",
    'import type { InquiryBundleV1 } from "./inquiry_bundle";\n',
    'import type { InquiryBundleV1 } from "./inquiry_bundle";\n'
    'import type { MergeMethod } from "./merge_method";\n',
)
replace_in_block(
    "03_Implement/frontend/src/domain/types.ts",
    "export type MergeSuggestionDecisionEntry = {\n",
    "\n};\n\nexport type PatchApplyStats",
    "  rationale?: string;\n",
    "  rationale?: string;\n  mergeMethod?: MergeMethod;\n",
)
replace_once(
    "03_Implement/frontend/src/domain/merge_suggestion_decisions.ts",
    'import type { DocumentV1 } from "./types";\n',
    'import type { DocumentV1 } from "./types";\nimport type { MergeMethod } from "./merge_method";\n',
)
replace_in_block(
    "03_Implement/frontend/src/domain/merge_suggestion_decisions.ts",
    "export type MergeSuggestionDecisionEntry = {\n",
    "\n};\n\ntype AppendMergeSuggestionDecisionInput",
    "  rationale?: string;\n",
    "  rationale?: string;\n  mergeMethod?: MergeMethod;\n",
)
replace_in_block(
    "03_Implement/frontend/src/domain/merge_suggestion_decisions.ts",
    "type AppendMergeSuggestionDecisionInput = {\n",
    "\n};\n\nfunction sortCardIds",
    "  rationale?: string;\n",
    "  rationale?: string;\n  mergeMethod: MergeMethod;\n",
)
replace_once(
    "03_Implement/frontend/src/domain/merge_suggestion_decisions.ts",
    '    rationale: input.rationale,\n    representativeCardId: originTrace.representativeCardId,\n',
    '    rationale: input.rationale,\n'
    '    mergeMethod: input.mergeMethod,\n'
    '    representativeCardId: originTrace.representativeCardId,\n',
)

# App records the method with the persistent decision snapshot. The short-lived
# audit event intentionally remains unchanged per R19.
app_path = "03_Implement/frontend/src/App.tsx"
app = read(app_path)
newline = "\r\n" if "\r\n" in app else "\n"
start = app.index("const nextDocument = appendMergeSuggestionDecision(document, {")
end = app.index(adapt("      });\n", newline), start) + len(adapt("      });\n", newline))
block = app[start:end]
anchor = adapt("        rationale: suggestion.rationale,\n", newline)
if block.count(anchor) != 1:
    raise SystemExit("App.tsx: decision rationale anchor mismatch")
block = block.replace(anchor, anchor + adapt("        mergeMethod: suggestion.mergeMethod,\n", newline), 1)
write(app_path, app[:start] + block + app[end:])

# Method is visible beside, not encoded into, rationale or human reason.
panel_path = "03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx"
replace_once(
    panel_path,
    "function representativeResolvedLabel(\n",
    'function mergeMethodLabel(method: MergeSuggestion["mergeMethod"]): string {\n'
    '  return method === "near_duplicate"\n'
    '    ? t("merge_suggestions.method.near_duplicate")\n'
    '    : t("merge_suggestions.method.kernel_fusion");\n'
    '}\n\n'
    "function representativeResolvedLabel(\n",
)
replace_once(
    panel_path,
    '        const isAccepted = suggestion.latestDecision === "accept";\n'
    '        const isApplied = isAccepted && (suggestion.representativeResolvedBy === "repOf" || suggestion.representativeResolvedBy === "mergedIntoCardId");\n',
    '        const isAccepted = suggestion.latestDecision === "accept";\n'
    '        const isApplied = isAccepted && (suggestion.representativeResolvedBy === "repOf" || suggestion.representativeResolvedBy === "mergedIntoCardId");\n'
    '        const methodLabel = mergeMethodLabel(suggestion.mergeMethod);\n',
)
replace_once(
    panel_path,
    '          {suggestion.rationale ? (\n'
    '            <div style={{ fontSize: 12, color: "#475569", marginBottom: 6 }}>{t("merge_suggestions.rationale")}: {suggestion.rationale}</div>\n'
    '          ) : null}\n',
    '          <div style={{ fontSize: 12, color: "#475569", marginBottom: 6 }}>\n'
    '            {t("merge_suggestions.method_label", { method: methodLabel })}\n'
    '          </div>\n'
    '          {suggestion.rationale ? (\n'
    '            <div style={{ fontSize: 12, color: "#475569", marginBottom: 6 }}>{t("merge_suggestions.rationale")}: {suggestion.rationale}</div>\n'
    '          ) : null}\n',
)
append_json_entries(
    "03_Implement/frontend/src/i18n/locales/ja.json",
    [
        ("merge_suggestions.method_label", "統合方法: {method}"),
        ("merge_suggestions.method.near_duplicate", "近接カードの整理（04ステップ型）"),
        ("merge_suggestions.method.kernel_fusion", "意味核の統合（核融合法型）"),
    ],
)
append_json_entries(
    "03_Implement/frontend/src/i18n/locales/en.json",
    [
        ("merge_suggestions.method_label", "Integration method: {method}"),
        ("merge_suggestions.method.near_duplicate", "Near-duplicate consolidation (04-step-like)"),
        ("merge_suggestions.method.kernel_fusion", "Meaning-kernel integration (kernel-fusion-style)"),
    ],
)

# ---------------------------------------------------------------------------
# Frontend tests and persistence evidence.
# ---------------------------------------------------------------------------
# Valid remote response fixture and expectation.
replace_once(
    "03_Implement/frontend/src/api/client.test.ts",
    '              mergedTextDraft: "Risk mitigation",\n              rationale: "Both cards express the same core concern.",\n',
    '              mergedTextDraft: "Risk mitigation",\n'
    '              mergeMethod: "kernel_fusion",\n'
    '              rationale: "Both cards express the same core concern.",\n',
)
replace_once(
    "03_Implement/frontend/src/api/client.test.ts",
    '        mergedTextDraft: "Risk mitigation",\n        rationale: "Both cards express the same core concern.",\n',
    '        mergedTextDraft: "Risk mitigation",\n'
    '        mergeMethod: "kernel_fusion",\n'
    '        rationale: "Both cards express the same core concern.",\n',
)
# Order-preservation fixture has two minimal suggestions.
client_test_path = "03_Implement/frontend/src/api/client.test.ts"
client_test = read(client_test_path)
client_test = client_test.replace(
    '{ groupId: "m1", cardIds: ["c1", "c2"], mergedTextDraft: "Risk mitigation" },',
    '{ groupId: "m1", cardIds: ["c1", "c2"], mergedTextDraft: "Risk mitigation", mergeMethod: "near_duplicate" },',
)
client_test = client_test.replace(
    '{ groupId: "m2", cardIds: ["c2", "c1"], mergedTextDraft: "Mitigate risk" },',
    '{ groupId: "m2", cardIds: ["c2", "c1"], mergedTextDraft: "Mitigate risk", mergeMethod: "kernel_fusion" },',
)
# Make fewer-than-two-cards fixture fail for its intended reason, not missing method.
client_test = client_test.replace(
    '{ groupId: "m1", cardIds: ["c1"], mergedTextDraft: "Risk mitigation" }',
    '{ groupId: "m1", cardIds: ["c1"], mergedTextDraft: "Risk mitigation", mergeMethod: "near_duplicate" }',
)
if 'it("fails fast when mergeMethod is missing"' not in client_test:
    newline = "\r\n" if "\r\n" in client_test else "\n"
    marker = adapt('  it("fails fast when a core backend field is missing", async () => {\n', newline)
    index = client_test.index(marker)
    new_tests = adapt('''  it("fails fast when mergeMethod is missing", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          suggestions: [{ groupId: "m1", cardIds: ["c1", "c2"], mergedTextDraft: "Risk mitigation" }],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );

    await expect(suggestMerges(createDocument())).rejects.toMatchObject({
      message: "Invalid merge suggestions contract payload",
      status: 500,
    });
  });

  it("fails fast when mergeMethod is unknown", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          suggestions: [{
            groupId: "m1",
            cardIds: ["c1", "c2"],
            mergedTextDraft: "Risk mitigation",
            mergeMethod: "summarize",
          }],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );

    await expect(suggestMerges(createDocument())).rejects.toMatchObject({
      message: "Invalid merge suggestions contract payload",
      status: 500,
    });
  });

''', newline)
    client_test = client_test[:index] + new_tests + client_test[index:]
write(client_test_path, client_test)

# Decision tests: every newly appended decision must specify a method. Historical
# literal fixtures remain allowed to omit it.
decision_test_path = "03_Implement/frontend/src/domain/merge_suggestion_decisions.test.ts"
decision_test = read(decision_test_path)
newline = "\r\n" if "\r\n" in decision_test else "\n"
# Scope only call-object occurrences by inserting after a 'decision:' line when
# the next nearby fields include cardIds and no mergeMethod yet.
lines = decision_test.splitlines(keepends=True)
result_lines = []
in_append = False
brace_depth = 0
for line in lines:
    if "appendMergeSuggestionDecision(" in line:
        in_append = True
        brace_depth = 0
    if in_append:
        brace_depth += line.count("(") - line.count(")")
    result_lines.append(line)
    if in_append and line.lstrip().startswith("decision:"):
        indent = line[: len(line) - len(line.lstrip())]
        result_lines.append(f'{indent}mergeMethod: "near_duplicate",{newline}')
    if in_append and brace_depth <= 0 and ")" in line:
        in_append = False
write(decision_test_path, "".join(result_lines))
# One deterministic-ordering test explicitly proves kernel_fusion survives.
replace_once(
    decision_test_path,
    '        decision: "accept",\n        mergeMethod: "near_duplicate",\n        cardIds: ["c2", "c1", "c2"],\n',
    '        decision: "accept",\n        mergeMethod: "kernel_fusion",\n        cardIds: ["c2", "c1", "c2"],\n',
)
replace_once(
    decision_test_path,
    '        rationale: undefined,\n        representativeCardId: "c1",\n',
    '        rationale: undefined,\n        mergeMethod: "kernel_fusion",\n        representativeCardId: "c1",\n',
)

# Apply test helper records a current decision; add its method.
replace_once(
    "03_Implement/frontend/src/domain/merge_suggestion_apply.test.ts",
    '      decisionReason: "二つの記述の差を残したうえで代表表現として採用する",\n',
    '      decisionReason: "二つの記述の差を残したうえで代表表現として採用する",\n'
    '      mergeMethod: "kernel_fusion",\n',
)

# Panel fixture needs the required common proposal field and visibly renders it.
replace_once(
    "03_Implement/frontend/src/ui/MergeSuggestionsPanel.test.ts",
    '        mergedTextDraft: "Risk mitigation",\n        editedText: "Risk mitigation",\n',
    '        mergedTextDraft: "Risk mitigation",\n'
    '        mergeMethod: "near_duplicate" as const,\n'
    '        editedText: "Risk mitigation",\n',
)
replace_once(
    "03_Implement/frontend/src/ui/MergeSuggestionsPanel.test.ts",
    '    expect(html).toContain(`${t("merge_suggestions.rationale")}: heuristic:normalized-text`);\n',
    '    expect(html).toContain(t("merge_suggestions.method_label", { method: t("merge_suggestions.method.near_duplicate") }));\n'
    '    expect(html).toContain(`${t("merge_suggestions.rationale")}: heuristic:normalized-text`);\n',
)

# Existing save/reload E2E uses deterministic fallback, therefore method must
# persist into the Document decision snapshot as near_duplicate.
replace_once(
    "03_Implement/frontend/e2e/merge_suggestion_apply_persistence.spec.ts",
    '  expect(decision).toBeTruthy();\n  expect(decision.representativeCardId).toBe(representative.id);\n',
    '  expect(decision).toBeTruthy();\n'
    '  expect(decision.mergeMethod).toBe("near_duplicate");\n'
    '  expect(decision.representativeCardId).toBe(representative.id);\n',
)

# API docs: correct the Card.sources meaning and document R19 method contract.
api_path = "02_Architecture/api.md"
replace_once(
    api_path,
    '- `claimType`、全島所属、`canonicalId` / `repOf`、出典の同一性は `suggest-merges` 専用の構造化文脈として重ねる。\n'
    '- `sources` の生値はproviderへ送らず、同じ出典を共有しているかを判別できる文書内の不透明参照へ変換する。\n',
    '- `claimType`、全島所属、`canonicalId` / `repOf` / `sources` のmerge系譜は `suggest-merges` 専用の構造化文脈として重ねる。\n'
    '- `Card.sources` はmerge元カードIDとして保持する。外部元記録を示す `Card.meta.source` はproviderへ送らない。\n',
)
replace_once(
    api_path,
    'LLM応答は信頼境界の外側として扱う。未知ID・重複ID・2件未満・件数上限に加え、hold、既merge、明示的な `negate`、`type=contradicts` のevidence、異なる既知 `claimType`、同じカードを複数候補へ含める競合提案を決定論的に拒否する。\n',
    'LLM応答は信頼境界の外側として扱う。未知ID・重複ID・2件未満・件数上限に加え、hold、既merge、明示的な `negate`、`type=contradicts` のevidence、異なる既知 `claimType`、同じカードを複数候補へ含める競合提案を決定論的に拒否する。\n\n'
    '新しくproviderから生成する各提案は `mergeMethod: "near_duplicate" | "kernel_fusion"` を必須とする。`near_duplicate` は04ステップ型の近接整理、`kernel_fusion` は核融合法型の意味核統合を表す。決定論的ローカルfallbackは実際の処理内容に合わせて `near_duplicate` を付与する。UIでは方式をAIの `rationale` と人間の判断理由とは別に表示し、新しく記録するDocument decision snapshotへ保存する。保存済みの旧decisionでは `mergeMethod` 欠落を許容し、方式を推測補完しない。短期 `MergeDecisionAuditEvent` への重複保存は行わない。\n',
)

print("R19 mergeMethod patch applied")
