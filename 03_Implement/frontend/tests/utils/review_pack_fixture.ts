import JSZip from "jszip";

export type ReviewPackFixtureName = "base_pack.zip" | "incoming_pack.zip" | "malicious_pack.zip";

const ROOT = "kj-atlas-review-pack-20260221-000000";

const diagnosticsText = "# Diagnostics\n\nPotential issue: <script>alert(1)</script>\n";

const baseDocument = {
  version: 1,
  id: "doc-review-pack-workflow",
  title: "Workflow Fixture",
  createdAt: "2026-02-21T00:00:00.000Z",
  updatedAt: "2026-02-21T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    { id: "c1", text: "Alpha", x: 0, y: 0, claimType: "unknown" },
    { id: "c2", text: "Beta", x: 120, y: 40, claimType: "fact" },
  ],
  edges: [],
  islands: [{ id: "i1", cardIds: ["c1", "c2"], shape: { kind: "rect" } }],
  readingOrder: ["c1", "c2"],
  relationSummaries: [],
  evidenceLinks: [],
};

const incomingDocument = {
  ...baseDocument,
  updatedAt: "2026-02-21T01:00:00.000Z",
  cards: [
    { id: "c1", text: "Alpha", x: 0, y: 0, claimType: "claim" },
    { id: "c2", text: "Beta", x: 120, y: 40, claimType: "fact" },
  ],
  readingOrder: ["c2", "c1"],
  evidenceLinks: [{ id: "e-support-1", type: "supports", fromCardId: "c2", toCardId: "c1" }],
};

const baseView = {
  version: "1",
  generatedAt: "2026-02-21T00:00:00.000Z",
  docSignature: "doc-review-pack-workflow",
  camera: { panX: 0, panY: 0, zoom: 1 },
  viewState: {
    summaryView: false,
    abstractMapView: false,
    hideSourceCards: false,
    maxDepth: "all",
    focusIslandId: null,
    showReadingOrder: false,
    perspectiveMode: "default",
    perspectiveStrictFilter: false,
  },
  export: { mode: "viewport" },
};

const incomingView = {
  ...baseView,
  generatedAt: "2026-02-21T01:00:00.000Z",
  camera: { panX: 20, panY: -10, zoom: 1.25 },
  viewState: {
    ...baseView.viewState,
    perspectiveMode: "review",
  },
};

async function buildZipFile(name: string, entries: Record<string, string>): Promise<File> {
  const zip = new JSZip();
  for (const [path, content] of Object.entries(entries).sort(([a], [b]) => a.localeCompare(b))) {
    zip.file(path, content, { date: new Date("2026-02-21T00:00:00.000Z") });
  }

  const blob = await zip.generateAsync({
    type: "blob",
    compression: "DEFLATE",
    compressionOptions: { level: 9 },
  });

  return new File([blob], name, { type: "application/zip" });
}

export async function loadReviewPackFixtureFile(name: ReviewPackFixtureName): Promise<File> {
  if (name === "base_pack.zip") {
    return buildZipFile(name, {
      [`${ROOT}/document.json`]: `${JSON.stringify(baseDocument, null, 2)}\n`,
      [`${ROOT}/view.json`]: `${JSON.stringify(baseView, null, 2)}\n`,
      [`${ROOT}/diagnostics.md`]: diagnosticsText,
    });
  }

  if (name === "incoming_pack.zip") {
    return buildZipFile(name, {
      [`${ROOT}/document.json`]: `${JSON.stringify(incomingDocument, null, 2)}\n`,
      [`${ROOT}/view.json`]: `${JSON.stringify(incomingView, null, 2)}\n`,
      [`${ROOT}/diagnostics.md`]: diagnosticsText,
    });
  }

  return buildZipFile(name, {
    "../document.json": "{}\n",
    "view.json": "{}\n",
  });
}
