import { useEffect, useRef, useState, type ChangeEvent, type KeyboardEvent } from "react";
import { t } from "../i18n/translate";
import {
  buildDiagnosticsBundle,
  DIAG_CLASSIFICATION_CODES,
  serializeDiagnosticsBundle,
  type DiagBundleDocumentInput,
  type DiagClassificationCode,
  type DiagProviderType,
} from "../export/diagnostics_bundle";

// PRODUCT-OPS-02 (ADR-0053): support diagnostics bundle. This panel is
// deliberately self-contained -- generation, preview, copy and download all
// happen here from ambient/read-only inputs (safeMode, providerType, the
// currently open document's counts). It reuses no export/review bundle
// machinery (ADR-0053 §生成契約) and never persists anything: closing or
// cancelling discards the in-memory preview.

type DiagnosticsBundlePanelProps = {
  isOpen: boolean;
  onClose: () => void;
  triggerRef: { current: HTMLElement | null };
  safeMode: boolean;
  providerType: DiagProviderType;
  documentSummary: DiagBundleDocumentInput | null;
};

const focusableSelector = [
  "button:not([disabled])",
  "a[href]",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  '[tabindex]:not([tabindex="-1"])',
].join(", ");

function getFocusableElements(root: HTMLElement): HTMLElement[] {
  return Array.from(root.querySelectorAll<HTMLElement>(focusableSelector)).filter(
    (element) => !element.hasAttribute("disabled") && element.getAttribute("aria-hidden") !== "true",
  );
}

function readAppRevision(): string | undefined {
  const env = import.meta.env as unknown as Record<string, string | undefined>;
  return env.KJ_ATLAS_APP_REVISION;
}

const fieldLabelStyle = { fontSize: 12, fontWeight: 600, color: "#334155" } as const;
const buttonStyle = {
  border: "1px solid #cbd5e1",
  borderRadius: 6,
  backgroundColor: "#ffffff",
  color: "#0f172a",
  padding: "6px 12px",
  fontWeight: 600,
  cursor: "pointer",
} as const;

export function DiagnosticsBundlePanel({
  isOpen,
  onClose,
  triggerRef,
  safeMode,
  providerType,
  documentSummary,
}: DiagnosticsBundlePanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const [classificationCode, setClassificationCode] = useState<DiagClassificationCode | "">("");
  const [httpStatusText, setHttpStatusText] = useState("");
  const [previewJson, setPreviewJson] = useState<string | null>(null);
  const [copyStatus, setCopyStatus] = useState<"idle" | "copied" | "failed">("idle");

  useEffect(() => {
    if (!isOpen || !panelRef.current) return;
    const [firstFocusable] = getFocusableElements(panelRef.current);
    (firstFocusable ?? panelRef.current).focus();
  }, [isOpen]);

  const discardAndClose = () => {
    setPreviewJson(null);
    setCopyStatus("idle");
    onClose();
    setTimeout(() => triggerRef.current?.focus(), 0);
  };

  const handlePanelKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Escape") {
      event.preventDefault();
      discardAndClose();
      return;
    }

    if (event.key !== "Tab" || !panelRef.current) {
      return;
    }

    const focusableElements = getFocusableElements(panelRef.current);
    if (focusableElements.length === 0) {
      event.preventDefault();
      panelRef.current.focus();
      return;
    }

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    if (event.shiftKey && document.activeElement === firstElement) {
      event.preventDefault();
      lastElement.focus();
      return;
    }

    if (!event.shiftKey && document.activeElement === lastElement) {
      event.preventDefault();
      firstElement.focus();
    }
  };

  const handleHttpStatusChange = (event: ChangeEvent<HTMLInputElement>) => {
    setHttpStatusText(event.target.value.replace(/[^0-9]/g, "").slice(0, 3));
  };

  const handleGenerate = () => {
    if (!classificationCode) return;

    const parsedHttpStatus = httpStatusText.trim().length > 0 ? Number(httpStatusText) : undefined;
    const bundle = buildDiagnosticsBundle({
      generatedAt: new Date().toISOString(),
      classificationCode,
      httpStatus: parsedHttpStatus,
      appRevision: readAppRevision(),
      safeMode,
      providerType,
      userAgent: typeof navigator !== "undefined" ? navigator.userAgent : undefined,
      platform: typeof navigator !== "undefined" ? navigator.platform : undefined,
      document: documentSummary ?? undefined,
    });

    setPreviewJson(serializeDiagnosticsBundle(bundle));
    setCopyStatus("idle");
  };

  const handleCopy = async () => {
    if (!previewJson) return;
    try {
      await navigator.clipboard.writeText(previewJson);
      setCopyStatus("copied");
    } catch {
      setCopyStatus("failed");
    }
  };

  const handleDownload = () => {
    if (!previewJson) return;
    const blob = new Blob([previewJson], { type: "application/json" });
    const objectUrl = URL.createObjectURL(blob);
    const downloadLink = document.createElement("a");
    downloadLink.href = objectUrl;
    downloadLink.download = `kj-atlas-diag-bundle-${Date.now()}.json`;
    document.body.appendChild(downloadLink);
    downloadLink.click();
    downloadLink.remove();
    URL.revokeObjectURL(objectUrl);
  };

  if (!isOpen) return null;

  return (
    <div
      ref={panelRef}
      data-ui-region="diagnostics-bundle"
      data-ui-complexity-tier="advanced-content"
      role="dialog"
      aria-label={t("diagnostics_bundle.title")}
      aria-modal="true"
      tabIndex={-1}
      onKeyDown={handlePanelKeyDown}
      style={{
        position: "absolute",
        inset: 0,
        zIndex: 500,
        backgroundColor: "#ffffff",
        overflow: "auto",
        padding: 16,
        display: "grid",
        gap: 12,
        alignContent: "start",
        maxWidth: 560,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ fontSize: 15, fontWeight: 800, color: "#0f172a" }}>{t("diagnostics_bundle.title")}</div>
        <button
          type="button"
          onClick={discardAndClose}
          aria-label={t("diagnostics_bundle.close")}
          data-focus-return-id="diagnostics-bundle-close"
          style={buttonStyle}
        >
          {t("diagnostics_bundle.close")}
        </button>
      </div>

      <div style={{ fontSize: 12, color: "#64748b", lineHeight: 1.5 }}>{t("diagnostics_bundle.intent_hint")}</div>

      <label style={{ display: "grid", gap: 4 }}>
        <span style={fieldLabelStyle}>{t("diagnostics_bundle.classification_label")}</span>
        <select
          data-testid="diagnostics-bundle-classification-select"
          value={classificationCode}
          onChange={(event) => {
            setClassificationCode(event.target.value as DiagClassificationCode);
            setPreviewJson(null);
            setCopyStatus("idle");
          }}
          style={{ ...buttonStyle, cursor: "pointer" }}
        >
          <option value="">{t("diagnostics_bundle.classification_placeholder")}</option>
          {DIAG_CLASSIFICATION_CODES.map((code) => (
            <option key={code} value={code}>
              {t(`diagnostics_bundle.classification.${code}`)}
            </option>
          ))}
        </select>
      </label>

      <label style={{ display: "grid", gap: 4, maxWidth: 160 }}>
        <span style={fieldLabelStyle}>{t("diagnostics_bundle.http_status_label")}</span>
        <input
          type="text"
          inputMode="numeric"
          data-testid="diagnostics-bundle-http-status-input"
          value={httpStatusText}
          onChange={handleHttpStatusChange}
          placeholder={t("diagnostics_bundle.http_status_placeholder")}
          style={{ ...buttonStyle, cursor: "text" }}
        />
      </label>

      <button
        type="button"
        data-testid="diagnostics-bundle-generate"
        disabled={!classificationCode}
        onClick={handleGenerate}
        style={{ ...buttonStyle, opacity: classificationCode ? 1 : 0.5, justifySelf: "start" }}
      >
        {t("diagnostics_bundle.generate")}
      </button>

      {previewJson ? (
        <div
          data-ui-region="diagnostics-bundle-preview"
          style={{ border: "1px solid #cbd5e1", borderRadius: 8, padding: 12, backgroundColor: "#f8fafc", display: "grid", gap: 8 }}
        >
          <div style={{ fontSize: 12, fontWeight: 700, color: "#0f172a" }}>{t("diagnostics_bundle.preview_title")}</div>
          <div style={{ fontSize: 11, color: "#64748b" }}>{t("diagnostics_bundle.excluded_categories_note")}</div>
          <textarea
            data-testid="diagnostics-bundle-preview-text"
            readOnly
            value={previewJson}
            rows={14}
            style={{
              fontFamily: "monospace",
              fontSize: 11,
              color: "#0f172a",
              backgroundColor: "#ffffff",
              border: "1px solid #e2e8f0",
              borderRadius: 6,
              padding: 8,
              resize: "vertical",
              whiteSpace: "pre",
            }}
          />
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
            <button type="button" data-testid="diagnostics-bundle-copy" onClick={handleCopy} style={buttonStyle}>
              {t("diagnostics_bundle.copy")}
            </button>
            <button type="button" data-testid="diagnostics-bundle-download" onClick={handleDownload} style={buttonStyle}>
              {t("diagnostics_bundle.download")}
            </button>
            {copyStatus === "copied" ? (
              <span role="status" aria-live="polite" style={{ fontSize: 12, color: "#166534" }}>{t("diagnostics_bundle.copied")}</span>
            ) : null}
            {copyStatus === "failed" ? (
              <span role="status" aria-live="polite" style={{ fontSize: 12, color: "#b91c1c" }}>{t("diagnostics_bundle.copy_failed")}</span>
            ) : null}
          </div>
        </div>
      ) : null}
    </div>
  );
}
