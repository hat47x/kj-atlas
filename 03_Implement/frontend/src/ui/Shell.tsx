import type { ReactNode } from "react";
import { t } from "../i18n/translate";

type ShellProps = {
  title: string;
  subtitle?: ReactNode;
  children: ReactNode;
  headerViewControls?: ReactNode;
  headerShareControls?: ReactNode;
  headerCenter?: ReactNode;
  headerRight?: ReactNode;
  hasUnsavedChanges?: boolean;
  saveConflictMessage?: string;
  onReloadAfterConflict?: () => void;
  onExportAfterConflict?: () => void;
  isReloadingAfterConflict?: boolean;
  sidePanel?: ReactNode;
};

export function Shell({
  title,
  subtitle,
  children,
  headerViewControls,
  headerShareControls,
  headerCenter,
  headerRight,
  hasUnsavedChanges = false,
  saveConflictMessage,
  onReloadAfterConflict,
  onExportAfterConflict,
  isReloadingAfterConflict = false,
  sidePanel,
}: ShellProps) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        width: "100vw",
        overflow: "hidden",
        fontFamily: "Inter, system-ui, -apple-system, Segoe UI, sans-serif",
      }}
    >
      <header
        style={{
          minHeight: "56px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "8px 16px",
          borderBottom: "1px solid #e2e8f0",
          backgroundColor: "#ffffff",
          color: "#0f172a",
          fontWeight: 600,
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 4, minWidth: 0 }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
            }}
          >
            <span style={{ whiteSpace: "nowrap" }}>{title}</span>
            {hasUnsavedChanges ? (
              <span
                style={{
                  fontSize: 12,
                  color: "#92400e",
                  backgroundColor: "#fef3c7",
                  border: "1px solid #fde68a",
                  borderRadius: 999,
                  padding: "2px 8px",
                  fontWeight: 600,
                }}
              >
                {t("shell.unsaved_changes")}
              </span>
            ) : null}
            {headerViewControls ? <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap" }}>{headerViewControls}</div> : null}
            {headerShareControls ? <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap" }}>{headerShareControls}</div> : null}
          </div>
          {subtitle ? <div style={{ fontSize: 12, color: "#475569", fontWeight: 500 }}>{subtitle}</div> : null}
          {saveConflictMessage ? (
            <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
              <span
                style={{
                  fontSize: 12,
                  color: "#991b1b",
                  backgroundColor: "#fee2e2",
                  border: "1px solid #fecaca",
                  borderRadius: 6,
                  padding: "2px 8px",
                }}
              >
                {saveConflictMessage}
              </span>
              {onReloadAfterConflict ? (
                <button
                  type="button"
                  onClick={onReloadAfterConflict}
                  disabled={isReloadingAfterConflict}
                  style={{
                    border: "1px solid #cbd5e1",
                    backgroundColor: "#ffffff",
                    color: "#0f172a",
                    borderRadius: 6,
                    padding: "4px 10px",
                    fontWeight: 600,
                    cursor: isReloadingAfterConflict ? "not-allowed" : "pointer",
                  }}
                >
                  {isReloadingAfterConflict ? t("shell.reloading") : t("shell.reload")}
                </button>
              ) : null}
              {onExportAfterConflict ? (
                <button
                  type="button"
                  onClick={onExportAfterConflict}
                  style={{
                    border: "1px solid #cbd5e1",
                    backgroundColor: "#ffffff",
                    color: "#0f172a",
                    borderRadius: 6,
                    padding: "4px 10px",
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                >
                  {t("shell.export_json")}
                </button>
              ) : null}
            </div>
          ) : null}
        </div>
        {headerCenter ? (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", flex: 1, padding: "0 16px" }}>
            {headerCenter}
          </div>
        ) : (
          <div style={{ flex: 1 }} />
        )}
        {headerRight ? (
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>{headerRight}</div>
        ) : null}
      </header>
      <main
        style={{
          display: "flex",
          flex: 1,
          minHeight: 0,
        }}
      >
        <div
          style={{
            position: "relative",
            flex: 1,
            minWidth: 0,
            minHeight: 0,
          }}
        >
          {children}
        </div>
        {sidePanel}
      </main>
    </div>
  );
}
