import { getDerivedIslandEdges } from "../island_edge_aggregate";
import type { DocumentV1, Island } from "../types";
import { buildReadingList, type ReadingPathViewState } from "./reading_path";

export type FindingEntityRef = {
  kind: "island" | "card";
  id: string;
};

export type Finding = {
  severity: "error" | "warn" | "info";
  code: string;
  title: string;
  detail: string;
  entityRefs?: FindingEntityRef[];
  suggestedAction?: string;
};

export type OutlineQualityReport = {
  generatedAt: string;
  stats: {
    totalIslands: number;
    totalCardsInPath: number;
    islandsWithTitleMissing: number;
    islandsWithSummaryMissing: number;
    islandsUnreviewed: number;
    relationSummariesTotal: number;
    relationSummariesUnreviewed: number;
    disconnectedIslands: number;
    pathLength: number;
  };
  findings: Finding[];
};

export type AnalyzeOutlineQualityOptions = {
  nowIso?: string;
  collapsedIslandIds?: ReadonlySet<string>;
};

function normalizeEmptyText(value: string | undefined): boolean {
  return (value ?? "").trim().length === 0;
}

function countIslandDegrees(doc: DocumentV1): Map<string, number> {
  const degreeByIslandId = new Map<string, number>(doc.islands.map((island) => [island.id, 0]));

  const addEdge = (a: string, b: string) => {
    if (a === b || !degreeByIslandId.has(a) || !degreeByIslandId.has(b)) {
      return;
    }

    degreeByIslandId.set(a, (degreeByIslandId.get(a) ?? 0) + 1);
    degreeByIslandId.set(b, (degreeByIslandId.get(b) ?? 0) + 1);
  };

  for (const edge of doc.edges) {
    const fromKind = edge.fromKind === "island" ? "island" : "card";
    const toKind = edge.toKind === "island" ? "island" : "card";
    if (fromKind === "island" && toKind === "island") {
      addEdge(edge.fromId, edge.toId);
    }
  }

  for (const derived of getDerivedIslandEdges(doc)) {
    addEdge(derived.fromId, derived.toId);
  }

  return degreeByIslandId;
}

function pickIslandRefs(islands: Island[], predicate: (island: Island) => boolean): FindingEntityRef[] {
  return islands.filter(predicate).slice(0, 10).map((island) => ({ kind: "island", id: island.id }));
}

export function analyzeOutlineQuality(
  doc: DocumentV1,
  readingState: ReadingPathViewState,
  options: AnalyzeOutlineQualityOptions = {},
): OutlineQualityReport {
  const list = buildReadingList(doc, readingState);
  const islands = doc.islands;
  const islandCount = islands.length;

  const islandsWithTitleMissing = islands.filter((island) => normalizeEmptyText(island.title)).length;
  const islandsWithSummaryMissing = islands.filter((island) => normalizeEmptyText(island.summaryText)).length;
  const islandsUnreviewed = islands.filter((island) => island.summaryReviewed !== true).length;

  const reviewedIslands = islands.filter((island) => island.summaryReviewed === true);
  const reviewedSummaryEmptyCount = reviewedIslands.filter((island) => normalizeEmptyText(island.summaryText)).length;

  const relationSummariesPresent = Array.isArray(doc.relationSummaries);
  const relationSummaries = doc.relationSummaries ?? [];
  const relationSummariesTotal = relationSummaries.length;
  const relationSummariesUnreviewed = relationSummaries.filter((summary) => summary.reviewed !== true).length;

  const degreeByIslandId = countIslandDegrees(doc);
  const disconnectedIslands = Array.from(degreeByIslandId.values()).filter((degree) => degree === 0).length;

  const totalCardsInPath = list.filter((entry) => entry.kind === "card").length;
  const pathLength = list.length;

  const refsInIsland = new Set<string>();
  for (const island of islands) {
    for (const cardId of island.cardIds) {
      refsInIsland.add(cardId);
    }
  }

  const loneCards = doc.cards.filter((card) => !refsInIsland.has(card.id));
  const collapsedCount = options.collapsedIslandIds?.size ?? 0;

  const findings: Finding[] = [];

  if (islandCount > 0 && islandsWithTitleMissing / islandCount > 0.3) {
    findings.push({
      severity: "error",
      code: "Q001",
      title: "Many islands are missing titles",
      detail: `${islandsWithTitleMissing}/${islandCount} islands have no title (threshold: >30%).`,
      entityRefs: pickIslandRefs(islands, (island) => normalizeEmptyText(island.title)),
      suggestedAction: "Add short titles for unlabeled islands to make the outline explainable at a glance.",
    });
  }

  if (islandCount > 0 && islandsWithSummaryMissing / islandCount > 0.4) {
    findings.push({
      severity: "warn",
      code: "Q002",
      title: "Many islands are missing summaries",
      detail: `${islandsWithSummaryMissing}/${islandCount} islands have empty summaries (threshold: >40%).`,
      entityRefs: pickIslandRefs(islands, (island) => normalizeEmptyText(island.summaryText)),
      suggestedAction: "Fill one- or two-line summaries for key islands.",
    });
  }

  if (islandCount > 0 && islandsUnreviewed / islandCount > 0.5) {
    findings.push({
      severity: "warn",
      code: "Q003",
      title: "Unreviewed summaries dominate",
      detail: `${islandsUnreviewed}/${islandCount} island summaries are unreviewed (threshold: >50%).`,
      entityRefs: pickIslandRefs(islands, (island) => island.summaryReviewed !== true),
      suggestedAction: "Review and confirm summaries before sharing the outline.",
    });
  }

  if (relationSummariesTotal < Math.max(0, islandCount - 1)) {
    findings.push({
      severity: "warn",
      code: "Q004",
      title: "Relation summaries may be insufficient",
      detail: `Relation summaries: ${relationSummariesTotal}. Heuristic target: at least ${Math.max(0, islandCount - 1)} for ${islandCount} islands.${relationSummariesPresent ? "" : " (No relation summary store found in document; treated as 0 deterministically.)"}`,
      suggestedAction: "Add relation summaries that explain why islands are connected.",
    });
  }

  if (islandCount > 0 && disconnectedIslands / islandCount > 0.2) {
    findings.push({
      severity: "info",
      code: "Q005",
      title: "Many islands are not connected to other islands",
      detail: `${disconnectedIslands}/${islandCount} islands have no island-to-island connections (threshold: >20%).`,
      entityRefs: pickIslandRefs(islands, (island) => (degreeByIslandId.get(island.id) ?? 0) === 0),
      // DOMAIN-SCORING-SURFACE-01 (案A): island independence is a value in
      // the method (kj_technique.md §4), so disconnectedness is a neutral
      // observation, not a defect to resolve. No resolution-oriented action.
      suggestedAction: "If the independence is intentional, make it explicit with a relation summary or edge label.",
    });
  }

  if (pathLength > 30 && islandCount > 0 && collapsedCount <= 1) {
    findings.push({
      severity: "info",
      code: "Q006",
      title: "Reading path is long with little hierarchy usage",
      detail: `Path length is ${pathLength} and only ${collapsedCount} island(s) are collapsed.`,
      suggestedAction: "Use collapse/overview to reduce scan load for long outlines.",
    });
  }

  if (readingState.readingMode === "islands+cards" && islandCount > 0 && doc.cards.length > 0) {
    if (loneCards.length > 0) {
      // DOMAIN-SCORING-SURFACE-01 (案A): a lone card is a neutral fact, not a
      // defect — kj_technique.md:109 "孤立した1枚が最も重要なことがある". So
      // this is reported as a neutral observation without a resolution action.
      findings.push({
        severity: "info",
        code: "Q007",
        title: "Lone cards are present",
        detail: `${loneCards.length} card(s) are not assigned to any island. A lone card can carry the most important meaning — keep it ungrouped unless it belongs.`,
        entityRefs: loneCards.slice(0, 10).map((card) => ({ kind: "card" as const, id: card.id })),
      });
    } else {
      // kj_technique.md:195 — "どの束にも入らないカードがゼロ枚（無理に入れた
      // 疑い）". Zero ungrouped cards is itself a failure signal: cards may have
      // been forced into islands. Surface it instead of treating it as ideal.
      findings.push({
        severity: "warn",
        code: "Q009",
        title: "No cards outside islands (possible forced grouping)",
        detail: `Every card is assigned to an island. kj_technique.md lists zero ungrouped cards as a failure signal — cards may have been forced into islands they do not belong to.`,
      });
    }
  }

  if (reviewedIslands.length > 0 && reviewedSummaryEmptyCount / reviewedIslands.length > 0.1) {
    findings.push({
      severity: "warn",
      code: "Q008",
      title: "Too many reviewed summaries are empty",
      detail: `${reviewedSummaryEmptyCount}/${reviewedIslands.length} reviewed summaries are empty (threshold: >10%).`,
      entityRefs: pickIslandRefs(reviewedIslands, (island) => normalizeEmptyText(island.summaryText)),
      suggestedAction: "Either fill the reviewed summaries or set them back to unreviewed.",
    });
  }

  return {
    generatedAt: options.nowIso ?? new Date().toISOString(),
    stats: {
      totalIslands: islandCount,
      totalCardsInPath,
      islandsWithTitleMissing,
      islandsWithSummaryMissing,
      islandsUnreviewed,
      relationSummariesTotal,
      relationSummariesUnreviewed,
      disconnectedIslands,
      pathLength,
    },
    findings,
  };
}
