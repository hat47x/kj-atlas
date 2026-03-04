# Issue Draft: AUTH-E2E-01 AuthContext contract Level1/Level2 regression track

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: QA Lead
- Scope: `03_Implement/frontend/`, `03_Implement/backend/`, `04_Documentation/e2e_testing.md`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0019`, `ADR-0020`, `04_Documentation/e2e_testing.md`, `02_Architecture/llm_runtime_constraints.md`
- Expected verification level: `e2e`

## RACI（簡易）

| 区分 | Role |
|---|---|
| R (Responsible) | QA Lead |
| A (Accountable) | Platform Architecture Owner |
| C (Consulted) | Auth Architecture Lead, Backend Lead, Frontend Lead |
| I (Informed) | PM/Triage |

## 1) 課題 / Problem statement

- ADR-0020 で定義された Level1/Level2 E2E の常時維持/条件付き維持が、active issueとして管理されていない。
- AUTH実装変更時に「どのE2Eを最低限回すか」がPRごとに揺れて回帰漏れが発生し得る。
- Mock SP/IdP fixture 回帰をいつ実施すべきか判断基準が散在している。

## 2) 背景 / Context

- ADR-0019 は結合バグを仕様レビュー前に除去する品質ゲートを規定。
- ADR-0020 は認証文脈で Level1必須 / Level2条件付き必須を規定。
- 現在 AUTH系 issue memo が Done 2件で止まり、E2E運用タスクの active 管理が空白化している。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 認証回帰は利用不能に直結し、価値提供を阻害する。
- 安全（THREAT_MODEL / SafeMode）: trusted proxy 境界やヘッダー契約の崩れを早期検知できる。
- 企業・行政要件（enterprise_architecture）: IdP連携の回帰証跡は導入審査で要求されやすい。
- 後方互換（schemas）: 認証属性契約（header/JWT）の互換を継続検証できる。

## 4) 提案する解決策 / Proposed solution

- 変更対象: E2E suite整理 + 運用手順明文化。
- 最小単位:
  - Level1固定シナリオ定義
  - Level2トリガー判定表
  - fixture管理と失敗時の記録テンプレ
- 非目標:
  - 全認証ケースの網羅E2E化
  - 本番IdP実機接続の常時実行
  - 認可仕様（RBAC）詳細検証

## 5) 受入条件 / Acceptance criteria

- [ ] Level1（AuthContext契約E2E）の必須シナリオと実行コマンドが固定される。
- [ ] Level2（Mock SP/IdP）は「IdP連携境界変更時に必須」の判定チェックリストを持つ。
- [ ] PRテンプレまたは運用文書に、実施/未実施理由の記録フォーマットが追加される。
- [ ] e2e レベルの検証（integration含む）を実施し、結果を追跡できる。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1: `04_Documentation/e2e_testing.md` に AUTH向け Level1/Level2 実行基準を追記する。
- [ ] T2: Playwright（または既存E2E基盤）で Level1 smoke フローを固定する。
- [ ] T3: Level2 fixture（主要IdP様式）を1つ以上回帰対象として定義する。
- [ ] T4: PR記録テンプレ（pass/fail/未実施理由）を整備する。
- [ ] T5: AUTH-API-02 / AUTH-IMPL-01 へ検証依存をリンクする。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "Level 1|Level 2|AuthContext|Mock SP/IdP" 01_Plans/adr/ADR-0020-oidc-saml-mock-idp-sp-profile.md 04_Documentation/e2e_testing.md`
  - `playwright test -g "auth"`
- 期待結果:
  - AUTH E2Eの必須/条件付き必須が文書化され、実行結果を一貫記録できる。
- 未実施時の理由・代替検証:
  - CIでブラウザ実行不可の場合は backend API contract test + fixture snapshot で代替し、後続でE2E実施を必須化する。

## 8) 代替案 / Alternatives considered

- 代替案A: unit/integration のみで認証回帰を吸収。
  - 却下理由: proxy/headers/UI連動境界の不具合を検知しにくい。
- 代替案B: Level2 を常時必須化。
  - 却下理由: 実行コストが高く、変更非該当PRの開発速度を過度に落とす。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: E2E flaky 増加で運用疲弊、または未実施容認で回帰漏れ。
- 影響範囲: CI時間、認証品質、PRレビュー運用。
- ロールバック手順: Level1を最低固定し、Level2は該当PRのみへ段階適用して安定化する。

## 10) Additional context

- 関連Issue/PR/議論ログ: N/A
- Source Issue記載方針: GitHub Issues正本運用の開始宣言までは `N/A` を維持し、開始宣言後の次回更新PRで対応URLへ切替する。
- ADR化が必要になる条件: Level2常時必須化など、E2Eポリシー自体を変更する場合。
