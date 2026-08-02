import type { ChangeEvent } from "react";
import { t } from "../i18n/translate";

type SearchBarProps = {
  query: string;
  totalMatches: number;
  currentMatchIndex: number;
  hideNonMatches: boolean;
  onQueryChange: (query: string) => void;
  onPrev: () => void;
  onNext: () => void;
  onHideNonMatchesChange: (hideNonMatches: boolean) => void;
};

export function SearchBar({
  query,
  totalMatches,
  currentMatchIndex,
  hideNonMatches,
  onQueryChange,
  onPrev,
  onNext,
  onHideNonMatchesChange,
}: SearchBarProps) {
  const handleInputChange = (event: ChangeEvent<HTMLInputElement>) => {
    onQueryChange(event.target.value);
  };

  const hasMatches = totalMatches > 0;
  const displayedIndex = hasMatches ? currentMatchIndex + 1 : 0;

  return (
    <div
      data-ui-region="header-search"
      style={{
        display: "flex",
        alignItems: "center",
        gap: 8,
        rowGap: 4,
        flexWrap: "wrap",
        width: "100%",
        minWidth: 0,
        whiteSpace: "nowrap",
      }}
    >
      <input
        type="text"
        value={query}
        onChange={handleInputChange}
        placeholder={t("search_bar.placeholder")}
        style={{
          width: "min(220px, 32vw)",
          minWidth: 120,
          height: 32,
          border: "1px solid #cbd5e1",
          borderRadius: 6,
          padding: "0 10px",
          fontSize: 14,
        }}
      />
      <span style={{ fontSize: 12, color: "#475569", minWidth: 56, textAlign: "center" }}>
        {displayedIndex}/{totalMatches}
      </span>
      <button
        type="button"
        onClick={onPrev}
        disabled={!hasMatches}
        style={{
          border: "1px solid #cbd5e1",
          backgroundColor: "#ffffff",
          borderRadius: 6,
          padding: "6px 10px",
          cursor: hasMatches ? "pointer" : "not-allowed",
        }}
      >
        {t("search_bar.prev")}
      </button>
      <button
        type="button"
        onClick={onNext}
        disabled={!hasMatches}
        style={{
          border: "1px solid #cbd5e1",
          backgroundColor: "#ffffff",
          borderRadius: 6,
          padding: "6px 10px",
          cursor: hasMatches ? "pointer" : "not-allowed",
        }}
      >
        {t("search_bar.next")}
      </button>
      <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: "#334155", whiteSpace: "nowrap" }}>
        <input
          type="checkbox"
          checked={hideNonMatches}
          onChange={(event) => {
            onHideNonMatchesChange(event.target.checked);
          }}
        />
        {t("search_bar.hide_non_matches")}
      </label>
    </div>
  );
}
