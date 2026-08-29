# Issue Draft: EXT-AGENT-03 Copilot Studio 参照キットと利用者向け運用文書

- Type: Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Claude Code
- Scope: `04_Documentation/`, `02_Architecture/external_agent_collaboration_spec.html`（参照）, `03_Implement/frontend/e2e/`（スモークのみ）
- Related Backlog: `EXT-AGENT-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`（D4・Copilot プロファイル）, `02_Architecture/external_agent_collaboration_spec.html`（§7 正本）, `01_Plans/issues/done/issue-CARD-META-UI-01-card-provenance-metadata-ui-boundary.md`（主体メタ表示・共有境界）
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: EXT-AGENT-03
- RequirementStatement: Copilot / Copilot Studio を代表とする定額エージェントとの往復運用を、利用者・運用者が追加開発なしで再現できる参照キット（エージェント Instructions テンプレート・逸脱時リカバリ定型文・運用手順・データ境界チェックリスト）として文書化する。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=EXT-AGENT-01/02 が利用可能 / 操作=文書の手順どおり M365 Copilot（またはCopilot Studio エージェント）で往復を実施 / 期待結果=手順内のテンプレートだけで依頼→応答→取込が完了し、確認チェックリスト（テナント設定・ログ・学習利用）を運用者が判定できる / 除外=Copilot Studio 環境の構築代行、Tier 1/2 の実装、他ベンダー個別手順の網羅（汎用契約で代替）。
- SecurityGateImpact: share-export（外部授受の運用手順。SafeMode/確認チェックリストを含む）

## 1) 課題 / Problem statement

- 契約（spec §3/§4）だけでは、Copilot 側の設定（Instructions・応答を JSON のみに固定する方法）と運用（逸脱時の再依頼・データ境界の確認）が利用者任せになり、再現性が出ない。

## 2) 背景 / Context

- spec §7 が骨子（最短運用／Studio 化テンプレ要点／リカバリ定型文／データ境界注意）を確定済み。本Issueは 04_Documentation の利用者向け文書として完成させ、公開区分（Gist 含める文書）へ登録する。

## 3) 判断基準による優先度評価

- 価値: 導入現場（企業・自治体）での実運用を成立させる最後の1マイル。
- 安全: データ境界チェックリスト（テナント・ログ保持・学習利用設定の確認）を利用前提として明文化。
- 規模拡大: Copilot 以外の定額エージェントにも同じ契約で展開可能な書き方にする。
- 後方互換: 文書のみ。

## 3.2 非目標 / Non-goals

- Copilot Studio テナントの構築・管理手順そのもの（Microsoft 公式に委ねリンクせず一般記述に留める）。Tier 1（Power Automate）/ Tier 2（API 直結）の実装。特定組織固有の承認フロー。

## 4) 提案する解決策 / Proposed solution

- `04_Documentation/external_agent_workflow.md`（利用者/運用者向け・公開候補）: 最短運用（チャット貼付け）／Copilot Studio エージェント化（**Instructions 全文テンプレート**・応答を JSON のみに固定する指示・taskId エコーバック）／逸脱時リカバリ定型文／データ境界チェックリスト／トラブルシュート（壊れた JSON・長すぎる文脈の分割=bundle の scope/depth 調整）。テンプレートは起票者・作成者・最終更新者などの主体メタ入力を利用者へ求めず、組織判断で必要になった場合のみ CARD-META-UI-01 の境界に従って別扱いにする。
- `04_Documentation/README.md` の境界マトリクス・Gist 表へ登録。`public_index.md` に導線1行。
- e2e スモーク（任意・EXT-AGENT-02 のフィクスチャ流用）: 文書内のテンプレ応答例が実際に取り込めることを固定（文書と実装の乖離防止）。

## 5) 受け入れ条件 / Acceptance criteria

- [x] AC-1: Instructions テンプレート・リカバリ定型文・チェックリストが文書に含まれ、spec §7 と矛盾しない（docs-check）。
- [x] AC-2: 文書内の応答例 JSON が agent-response.v1 として妥当（フィクスチャ化して検証テストに接続）。
- [x] AC-3: 04_Documentation README の公開境界マトリクス・Gist 表に登録され、リンク整合が取れる。
- [x] AC-4: 秘密情報・組織固有情報を含まない（公開文書規約準拠）。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 文書本体（テンプレ全文・手順・チェックリスト）。
- [x] T2 応答例のフィクスチャ化＋検証接続。※フィクスチャファイルを別途作らず、文書内のコードフェンスを直接抽出して検証する方式を採用（下記「完了記録」参照）。
- [x] T3 README/公開表・public_index 導線の登録。

## 7) 検証計画 / Validation plan

- `rg -n "agent-response.v1|agent-task.v1" 04_Documentation 02_Architecture`（契約表記の整合）
- 文書内 JSON 例を EXT-AGENT-02 のパーサ検証テストに通す。

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（文書のみ） / 保留操作の距離=不変 / 取り消し導線=N/A

## Traceability

- Related: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`, `02_Architecture/external_agent_collaboration_spec.html`（§7）
- Related: `01_Plans/issues/done/issue-EXT-AGENT-01-agent-task-package-export.md`, `issue-EXT-AGENT-02-agent-response-import.md`, `04_Documentation/README.md`（公開境界）
- Related: `01_Plans/issues/done/issue-GENAI-GOV-01-generative-ai-lane-boundary-and-readiness.md`（Lane C: 外部エージェント成果物連携）, `02_Architecture/value_traceability.md` §2.9
- Derived-from: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`

## 完了記録 2026-07-09（Claude Code）

ADR-0049 の D2（EXT-AGENT-01）・D3（EXT-AGENT-02）に続き、D4（Copilot プロファイル・spec §7）の最後の1マイルとして本Issueを実装した。

### 実装

- `04_Documentation/external_agent_workflow.md`（新規）: spec §7 を正本として、最短運用（追加構築なし）・Copilot Studio エージェント化（Instructions テンプレート全文・逸脱時リカバリ定型文）・データ境界チェックリスト（テナント境界・ログ保持・学習利用設定）・トラブルシュート（壊れたJSON・文脈分割・部分取り込み・孤立提案）・agent-response.v1 応答例を含む。テンプレートは主体メタ（起票者・作成者等）の入力を利用者へ求めない（CARD-META-UI-01 の境界に従う）。
- `04_Documentation/README.md`: 文書公開境界マトリクス（一般利用者/運用者向け公開文書）と Gist に含める文書表に登録。
- `04_Documentation/public_index.md`: 「目的別に読む」表に導線を1行追加。

### T2（応答例のフィクスチャ化）の実装方式

Issue本文は「応答例のフィクスチャ化＋検証テストに接続」を提案していたが、別ファイルとしてフィクスチャを複製すると文書とフィクスチャが将来ズレる（どちらかだけ更新される）リスクがあるため、**文書内のコードフェンスを直接抽出して検証する**方式を採用した: `03_Implement/frontend/src/import/external_agent_workflow_doc.test.ts` が `04_Documentation/external_agent_workflow.md` を直接読み込み、` ```json ` フェンスを正規表現で抽出し、EXT-AGENT-02 の `parseAgentResponse()` に厳格/寛容両モードで通す。複製が存在しないため、乖離が原理的に起きない。

このテストファイルは `03_Implement/frontend/src/import/` に配置されており、`04_Documentation` を4階層上に遡って見つける（`findRepoRoot` ヘルパー、固定階層数ではなく `04_Documentation` を含むディレクトリを探索）。これは、本セッションで使用している WSL ネイティブミラー（`03_Implement/frontend` のみをフラットにコピーしたもの）では固定階層数の相対パスが機能しないための設計判断であり、通常のリポジトリチェックアウトでも同様に正しく機能する。

### 検証

- typecheck 0 / vitest **988 passed**（188 files。文書検証テスト3件を追加）。
- `grep -rn "agent-response.v1|agent-task.v1" 04_Documentation 02_Architecture`: 文書内の契約表記が spec §7.2/§7.4 の固定文と一致することを目視確認（AC-1）。
- 秘密情報・内部管理情報の漏洩チェック（README.md の公開手順に記載の grep パターン）: 一致なし（AC-4）。

### 残課題（スコープ外）

- Tier 1/Tier 2（フォルダ授受・API直結）は spec §7.4 が「将来・概要のみ」と明記しており、本Issueの対象外（非目標に明記済み）。
- Copilot Studio テナントの構築・管理手順そのものは Microsoft 公式に委ね、本文書には含めていない（非目標）。
