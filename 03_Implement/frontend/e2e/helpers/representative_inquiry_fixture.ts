import type { DocumentV1 } from "../../src/domain/types";
import { ROUND_STAGES, type InquiryBundleV1 } from "../../src/domain/inquiry_journey";
import { recordInquiryRound, startInquiryJourney } from "../../src/domain/inquiry_journey_session";

export const REPRESENTATIVE_CARD_COUNT = 300;
export const REPRESENTATIVE_ISLAND_COUNT = 30;
export const REPRESENTATIVE_ROUND_COUNT = 6;

const CREATED_AT = "2026-07-18T00:00:00.000Z";

export function buildRepresentativePerformanceDocument(): DocumentV1 {
  const cards = Array.from({ length: REPRESENTATIVE_CARD_COUNT }, (_, index) => {
    const row = Math.floor(index / 20);
    const col = index % 20;
    return {
      id: `perf-card-${index + 1}`,
      text: index === 286 ? "rare performance signal 287" : `performance budget card ${index + 1}`,
      x: 100 + col * 150,
      y: 100 + row * 100,
      textReviewed: index % 4 === 0,
      claimType: index % 5 === 0 ? "hypothesis" as const : index % 3 === 0 ? "claim" as const : "fact" as const,
    };
  });
  const islands = Array.from({ length: REPRESENTATIVE_ISLAND_COUNT }, (_, index) => {
    const firstCardIndex = index * 10;
    return {
      id: `perf-island-${index + 1}`,
      title: `performance cluster ${index + 1}`,
      cardIds: cards.slice(firstCardIndex, firstCardIndex + 10).map((card) => card.id),
      shape: { kind: "rect" as const },
    };
  });
  const edges = Array.from({ length: REPRESENTATIVE_CARD_COUNT - 1 }, (_, index) => ({
    id: `perf-edge-${index + 1}`,
    fromId: `perf-card-${index + 1}`,
    toId: `perf-card-${index + 2}`,
    type: "related" as const,
  }));

  return {
    version: 1,
    id: "doc_perf_budget_01_representative",
    title: "PERF-BUDGET-01 representative document",
    createdAt: CREATED_AT,
    updatedAt: CREATED_AT,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards,
    edges,
    islands,
    readingOrder: cards.map((card) => card.id),
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

function sequentialIds(): () => string {
  let value = 0;
  return () => String(++value);
}

export async function buildRepresentativeInquiryBundle(): Promise<InquiryBundleV1> {
  const document = buildRepresentativePerformanceDocument();
  const idFactory = sequentialIds();
  let bundle = await startInquiryJourney(document, { idFactory, now: () => CREATED_AT });

  for (const [index, stage] of ROUND_STAGES.entries()) {
    const recordedAt = new Date(Date.parse(CREATED_AT) + (index + 1) * 60_000).toISOString();
    const result = await recordInquiryRound(bundle, document, stage, {
      idFactory,
      now: () => recordedAt,
    });
    if (!result.ok) throw new Error(`Could not build representative round ${index + 1}: ${result.reason}`);
    bundle = result.bundle;
  }

  return bundle;
}
