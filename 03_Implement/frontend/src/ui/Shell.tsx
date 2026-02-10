import type { ReactNode } from "react";

type ShellProps = {
  title: string;
  children: ReactNode;
};

export function Shell({ title, children }: ShellProps) {
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
          padding: "0 16px",
          borderBottom: "1px solid #e2e8f0",
          backgroundColor: "#ffffff",
          color: "#0f172a",
          fontWeight: 600,
        }}
      >
        {title}
      </header>
      <main
        style={{
          flex: 1,
          minHeight: 0,
        }}
      >
        {children}
      </main>
    </div>
  );
}
