import { describe, expect, it } from "vitest";

import { t } from "./translate";

// FB-RM-I18N-05: merge_apply.ts and document_import.ts pushed hardcoded
// English prose into MergeDiagnostic/ValidationError.message regardless of
// locale. This pins the fix at the i18n-key layer: every key those two files
// now call through t() must resolve to real ja/en text in both locales, not
// silently degrade to the bare key. That degradation is a real failure mode
// here, not a hypothetical -- one of the keys below originally contained a
// literal `{id, text, x, y}` (comma-separated, not a single `{name}`
// placeholder) and isTemplateWellFormed() rejected it as malformed, which
// would have shown users the raw key string instead of a message.
const KEYS_WITH_VALUES: Array<[string, Record<string, string | number>]> = [
  ["app.status.comparison.merge_error.evidence_add_missing_incoming", { id: "ev-1" }],
  ["app.status.comparison.merge_error.evidence_add_missing_card", { id: "ev-1", cardId: "card-1" }],
  ["app.status.comparison.merge_error.card_remove_missing_evidence_remove", { id: "card-1", linkId: "ev-1" }],
  ["app.status.comparison.merge_error.selection_exceeds_hard_limit", { count: 1200, limit: 1000 }],
  ["app.status.comparison.merge_error.conflict", { entityKey: "card:c1", reason: "both modified" }],
  ["app.status.comparison.merge_warning.auto_included_card_for_evidence_add", { cardId: "card-1", id: "ev-1" }],
  ["app.status.comparison.merge_warning.auto_included_evidence_remove_for_card_remove", { linkId: "ev-1", id: "card-1" }],
  ["app.status.comparison.merge_warning.large_selection", { count: 250 }],
  ["app.status.import.validation.island_missing_geometry", { islandId: "i1" }],
  ["app.status.import.validation.evidence_link_unknown_from_card", { linkId: "ev-1", cardId: "card-1" }],
  ["app.status.import.validation.evidence_link_unknown_to_card", { linkId: "ev-1", cardId: "card-1" }],
  ["app.status.import.validation_failed_more_suffix", { count: 3 }],
];

const KEYS_WITHOUT_VALUES = [
  "app.status.comparison.merge_error.warnings_require_confirmation",
  "app.status.comparison.conflict_reason.both_modified",
  "app.status.comparison.conflict_reason.delete_vs_update",
  "app.status.comparison.conflict_reason.update_vs_delete",
  "app.status.import.validation_failed_header",
  "app.status.import.validation.document_must_be_object",
  "app.status.import.validation.cards_field_missing",
  "app.status.import.validation.cards_field_wrong_type",
  "app.status.import.validation.card_not_object",
  "app.status.import.validation.card_id_invalid",
  "app.status.import.validation.card_text_invalid",
  "app.status.import.validation.islands_not_array",
  "app.status.import.validation.island_not_object",
  "app.status.import.validation.island_id_invalid",
  "app.status.import.validation.imported_data_not_object",
  "app.status.import.validation.version_required",
  "app.status.import.validation.version_unsupported",
  "app.status.import.validation.required_fields_missing",
  "app.status.import.validation.id_not_string",
  "app.status.import.validation.transform_invalid",
  "app.status.import.validation.cards_shape_invalid",
  "app.status.import.validation.edges_not_array",
  "app.status.import.validation.islands_field_not_array",
];

describe("FB-RM-I18N-05 domain error/warning keys", () => {
  it.each(KEYS_WITH_VALUES)("resolves %s in ja without degrading to the key", (key, values) => {
    const resolved = t(key, values, "ja");
    expect(resolved).not.toBe(key);
    for (const value of Object.values(values)) {
      expect(resolved).toContain(String(value));
    }
  });

  it.each(KEYS_WITH_VALUES)("resolves %s in en without degrading to the key", (key, values) => {
    const resolved = t(key, values, "en");
    expect(resolved).not.toBe(key);
    for (const value of Object.values(values)) {
      expect(resolved).toContain(String(value));
    }
  });

  it.each(KEYS_WITHOUT_VALUES)("resolves %s in ja without degrading to the key", (key) => {
    expect(t(key, undefined, "ja")).not.toBe(key);
  });

  it.each(KEYS_WITHOUT_VALUES)("resolves %s in en without degrading to the key", (key) => {
    expect(t(key, undefined, "en")).not.toBe(key);
  });

  it("ja and en text differ for a representative prose key (not just copied across)", () => {
    const ja = t("app.status.comparison.merge_error.evidence_add_missing_incoming", { id: "x" }, "ja");
    const en = t("app.status.comparison.merge_error.evidence_add_missing_incoming", { id: "x" }, "en");
    expect(ja).not.toBe(en);
  });

  it("the previously-malformed cards_shape_invalid key no longer contains a bare, non-interpolating brace pair", () => {
    // The original English text was "...an array of {id, text, x, y}." -- a
    // literal, comma-separated brace group, not a `{name}` placeholder.
    // isTemplateWellFormed() strips only `{[a-zA-Z0-9_]+}` before checking
    // for leftover braces, so that phrasing failed the well-formed check.
    for (const locale of ["ja", "en"] as const) {
      const resolved = t("app.status.import.validation.cards_shape_invalid", undefined, locale);
      expect(resolved).not.toBe("app.status.import.validation.cards_shape_invalid");
      expect(resolved).not.toMatch(/\{[^}]*,[^}]*\}/);
    }
  });
});
