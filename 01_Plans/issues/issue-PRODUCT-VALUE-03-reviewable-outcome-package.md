# Issue Draft: PRODUCT-VALUE-03 レビュー可能な成果物パッケージ

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex (Product Value contract steward; accountable owner remains Productization Program Owner)
- Scope: `03_Implement/frontend/src/`, `03_Implement/frontend/e2e/`, `02_Architecture/value_traceability.md`, `04_Documentation/narratives.md`, `04_Documentation/data_handling.md`
- Related Backlog: `PRODUCT-VALUE-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0032-product-value-realization-model.md`, `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `02_Architecture/review_attribution.md`, `02_Architecture/value_traceability.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: PRODUCT-VALUE-03
- RequirementStatement: ナラティブ、レビューパック、共有前確認を、確定点、保留点、未レビュー情報、根拠への戻り方を含むレビュー可能な成果物として束ねる。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=カード、島、関係、保留点を含む文書がある / 操作=ナラティブまたはレビューパックを作成し、共有前確認を行う / 期待結果=読者が確定点、未確定点、根拠、レビュー状態を理解できる / 除外=自動公開、組織固有の承認ワークフロー、電子署名必須化。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / public-exposure）: SafeMode / share-export / public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Pending（`ADR-0032` はAccepted済み。Open前のreviewable package fixture、共有前確認、trace-back証跡が未固定）
- DecisionQueueRef（未確定時の参照先）: `PRODUCT-QA-01` value gate evidence packet / `MVP-EXIT-01`

## 1) 課題 / Problem statement

- 現行の共有前確認は安全性を重視しているが、成果物が読者にとって「何を判断すればよいか」まで十分に設計されていない。
- ナラティブ文書はAI出力の扱いを説明しているが、画面上の成果物パッケージとして、確定点、保留点、根拠、未レビュー情報をどう束ねるかが未固定である。
- 共有物が読みやすいだけで、根拠や保留点へ戻れない場合、kj-atlasの価値であるレビュー可能性と可逆性が失われる。

## 2) 背景 / Context

- `ADR-0032` は V4 として、共有と学習を価値ループへ位置づけた。
- `review_attribution.md` はレビュー情報を安全に扱う方針を定義している。
- `PRODUCT-UX-03` は共有前確認のUIフローを扱うが、成果物の価値単位は別途整理が必要である。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 共有物が保留点や未レビュー情報を示せないと、単一正解化と早すぎる収束を招く。
- 安全（THREAT_MODEL / SafeMode）: 共有時に未レビュー本文や機微情報が混ざらない境界が必須である。
- 企業・行政要件（enterprise_architecture）: 判断資料として共有するには、根拠、レビュー状態、未解決点の説明可能性が必要である。
- 後方互換（schemas）: 既存のreview pack/export形式を壊さず、必要ならパッケージメタデータを拡張する。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - ナラティブ生成/確認、レビューパック、共有前確認、export診断、公開文書。
- 変更の最小単位:
  - 成果物パッケージの最小構成を「要約」「確定点」「保留点」「未レビュー情報」「根拠への戻り方」「SafeMode結果」として定義する。
  - 共有前確認で、この構成の有無と安全状態を確認できるようにする。
- 非目標:
  - 自動公開。
  - 組織固有の承認ワークフロー。
  - 電子署名や改ざん不能監査を既定必須にすること。

## 5) 受入条件 / Acceptance criteria

- [ ] ナラティブまたはレビューパックに、確定点、保留点、未レビュー情報、根拠への戻り方が含まれる。
- [ ] 共有前確認で、未レビュー情報と保留点を含めるか除外するかを安全側に確認できる。
- [ ] SafeMode ON時の成果物は、未レビュー本文や機微情報を既定で抑制する。
- [ ] 読者が元カード、島、関係、レビュー状態へ戻るための参照が残る。
- [ ] `narratives.md` と `data_handling.md` が、成果物パッケージの意味と確認観点を説明する。
- [ ] E2Eまたは手動受入で、共有前確認から成果物生成までの流れを検証できる。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 成果物パッケージの最小構成と非目標を定義する。
- [ ] T2 ナラティブ、レビューパック、共有前確認の現行出力を棚卸しする。
- [ ] T3 SafeMode ON/OFF時の含める情報、除外する情報、確認文言を整理する。
- [ ] T4 成果物から元データへ戻る参照方式を確認する。
- [ ] T5 E2Eと公開文書を同期する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "ナラティブ|レビューパック|保留点|未レビュー|根拠|SafeMode" 02_Architecture 03_Implement/frontend 04_Documentation`
  - `cd 03_Implement/frontend && node .\\node_modules\\vitest\\vitest.mjs run`
  - `cd 03_Implement/frontend && node .\\node_modules\\playwright\\cli.js test --reporter=line`
- 期待結果:
  - 成果物が、読みやすさだけでなくレビュー可能性、安全性、根拠参照を持つ。
- 未実施時の理由・代替検証:
  - 実装前は、出力例、スクリーンショット、文書上の受入確認で代替する。

## 8) 代替案 / Alternatives considered

- 代替案A: ナラティブを単なる本文出力として扱う。根拠や保留点が消えやすいため採用しない。
- 代替案B: 共有を完全に禁止する。プロダクト価値であるレビューと共同判断に接続しないため採用しない。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 成果物が情報過多になり、読者が結論と保留点を読み分けにくくなる。
- 影響範囲: share/export、narratives、review pack、公開文書。
- ロールバック手順: 成果物パッケージを詳細モードに戻し、既存の安全確認フローだけを維持する。

## 10) Additional context

- ADR化が必要になる条件: review pack形式、公開配布形式、署名/検証方式を新しい互換契約として固定する場合。


## 11) 価値実現シリアル（Hypothesis → Action → Evidence → Decision）

- 価値仮説: 成果物に「確定/保留/未レビュー/根拠導線」が揃うと、共同判断時の説明可能性と可逆性が向上する。
- 行動:
  1. ナラティブまたはレビューパックを生成する。
  2. 共有前確認で含有情報と除外情報を確認する。
  3. 生成物から元カード/島/関係/レビュー状態へ戻る。
  4. SafeMode ON条件で未レビュー本文と機微情報抑制を確認する。
- 証拠:
  - E1: 成果物内に最小構成要素が揃っている確認結果。
  - E2: 共有前確認の判定記録（含める/除外）。
  - E3: 参照導線（trace/back-link）確認記録。
  - E4: SafeMode ON時の抑制確認結果。
- 判定（Go/No-Go）:
  - Go: E1〜E4取得、かつ最小構成要素充足率100%。
  - No-Go: 要素欠落、参照不能、またはSafeMode抑制不成立。

## 12) KPI定義（定義可能・再測定可能・比較可能）

- KPI-01 `reviewable_package_completeness`
  - 定義: 最小構成6要素（要約/確定/保留/未レビュー/根拠導線/SafeMode結果）の充足率。
  - 再測定: 同一テンプレートで成果物を検査する。
  - 比較: 版間の充足率を比較する。
- KPI-02 `traceback_reachability`
  - 定義: 成果物から元データ参照に到達できる項目割合。
  - 再測定: 固定サンプルで導線検証する。
  - 比較: 導線欠落件数を版間で比較する。
- KPI-03 `safe_share_compliance`
  - 定義: SafeMode ON時に抑制対象が適切に除外された検証項目の合格率。
  - 再測定: 固定チェックリストで確認する。
  - 比較: 回帰有無を版間で比較する。


---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。


## Stream I 要件契約固定パック（2026-05-18）

### Phase 1: Read同期サマリ
- 重複論点: 画面導線の分かりやすさ、SafeMode境界、検証証跡要件。
- 曖昧論点: Open化の判定条件と、依存関係が契約依存か実装依存かの境界。
- 欠落補完: 価値→要件→受入→測定の追跡行と、Draft→Open判定を明文化。

### Phase 2-3: ADR要素 + 要件契約
| Context | Decision | Consequences |
| --- | --- | --- |
| 上流価値定義（ADR-0001/0031/0032）を実装入口へ接続する必要がある。 | AC/DoDを機械検証可能な粒度で固定し、未確定はDecision Queueへ隔離する。 | 下流実装Streamは要件の再発明をせず、検証可能なIssue単位で着手できる。 |

### 価値→要件→受入→測定 対応表（最小）
| 価値仮説 | 要件（Requirement） | 受入条件（AC） | 測定（Evidence/KPI） |
| --- | --- | --- | --- |
| 利用者が安全に判断を共有できる。 | SafeMode境界を保持し、共有前確認を必須化する。 | SafeMode/公開範囲/未レビュー状態を実行前に提示できる。 | docs-check + E2E記録 + 文言一致確認。 |
| 要件から実装へ手戻りなく移行できる。 | AC/DoDをOpen前に固定し、未確定はPending化する。 | Draft→Open条件を満たしたIssueのみ実装に着手する。 | checklist充足率、No-Go件数、Pending解消件数。 |

### Phase 4: Draft→Open 条件（要件側ゲート）
- [ ] `DecisionStatus=Fixed` の要求のみでACが評価可能（PendingはDecision Queueへ退避済み）。
- [ ] 依存が `契約依存`（schema/api/policy/ops）と `実装依存`（UI/Backend/E2E）に分離されている。
- [ ] Validation plan のコマンドがこのIssue本文だけで再実行可能。

### Phase 5-6: Verify / Proceed 引き継ぎ条件
- Verify合格条件: 価値仮説とACの1対1追跡が可能で、非検証要件が残っていない。
- Proceed条件: 実装ストリームが「どのACをどのテストで満たすか」を追加解釈なしで決定できる。
- フェイルセーフ: 上流価値定義との矛盾・非検証要件・競合編集を検出した場合はOpen化を停止する。

## Open化判定メタ（Draft gate解除条件）

### Open化に必要な最小条件（全件必須）
- [ ] O-OPEN-01: `Owner` が `TBD` ではなく、実行責務者（個人またはロール）に確定している。
- [ ] O-OPEN-02: 依存Issue/ADRごとに `依存待ち理由` と `再開条件` が1:1で明示されている。
- [ ] O-OPEN-03: `Acceptance criteria` と `Validation plan` が `Expected verification level` と一致している。
- [ ] O-OPEN-04: docs-only範囲外の要求が本文に混入していない（本memoの範囲と矛盾しない）。

### 依存待ち理由（未解消時は Draft 維持）
| Dependency | 依存待ち理由 | 再開条件 | Owner |
|---|---|---|---|
| 上位ADR/関連Issue | 上位合意または境界仕様の最終確定待ち | 参照先に承認IDまたは確定コミットを追記 | Platform Architecture Owner / 各Issue Owner |
| QA検証経路 | `e2e`/`integration` の実行経路と証跡フォーマット未固定 | 実行経路（Compose/SQLite/例外）を1件固定し、判定ログ形式を定義 | QA Lead |
| 実行責務 | 実装担当とレビュー担当の分離未確定 | RACI（R/A）を本文に追記し通知記録を残す | PM/Triage |

### Proceed / Stop
- Proceed（Open化可）: O-OPEN-01〜04がすべて充足。
- Stop（Draft維持）: 依存先不明 / Status正規化不能 / 競合ファイル検出時は更新停止し、理由を `Additional context` に記録。



## Stream H Contract Finalization (2026-05-20)

### Scope confirmation
- Stream H dedicated; plan/ADR layer only; no implementation code edits.
- Target backlog: `MVP-EXIT-01` / `PRODUCT-VALUE-01..03` only.

### C/D/C lock (Context / Decision / Consequences)
| Context | Decision | Consequences |
| --- | --- | --- |
| PRODUCT-VALUE-03 requires Open-ready contract quality before downstream execution. | AC/DoD/KPI/audit fields are locked for docs-only verification first. | Downstream streams can execute without re-interpreting value intent. |

### KPI + audit scorecard mapping
- KPI field quality gate: definition / formula / evidence / re-measurement must all exist.
- Audit field quality gate: `reviewer`, `date`, `artifact id`, `decision`, `re-decision condition` must be explicit.

### AC / DoD final lock
- [ ] AC-F1 Hypothesis→Action→Evidence→Decision chain is explicit.
- [ ] AC-F2 Go/No-Go rule is explicit and binary-decidable.
- [ ] AC-F3 KPI definitions are re-measurable by docs-only procedure.
- [ ] DoD-F1 No cross-stream implementation dependency is required for contract validation.
- [ ] DoD-F2 Safety boundary wording (SafeMode/share-export/review attribution) is consistent with ADR-0032.

### Verify (non-dependency)
- Result: Contract validation is executable without waiting for other stream code merges.
- Reason: Inputs are issue text completeness and evidence schema only.

### Self-correction (<=3)
1. Normalized gate terms to `Go / Conditional Go / No-Go`.
2. Removed ambiguous wording that implied implementation readiness was required at this phase.
3. Added explicit audit metadata requirements for approval traceability.

### Approval-wait packet
- This section + ADR-0032 Stream H block are the approval bundle for PRODUCT-VALUE-03.

## Draft Gate Assessment 2026-05-23: Open readiness

- Assessment scope: 計画層のreadiness確認のみ。`Status: Draft` は維持し、export実装や公開文書更新はこの追記では行わない。
- Gate result: Draft維持。`DecisionStatus=Pending` と `Owner: TBD` が残り、レビュー可能な成果物パッケージの最小構成が未確定。
- Proposed RACI: R=Product Value Stream Lead（未割当）, A=Productization Program Owner, C=QA Lead / Platform Architecture Owner / Security Officer, I=Documentation Maintainer。CodexはOwner確定までissue本文と証跡パックの整備を支援する。
- O-OPEN status:
  - O-OPEN-01: Blocked. `Owner` が `TBD` のため、実行責務者をロールまたは個人で確定する必要がある。
  - O-OPEN-02: Partial. review attribution、value traceability、SafeMode境界の依存は見えているが、成果物ごとの再開条件がまだ本文上で完結していない。
  - O-OPEN-03: Partial. ACとValidation planはいずれもe2e前提だが、review pack、narrative、共有前確認、証跡back-linkの代表経路が未固定。
  - O-OPEN-04: Pass for assessment. この追記はOpen判定の整理であり、docs-only範囲外の実装要求を追加しない。
- 契約依存:
  - `ADR-0032`: 「共有できる成果物」を価値ループの判定単位としてFixedにする根拠。
  - `02_Architecture/review_attribution.md`: レビュー済み、未レビュー、AI補助の帰属表現。
  - `02_Architecture/value_traceability.md`: 成果物から価値仮説と受入証跡へ戻れること。
- 実装/証跡依存:
  - review packまたはnarrative exportに、SafeMode状態、未レビュー状態、判断保留、根拠参照が欠落しないことを確認するE2E。
  - 共有前確認の画面状態と、エクスポート結果から元の判断・証跡へ戻れるback-link検証。
- Next action:
  - 成果物パッケージの最小構成を「要約」「根拠」「未確定事項」「レビュー帰属」「SafeMode表示」に分解して、ACと対応付ける。
  - ADR-0032でDecisionStatusをFixedにできる承認IDまたは確定コミットを得るまではOpen化しない。

## Draft Gate Reassessment 2026-05-27: owner fixed, package minimum split

- Assessment scope: 計画層のDraft維持理由を、担当未確定ではなくADR-0032承認待ちと成果物パッケージ最小構成の承認待ちへ絞り込む。
- Gate result: **Draft維持**. OwnerはCodexの契約・証跡整備責務として確定したが、`DecisionStatus=Pending` と `ADR-0032` Proposed が残るためOpen化しない。
- RACI:
  - R: Codex (Product Value contract steward)
  - A: Productization Program Owner
  - C: QA Lead / Platform Architecture Owner / Security Officer
  - I: Documentation Maintainer / Frontend Lead
- O-OPEN status:
  - O-OPEN-01: Pass. OwnerはCodexに確定し、最終説明責任はProductization Program Ownerに分離した。
  - O-OPEN-02: Partial. `ADR-0032` のV4価値ループと SafeMode/share-export 境界は接続済みだが、成果物パッケージの最小構成は承認待ち。
  - O-OPEN-03: Partial. e2e前提のACは維持するが、review pack、narrative、共有前確認、back-linkの代表fixtureと保存先は未固定。
  - O-OPEN-04: Pass. 本更新は契約整理であり、export実装や公開文書変更を直接要求しない。

### Reviewable package minimum

| 最小要素 | 利用者に伝えること | 現行設計上の候補 | 判定証跡 |
| --- | --- | --- | --- |
| 要約 | 何を整理した成果物か | Narrative / Review Pack summary | export結果の本文確認 |
| 確定点 | 人間が確認済みとして扱える内容 | `human_reviewed`、review attribution | reviewState集計と表示確認 |
| 未確定事項 | 保留、違和感、根拠不足、未レビュー情報 | `unreviewed`、critique、claimType unknown、evidence gap | SafeMode ONでの共有前確認と出力抑制確認 |
| 根拠への戻り方 | 読者が判断材料へ戻れること | evidenceLinks、trace/back-link、sourceBundleHash | back-link到達確認 |
| SafeMode結果 | 何が含まれ、何が抑制されたか | SharePanel safe-mode summary / diagnostics | SharePanel test + E2E export結果 |
| 再レビュー導線 | 受け取った人が差し戻し/確認できること | Review Pack import / readOnly view | import/readOnly E2E |

- Fixed evidence route candidate:
  - 共有前確認とSafeMode copy: `src/ui/SharePanel.test.ts`
  - 代表共有操作: `e2e/realistic_user_journey_expansion.spec.ts`
  - Review Pack遅延/キャンセル: `e2e/ops_recovery_guidance.spec.ts`
  - 大きな文書のbundle diagnostics: `e2e/large_document_operability.spec.ts`
### Evidence route refinement 2026-06-02

This refinement keeps `Status: Draft`. It does not authorize export format changes, public publishing changes, or release approval. It defines the minimum evidence needed before a reviewable outcome package can be treated as a product value gate.

Reviewer questions the package must answer:

1. What conclusion or working summary is being shared?
2. Which cards, groups, or relations support it?
3. What remains unresolved, unreviewed, or contested?
4. Who or what marked the content as reviewed?
5. What did SafeMode include, mask, or exclude?
6. How can the reader return to the source cards or evidence?

Required evidence packet before Open:

| Evidence item | Required content | Gate handoff |
| --- | --- | --- |
| Package fixture | A narrative or review pack with summary, evidence references, unresolved items, and SafeMode result | `PRODUCT-QA-01` V4 |
| Pre-share confirmation | UI state showing reviewed/unreviewed content and masking result before export/share | G1 / G5 |
| Trace-back proof | Back-link or source reference from package item to card/evidence | G2 / G7 |
| Read-only review proof | Imported or shared package can be inspected without mutating source data | G2 / G5 |
| Decision record | Go/Conditional Go/No-Go and any missing package element | `MVP-EXIT-01` |

No-Go conditions for this value gate:

- The package reads as a final answer while unresolved or unreviewed items remain hidden.
- SafeMode masks data but the package does not tell the reviewer what category was masked.
- A reviewer cannot navigate from package summary back to source evidence or card context.
- The evidence requires organization-wide approval workflow or signature semantics not covered by `ADR-0032`.

- Reopen/Open condition:
  - `ADR-0032` Accepted は充足済み。以後はProductization Program Ownerが上記Reviewable package minimumの証跡パケットをOpen前提として承認する。
  - review pack、narrative、共有前確認、back-linkの代表fixtureと保存先が本文で固定される。
  - 上記完了後、StatusをOpenへ変更し、`PRODUCT-QA-01` のValue Gate V4へ戻す。

## Current status sync 2026-06-03: ADR accepted, package evidence still pending

- Current decision source:
  - `ADR-0032-product-value-realization-model.md` is `Accepted` as of 2026-05-31 and fixes V4 as the reviewable outcome loop.
  - `ADR-0040-domain-expression-first-class-strategy.md` connects unresolved/hold/evidence/contradiction work to staged domain-expression issues, including `DOMAIN-EXPR-04` for evidence/claim/contradiction review.
- Current gate result: **Draft維持**. The value model is fixed, but this issue still needs a replayable package evidence route before Open.
- Remaining blocker now:
  - a narrative or review-pack fixture with summary, evidence references, unresolved items, and SafeMode result;
  - a pre-share confirmation state showing reviewed/unreviewed content and masking result;
  - trace-back proof from package item to source card/evidence;
  - read-only review proof after import or share;
  - `PRODUCT-QA-01` and `MVP-EXIT-01` decision record linkage.
- This sync does not authorize export format changes, public publishing changes, organization approval workflow, or release approval.

## Evidence route update 2026-06-04: review-pack trace export consistency candidate

- Candidate branch: `codex/review-pack-trace-ui-20260604`
- Status impact: **Draft remains**. This update adds a replayable trace-back evidence candidate, but it does not by itself open the value gate.
- Evidence added:
  - `03_Implement/frontend/e2e/review_pack_trace_export.spec.ts` covers a user path that imports a document, selects a source card, opens Share & Reproduce, switches review-pack granularity, exports ZIP files, and verifies whether trace files are actually present.
  - `03_Implement/frontend/src/ui/SharePanel.tsx` now keeps the selected-card trace checkbox disabled and visually unchecked when overview granularity is selected, matching the exported ZIP behavior.
- Evidence packet mapping:
  - Trace-back proof: partially satisfied by checking `evidence_trace_c-target.md`, `contradiction_trace_c-target.md`, and `trace_analytics_c-target.md` in detail export.
  - Pre-share confirmation: partially satisfied by the SharePanel hint that explains selected-card trace availability and overview-mode exclusion before export.
  - Package fixture: partially satisfied by `doc_review_pack_trace_export`.
  - Read-only review proof and final decision linkage remain pending.
- Remaining blockers before Open:
  - Productization Program Owner must accept this fixture as representative of a reviewable outcome package.
  - SafeMode masking result, unresolved/unreviewed summary readability, read-only review import, and `PRODUCT-QA-01` / `MVP-EXIT-01` decision linkage remain incomplete.

## Mainline evidence intake 2026-06-04: review-pack trace controls landed

- Candidate mainline: `origin/main@d1dfa3a0c50892d8d7aa354a5e83ba760e043919`
- Status impact: **Draft remains**. The selected-card trace export behavior and representative ZIP-content proof are now on `main`, but this issue still needs product-value acceptance, read-only review proof, and SafeMode/unreviewed readability evidence before Open.
- Evidence now canonical on `main`:
  - #2314 merged `03_Implement/frontend/e2e/review_pack_trace_export.spec.ts`, covering document import, card selection, Share & Reproduce, overview/detail granularity switching, ZIP export, and trace-file presence/absence.
  - #2314 merged SharePanel behavior that disables and visually unchecks selected-card trace export in Overview mode, then re-enables it in Detail mode.
  - #2319 records the post-2318 PRODUCT-QA / MVP-EXIT mainline gate sync, keeping full shipment No-Go while acknowledging the merged review-pack evidence lane.
- Evidence packet status:

| Evidence item | Current status | Remaining Open blocker |
| --- | --- | --- |
| Package fixture | Partially satisfied by `doc_review_pack_trace_export`. | Productization Program Owner must accept the fixture as representative of a reviewable outcome package, including summary, evidence, contradiction, and unresolved context. |
| Pre-share confirmation | Partially satisfied by SharePanel hints for selected-card traces and Overview-mode exclusion. | Confirm that SafeMode masking, reviewed/unreviewed status, and recipient-facing risk are understandable before export. |
| Trace-back proof | Satisfied for the selected-card trace files in Detail export. | Confirm that this trace-file proof is sufficient for V4, or require an additional in-app backlink/read-only inspection path. |
| Read-only review proof | Not yet satisfied by this evidence lane. | Add or cite an import/read-only review path that lets a reviewer inspect the package without mutating source data. |
| Decision record | Partially satisfied by PRODUCT-QA / MVP-EXIT post-2318 gate records. | Final product-value gate decision must explicitly cite this issue after fixture, SafeMode, and read-only review acceptance. |

- Next human task queue:
  - H-PV3-1: Productization Program Owner decides whether the review-pack fixture represents the promised reviewable outcome package.
  - H-PV3-2: QA Lead confirms whether ZIP file-name checks are enough trace-back evidence, or whether a reader-facing backlink/read-only UI proof is required.
  - H-PV3-3: UX reviewer confirms that Overview/Detail trace-control behavior is understandable before export.
- No ADR is needed for this intake. ADR routing is required only if the accepted package changes the product value model, review authority, SafeMode/share policy, or review-pack contract.

## Mainline E2E rerun 2026-06-06: review-pack trace export

- Candidate mainline: `origin/main@04e578abbb0c46fb5cb4cd41a8fb37a138ee0700`.
- Status impact: **Draft remains**. This rerun proves the review-pack trace export path is executable on current `main`; it does not replace Productization Program Owner acceptance, read-only review proof, release screenshot approval, Compose startup, or final program approval.
- Environment note: Vite and Playwright were executed with bundled Node.js because this Codex host does not expose `npm` on PATH for Playwright webServer startup:
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe`
  - Vite was started directly with `node .\node_modules\vite\bin\vite.js --host 127.0.0.1 --port 4173`.
- Verification command:
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\node_modules\playwright\cli.js test e2e/review_pack_trace_export.spec.ts --reporter=line`
- Result: **pass, 1 test**.

### Evidence packet update

| Evidence item | Current status after rerun | Remaining Open blocker |
| --- | --- | --- |
| Package fixture | Reconfirmed executable for `doc_review_pack_trace_export`. | Productization Program Owner must accept the fixture as representative of a reviewable outcome package. |
| Pre-share confirmation | Reconfirmed Overview/Detail trace-control hints before export. | Confirm that SafeMode masking and reviewed/unreviewed status are understandable to a standard reviewer. |
| Trace-back proof | Reconfirmed ZIP behavior: Overview excludes selected-card trace files; Detail includes evidence, contradiction, and trace analytics files. | QA Lead must decide whether ZIP file-name proof is sufficient or whether reader-facing backlink/read-only UI proof is required. |
| Read-only review proof | Still not satisfied by this rerun. | Add or cite an import/read-only inspection path that lets a reviewer inspect the package without mutating source data. |
| Decision record | This section adds a current-main rerun record. | Final Open decision must cite H-PV3-1/H-PV3-2/H-PV3-3 outcomes. |

- No ADR is needed for this rerun. ADR routing remains limited to changes in the product value model, review authority, SafeMode/share policy, or review-pack contract.

## Fixture manifest 2026-06-17: PV03 reviewable package packet entry

- Candidate mainline: `origin/main@4fe6740678dd970a18eacab094ec4e99c53496c5`.
- Fixture source: `03_Implement/frontend/e2e/helpers/product_value_fixtures.ts`.
- Fixture builder: `buildReviewPackTraceDocument()`.
- Fixture document ID: `doc_review_pack_trace_export`.
- Representative E2E: `03_Implement/frontend/e2e/review_pack_trace_export.spec.ts`.
- Status impact: **Draft remains**. This manifest names the reusable fixture entry for the PV03 evidence packet; it does not create Productization Program Owner / QA Lead acceptance, package contract approval, or shipment approval.

### Evidence packet mapping

| Evidence item | Manifest status | Remaining Open blocker |
| --- | --- | --- |
| Package fixture | Named and stored in `product_value_fixtures.ts`; includes a reviewed target claim, reviewed support note, unreviewed contradiction, a reviewable island, and support/contradiction links. | Productization Program Owner must accept this fixture as representative of the promised reviewable outcome package. |
| Pre-share confirmation | Existing E2E verifies Overview mode excludes selected-card traces and Detail mode enables them before ZIP export. | Confirm that SafeMode masking, reviewed/unreviewed status, and recipient-facing risk are understandable before export. |
| Trace-back proof | Existing E2E verifies Detail export contains `evidence_trace_c-target.md`, `contradiction_trace_c-target.md`, and `trace_analytics_c-target.md`. | QA Lead must decide whether ZIP file-name proof is sufficient or whether a reader-facing backlink/read-only UI proof is required. |
| Read-only review proof | Not added by this manifest. | Need import/read-only inspection evidence that a reviewer can inspect the package without mutating source data. |
| Decision record | This section provides the fixture identity that Product QA and MVP-EXIT can cite later. | Final Open decision must cite H-PV3-1/H-PV3-2/H-PV3-3 outcomes and the screenshot/trace bundle location. |

- No ADR is needed for this manifest. ADR routing remains limited to changes in product value model, review authority, SafeMode/share policy, review-pack public contract, approval/signature semantics, or automatic publication behavior.

## Read-only reviewer evidence 2026-06-18

- Candidate mainline: `origin/main@d2b5f8cfab8d5ac49388f0f130dae1eeb2315049`.
- Implementation scope:
  - `03_Implement/frontend/src/App.tsx` disables the primary document-edit actions in read-only mode, including legacy import, new card, island creation, deletion, and save.
  - `03_Implement/frontend/src/ui/SidePanel.tsx` disables claim type, reviewed state, evidence-link mutation, critique note, and critique-tag editing while keeping source/evidence inspection available.
  - `03_Implement/frontend/e2e/review_pack_trace_export.spec.ts` adds a read-only reviewer scenario using `doc_review_pack_trace_export`.
  - `04_Documentation/assets/screenshots/product-value-review-pack-readonly.png` records the Japanese UI state.
- Verification result:
  - Targeted Playwright: **2 passed**, including the existing trace-export test and the new read-only reviewer test.
  - Frontend typecheck: pass.
  - UX operability regression: pass, 6 tests.

### Evidence packet update

| Evidence item | Current status after read-only work | Remaining Open blocker |
| --- | --- | --- |
| Package fixture | Reused `doc_review_pack_trace_export` with reviewed target, evidence, contradiction, and unreviewed counter-signal. | Productization Program Owner must accept the fixture as representative. |
| Pre-share confirmation | Existing trace/SafeMode screenshot evidence remains available. | Human reviewer must confirm wording and risk comprehension. |
| Trace-back proof | Existing Detail export trace-file proof remains available. | QA Lead must decide whether file-level proof is sufficient for V4 acceptance. |
| Read-only review proof | **Implemented and replayable.** A reviewer can select the target, inspect reviewed state, supporting and contradicting evidence, and open Share & Reproduce while primary and card-level edit controls are disabled. | Physical keyboard and screen-reader acceptance remain human tasks. |
| Decision record | This issue now contains implementation, E2E, and screenshot locations. | Product QA / MVP-EXIT must consume the merged evidence before Open-gate decision. |

- Status impact: **Draft remains**. The automated read-only review blocker is addressed, but Productization Program Owner / QA Lead acceptance and human accessibility/operability acceptance remain required.
- No new ADR is needed. The change enforces the existing read-only authority boundary and does not change the review-pack contract, SafeMode policy, approval semantics, or release authority.
