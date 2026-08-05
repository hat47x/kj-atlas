# Issue Draft: QA-SMOKE-08 doc_phase1_canvas 読み込み時の API 500 切り分け

- Type: Bug
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex
- Scope: `03_Implement/frontend/`, `03_Implement/backend/`, `03_Implement/deploy/`
- Related Backlog: `QA-SMOKE-08`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `03_Implement/frontend/docs/e2e_testing.md`, `04_Documentation/installation.md`, `04_Documentation/diagnostics.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: QA-SMOKE-08
- RequirementStatement: 標準サンプル `doc_phase1_canvas` を開いたとき、必要プロセス起動済みの環境では `/api/docs/doc_phase1_canvas` が 500 にならず、利用者がキャンバス読み込みエラーなしで操作を開始できる。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=installation/e2e 手順に沿って frontend と backend を起動 / 操作=Chromium で `http://127.0.0.1:5173/?locale=ja` を開く / 期待結果=`/api/docs/doc_phase1_canvas` が 2xx で返り、画面本文に `Internal Server Error` が出ない / 除外=backend を起動しない frontend-only 開発時の既知の接続失敗。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

- 2026-05-14 のブラウザ smoke で `http://127.0.0.1:5173/?locale=ja&i18nAudit=1778707096017` を開いたところ、`/api/docs/doc_phase1_canvas` が 500 を返し、画面本文に `Internal Server Error` が表示された。
- 2026-05-14 18:00台の再確認で、port 8000 の backend が未起動だったことを確認した。`03_Implement/backend` から backend を起動すると backend 直アクセス、frontend proxy 経由ともに `doc_phase1_canvas` は 200 で返った。
- 同時に UI 本体は表示され、レイアウト見切れや主要ラベルの未翻訳は検出されなかったため、frontend 表示崩れとは別に API/起動手順/fixture 初期化の切り分けが必要。
- 標準サンプルは 04 文書のスクリーンショットや受け入れ確認の前提になっているため、利用者向け確認でエラーが混ざると文書品質と導入体験を損なう。

## 2) 背景 / Context

- `04_Documentation/installation.md` は Docker あり/なしの起動手順を案内している。
- `04_Documentation/diagnostics.md` は `/api/docs/<doc_id>` の status code と backend logs を確認対象としている。
- `03_Implement/frontend/docs/e2e_testing.md` は開発者向けの E2E 正本であり、標準サンプルを使う smoke もここで管理する。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 初回起動で標準サンプルが開けることは、KJ Atlas の価値を体験する入口になる。
- 安全（THREAT_MODEL / SafeMode）: 直接の安全境界変更ではないが、エラー時に詳細ログや内部情報を画面へ出しすぎない確認が必要。
- 企業・行政要件（enterprise_architecture）: 運用導入時のヘルスチェックと監視に接続できる状態が望ましい。
- 後方互換（schemas）: fixture/schema/DB seed の不整合が原因の場合、既存 document schema との互換性確認が必要。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - backend `/api/docs/{doc_id}` route と seed/fixture 初期化
  - frontend API error 表示とフォールバック可否
  - installation / diagnostics / E2E 手順
- 最小単位:
  - まず backend 単体で `doc_phase1_canvas` の取得可否とログを確認する。
  - 次に frontend dev proxy 経由で同じ URL を確認する。
  - 最後に Playwright smoke で画面本文に 500 が混入しないことを固定する。
- 非目標:
  - LLM provider や merge candidate fallback の仕様変更。
  - 標準サンプルの内容刷新。

## 5) 受入条件 / Acceptance criteria

- [x] `curl http://127.0.0.1:5173/api/docs/doc_phase1_canvas` または同等の proxy 経由確認で 2xx が返る。
- [x] backend 直アクセスでも `doc_phase1_canvas` が取得できるか、存在しない場合は明確な 404/初期化手順が返る。
- [x] Chromium smoke で画面本文に `Internal Server Error` が出ない。
- [x] 失敗時に利用者へ出す文言が過度に内部実装へ寄らない。
- [x] `03_Implement/frontend/docs/e2e_testing.md` に再現コマンドまたは確認観点が反映される。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 frontend dev proxy と backend 直アクセスの response/log を採取する。
- [x] T2 `doc_phase1_canvas` の seed/fixture/DB 初期化契約を確認する。
- [x] T3 原因に応じて route、seed、起動手順、または frontend error 表示を最小修正する。
- [x] T4 Chromium smoke と文書化で再発時の切り分け手順を固定する。自動 Playwright 追加は、今回の原因が backend 未起動であり実装回帰ではないため非採用。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `curl -i http://127.0.0.1:5173/api/docs/doc_phase1_canvas`
  - `curl -i http://127.0.0.1:8000/docs/doc_phase1_canvas`
  - `cd 03_Implement/frontend && node node_modules/vitest/vitest.mjs run <affected tests>`
  - `cd 03_Implement/frontend && npx playwright test <smoke spec>`
- 期待結果:
  - 標準サンプル取得が成功し、画面本文に `Internal Server Error` が残らない。
- 未実施時の理由・代替検証:
  - backend が起動できない環境では、route 単体テストと fixture 検証で代替し、E2E は再開条件として残す。

## 8) 代替案 / Alternatives considered

- 代替案A: frontend-only 時は常にローカルfixtureへフォールバックする。backend 実接続の失敗を隠す恐れがあるため、明示条件付きに限る。
- 代替案B: 標準サンプルを frontend bundle に固定同梱する。DB/API契約の検証が弱くなるため、主経路としては採用しない。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 500 の根本原因を隠す UI fallback を入れ、backend の初期化不備を見逃す。
- 影響範囲: 初回起動、スクリーンショット取得、E2E smoke、導入手順。
- ロールバック手順: fallback や seed 修正を戻し、診断手順で既知制限として扱う。

## 10) Additional context

- 2026-05-14 smoke:
  - `GET http://127.0.0.1:5173/api/docs/doc_phase1_canvas` -> 500
  - 画面本文に `Internal Server Error`
  - 主要UIラベルの日本語化と右端見切れは同時確認では再発なし
- 2026-05-14 follow-up:
  - backend process was not running on `127.0.0.1:8000` when the 500 occurred.
  - backend 起動後: `http://127.0.0.1:8000/healthz` -> 200
  - backend 起動後: `http://127.0.0.1:8000/docs/doc_phase1_canvas` -> 200, `id=doc_phase1_canvas`, `cards=3`
  - backend 起動後: `http://127.0.0.1:5173/api/docs/doc_phase1_canvas` -> 200, `id=doc_phase1_canvas`, `cards=3`
  - Chromium smoke で代表的な未翻訳ラベルと右端見切れは検出なし。`Internal Server Error` も消えた。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
