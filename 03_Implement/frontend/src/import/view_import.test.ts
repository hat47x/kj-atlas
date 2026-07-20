import { describe, expect, test } from "vitest";
import { buildExportViewMetadata } from "../export/view_metadata";
import { t } from "../i18n/translate";
import { parseViewJson } from "./view_import";

describe("parseViewJson", () => {
  test("returns invalid json error", () => {
    const result = parseViewJson("{");
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error).toContain(t("app.status.import.view_json_invalid"));
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
        hierarchyLevel: "mid",
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
      expect(result.metadata.viewState.hierarchyLevel).toBe("mid");
      expect(result.metadata.visibility).toBe("Restricted");
    }
  });


  test("loads legacy metadata without visibility using Restricted fallback", () => {
    const result = parseViewJson(JSON.stringify({
      version: "1",
      generatedAt: "2026-01-01T00:00:00.000Z",
      docSignature: "legacy",
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: false,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: false,
      },
      export: { mode: "viewport" },
    }));

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.metadata.visibility).toBe("Restricted");
    }
  });

  test("preserves each supported visibility value via export/import roundtrip", () => {
    const visibilities = ["Public", "Unlisted", "Org", "Restricted"] as const;

    for (const visibility of visibilities) {
      const metadata = buildExportViewMetadata({
        doc: { id: `doc-${visibility.toLowerCase()}`, title: "Doc" },
        camera: { panX: 0, panY: 0, zoom: 1 },
        viewState: {
          summaryView: false,
          abstractMapView: false,
          hideSourceCards: false,
          maxDepth: "all",
          focusIslandId: null,
          showReadingOrder: false,
        },
        exportMode: "viewport",
      });

      const result = parseViewJson(JSON.stringify({ ...metadata, visibility }));
      expect(result.ok).toBe(true);
      if (result.ok) {
        expect(result.metadata.visibility).toBe(visibility);
      }
    }
  });
});

test("preserves locale from view metadata", () => {
  const metadata = buildExportViewMetadata({
    doc: { id: "doc-locale", title: "Doc Locale" },
    camera: { panX: 0, panY: 0, zoom: 1 },
    viewState: {
      summaryView: false,
      abstractMapView: false,
      hideSourceCards: false,
      maxDepth: "all",
      focusIslandId: null,
      showReadingOrder: false,
      locale: "en",
    },
    exportMode: "viewport",
  });

  const result = parseViewJson(JSON.stringify(metadata));
  expect(result.ok).toBe(true);
  if (result.ok) {
    expect(result.metadata.viewState.locale).toBe("en");
  }
});
