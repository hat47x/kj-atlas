import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const readSource = (relativePath: string): string =>
  readFileSync(resolve(__dirname, "..", "..", relativePath), "utf8");

const readJson = (relativePath: string): Record<string, string> =>
  JSON.parse(readFileSync(resolve(__dirname, "..", "..", relativePath), "utf8"));

// DOMAIN-EXPR-01: 既存ドメイン状態（claimType / reviewState / evidence / critique）の
// 読取UI第一級化を、選択コンテキストへの表示として契約固定する。
// schema変更なし・read-only・AIによる状態変更なし、を非後退条件として検証する。
describe("DOMAIN-EXPR-01 read-only domain-state surfacing", () => {
  it("selection context surfaces claimType, evidence counts and critique for the selected card", () => {
    const sidePanelSource = readSource("src/ui/SidePanel.tsx");

    // claimType を選択コンテキストに表示する（既存 claimTypeLabels を再利用）。
    expect(sidePanelSource).toContain('t("side_panel.context.claim_type"');
    expect(sidePanelSource).toContain("claimTypeLabels[selectedCardClaimType]");

    // 根拠（supports/contradicts）件数の集計と表示。
    expect(sidePanelSource).toContain("selectedCardEvidenceCount");
    expect(sidePanelSource).toContain('t("side_panel.context.evidence_count"');
    expect(sidePanelSource).toContain('t("side_panel.context.evidence_none")');

    // 注意バッジ群（未レビュー / 根拠なし / 違和感あり）。
    expect(sidePanelSource).toContain('data-testid="selection-context-state-badges"');
    expect(sidePanelSource).toContain('t("side_panel.context.badge_unreviewed")');
    expect(sidePanelSource).toContain('t("side_panel.context.badge_no_evidence")');
    expect(sidePanelSource).toContain('t("side_panel.context.badge_has_critique")');
  });

  it("derives state from existing read-only fields without mutating schema or review state", () => {
    const sidePanelSource = readSource("src/ui/SidePanel.tsx");

    // 既存往復フィールドの読取のみ（claimType / textReviewed / critique / critiqueTags / evidenceLinks）。
    expect(sidePanelSource).toContain('selectedCard?.claimType ?? "unknown"');
    expect(sidePanelSource).toContain("selectedCard.textReviewed !== true");
    expect(sidePanelSource).toContain("selectedCardHasCritique");
    expect(sidePanelSource).toContain("selectedCard.critique?.trim()");
    expect(sidePanelSource).toContain("selectedCard.critiqueTags?.length");

    // バッジ算出は表示専用であり、状態を書き換える呼び出し（onCard...Change）を含めない。
    const badgeBlock = sidePanelSource.slice(
      sidePanelSource.indexOf('data-testid="selection-context-state-badges"'),
      sidePanelSource.indexOf('t("side_panel.context.focus_selected_card")'),
    );
    expect(badgeBlock).not.toContain("onCardTextReviewedChange");
    expect(badgeBlock).not.toContain("onCardClaimTypeChange");
  });

  it("keeps i18n catalogs in sync for the new selection-context keys (ja/en)", () => {
    const ja = readJson("src/i18n/locales/ja.json");
    const en = readJson("src/i18n/locales/en.json");

    const keys = [
      "side_panel.context.claim_type",
      "side_panel.context.evidence_count",
      "side_panel.context.evidence_none",
      "side_panel.context.badge_unreviewed",
      "side_panel.context.badge_no_evidence",
      "side_panel.context.badge_has_critique",
    ];

    for (const key of keys) {
      expect(ja[key], `ja.json missing ${key}`).toBeTruthy();
      expect(en[key], `en.json missing ${key}`).toBeTruthy();
    }
  });

  it("wires a domain-state filter into the canvas hidden-card computation (App.tsx)", () => {
    const appSource = readSource("src/App.tsx");

    // 純粋関数の利用（再実装ではなく state_filter モジュールへ委譲）。
    expect(appSource).toContain('from "./domain/view/state_filter"');
    expect(appSource).toContain("selectCardIdsByDomainState");
    expect(appSource).toContain("toggleDomainStateFilter");

    // フィルタUIと、hideNonStateMatches による非該当の非表示結線。
    expect(appSource).toContain('data-ui-region="domain-state-filter"');
    expect(appSource).toContain("hideNonStateMatches");
    expect(appSource).toContain("domainStateMatchedIdSet");

    // ドキュメント切替時にフィルタをリセットする（状態の持ち越し防止）。
    expect(appSource).toContain("setDomainStateFilter(createEmptyDomainStateFilter())");
  });

  it("keeps i18n catalogs in sync for the state-filter UI keys (ja/en)", () => {
    const ja = readJson("src/i18n/locales/ja.json");
    const en = readJson("src/i18n/locales/en.json");

    const keys = [
      "state_filter.label",
      "state_filter.unreviewed",
      "state_filter.no_evidence",
      "state_filter.has_critique",
      "state_filter.hide_non_matches",
      "state_filter.match_count",
    ];

    for (const key of keys) {
      expect(ja[key], `ja.json missing ${key}`).toBeTruthy();
      expect(en[key], `en.json missing ${key}`).toBeTruthy();
    }
  });
});
