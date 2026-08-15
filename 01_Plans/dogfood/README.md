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
| 2026-08-14 | **クライアント供給の x-auth-roles/groups が外部PDPへ転送される**（SEC-AUTH-ATTRIB-01・P1・QA-TENANT-ISOLATION-01周辺観測） | **修正（D-a）**: `_authorize_request` がクライアントヘッダを読まず、検証済みidentity（現状は空）の roles/groups のみをPDPへ送る（fail-closed）。`CapturingAdapter` テストでクライアント供給rolesがPDPに到達しないことを固定。回帰85 tests pass |
| 2026-08-14 | **廃止機能の残存参照の棚卸し（DX-CANON-INTENT-01 AC-3〜5）** | 実残存 `settings.py:295`（削除済みタスクを列挙するコメント）を修正。`canvas-projection-asymmetry`（2026-08-09日付分析）の3箇所に廃止注記を追加。`contract_reading_guide.md` §5-6 に廃止宣言の規約を明記（**案A: api.md内レジストリを採択**）。DX-CANON-INTENT-01 を Done 化 |
| 2026-08-15 | **documentsに主体と生涯が無い（DATA-DOC-LIFECYCLE-01・第2反復の起点・ADR-0073採択で着手可能に）** | **実装（データ次元）**: `DocumentRow` に `created_by`（nullable・不変）と `lifecycle_state`（active/archived）を追加。migration `20260815_0028`・persistence shapes・`save` の create時のみ設定・`put_document` からidentityを渡す。docs回帰57 tests・migration roundtrip pass。機能/UI次元（キャンバス一覧・アーカイブUI）は別issue |
| 2026-08-15 | **documentの楽観的並行制御（ETag/If-Match）がCLI/API検証経路に未統合** | `verify_api_write.sh` を拡張（7→**10チェック**）: GET が ETag を返す・現在の If-Match で PUT 成功・**stale If-Match で 409**（lost-update防止）を固定。DOGFOOD-06規約（成功＋異常系）準拠 |
| 2026-08-15 | **第3反復（共同編集）の並行性モデルが未選定**（PGM-ITER-03-01・方向性レビュー優先0） | **ADR-0076（Proposed）を起票** — 外部比較調査（Figmaサーバ権威LWW・Confluence手動merge・OT/CRDT論争）に基づき **D1=A（サーバ権威LWW＋既存CAS拡張）を推奨**。SafeMode・tenant境界のサーバ集中を保ち、新規並行制御機構を導入しない。採択は保守者の明示判断待ち |
| 2026-08-15 | **AIルートのfail-closed挙動がCLI/API検証経路に未統合** | `verify_api_ai.sh` を新設 — **未レビュー本文→422**（SEC-AI-SAFEMODE-01・ADR-0068）と **provider=none→構造化503**（`provider_unavailable`・trace_id付き・crashなし）を固定。`verify_all.sh` check 9 へ統合（7経路化）。実走行4 pass |
| 2026-08-15 | **documents一覧（GET /docs）が無く、キャンバス一覧の土台が無い**（第2反復機能次元） | **実装**: `GET /docs` 一覧APIを新設（tenant-scoped・行メタデータのみ・本文カードは非露出・`updated_at`降順）。`/docs` はdocuments APIが所有しSwagger UIを `/api-docs` へ移動。`verify_api.sh` に一覧チェックを追加（7 pass）。docs回帰66 tests pass |
| 2026-08-15 | **キャンバス一覧がrecent-idのみで全文書（タイトル付き）を表示できない**（第2反復機能次元のUI） | **実装**: `client.ts` に `listDocuments()` を追加し、`RecentDocumentsDialog` を拡張 — **GET /docs の全文書（タイトル・アーカイブ表示）**を recent-id の上に表示。App.tsx がダイアログ表示時に一覧をフェッチ。clientテスト2件追加（frontend 1450 tests pass） |
| 2026-08-15 | **lifecycle_state を遷移する操作が無い**（ADR-0073 D2=A の機能化・キャンバス無効化） | **実装**: `POST /docs/{id}/archive` / `unarchive`（tenant-scoped・204・欠損404）を追加。`verify_api_write.sh` にアーカイブ検証（13チェック）。docs回帰36 tests pass |
| 2026-08-15 | **「自分の文書」で絞り込めない**（キャンバス一覧・管理の残要件） | **実装**: `GET /docs?createdBy=` フィルタを追加（`created_by=NULL` の移行文書は一致しない）。frontend に「自分の文書のみ」トグルを追加（`storageScope.principalId` を渡す）。client/backendテスト追加（frontend 1451・backend 37 tests pass） |
| 2026-08-15 | **生成AIがMCPで文書lifecycle（created_by/archived）を検証できない**（MCP-PREP-01拡張） | **実装**: MCPの`get_context_projection`結果に`documentMetadata`（lifecycle_state・created_by）を追加（第2反復・ADR-0073のMCP検証）。`fetchDocumentMetadata`はadvisory（失敗時null・主投影を壊さない）。runbookにlifecycleシナリオ追加。MCP 58 tests pass・実走行で`lifecycle: active ✅` |
| 2026-08-15 | **rolesがfail-closed（空）のままでserver導出が無い**（SEC-AUTH-ATTRIB-01完結） | **実装**: `UserRow.roles`（server-verified）を追加し、`POST /admin/provision/users` が `roles` を受理・保存。`resolve_identity_context` が user row から roles を導出（**クライアントヘッダ非依存**）。`CapturingAdapter` テストで provisioned roles が運ばれ、クライアント供給 `x-auth-roles` が無視されることを固定。回帰90 tests pass |
| 2026-08-15 | **AIが論理構造（edges・evidenceLinks）を受け取っていない**（ADR-0069・方向性レビュー優先0） | **実装（一部）**: `generate-narrative` prompt に**型付き論理関係**（edgesの島間語彙・evidenceLinksのsupports/contradicts）を注入 — 叙述の骨格（因果・対立）を推測でなく使う。`detect-contradiction` はdoc context無しのため別途（契約変更を要する）。promptテスト追加（AI回帰42 tests pass） |
| 2026-08-15 | **非Web検証ハーネス全体を実走行してギャップを発見**（ドッグフーディングループ） | CLI 6経路58チェック＋MCP stdio/HTTP全PASS。**runbookの「bundle決定性」シナリオがverify_mcp.tsで未検証のギャップを発見** → 2回呼んでbundleHash一致を検証するよう拡張。これでrunbookの8シナリオすべてがverify_mcp.tsでカバー（MCP 58 tests pass） |
| 2026-08-15 | **island-summaryの表札が島の構造的位置を反映しない**（ADR-0069続き） | **実装**: `suggest-island-summary` prompt に**島の型付き関係**（他島とのcausal/negate等エッジ）を注入 — 表札が島の論理的位置を反映。promptテスト追加（AI回帰43 tests pass） |
| 2026-08-15 | **アーカイブ操作がbackendのみでUIに未配線**（第2反復UI完結） | **実装**: `client.ts` に `archiveDocument`/`unarchiveDocument`、`RecentDocumentsDialog` にアーカイブ/解除ボタン、App.tsx にtenant session wrapper経由のハンドラ＋一覧再フェッチ。frontend 1451 tests pass |
| 2026-08-15 | **キャンバス一覧UIのE2Eが無い**（第2反復UIの実証不足・検証経路の拡充） | **実装**: `e2e/recent_documents_dialog.spec.ts` に「canvas list」テストを追加 — **GET /docs 全文書（タイトル・archived表示）＋ Archive が `POST /docs/{id}/archive` を呼ぶ**ことを実走行で固定。Playwrightの `getByRole name` が**部分一致（大文字小文字無視）**のため `{ name: "Archive" }` が Archive/Unarchive 両ボタンに解決する strict-mode 失敗を発見 → `exact: true` で修正。recent_documents_dialog 6 tests pass |
| 2026-08-15 | **アーカイブ済み文書が編集可能なまま**（ADR-0073 D2=A に歯が無い: 一覧マーカーでしかなく業務次元の制約がない） | **実装（fail-closed）**: `PUT /docs/{id}` が `lifecycle_state=archived` の文書を **423 Locked（code `document_archived`）** で拒否（ETag一致でも拒否）。GETは200のまま（読取・監査は可、payload非変更のaudit系writeは許可）。backend unit test（アーカイブ→PUT 423・内容不変→unarchive→PUT 200）＋ **`verify_api_write.sh` を13→15チェックに拡張**（アーカイブ中PUT→423・解除後PUT→200）を実走行で固定。frontend は 423 を「アーカイブ済み・読み取り専用」の平易な status message に変換（en/ja）。backend 55 tests・frontend 1451 tests pass |
| 2026-08-15 | **全backend suite が第2反復の route 追加以来 RED**（iteration 28で検証を部分回帰でしか行わず、`test_tenant_session_precondition.py` の静的AST検査が新規routeを未認識） | **修正**: ① `/docs` 一覧が直接呼ぶ `_resolve_request_tenant` と、archive/unarchive が委譲する `_transition_lifecycle` を tenant-scoped boundary として承認 ② Swagger 移動（`/docs`→`/api-docs`・`/redoc`→`/api-redoc`）を `_NON_API_ROUTE_PATHS` に反映。**13→13 tests pass（全 suite 1101 passed へ回復）**。※検証経路として「部分回帰だけでなく full suite もCIで固定する」必要が再確認された（DOGFOOD-06の教訓の再発） |
| 2026-08-15 | **アーカイブ済み文書を開いても編集モードのまま**（423は保存時にしか効かず、開いた時点で読み取り専用にならない・第2反復UX完結） | **実装（proactive review-only）**: キャンバス一覧の `lifecycle_state=archived` を開く時に `isActiveDocumentArchived` を立てて既存の `isReadOnly` ゲートへ合流（開いた瞬間から全編集無効・読み取り専用バナー表示）。一覧から active を開く/アーカイブ解除/他経路のロードで解除。E2E 追加（active を開くとバナー無し・archived を開くと `[data-ui-region="read-only-banner"]` 表示）。frontend 1451 tests・recent_documents_dialog 7 tests pass |
| 2026-08-15 | **isReadOnly の実行時反転が mount-only effect を再実行し、開いた文書が既定文書に戻る**（FB-RM-UX-01の修復が `loadDocument` と `applyImportedViewMetadata` に未適用の潜伏バグ） | **修正**: `applyResolvedLocaleForView` は `[isReadOnly, locationSearch]` に依存するため、archived を開いて isReadOnly が反転すると `loadPublicPack`/`loadDocument`（mount effect の deps）が再生成→ `loadForMount` が既定文書を再ロード。既存の ref パターンを `loadDocument` と `applyImportedViewMetadata` へ延長して isReadOnly 非依存の安定 identity 化。E2E が2回の既定文書再取得（state revert）として実証し、修正後は不要な取得が消える |
| 2026-08-15 | **全非Web検証ハーネスを実走行して全体整合を確認**（結果分析） | `verify_all.sh` 17チェック全PASS（syntax・lint・unit/integration・docs・API読7・書15・AI fail-closed・inquiry CAS・W型journey・admin plane・MCP stdio/HTTP）を実走行。iteration 30の「archived write-block 423」がCLIハーネスとMCP経路で整合することを確認 |
| 2026-08-15 | **生成AI検証経路が archived 読み取り専用契約を未カバー**（iteration 30の新規契約をMCP runbookが未記載） | **拡充**: `verify_mcp.ts` の lifecycle 検査を強化（`lifecycle_state` を enum 検証＋archived時は「PUTは423で拒否・verify_api_write.sh で検証」を明示）。MCP README runbook に「archived read-only」シナリオを追加（HTTP write契約を横断検証可能と明記）。active/archived 両状態を実走行で確認（MCP 58 tests pass） |
| 2026-08-15 | **`app.toolbar.import_doc_json_legacy` がproduction未使用のままtestに直結**（FB-RM-I18N-06・孤立キー監査の判断保留） | **解決**: 案(a)を採択 — テストを実使用中の `_short` キー（en "Import JSON"・ja "JSON取り込み"）へ差し替え、legacyキーをカタログから削除。`export_legacy`・`trace.export_analytics` は実使用中なので維持。i18n 71 tests・frontend 1451 tests・typecheck pass |
| 2026-08-15 | **全AC完了なのに非Doneのままのissueが11件**（結果分析・計画在庫の正確性） | **棚卸し**: AC全`[x]`かつStatus≠Doneを機械抽出 → **11件をDoneへ更新**（DATA-DOC-LIFECYCLE-01・KJ-AB-CROSS-CHECK-01・KJ-PLACARD-RETURN-CHECK-01・KJ-PROMPT-ALIGN-01・KJ-VOIDS-01・MCP-PREP-01・SEC-AUTH-ATTRIB-01・OPS-OBSERV-01・FB-RM-I18N-06・PGM-ITER-03-01・SEC-RATE-LIMIT-01）。**これで第2反復（DATA-DOC-LIFECYCLE-01）が公式にクローズ**。残るOpen/Draftは実装または判断待ちの真の在庫 |
| 2026-08-15 | **折りたたみ島のピーク操作がwindowリスナー依存で蓄積・固着しうる**（UI-CANVAS-01・P2） | **修正**: ピークボタンの `window.addEventListener("mouseup", ..., { once: true })` を廃止し、CanvasShell が確立済みの `setPointerCapture` + `onPointerUp`/`onPointerCancel` へ移行（touch→scroll の `pointercancel` でも `onPeekEnd` が発火）。window リスナー非登録化で蓄積は構造的に不可能に。App 側の補助 mouseup リスナーは cleanup 付きのため無害と確認。full suite 1451 tests pass（自動化の未実施理由はissueに記録・jsdom 未導入のため構造検証＋回帰で固定） |
| 2026-08-15 | **context-audit/export-auditが再送・二重クリックで重複イベントを外部へ送出**（SEC-AUDIT-DUP-01・監査完全性） | **実装（案b・サーバー側dedup）**: `AuditDispatcher.emit` に bounded dedup（論理キー・LRU上限4096・`KJ_ATLAS_AUDIT_DEDUP_WINDOW_SECONDS`既定5秒）を追加。送信成功時のみ記録（失敗後の再送を誤抑制しない）＋未達キー追跡で「失敗→再送」も重複送出なし。context-audit/export-audit が論理キーを渡し、api.md に仕様明記。unit 5件＋統合2件追加（backend 18+26 tests pass） |
| 2026-08-15 | **エージェント取込レビュー一覧が無制限に蓄積**（FB-RM-UX-02・EXT-AGENT-02の回帰） | **実装**: `boundResolvedAgentImportedProposalReviews`（pending全保持・解決済みは直近50件）を `handleParseAgentResponse` の append 時に適用。未対応のpendingを失わない排出方針を採択。unit 3件追加（frontend 1453 tests pass） |
| 2026-08-15 | **provision_usersの必須空チェックが400で他と不一致**（SEC-HTTP-01・ステータスコード一貫性） | **解決**: §4 taxonomyを明文化（400＝トランスポート/パース境界のみ・422＝ドメイン契約違反）し、provision_usersの空チェックを 400→422 へ統一（ai.py/ai_relations.py と同クラス）。api.md §4・§9.3整合。test 2件更新（backend 19+31 tests・docs-check pass） |
| 2026-08-15 | **管理面操作の監査証跡が存在しない**（SEC-ADMIN-PLANE-01 AC-5・P0・三要素設計で起票→実装） | **実装**: `SEC-ADMIN-PLANE-03` を三要素分析で起票し D1〜D5 採択 → `admin_audit_events` テーブル（migration 0030）＋記録middleware（/admin/* の許可/拒否・fail-open・admin key FP）＋`GET /admin/provision/audit`（control-plane認可・allowlist・composite cursor・limit100/500）。`verify_api_admin.sh` 10/10実走行・`test_admin_audit_trail.py` 5件＋admin回帰67件・docs-check pass。**これで SEC-ADMIN-PLANE-01 が全ACクローズ** |
| 2026-08-15 | **標準業務フローが E2E で固定されていない＋AI が課金APIに依存**（新指令: シナリオ拡大・ローカルLLM縮退） | **実装**: `verify_business_flow_e2e.sh`（7チェック）で**定性調査アナリストの KJ 整理フロー**を固定（文書作成→読戻し→refine→島の表札→ナラティブ→未レビュー境界422）。`KJ_ATLAS_LLM_PROVIDER=local` + `KJ_ATLAS_LOCAL_LLM_BASE_URL` → `deploy/tools/mock_local_llm.py`（GPU不要・無料・決定的）で**課金API（DeepSeek）へ依存しない縮退**を実現。`mock_local_llm.py` の島表札 grounding をメンバーカード3件まで強化。シナリオテンプレート（業態/人物/領域/操作/注意事項）とスイッチ機構を `dogfood/business-flow-e2e-scenarios-2026-08-15.md` に起票。7/7 pass |
| 2026-08-15 | **別業態の標準業務フローを追加**（シナリオ拡大・iteration 42） | **実装**: **新規事業企画ワークショップ（ファシリテーター）** シナリオを `verify_business_flow_e2e.sh` に追加（suggest-card-groups の発言束ね提案を新規固定）。E2E を**新規 migration 済み temp DB** で実行するよう自己完結化（決定性向上）。`mock_local_llm.py` のカード行正規表現が前空白を許容（card-groups プロンプトはインデント有）。**10/10 pass** |
| 2026-08-15 | **人間×生成AIの多ラウンド協調KJを実API（DeepSeek）で検証できない**（DOMAIN-KJ-COLLAB-01・iteration 43） | **実装**: `verify_kj_multi_round.sh` を新設 — **R1発散（束ね提案）→R2構造化（表札提案）→R3深化（文面+ナラティブ草稿）** の協調ループを 7 チェックで固定。`KJ_ATLAS_DEEPSEEK_API_KEY` 設定時は実API・未設定時はローカルモックへ自動縮退。**DeepSeek wiring を検証**（Settings 認証・`get_provider()` が DeepSeekProvider 解決）。モック実走行 7/7 pass。実API runbook を issue に文書化（キー利用可能時に実走行して「結論の深化」を観測する） |
| 2026-08-15 | **CE4監査追跡辞書がプロセス寿命全体で無制限に蓄積**（DX-BACKEND-CE4-01・P3） | **実装（案a・TTL/eviction）**: `_Ce4AuditTrackerState` に `last_touched` を追加し、`_record_ce4_event_and_validate_completeness` が256件ごとに **TTL 24h＋LRU上限10,000** で bounded化（単一ワークセッション内で完結するCE4シーケンスを誤evictしない十分な余裕）。CE4完全性チェックの挙動は不変。unit 2件追加（CE4監査統合 28 tests pass） |
| 2026-08-15 | **並行実装された観測基盤のマージを解決**（OPS-OBSERV-01・`origin/feat/ops-observ-01-runtime-observability` マージ） | **解決**: HEAD 側 `logging_config.py`＋main.py 内蔵実装 と ブランチ側 `observability.py` モジュール実装が**並行実装**だった。ブランチ側（redaction・uvicorn配線・`/version` allowlist・checks-dict `/readyz`）を正として統合し `logging_config.py` を廃止。HEAD 側の後発機能（model-registry・admin-plane audit・OAuth broker・SEC-ADMIN-PLANE-02 skip・catch-all 500・`/api-docs`）を再適用。**ミドルウェア登録順のバグを実走行で検出**（`assign_request_id` を最後に登録しないと 401/422 ボディへ requestId が載らない）→ 修正。observability 26 tests pass・フル回帰確認中 |
| 2026-08-15 | **別業態の標準業務フローを追加**（シナリオ拡大・iteration 44） | **実装**: **カスタマーサポート品質管理（サポート品質マネージャー・クレーム真因分析）** シナリオを `verify_business_flow_e2e.sh` に追加 — **detect-contradiction（証言間の論理的矛盾をAI検出）を新規固定**（island-summary とあわせ4チェック追加）。業態=品質管理・操作=矛盾検出とカバー領域を拡大。**14/14 pass**。シナリオ3の注意事項（矛盾検出は「単なる相違」と「論理的矛盾」を区別）を `business-flow-e2e-scenarios-2026-08-15.md` に起票 |
| 2026-08-15 | **文書非依存AIルートが未レビュー本文をLLMへ送れる**（SEC-AI-SAFEMODE-01 の残余・iteration 44で実機検証） | **起票**: `detect-contradiction` に未レビュー本文のカードを送ると **200** でLLM（モック）へプロンプトが送信されることを実機確認（`suggest-island-summary` の422と非対称）。SEC-AI-SAFEMODE-01 の SafeMode ゲートは6ルート配線で、doc非依存3ルート（detect-contradiction / suggest-card-groups / refine-card-text）はレビュー検査なし。**`SEC-AI-SAFEMODE-02` を三要素分析で起票**（P1・案a=リクエストへ allowUnreviewedText 追加で422 / 案b=適用範囲を明示 / 案c=AI-IR-PROJECTION-01 AC-4へ委譲） |
| 2026-08-15 | **文書非依存AIルートのSafeMode境界穴を修正**（SEC-AI-SAFEMODE-02・関連課題対応・iteration 45） | **実装（案a）**: `_CardRef` / `RefineCardTextRequest` に `textReviewed`（既定 **false = fail-closed**、ADR-0068 D3=A）と `allowUnreviewedText`（`KJ_ATLAS_ALLOW_UNREVIEWED_AI_TEXT` ゲート）を追加。`routes/ai.py` に `_reject_unreviewed_cards` を新設し3ルート（detect-contradiction / suggest-card-groups / refine-card-text）へ配線。`test_ai_safemode.py` +5テスト（9 pass）。呼出側（E2Eシナリオ1〜3・verify_kj_multi_round・run_ai_eval・pipeline test）へ `textReviewed:true` を追加。**E2E 15/15 pass（未レビュー→422 の負例を固定）**・api.md に契約明記 |
| 2026-08-15 | **管理者のCLI/API運用フローを固定**（非Web経路の拡充・シナリオ4・iteration 45） | **実装**: `verify_admin_ops_flow_e2e.sh` を新設 — 業務キー＋管理キー両方設定の実バックエンド上で**文書ライフサイクル**（一覧→作成→アーカイブ→アーカイブ中書込 **423** →解除→書込）と**管理面監査**（専用キーで 200・業務キーで 401）・**キー分離の双方向**（/docs を管理キーで 401）を **11/11 pass** で固定。シナリオ4として `business-flow-e2e-scenarios-2026-08-15.md` に起票 |
| 2026-08-15 | **生成AIのMCP検証経路をマージ後バックエンドで確認**（非Web経路の拡充・iteration 45） | **検証**: `verify_mcp.ts`（stdio・get_context_projection）をマージ後バックエンド＋SEC-AI-SAFEMODE-02 適用後の実機で実行 — bundleHash 決定性・lifecycle active・scoring語彙なし・reviewed/unreviewed 集計を **PASSED**。生成AIがMCPで検証する経路が回帰していないことを確認 |
| 2026-08-15 | **別業態の標準業務フローを追加**（シナリオ拡大・iteration 46） | **実装**: **報道・編集（編集者・ナラティブのA/B照合検証）** シナリオを `verify_business_flow_e2e.sh` に追加 — **check-narrative（A/B照合）を新規固定**（generate-narrative→check-narrative→未レビュー422 の4チェック）。AI 操作カバーは **6操作**（refine / island-summary / narrative / card-groups / detect-contradiction / check-narrative）に拡大。**19/19 pass** |
| 2026-08-15 | **check-narrative の api.md 契約が実装と乖離**（逆方向ドリフト・iteration 46で発見） | **修正**: `POST /ai/check-narrative` の api.md 記述が `narrative: Narrative`（オブジェクト）と書かれていたが、実装は `narrativeText: string`＋`basedOnReadingOrder?`（`CheckNarrativeRequest`）。E2E シナリオ5の実走行で 422（`narrative` は extra_forbidden）として検出 → **api.md を実装へ整合**（G4/G6 の逆方向ドリフト監査と同型の実地例） |
| 2026-08-15 | **W型探究を業務フローとして固定**（シナリオ拡大・iteration 47） | **実装**: **調査研究員のW型探究** シナリオを `verify_business_flow_e2e.sh` に追加 — ジャーニー開始(If-None-Match:* →201+ETag) → 読戻し → **ラウンド深化(If-Match →204)** → **並行編集の検出(古いIf-Match →409)** → 前条件なし428 → **破棄もCAS(If-Match 必須)** を固定。**DELETE が CAS 必須であることを実走行で発見**（初回は 428 で失敗 → 現在 ETag で 204 を確認）。**26/26 pass**（シナリオ1〜6）。シナリオ6として `business-flow-e2e-scenarios-2026-08-15.md` に起票 |
| 2026-08-15 | **DOGFOOD-09 の pre-check に空DBの穴**（関連課題対応・iteration 48） | **修正**: `verify_all.sh` の migration pre-check は `alembic current` が**空**（`alembic_version` 行なし＝未適用）のとき `[ -n "$cur" ]` ガードで発火せず、未適用DBへAPI検証を流して500羅列を再発させ得ることを発見。`cur` 空を `none` へ正規化し **空DB→SKIP・適用済み→RUN** を実機確認。**DOGFOOD-09 を Done 化**（AC 全[x]） |
| 2026-08-15 | **モデル統制の MMR-04 を実装**（AI-MODEL-GOVERNANCE-01・iteration 49） | **実装**: `get_available_models` が `_is_user_selectable_model`（intermediate/generate 層のみ）でフィルタし、**final_judgement 専用モデルを選択子から除外**（check_narrative / detect_contradiction 等は管理者ポリシー固定）。`test_available_models_excludes_final_judgement_only`。governance 9件 pass |
| 2026-08-15 | **モデル選択子を初期タイトル生成へ横展開**（R2 UI・iteration 48） | **実装**: `DocumentTitleEditor` に `ModelSelector` を露出（`data-ui-region="model-selector-title"`）。`suggestDocumentTitle` へ `model` 追加し `/ai/suggest-document-title` 経由で backend allowlist 強制（403）が効く。frontend 1456 tests pass |
| 2026-08-15 | **モデル選択子をナラティブ生成へ横展開**（R2 UI・iteration 50） | **実装**: `NarrativesPanel` に `ModelSelector` を露出（`model-selector-narrative`）。`generateNarrative` へ `model` 追加し `/ai/generate-narrative` 経由で allowlist 強制。R2 UI は**島表札・初期タイトル・ナラティブ**の3操作をカバー（文面整え/束ね提案は UI 未露出のため選択子対象外）。frontend 1456 tests pass |
| 2026-08-15 | **member_groups データモデル設計を記録**（Phase 2 土台・iteration 51） | **設計**: `member_groups` / `member_group_members` / `member_group_model_allowlist`（tenant-scoped・RLS）と実効モデル解決（所属グループallowlist交差→テナント→タスク階層→既定）への組み込みを issue に確定。**AI-MODEL-GOVERNANCE-01 が全 AC 完了**（docs-check・backend 46・frontend 1456 検証） |
| 2026-08-15 | **学術研究・島間関係の要約をE2E固定**（シナリオ7・iteration 52） | **実装**: **学術研究/ナレッジマネジメント（研究者・概念間の関係構造化）** シナリオを追加 — `summarize-island-relation`（5語彙・derived=false 根拠付き接続）＋未レビュー境界422。**29/29 pass**（シナリオ1〜7・7業態）。最初のE2Eで未レビューが200になる事象はデバッグ用バックエンド残留が原因と特定（ルートはユニットテストで422を確認） |
| 2026-08-15 | **SafeMode境界の更なる2ルートの穴を発見・修正**（SEC-AI-SAFEMODE-02 拡張・iteration 48） | **発見**: シナリオ7のE2Eで `summarize-island-relation` が未レビューで **200** を返すのを再現。前記録の「デバッグ残留が原因」説を否定し、ルートを精査 — ① `summarize-island-relation`（`ai_relations.py`）は **doc 文脈なのに `_reject_unreviewed_text` 未配線**（SEC-AI-SAFEMODE-01 の6ルート配線の盲点）、② `suggest-document-title` も `cardTexts` をLLMへ送るのにレビュー検査なし。**修正**: 両ルートへゲートを配線（doc文脈= `_reject_unreviewed_text` / 文書非依存= `_reject_unreviewed_cards`＋`textReviewed`）。**全コンテンツAIルートのカバレッジカナリア**（`_CONTENT_ROUTE_CASES` 10ルート×未レビュー→422）を `test_ai_safemode.py` に追加（**20 pass**）。E2E シナリオ7で未レビュー→422 を再固定（**29/29 pass**） |
| 2026-08-15 | **最後の未固定AI操作をE2E固定**（シナリオ拡大・iteration 49） | **実装**: **ナレッジベース管理者の文書タイトル命名提案** シナリオを追加 — **suggest-document-title**（最後の未固定 AI 操作）を固定。モックLLMに `suggest_document_title` 応答を追加。未レビュー入力→422（textReviewed fail-closed）も固定。これで **AI 操作 8 種を全カバー**・**32/32 pass**（シナリオ1〜8・8業態） |
| 2026-08-15 | **CE4 proposal 連鎖をE2E固定**（シナリオ拡大・iteration 50） | **実装**: **人事マネージャーのAI提案レビュー** シナリオを追加 — **propose-island-summary（proposal-only）→ record-decision（採択・idempotencyKey）→ 再送の冪等確認 → 未登録404 → 文書が自動適用されない** を固定。`KJ_ATLAS_ALLOW_JIT_PROVISIONING=true`＋`x-forwarded-user` でレビューア identity を提供。**冪等性は key だけでなく理由まで同一ペイロードを要求**（409で検出）する仕様を実走行で確認。**39/39 pass**（シナリオ1〜9・9業態） |
| 2026-08-15 | **`mock:` プレフィックス bundle hash の契約不整合**（DATA-CONTRACT-02・iteration 50で発見） | **起票**: `SOURCE_BUNDLE_HASH_PATTERN` は `mock:[0-9a-f]{64}`（69文字）を許可するが、`ai_proposals.source_bundle_hash` の CheckConstraint は `length = 64` を強制。`mock:` 値で提案登録すると **409 Proposal registration conflicted**（実走行で再現）。API と DB の二重正本が矛盾。**`DATA-CONTRACT-02` を三要素分析で起票**（案a=DB制約緩和 / 案b=APIから mock: 除去 / 案c=文書化） |
| 2026-08-15 | **DATA-CONTRACT-02 を案bで解決**（関連課題対応・iteration 51） | **実装（案b）**: `SOURCE_BUNDLE_HASH_PATTERN` から `mock:` を除去し **64hex のみに統一**（`ai_proposals` 系4テーブルの CheckConstraint `length=64` と一致）。`mock:` は API 境界で **422** に。docs CE4 経路は独自の runtime policy（`ce4_source_bundle_hash_allow_mock`）で gate 継続。提案APIへの `mock:` 送信はテスト/実コードとも無いことを確認し migration 不要。**DATA-CONTRACT-02 を Done 化**（proposal 回帰 58 tests・E2E 39/39 pass） |
| 2026-08-15 | **W型探究 × AI支援の複合フローをE2E固定**（シナリオ拡大・iteration 52） | **実装**: **フィールドワーカーの現地調査** シナリオを追加 — ノートをカード化 → **AI束ね(suggest-card-groups)** → **島要約(suggest-island-summary)** → 整理済み文書を snapshot として **inquiry-bundle に保存（CAS create→読戻し→破棄）**、という**アプリの二つの差別化価値（AI KJ 整理 × W型探究）を統合した複合フロー**を一気通貫で固定。**45/45 pass**（シナリオ1〜10・10業態） |
| 2026-08-15 | **配置・統合提案をE2E固定しAIタスク全10種をカバー**（シナリオ拡大・iteration 53） | **実装**: **会議ファシリテーター** シナリオを追加 — **suggest-layout（配置提案）・suggest-merges（島統合提案）** を新規固定（最後の未固定 AI 操作）。これで **AI タスク全10種**（re_layout / suggest_merges / island-summary / island-relation / narrative / check-narrative / refine / card-groups / detect-contradiction / document-title）を E2E で全カバー。**49/49 pass**（シナリオ1〜11・11業態） |
| 2026-08-15 | **LLM呼び出し回数の計測を実装**（OPS-LLM-COST-01 段階2・関連課題対応・iteration 54） | **実装**: `llm/provider.py` にプロセス内 LLM 呼び出しカウンタ（provider種別別＋total）を追加し `generate_with_fallback` で計上。**`GET /ai/provider-status` の `callCounts`** から参照可能（単一プロセス前提・共有ストアは段階3）。トークン計上は `ADR-0050` D3 の provider `usage` 契約採択待ち。**OPS-LLM-COST-01 AC-2 を部分達成**（provider-status 4 tests・AI 回帰 111 tests pass） |
| 2026-08-15 | **GET /docs 一覧が無界（local-dev到達可）**（SEC-DOC-BOUND-05・iteration 55で実機確認） | **起票**: 60件作成 → `GET /docs` が**60件すべて**を返す（境界なし・local-devで到達可。`SEC-DOC-BOUND-04` の admin一覧はSaaS専用で503だが、こちらは無認証で動く）。並び順は `updated_at` 降順（Python sort）で、cursor方式の適用判断は人間待ち。**`SEC-DOC-BOUND-05` を起票**（判断支援: cursor方式・limit 100/max 500・`X-Next-Cursor`）。E2E 49/49 の回帰は緑 |
| 2026-08-16 | **GET /docs の keyset pagination を実装**（SEC-DOC-BOUND-05 解決・関連課題対応・iteration 69） | **実装（cursor方式・判断支援に準拠）**: `list_documents` に `cursor`/`limit`（既定500・最大500）を追加し `(updated_at DESC, id ASC)` で keyset ページング。カーソルは `{urlencoded(updated_at)}:{id}`（ISO の updated_at がコロンを含むため URL エンコード・実装中に発見）。`X-Next-Cursor` ヘッダーで次ページ。**レスポンスは配列のまま（後方互換）**。テスト `test_docs_list_keyset_pagination`（no overlap/loss）追加。**SEC-DOC-BOUND-05 を Done 化**（docs 回帰 42 tests・E2E 94/94 pass） |
| 2026-08-16 | **admin 一覧の keyset pagination を実装**（SEC-DOC-BOUND-04 解決・関連課題対応・iteration 70） | **実装**: `GET /tenant-admin/document-access` に `cursor`/`limit`（既定100・最大500・`DocumentRow.id` 昇順）を追加し `X-Next-Cursor` で次ページ。SEC-DOC-BOUND-05 と同じ keyset 方式を admin 一覧（SaaS専用）にも適用し、**pagination 規約を兄弟エンドポイントへ横展開**。テスト `test_list_keyset_pagination_bounds_response`（5文書・limit2で3ページ・no overlap・終端）追加。**SEC-DOC-BOUND-04 を Done 化**（admin 回帰 19 tests pass） |
| 2026-08-16 | **pagination を業務フローとして固定**（シナリオ強化・iteration 71） | **強化**: シナリオ12（ライブラリアン）に **SEC-DOC-BOUND-05 の keyset pagination**（`limit=1` で1件＋`X-Next-Cursor` → cursor で次ページ）を追加。**分页功能を CI 强制**（E2E 96/96 pass）。全バックエンド回帰（分页修正後）も実施中 |
| 2026-08-16 | **計画在庫の棚卸しで2課題をクローズ**（結果分析・iteration 72） | **棚卸し**: ① **DATA-INQUIRY-RETENTION-01** — 案A（自動期限なし）採択済みで AC-1/2 完了。AC-3〜7 は案B（purge機制）のため **N/A を明記し Done 化**。② **SEC-ADMIN-PLANE-01** — 全AC `[x]`（AC-5 は SEC-ADMIN-PLANE-03 で完了）。残作業（AC-3 の SaaS 通し検証）を **QA-E2E-SAAS-01 の範囲へ寄せて Done 化**。**在庫の正確性を向上** |
| 2026-08-16 | **品質監査官の批判的検証をE2E固定**（シナリオ拡大・iteration 73） | **実装**: **品質監査官（内部統制）** シナリオを追加 — **矛盾検出・反対視点提案・ナラティブA/B照合**の**「批判的検証」系操作を一つのレビュー・パイプラインとして**使用し、業務プロセス改善の決定を提案のみで多角的に検証。**101/101 pass**（シナリオ1〜20・20業態・CI強制） |
| 2026-08-16 | **CE4コンテキスト解決をE2E固定**（シナリオ拡大・非Web経路・iteration 74） | **実装**: **生成AIエージェント** シナリオを追加 — **CE4 context bundle の解決（`context/bundles:resolve`）** を固定。`equivalenceKey`/`bundleHash` の決定性応答・`proposalLifecycle=proposed`（proposal-only）・**safeMode=false→422（fail-closed）** を検証。生成AIが文書コンテキストを取得する基盤の動作を固定。**104/104 pass**（シナリオ1〜21・21業態・CI強制） |
| 2026-08-16 | **SafeModeカナリアの除外注記を更新＋check 10全体を確認**（結果分析・iteration 75） | **更新**: `test_ai_safemode.py` の除外注記に `/ai/proposals/opposing-viewpoint`（AI-OPPOSE-01）を追記（提案機械は永続化doc必須のため汎用カナリア対象外・SafeMode gateはシナリオ18/E2Eで検証）。**check 10 ブロック全体**（business-flow 104/104・admin 11/11・kj 7/7・**合計122 checks**）をハーネスポートで実走行確認 |
| 2026-08-16 | **共同研究のW型探索×並行制御をE2E固定**（シナリオ拡大・iteration 76） | **実装**: **共同研究チーム（アカデミア）** シナリオを追加 — **W型探究ジャーニー（シナリオ6/10）と楽観的並行制御（シナリオ13）を統合**し、複数研究者が同一ジャーニーを並行編集する際の **lost-update 防止（CAS競合検出 409）** を一気通貫で検証。**108/108 pass**（シナリオ1〜22・22業態・CI強制） |
| 2026-08-16 | **管理面監査の証跡フィールドをCI固定**（非Web経路・iteration 77） | **強化**: `verify_api_admin.sh` の監査チェックを**route の存在確認だけでなく証跡フィールド（`result`/`statusCode`/**`requestId`（相関ID）**/**`actorRefHash`（主体指紋）**）まで検証**するよう拡張。SEC-ADMIN-PLANE-03 のコンプライアンス証跡（ログとの相関・主体の非特定化ハッシュ）が CI で固定されることを実走行確認 |
| 2026-08-16 | **監査のdenied（拒否）操作記録をCI固定**（非Web経路・iteration 78） | **強化**: `verify_api_admin.sh` に**誤キーで拒否された `/admin/*` 操作が `result=denied` として監査に記録される**ことを検証するチェックを追加（DOGFOOD-06 の異常系も assert する規約）。許可と拒否の両方が監査証跡に残ることを CI 固定（**12/12 pass**） |
| 2026-08-16 | **MCP検証がナラティブA/Bのcountsをassert**（非Web経路・生成AIのMCP検証・iteration 79） | **発見・強化**: runbook は `narrativeChecks[].issueDirections` **と `counts`** が投影されると主張していたが、`verify_mcp.ts` は **counts を読み取っていなかった**（実文書で検証し確認）。**`verify_mcp.ts` を強化し、各チェックの `counts`（`bMissingInA`/`aMissingInB`）の存在と合計を assert**（counts 欠落はエラー）。生成AI検証者が A/B 合計を rely できるように。MCP 6 tests pass・実走行 PASSED |
| 2026-08-16 | **教育研修のカリキュラム改善をE2E固定**（シナリオ拡大・iteration 80） | **実装**: **教育企画担当（教育・研修）** シナリオを追加 — 受講者フィードバックの分析パイプライン（**束ね→島→矛盾→タイトル提案**）を固定し、カリキュラム改善のための KJ 分析を一気通貫で検証。**114/114 pass**（シナリオ1〜23・23業態・CI強制） |
| 2026-08-16 | **災害対応の現場報告整理をE2E固定**（シナリオ拡大・iteration 81） | **実装**: **災害対策本部スタッフ（防災・災害対応）** シナリオを追加 — **安全クリティカルな文脈で矛盾する現場報告（「食料が届いている」vs「不足している」）を表面化**し（detect-contradiction）、意思決定に対し反対視点を proposal-only で確認（opposing-viewpoint）。束ね・島要約と組み合わせて一気通貫で検証。**120/120 pass**（シナリオ1〜24・24業態・CI強制） |
| 2026-08-16 | **法務レビューの契約条項整理をE2E固定**（シナリオ拡大・iteration 82） | **実装**: **法務担当（法務・コンプライアンス）** シナリオを追加 — 契約条項のKJ整理（束ね→島要約）と**条項間の矛盾検出・法務意見の整合性（A/B照合）**を提案のみで検証（条項の文面は逐語保持）。**126/126 pass**（シナリオ1〜25・25業態・CI強制） |
| 2026-08-16 | **inquiry-bundle サイズ上限の契約乖離を発見・修正**（ドッグフーディング・iteration 83） | **発見**: api.md は inquiry-bundle の上限を **5 MiB** と記載していたが、実装は **20 MiB**（`MAX_INQUIRY_BUNDLE_PAYLOAD_BYTES`・`KJ_ATLAS_MAX_DOCUMENT_BYTES` と整合）を強制。6MB payload が 201 で受理され、21MB で 413 を確認。**修正**: api.md を 20 MiB へ訂正（2箇所）＋ `verify_api_inquiry.sh` に **>20MiB→413 のチェックを追加（18/18 pass・CI固定）** |
| 2026-08-16 | **政策立案のパブリックコメント整理をE2E固定**（シナリオ拡大・iteration 84） | **実装**: **政策担当（公的機関・政策立案）** シナリオを追加 — パブリックコメントのKJ整理（束ね→島要約）と**対立意見（「料金値上げ反対」vs「財源必要」）の矛盾検出**・ナラティブを固定。市民意見の分析を一気通貫で検証（意見は逐語保持・対立意見は表面化）。**132/132 pass**（シナリオ1〜26・26業態・CI強制） |
| 2026-08-16 | **suggest-document-title の SafeMode フィールドが api.md 未記載**（契約監査・iteration 85） | **発見**: `suggest-document-title`（文書非依存・SEC-AI-SAFEMODE-02）の `textReviewed`/`allowUnreviewedText` が api.md に未記載（refine/card-groups/detect-contradiction は記載済み）。**修正**: api.md のリクエスト記載へ 2 フィールドを追記（fail-closed 既定を明記）。契約文書の完全性を向上 |
| 2026-08-16 | **AIルートのapi.md契約ドリフトを系統的に修正**（契約監査・iteration 86） | **発見**: ① **`/ai/proposals/opposing-viewpoint`（AI-OPPOSE-01）が api.md に完全未記載**（コミット済み・E2E固定のルート）。② `generate-narrative` の応答が `narrative: Narrative` と記載されていたが実装は `text`/`basedOnReadingOrder`/`warnings`（かつ request に `allowUnreviewedText`/`narrativeTitle`/`model` 欠落）。③ `suggest-island-summary` の request が `cardTexts` と記載（実装は `doc`）。④ `check-narrative` に `allowUnreviewedText` 欠落。**修正**: 全該当箇所を実装へ整合（opposing-viewpoint 契約を新規記載・generate-narrative/island-summary/check-narrative のフィールドを訂正）。契約文書の完全性を向上 |
| 2026-08-16 | **summarize-island-relation / suggest-merges の api.md 欠落を修正**（契約監査・iteration 87） | **発見**: ① `summarize-island-relation` の request に `cardTexts`/`edgeTexts`/`allowUnreviewedText` が欠落（実装は必須）。② `suggest-merges` に `allowUnreviewedText`/`instruction` が欠落。**修正**: 両ルートの api.md リクエスト記載を実装へ整合。AI ルートの契約ドキュメント完全性を全ルートで確保 |
| 2026-08-16 | **金融・融資審査のリスク評価をE2E固定**（シナリオ拡大・iteration 88） | **実装**: **融資審査担当（金融・融資審査）** シナリオを追加 — リスク情報のKJ整理（束ね→島要約）と**矛盾リスク信号（「売上堅調」vs「在庫過剰」）の検出**・融資判断への反対視点を proposal-only で確認。**138/138 pass**（シナリオ1〜27・27業態・CI強制） |
| 2026-08-16 | **観光・宿泊の訪問者フィードバック整理をE2E固定**（シナリオ拡大・iteration 89） | **実装**: **宿泊施設マネージャー（観光・宿泊）** シナリオを追加 — 訪問者フィードバックのKJ整理（束ね→島要約）と**満足/不満の要因（「眺望が良い」vs「朝食が少ない」）の矛盾検出**・タイトル提案を固定。**144/144 pass**（シナリオ1〜28・28業態・CI強制） |
| 2026-08-15 | **ライブラリアンのコレクション管理をE2E固定**（シナリオ拡大・iteration 56） | **実装**: **ライブラリアン（ナレッジベース管理者）** シナリオを追加 — 複数文書作成 → 一覧(GET /docs) → **`createdBy` 絞り込み（自分の文書のみ・匿名文書除外）** → アーカイブ反映 → アーカイブ中423、という**文書集合の管理**を固定。`created_by` が JIT 解決 UUID であることを実走行で確認（frontend の principalId 相当の「自分の文書」セマンティクス）。**55/55 pass**（シナリオ1〜12・12業態） |
| 2026-08-15 | **凍結済みシナリオをCIハーネスへ統合**（非Web経路の拡充・iteration 57） | **実装**: `verify_all.sh` に check 10 を新設 — **自己完結型E2E**（`verify_business_flow_e2e.sh` 55/55・`verify_admin_ops_flow_e2e.sh` 11/11・`verify_kj_multi_round.sh` 7/7）を専用ポート（8005-8007）で実行し、**ドッグフーディングで凍結した標準業務フロー（シナリオ1〜12）をCI強制**。curlプローブでは出せない業務フローの回帰を、決定性モックLLMで毎回保証。3スクリプトをハーネスポートで実走行確認（合計73 checks） |
| 2026-08-15 | **共同編集の楽観的並行制御をE2E固定**（シナリオ拡大・iteration 58） | **実装**: **共同編集者（コンサルティングファーム）** シナリオを追加 — 文書作成 → GET(ETag) → AがIf-Match編集(200) → Bが古いETag編集(**409 競合検出**) → 最新ETag再取得 → B再編集(200) → 読戻し、という**lost-update 防止（ADR-0076 サーバ権威LWW+CAS）**を業務フローとして固定。**61/61 pass**（シナリオ1〜13・13業態・CI強制） |
| 2026-08-15 | **コンテンツ上限の検証ゲートをE2E固定**（シナリオ拡大・iteration 59） | **実装**: **出版・コンテンツQA（校正者）** シナリオを追加 — カード2001文字→**422**・2000文字→200・タイトル501文字→**422**・500文字→200・違反が**構造化A1エラー（errorEnvelope）**で返ることを固定（DOMAIN-CARD-TEXT-01 の API 境界強制を品質ゲートとして業務フロー化）。**66/66 pass**（シナリオ1〜14・14業態・CI強制） |
| 2026-08-15 | **統合決定ガバナンスをE2E固定**（シナリオ拡大・iteration 60） | **実装**: **編集者（ナレッジ統合）** シナリオを追加 — 統合決定を記録(POST merge-decision-logs **201**) → **グループ別ログ確認(GET by-group)** → **復元ログ参照(GET restore)** → **重複決定409**、という**マージ決定の append 専用 traceability** を固定（suggest-merges の採否を人間が記録・復元可能）。**71/71 pass**（シナリオ1〜15・15業態・CI強制） |
| 2026-08-15 | **生成AIのMCP検証がアーカイブ文書状態を正しく投影**（非Web経路の拡充・iteration 61） | **検証**: 実文書をアーカイブ（204）→ `verify_mcp.ts`（get_context_projection）で **`lifecycle: archived ✅`** ＋「PUT /docs/{id} は 423 Locked（ADR-0073 D2=A）」の横断参照を確認 → **PASSED**。シナリオ4/12（管理者・コレクション管理）のアーカイブ状態を、生成AIが MCP で検証できることを実機で再確認（runbook の archived read-only シナリオの実地裏付け） |
| 2026-08-15 | **外部エージェント連携（Org-D）をE2E固定**（シナリオ拡大・非Web経路・iteration 62） | **実装**: **外部エージェント（トリガー型AI）＋人間レビューア** シナリオを追加 — 外部タスク登録(/ai/external-tasks/register **200**) → **外部提案登録(/ai/external-proposals/register 200・未レビュー着地)** → **人間が決定(/ai/external-proposals/audit hold 200)** → 未登録提案への決定 **404**、という**外部AI成果物の提案受領・人間決定**（EXT-AGENT-02 proposal-only・Org-D）を固定。`baseDocSignature`（{docId}:{updatedAt}）不一致409も確認。**76/76 pass**（シナリオ1〜16・16業態・CI強制） |
| 2026-08-15 | **外部Agentのstale baseDocSignature 409を固定**（シナリオ強化・iteration 63） | **強化**: シナリオ16に**依頼時点の文書シグネチャ不一致（stale `baseDocSignature` → **409**）**を追加 — 外部タスク登録が過去の文書スナップショットに対する依頼を拒否する契約エッジを固定。**77/77 pass**（シナリオ1〜16・16業態・CI強制） |
| 2026-08-15 | **顧客レビュー全行程分析をE2E固定**（シナリオ拡大・iteration 64） | **実装**: **マーケティングアナリスト（eコマース）** シナリオを追加 — **5種のAI操作（束ね→島→ナラティブ→矛盾検出→タイトル提案）を一つの分析パイプラインとして連続使用**する包括フローを固定。個別操作のシナリオとは異なり、顧客レビュー分析の**全行程**を一気通貫で検証。**84/84 pass**（シナリオ1〜17・17業態・CI強制） |
| 2026-08-15 | **反対視点提案をE2E固定**（シナリオ拡大・iteration 65） | **実装**: **リスクレビューア（リスク管理・監査）** シナリオを追加 — **propose-opposing-viewpoint（AI-OPPOSE-01・反対視点/根拠不足の proposal-only 提案）** を新規固定（`status=proposed`・自動適用なし）。未レビューdoc→422（SafeMode）・存在しないtargetCardId→422も固定。**AI タスク全11種**（＋反対視点）。**88/88 pass**（シナリオ1〜18・18業態・CI強制） |
| 2026-08-15 | **多職種ケース会議をE2E固定**（シナリオ拡大・iteration 66） | **実装**: **ケースワーカー（医療・介護）** シナリオを追加 — **新規の反対視点操作（AI-OPPOSE-01）を束ね・島要約と組み合わせ**、在宅ケア継続の意思決定に対し proposal-only で反対視点を確認。新業態での新操作の活用を固定。**93/93 pass**（シナリオ1〜19・19業態・CI強制） |
| 2026-08-15 | **島要約の上限をE2E固定**（シナリオ強化・iteration 67） | **強化**: シナリオ14（コンテンツQA）に**島要約2001文字→422**（`ISLAND_SUMMARY_MAX_LENGTH=2000`）を追加。カード2000・タイトル500・**島要約2000**の**全コンテンツ上限をAPI境界で検証**完了。**94/94 pass**（シナリオ1〜19・19業態・CI強制） |
| 2026-08-16 | **check 10 ブロック全体をハーネスポートで実走行**（非Web経路の検証・iteration 68） | **確認**: `verify_all.sh` check 10 の3自己完結E2Eを専用ポートで実走行 — business-flow **94/94**・admin ops **11/11**・kj multi-round **7/7**（**合計112 checks**）。**シナリオ1〜19＋管理者CLI/API＋多ラウンド協調**をCIハーネスが毎回検証できることを確認 |
| 2026-08-15 | **全非Web検証ハーネスの全体整合を確認**（結果分析・iteration 57） | **実走行**: `verify_all.sh` 16項目全PASS（syntax/lint/unit/integration/admin/federation/LLM mock/docs/API読7・書15・AI fail-closed・inquiry CAS・W型journey・admin plane・MCP stdio/HTTP）を、**マージ（observability）＋モデル統制＋SEC-AI-SAFEMODE-02 適用後**のバックエンドで確認。全体整合の維持を結果分析として記録 |
| 2026-08-15 | **計画在庫の棚卸し・クローズ群**（結果分析・iteration 56-60） | **Done化**: AI-MODEL-GOVERNANCE-01（モデル統制・全AC）・DOMAIN-KJ-COLLAB-01（多ラウンド協調ハーネス）・**AI-TITLE-01（普遍語検査+UI警告+E2E）**。シナリオE2Eは10業態45+チェック、非Webハーネス16/16、frontend 1456 tests を維持 |
| 2026-08-16 | **AI-OPPOSE-01 反対視点・根拠不足提案を実装**（M4・iteration 64-67） | **実装**: ①R1 `POST /ai/proposals/opposing-viewpoint`（contradiction/evidence構造からproposal-only提案・SafeMode/モデルallowlist適用）②R2 Card Inspector に「反対視点を提案」ボタン＋proposal-only表示（evidenceGapバッジ・非自動適用注記）③**保留接続**（holdState=held へ非破壊遷移・元の違和感に戻れる）。E2E シナリオ18で固定。frontend 1456 tests・AI 66 tests。残ACは UI 390px E2E |
| 2026-08-16 | **反対視点提案のモデル選択経路を検証**（AI-MODEL-GOVERNANCE 連動） | R1 ルートが `_assert_model_allowed`（テナント allowlist・403）を適用し、選択子/クライアントの model 上書きと同一のガバナンス経路に乗ることを確認 |
