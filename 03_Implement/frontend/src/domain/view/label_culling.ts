export type LabelKind = "islandTitle" | "islandSummary" | "unreviewed" | "card";

export type LabelItem = {
  id: string;
  kind: LabelKind;
  priority: number;
  rect: { x: number; y: number; w: number; h: number };
  text?: string;
  payload: { islandId?: string; cardId?: string };
};

export type LabelCullingResult = {
  accepted: LabelItem[];
  culled: LabelItem[];
  acceptedIds: Set<string>;
};

export const LABEL_PRIORITIES: Record<LabelKind, number> = {
  islandTitle: 100,
  unreviewed: 90,
  islandSummary: 70,
  card: 30,
};

// QA-MONKEY-10: a card the user is actively working with (selected or being
// edited) must never lose its text to overlap culling -- freshly typed text
// disappearing reads as data loss. Above islandSummary so the active card's
// own words win against a nearby summary, but below the unreviewed badge and
// island title, which are safety/orientation signals.
export const ACTIVE_CARD_LABEL_PRIORITY = 80;

export function buildIslandTitleLabelId(islandId: string): string {
  return `island:${islandId}:title`;
}

export function buildIslandSummaryLabelId(islandId: string): string {
  return `island:${islandId}:summary`;
}

export function buildIslandUnreviewedLabelId(islandId: string): string {
  return `island:${islandId}:unreviewed`;
}

export function buildCardLabelId(cardId: string): string {
  return `card:${cardId}:label`;
}

function intersects(a: LabelItem["rect"], b: LabelItem["rect"]): boolean {
  return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

export function cullLabels(items: LabelItem[]): LabelCullingResult {
  const sorted = [...items].sort((a, b) => {
    if (b.priority !== a.priority) {
      return b.priority - a.priority;
    }

    if (a.id < b.id) {
      return -1;
    }
    if (a.id > b.id) {
      return 1;
    }
    return 0;
  });

  const accepted: LabelItem[] = [];
  const culled: LabelItem[] = [];

  for (const item of sorted) {
    const collides = accepted.some((acceptedItem) => intersects(item.rect, acceptedItem.rect));
    if (collides) {
      culled.push(item);
      continue;
    }

    accepted.push(item);
  }

  return {
    accepted,
    culled,
    acceptedIds: new Set(accepted.map((item) => item.id)),
  };
}
