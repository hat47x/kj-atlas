import React from "react";
import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { P2AReadinessPanel } from "./P2AReadinessPanel";

describe("P2AReadinessPanel", () => {
  it("renders go status and all mock cases", () => {
    const html = renderToStaticMarkup(React.createElement(P2AReadinessPanel));
    expect(html).toContain("FB-P2A A3 readiness");
    expect(html).toContain("Proceed:");
    expect(html).toContain("go");
    expect(html).toContain("M1: pass (A3)");
    expect(html).toContain("M2: pass (A3)");
    expect(html).toContain("M3: pass (A3)");
    expect(html).toContain("M4: fail (A2)");
  });
});
