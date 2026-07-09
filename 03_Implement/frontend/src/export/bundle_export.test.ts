import { afterEach, describe, expect, test, vi } from "vitest";
import type { DocumentV2 } from "../domain/types";
import JSZip from "jszip";
import { buildBundleZipBlob, buildExportBundle, buildExportBundleWithWorkers } from "./bundle_export";
import { canonicalizeJson } from "../domain/patch/patch_fingerprint";
import evidenceAddBaseRaw from "../../tests/fixtures/review-selective-merge/evidence-add.base.json?raw";
import evidenceAddIncomingRaw from "../../tests/fixtures/review-selective-merge/evidence-add.incoming.json?raw";
import claimTypeBaseRaw from "../../tests/fixtures/review-selective-merge/claim-type.base.json?raw";
import claimTypeIncomingRaw from "../../tests/fixtures/review-selective-merge/claim-type.incoming.json?raw";


const originalWorker = globalThis.Worker;
afterEach(() => {
  globalThis.Worker = originalWorker;
});

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
  mergeSuggestionDecisions: [
    {
      id: "decision-1",
      groupId: "group-1",
      decision: "accept",
      decidedAt: "2026-01-02T00:00:00.000Z",
      cardIds: ["c2", "c1"],
      mergedTextDraft: "fact+claim",
      editedText: "fact claim",
    },
  ],
};

async function sha256Hex(input: string): Promise<string> {
  const bytes = new TextEncoder().encode(input);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest))
    .map((value) => value.toString(16).padStart(2, "0"))
    .join("");
}

async function documentJsonHashFromBundle(doc: DocumentV2, viewState: unknown): Promise<string> {
  const files = buildExportBundle(doc, viewState, {
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

  const documentFile = files.find((file) => file.path.endsWith("/document.json"));
  if (!documentFile || typeof documentFile.content !== "string") {
    throw new Error("document.json not found in bundle output");
  }

  const canonical = canonicalizeJson(JSON.parse(documentFile.content));
  return sha256Hex(canonical);
}

function parseFixture(raw: string): DocumentV2 {
  return JSON.parse(raw) as DocumentV2;
}

describe("buildExportBundle", () => {
  test("keeps document.json hash stable across ja/en locale switch", async () => {
    const jaViewState = {
      camera: { zoom: 1 },
      ui: { locale: "ja", labels: { exportButton: "エクスポート" } },
    };
    const enViewState = {
      camera: { zoom: 1 },
      ui: { locale: "en", labels: { exportButton: "Export" } },
    };

    const jaHash = await documentJsonHashFromBundle(baseDoc, jaViewState);
    const enHash = await documentJsonHashFromBundle(baseDoc, enViewState);

    expect(jaHash).toBe(enHash);

    const files = buildExportBundle(baseDoc, enViewState, {
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
    const documentFile = files.find((file) => file.path.endsWith("/document.json"));
    expect(documentFile).toBeDefined();
    const documentJson = JSON.parse(String(documentFile?.content)) as Record<string, unknown>;
    expect(documentJson).not.toHaveProperty("ui");
    expect(documentJson).not.toHaveProperty("locale");
  });

  test("fixture documents keep deterministic document.json hash regardless of locale-specific view state", async () => {
    const fixtures = [
      parseFixture(evidenceAddBaseRaw),
      parseFixture(evidenceAddIncomingRaw),
      parseFixture(claimTypeBaseRaw),
      parseFixture(claimTypeIncomingRaw),
    ];

    for (const fixture of fixtures) {
      const jaHash = await documentJsonHashFromBundle(fixture, { locale: "ja", sidePanel: { tab: "share" } });
      const enHash = await documentJsonHashFromBundle(fixture, { locale: "en", sidePanel: { tab: "share" } });
      expect(jaHash).toBe(enHash);
    }
  });

  test("writes bundle manifest with selected export granularity", () => {
    const files = buildExportBundle(baseDoc, { camera: { zoom: 1 } }, {
      rootFolderPath: "kj-atlas-export-20260101-010203",
      safeMode: true,
      includeOutline: false,
      includeDiagnostics: false,
      includeSelectedCardTraces: true,
      selectedCardId: "c2",
      exportGranularity: "overview",
      viewVisibility: "Unlisted",
      packVisibility: "Org",
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

    const manifestRaw = files.find((file) => file.path.endsWith("/bundle_manifest.json"));
    expect(manifestRaw).toBeDefined();
    const manifest = JSON.parse(String(manifestRaw?.content)) as {
      exportGranularity: string;
      generatedAt: string;
      visibility?: { view?: string; pack?: string };
    };
    expect(manifest.exportGranularity).toBe("overview");
    expect(manifest.generatedAt).toBe("2026-01-02T00:00:00.000Z");
    expect(manifest.visibility).toEqual({ view: "Unlisted", pack: "Org" });
  });

  test("always includes document.json, merge_decision_audit.json and view.json sorted by path", () => {
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
      "kj-atlas-export-20260101-010203/bundle_manifest.json",
      "kj-atlas-export-20260101-010203/document.json",
      "kj-atlas-export-20260101-010203/merge_decision_audit.json",
      "kj-atlas-export-20260101-010203/view.json",
    ]);
  });

  test("merge decision audit json contains representative-source traceability", () => {
    const docWithRepresentative: DocumentV2 = {
      ...baseDoc,
      cards: [
        { id: "c1", text: "fact", x: 0, y: 0, claimType: "fact", textReviewed: true, mergedIntoCardId: "c-rep" },
        { id: "c2", text: "claim", x: 10, y: 10, claimType: "claim", textReviewed: true, mergedIntoCardId: "c-rep" },
        { id: "c-rep", text: "rep", x: 20, y: 20, repOf: ["c1", "c2"] },
      ],
    };
    const files = buildExportBundle(docWithRepresentative, { camera: { zoom: 1 } }, {
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

    const auditRaw = files.find((file) => file.path.endsWith("/merge_decision_audit.json"));
    expect(auditRaw).toBeDefined();
    const parsed = JSON.parse(String(auditRaw?.content)) as { entries: Array<Record<string, unknown>> };
    expect(parsed.entries).toEqual([
      {
        actorType: "human",
        cardIds: ["c1", "c2"],
        decisionId: "decision-1",
        decisionType: "accept",
        decidedAt: "2026-01-02T00:00:00.000Z",
        groupId: "group-1",
        representativeCardId: "c-rep",
        representativeResolvedBy: "repOf",
        sourceCardIds: ["c1", "c2"],
        missingSourceCardIds: [],
      },
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
    expect(files.map((file) => file.path)).toContain("kj-atlas-export-20260101-010203/trace_analytics_c2.md");
  });

  test("overview granularity suppresses selected-card traces", () => {
    const files = buildExportBundle(baseDoc, { camera: { zoom: 1 } }, {
      rootFolderPath: "kj-atlas-export-20260101-010203",
      safeMode: true,
      includeOutline: true,
      includeDiagnostics: true,
      includeSelectedCardTraces: true,
      selectedCardId: "c2",
      exportGranularity: "overview",
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

    expect(files.map((file) => file.path)).not.toContain("kj-atlas-export-20260101-010203/evidence_trace_c2.md");
    expect(files.map((file) => file.path)).not.toContain("kj-atlas-export-20260101-010203/contradiction_trace_c2.md");
    expect(files.map((file) => file.path)).not.toContain("kj-atlas-export-20260101-010203/trace_analytics_c2.md");
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
  test("defaults to safe mode for exports when context.safeMode is omitted", () => {
    const docWithSecret: DocumentV2 = {
      ...baseDoc,
      cards: baseDoc.cards.map((card) => ({ ...card, text: card.id === "c2" ? "SECRET_TEXT_DO_NOT_LEAK" : card.text })),
      islands: [{ ...baseDoc.islands[0], summaryReviewed: false, summaryText: "SECRET_TEXT_DO_NOT_LEAK" }],
    };

    const files = buildExportBundle(docWithSecret, { camera: { zoom: 1 } }, {
      rootFolderPath: "kj-atlas-export-20260101-010203",
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

    const markdownJoined = files
      .filter((file) => file.mime === "text/markdown")
      .map((file) => String(file.content))
      .join("\n");
    expect(markdownJoined).not.toContain("SECRET_TEXT_DO_NOT_LEAK");
  });

  test("strips Card.meta from shared document.json by default (schemas.md 15.4)", () => {
    const docWithMeta: DocumentV2 = {
      ...baseDoc,
      cards: baseDoc.cards.map((card) =>
        card.id === "c1" ? { ...card, meta: { seq: 7, source: "INTERVIEW_A_LINE_12" } } : card,
      ),
    };

    const files = buildExportBundle(docWithMeta, { camera: { zoom: 1 } }, {
      rootFolderPath: "kj-atlas-export-20260101-010203",
      safeMode: false,
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
        safeMode: false,
        generatedAt: "2026-01-02T00:00:00.000Z",
      },
    });

    const documentJson = String(files.find((file) => file.path.endsWith("/document.json"))?.content ?? "");
    expect(documentJson).not.toContain("INTERVIEW_A_LINE_12");
    expect(documentJson).not.toContain('"meta"');
    // The working document must stay untouched — only the shared copy is stripped.
    expect(docWithMeta.cards.find((card) => card.id === "c1")?.meta).toEqual({ seq: 7, source: "INTERVIEW_A_LINE_12" });
  });

  test("keeps Card.meta in shared document.json when includeSourceReferences is opted in", () => {
    const docWithMeta: DocumentV2 = {
      ...baseDoc,
      cards: baseDoc.cards.map((card) =>
        card.id === "c1" ? { ...card, meta: { seq: 7, source: "INTERVIEW_A_LINE_12" } } : card,
      ),
    };

    const files = buildExportBundle(docWithMeta, { camera: { zoom: 1 } }, {
      rootFolderPath: "kj-atlas-export-20260101-010203",
      safeMode: true,
      includeOutline: false,
      includeDiagnostics: false,
      includeSelectedCardTraces: false,
      selectedCardId: null,
      deterministicNowIso: "2026-01-02T00:00:00.000Z",
      readingMode: "islands",
      reviewedOnly: false,
      includeSourceReferences: true,
      readingState: {
        readingNavEnabled: false,
        readingIndex: 0,
        readingMode: "islands",
        reviewedOnly: false,
        safeMode: true,
        generatedAt: "2026-01-02T00:00:00.000Z",
      },
    });

    const documentJson = String(files.find((file) => file.path.endsWith("/document.json"))?.content ?? "");
    const parsed = JSON.parse(documentJson) as DocumentV2;
    expect(parsed.cards.find((card) => card.id === "c1")?.meta).toEqual({ seq: 7, source: "INTERVIEW_A_LINE_12" });
  });

  test("worker bundle path also strips Card.meta by default", async () => {
    globalThis.Worker = class {
      constructor() {
        throw new Error("worker unavailable");
      }
    } as unknown as typeof Worker;
    vi.spyOn(console, "warn").mockImplementation(() => {});

    const docWithMeta: DocumentV2 = {
      ...baseDoc,
      cards: baseDoc.cards.map((card) =>
        card.id === "c1" ? { ...card, meta: { seq: 7, source: "INTERVIEW_A_LINE_12" } } : card,
      ),
    };

    const files = await buildExportBundleWithWorkers(docWithMeta, { camera: { zoom: 1 } }, {
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

    const documentJson = String(files.find((file) => file.path.endsWith("/document.json"))?.content ?? "");
    expect(documentJson).not.toContain("INTERVIEW_A_LINE_12");
    // integrity.json must hash the stripped document, so it must not embed the raw reference either.
    const joined = files.map((file) => String(file.content)).join("\n");
    expect(joined).not.toContain("INTERVIEW_A_LINE_12");
  });

  test("falls back when worker init fails and still emits diagnostics/traces", async () => {
    globalThis.Worker = class {
      constructor() {
        throw new Error("worker unavailable");
      }
    } as unknown as typeof Worker;
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});

    const files = await buildExportBundleWithWorkers(baseDoc, { camera: { zoom: 1 } }, {
      rootFolderPath: "kj-atlas-export-20260101-010203",
      safeMode: true,
      includeOutline: false,
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

    expect(files.map((file) => file.path)).toContain("kj-atlas-export-20260101-010203/diagnostics.md");
    expect(files.map((file) => file.path)).toContain("kj-atlas-export-20260101-010203/evidence_trace_c2.md");
    expect(files.map((file) => file.path)).toContain("kj-atlas-export-20260101-010203/contradiction_trace_c2.md");
    expect(files.map((file) => file.path)).toContain("kj-atlas-export-20260101-010203/trace_analytics_c2.md");
    expect(warn).toHaveBeenCalled();
  });


test("uses bundle zip worker progress/result when available", async () => {
  const postMessage = vi.fn();
  globalThis.Worker = class {
    private readonly listeners = new Set<(event: MessageEvent) => void>();

    constructor() {}

    addEventListener(_type: string, listener: (event: MessageEvent) => void): void {
      this.listeners.add(listener);
    }

    removeEventListener(_type: string, listener: (event: MessageEvent) => void): void {
      this.listeners.delete(listener);
    }

    postMessage(message: { requestId: string }): void {
      postMessage(message);
      const zip = new JSZip();
      zip.file("a.txt", "a");
      void zip.generateAsync({ type: "arraybuffer" }).then((buffer) => {
        for (const listener of this.listeners) {
          listener({ data: { type: "bundle.zip.progress", requestId: message.requestId, percent: 55 } } as MessageEvent);
          listener({ data: { type: "bundle.zip.result", requestId: message.requestId, result: { zipBuffer: buffer } } } as MessageEvent);
        }
      });
    }

    terminate(): void {}
  } as unknown as typeof Worker;

  const progress: number[] = [];
  const blob = await buildBundleZipBlob([{ path: "a.txt", content: "a", mime: "text/plain" }], {
    onProgress: (percent) => progress.push(percent),
  });

  expect(postMessage).toHaveBeenCalledOnce();
  expect(progress).toContain(55);
  const zip = await JSZip.loadAsync(await blob.arrayBuffer());
  expect(Object.keys(zip.files)).toContain("a.txt");
});

test("falls back to main-thread zip when bundle worker init fails", async () => {
  globalThis.Worker = class {
    constructor() {
      throw new Error("worker unavailable");
    }
  } as unknown as typeof Worker;
  const warn = vi.spyOn(console, "warn").mockImplementation(() => {});

  const blob = await buildBundleZipBlob([{ path: "b.txt", content: "b", mime: "text/plain" }]);
  const zip = await JSZip.loadAsync(await blob.arrayBuffer());

  expect(Object.keys(zip.files)).toContain("b.txt");
  expect(warn).toHaveBeenCalled();
});

test("returns cancellation error when bundle zip is aborted", async () => {
  let capturedRequestId = "";
  globalThis.Worker = class {
    private readonly listeners = new Set<(event: MessageEvent) => void>();

    constructor() {}

    addEventListener(_type: string, listener: (event: MessageEvent) => void): void {
      this.listeners.add(listener);
    }

    removeEventListener(_type: string, listener: (event: MessageEvent) => void): void {
      this.listeners.delete(listener);
    }

    postMessage(message: { type: string; requestId: string }): void {
      if (message.type === "bundle.zip.request") {
        capturedRequestId = message.requestId;
        return;
      }

      if (message.type === "bundle.zip.cancel") {
        for (const listener of this.listeners) {
          listener({ data: { type: "bundle.zip.cancelled", requestId: capturedRequestId } } as MessageEvent);
        }
      }
    }

    terminate(): void {}
  } as unknown as typeof Worker;

  const controller = new AbortController();
  const promise = buildBundleZipBlob([{ path: "c.txt", content: "c", mime: "text/plain" }], {
    signal: controller.signal,
  });

  controller.abort();

  await expect(promise).rejects.toThrow("Bundle zip cancelled");
});


});
