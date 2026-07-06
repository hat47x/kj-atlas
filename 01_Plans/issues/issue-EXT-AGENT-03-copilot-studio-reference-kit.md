# Issue Draft: EXT-AGENT-03 Copilot Studio 参照キットと利用者向け運用文書

- Type: Documentation quality
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: TBD
- Scope: `04_Documentation/`, `02_Architecture/external_agent_collaboration_spec.md`（参照）, `03_Implement/frontend/e2e/`（スモークのみ）
- Related Backlog: `EXT-AGENT-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`（D4・Copilot プロファイル）, `02_Architecture/external_agent_collaboration_spec.md`（§7 正本）, `01_Plans/issues/issue-CARD-META-UI-01-card-provenance-metadata-ui-boundary.md`（主体メタ表示・共有境界）
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: EXT-AGENT-03
- RequirementStatement: Copilot / Copilot Studio を代表とする定額エージェントとの往復運用を、利用者・運用者が追加開発なしで再現できる参照キット（エージェント Instructions テンプレート・逸脱時リカバリ定型文・運用手順・データ境界チェックリスト）として文書化する。
- PriorityClass（Must / Should / Could）: Could
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=EXT-AGENT-01/02 が利用可能 / 操作=文書の手順どおり M365 Copilot（またはCopilot Studio エージェント）で往復を実施 / 期待結果=手順内のテンプレートだけで依頼→応答→取込が完了し、確認チェックリスト（テナント設定・ログ・学習利用）を運用者が判定できる / 除外=Copilot Studio 環境の構築代行、Tier 1/2 の実装、他ベンダー個別手順の網羅（汎用契約で代替）。
- GoNoGoGate（Required / Optional / N/A）: Optional
- SecurityGateImpact: share-export（外部授受の運用手順。SafeMode/確認チェックリストを含む）
- VerificationLevel: docs-check
- DecisionStatus（Fixed / Pending）: Fixed（ADR-0049 D4・spec §7）
- DecisionQueueRef: `ADR-0049`

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

- [ ] AC-1: Instructions テンプレート・リカバリ定型文・チェックリストが文書に含まれ、spec §7 と矛盾しない（docs-check）。
- [ ] AC-2: 文書内の応答例 JSON が agent-response.v1 として妥当（フィクスチャ化して検証テストに接続）。
- [ ] AC-3: 04_Documentation README の公開境界マトリクス・Gist 表に登録され、リンク整合が取れる。
- [ ] AC-4: 秘密情報・組織固有情報を含まない（公開文書規約準拠）。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 文書本体（テンプレ全文・手順・チェックリスト）。
- [ ] T2 応答例のフィクスチャ化＋検証接続。
- [ ] T3 README/公開表・public_index 導線の登録。

## 7) 検証計画 / Validation plan

- `rg -n "agent-response.v1|agent-task.v1" 04_Documentation 02_Architecture`（契約表記の整合）
- 文書内 JSON 例を EXT-AGENT-02 のパーサ検証テストに通す。

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（文書のみ） / 保留操作の距離=不変 / 取り消し導線=N/A

## Traceability

- Related: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`, `02_Architecture/external_agent_collaboration_spec.md`（§7）
- Related: `01_Plans/issues/issue-EXT-AGENT-01-agent-task-package-export.md`, `issue-EXT-AGENT-02-agent-response-import.md`, `04_Documentation/README.md`（公開境界）
- Derived-from: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`
