# ADR-0049: 定額課金AIエージェントとの非同期協調（成果物ベース連携の第一級化）

- Status: Proposed
- Date: 2026-07-05
- Deciders: Maintainer（委譲された意思決定権限）
- Scope: `02_Architecture/`, `03_Implement/frontend/src/`, `03_Implement/backend/src/`, `01_Plans/issues/`, `04_Documentation/`

## Context

- 生成AIの API 直接利用は従量課金がかさみ、MVP 段階では利用が困難な場合があることが既に記録されている（ROADMAP 要件D「API課金回避のための定額/オフライン AI 補完経路」、`ADR-0007` FB-RM-MID-07。ADR-0047 の R-1: 実利用摩擦に該当）。
- 一方、国内の多くの企業・自治体では、Microsoft Copilot / Copilot Studio 等の**定額課金ライセンス内の AI エージェント**による業務効率化が主流になりつつある。kj-atlas の想定利用環境（企業・自治体・自己ホスト）では、「組織が既に契約している定額エージェントに思考ワークロードを委ね、kj-atlas は文脈の供給と結果の受け入れ・レビューに徹する」構成が、コスト・ガバナンス（データ境界・監査）・導入障壁のすべてで現実解となる。
- 必要な構成要素の大半は実装済みである:
  - **出力側**: CE1 ContextBundle（`/context/query`（`previewConfirmed` 必須・`queryCanonicalHash`）→ `/context/bundle`（決定論・`bundleHash`）、`ContextQueryPreviewPanel` による「AI へ渡る範囲の事前確認」）、SafeMode 書き出し境界（`domain/policy/safe_mode.ts` の share 文脈・`SharePanel` preflight・`/export-audit`）。
  - **入力側**: レビューパック/ZIP 取込の信頼境界（容量・パス検査・`markdown_sanitize`・寛容/厳格検証）→ マージ項目化 → 選択レビュー → 原子的適用 → `merge-decision-logs`（追記専用・スナップショット復元）。
  - **構造化変更指示**: CE3 `PatchV1`（`baseDocSignature`・ops 列・lint・conflict 検出・`PatchWorkspacePanel` の採否/保留/ロールバック）。
  - **不変条件**: 提案のみ・自動確定なし・`human_reviewed` 昇格は人間のみ・SafeMode 既定ON・provider=none 既定（`llm/provider.py`）。
- 未定義（ギャップ）は3点のみ: (1) 外部エージェントへ渡す**依頼パッケージの契約**、(2) エージェントからの**応答契約**、(3) 応答を既存レビュー機構へ流し込む**取込経路**。

## Decision

**外部の定額課金 AI エージェントとの「成果物ベース・非同期」協調を、kj-atlas の企業向け AI 経路の第一級として採択する**（一文: kj-atlas はエージェントを呼ばず、人間が仲介する「依頼パッケージの書き出し → 外部エージェントでの処理 → 構造化応答の取り込み→提案化」を標準ワークフローとする）。

### D1. 連携モデル（成果物ベース・非同期・人間仲介）

- kj-atlas から外部エージェントへの**自動送信は行わない**。出力は人間の明示操作による書き出し（共有・書き出し境界を通過）、入力は人間の明示操作による取り込み（import 信頼境界を通過）とする。
- 非同期性を前提とする: 依頼と応答は `taskId` で相関し、依頼時点の `baseDocSignature`（CE3）/ `bundleHash`（CE1）を携行する。取り込み時に文書が進んでいた場合は、既存の conflict 検出 / rediff 経路で**安全に再突合**し、黙って上書きしない。複数依頼の並行、同一応答の再取込（冪等）を許す。
- ベンダー非依存を原則とする: 契約（パッケージ/応答スキーマ）は汎用とし、Copilot / Copilot Studio は**代表プロファイル**として運用手順とテンプレートを提供する（ChatGPT Enterprise 等の他の定額エージェントでも同一契約で動作する）。

### D2. 依頼パッケージ（AgentTaskPackage v1）

- 内容: ①タスク指示文（エージェント向け・日本語）②ガードレール（提案のみ・確定しない/点数・順位を付けない/曖昧さ・保留・対立を保持する/応答契約のJSONのみで返す）③文脈（ContextBundle の抜粋。**Context Query Preview で人間が確認した範囲のみ**）④応答契約（インライン JSON Schema＋記入例）⑤相関情報（`taskId`・`docId`・`baseDocSignature`・`bundleHash`・`queryCanonicalHash`）。
- 形態: 貼り付け可能な単一 Markdown（タスクシート）を正とし、機械可読 JSON（task.json / context_bundle.json）を随伴可能とする。
- **出力境界**: 書き出しは共有・書き出し境界（SafeMode 適用・未レビュー既定除外・出典参照既定OFF・共有前確認）を必ず通り、`/export-audit`（exportKind=agent-task）へ記録する。

### D3. 応答（AgentResponse v1）と取り込み

- 応答は `taskId` を携えた構造化 JSON とし、`proposals[]`（種別: 島タイトル候補 / マージ候補 / ナラティブ草稿 / 対立観点 / 違和感候補 / **patch**=CE3 PatchV1）を運ぶ。各提案は**根拠（rationale）必須**、**数値スコア・順位・確度フィールドは契約上禁止**（反スコアリング。存在した場合、取り込み時に破棄する）。
- 取り込みは import 信頼境界（スキーマ検証 寛容/厳格・文字列サニタイズ・容量制限）を通り、**すべて AI 由来・未レビューの提案**として既存面へ流し込む: マージ候補→MergeSuggestions、島タイトル→候補提示、ナラティブ→草稿、対立観点/違和感→critique 候補、patch→PatchWorkspace（lint→conflict→採否/保留→ロールバック可能）。
- **自動確定なし**をテストで固定する（提案の採用は常に人間操作・全操作可逆・`merge-decision-logs`/`context-audit`（operation=proposal/apply）へ記録）。

### D4. トランスポート段階（Tier）

- **Tier 0（MVP・本採択の範囲）**: 手動授受（コピー&ペースト / ファイル添付）。追加インフラ・認証・到達性を一切要さず、自己ホスト/クローズド環境で完結する。あらゆる定額エージェントで動作。
- **Tier 1（将来・kj-atlas 本体は無改修）**: SharePoint/OneDrive 等の受け渡しフォルダ＋Power Automate による投函/回収の自動化。契約は Tier 0 と同一。
- **Tier 2（将来・別決裁）**: Copilot Studio のアクション（カスタムコネクタ）から kj-atlas API を直接呼ぶ同期/半同期連携。ネットワーク到達性と認証（AUTH-* 系）が前提であり、着手時に別途判断する。

### 非目標

- エージェント出力の自動適用・自動確定（提案のみの不変条件を堅持）。
- kj-atlas からの外部自動送信（Tier 0/1 では kj-atlas は外部と直接通信しない）。
- 特定ベンダーへの固定（Copilot Studio はプロファイルであり契約は汎用）。
- リアルタイム/対話型の同期連携・チャットUIの主役化（ADR-0001 非目標）。
- 従量課金 API 経路（local / large-scale プロバイダ）の廃止（併存し、本経路は provider 設定と独立に動作する）。

## Consequences

- 期待される効果:
  - 従量課金なしで高度な思考支援を利用でき、MVP・企業/自治体導入の最大障壁（API コストとガバナンス）が解消される。組織の既存 Copilot 投資を活用できる。
  - データ境界が明確になる（出るものは人間確認済みの SafeMode 適用パッケージのみ・監査記録つき）。
  - provider=none 構成のまま「AIなしで完結」と「定額AIで増強」を両立し、P-07（自己ホスト・プライバシー既定）を侵さない。
- 想定される副作用/制約:
  - 手動授受の往復手間（Tier 1 で軽減可能）。エージェント側の応答契約逸脱（壊れた JSON）への再依頼運用が必要（定型文で対処）。
  - 応答品質はエージェント側能力に依存する（kj-atlas は検証とレビューで防御し、品質は保証しない）。
- 移行時に必要な対応（Action は issue で管理）:
  - 仕様正本: `02_Architecture/design/external_agent_collaboration_spec.html`（本 ADR と同時制定）。
  - 起票: `EXT-AGENT-01`（依頼パッケージ書き出し）/ `EXT-AGENT-02`（応答取り込み→提案化）/ `EXT-AGENT-03`（Copilot Studio 参照キット＋利用者向け文書）。
  - `ROADMAP` 要件D・`ADR-0007` FB-RM-MID-07 へ本 ADR を参照付け（本経路は同要件の (b) 構造化変更指示ルートの具体化。(a) ローカルLLM反映ルートは併存のまま将来判断）。

## Traceability

- Related: `01_Plans/adr/ADR-0001-value-to-requirements.md`（P-03 レビュー追跡・P-04 HIL・P-07 自己ホスト/プライバシー既定・非目標）
- Related: `01_Plans/adr/ADR-0007-future-backlog.md`（FB-RM-MID-07）, `ROADMAP.md`（要件D）
- Related: `01_Plans/adr/ADR-0047-design-decision-adr-saturation-and-execution-first.md`（R-1: 従量課金困難という記録済みの実利用摩擦への応答）
- Related: `02_Architecture/llm_provider_spec.md`, `02_Architecture/design/enterprise_architecture.html`（§03 アクセス制御/SafeMode/外部送出）, `02_Architecture/api.md`（context/export 監査）
- Related: `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md`, `issue-CE3-patch-workspace-presets.md`, `issue-CE4-api-cli-audit-integration.md`
- Derived-from: `ROADMAP.md` 要件D（2026-06 記録の従量課金摩擦）および 2026-07-05 の企業・自治体向け定額エージェント連携要件
