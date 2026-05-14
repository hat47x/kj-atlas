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

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
