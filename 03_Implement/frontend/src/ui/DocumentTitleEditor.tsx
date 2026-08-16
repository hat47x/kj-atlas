import React, { useCallback, useRef, useState } from "react";
import type { AvailableModelItem } from "../api/client";
import { t } from "../i18n/translate";
import { ModelSelector } from "./ModelSelector";

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
  modelSelectionVisible: boolean;
  // AI-MODEL-GOVERNANCE-01 (R2): per-operation model override ("" = auto).
  documentTitleModel: string;
  onDocumentTitleModelChange: (model: string) => void;
  availableModels: AvailableModelItem[] | null;
}

export function DocumentTitleEditor({
  documentTitle,
  islandTitles,
  cardTexts,
  onTitleChange,
  isReadOnly,
  onSuggestTitle,
  providerEnabled,
  modelSelectionVisible,
  documentTitleModel,
  onDocumentTitleModelChange,
  availableModels,
}: DocumentTitleEditorProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(documentTitle ?? "");
  const [candidates, setCandidates] = useState<string[]>([]);
  const [isSuggesting, setIsSuggesting] = useState(false);
  const [suggestError, setSuggestError] = useState<string | null>(null);
  const titleDisplayRef = useRef<HTMLButtonElement | null>(null);
  const suggestButtonRef = useRef<HTMLButtonElement | null>(null);

  const focusTitleDisplay = useCallback(() => {
    window.requestAnimationFrame(() => titleDisplayRef.current?.focus());
  }, []);

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
        focusTitleDisplay();
      } else if (e.key === "Escape") {
        e.preventDefault();
        handleCancelEdit();
        focusTitleDisplay();
      }
    },
    [focusTitleDisplay, handleSaveEdit, handleCancelEdit],
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
      focusTitleDisplay();
    },
    [focusTitleDisplay, onTitleChange],
  );

  const handleDismissCandidates = useCallback(() => {
    setCandidates([]);
    window.requestAnimationFrame(() => suggestButtonRef.current?.focus());
  }, []);

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
          <h1 style={{ margin: 0, fontSize: 16, lineHeight: 1.25, fontWeight: 700, whiteSpace: "nowrap" }}>
            {isReadOnly ? (
              <span data-testid="document-title-display">{displayTitle}</span>
            ) : (
              <button
                ref={titleDisplayRef}
                type="button"
                onClick={handleStartEdit}
                title={t("document_title.click_to_edit")}
                aria-label={t("document_title.edit_aria", { title: displayTitle })}
                style={{
                  background: "transparent",
                  border: 0,
                  padding: 0,
                  font: "inherit",
                  color: "inherit",
                  cursor: "pointer",
                  borderBottom: "1px dashed transparent",
                  transition: "border-color 0.15s",
                }}
                onMouseEnter={(event) => {
                  event.currentTarget.style.borderBottomColor = "#94a3b8";
                }}
                onMouseLeave={(event) => {
                  event.currentTarget.style.borderBottomColor = "transparent";
                }}
                data-testid="document-title-display"
              >
                {displayTitle}
              </button>
            )}
          </h1>
          {!isReadOnly && modelSelectionVisible && (
            <ModelSelector
              label={t("model_selector.label")}
              value={documentTitleModel}
              onChange={onDocumentTitleModelChange}
              disabled={isSuggesting}
              dataUiRegion="model-selector-title"
              models={availableModels}
            />
          )}
          {!isReadOnly && providerEnabled && (
            <button
              ref={suggestButtonRef}
              onClick={handleSuggest}
              disabled={isSuggesting}
              aria-label={isSuggesting ? t("document_title.suggesting") : t("document_title.suggest")}
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
              {isSuggesting ? t("document_title.suggesting") : t("document_title.suggest")}
            </button>
          )}
        </div>
      )}

      {candidates.length > 0 && (
        <div
          role="region"
          aria-labelledby="document-title-candidates-label"
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 6,
            justifyContent: "center",
            maxWidth: 400,
          }}
          data-testid="title-candidates"
        >
          <div id="document-title-candidates-label" style={{ fontSize: 12, fontWeight: 700 }}>
            {t("document_title.candidates_label")}
          </div>
          <div role="status" aria-live="polite" style={{ fontSize: 11, color: "#475569" }}>
            {t("document_title.candidates_ready", { count: candidates.length })}
          </div>
          <div style={{ fontSize: 11, color: "#475569", textAlign: "center" }}>
            {t("document_title.proposal_only_hint")}
          </div>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", justifyContent: "center" }}>
            {candidates.map((candidate, index) => (
              <button
                key={`${candidate}-${index}`}
                onClick={() => handleAdoptCandidate(candidate)}
                aria-label={t("document_title.adopt_candidate", { title: candidate })}
                title={candidate}
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
                data-testid={`title-candidate-${index}`}
              >
                {candidate}
              </button>
            ))}
          </div>
          <button type="button" onClick={handleDismissCandidates} style={{ fontSize: 11 }}>
            {t("document_title.dismiss_candidates")}
          </button>
        </div>
      )}

      {suggestError && (
        <div role="alert" style={{ fontSize: 11, color: "#b91c1c" }} data-testid="title-suggest-error">
          {suggestError}
        </div>
      )}
    </div>
  );
}
