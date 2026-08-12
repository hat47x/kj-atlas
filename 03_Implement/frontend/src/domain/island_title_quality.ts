/**
 * AI-TITLE-01: island-title universal-phrase inspection.
 *
 * A placard (island title) must be a one-sentence advocacy that only that
 * island's cards can bear (kj_technique.md §3). A universal phrase — one that
 * could be placed on any other island ("重要な論点", "今後の課題", …) — is a
 * classification label, not a placard, and raises rediscovery cost.
 *
 * This module implements the *inspection* logic (provider=none capable).
 * The rewrite proposal itself is AI-assisted (proposal-only), so it is
 * surfaced by the AI suggestion surface, never auto-applied.
 */

/** High-confidence universal phrases that fit any island. */
const UNIVERSAL_PHRASES: ReadonlyArray<string> = [
  "重要な論点",
  "今後の課題",
  "今後の方針",
  "技術的側面",
  "技術的な課題",
  "問題点",
  "課題と展望",
  "まとめ",
  "考察",
  "提案",
  "結論",
  "背景",
  "目的",
  "現状",
  "分析",
  "分類",
  "整理",
];

/** Strong process markers: any "Xについて" / "Xに関する" is a label even
 * when X is concrete — it names a topic, not an advocacy. */
const STRONG_PROCESS_MARKERS: ReadonlyArray<string> = ["について", "に関する"];

/** Weak markers: "Xの分析" etc. may be a placard when grounded in card
 * vocabulary, but a label when floating. */
const WEAK_PROCESS_MARKERS: ReadonlyArray<string> = [
  "の分析",
  "の整理",
  "の考察",
  "の課題",
  "のまとめ",
];

export type IslandTitleInspection = {
  /** true when the title is judged to be a universal phrase. */
  isUniversal: boolean;
  /** true when the title shares distinctive vocabulary with its cards. */
  grounded: boolean;
  /** short reason for the judgement (human-readable). */
  reason: string;
};

/**
 * Tokenize Japanese text into a small set of content tokens (ignores
 * stopwords, punctuation, kana-only particles).
 */
/** True when two tokens share a contiguous substring of >= 2 chars. */
function sharesBigram(a: string, b: string): boolean {
  if (a.length < 2 || b.length < 2) return false;
  const bigrams = new Set<string>();
  for (let i = 0; i < a.length - 1; i++) bigrams.add(a.slice(i, i + 2));
  for (let i = 0; i < b.length - 1; i++) {
    if (bigrams.has(b.slice(i, i + 2))) return true;
  }
  return false;
}

function contentTokens(text: string): Set<string> {
  // Split on punctuation/space; keep CJK word-ish tokens (2+ chars), drop
  // common particles and generic words.
  const stopwords = new Set([
    "の", "に", "は", "を", "が", "と", "で", "や", "も", "する", "ある",
    "なる", "いる", "こと", "もの", "これ", "それ", "ため", "など", "お", "て",
  ]);
  const tokens = new Set<string>();
  for (const part of text.split(/[\s、。．,.！？!?「」『』()（）・　]+/)) {
    if (part.length < 2) continue;
    if (stopwords.has(part)) continue;
    tokens.add(part);
  }
  return tokens;
}

/**
 * Inspect an island title for universal-phrase risk.
 *
 * @param title      the island title (placard) to inspect
 * @param cardTexts  the island's member card texts
 */
export function inspectIslandTitle(title: string, cardTexts: ReadonlyArray<string>): IslandTitleInspection {
  const trimmed = title.trim();

  if (!trimmed) {
    return { isUniversal: true, grounded: false, reason: "title is empty" };
  }

  // Exact match against a known universal phrase.
  if (UNIVERSAL_PHRASES.includes(trimmed)) {
    return {
      isUniversal: true,
      grounded: false,
      reason: "title matches a known universal phrase",
    };
  }

  // Strong process marker ("Xについて" / "Xに関する") is always a label —
  // it names a topic, not an advocacy, regardless of card vocabulary.
  if (STRONG_PROCESS_MARKERS.some((m) => trimmed.includes(m))) {
    return {
      isUniversal: true,
      grounded: false,
      reason: "title uses a strong process marker (について/に関する)",
    };
  }

  // Grounding first: if the title shares distinctive content vocabulary with
  // its own cards, it is a placard even when it contains a generic marker
  // (e.g. "高齢者の買い物困難" has "の" but is grounded in 高齢者/買い物).
  const titleTokens = contentTokens(trimmed);
  if (titleTokens.size === 0) {
    return { isUniversal: true, grounded: false, reason: "title has no content tokens" };
  }

  const cardTokens = new Set<string>();
  for (const cardText of cardTexts) {
    for (const t of contentTokens(cardText)) {
      cardTokens.add(t);
    }
  }

  const overlap = [...titleTokens].filter((t) => cardTokens.has(t));
  if (overlap.length > 0) {
    return {
      isUniversal: false,
      grounded: true,
      reason: "title is grounded in its cards' vocabulary",
    };
  }

  // Fallback: partial-token grounding. A title like "高齢者の買い物困難"
  // splits into one token that is a superstring of card tokens ("高齢者",
  // "買い物"). Check for a shared substring of >= 2 chars.
  const cardTokenList = [...cardTokens];
  const sharesSubstring = [...titleTokens].some((tt) =>
    cardTokenList.some((ct) => sharesBigram(tt, ct)),
  );
  if (sharesSubstring) {
    return {
      isUniversal: false,
      grounded: true,
      reason: "title shares distinctive substrings with its cards",
    };
  }

  // Not grounded: a weak marker or a floating label is universal.
  if (WEAK_PROCESS_MARKERS.some((m) => trimmed.includes(m))) {
    return {
      isUniversal: true,
      grounded: false,
      reason: "title uses a generic analysis/process marker and shares no card vocabulary",
    };
  }

  return {
    isUniversal: true,
    grounded: false,
    reason: "title shares no content vocabulary with its cards",
  };
}
