import type { Card, DocumentV1 } from "../types";

export type DomainStateFilterKind = "unreviewed" | "no_evidence" | "has_critique";

export type DomainStateFilter = {
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

function cardHasCritique(card: Card): boolean {
  return (card.critique?.trim().length ?? 0) > 0 || (card.critiqueTags?.length ?? 0) > 0;
}

export function collectCardIdsWithEvidence(document: DocumentV1): Set<string> {
  const ids = new Set<string>();
  for (const link of document.evidenceLinks ?? []) {
    ids.add(link.fromCardId);
    ids.add(link.toCardId);
  }
  return ids;
}

export function selectCardIdsByDomainState(
  document: DocumentV1,
  filter: DomainStateFilter,
): Set<string> {
  if (!isDomainStateFilterActive(filter)) {
    return new Set(document.cards.map((card) => card.id));
  }

  const evidenceCardIds = collectCardIdsWithEvidence(document);
  return new Set(document.cards.filter((card) => {
    if (filter.active.has("unreviewed") && card.textReviewed === true) {
      return false;
    }
    if (filter.active.has("no_evidence") && evidenceCardIds.has(card.id)) {
      return false;
    }
    if (filter.active.has("has_critique") && !cardHasCritique(card)) {
      return false;
    }
    return true;
  }).map((card) => card.id));
}
