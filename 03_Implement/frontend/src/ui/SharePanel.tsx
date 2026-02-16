import { useRef } from "react";
import type { ChangeEvent, ReactNode } from "react";

type SharePanelProps = {
  isOpen: boolean;
  onToggleOpen: () => void;
  hasDocument: boolean;
  isLoading: boolean;
  onExportSvgViewport: () => void;
  onExportSvgVisibleBounds: () => void;
  pngExportScale: 1 | 2;
  onPngExportScaleChange: (value: 1 | 2) => void;
  onExportPngViewport: () => void;
  onExportPngVisibleBounds: () => void;
  onExportAbstractMapMarkdownWithPng: () => void;
  onExportAbstractMapHtmlWithPng: () => void;
  onExportViewViewport: () => void;
  onExportViewVisibleBounds: () => void;
  onLoadViewMetadataFile: (file: File) => void;
  structuralDiffSection: ReactNode;
};

const sectionStyle = {
  display: "grid",
  gap: 8,
  paddingBottom: 10,
  marginBottom: 10,
  borderBottom: "1px solid #e2e8f0",
} as const;

export function SharePanel({
  isOpen,
  onToggleOpen,
  hasDocument,
  isLoading,
  onExportSvgViewport,
  onExportSvgVisibleBounds,
  pngExportScale,
  onPngExportScaleChange,
  onExportPngViewport,
  onExportPngVisibleBounds,
  onExportAbstractMapMarkdownWithPng,
  onExportAbstractMapHtmlWithPng,
  onExportViewViewport,
  onExportViewVisibleBounds,
  onLoadViewMetadataFile,
  structuralDiffSection,
}: SharePanelProps) {
  const viewMetadataInputRef = useRef<HTMLInputElement | null>(null);

  const handleViewMetadataFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    event.target.value = "";

    if (!selectedFile) {
      return;
    }

    onLoadViewMetadataFile(selectedFile);
  };

  return (
    <div style={{ position: "relative" }}>
      <button
        type="button"
        onClick={onToggleOpen}
        style={{
          border: "1px solid #cbd5e1",
          backgroundColor: "#ffffff",
          color: "#0f172a",
          borderRadius: 6,
          padding: "4px 10px",
          fontSize: 12,
          fontWeight: 700,
          cursor: "pointer",
        }}
      >
        Share &amp; Reproduce
      </button>
      {isOpen ? (
        <section
          style={{
            position: "absolute",
            top: "calc(100% + 8px)",
            left: 0,
            zIndex: 20,
            width: 340,
            border: "1px solid #cbd5e1",
            borderRadius: 8,
            backgroundColor: "#ffffff",
            padding: 10,
            boxShadow: "0 12px 24px rgba(15, 23, 42, 0.18)",
          }}
        >
          <div style={sectionStyle}>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>1) Export package</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>
              Export reproducible artifacts first (SVG/PNG/report + view.json metadata).
            </div>
            <button type="button" onClick={onExportSvgViewport} disabled={!hasDocument || isLoading}>
              Export SVG (Viewport)
            </button>
            <button type="button" onClick={onExportSvgVisibleBounds} disabled={!hasDocument || isLoading}>
              Export SVG (Visible bounds)
            </button>
            <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
              PNG scale
              <select
                value={String(pngExportScale)}
                onChange={(event) => {
                  onPngExportScaleChange(event.target.value === "2" ? 2 : 1);
                }}
              >
                <option value="1">1x</option>
                <option value="2">2x</option>
              </select>
            </label>
            <button type="button" onClick={onExportPngViewport} disabled={!hasDocument || isLoading}>
              Export PNG (Viewport)
            </button>
            <button type="button" onClick={onExportPngVisibleBounds} disabled={!hasDocument || isLoading}>
              Export PNG (Visible bounds)
            </button>
            <button type="button" onClick={onExportAbstractMapMarkdownWithPng} disabled={!hasDocument || isLoading}>
              Export Report (MD + PNG)
            </button>
            <button type="button" onClick={onExportAbstractMapHtmlWithPng} disabled={!hasDocument || isLoading}>
              Export Report (HTML + PNG)
            </button>
            <button type="button" onClick={onExportViewViewport} disabled={!hasDocument || isLoading}>
              Export view.json (Viewport)
            </button>
            <button type="button" onClick={onExportViewVisibleBounds} disabled={!hasDocument || isLoading}>
              Export view.json (Visible bounds)
            </button>
          </div>

          <div style={sectionStyle}>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>2) Restore view</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>Load view.json to restore camera and view toggles only.</div>
            <button
              type="button"
              onClick={() => {
                viewMetadataInputRef.current?.click();
              }}
              disabled={isLoading}
            >
              Import view.json
            </button>
            <input
              ref={viewMetadataInputRef}
              type="file"
              accept="application/json,.json"
              onChange={handleViewMetadataFileChange}
              style={{ display: "none" }}
            />
          </div>

          <div style={{ ...sectionStyle, marginBottom: 0, paddingBottom: 0, borderBottom: "none" }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>3) Diff / Verify</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>
              Structural doc diff (F3). Image diff (G2) and snapshot bundle verify (G3) remain available from legacy tools.
            </div>
            {structuralDiffSection}
          </div>
        </section>
      ) : null}
    </div>
  );
}
