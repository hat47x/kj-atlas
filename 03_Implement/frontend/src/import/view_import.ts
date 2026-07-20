import type { ExportViewMetadata } from "../export/view_metadata";
import { t } from "../i18n/translate";
import { validateView } from "./schema_validation";

export function parseViewJson(rawText: string): { ok: true; metadata: ExportViewMetadata } | { ok: false; error: string } {
  try {
    const parsedJson: unknown = JSON.parse(rawText);
    const result = validateView(parsedJson);
    if (!result.ok) {
      return { ok: false, error: result.errors.map((error) => `[${error.code}] ${error.path}: ${error.message}`).join("\n") };
    }
    return { ok: true, metadata: result.value };
  } catch (error) {
    if (error instanceof SyntaxError) {
      return { ok: false, error: t("app.status.import.view_json_invalid") };
    }
    return { ok: false, error: error instanceof Error ? error.message : t("app.status.import.view_parse_error_unknown") };
  }
}
