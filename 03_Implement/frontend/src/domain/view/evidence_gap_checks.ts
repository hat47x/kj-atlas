import type { Card, DocumentV1 } from "../types";

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

const FINDING_LIMIT_PER_CODE = 20;

function snippet(card: Card): string {
  const text = card.text.trim();
  return text.length > 80 ? `${text.slice(0, 80)}…` : text;
}

export function analyzeEvidenceGaps(document: DocumentV1): EvidenceGapReport {
  const cardsById = new Map(document.cards.map((card) => [card.id, card]));
  const evidenceLinks = document.evidenceLinks ?? [];

  const incomingSupports = new Map<string, Set<string>>();
  const incomingContradicts = new Map<string, Set<string>>();
  const outgoingSupports = new Map<string, Set<string>>();

  for (const link of evidenceLinks) {
    if (link.type === "supports") {
      const incoming = incomingSupports.get(link.toCardId) ?? new Set<string>();
      incoming.add(link.fromCardId);
      incomingSupports.set(link.toCardId, incoming);

      const outgoing = outgoingSupports.get(link.fromCardId) ?? new Set<string>();
      outgoing.add(link.toCardId);
      outgoingSupports.set(link.fromCardId, outgoing);
    }

    if (link.type === "contradicts") {
      const incoming = incomingContradicts.get(link.toCardId) ?? new Set<string>();
      incoming.add(link.fromCardId);
      incomingContradicts.set(link.toCardId, incoming);
    }
  }

  const hasIncomingFactSupport = (cardId: string): boolean => {
    const supportingCardIds = incomingSupports.get(cardId);
    if (!supportingCardIds) {
      return false;
    }

    for (const supportingCardId of supportingCardIds) {
      if (cardsById.get(supportingCardId)?.claimType === "fact") {
        return true;
      }
    }

    return false;
  };

  const hypotheses = document.cards.filter((card) => card.claimType === "hypothesis").sort((a, b) => a.id.localeCompare(b.id));
  const claims = document.cards.filter((card) => card.claimType === "claim").sort((a, b) => a.id.localeCompare(b.id));
  const facts = document.cards.filter((card) => card.claimType === "fact").sort((a, b) => a.id.localeCompare(b.id));

  const findings: EvidenceFinding[] = [];

  const hypothesisWithoutFact = hypotheses.filter((card) => !hasIncomingFactSupport(card.id));
  for (const card of hypothesisWithoutFact.slice(0, FINDING_LIMIT_PER_CODE)) {
    findings.push({
      severity: "warn",
      code: "E001",
      title: "Hypothesis lacks fact support",
      detail: `Hypothesis \"${snippet(card)}\" has no incoming supports link from a fact card.`,
      cardIds: [card.id],
      suggestedAction: "Add at least one supports link from a fact card.",
    });
  }

  const claimWithoutFact = claims.filter((card) => !hasIncomingFactSupport(card.id));
  for (const card of claimWithoutFact.slice(0, FINDING_LIMIT_PER_CODE)) {
    findings.push({
      severity: "warn",
      code: "E002",
      title: "Claim lacks fact support",
      detail: `Claim \"${snippet(card)}\" has no incoming supports link from a fact card.`,
      cardIds: [card.id],
      suggestedAction: "Attach supporting fact evidence for this claim.",
    });
  }

  const unusedFacts = facts.filter((card) => (outgoingSupports.get(card.id)?.size ?? 0) === 0);
  for (const card of unusedFacts.slice(0, FINDING_LIMIT_PER_CODE)) {
    findings.push({
      severity: "info",
      code: "E003",
      title: "Fact is unused as evidence",
      detail: `Fact \"${snippet(card)}\" does not support any other card.`,
      cardIds: [card.id],
      suggestedAction: "Connect this fact to a claim or hypothesis using supports.",
    });
  }

  const contradictionNeedingGrounding: EvidenceFinding[] = [];
  for (const link of evidenceLinks.filter((item) => item.type === "contradicts").sort((a, b) => a.id.localeCompare(b.id))) {
    const fromCard = cardsById.get(link.fromCardId);
    const toCard = cardsById.get(link.toCardId);
    if (!fromCard || !toCard) {
      continue;
    }

    const fromGrounded = hasIncomingFactSupport(fromCard.id);
    const toGrounded = hasIncomingFactSupport(toCard.id);
    if (fromGrounded || toGrounded) {
      continue;
    }

    contradictionNeedingGrounding.push({
      severity: "info",
      code: "E004",
      title: "Contradiction needs grounding",
      detail: `Contradiction between \"${snippet(fromCard)}\" and \"${snippet(toCard)}\" has no fact supports on either side.`,
      cardIds: [fromCard.id, toCard.id],
      suggestedAction: "Ground one or both sides with fact supports.",
    });
  }
  findings.push(...contradictionNeedingGrounding.slice(0, FINDING_LIMIT_PER_CODE));

  return {
    generatedAt: new Date().toISOString(),
    stats: {
      totalLinks: evidenceLinks.length,
      supportsLinks: evidenceLinks.filter((link) => link.type === "supports").length,
      contradictsLinks: evidenceLinks.filter((link) => link.type === "contradicts").length,
      hypothesisCount: hypotheses.length,
      claimCount: claims.length,
      factCount: facts.length,
      hypothesesWithNoFactSupport: hypothesisWithoutFact.length,
      claimsWithNoFactSupport: claimWithoutFact.length,
      factsUnusedAsEvidence: unusedFacts.length,
      contradictionsWithoutCounterSupport: contradictionNeedingGrounding.length,
    },
    findings,
  };
}
