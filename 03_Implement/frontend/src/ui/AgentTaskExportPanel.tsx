import { useEffect, useRef, type KeyboardEvent } from "react";
import { t } from "../i18n/translate";
import { AGENT_TASK_KINDS, type AgentTaskKind } from "../export/agent_task_export";

// EXT-AGENT-01 (ADR-0049 D2): a dedicated advanced-content surface for
// exporting an AgentTaskPackage v1 task sheet, following the WorkModePanel
// precedent (its own dialog rather than more props on the already-large
// SharePanel) rather than the issue's literal "route through
// ContextQueryPreviewPanel" suggestion -- see agent_task_export.ts's header
// comment for why (CE1's /context/bundle is a closed-world mock stub, not a
// real per-document adapter). This panel's own "scope confirmed" checkbox
// plays the same gating role previewConfirmed would have.

type AgentTaskExportPanelProps = {
  isOpen: boolean;
  onClose: () => void;
  triggerRef: { current: HTMLElement | null };
  safeMode: boolean;
  selectedCardCount: number;
  selectedIslandCount: number;
  taskKind: AgentTaskKind;
  onTaskKindChange: (value: AgentTaskKind) => void;
  desiredCount: number;
  onDesiredCountChange: (value: number) => void;
  includeUnreviewedDrafts: boolean;
  onIncludeUnreviewedDraftsChange: (value: boolean) => void;
  includeSourceReferences: boolean;
  onIncludeSourceReferencesChange: (value: boolean) => void;
  scopeConfirmed: boolean;
  onScopeConfirmedChange: (value: boolean) => void;
  onCopyMarkdown: () => void;
  onDownloadMarkdown: () => void;
  onDownloadTaskJson: () => void;
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

export function AgentTaskExportPanel({
  isOpen,
  onClose,
  triggerRef,
  safeMode,
  selectedCardCount,
  selectedIslandCount,
  taskKind,
  onTaskKindChange,
  desiredCount,
  onDesiredCountChange,
  includeUnreviewedDrafts,
  onIncludeUnreviewedDraftsChange,
  includeSourceReferences,
  onIncludeSourceReferencesChange,
  scopeConfirmed,
  onScopeConfirmedChange,
  onCopyMarkdown,
  onDownloadMarkdown,
  onDownloadTaskJson,
}: AgentTaskExportPanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const hasSelection = selectedCardCount > 0 || selectedIslandCount > 0;
  const canExport = hasSelection && scopeConfirmed;

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
      data-ui-region="agent-task-export"
      data-ui-complexity-tier="advanced-content"
      role="dialog"
      aria-label={t("agent_task_export.title")}
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
        <div style={{ fontSize: 15, fontWeight: 800, color: "#0f172a" }}>{t("agent_task_export.title")}</div>
        <button
          type="button"
          onClick={closePanelAndRestoreFocus}
          aria-label={t("agent_task_export.close")}
          data-focus-return-id="agent-task-export-close"
          style={buttonStyle}
        >
          {t("agent_task_export.close")}
        </button>
      </div>

      <div style={{ fontSize: 12, color: "#64748b", lineHeight: 1.5 }}>{t("agent_task_export.intent_hint")}</div>

      <label style={{ display: "grid", gap: 4 }}>
        <span style={fieldLabelStyle}>{t("agent_task_export.task_kind_label")}</span>
        <select
          data-testid="agent-task-kind-select"
          value={taskKind}
          onChange={(event) => onTaskKindChange(event.target.value as AgentTaskKind)}
          style={{ ...buttonStyle, cursor: "pointer" }}
        >
          {AGENT_TASK_KINDS.map((kind) => (
            <option key={kind} value={kind}>
              {t(`agent_task_export.task_kind.${kind}`)}
            </option>
          ))}
        </select>
      </label>

      <label style={{ display: "grid", gap: 4, maxWidth: 160 }}>
        <span style={fieldLabelStyle}>{t("agent_task_export.desired_count_label")}</span>
        <input
          type="number"
          min={1}
          max={20}
          value={desiredCount}
          onChange={(event) => onDesiredCountChange(Math.max(1, Math.min(20, Number(event.target.value) || 1)))}
          style={{ ...buttonStyle, cursor: "text" }}
        />
      </label>

      {!safeMode ? (
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={includeUnreviewedDrafts}
            onChange={(event) => onIncludeUnreviewedDraftsChange(event.target.checked)}
          />
          {t("agent_task_export.include_unreviewed_drafts")}
        </label>
      ) : null}

      <div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={includeSourceReferences}
            onChange={(event) => onIncludeSourceReferencesChange(event.target.checked)}
          />
          {t("agent_task_export.include_source_references")}
        </label>
        {includeSourceReferences ? (
          <div style={{ fontSize: 11, color: "#9a3412", marginTop: 4 }}>{t("agent_task_export.include_source_references_warning")}</div>
        ) : null}
      </div>

      <div
        data-ui-region="agent-task-export-scope-preview"
        style={{ border: "1px solid #cbd5e1", borderRadius: 8, padding: 12, backgroundColor: "#f8fafc" }}
      >
        <div style={{ fontSize: 12, fontWeight: 700, color: "#0f172a" }}>{t("agent_task_export.scope_preview_title")}</div>
        <div style={{ fontSize: 12, color: "#334155", marginTop: 4 }}>
          {hasSelection
            ? t("agent_task_export.scope_summary_selected", { cards: selectedCardCount, islands: selectedIslandCount })
            : t("agent_task_export.scope_summary_empty")}
        </div>
        {safeMode ? (
          <div style={{ fontSize: 11, color: "#64748b", marginTop: 4 }}>{t("agent_task_export.safe_mode_note")}</div>
        ) : null}
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155", marginTop: 8 }}>
          <input
            type="checkbox"
            data-testid="agent-task-scope-confirmed"
            checked={scopeConfirmed}
            disabled={!hasSelection}
            onChange={(event) => onScopeConfirmedChange(event.target.checked)}
          />
          {t("agent_task_export.scope_confirm_label")}
        </label>
      </div>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button type="button" disabled={!canExport} onClick={onCopyMarkdown} style={{ ...buttonStyle, opacity: canExport ? 1 : 0.5 }}>
          {t("agent_task_export.copy_task_sheet")}
        </button>
        <button type="button" disabled={!canExport} onClick={onDownloadMarkdown} style={{ ...buttonStyle, opacity: canExport ? 1 : 0.5 }}>
          {t("agent_task_export.download_task_sheet")}
        </button>
        <button type="button" disabled={!canExport} onClick={onDownloadTaskJson} style={{ ...buttonStyle, opacity: canExport ? 1 : 0.5 }}>
          {t("agent_task_export.download_task_json")}
        </button>
      </div>
    </div>
  );
}
