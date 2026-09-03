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

# After an accepted merge is applied, its representative intentionally remains
# textReviewed=false. SafeMode therefore blocks a fresh AI candidate collection
# immediately after reload. The persistence E2E should verify the saved document
# through the actual GET/render boundary rather than bypassing that safety rule by
# asking AI to recreate an ephemeral suggestion preview.
test_path = Path("03_Implement/frontend/e2e/merge_accept_apply_save_reload.spec.ts")
with test_path.open("r", encoding="utf-8", newline="") as handle:
    test_text = handle.read()
test_eol = "\r\n" if "\r\n" in test_text else "\n"
old_test = """  panel = await openMergePanel(page);
  await panel.getByRole(\"button\", { name: /Collect.*candidate/i }).click();
  suggestion = panel.locator(\"article\").filter({ hasText: \"c-source-1\" });
  await expect(suggestion.getByRole(\"button\", { name: \"Merge applied\" })).toBeDisabled();
  await expect(suggestion).toContainText(representative?.id ?? \"missing-representative\");

  const primaryFlow = page.locator('[data-ui-region=\"primary-flow\"]');
""".replace("\n", test_eol)
new_test = """  // The newly created representative is intentionally unreviewed, so SafeMode
  // correctly blocks a new AI merge-suggestion request at this point. Persistence
  // is therefore verified through the actual GET/render boundary below, not by
  // recreating an ephemeral suggestion preview after reload.
  const primaryFlow = page.locator('[data-ui-region=\"primary-flow\"]');
""".replace("\n", test_eol)
if test_text.count(old_test) != 1:
    raise SystemExit(f"reload persistence assertion: expected one match, got {test_text.count(old_test)}")
test_text = test_text.replace(old_test, new_test, 1)
with test_path.open("w", encoding="utf-8", newline="") as handle:
    handle.write(test_text)

print("merge decision/apply preview preservation and SafeMode-aligned reload E2E patched")
