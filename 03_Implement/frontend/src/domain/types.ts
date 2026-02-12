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
  critique?: string;
  critiqueTags?: string[];
  textReviewed?: boolean;
};

export const CRITIQUE_TAGS = [
  "too_close",
  "too_far",
  "belongs_together",
  "unrelated",
  "unclear_boundary",
] as const;

export type CritiqueTag = (typeof CRITIQUE_TAGS)[number];

export type EdgeType = "related" | "negate";

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
  type: EdgeType;
};

export type Island = {
  id: string;
  cardIds: string[];
  parentIslandId?: string;
  title?: string;
  titleReviewed?: boolean;
  summaryText?: string;
  summaryReviewed?: boolean;
  imageUrl?: string;
  imageReviewed?: boolean;
  critique?: string;
  critiqueTags?: string[];
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
};

export type Document = DocumentV1 | DocumentV2;
