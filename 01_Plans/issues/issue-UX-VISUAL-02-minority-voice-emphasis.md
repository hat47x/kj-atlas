# Issue Draft: UX-VISUAL-02 少数意見の可視化（一匹狼・小さな島の保護強調）

- Type: Feature request
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: TBD
- Scope: `03_Implement/frontend/src/canvas/`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/i18n/locales/`, `03_Implement/frontend/e2e/`
- Related Backlog: `UX-VISUAL-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D3 改訂 2026-07-03・D1 4チャネル規則）, `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`, `01_Plans/issues/issue-UX-VISUAL-01-card-meta-row-and-canvas-legend.md`（凡例への追記先）
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: UX-VISUAL-02
- RequirementStatement: 一匹狼（どの島にも属さないカード）・小さな島・単独の違和感を「弱い/劣る」でなく保護対象として淡く強調し、多数派への収束圧力に抗する表示を提供する。画面上のラベルは「保護」を用い、点数・順位・比率は提示しない（反スコアリング）。
- PriorityClass（Must / Should / Could）: Could
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=島に属するカード群と、属さないカード1枚を含む文書を開く / 操作=キャンバスを俯瞰・凡例を開く / 期待結果=一匹狼カードに控えめな「保護」マークが付き、凡例に意味（保護対象であり劣後ではない）が記載される。件数・比率・順位は表示されない / 除外=少数意見の自動抽出/AI 判定、強調の常時大型表示、スコア化。
- GoNoGoGate（Required / Optional / N/A）: Optional
- SecurityGateImpact: N/A（表示のみ）
- VerificationLevel: e2e
- DecisionStatus（Fixed / Pending）: Fixed（ADR-0048 D3 改訂）
- DecisionQueueRef: `ADR-0048`

## 1) 課題 / Problem statement

- KJ法の「一匹狼を許す」（無理に分類しない）は憲章として採択済みだが、表示上は無所属カード・小さな島が視覚的に「取り残し」に見え、束ねて解消したくなる収束圧力が働く。
- 少数・単独であることを健全な状態として肯定的に見せる手段が無い。

## 2) 背景 / Context

- ADR-0048 D3 改訂で条件付き採択: 保護対象としての淡い強調・表示のみ・反スコアリング・既定は控えめ（CB-1）。プロトタイプでカード面の「少数」バッジを検証済み。
- 判定は決定論（島メンバーシップ・違和感の単独性）で行い、AI を使わない。

## 3) 判断基準による優先度評価

- 価値（ADR-0001 P-01/P-02）: 一匹狼の保護は「早すぎる収束を防ぐ」核価値の表示面。単一正解への誘導をしない設計と一体。
- 安全: N/A。
- 規模拡大: 大規模文書ほど少数の埋没が起きやすく、俯瞰時の発見性に寄与（LOD 遠景での扱いは UX-VISUAL-01 の点規則に従属）。
- 後方互換: スキーマ変更なし（表示導出のみ）。

## 3.2 非目標 / Non-goals

- 少数意見の内容的な自動判定（意味解析）。件数・比率・順位・「少数派スコア」の表示。強調の常時大型化。束ね推奨の自動提示。

## 4) 提案する解決策 / Proposed solution

- 判定（決定論）: どの島にも属さないカード＝一匹狼。メンバー数が閾値以下（例: ≤2）の島＝小さな島。単独の違和感タグ＝単独 critique。いずれも導出値でスキーマに保存しない。
- 表示: メタ行に淡い「保護」ピル（amber 系ではなく中立色。保持系と混同しないチャネル選択は ADR-0048 D1 に従う）。島は表札の淡いマーク。ホバー/選択時に「保護対象（無理に分類しない）」の一文。
- 凡例（UX-VISUAL-01）に1行追加: 保護=保護対象（劣後ではない）。
- 表示トグル: View パネルに ON/OFF（既定は控えめ表示 ON か OFF かを実装時に CB-1 自己申告で決定し記録）。

## 5) 受け入れ条件 / Acceptance criteria

- [x] AC-1: 一匹狼カード・小さな島・単独違和感に決定論でマークが付くことが e2e で固定される。
- [x] AC-2: 件数・比率・順位・スコアがどこにも表示されない。
- [x] AC-3: 凡例に意味（保護対象・劣後ではない）が記載され、i18n（ja/en）が同期する。
- [x] AC-4: マークの追加で本文可読性（UX-VISUAL-01 のメタ行規則）が非回帰。
- [x] AC-5: 初期表示アンカー非回帰＋CB-1 自己申告の記録。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 決定論判定（島メンバーシップ・閾値）の導出ロジック。
- [x] T1a 一匹狼カード: どの島にも属さないカードを導出し、カードメタ行へ「保護」を表示する。
- [x] T1b 小さな島: メンバー数が閾値以下の島を導出し、島の表札へ「保護」を表示する。
- [x] T1c 単独違和感: ドキュメント内で単独の違和感タグを導出し、スコア化せずに保護対象として表示する。
- [x] T2 メタ行/表札マーク＋ホバー文言＋i18n。
- [x] T3 凡例追記＋View トグル。
- [x] T4 e2e（判定・非スコア・非回帰）。

## 7) 検証計画 / Validation plan

- `cd 03_Implement/frontend && npm run typecheck && npm test && npx playwright test`

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=マークのみ（小・淡色。凡例1行追加。トグルは View パネル内） / 保留操作の距離=不変（少数マークは保持系の位置規則を侵さない） / 取り消し導線=あり（View トグルで非表示化可能）

## Traceability

- Related: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D3 改訂・D1）
- Related: `01_Plans/issues/issue-UX-VISUAL-01-card-meta-row-and-canvas-legend.md`
- Related: `02_Architecture/design/kj-atlas 拡張提案.dc.html`（仕様精査 B）, `02_Architecture/design/kj-atlas プロトタイプ.dc.html`
- Derived-from: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`

## 実装設計の到着（2026-07-04）

- Claude Design Round 4 でマークのラベルが「少数」から**「保護」**（保護対象・無理に分類しない）へ改訂された。実装時は「保護」系ラベルを採用する（意味・条件は不変: 淡い強調・非スコア・CB-1）。

## 実装準備メモ（2026-07-07）

- 本 issue は Draft のまま維持する。理由は AC-1 が「一匹狼カード」「小さな島」「単独違和感」という3種類の導出対象を含み、表示位置もカードメタ行・島表札・違和感表示で分かれるため。実装は T1a -> T1b -> T1c の順に小さく進め、各段階で e2e のアンカーを追加する。
- 画面上の標準ラベルは「保護」とする。「少数」は要件・設計背景の説明語として残してよいが、利用者が操作時に読む UI ラベルには使わない。
- AC-2 の「件数・比率・順位・スコアを表示しない」は、新設する保護マークと凡例に適用する。既存の島カード枚数表示まで撤去する場合は、ナビゲーションや俯瞰性への影響があるため別 issue/ADR で扱う。
- ローカル環境では Playwright の Chromium ランタイムが不足していたが、2026-07-08 に `@playwright/test` 1.61.1 と一致する Chromium v1228 を導入してブラウザ実行まで確認した。Playwright config は `npm` 非依存の `node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 4173` で webServer を起動する。

## 実装進捗（2026-07-07）

- T1a を実装した。`CanvasShell` の既存 `loneWolfCardIdSet` を `CardView` へ渡し、一匹狼カードの通常カード表示に中立色の「保護」バッジを表示する。
- T1b を実装した。`IslandView` で2枚以下の島を導出し、島の表札に中立色の「保護」バッジを表示する。マーク自体には件数・比率・順位・スコアを表示しない。
- T1c を実装した。カード/島に直接保存された違和感（本文またはタグ）が文書内で1対象だけの場合、そのカード/島を保護対象として表示する。`critiqueInputs` はMVPでは個別編集UI外の契約保持データなので、画面上の単独違和感判定からは除外する。
- T2/T3 を実装した。カードメタ行、島表札、凡例、View パネルの「保護マークを表示」トグルに ja/en 文言を追加した。トグルは既定ONで、OFF時は保護マークのみ非表示にし、カード数・違和感・レビュー状態などの元データ表示は変えない。
- T4 用の Playwright 仕様 `e2e/protected_voice_markers.spec.ts` を追加した。既定表示、View トグルによる非表示、スコア/順位/比率文言の非表示、元データ表示の維持を検証する。2026-07-08 に実ブラウザで通過した。
- `CardView.accessibility.test.ts` で日本語ラベル、アクセシビリティ名、スコア/順位/比率の非表示を固定した。i18n カタログ整合テストも通過。
- 完了: `git diff --check`, `tsc --noEmit`, 関連 Vitest 30件, `node node_modules\@playwright\test\cli.js test e2e/protected_voice_markers.spec.ts --reporter=list` が通過。
