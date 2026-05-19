import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const readSource = (relativePath: string): string =>
  readFileSync(resolve(__dirname, "..", "..", relativePath), "utf8");

describe("UX Operability regression contracts", () => {
  it("keeps keyboard-selectable card contracts", () => {
    const source = readSource("src/canvas/CardView.tsx");
    expect(source).toContain('role="option"');
    expect(source).toContain('aria-selected={isSelected}');
    expect(source).toContain('tabIndex={0}');
    expect(source).toContain('event.key === "Enter" || event.key === " "');
    expect(source).toContain('onSelect(card.id, event.shiftKey)');
  });

  it("keeps selection-context and advanced disclosure contracts", () => {
    const source = readSource("src/ui/SidePanel.tsx");
    expect(source).toContain('data-ui-region="selection-context"');
    expect(source).toContain('data-panel="selection-context"');
    expect(source).toContain('data-panel-group="advanced"');
    expect(source).toContain('aria-expanded="false"');
  });

  it("keeps panel dismissal and focus return contracts", () => {
    const sharePanelSource = readSource("src/ui/SharePanel.tsx");
    expect(sharePanelSource).toContain('data-focus-return-id="share-panel-trigger"');
    expect(sharePanelSource).toContain('data-panel="share-replay"');
    expect(sharePanelSource).toContain('if (event.key === "Escape")');

    const appSource = readSource("src/App.tsx");
    expect(appSource).toContain('data-focus-return-id="view-controls-trigger"');
    expect(appSource).toContain('data-panel="view"');
    expect(appSource).toContain('if (event.key === "Escape")');
  });
});
