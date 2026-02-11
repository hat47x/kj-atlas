import type { ReactNode } from "react";

type ShellProps = {
  title: string;
  children: ReactNode;
  headerRight?: ReactNode;
};

export function Shell({ title, children, headerRight }: ShellProps) {
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
        <span>{title}</span>
        {headerRight ? <div>{headerRight}</div> : null}
      </header>
      <main
        style={{
          position: "relative",
          flex: 1,
          minHeight: 0,
        }}
      >
        {children}
      </main>
    </div>
  );
}
