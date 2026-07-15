import type { DocumentV1, EvidenceLink } from "../domain/types";

export type TraceAnalyticsOptions = {
  kind?: "evidence" | "contradiction" | "both";
  maxHops?: number;
  maxNodes?: number;
  safeMode?: boolean;
  includeCycleDetection?: boolean;
  topHubCount?: number;
};

export type TraceAnalytics = {
  startCardId: string;
  kind: "evidence" | "contradiction" | "both";
  maxHops: number;
  maxNodes: number;
  visitedCardIds: string[];
  visitedLinkIds: string[];
  byRelationType: Record<string, number>;
  depthHistogram: Record<number, number>;
  topHubs: Array<{ cardId: string; degree: number }>;
  cycles?: { count: number; notes?: string[] };
  truncated: boolean;
  notes: string[];
  // backward-compat fields used by existing UI/tests
  visitedRelationIds: string[];
  evidenceLinkCountsByType: Record<EvidenceLink["type"], number>;
  depthDistribution: Array<{ depth: number; count: number }>;
  cycleCount: number | null;
  evidenceLinkCount: number;
  isolatedNodeCount: number;
  isolatedNodeIds: string[];
  sourceDensity: number;
};

function roundTo4(value: number): number {
  return Math.round(value * 10_000) / 10_000;
}

export function computeTraceAnalytics(doc: DocumentV1, startCardId: string, options: TraceAnalyticsOptions = {}): TraceAnalytics {
  const safeMode = options.safeMode ?? true;
  const kind = options.kind ?? "both";
  const maxHops = Math.max(1, Math.floor(options.maxHops ?? 4));
  const maxNodes = Math.max(1, Math.floor(options.maxNodes ?? 80));
  const includeCycleDetection = options.includeCycleDetection ?? true;
  const topHubCount = Math.max(1, Math.floor(options.topHubCount ?? 5));
  const notes: string[] = [];

  const cardsById = new Map(doc.cards.map((card) => [card.id, card] as const));
  if (!cardsById.has(startCardId)) {
    return {
      startCardId,
      kind,
      maxHops,
      maxNodes,
      visitedCardIds: [],
      visitedLinkIds: [],
      byRelationType: {},
      depthHistogram: {},
      topHubs: [],
      cycles: includeCycleDetection ? { count: 0, notes: ["start card not found"] } : undefined,
      truncated: false,
      notes: ["start card not found"],
      visitedRelationIds: [],
      evidenceLinkCountsByType: { supports: 0, contradicts: 0 },
      depthDistribution: [],
      cycleCount: includeCycleDetection ? 0 : null,
      evidenceLinkCount: 0,
      isolatedNodeCount: 0,
      isolatedNodeIds: [],
      sourceDensity: 0,
    };
  }

  const links = [...(doc.evidenceLinks ?? [])]
    .filter((link) => (kind === "both" ? true : kind === "evidence" ? link.type === "supports" : link.type === "contradicts"))
    .sort((left, right) => left.id.localeCompare(right.id));

  const evidenceLinkCount = links.length;
  const connectedCardIds = new Set<string>();
  for (const link of links) {
    connectedCardIds.add(link.fromCardId);
    connectedCardIds.add(link.toCardId);
  }
  const isolatedNodeIds = [...cardsById.keys()].filter((cardId) => !connectedCardIds.has(cardId)).sort((left, right) => left.localeCompare(right));
  const isolatedNodeCount = isolatedNodeIds.length;
  const sourceDensity = roundTo4(evidenceLinkCount / Math.max(1, cardsById.size));

  const adjacency = new Map<string, Array<{ neighborId: string; linkId: string }>>();
  for (const link of links) {
    adjacency.set(link.fromCardId, [...(adjacency.get(link.fromCardId) ?? []), { neighborId: link.toCardId, linkId: link.id }]);
    adjacency.set(link.toCardId, [...(adjacency.get(link.toCardId) ?? []), { neighborId: link.fromCardId, linkId: link.id }]);
  }

  const queue: Array<{ cardId: string; depth: number }> = [{ cardId: startCardId, depth: 0 }];
  const depthByCardId = new Map<string, number>([[startCardId, 0]]);
  const visitedCardIdSet = new Set<string>([startCardId]);
  let truncated = false;

  while (queue.length > 0) {
    const current = queue.shift();
    if (!current) break;
    if (current.depth >= maxHops) continue;

    const neighbors = [...(adjacency.get(current.cardId) ?? [])]
      .sort((left, right) => left.neighborId.localeCompare(right.neighborId) || left.linkId.localeCompare(right.linkId));

    for (const neighbor of neighbors) {
      if (visitedCardIdSet.size >= maxNodes) {
        truncated = true;
        break;
      }
      if (visitedCardIdSet.has(neighbor.neighborId)) {
        continue;
      }
      visitedCardIdSet.add(neighbor.neighborId);
      depthByCardId.set(neighbor.neighborId, current.depth + 1);
      queue.push({ cardId: neighbor.neighborId, depth: current.depth + 1 });
    }

    if (truncated) {
      break;
    }
  }

  const visitedCardIds = [...visitedCardIdSet].sort((left, right) => left.localeCompare(right));
  const visitedSet = new Set(visitedCardIds);
  const visitedLinks = links.filter((link) => visitedSet.has(link.fromCardId) && visitedSet.has(link.toCardId));
  const visitedLinkIds = visitedLinks.map((link) => link.id).sort((left, right) => left.localeCompare(right));

  const byRelationType = visitedLinks.reduce<Record<string, number>>((acc, link) => {
    acc[link.type] = (acc[link.type] ?? 0) + 1;
    return acc;
  }, {});

  const depthHistogram = [...depthByCardId.entries()].reduce<Record<number, number>>((acc, [, depth]) => {
    acc[depth] = (acc[depth] ?? 0) + 1;
    return acc;
  }, {});

  const degreeByCardId = new Map<string, number>(visitedCardIds.map((cardId) => [cardId, 0]));
  for (const link of visitedLinks) {
    degreeByCardId.set(link.fromCardId, (degreeByCardId.get(link.fromCardId) ?? 0) + 1);
    degreeByCardId.set(link.toCardId, (degreeByCardId.get(link.toCardId) ?? 0) + 1);
  }

  const topHubs = [...degreeByCardId.entries()]
    .map(([cardId, degree]) => ({ cardId, degree }))
    .sort((left, right) => right.degree - left.degree || left.cardId.localeCompare(right.cardId))
    .slice(0, topHubCount);

  const cycleCount = includeCycleDetection
    ? Math.max(0, visitedLinks.length - visitedCardIds.length + countConnectedComponents(visitedCardIds, visitedLinks))
    : null;

  if (truncated) {
    notes.push(`Truncated to ${maxNodes} nodes.`);
  }
  if (safeMode) {
    notes.push("Safe mode enforced: ids/counts only.");
  }

  return {
    startCardId,
    kind,
    maxHops,
    maxNodes,
    visitedCardIds,
    visitedLinkIds,
    byRelationType,
    depthHistogram,
    topHubs,
    cycles: includeCycleDetection ? { count: cycleCount ?? 0 } : undefined,
    truncated,
    notes,
    visitedRelationIds: visitedLinkIds,
    evidenceLinkCountsByType: {
      supports: byRelationType.supports ?? 0,
      contradicts: byRelationType.contradicts ?? 0,
    },
    depthDistribution: Object.entries(depthHistogram)
      .map(([depth, count]) => ({ depth: Number(depth), count }))
      .sort((left, right) => left.depth - right.depth),
    cycleCount,
    evidenceLinkCount,
    isolatedNodeCount,
    isolatedNodeIds,
    sourceDensity,
  };
}

function countConnectedComponents(visitedCardIds: string[], relations: EvidenceLink[]): number {
  const adjacency = new Map<string, string[]>();
  for (const cardId of visitedCardIds) {
    adjacency.set(cardId, []);
  }
  for (const relation of relations) {
    adjacency.set(relation.fromCardId, [...(adjacency.get(relation.fromCardId) ?? []), relation.toCardId]);
    adjacency.set(relation.toCardId, [...(adjacency.get(relation.toCardId) ?? []), relation.fromCardId]);
  }

  let components = 0;
  const visited = new Set<string>();
  for (const cardId of [...visitedCardIds].sort((left, right) => left.localeCompare(right))) {
    if (visited.has(cardId)) continue;
    components += 1;
    const stack = [cardId];
    visited.add(cardId);
    while (stack.length > 0) {
      const current = stack.pop();
      if (!current) continue;
      const neighbors = [...(adjacency.get(current) ?? [])].sort((left, right) => left.localeCompare(right));
      for (const neighbor of neighbors) {
        if (visited.has(neighbor)) continue;
        visited.add(neighbor);
        stack.push(neighbor);
      }
    }
  }
  return components;
}

export function buildTraceAnalyticsMd(analytics: TraceAnalytics): string {
  const depthEntries = Object.entries(analytics.depthHistogram)
    .map(([depth, count]) => ({ depth: Number(depth), count }))
    .sort((left, right) => left.depth - right.depth);
  const relationEntries = Object.entries(analytics.byRelationType).sort((left, right) => left[0].localeCompare(right[0]));

  const lines: string[] = [
    "# Trace Analytics",
    "",
    `- startCardId: ${analytics.startCardId}`,
    `- kind: ${analytics.kind}`,
    `- maxHops: ${analytics.maxHops}`,
    `- maxNodes: ${analytics.maxNodes}`,
    `- visitedCards: ${analytics.visitedCardIds.length}`,
    `- visitedLinks: ${analytics.visitedLinkIds.length}`,
    `- evidenceLinkCount: ${analytics.evidenceLinkCount}`,
    `- isolatedNodeCount: ${analytics.isolatedNodeCount}`,
    `- sourceDensity: ${analytics.sourceDensity}`,
    "",
    "## Evidence links by type",
    ...(relationEntries.length === 0 ? ["- (none)"] : relationEntries.map(([type, count]) => `- ${type}: ${count}`)),
    "",
    "## Depth distribution",
    ...(depthEntries.length === 0 ? ["- (none)"] : depthEntries.map((entry) => `- depth:${entry.depth} count:${entry.count}`)),
    "",
    "## Top hubs",
    ...(analytics.topHubs.length === 0 ? ["- (none)"] : analytics.topHubs.map((hub) => `- card:${hub.cardId} degree:${hub.degree}`)),
    "",
    "## Cycle detection",
    `- cycleCount: ${analytics.cycles ? analytics.cycles.count : "skipped"}`,
    "",
    "## Notes",
    ...(analytics.notes.length === 0 ? ["- none"] : analytics.notes.map((note) => `- ${note}`)),
  ];

  if (analytics.isolatedNodeIds.length > 0) {
    lines.push("", "## Isolated nodes", ...analytics.isolatedNodeIds.map((cardId) => `- card:${cardId}`));
  }

  return `${lines.join("\n")}\n`;
}
