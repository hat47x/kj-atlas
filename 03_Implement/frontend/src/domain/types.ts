export type Transform = {
  panX: number;
  panY: number;
  zoom: number;
};

export type HoldState = "held" | "pending" | "shelved";

export type Card = {
  id: string;
  text: string;
  x: number;
  y: number;
  claimType?: "fact" | "claim" | "hypothesis" | "unknown";
  mergedIntoCardId?: string;
  repOf?: string[];
  canonicalId?: string;
  sources?: string[];
  critique?: string;
  critiqueTags?: string[];
  textReviewed?: boolean;
  /** DOMAIN-EXPR-02: optional hold state. Absent = not held (conventional card). */
  holdState?: HoldState;
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

export type EdgeType = "related" | "negate";

export type EdgeEndpointKind = "card" | "island";

export type EdgeV1 = {
  id: string;
  fromId: string;
  toId: string;
  type: "related";
};

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
  relationType: "related" | "negate" | "unknown";
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
  edges: EdgeV1[];
};

export type DocumentV2 = {
  version: 2;
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

export type Document = DocumentV1 | DocumentV2;
