import type { DocumentV2, EvidenceLink } from "../domain/types";

export type TraceAnalyticsOptions = {
  maxHops?: number;
  maxNodes?: number;
  safeMode?: boolean;
  includeCycleDetection?: boolean;
  topHubCount?: number;
};

export type TraceAnalytics = {
  startCardId: string;
  maxHops: number;
  maxNodes: number;
  visitedCardIds: string[];
  visitedRelationIds: string[];
  truncated: boolean;
  evidenceLinkCountsByType: Record<EvidenceLink["type"], number>;
  depthDistribution: Array<{ depth: number; count: number }>;
  topHubs: Array<{ cardId: string; degree: number }>;
  cycleCount: number | null;
  notes: string[];
};

export function computeTraceAnalytics(doc: DocumentV2, startCardId: string, options: TraceAnalyticsOptions = {}): TraceAnalytics {
  const safeMode = options.safeMode ?? true;
  const maxHops = Math.max(1, Math.floor(options.maxHops ?? 4));
  const maxNodes = Math.max(1, Math.floor(options.maxNodes ?? 80));
  const includeCycleDetection = options.includeCycleDetection ?? true;
  const topHubCount = Math.max(1, Math.floor(options.topHubCount ?? 5));
  const notes: string[] = [];

  const cardsById = new Map(doc.cards.map((card) => [card.id, card] as const));
  if (!cardsById.has(startCardId)) {
    return {
      startCardId,
      maxHops,
      maxNodes,
      visitedCardIds: [],
      visitedRelationIds: [],
      truncated: false,
      evidenceLinkCountsByType: { supports: 0, contradicts: 0 },
      depthDistribution: [],
      topHubs: [],
      cycleCount: null,
      notes: ["start card not found"],
    };
  }

  const links = [...(doc.evidenceLinks ?? [])].sort((left, right) => left.id.localeCompare(right.id));
  const adjacency = new Map<string, Array<{ neighborId: string; relationId: string }>>();
  for (const link of links) {
    adjacency.set(link.fromCardId, [...(adjacency.get(link.fromCardId) ?? []), { neighborId: link.toCardId, relationId: link.id }]);
    adjacency.set(link.toCardId, [...(adjacency.get(link.toCardId) ?? []), { neighborId: link.fromCardId, relationId: link.id }]);
  }

  const queue: Array<{ id: string; depth: number }> = [{ id: startCardId, depth: 0 }];
  const depthByCardId = new Map<string, number>([[startCardId, 0]]);
  const visited = new Set<string>([startCardId]);
  let truncated = false;

  while (queue.length > 0) {
    const current = queue.shift();
    if (!current) break;
    if (current.depth >= maxHops) continue;
    const neighbors = [...(adjacency.get(current.id) ?? [])]
      .sort((left, right) => left.neighborId.localeCompare(right.neighborId) || left.relationId.localeCompare(right.relationId));
    for (const neighbor of neighbors) {
      if (visited.size >= maxNodes) {
        truncated = true;
        break;
      }
      if (visited.has(neighbor.neighborId)) {
        continue;
      }
      visited.add(neighbor.neighborId);
      depthByCardId.set(neighbor.neighborId, current.depth + 1);
      queue.push({ id: neighbor.neighborId, depth: current.depth + 1 });
    }
    if (truncated) {
      break;
    }
  }

  const visitedCardIds = [...visited].sort((left, right) => left.localeCompare(right));
  const visitedSet = new Set(visitedCardIds);
  const visitedRelations = links.filter((link) => visitedSet.has(link.fromCardId) && visitedSet.has(link.toCardId));
  const visitedRelationIds = visitedRelations.map((link) => link.id).sort((left, right) => left.localeCompare(right));

  const evidenceLinkCountsByType = visitedRelations.reduce<Record<EvidenceLink["type"], number>>((acc, link) => {
    acc[link.type] += 1;
    return acc;
  }, { supports: 0, contradicts: 0 });

  const depthCounts = new Map<number, number>();
  for (const depth of depthByCardId.values()) {
    depthCounts.set(depth, (depthCounts.get(depth) ?? 0) + 1);
  }
  const depthDistribution = [...depthCounts.entries()]
    .sort((left, right) => left[0] - right[0])
    .map(([depth, count]) => ({ depth, count }));

  const degreeByCardId = new Map<string, number>();
  for (const cardId of visitedCardIds) {
    degreeByCardId.set(cardId, 0);
  }
  for (const link of visitedRelations) {
    degreeByCardId.set(link.fromCardId, (degreeByCardId.get(link.fromCardId) ?? 0) + 1);
    degreeByCardId.set(link.toCardId, (degreeByCardId.get(link.toCardId) ?? 0) + 1);
  }
  const topHubs = [...degreeByCardId.entries()]
    .map(([cardId, degree]) => ({ cardId, degree }))
    .sort((left, right) => right.degree - left.degree || left.cardId.localeCompare(right.cardId))
    .slice(0, topHubCount);

  const cycleCount = includeCycleDetection
    ? Math.max(0, visitedRelations.length - visitedCardIds.length + countConnectedComponents(visitedCardIds, visitedRelations))
    : null;

  if (truncated) {
    notes.push(`Truncated to ${maxNodes} nodes.`);
  }
  if (safeMode) {
    notes.push("Safe mode enforced: ids/counts only.");
  }

  return {
    startCardId,
    maxHops,
    maxNodes,
    visitedCardIds,
    visitedRelationIds,
    truncated,
    evidenceLinkCountsByType,
    depthDistribution,
    topHubs,
    cycleCount,
    notes,
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
    if (visited.has(cardId)) {
      continue;
    }
    components += 1;
    const stack = [cardId];
    visited.add(cardId);
    while (stack.length > 0) {
      const current = stack.pop();
      if (!current) {
        continue;
      }
      const neighbors = [...(adjacency.get(current) ?? [])].sort((left, right) => left.localeCompare(right));
      for (const neighbor of neighbors) {
        if (visited.has(neighbor)) {
          continue;
        }
        visited.add(neighbor);
        stack.push(neighbor);
      }
    }
  }
  return components;
}

export function buildTraceAnalyticsMd(analytics: TraceAnalytics): string {
  const lines: string[] = [
    "# Trace Analytics",
    "",
    `- startCardId: ${analytics.startCardId}`,
    `- maxHops: ${analytics.maxHops}`,
    `- maxNodes: ${analytics.maxNodes}`,
    `- visitedCards: ${analytics.visitedCardIds.length}`,
    `- visitedRelations: ${analytics.visitedRelationIds.length}`,
    "",
    "## Evidence links by type",
    `- supports: ${analytics.evidenceLinkCountsByType.supports}`,
    `- contradicts: ${analytics.evidenceLinkCountsByType.contradicts}`,
    "",
    "## Depth distribution",
    ...(analytics.depthDistribution.length === 0
      ? ["- (none)"]
      : analytics.depthDistribution.map((entry) => `- depth:${entry.depth} count:${entry.count}`)),
    "",
    "## Top hubs",
    ...(analytics.topHubs.length === 0
      ? ["- (none)"]
      : analytics.topHubs.map((hub) => `- card:${hub.cardId} degree:${hub.degree}`)),
    "",
    "## Cycle detection",
    `- cycleCount: ${analytics.cycleCount === null ? "skipped" : analytics.cycleCount}`,
    "",
    "## Notes",
    ...(analytics.notes.length === 0 ? ["- none"] : analytics.notes.map((note) => `- ${note}`)),
  ];

  return `${lines.join("\n")}\n`;
}
