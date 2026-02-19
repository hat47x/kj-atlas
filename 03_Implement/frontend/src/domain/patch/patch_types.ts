import type { Card, Edge, EvidenceLink, Island, RelationSummary } from "../types";

export type TrustLabel = "unknown" | "trusted" | "untrusted";

export type PatchOpKind =
  | "upsert_card"
  | "delete_card"
  | "upsert_island"
  | "delete_island"
  | "upsert_edge"
  | "delete_edge"
  | "upsert_relation_summary"
  | "delete_relation_summary"
  | "upsert_evidence_link"
  | "delete_evidence_link";

export type PatchOp =
  | { id: string; kind: "upsert_card"; card: Card }
  | { id: string; kind: "delete_card"; cardId: string }
  | { id: string; kind: "upsert_island"; island: Island }
  | { id: string; kind: "delete_island"; islandId: string }
  | { id: string; kind: "upsert_edge"; edge: Edge }
  | { id: string; kind: "delete_edge"; edgeId: string }
  | { id: string; kind: "upsert_relation_summary"; relationSummary: RelationSummary }
  | { id: string; kind: "delete_relation_summary"; sourceSignature: string }
  | { id: string; kind: "upsert_evidence_link"; evidenceLink: EvidenceLink }
  | { id: string; kind: "delete_evidence_link"; evidenceLinkId: string };

export type PatchV1 = {
  kind: "kj-atlas-patch";
  version: 1;
  baseDocSignature?: string;
  author?: string;
  authorNote?: string;
  sourceApp?: string;
  patchFingerprint?: string;
  patchId?: string;
  ops: PatchOp[];
};
