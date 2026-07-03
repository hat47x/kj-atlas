# Issue Draft: DOMAIN-KA-01 KAカード種別（出来事/心の声/価値）の追加的導入

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `02_Architecture/schemas.md`, `03_Implement/frontend/src/domain/types.ts`, `03_Implement/frontend/src/domain/validate.ts`, `03_Implement/frontend/src/ui/SidePanel.tsx`, `03_Implement/backend/`
- Related Backlog: `DOMAIN-KA-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D3 改訂 2026-07-03）, `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`（追加的拡張の系譜）, `02_Architecture/schemas.md`（§5 契約先行・L2.5）
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: DOMAIN-KA-01
- RequirementStatement: KA法（本質的価値抽出法）のカード3分割（出来事/心の声/価値）を、`Card.text`=出来事の正本を維持したまま「心の声」「価値」の optional 追加フィールドとして導入し、選択コンテキストで閲覧・編集できるようにする。
- PriorityClass（Must / Should / Could）: Could
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=カードを選択 / 操作=選択コンテキストで「心の声」「価値」を入力→保存→再読込→旧クライアント相当の取り込み / 期待結果=両フィールドが保持され、未入力カードは従来どおり表示される（KA欄は強制されない）。旧形式文書の取り込みで欠落・破壊が起きない / 除外=価値によるグルーピングの自動化・AI 推定、カード面（キャンバス）への常時3欄表示、claimType との統合。
- GoNoGoGate（Required / Optional / N/A）: Required（スキーマ契約に触れるため schemas.md 同期と後方互換確認を完了条件とする）
- SecurityGateImpact: import-sanitize（新フィールドの取り込み経路検証）
- VerificationLevel: integration
- DecisionStatus（Fixed / Pending）: Fixed（ADR-0048 D3 改訂）
- DecisionQueueRef: `ADR-0048`

## 1) 課題 / Problem statement

- UXリサーチ実務で普及した KA法は「出来事・心の声・価値」の3観点でカードを書く。kj-atlas には該当構造が無く（Card は text 単一）、KA 流のカード作成を行うと3観点が本文に混在し、価値でのグルーピング（KA法の核心）が構造化できない。
- 壁打ち成果（拡張提案・仕様精査）で「核と整合する追加推奨」と判定され、プロトタイプで選択コンテキスト内の3欄表示が検証済み。

## 2) 背景 / Context

- ADR-0048 D3 改訂（2026-07-03）で条件付き採択: text=出来事の正本維持／心の声・価値は optional／claimType と直交／schemas.md 先行／L2.5 開始。
- KA法のガードレール（嘘を書かない・話を盛らない・妄想しすぎない）は入力ヒントとして文言に反映する（機能強制はしない）。

## 3) 判断基準による優先度評価

- 価値（ADR-0001 P-01）: 「心の声」は違和感と同様、言語化途中の一級データ。3観点の分離は原文の声の保持（一枚一志）と整合。
- 安全: 追加フィールドは共有・書き出しの既存境界（SafeMode・未レビュー既定除外）に乗る。
- 規模拡大: optional のため未使用文書に影響ゼロ。
- 後方互換: 追加的（optional）で version: 2 維持。未知フィールド許容の既存方針（schemas.md §14.3）に適合。

## 3.2 非目標 / Non-goals

- 価値マップ（価値によるグルーピング画面）の新設。AI による心の声/価値の自動抽出。カードキャンバス面への3欄常時表示（CB-1）。claimType・critique との統合や再定義。

## 4) 提案する解決策 / Proposed solution

- スキーマ: `Card.kaVoice?: string` / `Card.kaValue?: string`（または `Card.ka?: {voice?, value?}`。schemas.md 更新時に確定）。text は従来どおり正本（=出来事）。
- UI: 選択コンテキストの基本編集群に「心の声」「価値」欄（未入力時は折りたたみ/プレースホルダ、入力ヒントに KA ガードレール文言）。カード面には表示しない（メタ行は UX-VISUAL-01 の規則を維持）。
- 取り込み/書き出し: validate の寛容/厳格両モードで保全。レビューパック・narrative_export への含め方は「本文に併記しない・任意セクション」とする。
- i18n（ja/en）。

## 5) 受け入れ条件 / Acceptance criteria

- [ ] AC-1: schemas.md が実装前に更新され、L2.5 として支援レベル表に登録される。
- [ ] AC-2: 入力→保存→再読込→旧形式往復のラウンドトリップで欠落しないことが integration で固定される。
- [ ] AC-3: 未入力カードの表示・操作が完全に従来どおり（KA欄の強制なし）。
- [ ] AC-4: カード面（キャンバス）の常時表示要素が増えない（初期表示アンカー非回帰）。
- [ ] AC-5: claimType・critique の既存動作が非回帰。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 schemas.md 更新（フィールド形の確定・L2.5 登録）。
- [ ] T2 types.ts/validate.ts＋backend 対応。
- [ ] T3 SidePanel の3欄 UI＋i18n。
- [ ] T4 export（レビューパック/narrative）の任意セクション対応。
- [ ] T5 integration（往復・寛容/厳格・非回帰）。

## 7) 検証計画 / Validation plan

- `cd 03_Implement/frontend && npm run typecheck && npm test`
- `cd 03_Implement/backend && ruff check src tests && pytest`
- 旧形式フィクスチャと KA 入り文書の相互取り込みテスト。

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（選択コンテキスト内のみ・未入力時は控えめ） / 保留操作の距離=不変 / 取り消し導線=あり（欄の編集は ⌘Z・空文字で除去）

## Traceability

- Related: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D3 改訂）
- Related: `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`
- Related: `02_Architecture/design/kj-atlas 拡張提案.dc.html`（仕様精査 A）, `02_Architecture/design/kj-atlas プロトタイプ.dc.html`（選択コンテキスト3欄）
- Derived-from: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`
