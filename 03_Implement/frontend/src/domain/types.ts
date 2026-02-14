export type Transform = {
  panX: number;
  panY: number;
  zoom: number;
};

export type Card = {
  id: string;
  text: string;
  x: number;
  y: number;
  canonicalId?: string;
  sources?: string[];
  critique?: string;
  critiqueTags?: string[];
  textReviewed?: boolean;
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
  "belongs_together",
  "unrelated",
  "unclear_boundary",
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

export type Island = {
  id: string;
  cardIds: string[];
  parentIslandId?: string;
  collapsed?: boolean;
  title?: string;
  titleReviewed?: boolean;
  summaryText?: string;
  summaryReviewed?: boolean;
  summaryGrounding?: string[];
  imageUrl?: string;
  imageReviewed?: boolean;
  critique?: string;
  critiqueTags?: string[];
  shape?: IslandShape;
  shapeStale?: boolean;
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
};

export type Document = DocumentV1 | DocumentV2;
