import type { DocumentV1 } from "../types";

export type DistributionFinding = {
  severity: "warn" | "info";
  code: string;
  title: string;
  detail: string;
  islandIds?: string[];
  suggestedAction?: string;
};

export type DistributionReport = {
  generatedAt: string;
  stats: {
    islandCount: number;
    cardCount: number;
    avgCardsPerIsland: number;
    medianCardsPerIsland: number;
    p90CardsPerIsland: number;
    islandsOverloadedCount: number;
    islandsTinyCount: number;
    isolatedIslandsCount: number;
  };
  findings: DistributionFinding[];
};

type IslandMetric = {
  id: string;
  cardCount: number;
  degree: number;
};

export type DistributionIslandRanking = {
  id: string;
  cardCount: number;
  degree: number;
};

export type DistributionRankings = {
  loaded: DistributionIslandRanking[];
  isolated: DistributionIslandRanking[];
};

function quantile(sortedValues: number[], q: number): number {
  if (sortedValues.length === 0) {
    return 0;
  }

  if (sortedValues.length === 1) {
    return sortedValues[0] ?? 0;
  }

  const index = (sortedValues.length - 1) * q;
  const lower = Math.floor(index);
  const upper = Math.ceil(index);
  if (lower === upper) {
    return sortedValues[lower] ?? 0;
  }

  const lowerValue = sortedValues[lower] ?? 0;
  const upperValue = sortedValues[upper] ?? 0;
  return lowerValue + (upperValue - lowerValue) * (index - lower);
}

function average(values: number[]): number {
  if (values.length === 0) {
    return 0;
  }

  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function buildIslandDegreeMap(doc: DocumentV1): Map<string, number> {
  const degreeByIslandId = new Map<string, number>();
  for (const island of doc.islands) {
    degreeByIslandId.set(island.id, 0);
  }

  for (const edge of doc.edges) {
    if (edge.fromKind !== "island" || edge.toKind !== "island") {
      continue;
    }

    if (!degreeByIslandId.has(edge.fromId) || !degreeByIslandId.has(edge.toId)) {
      continue;
    }

    degreeByIslandId.set(edge.fromId, (degreeByIslandId.get(edge.fromId) ?? 0) + 1);
    if (edge.toId !== edge.fromId) {
      degreeByIslandId.set(edge.toId, (degreeByIslandId.get(edge.toId) ?? 0) + 1);
    }
  }

  return degreeByIslandId;
}

export function analyzeDistribution(doc: DocumentV1, nowIso: string = new Date().toISOString()): DistributionReport {
  const islandCount = doc.islands.length;
  const cardCount = doc.cards.length;
  const degreeByIslandId = buildIslandDegreeMap(doc);

  const metrics: IslandMetric[] = doc.islands.map((island) => ({
    id: island.id,
    cardCount: island.cardIds.length,
    degree: degreeByIslandId.get(island.id) ?? 0,
  }));

  const cardCounts = metrics.map((item) => item.cardCount).sort((left, right) => left - right);
  const avgCardsPerIsland = average(cardCounts);
  const medianCardsPerIsland = quantile(cardCounts, 0.5);
  const p90CardsPerIsland = quantile(cardCounts, 0.9);
  const overloadedThreshold = Math.max(20, p90CardsPerIsland);

  const overloadedIslands = metrics
    .filter((item) => item.cardCount >= overloadedThreshold)
    .sort((left, right) => (right.cardCount - left.cardCount) || left.id.localeCompare(right.id));
  const tinyIslands = metrics.filter((item) => item.cardCount <= 1);
  const isolatedIslands = metrics
    .filter((item) => item.degree === 0)
    .sort((left, right) => (right.cardCount - left.cardCount) || left.id.localeCompare(right.id));

  const averageDegree = average(metrics.map((item) => item.degree));

  const findings: DistributionFinding[] = [];

  if (overloadedIslands.length > 0) {
    const topOverloaded = overloadedIslands.slice(0, 5);
    findings.push({
      severity: "warn",
      code: "D001",
      title: "Overloaded islands detected",
      detail: `カード数が閾値(${overloadedThreshold.toFixed(1)})以上の島が ${overloadedIslands.length} 件あります。`,
      islandIds: topOverloaded.map((item) => item.id),
      suggestedAction: "折りたたみ/階層化を検討。代表カードで統合。",
    });
  }

  if (islandCount > 0 && tinyIslands.length / islandCount > 0.3) {
    findings.push({
      severity: "info",
      code: "D002",
      title: "Fragmentation risk: too many tiny islands",
      detail: `tiny島(<=1 card)が ${tinyIslands.length}/${islandCount} 件です。`,
      islandIds: tinyIslands
        .sort((left, right) => left.id.localeCompare(right.id))
        .slice(0, 5)
        .map((item) => item.id),
      suggestedAction: "島の統合/関係整理",
    });
  }

  if (isolatedIslands.length > 0) {
    findings.push({
      severity: "warn",
      code: "D003",
      title: "Many isolated islands",
      detail: `島グラフで次数0の島が ${isolatedIslands.length} 件あります。`,
      islandIds: isolatedIslands.slice(0, 5).map((item) => item.id),
      suggestedAction: "孤立島どうしの関係線や中継島を検討してください。",
    });
  }

  if (islandCount >= 3 && (averageDegree < 0.5 || averageDegree > 4)) {
    findings.push({
      severity: "info",
      code: "D004",
      title: "Edge density looks extreme",
      detail: `平均次数が ${averageDegree.toFixed(2)} です。`,
      suggestedAction: averageDegree < 0.5 ? "関係線が少ないため接続候補の見直しを検討。" : "関係線が密なため主要関係へ絞り込みを検討。",
    });
  }

  findings.sort((left, right) => {
    if (left.severity !== right.severity) {
      return left.severity === "warn" ? -1 : 1;
    }
    return left.code.localeCompare(right.code);
  });

  return {
    generatedAt: nowIso,
    stats: {
      islandCount,
      cardCount,
      avgCardsPerIsland,
      medianCardsPerIsland,
      p90CardsPerIsland,
      islandsOverloadedCount: overloadedIslands.length,
      islandsTinyCount: tinyIslands.length,
      isolatedIslandsCount: isolatedIslands.length,
    },
    findings,
  };
}

export function rankDistributionIslands(doc: DocumentV1, limit = 5): DistributionRankings {
  const degreeByIslandId = buildIslandDegreeMap(doc);
  const rows: DistributionIslandRanking[] = doc.islands.map((island) => ({
    id: island.id,
    cardCount: island.cardIds.length,
    degree: degreeByIslandId.get(island.id) ?? 0,
  }));

  const loaded = [...rows]
    .sort((left, right) => (right.cardCount - left.cardCount) || (right.degree - left.degree) || left.id.localeCompare(right.id))
    .slice(0, Math.max(0, limit));
  const isolated = rows
    .filter((row) => row.degree === 0)
    .sort((left, right) => (right.cardCount - left.cardCount) || left.id.localeCompare(right.id))
    .slice(0, Math.max(0, limit));

  return {
    loaded,
    isolated,
  };
}
