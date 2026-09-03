from __future__ import annotations

from pathlib import Path

APP = Path("03_Implement/frontend/src/App.tsx")
PANEL = Path("03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx")
PANEL_TEST = Path("03_Implement/frontend/src/ui/MergeSuggestionsPanel.test.ts")
E2E = Path("03_Implement/frontend/e2e/merge_suggestion_partial_persistence.spec.ts")
API = Path("02_Architecture/api.md")
PARENT = Path("01_Plans/issues/issue-AI-MERGE-SEMANTICS-01-define-card-merge-semantics.md")
DONE = Path("01_Plans/issues/done/issue-AI-MERGE-PARTIAL-01-define-partial-merge-selection-contract.md")
METHOD = Path("01_Plans/issues/issue-AI-MERGE-METHOD-TRACE-01-track-merge-method-through-decision-audit.md")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: replacement count={count}")
    return text.replace(old, new, 1)


# App.tsx is CRLF-heavy. Keep byte-level CRLF intact so a four-line semantic
# change never becomes a whole-file diff.
app = APP.read_bytes()
replacements = [
    (
        b"  latestDecision?: MergeSuggestionDecision;\r\n  latestDecidedAt?: string;\r\n  representativeCardId?: string;",
        b"  latestDecision?: MergeSuggestionDecision;\r\n  latestDecidedAt?: string;\r\n  latestSelectedCardIds?: string[];\r\n  representativeCardId?: string;",
        "App draft type",
    ),
    (
        b"            latestDecision: latestDecision?.decision,\r\n            latestDecidedAt: latestDecision?.decidedAt,\r\n            representativeCardId:",
        b"            latestDecision: latestDecision?.decision,\r\n            latestDecidedAt: latestDecision?.decidedAt,\r\n            latestSelectedCardIds:\r\n              latestDecision?.decision === \"partial\" ? latestDecision.selectedCardIds : undefined,\r\n            representativeCardId:",
        "App suggestion reload mapping",
    ),
    (
        b"                latestDecision: decision,\r\n                latestDecidedAt: decidedAt,\r\n              }",
        b"                latestDecision: decision,\r\n                latestDecidedAt: decidedAt,\r\n                latestSelectedCardIds: decision === \"partial\" ? options.selectedCardIds : undefined,\r\n              }",
        "App decision mapping",
    ),
]
for old, new, label in replacements:
    count = app.count(old)
    if count != 1:
        raise SystemExit(f"{label}: replacement count={count}")
    app = app.replace(old, new, 1)
APP.write_bytes(app)

panel = PANEL.read_text(encoding="utf-8")
panel = replace_once(
    panel,
    '  latestDecision?: MergeSuggestionDecision;\n  latestDecidedAt?: string;\n  representativeCardId?: string;',
    '  latestDecision?: MergeSuggestionDecision;\n  latestDecidedAt?: string;\n  latestSelectedCardIds?: string[];\n  representativeCardId?: string;',
    "Panel draft type",
)
panel = replace_once(
    panel,
    '''    const suggestion = suggestions.find((item) => item.groupId === groupId);\n    const selectedCardIds = (partialSelectedCardIdsByGroup[groupId] ?? [])\n      .filter((cardId) => suggestion?.cardIds.includes(cardId))\n      .sort((left, right) => left.localeCompare(right));''',
    '''    const suggestion = suggestions.find((item) => item.groupId === groupId);\n    const hasLocalPartialSelection = Object.prototype.hasOwnProperty.call(\n      partialSelectedCardIdsByGroup,\n      groupId,\n    );\n    const selectedCardIds = (\n      hasLocalPartialSelection\n        ? partialSelectedCardIdsByGroup[groupId] ?? []\n        : suggestion?.latestSelectedCardIds ?? []\n    )\n      .filter((cardId) => suggestion?.cardIds.includes(cardId))\n      .sort((left, right) => left.localeCompare(right));''',
    "Panel decision selection",
)
panel = replace_once(
    panel,
    '''        const partialSelectedCardIds = (partialSelectedCardIdsByGroup[suggestion.groupId] ?? [])\n          .filter((cardId) => suggestion.cardIds.includes(cardId));''',
    '''        const hasLocalPartialSelection = Object.prototype.hasOwnProperty.call(\n          partialSelectedCardIdsByGroup,\n          suggestion.groupId,\n        );\n        const partialSelectedCardIds = (\n          hasLocalPartialSelection\n            ? partialSelectedCardIdsByGroup[suggestion.groupId] ?? []\n            : suggestion.latestSelectedCardIds ?? []\n        ).filter((cardId) => suggestion.cardIds.includes(cardId));''',
    "Panel rendered selection",
)
PANEL.write_text(panel, encoding="utf-8")

panel_test = PANEL_TEST.read_text(encoding="utf-8")
marker = '''  it("shows the explicit apply action only for an accepted suggestion", () => {'''
new_test = '''  it("restores a recorded partial subset so a later apply is human-visible", () => {\n    const base = buildProps();\n    const html = renderToStaticMarkup(\n      React.createElement(MergeSuggestionsPanel, {\n        ...base,\n        suggestions: [\n          {\n            ...base.suggestions[0],\n            cardIds: ["a", "b", "c"],\n            latestDecision: "partial" as const,\n            latestSelectedCardIds: ["a", "b"],\n          },\n        ],\n        cardsById: new Map([\n          ...base.cardsById,\n          ["c", { id: "c", text: "Different nuance", x: 20, y: 0 }],\n        ]),\n      }),\n    );\n\n    expect((html.match(/type="checkbox"[^>]*checked=""/g) ?? []).length).toBe(2);\n    expect(html).toContain(t("merge_suggestions.action.apply"));\n  });\n\n'''
if marker not in panel_test:
    raise SystemExit("Panel test marker missing")
panel_test = panel_test.replace(marker, new_test + marker, 1)
PANEL_TEST.write_text(panel_test, encoding="utf-8")

e2e = E2E.read_text(encoding="utf-8")
old_flow = '''  await partialButton.click();\n\n  const applyButton = workMode.getByRole("button", { name: "Apply accepted merge" });\n  await expect(applyButton).toBeEnabled();\n  await applyButton.click();\n  await expect(workMode.getByRole("button", { name: "Merge applied" })).toBeDisabled();\n\n  await workMode.getByRole("button", { name: "Close work mode" }).click();\n  await page.locator(SAVE).click();\n  await expect.poll(() => persistence.putCount()).toBe(1);\n\n  const saved = persistence.storedDocument();'''
new_flow = '''  await partialButton.click();\n\n  // Decision and apply are deliberately separate operations. Persist the\n  // decision first, reload it, and require the recorded subset to be visible\n  // again before the human can explicitly apply it.\n  await workMode.getByRole("button", { name: "Close work mode" }).click();\n  await page.locator(SAVE).click();\n  await expect.poll(() => persistence.putCount()).toBe(1);\n\n  await page.reload();\n  await openSample(page);\n  const reopenedWorkMode = await openMergePanel(page);\n  await reopenedWorkMode.getByRole("button", { name: "Collect candidates" }).click();\n  const reopenedPartialSelectionSummary = reopenedWorkMode.getByText("Select cards for partial acceptance");\n  await reopenedPartialSelectionSummary.click();\n  await expect(reopenedWorkMode.getByRole("checkbox", { name: /c1: Observation one/ })).toBeChecked();\n  await expect(reopenedWorkMode.getByRole("checkbox", { name: /c2: Observation two/ })).toBeChecked();\n  await expect(reopenedWorkMode.getByRole("checkbox", { name: /c3: Observation three/ })).not.toBeChecked();\n\n  const applyButton = reopenedWorkMode.getByRole("button", { name: "Apply accepted merge" });\n  await expect(applyButton).toBeEnabled();\n  await applyButton.click();\n  await expect(reopenedWorkMode.getByRole("button", { name: "Merge applied" })).toBeDisabled();\n\n  await reopenedWorkMode.getByRole("button", { name: "Close work mode" }).click();\n  await page.locator(SAVE).click();\n  await expect.poll(() => persistence.putCount()).toBe(2);\n\n  const saved = persistence.storedDocument();'''
e2e = replace_once(e2e, old_flow, new_flow, "E2E decision/apply separation")
E2E.write_text(e2e, encoding="utf-8")

api = API.read_text(encoding="utf-8")
anchor = '''- `snapshotVersion: string`\n\n\n\n### 2.7 CE4 Audit Integration Contract（API/CLI equivalence）'''
partial_contract = '''- `snapshotVersion: string`\n\n`partial` の新規判断では `selectedCardIds` を**人間が明示した真部分集合**として扱う。\n\n- `2 <= len(selectedCardIds) < len(cardIds)` を満たす。\n- `selectedCardIds` は `cardIds` の部分集合で、重複を含まない。\n- 全候補を採用する場合は `accept` を使う。1枚以下の選択はmergeとして成立しない。\n- 旧データで `partial` の `selectedCardIds` が欠落している、または全候補と同一の場合、採用集合を推測せず実適用をfail-closedにする。\n- 判断ログ・監査イベント・実mergeの `sourceCardIds` は同じ選択集合を保持する。\n- 判断と実適用は別操作とし、再読込後も記録済みの選択集合をUIで確認してから適用できる。\n- 選択されなかったカードは、実適用時にも本文・系譜・島所属・relation・review状態を変更しない。\n\n### 2.7 CE4 Audit Integration Contract（API/CLI equivalence）'''
api = replace_once(api, anchor, partial_contract, "API partial contract")
API.write_text(api, encoding="utf-8")

parent = PARENT.read_text(encoding="utf-8")
parent = replace_once(
    parent,
    '- Related ADR/Spec: `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`, `AI-IR-PROJECTION-01`, `AI-IR-STAGE5-SCOPE-01`, `AI-MERGE-APPLY-01`',
    '- Related ADR/Spec: `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`, `AI-IR-PROJECTION-01`, `AI-IR-STAGE5-SCOPE-01`, `AI-MERGE-APPLY-01`, `AI-MERGE-PARTIAL-01`, `AI-MERGE-METHOD-TRACE-01`',
    "parent related",
)
parent = replace_once(
    parent,
    '- decision → apply → save → reload はE2Eで固定済み。\n- R18で検出したremote AI提案と決定論ローカルfallbackの契約混線も解消済み。remote/common `MergeSuggestion` はbackend正本へ揃え、fallback固有metadataは派生表現へ分離した。',
    '- decision → apply → save → reload はE2Eで固定済み。\n- `partial` は、人間が2枚以上・全候補未満の真部分集合を明示し、その集合だけを判断・監査・実merge・保存／再読込まで追跡する契約へ移行済み。\n- R18で検出したremote AI提案と決定論ローカルfallbackの契約混線も解消済み。remote/common `MergeSuggestion` はbackend正本へ揃え、fallback固有metadataは派生表現へ分離した。',
    "parent current state",
)
parent = replace_once(
    parent,
    '''R19では、単にフィールドを増やすことを完了条件にしない。次を満たす場合に、後方互換な任意フィールドとして方式識別を追加する。\n\n1. 人間が提案を読む際、近接整理なのか意味核統合なのかが採否判断に実際に影響する。\n2. decision / auditへ残すことで、後から「なぜこの統合を採用したか」へ戻りやすくなる。\n3. remote AI提案と決定論fallbackの責務差を再び混線させず、remote → frontend → decision → auditまで同じ意味で通せる。\n\n追加する場合の候補語彙は `near_duplicate` / `kernel_fusion` とするが、API名は実装時に既存語彙と整合させる。方式が監査上使われないと確認できた場合は、フィールドを増やさず、その理由を記録して本Issueを閉じる。\n\n`partial` は別問題である。採用するsource部分集合をUIで明示する契約がない現状では自動適用しない。必要になった時点で、曖昧な既存値を流用せず部分集合の操作契約を先に定める。''',
    '''R18/R19の横断監査から、方式は実mergeの自動分岐条件ではなくても、人間が後から「なぜこの統合を採ったか」へ戻るための判断・監査文脈として追跡価値があると判断した。`AI-MERGE-METHOD-TRACE-01` で、remote/commonと決定論fallbackの責務差を再び混線させず、proposal → decision → auditへ同じ方式を通す。\n\n候補語彙は `near_duplicate` / `kernel_fusion` とし、API名は実装時に既存語彙と整合させる。方式ラベルだけを理由に実mergeのデータ変換を自動分岐させない。\n\n`partial` は `AI-MERGE-PARTIAL-01` で別途完了した。旧来の曖昧な `selectedCardIds` を推測せず、人間が明示した真部分集合だけを実適用する。''',
    "parent method decision",
)
parent = replace_once(
    parent,
    '- [x] remote/common提案契約と決定論fallback固有契約を分離した（R18 / PR #2853）。\n- [x] SafeMode二層、PII最小化、IR上限のfail-closedを維持した。\n- [ ] 統合方法をproposal → decision → auditへ機械可読に残すことが実利用上必要かを確定し、必要なら後方互換に実装する。',
    '- [x] remote/common提案契約と決定論fallback固有契約を分離した（R18 / PR #2853）。\n- [x] `partial` の真部分集合を人間が明示し、判断・監査・実適用・保存／再読込まで同じ集合として保持する（`AI-MERGE-PARTIAL-01`）。\n- [x] SafeMode二層、PII最小化、IR上限のfail-closedを維持した。\n- [ ] 統合方法をproposal → decision → auditへ機械可読に追跡する（`AI-MERGE-METHOD-TRACE-01`）。',
    "parent AC",
)
parent = replace_once(
    parent,
    '主要なmerge経路は実装済みである。本Issueの残作業は方式追跡性の要否判断だけに限定する。新しい実使用証拠なしに `residuals`、自動partial適用、追加のmerge自動化へ範囲を広げない。',
    '主要なmerge経路とpartialの明示選択契約は実装済みである。本Issueの残作業は `AI-MERGE-METHOD-TRACE-01` の方式追跡だけに限定する。自由記述 `residuals` や追加のmerge自動化へ範囲を広げない。',
    "parent completion",
)
PARENT.write_text(parent, encoding="utf-8")

DONE.parent.mkdir(parents=True, exist_ok=True)
if DONE.exists():
    raise SystemExit(f"Done memo already exists: {DONE}")
DONE.write_text(
    '''# Issue: AI-MERGE-PARTIAL-01 `partial` の部分採用契約を定める\n\n> 実装履歴はGit/PRを正本とし、このメモは完了境界と検証結果だけを残す。\n\n- Type: Feature / Domain Integrity\n- Status: Done\n- Source Issue: `AI-MERGE-SEMANTICS-01`\n- Priority: P1\n- Owner: Maintainer\n- Scope: `03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx`, `03_Implement/frontend/src/domain/merge_suggestion_decisions.ts`, `03_Implement/frontend/src/domain/merge_suggestion_apply.ts`, `03_Implement/frontend/src/domain/merge/decision_audit_events.ts`, `03_Implement/frontend/e2e/merge_suggestion_partial_persistence.spec.ts`, `02_Architecture/api.md`\n- Related ADR/Spec: `AI-MERGE-SEMANTICS-01`, `AI-MERGE-APPLY-01`, `ADR-0068`, `ADR-0069`\n- Expected verification level: `e2e`\n\n## 完了した契約\n\n`partial` は、提案されたsourceカードの**真部分集合を人間が明示して採用する判断**とする。\n\n- 2枚以上、かつ候補全件未満だけを許す。全件採用は `accept` とする。\n- 新規 `partial` は `selectedCardIds` を必須とし、候補集合外のIDや重複を許さない。\n- 旧データで選択集合が欠落・全件同一など曖昧な場合は、推測せず実適用をfail-closedにする。\n- 判断ログと監査に全候補 `cardIds` と実採用 `selectedCardIds` を分けて残す。\n- 実適用は選択されたsourceだけをmergeし、非選択カードを変更しない。\n- hold、既merge/canonicalization、`negate` / `contradicts`、異なる既知 `claimType` は適用直前にも再検査する。\n- 判断・実適用・保存は別操作のまま維持する。再読込後も記録済みの選択集合をUIへ復元し、人間が確認してからApplyできる。\n- 自由記述 `residuals` は追加せず、残差の一次記録は削除されず残るsourceカードそのものとする。\n\n## 検証\n\n- domain / audit / UI / i18n / API clientの回帰テスト\n- frontend typecheck\n- Playwrightで、3枚候補から2枚だけを選択 → 判断を保存 → 再読込 → 選択集合を再表示 → 明示適用 → 保存 → 再読込まで確認\n- 非選択カードが本文・系譜とも変更されないことを確認\n- `docs_check.py`、active issue validator、triage、diff check\n\n## 完了境界\n\n人間が明示した真部分集合が判断・監査・実merge・保存／再読込まで同じ集合として保たれ、後から適用する場合もその集合をUIで確認でき、非選択カードへ副作用を与えないことをもって完了とする。merge方式の追跡は `AI-MERGE-METHOD-TRACE-01` へ分離する。\n''',
    encoding="utf-8",
)

if METHOD.exists():
    raise SystemExit(f"Method issue already exists: {METHOD}")
METHOD.write_text(
    '''# Issue: AI-MERGE-METHOD-TRACE-01 merge方式を判断・監査まで追跡可能にする\n\n> Issue本文は現在の実行に必要な情報へ絞り、実装履歴はGit/PRを正本とする。\n\n- Type: Feature / Domain Integrity / AI Integration\n- Status: Open\n- Source Issue: `AI-MERGE-SEMANTICS-01`\n- Priority: P2\n- Owner: Maintainer\n- Scope: `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/frontend/src/api/client.ts`, `03_Implement/frontend/src/domain/merge_suggestion_decisions.ts`, `03_Implement/frontend/src/domain/merge/decision_audit_events.ts`, `03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx`, `02_Architecture/api.md`\n- Related ADR/Spec: `ADR-0069`, `AI-MERGE-SEMANTICS-01`, `AI-MERGE-PARTIAL-01`, `AI-MERGE-APPLY-01`, 継続dogfood R18/R19\n- Expected verification level: `integration`\n\n## 課題\n\nmerge promptは04ステップ型の近接整理と核融合法型の意味核統合を区別するが、共通 `MergeSuggestion` では方式が失われる。実mergeのデータ変換が同じでも、人間が後から「なぜこの統合を採ったか」を判断理由と一緒にたどるための監査文脈として方式には価値がある。\n\n## 契約方針\n\n- 候補語彙は `near_duplicate` / `kernel_fusion`。フィールド名は `mergeMethod` を第一候補とし、既存語彙と照合して確定する。\n- remote/common提案はbackend正式schemaから方式を返す。新規provider応答の未知・欠落方式を黙って採用しない。\n- 決定論ローカルfallbackは、その候補生成規則が近接整理に相当する場合だけ `near_duplicate` を付与する。Stream B固有metadataをremote/commonへ逆流させない。\n- proposal → decision snapshot → decision auditへ同じ方式を通し、UIで判断前後に確認できるようにする。\n- accept / partial の実mergeは、方式ラベルだけを理由に異なるデータ変換へ自動分岐しない。\n- 旧Document・旧provider fixture・旧decision logは後方互換に読み込む。\n- 自由記述 `residuals` は追加せず、元カードへのtraceabilityを残差の一次記録とする。\n\n## 受入条件\n\n- [ ] 機械可読な方式語彙とフィールド名を確定する。\n- [ ] backendの新規provider提案で方式を欠落させない。\n- [ ] remote/commonとlocal派生の契約分離を維持する。\n- [ ] proposal → decision → auditで方式が一致する。\n- [ ] UIで判断前後に方式を確認できる。\n- [ ] 方式ラベルによる自動適用分岐を導入しない。\n- [ ] 旧データ・fixtureとの後方互換を確認する。\n- [ ] API文書と親Issueを実装結果へ同期する。\n- [ ] 最終成果物を、意味を変えず自然な日本語として全文を読み直す。\n\n## 完了境界\n\n表示用ラベルを足すだけでは完了しない。新しい提案で方式を欠落させず、remote/commonとlocal派生の契約境界を壊さず、proposalから人間判断・監査まで同じ方式を追跡できることを回帰で固定した時点で完了とする。\n''',
    encoding="utf-8",
)

print("partial integration assembled")
