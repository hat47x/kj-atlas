import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it } from "vitest";
import { HilRsRediffPreview } from "./HilRsRediffPreview";
import { setActiveLocale } from "../i18n/translate";

describe("HilRsRediffPreview", () => {
  beforeEach(() => {
    setActiveLocale("en");
  });

  it("renders empty state when payload is null", () => {
    const html = renderToStaticMarkup(React.createElement(HilRsRediffPreview, { payload: null }));
    expect(html).toContain("No re-proposal changes yet.");
    expect(html).not.toContain("mock");
  });

  it("renders payload summary with human-review guard and actions", () => {
    const html = renderToStaticMarkup(
      React.createElement(HilRsRediffPreview, {
        payload: {
          schemaVersion: "1.0.0",
          proposalId: "proposal-1",
          basedOnIteration: 2,
          traceKey: "trace:card:c1:2",
          diffOps: [
            {
              opId: "op:move:c1",
              opType: "move",
              targetRef: "card:c1",
              before: { x: 0, y: 0 },
              after: { x: 1, y: 1 },
            },
          ],
        },
      }),
    );

    expect(html).toContain("proposal-1");
    expect(html).toContain("1.0.0");
    expect(html).toContain("Based on iteration:");
    expect(html).toContain("Diff operations:</strong> 1");
    expect(html).toContain("move / card:c1");
    expect(html).toContain("Human approval required");
    expect(html).toContain("Apply proposal");
    expect(html).toContain("Discard proposal");
  });

  it("renders deterministic empty-op message when diffOps is empty", () => {
    const html = renderToStaticMarkup(
      React.createElement(HilRsRediffPreview, {
        payload: {
          schemaVersion: "1.0.0",
          proposalId: "proposal-empty",
          basedOnIteration: 3,
          traceKey: "trace:card:c9:3",
          diffOps: [],
        },
      }),
    );

    expect(html).toContain("Diff operations:</strong> 0");
    expect(html).toContain("No diff operations returned for this proposal.");
  });
});
