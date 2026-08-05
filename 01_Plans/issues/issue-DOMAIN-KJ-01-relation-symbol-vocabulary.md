# Issue Draft: DOMAIN-KJ-01 関係記号の語彙拡張（関連/因果/相互/対立/同値・契約先行）

- Type: Feature request
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Claude Code
- Scope: `02_Architecture/schemas.md`, `03_Implement/frontend/src/domain/types.ts`, `03_Implement/frontend/src/domain/validate.ts`, `03_Implement/frontend/src/canvas/EdgeLayer.tsx`, `03_Implement/backend/`
- Related Backlog: `DOMAIN-KJ-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D3・前提条件3点）, `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`（追加的拡張の系譜）, `02_Architecture/schemas.md`（§5 契約先行）
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: DOMAIN-KJ-01
- RequirementStatement: KJ法原典の関係記号に対応する関係種別（関連=無方向既定/因果=有向/相互/対立/同値）を、契約文書先行・追加的・ラウンドトリップ保全の条件下で EdgeType へ拡張し、キャンバス上で種別を付与・変更・視認できるようにする。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=2枚のカード間に関係線がある / 操作=右クリック等で種別を「因果」へ変更→保存→再読込→旧仕様相当の取り込み経路を通す / 期待結果=種別と向きが保持され、未知種別を破棄せず「関連（不明）」として保全する。EdgeLayer で種別が視覚的に区別できる / 除外=関係線の自動推定（AI）、negate/contradicts の廃止、破壊的スキーマ変更（version: 3）。
- SecurityGateImpact: import-sanitize（取り込み時の未知種別の扱いを変更するため、寛容/厳格の両検証を通す）

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
- 波及同期: RelationSummary.relationType・edge_aggregate・narrative_export の種別対応、i18n、`02_Architecture/design/data_model_operations_overview.html`。

## 5) 受け入れ条件 / Acceptance criteria

- [x] AC-1: schemas.md（Edge/Narrative 含む型ブロック）が実装前に更新され、types.ts との乖離が解消されている（§3.3 全面改訂＋Narrative/RelationSummary/EvidenceLink.contradictionState の型ブロック同期を実装コミットに先行して実施）。
- [x] AC-2: 5種別（＋negate 方針）の作成・変更・保存・再読込のラウンドトリップが integration で固定される（`validate_roundtrip_reversibility.test.ts`・backend `test_docs_roundtrip.py`・`e2e/edge_type_vocabulary.spec.ts`）。
- [x] AC-3: 未知種別を含む文書の取り込みで、エッジが破棄されず保全されることが寛容/厳格両モードで固定される（＋バックエンドの Pydantic `Literal` による保存時 422 拒否＝第2の損失経路も同時に解消）。
- [x] AC-4: EdgeLayer で種別が視覚的に区別され（因果=境界への矢印・相互=両矢印・同値=中点「=」・対立=既存破線）、既定の新規線は「関連（無方向）」である。
- [x] AC-5: 語彙境界（negate/contradicts/canonical との役割分担）が schemas.md §3.3.2 に明文化されている。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 語彙境界の定義（negate 移行方針の決定を含む）→ schemas.md 更新。
- [x] T2 types.ts/validate.ts（保全化）＋ backend スキーマ対応。
- [x] T3 EdgeLayer 種別描画＋種別変更メニュー。
- [x] T4 RelationSummary/集約/narrative_export/i18n の同期。
- [x] T5 integration（ラウンドトリップ・保全・寛容/厳格）＋回帰。

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

## 完了記録 2026-07-08（Claude Code）

### T1 語彙境界の確定（schemas.md §3.3.2 に正本化）

1. **negate ≡ 対立**: 新しい `opposition` enum 値は追加せず、既存 `negate` を KJ法「対立」の永続値として維持（データ移行ゼロ・重複語彙ゼロ・C001 矛盾チェックの意味も不変）。UI 表示名のみ「否定」→「対立」（en: negate → opposition）。
2. **同値 vs canonical化**: 同値=記述（両カード第一級のまま・線の削除で可逆）、canonical化=統合の実行。同値線は統合を自動実行しない。
3. **未知種別の保全方式**: `type` フィールドに未知文字列を**そのまま保持**（別フィールド案は不採用—単一の真実源・完全な往復忠実性・復元ロジック不要）。表示・挙動は `resolveKnownEdgeType()` で「関連」に解決。TypeScript は `KnownEdgeType | (string & {})` の LiteralUnion。
4. **方向規約**: `causal` のみ有向（fromId=原因→toId=結果）。abstract map 書き出しでは causal のみペア正規化を行わず方向を保存。派生（集約）エッジは UX-SCALE-01 レッドラインどおり種別抑制のまま（端点正規化により矢印が誤方向を指しうるため記号は非表示）。

### 実装

- **契約先行**: schemas.md §3.3 全面改訂（§3.3.1 方向規約・§3.3.2 語彙境界）＋参照のみで未定義だった `Narrative`/`RelationSummary` 型ブロックと `EvidenceLink.contradictionState` の同期（既存ドキュメント遅延の解消）。
- **保全化（3つの損失経路すべて）**: ①寛容 `validate.ts parseEdges`（未知種別破棄→保持、非空文字列のみ要求）②厳格 `validate_doc.ts validateEdgeType`（enum→非空文字列）③バックエンド `models.py EdgeV2.type`（`Literal`→`str min_length=1`、**保存時422拒否の解消**）。加えて ④CE3 パッチ経路 `patch_apply.ts parseEdge`（レビューで発見・同修正）。RelationSummary は再生成可能な派生データのため未知 relationType を「unknown」へ正規化して行を保持（4経路とも）。
- **描画（EdgeLayer）**: 因果=to端矢印・相互=両端矢印・同値=中点「=」・対立=既存破線。矢先はカード矩形/島ポリゴンの境界に配置。**長年の重大バグを発見・修正**: 外側 `<svg>` の `x`/`y` 属性は HTML 埋め込みでは無効のため、全関係線が +100000px 画面外に描画されており**関係線は一度も画面に表示されていなかった**（クリーンな main で再現確認済み）。CSS `left/top: -100000px` への変更で修正。
- **操作**: SidePanel の接続セクションが5種別を提示（既定は「関連」＝種別確定を強制しない）。エッジインスペクタに種別変更 select（1操作=1取り消しステップ）と未知種別の保全notice。`visibleEdgeInspectorMeta` をカード↔カード関係線にも拡張（従来は island↔island のみで、カード間関係線は選択しても即解除されインスペクタ不可だった）。
- **波及同期**: `relationTypeLabel`（abstract map: CAUSAL/MUTUAL/EQUIVALENCE）・`island_relation_explain`・`relation_summary_ops`（`normalizeRelationType`）・`structural_metrics`（typed edge 判定を既知5種別へ）・`api/client.ts`・`models_ai.py`・i18n（両ロケール）。

### 検証

- typecheck 0 / vitest **925 passed**（184 files。保全ラウンドトリップ7件＋回帰アンカー1件を追加）
- backend: ruff クリーン / pytest **283 passed**（語彙往復・未知種別保全・空文字列422の3テスト追加）
- e2e 新規3件 passed: `edge_type_vocabulary.spec.ts`（種別記号の描画区別／インスペクタからの種別変更＋Ctrl+Z／未知種別の import→save 往復保全を PUT ペイロード実測で検証）
- 既存の広範な e2e（33件バッチ）で非回帰確認
- レビュー: アドバーサリアルworkflowはセッション上限で全エージェント失敗（16時リセット）のため、同5観点（往復整合・契約整合・描画幾何・UIフロー・テスト/i18n同期）を**メインループで手動実施**し、CE3パッチ経路の enum 残存（`patch_apply.ts` 2箇所）・`App.tsx` の relationType 正規化・`structural_metrics.ts` の typed 判定を発見・修正した。

### 残課題（スコープ外・別issue候補）

- 凡例（CanvasLegend）への関係記号エントリ追加（ADR-0048 D1 の凡例1行追加運用は「状態」向けの規約であり本Issueの契約違反ではないが、発見可能性のため追加が望ましい）。
- 派生（島間集約）エッジの方向保存表示（現状は種別抑制の汎用表示＝UX-SCALE-01 レッドライン準拠）。

### 追記 2026-07-09: 実装照合レビュー（design-qa-checklist、初回）— クリーンパス

`02_Architecture/design/design-qa-checklist.md` 第5回として実施。`03_Implement/frontend/scripts/capture_design_conformance_kj_20260709.mjs` で因果・相互・同値・対立・未知種別の5種別を1文書に並べ実機（Docker Playwright）取得し、A/B/C/D 全節を照合した結果、乖離なし（詳細はチェックリスト側に記録）。

調査過程で「相互（mutual）の逆方向矢印が全体像スクショで視認できない」という視覚的懸念が生じたが、(1) 既存 `e2e/edge_type_vocabulary.spec.ts`（3/3 passed）で `arrow-from` の存在を再確認、(2) `data-edge-symbol="arrow-from"` 要素の `boundingBox()`/`outerHTML` を直接検査し、正しい座標（カード境界近傍、幅12.6×高さ12.1px）に存在することを確認——**誤検知**であり、フルページスクショの縮小表示で小さな三角形がカード境界に近接して視認しづらかっただけと判明。実装バグではないため修正は行っていない。
