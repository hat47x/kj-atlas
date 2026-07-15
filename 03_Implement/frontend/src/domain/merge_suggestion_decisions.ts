import type { DocumentV1 } from "./types";
import { STREAM_B_CONTRACTS } from "./stream_b_contract";

export const MERGE_SUGGESTION_DECISIONS = ["accept", "partial", "reject", "defer"] as const;
const DECISION_LOG_SNAPSHOT_VERSION = STREAM_B_CONTRACTS.decisionLog.contractId;

export type MergeSuggestionDecision = (typeof MERGE_SUGGESTION_DECISIONS)[number];

export type MergeSuggestionDecisionEntry = {
  id: string;
  decisionId?: string;
  groupId: string;
  decision: MergeSuggestionDecision;
  action?: MergeSuggestionDecision;
  decidedAt: string;
  decidedBy?: string;
  cardIds: string[];
  selectedCardIds?: string[];
  mergedTextDraft: string;
  editedText: string;
  note?: string;
  snapshotVersion?: string;
  rationale?: string;
};

type AppendMergeSuggestionDecisionInput = {
  groupId: string;
  decision: MergeSuggestionDecision;
  cardIds: string[];
  mergedTextDraft: string;
  editedText: string;
  rationale?: string;
  decisionReason?: string;
};

function sortCardIds(cardIds: string[]): string[] {
  return [...new Set(cardIds)].sort((left, right) => left.localeCompare(right));
}

function assertNonEmptyString(value: string, field: string): void {
  if (value.trim().length === 0) {
    throw new Error(`${field} must be a non-empty string`);
  }
}

function isMergeSuggestionDecision(value: unknown): value is MergeSuggestionDecision {
  return typeof value === "string" && MERGE_SUGGESTION_DECISIONS.includes(value as MergeSuggestionDecision);
}

export function appendMergeSuggestionDecision(
  document: DocumentV1,
  input: AppendMergeSuggestionDecisionInput,
  options?: { idFactory?: () => string; now?: string }
): DocumentV1 {
  assertNonEmptyString(input.groupId, "groupId");
  assertNonEmptyString(input.mergedTextDraft, "mergedTextDraft");
  assertNonEmptyString(input.editedText, "editedText");
  if (!isMergeSuggestionDecision(input.decision)) {
    throw new Error("decision must be one of accept|partial|reject|defer");
  }

  const idFactory = options?.idFactory ?? (() => crypto.randomUUID());
  const now = options?.now ?? new Date().toISOString();

  const sortedCardIds = sortCardIds(input.cardIds);
  if (sortedCardIds.length === 0) {
    throw new Error("cardIds must contain at least one id");
  }

  const decisionId = idFactory();
  const entry: MergeSuggestionDecisionEntry = {
    id: decisionId,
    decisionId,
    groupId: input.groupId,
    decision: input.decision,
    action: input.decision,
    decidedAt: now,
    decidedBy: "human",
    cardIds: sortedCardIds,
    selectedCardIds: sortedCardIds,
    mergedTextDraft: input.mergedTextDraft,
    editedText: input.editedText,
    note: input.decisionReason ?? input.editedText,
    snapshotVersion: DECISION_LOG_SNAPSHOT_VERSION,
    rationale: input.rationale,
  };

  return {
    ...document,
    mergeSuggestionDecisions: [...(document.mergeSuggestionDecisions ?? []), entry],
  };
}

export function getLatestMergeSuggestionDecisionByGroup(
  decisions: DocumentV1["mergeSuggestionDecisions"]
): Map<string, MergeSuggestionDecisionEntry> {
  const latest = new Map<string, MergeSuggestionDecisionEntry>();
  for (const decision of decisions ?? []) {
    const current = latest.get(decision.groupId);
    if (!current || current.decidedAt <= decision.decidedAt) {
      latest.set(decision.groupId, decision);
    }
  }
  return latest;
}

export function listMergeSuggestionDecisionsByGroup(
  decisions: DocumentV1["mergeSuggestionDecisions"],
  groupId: string
): MergeSuggestionDecisionEntry[] {
  assertNonEmptyString(groupId, "groupId");
  return (decisions ?? []).filter((decision) => decision.groupId === groupId);
}

export function restoreMergeSuggestionDecisionsBySnapshot(
  decisions: DocumentV1["mergeSuggestionDecisions"],
  snapshotVersion: string
): MergeSuggestionDecisionEntry[] {
  assertNonEmptyString(snapshotVersion, "snapshotVersion");
  if (snapshotVersion !== DECISION_LOG_SNAPSHOT_VERSION) {
    throw new Error(
      `snapshotVersion must match ${DECISION_LOG_SNAPSHOT_VERSION}; contract deviations must be routed to A1`
    );
  }
  return (decisions ?? []).filter(
    (decision) =>
      decision.snapshotVersion === snapshotVersion
      && isMergeSuggestionDecision(decision.action)
      && decision.decidedBy === "human"
  );
}
