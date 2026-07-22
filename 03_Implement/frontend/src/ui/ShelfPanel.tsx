import { useMemo } from "react";
import type { Card, ShelfEntry } from "../domain/types";
import { t } from "../i18n/translate";

type ShelfPanelProps = {
  cards: Card[];
  shelf: ShelfEntry[];
  isReadOnly?: boolean;
  onRestoreCard?: (cardId: string) => void;
  onFocusCard?: (cardId: string) => void;
};

export function ShelfPanel({ cards, shelf, isReadOnly = false, onRestoreCard, onFocusCard }: ShelfPanelProps) {
  const shelvedCards = useMemo(() => {
    if (shelf.length === 0) return [];
    const cardMap = new Map(cards.map((c) => [c.id, c]));
    return shelf
      .map((entry) => ({
        entry,
        card: cardMap.get(entry.cardId),
      }))
      .filter((item) => item.card != null) as { entry: ShelfEntry; card: Card }[];
  }, [cards, shelf]);

  if (shelvedCards.length === 0) {
    return null;
  }

  return (
    <section
      aria-label={t("shelf_panel.title")}
      style={{
        display: "grid",
        gap: 6,
        padding: "8px 0",
        borderBottom: "1px solid #e2e8f0",
        marginBottom: 8,
      }}
    >
      <div style={{ fontSize: 12, fontWeight: 700, color: "#0f172a" }}>
        {t("shelf_panel.title")} ({shelvedCards.length})
      </div>
      <div style={{ fontSize: 11, color: "#64748b", marginBottom: 2 }}>
        {t("shelf_panel.description")}
      </div>
      {shelvedCards.map(({ entry, card }) => (
        <div
          key={entry.cardId}
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 8,
            border: "1px solid #e2e8f0",
            borderRadius: 6,
            padding: "6px 8px",
            backgroundColor: "#f8fafc",
            fontSize: 12,
          }}
        >
          <div
            style={{
              flex: "1 1 auto",
              minWidth: 0,
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
              color: "#334155",
              cursor: onFocusCard ? "pointer" : "default",
            }}
            onClick={() => onFocusCard?.(card.id)}
            role="button"
            tabIndex={onFocusCard ? 0 : undefined}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                onFocusCard?.(card.id);
              }
            }}
            title={card.text}
          >
            {card.text.trim().split("\n")[0].slice(0, 80)}
            {card.text.length > 80 ? "…" : ""}
          </div>
          {entry.reason ? (
            <div style={{ fontSize: 10, color: "#94a3b8", flex: "0 0 auto", maxWidth: 100, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={entry.reason}>
              {entry.reason}
            </div>
          ) : null}
          {onRestoreCard ? (
            <button
              type="button"
              disabled={isReadOnly}
              onClick={() => onRestoreCard(entry.cardId)}
              style={{
                flex: "0 0 auto",
                border: "1px solid #cbd5e1",
                borderRadius: 4,
                backgroundColor: "#ffffff",
                color: "#0f172a",
                fontSize: 11,
                padding: "2px 8px",
                cursor: isReadOnly ? "not-allowed" : "pointer",
              }}
            >
              {t("shelf_panel.restore")}
            </button>
          ) : null}
        </div>
      ))}
    </section>
  );
}
