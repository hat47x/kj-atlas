import { useEffect, useRef, type ChangeEvent, type KeyboardEvent } from "react";
import { t } from "../i18n/translate";

// ADR-0052: the File menu's recent-documents form used to render as
// `extraContent` directly inside MenuBar's role="menu" dropdown -- ARIA
// forbids non-menuitem children there (axe aria-required-children). This is
// its own dialog instead, launched from a `menuitem` ("Open recent
// document...") the same way AgentTaskExportPanel/DiagnosticsBundlePanel are
// launched from a toolbar button; only the trigger differs.

type RecentDocumentsDialogProps = {
  isOpen: boolean;
  onClose: () => void;
  triggerRef: { current: HTMLElement | null };
  recentDocumentIds: string[];
  selectedRecentDocumentId: string;
  onSelectedRecentDocumentChange: (value: string) => void;
  onOpenRecent: () => void;
  isLoading: boolean;
  activeDocumentId: string;
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

export function RecentDocumentsDialog({
  isOpen,
  onClose,
  triggerRef,
  recentDocumentIds,
  selectedRecentDocumentId,
  onSelectedRecentDocumentChange,
  onOpenRecent,
  isLoading,
  activeDocumentId,
}: RecentDocumentsDialogProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const canOpen = selectedRecentDocumentId.length > 0 && selectedRecentDocumentId !== activeDocumentId && !isLoading;

  useEffect(() => {
    if (!isOpen || !panelRef.current) return;
    const [firstFocusable] = getFocusableElements(panelRef.current);
    (firstFocusable ?? panelRef.current).focus();
  }, [isOpen]);

  const closePanelAndRestoreFocus = () => {
    onClose();
    setTimeout(() => triggerRef.current?.focus(), 0);
  };

  const handlePanelKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Escape") {
      event.preventDefault();
      closePanelAndRestoreFocus();
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

  const handleSelectChange = (event: ChangeEvent<HTMLSelectElement>) => {
    onSelectedRecentDocumentChange(event.target.value);
  };

  const handleOpenClick = () => {
    onOpenRecent();
    closePanelAndRestoreFocus();
  };

  if (!isOpen) return null;

  return (
    <div
      ref={panelRef}
      data-ui-region="recent-documents-dialog"
      role="dialog"
      aria-label={t("recent_documents_dialog.title")}
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
        maxWidth: 420,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ fontSize: 15, fontWeight: 800, color: "#0f172a" }}>{t("recent_documents_dialog.title")}</div>
        <button
          type="button"
          onClick={closePanelAndRestoreFocus}
          aria-label={t("recent_documents_dialog.close")}
          data-focus-return-id="recent-documents-dialog-close"
          style={buttonStyle}
        >
          {t("recent_documents_dialog.close")}
        </button>
      </div>

      {recentDocumentIds.length === 0 ? (
        <div style={{ fontSize: 12, color: "#64748b" }}>{t("recent_documents_dialog.empty")}</div>
      ) : (
        <>
          <label style={{ display: "grid", gap: 4 }}>
            <span style={fieldLabelStyle}>{t("app.toolbar.recent_documents")}</span>
            <select
              value={selectedRecentDocumentId}
              onChange={handleSelectChange}
              disabled={isLoading}
              style={{ ...buttonStyle, cursor: "pointer" }}
            >
              <option value="">{t("recent_documents_dialog.placeholder")}</option>
              {recentDocumentIds.map((docId) => (
                <option key={docId} value={docId}>
                  {docId}
                </option>
              ))}
            </select>
          </label>
          <button type="button" onClick={handleOpenClick} disabled={!canOpen} style={{ ...buttonStyle, opacity: canOpen ? 1 : 0.5, justifySelf: "start" }}>
            {t("app.toolbar.open")}
          </button>
        </>
      )}
    </div>
  );
}
