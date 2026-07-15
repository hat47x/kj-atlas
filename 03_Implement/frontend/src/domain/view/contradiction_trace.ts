import type { Card, DocumentV1 } from "../types";
import { SafeModePolicy } from "../policy/safe_mode";

type ClaimType = "fact" | "claim" | "hypothesis" | "unknown";

export type ContradictionTraceOptions = {
  depthLimit?: number;
  includeSupports?: boolean;
  maxNodes?: number;
  safeMode?: boolean;
};

const CLAIM_TYPE_PRIORITY: Record<ClaimType, number> = {
  fact: 0,
  claim: 1,
  hypothesis: 2,
  unknown: 3,
};

function resolveClaimType(card: Card | undefined): ClaimType {
  if (!card) {
    return "unknown";
  }

  return card.claimType ?? "unknown";
}

function clampDepthLimit(depthLimit: number | undefined): number {
  if (depthLimit === undefined) {
    return 1;
  }

  const normalized = Math.floor(depthLimit);
  return Math.max(1, Math.min(3, normalized));
}

function clampMaxNodes(maxNodes: number | undefined): number {
  if (maxNodes === undefined) {
    return 60;
  }

  const normalized = Math.floor(maxNodes);
  return Math.max(1, normalized);
}

function buildSnippet(text: string | undefined): string {
  const trimmed = (text ?? "").trim();
  if (trimmed.length === 0) {
    return "(empty)";
  }

  const oneLine = trimmed.split(/\r?\n/, 1)[0] ?? "";
  if (oneLine.length <= 120) {
    return oneLine;
  }

  return `${oneLine.slice(0, 120)}…`;
}

function sortCardIds(ids: Iterable<string>, cardsById: Map<string, Card>): string[] {
  return [...new Set(ids)].sort((leftId, rightId) => {
    const leftType = resolveClaimType(cardsById.get(leftId));
    const rightType = resolveClaimType(cardsById.get(rightId));

    if (CLAIM_TYPE_PRIORITY[leftType] !== CLAIM_TYPE_PRIORITY[rightType]) {
      return CLAIM_TYPE_PRIORITY[leftType] - CLAIM_TYPE_PRIORITY[rightType];
    }

    return leftId.localeCompare(rightId);
  });
}

function buildCardLine(card: Card, safeMode: boolean): string {
  const body = safeMode ? `card:${card.id}` : buildSnippet(card.text);
  return `- [${resolveClaimType(card)}] ${body} (id: ${card.id})`;
}

function buildContradictorMarkers(card: Card, hasFactSupport: boolean): string[] {
  const markers: string[] = [];
  const claimType = resolveClaimType(card);

  if (claimType === "hypothesis") {
    markers.push("⚠ hypothesis-as-contradiction");
  }

  if (claimType === "unknown") {
    markers.push("⚠ unknown-type");
  }

  if (!hasFactSupport) {
    markers.push("⚠ unsupported-contradiction");
  }

  return markers;
}

export function buildContradictionTraceMd(doc: DocumentV1, targetCardId: string, options: ContradictionTraceOptions = {}): string {
  const depthLimit = clampDepthLimit(options.depthLimit);
  const includeSupports = options.includeSupports ?? true;
  const maxNodes = clampMaxNodes(options.maxNodes);
  const safeMode = options.safeMode ?? false;

  const cardsById = new Map(doc.cards.map((card) => [card.id, card] as const));
  const targetCard = cardsById.get(targetCardId);
  if (!targetCard) {
    return `Error: target card not found (id: ${targetCardId})`;
  }

  const incomingContradictions = new Map<string, string[]>();
  const outgoingContradictions = new Map<string, string[]>();
  const neighbors = new Map<string, string[]>();
  const incomingFactSupports = new Map<string, string[]>();

  for (const link of doc.evidenceLinks ?? []) {
    if (link.type === "contradicts") {
      outgoingContradictions.set(link.fromCardId, [...(outgoingContradictions.get(link.fromCardId) ?? []), link.toCardId]);
      incomingContradictions.set(link.toCardId, [...(incomingContradictions.get(link.toCardId) ?? []), link.fromCardId]);

      // for depth exploration: treat contradiction graph as undirected
      neighbors.set(link.fromCardId, [...(neighbors.get(link.fromCardId) ?? []), link.toCardId]);
      neighbors.set(link.toCardId, [...(neighbors.get(link.toCardId) ?? []), link.fromCardId]);
      continue;
    }

    if (link.type === "supports") {
      const supportCard = cardsById.get(link.fromCardId);
      if (resolveClaimType(supportCard) !== "fact") {
        continue;
      }

      incomingFactSupports.set(link.toCardId, [...(incomingFactSupports.get(link.toCardId) ?? []), link.fromCardId]);
    }
  }

  const factSupportIdsFor = (cardId: string): string[] => {
    return sortCardIds(incomingFactSupports.get(cardId) ?? [], cardsById).filter((id) => cardsById.has(id));
  };

  const targetSupportIds = factSupportIdsFor(targetCardId);
  const incomingIds = sortCardIds(incomingContradictions.get(targetCardId) ?? [], cardsById).filter((id) => cardsById.has(id));
  const outgoingIds = sortCardIds(outgoingContradictions.get(targetCardId) ?? [], cardsById).filter((id) => cardsById.has(id));

  const lines: string[] = [
    "# Contradiction Trace",
    "",
    "## Target",
    buildCardLine(targetCard, safeMode),
  ];

  if (includeSupports) {
    if (targetSupportIds.length === 0) {
      lines.push("- ⚠ No fact support");
    } else {
      lines.push("- Fact supports:");
      for (const supportId of targetSupportIds) {
        const support = cardsById.get(supportId);
        if (!support) {
          continue;
        }

        lines.push(`  - ${safeMode ? `card:${support.id}` : buildSnippet(support.text)} (id: ${support.id})`);
      }
    }
  }

  lines.push("", "## Incoming contradictions");

  const appendContradiction = (cardId: string): void => {
    const card = cardsById.get(cardId);
    if (!card) {
      return;
    }

    const supportIds = factSupportIdsFor(cardId);
    const markers = buildContradictorMarkers(card, supportIds.length > 0);
    const markerSuffix = markers.length > 0 ? ` ${markers.join(" ")}` : "";
    lines.push(`${buildCardLine(card, safeMode)}${markerSuffix}`);

    if (!includeSupports) {
      return;
    }

    lines.push("  - This side fact supports:");
    if (supportIds.length === 0) {
      lines.push("    - ⚠ No fact support");
    } else {
      for (const supportId of supportIds) {
        const support = cardsById.get(supportId);
        if (!support) {
          continue;
        }

        lines.push(`    - ${safeMode ? `card:${support.id}` : buildSnippet(support.text)} (id: ${support.id})`);
      }
    }

    lines.push("  - Target side fact supports:");
    if (targetSupportIds.length === 0) {
      lines.push("    - ⚠ No fact support");
    } else {
      for (const supportId of targetSupportIds) {
        const support = cardsById.get(supportId);
        if (!support) {
          continue;
        }

        lines.push(`    - ${safeMode ? `card:${support.id}` : buildSnippet(support.text)} (id: ${support.id})`);
      }
    }
  };

  if (incomingIds.length === 0) {
    lines.push("- No contradiction links found.");
  } else {
    for (const cardId of incomingIds) {
      appendContradiction(cardId);
    }
  }

  lines.push("", "## Outgoing contradictions");

  if (outgoingIds.length === 0) {
    lines.push("- No contradiction links found.");
  } else {
    for (const cardId of outgoingIds) {
      appendContradiction(cardId);
    }
  }

  if (depthLimit > 1) {
    lines.push("", `## Contradiction network (depth ${depthLimit})`);
    lines.push(buildCardLine(targetCard, safeMode));

    const queue: Array<{ id: string; depth: number }> = [{ id: targetCardId, depth: 0 }];
    const depthById = new Map<string, number>([[targetCardId, 0]]);
    const parentById = new Map<string, string | null>([[targetCardId, null]]);
    const order: string[] = [targetCardId];
    let expandedCount = 0;
    let truncated = false;

    while (queue.length > 0) {
      const current = queue.shift();
      if (!current) {
        break;
      }

      if (current.depth >= depthLimit) {
        continue;
      }

      const nextIds = sortCardIds(neighbors.get(current.id) ?? [], cardsById).filter((id) => cardsById.has(id));
      for (const nextId of nextIds) {
        if (expandedCount >= maxNodes) {
          truncated = true;
          queue.length = 0;
          break;
        }

        if (depthById.has(nextId)) {
          continue;
        }

        depthById.set(nextId, current.depth + 1);
        parentById.set(nextId, current.id);
        order.push(nextId);
        queue.push({ id: nextId, depth: current.depth + 1 });
        expandedCount += 1;
      }
    }

    const childrenByParent = new Map<string, string[]>();
    for (const cardId of order) {
      const parentId = parentById.get(cardId);
      if (!parentId) {
        continue;
      }

      childrenByParent.set(parentId, [...(childrenByParent.get(parentId) ?? []), cardId]);
    }

    for (const [parentId, childIds] of childrenByParent.entries()) {
      childrenByParent.set(parentId, sortCardIds(childIds, cardsById));
    }

    const printTree = (cardId: string, indent: number): void => {
      const childIds = childrenByParent.get(cardId) ?? [];
      for (const childId of childIds) {
        const child = cardsById.get(childId);
        if (!child) {
          continue;
        }

        lines.push(`${"  ".repeat(indent)}- [${resolveClaimType(child)}] ${safeMode ? `card:${child.id}` : buildSnippet(child.text)} (id: ${child.id})`);

        const childNeighbors = sortCardIds(neighbors.get(childId) ?? [], cardsById).filter((id) => cardsById.has(id));
        const treeNeighbors = new Set<string>([...(childrenByParent.get(childId) ?? []), parentById.get(childId) ?? ""]);
        const hasCycleEdge = childNeighbors.some((neighborId) => depthById.has(neighborId) && !treeNeighbors.has(neighborId));
        if (hasCycleEdge) {
          lines.push(`${"  ".repeat(indent + 1)}- ↺ cycle`);
        }

        printTree(childId, indent + 1);
      }
    };

    printTree(targetCardId, 1);

    if (truncated) {
      lines.push("- ... truncated");
    }
  }

  if (safeMode && !SafeModePolicy.canExposeText("trace.text", "share", true)) {
    lines.push("- Safe mode enforced: text content redacted.");
  }

  lines.push(
    "",
    "## Notes",
    "- This trace reflects explicit contradicts links only.",
    "- No inference beyond declared structure.",
  );

  return lines.join("\n");
}
