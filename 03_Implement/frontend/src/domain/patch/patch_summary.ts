import { SafeModePolicy } from "../policy/safe_mode";
import type { ConflictReport } from "./conflict_detect";
import type { PatchDocument } from "./patch_apply";

export type PatchSummaryModel = {
  headline: string;
  stats: {
    upsertCards: number;
    deleteCards: number;
    upsertIslands: number;
    deleteIslands: number;
    upsertEdges: number;
    deleteEdges: number;
    upsertRelationSummaries: number;
    deleteRelationSummaries: number;
    upsertEvidenceLinks: number;
    deleteEvidenceLinks: number;
  };
  highlights: { label: string; detail: string }[];
  warnings: string[];
};

type HighlightItem = {
  priority: number;
  stableKey: string;
  label: string;
  detail: string;
};

function clipText(value: string | undefined, maxLength = 60): string {
  const normalized = (value ?? "").trim();
  if (normalized.length <= maxLength) {
    return normalized;
  }

  return `${normalized.slice(0, maxLength)}…`;
}

function formatSnippet(value: string): string {
  return value.length > 0 ? value : "(empty)";
}

function formatHeadlineCount(count: number, singular: string, plural: string): string {
  return `${count} ${count === 1 ? singular : plural}`;
}

function buildHeadline(summary: PatchSummaryModel["stats"]): string {
  const segments: string[] = [];

  if (summary.upsertCards > 0) segments.push(`${formatHeadlineCount(summary.upsertCards, "card", "cards")} updated`);
  if (summary.deleteCards > 0) segments.push(`${formatHeadlineCount(summary.deleteCards, "card", "cards")} deleted`);
  if (summary.upsertIslands > 0) segments.push(`${formatHeadlineCount(summary.upsertIslands, "island", "islands")} added`);
  if (summary.deleteIslands > 0) segments.push(`${formatHeadlineCount(summary.deleteIslands, "island", "islands")} deleted`);
  if (summary.upsertEdges > 0) segments.push(`${formatHeadlineCount(summary.upsertEdges, "edge", "edges")} updated`);
  if (summary.deleteEdges > 0) segments.push(`${formatHeadlineCount(summary.deleteEdges, "edge", "edges")} deleted`);
  if (summary.upsertRelationSummaries > 0) {
    segments.push(`${formatHeadlineCount(summary.upsertRelationSummaries, "relation", "relations")} added`);
  }
  if (summary.deleteRelationSummaries > 0) {
    segments.push(`${formatHeadlineCount(summary.deleteRelationSummaries, "relation", "relations")} deleted`);
  }

  if (segments.length === 0) {
    return "Patch: no changes";
  }

  return `Patch: ${segments.slice(0, 3).join(", ")}`;
}

function buildWarnings(conflictReport?: ConflictReport, signatureMatch?: boolean): string[] {
  const warnings: string[] = [];

  if (signatureMatch === false) {
    warnings.push("Base signature mismatch: loaded patch baseline does not match the current document.");
  }

  const conflictCount = conflictReport?.conflicts.length ?? 0;
  if (conflictCount > 0) {
    warnings.push(`${conflictCount} conflict(s) detected in patch operations.`);
  }

  return warnings;
}

export function buildPatchSummary(
  patch: PatchDocument,
  conflictReport?: ConflictReport,
  signatureMatch?: boolean,
  safeMode: boolean = true
): PatchSummaryModel {
  const canExposeCardText = SafeModePolicy.canExposeText("card.text", "share", safeMode);
  const canExposeIslandSummary = SafeModePolicy.canExposeText("island.summary", "share", safeMode);
  const canExposeRelationSummary = SafeModePolicy.canExposeText("relation.summary", "share", safeMode);
  const stats: PatchSummaryModel["stats"] = {
    upsertCards: 0,
    deleteCards: 0,
    upsertIslands: 0,
    deleteIslands: 0,
    upsertEdges: 0,
    deleteEdges: 0,
    upsertRelationSummaries: 0,
    deleteRelationSummaries: 0,
    upsertEvidenceLinks: 0,
    deleteEvidenceLinks: 0,
  };

  const highlightItems: HighlightItem[] = [];

  for (const op of patch.ops) {
    switch (op.kind) {
      case "upsert_card":
        stats.upsertCards += 1;
        highlightItems.push({
          priority: 2,
          stableKey: `card:${op.card.id}`,
          label: `Card ${op.card.id}`,
          detail: canExposeCardText ? formatSnippet(clipText(op.card.text)) : SafeModePolicy.summarizeForSafeMode(op.card.text),
        });
        break;
      case "delete_card":
        stats.deleteCards += 1;
        highlightItems.push({
          priority: 2,
          stableKey: `card:${op.cardId}`,
          label: `Card ${op.cardId}`,
          detail: "deleted",
        });
        break;
      case "upsert_island":
        stats.upsertIslands += 1;
        highlightItems.push({
          priority: 0,
          stableKey: `island:${op.island.id}`,
          label: `Island ${op.island.id}`,
          detail: formatSnippet(
            clipText(
              `${op.island.title ?? ""} ${
                canExposeIslandSummary ? (op.island.summaryText ?? "") : SafeModePolicy.summarizeForSafeMode(op.island.summaryText ?? "")
              }`
            )
          ),
        });
        break;
      case "delete_island":
        stats.deleteIslands += 1;
        highlightItems.push({
          priority: 0,
          stableKey: `island:${op.islandId}`,
          label: `Island ${op.islandId}`,
          detail: "deleted",
        });
        break;
      case "upsert_edge":
        stats.upsertEdges += 1;
        break;
      case "delete_edge":
        stats.deleteEdges += 1;
        break;
      case "upsert_relation_summary":
        stats.upsertRelationSummaries += 1;
        highlightItems.push({
          priority: 1,
          stableKey: `relation:${op.relationSummary.sourceSignature}`,
          label: `Relation ${op.relationSummary.sourceSignature}`,
          detail: canExposeRelationSummary
            ? formatSnippet(clipText(op.relationSummary.text))
            : SafeModePolicy.summarizeForSafeMode(op.relationSummary.text),
        });
        break;
      case "delete_relation_summary":
        stats.deleteRelationSummaries += 1;
        highlightItems.push({
          priority: 1,
          stableKey: `relation:${op.sourceSignature}`,
          label: `Relation ${op.sourceSignature}`,
          detail: "deleted",
        });
        break;
    }
  }

  const highlights = highlightItems
    .sort((left, right) => {
      if (left.priority !== right.priority) {
        return left.priority - right.priority;
      }
      return left.stableKey.localeCompare(right.stableKey);
    })
    .slice(0, 10)
    .map((item) => ({ label: item.label, detail: item.detail }));

  return {
    headline: buildHeadline(stats),
    stats,
    highlights,
    warnings: buildWarnings(conflictReport, signatureMatch),
  };
}

export function formatPatchSummaryMarkdown(summary: PatchSummaryModel): string {
  const lines: string[] = [
    "## Summary",
    summary.headline,
    "",
    "## Stats",
    `- upsertCards: ${summary.stats.upsertCards}`,
    `- deleteCards: ${summary.stats.deleteCards}`,
    `- upsertIslands: ${summary.stats.upsertIslands}`,
    `- deleteIslands: ${summary.stats.deleteIslands}`,
    `- upsertEdges: ${summary.stats.upsertEdges}`,
    `- deleteEdges: ${summary.stats.deleteEdges}`,
    `- upsertRelationSummaries: ${summary.stats.upsertRelationSummaries}`,
    `- deleteRelationSummaries: ${summary.stats.deleteRelationSummaries}`,
    "",
    "## Highlights",
  ];

  if (summary.highlights.length === 0) {
    lines.push("- (none)");
  } else {
    for (const highlight of summary.highlights) {
      lines.push(`- ${highlight.label}: ${highlight.detail}`);
    }
  }

  if (summary.warnings.length > 0) {
    lines.push("", "## Warnings");
    for (const warning of summary.warnings) {
      lines.push(`- ${warning}`);
    }
  }

  return lines.join("\n");
}
