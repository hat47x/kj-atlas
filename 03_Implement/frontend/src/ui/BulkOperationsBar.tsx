import { useRef, useState } from "react";
import { t } from "../i18n/translate";
import type { ClaimType } from "../domain/view/claim_type_checks";

export type BulkOperationsBarProps = {
  count: number;
  onToggleHold: () => void;
  onToggleCritique: () => void;
  onAddCritiqueReason: (reason: string) => void;
  onChangeClaimType: (claimType: ClaimType) => void;
  onBundleIntoIsland: () => void;
  onDelete: () => void;
};

const CLAIM_TYPES: ClaimType[] = ["fact", "claim", "hypothesis", "unknown"];

const buttonStyle: React.CSSProperties = {
  border: "1px solid #cbd5e1",
  backgroundColor: "#ffffff",
  color: "#0f172a",
  borderRadius: 6,
  padding: "6px 10px",
  fontSize: 12,
  fontWeight: 600,
  cursor: "pointer",
  whiteSpace: "nowrap",
};

// UX-SCALE-01 (b) (ADR-0048 D2, Round 5 redline): a bottom-center bar that
// appears only when 2+ cards are selected. Retention ops (hold/critique) are
// pinned leftmost per CB-2. Every button delegates to an EXISTING handler
// that already applies its change as exactly one document/history step —
// no new mutation logic beyond generalizing single-card handlers to a
// selection (bundle-into-island and delete already were selection-generic).
export function BulkOperationsBar({
  count,
  onToggleHold,
  onToggleCritique,
  onAddCritiqueReason,
  onChangeClaimType,
  onBundleIntoIsland,
  onDelete,
}: BulkOperationsBarProps) {
  const [isReasonEditorOpen, setIsReasonEditorOpen] = useState(false);
  const [reason, setReason] = useState("");
  const triggerButtonRef = useRef<HTMLButtonElement>(null);

  const closeReasonEditor = () => {
    setIsReasonEditorOpen(false);
    setReason("");
    setTimeout(() => triggerButtonRef.current?.focus(), 0);
  };

  const submitReason = () => {
    const trimmedReason = reason.trim();
    if (!trimmedReason) {
      return;
    }

    onAddCritiqueReason(trimmedReason);
    closeReasonEditor();
  };

  return (
    <div
      data-ui-region="bulk-operations-bar"
      style={{
        position: "absolute",
        left: "50%",
        bottom: 16,
        transform: "translateX(-50%)",
        zIndex: 15,
        display: "flex",
        alignItems: "center",
        gap: 8,
        padding: "8px 12px",
        borderRadius: 8,
        border: "1px solid #cbd5e1",
        backgroundColor: "rgba(255, 255, 255, 0.97)",
        boxShadow: "0 4px 16px rgba(15, 23, 42, 0.15)",
      }}
    >
      {isReasonEditorOpen ? (
        <div
          data-ui-region="bulk-critique-reason"
          role="dialog"
          aria-label={t("bulk_ops_bar.reason_editor.title")}
          onKeyDown={(event) => {
            if (event.key === "Escape") {
              event.preventDefault();
              closeReasonEditor();
            }
          }}
          style={{
            position: "absolute",
            right: 0,
            bottom: "calc(100% + 8px)",
            width: "min(320px, calc(100vw - 32px))",
            boxSizing: "border-box",
            padding: 12,
            border: "1px solid #cbd5e1",
            borderRadius: 8,
            backgroundColor: "#ffffff",
            boxShadow: "0 4px 16px rgba(15, 23, 42, 0.15)",
          }}
        >
          <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a", marginBottom: 6 }}>
            {t("bulk_ops_bar.reason_editor.title")}
          </div>
          <div style={{ fontSize: 11, lineHeight: 1.45, color: "#475569", marginBottom: 8 }}>
            {t("bulk_ops_bar.reason_editor.hint", { count })}
          </div>
          <textarea
            aria-label={t("bulk_ops_bar.reason_editor.input_label")}
            autoFocus
            value={reason}
            onChange={(event) => setReason(event.target.value)}
            onKeyDown={(event) => {
              if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
                event.preventDefault();
                submitReason();
              }
            }}
            rows={3}
            placeholder={t("bulk_ops_bar.reason_editor.placeholder")}
            style={{
              width: "100%",
              boxSizing: "border-box",
              resize: "vertical",
              border: "1px solid #cbd5e1",
              borderRadius: 6,
              padding: "6px 8px",
              fontSize: 12,
              color: "#0f172a",
            }}
          />
          <div style={{ display: "flex", justifyContent: "flex-end", gap: 6, marginTop: 8 }}>
            <button type="button" style={buttonStyle} onClick={closeReasonEditor}>
              {t("side_panel.action.cancel")}
            </button>
            <button type="button" style={buttonStyle} disabled={!reason.trim()} onClick={submitReason}>
              {t("bulk_ops_bar.reason_editor.save")}
            </button>
          </div>
        </div>
      ) : null}
      {/* design-qa conformance fix (2026-07-09): missing whiteSpace: "nowrap"
          let this be the one flex child that absorbed container squeeze by
          wrapping -- since the Japanese count text has no spaces, it wrapped
          one character per line instead of overflowing like the (nowrap)
          buttons beside it. */}
      <div role="status" aria-live="polite" style={{ fontSize: 12, color: "#334155", fontWeight: 600, paddingRight: 4, whiteSpace: "nowrap" }}>
        {t("side_panel.selection.card_multiple", { count })}
      </div>
      <button type="button" style={buttonStyle} onClick={onToggleHold}>
        {t("bulk_ops_bar.toggle_hold")}
      </button>
      <button type="button" style={buttonStyle} onClick={onToggleCritique}>
        {t("bulk_ops_bar.toggle_critique")}
      </button>
      <button
        ref={triggerButtonRef}
        type="button"
        style={buttonStyle}
        aria-expanded={isReasonEditorOpen}
        onClick={() => setIsReasonEditorOpen((open) => !open)}
      >
        {t("bulk_ops_bar.add_critique_reason")}
      </button>
      <div style={{ width: 1, alignSelf: "stretch", backgroundColor: "#e2e8f0" }} />
      <select
        style={buttonStyle}
        defaultValue=""
        aria-label={t("bulk_ops_bar.claim_type_label")}
        onChange={(event) => {
          const value = event.target.value as ClaimType | "";
          if (value) {
            onChangeClaimType(value);
          }
          event.target.value = "";
        }}
      >
        <option value="" disabled>
          {t("bulk_ops_bar.claim_type_label")}
        </option>
        {CLAIM_TYPES.map((claimType) => (
          <option key={claimType} value={claimType}>
            {t(`side_panel.claim_type.${claimType}`)}
          </option>
        ))}
      </select>
      <button type="button" style={buttonStyle} onClick={onBundleIntoIsland}>
        {t("app.toolbar.create_island")}
      </button>
      <button type="button" style={{ ...buttonStyle, borderColor: "#fecaca", color: "#991b1b" }} onClick={onDelete}>
        {t("app.toolbar.delete_selection")}
      </button>
    </div>
  );
}
