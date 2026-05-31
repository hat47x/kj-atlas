import { useRef } from "react";
import type { ChangeEvent } from "react";
import { t } from "../i18n/translate";
import { getSafeModeIndicator } from "./safe_mode_status";

type StartPanelProps = {
  isOpen: boolean;
  safeMode: boolean;
  isLoading: boolean;
  isSaving: boolean;
  hasDocument: boolean;
  onClose: () => void;
  onCreateDocument: () => void;
  onOpenSampleDocument: () => void;
  onLoadDocumentFile: (file: File) => void;
  onImportReviewPackFile: (file: File) => void;
};

const actionButtonStyle = {
  border: "1px solid #cbd5e1",
  backgroundColor: "#ffffff",
  color: "#0f172a",
  borderRadius: 6,
  padding: "8px 10px",
  fontWeight: 700,
  cursor: "pointer",
  textAlign: "left" as const,
  width: "100%",
};

const mutedTextStyle = {
  fontSize: 12,
  lineHeight: 1.5,
  color: "#475569",
};

export function StartPanel({
  isOpen,
  safeMode,
  isLoading,
  isSaving,
  hasDocument,
  onClose,
  onCreateDocument,
  onOpenSampleDocument,
  onLoadDocumentFile,
  onImportReviewPackFile,
}: StartPanelProps) {
  const documentInputRef = useRef<HTMLInputElement | null>(null);
  const reviewPackInputRef = useRef<HTMLInputElement | null>(null);
  const safeModeIndicator = getSafeModeIndicator(safeMode);
  const isBusy = isLoading || isSaving;

  if (!isOpen) {
    return null;
  }

  const handleDocumentFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }
    onLoadDocumentFile(file);
    onClose();
  };

  const handleReviewPackFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }
    onImportReviewPackFile(file);
    onClose();
  };

  return (
    <section
      data-ui-region="start-panel"
      aria-label={t("start_panel.title")}
      style={{
        position: "absolute",
        top: 16,
        right: 16,
        zIndex: 20,
        width: "min(380px, calc(100% - 32px))",
        maxHeight: "calc(100% - 32px)",
        overflowY: "auto",
        border: "1px solid #cbd5e1",
        borderRadius: 8,
        backgroundColor: "#ffffff",
        boxShadow: "0 16px 36px rgba(15, 23, 42, 0.14)",
        padding: 14,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "flex-start" }}>
        <div>
          <div style={{ fontSize: 13, color: "#475569", fontWeight: 700 }}>{t("start_panel.eyebrow")}</div>
          <h2 style={{ fontSize: 18, lineHeight: 1.3, margin: "2px 0 4px", color: "#0f172a" }}>
            {t("start_panel.title")}
          </h2>
          <div style={mutedTextStyle}>{t("start_panel.description")}</div>
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label={t("start_panel.close")}
          style={{
            border: "1px solid #cbd5e1",
            backgroundColor: "#ffffff",
            color: "#0f172a",
            borderRadius: 6,
            padding: "4px 8px",
            fontSize: 12,
            fontWeight: 700,
            cursor: "pointer",
            flex: "0 0 auto",
          }}
        >
          {t("start_panel.close")}
        </button>
      </div>

      <div
        style={{
          marginTop: 12,
          display: "grid",
          gap: 8,
        }}
      >
        <button
          type="button"
          onClick={() => {
            onCreateDocument();
            onClose();
          }}
          disabled={isBusy}
          style={{
            ...actionButtonStyle,
            cursor: isBusy ? "not-allowed" : "pointer",
            opacity: isBusy ? 0.6 : 1,
          }}
        >
          <span style={{ display: "block" }}>{t("start_panel.action.new")}</span>
          <span style={{ ...mutedTextStyle, display: "block", fontWeight: 500 }}>
            {t("start_panel.action.new_hint")}
          </span>
        </button>
        <button
          type="button"
          onClick={() => {
            onOpenSampleDocument();
            onClose();
          }}
          disabled={isBusy}
          style={{
            ...actionButtonStyle,
            cursor: isBusy ? "not-allowed" : "pointer",
            opacity: isBusy ? 0.6 : 1,
          }}
        >
          <span style={{ display: "block" }}>{t("start_panel.action.sample")}</span>
          <span style={{ ...mutedTextStyle, display: "block", fontWeight: 500 }}>
            {hasDocument ? t("start_panel.action.sample_hint_loaded") : t("start_panel.action.sample_hint")}
          </span>
        </button>
        <button
          type="button"
          onClick={() => documentInputRef.current?.click()}
          disabled={isBusy}
          style={{
            ...actionButtonStyle,
            cursor: isBusy ? "not-allowed" : "pointer",
            opacity: isBusy ? 0.6 : 1,
          }}
        >
          <span style={{ display: "block" }}>{t("start_panel.action.load_document")}</span>
          <span style={{ ...mutedTextStyle, display: "block", fontWeight: 500 }}>
            {t("start_panel.action.load_document_hint")}
          </span>
        </button>
        <input
          ref={documentInputRef}
          type="file"
          accept=".json,application/json"
          onChange={handleDocumentFileChange}
          style={{ display: "none" }}
        />
        <button
          type="button"
          onClick={() => reviewPackInputRef.current?.click()}
          disabled={isBusy}
          style={{
            ...actionButtonStyle,
            cursor: isBusy ? "not-allowed" : "pointer",
            opacity: isBusy ? 0.6 : 1,
          }}
        >
          <span style={{ display: "block" }}>{t("start_panel.action.import_pack")}</span>
          <span style={{ ...mutedTextStyle, display: "block", fontWeight: 500 }}>
            {t("start_panel.action.import_pack_hint")}
          </span>
        </button>
        <input
          ref={reviewPackInputRef}
          type="file"
          accept=".zip,application/zip"
          onChange={handleReviewPackFileChange}
          style={{ display: "none" }}
        />
      </div>

      <div
        style={{
          marginTop: 12,
          borderTop: "1px solid #e2e8f0",
          paddingTop: 10,
          display: "grid",
          gap: 4,
        }}
      >
        <div style={{ fontSize: 12, fontWeight: 800, color: safeModeIndicator.tone === "safe" ? "#166534" : "#9a3412" }}>
          {t("start_panel.safe_mode_label", { state: safeModeIndicator.label })}
        </div>
        <div style={mutedTextStyle}>{t("start_panel.safe_mode_hint")}</div>
      </div>
    </section>
  );
}
