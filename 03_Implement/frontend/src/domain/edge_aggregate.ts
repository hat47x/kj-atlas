import { isSourceCard, type DocumentV1, type EdgeEndpointKind, type EdgeType } from "./types";

export type RenderEdge = {
  id: string;
  fromId: string;
  toId: string;
  type: EdgeType;
  fromKind: EdgeEndpointKind;
  toKind: EdgeEndpointKind;
  isDerived?: boolean;
  aggregateCount?: number;
};

type Endpoint = {
  kind: EdgeEndpointKind;
  id: string;
};

function getEndpoint(rawKind: unknown, id: string): Endpoint {
  return {
    kind: rawKind === "island" ? "island" : "card",
    id,
  };
}

function endpointKey(endpoint: Endpoint): string {
  return `${endpoint.kind}:${endpoint.id}`;
}

function edgeKey(from: Endpoint, to: Endpoint, type: EdgeType): string {
  return `${endpointKey(from)}|${endpointKey(to)}|${type}`;
}

export function getEdgesToRender(document: DocumentV1, hideSourceCards: boolean): RenderEdge[] {
  const cardById = new Map(document.cards.map((card) => [card.id, card]));
  const hiddenSourceCardIdSet = new Set<string>();

  if (hideSourceCards) {
    for (const card of document.cards) {
      if (isSourceCard(card)) {
        hiddenSourceCardIdSet.add(card.id);
      }
    }
  }

  const visibleEdges: RenderEdge[] = [];
  const aggregateMap = new Map<
    string,
    {
      from: Endpoint;
      to: Endpoint;
      type: EdgeType;
      count: number;
    }
  >();

  for (const rawEdge of document.edges) {
    const from = getEndpoint(rawEdge.fromKind, rawEdge.fromId);
    const to = getEndpoint(rawEdge.toKind, rawEdge.toId);

    const fromIsHiddenSource = from.kind === "card" && hiddenSourceCardIdSet.has(from.id);
    const toIsHiddenSource = to.kind === "card" && hiddenSourceCardIdSet.has(to.id);

    if (!hideSourceCards || (!fromIsHiddenSource && !toIsHiddenSource)) {
      visibleEdges.push({
        id: rawEdge.id,
        fromId: from.id,
        toId: to.id,
        fromKind: from.kind,
        toKind: to.kind,
        type: rawEdge.type,
      });
      continue;
    }

    const mappedFrom = fromIsHiddenSource
      ? getEndpoint("card", cardById.get(from.id)?.canonicalId ?? from.id)
      : from;
    const mappedTo = toIsHiddenSource
      ? getEndpoint("card", cardById.get(to.id)?.canonicalId ?? to.id)
      : to;

    if (mappedFrom.kind === mappedTo.kind && mappedFrom.id === mappedTo.id) {
      continue;
    }

    const key = edgeKey(mappedFrom, mappedTo, rawEdge.type);
    const existing = aggregateMap.get(key);

    if (existing) {
      existing.count += 1;
      continue;
    }

    aggregateMap.set(key, {
      from: mappedFrom,
      to: mappedTo,
      type: rawEdge.type,
      count: 1,
    });
  }

  const aggregateEdges: RenderEdge[] = Array.from(aggregateMap.entries()).map(([key, value]) => {
    return {
      id: `agg:${key}`,
      fromId: value.from.id,
      toId: value.to.id,
      fromKind: value.from.kind,
      toKind: value.to.kind,
      type: value.type,
      isDerived: true,
      aggregateCount: value.count,
    };
  });

  return [...visibleEdges, ...aggregateEdges];
}
