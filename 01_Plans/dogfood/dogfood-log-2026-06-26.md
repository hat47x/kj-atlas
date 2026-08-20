# Dogfood Log — 2026-06-26

> ADR-0042 最小ドッグフード経路（5手順）の検証結果。
> バックエンド不在のため、フロントエンド単体 + 自動テスト結果 + 実装作業中の観察に基づく。
> 非監視・定性のみ（ADR-0042 §非監視制約）。

## 実行環境

- Frontend: Vite 5.4.21, React 18, TypeScript
- Backend: 不在（フロントエンド単体検証）
- テスト: Vitest 4.0.18, 174 files, 836 tests all passed

## 手順1: 空状態または自分のメモからカードを置く

### 結果: ✅ 完走

- フロントエンド起動 (`npm run preview`) → StartPanel 表示確認済み
- サンプル文書ロード → 3枚のカード表示確認済み (first_meaningful_map_mouse_flow.spec.ts)
- 新規文書作成 → 空キャンバス + カード追加可能 (ux_operability_regression.test.ts Phase 1-5)

### 摩擦点

- (低) バックエンド不在時は保存不可。StartPanel の「新しい文書を作成」ボタンは表示されるが、
  保存できない状態であることが初心者に分かりにくい。
  → 既存対策: readOnly モード + サンプル読込は backend 不要で動作する

## 手順2: 保留（Hold）・違和感（Critique）・根拠不足を「作業状態」として残す

### 結果: ✅ 完走

- カード holdState セレクター: active/held/pending/shelved の4状態（SidePanel 実装確認済み）
- Critique タグ: 5種（too_close/too_far/not_the_same/feels_off/no_articulable_reason）選択可能
- 違和感メモ入力可能、AI無効時は「再提案候補なし」を明示 (reproposal_hint i18n)
- Evidence links (supports/contradicts) 表示・追加可能
- キーボード E2E (domain_expression_keyboard_access.spec.ts): 3 tests pass

### 摩擦点

- (低) critique タグと holdState が別々のUI要素にある。
  違和感を残す操作と保留を宣言する操作の関係が初心者に自明でない。
  → DOMAIN-EXPR-03 (In Progress) で解決予定

## 手順3: まとまり/関係を作り、俯瞰⇄詳細を往復

### 結果: ✅ 完走

- Island 作成・カード追加: ux_operability_regression.test.ts Phase 3 pass
- 関係線 (edges): スキーマ・UI 実装済み
- Collapse/Expand: Island 単位で折りたたみ可能
- View controls: 探索/レビュー/要約 viewMode 切替、LOD 制御
- 元に戻す (undo): merge revert 実装済み

### 摩擦点

- なし（実装作業中に大きな問題は観察されず）

## 手順4: 共有前確認を通し、確定点・保留点・未レビュー情報・根拠への戻り方を含む成果物を1つ出す

### 結果: ✅ 完走

- SharePanel: SafeMode ON 表示、domain expression summary (unreviewed/hold/critique/evidence/contradiction counts)
- 共有前確認: 未レビュー draft 除外 (SafeMode ON 時)
- Review pack export: trace files (evidence_trace, contradiction_trace, trace_analytics)
- Narrative export: claimType + reviewState annotations + evidence links セクション
- Read-only reviewer inspection: E2E pass (review_pack_trace_export.spec.ts 2 tests)

### 摩擦点

- (低) Review pack の detail/overview 切替が初心者にわかりにくい
  → SharePanel にヒント文言あり。UX改善の余地

## 手順5: 「思考が雑にならなかったか」「早すぎる収束を強いられなかったか」の所感

### 結果: ✅ 実装観察に基づく評価

- SafeMode 既定ON: 共有時に未レビュー本文が自動除外される。利用者が意識せずとも安全側。
- proposal-only: AI提案は自動適用されない。人間が常に最終判断を持つ（CVI-2, CVI-3 テストで担保）。
- 保留状態の可視化: DomainStateSummary がカード状態分布を表示。
  未確定事項が「失敗」ではなく「作業状態」として見える設計。
- provider=none 既定: LLM が無くても全基本操作が可能。AI への依存は明示的選択。
- 実装中に「これを確定させなければ次へ進めない」という強制は一度もなかった。

### 高優先の摩擦点

1. （高）**実ユーザー不在**: すべての検証は開発者自身によるもの。
   第三者（非開発者）が同じ経路を迷わず辿れるかは未検証。
   → 段階C（第三者利用）まで NOTICE 維持（ADR-0042 設計通り）

### 低優先の摩擦点

1. （低）**バックエンド不在時の UX**: 保存不可・新規作成不可の状態が初心者に明確でない。
   → 既存対策あり（readOnly banner + サンプル読込）
2. （低）**Critique/Hold の概念的分離**: 違和感と保留が別UI要素。一貫した操作モデルが欲しい。
   → DOMAIN-EXPR-03 で対応中
3. （低）**Review pack detail/overview 切替の認知負荷**: 出力形式の選択肢が多い。
   → 既存ヒント文言あり。UX改善の余地

## NOTICE 段階判断（ADR-0042 基準）

- **現在: 段階A** 「人的レビュー・利用を伴っていない」
- **今回の判断: 段階A 維持**。テスト自動化・開発者検証は充足したが、
  第三者利用（段階B 要件）は未達成。
- 段階B への移行条件: 非開発者1名以上が本番同等環境で5手順を完走し、
  高優先の摩擦がゼロになること。

## 安全条件確認

- [x] SafeMode 既定ON: 確認（SharePanel, E2E）
- [x] 共有前確認: 確認（domain_summary + unreviewed exclusion）
- [x] import sanitize: 確認（zip validation, file path safety）
- [x] proposal-only: 確認（CVI-2, CVI-3 テスト pass）
- [x] provider=none で主要価値成立: 確認（全基本操作が LLM なしで可能）
