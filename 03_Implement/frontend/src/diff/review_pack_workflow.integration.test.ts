import { describe, expect, it } from "vitest";
import JSZip from "jszip";
import { appendMergeAuditEntry, createMergeAuditEntry, MERGE_AUDIT_LOG_LIMIT, type MergeAuditEntry } from "../domain/view/audit_log";
import { buildExportBundle, buildBundleZipBlob } from "../export/bundle_export";
import { parseDocumentJson } from "../import/document_import";
import { sanitizeMarkdownForDisplay } from "../import/markdown_sanitize";
import { parseViewJson } from "../import/view_import";
import { detectReviewPackFiles, readZipFiles, ZipImportError } from "../import/zip_import";
import { applySelectedMergeItemsAtomic } from "./merge_apply";
import { buildMergeItems } from "./merge_items";
import { loadReviewPackFixtureFile } from "../../tests/utils/review_pack_fixture";

function requireStringEntry(entries: Map<string, Uint8Array | string>, path: string | null): string {
  if (!path) {
    throw new Error("missing fixture path");
  }
  const value = entries.get(path);
  if (typeof value !== "string") {
    throw new Error(`missing string entry: ${path}`);
  }
  return value;
}

function countViewMetadataDiffs(baseText: string, incomingText: string): number {
  const base = parseViewJson(baseText);
  const incoming = parseViewJson(incomingText);
  if (!base.ok || !incoming.ok) {
    throw new Error("invalid view fixture json");
  }

  let count = 0;
  if (base.metadata.camera.panX !== incoming.metadata.camera.panX) count += 1;
  if (base.metadata.camera.panY !== incoming.metadata.camera.panY) count += 1;
  if (base.metadata.camera.zoom !== incoming.metadata.camera.zoom) count += 1;
  if (base.metadata.viewState.perspectiveMode !== incoming.metadata.viewState.perspectiveMode) count += 1;
  return count;
}

describe("review pack full workflow integration", () => {
  it("imports, diffs, selectively merges, audits, exports, and sanitizes deterministically", async () => {
    const baseZip = await loadReviewPackFixtureFile("base_pack.zip");
    const incomingZip = await loadReviewPackFixtureFile("incoming_pack.zip");

    const baseImport = await readZipFiles(baseZip);
    const incomingImport = await readZipFiles(incomingZip);

    const basePaths = detectReviewPackFiles(baseImport.entries);
    const incomingPaths = detectReviewPackFiles(incomingImport.entries);

    const baseDocumentText = requireStringEntry(baseImport.entries, basePaths.documentPath);
    const incomingDocumentText = requireStringEntry(incomingImport.entries, incomingPaths.documentPath);
    const baseViewText = requireStringEntry(baseImport.entries, basePaths.viewPath);
    const incomingViewText = requireStringEntry(incomingImport.entries, incomingPaths.viewPath);
    const diagnosticsText = requireStringEntry(baseImport.entries, basePaths.diagnosticsPath);

    const parsedBaseDocument = parseDocumentJson(baseDocumentText);
    const parsedIncomingDocument = parseDocumentJson(incomingDocumentText);
    const parsedIncomingView = parseViewJson(incomingViewText);
    expect(parsedBaseDocument.ok).toBe(true);
    expect(parsedIncomingDocument.ok).toBe(true);
    expect(parsedIncomingView.ok).toBe(true);
    if (!parsedBaseDocument.ok || !parsedIncomingDocument.ok || !parsedIncomingView.ok) {
      return;
    }

    const baseDocument = parsedBaseDocument.document;
    const incomingDocument = parsedIncomingDocument.document;

    expect(baseDocument.cards).toHaveLength(2);

    const mergeItems = buildMergeItems(baseDocument, incomingDocument);
    const claimTypeItem = mergeItems.find(
      (item) => item.kind === "card.field" && item.entityRef.id === "c1" && item.field === "claimType"
    );
    const evidenceAddItem = mergeItems.find((item) => item.kind === "evidence.add" && item.entityRef.id === "e-support-1");
    expect(claimTypeItem).toBeDefined();
    expect(evidenceAddItem).toBeDefined();
    expect(mergeItems.filter((item) => item.kind !== "view.field").length).toBeGreaterThanOrEqual(1);
    expect(countViewMetadataDiffs(baseViewText, incomingViewText)).toBeGreaterThanOrEqual(1);

    const claimResult = applySelectedMergeItemsAtomic(baseDocument, baseDocument, incomingDocument, [claimTypeItem!]);
    expect(claimResult.ok).toBe(true);
    if (!claimResult.ok) {
      return;
    }
    expect(claimResult.document.cards.find((card) => card.id === "c1")?.claimType).toBe("claim");

    const evidenceResult = applySelectedMergeItemsAtomic(claimResult.document, baseDocument, incomingDocument, [evidenceAddItem!]);
    expect(evidenceResult.ok).toBe(true);
    if (!evidenceResult.ok) {
      return;
    }
    expect(evidenceResult.document.evidenceLinks).toEqual([
      { id: "e-support-1", type: "supports", fromCardId: "c2", toCardId: "c1" },
    ]);

    const auditEntry = createMergeAuditEntry([claimTypeItem!, evidenceAddItem!], { kind: "zip", fileName: "incoming_pack.zip" }, "2026-02-21T02:00:00.000Z");
    expect(auditEntry.summary.byKind["card.field"]).toBe(1);
    expect(auditEntry.summary.byKind["evidence.add"]).toBe(1);
    expect(JSON.stringify(auditEntry)).not.toContain("Alpha");
    expect(JSON.stringify(auditEntry)).not.toContain("Beta");

    const existingAudit: MergeAuditEntry[] = Array.from({ length: MERGE_AUDIT_LOG_LIMIT }, (_, index) => ({
      id: `entry-${index}`,
      createdAt: `2026-02-21T00:${String(index).padStart(2, "0")}:00.000Z`,
      source: { kind: "unknown" },
      summary: { totalItems: 1, byKind: { "card.field": 1 } },
      details: { itemIds: { ids: [`old-${index}`] } },
    }));
    const appended = appendMergeAuditEntry({ mergeAuditLog: existingAudit }, auditEntry).mergeAuditLog ?? [];
    expect(appended).toHaveLength(MERGE_AUDIT_LOG_LIMIT);
    expect(appended[0]?.id).toBe("entry-1");
    expect(appended[appended.length - 1]?.id).toBe(auditEntry.id);

    const sanitizedDiagnostics = sanitizeMarkdownForDisplay(diagnosticsText);
    expect(sanitizedDiagnostics).not.toContain("<script>");
    expect(sanitizedDiagnostics).toContain("alert(1)");

    const exportFiles = buildExportBundle(
      evidenceResult.document,
      parsedIncomingView.metadata,
      {
        rootFolderPath: "kj-atlas-review-pack-20260221-020000",
        safeMode: false,
        includeOutline: false,
        includeDiagnostics: false,
        includeSelectedCardTraces: false,
        selectedCardId: null,
        deterministicNowIso: "2026-02-21T02:00:00.000Z",
        readingState: {
          readingNavEnabled: false,
          readingIndex: 0,
          readingMode: "islands",
          reviewedOnly: false,
          safeMode: false,
          generatedAt: "2026-02-21T02:00:00.000Z",
        },
        readingMode: "islands",
        reviewedOnly: false,
      }
    );
    const exportZipBlob = await buildBundleZipBlob(exportFiles);
    const exportZip = await JSZip.loadAsync(await exportZipBlob.arrayBuffer());
    const exportPaths = Object.keys(exportZip.files);
    expect(exportPaths.some((path) => path.endsWith("/document.json"))).toBe(true);
    expect(exportPaths.some((path) => path.endsWith("/view.json"))).toBe(true);
  });

  it("rejects path traversal review packs with explicit Z002", async () => {
    const maliciousZip = await loadReviewPackFixtureFile("malicious_pack.zip");

    let failure: unknown = null;
    try {
      await readZipFiles(maliciousZip);
    } catch (error) {
      failure = error;
    }

    expect(failure).toBeInstanceOf(ZipImportError);
    expect((failure as ZipImportError).code).toBe("Z002");
    expect(String((failure as Error).message)).toContain("Z002");
  });
});
