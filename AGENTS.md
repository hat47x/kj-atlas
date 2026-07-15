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
| 用語・KJ法 | `00_Prompt/domain.md` |
| カード品質 | `00_Prompt/qualitative_card_quality_requirements.md` |
| W型反復 | `00_Prompt/w_type_iterative_inquiry_requirements.md`, `02_Architecture/inquiry_journey_model.md` |
| 全体構成 | `02_Architecture/architecture.md` |
| データ型・互換性 | `02_Architecture/schemas.md` |
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
- `00_Prompt/virtual_stakeholder_consensus.md`
- GSD、RTK、Claude Codeなど特定ツールの運用文書

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

## 4. 作業手順

1. **確認**: 対象、期待結果、非目標を短く定める。
2. **変更**: 既存パターンに沿って最小差分で実装する。
3. **検証**: 近接テストから始め、影響が広い場合だけ範囲を広げる。
4. **記録**: 変更理由、検証結果、残課題をissueまたはPRへ一度だけ記録する。

固定の5フェーズ、rerun番号、Stream別同期ログ、複数台帳の件数同期、毎回のRACI更新は不要です。

## 5. 変更時の追随範囲

- Schema変更: `schemas.md`、import/export/validation、関連テストを確認する。
- API変更: `api.md`、client/server、契約テストを確認する。
- 環境変数変更: `KJ_ATLAS_*` 命名を守り、`runtime_parameter_registry.md` と設定例を同期する。
- UI視覚変更: 対象画面を実ブラウザで確認する。スクリーンショットは公開文書または視覚回帰の根拠として必要な場合だけ更新する。
- SafeMode・共有・import変更: fail-closed、proposal-only、人手レビュー境界を対象テストで確認する。

無関係なダッシュボード、decision-pack、過去ログ、全Project Mapを同じPRで更新しません。

## 6. ガバナンス

現段階は個人OSS・プレリリースであり、`ADR-0039` を適用します。

- 意思決定者と実行者は `Maintainer` に集約する。
- issue memoは `Type / Status / Lifecycle / Source Issue / Priority / Scope / Related ADR / Expected verification level / Acceptance / Validation` を最小項目とする。
- ADRは、長期的・横断的・破壊的な契約変更、安全境界変更、複数の合理的選択肢が残る場合に限る。
- 仮想ステークホルダー会議、2者承認、Decision Queue、RACI、KPIは、実ユーザーまたは継続的な協力者が現れるまで既定では使わない。
- 進捗の正本はActive issue memoとGit履歴であり、手書きダッシュボードは正本にしない。

削減対象と再導入条件は `01_Plans/lean_operations_inventory.md` を参照してください。

## 7. 安全不変条件

- SafeModeは既定ON。
- AI出力はproposal-onlyで、自動適用しない。
- `human_reviewed` は人間だけが設定する。
- `KJ_ATLAS_LLM_PROVIDER=none` でも主要価値が成立する。
- share/exportで未レビュー情報や秘密情報を意図せず共有しない。
- import/zip/markdownは不正入力を安全側で拒否または無害化する。

## 8. ツール出力

長い `git`、test、build、log出力は、正確な全文が不要なら `00_Prompt/codex_rtk_token_saving_ops.md` に従ってRTKで圧縮します。診断に情報が不足した場合だけ、必要最小範囲を通常コマンドで再実行します。

## 9. 本書の更新

本書はパス単位の入口に留めます。個別ファイルを追加するたびに一覧へ追記せず、タスク別の正本が変わった場合だけ更新してください。
