import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const readSource = (rel: string): string =>
  readFileSync(resolve(__dirname, "..", "..", rel), "utf8");

// ADR-0048 D1: 4チャネル視覚言語の非後退ガード。
// claimType=色チャネル（fact=green / claim=blue / hypothesis=violet / unknown=slate）。
// amber(#fef3c7 / #f59e0b 系)は「保留・違和感(保持系)」に予約し、claimType 色に使わない
// （同一チャネルに2つの意味を載せない）。SidePanel と CardView で意味割当を一致させる。
//
// 背景: codex/ui-ux-polish で CardView は D1 に更新されたが SidePanel の
// claimTypeBadgeColors.hypothesis が amber のまま残り、hold の amber と衝突していた
// （2026-07-05 検証で発見・修正）。本ガードで再発を防ぐ。

const VIOLET_BG = "#f3e8ff"; // hypothesis の予約色（violet 系）
const AMBER_BG = "#fef3c7"; // hold/critique の予約色（amber 系）

describe("ADR-0048 D1: visual language channel separation guard", () => {
  it("SidePanel の claimTypeBadgeColors は hypothesis=violet で、amber を使わない", () => {
    const src = readSource("src/ui/SidePanel.tsx");
    const block = src.slice(
      src.indexOf("const claimTypeBadgeColors"),
      src.indexOf("const claimTypeBadgeColors") + 400,
    );
    // hypothesis は violet 予約色を使う
    expect(block).toContain(`hypothesis: { backgroundColor: "${VIOLET_BG}"`);
    // claimType 色ブロックに amber を含めない（amber は保持系に予約）
    expect(block).not.toContain(AMBER_BG);
  });

  it("CardView の CLAIM_TYPE_STYLE は hypothesis=violet で、amber を使わない", () => {
    const src = readSource("src/canvas/CardView.tsx");
    const block = src.slice(
      src.indexOf("CLAIM_TYPE_STYLE"),
      src.indexOf("CLAIM_TYPE_STYLE") + 400,
    );
    expect(block).toContain(`hypothesis: { bg: "${VIOLET_BG}"`);
    expect(block).not.toContain(AMBER_BG);
  });

  it("amber は保持系(hold/held)に予約されている（CardView.HOLD_STATE_STYLE）", () => {
    const src = readSource("src/canvas/CardView.tsx");
    const holdBlock = src.slice(
      src.indexOf("HOLD_STATE_STYLE"),
      src.indexOf("HOLD_STATE_STYLE") + 300,
    );
    expect(holdBlock).toContain(`held: { bg: "${AMBER_BG}"`);
  });

  it("SidePanel と CardView で claimType の意味割当（色の系）が一致する", () => {
    const sidePanel = readSource("src/ui/SidePanel.tsx");
    const cardView = readSource("src/canvas/CardView.tsx");
    // fact=green(#dcfce7), claim=blue(#dbeafe), hypothesis=violet(#f3e8ff) を両面で共有
    for (const bg of ["#dcfce7", "#dbeafe", VIOLET_BG]) {
      expect(sidePanel, `SidePanel に ${bg} が無い`).toContain(bg);
      expect(cardView, `CardView に ${bg} が無い`).toContain(bg);
    }
  });
});
