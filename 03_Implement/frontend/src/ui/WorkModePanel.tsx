/**
 * UX-NAV-01: Work-mode surface (ADR-0031 Area 4)
 * Hosts advanced features (diff, narrative, AI/proposal) in an
 * independent DOM region, separate from the selection-context sidebar.
 */

import { useEffect, useRef, type ReactNode } from "react";
import { t } from "../i18n/translate";

type WorkModePanelProps = {
  isOpen: boolean;
  onClose: () => void;
  triggerRef: { current: HTMLElement | null };
  children: ReactNode;
};

export function WorkModePanel({ isOpen, onClose, triggerRef, children }: WorkModePanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen || !panelRef.current) return;
    const firstButton = panelRef.current.querySelector<HTMLElement>("button, [tabindex]");
    firstButton?.focus();
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
        setTimeout(() => triggerRef.current?.focus(), 0);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose, triggerRef]);

  if (!isOpen) return null;

  return (
    <div
      ref={panelRef}
      data-ui-region="work-mode"
      data-ui-complexity-tier="advanced-content"
      role="dialog"
      aria-label={t("work_mode.title")}
      aria-modal="true"
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
          onClick={() => {
            onClose();
            setTimeout(() => triggerRef.current?.focus(), 0);
          }}
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
