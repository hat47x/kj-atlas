import { t } from "../i18n/translate";

type EmptyCanvasHintProps = {
  onCreateCard: () => void;
  onOpenSample: () => void;
};

const actionButtonStyle = {
  border: "1px solid #0f766e",
  borderRadius: 6,
  backgroundColor: "#0f766e",
  color: "#ffffff",
  padding: "6px 10px",
  fontWeight: 700,
  cursor: "pointer",
} as const;

const secondaryButtonStyle = {
  border: "1px solid #cbd5e1",
  borderRadius: 6,
  backgroundColor: "#ffffff",
  color: "#0f172a",
  padding: "6px 10px",
  fontWeight: 600,
  cursor: "pointer",
} as const;

export function EmptyCanvasHint({ onCreateCard, onOpenSample }: EmptyCanvasHintProps) {
  return (
    <section
      data-ui-region="empty-canvas-hint"
      aria-live="polite"
      style={{
        position: "absolute",
        inset: "24px auto auto 24px",
        zIndex: 12,
        width: "min(360px, calc(100% - 48px))",
        border: "1px solid #cbd5e1",
        borderRadius: 8,
        backgroundColor: "rgba(255, 255, 255, 0.96)",
        boxShadow: "0 10px 20px rgba(15, 23, 42, 0.12)",
        padding: 12,
        display: "grid",
        gap: 8,
      }}
    >
      <div style={{ fontSize: 14, fontWeight: 800, color: "#0f172a" }}>{t("empty_canvas_hint.title")}</div>
      <div style={{ fontSize: 13, color: "#334155", lineHeight: 1.45 }}>{t("empty_canvas_hint.body")}</div>
      <div style={{ fontSize: 12, color: "#475569", lineHeight: 1.45 }}>{t("empty_canvas_hint.hold_note")}</div>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button type="button" onClick={onCreateCard} style={actionButtonStyle}>
          {t("empty_canvas_hint.create_card")}
        </button>
        <button type="button" onClick={onOpenSample} style={secondaryButtonStyle}>
          {t("empty_canvas_hint.open_sample")}
        </button>
      </div>
    </section>
  );
}
