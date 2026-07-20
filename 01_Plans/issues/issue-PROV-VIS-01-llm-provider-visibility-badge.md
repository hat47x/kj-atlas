# Issue Draft: PROV-VIS-01 LLMプロバイダ可視性バッジ（読み取り専用・View パネル）

- Type: Feature request
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: Claude Code
- Scope: `03_Implement/frontend/src/ui/ViewControlsPanel.tsx`, `03_Implement/frontend/src/App.tsx`, `03_Implement/backend/src/kj_atlas_api/routes/`, `03_Implement/frontend/src/i18n/locales/`, `03_Implement/frontend/e2e/`
- Related Backlog: `PROV-VIS-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0050-llm-provider-observability-and-contract-fidelity.md`（D1）, `02_Architecture/llm_provider_spec.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: PROV-VIS-01
- RequirementStatement: 現在有効な LLM provider（none/local/large-scale/fixture）と直近の呼び出し結果（成功／`provider_unavailable`／`provider_timeout`／`provider_validation`／未使用）を、View パネル内に読み取り専用で表示する。ランタイムでの provider 切替 UI は提供しない。
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=`KJ_ATLAS_LLM_PROVIDER=none`（既定） / 操作=View パネルを開く / 期待結果=「AI: 無効（none）」等が表示され、切替ボタンは存在しない。AI提案を実行し接続エラーが起きた場合、パネルの状態ラベルが `provider_unavailable` 等へ変わる（PROV-ERROR-01 の構造化エラーに依存） / 除外=provider のランタイム変更 UI、％・スコア・信頼度の表示。
- GoNoGoGate（Required / Optional / N/A）: Optional
- SecurityGateImpact: N/A（表示のみ・ガバナンス境界は不変＝運用者設定のまま）
- VerificationLevel: e2e
- DecisionStatus（Fixed / Pending）: Fixed（ADR-0050 D1）
- DecisionQueueRef: `ADR-0050`

## 1) 課題 / Problem statement

- `KJ_ATLAS_LLM_PROVIDER` はデプロイ時の環境変数のみで、アプリ内に「今 AI が有効か、有効なら何が動いているか」を示す手段が一切ない。運用者・利用者とも、AI提案が失敗したときに「意図的に無効」なのか「設定ミス/接続断」なのか画面から判断できない。

## 2) 背景 / Context

- ADR-0050 D1 で確定: 読み取り専用・View パネル内（既存の開示済み領域）に配置し、初期表示アンカーへの純増をゼロにする。ランタイム切替は設けない（SafeMode と同じ運用者制御のガバナンス境界を維持）。
- 状態ラベルは PROV-ERROR-01（構造化エラー伝播）の成果を利用する。エラー種別が伝わらない段階では「provider種別のみ」を先行表示してよい（依存関係は緩い順序）。

## 3) 判断基準による優先度評価

- 価値: 「AIなしで完結」の透明性を高め、provider=none が既定であることをユーザーが自分で確認できるようにする（ADR-0001 P-07 自己ホスト/プライバシー既定と整合）。
- 安全: 表示のみ。ランタイム切替を提供しないため、ガバナンス（大規模外部送信の opt-in 制御）を弱めない。
- 規模拡大: 運用形態（Offline/Intranet/Enterprise、ADR-0009 Phase E）の切り分けに役立つ。
- 後方互換: スキーマ変更なし。

## 3.2 非目標 / Non-goals

- provider のランタイム変更・設定画面。％・信頼度・成功率などのスコア表示（反スコアリング）。ヘッダーへの常時表示バッジ（CB-1: View パネル内に留める）。

## 4) 提案する解決策 / Proposed solution

- `ViewControlsPanel` に「AI プロバイダ」節を追加: 現在の provider 種別（バックエンドから `/healthz` 等で取得、または起動時の設定エコーバック）＋直近の呼び出し状態ラベル。
- 状態ラベルは中立色（amberは保持系に予約済みのため使わない）。
- i18n（ja/en）。

## 5) 受け入れ条件 / Acceptance criteria

- [x] AC-1: View パネルに現在の provider 種別が読み取り専用で表示されることが e2e で固定される（`e2e/ai_provider_status.spec.ts`）。
- [x] AC-2: provider を切り替える UI 要素が存在しないこと（combobox/radiogroup 皆無・`onProviderKindChange` 等の handler 不在）を e2e＋回帰アンカーで固定。
- [x] AC-3: 表示に％・スコア・信頼度が含まれない（種別と直近呼び出し結果ラベルのみ）。
- [x] AC-4: 初期表示アンカーが非回帰（新セクションは View パネル内の既存開示領域に追加。vitest 882 件全通過）。
- [x] AC-5: i18n（ja/en）キー整合テストが通る。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 provider 種別の取得経路（起動時設定エコーバック or 軽量エンドポイント）確定。
- [x] T2 View パネル UI＋i18n。
- [x] T3 PROV-ERROR-01 の状態コードとの接続（先行実装分は provider種別のみで暫定表示）。
- [x] T4 e2e。

## 7) 検証計画 / Validation plan

- `cd 03_Implement/frontend && npm run typecheck && npm test && npx playwright test`

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（View パネル内・既存開示領域） / 保留操作の距離=不変 / 取り消し導線=N/A（表示のみ）

## Traceability

- Related: `01_Plans/adr/ADR-0050-llm-provider-observability-and-contract-fidelity.md`（D1）
- Related: `01_Plans/issues/issue-PROV-ERROR-01-structured-provider-error-propagation.md`
- Related: `01_Plans/issues/issue-GENAI-GOV-01-generative-ai-lane-boundary-and-readiness.md`（Lane B: LLMProvider経路）, `02_Architecture/value_traceability.md` §2.9
- Derived-from: `01_Plans/adr/ADR-0050-llm-provider-observability-and-contract-fidelity.md`

## 完了記録 2026-07-06（Claude Code）

- **取得経路（T1確定）**: 新規エンドポイント `GET /ai/provider-status`（`ai.py`・既存の `x-api-key` 認証ミドルウェア配下＝`/healthz` のような無認証エンドポイントにはしない）。`get_provider().provider_kind` を返すだけの**静的な設定エコー**で、接続先への疎通確認は行わない（`local_http` 等のエイリアスは解決済みの `local` として返る）。バックエンド新規テスト3件（`test_ai_provider_status_route.py`）で疎通確認なし・エイリアス解決を固定。backend 全体 281 passed / 20 skipped・ruff clean。
- **直近の呼び出し結果**: 新規バックエンドAPIは持たず、**フロントエンド側で実際のAI呼び出し4箇所**（レイアウト提案・島サマリ・ナラティブ整合性チェック・ナラティブ生成。PROV-ERROR-01 で整備した `classifyAiProviderError` を再利用）の成否をその場で `lastAiCallOutcome` state に反映する設計とした（ADR-0050 D1「直近の呼び出し結果」の実装解釈）。
- **UI**: `ViewControlsPanel` に「AI プロバイダ」節を追加（種別表示＋直近結果ラベル）。**切替コントロールは一切設置していない**（select/radiogroup/onChange 皆無であることを回帰テストで固定）。
- 検証: typecheck 0 / vitest **882 passed**（180 files）/ e2e 新規2件 passed（`ai_provider_status.spec.ts`: local表示・none表示）+ 既存 `canvas_legend`/`canvas_protection`/`card_meta_row`/`empty_canvas_onboarding` 等13件で非回帰確認 / 実機スクショで「AI プロバイダ / ローカル（local）」の読み取り専用表示を確認。
