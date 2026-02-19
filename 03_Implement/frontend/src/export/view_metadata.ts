import type { DocumentV2 } from "../domain/types";
import type { LODLevel, LODThresholds } from "../domain/view/lod";

export type ExportViewMetadata = {
  version: "1";
  generatedAt: string;
  docSignature: string;
  camera: {
    panX: number;
    panY: number;
    zoom: number;
  };
  viewState: {
    summaryView: boolean;
    abstractMapView: boolean;
    hideSourceCards: boolean;
    maxDepth: number | "all";
    focusIslandId: string | null;
    showReadingOrder: boolean;
    editReadingOrder?: boolean;
    readingNavEnabled?: boolean;
    readingIndex?: number;
    readingMode?: "islands" | "islands+cards";
    reviewedOnly?: boolean;
    safeMode?: boolean;
    lodEnabled?: boolean;
    lodThresholds?: LODThresholds;
    lodLevelOverride?: LODLevel | null;
    lodShowLoneWolvesWhenFar?: boolean;
    resolvedLodLevel?: LODLevel;
    evidenceOverlayEnabled?: boolean;
    evidenceOverlayMode?: "supports" | "contradicts" | "both";
    evidenceOverlayDepth?: number;
    evidenceOverlayScope?: "all" | "selection";
    evidenceOverlayDimOthers?: boolean;
  };
  export: {
    mode: "viewport" | "bounds";
    bounds?: {
      x: number;
      y: number;
      w: number;
      h: number;
    };
    padding?: number;
  };
  notes?: string;
};

type ExportViewMetadataArgs = {
  doc: Pick<DocumentV2, "id" | "title"> | null;
  camera: {
    panX: number;
    panY: number;
    zoom: number;
  };
  viewState: {
    summaryView: boolean;
    abstractMapView: boolean;
    hideSourceCards: boolean;
    maxDepth: number | "all";
    focusIslandId: string | null;
    showReadingOrder: boolean;
    editReadingOrder?: boolean;
    readingNavEnabled?: boolean;
    readingIndex?: number;
    readingMode?: "islands" | "islands+cards";
    reviewedOnly?: boolean;
    safeMode?: boolean;
    lodEnabled?: boolean;
    lodThresholds?: LODThresholds;
    lodLevelOverride?: LODLevel | null;
    lodShowLoneWolvesWhenFar?: boolean;
    resolvedLodLevel?: LODLevel;
    evidenceOverlayEnabled?: boolean;
    evidenceOverlayMode?: "supports" | "contradicts" | "both";
    evidenceOverlayDepth?: number;
    evidenceOverlayScope?: "all" | "selection";
    evidenceOverlayDimOthers?: boolean;
  };
  exportMode: "viewport" | "bounds";
  bounds?: {
    x: number;
    y: number;
    w: number;
    h: number;
  };
  padding?: number;
  generatedAt?: string;
};

function hashTitle(value: string): string {
  let hash = 0;
  for (let index = 0; index < value.length; index += 1) {
    hash = (hash * 31 + value.charCodeAt(index)) >>> 0;
  }

  return hash.toString(16).padStart(8, "0");
}

function resolveDocSignature(doc: Pick<DocumentV2, "id" | "title"> | null): string {
  if (!doc) {
    return "unknown";
  }

  if (doc.id && doc.id.trim().length > 0) {
    return doc.id;
  }

  const title = doc.title?.trim();
  if (!title) {
    return "unknown";
  }

  return `title-${hashTitle(title)}`;
}

export function buildExportViewMetadata({ doc, camera, viewState, exportMode, bounds, padding, generatedAt }: ExportViewMetadataArgs): ExportViewMetadata {
  return {
    version: "1",
    generatedAt: generatedAt ?? new Date().toISOString(),
    docSignature: resolveDocSignature(doc),
    camera: {
      panX: camera.panX,
      panY: camera.panY,
      zoom: camera.zoom,
    },
    viewState: {
      summaryView: viewState.summaryView,
      abstractMapView: viewState.abstractMapView,
      hideSourceCards: viewState.hideSourceCards,
      maxDepth: viewState.maxDepth,
      focusIslandId: viewState.focusIslandId,
      showReadingOrder: viewState.showReadingOrder,
      ...(viewState.editReadingOrder === undefined ? {} : { editReadingOrder: viewState.editReadingOrder }),
      ...(viewState.readingNavEnabled === undefined ? {} : { readingNavEnabled: viewState.readingNavEnabled }),
      ...(viewState.readingIndex === undefined ? {} : { readingIndex: viewState.readingIndex }),
      ...(viewState.readingMode === undefined ? {} : { readingMode: viewState.readingMode }),
      ...(viewState.reviewedOnly === undefined ? {} : { reviewedOnly: viewState.reviewedOnly }),
      ...(viewState.safeMode === undefined ? {} : { safeMode: viewState.safeMode }),
      ...(viewState.lodEnabled === undefined ? {} : { lodEnabled: viewState.lodEnabled }),
      ...(viewState.lodThresholds === undefined ? {} : { lodThresholds: viewState.lodThresholds }),
      ...(viewState.lodLevelOverride === undefined ? {} : { lodLevelOverride: viewState.lodLevelOverride }),
      ...(viewState.lodShowLoneWolvesWhenFar === undefined
        ? {}
        : { lodShowLoneWolvesWhenFar: viewState.lodShowLoneWolvesWhenFar }),
      ...(viewState.resolvedLodLevel === undefined ? {} : { resolvedLodLevel: viewState.resolvedLodLevel }),
      ...(viewState.evidenceOverlayEnabled === undefined ? {} : { evidenceOverlayEnabled: viewState.evidenceOverlayEnabled }),
      ...(viewState.evidenceOverlayMode === undefined ? {} : { evidenceOverlayMode: viewState.evidenceOverlayMode }),
      ...(viewState.evidenceOverlayDepth === undefined ? {} : { evidenceOverlayDepth: viewState.evidenceOverlayDepth }),
      ...(viewState.evidenceOverlayScope === undefined ? {} : { evidenceOverlayScope: viewState.evidenceOverlayScope }),
      ...(viewState.evidenceOverlayDimOthers === undefined ? {} : { evidenceOverlayDimOthers: viewState.evidenceOverlayDimOthers }),
    },
    export: {
      mode: exportMode,
      ...(bounds ? { bounds } : {}),
      ...(padding === undefined ? {} : { padding }),
    },
    notes: "",
  };
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function readRequiredBoolean(value: Record<string, unknown>, key: string): { ok: true; value: boolean } | { ok: false; error: string } {
  if (typeof value[key] !== "boolean") {
    return { ok: false, error: `viewState.${key} must be a boolean` };
  }

  return { ok: true, value: value[key] };
}

export function validateImportViewMetadata(value: unknown): { ok: true; metadata: ExportViewMetadata } | { ok: false; error: string } {
  if (!isObject(value)) {
    return { ok: false, error: "Metadata must be a JSON object" };
  }

  if (value.version !== "1") {
    return { ok: false, error: "metadata.version must be \"1\"" };
  }

  if (typeof value.generatedAt !== "string") {
    return { ok: false, error: "metadata.generatedAt must be a string" };
  }

  if (typeof value.docSignature !== "string") {
    return { ok: false, error: "metadata.docSignature must be a string" };
  }

  if (!isObject(value.camera)) {
    return { ok: false, error: "metadata.camera must be an object" };
  }

  if (typeof value.camera.panX !== "number" || !Number.isFinite(value.camera.panX)) {
    return { ok: false, error: "metadata.camera.panX must be a finite number" };
  }

  if (typeof value.camera.panY !== "number" || !Number.isFinite(value.camera.panY)) {
    return { ok: false, error: "metadata.camera.panY must be a finite number" };
  }

  if (typeof value.camera.zoom !== "number" || !Number.isFinite(value.camera.zoom) || value.camera.zoom <= 0) {
    return { ok: false, error: "metadata.camera.zoom must be a finite number > 0" };
  }

  if (!isObject(value.viewState)) {
    return { ok: false, error: "metadata.viewState must be an object" };
  }

  const summaryViewResult = readRequiredBoolean(value.viewState, "summaryView");
  if (!summaryViewResult.ok) {
    return summaryViewResult;
  }

  const abstractMapViewResult = readRequiredBoolean(value.viewState, "abstractMapView");
  if (!abstractMapViewResult.ok) {
    return abstractMapViewResult;
  }

  const hideSourceCardsResult = readRequiredBoolean(value.viewState, "hideSourceCards");
  if (!hideSourceCardsResult.ok) {
    return hideSourceCardsResult;
  }

  const showReadingOrderResult = readRequiredBoolean(value.viewState, "showReadingOrder");
  if (!showReadingOrderResult.ok) {
    return showReadingOrderResult;
  }

  const maxDepth = value.viewState.maxDepth;
  if (!(maxDepth === "all" || (typeof maxDepth === "number" && Number.isFinite(maxDepth) && maxDepth >= 0))) {
    return { ok: false, error: 'viewState.maxDepth must be "all" or a number >= 0' };
  }

  const focusIslandId = value.viewState.focusIslandId;
  if (!(focusIslandId === null || typeof focusIslandId === "string")) {
    return { ok: false, error: "viewState.focusIslandId must be a string or null" };
  }

  if (value.viewState.editReadingOrder !== undefined && typeof value.viewState.editReadingOrder !== "boolean") {
    return { ok: false, error: "viewState.editReadingOrder must be a boolean when present" };
  }

  if (value.viewState.readingNavEnabled !== undefined && typeof value.viewState.readingNavEnabled !== "boolean") {
    return { ok: false, error: "viewState.readingNavEnabled must be a boolean when present" };
  }

  if (
    value.viewState.readingIndex !== undefined &&
    (typeof value.viewState.readingIndex !== "number" || !Number.isInteger(value.viewState.readingIndex) || value.viewState.readingIndex < 0)
  ) {
    return { ok: false, error: "viewState.readingIndex must be an integer >= 0 when present" };
  }

  if (
    value.viewState.readingMode !== undefined &&
    value.viewState.readingMode !== "islands" &&
    value.viewState.readingMode !== "islands+cards"
  ) {
    return { ok: false, error: 'viewState.readingMode must be "islands" | "islands+cards" when present' };
  }

  if (value.viewState.reviewedOnly !== undefined && typeof value.viewState.reviewedOnly !== "boolean") {
    return { ok: false, error: "viewState.reviewedOnly must be a boolean when present" };
  }

  if (value.viewState.safeMode !== undefined && typeof value.viewState.safeMode !== "boolean") {
    return { ok: false, error: "viewState.safeMode must be a boolean when present" };
  }

  if (value.viewState.lodEnabled !== undefined && typeof value.viewState.lodEnabled !== "boolean") {
    return { ok: false, error: "viewState.lodEnabled must be a boolean when present" };
  }

  if (value.viewState.lodThresholds !== undefined) {
    if (!isObject(value.viewState.lodThresholds)) {
      return { ok: false, error: "viewState.lodThresholds must be an object when present" };
    }

    if (
      typeof value.viewState.lodThresholds.close !== "number" ||
      !Number.isFinite(value.viewState.lodThresholds.close) ||
      typeof value.viewState.lodThresholds.mid !== "number" ||
      !Number.isFinite(value.viewState.lodThresholds.mid)
    ) {
      return { ok: false, error: "viewState.lodThresholds.close and .mid must be finite numbers" };
    }
  }

  if (
    value.viewState.lodLevelOverride !== undefined &&
    value.viewState.lodLevelOverride !== null &&
    value.viewState.lodLevelOverride !== "close" &&
    value.viewState.lodLevelOverride !== "mid" &&
    value.viewState.lodLevelOverride !== "far"
  ) {
    return { ok: false, error: 'viewState.lodLevelOverride must be "close" | "mid" | "far" | null when present' };
  }

  if (
    value.viewState.lodShowLoneWolvesWhenFar !== undefined &&
    typeof value.viewState.lodShowLoneWolvesWhenFar !== "boolean"
  ) {
    return { ok: false, error: "viewState.lodShowLoneWolvesWhenFar must be a boolean when present" };
  }

  if (
    value.viewState.resolvedLodLevel !== undefined &&
    value.viewState.resolvedLodLevel !== "close" &&
    value.viewState.resolvedLodLevel !== "mid" &&
    value.viewState.resolvedLodLevel !== "far"
  ) {
    return { ok: false, error: 'viewState.resolvedLodLevel must be "close" | "mid" | "far" when present' };
  }

  if (value.viewState.evidenceOverlayEnabled !== undefined && typeof value.viewState.evidenceOverlayEnabled !== "boolean") {
    return { ok: false, error: "viewState.evidenceOverlayEnabled must be a boolean when present" };
  }

  if (
    value.viewState.evidenceOverlayMode !== undefined &&
    value.viewState.evidenceOverlayMode !== "supports" &&
    value.viewState.evidenceOverlayMode !== "contradicts" &&
    value.viewState.evidenceOverlayMode !== "both"
  ) {
    return { ok: false, error: 'viewState.evidenceOverlayMode must be "supports" | "contradicts" | "both" when present' };
  }

  if (
    value.viewState.evidenceOverlayDepth !== undefined &&
    (typeof value.viewState.evidenceOverlayDepth !== "number" ||
      !Number.isFinite(value.viewState.evidenceOverlayDepth) ||
      value.viewState.evidenceOverlayDepth < 1 ||
      value.viewState.evidenceOverlayDepth > 3)
  ) {
    return { ok: false, error: "viewState.evidenceOverlayDepth must be a number within 1..3 when present" };
  }

  if (
    value.viewState.evidenceOverlayScope !== undefined &&
    value.viewState.evidenceOverlayScope !== "all" &&
    value.viewState.evidenceOverlayScope !== "selection"
  ) {
    return { ok: false, error: 'viewState.evidenceOverlayScope must be "all" | "selection" when present' };
  }

  if (value.viewState.evidenceOverlayDimOthers !== undefined && typeof value.viewState.evidenceOverlayDimOthers !== "boolean") {
    return { ok: false, error: "viewState.evidenceOverlayDimOthers must be a boolean when present" };
  }

  if (!isObject(value.export)) {
    return { ok: false, error: "metadata.export must be an object" };
  }

  if (value.export.mode !== "viewport" && value.export.mode !== "bounds") {
    return { ok: false, error: 'metadata.export.mode must be "viewport" or "bounds"' };
  }

  if (value.export.bounds !== undefined) {
    if (!isObject(value.export.bounds)) {
      return { ok: false, error: "metadata.export.bounds must be an object when present" };
    }

    if (
      typeof value.export.bounds.x !== "number" ||
      !Number.isFinite(value.export.bounds.x) ||
      typeof value.export.bounds.y !== "number" ||
      !Number.isFinite(value.export.bounds.y) ||
      typeof value.export.bounds.w !== "number" ||
      !Number.isFinite(value.export.bounds.w) ||
      typeof value.export.bounds.h !== "number" ||
      !Number.isFinite(value.export.bounds.h)
    ) {
      return { ok: false, error: "metadata.export.bounds fields must be finite numbers" };
    }
  }

  if (value.export.padding !== undefined && (typeof value.export.padding !== "number" || !Number.isFinite(value.export.padding))) {
    return { ok: false, error: "metadata.export.padding must be a finite number when present" };
  }

  if (value.notes !== undefined && typeof value.notes !== "string") {
    return { ok: false, error: "metadata.notes must be a string when present" };
  }

  return { ok: true, metadata: value as ExportViewMetadata };
}
