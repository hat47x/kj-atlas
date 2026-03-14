export const P2B_DECISION_ACTIONS = ["accept", "partial", "reject", "defer"] as const;

export type P2BDecisionAction = (typeof P2B_DECISION_ACTIONS)[number];

export type MergeDecisionRecord = {
  decisionId: string;
  groupId: string;
  action: P2BDecisionAction;
  selectedCardIds: string[];
  note: string;
  decidedBy: string;
  decidedAt: string;
  snapshotVersion: string;
};

function isDecisionAction(action: string): action is P2BDecisionAction {
  return P2B_DECISION_ACTIONS.includes(action as P2BDecisionAction);
}

export class P2BDecisionLogMockStore {
  private readonly records: MergeDecisionRecord[] = [];

  append(record: MergeDecisionRecord): void {
    this.records.push({
      ...record,
      selectedCardIds: [...record.selectedCardIds],
    });
  }

  listByGroup(groupId: string): MergeDecisionRecord[] {
    return this.records
      .filter((record) => record.groupId === groupId)
      .map((record) => ({ ...record, selectedCardIds: [...record.selectedCardIds] }));
  }

  restore(snapshotVersion: string): MergeDecisionRecord[] {
    return this.records
      .filter((record) => record.snapshotVersion === snapshotVersion)
      .filter((record) => isDecisionAction(record.action))
      .map((record) => ({ ...record, selectedCardIds: [...record.selectedCardIds] }));
  }
}
