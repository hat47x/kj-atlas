import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { HilRsRediffPreview } from "./HilRsRediffPreview";

describe("HilRsRediffPreview", () => {
  it("renders empty state when payload is null", () => {
    const html = renderToStaticMarkup(React.createElement(HilRsRediffPreview, { payload: null }));
    expect(html).toContain("No mock re-proposal diff yet");
  });

  it("renders payload summary", () => {
    const html = renderToStaticMarkup(
      React.createElement(HilRsRediffPreview, {
        payload: {
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
    expect(html).toContain("move / card:c1");
  });
});
