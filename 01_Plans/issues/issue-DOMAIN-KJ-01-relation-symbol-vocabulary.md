# Issue Draft: DOMAIN-KJ-01 関係記号の語彙拡張（関連/因果/相互/対立/同値・契約先行）

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `02_Architecture/schemas.md`, `03_Implement/frontend/src/domain/types.ts`, `03_Implement/frontend/src/domain/validate.ts`, `03_Implement/frontend/src/canvas/EdgeLayer.tsx`, `03_Implement/backend/`
- Related Backlog: `DOMAIN-KJ-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D3・前提条件3点）, `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`（追加的拡張の系譜）, `02_Architecture/schemas.md`（§5 契約先行）
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: DOMAIN-KJ-01
- RequirementStatement: KJ法原典の関係記号に対応する関係種別（関連=無方向既定/因果=有向/相互/対立/同値）を、契約文書先行・追加的・ラウンドトリップ保全の条件下で EdgeType へ拡張し、キャンバス上で種別を付与・変更・視認できるようにする。
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=2枚のカード間に関係線がある / 操作=右クリック等で種別を「因果」へ変更→保存→再読込→旧仕様相当の取り込み経路を通す / 期待結果=種別と向きが保持され、未知種別を破棄せず「関連（不明）」として保全する。EdgeLayer で種別が視覚的に区別できる / 除外=関係線の自動推定（AI）、negate/contradicts の廃止、破壊的スキーマ変更（version: 3）。
- GoNoGoGate（Required / Optional / N/A）: Required（スキーマ契約に触れるため、schemas.md 同期と後方互換確認を完了条件とする）
- SecurityGateImpact: import-sanitize（取り込み時の未知種別の扱いを変更するため、寛容/厳格の両検証を通す）
- VerificationLevel: integration
- DecisionStatus（Fixed / Pending）: Fixed（採択は ADR-0048 D3。実装開始は前提条件3点の充足後）
- DecisionQueueRef: `ADR-0048`

## 1) 課題 / Problem statement

- 現行 EdgeType は `related`/`negate` の2値（`types.ts:51-69`）で方向性を持たず、KJ法の A型図解に必要な関係語彙（因果→・相互⇄・対立・同値）を表現できない。
- `validate.ts:129-136` は取り込み時に未知のエッジ種別を**破棄**するため、素朴な enum 追加は旧クライアント経由のラウンドトリップでデータ損失を起こす（実質 breaking）。
- 「対立」は既存の `negate`（Edge）・`contradicts`（EvidenceLink）と、「同値」は canonical 化（`canonicalId`/`sources`）と意味が重なる。境界を定義しないと重複語彙が生まれる。

## 2) 背景 / Context

- ADR-0048 D3 が採択済み。実装は次の**前提条件3点**の充足後に限る:
  1. `schemas.md` の契約更新を実装に先行（§5 方針。Narrative 型など既存のドキュメント遅延も同時に同期）。
  2. `validate.ts` を「未知種別の保全（例: 種別未知として保持し表示は関連扱い）」へ変更し、寛容/厳格両モードの取り込みテストで確認。
  3. 語彙境界の明文化: 対立 vs negate/contradicts（Edge の対立=構造上の関係、EvidenceLink の contradicts=根拠の反証。negate は対立へ移行 or 別名維持を決める）、同値 vs canonical 化（同値=関係の記述、canonical=統合の実行）。
- 島↔島・島↔カードの端点（`fromKind`/`toKind`）は実装済みで、種別拡張は端点モデルに乗る。

## 3) 判断基準による優先度評価

- 価値（ADR-0001 P-01/P-04）: 「関連（無方向）」を既定とし種別確定を強制しない設計は、早すぎる収束を防ぐ核価値と一致。島間の関係づけは KJ法の「混沌→秩序」の要。
- 安全: 取り込み経路の変更を伴うため import-sanitize の回帰を必須とする。
- 規模拡大: RelationSummary（`relationType`）・集約エッジ・narrative_export への波及を Task に含め、部分実装で語彙が割れないようにする。
- 後方互換: 追加的（optional/enum 拡張）で version: 2 を維持。保全化により旧データ・旧クライアントとの往復でも損失なし。

## 3.2 非目標 / Non-goals

- AI による関係種別の自動推定・自動付与。EvidenceLink 機構の統合・廃止。version: 3 への破壊的変更。関係線の自動迂回描画（UX-SCALE-01 の領分）。

## 4) 提案する解決策 / Proposed solution

- スキーマ: `EdgeType = "related" | "negate" | "causal" | "mutual" | "opposition" | "equivalence"`（案。negate の扱いは境界定義の結論に従う）＋有向種別のための向き規約（fromId→toId を意味方向とする）。すべて optional/追加的。
- validate: 未知種別は `type: "related"` へ正規化しつつ元値を保全するフィールド（または未知許容）で往復損失をなくす。
- 描画（EdgeLayer）: 種別を線形＋終端記号で区別（因果=矢印、相互=両矢印、対立=負記号/破線、同値==記号）。色は既存トークンの意味再利用（ADR-0048 D1）。
- 操作: 関係線の右クリック/選択メニューに種別を独立項目として提示（一手で到達）。ダブルクリック循環は補助。
- 波及同期: RelationSummary.relationType・edge_aggregate・narrative_export の種別対応、i18n、`data_model_operations_overview.md`。

## 5) 受け入れ条件 / Acceptance criteria

- [ ] AC-1: schemas.md（Edge/Narrative 含む型ブロック）が実装前に更新され、types.ts との乖離が解消されている。
- [ ] AC-2: 5種別（＋negate 方針）の作成・変更・保存・再読込のラウンドトリップが integration で固定される。
- [ ] AC-3: 未知種別を含む文書の取り込みで、エッジが破棄されず保全されることが寛容/厳格両モードで固定される。
- [ ] AC-4: EdgeLayer で種別が視覚的に区別され、既定の新規線は「関連（無方向）」である。
- [ ] AC-5: 語彙境界（negate/contradicts/canonical との役割分担）が本メモまたは schemas.md に明文化されている。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 語彙境界の定義（negate 移行方針の決定を含む）→ schemas.md 更新。
- [ ] T2 types.ts/validate.ts（保全化）＋ backend スキーマ対応。
- [ ] T3 EdgeLayer 種別描画＋種別変更メニュー。
- [ ] T4 RelationSummary/集約/narrative_export/i18n の同期。
- [ ] T5 integration（ラウンドトリップ・保全・寛容/厳格）＋回帰。

## 7) 検証計画 / Validation plan

- `cd 03_Implement/frontend && npm run typecheck && npm test`（import/export・validate 系を含む）
- `cd 03_Implement/backend && ruff check src tests && pytest`
- 旧形式フィクスチャ（related/negate のみ）と新種別入り文書の相互取り込みテスト。

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（種別UIは関係線の選択/右クリック時のみ） / 保留操作の距離=不変（既定「関連」は種別確定を強制しない＝保留寄りの既定） / 取り消し導線=あり（種別変更は ⌘Z で可逆）

## Traceability

- Related: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`
- Related: `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`, `01_Plans/issues/issue-DOMAIN-EXPR-04-evidence-claim-contradiction-review.md`（contradictionState との整合）
- Related: `02_Architecture/design/kj-atlas 拡張提案.dc.html`（図V-2・リサーチ反映）
- Derived-from: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`
