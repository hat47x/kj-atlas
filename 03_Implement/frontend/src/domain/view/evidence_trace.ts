import type { Card, DocumentV1 } from "../types";
import { SafeModePolicy } from "../policy/safe_mode";

type ClaimType = "fact" | "claim" | "hypothesis" | "unknown";

export type EvidenceTraceOptions = {
  safeMode?: boolean;
  depthLimit?: number;
  includeContradictions?: boolean;
  includeUnknown?: boolean;
  includeFact?: boolean;
  includeClaim?: boolean;
  includeHypothesis?: boolean;
  stopAtFacts?: boolean;
  maxNodes?: number;
};

const CLAIM_TYPE_PRIORITY: Record<ClaimType, number> = {
  fact: 0,
  claim: 1,
  hypothesis: 2,
  unknown: 3,
};

function clampDepthLimit(depthLimit: number | undefined): number {
  if (depthLimit === undefined) {
    return 3;
  }

  const normalized = Math.floor(depthLimit);
  return Math.max(1, Math.min(5, normalized));
}

function clampMaxNodes(maxNodes: number | undefined): number {
  if (maxNodes === undefined) {
    return 80;
  }

  const normalized = Math.floor(maxNodes);
  return Math.max(1, normalized);
}

function resolveClaimType(card: Card | undefined): ClaimType {
  if (!card) {
    return "unknown";
  }

  return card.claimType ?? "unknown";
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

function buildLine(card: Card, options: { seeAbove?: boolean; cycle?: boolean; safeMode: boolean }): string {
  const claimType = resolveClaimType(card);
  const markers: string[] = [];

  if (claimType === "fact") {
    markers.push("✓ fact-evidence");
  }

  if (claimType === "hypothesis") {
    markers.push("⚠ hypothesis-as-evidence");
  }

  if (claimType === "unknown") {
    markers.push("⚠ unknown-type");
  }

  if (options.seeAbove) {
    markers.push("(see above)");
  }

  if (options.cycle) {
    markers.push("↺ cycle");
  }

  const markerSuffix = markers.length > 0 ? ` ${markers.join(" ")}` : "";
  const body = options.safeMode
    ? `card:${card.id}`
    : buildSnippet(card.text);
  return `- [${claimType}] ${body} (id: ${card.id})${markerSuffix}`;
}

function shouldIncludeType(claimType: ClaimType, options: EvidenceTraceOptions): boolean {
  if (claimType === "fact") {
    return options.includeFact ?? true;
  }

  if (claimType === "claim") {
    return options.includeClaim ?? true;
  }

  if (claimType === "hypothesis") {
    return options.includeHypothesis ?? true;
  }

  return options.includeUnknown ?? true;
}

export function buildEvidenceTraceMd(doc: DocumentV1, targetCardId: string, options: EvidenceTraceOptions = {}): string {
  const depthLimit = clampDepthLimit(options.depthLimit);
  const stopAtFacts = options.stopAtFacts ?? false;
  const maxNodes = clampMaxNodes(options.maxNodes);
  const safeMode = options.safeMode ?? false;

  const cardsById = new Map(doc.cards.map((card) => [card.id, card] as const));
  const targetCard = cardsById.get(targetCardId);

  if (!targetCard) {
    return `Error: target card not found (id: ${targetCardId})`;
  }

  const incomingSupports = new Map<string, string[]>();
  for (const link of doc.evidenceLinks ?? []) {
    if (link.type !== "supports") {
      continue;
    }

    incomingSupports.set(link.toCardId, [...(incomingSupports.get(link.toCardId) ?? []), link.fromCardId]);
  }

  const sortedChildren = (cardId: string): string[] => {
    const raw = incomingSupports.get(cardId) ?? [];
    const unique = [...new Set(raw)];

    return unique
      .filter((childId) => {
        const childCard = cardsById.get(childId);
        if (!childCard) {
          return false;
        }

        return shouldIncludeType(resolveClaimType(childCard), options);
      })
      .sort((leftId, rightId) => {
        const leftType = resolveClaimType(cardsById.get(leftId));
        const rightType = resolveClaimType(cardsById.get(rightId));

        if (CLAIM_TYPE_PRIORITY[leftType] !== CLAIM_TYPE_PRIORITY[rightType]) {
          return CLAIM_TYPE_PRIORITY[leftType] - CLAIM_TYPE_PRIORITY[rightType];
        }

        return leftId.localeCompare(rightId);
      });
  };

  const lines: string[] = [
    "# Evidence Trace",
    "",
    "## Target",
    buildLine(targetCard, { safeMode }),
    "",
    `## Supports (up to depth ${depthLimit})`,
  ];

  const rootChildren = sortedChildren(targetCard.id);
  if (rootChildren.length === 0) {
    lines.push("- No supports links found for this card.");
  }

  const globalSeen = new Set<string>([targetCard.id]);
  let expandedNodeCount = 0;
  let truncated = false;

  const walk = (cardId: string, depth: number, path: Set<string>, indentLevel: number): void => {
    if (truncated) {
      return;
    }

    const card = cardsById.get(cardId);
    if (!card) {
      return;
    }

    const indent = "  ".repeat(indentLevel);

    if (path.has(cardId)) {
      lines.push(`${indent}${buildLine(card, { cycle: true, safeMode })}`);
      return;
    }

    if (globalSeen.has(cardId)) {
      lines.push(`${indent}${buildLine(card, { seeAbove: true, safeMode })}`);
      return;
    }

    if (expandedNodeCount >= maxNodes) {
      truncated = true;
      return;
    }

    expandedNodeCount += 1;
    lines.push(`${indent}${buildLine(card, { safeMode })}`);
    globalSeen.add(cardId);

    if (depth >= depthLimit) {
      return;
    }

    const claimType = resolveClaimType(card);
    if (stopAtFacts && claimType === "fact") {
      return;
    }

    const nextPath = new Set(path);
    nextPath.add(cardId);

    for (const childId of sortedChildren(cardId)) {
      walk(childId, depth + 1, nextPath, indentLevel + 1);
      if (truncated) {
        return;
      }
    }
  };

  for (const childId of rootChildren) {
    walk(childId, 1, new Set([targetCard.id]), 0);
    if (truncated) {
      break;
    }
  }

  if (truncated) {
    lines.push("- …truncated (maxNodes reached)");
  }

  if (safeMode && !SafeModePolicy.canExposeText("trace.text", "share", true)) {
    lines.push("- Safe mode enforced: text content redacted.");
  }
  lines.push("", "## Notes", "- This is an extracted structure, not an AI-generated argument.");

  return lines.join("\n");
}
