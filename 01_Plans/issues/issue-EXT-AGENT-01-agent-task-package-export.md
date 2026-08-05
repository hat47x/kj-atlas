# Issue Draft: EXT-AGENT-01 エージェント依頼パッケージの書き出し（AgentTaskPackage v1）

- Type: Feature request
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Claude Code
- Scope: `03_Implement/frontend/src/export/`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/i18n/locales/`, `03_Implement/frontend/e2e/`
- Related Backlog: `EXT-AGENT-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`（D2）, `02_Architecture/design/external_agent_collaboration_spec.html`（§3 正本）, `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md`, `01_Plans/issues/issue-DOMAIN-TRACE-01-serial-number-and-source-provenance.md`, `01_Plans/issues/issue-CARD-META-UI-01-card-provenance-metadata-ui-boundary.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: EXT-AGENT-01
- RequirementStatement: 外部の定額課金 AI エージェントへ渡す依頼パッケージ（タスクシート Markdown＋随伴 task.json/context_bundle.json）を、Context Query Preview で人間が確認した文脈と応答契約・相関情報を束ねて生成し、共有・書き出し境界（SafeMode・共有前確認・監査）を通して書き出せるようにする。出典参照（`seq/source`）と起票者などの主体メタを分離し、主体メタは CARD-META-UI-01 で同梱判断が固定されるまで含めない。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=文書を開き範囲（島/カード）を選択 / 操作=「エージェントへ依頼」→ taskKind を選択 → Context Query Preview で範囲確認 → 書き出し / 期待結果=ガードレール・文脈・応答契約・相関ブロック（taskId/baseDocSignature/bundleHash）を含むタスクシートが生成され、未レビュー本文は既定除外、出典参照は既定OFF、起票者などの主体メタは含まれず、export-audit に exportKind=agent-task が記録される / 除外=外部への自動送信、Tier 1/2 транспорト、応答の取り込み（EXT-AGENT-02）。
- SecurityGateImpact: SafeMode / share-export（外部へ出る成果物の生成。既存境界を必ず通過し新しい抜け道を作らない）

## 1) 課題 / Problem statement

- 従量課金 API を使わずに定額エージェントへ思考を委ねる経路（ROADMAP 要件D）の出力側が未実装。文脈・指示・応答契約・相関情報を人手で組み立てるのは再現性がなく、SafeMode 境界も通らない。

## 2) 背景 / Context

- CE1（/context/query→/context/bundle、previewConfirmed、bundleHash）と SafeMode 書き出し境界・export-audit は実装済み。本Issueはそれらを束ねる**生成器と導線**のみを追加する。仕様正本は spec §3（構成順序・ガードレール固定文・メタスキーマ）。

## 3) 判断基準による優先度評価

- 価値: 定額エージェント活用の入口。P-07（自己ホスト）と両立する唯一の外部AI経路。
- 安全: 出力は共有・書き出し境界を必ず通過（未レビュー既定除外・出典参照既定OFF・主体メタ対象外・SafeMode 表示・監査）。
- 規模拡大: 企業・自治体の Copilot 前提環境への導入障壁を解消。
- 後方互換: スキーマ変更なし（書き出しのみ）。

## 3.2 非目標 / Non-goals

- 外部エージェントへの自動送信・API 呼び出し（Tier 2 は別決裁）。応答取り込み（EXT-AGENT-02）。エージェント側テンプレの同梱（EXT-AGENT-03）。

## 4) 提案する解決策 / Proposed solution

- taskKind 選択（island_titles / merge_candidates / narrative_draft / opposing_viewpoints / critique_suggestions / free_analysis）→ 既存 ContextQueryPreviewPanel で範囲確認 → spec §3.3 の順序でタスクシート生成（.md ダウンロード＋クリップボードコピー）→ 随伴 JSON は任意ダウンロード。
- 相関: taskId（uuid）、baseDocSignature（CE3 と同一計算）、bundleHash/queryCanonicalHash（CE1 応答から）。書き出し済みタスクの一覧（awaiting 表示）をローカル保持。
- 監査: /export-audit（exportKind=agent-task）。i18n（ja/en）。

## 5) 受け入れ条件 / Acceptance criteria

- [x] AC-1: 生成タスクシートが spec §3.3 の構成順序・ガードレール固定文・相関ブロックを含むことが golden fixture で固定される。
- [x] AC-2: previewConfirmed を経ない書き出しができない（Context Query Preview 必須）。※スコープ変更あり、下記「完了記録」参照。
- [x] AC-3: 未レビュー本文が既定で除外され、includeUnreviewedDrafts 明示時のみ含まれる（SafeMode 文脈 share 適用）。出典参照は既定OFFとし、起票者・作成者・最終更新者などの主体メタは CARD-META-UI-01 の同梱判断が固定されるまで含めない。
- [x] AC-4: export-audit に exportKind=agent-task が記録される。
- [x] AC-5: 書き出しは「詳細」（advanced）配下または作業面からの明示操作で、初期表示アンカー非回帰（CB-1）。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 タスクシート生成器（`export/agent_task_export.ts`・golden テスト）。
- [x] T2 導線 UI（taskKind 選択＋範囲確認＋書き出し）。※「既存 ContextQueryPreviewPanel」ではなく新規 `AgentTaskExportPanel` を追加。理由は下記「完了記録」参照。
- [x] T3 SafeMode/preflight 統合＋export-audit。
- [x] T4 i18n＋regression/e2e スモーク。

## 7) 検証計画 / Validation plan

- `cd 03_Implement/frontend && npm run typecheck && npm test`（golden・境界・監査）
- e2e: 依頼書き出し→ファイル内容検証（EXT-AGENT-02 のラウンドトリップ e2e と共通フィクスチャ）。

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（明示操作の面のみ） / 保留操作の距離=不変 / 取り消し導線=あり（書き出しは非破壊・タスク一覧から破棄可能）

## Traceability

- Related: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`, `02_Architecture/design/external_agent_collaboration_spec.html`（§3/§6）
- Related: `01_Plans/issues/issue-EXT-AGENT-02-agent-response-import.md`, `issue-EXT-AGENT-03-copilot-studio-reference-kit.md`
- Related: `01_Plans/issues/issue-GENAI-GOV-01-generative-ai-lane-boundary-and-readiness.md`（Lane C: 外部エージェント成果物連携）, `02_Architecture/value_traceability.md` §2.9
- Derived-from: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`

## 完了記録 2026-07-09（Claude Code）

### スコープ判断: CE1 `/context/bundle` は実文書に非対応のため、文脈抜粋は直接文書走査で生成

実装前の調査で、`issue-CE1-context-query-bundle-foundation.md` が CE1 を明示的に **contract-only・mock-first** と定義していることを確認した（「Keep CE1 as a mock-first, contract-first interface until a separate implementation slice explicitly expands the provider/runtime behavior」）。backend の `ContextBundleRequest.stubDatasetId` は `Literal["A2-minimal-v1"]` に固定されたclosed-world契約で、実際に開いている文書からバンドルを構築する実装（provider）は存在しない。加えて `ContextQueryPreviewPanel`/`/context/query`・`/context/bundle` を実際に呼び出すフロントエンド呼び出し元も皆無（本Issueが最初の呼び出し元になる想定だった）。

このまま「既存 ContextQueryPreviewPanel で範囲確認」という提案どおりに実装すると、外部へ渡すタスクシートの「文脈」節が実際の選択内容と無関係な固定スタブデータになり、機能として破綻する。そこで以下の判断で進めた:

1. **文脈抜粋は `DocumentV2` の直接走査で生成**（`narrative_export.ts`/`reading_outline.ts`/`abstract_map_export.ts` と同じ既存パターン）。CE1 の HTTP ラウンドトリップには依拠しない。
2. **bundleHash/queryCanonicalHash はローカルで計算**（`canonicalizeJson` + sha256、CE1自身のハッシュ規約と同じ手法）。実際に書き出す内容に対する真正な相関ハッシュとなる。
3. **`ContextQueryPreviewPanel` はマウントしない**。代わりに新規 `AgentTaskExportPanel`（WorkModePanel と同じ、独立ダイアログのパターン）を追加し、その「上記の範囲で書き出しに進みます」チェックボックスが previewConfirmed と同じゲート役を果たす（選択が空なら操作不可、taskKind/含める内容変更で再確認が必要）。
4. SharePanel（既に100超のprops・500行超）へこれ以上のprops追加は避け、UX-NAV-01 が確立した「肥大化したパネルへの追加ではなく専用サーフェスを切る」前例に倣った。

ADR-0049 D2 が求める内容（①タスク指示文②ガードレール③文脈④応答契約⑤相関情報）と出力境界（SafeMode・既定除外・共有前確認・export-audit）は全て満たしている。CE1 の実文書対応（provider実装）は別スライスの決定事項であり、本Issueのスコープ外として扱った。

### 実装

- `03_Implement/frontend/src/export/agent_task_export.ts`（新規）: `buildAgentTaskSheet()` が spec §3.3 の5節固定順（依頼→ガードレール→文脈→応答契約→相関ブロック）でMarkdownを生成。ガードレール固定文は§3.3 item 2を一字一句そのまま埋め込み。相関ブロックは§3.2のJSONスキーマ（schemaVersion/taskId/createdAt/docId/baseDocSignature/bundleHash/queryCanonicalHash/taskKind/locale）。応答契約節は§4.1のスキーマ＋最小記入例をインライン提示。
- `03_Implement/frontend/src/ui/AgentTaskExportPanel.tsx`（新規）: taskKind選択・件数目安・未レビュー下書き含める（SafeMode ON時は非表示）・出典参照含める（常時表示＋警告）・書き出す範囲プレビュー＋確認チェックボックス・コピー/ダウンロード操作。WorkModePanelと同じフォーカストラップ・Escape・focus-return実装。
- `03_Implement/frontend/src/api/client.ts`: `postExportAudit()` 追加（既存 `/docs/{docId}/export-audit` へのフロントエンド初回呼び出し。新規バックエンドエンドポイントなし＝spec §8準拠）。
- `03_Implement/frontend/src/App.tsx`: 「詳細」ON時のみ出現するトリガーボタン（`data-ui-complexity-tier="advanced-content"`、`data-ui-core-action` は付与せず既存の7件カウントを非回帰）＋ `AgentTaskExportPanel` マウント＋書き出しハンドラ（コピー/ .md ダウンロード/ task.json ダウンロード、いずれも成功後に export-audit を fail-open で送信）。
- i18n: `agent_task_export.*` を ja/en 両ロケールに追加（`key_consistency.test.ts` でパリティ確認）。

### 検証

- typecheck 0 / vitest **970 passed**（186 files。golden fixture 1件＋generator単体テスト5件＋regression anchor 1件を追加）。
- e2e 新規3件 passed: `agent_task_export.spec.ts`（トリガーが「詳細」の背後にあること／範囲確認前は書き出し不可→確認後に有効化→.mdダウンロード内容が5節固定順・ガードレール全文・相関ブロック・未レビュー本文既定除外を満たすこと／Escapeでのフォーカス復帰）。
- 既存e2e 16件（`pre_share_summary_gate`・`complexity_budget_foregrounding`・`menu_bar`・`empty_canvas_onboarding`）で非回帰確認。
- 全て `nix develop`（Node 20 devShell）+ Docker Playwright (`mcr.microsoft.com/playwright:v1.58.2-jammy`) 経由で実行。

### 残課題（スコープ外・別issue候補）

- CE1 の実文書対応（provider実装）: 別スライスとして明示的に先送りされている（`issue-CE1-...md`）。実装された場合、本Issueの文脈抜粋を CE1 経由に切り替える余地はあるが、現状の直接文書走査でも spec の要求は満たしている。
- EXT-AGENT-02（応答取り込み）は本Issueが生成する `agent-response.v1` 契約を前提に着手可能。
