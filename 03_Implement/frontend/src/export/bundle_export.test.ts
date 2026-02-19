import { describe, expect, test } from "vitest";
import type { DocumentV2 } from "../domain/types";
import JSZip from "jszip";
import { buildBundleZipBlob, buildExportBundle } from "./bundle_export";

const baseDoc: DocumentV2 = {
  version: 2,
  id: "doc-1",
  title: "Doc",
  createdAt: "2026-01-01T00:00:00.000Z",
  updatedAt: "2026-01-02T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    { id: "c1", text: "fact", x: 0, y: 0, claimType: "fact", textReviewed: true },
    { id: "c2", text: "claim", x: 10, y: 10, claimType: "claim", textReviewed: true },
  ],
  edges: [],
  islands: [{ id: "i1", cardIds: ["c1", "c2"], title: "Island", summaryText: "Summary", summaryReviewed: true }],
  evidenceLinks: [{ id: "e1", type: "supports", fromCardId: "c1", toCardId: "c2" }],
};

describe("buildExportBundle", () => {
  test("always includes document.json and view.json and sorted by path", () => {
    const files = buildExportBundle(baseDoc, { camera: { zoom: 1 } }, {
      rootFolderPath: "kj-atlas-export-20260101-010203",
      safeMode: true,
      includeOutline: false,
      includeDiagnostics: false,
      includeSelectedCardTraces: false,
      selectedCardId: null,
      deterministicNowIso: "2026-01-02T00:00:00.000Z",
      readingMode: "islands",
      reviewedOnly: false,
      readingState: {
        readingNavEnabled: false,
        readingIndex: 0,
        readingMode: "islands",
        reviewedOnly: false,
        safeMode: true,
        generatedAt: "2026-01-02T00:00:00.000Z",
      },
    });

    expect(files.map((file) => file.path)).toEqual([
      "kj-atlas-export-20260101-010203/document.json",
      "kj-atlas-export-20260101-010203/view.json",
    ]);
  });

  test("includes optional markdown files when requested", () => {
    const files = buildExportBundle(baseDoc, { camera: { zoom: 1 } }, {
      rootFolderPath: "kj-atlas-export-20260101-010203",
      safeMode: true,
      includeOutline: true,
      includeDiagnostics: true,
      includeSelectedCardTraces: true,
      selectedCardId: "c2",
      deterministicNowIso: "2026-01-02T00:00:00.000Z",
      readingMode: "islands",
      reviewedOnly: false,
      readingState: {
        readingNavEnabled: false,
        readingIndex: 0,
        readingMode: "islands",
        reviewedOnly: false,
        safeMode: true,
        generatedAt: "2026-01-02T00:00:00.000Z",
      },
    });

    expect(files.map((file) => file.path)).toContain("kj-atlas-export-20260101-010203/outline.md");
    expect(files.map((file) => file.path)).toContain("kj-atlas-export-20260101-010203/diagnostics.md");
    expect(files.map((file) => file.path)).toContain("kj-atlas-export-20260101-010203/evidence_trace_c2.md");
    expect(files.map((file) => file.path)).toContain("kj-atlas-export-20260101-010203/contradiction_trace_c2.md");
  });
  test("creates a readable zip archive", async () => {
    const files = buildExportBundle(baseDoc, { camera: { zoom: 1 } }, {
      rootFolderPath: "kj-atlas-export-20260101-010203",
      safeMode: true,
      includeOutline: true,
      includeDiagnostics: true,
      includeSelectedCardTraces: false,
      selectedCardId: null,
      deterministicNowIso: "2026-01-02T00:00:00.000Z",
      readingMode: "islands",
      reviewedOnly: false,
      readingState: {
        readingNavEnabled: false,
        readingIndex: 0,
        readingMode: "islands",
        reviewedOnly: false,
        safeMode: true,
        generatedAt: "2026-01-02T00:00:00.000Z",
      },
    });

    const blob = await buildBundleZipBlob(files);
    const zip = await JSZip.loadAsync(await blob.arrayBuffer());
    const archivePaths = Object.values(zip.files).filter((entry) => !entry.dir).map((entry) => entry.name).sort();
    expect(archivePaths).toEqual(files.map((file) => file.path));
  });

  test("safe mode bundle hides unreviewed outline text and diagnostic detail", () => {
    const docWithUnreviewed: DocumentV2 = {
      ...baseDoc,
      islands: [{ ...baseDoc.islands[0], summaryReviewed: false, summaryText: "SECRET_UNREVIEWED_SUMMARY" }],
    };

    const files = buildExportBundle(docWithUnreviewed, { camera: { zoom: 1 } }, {
      rootFolderPath: "kj-atlas-export-20260101-010203",
      safeMode: true,
      includeOutline: true,
      includeDiagnostics: true,
      includeSelectedCardTraces: false,
      selectedCardId: null,
      deterministicNowIso: "2026-01-02T00:00:00.000Z",
      readingMode: "islands",
      reviewedOnly: false,
      readingState: {
        readingNavEnabled: false,
        readingIndex: 0,
        readingMode: "islands",
        reviewedOnly: false,
        safeMode: true,
        generatedAt: "2026-01-02T00:00:00.000Z",
      },
      outlineOptions: {
        includeUnreviewedSummaries: true,
      },
      outlineQualityReport: {
        generatedAt: "2026-01-02T00:00:00.000Z",
        stats: {
          totalIslands: 1,
          totalCardsInPath: 2,
          islandsWithTitleMissing: 0,
          islandsWithSummaryMissing: 0,
          islandsUnreviewed: 1,
          relationSummariesTotal: 0,
          relationSummariesUnreviewed: 0,
          disconnectedIslands: 0,
          pathLength: 1,
        },
        findings: [{ severity: "warn", code: "QX", title: "title", detail: "SECRET_DIAGNOSTIC_DETAIL", entityRefs: [{ kind: "island", id: "i1" }] }],
      },
    });

    const outline = String(files.find((file) => file.path.endsWith('/outline.md'))?.content ?? '');
    const diagnostics = String(files.find((file) => file.path.endsWith('/diagnostics.md'))?.content ?? '');

    expect(outline).not.toContain("SECRET_UNREVIEWED_SUMMARY");
    expect(diagnostics).not.toContain("SECRET_DIAGNOSTIC_DETAIL");
  });

});
