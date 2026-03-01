import { useRef, useState, type ChangeEvent, type DragEvent } from "react";
import { t } from "../i18n/translate";

type ImportPanelProps = {
  isLoading: boolean;
  onImportZip: (file: File) => void;
  onInvalidFileType: () => void;
  packImportError: string | null;
  importedPackSummary:
    | {
        fileName: string;
        cardCount: number;
        islandCount: number;
        perspectiveMode: string;
        visibility: string;
        warningCount: number;
      }
    | null;
};

export function ImportPanel({ isLoading, onImportZip, onInvalidFileType, packImportError, importedPackSummary }: ImportPanelProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const triggerImport = (file: File | null | undefined) => {
    if (!file) {
      return;
    }

    if (!file.name.toLowerCase().endsWith(".zip")) {
      onInvalidFileType();
      return;
    }

    onImportZip(file);
  };

  const handleInputChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    event.target.value = "";
    triggerImport(selectedFile);
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
    triggerImport(event.dataTransfer.files?.[0]);
  };

  return (
    <section style={{ border: "1px solid #cbd5e1", borderRadius: 8, padding: 10, display: "grid", gap: 8 }}>
      <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{t("import.panel.title")}</div>
      <div
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => {
          setIsDragging(false);
        }}
        onDrop={handleDrop}
        style={{
          border: `1px dashed ${isDragging ? "#2563eb" : "#94a3b8"}`,
          borderRadius: 8,
          padding: 12,
          backgroundColor: isDragging ? "#eff6ff" : "#f8fafc",
          fontSize: 12,
          color: "#334155",
          textAlign: "center",
        }}
      >
        {t("import.panel.dropzone")}
      </div>
      <button
        type="button"
        onClick={() => {
          inputRef.current?.click();
        }}
        disabled={isLoading}
      >
        {t("import.panel.choose_zip")}
      </button>
      <input ref={inputRef} type="file" accept=".zip,application/zip" onChange={handleInputChange} style={{ display: "none" }} />
      {importedPackSummary ? (
        <div style={{ fontSize: 12, color: "#334155", display: "grid", gap: 4 }}>
          <div>{t("import.panel.summary", { fileName: importedPackSummary.fileName, cardCount: importedPackSummary.cardCount, islandCount: importedPackSummary.islandCount, perspectiveMode: importedPackSummary.perspectiveMode })}</div>
          <div>{`visibility: ${importedPackSummary.visibility}`}</div>
          {importedPackSummary.warningCount > 0 ? (
            <div style={{ color: "#92400e" }}>{t("import.panel.ignored_warning", { warningCount: importedPackSummary.warningCount })}</div>
          ) : null}
        </div>
      ) : null}
      {packImportError ? <div style={{ fontSize: 12, color: "#b91c1c", whiteSpace: "pre-wrap" }}>{packImportError}</div> : null}
    </section>
  );
}
