import type { DocumentV1 } from "../types";
import { analyzeEvidenceGaps, type EvidenceGapReport } from "./evidence_gap_checks";
import type { PerspectiveMode } from "./perspective";
import { t } from "../../i18n/translate";

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
  targetSelector: (doc: DocumentV1, viewState: GuidedFlowViewState) => string[];
  suggestedActions: string[];
  optional?: boolean;
};

function isUnknownClaimType(claimType: DocumentV1["cards"][number]["claimType"]): boolean {
  return claimType === undefined || claimType === "unknown";
}

function buildReviewTargets(doc: DocumentV1): string[] {
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

function buildClassifyTargets(doc: DocumentV1): string[] {
  return doc.cards
    .filter((card) => isUnknownClaimType(card.claimType))
    .map((card) => card.id)
    .sort((left, right) => left.localeCompare(right));
}

function buildEvidenceTargets(doc: DocumentV1, evidenceGapReport?: EvidenceGapReport | null): string[] {
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

function buildContradictionTargets(doc: DocumentV1): string[] {
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
      title: t("guided_flow.review.title"),
      description: t("guided_flow.review.description"),
      perspectiveMode: "review",
      targetSelector: (doc) => buildReviewTargets(doc),
      suggestedActions: [t("guided_flow.review.action_review"), t("guided_flow.review.action_confirm")],
    },
    {
      id: "classify",
      title: t("guided_flow.classify.title"),
      description: t("guided_flow.classify.description"),
      perspectiveMode: "unknown",
      targetSelector: (doc) => buildClassifyTargets(doc),
      suggestedActions: [t("guided_flow.classify.action_set"), t("guided_flow.classify.action_skip")],
    },
    {
      id: "evidence",
      title: t("guided_flow.evidence.title"),
      description: t("guided_flow.evidence.description"),
      perspectiveMode: "evidence",
      targetSelector: (doc) => buildEvidenceTargets(doc, evidenceGapReport),
      suggestedActions: [t("guided_flow.evidence.action_open_editor"), t("guided_flow.evidence.action_add_supports")],
    },
    {
      id: "contradiction",
      title: t("guided_flow.contradiction.title"),
      description: t("guided_flow.contradiction.description"),
      perspectiveMode: "contradiction",
      targetSelector: (doc) => buildContradictionTargets(doc),
      suggestedActions: [t("guided_flow.contradiction.action_inspect"), t("guided_flow.contradiction.action_add")],
      optional: true,
    },
  ];
}

export function getGuidedFlowStepIndex(steps: GuidedFlowStep[], stepId: GuidedFlowStepId): number {
  const index = steps.findIndex((step) => step.id === stepId);
  return index >= 0 ? index : 0;
}
