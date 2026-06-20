import { describe, expect, it } from "vitest";
import {
  DEFAULT_LOCALE,
  getActiveLocale,
  isLocale,
  resolveTemplate,
  resolveTemplateFromCatalogs,
  setActiveLocale,
  subscribeActiveLocaleChange,
  t,
  validateLocaleMessages,
  type Locale,
} from "./translate";
import type { MessageCatalog } from "./messages";
import en from "./locales/en.json";
import ja from "./locales/ja.json";

describe("translate", () => {
  it("resolves known keys in default locale", () => {
    expect(t("share.panel.trigger")).toBe("共有と再現");
  });

  it("interpolates placeholder values", () => {
    expect(
      t("import.panel.summary", {
        fileName: "sample.zip",
        cardCount: 12,
        islandCount: 3,
        perspectiveMode: "default",
      }),
    ).toBe("sample.zip を取り込みました: カード 12、島 3、表示モード default");
  });

  it("falls back to default locale when requested locale misses a key", () => {
    const catalogs = {
      ja: { "safe_mode.indicator.on.label": "セーフモード: ON" },
      en: {} as MessageCatalog,
    };
    expect(resolveTemplateFromCatalogs("safe_mode.indicator.on.label", "en", catalogs)).toBe("セーフモード: ON");
  });

  it("falls back to key string when key is unknown in all locales", () => {
    expect(t("unknown.key" as string, undefined, "en")).toBe("unknown.key");
  });

  it("falls back to default locale when requested locale template is broken", () => {
    const catalogs = {
      ja: { "sample.template": "値: {value}" },
      en: { "sample.template": "Value: {value" },
    };

    expect(resolveTemplateFromCatalogs("sample.template", "en", catalogs)).toBe("値: {value}");
  });

  it("falls back to key when all locale templates are broken", () => {
    const catalogs = {
      ja: { "sample.template": "値: {value" },
      en: { "sample.template": "Value: {value" },
    };

    expect(resolveTemplateFromCatalogs("sample.template", "en", catalogs)).toBe("sample.template");
  });

  it("supports locale override for known locale", () => {
    expect(t("share.panel.export.bundle_cancel", undefined, "en")).toBe("Cancel");
  });

  it("supports active locale switch without per-call locale argument", () => {
    setActiveLocale("en");
    expect(getActiveLocale()).toBe("en");
    expect(t("share.panel.trigger")).toBe("Share & Reproduce");

    setActiveLocale("ja");
    expect(getActiveLocale()).toBe("ja");
    expect(t("share.panel.trigger")).toBe("共有と再現");
  });

  it("normalizes unknown locale to default", () => {
    expect(isLocale("ja")).toBe(true);
    expect(isLocale("en")).toBe(true);
    expect(isLocale("fr")).toBe(false);

    const locale: Locale = DEFAULT_LOCALE;
    expect(locale).toBe("ja");

    setActiveLocale("fr");
    expect(getActiveLocale()).toBe("ja");
  });

  it("validates locale message payload contract", () => {
    expect(validateLocaleMessages({ hello: "world" })).toEqual({ ok: true, errors: [] });
    expect(validateLocaleMessages(null)).toEqual({ ok: false, errors: ["Locale messages must be a JSON object."] });
    expect(validateLocaleMessages({ hello: 1 })).toEqual({
      ok: false,
      errors: ["Locale message value for key \"hello\" must be a string."],
    });
  });

  it("keeps ja/en dictionaries key-equivalent", () => {
    const jaKeys = Object.keys(ja).sort();
    const enKeys = Object.keys(en).sort();
    expect(enKeys).toEqual(jaKeys);
  });

  it("resolves explicit locale via resolveTemplate", () => {
    expect(resolveTemplate("safe_mode.indicator.on.label", "en")).toBe("SafeMode: ON");
  });

  it("keeps AI summary drafts explicitly unreviewed and grounded", () => {
    expect(t("app.status.island_summary.ready_unreviewed", undefined, "ja")).toContain("未レビュー");
    expect(t("app.status.island_summary.ready_unreviewed", undefined, "ja")).toContain("根拠カード");
    expect(t("app.status.relation_summary.generated_unreviewed", undefined, "ja")).toContain("未レビュー");
    expect(t("app.status.relation_summary.generated_unreviewed", undefined, "ja")).toContain("根拠カードと関係線");

    expect(t("app.status.island_summary.ready_unreviewed", undefined, "en")).toContain("unreviewed");
    expect(t("app.status.island_summary.ready_unreviewed", undefined, "en")).toContain("grounding cards");
    expect(t("app.status.relation_summary.generated_unreviewed", undefined, "en")).toContain("unreviewed");
    expect(t("app.status.relation_summary.generated_unreviewed", undefined, "en")).toContain("grounding cards and edges");
  });

  it("provides actionable guided-flow and outline feedback", () => {
    expect(t("app.status.guided_flow.use_claim_type", undefined, "ja")).toContain("主張種別");
    expect(t("app.status.guided_flow.use_review_fields", undefined, "ja")).toContain("右側");
    expect(t("app.status.guided_flow.use_contradiction_links", undefined, "ja")).toContain("矛盾");
    expect(t("app.status.diagnostics.no_document", undefined, "ja")).toContain("ドキュメントを開いて");
    expect(t("app.status.outline.copy_failed", undefined, "ja")).toContain("クリップボード権限");

    expect(t("app.status.guided_flow.use_claim_type", undefined, "en")).toContain("Claim Type");
    expect(t("app.status.outline.downloaded", undefined, "en")).toContain("outline.md");
  });

  it("provides actionable focus and aggregated-edge recovery feedback", () => {
    expect(t("app.status.focus.item_not_found", { kind: "カード", id: "card-1" }, "ja")).toContain("card-1");
    expect(t("app.status.focus.item_hidden", { kind: "カード" }, "ja")).toContain("階層の深さ");
    expect(t("app.status.focus.item_hidden", { kind: "カード" }, "ja")).toContain("ソースカード表示");
    expect(t("app.status.aggregated_edge.not_found", undefined, "ja")).toContain("選び直して");
    expect(t("app.status.aggregated_edge.promoted", undefined, "ja")).toContain("編集可能");

    expect(t("app.status.focus.item_hidden", { kind: "card" }, "en")).toContain("hierarchy depth");
    expect(t("app.status.aggregated_edge.not_found", undefined, "en")).toContain("select it again");
  });

  it("distinguishes reviewed and unreviewed editing history", () => {
    expect(t("app.history.card.marked_reviewed", undefined, "ja")).toContain("レビュー済み");
    expect(t("app.history.card.marked_unreviewed", undefined, "ja")).toContain("未レビュー");
    expect(t("app.history.island.title_marked_unreviewed", undefined, "ja")).toContain("タイトル");
    expect(t("app.history.island.summary_version_restored", undefined, "ja")).toContain("履歴");
    expect(t("app.history.island.image_marked_reviewed", undefined, "ja")).toContain("画像");

    expect(t("app.history.card.marked_reviewed", undefined, "en")).toContain("reviewed");
    expect(t("app.history.card.marked_unreviewed", undefined, "en")).toContain("unreviewed");
  });

  it("provides localized reading-order and island-membership history", () => {
    expect(t("app.history.reading_order.card_added", undefined, "ja")).toContain("カード");
    expect(t("app.history.reading_order.island_added", undefined, "ja")).toContain("島");
    expect(t("app.history.reading_order.reordered", undefined, "ja")).toContain("並べ替え");
    expect(t("app.history.reading_order.item_removed", undefined, "ja")).toContain("読み順から削除");
    expect(t("app.history.island.selected_cards_added", undefined, "ja")).toContain("島に追加");
    expect(t("app.history.island.selected_cards_removed", undefined, "ja")).toContain("島から外");

    expect(t("app.history.reading_order.reordered", undefined, "en")).toContain("Reordered");
    expect(t("app.history.island.deleted", undefined, "en")).toContain("Deleted");
  });

  it("localizes public-pack, view-metadata, and merge-decision feedback", () => {
    expect(t("app.status.public_pack.invalid_index_json", undefined, "ja")).toContain("packs/index.json");
    expect(t("app.status.public_pack.not_found", { packId: "sample" }, "ja")).toContain("sample");
    expect(t("app.status.public_pack.document_invalid", { detail: "schema" }, "ja")).toContain("検証");
    expect(t("app.status.import.view_metadata_document_required", undefined, "ja")).toContain("ドキュメントを開いて");
    expect(t("app.status.import.view_metadata_load_failed", { detail: "JSON" }, "ja")).toContain("JSON");
    expect(t("app.status.merge_suggestion.no_longer_applicable", undefined, "ja")).toContain("候補を更新");
    expect(t("app.status.merge_suggestion.decision_recorded", { decision: "保留中" }, "ja")).toContain("保留中");
    expect(t("app.history.merge_suggestion.decision_recorded", { decision: "採用済み" }, "ja")).toContain("採用済み");

    expect(t("app.status.public_pack.load_failed", undefined, "en")).toContain("could not be loaded");
    expect(t("app.status.merge_suggestion.trusted_interaction_required", undefined, "en")).toContain("human decision");
  });

  it("localizes merge-review boundary and representative-resolution labels", () => {
    expect(t("merge_suggestions.trust_boundary.read_only", undefined, "ja")).toContain("マージ判断");
    expect(t("merge_suggestions.trust_boundary.untrusted_event", undefined, "ja")).toContain("人間");
    expect(t("merge_suggestions.representative_resolution.source_mapping", undefined, "ja")).toContain("参照元");
    expect(t("merge_suggestions.representative_resolution.merged_target", undefined, "ja")).toContain("統合先");
    expect(t("merge_suggestions.representative_resolution.fallback", undefined, "ja")).toContain("暫定");

    expect(t("merge_suggestions.trust_boundary.read_only", undefined, "en")).toContain("open for inspection");
    expect(t("merge_suggestions.representative_resolution.fallback", undefined, "en")).toContain("fallback");
  });

  it("uses plain Japanese terminology throughout the diff panel", () => {
    expect(t("diff.panel.section.cards", undefined, "ja")).toBe("カード");
    expect(t("diff.panel.section.islands", undefined, "ja")).toBe("島");
    expect(t("diff.panel.section.reading_order", undefined, "ja")).toBe("読み順");
    expect(t("diff.panel.section.relation_summaries", undefined, "ja")).toBe("関係要約");
    expect(t("diff.panel.item.reviewed_changed", undefined, "ja")).toContain("レビュー状態");
    expect(t("diff.panel.summary.cards", { added: 1, removed: 2, changedText: 3 }, "ja")).toContain("本文変更");
    expect(t("diff.panel.first_differing_index", { index: 2 }, "ja")).toContain("相違位置");
    expect(t("diff.panel.label.a_strong", undefined, "ja")).toBe("現在の文書");
    expect(t("diff.panel.label.b_strong", undefined, "ja")).toBe("比較対象");
    expect(t("diff.panel.review_state_unknown", undefined, "ja")).toBe("記録なし");
  });

  it("provides localized perspective guidance", () => {
    expect(t("app.perspective_hint.review", undefined, "ja")).toContain("未レビュー");
    expect(t("app.perspective_hint.review", undefined, "ja")).toContain("主張種別");
    expect(t("app.perspective_hint.select_card_for_evidence", undefined, "ja")).toContain("カードを選択");
    expect(t("app.perspective_hint.zoom_in", undefined, "ja")).toContain("拡大");

    expect(t("app.perspective_hint.review", undefined, "en")).toContain("unreviewed");
    expect(t("app.perspective_hint.select_card_for_neighborhood", undefined, "en")).toContain("Select a card");
  });

  it("notifies listeners when active locale changes", () => {
    const calls: string[] = [];
    const unsubscribe = subscribeActiveLocaleChange((locale) => {
      calls.push(locale);
    });

    setActiveLocale("en");
    setActiveLocale("ja");
    unsubscribe();
    setActiveLocale("en");

    expect(calls).toEqual(["en", "ja"]);
  });
});
