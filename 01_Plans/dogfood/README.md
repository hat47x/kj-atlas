# kj-atlas ドッグフーディング

kj-atlas を使った kj-atlas 開発プロセスの管理。ADR-0042（ドッグフーディング）に基づく。

## 文書一覧

| ファイル | 内容 | 状態 |
|---------|------|------|
| `doc_kj_atlas_dogfood_r1.json` | R1 問題提起: 開発プロセスの摩擦と設計課題 | カード化完了 + 5摩擦領域の対応完了反映 |
| `doc_kj_atlas_dogfood_r2.json` | R2 現状把握: 設計判断の実態と構造的課題 | カード化完了 + 2026-08-12ナラティブ最新化 |
| `doc_kj_atlas_dogfood_r3.json` | R3 本質追求: 不整合が生まれ解消されない根本原因 | カード化完了 + 根本原因への対応状況反映 |
| `doc_kj_atlas_dogfood_r4.json` | R4 構想: 開発プロセスの理想像 | カード化完了 + 理想状態の達成状況反映 |
| `doc_kj_atlas_dogfood_r5.json` | R5 具体策: 短期・中期・長期の3段階実行計画 | カード化完了 + 全期間の実行状況反映 |
| `doc_kj_atlas_dogfood_r6.json` | R6 手順: 4フェーズ14ステップの依存関係付き実行計画 | カード化完了 + 14ステップ実行状況反映 |
| `adopting-org-patterns.md` | 導入組織4種×利用経路×検証軸のパターン多様化分析（+MCP価値ギャップの実測） | 2026-08-12作成・DOGFOOD-05起票 |
| `dogfood-analysis-synthesis-2026-08-12.md` | DOGFOOD-02〜06の横断分析（共通根本原因: 検証経路の正常系偏重） | 2026-08-12作成・DOGFOOD-06起票 |

## 使い方

1. kj-atlas を起動
2. 「ファイルから読み込み」→ `doc_kj_atlas_dogfood_r1.json` を選択
3. カード・島・関係線を確認し、不足する視点があれば追加
4. 配置を調整し、A型図解として成立させる
5. 空白を発見したら言語化し、次のラウンド（R2）の材料とする

## 週次運用（W型サイクル）— 2026-08-11 開始

R1〜R6の完全サイクルは初期構築として完了した。以後は短縮週次サイクルで運用する。

### 第1回週次サイクル完了（2026-08-11〜12）

第1回の完全サイクルを実行し、R1-R6全ラウンドに実行・達成状況を反映した。

| 活動 | 成果 |
|------|------|
| R1摩擦の対応 | 5摩擦領域すべて対応（タイトル補正・方法論確立・AI基盤・ドッグフード・コード生成） |
| R2現状把握 | ナラティブ最新化（ADR 75/75・警告1・評価自動化） |
| R3根本原因 | 3件すべて対応（ベースライン・テンプレート必須化・フィードバックループ） |
| R5具体策 | 短期3策完了 + 長期コード生成拡張完了 |
| 計測 | 4指標更新（警告1・ADR 75・実API 2/2達成・**L2昇格**） |
| 改善点 | 11件記録（すべて対応） |

第2回以降は、人間の月曜サイクルでR1（先週の摩擦）→R5（今週の具体策）を実行する。

### 週次サイクル（毎週月曜）

| ラウンド | 内容 | 入力 → 出力 |
|---------|------|------------|
| R1 | 先週の摩擦のカード化 | ドッグフード記録・issue・CI警告 → カード群 |
| R5 | 今週の具体策 | 摩擦カード → 対応issue（可能なものは即対応） |
| 計測 | 4指標の更新 | AGENTS.md L2進捗を更新 |

### 月初サイクル（毎月1日）

全R1〜R6を1回通し、プロセスとプロダクトの改善を同期させる。

### 計測指標（4指標）

| 指標 | 正本 | 直近値（2026-08-12） |
|------|------|---------------------|
| 設計整合警告数 | `check_design_consistency.py` | 1（目標50未満✅、139→1） |
| 三要素検証済みADR数 | ADRの`Three-Element Verification`節 | 76/76（全ADR✅、目標10） |
| 実API検証操作数 | `ai_eval_results.md` | **2/2達成**（refine_card_text 10/10・suggest_island_summary 4/4） |
| 自律実行率 | 四半期判定ADR | **L2: 昇格済み（ADR-0075）** / L3: 基盤整備+①達成 |

### 測定の健全性（DOGFOOD-METRIC-01、案A+案B 併用を採択・2026-08-12）

自己測定ゲート（上の4指標）は**測定器と指標が同一主体の管理下**にあるため、次の2点で健全性を担保する。

- **案A（能力カナリア）**: 各測定器が検出できるはずの既知の陽性例をテストで固定する。`check_design_consistency.py` は `test_design_consistency_discrimination.py`（DX-DESIGN-CHECK-01 AC-3）が該当。カナリアを意図的に壊せばCIが落ちることを確認して追加する。
- **案B（測定器変更の分離記録）**: 昇格判定に使う指標の変化が**測定器変更に由来する分**と**対象修正に由来する分**を分離記録する。昇格判定ADRはテンプレートの「Measurement Integrity」節を必須とする。①の「139→1」には検出器変更が含まれ、`ADR-0075` 追記・`DX-DESIGN-CHECK-01` で記録済み。

### コード生成成功率（L3自律基準①、3軸）

| 種別 | 成功率 | 正本 | DX-CODEGEN |
|------|--------|------|-----------|
| 骨格生成 | 80%（4/5） | `codegen_results.md` | 01 |
| ロジック生成 | 100%（3/3） | `codegen_results.md` | 02 |
| テスト生成 | 100%（2/2） | `codegen_results.md` | 03 |

### 四半期サイクル（自律性昇格判定）

AGENTS.md §1.3の昇格条件を四半期ごとに評価し、判定結果をADRとして記録する。

### 検証経路の追加規約（DOGFOOD-06、2026-08-12 制定）

Web/API/MCP など検証経路を新規追加・拡張するときは、次の3点を守る（DOGFOOD-03/04 の「異常系未検証」再発防止）。

1. **成功系だけでなく異常系も assert する**。最低限: not_found / 503相当 / 契約外version / 対象なし を検証入力に固定する。
2. **検証スクリプト自身に unit テストを付ける**（スクリプトのロジックを直接 assert。`verify_mcp.ts` は `src/mcp_verify_result.ts` + `mcp_verify_result.test.ts` で固定済み）。
3. **検証対象データを「理想状態」だけでなく「実状態」にする**（旧version・未レビューのみ・空DB を含める）。

## ドッグフーディングで発見された kj-atlas 改善点

| 日付 | 発見 | 対応 |
|------|------|------|
| 2026-08-11 | 管理面のタイトル非表示が文書識別を不可能にする | `admin-surface-metadata-display-correction.html`（補正済み） |
| 2026-08-11 | 設計文書の警告がスクリプトのregex限界で誤検出される | `check_design_consistency.py` 正規化追加（139→1） |
| 2026-08-11 | 契約ドリフトがrouter prefixを解決しない | `check_contract_drift.py` prefix解決追加（11→2） |
| 2026-08-11 | 自律性L1→L2の移行判定が間接参照で永遠に満たされない | `AGENTS.md` §1.3 昇格条件を定量化（警告<50・ADR適用≥10・実API検証≥2） |
| 2026-08-11 | 設計判断の記録場所が3種に分散し判断が追跡困難 | ADR/issueテンプレートに三要素検証欄を必須化 |
| 2026-08-12 | 設計判断の三要素整合を人間の記憶に依存 | 全75 ADRに三要素検証を適用（100%） |
| 2026-08-12 | コード生成が骨格のみでロジック・テストが欠落 | DX-CODEGEN-01/02/03で3軸（骨格80%・ロジック100%・テスト100%）に拡張 |
| 2026-08-12 | 実API評価が手動で実行しづらい | `run_ai_eval.py`でワンコマンド自動化（API key投入で実行） |
| 2026-08-11 | コード生成が既存実装を検出せず重複コードを生成 | `generate_from_design_decision.py` 既存実装チェック追加 |
| 2026-08-11 | 骨格生成成功率の解釈が不正確（完全コード生成と混同） | `codegen_results.md` で骨格生成成功率とロジック生成を分離計上（80%） |
| 2026-08-12 | L2での三要素チェック実践: FieldworkRequestV1実組み込みを検証し「InquiryJourneyV1整合待ち」と指摘 | AIが自律検証し最終判断を人間へ（L2の動作実証） |
| 2026-08-12 | Web以外の検証経路が未整備 | `verify_api.sh`（CLI/API・curlベース）+ `verify_mcp.ts`（MCP・クライアントベース）を追加 |
| 2026-08-12 | GET /docs/{id}が旧版文書（version≠1）で素の500を返す（GET/PUTの検証経路が非対称、ADR-0058のfail-closed意図は正しいが拒否方法が非対称） | `issue-DOGFOOD-02`起票（三要素分析済み・P1） |
| 2026-08-12 | verify_mcp.tsがnot_found/error応答（isError=true）をJSON.parseで破壊する（サーバー契約は正しく、クライアント側の仮定が誤り） | `issue-DOGFOOD-03`起票→**修正済み**（isError事前確認・not_foundを区別報告。MCP 49 tests pass） |
| 2026-08-12 | verify_api.shの`/session/context`チェックが503を「reachable」と判定（local-devでは常に503のため無内容、saas-multitenantでは実障害を隠す） | `issue-DOGFOOD-04`起票→**修正済み**（503をINFO・非reachableとして区別報告） |
| 2026-08-12 | ドッグフーディングが「自己言及（kj-atlasでkj-atlas）」の単一パターンに偏っていた | `adopting-org-patterns.md`作成（4組織×経路×検証軸のパターン多様化分析） |
| 2026-08-12 | MCP経路は未レビューカードを一切露出せず、Org-D「AI委譲による初期探索」が支援できない（SEC-CONTEXT-PROJECTION-01のfail-closedと業務価値の衝突） | `adopting-org-patterns.md` §3.5に三要素分析で記録（安全境界は緩和せず適用範囲を明示） |
| 2026-08-12 | MCPの未レビュー不可視を issue 化し、適用範囲の明示(A)／探索専用経路(B)／現状維持(C)の判断材料を整理 | `issue-DOGFOOD-05`起票（設計判断・P2） |
| 2026-08-12 | Web初回起動がデフォルト文書`doc_phase1_canvas`を自動ロードし、旧版文書では500エラー画面に（DOGFOOD-02のWeb増幅・allowCreateOnNotFoundは404のみ救済） | `issue-DOGFOOD-02`に実地確認・受入条件追記（P1） |
| 2026-08-12 | Web経路のOrg-A検証スクリプトを追加（バッチ文書を実UIで開くPlaywright走行） | `03_Implement/frontend/scripts/dogfood_orga_web_20260812.mjs` |
| 2026-08-12 | DOGFOOD-02〜05の横断分析から、共通根本原因を抽出（正常系偏重・理想状態前提・GET/PUT非対称・適用範囲未明示） | `dogfood-analysis-synthesis-2026-08-12.md`作成 |
| 2026-08-12 | 検証経路の追加時に異常系をCIで固定するルールの欠如（DOGFOOD-03/04の共通原因） | `issue-DOGFOOD-06`起票（プロセス改善・P2） |
| 2026-08-12 | `.gitignore` の `result-*`（Nix出力用）が無アンカーのため全階層のファイルを無視し、分析文書が git 管理外になった | `issue-DOGFOOD-07`起票（ルート限定 `/result` `/result-*` へアンカー案）→**修正済み**（`/result` `/result-*` へアンカー・`git check-ignore` で両方向を確認） |
| 2026-08-12 | DOGFOOD-02（GET raw 500）の修正案を実機検証（`version:2`→A1 422）し、GETをA1契約検証へ通す具体案を issue に明記 | `issue-DOGFOOD-02`に修正案追記（proposal-only・P1） |
| 2026-08-12 | CLI/API経路の実走行（`verify_api.sh`・実DB`kj_atlas.db`）: 旧版文書 GET が構造化422（DOGFOOD-02修正のe2e確認）、`/session/context` 503をINFO区別（DOGFOOD-04） | `verify_api.sh`実走行 3 pass 0 fail（exit 0）を確認 |
| 2026-08-12 | API書込経路の検証スクリプトが無く、admin の「自前スクリプトで文書を作る」経路が未検証 | `verify_api_write.sh` 追加（PUT /docs/{id} 作成＋GET 読戻しの往復）。実走行 4 pass 0 fail（作成200・読戻し・title/card件数往復） |
| 2026-08-12 | MCP 検証経路がカード作業状態（holdState）を表示せず、生成AIが保留状態を読めない | `verify_mcp.ts` に holdState/counts 表示を追加。Hold/Critique文書（held2/shelved1）を実走行し `cards: 3 (held:2, pending:0, shelved:1)`・SafeModeでも holdState 投影を確認（DOGFOOD-08 の e2e 検証） |
| 2026-08-12 | `saas-multitenant` の起動ゲートが fail-fast で機能することを実地確認（必須アダプタ欠損→起動拒否） | `adopting-org-patterns.md` §4 に実地確認を記録 |
| 2026-08-12 | Org-Bパターン（Hold/Critique週跨ぎ）を実走行。API保存→再読込で作業状態が完全維持（held2/shelved1/critiqued2） | `adopting-org-patterns.md` §3.6 に記録 |
| 2026-08-12 | MCP/外部プロジェクションが Hold/Critique 作業状態をスキーマごと落とす（AI協働の基本情報欠落） | `issue-DOGFOOD-08`起票（三要素分析済み・P2） |
| 2026-08-12 | DOGFOOD-08 の修正案（`ProjectedCard` へ holdState 追加・critique は SafeMode 判断と分離）を具体化 | `issue-DOGFOOD-08`に修正案追記（proposal-only・反スコアリング語彙との衝突なしを確認） |
