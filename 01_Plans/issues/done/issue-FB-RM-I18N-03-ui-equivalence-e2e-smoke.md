# Issue Memo: FB-RM-I18N-03 UI equivalence E2E smoke gate

- Type: QA/E2E
- Status: Done
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P1
- Scope: `03_Implement/frontend/e2e/`, `01_Plans/issues/`
- Related Backlog: `FB-RM-I18N-03` (`01_Plans/adr/ADR-0007-future-backlog.md`)
- Expected verification level: `e2e`

## Goal

直近の i18n 等価化変更に対して、価値境界ベースの最小有効E2E（smoke + 変更フロー）を追加し、
Compose不可環境でも SQLite 代替経路で品質ゲートを継続できる状態を作る。

## Added scenario

- `e2e/i18n_locale_query_equivalence.spec.ts`
  - smoke: `?locale=en` で主要シェル導線（Share / View）が英語表示になる
  - flow: `?locale=en` で Share Panel の `Load document.json -> Replace current document` が成功し、カード表示まで到達

## Validation log (2026-03-02)

- Compose優先経路:
  - `docker compose version` -> 未実施（環境に docker コマンドが存在しない）
- SQLite代替経路:
  - backend: `uvicorn kj_atlas_api.main:app --host 127.0.0.1 --port 8000`
  - frontend: `npm run dev -- --host 127.0.0.1 --port 4173`
  - health:
    - `curl -fsS http://127.0.0.1:8000/healthz` -> pass
    - `curl -fsS http://127.0.0.1:4173/api/healthz` -> pass
  - docs roundtrip:
    - `PUT /docs/e2e-qa-roundtrip` -> pass
    - `GET /docs/e2e-qa-roundtrip` -> pass
  - Playwright:
    - `npm run e2e -- e2e/i18n_locale_query_equivalence.spec.ts` -> pass
    - 再実行（flake check）`npm run e2e -- e2e/i18n_locale_query_equivalence.spec.ts` -> pass

## Task contract freeze (2026-03-03)

### Scope
- Frontend i18n functional-equivalence verification for ja/en in unit + E2E.
- Observation points are fixed as: **操作可否 / 表示文言 / 副作用（永続状態） / export結果**.
- SafeMode + readOnly behavior parity verification in ja/en.

### Non-Goals
- 新規ロケール追加（fr等）は対象外。
- 文言改善・翻訳品質改善（意訳調整）は対象外。
- API/Backend のlocale-aware behavior追加は対象外。

### Acceptance Criteria (AC)
- [x] AC1: ja/en切替で主要UI操作（Share導線・document置換）が同一に成立する（E2E）。
- [x] AC2: ja/enでSafeMode + readOnlyの禁止操作・固定マスク挙動が同値（E2E）。
- [x] AC3: ja/enで辞書キー等価 + fallback契約（requested -> ja -> key）を維持（unit）。
- [x] AC4: export結果はlocaleに依存せず決定論が維持される（unit）。
- [x] AC5: VerifyでAC/DoD照合結果を記録し、未達なら原因/次手を明記。

### Checks
- [x] unit: i18n translate / i18n UI equivalence / bundle export locale-independence
- [x] e2e: locale=en smoke + replace flow, visibility persistence, safeMode/readOnly parity (ja/en)
- [x] contract: fallback order and dictionary key-equivalence remain green

## Verify (AC / DoD cross-check)

| ID | 判定 | 根拠 |
|---|---|---|
| AC1 | ✅ 達成 | `i18n_locale_query_equivalence.spec.ts` と `pub_visibility_i18n_readonly_flow.spec.ts` の locale=en flow が pass。 |
| AC2 | ✅ 達成 | `i18n_locale_functional_equivalence.spec.ts` で ja/en それぞれ readOnly + SafeMode locked context を確認。 |
| AC3 | ✅ 達成 | `src/i18n/translate.test.ts` で fallback順序・辞書キー等価テストが pass。 |
| AC4 | ✅ 達成 | `src/export/bundle_export.test.ts` の locale差分非依存ハッシュ検証が pass。 |
| AC5 | ✅ 達成 | 本セクションでAC/DoD全照合を明文化。 |

### 未達
- なし。

### 備考
- E2E実行時に dev server から `/docs/*` proxy の `ECONNREFUSED` 警告は出るが、今回のフローは UI-only でテストはすべて pass。


## Context / Decision / Consequences (Stream H addendum, 2026-05-02)

### Context
- I18N-03 は `Done` だが、回帰監視観点が E2E 1 系統（query locale）に偏っている。
- RM stream（MID/SEC/I18N/RS）を独立運用する場合、I18N 側の失敗を feature-level で局所検知できる DoD 文面が必要。

### Decision
- 本メモの AC/DoD は維持し、追加の **運用DoD案** を提案として固定する（実装変更なし）。
- 追加DoD案: 「`src/i18n/*.json` の key set 差分を CI で fail-fast 検知する専用チェックを I18N lane の必須ゲートに含める」。

### Consequences
- 利点: 翻訳差分起因の UI 欠損を unit/E2E 実行前に検出でき、RS/SEC lane へ影響波及しにくくなる。
- トレードオフ: CI チェック追加時に locale追加PRの手順が増えるため、`I18N-04` 以降で運用テンプレート整備が必要。

## AC/DoD gap draft proposal (for next RM-I18N cycle)

- Draft-AC-G1: locale key-set drift を検知する静的テストが `npm run test:regression-guards` に常時含まれること。
- Draft-AC-G2: locale query 不正値（例: `?locale=zz`）時に `requested -> ja -> key` へ収束する E2E を 1 本追加すること。
- Draft-DoD-G3: 失敗時は I18N lane 単独で再現可能な最小 fixture（document 1件）を保持すること。

### Gap resolution note (2026-06-03)

- `Draft-AC-G2` は `03_Implement/frontend/e2e/i18n_locale_query_equivalence.spec.ts` で検証済み。
- シナリオ: `/?locale=zz` で日本語の主要ボタン（`共有と再現`, `表示`）が表示され、英語ボタン（`Share & Reproduce`, `View`）が表示されないことを確認する。
- Browser check: `http://127.0.0.1:4173/?locale=zz` -> `共有と再現`: 1, `表示`: 1, `Share & Reproduce`: 0, `View`: 0。
- Validation: `node .\node_modules\playwright\cli.js test e2e/i18n_locale_query_equivalence.spec.ts --reporter=line` -> 3 passed。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- Dependencies: `FB-RM-I18N-03` (`01_Plans/adr/ADR-0007-future-backlog.md`)
- 重複Backlog: 該当なし。


## Stream H realignment (2026-05-04)

### Phase 1: Read同期（依存/優先度再評価）
- 系列依存の再評価: `I18N -> MID -> RS -> SEC` を基本順とし、`FB-RM-I18N-03-ui-equivalence-e2e-smoke` はこの順序に従って前後の成果物契約を参照する。
- 優先度再評価: reversible synthesis の実装引き渡し観点で、**決定論（reproducibility）** と **監査可能性（auditability）** を同列最優先とする。

### Phase 2: Plan（A1/A2 契約）
- A1（実装契約依存点）: downstream 実装は本メモの `Acceptance criteria` と `Validation plan` を満たす I/F を維持する。
- A2（モック先行可能点）: deterministic 候補生成・監査出力フォーマット・固定フィクスチャを先行モック化して検証可能。

### Phase 3: Execute（I/F・出力・監査証跡・Proceed条件）
- 入力I/F: Document/locale/query/export context など、本メモで規定済みの入力契約を採用。
- 期待出力: 同一入力で同一順序/同一内容の出力を返す（非決定挙動を禁止）。
- 監査証跡: 実行コマンド、判定結果、失敗理由、再試行回数を issue memo に記録する。
- Proceed条件: AC/DoD が満たされ、依存系列の受入条件と矛盾しないこと。

### Phase 4: Verify（欠落検査 + 自己修復）
- 決定論要件と監査要件の欠落をチェックし、欠落時は最大3回まで自己修復を試行する。
- 3回で是正不可の場合はフェイルセーフ停止（非決定仕様混入 / 監査要件欠落 / 依存矛盾）。

### Phase 5: Proceed（実装引き渡し優先度）
- Frontend/Backend 実装への引き渡しは、`I18N-02 -> MID-01 -> MID-02 -> MID-03 -> MID-05 -> RS-02 -> SEC-02 -> I18N-03` の優先バックログ順を基準とする。

## Stream F independent pass (2026-05-06)

### Phase 1 Read同期
- `AGENTS.md` の Stream F 対象境界を再確認し、本メモの編集範囲を QA/I18N/RM の独立検証記録に限定した。
- 上流方針（`ADR-0019`, SafeMode既定ON, share/export fail-closed）との整合を再確認した。

### Phase 2 依存確認（モック契約基準）
- 依存 I/F は contract-first とし、内部実装詳細ではなく観測可能な入出力・状態遷移を判定対象に固定した。
- 先行依存（I18N→MID→RS→SEC / PUB境界）に矛盾がないかを確認し、矛盾時は Proceed せず Stop する条件を維持した。

### Phase 3 Plan / Execute / Verify / Proceed
- Plan: AC/DoD/Go-NoGo と検証コマンドの対応を再点検した。
- Execute: docs-only で判定文面を整備し、実装コード変更は行わない方針を維持した。
- Verify: 本メモ記載の証跡形式（Command/Result/Decision/Next action）で再実行可能性を確認した。
- Proceed: 依存未解決・環境制約・境界後退のいずれかがある場合は Hold/Stop を優先する。

### Phase 4 Self-Correction（最大3回）
- 自己修復上限を `3回` に固定し、4回目相当が必要な場合は Fail-safe 停止を適用する。
- 修復時は「欠落AC補完 → 判定再確認 → 証跡更新」の順で最小差分更新のみ許容する。

### Phase 5 Stopper
- 停止トリガー: 依存矛盾、SafeMode境界後退、GoNoGo未充足、または自己修復上限超過。
- 停止時は未達項目と再開前提（必要I/F・実行環境・判定根拠）を本メモへ追記して引き継ぐ。

## Stream G pass (2026-05-10)

### Phase 1: Interface Read固定
- domain/worker/export の既存I/F境界（入力契約・出力順序・型）を再確認し、今回の変更は **issue memo更新のみ** に限定する。
- 決定論優先順位を P1 とし、乱数・非安定ソート・時刻依存を新規導入しない。

### Phase 2: ADR明文化（Context/Decision/Consequences）
- Context: MID/I18N/RS/SEC 系列は既に実装済みで、現在は運用上の受入境界を明文化する段階。
- Decision: 「人間の最終判断を残す」「決定論を壊さない」「監査可能な証跡を維持する」を共通規範として固定。
- Consequences: 後続streamは同一AC/DoDを参照可能になり、衝突なく局所改善できる。

### Phase 3-6: Execute/Verify要点
- Deterministic化: 既存比較キー・ソート規約の維持を前提化（仕様追加なし）。
- 監査: manual intervention は audit log/export へ残す方針を再確認。
- i18n/worker: fallback順序・worker fail-safe（fallback/cancel）を受入境界として再固定。
- 構造メトリクス: locale非依存・再現可能出力の維持を受入条件として明記。

### Phase 7: 完了判定
- 判定: ✅ Done維持（docs整合）。
- 根拠: 決定論 / 監査性 / 後方互換 / 最小E2E観点が既存AC/DoDと矛盾しない。
- Stop条件: 依存矛盾またはAC欠落が観測された場合は3回自己修復後にFail-safe停止。

## Current-main Evidence Refresh (2026-06-07)

- Candidate: `origin/main@ec08690eb98124820dfbc946f202b081eb7a2c0d`.
- Scope: targeted rerun of the ja/en readOnly + SafeMode locked-context equivalence path. This is an evidence refresh only; it does not change locale catalogs, fallback order, SafeMode policy, readOnly behavior, public documentation, issue status, or release authority.
- Command:
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\node_modules\playwright\cli.js test e2e/i18n_locale_functional_equivalence.spec.ts --reporter=line` -> pass, 1 test.
- Evidence detail:
  - Opened `?locale=ja&readOnly=1` and `?locale=en&readOnly=1` in the same browser test.
  - Confirmed the layout suggestion action remains disabled in read-only mode for both locales.
  - Opened Share & Reproduce and confirmed the SafeMode locked redaction-context message is visible in each locale.
- Decision impact: Done status remains valid. No ADR is required because this refresh does not change i18n authority, SafeMode/share policy, or readOnly semantics.

## Current-main Evidence Refresh (2026-06-07): locale query fallback

- Candidate: `origin/main@14b2d9d44cbae54aee10ab9f13e3396a3f153035`.
- Scope: targeted rerun of locale query shell-label switching, invalid-locale fallback, and English document replace flow. This is an evidence refresh only; it does not change locale catalogs, fallback order, SafeMode policy, readOnly behavior, public documentation, issue status, or release authority.
- Command:
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\node_modules\playwright\cli.js test e2e/i18n_locale_query_equivalence.spec.ts --reporter=line` -> pass, 3 tests.
- Evidence detail:
  - Confirmed `?locale=en` shows English shell labels for Share & Reproduce and View.
  - Confirmed invalid `?locale=zz` falls back to Japanese shell labels and does not show the English shell buttons.
  - Confirmed `?locale=en` preserves the browser document-load and replace-confirmation flow through to visible card rendering.
- Decision impact: Done status remains valid. No ADR is required because this refresh does not change i18n authority, locale fallback policy, import behavior, or share/export policy.
