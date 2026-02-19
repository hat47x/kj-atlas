import type { DocumentV2 } from "../types";

export type EvidenceFinding = {
  severity: "warn" | "info";
  code: "E001" | "E002" | "E003" | "E004";
  title: string;
  detail: string;
  cardIds: string[];
  suggestedAction: string;
};

export type EvidenceGapReport = {
  generatedAt: string;
  stats: {
    totalLinks: number;
    supportsLinks: number;
    contradictsLinks: number;
    hypothesisCount: number;
    claimCount: number;
    factCount: number;
    hypothesesWithNoFactSupport: number;
    claimsWithNoFactSupport: number;
    factsUnusedAsEvidence: number;
    contradictionsWithoutCounterSupport: number;
  };
  findings: EvidenceFinding[];
};

const MAX_ITEMS_PER_CATEGORY = 20;

export function analyzeEvidenceGaps(doc: DocumentV2): EvidenceGapReport {
  const links = doc.evidenceLinks ?? [];
  const cardsById = new Map(doc.cards.map((card) => [card.id, card]));
  const sortedCards = [...doc.cards].sort((a, b) => a.id.localeCompare(b.id));

  const incomingSupportsByCardId = new Map<string, Set<string>>();
  const outgoingSupportsByCardId = new Map<string, Set<string>>();
  const contradictLinks = links
    .filter((link) => link.type === "contradicts")
    .sort((a, b) =>
      a.fromCardId.localeCompare(b.fromCardId) ||
      a.toCardId.localeCompare(b.toCardId) ||
      a.id.localeCompare(b.id)
    );

  for (const link of links) {
    if (!cardsById.has(link.fromCardId) || !cardsById.has(link.toCardId)) {
      continue;
    }

    if (link.type === "supports") {
      const incoming = incomingSupportsByCardId.get(link.toCardId) ?? new Set<string>();
      incoming.add(link.fromCardId);
      incomingSupportsByCardId.set(link.toCardId, incoming);

      const outgoing = outgoingSupportsByCardId.get(link.fromCardId) ?? new Set<string>();
      outgoing.add(link.toCardId);
      outgoingSupportsByCardId.set(link.fromCardId, outgoing);
    }
  }

  const hasIncomingFactSupport = (cardId: string): boolean => {
    const incoming = incomingSupportsByCardId.get(cardId);
    if (!incoming) {
      return false;
    }

    for (const fromCardId of incoming) {
      if (cardsById.get(fromCardId)?.claimType === "fact") {
        return true;
      }
    }

    return false;
  };

  const hypotheses = sortedCards.filter((card) => card.claimType === "hypothesis");
  const claims = sortedCards.filter((card) => card.claimType === "claim");
  const facts = sortedCards.filter((card) => card.claimType === "fact");

  const hypothesisNoSupportAll = hypotheses.filter((card) => !hasIncomingFactSupport(card.id));
  const claimNoSupportAll = claims.filter((card) => !hasIncomingFactSupport(card.id));
  const unusedFactsAll = facts.filter((card) => !outgoingSupportsByCardId.has(card.id));

  const contradictionWithoutGroundingAll = contradictLinks
    .filter((link) => !hasIncomingFactSupport(link.fromCardId) && !hasIncomingFactSupport(link.toCardId));

  const hypothesisNoSupport = hypothesisNoSupportAll.slice(0, MAX_ITEMS_PER_CATEGORY);
  const claimNoSupport = claimNoSupportAll.slice(0, MAX_ITEMS_PER_CATEGORY);
  const unusedFacts = unusedFactsAll.slice(0, MAX_ITEMS_PER_CATEGORY);
  const contradictionWithoutGrounding = contradictionWithoutGroundingAll.slice(0, MAX_ITEMS_PER_CATEGORY);

  const findings: EvidenceFinding[] = [
    ...hypothesisNoSupport.map((card) => ({
      severity: "warn" as const,
      code: "E001" as const,
      title: "Hypothesis has no fact support",
      detail: `Card ${card.id} has no incoming supports links from fact cards.`,
      cardIds: [card.id],
      suggestedAction: "Link at least one fact card with supports.",
    })),
    ...claimNoSupport.map((card) => ({
      severity: "warn" as const,
      code: "E002" as const,
      title: "Claim has no fact support",
      detail: `Card ${card.id} has no incoming supports links from fact cards.`,
      cardIds: [card.id],
      suggestedAction: "Link at least one fact card with supports.",
    })),
    ...unusedFacts.map((card) => ({
      severity: "info" as const,
      code: "E003" as const,
      title: "Fact is unused as evidence",
      detail: `Fact card ${card.id} has no outgoing supports links.`,
      cardIds: [card.id],
      suggestedAction: "Use this fact to support a hypothesis or claim.",
    })),
    ...contradictionWithoutGrounding.map((link) => ({
      severity: "info" as const,
      code: "E004" as const,
      title: "Contradiction needs grounding",
      detail: `Contradiction ${link.fromCardId} -> ${link.toCardId} has no fact support on either side.`,
      cardIds: [link.fromCardId, link.toCardId],
      suggestedAction: "Add supporting fact links for one or both sides.",
    })),
  ];

  return {
    generatedAt: new Date().toISOString(),
    stats: {
      totalLinks: links.length,
      supportsLinks: links.filter((link) => link.type === "supports").length,
      contradictsLinks: links.filter((link) => link.type === "contradicts").length,
      hypothesisCount: hypotheses.length,
      claimCount: claims.length,
      factCount: facts.length,
      hypothesesWithNoFactSupport: hypothesisNoSupportAll.length,
      claimsWithNoFactSupport: claimNoSupportAll.length,
      factsUnusedAsEvidence: unusedFactsAll.length,
      contradictionsWithoutCounterSupport: contradictionWithoutGroundingAll.length,
    },
    findings,
  };
}
