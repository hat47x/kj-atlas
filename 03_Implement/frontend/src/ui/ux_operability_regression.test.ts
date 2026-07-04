import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const readSource = (relativePath: string): string =>
  readFileSync(resolve(__dirname, "..", "..", relativePath), "utf8");

describe("UX Operability regression contracts", () => {
  it("Phase 1: pointer-keyboard-flow-review", () => {
    const cardViewSource = readSource("src/canvas/CardView.tsx");

    expect(cardViewSource).toContain("function canStartDrag");
    expect(cardViewSource).toContain('if (event.pointerType === "mouse")');
    expect(cardViewSource).toContain("event.currentTarget.setPointerCapture(event.pointerId)");
    expect(cardViewSource).toContain("event.currentTarget.releasePointerCapture(event.pointerId)");
    expect(cardViewSource).toContain('event.key === "Enter" || event.key === " "');
  });

  it("Phase 2: keyboard-card-selection", () => {
    const cardViewSource = readSource("src/canvas/CardView.tsx");

    expect(cardViewSource).toContain('role="option"');
    expect(cardViewSource).toContain("aria-selected={isSelected}");
    expect(cardViewSource).toContain("const [isFocused, setIsFocused] = useState(false)");
    expect(cardViewSource).toContain("onFocus={handleFocus}");
    expect(cardViewSource).toContain("onBlur={handleBlur}");
    expect(cardViewSource).toContain('data-focus={isFocused ? "card" : undefined}');
    expect(cardViewSource).toContain("tabIndex={0}");
    expect(cardViewSource).toContain("onKeyDown={handleKeyDown}");
    expect(cardViewSource).toContain("onSelect(card.id, event.shiftKey)");
  });

  it("Phase 3: contextual-selection-panel", () => {
    const sidePanelSource = readSource("src/ui/SidePanel.tsx");

    expect(sidePanelSource).toContain('data-ui-region="selection-context"');
    expect(sidePanelSource).toContain('data-panel="selection-context"');
    expect(sidePanelSource).toContain('t("side_panel.context.title")');
    expect(sidePanelSource).toContain('t("side_panel.context.review_state"');
    expect(sidePanelSource).toContain('data-panel-group="advanced"');
    expect(sidePanelSource).toContain('aria-expanded={isAdvancedPanelOpen ? "true" : "false"}');
    expect(sidePanelSource).toContain('onToggle={(event) => {');
  });

  it("Phase 4: panel-dismissal-focus-scope", () => {
    const sharePanelSource = readSource("src/ui/SharePanel.tsx");
    expect(sharePanelSource).toContain('data-focus-return-id="share-panel-trigger"');
    expect(sharePanelSource).toContain('data-panel="share-replay"');
    expect(sharePanelSource).toContain('if (event.key === "Escape")');

    const appSource = readSource("src/App.tsx");
    expect(appSource).toContain('data-focus-return-id="view-controls-trigger"');
    expect(appSource).toContain('data-panel="view"');
    expect(appSource).toContain('if (event.key === "Escape")');
  });

  it("Phase 5: primary-toolbar-task-prioritization", () => {
    const appSource = readSource("src/App.tsx");
    const shellSource = readSource("src/ui/Shell.tsx");

    expect(appSource).toContain('data-ui-region="primary-flow"');
    expect(appSource).toContain('data-ui-complexity-tier="core-context"');
    expect(appSource).toContain('data-ui-complexity-tier="core-view"');
    expect(shellSource).toContain('data-ui-complexity-tier="core-share"');
    expect(appSource).toContain('data-ui-complexity-tier="core-toolbar"');
    expect(appSource).toContain('data-ui-complexity-tier="advanced-disclosure"');
    expect(appSource).toContain('data-ui-complexity-tier="advanced-content"');
    expect(appSource.match(/data-ui-core-action=/g)).toHaveLength(7);
    expect(appSource).toContain('t("app.toolbar.new")');
    expect(appSource).toContain('t("app.toolbar.open")');
    expect(appSource).toContain('t("app.toolbar.undo")');
    expect(appSource).toContain('t("app.toolbar.save")');
  });

  it("Phase 5b: work-mode surface owns advanced narrative and HIL panels", () => {
    const appSource = readSource("src/App.tsx");

    expect(appSource).toContain("const advancedWorkModeContent = (");
    expect(appSource).toContain("<WorkModePanel");
    expect(appSource).toContain('data-ui-core-action="work-mode"');

    const sidePanelStart = appSource.indexOf("sidePanel={");
    const sidePanelEnd = appSource.indexOf("selectedIsland={", sidePanelStart);
    const sidePanelCall = appSource.slice(sidePanelStart, sidePanelEnd);
    expect(sidePanelCall).not.toContain("topContent=");
    expect(sidePanelCall).not.toContain("NarrativesPanel");
    expect(sidePanelCall).not.toContain("HilRsWorkflowPanel");

    const workModeStart = appSource.indexOf("const advancedWorkModeContent = (");
    const workModeEnd = appSource.indexOf("return (", workModeStart);
    const workModeContent = appSource.slice(workModeStart, workModeEnd);
    expect(workModeContent).toContain("<NarrativesPanel");
    expect(workModeContent).toContain("<HilRsWorkflowPanel");
    expect(workModeContent).toContain("{structuralDiffPanel}");
  });

  it("Phase 5c: domain detail filters and guided flow stay behind advanced disclosure", () => {
    const appSource = readSource("src/App.tsx");
    const sidePanelSource = readSource("src/ui/SidePanel.tsx");

    expect(sidePanelSource).toContain('data-panel="domain-detail-filters"');
    expect(sidePanelSource).toContain('data-panel="guided-flow"');
    expect(sidePanelSource).toContain('data-ui-complexity-tier="advanced-content"');
    expect(sidePanelSource).toContain("{isAdvancedUiEnabled ? (");
    expect(appSource).toContain("if (!isAdvancedUiEnabled) {");
    expect(appSource).toContain("setGuidedFlowEnabled(false);");
  });

  it("Phase 6: read-only-review-disables-edit-surfaces", () => {
    const appSource = readSource("src/App.tsx");
    expect(appSource).toContain("disabled={isReadOnly || isLoading || !document || isSuggesting}");
    expect(appSource).toContain("disabled={isReadOnly || isLoading || !document}");
    expect(appSource).toContain("disabled={isReadOnly || isLoading || !document || !canCreateIsland}");
    expect(appSource).toContain(
      "disabled={isReadOnly || isLoading || !document || (selectedCardIds.length === 0 && !selectedIslandId)}",
    );
    expect(appSource).toContain("disabled={isReadOnly || isLoading || !document || isSaving || !isDirty}");

    const sidePanelSource = readSource("src/ui/SidePanel.tsx");
    expect(sidePanelSource).toMatch(/value=\{selectedCard\.claimType \?\? "unknown"\}\s+disabled=\{isReadOnly\}/);
    expect(sidePanelSource).toMatch(/value=\{selectedCard\.holdState \?\? "active"\}\s+disabled=\{isReadOnly\}/);
    expect(sidePanelSource).toMatch(/disabled=\{isReadOnly\}/);
    expect(sidePanelSource).toMatch(/import.*ShelfPanel.*from/);
    expect(sidePanelSource).toMatch(/checked=\{selectedCard\.textReviewed === true\}\s+disabled=\{isReadOnly\}/);
    expect(sidePanelSource).toMatch(/value=\{selectedCard\.critique \?\? ""\}\s+disabled=\{isReadOnly\}/);
  });

  it("Phase 7: empty-canvas-onboarding-stays-operable", () => {
    const appSource = readSource("src/App.tsx");
    const emptyCanvasHintSource = readSource("src/ui/EmptyCanvasHint.tsx");

    expect(appSource).toContain("cards: []");
    expect(appSource).toContain("const shouldShowEmptyCanvasHint =");
    expect(appSource).toContain("!isStartPanelVisible");
    expect(appSource).toContain("!isReadOnly");
    expect(appSource).toContain("(document?.cards.length ?? 0) === 0");
    expect(appSource).toContain("<EmptyCanvasHint");
    expect(emptyCanvasHintSource).toContain('data-ui-region="empty-canvas-hint"');
    expect(emptyCanvasHintSource).toContain('aria-live="polite"');
    expect(emptyCanvasHintSource).not.toContain("autoFocus");
  });
});
