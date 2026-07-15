import type { DocumentV1, EvidenceLink } from "../types";

export type EvidenceOverlayMode = "supports" | "contradicts" | "both";

export type EvidenceAdjacency = {
  outSupports: Map<string, EvidenceLink[]>;
  outContradicts: Map<string, EvidenceLink[]>;
  inSupports: Map<string, EvidenceLink[]>;
  inContradicts: Map<string, EvidenceLink[]>;
};

export type EvidenceNeighborhood = {
  nodes: Set<string>;
  edges: Set<string>;
};

function sortLinks(links: EvidenceLink[]): EvidenceLink[] {
  return [...links].sort((left, right) => left.id.localeCompare(right.id));
}

function buildMap(entries: Array<[string, EvidenceLink[]]>): Map<string, EvidenceLink[]> {
  const map = new Map<string, EvidenceLink[]>();
  for (const [key, links] of entries.sort((left, right) => left[0].localeCompare(right[0]))) {
    map.set(key, sortLinks(links));
  }
  return map;
}

export function buildEvidenceAdjacency(doc: Pick<DocumentV1, "evidenceLinks">): EvidenceAdjacency {
  const outSupportsEntries = new Map<string, EvidenceLink[]>();
  const outContradictsEntries = new Map<string, EvidenceLink[]>();
  const inSupportsEntries = new Map<string, EvidenceLink[]>();
  const inContradictsEntries = new Map<string, EvidenceLink[]>();

  const links = [...(doc.evidenceLinks ?? [])].sort((left, right) => left.id.localeCompare(right.id));

  for (const link of links) {
    const outMap = link.type === "supports" ? outSupportsEntries : outContradictsEntries;
    const inMap = link.type === "supports" ? inSupportsEntries : inContradictsEntries;

    outMap.set(link.fromCardId, [...(outMap.get(link.fromCardId) ?? []), link]);
    inMap.set(link.toCardId, [...(inMap.get(link.toCardId) ?? []), link]);
  }

  return {
    outSupports: buildMap(Array.from(outSupportsEntries.entries())),
    outContradicts: buildMap(Array.from(outContradictsEntries.entries())),
    inSupports: buildMap(Array.from(inSupportsEntries.entries())),
    inContradicts: buildMap(Array.from(inContradictsEntries.entries())),
  };
}

function getRelevantLinks(adjacency: EvidenceAdjacency, cardId: string, mode: EvidenceOverlayMode): EvidenceLink[] {
  const links: EvidenceLink[] = [];
  const addForType = (type: "supports" | "contradicts") => {
    const outMap = type === "supports" ? adjacency.outSupports : adjacency.outContradicts;
    const inMap = type === "supports" ? adjacency.inSupports : adjacency.inContradicts;
    links.push(...(outMap.get(cardId) ?? []), ...(inMap.get(cardId) ?? []));
  };

  if (mode === "both" || mode === "supports") {
    addForType("supports");
  }

  if (mode === "both" || mode === "contradicts") {
    addForType("contradicts");
  }

  return links.sort((left, right) => left.id.localeCompare(right.id));
}

export function getEvidenceNeighborhood(
  selectedCardId: string,
  adjacency: EvidenceAdjacency,
  mode: EvidenceOverlayMode,
  depth: number,
): EvidenceNeighborhood {
  const clampedDepth = Math.max(1, Math.min(3, Math.floor(depth)));
  const nodes = new Set<string>([selectedCardId]);
  const edges = new Set<string>();
  const visited = new Set<string>([selectedCardId]);
  let frontier: string[] = [selectedCardId];

  for (let step = 0; step < clampedDepth; step += 1) {
    const nextFrontier = new Set<string>();
    const sortedFrontier = [...frontier].sort((left, right) => left.localeCompare(right));

    for (const cardId of sortedFrontier) {
      const links = getRelevantLinks(adjacency, cardId, mode);
      for (const link of links) {
        edges.add(link.id);
        nodes.add(link.fromCardId);
        nodes.add(link.toCardId);

        if (!visited.has(link.fromCardId)) {
          nextFrontier.add(link.fromCardId);
        }

        if (!visited.has(link.toCardId)) {
          nextFrontier.add(link.toCardId);
        }
      }
    }

    frontier = [...nextFrontier].sort((left, right) => left.localeCompare(right));
    for (const cardId of frontier) {
      visited.add(cardId);
    }

    if (frontier.length === 0) {
      break;
    }
  }

  return { nodes, edges };
}
