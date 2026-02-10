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
};

export type EdgeType = "related";

export type Edge = {
  id: string;
  fromId: string;
  toId: string;
  type: EdgeType;
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
};
