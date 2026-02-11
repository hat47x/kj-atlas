import type { ReactNode } from "react";

type ShellProps = {
  title: string;
  children: ReactNode;
  headerRight?: ReactNode;
  hasUnsavedChanges?: boolean;
  sidePanel?: ReactNode;
};

export function Shell({ title, children, headerRight, hasUnsavedChanges = false, sidePanel }: ShellProps) {
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
          height: "56px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 16px",
          borderBottom: "1px solid #e2e8f0",
          backgroundColor: "#ffffff",
          color: "#0f172a",
          fontWeight: 600,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
          }}
        >
          <span>{title}</span>
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
              Unsaved changes
            </span>
          ) : null}
        </div>
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
