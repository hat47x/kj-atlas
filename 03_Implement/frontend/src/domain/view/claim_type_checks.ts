import type { Card, DocumentV1 } from "../types";

export type ClaimType = "fact" | "claim" | "hypothesis" | "unknown";

export type ClaimTypeMixFinding = {
  severity: "warn" | "info";
  code: "T001" | "T002" | "T003" | "T004";
  title: string;
  detail: string;
  islandIds: string[];
  suggestedAction: string;
};

export type ClaimTypeMixReport = {
  generatedAt: string;
  stats: {
    totalCards: number;
    countsByType: Record<ClaimType, number>;
    islandsChecked: number;
    islandsMixedCount: number;
    islandsHypothesisDominantCount: number;
    islandsUnknownDominantCount: number;
  };
  findings: ClaimTypeMixFinding[];
};

function resolveClaimType(card: Card): ClaimType {
  return card.claimType ?? "unknown";
}

function share(count: number, total: number): number {
  if (total <= 0) {
    return 0;
  }
  return count / total;
}

export function analyzeClaimTypeMix(doc: DocumentV1, nowIso: string = new Date().toISOString()): ClaimTypeMixReport {
  const cardsById = new Map(doc.cards.map((card) => [card.id, card] as const));
  const countsByType: Record<ClaimType, number> = {
    fact: 0,
    claim: 0,
    hypothesis: 0,
    unknown: 0,
  };

  for (const card of doc.cards) {
    countsByType[resolveClaimType(card)] += 1;
  }

  const findings: ClaimTypeMixFinding[] = [];
  let islandsChecked = 0;
  let islandsMixedCount = 0;
  let islandsHypothesisDominantCount = 0;
  let islandsUnknownDominantCount = 0;

  for (const island of [...doc.islands].sort((a, b) => a.id.localeCompare(b.id))) {
    const memberCards = island.cardIds
      .map((cardId) => cardsById.get(cardId))
      .filter((card): card is Card => card !== undefined);

    if (memberCards.length < 3) {
      continue;
    }

    islandsChecked += 1;

    const islandCounts: Record<ClaimType, number> = {
      fact: 0,
      claim: 0,
      hypothesis: 0,
      unknown: 0,
    };

    for (const card of memberCards) {
      islandCounts[resolveClaimType(card)] += 1;
    }

    const total = memberCards.length;
    const nonZeroTypeCount = (Object.values(islandCounts).filter((count) => count > 0)).length;
    const maxShare = Math.max(...Object.values(islandCounts).map((count) => share(count, total)));
    const hypothesisShare = share(islandCounts.hypothesis, total);
    const unknownShare = share(islandCounts.unknown, total);

    if (nonZeroTypeCount >= 3 && maxShare < 0.6) {
      islandsMixedCount += 1;
      findings.push({
        severity: "warn",
        code: "T001",
        title: "Heavily mixed claim types",
        detail: `${island.id} has 3+ type categories and no single type exceeds 60%.`,
        islandIds: [island.id],
        suggestedAction: "島を分割する / 代表カードで論点を整理する",
      });
    }

    if (total >= 5 && hypothesisShare >= 0.7) {
      islandsHypothesisDominantCount += 1;
      findings.push({
        severity: "warn",
        code: "T002",
        title: "Hypothesis-dominant island",
        detail: `${island.id} has ${(hypothesisShare * 100).toFixed(0)}% hypothesis cards (${islandCounts.hypothesis}/${total}).`,
        islandIds: [island.id],
        suggestedAction: "裏付けとなるfactカードを追加する / 仮説の前提を明記する",
      });
    }

    if (total >= 5 && unknownShare >= 0.7) {
      islandsUnknownDominantCount += 1;
      findings.push({
        severity: "info",
        code: "T003",
        title: "Unknown-dominant island",
        detail: `${island.id} has ${(unknownShare * 100).toFixed(0)}% unknown cards (${islandCounts.unknown}/${total}).`,
        islandIds: [island.id],
        suggestedAction: "カード種別を分類する",
      });
    }
  }

  const factShare = share(countsByType.fact, doc.cards.length);
  if (doc.cards.length >= 20 && factShare < 0.1) {
    findings.push({
      severity: "info",
      code: "T004",
      title: "Facts are scarce in this document",
      detail: `Fact cards are ${(factShare * 100).toFixed(0)}% (${countsByType.fact}/${doc.cards.length}).`,
      islandIds: [],
      suggestedAction: "一次情報（fact）を補強する",
    });
  }

  findings.sort((left, right) => {
    if (left.severity !== right.severity) {
      return left.severity === "warn" ? -1 : 1;
    }
    const codeCompare = left.code.localeCompare(right.code);
    if (codeCompare !== 0) {
      return codeCompare;
    }
    return left.islandIds.join(",").localeCompare(right.islandIds.join(","));
  });

  return {
    generatedAt: nowIso,
    stats: {
      totalCards: doc.cards.length,
      countsByType,
      islandsChecked,
      islandsMixedCount,
      islandsHypothesisDominantCount,
      islandsUnknownDominantCount,
    },
    findings,
  };
}
