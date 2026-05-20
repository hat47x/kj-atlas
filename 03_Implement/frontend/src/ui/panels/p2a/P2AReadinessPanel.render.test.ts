import React from "react";
import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { P2AReadinessPanel } from "./P2AReadinessPanel";

describe("P2AReadinessPanel", () => {
  it("renders go status and all mock cases", () => {
    const html = renderToStaticMarkup(React.createElement(P2AReadinessPanel));
    expect(html).toContain("FB-P2A A3 readiness");
    expect(html).toContain("data-ui-region=\"stream-b-p2a-readiness\"");
    expect(html).toContain("data-testid=\"p2a-proceed-status\"");
    expect(html).toContain("aria-live=\"polite\"");
    expect(html).toContain("aria-label=\"p2a-mock-validation-log\"");
    expect(html).toContain("Proceed:");
    expect(html).toContain("go");
    expect(html).toContain("M1: pass (A3)");
    expect(html).toContain("M2: pass (A3)");
    expect(html).toContain("M3: pass (A3)");
    expect(html).toContain("M4: fail (A2)");
    expect(html).toContain("CTR-2A-02-COLLAPSE-EXPAND-V1");
    expect(html).toContain("IslandVisibilityContractV1");
    expect(html).toContain("Accepted: M1, M2, M3 / Blocked: M4");
  });
});
