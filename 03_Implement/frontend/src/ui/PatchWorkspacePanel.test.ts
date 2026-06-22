import React from "react";
import { beforeEach, describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { PatchWorkspacePanel } from "./PatchWorkspacePanel";
import { setActiveLocale } from "../i18n/translate";

describe("PatchWorkspacePanel", () => {
  beforeEach(() => {
    setActiveLocale("en");
  });

  it("renders CE3 workspace controls and recovery guidance", () => {
    const html = renderToStaticMarkup(
      React.createElement(PatchWorkspacePanel, {
        candidates: [
          {
            id: "cand-1",
            label: "cand-1 (3 cards)",
            preview: {
              sourceSnippets: ["alpha", "beta"],
              draftText: "alpha beta gamma",
            },
          },
          { id: "cand-2", label: "cand-2 (2 cards)" },
          { id: "cand-3", label: "cand-3 (1 card)" },
        ],
      })
    );

    expect(html).toContain("Review patch candidates");
    expect(html).toContain("Adopt (partial)");
    expect(html).toContain("Hold");
    expect(html).toContain("Discard");
    expect(html).toContain("Display settings affect only the current view");
    expect(html).toContain("Roll back last workspace decision");
    expect(html).toContain("Run current conditions");
    expect(html).toContain("status: Ready");
    expect(html).toContain("No saved condition sets.");
    expect(html).toContain("Audit transitions");
    expect(html).toContain("Last executed conditions");
    expect(html).toContain("Review changes");
    expect(html).toContain("Word changes:");
    expect(html).toContain("ce3-candidate-count");
    expect(html).toContain("(3)");
    expect(html).toContain("Recovery path:");
  });

  it("keeps CE3 state-machine checkpoints observable for each candidate", () => {
    const html = renderToStaticMarkup(
      React.createElement(PatchWorkspacePanel, {
        candidates: [
          { id: "cand-alpha", label: "cand-alpha (3 cards)" },
          { id: "cand-beta", label: "cand-beta (2 cards)" },
          { id: "cand-gamma", label: "cand-gamma (1 card)" },
        ],
      }),
    );

    expect(html).toContain('data-testid="ce3-decision-state"');
    expect(html).toContain('data-testid="ce3-candidate-state-list"');
    expect(html).toContain('data-testid="ce3-candidate-state-cand-alpha"');
    expect(html).toContain('data-testid="ce3-candidate-state-cand-beta"');
    expect(html).toContain('data-testid="ce3-candidate-state-cand-gamma"');
    expect(html).toContain('data-testid="ce3-candidate-audit-cand-alpha"');
    expect(html).toContain('data-testid="ce3-candidate-audit-cand-beta"');
    expect(html).toContain('data-testid="ce3-candidate-audit-cand-gamma"');
    expect(html).toContain('data-testid="ce3-audit-log-size"');
    expect(html).toMatch(/data-testid="ce3-audit-log-size"[^>]*>Audit transitions: \d+</);
    expect(html).toContain("No decision changes");
    expect(html).not.toContain("share");
    expect(html).not.toContain("export");
  });

  it("disables preset and decision controls in read-only mode", () => {
    const html = renderToStaticMarkup(
      React.createElement(PatchWorkspacePanel, {
        isReadOnly: true,
        candidates: [{ id: "cand-1", label: "cand-1 (3 cards)" }],
      })
    );

    expect(html).toContain('data-testid="ce3-adopt" disabled=""');
    expect(html).toContain('data-testid="ce3-hold" disabled=""');
    expect(html).toContain('data-testid="ce3-reject" disabled=""');
    expect(html).toMatch(/data-testid="ce3-preset-name"[^>]*disabled=""/);
    expect(html).toMatch(/data-testid="ce3-preset-scope"[^>]*disabled=""/);
    expect(html).toMatch(/data-testid="ce3-preset-depth"[^>]*disabled=""/);
    expect(html).toMatch(/data-testid="ce3-preset-filters"[^>]*disabled=""/);
    expect(html).toContain('data-testid="ce3-run-inline-preset" disabled=""');
  });

  it("uses plain Japanese terminology instead of implementation phases and delta notation", () => {
    setActiveLocale("ja");
    const html = renderToStaticMarkup(
      React.createElement(PatchWorkspacePanel, {
        candidates: [{
          id: "candidate-1",
          label: "候補 1（カード 3 件）",
          preview: {
            sourceSnippets: ["変更前の本文"],
            draftText: "変更後の本文",
          },
        }],
      }),
    );

    expect(html).toContain("パッチ候補の判断");
    expect(html).toContain("現在の判断: 保留（処理状態: 操作待ち）");
    expect(html).toContain("変更内容の確認");
    expect(html).toContain("語句の変更量: 追加");
    expect(html).toContain("直前に実行した条件: (未実行)");
    expect(html).toContain("変更履歴なし");
    expect(html).not.toContain("CE3");
    expect(html).not.toContain("phase:");
    expect(html).not.toContain("トークン差分");
    expect(html).not.toContain("+");
  });
});
