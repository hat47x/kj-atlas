import type { Card, DocumentV2, Island, RelationSummary } from "../types";
import { SafeModePolicy, type SafeModeContext } from "../policy/safe_mode";
import { buildReadingList, type ReadingMode } from "./reading_path";
import type { OutlineQualityReport } from "./outline_quality";
import type { Recommendation } from "./recommendations";

const DEFAULT_MAX_SNIPPET_LEN = 140;

export type ReadingOutlineState = {
  readingNavEnabled: boolean;
  readingIndex: number;
  readingMode: ReadingMode;
  reviewedOnly: boolean;
  safeMode: boolean;
  lod?: string | null;
  generatedAt?: string;
};

export type ReadingOutlineOptions = {
  context?: SafeModeContext;
  includeCardTexts?: boolean;
  includeUnreviewedSummaries?: boolean;
  includeRelationSummaries?: boolean;
  maxSnippetLen?: number;
  appendDiagnostics?: boolean;
  diagnosticsReport?: OutlineQualityReport | null;
  appendRecommendations?: boolean;
  recommendations?: Recommendation[];
  /** DOMAIN-KA-01 (schemas.md §17.4): optional, default-OFF section listing cards with KA fields set. */
  appendKaFields?: boolean;
};

function formatRecommendations(recommendations: Recommendation[]): string[] {
  const lines: string[] = ["## Suggested Next Steps", ""];

  if (recommendations.length === 0) {
    lines.push("1. No recommendations.", "");
    return lines;
  }

  recommendations.forEach((recommendation, index) => {
    lines.push(`${index + 1}. ${recommendation.title} [${recommendation.impactLevel}]`);
    lines.push(`   - ${recommendation.description}`);
    lines.push(`   - Why: ${recommendation.rationaleCodes.join(", ")}`);
    for (const action of recommendation.suggestedActions) {
      lines.push(`   - Action: ${action}`);
    }
  });
  lines.push("");

  return lines;
}

function formatDiagnostics(report: OutlineQualityReport): string[] {
  const lines: string[] = ["## Diagnostics", "", `GeneratedAt: ${report.generatedAt}`, ""];

  lines.push("| Metric | Value |", "| --- | ---: |");
  lines.push(`| totalIslands | ${report.stats.totalIslands} |`);
  lines.push(`| totalCardsInPath | ${report.stats.totalCardsInPath} |`);
  lines.push(`| islandsWithTitleMissing | ${report.stats.islandsWithTitleMissing} |`);
  lines.push(`| islandsWithSummaryMissing | ${report.stats.islandsWithSummaryMissing} |`);
  lines.push(`| islandsUnreviewed | ${report.stats.islandsUnreviewed} |`);
  lines.push(`| relationSummariesTotal | ${report.stats.relationSummariesTotal} |`);
  lines.push(`| relationSummariesUnreviewed | ${report.stats.relationSummariesUnreviewed} |`);
  lines.push(`| disconnectedIslands | ${report.stats.disconnectedIslands} |`);
  lines.push(`| pathLength | ${report.stats.pathLength} |`);
  lines.push("");

  if (report.findings.length === 0) {
    lines.push("- No findings.");
    lines.push("");
    return lines;
  }

  for (const finding of report.findings) {
    lines.push(`- [${finding.severity.toUpperCase()}] ${finding.code} ${finding.title}`);
    lines.push(`  - ${finding.detail}`);
    if (finding.suggestedAction) {
      lines.push(`  - Action: ${finding.suggestedAction}`);
    }
    if (finding.entityRefs && finding.entityRefs.length > 0) {
      lines.push(`  - Refs: ${finding.entityRefs.map((ref) => `${ref.kind}:${ref.id}`).join(", ")}`);
    }
  }
  lines.push("");

  return lines;
}

// DOMAIN-KA-01 (schemas.md §17.4): optional, default-OFF section — KA fields
// are never interleaved with a card's body text, and reuse card.text's
// SafeMode exposure gate (voice/value are equally-or-more sensitive drafts).
function formatKaFields(cards: Card[], context: SafeModeContext, safeMode: boolean): string[] {
  const cardsWithKa = cards.filter((card) => (card.ka?.voice?.length ?? 0) > 0 || (card.ka?.value?.length ?? 0) > 0);
  if (cardsWithKa.length === 0) {
    return [];
  }

  const lines: string[] = ["## KA Fields (inner voice / value)", ""];
  if (!SafeModePolicy.canExposeText("card.text", context, safeMode)) {
    lines.push("> [SAFE MODE: KA fields hidden]", "");
    return lines;
  }

  for (const card of cardsWithKa) {
    const parts: string[] = [];
    if (card.ka?.voice) {
      parts.push(`Inner voice: ${card.ka.voice}`);
    }
    if (card.ka?.value) {
      parts.push(`Value: ${card.ka.value}`);
    }
    lines.push(`- Card ${card.id} — ${parts.join(" / ")}`);
  }
  lines.push("");

  return lines;
}

function clipSnippet(value: string | undefined, maxLen: number, oneLine: boolean): string {
  const trimmed = (value ?? "").trim();
  if (trimmed.length === 0) {
    return "(untitled)";
  }

  const source = oneLine ? (trimmed.split(/\r?\n/, 1)[0]?.trim() || trimmed) : trimmed;
  if (source.length <= maxLen) {
    return source;
  }

  return `${source.slice(0, maxLen)}…`;
}

function formatMetaBlock(state: ReadingOutlineState): string[] {
  const lines = [
    `- GeneratedAt: ${state.generatedAt ?? new Date().toISOString()}`,
    `- Mode: ${state.readingMode}`,
    `- ReadingNavEnabled: ${state.readingNavEnabled}`,
    `- ReadingIndex: ${state.readingIndex}`,
    `- ReviewedOnly: ${state.reviewedOnly}`,
    `- SafeMode: ${state.safeMode}`,
  ];

  if (state.lod && state.lod.trim().length > 0) {
    lines.push(`- LOD: ${state.lod}`);
  }

  return lines;
}

function resolveIslandTitle(island: Island): string {
  const trimmed = island.title?.trim() ?? "";
  return trimmed.length > 0 ? trimmed : "(untitled)";
}

function formatSummaryBlock(summaryText: string, reviewed: boolean, includeUnreviewed: boolean): string[] {
  const trimmed = summaryText.trim();
  if (trimmed.length === 0) {
    return [];
  }

  if (reviewed) {
    return [trimmed];
  }

  if (!includeUnreviewed) {
    return ["> [UNREVIEWED HIDDEN]"];
  }

  return trimmed
    .split(/\r?\n/)
    .map((line, index) => (index === 0 ? `> [UNREVIEWED] ${line}` : `> ${line}`));
}

function sortRelationSummaries(summaries: RelationSummary[], islandsById: Map<string, Island>, pivotIslandId: string): RelationSummary[] {
  return [...summaries].sort((a, b) => {
    const otherAId = a.islandAId === pivotIslandId ? a.islandBId : a.islandAId;
    const otherBId = b.islandAId === pivotIslandId ? b.islandBId : b.islandAId;
    const otherATitle = resolveIslandTitle(islandsById.get(otherAId) ?? { id: "", cardIds: [] });
    const otherBTitle = resolveIslandTitle(islandsById.get(otherBId) ?? { id: "", cardIds: [] });

    if (otherATitle !== otherBTitle) {
      return otherATitle.localeCompare(otherBTitle);
    }

    if (otherAId !== otherBId) {
      return otherAId.localeCompare(otherBId);
    }

    return a.id.localeCompare(b.id);
  });
}

function getRelationLabel(summary: RelationSummary, island: Island, islandsById: Map<string, Island>): string {
  const otherIslandId = summary.islandAId === island.id ? summary.islandBId : summary.islandAId;
  const otherIsland = islandsById.get(otherIslandId);
  const otherTitle = otherIsland ? resolveIslandTitle(otherIsland) : "(untitled)";
  return `- [Relation] ${otherTitle} (${otherIslandId})`;
}

export function buildReadingOutlineMd(doc: DocumentV2, readingState: ReadingOutlineState, options: ReadingOutlineOptions = {}): string {
  const context = options.context ?? "ui";
  const includeCardTexts = options.includeCardTexts ?? false;
  const includeRelationSummaries = options.includeRelationSummaries ?? true;
  const appendDiagnostics = options.appendDiagnostics ?? false;
  const appendRecommendations = options.appendRecommendations ?? false;
  const appendKaFields = options.appendKaFields ?? false;
  const maxSnippetLen = options.maxSnippetLen ?? DEFAULT_MAX_SNIPPET_LEN;
  const includeUnreviewed = !readingState.safeMode && (options.includeUnreviewedSummaries ?? false);

  const cardsById = new Map(doc.cards.map((card) => [card.id, card]));
  const islandsById = new Map(doc.islands.map((island) => [island.id, island]));
  const list = buildReadingList(doc, {
    readingMode: readingState.readingMode,
    reviewedOnly: readingState.reviewedOnly,
  });

  const relationSummaries = doc.relationSummaries ?? [];
  const lines: string[] = ["# Reading Outline", "", ...formatMetaBlock(readingState), ""];

  for (const item of list) {
    if (item.kind === "island") {
      const island = islandsById.get(item.id);
      if (!island) {
        continue;
      }

      lines.push(`## [Island] ${resolveIslandTitle(island)}`);

      const summaryText = island.summaryText?.trim() ?? "";
      if (summaryText.length > 0) {
        const summaryReviewed = island.summaryReviewed === true;
        const summaryValue = SafeModePolicy.canExposeText("island.summary", context, readingState.safeMode)
          ? summaryText
          : SafeModePolicy.summarizeForSafeMode(summaryText);
        lines.push(...formatSummaryBlock(summaryValue, summaryReviewed, includeUnreviewed));
      }

      if (includeRelationSummaries) {
        const related = sortRelationSummaries(
          relationSummaries.filter((summary) => summary.islandAId === island.id || summary.islandBId === island.id),
          islandsById,
          island.id,
        );

        for (const relation of related) {
          lines.push(getRelationLabel(relation, island, islandsById));
          const relationText = SafeModePolicy.canExposeText("relation.summary", context, readingState.safeMode)
            ? relation.text
            : SafeModePolicy.summarizeForSafeMode(relation.text);
          lines.push(
            ...formatSummaryBlock(
              relationText,
              relation.reviewed,
              includeUnreviewed,
            ).map((line) => `  ${line}`),
          );
        }
      }

      lines.push("");
      continue;
    }

    const card: Card | undefined = cardsById.get(item.id);
    if (!card) {
      continue;
    }

    const cardSnippet = SafeModePolicy.canExposeText("card.text", context, readingState.safeMode)
      ? clipSnippet(card.text, maxSnippetLen, true)
      : `card:${card.id}`;
    lines.push(`### [Card] ${cardSnippet}`);
    if (includeCardTexts && SafeModePolicy.canExposeText("card.text", context, readingState.safeMode)) {
      lines.push(clipSnippet(card.text, maxSnippetLen, false));
    }
    lines.push("");
  }

  if (appendDiagnostics && options.diagnosticsReport) {
    lines.push(...formatDiagnostics(options.diagnosticsReport));
  }

  if (appendRecommendations) {
    lines.push(...formatRecommendations(options.recommendations ?? []));
  }

  if (appendKaFields) {
    lines.push(...formatKaFields(doc.cards, context, readingState.safeMode));
  }

  return `${lines.join("\n").trimEnd()}\n`;
}
