import type { Card } from "./types";
import type { CardQualityFixtureKind } from "./card_quality";

export type CardQualityFixture = {
  kind: CardQualityFixtureKind;
  card: Card;
};

// Representative fixtures per qualitative_card_quality_requirements.md §7.
// These are read-only inputs for the assist state machine's tests — none of
// them carry meaning that should change which questions get queued.
export const CARD_QUALITY_FIXTURES: readonly CardQualityFixture[] = [
  {
    kind: "single_center",
    card: {
      id: "card-single-center",
      text: "受付開始直後、窓口担当者Aが来庁者から同じ質問を三度受けた。",
      x: 40,
      y: 60,
      claimType: "fact",
      meta: { source: "観察記録2026-07-10 9:03" },
    },
  },
  {
    kind: "multi_center",
    card: {
      id: "card-multi-center",
      text: "案内表示が分かりにくく、また窓口の呼び出し順が来庁者に伝わっていなかった。",
      x: 260,
      y: 60,
      claimType: "fact",
    },
  },
  {
    kind: "context_poor",
    card: {
      id: "card-context-poor",
      text: "また同じことを聞かれた。",
      x: 40,
      y: 220,
      claimType: "unknown",
    },
  },
  {
    kind: "quote_interpretation_mixed",
    card: {
      id: "card-quote-interpretation-mixed",
      text: "「番号を呼ばれても気づかない」という発言があった。つまり音声案内が弱いのだと思う。",
      x: 260,
      y: 220,
      claimType: "claim",
      meta: { source: "参加者Aへの聞き取り" },
    },
  },
  {
    kind: "minority_or_contradiction",
    card: {
      id: "card-minority-or-contradiction",
      text: "他の参加者Aとは反対に、参加者Bは案内表示だけで迷わず順番を理解できたと述べた。",
      x: 40,
      y: 380,
      claimType: "fact",
      meta: { source: "参加者Bへの聞き取り" },
      critiqueTags: ["not_the_same"],
    },
  },
  {
    kind: "unknown_source",
    card: {
      id: "card-unknown-source",
      text: "混雑時は掲示だけでは伝わりにくいという声がある。",
      x: 260,
      y: 380,
      claimType: "unknown",
    },
  },
];

export function findCardQualityFixture(kind: CardQualityFixtureKind): CardQualityFixture {
  const fixture = CARD_QUALITY_FIXTURES.find((candidate) => candidate.kind === kind);
  if (!fixture) {
    throw new Error(`missing card quality fixture: ${kind}`);
  }
  return fixture;
}
