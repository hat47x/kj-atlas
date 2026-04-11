export type WorkspaceDecision = "adopt" | "reject" | "hold";
export type QueryScope = "all" | "selection" | "island";

export type CandidateItem = {
  id: string;
  label: string;
  note?: string;
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
};

export type WorkspaceAuditEntry = {
  candidateId: string;
  from: WorkspaceDecision;
  to: WorkspaceDecision;
  at: string;
};

export type WorkspaceState = {
  decisions: Record<string, WorkspaceDecision>;
  selectedCandidateId: string | null;
  rollbackStack: WorkspaceSnapshot[];
  auditLog: WorkspaceAuditEntry[];
};

export function normalizeFilters(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim().toLowerCase())
    .filter((item) => item.length > 0)
    .sort((left, right) => left.localeCompare(right));
}

export function normalizePresetQuery(preset: Pick<QueryPreset, "scope" | "depth" | "filters">): string {
  return JSON.stringify({
    scope: preset.scope,
    depth: Math.max(1, Math.floor(preset.depth)),
    filters: [...preset.filters].sort((left, right) => left.localeCompare(right)),
  });
}

function buildInitialDecisions(candidates: CandidateItem[]): Record<string, WorkspaceDecision> {
  return Object.fromEntries(candidates.map((candidate) => [candidate.id, "hold"])) as Record<string, WorkspaceDecision>;
}

export function buildInitialWorkspaceState(candidates: CandidateItem[]): WorkspaceState {
  return {
    decisions: buildInitialDecisions(candidates),
    selectedCandidateId: candidates[0]?.id ?? null,
    rollbackStack: [],
    auditLog: [],
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
  return {
    ...state,
    decisions: {
      ...state.decisions,
      [candidateId]: decision,
    },
    rollbackStack: [
      ...state.rollbackStack,
      {
        decisions: { ...state.decisions },
        selectedCandidateId: state.selectedCandidateId,
      },
    ],
    auditLog: [
      ...state.auditLog,
      {
        candidateId,
        from: previousDecision,
        to: decision,
        at: now,
      },
    ],
  };
}

export function rollbackWorkspaceDecision(state: WorkspaceState): WorkspaceState {
  const snapshot = state.rollbackStack[state.rollbackStack.length - 1];
  if (!snapshot) {
    return state;
  }

  return {
    ...state,
    decisions: snapshot.decisions,
    selectedCandidateId: snapshot.selectedCandidateId,
    rollbackStack: state.rollbackStack.slice(0, -1),
  };
}
