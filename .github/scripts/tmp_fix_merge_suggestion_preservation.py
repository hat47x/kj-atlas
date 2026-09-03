from pathlib import Path

path = Path("03_Implement/frontend/src/App.tsx")
text = path.read_text(encoding="utf-8")

replacements = [
    (
        """      options?: {\n        preserveSuggestionPreview?: boolean;\n      }\n""",
        """      options?: {\n        preserveSuggestionPreview?: boolean;\n        preserveMergeSuggestions?: boolean;\n      }\n""",
    ),
    (
        """      setMergeSuggestions([]);\n      setMergeSuggestionError(null);\n""",
        """      if (!options?.preserveMergeSuggestions) {\n        setMergeSuggestions([]);\n      }\n      setMergeSuggestionError(null);\n""",
    ),
    (
        """      applyDocumentChange(\n        nextDocument,\n        t(\"app.history.merge_suggestion.decision_recorded\", { decision: decisionLabel })\n      );\n""",
        """      applyDocumentChange(\n        nextDocument,\n        t(\"app.history.merge_suggestion.decision_recorded\", { decision: decisionLabel }),\n        { preserveMergeSuggestions: true },\n      );\n""",
    ),
    (
        """      const changed = applyDocumentChange(\n        result.document,\n        t(\"app.history.merge_suggestion_applied\"),\n        { preserveSuggestionPreview: true },\n      );\n""",
        """      const changed = applyDocumentChange(\n        result.document,\n        t(\"app.history.merge_suggestion_applied\"),\n        { preserveSuggestionPreview: true, preserveMergeSuggestions: true },\n      );\n""",
    ),
]

for old, new in replacements:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected exactly one match, found {count}: {old[:80]!r}")
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
print("merge suggestion preservation patch applied")
