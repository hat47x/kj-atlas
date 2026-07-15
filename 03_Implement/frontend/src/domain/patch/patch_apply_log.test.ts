import { describe, expect, it } from "vitest";

import { validateDocumentV1Strict } from "../validate_doc";
import type { DocumentV1 } from "../types";
import type { PatchDocument } from "./patch_apply";
import { appendPatchApplyLog } from "./patch_apply_log";

function makeDoc(): DocumentV1 {
  return {
    version: 1,
    id: "doc-1",
    createdAt: "2024-01-01T00:00:00.000Z",
    updatedAt: "2024-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [],
    edges: [],
    islands: [],
  };
}

describe("appendPatchApplyLog", () => {
  it("appends exactly one persistent log entry", () => {
    const patch: PatchDocument = {
      kind: "kj-atlas-patch",
      version: 1,
      ops: [{ id: "op-1", kind: "upsert_card", card: { id: "c1", text: "x", x: 0, y: 0 } }],
    };

    const next = appendPatchApplyLog(makeDoc(), patch, {
      appliedOpIds: ["op-1"],
      stats: {
        upsertCards: 1,
        deleteCards: 0,
        upsertIslands: 0,
        deleteIslands: 0,
        upsertEdges: 0,
        deleteEdges: 0,
        upsertRelationSummaries: 0,
        deleteRelationSummaries: 0,
        upsertEvidenceLinks: 0,
        deleteEvidenceLinks: 0,
      },
      patchTitle: "sample.patch.json",
      baseDocSignature: "doc-1:2024-01-01T00:00:00.000Z",
    });

    expect(next.patchApplyLog).toHaveLength(1);
    expect(next.patchApplyLog?.[0]?.patchVersion).toBe("1");
    expect(next.patchApplyLog?.[0]?.appliedOpIds).toEqual(["op-1"]);
    expect(next.patchApplyLog?.[0]?.patchSourceSignature?.startsWith("fnv1a:")).toBe(true);
  });

  it("survives save/reload roundtrip via strict validation", () => {
    const patch: PatchDocument = {
      kind: "kj-atlas-patch",
      version: 1,
      ops: [],
    };

    const logged = appendPatchApplyLog(makeDoc(), patch, {
      appliedOpIds: [],
      stats: {
        upsertCards: 0,
        deleteCards: 0,
        upsertIslands: 0,
        deleteIslands: 0,
        upsertEdges: 0,
        deleteEdges: 0,
        upsertRelationSummaries: 0,
        deleteRelationSummaries: 0,
        upsertEvidenceLinks: 0,
        deleteEvidenceLinks: 0,
      },
    });

    const roundTrip = JSON.parse(JSON.stringify(logged));
    const validation = validateDocumentV1Strict(roundTrip);

    expect(validation.ok).toBe(true);
    if (!validation.ok) {
      return;
    }

    expect(validation.document.patchApplyLog).toHaveLength(1);
  });
});
