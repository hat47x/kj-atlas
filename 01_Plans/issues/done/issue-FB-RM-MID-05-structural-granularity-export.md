# Issue Memo: FB-RM-MID-05 structural granularity export

- Type: Feature
- Status: Done
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/frontend/src/export/`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/i18n/locales/`, `01_Plans/adr/ADR-0007-future-backlog.md`, `04_Documentation/operations.md`
- Related Backlog: `FB-RM-MID-05`
- Related ADR/Spec: `01_Plans/adr/ADR-0001-value-to-requirements.md`, `01_Plans/adr/ADR-0007-future-backlog.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Dependencies: `FB-RM-MID-05`
- Expected verification level: `unit`

## 1) 課題 / Problem statement

既存の bundle export は detail 相当の単一粒度のみで、
overview/detail を使い分けた再現可能な出力モードがなかった。
同一 Document から目的に応じて粒度を切り替える導線が不足していた。

## 2) 提案する解決策 / Proposed solution

- Bundle export に `exportGranularity`（`overview` / `detail`）を導入する。
- 出力物に `bundle_manifest.json` を追加し、選択粒度と生成時刻を記録する。
- `overview` 時は selected-card trace を抑止し、俯瞰用途の出力に寄せる。
- SharePanel に粒度選択 UI（radio）を追加し、bundle export 実行時に反映する。
- 非目標: backend API変更、SafeMode ポリシー変更、AI要約機能の新規導入。

## 3) 受入条件 / Acceptance criteria

- [x] overview/detail の粒度を選択して bundle export できる。
- [x] `bundle_manifest.json` に粒度情報が記録される。
- [x] `overview` では selected-card trace が出力されない。
- [x] 既存 detail export（outline/diagnostics/trace）との後方互換を維持する。
- [x] SafeMode 既定ON・share/export の漏えい防止に回帰がない。
- [x] unit test / typecheck が通過する。

## 4) 実装タスク分解 / Task breakdown

- [x] T1 `bundle_export.ts` に export granularity / manifest 追加。
- [x] T2 `buildExportBundleWithWorkers` へ同粒度ルールを反映。
- [x] T3 `SharePanel.tsx` に粒度選択 UI を追加。
- [x] T4 `App.tsx` で export granularity を context へ伝搬。
- [x] T5 `bundle_export.test.ts` / `SharePanel.test.ts` を更新。
- [x] T6 `ADR-0007` / `operations.md` / issue index を同期。

## 5) 検証計画 / Validation plan

- 実行コマンド:
  - `npm run test -- src/export/bundle_export.test.ts src/ui/SharePanel.test.ts`
  - `npm run typecheck`
- 期待結果:
  - granularity/manifest/trace抑止がユニットテストで固定される。
  - TS型整合が崩れていない。

## 6) Progress log

- 2026-03-01: テスト先行で `bundle_manifest.json` と overview trace抑止の期待仕様を追加。
- 2026-03-01: `exportGranularity` を bundle export context に導入し、overview/detail 分岐を実装。
- 2026-03-01: SharePanel の bundle export UI に granularity radio を追加。
- 2026-03-01: unit test + typecheck を実行し、回帰なしを確認。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。


## Stream H realignment (2026-05-04)

### Phase 1: Read同期（依存/優先度再評価）
- 系列依存の再評価: `I18N -> MID -> RS -> SEC` を基本順とし、`FB-RM-MID-05-structural-granularity-export` はこの順序に従って前後の成果物契約を参照する。
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

## Current-main Evidence Refresh (2026-06-06)

- Candidate: `origin/main@eca7c4979374a264a50820b14598be5eb760bde0`.
- Scope: targeted rerun of hierarchy level visibility and bundle export persistence for the related `FB-RM-MID-04` / `FB-RM-MID-05` structural granularity path.
- Command:
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\node_modules\playwright\cli.js test e2e/hierarchy_level_persistence.spec.ts --reporter=line` -> pass, 1 test.
- Evidence detail:
  - Imported a hierarchy document through the Chrome file picker flow.
  - Switched View -> Structure level to `overview` and confirmed only the root placard remains visible while child/member cards are hidden.
  - Switched back to `detail` and confirmed root/child member cards are visible again.
  - Exported a review bundle and confirmed `document.json` preserves `parentIslandId` and `placardCardId` for the child and root islands.
- Decision impact: Done status remains valid. No ADR is required because this refresh does not change the hierarchy data contract, export granularity policy, or UI authority.
