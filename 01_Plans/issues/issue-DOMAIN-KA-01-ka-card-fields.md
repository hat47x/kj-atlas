# Issue Draft: DOMAIN-KA-01 KAカード種別（出来事/心の声/価値）の追加的導入

- Type: Feature request
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Claude Code
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

- [x] AC-1: schemas.md が実装前に更新され、L2.5 として支援レベル表に登録される。
- [x] AC-2: 入力→保存→再読込→旧形式往復のラウンドトリップで欠落しないことが integration で固定される。
- [x] AC-3: 未入力カードの表示・操作が完全に従来どおり（KA欄の強制なし）。
- [x] AC-4: カード面（キャンバス）の常時表示要素が増えない（初期表示アンカー非回帰）。
- [x] AC-5: claimType・critique の既存動作が非回帰。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 schemas.md 更新（フィールド形の確定・L2.5 登録）。
- [x] T2 types.ts/validate.ts＋backend 対応。
- [x] T3 SidePanel の3欄 UI＋i18n。
- [x] T4 export（レビューパック/narrative）の任意セクション対応。
- [x] T5 integration（往復・寛容/厳格・非回帰）。

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

## 完了記録 2026-07-09（Claude Code）

DOMAIN-TRACE-01（§15、同一 ADR-0048 D3改訂バッチ）に続く実装。

### T1 要件の再定義（schemas.md §17 に正本化）

- **形状の決定**: `Card.ka?: { voice?: string; value?: string }`（issue本文が両論併記していたフラット `kaVoice`/`kaValue` ではなく、ネストしたオブジェクト形式を採用）。`Card.meta`（§15.1）と同じ「関連する複数の optional フィールドを1つの入れ子オブジェクトへ束ねる」規約を踏襲し、Card ルート名前空間の肥大化を避けた。
- **`Card.text` は不変**: 出来事の正本として維持。`voice`/`value` は本文に併記しない別フィールド（AC-3 と非目標が要求する分離を型レベルで保証）。
- **成果物境界**: 「本文に併記しない・任意セクション」の解釈を確定 — narrative 本文へのインライン挿入ではなく、`outline.md` に追加する独立セクション（`## KA Fields`）とし、既定 OFF のオプトインとした。
- **SafeMode露出判定**: 新しい判定基準を作らず、既存の `card.text` チャネル（`SafeModePolicy.canExposeText("card.text", ...)`）を再利用 — KA欄は本文と同等以上に機微な言語化途中データであるため。

### 実装

- **契約先行**: schemas.md §17（新設）＋ data_model_operations_overview.md §4.1 行追加。
- **往復（3経路）**: ①寛容 `validate.ts parseCardKa`（`parseCardMeta` と同一パターン：既知キーのみ受理、両方欠落/空文字なら `ka` 自体省略）②厳格 `validate_doc.ts`（`hasOnlyKeys(["voice","value"])`）③CE3パッチ経路 `patch_apply.ts parseCard`（`meta`/`ka` 両方が独立に安全にサニタイズされるようリファクタ）④バックエンド `models.py CardKa`（`CardV2` のみ、`extra="ignore"` 既定で未知キー破棄）。
- **UI（選択コンテキストのみ・カード面表示なし）**: SidePanel の遡及情報エディタ（`card-trace-editor`）の直後に KA エディタボックス（`card-ka-editor`）を追加。「心の声」「価値」の2つの textarea、KA ガードレール文言（嘘を書かない・話を盛らない・妄想しすぎない）をヒントとして表示。空にすると欄削除（`Card.meta` と同じ規約）。編集は `applyDocumentChange` 1操作=1履歴ステップ。
- **成果物**: `reading_outline.ts` に `formatKaFields()` と `appendKaFields` オプション（既定 OFF）を追加。設定時のみ、KA欄が設定されているカードを列挙する独立セクションを本文末尾に追加（本文中のカードエントリには一切混在しない）。SharePanel/App.tsx に対応するトグル「KA欄（心の声・価値）を追加」を配線。
- **CardView.tsx は変更なし**: KA欄はカード面（キャンバス）に一切表示しない（AC-4）。

### 検証

- typecheck 0 / vitest **961 passed**（185 files。Card.ka往復5件・reading_outline export 3件・回帰アンカー1件を追加）
- backend: ruff クリーン / pytest **287 passed**（PUT+GET で voice/value 保持・未知キー authorRating 破棄・text不変・未設定カード ka 無しの sqlite/postgres ペア追加）
- e2e 新規 `card_ka_fields.spec.ts` **2/2 passed**（エディタ入力→2段階 ⌘Z 復帰／PUTペイロード実測での text 不変・ka 往復・カード面への非表示確認）
- 関連 e2e 非回帰（card_trace_meta / contradiction_signal_decision / domain_expression_keyboard_access / complexity_budget_foregrounding / edge_type_vocabulary）17件すべて passed。
