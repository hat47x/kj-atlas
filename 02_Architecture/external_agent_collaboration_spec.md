# 外部定額AIエージェント非同期協調 仕様（AgentTaskPackage / AgentResponse v1）

- 正本区分: 本書が外部エージェント連携契約の正本（決定は `ADR-0049`）。
- Scope: `03_Implement/frontend/src/`（export/import/UI）、`03_Implement/backend/`（監査のみ・新規エンドポイント不要 Tier 0）、`04_Documentation/`（利用手順）。
- 対象読者: 実装者、Copilot Studio 等でエージェントを構成する運用者。

## 1. 目的と原則

組織が定額課金で契約済みの AI エージェント（Microsoft Copilot / Copilot Studio、ChatGPT Enterprise 等）に思考ワークロード（束ねる観点・対立点・草稿化など）を委ね、kj-atlas は**文脈の供給・結果の検証・人間レビュー・可逆な適用**に徹する。

原則（ADR-0049 / ADR-0001 準拠）:
1. **非同期・人間仲介**: kj-atlas は外部と直接通信しない（Tier 0）。書き出し・取り込みは人間の明示操作。
2. **提案のみ**: エージェント出力は常に AI 由来・未レビューの提案。自動確定なし。適用は人間操作・全て可逆・監査記録。
3. **反スコアリング**: 応答契約に数値スコア・順位・確度を含めない（存在すれば取り込み時に破棄）。
4. **境界の再利用**: 出力は共有・書き出し境界（SafeMode/preflight/`/export-audit`）、入力は import 信頼境界（検証・サニタイズ）を通る。新しい抜け道を作らない。
5. **ベンダー非依存**: 契約は汎用。Copilot Studio は代表プロファイル（§7）。

## 2. 用語・アクター・信頼境界

| アクター | 信頼 | 役割 |
|---|---|---|
| kj-atlas（自己ホスト） | 信頼 | パッケージ生成・応答検証・提案化・レビュー・適用・監査 |
| 利用者（人間） | 信頼（操作主体） | 書き出し確認・エージェントへの投函・応答の持ち帰り・提案の採否 |
| 外部エージェント | **非信頼** | 思考の委任先。出力はデータとして扱い、指示として扱わない |
| エージェント基盤（M365 等） | 組織契約に依存 | データ境界は組織のライセンス/テナント設定に従う（本仕様の管轄外・§7 注意） |

境界: 【kj-atlas】—(A: 依頼パッケージ / 共有・書き出し境界)→【人間】→【エージェント】→【人間】—(B: 応答 / import 信頼境界)→【kj-atlas】

## 3. AgentTaskPackage v1（依頼パッケージ）

### 3.1 形態

- **正**: 単一 Markdown「タスクシート」（チャットへ貼り付け/添付可能・人間可読）。
- **随伴（任意）**: `task.json`（下記メタ）＋ `context_bundle.json`（CE1 バンドル抜粋）。Tier 1 のフォルダ授受ではこちらを正とする。

### 3.2 メタスキーマ（task.json / タスクシート冒頭ブロック共通）

```json
{
  "schemaVersion": "agent-task.v1",
  "taskId": "uuid",
  "createdAt": "ISO8601",
  "docId": "string",
  "baseDocSignature": "string (CE3 PatchV1 と同一の文書署名)",
  "bundleHash": "string (CE1)",
  "queryCanonicalHash": "string (CE1)",
  "taskKind": "island_titles | merge_candidates | narrative_draft | opposing_viewpoints | critique_suggestions | free_analysis",
  "locale": "ja"
}
```

### 3.3 タスクシート構成（Markdown・生成順序固定）

1. **依頼**: taskKind 別の指示文（日本語。何を・どの範囲で・何件程度）。
2. **ガードレール**（固定文・省略禁止）: 「あなたの出力は提案であり確定しません／点数・順位・％・優先度の数値を付けないでください／曖昧・対立・未確定はそのまま保持して提示してください／出典のない断定をしないでください／応答は§4の JSON のみで返してください（前後の説明文は不要）」。
3. **文脈**: ContextBundle 抜粋（selected カード/島・relations・evidence・contradictions・reviewFlags 集計）。**Context Query Preview（`previewConfirmed=true`）を経た範囲のみ**。SafeMode 適用済み（redaction 注記付き）。
4. **応答契約**: §4 スキーマのインライン提示＋最小記入例。
5. **相関ブロック**: §3.2 の JSON をコードフェンスで埋め込み（応答へのエコーバック指示付き）。

### 3.3a 制約節（任意・EXT-CONN-03 / agent-constraints.v1 の埋め込みプロファイル）

- 文書の `constraintExportOptIn` が ON（既定 OFF・明示 opt-in）の場合に限り、タスクシートの**ガードレール（2）と文脈（3）の間**に任意節「制約（過去の訂正）」を挿入する。
- 内容: `agent-constraints.v1`（正本: `schemas.md` §18.2）の JSON をコードフェンスで埋め込み、次の固定文を添える: 「以下は過去の人間の判断（違和感・保留・却下）です。同種の提案を繰り返さないでください。制約に重み・点数・順位はありません。制約への回答・遵守報告は不要です」。
- 同梱時は §3.2 相関ブロックに `constraintsHash`（optional）を追加する。応答（agent-response.v1）側に制約への応答フィールドは設けない（`schemas.md` §18.8 往復互換）。
- 安全境界は `schemas.md` §18.5 に従う（未レビューカード ID 不出・SafeMode による note 秘匿・本文フィールドなし）。本節の追加は §3.4 の出力境界を変更しない。

### 3.4 出力境界（必須）

- 書き出しは SharePanel の共有前確認フローに乗せる: SafeMode 状態表示・**未レビュー本文は既定除外**（`includeUnreviewedDrafts` 明示時のみ含む）・出典参照（DOMAIN-TRACE-01 の `Card.meta.seq/source` 系）は既定OFF。起票者・作成者・最終更新者などの主体メタ（CARD-META-UI-01）は、別ゲートで同梱判断が固定されるまで依頼パッケージに含めない。共有直前サマリ（UX-SHARE-01 到達後はそれに従う）。
- `/docs/{id}/export-audit` に `exportKind: "agent-task"` を記録。CE1 の query/bundle 監査連鎖（`ce4.audit.v1`）は既存どおり発火。

## 4. AgentResponse v1（応答契約）

### 4.1 スキーマ

```json
{
  "schemaVersion": "agent-response.v1",
  "taskId": "uuid (依頼のエコーバック・必須)",
  "respondedAt": "ISO8601 (任意)",
  "agent": "string (例: copilot-studio:<agent名> / m365-copilot。自由記述)",
  "proposals": [
    {
      "proposalId": "string (応答内一意)",
      "kind": "island_title | merge_candidate | narrative_draft | opposing_viewpoint | critique | patch",
      "targetRef": { "islandId": "string?", "cardIds": ["string"] },
      "content": { "title": "string?", "text": "string?", "mergedText": "string?" },
      "rationale": "string (必須・なぜそう考えたか)",
      "patch": "PatchV1? (kind=patch のときのみ。baseDocSignature は依頼と一致必須)"
    }
  ]
}
```

### 4.2 制約

- **禁止フィールド**: score / rank / confidence / priority 等の数値評価。厳格モードでは拒否、寛容モードでは**破棄して警告**（反スコアリング）。
- `rationale` 欠落: 厳格=拒否、寛容=「根拠未記載」ラベル付きで受理（提案としては残す＝保全）。
- `patch.ops` は CE3 の PatchOpKind ホワイトリストのみ。`delete_*` を含む patch は取り込み時に**明示の警告バッジ**を付す。
- 文字列は全て `markdown_sanitize` を通す。応答全体に ZIP 取込と同等の容量制限を適用。
- 応答本文中の指示的文言（「これを適用してください」等）は**データとして表示するのみ**で、いかなる自動動作にも接続しない（プロンプトインジェクション境界）。

### 4.3 取り込み経路（種別→既存面）

| kind | 行き先（すべて AI 由来・未レビューの提案として） |
|---|---|
| island_title | 島タイトル候補（既存の候補提示 UI。複数候補・選択/編集/破棄） |
| merge_candidate | MergeSuggestions（既存の採否・監査 `merge-decision-logs`） |
| narrative_draft | Narratives の草稿（レビュー必須のドラフト） |
| opposing_viewpoint / critique | 選択コンテキストの違和感候補（人間が付与を確定して初めて critiqueInputs になる） |
| patch | PatchWorkspace（lint → conflict 検出 → 粒度別採否/保留 → ロールバック） |

### 4.4 非同期整合（staleness）

- 取り込み時に `baseDocSignature` を現文書と照合。不一致（文書が進んだ）の場合: patch は CE3 conflict/rediff 経路で再突合プレビュー、非 patch は `targetRef` 解決を試み、解決不能な提案は**破棄せず「孤立提案」として保持表示**（一匹狼と同じ保全思想）。
- 同一 `taskId`＋同一応答ハッシュの再取込は冪等（重複作成しない）。複数タスクの並行を許す（提案は taskId でグルーピング表示）。

## 5. 状態機械

`drafted →(書き出し・監査) exported →(外部・不透明) awaiting → (取り込み) imported → under-review →(提案ごと) adopted | rejected | held →(適用分) applied(可逆)`

- kj-atlas が保持するのは drafted/exported と imported 以降のみ（awaiting は外部状態であり追跡しない。exported 一覧に「応答待ち」として表示するに留める）。
- すべての採否は既存の決定ログへ（merge 系=`merge-decision-logs`、CE4 系=`context-audit` operation=proposal/apply）。

## 6. 検証レベル（Expected verification）

- 契約: golden fixture（task package 生成のスナップショット・response 取込のラウンドトリップ）＝ unit/integration。
- 不変条件: 「自動確定なし」「スコア破棄」「サニタイズ」「stale 時の非破壊」= integration で固定。
- 利用フロー: 依頼書き出し→（模擬応答貼付け）→提案出現（未レビュー）→1件採用→⌘Z で復帰 = e2e。

## 7. Copilot / Copilot Studio プロファイル（代表運用）

### 7.1 最短運用（追加構築なし・M365 Copilot チャット）

1. kj-atlas で範囲を選び「エージェントへ依頼」を書き出し（タスクシート .md）。
2. Copilot チャットにタスクシートを貼付け（または添付）。
3. 返ってきた JSON（コードフェンス）をコピーし、kj-atlas の「応答を取り込む」へ貼付け。
4. 提案（未レビュー）をレビューし、採用/却下/保留。

### 7.2 Copilot Studio エージェント化（推奨・再現性向上）

- **Instructions テンプレート**（EXT-AGENT-03 で同梱・要点）: 役割=「KJ法支援の候補生成器。確定しない」／§3.3 のガードレール全文／「入力にタスクシートが含まれる場合、応答は agent-response.v1 の JSON のみ。説明文・前置きを付けない」／「相関ブロックの taskId を必ずエコーバック」。
- ナレッジ: 不要（文脈は毎回タスクシートで供給。組織用語集の追加は任意）。
- 配布: Teams/M365 チャネルに公開し、利用者はタスクシートを投げるだけにする。
- **逸脱時リカバリ定型文**: 「直前の応答を、説明文を除き agent-response.v1 スキーマの JSON のみで再出力してください。taskId は <id> です。」

### 7.3 注意（データ境界）

- タスクシートに載るのは SafeMode 適用済み・人間確認済みの範囲のみだが、**組織のエージェント基盤のデータ取り扱い（テナント境界・ログ保持・学習利用設定）は組織側の契約・設定に従う**。運用文書（EXT-AGENT-03）に確認チェックリストを含める。

### 7.4 Tier 1 / Tier 2（将来・概要のみ）

- Tier 1: 受け渡しフォルダ（SharePoint/OneDrive）に task.json/response.json を投函・回収。Power Automate で Copilot Studio 実行を仲介。kj-atlas 本体は無改修（ファイルの書き出し/取り込みは Tier 0 と同一機能）。
- Tier 2: Copilot Studio アクション→kj-atlas API 直接呼び出し。AUTH-*（認証）と到達性の決裁後に別途仕様化（本書は予約のみ）。

## 8. 実装マッピング（Tier 0）

| 要素 | 実装先 | 再利用 |
|---|---|---|
| 依頼書き出し | frontend（SharePanel 系 or 専用パネル）＋ `export/` | ContextQueryPreviewPanel・SafeModePolicy・bundle_export・export-audit |
| 応答取り込み | frontend `import/agent_response_import.ts`（新規） | zip_import の制限値・markdown_sanitize・document/view import の検証パターン |
| 提案化 | 既存面へ変換（§4.3） | MergeSuggestions・Narratives・PatchWorkspace・critique 候補 |
| 監査 | 既存ルート | /export-audit・/context-audit・merge-decision-logs |
| バックエンド | **新規エンドポイント不要**（Tier 0） | — |

## Traceability

- Decision: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`
- Related: `02_Architecture/llm_provider_spec.md`（provider 独立）, `02_Architecture/enterprise_architecture.md`（§4）, `02_Architecture/api.md`（監査）, `02_Architecture/schemas.md`（PatchV1/DocumentV2。§18 = agent-constraints.v1 正本 — §3.3a はその埋め込みプロファイル）
- Related issues: `EXT-AGENT-01` / `EXT-AGENT-02` / `EXT-AGENT-03`, `EXT-CONN-03`（§3.3a）, `issue-CE1-context-query-bundle-foundation.md`, `issue-CE3-patch-workspace-presets.md`
- Derived-from: `ROADMAP.md` 要件D / `ADR-0007` FB-RM-MID-07
