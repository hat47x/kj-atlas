import { validateImportViewMetadata } from "../export/view_metadata";
import type { ExportViewMetadata } from "../export/view_metadata";

export function parseViewJson(rawText: string): { ok: true; metadata: ExportViewMetadata } | { ok: false; error: string } {
  try {
    const parsedJson: unknown = JSON.parse(rawText);
    const result = validateImportViewMetadata(parsedJson);
    if (!result.ok) {
      return { ok: false, error: result.error };
    }
    return { ok: true, metadata: result.metadata };
  } catch (error) {
    if (error instanceof SyntaxError) {
      return { ok: false, error: "Invalid JSON in view.json" };
    }
    return { ok: false, error: error instanceof Error ? error.message : "Unknown view parse error" };
  }
}
