import type { DocumentV2 } from "./types";
import {
  INQUIRY_SCHEMA_VERSION,
  type InquiryBundleV1,
  type RoundSnapshotV1,
} from "./inquiry_journey";

const CREATED_AT = "2026-07-15T00:00:00.000Z";

function makeDocument(id: string, cards: DocumentV2["cards"]): DocumentV2 {
  return {
    version: 2,
    id,
    title: "窓口対応の待ち時間を捉え直す",
    createdAt: CREATED_AT,
    updatedAt: CREATED_AT,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards,
    edges: [],
    islands: [],
  };
}

function makeSnapshot(
  snapshotId: string,
  digestCharacter: string,
  document: DocumentV2
): RoundSnapshotV1 {
  return {
    schemaVersion: INQUIRY_SCHEMA_VERSION,
    snapshotId,
    createdAt: CREATED_AT,
    canonicalDigest: `sha256:${digestCharacter.repeat(64)}` as `sha256:${string}`,
    document,
  };
}

export function createRepresentativeInquiryBundle(): InquiryBundleV1 {
  const origin = makeSnapshot(
    "snapshot-origin",
    "a",
    makeDocument("doc-origin", [
      { id: "observation-1", text: "受付開始直後に来庁者が同じ質問を三度尋ねた", x: 40, y: 60 },
    ])
  );
  const situation = makeSnapshot(
    "snapshot-r2-1",
    "b",
    makeDocument("doc-r2-1", [
      { id: "observation-1", text: "受付開始直後に来庁者が同じ質問を三度尋ねた", x: 40, y: 60 },
      { id: "information-gap-1", text: "案内表示を見たかどうかは確認できていない", x: 260, y: 60 },
    ])
  );
  const essence = makeSnapshot(
    "snapshot-r3-1",
    "c",
    makeDocument("doc-r3-1", [
      { id: "observation-1", text: "受付開始直後に来庁者が同じ質問を三度尋ねた", x: 40, y: 60 },
      { id: "information-gap-1", text: "案内表示を見たかどうかは確認できていない", x: 260, y: 60 },
      { id: "hypothesis-1", text: "待ち時間よりも次の行動が分からないことが負担なのではないか", x: 150, y: 220, claimType: "hypothesis" },
    ])
  );
  const secondSituation = makeSnapshot(
    "snapshot-r2-2",
    "d",
    makeDocument("doc-r2-2", [
      { id: "observation-1", text: "受付開始直後に来庁者が同じ質問を三度尋ねた", x: 40, y: 60 },
      { id: "unexpected-observation-1", text: "案内表示を読んだ来庁者も受付順を尋ね直した", x: 260, y: 60 },
    ])
  );

  return {
    schemaVersion: INQUIRY_SCHEMA_VERSION,
    journey: {
      schemaVersion: INQUIRY_SCHEMA_VERSION,
      journeyId: "journey-counter-waiting",
      title: "窓口対応の待ち時間を捉え直す",
      originSnapshotIds: [origin.snapshotId],
      roundRecords: [
        {
          roundId: "round-r2-1",
          createdAt: CREATED_AT,
          updatedAt: CREATED_AT,
          stage: "r2_situation_grasp",
          iteration: 1,
          parentRoundIds: [],
          status: "handed_off",
          theme: "来庁者が待っている間に実際に何が起きているか",
          inputSnapshotIds: [origin.snapshotId],
          outputSnapshotId: situation.snapshotId,
          handoff: {
            carryoverRefs: [
              { snapshotId: situation.snapshotId, kind: "card", entityId: "observation-1" },
            ],
            heldRefs: [],
            unresolvedQuestions: ["案内表示を読んだか"],
            fieldworkRequests: [
              { requestId: "fieldwork-1", question: "質問した来庁者は案内表示をどこまで読んだか" },
            ],
            understandingDelta: "単純な混雑だけでは説明できない可能性が見えた",
          },
        },
        {
          roundId: "round-r3-1",
          createdAt: CREATED_AT,
          updatedAt: CREATED_AT,
          stage: "r3_essence_pursuit",
          iteration: 1,
          parentRoundIds: ["round-r2-1"],
          status: "handed_off",
          theme: "繰り返し質問する負担の核心は何か",
          inputSnapshotIds: [situation.snapshotId],
          outputSnapshotId: essence.snapshotId,
        },
        {
          roundId: "round-r2-2",
          createdAt: CREATED_AT,
          updatedAt: CREATED_AT,
          stage: "r2_situation_grasp",
          iteration: 2,
          parentRoundIds: ["round-r3-1"],
          status: "paused",
          theme: "案内を読んだ後にも残る不明点は何か",
          inputSnapshotIds: [essence.snapshotId],
          outputSnapshotId: secondSituation.snapshotId,
          handoff: {
            carryoverRefs: [
              { snapshotId: secondSituation.snapshotId, kind: "card", entityId: "unexpected-observation-1" },
            ],
            heldRefs: [],
            unresolvedQuestions: ["表示内容と職員説明のどちらが行動判断に影響したか"],
            fieldworkRequests: [
              {
                requestId: "fieldwork-1",
                question: "質問した来庁者は案内表示をどこまで読んだか",
                outcome: {
                  kind: "unexpected",
                  responseCardRefs: [
                    { snapshotId: secondSituation.snapshotId, cardId: "unexpected-observation-1" },
                  ],
                },
              },
            ],
          },
        },
      ],
      headRoundIds: ["round-r2-2"],
      defaultHeadRoundId: "round-r2-2",
      createdAt: CREATED_AT,
      updatedAt: CREATED_AT,
    },
    snapshots: [origin, situation, essence, secondSituation],
    cardLineage: [
      {
        lineageId: "lineage-origin-situation",
        kind: "carried",
        from: { snapshotId: origin.snapshotId, cardId: "observation-1" },
        to: { snapshotId: situation.snapshotId, cardId: "observation-1" },
      },
      {
        lineageId: "lineage-situation-essence",
        kind: "carried",
        from: { snapshotId: situation.snapshotId, cardId: "observation-1" },
        to: { snapshotId: essence.snapshotId, cardId: "observation-1" },
      },
      {
        lineageId: "lineage-hypothesis",
        kind: "derived",
        from: [
          { snapshotId: situation.snapshotId, cardId: "observation-1" },
          { snapshotId: situation.snapshotId, cardId: "information-gap-1" },
        ],
        to: { snapshotId: essence.snapshotId, cardId: "hypothesis-1" },
      },
      {
        lineageId: "lineage-second-situation",
        kind: "carried",
        from: { snapshotId: essence.snapshotId, cardId: "observation-1" },
        to: { snapshotId: secondSituation.snapshotId, cardId: "observation-1" },
      },
      {
        lineageId: "lineage-unexpected-observation",
        kind: "new",
        to: { snapshotId: secondSituation.snapshotId, cardId: "unexpected-observation-1" },
      },
    ],
  };
}
