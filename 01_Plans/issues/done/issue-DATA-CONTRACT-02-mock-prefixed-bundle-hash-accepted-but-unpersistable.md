# Issue: DATA-CONTRACT-02 `mock:` プレフィックス付き bundle hash が API では許可されるが DB では拒否される

> ドッグフーディング iteration 50（シナリオ9: CE4 proposal 連鎖の E2E 固定）で発見。

- Type: Bug / Data contract
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/models_ai.py`, `03_Implement/backend/src/kj_atlas_api/models.py`（`AIProposalRow` CheckConstraint）, `03_Implement/backend/src/kj_atlas_api/proposal_decision_repository.py`
- Related ADR/Spec: `02_Architecture/api.md`（proposal・audit 節）, `01_Plans/issues/done/issue-CE4-api-cli-audit-integration.md`
- Expected verification level: `unit`

## 三要素整合（ADR-0067）

- **業務設計（Business）**: `mock:` ハッシュはテスト・評価・モック環境で bundle を識別するための便宜値。プロポーザル登録（`POST /ai/proposals/island-summary`）を E2E で実行すると、`mock:` プレフィックス値で **409 Proposal registration conflicted** になる（実走行で再現）。
- **データ設計（Data）**: `AIProposalRow` の `CheckConstraint("length(source_bundle_hash) = 64")` が **正確に 64 文字** を要求。一方 API 契約 `SOURCE_BUNDLE_HASH_PATTERN` は `[0-9a-f]{64}` または `mock:[0-9a-f]{64}`（**69 文字**）を許可。API と永続層の境界が不一致。
- **機能設計（Function）**: 提案登録 API は pattern 検証だけ通り、DB flush で CheckConstraint 違反 → IntegrityError → 409。クライアントは「登録競合」と誤読し得る（実際は契約不整合）。

## 課題

- 現在の問題: リクエストスキーマ（`SOURCE_BUNDLE_HASH_PATTERN`）が `mock:` プレフィックスを許容する一方、`ai_proposals.source_bundle_hash` の CheckConstraint が `length = 64` を強制しており、**`mock:` 値は API では受理され永続化できない**。`mock:` プレフィックス付きで提案を登録すると 409 が返る。
- 利用者または開発への影響:
  - モック/評価ツールが `mock:` ハッシュで提案登録すると不可解な 409 に当たる。
  - 正しい 64hex を使えば通るため実運用への影響は小さいが、契約の二重正本（API pattern vs DB constraint）が互いに矛盾している。

## 対応方針

- 実施すること（候補案。保守者判断を要する）:
  1. ~~**案a**: `ai_proposals.source_bundle_hash` の CheckConstraint を `length IN (64, 69)` または `mock:` プレフィックス許容に緩和（migration 追加）。~~
  2. **案b（採択）**: `SOURCE_BUNDLE_HASH_PATTERN` から `mock:` を除去し、API も 64hex のみに統一。— 提案APIへの `mock:` 送信はテスト/実コードとも無く（`test_ce2_proposal_api` は 64hex・docs CE4 は独自の runtime policy `ce4_source_bundle_hash_allow_mock` で gate）、migration 不要で API/DB の二重正本が**より厳しい側（64文字）に収束**する。
  3. ~~**案c**: 現状維持 + api.md に明記。~~
- 実施しないこと:
  - bundle hash の実ハッシュ検証ロジックの変更（`sha256` 実値の検証は別途の判断）。
  - docs CE4 経路（`ce4_source_bundle_hash_allow_mock`）の変更 — 独自の policy gate として維持。

## 受入条件

- [x] 採択案に応じて、API 契約と DB 制約が一致する（`mock:` が両方で通る or 両方で拒否される）。— 案b で **API パターンを 64hex のみへ統一**（DB 制約と一致）。`mock:` は API 境界で 422。
- [x] シナリオ9 の E2E（64hex 使用）が引き続き pass する。— **39/39 pass**。proposal 回帰（test_ce2 他）58 tests pass。

## 検証計画

- 実行する確認: `POST /ai/proposals/island-summary` を `mock:` ハッシュで呼び 409 になること（穴の存在）と、採択案適用後の挙動。
- 期待結果: 契約が単一の正本に収束する。
