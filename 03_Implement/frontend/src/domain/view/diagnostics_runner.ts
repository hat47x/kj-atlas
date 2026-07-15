import { analyzeClaimTypeMix, type ClaimTypeMixReport } from "./claim_type_checks";
import { analyzeContradictions, type ContradictionReport } from "./contradiction_checks";
import { analyzeDialecticBalance, type DialecticBalanceReport } from "./dialectic_balance";
import { analyzeDistribution, type DistributionReport } from "./distribution_checks";
import { analyzeEvidenceGaps, type EvidenceGapReport } from "./evidence_gap_checks";
import { analyzeOutlineQuality, type OutlineQualityReport } from "./outline_quality";
import type { ReadingMode } from "./reading_path";
import type { DocumentV1 } from "../types";
import type { ComputeTaskContext } from "../../utils/compute_scheduler";

export type DiagnosticsGuardrails = {
  maxNodes?: number;
  maxMs?: number;
};

export type DiagnosticsRunResult = {
  report: OutlineQualityReport;
  contradiction: ContradictionReport;
  distribution: DistributionReport;
  claimTypeMix: ClaimTypeMixReport;
  evidenceGaps: EvidenceGapReport;
  dialecticBalance: DialecticBalanceReport;
  truncated: boolean;
  notes: string[];
};

export async function runDiagnosticsIncremental(
  doc: DocumentV1,
  opts: { readingMode: ReadingMode; reviewedOnly: boolean; collapsedIslandIds: ReadonlySet<string> },
  ctx: ComputeTaskContext,
  guardrails: DiagnosticsGuardrails = {}
): Promise<DiagnosticsRunResult> {
  const maxNodes = Math.max(1, Math.floor(guardrails.maxNodes ?? 1000));
  const maxMs = Math.max(1, Math.floor(guardrails.maxMs ?? 2000));
  const startedAt = Date.now();
  const notes: string[] = [];

  const sections = [
    "Outline quality",
    "Contradictions",
    "Distribution",
    "Claim type mix",
    "Evidence gaps",
    "Dialectic balance",
  ];

  const nodeCount = doc.cards.length + doc.islands.length + (doc.evidenceLinks?.length ?? 0);
  const shouldTruncate = nodeCount > maxNodes;
  if (shouldTruncate) {
    notes.push(`Truncated due to node limit (${nodeCount}/${maxNodes}).`);
  }

  ctx.reportProgress({ message: `Running ${sections[0]}`, completed: 0, total: sections.length });
  const report = analyzeOutlineQuality(doc, { readingMode: opts.readingMode, reviewedOnly: opts.reviewedOnly }, { collapsedIslandIds: opts.collapsedIslandIds });
  await ctx.yieldToMainThread();
  if (ctx.isCancelled()) {
    return {
      report,
      contradiction: analyzeContradictions(doc),
      distribution: analyzeDistribution(doc),
      claimTypeMix: analyzeClaimTypeMix(doc),
      evidenceGaps: analyzeEvidenceGaps(doc),
      dialecticBalance: analyzeDialecticBalance(doc),
      truncated: true,
      notes: ["Cancelled"],
    };
  }

  const contradiction = analyzeContradictions(doc);
  ctx.reportProgress({ message: `Running ${sections[1]}`, completed: 2, total: sections.length });
  await ctx.yieldToMainThread();
  const distribution = analyzeDistribution(doc);
  ctx.reportProgress({ message: `Running ${sections[2]}`, completed: 3, total: sections.length });
  await ctx.yieldToMainThread();
  const claimTypeMix = analyzeClaimTypeMix(doc);
  ctx.reportProgress({ message: `Running ${sections[3]}`, completed: 4, total: sections.length });
  await ctx.yieldToMainThread();
  const evidenceGaps = analyzeEvidenceGaps(doc);
  ctx.reportProgress({ message: `Running ${sections[4]}`, completed: 5, total: sections.length });
  await ctx.yieldToMainThread();
  const dialecticBalance = analyzeDialecticBalance(doc);
  ctx.reportProgress({ message: `Running ${sections[5]}`, completed: 6, total: sections.length });

  if (Date.now() - startedAt > maxMs) {
    notes.push(`Truncated due to time limit (${maxMs}ms).`);
  }

  return {
    report,
    contradiction,
    distribution,
    claimTypeMix,
    evidenceGaps,
    dialecticBalance,
    truncated: shouldTruncate || Date.now() - startedAt > maxMs,
    notes,
  };
}
