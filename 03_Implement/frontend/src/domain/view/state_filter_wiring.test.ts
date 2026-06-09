import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const readSource = (relativePath: string): string =>
  readFileSync(resolve(__dirname, "..", "..", "..", relativePath), "utf8");

const readJson = (relativePath: string): Record<string, string> =>
  JSON.parse(readFileSync(resolve(__dirname, "..", "..", "..", relativePath), "utf8"));

// DOMAIN-EXPR-01（絞り込み）: state_filter 純粋関数のキャンバスへの配線を契約固定する。
// 選択コンテキストの状態表示そのものは別実装（domain_expression_keyboard_access E2E）が
// 担当するため、本テストはフィルタの結線・UI・i18n のみを対象とする。
describe("DOMAIN-EXPR-01 state filter wiring", () => {
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
