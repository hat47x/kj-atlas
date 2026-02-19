import type { DocumentV2 } from "../types";
import { analyzeEvidenceGaps, type EvidenceGapReport } from "./evidence_gap_checks";
import type { PerspectiveMode } from "./perspective";

export type GuidedFlowStepId = "review" | "classify" | "evidence" | "contradiction";

export type GuidedFlowViewState = {
  guidedFlowEnabled: boolean;
  guidedFlowStepId: GuidedFlowStepId;
  guidedFlowTargetIndex: number;
};

export type GuidedFlowStep = {
  id: GuidedFlowStepId;
  title: string;
  description: string;
  perspectiveMode: PerspectiveMode;
  targetSelector: (doc: DocumentV2, viewState: GuidedFlowViewState) => string[];
  suggestedActions: string[];
  optional?: boolean;
};

function isUnknownClaimType(claimType: DocumentV2["cards"][number]["claimType"]): boolean {
  return claimType === undefined || claimType === "unknown";
}

function buildReviewTargets(doc: DocumentV2): string[] {
  const unknownCardIds = doc.cards
    .filter((card) => isUnknownClaimType(card.claimType))
    .map((card) => card.id)
    .sort((left, right) => left.localeCompare(right));

  const unreviewedIslandIds = doc.islands
    .filter((island) => island.summaryReviewed === false)
    .map((island) => island.id)
    .sort((left, right) => left.localeCompare(right));

  return [...unreviewedIslandIds, ...unknownCardIds];
}

function buildClassifyTargets(doc: DocumentV2): string[] {
  return doc.cards
    .filter((card) => isUnknownClaimType(card.claimType))
    .map((card) => card.id)
    .sort((left, right) => left.localeCompare(right));
}

function buildEvidenceTargets(doc: DocumentV2, evidenceGapReport?: EvidenceGapReport | null): string[] {
  const report = evidenceGapReport ?? analyzeEvidenceGaps(doc);
  const ids = new Set<string>();

  for (const finding of report.findings) {
    if (finding.code !== "E001" && finding.code !== "E002") {
      continue;
    }

    for (const cardId of finding.cardIds) {
      ids.add(cardId);
    }
  }

  return [...ids].sort((left, right) => left.localeCompare(right));
}

function buildContradictionTargets(doc: DocumentV2): string[] {
  const contradictingCardIdSet = new Set<string>();
  for (const link of doc.evidenceLinks ?? []) {
    if (link.type !== "contradicts") {
      continue;
    }

    contradictingCardIdSet.add(link.fromCardId);
    contradictingCardIdSet.add(link.toCardId);
  }

  return doc.cards
    .filter((card) => card.claimType === "hypothesis" && !contradictingCardIdSet.has(card.id))
    .map((card) => card.id)
    .sort((left, right) => left.localeCompare(right));
}

export function buildDefaultGuidedFlowSteps(evidenceGapReport?: EvidenceGapReport | null): GuidedFlowStep[] {
  return [
    {
      id: "review",
      title: "Review targets",
      description: "Unreviewed islands first, then unknown cards.",
      perspectiveMode: "review",
      targetSelector: (doc) => buildReviewTargets(doc),
      suggestedActions: ["Review summaries", "Confirm or keep pending"],
    },
    {
      id: "classify",
      title: "Classify unknown cards",
      description: "Assign claim types to unknown cards.",
      perspectiveMode: "unknown",
      targetSelector: (doc) => buildClassifyTargets(doc),
      suggestedActions: ["Set claim type", "Skip if intentionally unknown"],
    },
    {
      id: "evidence",
      title: "Add evidence links",
      description: "Focus hypotheses/claims lacking fact support.",
      perspectiveMode: "evidence",
      targetSelector: (doc) => buildEvidenceTargets(doc, evidenceGapReport),
      suggestedActions: ["Open evidence link editor", "Add fact supports"],
    },
    {
      id: "contradiction",
      title: "Add contradiction links (optional)",
      description: "Find hypotheses with no contradiction links.",
      perspectiveMode: "contradiction",
      targetSelector: (doc) => buildContradictionTargets(doc),
      suggestedActions: ["Inspect opposing cards", "Add contradicts links if needed"],
      optional: true,
    },
  ];
}

export function getGuidedFlowStepIndex(steps: GuidedFlowStep[], stepId: GuidedFlowStepId): number {
  const index = steps.findIndex((step) => step.id === stepId);
  return index >= 0 ? index : 0;
}

export function clampGuidedFlowTargetIndex(targetIndex: number, total: number): number {
  if (total <= 0) {
    return 0;
  }

  if (targetIndex < 0) {
    return 0;
  }

  if (targetIndex >= total) {
    return total - 1;
  }

  return targetIndex;
}
