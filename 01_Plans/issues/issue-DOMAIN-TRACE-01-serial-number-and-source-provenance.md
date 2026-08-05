# Issue Draft: DOMAIN-TRACE-01 通し番号と原データ遡及（Card.meta 系の追加的導入）

- Type: Feature request
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Claude Code
- Scope: `02_Architecture/schemas.md`, `03_Implement/frontend/src/domain/types.ts`, `03_Implement/frontend/src/domain/validate.ts`, `03_Implement/frontend/src/ui/SidePanel.tsx`, `03_Implement/backend/`
- Related Backlog: `DOMAIN-TRACE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D3 改訂 2026-07-03）, `02_Architecture/schemas.md`（§5 future item: `Card.meta`）, `01_Plans/issues/issue-CARD-META-UI-01-card-provenance-metadata-ui-boundary.md`, `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: DOMAIN-TRACE-01
- RequirementStatement: 質的研究の実践（原データへの遡及・監査可能性）を支えるため、カードに任意の通し番号と出典参照（原発話・行番号・URL 等の自由記述）を追加的フィールドとして保持し、選択時に参照できるようにする。
- PriorityClass（Must / Should / Could）: Could
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=カードを選択 / 操作=通し番号と出典を入力→保存→再読込→旧形式往復 / 期待結果=値が保持され、選択コンテキストに「#番号」「原データ: 出典」が表示される。未設定カードは従来どおり。既定ではカード面（キャンバス）に番号バッジを常時表示しない / 除外=出典の自動取得・リンク先の取得/埋め込み、`Card.sources`（統合元 id）の意味変更、採番の自動連番強制。
- GoNoGoGate（Required / Optional / N/A）: Required（スキーマ契約に触れるため schemas.md 同期と後方互換確認を完了条件とする）
- SecurityGateImpact: share-export（出典は内部情報を含み得るため、SafeMode/共有前チェックでの扱いを明示する）
- VerificationLevel: integration
- DecisionStatus（Fixed / Pending）: Fixed（ADR-0048 D3 改訂。カード面常時表示のみ実装時の CB-1 自己申告で最終判断）
- DecisionQueueRef: `ADR-0048`

## 1) 課題 / Problem statement

- グラウンデッド・セオリー等の実務では「カード→原データ（発話・観察記録）への遡及」が監査可能性の要件だが、kj-atlas に出典参照の置き場が無い。
- 既存 `Card.sources` は**統合元カード id** の意味で使用中（canonical 化）であり、外部出典に流用すると意味変更＝契約違反になる。専用の追加フィールドが必要。

## 2) 背景 / Context

- ADR-0048 D3 改訂で条件付き採択: `Card.meta` 系の新フィールド（schemas.md §5 予約枠）／表示は選択時のみ／番号バッジのカード面常時表示は既定 OFF を基本とし CB-1 自己申告で最終判断。
- プロトタイプで選択コンテキストの「#番号・原データ」表示とカード面バッジの両案が検証済み（採否は本Issueで確定）。
- `CARD-META-UI-01` は起票者・作成者・最終更新者などの個人/組織識別を含み得るprovenance/accountabilityメタのUI境界を扱う。本Issueはそのうち `seq` / `source`（通し番号と原データ遡及）に限った具体実装候補であり、起票者・所有者・レビュー者の表示/編集/共有可否を確定しない。

## 3) 判断基準による優先度評価

- 価値（ADR-0001 P-03、判断軸4）: 差分・監査・レビューに載る形での遡及可能性を強化。原文の声（一枚一志）への回帰路を作る。
- 安全: 出典は共有時に露出し得るため、共有前チェックでの表示（含める/除く）を明示する。
- 規模拡大: research 用途での採用障壁を下げる。未使用文書への影響ゼロ。
- 後方互換: 追加的（optional）で version: 2 維持。`sources` の意味は不変。

## 3.2 非目標 / Non-goals

- 出典 URL の自動取得・プレビュー・埋め込み。自動採番の強制（任意入力・一括採番はあっても上書きは人間操作）。`Card.sources` の再定義。research モード（Pending 継続）の導入。

## 4) 提案する解決策 / Proposed solution

- スキーマ: `Card.meta?: { seq?: number; source?: string }`（schemas.md 更新時に形を確定。§5 予約の `Card.meta（出自情報、タグ、引用元など）` に整合）。`createdBy` / `reportedBy` / `updatedBy` / `ownerRef` などの主体メタは `CARD-META-UI-01` のDecision Queue対象とし、本Issueでは追加しない。
- UI: 選択コンテキストに「#番号」「原データ」欄（未設定時は非表示/折りたたみ）。カード面の番号バッジは既定 OFF とし、View パネルのトグルで表示（research 的用途向け）。
- 共有: 共有前チェックに「出典参照を含める」可否を明示（既定は既存の SafeMode 方針に整合させる）。
- 取り込み/書き出し: 寛容/厳格両モードで保全。i18n（ja/en）。

## 5) 受け入れ条件 / Acceptance criteria

- [x] AC-1: schemas.md が実装前に更新され（`Card.meta` の形確定・L2.5 登録）、`sources` との役割分担が明文化される。
- [x] AC-2: 入力→保存→再読込→旧形式往復のラウンドトリップで欠落しないことが integration で固定される。
- [x] AC-3: 既定でカード面に番号バッジが表示されず、View トグルで表示できる（CB-1 自己申告を記録）。
- [x] AC-4: 共有前チェックで出典参照の扱いが明示され、SafeMode 既定の安全性が弱まらない。
- [x] AC-5: 未設定カードの表示・操作が従来どおり。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 schemas.md 更新（Card.meta 形・sources 役割分担・L2.5。主体メタは `CARD-META-UI-01` へ分離）。
- [x] T2 types.ts/validate.ts＋backend 対応。
- [x] T3 選択コンテキスト UI＋View トグル＋i18n。
- [x] T4 共有前チェックへの反映。
- [x] T5 integration（往復・寛容/厳格・共有非回帰）。

## 7) 検証計画 / Validation plan

- `cd 03_Implement/frontend && npm run typecheck && npm test`
- `cd 03_Implement/backend && ruff check src tests && pytest`
- 共有前チェック（SharePanel）の e2e スモーク（出典の含める/除く表示）。

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（選択時のみ表示。番号バッジは既定 OFF・View トグル） / 保留操作の距離=不変 / 取り消し導線=あり（欄の編集は ⌘Z・トグルで非表示化）

## Traceability

- Related: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D3 改訂）
- Related: `02_Architecture/schemas.md`（§5 `Card.meta` 予約・`Card.sources` 現行意味）
- Related: `01_Plans/issues/issue-CARD-META-UI-01-card-provenance-metadata-ui-boundary.md`（主体メタ/起票者UI境界）
- Related: `02_Architecture/design/kj-atlas 拡張提案.dc.html`（仕様精査 C）, `02_Architecture/design/kj-atlas プロトタイプ.dc.html`
- Derived-from: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`

## 実装設計の到着（2026-07-04）

- Claude Design Round 4 プロトタイプに「通し番号をカードに表示」トグル（既定OFF）と選択時のみの原データ表示が実装され、本Issueの AC-3 の参照実装となった。共有前チェックの出典参照トグル（既定OFF＋警告1行）の設計も同成果 §領域5 に確定。

## 完了記録 2026-07-08（Claude Code）

### T1 要件の再定義（schemas.md §15 に正本化）

1. **`Card.meta` の形**: `{ seq?: number; source?: string }`（両方 optional・L2.5）。seq は任意の通し番号で自動連番を強制しない。source は文書外部の原データ参照（発話・行番号・URL 等の自由記述）。
2. **語彙境界（§15.2）**: `Card.sources`（統合元カード id・canonical 化の系譜）と `Card.meta.source`（外部原データ参照）は別語彙であり相互不変。起票者・作成者等の**主体メタは追加しない**（`CARD-META-UI-01` の Decision Queue 対象。Owner: Security Officer / UX Lead — 本Issueでは非主体の seq/source 境界のみ確定）。
3. **未知 meta キーは fail-closed（§15.3）**: 寛容/厳格の両モードで seq/source 以外を**破棄**。DOMAIN-KJ-01 §3.3.2 の未知エッジ種別「保全」とは**意図的に逆**の規則 — CARD-META-UI-01 確定前に import 経由で主体/出自メタが密輸される経路を閉じる。
4. **共有境界（§15.4）**: 共有向け書き出し（バンドル document.json）は Card.meta を**既定で除外**。「出典参照を含める」トグル（既定OFF＋警告1行）で明示オプトイン。SafeMode とは**独立軸**（トグルは safeMode に関係なく表示）。バックアップ用 document.json 読み書き・PUT は除外対象外（meta 保持）。

### 実装

- **契約先行**: schemas.md §15（新設）＋ §5 項目5更新、data_model_operations_overview.md §4.1 行追加。
- **往復（4経路すべて）**: ①寛容 `validate.ts parseCardMeta`（有限数 seq・非空文字列 source のみ受理、無効値/未知キーは黙って破棄、全滅時は meta 自体を省略）②厳格 `validate_doc.ts`（meta ホワイトリスト＋`hasOnlyKeys(["seq","source"])`＋型検査）③CE3 パッチ経路 `patch_apply.ts parseCard`（`value as Card` による未知キー密輸を防ぐ明示再構築）④バックエンド `models.py CardMeta`（V2のみ。Pydantic 既定 `extra="ignore"` が §15.3 を実装。**CardMeta 追加前は PUT で meta が黙って全損していた**—T2で事前修正）。
- **UI（選択時のみ・ADR-0048 D3改訂準拠）**: SidePanel 選択コンテキストに `#番号`・`原データ:` チップ（未設定時は非表示=AC-5）、カードインスペクタに遡及情報エディタ（空にすると欄削除・カード未設定時はバイト同一維持）。編集は `applyDocumentChange` 1ステップ（⌘Z 可逆）。
- **カード面バッジ**: `CardView` メタ行に中立スレート色の `#n` テキスト（ピル無し=視覚言語チャネルを消費しない）。View パネル「通し番号をカードに表示」トグルで表示、**既定OFF**。
- **共有除外**: `bundle_export.ts resolveShareDocument()` を両ビルド関数（同期/worker）の入口で適用 — document.json 2書き出し点と integrity.json ハッシュ計算の**すべてに先行**。SharePanel にトグル＋警告1行＋共有前チェック行（含める時は強調表示）。作業中ドキュメントは非破壊（共有コピーのみ剥離）。view.json は cards を含まないため対象外を確認。
- i18n 両ロケール 17 キー追加。

### 検証

- typecheck 0 / vitest **944 passed**（185 files。バンドル剥離3件・meta往復4件・回帰アンカー1件を追加）
- backend: ruff クリーン / pytest **284 passed**（PUT+GET で seq/source 保持・未知キー createdBy 破棄・未設定カード meta 無しの sqlite/postgres ペア追加）
- e2e 新規 `card_trace_meta.spec.ts` **4/4 passed**（エディタ→サマリ表示→⌘Z 2段階復帰／バッジ既定OFF→トグルON／PUT ペイロード実測での往復保全／共有前チェック既定除外→オプトイン警告）
- 関連 e2e 非回帰: card_meta_row / domain_expression_keyboard_access / first_value_share_preflight / review_pack_trace_export / edge_type_vocabulary / esc_staged_closing すべて passed。header_toolbar_layout の4件失敗は**クリーンな main で再現する既存問題**（ショートカットヘルプボタンのメニューバー移行と spec の不整合）であり本Issueとは無関係 — 別タスク起票済み。

### CB-1 自己申告（ADR-0043 / ADR-0048 D3改訂）

複雑性予算: 初期表示への純増=**なし**（選択時のみ表示。カード面バッジは既定OFF・View トグル。共有トグルも既定OFF） / 保留操作の距離=不変 / 取り消し導線=あり（meta 編集は ⌘Z 1ステップ・バッジはトグルで非表示化・共有トグルは再チェックで解除）。番号バッジのカード面常時表示は**不採択**（既定OFF を維持）— 表示は明示オプトインのみ、という D3改訂の基本線どおりで CB-1 逸脱なし。
