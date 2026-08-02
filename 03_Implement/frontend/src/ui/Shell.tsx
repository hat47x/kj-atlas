import { useLayoutEffect, useRef, useState, type CSSProperties, type ReactNode } from "react";
import { t } from "../i18n/translate";

const headerPanelGapPx = 8;

type ShellProps = {
  title: string;
  subtitle?: ReactNode;
  children: ReactNode;
  headerViewControls?: ReactNode;
  headerShareControls?: ReactNode;
  headerCenter?: ReactNode;
  headerRight?: ReactNode;
  menuBar?: ReactNode;
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
  menuBar,
  hasUnsavedChanges = false,
  saveConflictMessage,
  onReloadAfterConflict,
  onExportAfterConflict,
  isReloadingAfterConflict = false,
  sidePanel,
}: ShellProps) {
  const headerRef = useRef<HTMLElement | null>(null);
  const [headerPanelTop, setHeaderPanelTop] = useState(72);

  useLayoutEffect(() => {
    const updateHeaderPanelTop = () => {
      const rect = headerRef.current?.getBoundingClientRect();
      if (!rect) {
        return;
      }

      const nextTop = Math.ceil(rect.bottom + headerPanelGapPx);
      setHeaderPanelTop((previousTop) => (previousTop === nextTop ? previousTop : nextTop));
    };

    updateHeaderPanelTop();

    const headerElement = headerRef.current;
    let resizeObserver: ResizeObserver | undefined;
    if (typeof ResizeObserver !== "undefined" && headerElement) {
      resizeObserver = new ResizeObserver(updateHeaderPanelTop);
      resizeObserver.observe(headerElement);
    }
    window.addEventListener("resize", updateHeaderPanelTop);

    return () => {
      resizeObserver?.disconnect();
      window.removeEventListener("resize", updateHeaderPanelTop);
    };
  }, []);

  const shellStyle: CSSProperties & { "--kj-atlas-header-panel-top": string } = {
    display: "flex",
    flexDirection: "column",
    height: "100vh",
    width: "100vw",
    overflow: "hidden",
    fontFamily: "Inter, system-ui, -apple-system, Segoe UI, sans-serif",
    "--kj-atlas-header-panel-top": `${headerPanelTop}px`,
  };

  return (
    <div style={shellStyle}>
      <header
        ref={headerRef}
        style={{
          minHeight: "56px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "8px 12px",
          padding: "8px 16px",
          borderBottom: "1px solid #e2e8f0",
          backgroundColor: "#ffffff",
          color: "#0f172a",
          fontWeight: 600,
          overflow: "visible",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 4, minWidth: 280, flex: "0 1 auto" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              flexWrap: "wrap",
              rowGap: 6,
            }}
          >
            <h1 style={{ margin: 0, fontSize: 16, lineHeight: 1.25, fontWeight: 700, whiteSpace: "nowrap" }}>{title}</h1>
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
            {headerViewControls ? <div style={{ display: "flex", alignItems: "center", flexWrap: "nowrap", whiteSpace: "nowrap" }}>{headerViewControls}</div> : null}
            {headerShareControls ? (
              <div
                data-ui-complexity-tier="core-share"
                style={{ display: "flex", alignItems: "center", flexWrap: "nowrap", whiteSpace: "nowrap" }}
              >
                {headerShareControls}
              </div>
            ) : null}
          </div>
          {subtitle ? <div style={{ fontSize: 12, color: "#475569", fontWeight: 500 }}>{subtitle}</div> : null}
          {saveConflictMessage ? (
            <div style={{ display: "flex", alignItems: "center", justifyContent: "flex-end", gap: 8, flexWrap: "wrap", flex: "1 1 520px", minWidth: 320 }}>
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
          <div
            data-ui-region="header-center"
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "flex-start",
              flex: "1 1 360px",
              minWidth: 0,
              maxWidth: 520,
              padding: "0 4px",
            }}
          >
            {headerCenter}
          </div>
        ) : (
          <div style={{ flex: "1 1 320px" }} />
        )}
        {headerRight ? (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "flex-start",
              gap: 8,
              flexWrap: "wrap",
              flex: "1 1 520px",
              minWidth: 0,
              overflowX: "visible",
              overflowY: "visible",
              paddingBottom: 2,
              whiteSpace: "nowrap",
            }}
          >
            {headerRight}
          </div>
        ) : null}
        {menuBar ? (
          <div data-ui-region="menu-bar-row" style={{ flexBasis: "100%", display: "flex" }}>
            {menuBar}
          </div>
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
