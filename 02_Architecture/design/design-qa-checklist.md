# 実装照合レビュー チェックリスト（設計⇔実装 QA 定型）

出典: Claude Design Round 5 回答（`kj-atlas 拡張提案.dc.html` §依頼3、2026-07-04 受領）を運用用に md 化。
用途: 実装が main に載るたび、実機スクリーンショットを Claude Design に渡して設計意図との乖離をレビューする際の定型。各項目は **✓（適合）/ △（軽微な乖離・所見つき）/ ✗（乖離・要修正）** で回答する。
運用: 各実装 PR の本文にこのチェックリストの該当節を貼り、実装者が自己申告 → スクショとともに Claude Design へレビュー依頼 → 回答を issue/PR に記録する。

## A. 視覚言語

- [ ] slate 階層（濃=前景 / 淡=後景）に一致
- [ ] amber は保持系のみ（保留/違和感）に使用、他意味に流用なし
- [ ] 4チャネル1意味（色=型 / 位置=保持系 / 形=確認 / 密度=違和感）で衝突なし
- [ ] タイポ 13/12/11/10・ウェイト 600/700・角丸 6/8/999・間隔 2/4/6/8

## B. 状態遷移

- [ ] 空状態ヒントが 0枚時のみ出現・初回作成で消滅
- [ ] 凡例・番号バッジが既定 OFF
- [ ] 非同期（差分読込等）に進捗＋キャンセル
- [ ] 適用/マージに取消（可逆）と監査記録

## C. 核の保護

- [ ] 点数・ランク・%・準備度スコアが存在しない（反スコアリング）
- [ ] provider=none で書く/並べる/束ねる/つなぐ/保留が完結・AI タブは肯定提示
- [ ] 保留・違和感が確定より遠くない（CB-2）
- [ ] SafeMode 既定ON・共有前確認・出典参照トグル既定OFF

## D. a11y / 契約

- [ ] 読み上げ順 型→保持系→確認→根拠→本文
- [ ] フォーカス初期位置・Tab順・Escape 段階が仕様表どおり
- [ ] role/aria（tablist・dialog・live）付与
- [ ] 既存キーボード/フォーカス契約を破壊しない・OS 別キー表記

---

- 第1回対象: 段階1（カードメタ行＋凡例=UX-VISUAL-01・空状態=UX-EMPTY-01）実装後。
- 関連: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`、`04_Documentation/ui_catalog.md`（スクショ再生成手順）。

## 第2回 2026-07-09: DOMAIN-KA-01 / DOMAIN-TRACE-01 / UX-SHARE-01 / UI-QUALITY-A11Y-02（選択コンテキスト・共有前確認）

出典: 03_Implement/frontend/scripts/capture_design_conformance_20260709.mjs で実機（Docker Playwright, Chromium）スクリーンショット6枚を取得し、実装者（Claude Code）が自己申告で本チェックリストに照合。外部の Claude Design レビュー依頼は行っていない（このラウンドは自己適合確認）。

| 節 | 結果 | 所見 |
| --- | --- | --- |
| A. 視覚言語 | △→✓ | slate階層・amber保持系限定・4チャネル・タイポ/角丸は準拠。**発見・修正**: 共有直前サマリのSafeMode表示が「SafeMode: セーフモード: ON」と二重表記（`safeModeIndicator.label` が既に接頭辞を含むのに、i18nテンプレートで再度ラップしていた）。`SharePanel.tsx` から二重ラップを除去し、未使用化した `share.panel.pre_share_gate.safe_mode` キーを両ロケールから削除。回帰アンカーを追加。 |
| B. 状態遷移 | ✓ | 通し番号バッジは既定OFF・View トグルでのみON（スクショで確認）。KA欄はキャンバス非表示（選択コンテキスト限定、DOMAIN-KA-01 AC-4）。 |
| C. 核の保護 | ✓ | 共有直前サマリは件数のみ（%・スコア・準備度語彙なし）。SafeMode既定ON・出典参照トグル既定OFF をスクショで確認。 |
| D. a11y/契約 | ✓ | 選択コンテキストの読み上げ順が型→保持系→確認→根拠の順であることをスクショと既存e2eの双方で確認。 |

- 残存所見（△・非ブロッキング）: 選択コンテキストに主張種別・根拠件数が要約チップと個別ブロックの二重表示として残っている（既存挙動、本ラウンドの変更対象外）。次回の見直し対象として記録するのみ。
- 検証: typecheck 0 / vitest 963 passed / 関連 e2e 7 passed（`pre_share_summary_gate.spec.ts`, `a11y_selection_and_share_gate.spec.ts`）。
- 生成物: `03_Implement/frontend/scripts/capture_design_conformance_20260709.mjs`（一時利用。`04_Documentation/assets/screenshots/` の正規セットには追加しない）。
