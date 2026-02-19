import type { Card, DocumentV2, Island, RelationSummary } from "../types";
import { buildReadingList, type ReadingMode } from "./reading_path";

const DEFAULT_MAX_SNIPPET_LEN = 140;

export type ReadingOutlineState = {
  readingNavEnabled: boolean;
  readingIndex: number;
  readingMode: ReadingMode;
  reviewedOnly: boolean;
  safeMode: boolean;
  lod?: string | null;
};

export type ReadingOutlineOptions = {
  includeCardTexts?: boolean;
  includeUnreviewedSummaries?: boolean;
  includeRelationSummaries?: boolean;
  maxSnippetLen?: number;
};

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
    `- GeneratedAt: ${new Date().toISOString()}`,
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
  const includeCardTexts = options.includeCardTexts ?? false;
  const includeRelationSummaries = options.includeRelationSummaries ?? true;
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
        lines.push(...formatSummaryBlock(summaryText, summaryReviewed, includeUnreviewed));
      }

      if (includeRelationSummaries) {
        const related = sortRelationSummaries(
          relationSummaries.filter((summary) => summary.islandAId === island.id || summary.islandBId === island.id),
          islandsById,
          island.id,
        );

        for (const relation of related) {
          lines.push(getRelationLabel(relation, island, islandsById));
          lines.push(
            ...formatSummaryBlock(
              relation.text,
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

    const cardSnippet = clipSnippet(card.text, maxSnippetLen, true);
    lines.push(`### [Card] ${cardSnippet}`);
    if (includeCardTexts) {
      lines.push(clipSnippet(card.text, maxSnippetLen, false));
    }
    lines.push("");
  }

  return `${lines.join("\n").trimEnd()}\n`;
}
