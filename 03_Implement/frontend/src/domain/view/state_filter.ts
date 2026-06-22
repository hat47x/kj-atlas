import type { Card, DocumentV2 } from "../types";

// DOMAIN-EXPR-01: 既存ドメイン状態（reviewState / evidence / critique）で
// カードを絞り込む純粋関数。React 非依存・read-only・schema非依存。
//
// 設計境界（architecture.md §3.3）: Canvas Engine 同様、判定ロジックは
// React へ依存しない純モジュールとして実装し、UI 側は結果集合のみ受け取る。

export type DomainStateFilterKind = "unreviewed" | "no_evidence" | "has_critique";

export type DomainStateFilter = {
  // 空集合のときはフィルタ無効（全カードが対象）。
  active: Set<DomainStateFilterKind>;
};

export const ALL_DOMAIN_STATE_FILTER_KINDS: readonly DomainStateFilterKind[] = [
  "unreviewed",
  "no_evidence",
  "has_critique",
] as const;

export function createEmptyDomainStateFilter(): DomainStateFilter {
  return { active: new Set() };
}

export function toggleDomainStateFilter(
  filter: DomainStateFilter,
  kind: DomainStateFilterKind,
): DomainStateFilter {
  const next = new Set(filter.active);
  if (next.has(kind)) {
    next.delete(kind);
  } else {
    next.add(kind);
  }
  return { active: next };
}

export function isDomainStateFilterActive(filter: DomainStateFilter): boolean {
  return filter.active.size > 0;
}

// 1枚のカードが、ある状態種別に該当するか（read-only 判定）。
function cardHasNoEvidence(card: Card, evidenceCardIds: ReadonlySet<string>): boolean {
  return !evidenceCardIds.has(card.id);
}

function cardIsUnreviewed(card: Card): boolean {
  return card.textReviewed !== true;
}

function cardHasCritique(card: Card): boolean {
  return (card.critique?.trim().length ?? 0) > 0 || (card.critiqueTags?.length ?? 0) > 0;
}

// document.evidenceLinks に from/to いずれかで現れるカードIDの集合。
export function collectCardIdsWithEvidence(document: DocumentV2): Set<string> {
  const ids = new Set<string>();
  for (const link of document.evidenceLinks ?? []) {
    ids.add(link.fromCardId);
    ids.add(link.toCardId);
  }
  return ids;
}

// AND セマンティクス: 選択された全種別を満たすカードのみ返す。
// フィルタ無効時は全カードIDを返す（呼び出し側で「絞り込みなし」と解釈できる）。
export function selectCardIdsByDomainState(
  document: DocumentV2,
  filter: DomainStateFilter,
): Set<string> {
  if (!isDomainStateFilterActive(filter)) {
    return new Set(document.cards.map((card) => card.id));
  }

  const evidenceCardIds = collectCardIdsWithEvidence(document);
  const matched = new Set<string>();

  for (const card of document.cards) {
    let ok = true;
    if (filter.active.has("unreviewed") && !cardIsUnreviewed(card)) {
      ok = false;
    }
    if (ok && filter.active.has("no_evidence") && !cardHasNoEvidence(card, evidenceCardIds)) {
      ok = false;
    }
    if (ok && filter.active.has("has_critique") && !cardHasCritique(card)) {
      ok = false;
    }
    if (ok) {
      matched.add(card.id);
    }
  }

  return matched;
}
