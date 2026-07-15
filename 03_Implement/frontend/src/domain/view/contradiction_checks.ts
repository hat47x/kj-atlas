import type { DocumentV1, Edge, RelationSummary } from "../types";

export type ContradictionEntityRef = {
  kind: "island" | "card" | "edge" | "relationSummary";
  idOrSignature: string;
};

export type ContradictionSignal = {
  severity: "warn" | "info";
  code: string;
  title: string;
  detail: string;
  entityRefs: ContradictionEntityRef[];
  pairKey?: string;
  suggestedAction?: string;
};

export type ContradictionReport = {
  generatedAt: string;
  stats: {
    pairsChecked: number;
    signals: number;
  };
  signals: ContradictionSignal[];
};

// DOMAIN-EXPR-04 (schemas.md §16.2): deterministic identity for a signal across
// re-runs of analyzeContradictions(), used as the key for a persisted human
// review decision. Signals themselves are never persisted.
export function signatureKeyForContradictionSignal(signal: Pick<ContradictionSignal, "code" | "pairKey" | "entityRefs">): string {
  const suffix = signal.pairKey ?? signal.entityRefs[0]?.idOrSignature ?? "";
  return `${signal.code}:${suffix}`;
}

type PairAccumulator = {
  islandAId: string;
  islandBId: string;
  positiveEdgeIds: string[];
  negativeEdgeIds: string[];
  summaries: RelationSummary[];
};

const SUMMARY_CONFLICT_MARKERS = ["しかし", "一方", "反対", "矛盾", "否定"];
const SUMMARY_ALIGNMENT_MARKERS = ["一致", "同じ", "支持", "相互"];
const ISLAND_MUST_MARKERS = ["べき", "必要"];
const ISLAND_MUST_NOT_MARKERS = ["べきでない", "不要", "禁止"];

function toEdgePolarity(edgeType: string): "pos" | "neg" | "unknown" {
  if (edgeType === "related") {
    return "pos";
  }

  if (edgeType === "negate" || edgeType === "negation" || edgeType === "denial") {
    return "neg";
  }

  return "unknown";
}

function canonicalPair(islandAId: string, islandBId: string): { pairKey: string; ordered: [string, string] } {
  const ordered: [string, string] = islandAId <= islandBId ? [islandAId, islandBId] : [islandBId, islandAId];
  return {
    pairKey: `island:${ordered[0]}|island:${ordered[1]}`,
    ordered,
  };
}

function hasAnyKeyword(text: string, keywords: readonly string[]): boolean {
  return keywords.some((keyword) => text.includes(keyword));
}

function getSummaryPolarity(summary: RelationSummary): "pos" | "neg" | null {
  const direct = (summary as RelationSummary & { polarity?: unknown }).polarity;
  if (direct === "pos" || direct === "positive") {
    return "pos";
  }

  if (direct === "neg" || direct === "negative") {
    return "neg";
  }

  const tags = (summary as RelationSummary & { tags?: unknown }).tags;
  if (Array.isArray(tags)) {
    const normalizedTags = tags.filter((tag): tag is string => typeof tag === "string");
    const hasPos = normalizedTags.some((tag) => tag === "pos" || tag === "positive");
    const hasNeg = normalizedTags.some((tag) => tag === "neg" || tag === "negative");

    if (hasPos && !hasNeg) {
      return "pos";
    }

    if (hasNeg && !hasPos) {
      return "neg";
    }
  }

  return null;
}

function pushPairEdge(pairMap: Map<string, PairAccumulator>, edge: Edge): void {
  if (edge.fromKind === "island" && edge.toKind === "island") {
    const { pairKey, ordered } = canonicalPair(edge.fromId, edge.toId);
    const existing = pairMap.get(pairKey) ?? {
      islandAId: ordered[0],
      islandBId: ordered[1],
      positiveEdgeIds: [],
      negativeEdgeIds: [],
      summaries: [],
    };
    const polarity = toEdgePolarity(edge.type);
    if (polarity === "pos") {
      existing.positiveEdgeIds.push(edge.id);
    }
    if (polarity === "neg") {
      existing.negativeEdgeIds.push(edge.id);
    }
    pairMap.set(pairKey, existing);
  }
}

function pushPairSummary(pairMap: Map<string, PairAccumulator>, summary: RelationSummary): void {
  const { pairKey, ordered } = canonicalPair(summary.islandAId, summary.islandBId);
  const existing = pairMap.get(pairKey) ?? {
    islandAId: ordered[0],
    islandBId: ordered[1],
    positiveEdgeIds: [],
    negativeEdgeIds: [],
    summaries: [],
  };
  existing.summaries.push(summary);
  pairMap.set(pairKey, existing);
}

export function analyzeContradictions(doc: DocumentV1, nowIso: string = new Date().toISOString()): ContradictionReport {
  const pairMap = new Map<string, PairAccumulator>();

  for (const edge of doc.edges) {
    pushPairEdge(pairMap, edge);
  }

  for (const summary of doc.relationSummaries ?? []) {
    if (!doc.islands.some((island) => island.id === summary.islandAId) || !doc.islands.some((island) => island.id === summary.islandBId)) {
      continue;
    }
    pushPairSummary(pairMap, summary);
  }

  const signals: ContradictionSignal[] = [];
  const sortedPairEntries = Array.from(pairMap.entries()).sort(([left], [right]) => left.localeCompare(right));

  for (const [pairKey, pair] of sortedPairEntries) {
    if (pair.positiveEdgeIds.length > 0 && pair.negativeEdgeIds.length > 0) {
      signals.push({
        severity: "warn",
        code: "C001",
        title: "Conflicting relation types for same island pair",
        detail: `${pair.islandAId} と ${pair.islandBId} の間に positive/negative の両方の関係線があります。`,
        pairKey,
        entityRefs: [
          { kind: "island", idOrSignature: pair.islandAId },
          { kind: "island", idOrSignature: pair.islandBId },
          ...pair.positiveEdgeIds.map((edgeId) => ({ kind: "edge" as const, idOrSignature: edgeId })),
          ...pair.negativeEdgeIds.map((edgeId) => ({ kind: "edge" as const, idOrSignature: edgeId })),
        ],
        suggestedAction: "対象ペアの関係線を確認し、否定関係か補足説明かを明示してください。",
      });
    }

    const summaryPolarities = pair.summaries.map((summary) => ({ summary, polarity: getSummaryPolarity(summary) }));
    const hasPosSummary = summaryPolarities.some((item) => item.polarity === "pos");
    const hasNegSummary = summaryPolarities.some((item) => item.polarity === "neg");
    if (hasPosSummary && hasNegSummary) {
      signals.push({
        severity: "warn",
        code: "C002",
        title: "Relation summaries with opposite polarity tags",
        detail: `${pair.islandAId} と ${pair.islandBId} の relation summary に正負が混在しています。`,
        pairKey,
        entityRefs: [
          { kind: "island", idOrSignature: pair.islandAId },
          { kind: "island", idOrSignature: pair.islandBId },
          ...summaryPolarities
            .filter((item) => item.polarity !== null)
            .map((item) => ({ kind: "relationSummary" as const, idOrSignature: item.summary.id })),
        ],
        suggestedAction: "summary polarity を整理し、同一ペア内で矛盾しないように見直してください。",
      });
    }

    const conflictMarkerSummaryIds = pair.summaries
      .filter((summary) => hasAnyKeyword(summary.text, SUMMARY_CONFLICT_MARKERS))
      .map((summary) => summary.id);
    const alignmentMarkerSummaryIds = pair.summaries
      .filter((summary) => hasAnyKeyword(summary.text, SUMMARY_ALIGNMENT_MARKERS))
      .map((summary) => summary.id);
    const hasDifferentMarkerSources = conflictMarkerSummaryIds.some(
      (conflictId) => !alignmentMarkerSummaryIds.includes(conflictId)
    );
    if (conflictMarkerSummaryIds.length > 0 && alignmentMarkerSummaryIds.length > 0 && hasDifferentMarkerSources) {
      signals.push({
        severity: "info",
        code: "C003",
        title: "Summary marker mismatch detected",
        detail: `${pair.islandAId} と ${pair.islandBId} の summary に衝突系/一致系マーカーが併存しています。`,
        pairKey,
        entityRefs: [
          { kind: "island", idOrSignature: pair.islandAId },
          { kind: "island", idOrSignature: pair.islandBId },
          ...pair.summaries.map((summary) => ({ kind: "relationSummary" as const, idOrSignature: summary.id })),
        ],
        suggestedAction: "表現の意図を人手で確認し、必要なら summary を分離・修正してください。",
      });
    }
  }

  for (const island of [...doc.islands].sort((a, b) => a.id.localeCompare(b.id))) {
    const summaryText = island.summaryText ?? "";
    if (summaryText.length === 0) {
      continue;
    }

    if (hasAnyKeyword(summaryText, ISLAND_MUST_MARKERS) && hasAnyKeyword(summaryText, ISLAND_MUST_NOT_MARKERS)) {
      signals.push({
        severity: "info",
        code: "C004",
        title: "Island summary has both must and must-not markers",
        detail: `Island ${island.id} の summary に「べき/必要」と「べきでない/不要/禁止」が同居しています。`,
        entityRefs: [{ kind: "island", idOrSignature: island.id }],
        suggestedAction: "要件と禁止事項の境界を人手で確認してください。",
      });
    }
  }

  signals.sort((left, right) => {
    if (left.severity !== right.severity) {
      return left.severity === "warn" ? -1 : 1;
    }
    if (left.code !== right.code) {
      return left.code.localeCompare(right.code);
    }
    return (left.pairKey ?? left.detail).localeCompare(right.pairKey ?? right.detail);
  });

  return {
    generatedAt: nowIso,
    stats: {
      pairsChecked: pairMap.size,
      signals: signals.length,
    },
    signals,
  };
}
