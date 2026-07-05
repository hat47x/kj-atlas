import React from "react";
import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { P2AReadinessPanel } from "./P2AReadinessPanel";
import { setActiveLocale } from "../../../i18n/translate";

describe("P2AReadinessPanel", () => {
  it("renders go status and all mock cases", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(React.createElement(P2AReadinessPanel));
    expect(html).toContain("FB-P2A A3 readiness");
    expect(html).toContain("data-ui-region=\"stream-b-p2a-readiness\"");
    expect(html).toContain("data-testid=\"p2a-proceed-status\"");
    expect(html).toContain("aria-live=\"polite\"");
    expect(html).toContain("aria-label=\"P2A mock validation log\"");
    expect(html).toContain("Proceed:");
    expect(html).toContain("Go");
    expect(html).toContain("M1: Pass (A3)");
    expect(html).toContain("M2: Pass (A3)");
    expect(html).toContain("M3: Pass (A3)");
    expect(html).toContain("M4: Fail (A2)");
    expect(html).toContain("CTR-2A-02-COLLAPSE-EXPAND-V1");
    expect(html).toContain("IslandVisibilityContractV1");
    expect(html).toContain("Accepted: M1, M2, M3 / Blocked: M4");
  });

  it("renders Japanese user-facing status labels without raw validation values", () => {
    setActiveLocale("ja");
    try {
      const html = renderToStaticMarkup(React.createElement(P2AReadinessPanel));

      expect(html).toContain("FB-P2A A3 準備状況");
      expect(html).toContain("判定:");
      expect(html).toContain("進行可");
      expect(html).toContain("理由: 進行できます");
      expect(html).toContain("M1: 合格 (A3)");
      expect(html).toContain("M4: 不合格 (A2)");
      expect(html).toContain("受理: M1, M2, M3 / ブロック: M4");
      expect(html).not.toContain(">go<");
      expect(html).not.toContain(": pass ");
      expect(html).not.toContain(": fail ");
    } finally {
      setActiveLocale("en");
    }
  });
});
