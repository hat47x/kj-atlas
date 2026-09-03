from pathlib import Path

path = Path("03_Implement/frontend/src/App.tsx")
with path.open("r", encoding="utf-8", newline="") as handle:
    text = handle.read()
eol = "\r\n" if "\r\n" in text else "\n"


def replace_once(old: str, new: str, label: str) -> None:
    global text
    old_value = old.replace("\n", eol)
    new_value = new.replace("\n", eol)
    count = text.count(old_value)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, got {count}")
    text = text.replace(old_value, new_value, 1)


replace_once(
    """      setMergeSuggestions((previousSuggestions) =>
        previousSuggestions.map((item) =>
          item.groupId === groupId
            ? {
                ...item,
                latestDecision: decision,
                latestDecidedAt: decidedAt,
              }
            : item
        )
      );
""",
    """      // applyDocumentChange() clears merge suggestion previews as part of a
      // normal Document mutation. A recorded human decision must nevertheless
      // keep the currently reviewed candidates visible so that the separate
      // explicit apply step remains available. Rebuild from this callback's
      // captured suggestion set instead of mapping the just-cleared state.
      setMergeSuggestions(
        mergeSuggestions.map((item) =>
          item.groupId === groupId
            ? {
                ...item,
                latestDecision: decision,
                latestDecidedAt: decidedAt,
              }
            : item
        )
      );
""",
    "decision preview",
)

replace_once(
    """      setMergeSuggestions((current) =>
        current.map((suggestion) =>
          suggestion.groupId === groupId
            ? {
                ...suggestion,
                representativeCardId: result.representativeCardId,
                representativeResolvedBy: "repOf",
                representativeSourceCount: result.sourceCardIds.length,
              }
            : suggestion,
        ),
      );
""",
    """      // The explicit apply is another Document mutation, so
      // applyDocumentChange() clears the preview state here as well. Keep the
      // reviewed candidate visible and replace only its lineage snapshot with
      // the representative that was actually created.
      setMergeSuggestions(
        mergeSuggestions.map((suggestion) =>
          suggestion.groupId === groupId
            ? {
                ...suggestion,
                representativeCardId: result.representativeCardId,
                representativeResolvedBy: "repOf",
                representativeSourceCount: result.sourceCardIds.length,
              }
            : suggestion,
        ),
      );
""",
    "apply preview",
)

replace_once(
    """    [applyDocumentChange, document],
  );

  const handleExport = useCallback(() => {
""",
    """    [applyDocumentChange, document, mergeSuggestions],
  );

  const handleExport = useCallback(() => {
""",
    "apply dependencies",
)

with path.open("w", encoding="utf-8", newline="") as handle:
    handle.write(text)
print("merge decision/apply preview preservation patched")
