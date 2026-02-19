import JSZip from "jszip";
import type { DocumentV2 } from "../domain/types";
import { buildContradictionTraceMd } from "../domain/view/contradiction_trace";
import { analyzeContradictions, type ContradictionReport } from "../domain/view/contradiction_checks";
import { analyzeDialecticBalance, type DialecticBalanceReport } from "../domain/view/dialectic_balance";
import { analyzeDistribution, type DistributionReport } from "../domain/view/distribution_checks";
import { buildEvidenceTraceMd } from "../domain/view/evidence_trace";
import { analyzeOutlineQuality, type OutlineQualityReport } from "../domain/view/outline_quality";
import { buildReadingOutlineMd, type ReadingOutlineOptions, type ReadingOutlineState } from "../domain/view/reading_outline";
import { generateRecommendations } from "../domain/view/recommendations";
import type { ReadingMode } from "../domain/view/reading_path";

export type BundleFile = {
  path: string;
  content: string | Uint8Array;
  mime: string;
};

export type BundleExportContext = {
  rootFolderPath: string;
  safeMode: boolean;
  includeOutline: boolean;
  includeDiagnostics: boolean;
  includeSelectedCardTraces: boolean;
  selectedCardId: string | null;
  deterministicNowIso: string;
  readingState: ReadingOutlineState;
  readingMode: ReadingMode;
  reviewedOnly: boolean;
  outlineOptions?: ReadingOutlineOptions;
  outlineQualityReport?: OutlineQualityReport | null;
  contradictionReport?: ContradictionReport | null;
  distributionReport?: DistributionReport | null;
  dialecticBalanceReport?: DialecticBalanceReport | null;
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

function summarizeRecommendations(doc: DocumentV2, report: OutlineQualityReport, readingMode: ReadingMode, reviewedOnly: boolean): string[] {
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

function buildDiagnosticsMd(doc: DocumentV2, context: BundleExportContext): string {
  const outlineReport = context.outlineQualityReport ?? analyzeOutlineQuality(doc, { readingMode: context.readingMode, reviewedOnly: context.reviewedOnly }, { nowIso: context.deterministicNowIso });
  const contradictionReport = context.contradictionReport ?? analyzeContradictions(doc, context.deterministicNowIso);
  const distributionReport = context.distributionReport ?? analyzeDistribution(doc, context.deterministicNowIso);
  const dialecticBalanceReport = context.dialecticBalanceReport ?? analyzeDialecticBalance(doc, context.deterministicNowIso);

  const lines: string[] = ["# Diagnostics", ""];
  lines.push(...summarizeOutlineQuality(outlineReport, context.safeMode));
  lines.push(...summarizeRecommendations(doc, outlineReport, context.readingMode, context.reviewedOnly));
  lines.push(...summarizeContradictions(contradictionReport));
  lines.push(...summarizeDistribution(distributionReport));
  lines.push(...summarizeDialecticBalance(dialecticBalanceReport));
  return `${lines.join("\n")}\n`;
}

export function buildExportBundle(doc: DocumentV2, viewState: unknown, context: BundleExportContext): BundleFile[] {
  const root = context.rootFolderPath.endsWith("/") ? context.rootFolderPath.slice(0, -1) : context.rootFolderPath;
  const bundleFiles: BundleFile[] = [
    toJsonFile(`${root}/document.json`, doc),
    toJsonFile(`${root}/view.json`, viewState),
  ];

  if (context.includeOutline) {
    const outline = buildReadingOutlineMd(doc, context.readingState, {
      ...context.outlineOptions,
      includeUnreviewedSummaries: context.safeMode ? false : context.outlineOptions?.includeUnreviewedSummaries,
    });
    bundleFiles.push({ path: `${root}/outline.md`, content: outline, mime: "text/markdown" });
  }

  if (context.includeDiagnostics) {
    bundleFiles.push({
      path: `${root}/diagnostics.md`,
      content: buildDiagnosticsMd(doc, context),
      mime: "text/markdown",
    });
  }

  if (context.includeSelectedCardTraces && context.selectedCardId) {
    const evidenceTrace = buildEvidenceTraceMd(doc, context.selectedCardId);
    if (!evidenceTrace.startsWith("Error:")) {
      bundleFiles.push({
        path: `${root}/evidence_trace_${context.selectedCardId}.md`,
        content: evidenceTrace,
        mime: "text/markdown",
      });
    }

    const contradictionTrace = buildContradictionTraceMd(doc, context.selectedCardId);
    if (!contradictionTrace.startsWith("Error:")) {
      bundleFiles.push({
        path: `${root}/contradiction_trace_${context.selectedCardId}.md`,
        content: contradictionTrace,
        mime: "text/markdown",
      });
    }
  }

  return [...bundleFiles].sort((left, right) => left.path.localeCompare(right.path));
}

export async function buildBundleZipBlob(files: BundleFile[]): Promise<Blob> {
  const zip = new JSZip();
  for (const file of [...files].sort((left, right) => left.path.localeCompare(right.path))) {
    zip.file(file.path, file.content);
  }

  return zip.generateAsync({ type: "blob" });
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
