import { useEffect, useRef, type KeyboardEvent } from "react";

import { t } from "../i18n/translate";

export type InquiryEndDecision = "cancel" | "discard" | "save";

type InquiryEndConfirmationDialogProps = Readonly<{
  isProcessing?: boolean;
  onDecision: (decision: InquiryEndDecision) => void;
}>;

// DOMAIN-W-ITERATION-01 AC-13 / T10 (Claude Design P35): the destructive
// "end inquiry" action follows the same save/discard/cancel alertdialog
// pattern as A-1's TenantChangeConfirmationDialog (SafeMode default ON is
// satisfied by construction — this dialog never interpolates round/card
// content, only generic static copy).
export function InquiryEndConfirmationDialog({
  isProcessing = false,
  onDecision,
}: InquiryEndConfirmationDialogProps) {
  const dialogRef = useRef<HTMLElement>(null);
  const cancelButtonRef = useRef<HTMLButtonElement>(null);
  const processingStatusRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isProcessing) {
      processingStatusRef.current?.focus();
    } else {
      cancelButtonRef.current?.focus();
    }
  }, [isProcessing]);

  const handleKeyDown = (event: KeyboardEvent<HTMLElement>) => {
    if (event.key === "Escape" && !isProcessing) {
      event.preventDefault();
      event.stopPropagation();
      onDecision("cancel");
      return;
    }
    if (event.key !== "Tab") {
      return;
    }
    const focusableElements = [...(dialogRef.current?.querySelectorAll<HTMLElement>(
      "button:not([disabled])",
    ) ?? [])];
    if (focusableElements.length === 0) {
      event.preventDefault();
      return;
    }
    const firstElement = focusableElements[0];
    const lastElement = focusableElements.at(-1);
    if (!firstElement || !lastElement) return;
    if (event.shiftKey && document.activeElement === firstElement) {
      event.preventDefault();
      lastElement.focus();
    } else if (!event.shiftKey && document.activeElement === lastElement) {
      event.preventDefault();
      firstElement.focus();
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 1000,
        display: "grid",
        placeItems: "center",
        padding: 20,
        background: "rgba(15, 23, 42, 0.48)",
      }}
    >
      <section
        ref={dialogRef}
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="inquiry-end-confirmation-title"
        aria-describedby="inquiry-end-confirmation-description"
        onKeyDown={handleKeyDown}
        style={{
          width: "min(100%, 460px)",
          boxSizing: "border-box",
          display: "grid",
          gap: 14,
          padding: 22,
          border: "1px solid #cbd5e1",
          borderRadius: 10,
          background: "#ffffff",
          color: "#0f172a",
          boxShadow: "0 18px 42px rgba(15, 23, 42, 0.24)",
          fontFamily: "system-ui, sans-serif",
        }}
      >
        <h1
          id="inquiry-end-confirmation-title"
          style={{ margin: 0, fontSize: 20, lineHeight: 1.35 }}
        >
          {t("inquiry_journey.prototype.end_confirm_title")}
        </h1>
        <p
          id="inquiry-end-confirmation-description"
          style={{ margin: 0, color: "#475569", lineHeight: 1.65 }}
        >
          {t("inquiry_journey.prototype.end_confirm")}
        </p>
        {isProcessing ? (
          <div
            ref={processingStatusRef}
            role="status"
            aria-live="polite"
            tabIndex={-1}
            style={{ color: "#334155" }}
          >
            {t("inquiry_journey.prototype.end_confirm_processing")}
          </div>
        ) : null}
        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            gap: 8,
            flexWrap: "wrap",
          }}
        >
          <button
            ref={cancelButtonRef}
            type="button"
            disabled={isProcessing}
            onClick={() => onDecision("cancel")}
            style={{
              border: "1px solid #cbd5e1",
              borderRadius: 7,
              padding: "7px 12px",
              background: "#ffffff",
              color: "#0f172a",
              fontWeight: 600,
            }}
          >
            {t("inquiry_journey.prototype.end_cancel")}
          </button>
          <button
            type="button"
            disabled={isProcessing}
            onClick={() => onDecision("discard")}
            style={{
              border: "1px solid #b91c1c",
              borderRadius: 7,
              padding: "7px 12px",
              background: "#ffffff",
              color: "#991b1b",
              fontWeight: 600,
            }}
          >
            {t("inquiry_journey.prototype.end_confirm_action")}
          </button>
          <button
            type="button"
            disabled={isProcessing}
            onClick={() => onDecision("save")}
            style={{
              border: "1px solid #334155",
              borderRadius: 7,
              padding: "7px 12px",
              background: "#334155",
              color: "#ffffff",
              fontWeight: 600,
            }}
          >
            {t("inquiry_journey.prototype.end_confirm_save")}
          </button>
        </div>
      </section>
    </div>
  );
}
