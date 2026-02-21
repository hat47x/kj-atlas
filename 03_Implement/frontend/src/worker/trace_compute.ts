import type { TraceRequestPayload } from "./trace_protocol";

export function computeTrace(payload: TraceRequestPayload): { traceMd: string; traceData: { visitedCardIds: string[]; visitedRelationIds?: string[]; truncated: boolean; notes: string[] } } {
  const { doc } = payload;
  const safeMode = payload.options.safeMode ?? true;
  const startCardId = payload.options.startCardId;
  const maxHops = Math.max(1, Math.floor(payload.options.maxHops ?? 4));
  const maxNodes = Math.max(1, Math.floor(payload.options.maxNodes ?? 80));
  const notes: string[] = [];

  const cardsById = new Map(doc.cards.map((card) => [card.id, card] as const));
  if (!cardsById.has(startCardId)) {
    return {
      traceMd: `Error: start card not found (${startCardId})`,
      traceData: { visitedCardIds: [], truncated: false, notes: ["start card not found"] },
    };
  }

  const links = (doc.evidenceLinks ?? []).filter((link) => payload.options.kind === "evidence" ? link.type === "supports" : link.type === "contradicts");
  const neighborMap = new Map<string, string[]>();
  for (const link of links) {
    neighborMap.set(link.fromCardId, [...(neighborMap.get(link.fromCardId) ?? []), link.toCardId]);
    neighborMap.set(link.toCardId, [...(neighborMap.get(link.toCardId) ?? []), link.fromCardId]);
  }

  const queue: Array<{ id: string; depth: number }> = [{ id: startCardId, depth: 0 }];
  const visited = new Set<string>([startCardId]);
  let truncated = false;
  while (queue.length > 0) {
    const item = queue.shift();
    if (!item) break;
    if (item.depth >= maxHops) continue;
    const neighbors = [...(neighborMap.get(item.id) ?? [])].sort((a, b) => a.localeCompare(b));
    for (const neighbor of neighbors) {
      if (visited.size >= maxNodes) {
        truncated = true;
        break;
      }
      if (visited.has(neighbor)) continue;
      visited.add(neighbor);
      queue.push({ id: neighbor, depth: item.depth + 1 });
    }
    if (truncated) break;
  }

  const visitedCardIds = [...visited].sort();
  const visitedRelationIds = links
    .filter((link) => visited.has(link.fromCardId) && visited.has(link.toCardId))
    .map((link) => link.id)
    .sort();

  if (truncated) notes.push(`Truncated to ${maxNodes} nodes.`);
  if (safeMode) notes.push("Safe mode enforced: no raw card text included.");

  const lines = [
    payload.options.kind === "evidence" ? "# Evidence Trace" : "# Contradiction Trace",
    "",
    `- startCardId: ${startCardId}`,
    `- maxHops: ${maxHops}`,
    `- maxNodes: ${maxNodes}`,
    "",
    "## Visited cards",
    ...visitedCardIds.map((id) => `- card:${id}`),
    "",
    "## Visited relations",
    ...(visitedRelationIds.length === 0 ? ["- (none)"] : visitedRelationIds.map((id) => `- relation:${id}`)),
    "",
    "## Notes",
    ...(notes.length === 0 ? ["- none"] : notes.map((note) => `- ${note}`)),
  ];

  return {
    traceMd: `${lines.join("\n")}\n`,
    traceData: { visitedCardIds, visitedRelationIds, truncated, notes },
  };
}
