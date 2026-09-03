from __future__ import annotations

import json
from pathlib import Path

APP = Path("03_Implement/frontend/src/App.tsx")
PANEL = Path("03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx")
PANEL_TEST = Path("03_Implement/frontend/src/ui/MergeSuggestionsPanel.test.ts")
JA = Path("03_Implement/frontend/src/i18n/locales/ja.json")
EN = Path("03_Implement/frontend/src/i18n/locales/en.json")
ISSUE = Path("01_Plans/issues/issue-AI-MERGE-APPLY-01-connect-recorded-accept-to-explicit-merge-apply.md")


def read_preserving(path: Path) -> tuple[str, str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        text = handle.read()
    eol = "\r\n" if "\r\n" in text else "\n"
    return text, eol


def write_preserving(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def adapt(value: str, eol: str) -> str:
    return value.replace("\n", eol)


def replace_once(text: str, old: str, new: str, label: str, eol: str) -> str:
    old_value = adapt(old, eol)
    new_value = adapt(new, eol)
    count = text.count(old_value)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, got {count}")
    return text.replace(old_value, new_value, 1)


app, app_eol = read_preserving(APP)
app = replace_once(
    app,
    'import { resolveDecisionOriginTrace, resolveRepresentativeOriginTrace } from "./domain/merge_traceability";\n',
    'import { resolveDecisionOriginTrace, resolveRepresentativeOriginTrace } from "./domain/merge_traceability";\n'
    'import { applyRecordedMergeSuggestionDecision } from "./domain/merge_suggestion_apply";\n',
    "App import",
    app_eol,
)
handler = '''\n  const handleApplyRecordedMergeSuggestion = useCallback(\n    (groupId: string, options: { isTrusted: boolean }) => {\n      if (!document) {\n        return;\n      }\n      if (!options.isTrusted) {\n        setMergeSuggestionError(t("app.status.merge_suggestion.trusted_interaction_required"));\n        return;\n      }\n\n      const latestDecision = getLatestMergeSuggestionDecisionByGroup(\n        document.mergeSuggestionDecisions,\n      ).get(groupId);\n      if (!latestDecision) {\n        setMergeSuggestionError(t("app.status.merge_suggestion.apply_failed", { code: "decision_not_recorded" }));\n        return;\n      }\n\n      const result = applyRecordedMergeSuggestionDecision(document, latestDecision);\n      if (!result.ok) {\n        setMergeSuggestionError(t("app.status.merge_suggestion.apply_failed", { code: result.code }));\n        return;\n      }\n\n      const changed = applyDocumentChange(\n        result.document,\n        t("app.history.merge_suggestion_applied"),\n        { preserveSuggestionPreview: true },\n      );\n      if (!changed) {\n        return;\n      }\n\n      setMergeSuggestions((current) =>\n        current.map((suggestion) =>\n          suggestion.groupId === groupId\n            ? {\n                ...suggestion,\n                representativeCardId: result.representativeCardId,\n                representativeResolvedBy: "repOf",\n                representativeSourceCount: result.sourceCardIds.length,\n              }\n            : suggestion,\n        ),\n      );\n      setMergeSuggestionError(null);\n    },\n    [applyDocumentChange, document],\n  );\n'''
app = replace_once(app, '  const handleExport = useCallback(() => {\n', handler + '\n  const handleExport = useCallback(() => {\n', "App handler", app_eol)
app = replace_once(
    app,
    '                onDecide={handleRecordMergeSuggestionDecision}\n',
    '                onDecide={handleRecordMergeSuggestionDecision}\n                onApplyAccepted={handleApplyRecordedMergeSuggestion}\n',
    "App panel prop",
    app_eol,
)
write_preserving(APP, app)

panel, panel_eol = read_preserving(PANEL)
panel = replace_once(
    panel,
    '  latestAuditEventByGroup?: ReadonlyMap<string, MergeDecisionAuditEvent>;\n',
    '  onApplyAccepted: (groupId: string, options: { isTrusted: boolean }) => void;\n  latestAuditEventByGroup?: ReadonlyMap<string, MergeDecisionAuditEvent>;\n',
    "Panel prop",
    panel_eol,
)
panel = replace_once(panel, '  onDecide,\n  latestAuditEventByGroup,\n', '  onDecide,\n  onApplyAccepted,\n  latestAuditEventByGroup,\n', "Panel destructure", panel_eol)
apply_handler = '''\n  const handleApplyClick = (groupId: string, event: MouseEvent<HTMLButtonElement>) => {\n    const trustBoundary = evaluateMergeDecisionTrustBoundary({\n      isReadOnly,\n      isTrustedEvent: event.isTrusted,\n    });\n    if (!trustBoundary.allowDecision) {\n      setTrustBoundaryErrorMessage(\n        trustBoundary.rejectionReason === "read_only"\n          ? t("merge_suggestions.trust_boundary.read_only")\n          : t("merge_suggestions.trust_boundary.untrusted_event"),\n      );\n      return;\n    }\n\n    setTrustBoundaryErrorMessage(null);\n    onApplyAccepted(groupId, { isTrusted: event.isTrusted });\n  };\n'''
panel = replace_once(panel, '  return (\n    <section\n', apply_handler + '\n  return (\n    <section\n', "Panel handler", panel_eol)
panel = replace_once(
    panel,
    '        const hasDecisionReason = Boolean(normalizeHilDecisionReason(decisionReasonByGroup[suggestion.groupId]));\n',
    '        const hasDecisionReason = Boolean(normalizeHilDecisionReason(decisionReasonByGroup[suggestion.groupId]));\n        const isAccepted = suggestion.latestDecision === "accept";\n        const isApplied = isAccepted && (suggestion.representativeResolvedBy === "repOf" || suggestion.representativeResolvedBy === "mergedIntoCardId");\n',
    "Panel state",
    panel_eol,
)
panel = replace_once(
    panel,
    '            <button type="button" disabled={isReadOnly || !hasDecisionReason} onClick={(event) => handleDecisionClick(suggestion.groupId, "defer", event)}>{t("merge_suggestions.action.defer")}</button>\n',
    '            <button type="button" disabled={isReadOnly || !hasDecisionReason} onClick={(event) => handleDecisionClick(suggestion.groupId, "defer", event)}>{t("merge_suggestions.action.defer")}</button>\n            {isAccepted ? (\n              <button\n                type="button"\n                disabled={isReadOnly || isApplied}\n                onClick={(event) => handleApplyClick(suggestion.groupId, event)}\n              >\n                {t(isApplied ? "merge_suggestions.action.applied" : "merge_suggestions.action.apply")}\n              </button>\n            ) : null}\n',
    "Panel button",
    panel_eol,
)
write_preserving(PANEL, panel)

panel_test, test_eol = read_preserving(PANEL_TEST)
panel_test = replace_once(
    panel_test,
    '    onMergedTextChange: vi.fn(),\n    onDecide: vi.fn(),\n',
    '    onMergedTextChange: vi.fn(),\n    onDecide: vi.fn(),\n    onApplyAccepted: vi.fn(),\n',
    "Test props",
    test_eol,
)
new_test = '''  it("shows the explicit apply action only for an accepted suggestion", () => {\n    const base = buildProps();\n    const pendingHtml = renderToStaticMarkup(\n      React.createElement(MergeSuggestionsPanel, {\n        ...base,\n        suggestions: [\n          {\n            ...base.suggestions[0],\n            latestDecision: "accept" as const,\n            representativeResolvedBy: "fallback" as const,\n          },\n        ],\n      }),\n    );\n    expect(pendingHtml).toContain(t("merge_suggestions.action.apply"));\n    expect(pendingHtml).not.toContain(t("merge_suggestions.action.applied"));\n\n    const appliedHtml = renderToStaticMarkup(\n      React.createElement(MergeSuggestionsPanel, {\n        ...base,\n        suggestions: [\n          {\n            ...base.suggestions[0],\n            latestDecision: "accept" as const,\n            representativeResolvedBy: "repOf" as const,\n          },\n        ],\n      }),\n    );\n    expect(appliedHtml).toContain(t("merge_suggestions.action.applied"));\n  });\n\n'''
panel_test = replace_once(panel_test, '  it("disables merge-decision editing controls in read-only mode", () => {\n', new_test + '  it("disables merge-decision editing controls in read-only mode", () => {\n', "Test insertion", test_eol)
write_preserving(PANEL_TEST, panel_test)


def update_locale(path: Path, values: dict[str, str]) -> None:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    data.update(values)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


update_locale(JA, {
    "merge_suggestions.action.apply": "採用した統合を適用",
    "merge_suggestions.action.applied": "統合を適用済み",
    "app.status.merge_suggestion.apply_failed": "統合を適用できませんでした（{code}）。現在のカード状態を確認してください。",
    "app.history.merge_suggestion_applied": "採用済みの統合候補をDocumentへ適用しました",
})
update_locale(EN, {
    "merge_suggestions.action.apply": "Apply accepted merge",
    "merge_suggestions.action.applied": "Merge applied",
    "app.status.merge_suggestion.apply_failed": "The merge could not be applied ({code}). Check the current card state.",
    "app.history.merge_suggestion_applied": "Applied the accepted merge suggestion to the document",
})

issue, issue_eol = read_preserving(ISSUE)
issue = replace_once(
    issue,
    '- [ ] UIから、記録済みacceptに対する明示的な実適用操作を呼び出せる。\n',
    '- [x] UIから、記録済みacceptに対する明示的な実適用操作を呼び出せる。accept自体は判断記録のまま維持し、別の「採用した統合を適用」操作でdomain transactionを呼ぶ。\n',
    "Issue AC",
    issue_eol,
)
result_section = '''\n## 第二段階の実装結果（2026-09-03）\n\n`MergeSuggestionsPanel` に、最新判断が `accept` の候補だけへ明示的な「採用した統合を適用」操作を追加した。`accept` ボタン自体の意味は変更せず、判断記録とDocument変更を別操作のまま保っている。\n\n適用操作もtrusted human eventを要求し、AppはDocumentに記録された最新decisionを取得して `applyRecordedMergeSuggestionDecision()` へ渡す。成功時は既存の `applyDocumentChange()` を通してDocumentをdirtyにし、保存はアプリ既存の明示的な保存操作に委ねる。したがって、AI提案やacceptクリックだけで自動保存・自動mergeは発生しない。\n\n実適用後は候補表示の代表カードID・解決方法・source件数を即時更新し、重複適用の操作を無効化する。\n'''
issue = replace_once(issue, '\n## 検証計画\n', result_section + '\n## 検証計画\n', "Issue result", issue_eol)
write_preserving(ISSUE, issue)

print("clean merge apply UI patch applied")
