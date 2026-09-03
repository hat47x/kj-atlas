from pathlib import Path

path = Path("03_Implement/frontend/src/App.tsx")
with path.open("r", encoding="utf-8", newline="") as handle:
    text = handle.read()
eol = "\r\n" if "\r\n" in text else "\n"

old = """      setMergeSuggestions((previousSuggestions) =>
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
""".replace("\n", eol)
new = """      // applyDocumentChange() clears merge suggestion previews as part of a
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
""".replace("\n", eol)

count = text.count(old)
if count != 1:
    raise SystemExit(f"expected one merge decision preview block, got {count}")
text = text.replace(old, new, 1)
with path.open("w", encoding="utf-8", newline="") as handle:
    handle.write(text)
print("merge decision preview preservation patched")
