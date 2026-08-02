import type { DocumentV1 } from "../domain/types";
import {
  HAND_DRAWN_CUE_BUNDLE_FILE_NAME,
  parseHandDrawnCueAssetBundle,
  stripHandDrawnVisualCues,
  type HandDrawnCueAssetBundleV1,
} from "../domain/representative_visual_cue_assets";
import { deriveDocumentSafeModeProjection } from "../domain/inquiry_bundle_safe_mode";
import { buildContradictionTraceMd } from "../domain/view/contradiction_trace";
import { analyzeContradictions, type ContradictionReport } from "../domain/view/contradiction_checks";
import { analyzeDialecticBalance, type DialecticBalanceReport } from "../domain/view/dialectic_balance";
import { analyzeDistribution, type DistributionReport } from "../domain/view/distribution_checks";
import { buildEvidenceTraceMd } from "../domain/view/evidence_trace";
import { analyzeOutlineQuality, type OutlineQualityReport } from "../domain/view/outline_quality";
import { buildReadingOutlineMd, type ReadingOutlineOptions, type ReadingOutlineState } from "../domain/view/reading_outline";
import { generateRecommendations } from "../domain/view/recommendations";
import type { ReadingMode } from "../domain/view/reading_path";
import { buildMergeDecisionAuditEntries } from "../domain/merge_decision_audit";
import { DiagnosticsWorkerClient } from "../worker/diagnostics_client";
import { TraceWorkerClient } from "../worker/trace_client";
import { buildTraceAnalyticsMd, computeTraceAnalytics } from "../worker/trace_analytics";
import { BundleZipWorkerClient } from "../worker/bundle_zip_client";
import type { PublishVisibility } from "../domain/policy/publish_visibility";
import { buildIntegrityManifest } from "../security/artifact_integrity";

export type BundleFile = {
  path: string;
  content: string | Uint8Array;
  mime: string;
};

export type ExportGranularity = "overview" | "detail";
export type BundleExportProgressStage = "diagnostics" | "evidence_trace" | "contradiction_trace" | "trace_analytics";

export type BundleExportContext = {
  rootFolderPath: string;
  safeMode?: boolean;
  includeOutline: boolean;
  includeDiagnostics: boolean;
  includeSelectedCardTraces: boolean;
  selectedCardId: string | null;
  exportGranularity?: ExportGranularity;
  deterministicNowIso: string;
  readingState: ReadingOutlineState;
  readingMode: ReadingMode;
  reviewedOnly: boolean;
  outlineOptions?: ReadingOutlineOptions;
  outlineQualityReport?: OutlineQualityReport | null;
  contradictionReport?: ContradictionReport | null;
  distributionReport?: DistributionReport | null;
  dialecticBalanceReport?: DialecticBalanceReport | null;
  viewVisibility?: PublishVisibility;
  packVisibility?: PublishVisibility;
  /**
   * DOMAIN-TRACE-01 (schemas.md §15.4): share exports exclude Card.meta
   * (seq/source) unless the user explicitly opts in. Independent of safeMode.
   */
  includeSourceReferences?: boolean;
  /**
   * DOMAIN-VISUAL-CUE-01: hand-drawn bodies are excluded by default.
   * Explicit opt-in requires the exact, preloaded asset bundle.
   */
  includeVisualCueAssets?: boolean;
  handDrawnVisualCueAssetBundle?: HandDrawnCueAssetBundleV1;
};

function sortObjectKeys<T>(value: T): T {
  if (Array.isArray(value)) {
    return value.map((item) => sortObjectKeys(item)) as T;
  }

  if (value && typeof value === "object") {
    const sortedEntries = Object.entries(value as Record<string, unknown>)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([key, nestedValue]) => [key, sortObjectKeys(nestedValue)] as const);
    return Object.fromEntries(sortedEntries) as T;
  }

  return value;
}

function toJsonFile(path: string, value: unknown): BundleFile {
  const sorted = sortObjectKeys(value);
  return {
    path,
    content: `${JSON.stringify(sorted, null, 2)}\n`,
    mime: "application/json",
  };
}

function summarizeOutlineQuality(report: OutlineQualityReport, safeMode: boolean): string[] {
  const lines: string[] = ["## Outline quality report (I10)", ""];
  lines.push(`- totalIslands: ${report.stats.totalIslands}`);
  lines.push(`- totalCardsInPath: ${report.stats.totalCardsInPath}`);
  lines.push(`- pathLength: ${report.stats.pathLength}`);
  lines.push(`- findings: ${report.findings.length}`);
  for (const finding of report.findings) {
    const refs = (finding.entityRefs ?? []).map((ref) => `${ref.kind}:${ref.id}`).sort();
    lines.push(`- [${finding.severity.toUpperCase()}] ${finding.code}: ${finding.title}`);
    if (!safeMode && finding.detail.trim().length > 0) {
      lines.push(`  - detail: ${finding.detail}`);
    }
    if (refs.length > 0) {
      lines.push(`  - refs: ${refs.join(", ")}`);
    }
  }
  lines.push("");
  return lines;
}

function summarizeRecommendations(doc: DocumentV1, report: OutlineQualityReport, readingMode: ReadingMode, reviewedOnly: boolean): string[] {
  const lines: string[] = ["## Recommendations (I11)", ""];
  const recommendations = generateRecommendations(report, doc, { readingMode, reviewedOnly });
  lines.push(`- count: ${recommendations.length}`);
  for (const recommendation of recommendations) {
    lines.push(`- [${recommendation.impactLevel}] ${recommendation.id}: ${recommendation.title}`);
    const sortedTargets = [...(recommendation.targetEntities ?? [])].sort((left, right) => {
      if (left.kind !== right.kind) {
        return left.kind.localeCompare(right.kind);
      }
      return left.id.localeCompare(right.id);
    });
    if (sortedTargets.length > 0) {
      lines.push(`  - targets: ${sortedTargets.map((target) => `${target.kind}:${target.id}`).join(", ")}`);
    }
  }
  lines.push("");
  return lines;
}

function summarizeContradictions(report: ContradictionReport): string[] {
  const lines: string[] = ["## Contradiction signals (I12)", ""];
  lines.push(`- signals: ${report.stats.signals}`);
  for (const signal of report.signals) {
    const refs = signal.entityRefs.map((ref) => `${ref.kind}:${ref.idOrSignature}`).sort();
    lines.push(`- [${signal.severity.toUpperCase()}] ${signal.code}: ${signal.title}`);
    if (refs.length > 0) {
      lines.push(`  - refs: ${refs.join(", ")}`);
    }
  }
  lines.push("");
  return lines;
}

function summarizeDistribution(report: DistributionReport): string[] {
  const lines: string[] = ["## Distribution signals (I13)", ""];
  lines.push(`- islands: ${report.stats.islandCount}`);
  lines.push(`- cards: ${report.stats.cardCount}`);
  lines.push(`- findings: ${report.findings.length}`);
  for (const finding of report.findings) {
    lines.push(`- [${finding.severity.toUpperCase()}] ${finding.code}: ${finding.title}`);
    const ids = [...(finding.islandIds ?? [])].sort();
    if (ids.length > 0) {
      lines.push(`  - islands: ${ids.join(", ")}`);
    }
  }
  lines.push("");
  return lines;
}

function summarizeDialecticBalance(report: DialecticBalanceReport): string[] {
  const lines: string[] = ["## Dialectic balance (I19)", ""];
  lines.push(`- hypotheses: ${report.stats.hypothesisCount}`);
  lines.push(`- claims: ${report.stats.claimCount}`);
  lines.push(`- facts: ${report.stats.factCount}`);
  lines.push(`- findings: ${report.findings.length}`);
  for (const finding of report.findings) {
    lines.push(`- [${finding.severity.toUpperCase()}] ${finding.code}: ${finding.title}`);
    const ids = [...(finding.cardIds ?? [])].sort();
    if (ids.length > 0) {
      lines.push(`  - cards: ${ids.join(", ")}`);
    }
  }
  lines.push("");
  return lines;
}


function resolveExportGranularity(context: BundleExportContext): ExportGranularity {
  return context.exportGranularity ?? "detail";
}

/**
 * schemas.md §15.4: Card.meta stays out of shared bundles by default so raw-data
 * references never leave the workspace without an explicit opt-in. Backup
 * JSON/PUT paths do not go through here and keep meta intact.
 */
function resolveShareDocument(
  doc: DocumentV1,
  context: BundleExportContext,
): DocumentV1 {
  const visualCueScopedDocument = context.includeVisualCueAssets
    ? doc
    : stripHandDrawnVisualCues(doc);
  if (context.includeSourceReferences) {
    return visualCueScopedDocument;
  }
  if (!visualCueScopedDocument.cards.some((card) => card.meta !== undefined)) {
    return visualCueScopedDocument;
  }
  return {
    ...visualCueScopedDocument,
    cards: visualCueScopedDocument.cards.map((card) => {
      if (card.meta === undefined) {
        return card;
      }
      const { meta: _meta, ...rest } = card;
      return rest;
    }),
  };
}

function resolveBundledDocument(
  sourceScopedDocument: DocumentV1,
  context: BundleExportContext,
): DocumentV1 {
  if (!(context.safeMode ?? true)) {
    return sourceScopedDocument;
  }
  return deriveDocumentSafeModeProjection(sourceScopedDocument, {
    includeSourceReferences: context.includeSourceReferences ?? false,
  });
}

function shouldIncludeSelectedCardTraces(context: BundleExportContext): boolean {
  return resolveExportGranularity(context) === "detail" && context.includeSelectedCardTraces;
}

function resolveOutlineOptions(context: BundleExportContext, safeMode: boolean): ReadingOutlineOptions {
  const granularity = resolveExportGranularity(context);
  if (granularity === "overview") {
    return {
      ...context.outlineOptions,
      includeCardTexts: false,
      includeRelationSummaries: true,
      includeUnreviewedSummaries: false,
      context: "share",
    };
  }

  return {
    ...context.outlineOptions,
    context: "share",
    includeUnreviewedSummaries: safeMode ? false : context.outlineOptions?.includeUnreviewedSummaries,
  };
}

function buildBundleManifest(context: BundleExportContext): {
  exportGranularity: ExportGranularity;
  generatedAt: string;
  visibility?: { view?: PublishVisibility; pack?: PublishVisibility };
  representativeVisualCueAssets?: { version: "1"; count: number };
} {
  return {
    exportGranularity: resolveExportGranularity(context),
    generatedAt: context.deterministicNowIso,
    ...(context.viewVisibility || context.packVisibility
      ? {
          visibility: {
            ...(context.viewVisibility ? { view: context.viewVisibility } : {}),
            ...(context.packVisibility ? { pack: context.packVisibility } : {}),
          },
        }
      : {}),
    ...(context.includeVisualCueAssets && context.handDrawnVisualCueAssetBundle
      ? {
          representativeVisualCueAssets: {
            version: "1" as const,
            count: context.handDrawnVisualCueAssetBundle.assets.length,
          },
        }
      : {}),
  };
}

function appendHandDrawnCueAssetFile(
  files: BundleFile[],
  root: string,
  bundledDocument: DocumentV1,
  context: BundleExportContext,
): void {
  if (!context.includeVisualCueAssets) {
    if (context.handDrawnVisualCueAssetBundle) {
      throw new Error("hand-drawn visual cue assets require explicit export opt-in");
    }
    return;
  }
  if (!context.handDrawnVisualCueAssetBundle) {
    throw new Error("hand-drawn visual cue asset bundle is required");
  }
  const assetBundle = parseHandDrawnCueAssetBundle(
    context.handDrawnVisualCueAssetBundle,
    bundledDocument,
  );
  files.push(toJsonFile(`${root}/${HAND_DRAWN_CUE_BUNDLE_FILE_NAME}`, assetBundle));
}

function buildDiagnosticsMd(doc: DocumentV1, context: BundleExportContext): string {
  const safeMode = context.safeMode ?? true;
  const outlineReport = context.outlineQualityReport ?? analyzeOutlineQuality(doc, { readingMode: context.readingMode, reviewedOnly: context.reviewedOnly }, { nowIso: context.deterministicNowIso });
  const contradictionReport = context.contradictionReport ?? analyzeContradictions(doc, context.deterministicNowIso);
  const distributionReport = context.distributionReport ?? analyzeDistribution(doc, context.deterministicNowIso);
  const dialecticBalanceReport = context.dialecticBalanceReport ?? analyzeDialecticBalance(doc, context.deterministicNowIso);

  const lines: string[] = ["# Diagnostics", ""];
  lines.push(...summarizeOutlineQuality(outlineReport, safeMode));
  lines.push(...summarizeRecommendations(doc, outlineReport, context.readingMode, context.reviewedOnly));
  lines.push(...summarizeContradictions(contradictionReport));
  lines.push(...summarizeDistribution(distributionReport));
  lines.push(...summarizeDialecticBalance(dialecticBalanceReport));
  return `${lines.join("\n")}\n`;
}

export function buildExportBundle(doc: DocumentV1, viewState: unknown, context: BundleExportContext): BundleFile[] {
  const safeMode = context.safeMode ?? true;
  const contentDocument = resolveShareDocument(doc, context);
  const bundledDocument = resolveBundledDocument(contentDocument, context);
  const root = context.rootFolderPath.endsWith("/") ? context.rootFolderPath.slice(0, -1) : context.rootFolderPath;
  const bundleFiles: BundleFile[] = [
    toJsonFile(`${root}/bundle_manifest.json`, buildBundleManifest(context)),
    toJsonFile(`${root}/document.json`, bundledDocument),
    toJsonFile(`${root}/merge_decision_audit.json`, { entries: buildMergeDecisionAuditEntries(bundledDocument) }),
    toJsonFile(`${root}/view.json`, viewState),
  ];
  appendHandDrawnCueAssetFile(bundleFiles, root, bundledDocument, context);

  if (context.includeOutline) {
    const outline = buildReadingOutlineMd(contentDocument, context.readingState, resolveOutlineOptions(context, safeMode));
    bundleFiles.push({ path: `${root}/outline.md`, content: outline, mime: "text/markdown" });
  }

  if (context.includeDiagnostics) {
    bundleFiles.push({
      path: `${root}/diagnostics.md`,
      content: buildDiagnosticsMd(contentDocument, context),
      mime: "text/markdown",
    });
  }

  if (shouldIncludeSelectedCardTraces(context) && context.selectedCardId) {
    const evidenceTrace = buildEvidenceTraceMd(contentDocument, context.selectedCardId, { safeMode });
    if (!evidenceTrace.startsWith("Error:")) {
      bundleFiles.push({
        path: `${root}/evidence_trace_${context.selectedCardId}.md`,
        content: evidenceTrace,
        mime: "text/markdown",
      });
    }

    const contradictionTrace = buildContradictionTraceMd(contentDocument, context.selectedCardId, { safeMode });
    if (!contradictionTrace.startsWith("Error:")) {
      bundleFiles.push({
        path: `${root}/contradiction_trace_${context.selectedCardId}.md`,
        content: contradictionTrace,
        mime: "text/markdown",
      });
    }

    const analytics = computeTraceAnalytics(contentDocument, context.selectedCardId, { kind: "both", safeMode, maxHops: 4, maxNodes: 80, includeCycleDetection: true });
    bundleFiles.push({
      path: `${root}/trace_analytics_${context.selectedCardId}.md`,
      content: buildTraceAnalyticsMd(analytics),
      mime: "text/markdown",
    });
  }

  return [...bundleFiles].sort((left, right) => left.path.localeCompare(right.path));
}

export async function buildExportBundleWithWorkers(
  doc: DocumentV1,
  viewState: unknown,
  context: BundleExportContext,
  options: { signal?: AbortSignal; onProgress?: (stage: BundleExportProgressStage) => void } = {}
 ): Promise<BundleFile[]> {
  const safeMode = context.safeMode ?? true;
  const contentDocument = resolveShareDocument(doc, context);
  const bundledDocument = resolveBundledDocument(contentDocument, context);
  const root = context.rootFolderPath.endsWith("/") ? context.rootFolderPath.slice(0, -1) : context.rootFolderPath;
  const bundleFiles: BundleFile[] = [
    toJsonFile(`${root}/bundle_manifest.json`, buildBundleManifest(context)),
    toJsonFile(`${root}/document.json`, bundledDocument),
    toJsonFile(`${root}/merge_decision_audit.json`, { entries: buildMergeDecisionAuditEntries(bundledDocument) }),
    toJsonFile(`${root}/view.json`, viewState),
  ];
  appendHandDrawnCueAssetFile(bundleFiles, root, bundledDocument, context);

  if (context.includeOutline) {
    const outline = buildReadingOutlineMd(contentDocument, context.readingState, resolveOutlineOptions(context, safeMode));
    bundleFiles.push({ path: `${root}/outline.md`, content: outline, mime: "text/markdown" });
  }

  const diagnosticsClient = new DiagnosticsWorkerClient();
  const traceClient = new TraceWorkerClient();
  try {
    if (context.includeDiagnostics) {
      options.onProgress?.("diagnostics");
      const diagnosticsOutcome = await diagnosticsClient.computeDiagnostics({
        doc: contentDocument,
        view: {
          readingMode: context.readingMode,
          reviewedOnly: context.reviewedOnly,
          collapsedIslandIds: [],
        },
        options: { safeMode, deterministicNowIso: context.deterministicNowIso },
      }, { signal: options.signal });
      if (diagnosticsOutcome.status === "cancelled") {
        throw new Error("Diagnostics generation cancelled");
      }
      bundleFiles.push({ path: `${root}/diagnostics.md`, content: diagnosticsOutcome.result.diagnosticsMd, mime: "text/markdown" });
    }

    if (shouldIncludeSelectedCardTraces(context) && context.selectedCardId) {
      const sharedOptions = {
        startCardId: context.selectedCardId,
        maxHops: 4,
        maxNodes: 80,
        safeMode,
        includeRationale: false,
      };
      options.onProgress?.("evidence_trace");
      const evidenceOutcome = await traceClient.computeTrace({ doc: contentDocument, options: { ...sharedOptions, kind: "evidence" } }, { signal: options.signal });
      if (evidenceOutcome.status === "cancelled") {
        throw new Error("Trace generation cancelled");
      }
      if (!evidenceOutcome.result.traceMd.startsWith("Error:")) {
        bundleFiles.push({ path: `${root}/evidence_trace_${context.selectedCardId}.md`, content: evidenceOutcome.result.traceMd, mime: "text/markdown" });
      }

      options.onProgress?.("contradiction_trace");
      const contradictionOutcome = await traceClient.computeTrace({ doc: contentDocument, options: { ...sharedOptions, kind: "contradiction" } }, { signal: options.signal });
      if (contradictionOutcome.status === "cancelled") {
        throw new Error("Trace generation cancelled");
      }
      if (!contradictionOutcome.result.traceMd.startsWith("Error:")) {
        bundleFiles.push({ path: `${root}/contradiction_trace_${context.selectedCardId}.md`, content: contradictionOutcome.result.traceMd, mime: "text/markdown" });
      }

      options.onProgress?.("trace_analytics");
      const analyticsOutcome = await traceClient.computeTraceAnalytics({
        doc: contentDocument,
        options: {
          startCardId: context.selectedCardId,
          kind: "both",
          maxHops: sharedOptions.maxHops,
          maxNodes: sharedOptions.maxNodes,
          safeMode,
          includeCycleDetection: true,
        },
      }, { signal: options.signal });
      if (analyticsOutcome.status === "cancelled") {
        throw new Error("Trace analytics generation cancelled");
      }
      bundleFiles.push({ path: `${root}/trace_analytics_${context.selectedCardId}.md`, content: analyticsOutcome.result.analyticsMd, mime: "text/markdown" });
    }
  } finally {
    diagnosticsClient.dispose();
    traceClient.dispose();
  }

  const integrityManifest = await buildIntegrityManifest(bundleFiles, context.deterministicNowIso);
  bundleFiles.push(toJsonFile(`${root}/integrity.json`, integrityManifest));
  return [...bundleFiles].sort((left, right) => left.path.localeCompare(right.path));
}

export async function buildBundleZipBlob(
  files: BundleFile[],
  options: { signal?: AbortSignal; onProgress?: (percent: number) => void } = {},
): Promise<Blob> {
  const bundleZipClient = new BundleZipWorkerClient();
  try {
    const outcome = await bundleZipClient.buildZip({ files }, options);
    if (outcome.status === "cancelled") {
      throw new Error("Bundle zip cancelled");
    }
    return new Blob([outcome.result.zipBuffer], { type: "application/zip" });
  } finally {
    bundleZipClient.dispose();
  }
}

export function downloadBlobAsFile(filename: string, blob: Blob): void {
  const anchor = document.createElement("a");
  const url = URL.createObjectURL(blob);
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

export function formatBundleTimestamp(value: Date): string {
  const year = String(value.getFullYear());
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  const hour = String(value.getHours()).padStart(2, "0");
  const minute = String(value.getMinutes()).padStart(2, "0");
  const second = String(value.getSeconds()).padStart(2, "0");
  return `${year}${month}${day}-${hour}${minute}${second}`;
}
