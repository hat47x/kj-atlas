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
| `three-element-synthesis-2026-08-13.md` | 三要素分析法による全発見の統合（共通原因: 一次元の変更が他次元の牽制を通らない）・設計規則R1-R5と抜け漏れG1-G6の再回収 | 2026-08-13作成・ADR-0067ベース |

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
| 設計整合警告数 | `check_design_consistency.py` | 4（目標50未満✅・baseline一致。139→1→識別力回復の後、構造的照合化で参照誤差2件が可視化され4で安定） |
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
| 2026-08-12 | 書込経路の **UPDATE ライフサイクル**（PUT 変更→GET 反映）が未検証 | `verify_api_write.sh` を create→read→**update→read** の7チェックへ拡張。実走行 7 pass 0 fail（更新反映・3カード化を確認） |
| 2026-08-12 | コンテンツ上限（DOMAIN-CARD-TEXT-01: カード本文2000文字）の**実API 強制**をライブ検証 | 2001文字のカード本文を PUT → **422**（`String should have at most 2000 characters`・構造化 A1 エラー）。上限が API 境界で強制されることを実証 |
| 2026-08-13 | **JIT provisioning の濫用を実証**（無認証GETの未知ヘッダーでユーザー行自動作成）→ **既定値を fail-closed（false）に変更** | `KJ_ATLAS_ALLOW_JIT_PROVISIONING` 既定 `false`（SEC-RATE-LIMIT-01）。未知ユーザー→403・フルスイート 981 pass（JIT=false）・依存テストを既定非依存化・ドキュメント同期 |
| 2026-08-13 | API の楽観的並行制御（ETag/If-Match）を実機検証 | 正しい If-Match → 200・stale If-Match → **409**（競合検出）。複数利用者の同時保存競合が安全に拒否されることを実証 |
| 2026-08-13 | **ドキュメントタイトルの上限同期ギャップを検出**（DOMAIN-CARD-TEXT-01） | 501文字タイトルが PUT で **200（無界）** を実測。frontend は 500 上限・backend は無界だった。**backend に `DOCUMENT_TITLE_MAX_LENGTH=500` を追加**し、同期テストの対象にも追加（501→422・500→200 を実機確認） |
| 2026-08-13 | 他コンテンツ上限（島タイトル500）の backend 強制を確認 | 501文字の島タイトル → **422**（強制済み）。ドキュメントタイトルのみが漏れており、修正で全コンテンツ上限の同期が完了 |
| 2026-08-13 | 島要約（2000）の backend 強制を確認 | 2001文字の島要約 → **422**。主要コンテンツ上限（カード2000・ドキュメント/島タイトル500・島要約2000）の API 強制を全て実機確認（ナラティブ/エビデンスは同期テストで担保） |
| 2026-08-13 | エビデンス注記（2000）の backend 強制を確認 | 2001文字の注記 → **422**・2000文字 → 200。**DOMAIN-CARD-TEXT-01 の全コンテンツ上限が API 境界で強制されることを実機検証完了** |
| 2026-08-13 | **三要素分析 R2（対称性）で `Card.critique`/`Island.critique` の backend 無界を検出** | frontend は `CRITIQUE_MAX_LENGTH=2000` で上限、backend は無界だった（タイトルと同型の非対称）。**backend に `CRITIQUE_MAX_LENGTH=2000` を追加**し同期テスト対象化（2001文字→422）。R2 の非対称2件目を解消 |
| 2026-08-13 | PUT の id と URL パスの不一致（契約エッジ）を検証 | `PUT /docs/url_id` に `doc.id=mismatch_id` → **400**「Path doc_id and document.id must match」（部分保存なし）。文書の同一性が URL と整合することを保証 |
| 2026-08-13 | 文書の DELETE（未実装メソッド）の挙動を検証 | `DELETE /docs/{id}` → **405**（文書削除エンドポイントなし・文書は保持）。誤削除の防止が API 境界で保証される |
| 2026-08-13 | ドキュメントのサイズ/カード件数上限の不在を実証（SEC-DOC-BOUND-01） | 約2MB・20,000カード文書が PUT 200（1.4s）・GET 3.2MB。backend に明示的な本文上限が無く、無界カード件数で DB 行が膨張し得る |
| 2026-08-12 | AI ルートの **fail-closed 挙動**（provider=none 時）をライブ検証 | `/ai/refine-card-text` → **構造化503**（`provider_unavailable`・provider/model/trace_id 付き・クラッシュなし）。AI 無効時に安全側で拒否されることを実証 |
| 2026-08-12 | 非Web検証経路（CLI/API 読/書・MCP）がローカル検証ハーネスに未統合 | `verify_all.sh` check 9 を追加（backend 稼働時のみ実行・不稼働時 SKIP）。API 読取3 + 書込7 + MCP not_found を実走行確認（DOGFOOD-06 規則の適用） |
| 2026-08-12 | 本番でも `/docs`・`/openapi.json`（全ルート・全ペイロードの偵察面）が無保護で公開（SEC-HEADERS-01） | **修正（案a）**: `enterprise-production`/`saas-multitenant` で無効化・`local-dev`/`evaluation` で維持。実機で prod 起動 OK・/docs と /openapi.json が 404 を確認 |
| 2026-08-12 | 多数カード文書（500枚）の API 応答性能を実測 | PUT 0.13s・GET **0.03s**・52KB応答。PERF-BUDGET（PB-2: 同期処理 100ms 超なし）に適合。API 経路の大規模文書性能を実証 |
| 2026-08-12 | MCP 投影経路の大規模文書（500カード）処理を実測 | `verify_mcp.ts` で 500カード文書を投影 → cards:500（safeMode で redacted:500）・bundleHash 計算・PASSED。MCP 経路も大規模文書を正常処理 |
| 2026-08-12 | MCP 検証経路がカード作業状態（holdState）を表示せず、生成AIが保留状態を読めない | `verify_mcp.ts` に holdState/counts 表示を追加。Hold/Critique文書（held2/shelved1）を実走行し `cards: 3 (held:2, pending:0, shelved:1)`・SafeModeでも holdState 投影を確認（DOGFOOD-08 の e2e 検証） |
| 2026-08-12 | 生成AIがMCPサーバへ接続するためのクライアント設定例が無い（「準備」の不足） | `03_Implement/mcp/README.md` に「Connecting a generative-AI MCP client」節を追加（stdio 設定例＋AI向け注意: 未レビュー非表示・holdState・HTTP/OAuth） |
| 2026-08-12 | MCP HTTP トランスポートのフルセッション（initialize→tools/list→tools/call）を検証したところ、2番目以降のリクエストが500（statelessモードで単一transportを再利用していた） | **修正**: `http_server.ts` を「リクエスト毎に fresh server+transport」へ変更（SDK要件）。`http_server.test.ts` にフルセッションe2eを追加（MCP 56 tests pass）。リモート生成AIが HTTP 経由でフルセッション可能に |
| 2026-08-12 | MCP HTTP 経路の**実エンドツーエンド**（mock IdP の実JWT + 実backend の実文書）を走行 | `scripts/dogfood_mcp_http_e2e.mjs` 追加。mock JWKS サーバ＋署名JWT＋MCP HTTP サーバ＋実backend文書で `get_context_projection` 成功（bundleHash・cards:1）。**生成AIがMCP HTTPで検証する経路が実証完了** |
| 2026-08-12 | L2/L3指標③（実API検証）の計測ハーネス `run_ai_eval.py --dry-run` を実行 | refine_card_text 10/10・suggest_island_summary 4/4 を stub provider でパイプライン検証（キー無し）。計測ハーネスが機能していることを確認（実API結果は `ai_eval_results.md`） |
| 2026-08-12 | MCP HTTP トランスポートの**レート制限（60 req/min）**を実走行検証 | mock IdP + 実JWT で70連続リクエスト → 60件が受理され**10件が 429**。レート制限制御が機能（THREAT_MODEL §6 の制御を実証・fail-closed） |
| 2026-08-13 | **backend の admin provisioning 面にレート制限を実装**（SEC-RATE-LIMIT-01） | `/admin/provision/*`（users/identity-providers/tenant-identity-providers）へ in-process・per-IP・60 req/min を適用。**61件目で 429 + Retry-After** を実機確認。MCP と対称になり非対称（issue の本題）を解消。フル backend 984 pass |
| 2026-08-13 | **P0: 未レビュー本文が API 境界で外部 LLM へ送出される**（SEC-AI-SAFEMODE-01） | **修正**: ADR-0068 D1=C/D2=B/D3=A を採択。backend `/ai/*` 6ルートが未レビュー本文を **422 拒否**（fail-closed）。frontend も事前ブロック＋「レビューしてから」案内。api.md/THREAT_MODEL 同期。**全 AC 完了** |
| 2026-08-13 | ドキュメントのサイズ/カード件数上限が無い（SEC-DOC-BOUND-01・実証済み） | **修正**: `KJ_ATLAS_MAX_DOCUMENT_BYTES`（既定20MiB）・`KJ_ATLAS_MAX_DOCUMENT_CARDS`（既定10,000）を設定ベースで導入（413 拒否） |
| 2026-08-13 | IR とキャンバスの関係型語彙ドリフト（AI-REL-VOCAB-DRIFT-01） | **修正（ADR-0069 D2=A）**: `llm_input_ir_spec.md` をキャンバス5値へ統一（`arrow`→`causal`・`negation`→`negate`） |
| 2026-08-12 | `check_contract_drift.py` が抽出漏れ（複数行デコレータ・空パス）＋形状正規化で実装ルートの63%を見落とし、`/ai/external-*` 3ルートの api.md 未記載を隠していた | **DX-CONTRACT-DRIFT-01** で修正（構造的照合・カナリア追加・実3ルートを api.md へ追記）。`check_design_consistency.py` も構造的照合へ書き換え（DX-DESIGN-CHECK-01）。backend 979 tests pass |
| 2026-08-12 | api.md 記述先行の未実装エンドポイント（`POST /ai/assess-card-importance`＝AI-ROUTE-01 MMR 計画タスク）が逆方向ドリフトとして存在 | api.md に「**未実装（計画）**」を明記（契約は実装前の正本として維持） |
| 2026-08-12 | AI ルートのルーティング＋監査の統合検証が無い | `test_ai_eval_pipeline.py::test_ai_route_emits_routing_audit_event` を追加 — /ai 実走行で `llm` 監査イベントが CE2-C5 項目で dispatcher へ出ることを固定（AI-ROUTE-01 AC-6 部分） |
| 2026-08-12 | W型探究（inquiry-bundles）の保存APIを実走行したところ local-dev で `503 tenant_admin_auth_unavailable`（SaaSセッション必須）・**frontend 呼び出し元なし**・`InquiryJourneyPrototypePanel` はプロトタイプのみ | **業務領域カバレッジ評価**: W型累積探究は「サポートL0: Planned」と整合（api.md §11 どおり）。API単体のdogfood不可。prototype→production 化の要件が判明 |
| 2026-08-13 | **W型 inquiry 保存 API を single-tenant 化**（G5・backend 側） | `_trusted_session` を `tenant_session_precondition_required` で分岐し、local-dev でも保存・読込・削除が可能に。実機 `POST 204 / GET 200 roundtrip / DELETE 204`。テストフィクスチャを header 由来 identity に改修（6 tests pass）。**frontend 接続（client+UI）は残** |
| 2026-08-12 | `saas-multitenant` の起動ゲートが fail-fast で機能することを実地確認（必須アダプタ欠損→起動拒否） | `adopting-org-patterns.md` §4 に実地確認を記録 |
| 2026-08-12 | Org-Bパターン（Hold/Critique週跨ぎ）を実走行。API保存→再読込で作業状態が完全維持（held2/shelved1/critiqued2） | `adopting-org-patterns.md` §3.6 に記録 |
| 2026-08-12 | MCP/外部プロジェクションが Hold/Critique 作業状態をスキーマごと落とす（AI協働の基本情報欠落） | `issue-DOGFOOD-08`起票（三要素分析済み・P2） |
| 2026-08-12 | DOGFOOD-08 の修正案（`ProjectedCard` へ holdState 追加・critique は SafeMode 判断と分離）を具体化 | `issue-DOGFOOD-08`に修正案追記（proposal-only・反スコアリング語彙との衝突なしを確認） |
| 2026-08-13 | **inquiry-bundle CAS ライフサイクルを実API経路で検証**（CLI/API経路の拡充） | `verify_api_inquiry.sh` を新設 — create(If-None-Match 201)→read→update(If-Match 204)→stale 409→欠損428→不正422→delete 204→re-delete 409 の17チェックを実走行（**17 pass**）。DOGFOOD-06規約（成功＋異常系）に準拠し `verify_all.sh` check 9 へ統合（read/write/inquiry/MCP の4経路化） |
| 2026-08-13 | MCP HTTP 経路のフルセッションe2eを実backend・実DBで再確認 | `dogfood_mcp_http_e2e.mjs`（mock IdP＋実JWT）を live 走行 — initialize→tools/list→tools/call が成功。生成AIがMCP HTTPで検証する経路の実証が継続 |
| 2026-08-13 | **local main の alembic lineage が broken**（0027が存在しない0026を参照 → `alembic heads` KeyError・バックエンド起動不能） | 0027のdown_revisionを0026（マージ済み）へ再チェーンで修復（0025→0026→0027の単一head）。migration追加と検証経路の前提（DB=head）の関係が **DOGFOOD-09** として浮上 |
| 2026-08-13 | 出荷中不変条件違反: 画面の「健全性 N%」・接続スコア・impact等級（DOMAIN-SCORING-SURFACE-01・P1） | **修正（案A）**: `health`(0-100)削除・Q007中立事実化・**Q009**（ゼロ孤立カード＝forced grouping警告）追加・connectivityScore/impactバッジ/高影響フィルタ撤去・UI反スコアリング検査をテスト固定。frontend 1439 tests pass |
| 2026-08-13 | 検証ハーネスが DB migration 未適用を 500 としてしか見せない | `issue-DOGFOOD-09`起票（P2）: `verify_all.sh` check 9 が前提（DB=alembic head）を事前検査する案。`alembic upgrade head` 後に 17/17 pass へ回復した実地記録 |
| 2026-08-14 | **管理面の認可分離が不完成**（両キー設定時に admin キー単独で 401・a2a3-gate:validate は業務キーで 200） | `issue-SEC-ADMIN-PLANE-02`起票（P1）→ **修正（D-a）**: `require_api_key` middleware が `/admin/` を業務キー要求から除外、a2a3-gate:validate へ `require_control_plane_authorization` を追加。両キー設定実機で「adminキー単独 200/201・業務キー単独 401」を確認 |
| 2026-08-14 | **管理面 CLI/API 経路の検証スクリプトが無い** | `verify_api_admin.sh` を新設 — a2a3-gate（200/409/401）・provision/users（201/401）・業務/管理キー分離をプローブベースでモード判定し検証。`verify_all.sh` check 9 へ統合（5経路化） |
| 2026-08-14 | `verify_all.sh` check 9 が DB migration 未適用時に無意味な 500 を羅列する（DOGFOOD-09 対応） | **修正**: check 9 冒頭で `alembic current` vs `heads` を比較し、不一致時は「migrations not applied — run alembic upgrade head」と報告して SKIP。500 羅列を解消 |
| 2026-08-14 | ADR-0074 policy 要件追加後に `test_admin_identity_provider_registration.py` が追随していない（`TrustedSaasRuntimePolicy.validate()` が新しい必須フィールドを要求） | **修正**: テストの policy 構築へ `saas_oauth_broker_http_authorize_endpoint` / `saas_auth_session_hash_key` を追加。`test_trusted_saas_runtime.py` と整合 |
| 2026-08-14 | MCP HTTP e2e が固定ポート（8788/8799）依存で CI 並走に弱い | `dogfood_mcp_http_e2e.mjs` を**動的エフェメラルポート**へ変更（freePort）。`verify_all.sh` check 9 の MCP HTTP 経路として統合（生成AIのMCP検証経路の継続的検証） |
| 2026-08-14 | **観測基盤が存在しない**（OPS-OBSERV-01・P1、方向性レビュー優先1） | **修正（項目1〜4＋文書）**: `logging_config.py`（JSON formatter が `extra` ペイロードを描画・`KJ_ATLAS_LOG_LEVEL`）・リクエストID middleware（`X-Request-Id` エコー・ログ/エラーボディへ注入・inbound `x-trace-id` 尊重）・`/readyz`（`SELECT 1` + `alembic_version`×heads、DB停止/スキーマ齟齬で503）・`/version` + `KJ_ATLAS_APP_REVISION` 配線（Dockerfile/compose/registry）。`04_Documentation/observability.md` 新設。実走行でログの `requestId` == レスポンス `X-Request-Id` を確認 |
| 2026-08-14 | **ナラティブ検査が A/B 照合の方向と件数を落としている**（KJ-AB-CROSS-CHECK-01・方向性レビュー優先3） | **修正（D-a）**: `NarrativeCheckIssue.direction`（`b_missing_in_a`/`a_missing_in_b`）と `NarrativeCheck.counts` を追加。prompt に A/B 双方向照合＋件数報告を要求（`kj_technique.md:180-186`）。TS/Python/schemas を同期し drift test の TYPE_MAP へ追加。SafeMode は構造値を preserve。frontend 1440 tests・backend 81 tests 通過 |
| 2026-08-14 | **実行時プロンプトが ai_kj_execution_procedures.md と乖離**（KJ-PROMPT-ALIGN-01・方向性レビュー優先3-4） | **修正（実装のみ）**: `refine_card_text` に名詞止め禁止・`suggest_card_groups` から「thematic」除去＋2〜3枚制約/孤立カード非強制/訴えの類似性・`suggest_island_summary` に表札検査（転置/戻し）＋代弁/名詞止め禁止・`generate_narrative` に A/B照合自己実行を追加。`test_ai_prompt.py` に4テスト追加（20 tests pass） |
| 2026-08-14 | **文書に空白（voids）を保持する場所が無い**（KJ-VOIDS-01・方向性レビュー優先3-1） | **修正（D-a）**: `DocumentV1.voids?: VoidEntry[]` を追加し、`detectVoidCandidates`（5種の構造ルールで決定論的検出・ゼロ空白警告）を新設。UI に「空白を検出」ボタン、SafeMode は title/detail redact・構造値 preserve。schemas/Pydantic/drift test/validate を同期。frontend 1446 tests・backend 61 tests 通過 |
| 2026-08-14 | **表札の戻し検査（カード→表札の異議）が再提案に反映されない**（KJ-PLACARD-RETURN-CHECK-01・方向性レビュー優先3-3） | **修正（D-a・既存 critiqueTags 再利用）**: メンバーカードの `not_the_same`/`feels_off` を島要約 prompt で「前の表札に異議」として明示し、再提案に反映。UI に戻し検査のヒント追加。これで**優先3（検査の実装）4項目すべて完了** |
| 2026-08-14 | **生成AIがMCPで検証する経路の準備が不足**（MCP-PREP-01・DOGFOOD-03/06/08系譜） | **拡張**: `context-projection.v1` に `voids`（KJ-VOIDS-01）と `narrativeChecks`（KJ-AB-CROSS-CHECK-01）を構造値として追加。`verify_mcp.ts` に状態表示、MCP README に検証runbook（7シナリオ）を追加。`verify_api.sh` に `/readyz`・`/version` を追加（5チェック）。frontend 1448 tests・MCP 56 tests・実走行で void 1件/ナラティブ方向 1件 を MCP 経由で確認 |
| 2026-08-14 | **プログラム第3〜第5反復に対応する issue が1件も存在しない**（方向性レビュー優先4・計画起票） | `PGM-ITER-03-01`（共同編集の並行性モデル選定に必要な外部比較調査 — Miro/Notion/Figma/Slack/Atlassian）・`PGM-ITER-04-01`（成果物の複数化スコープ）・`PGM-ITER-05-01`（テナント間連携スコープ）を起票。三要素チェックリストに **B5（無効化時の振る舞い）** を追加（program §7-3） |
| 2026-08-14 | **PGM-ITER-03-01 の外部比較調査を実行**（第3反復の並行性モデル選定をアンブロック） | deep-research（105エージェント・108主張を3票反証検証）で Figma（サーバ権威LWW・OT却下・DynamoDB journal）・Miro（単一owner・5段階ロール）・Confluence（保存時手動merge・CONFSERVER-32286履歴破損）を検証。設計正本 `collaboration-concurrency-comparison-2026-08-14.html` として記録し、**サーバ権威LWW＋既存CAS（選択肢A）を推奨**。Notion/Slack/Jiraは一次ソース未確認（open questions） |
| 2026-08-14 | **W型探究の保持期限・purge契約が未定義**（DATA-INQUIRY-RETENTION-01・AC-11） | **D1=案Aを採択**（自動期限なし・明示DELETEまで永続）。非保証を api.md / frontend UI（`retention_note`）/ 運用文書へ明記。`verify_api_inquiry_journey.sh` を新設 — 現実的なW型journey（2→3ラウンド・handoff・fieldwork）の opaque round-trip を CAS 経由で検証（**14 pass**・業務領域カバレッジ実証） |
| 2026-08-14 | **テナント分離の二層防御が一度も同時検証されていない**（QA-TENANT-ISOLATION-01・P1） | **修正**: `test_tenant_isolation_postgres_rls.py` を新設 — 実際のHTTP経路を PostgreSQL + runtime role（NOBYPASSRLS）で実行し、**アプリ層WHEREフィルタとRLSが同時に発火**することを固定（tenant A書込→tenant B読取404）。カナリア（生SELECTでRLS単独が越境を止める）も追加。`-m postgres` でCIのPostgreSQL matrixに自動組み込み。THREAT_MODEL留保を解消。fresh DBで6 pass |
