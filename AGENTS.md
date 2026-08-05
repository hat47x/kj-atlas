# AGENTS.md

このファイルは、生成AIが kj-atlas で作業を始めるための最小入口です。リポジトリ全体を先読みせず、現在のタスクに必要な正本とコードだけを参照してください。

## 1. 必須ルール

1. 変更範囲を絞り、既存の利用者変更を取り消さない。
2. 仕様と実装が矛盾する場合は、現在の正本を確認してから修正する。
3. 変更リスクに応じたテストを実行し、未実施項目は明記する。
4. SafeMode、共有・export、import、AI提案に関わる安全不変条件を緩和しない。
5. 現在のissueだけを更新し、同じ進捗を複数の台帳へ転記しない。

## 2. 最小読取ルール

通常は次の順で十分です。

1. 本書
2. 変更対象のコードと近接テスト
3. 下表から該当する正本を1〜2件
4. 作業対象のActive issue memo（存在する場合）

| タスク | 先に読む正本 |
|---|---|
| 価値・要件判断 | `01_Plans/adr/ADR-0001-value-to-requirements.md` |
| 用語・KJ法の概念 | `00_Prompt/domain.md` |
| KJ法の実行（束ね・表札・空白・検査） | `00_Prompt/kj_technique.md` |
| カード品質 | `00_Prompt/qualitative_card_quality_requirements.md` |
| W型反復 | `00_Prompt/w_type_iterative_inquiry_requirements.md`, `02_Architecture/design/inquiry_journey_model.html` |
| 全体構成 | `02_Architecture/design/architecture.html` |
| Document契約・互換性 | `01_Plans/adr/ADR-0058-document-contract-v1-rebaseline.md`, `02_Architecture/schemas.md` |
| API | `02_Architecture/api.md` |
| 環境変数 | `02_Architecture/runtime_parameter_registry.md` |
| UI/UX | `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md` |
| SafeMode・脅威 | `THREAT_MODEL.md` と対象ポリシー実装 |
| LLM | 該当する `02_Architecture/llm_*.md` |
| 利用者向け手順 | `04_Documentation/public_index.md` から該当文書へ進む |
| 開発・CI | `CONTRIBUTING.md`, 対象workflow, 対象パッケージのREADME |

次の文書は、タスクが直接関係するときだけ読みます。

- 過去ADR、Done issue、`02_Architecture/history/`
- `01_Plans/project-progress-dashboard.md`
- `01_Plans/issues/decision-pack-2026-03-human-judgement.md`
- `00_Prompt/agent_handover.md`
- Claude Codeなど特定ツールの運用文書

全ADR、全issue、00〜04の全ファイルを作業開始時に読む必要はありません。検索や `01_Plans/triage_actionable_plans.py` で対象を絞ってください。

## 3. ディレクトリの役割

| パス | 役割 |
|---|---|
| `00_Prompt/` | プロダクト固有の概念・要件 |
| `01_Plans/adr/` | 長期的な設計判断 |
| `01_Plans/issues/` | 実行可能な内部タスク |
| `02_Architecture/` | 現行の設計・契約 |
| `03_Implement/` | frontend、backend、MCP、deployとテスト |
| `04_Documentation/` | 一般利用者・運用者向けガイド |

人間向け入口は `README.md`、一般公開文書の入口は `04_Documentation/public_index.md` です。

### 文書の形式（2026-08-05改定）

- `01_Plans/`（ADR・issue）は Markdown を維持します。正規化・機械検証・差分レビューの対象であり、形式を揺らしません。
- **新規の `02_Architecture/` 設計文書は、原則 HTML + Mermaid 単独（`.dc.html`）で作成します。** Markdown を並行して作らない。理由は継ぎ目のドリフトです（`02_Architecture/contract-seam-integrity-2026-08-05.html` が実例と根拠を示す：手保守で二重化された契約表現は片方だけが更新されドリフトするが、単一表現ならその余地がない）。対象読者は開発者であり、構造・状態遷移・階層を図で伝えることが認知負荷を下げる目的に直結する文書（アーキテクチャ、状態機械、承認フロー、DAG的データモデル等）から優先する。純粋な原則列挙・箇条書き方針文書まで無理に図解化する必要はない。
- **既存 Markdown 設計文書は、図解が必要になった段階で HTML + Mermaid 化し、Markdown を退役させます。** 変換時は参照元リンクをすべて新パスへ置き換える（`git grep -l 'ファイル名\.md'` で洗い出す）。**旧来のように Markdown 側を正本として残し続けることはしません** — 双方向に手保守される表現はどちらかがドリフトする、というのが上記実例で確認された構造的リスクだからです。参照コストは変換時の一括更新で払い切り、その後の継続コストにしない。
- 文書HTMLはリンク切れ検査の対象です（`DX-DOC-07`）。`00_Prompt` / `01_Plans` / `02_Architecture` / `04_Documentation` 配下の追跡HTMLが対象で、アプリ・ビルド成果物のHTMLは除外されます（`03_Implement/frontend/index.html` の `src="/src/main.tsx"` は dev server 基準であり、リポジトリ基準ではないため）。
- Mermaid は CDN 取得で構いませんが、**`.dc.html` は `file://` で直接開く運用を前提とするため ES module 版（`.esm.mjs`）を使わない。** Chrome は `file://` 上の module script を CORS でブロックし、図が全て空白になる。UMD版（`mermaid.min.js`）を classic `<script>` で読み込む。
- `<x-dc>` ランタイム（`support.js`）は読み込み後に DOM を非同期で再構築し、その前に描画した Mermaid SVG を破棄する。`mermaid.initialize({ startOnLoad: false, ... })` とし、`MutationObserver` で `.mermaid:not([data-processed])` を検出するたびに再描画する（`contract-seam-integrity-2026-08-05.html` の実装を雛形にする）。
- 新規・既存いずれの `.dc.html` も、Claude Design のエクスポート形式（`<x-dc>` + `<script src="./support.js">` + `helmet`）を保持する。

## 4. 作業手順

1. **確認**: 対象、期待結果、非目標を短く定める。
2. **変更**: 既存パターンに沿って最小差分で実装する。
3. **検証**: 近接テストから始め、影響が広い場合だけ範囲を広げる。
4. **記録**: 変更理由、検証結果、残課題をissueまたはPRへ一度だけ記録する。

固定の5フェーズ、rerun番号、Stream別同期ログ、複数台帳の件数同期、毎回のRACI更新は不要です。

### 失敗からの学習

作業中に遭遇した失敗（CIエラー、コンフリクト解決ミス、環境不具合、手順の見落としなど）は、**原因分析と対応内容を自律的に記録し、次回から参照**してください。記録の対象・形式・参照タイミングは `01_Plans/agent_failure_lessons.md`、実記録は `01_Plans/agent_failure_log.md` にあります。

- 検証（テスト・typecheck・lint）が失敗したとき、マージ・リベース前後、環境依存エラーに遭遇したときは、まず `agent_failure_log.md` に同じ失敗の記録がないか確認する。
- 復旧が完了したその場で、事象・原因・対応・再発防止の4点をログへ追記する（後回しにしない）。
- ログは簡潔に（1件5〜15行）、issue/PRの進捗欄には書き込まない。

## 5. 変更時の追随範囲

- Document契約変更: `ADR-0058`、`schemas.md`、`api.md`、frontend/backend/MCPの契約と関連テストを確認する。
- API変更: `api.md`、client/server、契約テストを確認する。
- 環境変数変更: `KJ_ATLAS_*` 命名を守り、`runtime_parameter_registry.md` と設定例を同期する。
- UI視覚変更: 対象画面を実ブラウザで確認する。スクリーンショットは公開文書または視覚回帰の根拠として必要な場合だけ更新する。
- SafeMode・共有・import変更: fail-closed、proposal-only、人手レビュー境界を対象テストで確認する。

無関係なダッシュボード、decision-pack、過去ログ、全Project Mapを同じPRで更新しません。

## 6. ガバナンス

現段階は個人OSS・プレリリースであり、`ADR-0039` を適用します。

- 意思決定者と実行者は `Maintainer` に集約する。
- issue memoは `Type / Status / Source Issue / Priority / Scope / Related ADR / Expected verification level / Acceptance / Validation` を最小項目とする。
- ADRは、長期的・横断的・破壊的な契約変更、安全境界変更、複数の合理的選択肢が残る場合に限る。
- 2者承認、Decision Queue、RACI、KPIは、実ユーザーまたは継続的な協力者が現れるまで既定では使わない。
- 進捗の正本はActive issue memoとGit履歴であり、手書きダッシュボードは正本にしない。
- issue本文に記録された未決事項（`DecisionStatus: Pending` 等）は、**何が未決かの記録であり、それ自体が着手を禁じるゲートではありません。** 未決のまま進められる部分は進め、決定が必要になった時点で判断を仰いでください。ただし SafeMode・`human_reviewed`・外部共有条件・自動適用に触れる変更は例外で、`GENAI-GOV-01`（`02_Architecture/value_traceability.md` §2.9）のとおり実装PRより先にADRまたは内部issueで扱います。
- 決定済みの参照（採択済みADRを指す `DecisionStatus: Fixed` 等）はissue本文へ書き写さない。ADR側のStatusが正本であり、二重管理は取りやめました。

削減対象と再導入条件は `01_Plans/lean_operations_inventory.md` を参照してください。

## 7. 安全不変条件

- SafeModeは既定ON。
- AI出力はproposal-onlyで、自動適用しない。
- `human_reviewed` は人間だけが設定する。
- `KJ_ATLAS_LLM_PROVIDER=none` でも主要価値が成立する。
- share/exportで未レビュー情報や秘密情報を意図せず共有しない。
- import/zip/markdownは不正入力を安全側で拒否または無害化する。

## 8. 本書の更新

本書はパス単位の入口に留めます。個別ファイルを追加するたびに一覧へ追記せず、タスク別の正本が変わった場合だけ更新してください。新しい契約やADRは、全件読取へ追加せず、該当タスクの行だけを更新します。
