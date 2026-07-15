export type Transform = {
  panX: number;
  panY: number;
  zoom: number;
};

export type HoldState = "held" | "pending" | "shelved";

// DOMAIN-TRACE-01 (schemas.md §15): non-subject trace metadata only.
// seq = optional serial number (never auto-forced); source = free-text
// reference back to the RAW DATA outside the document (utterance, line
// number, URL...). Subject/provenance metadata (author, owner, updater)
// is NOT allowed here until CARD-META-UI-01's decision queue settles —
// validators drop unknown meta keys fail-closed (§15.3).
export type CardMeta = {
  seq?: number;
  source?: string;
};

// DOMAIN-KA-01 (schemas.md §17): KA-method fields, separate from Card.text
// (which stays the 出来事/event-of-record). voice = 心の声 (inner voice,
// unfiltered — guardrails against embellishing/fabricating are UI hints
// only, never enforced). value = 価値 (the KA-method's extracted value).
export type CardKa = {
  voice?: string;
  value?: string;
};

export type Card = {
  id: string;
  text: string;
  x: number;
  y: number;
  claimType?: "fact" | "claim" | "hypothesis" | "unknown";
  mergedIntoCardId?: string;
  repOf?: string[];
  canonicalId?: string;
  /** Merge provenance: ids of the cards consolidated INTO this one (canonicalization). Not an external source reference — that is Card.meta.source. */
  sources?: string[];
  critique?: string;
  critiqueTags?: string[];
  textReviewed?: boolean;
  /** DOMAIN-EXPR-02: optional hold state. Absent = not held (conventional card). */
  holdState?: HoldState;
  meta?: CardMeta;
  ka?: CardKa;
};

/** DOMAIN-EXPR-02: a shelved item — set aside from the main canvas without deletion. */
export type ShelfEntry = {
  cardId: string;
  shelvedAt: string;
  reason?: string;
};

export function isCanonicalCard(card: Card): boolean {
  return card.canonicalId === undefined;
}

export function isSourceCard(card: Card): boolean {
  return card.canonicalId !== undefined;
}

export const CRITIQUE_TAGS = [
  "too_close",
  "too_far",
  "not_the_same",
  "feels_off",
  "no_articulable_reason",
] as const;

export type CritiqueTag = (typeof CRITIQUE_TAGS)[number];

// DOMAIN-KJ-01 (ADR-0048 D3, schemas.md §3.3): KJ-method relation vocabulary.
// "negate" is the persisted value for KJ's 対立 — no separate opposition enum
// value exists (duplicate-vocabulary ban); only the UI label changed.
// "causal" is the only DIRECTED type (fromId=cause → toId=effect).
export const KNOWN_EDGE_TYPES = ["related", "negate", "causal", "mutual", "equivalence"] as const;

export type KnownEdgeType = (typeof KNOWN_EDGE_TYPES)[number];

// Unknown-type PRESERVATION (schemas.md §3.3.2): an imported type string
// outside the known set is kept verbatim (round-trip safety) and resolved to
// "related" for display/behavior only. The (string & {}) union keeps known-
// value autocomplete while accepting any string.
export type EdgeType = KnownEdgeType | (string & {});

export function resolveKnownEdgeType(type: EdgeType): KnownEdgeType {
  return (KNOWN_EDGE_TYPES as readonly string[]).includes(type) ? (type as KnownEdgeType) : "related";
}

export function isDirectedEdgeType(type: EdgeType): boolean {
  return resolveKnownEdgeType(type) === "causal";
}

export type EdgeEndpointKind = "card" | "island";

export type Edge = {
  id: string;
  fromId: string;
  toId: string;
  fromKind?: EdgeEndpointKind;
  toKind?: EdgeEndpointKind;
  type: EdgeType;
};

export type Point = {
  x: number;
  y: number;
};

export type IslandShapeGeneratedFrom = {
  cardIds: string[];
  versionToken: string;
};

export type RectIslandShape = {
  kind: "rect";
  generatedFrom?: IslandShapeGeneratedFrom;
};

export type PolygonIslandShape = {
  kind: "polygon";
  points: Point[];
  generatedFrom?: IslandShapeGeneratedFrom;
};

export type IslandShape = RectIslandShape | PolygonIslandShape;

export type IslandGeometry =
  | {
      type: "rect";
      x?: number;
      y?: number;
      w?: number;
      h?: number;
    }
  | {
      type: "polygon";
      points: Point[];
    };

export type SummaryHistoryEntry = {
  id: string;
  createdAt: string;
  fromText: string | null;
  toText: string | null;
  fromReviewed: boolean | null;
  toReviewed: boolean | null;
  changeKind: "manual" | "ai" | "import" | "unknown";
  note?: string;
  groundingIds?: string[];
};

export type Island = {
  id: string;
  cardIds: string[];
  parentIslandId?: string;
  placardCardId?: string;
  collapsed?: boolean;
  title?: string;
  titleReviewed?: boolean;
  summaryText?: string;
  summaryReviewed?: boolean;
  summaryGrounding?: string[];
  summaryHistory?: SummaryHistoryEntry[];
  imageUrl?: string;
  imageReviewed?: boolean;
  critique?: string;
  critiqueTags?: string[];
  geometry?: IslandGeometry;
  shape?: IslandShape;
  shapeStale?: boolean;
};

export type EvidenceLink = {
  id: string;
  type: "supports" | "contradicts";
  fromCardId: string;
  toCardId: string;
  note?: string;
  createdAt?: string;
  /** DOMAIN-EXPR-04: reversible contradiction review state */
  contradictionState?: "unconfirmed" | "confirmed" | "held" | "resolved";
};

export type A1TargetRef = `card:${string}` | `island:${string}` | `cluster:${string}` | `edge:${string}` | `proposal:${string}`;

export type CritiqueInput = {
  schemaVersion: "1.0.0";
  critiqueId: string;
  targetRef: A1TargetRef;
  critiqueType: "too_close" | "too_far" | "not_the_same" | "feels_off" | "no_articulable_reason";
  createdAt: string;
  iteration: number;
  comment?: string;
  constraintHints?: string[];
};

export type ReproposalDiffOp = {
  opId: string;
  opType: "add" | "remove" | "move" | "regroup" | "relabel";
  targetRef: A1TargetRef;
  before: Record<string, unknown> | null;
  after: Record<string, unknown> | null;
  rationale?: string;
};

export type ReproposalDiff = {
  schemaVersion: "1.0.0";
  proposalId: string;
  basedOnIteration: number;
  diffOps: ReproposalDiffOp[];
  traceKey: string;
  rationale?: string;
};

export type ReviewAttribution = {
  schemaVersion: "1.0.0";
  reviewState: "unreviewed" | "human_reviewed";
  reviewedAt: string | null;
  reviewerRef: string;
  auditRecordedAt: string;
  overridePolicy: "human_dual_control_only";
  reviewContext?: string;
  ownerRef?: string;
};

export type DeterministicTieBreak = {
  schemaVersion: "1.0.0";
  order: [
    "padding_compliance",
    "self_intersection_avoidance",
    "minimum_area_delta",
    "minimum_vertex_count",
  ];
};

export type NarrativeCheckReference = {
  id: string;
  kind: "card" | "island";
};

export type NarrativeCheckIssue = {
  severity: "info" | "warn" | "error";
  message: string;
  references?: NarrativeCheckReference[];
};

export type NarrativeCheck = {
  id: string;
  createdAt: string;
  kind: "consistency";
  issues: NarrativeCheckIssue[];
};


export type RelationSummary = {
  id: string;
  createdAt: string;
  islandAId: string;
  islandBId: string;
  relationType: KnownEdgeType | "unknown";
  derived: boolean;
  text: string;
  reviewed: boolean;
  groundingCardIds: string[];
  groundingEdgeIds: string[];
  warnings?: string[];
  sourceSignature: string;
  history?: RelationSummaryHistoryEntry[];
};

export type RelationSummaryHistoryEntry = {
  id: string;
  createdAt: string;
  changeKind: "ai" | "manual" | "rollback" | "import" | "unknown";
  fromText: string | null;
  toText: string | null;
  fromReviewed: boolean | null;
  toReviewed: boolean | null;
  warningsSnapshot?: string[];
  groundingCardIdsSnapshot?: string[];
  groundingEdgeIdsSnapshot?: string[];
  note?: string;
};

export type Narrative = {
  id: string;
  title: string;
  text: string;
  createdAt?: string;
  basedOnReadingOrder?: string[];
  reviewed: boolean;
  checks?: NarrativeCheck[];
};

export type DocumentV1 = {
  version: 1;
  id: string;
  title?: string;
  createdAt: string;
  updatedAt: string;
  transform: Transform;
  cards: Card[];
  edges: Edge[];
  islands: Island[];
  readingOrder?: string[];
  narratives?: Narrative[];
  relationSummaries?: RelationSummary[];
  evidenceLinks?: EvidenceLink[];
  patchApplyLog?: PatchApplyLogEntry[];
  mergeSuggestionDecisions?: MergeSuggestionDecisionEntry[];
  critiqueInputs?: CritiqueInput[];
  reproposalDiffs?: ReproposalDiff[];
  reviewAttribution?: ReviewAttribution;
  deterministicTieBreak?: DeterministicTieBreak;
  /** DOMAIN-EXPR-02: optional shelf — cards set aside without deletion. */
  shelf?: ShelfEntry[];
  /** DOMAIN-EXPR-04 (schemas.md §16): human review decisions on analyzeContradictions() signals. */
  contradictionSignalDecisions?: ContradictionSignalDecision[];
};

// DOMAIN-EXPR-04 (schemas.md §16): reuses CE2-PROPOSAL-IF's ProposalStatus vocabulary —
// not a new AI-authority grant. "proposed" (undecided) is never persisted; absence of an
// entry for a signatureKey IS the "proposed" state.
export type ContradictionSignalReviewStatus = "accepted" | "held" | "rejected";

export type ContradictionSignalDecision = {
  signatureKey: string;
  status: ContradictionSignalReviewStatus;
  decidedAt: string;
};

export type MergeSuggestionDecision = "accept" | "partial" | "reject" | "defer";

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

export type PatchApplyStats = {
  upsertCards: number;
  deleteCards: number;
  upsertIslands: number;
  deleteIslands: number;
  upsertEdges: number;
  deleteEdges: number;
  upsertRelationSummaries: number;
  deleteRelationSummaries: number;
  upsertEvidenceLinks: number;
  deleteEvidenceLinks: number;
};

export type PatchConflictMeta = {
  totalConflicts: number;
  chosenYours: number;
  chosenTheirs: number;
  chosenSkip: number;
};

export type PatchApplyLogEntry = {
  id: string;
  createdAt: string;
  patchVersion: "1";
  patchTitle?: string;
  baseDocSignature?: string;
  patchSourceSignature?: string;
  appliedOpIds: string[];
  stats: PatchApplyStats;
  conflictMeta?: PatchConflictMeta;
  note?: string;
};

export type Document = DocumentV1;
