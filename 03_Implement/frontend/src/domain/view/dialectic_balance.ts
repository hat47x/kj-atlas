import type { DocumentV1 } from "../types";

export type BalanceFindingCode = "B001" | "B002" | "B003" | "B004" | "B005" | "B006";

export type BalanceFinding = {
  severity: "warn" | "info";
  code: BalanceFindingCode;
  title: string;
  detail: string;
  cardIds?: string[];
  suggestedAction: string;
};

export type DialecticBalanceReport = {
  generatedAt: string;
  stats: {
    totalCards: number;
    factCount: number;
    claimCount: number;
    hypothesisCount: number;
    supportsCount: number;
    contradictsCount: number;
    hypothesisWithSupportCount: number;
    hypothesisWithContradictionCount: number;
    claimWithSupportCount: number;
    claimWithContradictionCount: number;
  };
  findings: BalanceFinding[];
};

type CardSignal = {
  incomingSupportsFromFact: number;
  incomingContradictions: number;
  outgoingSupports: number;
  outgoingContradictions: number;
};

function ratio(numerator: number, denominator: number): number {
  if (denominator <= 0) {
    return 0;
  }
  return numerator / denominator;
}

export function analyzeDialecticBalance(doc: DocumentV1, nowIso: string = new Date().toISOString()): DialecticBalanceReport {
  const cardsById = new Map(doc.cards.map((card) => [card.id, card] as const));
  const evidenceLinks = doc.evidenceLinks ?? [];
  const cardSignals = new Map<string, CardSignal>();

  for (const card of doc.cards) {
    cardSignals.set(card.id, {
      incomingSupportsFromFact: 0,
      incomingContradictions: 0,
      outgoingSupports: 0,
      outgoingContradictions: 0,
    });
  }

  for (const link of evidenceLinks) {
    const fromCard = cardsById.get(link.fromCardId);
    const toCard = cardsById.get(link.toCardId);
    if (!fromCard || !toCard) {
      continue;
    }

    const fromSignal = cardSignals.get(fromCard.id);
    const toSignal = cardSignals.get(toCard.id);
    if (!fromSignal || !toSignal) {
      continue;
    }

    if (link.type === "supports") {
      fromSignal.outgoingSupports += 1;
      if ((fromCard.claimType ?? "unknown") === "fact") {
        toSignal.incomingSupportsFromFact += 1;
      }
      continue;
    }

    if (link.type === "contradicts") {
      fromSignal.outgoingContradictions += 1;
      toSignal.incomingContradictions += 1;
    }
  }

  const facts = doc.cards.filter((card) => (card.claimType ?? "unknown") === "fact");
  const claims = doc.cards.filter((card) => (card.claimType ?? "unknown") === "claim");
  const hypotheses = doc.cards.filter((card) => (card.claimType ?? "unknown") === "hypothesis");

  const hypothesisWithSupportIds = hypotheses
    .filter((card) => (cardSignals.get(card.id)?.incomingSupportsFromFact ?? 0) > 0)
    .map((card) => card.id)
    .sort();
  const hypothesisWithContradictionIds = hypotheses
    .filter((card) => (cardSignals.get(card.id)?.incomingContradictions ?? 0) > 0)
    .map((card) => card.id)
    .sort();
  const claimWithSupportIds = claims
    .filter((card) => (cardSignals.get(card.id)?.incomingSupportsFromFact ?? 0) > 0)
    .map((card) => card.id)
    .sort();
  const claimWithContradictionIds = claims
    .filter((card) => (cardSignals.get(card.id)?.incomingContradictions ?? 0) > 0)
    .map((card) => card.id)
    .sort();

  const findings: BalanceFinding[] = [];

  const contradictionPairsWithoutFactGrounding: string[][] = [];
  const seenContradictionPair = new Set<string>();
  for (const link of evidenceLinks) {
    if (link.type !== "contradicts") {
      continue;
    }
    const fromCard = cardsById.get(link.fromCardId);
    const toCard = cardsById.get(link.toCardId);
    if (!fromCard || !toCard) {
      continue;
    }

    const pair = [fromCard.id, toCard.id].sort();
    const pairKey = `${pair[0]}|${pair[1]}`;
    if (seenContradictionPair.has(pairKey)) {
      continue;
    }
    seenContradictionPair.add(pairKey);

    const fromGrounded = (cardSignals.get(fromCard.id)?.incomingSupportsFromFact ?? 0) > 0;
    const toGrounded = (cardSignals.get(toCard.id)?.incomingSupportsFromFact ?? 0) > 0;
    if (!fromGrounded && !toGrounded) {
      contradictionPairsWithoutFactGrounding.push(pair);
    }
  }

  const hypothesisWithContradictionShare = ratio(hypothesisWithContradictionIds.length, hypotheses.length);
  if (hypotheses.length >= 3 && hypothesisWithContradictionShare < 0.3) {
    const sample = hypotheses
      .filter((card) => (cardSignals.get(card.id)?.incomingContradictions ?? 0) === 0)
      .map((card) => card.id)
      .sort()
      .slice(0, 5);
    findings.push({
      severity: "warn",
      code: "B001",
      title: "Hypotheses are rarely contradicted",
      detail: `Only ${hypothesisWithContradictionIds.length}/${hypotheses.length} hypotheses have contradiction links.`,
      cardIds: sample,
      suggestedAction: "仮説に対する反証可能性を検討する",
    });
  }

  const hypothesisWithSupportShare = ratio(hypothesisWithSupportIds.length, hypotheses.length);
  if (hypotheses.length > 0 && hypothesisWithSupportShare < 0.5) {
    const sample = hypotheses
      .filter((card) => (cardSignals.get(card.id)?.incomingSupportsFromFact ?? 0) === 0)
      .map((card) => card.id)
      .sort()
      .slice(0, 5);
    findings.push({
      severity: "warn",
      code: "B002",
      title: "Hypotheses lack fact support",
      detail: `Only ${hypothesisWithSupportIds.length}/${hypotheses.length} hypotheses have incoming supports from fact cards.`,
      cardIds: sample,
      suggestedAction: "仮説にfactカードを紐付ける",
    });
  }

  if (claimWithContradictionIds.length === 0 && claims.length >= 5) {
    findings.push({
      severity: "info",
      code: "B003",
      title: "Claims have no dialectic tension",
      detail: `No claim card has incoming contradiction links (${claims.length} claims).`,
      cardIds: claims.map((card) => card.id).sort().slice(0, 5),
      suggestedAction: "対立する視点の有無を確認する",
    });
  }

  if (contradictionPairsWithoutFactGrounding.length > 0) {
    const sample = contradictionPairsWithoutFactGrounding
      .flatMap((pair) => pair)
      .sort()
      .filter((value, index, arr) => index === 0 || arr[index - 1] !== value)
      .slice(0, 6);
    findings.push({
      severity: "warn",
      code: "B004",
      title: "Contradictions are not fact-grounded",
      detail: `${contradictionPairsWithoutFactGrounding.length} contradiction pair(s) have no fact supports on either side.`,
      cardIds: sample,
      suggestedAction: "反証に事実根拠を追加する",
    });
  }

  if (facts.length > 0 && ratio(evidenceLinks.filter((link) => link.type === "supports").length, facts.length) < 1) {
    const usedFactIds = new Set(
      evidenceLinks
        .filter((link) => link.type === "supports")
        .map((link) => cardsById.get(link.fromCardId))
        .filter((card): card is NonNullable<typeof card> => card !== undefined)
        .filter((card) => (card.claimType ?? "unknown") === "fact")
        .map((card) => card.id)
    );
    findings.push({
      severity: "info",
      code: "B005",
      title: "Facts are underutilized",
      detail: `Supports per fact is ${(ratio(evidenceLinks.filter((link) => link.type === "supports").length, facts.length)).toFixed(2)} (${evidenceLinks.filter((link) => link.type === "supports").length}/${facts.length}).`,
      cardIds: facts.map((card) => card.id).filter((id) => !usedFactIds.has(id)).sort().slice(0, 5),
      suggestedAction: "factをsupportsリンクに接続する",
    });
  }

  if (evidenceLinks.filter((link) => link.type === "supports").length === 0 && evidenceLinks.filter((link) => link.type === "contradicts").length === 0 && doc.cards.length > 10) {
    findings.push({
      severity: "warn",
      code: "B006",
      title: "Dialectic structure is missing",
      detail: `No supports/contradicts links across ${doc.cards.length} cards.`,
      suggestedAction: "supports/contradictsリンクを導入する",
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
      totalCards: doc.cards.length,
      factCount: facts.length,
      claimCount: claims.length,
      hypothesisCount: hypotheses.length,
      supportsCount: evidenceLinks.filter((link) => link.type === "supports").length,
      contradictsCount: evidenceLinks.filter((link) => link.type === "contradicts").length,
      hypothesisWithSupportCount: hypothesisWithSupportIds.length,
      hypothesisWithContradictionCount: hypothesisWithContradictionIds.length,
      claimWithSupportCount: claimWithSupportIds.length,
      claimWithContradictionCount: claimWithContradictionIds.length,
    },
    findings,
  };
}
