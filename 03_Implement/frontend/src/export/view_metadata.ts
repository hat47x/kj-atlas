import type { DocumentV1 } from "../domain/types";
import type { HierarchyLevel } from "../domain/view/hierarchy_level";
import type { LODLevel, LODThresholds } from "../domain/view/lod";
import type { ViewPreset } from "../domain/view/presets";
import { PERSPECTIVE_MODE_VALUES, type PerspectiveMode, type PerspectivePreset, type PerspectiveState } from "../domain/view/perspective";
import { type MergeAuditEntry } from "../domain/view/audit_log";
import { type ReviewEvent } from "../domain/view/review_events";
import { normalizeReviewGovernanceLogs, type ReviewRedactionMode } from "../domain/view/review_governance_log";
import { isPublishVisibility, normalizeViewVisibility, type PublishVisibility } from "../domain/policy/publish_visibility";
import { isLocale, type Locale } from "../i18n/translate";


function buildPerspectiveStateFromViewState(viewState: ExportViewMetadataArgs["viewState"]): PerspectiveState {
  const perspective: PerspectiveState = {
    mode: viewState.perspectiveMode ?? "default",
    strictFilter: viewState.perspectiveStrictFilter ?? false,
  };

  if (viewState.lodEnabled !== undefined) {
    perspective.lodEnabled = viewState.lodEnabled;
  }

  if (
    viewState.evidenceOverlayMode !== undefined
    && viewState.evidenceOverlayDepth !== undefined
    && viewState.evidenceOverlayScope !== undefined
    && viewState.evidenceOverlayDimOthers !== undefined
  ) {
    perspective.evidenceOverlayPrefs = {
      mode: viewState.evidenceOverlayMode,
      depth: viewState.evidenceOverlayDepth,
      scope: viewState.evidenceOverlayScope,
      dimOthers: viewState.evidenceOverlayDimOthers,
    };
  }

  return perspective;
}

function sortPerspectivePresets(presets: PerspectivePreset[]): PerspectivePreset[] {
  return [...presets].sort((left, right) => {
    const nameCompared = left.name.localeCompare(right.name);
    if (nameCompared !== 0) {
      return nameCompared;
    }

    return left.id.localeCompare(right.id);
  });
}

export type ExportViewMetadata = {
  version: "1";
  generatedAt: string;
  docSignature: string;
  visibility: PublishVisibility;
  camera: {
    panX: number;
    panY: number;
    zoom: number;
  };
  viewState: {
    summaryView: boolean;
    abstractMapView: boolean;
    hideSourceCards: boolean;
    hierarchyLevel?: HierarchyLevel;
    maxDepth: number | "all";
    focusIslandId: string | null;
    showReadingOrder: boolean;
    editReadingOrder?: boolean;
    readingNavEnabled?: boolean;
    readingIndex?: number;
    readingMode?: "islands" | "islands+cards";
    reviewedOnly?: boolean;
    collapsedIslandIds?: string[];
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
    perspectiveMode?: "default" | "facts" | "claims" | "hypotheses" | "unknown" | "evidence" | "contradiction" | "review";
    perspectiveStrictFilter?: boolean;
    locale?: Locale;
    perspective?: PerspectiveState;
    perspectivePresets?: PerspectivePreset[];
    presets?: ViewPreset[];
    activePresetId?: string;
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
  mergeAuditLog?: MergeAuditEntry[];
  reviewEvents?: ReviewEvent[];
};

type ExportViewMetadataArgs = {
  doc: Pick<DocumentV1, "id" | "title"> | null;
  visibility?: PublishVisibility;
  camera: {
    panX: number;
    panY: number;
    zoom: number;
  };
  viewState: {
    summaryView: boolean;
    abstractMapView: boolean;
    hideSourceCards: boolean;
    hierarchyLevel?: HierarchyLevel;
    maxDepth: number | "all";
    focusIslandId: string | null;
    showReadingOrder: boolean;
    editReadingOrder?: boolean;
    readingNavEnabled?: boolean;
    readingIndex?: number;
    readingMode?: "islands" | "islands+cards";
    reviewedOnly?: boolean;
    collapsedIslandIds?: string[];
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
    perspectiveMode?: "default" | "facts" | "claims" | "hypotheses" | "unknown" | "evidence" | "contradiction" | "review";
    perspectiveStrictFilter?: boolean;
    locale?: Locale;
    perspectivePresets?: PerspectivePreset[];
    presets?: ViewPreset[];
    activePresetId?: string;
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
  mergeAuditLog?: MergeAuditEntry[];
  reviewEvents?: ReviewEvent[];
  reviewRedactionMode?: ReviewRedactionMode;
};

function hashTitle(value: string): string {
  let hash = 0;
  for (let index = 0; index < value.length; index += 1) {
    hash = (hash * 31 + value.charCodeAt(index)) >>> 0;
  }

  return hash.toString(16).padStart(8, "0");
}

function resolveDocSignature(doc: Pick<DocumentV1, "id" | "title"> | null): string {
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

export function buildExportViewMetadata({ doc, visibility, camera, viewState, exportMode, bounds, padding, generatedAt, mergeAuditLog, reviewEvents, reviewRedactionMode }: ExportViewMetadataArgs): ExportViewMetadata {
  const normalizedGovernanceLogs = normalizeReviewGovernanceLogs({
    mergeAuditLog,
    reviewEvents,
    redactionMode: reviewRedactionMode,
  });

  return {
    version: "1",
    generatedAt: generatedAt ?? new Date().toISOString(),
    docSignature: resolveDocSignature(doc),
    visibility: normalizeViewVisibility(visibility),
    camera: {
      panX: camera.panX,
      panY: camera.panY,
      zoom: camera.zoom,
    },
    viewState: {
      summaryView: viewState.summaryView,
      abstractMapView: viewState.abstractMapView,
      hideSourceCards: viewState.hideSourceCards,
      ...(viewState.hierarchyLevel === undefined ? {} : { hierarchyLevel: viewState.hierarchyLevel }),
      maxDepth: viewState.maxDepth,
      focusIslandId: viewState.focusIslandId,
      showReadingOrder: viewState.showReadingOrder,
      ...(viewState.editReadingOrder === undefined ? {} : { editReadingOrder: viewState.editReadingOrder }),
      ...(viewState.readingNavEnabled === undefined ? {} : { readingNavEnabled: viewState.readingNavEnabled }),
      ...(viewState.readingIndex === undefined ? {} : { readingIndex: viewState.readingIndex }),
      ...(viewState.readingMode === undefined ? {} : { readingMode: viewState.readingMode }),
      ...(viewState.reviewedOnly === undefined ? {} : { reviewedOnly: viewState.reviewedOnly }),
      ...(viewState.collapsedIslandIds === undefined ? {} : { collapsedIslandIds: [...viewState.collapsedIslandIds].sort() }),
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
      ...(viewState.perspectiveMode === undefined ? {} : { perspectiveMode: viewState.perspectiveMode }),
      ...(viewState.perspectiveStrictFilter === undefined ? {} : { perspectiveStrictFilter: viewState.perspectiveStrictFilter }),
      ...(viewState.locale === undefined ? {} : { locale: viewState.locale }),
      perspective: buildPerspectiveStateFromViewState(viewState),
      ...(viewState.perspectivePresets === undefined ? {} : { perspectivePresets: sortPerspectivePresets(viewState.perspectivePresets) }),
      ...(viewState.presets === undefined ? {} : { presets: viewState.presets }),
      ...(viewState.activePresetId === undefined ? {} : { activePresetId: viewState.activePresetId }),
    },
    export: {
      mode: exportMode,
      ...(bounds ? { bounds } : {}),
      ...(padding === undefined ? {} : { padding }),
    },
    notes: "",
    ...(normalizedGovernanceLogs.mergeAuditLog === undefined ? {} : { mergeAuditLog: normalizedGovernanceLogs.mergeAuditLog }),
    ...(normalizedGovernanceLogs.reviewEvents === undefined ? {} : { reviewEvents: normalizedGovernanceLogs.reviewEvents }),
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

function isPerspectiveModeValue(value: unknown): value is PerspectiveMode {
  return typeof value === "string" && PERSPECTIVE_MODE_VALUES.includes(value as PerspectiveMode);
}

function validateEvidenceOverlayPrefs(value: unknown, path: string): { ok: true } | { ok: false; error: string } {
  if (!isObject(value)) {
    return { ok: false, error: `${path} must be an object` };
  }

  if (value.mode !== "supports" && value.mode !== "contradicts" && value.mode !== "both") {
    return { ok: false, error: `${path}.mode must be "supports" | "contradicts" | "both"` };
  }

  if (typeof value.depth !== "number" || !Number.isFinite(value.depth)) {
    return { ok: false, error: `${path}.depth must be a finite number` };
  }

  if (value.scope !== "all" && value.scope !== "selection") {
    return { ok: false, error: `${path}.scope must be "all" | "selection"` };
  }

  if (typeof value.dimOthers !== "boolean") {
    return { ok: false, error: `${path}.dimOthers must be a boolean` };
  }

  return { ok: true };
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

  if (value.visibility !== undefined && !isPublishVisibility(value.visibility)) {
    return { ok: false, error: 'metadata.visibility must be "Public" | "Unlisted" | "Org" | "Restricted" when present' };
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

  if (
    value.viewState.hierarchyLevel !== undefined
    && value.viewState.hierarchyLevel !== "overview"
    && value.viewState.hierarchyLevel !== "mid"
    && value.viewState.hierarchyLevel !== "detail"
  ) {
    return { ok: false, error: 'viewState.hierarchyLevel must be "overview" | "mid" | "detail" when present' };
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

  if (value.viewState.collapsedIslandIds !== undefined) {
    if (!Array.isArray(value.viewState.collapsedIslandIds)) {
      return { ok: false, error: "viewState.collapsedIslandIds must be an array when present" };
    }

    for (let index = 0; index < value.viewState.collapsedIslandIds.length; index += 1) {
      if (typeof value.viewState.collapsedIslandIds[index] !== "string") {
        return { ok: false, error: `viewState.collapsedIslandIds[${index}] must be a string` };
      }
    }
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

  if (value.viewState.perspectiveStrictFilter !== undefined && typeof value.viewState.perspectiveStrictFilter !== "boolean") {
    return { ok: false, error: "viewState.perspectiveStrictFilter must be a boolean" };
  }

  if (value.viewState.perspectiveMode !== undefined && !isPerspectiveModeValue(value.viewState.perspectiveMode)) {
    return { ok: false, error: "viewState.perspectiveMode must be a supported perspective mode" };
  }

  if (value.viewState.locale !== undefined && (typeof value.viewState.locale !== "string" || !isLocale(value.viewState.locale))) {
    return { ok: false, error: "viewState.locale must be a supported locale when present" };
  }

  if (value.viewState.perspective !== undefined) {
    if (!isObject(value.viewState.perspective)) {
      return { ok: false, error: "viewState.perspective must be an object" };
    }

    if (typeof value.viewState.perspective.mode !== "string") {
      return { ok: false, error: "viewState.perspective.mode must be a string" };
    }

    if (typeof value.viewState.perspective.strictFilter !== "boolean") {
      return { ok: false, error: "viewState.perspective.strictFilter must be a boolean" };
    }

    if (value.viewState.perspective.lodEnabled !== undefined && typeof value.viewState.perspective.lodEnabled !== "boolean") {
      return { ok: false, error: "viewState.perspective.lodEnabled must be a boolean when present" };
    }

    if (value.viewState.perspective.evidenceOverlayPrefs !== undefined) {
      const result = validateEvidenceOverlayPrefs(value.viewState.perspective.evidenceOverlayPrefs, "viewState.perspective.evidenceOverlayPrefs");
      if (!result.ok) {
        return result;
      }
    }
  }

  if (value.viewState.perspectivePresets !== undefined) {
    if (!Array.isArray(value.viewState.perspectivePresets)) {
      return { ok: false, error: "viewState.perspectivePresets must be an array when present" };
    }

    for (let index = 0; index < value.viewState.perspectivePresets.length; index += 1) {
      const preset = value.viewState.perspectivePresets[index];
      if (!isObject(preset)) {
        return { ok: false, error: `viewState.perspectivePresets[${index}] must be an object` };
      }
      if (typeof preset.id !== "string") {
        return { ok: false, error: `viewState.perspectivePresets[${index}].id must be a string` };
      }
      if (typeof preset.name !== "string") {
        return { ok: false, error: `viewState.perspectivePresets[${index}].name must be a string` };
      }
      if (!isObject(preset.perspective)) {
        return { ok: false, error: `viewState.perspectivePresets[${index}].perspective must be an object` };
      }
      if (typeof preset.perspective.mode !== "string") {
        return { ok: false, error: `viewState.perspectivePresets[${index}].perspective.mode must be a string` };
      }
      if (typeof preset.perspective.strictFilter !== "boolean") {
        return { ok: false, error: `viewState.perspectivePresets[${index}].perspective.strictFilter must be a boolean` };
      }
      if (preset.perspective.lodEnabled !== undefined && typeof preset.perspective.lodEnabled !== "boolean") {
        return { ok: false, error: `viewState.perspectivePresets[${index}].perspective.lodEnabled must be a boolean when present` };
      }
      if (preset.perspective.evidenceOverlayPrefs !== undefined) {
        const result = validateEvidenceOverlayPrefs(
          preset.perspective.evidenceOverlayPrefs,
          `viewState.perspectivePresets[${index}].perspective.evidenceOverlayPrefs`
        );
        if (!result.ok) {
          return result;
        }
      }
    }
  }

  if (value.viewState.presets !== undefined) {
    if (!Array.isArray(value.viewState.presets)) {
      return { ok: false, error: "viewState.presets must be an array when present" };
    }
    for (let index = 0; index < value.viewState.presets.length; index += 1) {
      const preset = value.viewState.presets[index];
      if (!isObject(preset)) {
        return { ok: false, error: `viewState.presets[${index}] must be an object` };
      }
      if (typeof preset.id !== "string" || typeof preset.name !== "string") {
        return { ok: false, error: `viewState.presets[${index}] id/name must be strings` };
      }
      if (!isObject(preset.viewPatch)) {
        return { ok: false, error: `viewState.presets[${index}].viewPatch must be an object` };
      }
      if (typeof preset.createdAt !== "string" || typeof preset.updatedAt !== "string") {
        return { ok: false, error: `viewState.presets[${index}] createdAt/updatedAt must be strings` };
      }
    }
  }

  if (value.viewState.activePresetId !== undefined && typeof value.viewState.activePresetId !== "string") {
    return { ok: false, error: "viewState.activePresetId must be a string when present" };
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

  if (value.mergeAuditLog !== undefined && !Array.isArray(value.mergeAuditLog)) {
    return { ok: false, error: "metadata.mergeAuditLog must be an array when present" };
  }

  if (value.reviewEvents !== undefined && !Array.isArray(value.reviewEvents)) {
    return { ok: false, error: "metadata.reviewEvents must be an array when present" };
  }

  return { ok: true, metadata: {
    ...(value as ExportViewMetadata),
    visibility: normalizeViewVisibility(value.visibility),
    ...normalizeReviewGovernanceLogs({
      mergeAuditLog: value.mergeAuditLog,
      reviewEvents: value.reviewEvents,
    }),
  } };
}
