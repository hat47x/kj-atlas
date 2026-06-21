import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it } from "vitest";
import { setActiveLocale } from "../i18n/translate";
import { ShelfPanel } from "./ShelfPanel";

describe("ShelfPanel accessibility (UQ-2)", () => {
  beforeEach(() => {
    setActiveLocale("ja");
  });

  it("has an accessible section label", () => {
    const html = renderToStaticMarkup(
      createElement(ShelfPanel, {
        cards: [{ id: "c1", text: "退避中カード", x: 0, y: 0 }],
        shelf: [{ cardId: "c1", shelvedAt: "2026-06-21T00:00:00Z" }],
      })
    );
    expect(html).toContain('aria-label=');
  });

  it("renders restore button with accessible text", () => {
    const html = renderToStaticMarkup(
      createElement(ShelfPanel, {
        cards: [{ id: "c1", text: "退避中カード", x: 0, y: 0 }],
        shelf: [{ cardId: "c1", shelvedAt: "2026-06-21T00:00:00Z" }],
      })
    );
    expect(html).toContain("復帰");
    expect(html).toContain("退避中カード");
  });

  it("renders nothing when shelf is empty (no DOM noise)", () => {
    const html = renderToStaticMarkup(
      createElement(ShelfPanel, { cards: [], shelf: [] })
    );
    expect(html).toBe("");
  });

  it("shows shelf reason when present", () => {
    const html = renderToStaticMarkup(
      createElement(ShelfPanel, {
        cards: [{ id: "c1", text: "要検討", x: 0, y: 0 }],
        shelf: [{ cardId: "c1", shelvedAt: "2026-06-21T00:00:00Z", reason: "後で再考" }],
      })
    );
    expect(html).toContain("後で再考");
  });
});
