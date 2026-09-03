from pathlib import Path

ROOT = Path('.')


def replace_once(path: str, old: str, new: str) -> None:
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{path}: expected one match, found {count}: {old[:80]!r}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')


# ---- MergeSuggestionsPanel -------------------------------------------------
ui = '03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx'
replace_once(
    ui,
    '    options: { isTrusted: boolean; decisionReason?: string }\n  ) => void;',
    '    options: { isTrusted: boolean; decisionReason?: string; selectedCardIds?: string[] }\n  ) => void;',
)
replace_once(
    ui,
    '  const [decisionReasonByGroup, setDecisionReasonByGroup] = useState<Record<string, string>>({});\n',
    '  const [decisionReasonByGroup, setDecisionReasonByGroup] = useState<Record<string, string>>({});\n'
    '  const [partialSelectedCardIdsByGroup, setPartialSelectedCardIdsByGroup] = useState<Record<string, string[]>>({});\n',
)
replace_once(
    ui,
    '    setTrustBoundaryErrorMessage(null);\n    onDecide(groupId, decision, { isTrusted: event.isTrusted, decisionReason });\n  };\n\n\n  const handleApplyClick',
    '    const suggestion = suggestions.find((item) => item.groupId === groupId);\n'
    '    const selectedCardIds = (partialSelectedCardIdsByGroup[groupId] ?? [])\n'
    '      .filter((cardId) => suggestion?.cardIds.includes(cardId))\n'
    '      .sort((left, right) => left.localeCompare(right));\n'
    '    if (decision === "partial" && (!suggestion || selectedCardIds.length < 2 || selectedCardIds.length >= suggestion.cardIds.length)) {\n'
    '      setTrustBoundaryErrorMessage(t("merge_suggestions.partial_selection.invalid"));\n'
    '      return;\n'
    '    }\n\n'
    '    setTrustBoundaryErrorMessage(null);\n'
    '    onDecide(groupId, decision, {\n'
    '      isTrusted: event.isTrusted,\n'
    '      decisionReason,\n'
    '      selectedCardIds: decision === "partial" ? selectedCardIds : undefined,\n'
    '    });\n'
    '  };\n\n'
    '  const handlePartialSelectionToggle = (groupId: string, cardId: string) => {\n'
    '    setPartialSelectedCardIdsByGroup((current) => {\n'
    '      const selected = new Set(current[groupId] ?? []);\n'
    '      if (selected.has(cardId)) selected.delete(cardId);\n'
    '      else selected.add(cardId);\n'
    '      return { ...current, [groupId]: [...selected].sort((left, right) => left.localeCompare(right)) };\n'
    '    });\n'
    '    setTrustBoundaryErrorMessage(null);\n'
    '  };\n\n\n'
    '  const handleApplyClick',
)
replace_once(
    ui,
    '        const hasDecisionReason = Boolean(normalizeHilDecisionReason(decisionReasonByGroup[suggestion.groupId]));\n        const isAccepted = suggestion.latestDecision === "accept";\n        const isApplied = isAccepted && (suggestion.representativeResolvedBy === "repOf" || suggestion.representativeResolvedBy === "mergedIntoCardId");',
    '        const hasDecisionReason = Boolean(normalizeHilDecisionReason(decisionReasonByGroup[suggestion.groupId]));\n'
    '        const partialSelectedCardIds = (partialSelectedCardIdsByGroup[suggestion.groupId] ?? [])\n'
    '          .filter((cardId) => suggestion.cardIds.includes(cardId));\n'
    '        const hasValidPartialSelection = partialSelectedCardIds.length >= 2 && partialSelectedCardIds.length < suggestion.cardIds.length;\n'
    '        const isApplicableDecision = suggestion.latestDecision === "accept" || suggestion.latestDecision === "partial";\n'
    '        const isApplied = isApplicableDecision && (suggestion.representativeResolvedBy === "repOf" || suggestion.representativeResolvedBy === "mergedIntoCardId");',
)
replace_once(
    ui,
    '          </ul>\n          <textarea\n            value={suggestion.editedText}',
    '          </ul>\n'
    '          <details style={{ marginBottom: 8 }}>\n'
    '            <summary style={{ cursor: "pointer", fontSize: 12, fontWeight: 600 }}>\n'
    '              {t("merge_suggestions.partial_selection.title")}\n'
    '            </summary>\n'
    '            <div style={{ fontSize: 11, color: "#64748b", margin: "6px 0" }}>\n'
    '              {t("merge_suggestions.partial_selection.hint")}\n'
    '            </div>\n'
    '            <div style={{ display: "grid", gap: 4 }}>\n'
    '              {suggestion.cardIds.map((cardId) => {\n'
    '                const card = cardsById.get(cardId);\n'
    '                return (\n'
    '                  <label key={`${suggestion.groupId}-partial-${cardId}`} style={{ fontSize: 12, color: "#334155" }}>\n'
    '                    <input\n'
    '                      type="checkbox"\n'
    '                      disabled={isReadOnly}\n'
    '                      checked={partialSelectedCardIds.includes(cardId)}\n'
    '                      onChange={() => handlePartialSelectionToggle(suggestion.groupId, cardId)}\n'
    '                    />{" "}\n'
    '                    {cardId}: {card ? snippet(card.text) : t("merge_suggestions.card_not_found")}\n'
    '                  </label>\n'
    '                );\n'
    '              })}\n'
    '            </div>\n'
    '            {!hasValidPartialSelection ? (\n'
    '              <div style={{ fontSize: 11, color: "#64748b", marginTop: 4 }}>\n'
    '                {t("merge_suggestions.partial_selection.invalid")}\n'
    '              </div>\n'
    '            ) : null}\n'
    '          </details>\n'
    '          <textarea\n'
    '            value={suggestion.editedText}',
)
replace_once(
    ui,
    '<button type="button" disabled={isReadOnly || !hasDecisionReason} onClick={(event) => handleDecisionClick(suggestion.groupId, "partial", event)}>{t("merge_suggestions.action.partial")}</button>',
    '<button type="button" disabled={isReadOnly || !hasDecisionReason || !hasValidPartialSelection} onClick={(event) => handleDecisionClick(suggestion.groupId, "partial", event)}>{t("merge_suggestions.action.partial")}</button>',
)
replace_once(ui, '{isAccepted ? (', '{isApplicableDecision ? (')

# ---- App.tsx (preserve CRLF) ----------------------------------------------
app_path = ROOT / '03_Implement/frontend/src/App.tsx'
b = app_path.read_bytes()
replacements = [
    (
        b'(groupId: string, decision: MergeSuggestionDecision, options: { isTrusted: boolean; decisionReason?: string }) => {',
        b'(groupId: string, decision: MergeSuggestionDecision, options: { isTrusted: boolean; decisionReason?: string; selectedCardIds?: string[] }) => {',
    ),
    (
        b'        cardIds: suggestion.cardIds,\r\n        mergedTextDraft: suggestion.mergedTextDraft,',
        b'        cardIds: suggestion.cardIds,\r\n        selectedCardIds: options.selectedCardIds,\r\n        mergedTextDraft: suggestion.mergedTextDraft,',
    ),
    (
        b'        cardIds: suggestion.cardIds,\r\n        snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",',
        b'        cardIds: suggestion.cardIds,\r\n        selectedCardIds: options.selectedCardIds,\r\n        snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",',
    ),
]
for old, new in replacements:
    count = b.count(old)
    if count != 1:
        raise SystemExit(f'App.tsx: expected one byte match, found {count}: {old[:80]!r}')
    b = b.replace(old, new, 1)
app_path.write_bytes(b)

# ---- Audit tests already updated separately; update decision tests ---------
decision_test = '03_Implement/frontend/src/domain/merge_suggestion_decisions.test.ts'
replace_once(
    decision_test,
    '      { id: "c2", text: "Alpha", x: 100, y: 0 },\n',
    '      { id: "c2", text: "Alpha", x: 100, y: 0 },\n      { id: "c3", text: "Alpha context", x: 200, y: 0 },\n',
)
replace_once(
    decision_test,
    '          cardIds: ["c1", "c2"],\n          mergedTextDraft: "alpha",\n          editedText: append.editedText,',
    '          cardIds: append.decision === "partial" ? ["c1", "c2", "c3"] : ["c1", "c2"],\n'
    '          selectedCardIds: append.decision === "partial" ? ["c1", "c2"] : undefined,\n'
    '          mergedTextDraft: "alpha",\n'
    '          editedText: append.editedText,',
)
append_marker = '\n  it("returns latest decision per group", () => {'
new_tests = '''\n  it("records a valid partial decision with a strict selected subset", () => {\n    const result = appendMergeSuggestionDecision(\n      createBaseDocument(),\n      {\n        groupId: "g-partial",\n        decision: "partial",\n        cardIds: ["c3", "c1", "c2"],\n        selectedCardIds: ["c2", "c1"],\n        mergedTextDraft: "alpha",\n        editedText: "alpha partial",\n      },\n      { idFactory: () => "d-partial", now: "2026-01-02T00:00:00.000Z" },\n    );\n\n    expect(result.mergeSuggestionDecisions?.at(-1)).toMatchObject({\n      decision: "partial",\n      cardIds: ["c1", "c2", "c3"],\n      selectedCardIds: ["c1", "c2"],\n      representativeCardId: "c1",\n    });\n  });\n\n  it("rejects partial decisions without a true subset", () => {\n    const base = createBaseDocument();\n    const common = {\n      groupId: "g-partial",\n      decision: "partial" as const,\n      cardIds: ["c1", "c2", "c3"],\n      mergedTextDraft: "alpha",\n      editedText: "alpha partial",\n    };\n\n    expect(() => appendMergeSuggestionDecision(base, common)).toThrowError("partial decision requires selectedCardIds");\n    expect(() => appendMergeSuggestionDecision(base, { ...common, selectedCardIds: ["c1"] })).toThrowError(\n      "partial selectedCardIds must contain at least two ids",\n    );\n    expect(() => appendMergeSuggestionDecision(base, { ...common, selectedCardIds: ["c1", "c2", "c3"] })).toThrowError(\n      "partial selectedCardIds must be a strict subset of cardIds",\n    );\n    expect(() => appendMergeSuggestionDecision(base, { ...common, selectedCardIds: ["c1", "outside"] })).toThrowError(\n      "partial selectedCardIds must be a subset of cardIds",\n    );\n  });\n'''
replace_once(decision_test, append_marker, new_tests + append_marker)

# ---- Apply tests -----------------------------------------------------------
apply_test = '03_Implement/frontend/src/domain/merge_suggestion_apply.test.ts'
replace_once(
    apply_test,
    '      cardIds: ["c1", "c2"],\n      mergedTextDraft: "待ち時間は利用継続の負担になる",',
    '      cardIds: decision === "partial" ? ["c1", "c2", "c3"] : ["c1", "c2"],\n'
    '      selectedCardIds: decision === "partial" ? ["c1", "c2"] : undefined,\n'
    '      mergedTextDraft: "待ち時間は利用継続の負担になる",',
)
old_apply_test = '''  it("refuses partial/reject/defer until partial source selection has an explicit UI contract", () => {\n    for (const decision of ["partial", "reject", "defer"] as const) {\n      const recorded = recordDecision(documentFixture(), decision);\n      expect(applyRecordedMergeSuggestionDecision(recorded.document, recorded.decision)).toEqual({\n        ok: false,\n        code: "decision_not_accepted",\n      });\n    }\n  });'''
new_apply_test = '''  it("applies only the human-selected subset for a recorded partial decision", () => {\n    const before = documentFixture();\n    const recorded = recordDecision(before, "partial");\n    vi.spyOn(crypto, "randomUUID").mockReturnValue("00000000-0000-0000-0000-000000000103");\n\n    const result = applyRecordedMergeSuggestionDecision(recorded.document, recorded.decision);\n    expect(result.ok).toBe(true);\n    if (!result.ok) return;\n\n    expect(result.sourceCardIds).toEqual(["c1", "c2"]);\n    expect(result.document.cards.find((card) => card.id === "c1")?.mergedIntoCardId).toBe(result.representativeCardId);\n    expect(result.document.cards.find((card) => card.id === "c2")?.mergedIntoCardId).toBe(result.representativeCardId);\n    expect(result.document.cards.find((card) => card.id === "c3")).toEqual(before.cards.find((card) => card.id === "c3"));\n    expect(result.document.mergeSuggestionDecisions?.at(-1)).toMatchObject({\n      decision: "partial",\n      selectedCardIds: ["c1", "c2"],\n      sourceCardIds: ["c1", "c2"],\n      representativeCardId: result.representativeCardId,\n    });\n  });\n\n  it("refuses ambiguous legacy partial decisions and still refuses reject/defer", () => {\n    const base = documentFixture();\n    const legacyMissing = {\n      id: "legacy-missing",\n      decisionId: "legacy-missing",\n      groupId: "g1",\n      decision: "partial" as const,\n      action: "partial" as const,\n      decidedAt: "2026-09-03T00:01:00.000Z",\n      cardIds: ["c1", "c2", "c3"],\n      mergedTextDraft: "draft",\n      editedText: "draft",\n    };\n    const missingDoc = { ...base, mergeSuggestionDecisions: [legacyMissing] };\n    expect(applyRecordedMergeSuggestionDecision(missingDoc, legacyMissing)).toEqual({\n      ok: false, code: "partial_selection_missing",\n    });\n\n    const legacyFull = { ...legacyMissing, id: "legacy-full", decisionId: "legacy-full", selectedCardIds: ["c1", "c2", "c3"] };\n    const fullDoc = { ...base, mergeSuggestionDecisions: [legacyFull] };\n    expect(applyRecordedMergeSuggestionDecision(fullDoc, legacyFull)).toEqual({\n      ok: false, code: "partial_selection_invalid",\n    });\n\n    for (const decision of ["reject", "defer"] as const) {\n      const recorded = recordDecision(documentFixture(), decision);\n      expect(applyRecordedMergeSuggestionDecision(recorded.document, recorded.decision)).toEqual({\n        ok: false,\n        code: "decision_not_accepted",\n      });\n    }\n  });'''
replace_once(apply_test, old_apply_test, new_apply_test)

# ---- UI static test --------------------------------------------------------
ui_test = '03_Implement/frontend/src/ui/MergeSuggestionsPanel.test.ts'
replace_once(
    ui_test,
    '    expect(html).toContain(t("merge_suggestions.action.partial"));\n',
    '    expect(html).toContain(t("merge_suggestions.action.partial"));\n'
    '    expect(html).toContain(t("merge_suggestions.partial_selection.title"));\n'
    '    expect(html).toContain(t("merge_suggestions.partial_selection.hint"));\n',
)
replace_once(
    ui_test,
    '  it("shows the explicit apply action only for an accepted suggestion", () => {',
    '  it("shows the explicit apply action for accepted and partially accepted suggestions", () => {',
)
replace_once(
    ui_test,
    '    expect(pendingHtml).toContain(t("merge_suggestions.action.apply"));\n    expect(pendingHtml).not.toContain(t("merge_suggestions.action.applied"));\n\n    const appliedHtml =',
    '    expect(pendingHtml).toContain(t("merge_suggestions.action.apply"));\n'
    '    expect(pendingHtml).not.toContain(t("merge_suggestions.action.applied"));\n\n'
    '    const partialHtml = renderToStaticMarkup(\n'
    '      React.createElement(MergeSuggestionsPanel, {\n'
    '        ...base,\n'
    '        suggestions: [{ ...base.suggestions[0], latestDecision: "partial" as const, representativeResolvedBy: "fallback" as const }],\n'
    '      }),\n'
    '    );\n'
    '    expect(partialHtml).toContain(t("merge_suggestions.action.apply"));\n\n'
    '    const appliedHtml =',
)

# ---- Locales ---------------------------------------------------------------
replace_once(
    '03_Implement/frontend/src/i18n/locales/ja.json',
    '  "merge_suggestions.action.partial": "一部採用",\n',
    '  "merge_suggestions.action.partial": "一部採用",\n'
    '  "merge_suggestions.partial_selection.title": "部分採用の対象を選ぶ",\n'
    '  "merge_suggestions.partial_selection.hint": "2枚以上、かつ候補の全件未満を選択してください。選ばなかったカードは変更しません。",\n'
    '  "merge_suggestions.partial_selection.invalid": "部分採用には、候補の一部を2枚以上選んでください。全件を採用する場合は「採用」を使ってください。",\n',
)
replace_once(
    '03_Implement/frontend/src/i18n/locales/en.json',
    '  "merge_suggestions.action.partial": "Partially accept",\n',
    '  "merge_suggestions.action.partial": "Partially accept",\n'
    '  "merge_suggestions.partial_selection.title": "Select cards for partial acceptance",\n'
    '  "merge_suggestions.partial_selection.hint": "Select at least two, but not all candidate cards. Unselected cards remain unchanged.",\n'
    '  "merge_suggestions.partial_selection.invalid": "Partial acceptance requires at least two selected cards and must leave at least one candidate unselected. Use Accept when adopting all candidates.",\n',
)

# ---- Partial E2E -----------------------------------------------------------
e2e = ROOT / '03_Implement/frontend/e2e/merge_suggestion_partial_persistence.spec.ts'
e2e.write_text(r'''import { expect, test, type Page } from "@playwright/test";

const START_PANEL = '[data-panel="start-document-entry"]';
const SAVE = '[data-ui-core-action="save"]';
const WORK_MODE = '[data-ui-core-action="work-mode"]';
const MERGED_TEXT = "Two matching observations are represented together.";

function buildDocument() {
  return {
    version: 1,
    id: "doc_phase1_canvas",
    title: "Partial merge persistence sample",
    createdAt: "2026-09-03T00:00:00.000Z",
    updatedAt: "2026-09-03T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "Observation one", x: 0, y: 0, textReviewed: true, claimType: "fact" },
      { id: "c2", text: "Observation two", x: 280, y: 0, textReviewed: true, claimType: "fact" },
      { id: "c3", text: "Observation three should remain separate", x: 560, y: 0, textReviewed: true, claimType: "fact" },
    ],
    edges: [],
    islands: [],
    readingOrder: ["c1", "c2", "c3"],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

async function routePersistentDocument(page: Page) {
  let storedDocument: any = buildDocument();
  let putCount = 0;

  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ providerKind: "none", callCounts: {}, tokenUsage: {} }),
    });
  });
  await page.route("**/ai/suggest-merges", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        suggestions: [{
          groupId: "partial-three-cards",
          cardIds: ["c1", "c2", "c3"],
          mergedTextDraft: MERGED_TEXT,
          rationale: "The first two can be represented together while the third may remain independent.",
        }],
      }),
    });
  });
  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    if (route.request().method() === "PUT") {
      storedDocument = JSON.parse(route.request().postData() ?? "{}");
      putCount += 1;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: `"partial-merge-${putCount}"` },
      body: JSON.stringify(storedDocument),
    });
  });
  return { storedDocument: () => storedDocument, putCount: () => putCount };
}

async function openSample(page: Page) {
  const startPanel = page.locator(START_PANEL);
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();
}

async function openMergePanel(page: Page) {
  const advanced = page.getByRole("button", { name: "Advanced", exact: true });
  if ((await advanced.getAttribute("aria-pressed")) !== "true") await advanced.click();
  await page.locator(WORK_MODE).click();
  const workMode = page.locator('[data-ui-region="work-mode"]');
  await expect(workMode).toBeVisible();
  await workMode.getByRole("tab", { name: "Merge selection" }).click();
  return workMode;
}

test("a human-selected partial subset is the only subset merged and survives save/reload", async ({ page }) => {
  const persistence = await routePersistentDocument(page);
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/?locale=en");
  await openSample(page);

  const workMode = await openMergePanel(page);
  await workMode.getByRole("button", { name: "Collect candidates" }).click();
  await expect(workMode.getByText("Select cards for partial acceptance")).toBeVisible();

  const reason = workMode.getByPlaceholder("Record why you accept/partial/reject/defer this proposal");
  await reason.fill("I want to merge only c1 and c2; c3 has a distinct nuance that should remain separate.");
  const partialButton = workMode.getByRole("button", { name: "Partially accept" });
  await expect(partialButton).toBeDisabled();

  await workMode.getByRole("checkbox", { name: /c1: Observation one/ }).check();
  await expect(partialButton).toBeDisabled();
  await workMode.getByRole("checkbox", { name: /c2: Observation two/ }).check();
  await expect(partialButton).toBeEnabled();
  await partialButton.click();

  const applyButton = workMode.getByRole("button", { name: "Apply accepted merge" });
  await expect(applyButton).toBeEnabled();
  await applyButton.click();
  await expect(workMode.getByRole("button", { name: "Merge applied" })).toBeDisabled();

  await workMode.getByRole("button", { name: "Close work mode" }).click();
  await page.locator(SAVE).click();
  await expect.poll(() => persistence.putCount()).toBe(1);

  const saved = persistence.storedDocument();
  const representative = saved.cards.find((card: any) => Array.isArray(card.repOf) && card.repOf.includes("c1") && card.repOf.includes("c2"));
  expect(representative).toBeTruthy();
  expect(new Set(representative.sources)).toEqual(new Set(["c1", "c2"]));
  expect(saved.cards.find((card: any) => card.id === "c1").mergedIntoCardId).toBe(representative.id);
  expect(saved.cards.find((card: any) => card.id === "c2").mergedIntoCardId).toBe(representative.id);

  const untouched = saved.cards.find((card: any) => card.id === "c3");
  expect(untouched.text).toBe("Observation three should remain separate");
  expect(untouched.mergedIntoCardId).toBeUndefined();
  expect(untouched.canonicalId).toBeUndefined();

  const decision = saved.mergeSuggestionDecisions.find((item: any) => item.decision === "partial");
  expect(decision.cardIds).toEqual(["c1", "c2", "c3"]);
  expect(decision.selectedCardIds).toEqual(["c1", "c2"]);
  expect(decision.sourceCardIds).toEqual(["c1", "c2"]);
  expect(decision.representativeCardId).toBe(representative.id);

  await page.reload();
  await openSample(page);
  const primaryFlow = page.locator('[data-ui-region="primary-flow"]');
  await expect(primaryFlow).toContainText(MERGED_TEXT);
  await expect(primaryFlow).toContainText("Observation three should remain separate");
});
''', encoding='utf-8')

print('partial merge contract patch applied')
