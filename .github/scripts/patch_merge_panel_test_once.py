from pathlib import Path

path = Path("03_Implement/frontend/src/ui/MergeSuggestionsPanel.test.ts")
text = path.read_text(encoding="utf-8")

old = "    onMergedTextChange: vi.fn(),\n    onDecide: vi.fn(),\n"
new = "    onMergedTextChange: vi.fn(),\n    onDecide: vi.fn(),\n    onApplyAccepted: vi.fn(),\n"
if text.count(old) != 1:
    raise SystemExit(f"buildProps patch match count={text.count(old)}")
text = text.replace(old, new, 1)

marker = '  it("disables merge-decision editing controls in read-only mode", () => {\n'
if text.count(marker) != 1:
    raise SystemExit(f"test insertion match count={text.count(marker)}")

test = '''  it("shows the explicit apply action only for an accepted suggestion", () => {\n    const base = buildProps();\n    const pendingHtml = renderToStaticMarkup(\n      React.createElement(MergeSuggestionsPanel, {\n        ...base,\n        suggestions: [\n          {\n            ...base.suggestions[0],\n            latestDecision: "accept" as const,\n            representativeResolvedBy: "fallback" as const,\n          },\n        ],\n      }),\n    );\n    expect(pendingHtml).toContain(t("merge_suggestions.action.apply"));\n    expect(pendingHtml).not.toContain(t("merge_suggestions.action.applied"));\n\n    const appliedHtml = renderToStaticMarkup(\n      React.createElement(MergeSuggestionsPanel, {\n        ...base,\n        suggestions: [\n          {\n            ...base.suggestions[0],\n            latestDecision: "accept" as const,\n            representativeResolvedBy: "repOf" as const,\n          },\n        ],\n      }),\n    );\n    expect(appliedHtml).toContain(t("merge_suggestions.action.applied"));\n  });\n\n'''
text = text.replace(marker, test + marker, 1)
path.write_text(text, encoding="utf-8")
print("MergeSuggestionsPanel tests patched")
