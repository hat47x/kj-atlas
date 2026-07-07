import { memo, useRef, useState } from "react";
import type { FocusEvent, KeyboardEvent, PointerEvent } from "react";

import type { Card } from "../domain/types";
import { t } from "../i18n/translate";

type CardDragState = {
  pointerId: number;
  lastClientX: number;
  lastClientY: number;
  didMove: boolean;
};

type CardViewProps = {
  card: Card;
  isSelected: boolean;
  isDeemphasized?: boolean;
  isHighlighted?: boolean;
  searchQuery?: string;
  isSearchMatch?: boolean;
  isActiveSearchMatch?: boolean;
  onMove: (cardId: string, deltaScreenX: number, deltaScreenY: number) => void;
  onSelect: (cardId: string, isShiftPressed: boolean) => void;
  isPickingEdgeTarget?: boolean;
  compactMode?: boolean;
  markerMode?: boolean;
  isProtectedVoice?: boolean;
  showLabelText?: boolean;
  isEditing?: boolean;
  onBeginEdit?: (cardId: string) => void;
  onCommitEdit?: (cardId: string, text: string) => void;
  onCancelEdit?: () => void;
  onCardContextMenu?: (cardId: string, clientX: number, clientY: number) => void;
};

function canStartDrag(event: PointerEvent<HTMLDivElement>): boolean {
  if (event.pointerType === "mouse") {
    return event.button === 0;
  }

  return true;
}

function renderHighlightedText(text: string, searchQuery: string): JSX.Element {
  if (!searchQuery) {
    return <>{text}</>;
  }

  const query = searchQuery.toLowerCase();
  const lowerText = text.toLowerCase();
  const parts: JSX.Element[] = [];
  let cursor = 0;
  let key = 0;

  while (cursor < text.length) {
    const foundIndex = lowerText.indexOf(query, cursor);
    if (foundIndex < 0) {
      parts.push(<span key={key}>{text.slice(cursor)}</span>);
      break;
    }

    if (foundIndex > cursor) {
      parts.push(<span key={key}>{text.slice(cursor, foundIndex)}</span>);
      key += 1;
    }

    parts.push(
      <mark
        key={key}
        style={{
          backgroundColor: "#fde68a",
          color: "inherit",
          padding: 0,
        }}
      >
        {text.slice(foundIndex, foundIndex + searchQuery.length)}
      </mark>
    );
    key += 1;
    cursor = foundIndex + searchQuery.length;
  }

  return <>{parts}</>;
}

function CardViewComponent({
  card,
  isSelected,
  searchQuery = "",
  isSearchMatch = false,
  isActiveSearchMatch = false,
  onMove,
  onSelect,
  isPickingEdgeTarget = false,
  isDeemphasized = false,
  isHighlighted = false,
  compactMode = false,
  markerMode = false,
  isProtectedVoice = false,
  showLabelText = true,
  isEditing = false,
  onBeginEdit,
  onCommitEdit,
  onCancelEdit,
  onCardContextMenu,
}: CardViewProps) {
  const dragRef = useRef<CardDragState | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const hasCritique = typeof card.critique === "string" && card.critique.trim().length > 0;
  const critiqueTagCount = card.critiqueTags?.length ?? 0;
  const claimType = card.claimType;
  const isTextReviewed = card.textReviewed === true;
  const holdState = card.holdState;
  const representativeCount = card.repOf?.length ?? 0;
  const compactText = card.text.trim().split(/\n+/).join(" ").slice(0, 72);
  // UX-VISUAL-01 AC-3 (ADR-0048 D1): even at far LOD the "needs attention"
  // signal (unreviewed / has critique) must stay discoverable, so far-view
  // markers keep an amber tint instead of the neutral slate dot.
  const markerNeedsAttention = !isTextReviewed || hasCritique;

  // Domain state badge styling (DOMAIN-EXPR-01/02)
  const CLAIM_TYPE_STYLE: Record<string, { bg: string; fg: string; label: string }> = {
    fact: { bg: "#dcfce7", fg: "#166534", label: t("card_view.claim_type.fact") },
    claim: { bg: "#dbeafe", fg: "#1e40af", label: t("card_view.claim_type.claim") },
    hypothesis: { bg: "#f3e8ff", fg: "#6b21a8", label: t("card_view.claim_type.hypothesis") },
    unknown: { bg: "#f1f5f9", fg: "#475569", label: "?" },
  };
  const HOLD_STATE_STYLE: Record<string, { bg: string; fg: string }> = {
    held: { bg: "#fef3c7", fg: "#92400e" },
    pending: { bg: "#e0e7ff", fg: "#3730a3" },
    shelved: { bg: "#f1f5f9", fg: "#64748b" },
  };
  const holdStateLabel = holdState ? t(`side_panel.hold_state.${holdState}`) : "";

  const clearDragState = (event: PointerEvent<HTMLDivElement>) => {
    dragRef.current = null;
    setIsDragging(false);

    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
  };

  const handlePointerDown = (event: PointerEvent<HTMLDivElement>) => {
    if (isEditing) {
      // While the inline text editor is open, let the textarea own pointer input
      // (do not start a card drag or change selection).
      return;
    }

    if (isPickingEdgeTarget) {
      event.stopPropagation();
      onSelect(card.id, false);
      return;
    }

    if (!canStartDrag(event)) {
      return;
    }

    event.stopPropagation();

    dragRef.current = {
      pointerId: event.pointerId,
      lastClientX: event.clientX,
      lastClientY: event.clientY,
      didMove: false,
    };
    setIsDragging(true);

    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const handlePointerMove = (event: PointerEvent<HTMLDivElement>) => {
    const drag = dragRef.current;
    if (!drag || drag.pointerId !== event.pointerId) {
      return;
    }

    event.stopPropagation();

    const deltaScreenX = event.clientX - drag.lastClientX;
    const deltaScreenY = event.clientY - drag.lastClientY;

    if (deltaScreenX === 0 && deltaScreenY === 0) {
      return;
    }

    dragRef.current = {
      ...drag,
      lastClientX: event.clientX,
      lastClientY: event.clientY,
      didMove: true,
    };

    onMove(card.id, deltaScreenX, deltaScreenY);
  };

  const handlePointerUp = (event: PointerEvent<HTMLDivElement>) => {
    const drag = dragRef.current;
    if (!drag || drag.pointerId !== event.pointerId) {
      return;
    }

    event.stopPropagation();

    if (!drag.didMove) {
      onSelect(card.id, event.shiftKey);
    }

    clearDragState(event);
  };

  const handlePointerCancel = (event: PointerEvent<HTMLDivElement>) => {
    const drag = dragRef.current;
    if (!drag || drag.pointerId !== event.pointerId) {
      return;
    }

    event.stopPropagation();
    clearDragState(event);
  };



  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      onSelect(card.id, event.shiftKey);
    }
  };

  const handleFocus = (_event: FocusEvent<HTMLDivElement>) => {
    setIsFocused(true);
  };

  const handleBlur = (_event: FocusEvent<HTMLDivElement>) => {
    setIsFocused(false);
  };

  return (
    <div
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerCancel={handlePointerCancel}
      style={{
        position: "absolute",
        left: card.x,
        top: card.y,
        width: markerMode ? 10 : 220,
        minHeight: markerMode ? 10 : compactMode ? 52 : 80,
        padding: markerMode ? 0 : compactMode ? "8px 10px" : 12,
        border: markerMode
          ? markerNeedsAttention
            ? "1px solid #f59e0b"
            : "1px solid #64748b"
          : "1px solid #cbd5e1",
        // UX-VISUAL-01 D1: 3px left band tinted by claimType (色チャネル=型)。
        borderLeft:
          !markerMode && claimType && claimType !== "unknown"
            ? `3px solid ${CLAIM_TYPE_STYLE[claimType]?.fg ?? "#cbd5e1"}`
            : undefined,
        outline: isActiveSearchMatch
          ? "3px solid #f59e0b"
          : isSelected
            ? "2px solid #2563eb"
            : isSearchMatch
              ? "2px solid #fcd34d"
              : "none",
        outlineOffset: 1,
        borderRadius: markerMode ? 999 : 8,
        backgroundColor: markerMode
          ? markerNeedsAttention
            ? "rgba(245, 158, 11, 0.45)"
            : "rgba(100, 116, 139, 0.25)"
          : "#ffffff",
        opacity: markerMode ? (markerNeedsAttention ? 0.8 : 0.4) : isDeemphasized ? 0.55 : 1,
        boxShadow: isHighlighted
          ? "0 0 0 3px rgba(245, 158, 11, 0.35), 0 0 0 1px rgba(245, 158, 11, 0.9), 0 1px 2px rgba(15, 23, 42, 0.08)"
          : isSelected
            ? "0 0 0 2px rgba(37, 99, 235, 0.2), 0 1px 2px rgba(15, 23, 42, 0.08)"
            : "0 1px 2px rgba(15, 23, 42, 0.08)",
        color: "#0f172a",
        lineHeight: compactMode ? 1.25 : 1.4,
        whiteSpace: compactMode ? "normal" : "pre-wrap",
        fontSize: compactMode ? 12 : 14,
        cursor: isPickingEdgeTarget ? "crosshair" : isDragging ? "grabbing" : "grab",
      }}
      title={
        markerMode && markerNeedsAttention
          ? t("card_view.marker_attention")
          : compactMode
            ? card.text
            : undefined
      }
      role="option"
      aria-selected={isSelected}
      data-focus={isFocused ? "card" : undefined}
      tabIndex={0}
      onKeyDown={handleKeyDown}
      onFocus={handleFocus}
      onBlur={handleBlur}
      onDoubleClick={(event) => {
        if (markerMode || !onBeginEdit) {
          return;
        }
        event.stopPropagation();
        onBeginEdit(card.id);
      }}
      onContextMenu={(event) => {
        if (markerMode || !onCardContextMenu) {
          return;
        }
        event.preventDefault();
        event.stopPropagation();
        onCardContextMenu(card.id, event.clientX, event.clientY);
      }}
    >
      {/* UX-VISUAL-01 (ADR-0048 D1): state badges live in a normal-flow meta-row
          ABOVE the body so the card body first line is never overlapped. Channels:
          色=claimType(型) / 位置=保持系(amberピル) / 密度=違和感(件数) / 形=未レビュー(右上の点)。 */}
      {!markerMode &&
      (representativeCount > 0 ||
        (claimType && claimType !== "unknown") ||
        holdState ||
        isProtectedVoice ||
        hasCritique) ? (
        <div
          data-card-meta-row=""
          style={{
            display: "flex",
            flexWrap: "wrap",
            alignItems: "center",
            gap: 4,
            marginBottom: 6,
            minHeight: 16,
          }}
        >
          {claimType && claimType !== "unknown" ? (
            <span
              aria-label={t("card_view.claim_type.aria", { value: CLAIM_TYPE_STYLE[claimType]?.label ?? claimType })}
              title={t("card_view.claim_type.title", { value: CLAIM_TYPE_STYLE[claimType]?.label ?? claimType })}
              style={{
                borderRadius: 4,
                backgroundColor: CLAIM_TYPE_STYLE[claimType]?.bg ?? "#f1f5f9",
                color: CLAIM_TYPE_STYLE[claimType]?.fg ?? "#475569",
                fontSize: 10,
                fontWeight: 600,
                padding: "1px 6px",
                lineHeight: "14px",
              }}
            >
              {CLAIM_TYPE_STYLE[claimType]?.label ?? claimType}
            </span>
          ) : null}
          {holdState ? (
            <span
              aria-label={t("card_view.hold_state.aria", { value: holdStateLabel })}
              title={t("card_view.hold_state.title", { value: holdStateLabel })}
              style={{
                borderRadius: 4,
                backgroundColor: HOLD_STATE_STYLE[holdState]?.bg ?? "#f1f5f9",
                color: HOLD_STATE_STYLE[holdState]?.fg ?? "#475569",
                fontSize: 10,
                fontWeight: 600,
                padding: "1px 6px",
                lineHeight: "14px",
              }}
            >
              {holdStateLabel}
            </span>
          ) : null}
          {representativeCount > 0 ? (
            <span
              style={{
                borderRadius: 4,
                backgroundColor: "#dbeafe",
                color: "#1d4ed8",
                fontSize: 10,
                fontWeight: 700,
                padding: "1px 6px",
                lineHeight: "14px",
              }}
            >
              {t("card_view.representative_count", { count: representativeCount })}
            </span>
          ) : null}
          {isProtectedVoice ? (
            <span
              aria-label={t("card_view.protected_voice.aria")}
              title={t("card_view.protected_voice.title")}
              style={{
                borderRadius: 4,
                border: "1px dashed #cbd5e1",
                backgroundColor: "#f8fafc",
                color: "#475569",
                fontSize: 10,
                fontWeight: 700,
                padding: "1px 6px",
                lineHeight: "14px",
              }}
            >
              {t("card_view.protected_voice.label")}
            </span>
          ) : null}
          {hasCritique ? (
            <span
              aria-label={critiqueTagCount > 0
                ? t("card_view.critique_with_tags", { count: critiqueTagCount })
                : t("card_view.critique_note")}
              title={critiqueTagCount > 0
                ? t("card_view.critique_with_tags_title", { count: critiqueTagCount })
                : t("card_view.critique_note")}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 3,
                borderRadius: 4,
                backgroundColor: "#fef3c7",
                color: "#92400e",
                fontSize: 10,
                fontWeight: 600,
                padding: "1px 6px",
                lineHeight: "14px",
              }}
            >
              <span aria-hidden="true" style={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: "#f59e0b" }} />
              {critiqueTagCount > 0 ? t("card_view.critique_tag_count", { count: critiqueTagCount }) : null}
            </span>
          ) : null}
        </div>
      ) : null}
      {!markerMode && !isTextReviewed ? (
        <span
          aria-label={t("card_view.unreviewed")}
          title={t("card_view.unreviewed")}
          style={{
            position: "absolute",
            top: 6,
            right: 6,
            width: 7,
            height: 7,
            borderRadius: "50%",
            backgroundColor: "#f59e0b",
            opacity: 0.7,
          }}
        />
      ) : null}
      {!markerMode && isEditing ? (
        <textarea
          defaultValue={card.text}
          autoFocus
          onFocus={(event) => event.currentTarget.select()}
          onPointerDown={(event) => event.stopPropagation()}
          onDoubleClick={(event) => event.stopPropagation()}
          onKeyDown={(event) => {
            event.stopPropagation();
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              onCommitEdit?.(card.id, event.currentTarget.value);
            } else if (event.key === "Escape") {
              event.preventDefault();
              onCancelEdit?.();
            }
          }}
          onBlur={(event) => onCommitEdit?.(card.id, event.currentTarget.value)}
          style={{
            width: "100%",
            minHeight: compactMode ? 36 : 56,
            boxSizing: "border-box",
            border: "none",
            outline: "none",
            resize: "none",
            padding: 0,
            margin: 0,
            fontFamily: "inherit",
            fontSize: compactMode ? 12 : 14,
            lineHeight: compactMode ? 1.25 : 1.4,
            color: "inherit",
            backgroundColor: "transparent",
          }}
        />
      ) : !markerMode && showLabelText ? (
        compactMode
          ? renderHighlightedText(compactText, searchQuery)
          : renderHighlightedText(card.text, searchQuery)
      ) : null}
    </div>
  );
}

export const CardView = memo(CardViewComponent);
