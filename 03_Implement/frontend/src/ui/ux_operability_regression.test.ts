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

  it("UX-VISUAL-01: card state badges sit in a normal-flow meta-row above the body (no first-line overlap)", () => {
    const cardViewSource = readSource("src/canvas/CardView.tsx");

    // The meta-row is a normal-flow band ABOVE the body: badges no longer use
    // position:absolute over the body first line (ADR-0048 D1).
    expect(cardViewSource).toContain('data-card-meta-row=""');
    // claimType tints a 3px left band (color channel).
    expect(cardViewSource).toContain("borderLeft:");
    // Unreviewed marker is a small top-right dot (form channel), preserved.
    expect(cardViewSource).toContain('t("card_view.unreviewed")');
    // AC-3: far-LOD markers keep the needs-attention (unreviewed/critique) tint.
    expect(cardViewSource).toContain("markerNeedsAttention");
  });

  it("UX-VISUAL-01 AC-2: in-canvas legend is default-OFF with Escape/focus-return contract", () => {
    const legendSource = readSource("src/ui/CanvasLegend.tsx");
    expect(legendSource).toContain('data-ui-region="canvas-legend"');
    expect(legendSource).toContain('role="dialog"');
    expect(legendSource).toContain('if (event.key === "Escape")');

    const appSource = readSource("src/App.tsx");
    // Default OFF (CB-1): the legend only renders behind explicit state.
    expect(appSource).toContain("const [isCanvasLegendOpen, setIsCanvasLegendOpen] = useState(false)");

    const viewControlsSource = readSource("src/ui/ViewControlsPanel.tsx");
    expect(viewControlsSource).toContain('data-focus-return-id="legend-trigger"');
  });

  it("UX-VISUAL-02: protection mark is deterministic, non-scoring, and toggleable", () => {
    const cardViewSource = readSource("src/canvas/CardView.tsx");
    expect(cardViewSource).toContain('t("card_view.protected")');

    // Detection is deterministic (lone-wolf gated on islands existing), not AI.
    const canvasShellSource = readSource("src/canvas/CanvasShell.tsx");
    expect(canvasShellSource).toContain("protectedCardIdSet");
    expect(canvasShellSource).toContain("document.islands.length === 0");

    // App owns the toggle; default ON but toggleable OFF (ADR-0048 D3, CB-1 self-report).
    const appSource = readSource("src/App.tsx");
    expect(appSource).toContain("const [showProtectionMarks, setShowProtectionMarks] = useState(true)");
    // Small-island threshold is a named, auditable constant (not a bare magic
    // number) and excludes degenerate 0-card islands.
    expect(appSource).toContain("const SMALL_ISLAND_MAX_MEMBERS = 2");
    expect(appSource).toContain("island.cardIds.length > 0 &&");

    // Card and island marks share one visual signature (dashed border + square
    // dot) so "protection" reads as a single channel, and the legend describes it.
    const islandViewSource = readSource("src/canvas/IslandView.tsx");
    expect(cardViewSource).toContain("1px dashed #94a3b8");
    expect(islandViewSource).toContain("1px dashed #94a3b8");
    const legendSource = readSource("src/ui/CanvasLegend.tsx");
    expect(legendSource).toContain('"legend.item.protected"');
  });

  it("PROV-VIS-01: AI provider status is read-only (no runtime switch UI) and lives in the View panel", () => {
    const viewControlsSource = readSource("src/ui/ViewControlsPanel.tsx");
    expect(viewControlsSource).toContain('"view_controls.ai_provider.title"');
    expect(viewControlsSource).toContain("providerKind");
    expect(viewControlsSource).toContain("lastAiCallOutcome");
    // Governance boundary (ADR-0050 D1): no <select>/onChange for provider,
    // and no fetch/mutation call from this display-only panel.
    expect(viewControlsSource).not.toMatch(/onProviderKindChange|onChangeProviderKind|setProviderKind/);

    const appSource = readSource("src/App.tsx");
    expect(appSource).toContain("const [providerKind, setProviderKind] = useState<ProviderKind | null>(null)");
    expect(appSource).toContain("getProviderStatus()");
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
    const workModePanelSource = readSource("src/ui/WorkModePanel.tsx");

    expect(appSource).toContain("const advancedWorkModeContent = (");
    expect(appSource).toContain("<WorkModePanel");
    expect(appSource).toContain('data-ui-core-action="work-mode"');
    expect(workModePanelSource).toContain('role="dialog"');
    expect(workModePanelSource).toContain('aria-modal="true"');
    expect(workModePanelSource).toContain("tabIndex={-1}");
    expect(workModePanelSource).toContain("onKeyDown={handlePanelKeyDown}");
    expect(workModePanelSource).toContain("function getFocusableElements");
    expect(workModePanelSource).toContain('event.key !== "Tab"');
    expect(workModePanelSource).toContain("closePanelAndRestoreFocus");

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
    const viewControlsPanelSource = readSource("src/ui/ViewControlsPanel.tsx");

    expect(appSource).toContain("loadEmptyCanvasHintCompleted");
    expect(appSource).toContain("cards: []");
    expect(appSource).toContain("const shouldShowEmptyCanvasHint =");
    expect(appSource).toContain("!isStartPanelVisible");
    expect(appSource).toContain("!isReadOnly");
    expect(appSource).toContain("!emptyCanvasHintCompleted");
    expect(appSource).toContain("(document?.cards.length ?? 0) === 0");
    expect(appSource).toContain("<EmptyCanvasHint");
    expect(appSource).toContain("markEmptyCanvasHintCompleted();");
    expect(appSource).toContain("onResetEmptyCanvasHint={handleResetEmptyCanvasHint}");
    expect(emptyCanvasHintSource).toContain('data-ui-region="empty-canvas-hint"');
    expect(emptyCanvasHintSource).toContain('aria-live="polite"');
    expect(emptyCanvasHintSource).not.toContain("autoFocus");
    expect(viewControlsPanelSource).toContain("emptyCanvasHintCompleted");
    expect(viewControlsPanelSource).toContain('t("view_controls.onboarding.reset_empty_canvas")');
  });
});
