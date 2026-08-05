# Issue: CORE-VALUE-GUARD-01 根幹価値不変条件（CVI）の横断ガードテスト

> 個人OSS段階（`ADR-0039`）の軽量起票。`ADR-0041` の実装入口。重量級RACI/KPIは課さない。

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P0
- Owner: Codex
- Scope: `03_Implement/frontend/`, `03_Implement/backend/tests/`, `02_Architecture/value_traceability.md`
- Related Backlog: `CORE-VALUE-GUARD-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0041-core-value-invariants-single-guard.md`, `02_Architecture/value_traceability.md`（§2.5 CVI 正本）
- Expected verification level: `unit`

## 1) 課題 / Problem statement

根幹価値の非後退不変条件（CVI-1..7：SafeMode既定ON / proposal-only / `human_reviewed`人手昇格 / Consensus直接更新禁止 / dryRun無副作用 / provider=none成立 / 保留・違和感の非破壊）を守るテストが**実装に散在**しており（`safe_mode.test.ts` / `ce2_proposal_only.test.ts` / `ce2_suggestion_candidates.test.ts` / backend `test_ce2_proposal_api.py` / `test_audit.py` 等）、横断的に1つで守る砦が無い。並行実装が進む中、1つの PR が静かに1条件を後退させても、関連個別テストが変更対象でなければ気づけない。

## 2) 背景 / Context

- `ADR-0041` が CVI-1..7 を定義し、正本を `value_traceability.md` §2.5 の対応表に索引化した。
- 各 CVI には既に担保する個別テストが存在する（§2.5 参照）。本issueは**再実装ではなく索引化＋欠落補完**。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 根幹価値そのものの保護。最優先（P0）。
- 安全（THREAT_MODEL / SafeMode）: CVI-1（SafeMode）/ CVI-5（dryRun）の後退は安全境界の崩壊に直結。
- 後方互換（schemas）: テスト追加のみでスキーマ・挙動は変えない。

## 4) 提案する解決策 / Proposed solution

- 変更対象（テストのみ、挙動変更なし）:
  - CVI-1..7 を集約参照する**単一の横断テスト**を新設（frontend に1ファイル、必要なら backend に対の1ファイル）。
  - 各 CVI が「どの既存テスト／コード契約で担保されるか」を参照リンク（source-string contract 方式で可）として列挙。
  - 既存テストで担保されていない CVI があれば、その最小ケースのみ新規追加。
- 最小単位: まず索引（既存テストの存在＋契約文字列の確認）。欠落 CVI のみ実ケース追加。
- 非目標: 新しい不変条件の追加・厳格化、形式手法の導入、既存テストの再実装。

## 5) 受入条件 / Acceptance criteria

- [ ] CVI-1..7 を一覧で確認できる単一の横断テストが存在し、緑である。
- [ ] 各 CVI が `value_traceability.md` §2.5 の担保テスト/契約に 1:1 で対応づく。
- [ ] 担保が欠落していた CVI は最小ケースで新規カバーされる（無ければ「全CVI既存担保あり」を明記）。
- [ ] スキーマ・実行挙動に変更がない（テスト追加のみ）。
- [ ] CI（既存 vitest/pytest 実行）に含まれ、回帰時に赤になる。

## 6) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && node ./node_modules/vitest/vitest.mjs run <new guard test>`
  - `cd 03_Implement/backend && pytest -q <new guard test>`（backend 対が必要な場合）
  - `rg -n "CVI-[1-7]" 02_Architecture/value_traceability.md 03_Implement`
- 期待結果: CVI-1..7 が単一テストで確認でき、§2.5 と整合する。
- 未実施時の代替: 実装前は §2.5 の対応表レビューで担保有無を確認。

## 7) リスクとロールバック / Risks & rollback

- 失敗モード: source-string contract が実挙動と乖離（文字列はあるが挙動が後退）。→ 重要 CVI（CVI-1/2/3/5）は挙動アサーションも持たせる。
- 影響範囲: テストのみ。ロールバック=ガードテスト無効化（挙動非依存のため安全）。

## 8) Additional context

- 専用CIジョブの新設は必須でない（`ADR-0039` 軽量運用）。既存テスト実行への同梱でよい。
- ADR化が必要になる条件: CVI の追加・変更が必要になった場合は `ADR-0041` を改訂してから本issueを更新する。
