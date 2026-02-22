import { describe, expect, test } from "vitest";
import { buildExportViewMetadata } from "../export/view_metadata";
import { parseViewJson } from "./view_import";

describe("parseViewJson", () => {
  test("returns invalid json error", () => {
    const result = parseViewJson("{");
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error).toContain("Invalid JSON in view.json");
    }
  });

  test("preserves collapsedIslandIds via export/import roundtrip", () => {
    const metadata = buildExportViewMetadata({
      doc: { id: "doc-1", title: "Doc 1" },
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: false,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: false,
        collapsedIslandIds: ["island-b", "island-a"],
      },
      exportMode: "viewport",
    });

    const result = parseViewJson(JSON.stringify(metadata));
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.metadata.viewState.collapsedIslandIds).toEqual(["island-a", "island-b"]);
    }
  });

});
