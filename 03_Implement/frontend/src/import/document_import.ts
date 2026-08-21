import type { DocumentV1 } from "../domain/types";
import { t } from "../i18n/translate";
import { validateDocument, type ValidationError } from "./schema_validation";

function formatValidationErrors(errors: ValidationError[]): string {
  const details = errors
    .slice(0, 6)
    .map((error) => `- [${error.code}] ${error.path}: ${error.message}`)
    .join("\n");
  const suffix =
    errors.length > 6
      ? `\n- ${t("app.status.import.validation_failed_more_suffix", { count: errors.length - 6 })}`
      : "";
  return `${t("app.status.import.validation_failed_header")}\n${details}${suffix}`;
}

export function parseDocumentJson(rawText: string): { ok: true; document: DocumentV1 } | { ok: false; error: string } {
  try {
    const parsedJson: unknown = JSON.parse(rawText);
    const validation = validateDocument(parsedJson);
    if (!validation.ok) {
      return { ok: false, error: formatValidationErrors(validation.errors) };
    }

    return { ok: true, document: validation.value };
  } catch (error) {
    if (error instanceof SyntaxError) {
      return { ok: false, error: t("app.status.import.document_json_invalid") };
    }
    return { ok: false, error: error instanceof Error ? error.message : t("app.status.import.document_parse_error_unknown") };
  }
}
