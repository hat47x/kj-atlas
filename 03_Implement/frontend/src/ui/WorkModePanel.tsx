/**
 * UX-NAV-01: Work-mode surface (ADR-0031 Area 4)
 * Hosts advanced features (diff, narrative, AI/proposal) in an
 * independent DOM region, separate from the selection-context sidebar.
 */

import { useEffect, useRef, type KeyboardEvent, type ReactNode } from "react";
import { t } from "../i18n/translate";

type WorkModePanelProps = {
  isOpen: boolean;
  onClose: () => void;
  triggerRef: { current: HTMLElement | null };
  children: ReactNode;
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

export function WorkModePanel({ isOpen, onClose, triggerRef, children }: WorkModePanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);

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

  if (!isOpen) return null;

  return (
    <div
      ref={panelRef}
      data-ui-region="work-mode"
      data-ui-complexity-tier="advanced-content"
      role="dialog"
      aria-label={t("work_mode.title")}
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
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ fontSize: 15, fontWeight: 800, color: "#0f172a" }}>
          {t("work_mode.title")}
        </div>
        <button
          type="button"
          onClick={closePanelAndRestoreFocus}
          aria-label={t("work_mode.close")}
          data-focus-return-id="work-mode-close"
          style={{
            border: "1px solid #cbd5e1",
            borderRadius: 6,
            backgroundColor: "#ffffff",
            color: "#0f172a",
            padding: "4px 12px",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          {t("work_mode.close")}
        </button>
      </div>
      {children}
    </div>
  );
}
