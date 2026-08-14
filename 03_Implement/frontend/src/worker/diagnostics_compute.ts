import { SafeModePolicy } from "../domain/policy/safe_mode";
import { analyzeContradictions } from "../domain/view/contradiction_checks";
import { analyzeDialecticBalance } from "../domain/view/dialectic_balance";
import { analyzeDistribution } from "../domain/view/distribution_checks";
import { analyzeOutlineQuality } from "../domain/view/outline_quality";
import { generateRecommendations } from "../domain/view/recommendations";
import { computeStructureMetrics } from "../domain/view/structural_metrics";
import { DIAGNOSTICS_DATA_SCHEMA_VERSION } from "./diagnostics_protocol";
import type { DiagnosticsData, DiagnosticsRequestPayload } from "./diagnostics_protocol";

function toSafeOutline(data: DiagnosticsData["outlineReport"]): DiagnosticsData["outlineReport"] {
  return {
    ...data,
    findings: data.findings.map((finding) => ({
      ...finding,
      detail: SafeModePolicy.redactText(finding.detail, true),
    })),
  };
}

function buildDiagnosticsMd(data: DiagnosticsData, safeMode: boolean): string {
  const lines: string[] = ["# Diagnostics", "", "## Outline quality report (I10)", ""];
  lines.push(`- schemaVersion: ${data.schemaVersion}`);
  lines.push(`- totalIslands: ${data.outlineReport.stats.totalIslands}`);
  lines.push(`- totalCardsInPath: ${data.outlineReport.stats.totalCardsInPath}`);
  lines.push(`- pathLength: ${data.outlineReport.stats.pathLength}`);
  lines.push(`- findings: ${data.outlineReport.findings.length}`);
  for (const finding of data.outlineReport.findings) {
    const refs = (finding.entityRefs ?? []).map((ref) => `${ref.kind}:${ref.id}`).sort();
    lines.push(`- [${finding.severity.toUpperCase()}] ${finding.code}: ${finding.title}`);
    if (finding.detail.trim().length > 0 && SafeModePolicy.canExposeText("diagnostics.detail", "ui", safeMode)) {
      lines.push(`  - detail: ${finding.detail}`);
    }
    if (refs.length > 0) {
      lines.push(`  - refs: ${refs.join(", ")}`);
    }
  }

  lines.push("", "## Recommendations (I11)", "", `- count: ${data.recommendations.length}`);
  for (const recommendation of data.recommendations) {
    const targets = [...(recommendation.targetEntities ?? [])].sort((a, b) => `${a.kind}:${a.id}`.localeCompare(`${b.kind}:${b.id}`));
    lines.push(`- ${recommendation.id}: ${recommendation.title}`);
    if (targets.length > 0) {
      lines.push(`  - targets: ${targets.map((target) => `${target.kind}:${target.id}`).join(", ")}`);
    }
  }

  lines.push("", "## Contradiction signals (I12)", "", `- signals: ${data.contradictionReport.stats.signals}`);
  for (const signal of data.contradictionReport.signals) {
    const refs = signal.entityRefs.map((ref) => `${ref.kind}:${ref.idOrSignature}`).sort();
    lines.push(`- [${signal.severity.toUpperCase()}] ${signal.code}: ${signal.title}`);
    if (refs.length > 0) lines.push(`  - refs: ${refs.join(", ")}`);
  }

  lines.push("", "## Distribution signals (I13)", "", `- islands: ${data.distributionReport.stats.islandCount}`, `- cards: ${data.distributionReport.stats.cardCount}`, `- findings: ${data.distributionReport.findings.length}`);
  for (const finding of data.distributionReport.findings) {
    lines.push(`- [${finding.severity.toUpperCase()}] ${finding.code}: ${finding.title}`);
    const islandIds = [...(finding.islandIds ?? [])].sort();
    if (islandIds.length > 0) lines.push(`  - islands: ${islandIds.join(", ")}`);
  }

  lines.push("", "## Dialectic balance (I19)", "", `- hypotheses: ${data.dialecticBalanceReport.stats.hypothesisCount}`, `- claims: ${data.dialecticBalanceReport.stats.claimCount}`, `- facts: ${data.dialecticBalanceReport.stats.factCount}`, `- findings: ${data.dialecticBalanceReport.findings.length}`);
  for (const finding of data.dialecticBalanceReport.findings) {
    lines.push(`- [${finding.severity.toUpperCase()}] ${finding.code}: ${finding.title}`);
    const cardIds = [...(finding.cardIds ?? [])].sort();
    if (cardIds.length > 0) lines.push(`  - cards: ${cardIds.join(", ")}`);
  }

  lines.push("", "## Metrics", "", "| metric | value |", "| --- | ---: |");
  lines.push(`| cardCount | ${data.structuralMetrics.cardCount} |`);
  lines.push(`| islandCount | ${data.structuralMetrics.islandCount} |`);
  lines.push(`| evidenceLinkCount | ${data.structuralMetrics.evidenceLinkCount} |`);
  lines.push(`| evidenceLinkDensity | ${data.structuralMetrics.evidenceLinkDensity} |`);
  lines.push(`| isolatedCardCount | ${data.structuralMetrics.isolatedCardCount} |`);
  lines.push(`| isolationRate | ${data.structuralMetrics.isolationRate} |`);
  lines.push(`| connectedComponentCount | ${data.structuralMetrics.connectedComponentCount} |`);
  lines.push(`| largestComponentRatio | ${data.structuralMetrics.largestComponentRatio} |`);
  lines.push(`| averageDegree | ${data.structuralMetrics.averageDegree} |`);
  lines.push(`| degreeP95 | ${data.structuralMetrics.degreeP95} |`);
  lines.push(`| degreeSkewRatio | ${data.structuralMetrics.degreeSkewRatio} |`);
  lines.push(`| bridgeEdgeCount | ${data.structuralMetrics.bridgeEdgeCount} |`);
  if (data.structuralMetrics.contradictionRatio !== null) {
    lines.push(`| contradictionRatio | ${data.structuralMetrics.contradictionRatio} |`);
  }
  if (data.structuralMetrics.reviewedCoverage !== null) {
    lines.push(`| reviewedCoverage | ${data.structuralMetrics.reviewedCoverage} |`);
  }

  lines.push("", "### islandSizeDistribution", "", "| size | islands |", "| ---: | ---: |");
  if (data.structuralMetrics.islandSizeDistribution.length === 0) {
    lines.push("| (none) | 0 |");
  } else {
    for (const bin of data.structuralMetrics.islandSizeDistribution) {
      lines.push(`| ${bin.size} | ${bin.islands} |`);
    }
  }

  return `${lines.join("\n")}\n`;
}

export function computeDiagnostics(payload: DiagnosticsRequestPayload): { diagnosticsData: DiagnosticsData; diagnosticsMd: string } {
  const safeMode = payload.options?.safeMode ?? true;
  const nowIso = payload.options?.deterministicNowIso;
  const outline = analyzeOutlineQuality(payload.doc, { readingMode: payload.view.readingMode, reviewedOnly: payload.view.reviewedOnly }, { nowIso, collapsedIslandIds: new Set(payload.view.collapsedIslandIds ?? []) });
  const recommendations = generateRecommendations(outline, payload.doc, { readingMode: payload.view.readingMode, reviewedOnly: payload.view.reviewedOnly });
  const contradiction = analyzeContradictions(payload.doc, nowIso);
  const distribution = analyzeDistribution(payload.doc, nowIso);
  const dialectic = analyzeDialecticBalance(payload.doc, nowIso);
  const structuralMetrics = computeStructureMetrics(payload.doc, payload.view);

  const diagnosticsData: DiagnosticsData = {
    schemaVersion: DIAGNOSTICS_DATA_SCHEMA_VERSION,
    outlineReport: safeMode ? toSafeOutline(outline) : outline,
    recommendations,
    contradictionReport: contradiction,
    distributionReport: distribution,
    dialecticBalanceReport: dialectic,
    structuralMetrics,
  };

  return {
    diagnosticsData,
    diagnosticsMd: buildDiagnosticsMd(diagnosticsData, safeMode),
  };
}
