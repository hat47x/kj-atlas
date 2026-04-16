export type WorkspaceDecision = "adopt" | "reject" | "hold";
export type QueryScope = "all" | "selection" | "island";
export type WorkspacePhase = "idle" | "decision_recorded" | "preset_replayed" | "rollback_ready" | "error";

export type CandidatePatchPreview = {
  sourceSnippets: string[];
  draftText: string;
  editedText?: string;
};

export type CandidateItem = {
  id: string;
  label: string;
  note?: string;
  preview?: CandidatePatchPreview;
};

export type CandidatePatchDiffSummary = {
  additions: number;
  removals: number;
  hasChanges: boolean;
};

export type QueryPreset = {
  id: string;
  name: string;
  scope: QueryScope;
  depth: number;
  filters: string[];
};

export type WorkspaceSnapshot = {
  decisions: Record<string, WorkspaceDecision>;
  selectedCandidateId: string | null;
  phase: WorkspacePhase;
};

export type WorkspaceAuditEntry = {
  candidateId: string;
  from: WorkspaceDecision;
  to: WorkspaceDecision;
  at: string;
  reason: "decision" | "rollback";
};

export type WorkspaceState = {
  decisions: Record<string, WorkspaceDecision>;
  selectedCandidateId: string | null;
  rollbackStack: WorkspaceSnapshot[];
  auditLog: WorkspaceAuditEntry[];
  phase: WorkspacePhase;
  lastExecutedQuery: string | null;
  failureMessage: string | null;
};

export function normalizeFilters(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim().toLowerCase())
    .filter((item) => item.length > 0)
    .sort((left, right) => left.localeCompare(right));
}

export function normalizePresetQuery(preset: Pick<QueryPreset, "scope" | "depth" | "filters">): string {
  const normalizedDepth = Number.isFinite(preset.depth) ? Math.max(1, Math.floor(preset.depth)) : 1;
  return JSON.stringify({
    scope: preset.scope,
    depth: normalizedDepth,
    filters: [...preset.filters].sort((left, right) => left.localeCompare(right)),
  });
}

function tokenizeDiffText(text: string): string[] {
  return text.trim().split(/\s+/).filter((token) => token.length > 0);
}

export function summarizeCandidatePatchDiff(preview: CandidatePatchPreview): CandidatePatchDiffSummary {
  const beforeTokens = tokenizeDiffText(preview.sourceSnippets.join(" "));
  const afterTokens = tokenizeDiffText(preview.editedText ?? preview.draftText);

  const beforeCount = new Map<string, number>();
  const afterCount = new Map<string, number>();

  for (const token of beforeTokens) {
    beforeCount.set(token, (beforeCount.get(token) ?? 0) + 1);
  }
  for (const token of afterTokens) {
    afterCount.set(token, (afterCount.get(token) ?? 0) + 1);
  }

  const tokenSet = new Set([...beforeCount.keys(), ...afterCount.keys()]);
  let additions = 0;
  let removals = 0;
  for (const token of tokenSet) {
    const before = beforeCount.get(token) ?? 0;
    const after = afterCount.get(token) ?? 0;
    if (after > before) {
      additions += after - before;
      continue;
    }
    if (before > after) {
      removals += before - after;
    }
  }

  return {
    additions,
    removals,
    hasChanges: additions > 0 || removals > 0,
  };
}

function buildInitialDecisions(candidates: CandidateItem[]): Record<string, WorkspaceDecision> {
  return Object.fromEntries(candidates.map((candidate) => [candidate.id, "hold"])) as Record<string, WorkspaceDecision>;
}

function snapshotState(state: WorkspaceState): WorkspaceSnapshot {
  return {
    decisions: { ...state.decisions },
    selectedCandidateId: state.selectedCandidateId,
    phase: state.phase,
  };
}

export function buildInitialWorkspaceState(candidates: CandidateItem[]): WorkspaceState {
  return {
    decisions: buildInitialDecisions(candidates),
    selectedCandidateId: candidates[0]?.id ?? null,
    rollbackStack: [],
    auditLog: [],
    phase: "idle",
    lastExecutedQuery: null,
    failureMessage: null,
  };
}

export function syncWorkspaceCandidates(state: WorkspaceState, candidates: CandidateItem[]): WorkspaceState {
  const nextDecisions = buildInitialDecisions(candidates);
  for (const candidate of candidates) {
    if (state.decisions[candidate.id]) {
      nextDecisions[candidate.id] = state.decisions[candidate.id];
    }
  }

  const selectedCandidateId =
    state.selectedCandidateId && candidates.some((candidate) => candidate.id === state.selectedCandidateId)
      ? state.selectedCandidateId
      : candidates[0]?.id ?? null;

  return {
    ...state,
    decisions: nextDecisions,
    selectedCandidateId,
  };
}

export function commitWorkspaceDecision(
  state: WorkspaceState,
  candidateId: string,
  decision: WorkspaceDecision,
  now: string
): WorkspaceState {
  const previousDecision = state.decisions[candidateId] ?? "hold";
  if (previousDecision === decision) {
    return {
      ...state,
      phase: state.rollbackStack.length > 0 ? "rollback_ready" : "idle",
      failureMessage: null,
    };
  }

  return {
    ...state,
    decisions: {
      ...state.decisions,
      [candidateId]: decision,
    },
    rollbackStack: [...state.rollbackStack, snapshotState(state)],
    auditLog: [
      ...state.auditLog,
      {
        candidateId,
        from: previousDecision,
        to: decision,
        at: now,
        reason: "decision",
      },
    ],
    phase: "decision_recorded",
    failureMessage: null,
  };
}

export function rollbackWorkspaceDecision(state: WorkspaceState, now: string = new Date().toISOString()): WorkspaceState {
  const snapshot = state.rollbackStack[state.rollbackStack.length - 1];
  if (!snapshot) {
    return {
      ...state,
      phase: "error",
      failureMessage: "No rollback point available.",
    };
  }

  const rollbackEntries: WorkspaceAuditEntry[] = [];
  const candidateIds = new Set([...Object.keys(state.decisions), ...Object.keys(snapshot.decisions)]);
  for (const candidateId of candidateIds) {
    const from = state.decisions[candidateId] ?? "hold";
    const to = snapshot.decisions[candidateId] ?? "hold";
    if (from === to) {
      continue;
    }
    rollbackEntries.push({
      candidateId,
      from,
      to,
      at: now,
      reason: "rollback",
    });
  }

  return {
    ...state,
    decisions: { ...snapshot.decisions },
    selectedCandidateId: snapshot.selectedCandidateId,
    rollbackStack: state.rollbackStack.slice(0, -1),
    auditLog: [...state.auditLog, ...rollbackEntries],
    phase: state.rollbackStack.length > 1 ? "rollback_ready" : "idle",
    failureMessage: null,
  };
}

export function replayPreset(
  state: WorkspaceState,
  preset: Pick<QueryPreset, "scope" | "depth" | "filters">,
  hasCandidates: boolean
): WorkspaceState {
  if (!hasCandidates) {
    return {
      ...state,
      phase: "error",
      failureMessage: "No candidates available. Collect candidates before preset execution.",
    };
  }

  return {
    ...state,
    phase: "preset_replayed",
    lastExecutedQuery: normalizePresetQuery(preset),
    failureMessage: null,
  };
}
