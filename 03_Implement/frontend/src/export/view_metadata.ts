import type { DocumentV2 } from "../domain/types";

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
    },
    export: {
      mode: exportMode,
      ...(bounds ? { bounds } : {}),
      ...(padding === undefined ? {} : { padding }),
    },
    notes: "",
  };
}
