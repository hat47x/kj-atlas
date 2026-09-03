from pathlib import Path

path = Path("03_Implement/frontend/src/api/client.ts")
text = path.read_text(encoding="utf-8")
anchor = "function isMergeSuggestion(value: unknown): value is MergeSuggestion {\n"
helpers = '''function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((entry) => isNonEmptyString(entry));
}

'''
if text.count(anchor) != 1:
    raise SystemExit("isMergeSuggestion anchor drifted")
if "function isNonEmptyString(value: unknown)" in text:
    raise SystemExit("validator helpers already present after contract separation")
path.write_text(text.replace(anchor, helpers + anchor, 1), encoding="utf-8")
