import { describe, expect, test } from "vitest";

import type { DocumentV1 } from "../domain/types";
import { canonicalizeJson } from "../domain/patch/patch_fingerprint";
import { buildExportBundle, type BundleFile, type BundleExportContext } from "../export/bundle_export";
import { resolveViewLocale } from "./view_locale_resolution";

type LeakLayer = "ui-state" | "view-metadata" | "document-payload";

type LocaleLeakDiagnostic = {
  layer: LeakLayer;
  details: string[];
};

const deterministicContext: Omit<BundleExportContext, "rootFolderPath"> = {
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
};

const baseDoc: DocumentV1 = {
  version: 1,
  id: "doc-i18n-05",
  title: "Locale invariance",
  createdAt: "2026-01-01T00:00:00.000Z",
  updatedAt: "2026-01-02T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    { id: "c1", text: "観測", x: 0, y: 0, claimType: "fact", textReviewed: true },
    { id: "c2", text: "解釈", x: 40, y: 10, claimType: "claim", textReviewed: true },
  ],
  edges: [{ id: "e1", fromId: "c1", toId: "c2", type: "related" }],
  islands: [{ id: "i1", cardIds: ["c1", "c2"], title: "I1", summaryText: "S1", summaryReviewed: true }],
};

function readJsonFile(files: BundleFile[], suffix: "/document.json" | "/view.json"): Record<string, unknown> {
  const file = files.find((entry) => entry.path.endsWith(suffix));
  if (!file || typeof file.content !== "string") {
    throw new Error(`${suffix} was not emitted`);
  }
  return JSON.parse(file.content) as Record<string, unknown>;
}

function buildBundleWithLocale(doc: DocumentV1, locale: "ja" | "en", extraViewState: Record<string, unknown> = {}): BundleFile[] {
  return buildExportBundle(doc, {
    viewState: {
      locale,
      sidePanel: "share",
      ...extraViewState,
    },
  }, {
    ...deterministicContext,
    rootFolderPath: `kj-atlas-export-${locale}`,
  });
}

async function hashJson(value: unknown): Promise<string> {
  const payload = new TextEncoder().encode(canonicalizeJson(value));
  const digest = await crypto.subtle.digest("SHA-256", payload);
  return Array.from(new Uint8Array(digest)).map((entry) => entry.toString(16).padStart(2, "0")).join("");
}

function detectLocaleLeak(args: {
  baseDocument: Record<string, unknown>;
  switchedDocument: Record<string, unknown>;
  baseView: Record<string, unknown>;
  switchedView: Record<string, unknown>;
}): LocaleLeakDiagnostic[] {
  const diagnostics: LocaleLeakDiagnostic[] = [];
  if (canonicalizeJson(args.baseDocument) !== canonicalizeJson(args.switchedDocument)) {
    diagnostics.push({
      layer: "document-payload",
      details: ["document.json canonical payload changed across locale switch"],
    });
  }

  if (canonicalizeJson(args.baseView) !== canonicalizeJson(args.switchedView)) {
    diagnostics.push({
      layer: "view-metadata",
      details: ["view.json changed (expected when locale metadata changes)"],
    });
  }

  const baseUi = (args.baseView.viewState as Record<string, unknown> | undefined)?.locale;
  const switchedUi = (args.switchedView.viewState as Record<string, unknown> | undefined)?.locale;
  if (baseUi !== switchedUi) {
    diagnostics.push({
      layer: "ui-state",
      details: [`ui locale transition detected: ${String(baseUi)} -> ${String(switchedUi)}`],
    });
  }

  return diagnostics;
}

describe("FB-RM-I18N-05 document hash invariance", () => {
  test("keeps document hash invariant for locale sequence ja -> en -> ja", async () => {
    const ja1Bundle = buildBundleWithLocale(baseDoc, "ja", { marker: "ja-1" });
    const enBundle = buildBundleWithLocale(baseDoc, "en", { marker: "en" });
    const ja2Bundle = buildBundleWithLocale(baseDoc, "ja", { marker: "ja-2" });

    const ja1Doc = readJsonFile(ja1Bundle, "/document.json");
    const enDoc = readJsonFile(enBundle, "/document.json");
    const ja2Doc = readJsonFile(ja2Bundle, "/document.json");

    const ja1Hash = await hashJson(ja1Doc);
    const enHash = await hashJson(enDoc);
    const ja2Hash = await hashJson(ja2Doc);

    expect(ja1Hash).toBe(enHash);
    expect(enHash).toBe(ja2Hash);

    const ja1View = readJsonFile(ja1Bundle, "/view.json");
    const enView = readJsonFile(enBundle, "/view.json");
    const diagnostics = detectLocaleLeak({
      baseDocument: ja1Doc,
      switchedDocument: enDoc,
      baseView: ja1View,
      switchedView: enView,
    });

    expect(diagnostics.find((entry) => entry.layer === "document-payload")).toBeUndefined();
    expect(diagnostics.find((entry) => entry.layer === "view-metadata")).toBeDefined();
    expect(diagnostics.find((entry) => entry.layer === "ui-state")).toBeDefined();
  });

  test("URL locale priority changes view metadata only", async () => {
    const resolvedFromUrl = resolveViewLocale({
      search: "?locale=en",
      metadataLocale: "ja",
      persistedLocale: "ja",
      isReadOnly: false,
    });
    const resolvedWithoutUrl = resolveViewLocale({
      search: "",
      metadataLocale: "ja",
      persistedLocale: "ja",
      isReadOnly: false,
    });

    expect(resolvedFromUrl).toEqual({ locale: "en", source: "url", shouldPersist: false });
    expect(resolvedWithoutUrl).toEqual({ locale: "ja", source: "view-metadata", shouldPersist: true });

    const urlBundle = buildBundleWithLocale(baseDoc, resolvedFromUrl.locale, {
      resolutionSource: resolvedFromUrl.source,
    });
    const metadataBundle = buildBundleWithLocale(baseDoc, resolvedWithoutUrl.locale, {
      resolutionSource: resolvedWithoutUrl.source,
    });

    const urlDocHash = await hashJson(readJsonFile(urlBundle, "/document.json"));
    const metadataDocHash = await hashJson(readJsonFile(metadataBundle, "/document.json"));
    expect(urlDocHash).toBe(metadataDocHash);
  });

  test("read-only locale resolution never mutates document payload", async () => {
    const resolvedReadOnly = resolveViewLocale({
      search: "",
      metadataLocale: "en",
      persistedLocale: "ja",
      isReadOnly: true,
    });
    expect(resolvedReadOnly).toEqual({ locale: "en", source: "view-metadata", shouldPersist: false });

    const roBundle = buildBundleWithLocale(baseDoc, resolvedReadOnly.locale, {
      readOnly: true,
      shouldPersist: resolvedReadOnly.shouldPersist,
    });
    const rwBundle = buildBundleWithLocale(baseDoc, "ja", {
      readOnly: false,
      shouldPersist: true,
    });

    const roDocument = readJsonFile(roBundle, "/document.json");
    const rwDocument = readJsonFile(rwBundle, "/document.json");
    expect(await hashJson(roDocument)).toBe(await hashJson(rwDocument));
  });
});
