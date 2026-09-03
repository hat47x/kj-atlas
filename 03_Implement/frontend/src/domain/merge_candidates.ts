import type { MergeSuggestion } from "../api/client";
import type { Card, DocumentV1 } from "./types";
import { STREAM_B_CONTRACTS } from "./stream_b_contract";

export type DeterministicMergeSuggestion = MergeSuggestion & {
  targetCardId: string;
  candidateCardIds: string[];
  scoreSummary: {
    min: number;
    max: number;
    avg: number;
  };
  reasonCodes: string[];
  snapshotVersion: string;
};

type CandidateReason = "normalized-text" | "token-signature";

type CandidateGroup = {
  reason: CandidateReason;
  cards: Card[];
  score: number;
};

const TOKEN_SPLIT = /[^a-z0-9]+/g;

function normalizeText(text: string): string {
  return text
    .trim()
    .toLowerCase()
    .replace(/[-_]+/g, " ")
    .replace(/\s+/g, " ");
}

function normalizeStrictText(text: string): string {
  return normalizeText(text).replace(/[^a-z0-9 ]+/g, "").replace(/\s+/g, " ").trim();
}

function tokenSignature(text: string): string {
  const tokens = normalizeStrictText(text)
    .split(TOKEN_SPLIT)
    .map((token) => token.trim())
    .filter((token) => token.length >= 3);
  if (tokens.length === 0) {
    return "";
  }
  return [...new Set(tokens)].sort((left, right) => left.localeCompare(right)).join("|");
}

function isEligible(card: Card): boolean {
  if (card.canonicalId !== undefined) {
    return false;
  }
  if (card.mergedIntoCardId !== undefined) {
    return false;
  }
  return normalizeText(card.text).length > 0;
}

function toSuggestions(groups: CandidateGroup[]): DeterministicMergeSuggestion[] {
  return groups
    .map((group) => {
      const sortedCards = [...group.cards].sort((left, right) => left.id.localeCompare(right.id));
      const mergedTextDraft = sortedCards
        .map((card) => card.text.trim())
        .sort((left, right) => right.length - left.length || left.localeCompare(right))[0] ?? "";
      const cardIds = sortedCards.map((card) => card.id);
      const targetCardId = cardIds[0] ?? "";
      const candidateCardIds = cardIds.filter((cardId) => cardId !== targetCardId);
      return {
        groupId: `heuristic-${normalizeText(mergedTextDraft).replace(/[^a-z0-9]+/g, "-")}-${cardIds.join("-")}`,
        targetCardId,
        candidateCardIds,
        scoreSummary: {
          min: group.score,
          max: group.score,
          avg: group.score,
        },
        reasonCodes: [`heuristic:${group.reason}`],
        snapshotVersion: STREAM_B_CONTRACTS.candidateGroup.contractId,
        cardIds,
        mergedTextDraft,
        rationale: `heuristic:${group.reason}`,
      } satisfies DeterministicMergeSuggestion;
    })
    .sort((left, right) => {
      const leftKey = left.cardIds.join(",");
      const rightKey = right.cardIds.join(",");
      return leftKey.localeCompare(rightKey);
    });
}

export function collectMergeCandidates(document: DocumentV1): DeterministicMergeSuggestion[] {
  const eligibleCards = document.cards.filter(isEligible);
  if (eligibleCards.length < 2) {
    return [];
  }

  const strictBuckets = new Map<string, Card[]>();
  for (const card of eligibleCards) {
    const key = normalizeStrictText(card.text);
    if (!key) {
      continue;
    }
    const list = strictBuckets.get(key);
    if (list) {
      list.push(card);
    } else {
      strictBuckets.set(key, [card]);
    }
  }

  const assigned = new Set<string>();
  const groups: CandidateGroup[] = [];

  for (const cards of strictBuckets.values()) {
    if (cards.length < 2) {
      continue;
    }
    cards.forEach((card) => assigned.add(card.id));
    groups.push({ reason: "normalized-text", cards, score: 1 });
  }

  const tokenBuckets = new Map<string, Card[]>();
  for (const card of eligibleCards) {
    if (assigned.has(card.id)) {
      continue;
    }
    const signature = tokenSignature(card.text);
    if (!signature) {
      continue;
    }
    const list = tokenBuckets.get(signature);
    if (list) {
      list.push(card);
    } else {
      tokenBuckets.set(signature, [card]);
    }
  }

  for (const cards of tokenBuckets.values()) {
    if (cards.length < 2) {
      continue;
    }
    groups.push({ reason: "token-signature", cards, score: 0.75 });
  }

  return toSuggestions(groups);
}
