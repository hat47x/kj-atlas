from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

SOURCE_BRANCH = "origin/dogfood/r20-merge-method-traceability-20260904"
SOURCE_FILES = [
    "03_Implement/backend/src/kj_atlas_api/models.py",
    "03_Implement/backend/src/kj_atlas_api/routes/ai.py",
    "03_Implement/backend/tests/test_ai_merge_ir.py",
    "03_Implement/backend/tests/test_ai_merge_semantics.py",
    "03_Implement/deploy/tools/mock_local_llm.py",
    "03_Implement/frontend/src/api/client.test.ts",
    "03_Implement/frontend/src/api/client.ts",
    "03_Implement/frontend/src/domain/merge_candidates.test.ts",
    "03_Implement/frontend/src/domain/merge_candidates.ts",
    "03_Implement/frontend/src/domain/merge_method.ts",
    "03_Implement/frontend/src/domain/merge_suggestion_decisions.test.ts",
    "03_Implement/frontend/src/domain/merge_suggestion_decisions.ts",
]


def run(*args: str) -> None:
    subprocess.run(args, check=True)


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    data = target.read_bytes()
    old_bytes = old.encode("utf-8")
    new_bytes = new.encode("utf-8")
    count = data.count(old_bytes)
    if count != 1:
        raise RuntimeError(f"{path}: expected one replacement, found {count}")
    target.write_bytes(data.replace(old_bytes, new_bytes, 1))


def insert_after_once(path: str, anchor: str, addition: str) -> None:
    replace_once(path, anchor, anchor + addition)


def apply_product_changes() -> None:
    run("git", "fetch", "origin", "dogfood/r20-merge-method-traceability-20260904")
    run("git", "checkout", SOURCE_BRANCH, "--", *SOURCE_FILES)

    # DocumentV1's actual persisted decision type is independently declared in
    # domain/types.ts. Keep it backward-compatible: old decisions may omit the
    # field, while every new append requires it in merge_suggestion_decisions.ts.
    types_path = "03_Implement/frontend/src/domain/types.ts"
    types_data = Path(types_path).read_bytes()
    newline = "\r\n" if b"\r\n" in types_data[:500] else "\n"
    if b'import type { MergeMethod } from "./merge_method";' not in types_data:
        prefix = f'import type {{ MergeMethod }} from "./merge_method";{newline}{newline}'
        if not types_data.startswith(b"export type Transform"):
            raise RuntimeError("types.ts: unexpected file start")
        Path(types_path).write_bytes(prefix.encode("utf-8") + types_data)
    replace_once(
        types_path,
        f"  snapshotVersion?: string;{newline}  rationale?: string;{newline}  /**{newline}   * R3-tier-1",
        f"  snapshotVersion?: string;{newline}  rationale?: string;{newline}  /** R20: optional only for documents persisted before mergeMethod existed. */{newline}  mergeMethod?: MergeMethod;{newline}  /**{newline}   * R3-tier-1",
    )

    # Propagate the proposal's method into the durable human decision snapshot.
    app_path = "03_Implement/frontend/src/App.tsx"
    app_data = Path(app_path).read_bytes()
    app_nl = "\r\n" if b"\r\n" in app_data[:2000] else "\n"
    replace_once(
        app_path,
        f"        editedText: suggestion.editedText,{app_nl}        rationale: suggestion.rationale,{app_nl}        decisionReason: options.decisionReason,{app_nl}",
        f"        editedText: suggestion.editedText,{app_nl}        mergeMethod: suggestion.mergeMethod,{app_nl}        rationale: suggestion.rationale,{app_nl}        decisionReason: options.decisionReason,{app_nl}",
    )

    # Strict document import accepts the field only when it is one of the two
    # canonical methods, while still accepting old decisions with no field.
    validate_path = "03_Implement/frontend/src/domain/validate_doc.ts"
    insert_after_once(
        validate_path,
        'import { canUsePolygonPoints } from "./geometry/polygon_edit";\n',
        'import { isMergeMethod } from "./merge_method";\n',
    )
    replace_once(
        validate_path,
        '"note", "snapshotVersion", "rationale", "representativeCardId"',
        '"note", "snapshotVersion", "rationale", "mergeMethod", "representativeCardId"',
    )
    replace_once(
        validate_path,
        '  if (item.rationale !== undefined && typeof item.rationale !== "string") {\n    errors.push(`${path}.rationale: must be a string when provided`);\n    valid = false;\n  }\n  if (item.representativeCardId !== undefined && typeof item.representativeCardId !== "string") {',
        '  if (item.rationale !== undefined && typeof item.rationale !== "string") {\n    errors.push(`${path}.rationale: must be a string when provided`);\n    valid = false;\n  }\n  if (item.mergeMethod !== undefined && !isMergeMethod(item.mergeMethod)) {\n    errors.push(`${path}.mergeMethod: must be \'near_duplicate\' | \'kernel_fusion\' when provided`);\n    valid = false;\n  }\n  if (item.representativeCardId !== undefined && typeof item.representativeCardId !== "string") {',
    )

    # Show the model-selected integration method separately from both the AI
    # rationale and the human decision reason.
    panel_path = "03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx"
    replace_once(
        panel_path,
        'function representativeResolvedLabel(\n',
        'function mergeMethodLabel(method: MergeSuggestion["mergeMethod"]): string {\n  return method === "near_duplicate"\n    ? t("merge_suggestions.merge_method.near_duplicate")\n    : t("merge_suggestions.merge_method.kernel_fusion");\n}\n\nfunction representativeResolvedLabel(\n',
    )
    replace_once(
        panel_path,
        '          {suggestion.rationale ? (\n            <div style={{ fontSize: 12, color: "#475569", marginBottom: 6 }}>{t("merge_suggestions.rationale")}: {suggestion.rationale}</div>\n          ) : null}\n',
        '          <div style={{ fontSize: 12, color: "#475569", marginBottom: 6 }}>\n            {t("merge_suggestions.merge_method")}: {mergeMethodLabel(suggestion.mergeMethod)}\n          </div>\n          {suggestion.rationale ? (\n            <div style={{ fontSize: 12, color: "#475569", marginBottom: 6 }}>{t("merge_suggestions.rationale")}: {suggestion.rationale}</div>\n          ) : null}\n',
    )

    # i18n labels stay semantic rather than exposing protocol codes to reviewers.
    for path, rationale, insertion in [
        (
            "03_Implement/frontend/src/i18n/locales/ja.json",
            '  "merge_suggestions.rationale": "理由",\n',
            '  "merge_suggestions.merge_method": "統合方法",\n'
            '  "merge_suggestions.merge_method.near_duplicate": "近接カードの整理（04ステップ型）",\n'
            '  "merge_suggestions.merge_method.kernel_fusion": "意味核の統合（核融合法型）",\n',
        ),
        (
            "03_Implement/frontend/src/i18n/locales/en.json",
            '  "merge_suggestions.rationale": "Rationale",\n',
            '  "merge_suggestions.merge_method": "Integration method",\n'
            '  "merge_suggestions.merge_method.near_duplicate": "Near-duplicate consolidation (04-step style)",\n'
            '  "merge_suggestions.merge_method.kernel_fusion": "Meaning-kernel integration (kernel-fusion style)",\n',
        ),
    ]:
        insert_after_once(path, rationale, insertion)

    # Existing UI fixture must satisfy the newly strict proposal contract and
    # explicitly verify the reviewer-facing label.
    panel_test = "03_Implement/frontend/src/ui/MergeSuggestionsPanel.test.ts"
    replace_once(
        panel_test,
        '        mergedTextDraft: "Risk mitigation",\n        editedText: "Risk mitigation",',
        '        mergedTextDraft: "Risk mitigation",\n        mergeMethod: "near_duplicate" as const,\n        editedText: "Risk mitigation",',
    )
    replace_once(
        panel_test,
        '    expect(html).toContain(`${t("merge_suggestions.rationale")}: heuristic:normalized-text`);\n',
        '    expect(html).toContain(`${t("merge_suggestions.merge_method")}: ${t("merge_suggestions.merge_method.near_duplicate")}`);\n    expect(html).toContain(`${t("merge_suggestions.rationale")}: heuristic:normalized-text`);\n',
    )

    # Strict document tests: new decisions keep the method, old decisions still
    # load, and unknown values fail closed.
    validate_test = "03_Implement/frontend/src/domain/validate_doc.test.ts"
    marker = '  it("rejects merge suggestion decisions with invalid status", () => {'
    addition = '''  it("accepts known merge methods and legacy decisions without a method, but rejects unknown methods", () => {\n    const known = validateDocumentV1Strict({\n      ...validDocument,\n      mergeSuggestionDecisions: [{\n        id: "decision-method",\n        groupId: "g1",\n        decision: "accept",\n        decidedAt: now,\n        cardIds: ["c1", "c2"],\n        mergedTextDraft: "A",\n        editedText: "A",\n        mergeMethod: "kernel_fusion",\n      }],\n    });\n    expect(known.ok).toBe(true);\n\n    const legacy = validateDocumentV1Strict({\n      ...validDocument,\n      mergeSuggestionDecisions: [{\n        id: "decision-legacy",\n        groupId: "g1",\n        decision: "defer",\n        decidedAt: now,\n        cardIds: ["c1", "c2"],\n        mergedTextDraft: "A",\n        editedText: "A",\n      }],\n    });\n    expect(legacy.ok).toBe(true);\n\n    const unknown = validateDocumentV1Strict({\n      ...validDocument,\n      mergeSuggestionDecisions: [{\n        id: "decision-unknown",\n        groupId: "g1",\n        decision: "accept",\n        decidedAt: now,\n        cardIds: ["c1", "c2"],\n        mergedTextDraft: "A",\n        editedText: "A",\n        mergeMethod: "semantic_similarity",\n      }],\n    });\n    expect(unknown.ok).toBe(false);\n    if (unknown.ok) return;\n    expect(unknown.errors).toContain(\n      "mergeSuggestionDecisions[0].mergeMethod: must be 'near_duplicate' | 'kernel_fusion' when provided",\n    );\n  });\n\n'''
    replace_once(validate_test, marker, addition + marker)

    # Existing apply fixture creates a new decision directly; give it the
    # canonical method explicitly rather than letting tests rely on inference.
    apply_test = "03_Implement/frontend/src/domain/merge_suggestion_apply.test.ts"
    replace_once(
        apply_test,
        '      editedText: "待ち時間は利用継続の負担になる",\n      decisionReason:',
        '      editedText: "待ち時間は利用継続の負担になる",\n      mergeMethod: "near_duplicate",\n      decisionReason:',
    )

    # The persistence E2E now verifies the durable method snapshot as part of
    # decision -> apply -> save -> reload traceability.
    e2e_path = "03_Implement/frontend/e2e/merge_suggestion_apply_persistence.spec.ts"
    replace_once(
        e2e_path,
        '  expect(decision.representativeCardId).toBe(representative.id);\n  expect(new Set(decision.sourceCardIds)).toEqual(new Set(["c1", "c2"]));\n',
        '  expect(decision.representativeCardId).toBe(representative.id);\n  expect(decision.mergeMethod).toBe("near_duplicate");\n  expect(new Set(decision.sourceCardIds)).toEqual(new Set(["c1", "c2"]));\n',
    )


def finalize_docs() -> None:
    api_path = "02_Architecture/api.md"
    replace_once(
        api_path,
        "LLM応答は信頼境界の外側として扱う。未知ID・重複ID・2件未満・件数上限に加え、hold、既merge、明示的な `negate`、`type=contradicts` のevidence、異なる既知 `claimType`、同じカードを複数候補へ含める競合提案を決定論的に拒否する。",
        "LLM応答は信頼境界の外側として扱う。新しい提案では `mergeMethod` を必須とし、`near_duplicate`（04ステップ型の近接整理）または `kernel_fusion`（核融合法型の意味核統合）のどちらかを明示する。欠落値・未知値は拒否する。決定論的fallbackは意味核を新規生成しないため `near_duplicate` を付与する。未知ID・重複ID・2件未満・件数上限に加え、hold、既merge、明示的な `negate`、`type=contradicts` のevidence、異なる既知 `claimType`、同じカードを複数候補へ含める競合提案も決定論的に拒否する。人間が判断を記録する際は `mergeMethod` をDocumentのdecision snapshotへ保存するが、旧Documentのdecisionでは欠落を許容し、方式を推測補完しない。",
    )

    issue = Path("01_Plans/issues/issue-AI-MERGE-SEMANTICS-01-define-card-merge-semantics.md")
    text = issue.read_text(encoding="utf-8")
    text = text.replace("- Status: In Progress", "- Status: Done", 1)
    text = text.replace(
        '- [ ] `mergeMethod` をprovider出力、frontend共通契約、fallback、Document decision snapshotへ実装する。',
        '- [x] `mergeMethod` をprovider出力、frontend共通契約、fallback、Document decision snapshotへ実装した。',
        1,
    )
    text = text.replace(
        '- [ ] 新規remote応答の欠落・未知方式を拒否し、旧decisionの方式欠落は読めることを回帰テストで固定する。',
        '- [x] 新規remote応答の欠落・未知方式を拒否し、旧decisionの方式欠落は読めることを回帰テストで固定した。',
        1,
    )
    completion_marker = "## 完了境界"
    if completion_marker not in text:
        raise RuntimeError("AI-MERGE-SEMANTICS-01: completion marker not found")
    implementation = '''## R20実装結果（2026-09-04）\n\nR19で確定した方式追跡性を実装した。remote providerは各提案に `mergeMethod` を必須で返し、backendとfrontendの双方で `near_duplicate` / `kernel_fusion` 以外をfail-closedにする。決定論的fallbackは処理実態に合わせて `near_duplicate` を付ける。UIでは方式をAI rationale・人間判断理由とは別に表示し、新しく記録するDocument decision snapshotへそのまま保存する。\n\n保存済みの旧decisionは `mergeMethod` 欠落を許容し、方式を推測補完しない。`residuals` やpartial自動適用、短期audit eventへの重複保存には範囲を広げていない。decision → apply → save → reload の既存E2Eでも方式が保持されることを確認する。\n\n'''
    text = text.replace(completion_marker, implementation + completion_marker, 1)
    issue.write_text(text, encoding="utf-8")
    done = issue.parent / "done" / issue.name
    done.parent.mkdir(parents=True, exist_ok=True)
    issue.replace(done)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["apply", "finalize-docs"])
    args = parser.parse_args()
    if args.mode == "apply":
        apply_product_changes()
    else:
        finalize_docs()
