# Issue Draft: PRODUCT-VALUE-03 レビュー可能な成果物パッケージ

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD
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
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0032`

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
