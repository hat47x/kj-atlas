import { validateImportedDocument } from "../domain/validate";
import type { DocumentV1 } from "../domain/types";
import { validateImportViewMetadata, type ExportViewMetadata } from "../export/view_metadata";
import { DEFAULT_VIEW_PRESETS } from "../domain/view/presets";
import { isLocale } from "../i18n/translate";
import { PERSPECTIVE_MODE_VALUES } from "../domain/view/perspective";
import { DEFAULT_VIEW_VISIBILITY } from "../domain/policy/publish_visibility";

export type ValidationError = {
  code: `V${string}`;
  path: string;
  message: string;
  severity: "error" | "warn";
};

export type ViewState = ExportViewMetadata;

type ValidateResult<T> = { ok: true; value: T } | { ok: false; errors: ValidationError[] };

function isPerspectiveMode(value: unknown): value is (typeof PERSPECTIVE_MODE_VALUES)[number] {
  return typeof value === "string" && PERSPECTIVE_MODE_VALUES.some((mode) => mode === value);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function toCardArray(rawCards: unknown): unknown {
  if (Array.isArray(rawCards)) {
    return rawCards;
  }

  if (!isRecord(rawCards)) {
    return rawCards;
  }

  return Object.entries(rawCards).map(([key, value]) => {
    if (!isRecord(value)) {
      return value;
    }

    return {
      ...value,
      id: typeof value.id === "string" ? value.id : key,
      x: typeof value.x === "number" && Number.isFinite(value.x) ? value.x : 0,
      y: typeof value.y === "number" && Number.isFinite(value.y) ? value.y : 0,
    };
  });
}

function collectDocumentPreflightErrors(input: Record<string, unknown>): ValidationError[] {
  const errors: ValidationError[] = [];

  if (!("cards" in input)) {
    errors.push({ code: "V001", path: "cards", message: "Document must include cards (array or map).", severity: "error" });
  } else if (!Array.isArray(input.cards) && !isRecord(input.cards)) {
    errors.push({ code: "V001", path: "cards", message: "Document cards must be an array or object map.", severity: "error" });
  }

  const cards = toCardArray(input.cards);
  if (Array.isArray(cards)) {
    cards.forEach((card, index) => {
      if (!isRecord(card)) {
        errors.push({ code: "V002", path: `cards[${index}]`, message: "Card must be an object.", severity: "error" });
        return;
      }

      if (typeof card.id !== "string" || card.id.trim().length === 0) {
        errors.push({ code: "V002", path: `cards[${index}].id`, message: "Card id must be a non-empty string.", severity: "error" });
      }

      if (typeof card.text !== "string") {
        errors.push({ code: "V002", path: `cards[${index}].text`, message: "Card text must be a string.", severity: "error" });
      }
    });
  }

  if (input.islands !== undefined) {
    if (!Array.isArray(input.islands)) {
      errors.push({ code: "V003", path: "islands", message: "Islands must be an array when provided.", severity: "error" });
    } else {
      input.islands.forEach((island, index) => {
        if (!isRecord(island)) {
          errors.push({ code: "V003", path: `islands[${index}]`, message: "Island must be an object.", severity: "error" });
          return;
        }

        if (typeof island.id !== "string" || island.id.trim().length === 0) {
          errors.push({ code: "V003", path: `islands[${index}].id`, message: "Island id must be a non-empty string.", severity: "error" });
        }

        const hasShape = isRecord(island.shape);
        const hasGeometry = isRecord(island.geometry);
        const hasBbox = isRecord(island.bbox)
          && typeof island.bbox.x === "number"
          && typeof island.bbox.y === "number"
          && typeof island.bbox.w === "number"
          && typeof island.bbox.h === "number";

        if (!hasShape && !hasGeometry && !hasBbox) {
          errors.push({
            code: "V003",
            path: `islands[${index}]`,
            message: `Island '${typeof island.id === "string" ? island.id : `#${index}`}' has no geometry. It will render using card bounds fallback.`,
            severity: "warn",
          });
        }
      });
    }
  }

  return errors;
}

function mapUpgradeErrorToValidationError(error: string): ValidationError {
  if (error.toLowerCase().includes("transform")) {
    return { code: "V001", path: "transform", message: error, severity: "error" };
  }

  if (error.toLowerCase().includes("version")) {
    return { code: "V001", path: "version", message: error, severity: "error" };
  }

  if (error.toLowerCase().includes("cards")) {
    return { code: "V002", path: "cards", message: error, severity: "error" };
  }

  return { code: "V001", path: "document", message: error, severity: "error" };
}

export function validateDocument(
  input: unknown,
  options: { evidenceEndpointSeverity?: "error" | "warn" } = {}
): ValidateResult<DocumentV1> {
  if (!isRecord(input)) {
    return {
      ok: false,
      errors: [{ code: "V001", path: "document", message: "Document must be a JSON object.", severity: "error" }],
    };
  }

  const preflightErrors = collectDocumentPreflightErrors(input);
  if (preflightErrors.some((error) => error.severity === "error")) {
    return { ok: false, errors: preflightErrors.filter((error) => error.severity === "error") };
  }

  const normalizedInput: Record<string, unknown> = {
    ...input,
    cards: toCardArray(input.cards),
  };

  const parsed = validateImportedDocument(normalizedInput);
  if (!parsed.ok) {
    return { ok: false, errors: [mapUpgradeErrorToValidationError(parsed.error)] };
  }

  const endpointSeverity = options.evidenceEndpointSeverity ?? "warn";
  const cardIdSet = new Set(parsed.document.cards.map((card) => card.id));
  const linkErrors: ValidationError[] = [];

  (parsed.document.evidenceLinks ?? []).forEach((link, index) => {
    if (!cardIdSet.has(link.fromCardId)) {
      linkErrors.push({
        code: "V004",
        path: `evidenceLinks[${index}].fromCardId`,
        message: `Evidence link '${link.id}' points to unknown fromCardId '${link.fromCardId}'.`,
        severity: endpointSeverity,
      });
    }

    if (!cardIdSet.has(link.toCardId)) {
      linkErrors.push({
        code: "V005",
        path: `evidenceLinks[${index}].toCardId`,
        message: `Evidence link '${link.id}' points to unknown toCardId '${link.toCardId}'.`,
        severity: endpointSeverity,
      });
    }
  });

  if (linkErrors.some((entry) => entry.severity === "error")) {
    return { ok: false, errors: linkErrors.filter((entry) => entry.severity === "error") };
  }

  return { ok: true, value: parsed.document };
}

function buildDefaultViewMetadata(input: Record<string, unknown>): ExportViewMetadata {
  const rawCamera = isRecord(input.camera) ? input.camera : {};
  const rawViewState = isRecord(input.viewState) ? input.viewState : {};
  const rawExport = isRecord(input.export) ? input.export : {};
  const perspectiveMode: ExportViewMetadata["viewState"]["perspectiveMode"] =
    isPerspectiveMode(rawViewState.perspectiveMode) ? rawViewState.perspectiveMode : "default";

  return {
    ...(input as Partial<ExportViewMetadata>),
    version: "1",
    generatedAt: typeof input.generatedAt === "string" ? input.generatedAt : new Date().toISOString(),
    docSignature: typeof input.docSignature === "string" ? input.docSignature : "unknown",
    visibility: input.visibility === undefined ? DEFAULT_VIEW_VISIBILITY : (input.visibility as ExportViewMetadata["visibility"]),
    camera: {
      ...(rawCamera as ExportViewMetadata["camera"]),
      panX: typeof rawCamera.panX === "number" && Number.isFinite(rawCamera.panX) ? rawCamera.panX : 0,
      panY: typeof rawCamera.panY === "number" && Number.isFinite(rawCamera.panY) ? rawCamera.panY : 0,
      zoom: typeof rawCamera.zoom === "number" && Number.isFinite(rawCamera.zoom) ? rawCamera.zoom : 1,
    },
    viewState: {
      ...(rawViewState as ExportViewMetadata["viewState"]),
      summaryView: rawViewState.summaryView === true,
      abstractMapView: rawViewState.abstractMapView === true,
      hideSourceCards: rawViewState.hideSourceCards === true,
      hierarchyLevel:
        rawViewState.hierarchyLevel === "overview" || rawViewState.hierarchyLevel === "mid" || rawViewState.hierarchyLevel === "detail"
          ? rawViewState.hierarchyLevel
          : undefined,
      maxDepth: typeof rawViewState.maxDepth === "number" || rawViewState.maxDepth === "all" ? rawViewState.maxDepth : "all",
      focusIslandId: typeof rawViewState.focusIslandId === "string" ? rawViewState.focusIslandId : null,
      showReadingOrder: rawViewState.showReadingOrder === true,
      collapsedIslandIds: Array.isArray(rawViewState.collapsedIslandIds)
        ? rawViewState.collapsedIslandIds.filter((value): value is string => typeof value === "string")
        : [],
      perspectiveMode,
      perspectiveStrictFilter: rawViewState.perspectiveStrictFilter === true,
      locale: typeof rawViewState.locale === "string" && isLocale(rawViewState.locale) ? rawViewState.locale : undefined,
      presets: Array.isArray(rawViewState.presets) ? (rawViewState.presets as ExportViewMetadata["viewState"]["presets"]) : DEFAULT_VIEW_PRESETS,
      activePresetId: typeof rawViewState.activePresetId === "string" ? rawViewState.activePresetId : undefined,
    },
    export: {
      ...(rawExport as ExportViewMetadata["export"]),
      mode: rawExport.mode === "bounds" ? "bounds" : "viewport",
    },
  };
}

export function validateView(input: unknown): ValidateResult<ViewState> {
  if (!isRecord(input)) {
    return {
      ok: false,
      errors: [{ code: "V101", path: "view", message: "View metadata must be a JSON object.", severity: "error" }],
    };
  }

  const normalized = buildDefaultViewMetadata(input);
  const validated = validateImportViewMetadata(normalized);
  if (!validated.ok) {
    return {
      ok: false,
      errors: [{ code: "V102", path: "view", message: validated.error, severity: "error" }],
    };
  }

  return { ok: true, value: validated.metadata };
}
