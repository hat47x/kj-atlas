import React, { useCallback, useState } from "react";
import { t } from "../i18n/translate";

export interface DocumentTitleEditorProps {
  documentTitle: string | undefined;
  islandTitles: string[];
  cardTexts: string[];
  onTitleChange: (newTitle: string) => void;
  isReadOnly: boolean;
  onSuggestTitle: (
    islandTitles: string[],
    cardTexts: string[],
    currentTitle: string | undefined,
  ) => Promise<{ candidates: { title: string }[] }>;
  providerEnabled: boolean;
}

export function DocumentTitleEditor({
  documentTitle,
  islandTitles,
  cardTexts,
  onTitleChange,
  isReadOnly,
  onSuggestTitle,
  providerEnabled,
}: DocumentTitleEditorProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(documentTitle ?? "");
  const [candidates, setCandidates] = useState<string[]>([]);
  const [isSuggesting, setIsSuggesting] = useState(false);
  const [suggestError, setSuggestError] = useState<string | null>(null);

  const handleStartEdit = useCallback(() => {
    if (isReadOnly) return;
    setEditValue(documentTitle ?? "");
    setIsEditing(true);
  }, [documentTitle, isReadOnly]);

  const handleSaveEdit = useCallback(() => {
    const trimmed = editValue.trim();
    if (trimmed && trimmed !== (documentTitle ?? "")) {
      onTitleChange(trimmed);
    }
    setIsEditing(false);
  }, [editValue, documentTitle, onTitleChange]);

  const handleCancelEdit = useCallback(() => {
    setIsEditing(false);
    setEditValue(documentTitle ?? "");
  }, [documentTitle]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter") {
        e.preventDefault();
        handleSaveEdit();
      } else if (e.key === "Escape") {
        e.preventDefault();
        handleCancelEdit();
      }
    },
    [handleSaveEdit, handleCancelEdit],
  );

  const handleSuggest = useCallback(async () => {
    if (!providerEnabled) return;
    setIsSuggesting(true);
    setSuggestError(null);
    setCandidates([]);
    try {
      const result = await onSuggestTitle(
        islandTitles,
        cardTexts,
        documentTitle,
      );
      setCandidates(result.candidates.map((c) => c.title));
    } catch (err) {
      setSuggestError(err instanceof Error ? err.message : String(err));
    } finally {
      setIsSuggesting(false);
    }
  }, [
    providerEnabled,
    islandTitles,
    cardTexts,
    documentTitle,
    onSuggestTitle,
  ]);

  const handleAdoptCandidate = useCallback(
    (candidate: string) => {
      onTitleChange(candidate);
      setCandidates([]);
      setEditValue(candidate);
    },
    [onTitleChange],
  );

  const displayTitle = documentTitle || t("document_title.untitled");

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
      {isEditing ? (
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <input
            type="text"
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            onKeyDown={handleKeyDown}
            onBlur={handleSaveEdit}
            autoFocus
            style={{
              fontSize: 16,
              fontWeight: 700,
              border: "1px solid #94a3b8",
              borderRadius: 6,
              padding: "2px 8px",
              background: "var(--bg, #fff)",
              color: "var(--fg, #0f172a)",
              minWidth: 200,
            }}
            data-testid="document-title-input"
          />
          <button
            onClick={handleSaveEdit}
            style={{
              fontSize: 12,
              padding: "2px 8px",
              borderRadius: 4,
              border: "1px solid #cbd5e1",
              background: "var(--panel, #f8fafc)",
              color: "var(--fg, #0f172a)",
              cursor: "pointer",
            }}
          >
            {t("app.toolbar.save")}
          </button>
        </div>
      ) : (
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <h1
            onClick={handleStartEdit}
            title={isReadOnly ? undefined : t("document_title.click_to_edit")}
            style={{
              margin: 0,
              fontSize: 16,
              lineHeight: 1.25,
              fontWeight: 700,
              whiteSpace: "nowrap",
              cursor: isReadOnly ? "default" : "pointer",
              borderBottom: isReadOnly ? "none" : "1px dashed transparent",
              transition: "border-color 0.15s",
            }}
            onMouseEnter={(e) => {
              if (!isReadOnly) (e.target as HTMLElement).style.borderBottomColor = "#94a3b8";
            }}
            onMouseLeave={(e) => {
              if (!isReadOnly) (e.target as HTMLElement).style.borderBottomColor = "transparent";
            }}
            data-testid="document-title-display"
          >
            {displayTitle}
          </h1>
          {!isReadOnly && providerEnabled && (
            <button
              onClick={handleSuggest}
              disabled={isSuggesting}
              style={{
                fontSize: 11,
                padding: "2px 6px",
                borderRadius: 4,
                border: "1px solid #cbd5e1",
                background: "var(--panel, #f8fafc)",
                color: "var(--fg, #0f172a)",
                cursor: isSuggesting ? "not-allowed" : "pointer",
                opacity: isSuggesting ? 0.5 : 1,
              }}
              data-testid="suggest-title-button"
            >
              {isSuggesting ? "..." : t("document_title.suggest")}
            </button>
          )}
        </div>
      )}

      {candidates.length > 0 && (
        <div
          style={{
            display: "flex",
            gap: 6,
            flexWrap: "wrap",
            justifyContent: "center",
            maxWidth: 400,
          }}
          data-testid="title-candidates"
        >
          {candidates.map((c, i) => (
            <button
              key={i}
              onClick={() => handleAdoptCandidate(c)}
              style={{
                fontSize: 12,
                padding: "3px 10px",
                borderRadius: 999,
                border: "1px solid #0f766e",
                background: "var(--panel, #f8fafc)",
                color: "#0f766e",
                cursor: "pointer",
                whiteSpace: "nowrap",
                maxWidth: 280,
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
              data-testid={`title-candidate-${i}`}
            >
              {c}
            </button>
          ))}
        </div>
      )}

      {suggestError && (
        <div style={{ fontSize: 11, color: "#b91c1c" }} data-testid="title-suggest-error">
          {suggestError}
        </div>
      )}
    </div>
  );
}
