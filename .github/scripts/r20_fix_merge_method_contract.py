from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replace_bytes(path: str, old: bytes, new: bytes, *, count: int = 1) -> None:
    target = ROOT / path
    data = target.read_bytes()
    actual = data.count(old)
    if actual != count:
        raise SystemExit(f"{path}: expected {count} occurrence(s), found {actual}")
    target.write_bytes(data.replace(old, new, count))


def replace_text(path: str, old: str, new: str, *, count: int = 1) -> None:
    target = ROOT / path
    data = target.read_text(encoding="utf-8")
    actual = data.count(old)
    if actual != count:
        raise SystemExit(f"{path}: expected {count} occurrence(s), found {actual}")
    target.write_text(data.replace(old, new, count), encoding="utf-8")


# 1) Persisted DocumentV1 type: old entries may omit mergeMethod, new entries may carry only the two R20 values.
replace_bytes(
    "03_Implement/frontend/src/domain/types.ts",
    b"  rationale?: string;\r\n  /**\r\n   * R3-tier-1",
    b"  rationale?: string;\r\n  mergeMethod?: \"near_duplicate\" | \"kernel_fusion\";\r\n  /**\r\n   * R3-tier-1",
)

# 2) Strict validator: allow and validate the optional persisted field.
replace_text(
    "03_Implement/frontend/src/domain/validate_doc.ts",
    '      "rationale",\n      "representativeCardId",',
    '      "rationale",\n      "mergeMethod",\n      "representativeCardId",',
)
replace_text(
    "03_Implement/frontend/src/domain/validate_doc.ts",
    '  if (item.rationale !== undefined && typeof item.rationale !== "string") {\n    errors.push(`${path}.rationale: must be a string when provided`);\n    valid = false;\n  }\n',
    '  if (item.rationale !== undefined && typeof item.rationale !== "string") {\n    errors.push(`${path}.rationale: must be a string when provided`);\n    valid = false;\n  }\n  if (\n    item.mergeMethod !== undefined\n    && item.mergeMethod !== "near_duplicate"\n    && item.mergeMethod !== "kernel_fusion"\n  ) {\n    errors.push(`${path}.mergeMethod: must be \'near_duplicate\' | \'kernel_fusion\' when provided`);\n    valid = false;\n  }\n',
)

# 3) Lenient parser used by imports/normalization: preserve a valid method and drop unknown values.
replace_text(
    "03_Implement/frontend/src/domain/validate.ts",
    '      ...(typeof item.rationale === "string" ? { rationale: item.rationale } : {}),\n      ...(typeof item.representativeCardId === "string" ? { representativeCardId: item.representativeCardId } : {}),',
    '      ...(typeof item.rationale === "string" ? { rationale: item.rationale } : {}),\n      ...(item.mergeMethod === "near_duplicate" || item.mergeMethod === "kernel_fusion"\n        ? { mergeMethod: item.mergeMethod }\n        : {}),\n      ...(typeof item.representativeCardId === "string" ? { representativeCardId: item.representativeCardId } : {}),',
)

# 4) Strict validator regressions: new values round-trip, unknown rejects, old method-less decision remains valid.
replace_text(
    "03_Implement/frontend/src/domain/validate_doc.test.ts",
    '  it("rejects merge suggestion decisions with invalid status", () => {',
    '''  it("accepts known merge methods and keeps legacy method-less decisions readable", () => {
    const withMethod = validateDocumentV1Strict({
      ...validDocument,
      mergeSuggestionDecisions: [
        {
          id: "decision-method",
          groupId: "merge-a-b",
          decision: "accept",
          decidedAt: now,
          cardIds: ["c1", "c2"],
          mergedTextDraft: "A",
          editedText: "A",
          mergeMethod: "kernel_fusion",
        },
      ],
    });
    expect(withMethod.ok).toBe(true);
    if (withMethod.ok) {
      expect(withMethod.document.mergeSuggestionDecisions?.[0]?.mergeMethod).toBe("kernel_fusion");
    }

    const legacy = validateDocumentV1Strict({
      ...validDocument,
      mergeSuggestionDecisions: [
        {
          id: "decision-legacy",
          groupId: "merge-a-b",
          decision: "defer",
          decidedAt: now,
          cardIds: ["c1", "c2"],
          mergedTextDraft: "A",
          editedText: "A",
        },
      ],
    });
    expect(legacy.ok).toBe(true);
  });

  it("rejects unknown merge methods on persisted decisions", () => {
    const result = validateDocumentV1Strict({
      ...validDocument,
      mergeSuggestionDecisions: [
        {
          id: "decision-unknown-method",
          groupId: "merge-a-b",
          decision: "accept",
          decidedAt: now,
          cardIds: ["c1", "c2"],
          mergedTextDraft: "A",
          editedText: "A",
          mergeMethod: "semantic_fusion",
        },
      ],
    });
    expect(result.ok).toBe(false);
    if (result.ok) return;
    expect(result.errors).toContain(
      "mergeSuggestionDecisions[0].mergeMethod: must be 'near_duplicate' | 'kernel_fusion' when provided"
    );
  });

  it("rejects merge suggestion decisions with invalid status", () => {''',
)

# 5) Normalizing parser regression.
replace_text(
    "03_Implement/frontend/src/domain/validate.test.ts",
    'describe("validateDocument", () => {',
    '''describe("validateDocument", () => {
  it("preserves a known mergeMethod and does not infer one for legacy decisions", () => {
    const base = {
      version: 1,
      id: "doc-merge-method",
      createdAt: "2026-09-04T00:00:00.000Z",
      updatedAt: "2026-09-04T00:00:00.000Z",
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [{ id: "c1", text: "A", x: 0, y: 0 }],
      edges: [],
      islands: [],
    };
    const parsed = validateDocument({
      ...base,
      mergeSuggestionDecisions: [
        {
          id: "d1",
          groupId: "g1",
          decision: "accept",
          decidedAt: "2026-09-04T00:01:00.000Z",
          cardIds: ["c1", "c2"],
          mergedTextDraft: "A",
          editedText: "A",
          mergeMethod: "near_duplicate",
        },
        {
          id: "d2",
          groupId: "g2",
          decision: "defer",
          decidedAt: "2026-09-04T00:02:00.000Z",
          cardIds: ["c1", "c2"],
          mergedTextDraft: "A",
          editedText: "A",
        },
      ],
    });
    expect(parsed.ok).toBe(true);
    if (!parsed.ok) return;
    expect(parsed.document.mergeSuggestionDecisions?.[0]?.mergeMethod).toBe("near_duplicate");
    expect(parsed.document.mergeSuggestionDecisions?.[1]?.mergeMethod).toBeUndefined();
  });
''',
)

# 6) Stream-B new decision generation must state the deterministic method instead of silently omitting it.
replace_text(
    "03_Implement/frontend/src/domain/stream_b_contract_handoff.ts",
    'import { appendMergeSuggestionDecision, type MergeSuggestionDecision } from "./merge_suggestion_decisions";\n',
    'import { appendMergeSuggestionDecision, type MergeSuggestionDecision } from "./merge_suggestion_decisions";\nimport type { MergeMethod } from "./merge_method";\n',
)
replace_text(
    "03_Implement/frontend/src/domain/stream_b_contract_handoff.ts",
    '  editedText: string;\n};',
    '  editedText: string;\n  mergeMethod: MergeMethod;\n};',
)

# 7) Existing fixtures that generate *new* decisions explicitly identify their deterministic near-duplicate path.
for test_path in [
    "03_Implement/frontend/src/domain/merge_suggestion_apply.test.ts",
    "03_Implement/frontend/src/domain/stream_b_mock_validation.test.ts",
]:
    target = ROOT / test_path
    text = target.read_text(encoding="utf-8")
    needle = '      editedText:'
    # Insert only into appendMergeSuggestionDecision fixture objects that are missing the new required field.
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    in_append = False
    depth = 0
    inserted_for_block = False
    for line in lines:
      if "appendMergeSuggestionDecision(" in line:
        in_append = True
        inserted_for_block = False
      if in_append and "mergeMethod:" in line:
        inserted_for_block = True
      out.append(line)
      if in_append and "editedText:" in line and not inserted_for_block:
        newline = "\r\n" if line.endswith("\r\n") else "\n"
        indent = line[: len(line) - len(line.lstrip())]
        out.append(f'{indent}mergeMethod: "near_duplicate",{newline}')
        inserted_for_block = True
      if in_append and line.lstrip().startswith("},") and inserted_for_block:
        # This is deliberately permissive; later typecheck/tests verify the exact call shape.
        in_append = False
    target.write_text("".join(out), encoding="utf-8", newline="")

# 8) General panel test fixture represents deterministic normalized-text candidates.
replace_text(
    "03_Implement/frontend/src/ui/MergeSuggestionsPanel.test.ts",
    '        mergedTextDraft: "Risk mitigation",\n        editedText: "Risk mitigation",',
    '        mergedTextDraft: "Risk mitigation",\n        mergeMethod: "near_duplicate" as const,\n        editedText: "Risk mitigation",',
)

# 9) External-agent imported merge candidates may genuinely have no method.
# Keep display draft permissive, but prevent a new persisted decision from being recorded without method.
replace_bytes(
    "03_Implement/frontend/src/App.tsx",
    b'type MergeSuggestionDraft = MergeSuggestion & {\r\n',
    b'type MergeSuggestionDraft = Omit<MergeSuggestion, "mergeMethod"> & {\r\n  mergeMethod?: MergeSuggestion["mergeMethod"];\r\n',
)
replace_bytes(
    "03_Implement/frontend/src/App.tsx",
    b'      const availableCardCount = document.cards.filter((card) => suggestion.cardIds.includes(card.id)).length;\r\n',
    b'      if (!suggestion.mergeMethod) {\r\n        setMergeSuggestionError(t("app.status.merge_suggestion.method_missing"));\r\n        return;\r\n      }\r\n\r\n      const availableCardCount = document.cards.filter((card) => suggestion.cardIds.includes(card.id)).length;\r\n',
)

# Panel accepts method-less drafts only for display/import. New normal proposals still supply it.
replace_text(
    "03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx",
    'type MergeSuggestionDraft = MergeSuggestion & {\n',
    'type MergeSuggestionDraft = Omit<MergeSuggestion, "mergeMethod"> & {\n  mergeMethod?: MergeSuggestion["mergeMethod"];\n',
)

# 10) Localized fail-closed message for method-less imported candidates.
for locale, text_value in [
    ("en", "This imported merge candidate does not record an integration method. Collect a new candidate before recording a decision."),
    ("ja", "この統合候補には統合方式が記録されていません。判断を記録する前に、候補をあらためて生成してください。"),
]:
    path = f"03_Implement/frontend/src/i18n/locales/{locale}.json"
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    anchor = '  "app.status.merge_suggestion.no_longer_applicable"'
    idx = text.find(anchor)
    if idx < 0:
        raise SystemExit(f"{path}: anchor not found")
    line_end = text.find("\n", idx)
    if line_end < 0:
        raise SystemExit(f"{path}: anchor line end not found")
    insertion = f'  "app.status.merge_suggestion.method_missing": {text_value!r},\n'.replace("'", '"')
    text = text[: line_end + 1] + insertion + text[line_end + 1 :]
    target.write_text(text, encoding="utf-8")

print("R20 mergeMethod contract correction applied")
