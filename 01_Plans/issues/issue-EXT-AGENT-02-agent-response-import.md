# Issue Draft: EXT-AGENT-02 エージェント応答の取り込みと提案化（AgentResponse v1）

- Type: Feature request
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Claude Code
- Scope: `03_Implement/frontend/src/import/`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/domain/`, `03_Implement/frontend/e2e/`
- Related Backlog: `EXT-AGENT-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`（D3）, `02_Architecture/external_agent_collaboration_spec.md`（§4/§5 正本）, `01_Plans/issues/issue-CE3-patch-workspace-presets.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: EXT-AGENT-02
- RequirementStatement: 外部エージェントの応答（agent-response.v1・貼り付け/ファイル）を import 信頼境界（検証・サニタイズ・容量制限）で受け、種別ごとに既存の提案面（マージ候補・島タイトル候補・ナラティブ草稿・違和感候補・PatchWorkspace）へ AI 由来・未レビューの提案として流し込む。自動確定なし・全操作可逆・監査記録を不変条件とする。
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=EXT-AGENT-01 で書き出した依頼に対する応答 JSON を得ている / 操作=「応答を取り込む」へ貼付け→検証結果を確認→取り込み / 期待結果=提案が種別ごとの既存面に未レビューとして出現し、taskId でグルーピング表示される。score/rank/confidence フィールドは破棄され警告表示。baseDocSignature 不一致時は conflict/rediff 経路に乗り黙って適用されない。1件採用→⌘Z で復帰できる / 除外=外部からの自動受信、応答の自動適用、エージェント品質の保証。
- GoNoGoGate（Required / Optional / N/A）: Required（外部由来データの取り込み経路の新設のため、import-sanitize 検証を完了条件とする）
- SecurityGateImpact: import-sanitize（非信頼データの新規取込面。指示文言をデータとして扱いいかなる自動動作にも接続しない）
- VerificationLevel: e2e
- DecisionStatus（Fixed / Pending）: Fixed（ADR-0049 D3・spec §4）
- DecisionQueueRef: `ADR-0049`

## 1) 課題 / Problem statement

- 定額エージェント経路の入力側が未実装。構造化応答を安全に検証し既存レビュー機構へ流し込む取込面（spec の設計ギャップ (2)(5)）が無い。

## 2) 背景 / Context

- 再利用する信頼境界: zip_import の制限値・markdown_sanitize・document/view import の寛容/厳格検証・merge items→選択レビュー→原子的適用・merge-decision-logs・PatchWorkspace（lint/conflict/採否/ロールバック）。本Issueは**パーサ＋変換＋グルーピング表示**のみを新設する。

## 3) 判断基準による優先度評価

- 価値（P-03/P-04）: 外部の思考結果を、レビュー追跡可能な提案として取り込む HIL の完成。EXT-AGENT-01 と対で要件Dを充足。
- 安全: 非信頼データ境界。禁止フィールド破棄（反スコアリング）・サニタイズ・自動確定なしをテスト固定。
- 規模拡大: あらゆる定額エージェントに対応（契約準拠なら取り込める）。
- 後方互換: スキーマ変更なし（提案は既存型・PatchV1 を運搬するのみ）。

## 3.2 非目標 / Non-goals

- 外部からの自動受信（Tier 1/2）。応答の自動適用・自動レビュー昇格。エージェント出力品質の補正（壊れた JSON の再依頼は運用定型文＝EXT-AGENT-03）。ローカルLLMによる反映経路（要件D (a)・別判断）。

## 4) 提案する解決策 / Proposal solution

- `import/agent_response_import.ts`（新規）: フェンス付き JSON 抽出→スキーマ検証（厳格/寛容）→禁止フィールド破棄＋警告→全文字列サニタイズ→容量制限。
- 変換: spec §4.3 の対応表どおり既存面へ（すべて AI 由来・未レビュー）。patch は lint→conflict 検出→PatchWorkspace へ。orphaned targetRef は破棄せず「孤立提案」として保持表示。
- 整合: baseDocSignature 照合・taskId 相関・同一応答の再取込は冪等。取り込みイベントを context-audit（operation=proposal）へ記録。
- UI: 「応答を取り込む」（貼付け＋ファイル）。取込結果サマリ（受理 n・警告 m・破棄フィールド一覧）。

## 5) 受け入れ条件 / Acceptance criteria

- [x] AC-1: 正常応答の取り込みで、5種別が各既存面に未レビュー提案として出現することが e2e で固定される（採用→⌘Z 復帰含む）。※「各既存面」の解釈に関するスコープ判断は下記「完了記録」参照。
- [x] AC-2: score/rank/confidence を含む応答で、寛容=破棄＋警告・厳格=拒否となることが integration で固定される。
- [x] AC-3: baseDocSignature 不一致の patch が黙って適用されず conflict/rediff 経路に乗る。orphaned 提案が保持表示される。
- [x] AC-4: 同一 taskId＋同一応答の再取込が重複を作らない（冪等）。
- [x] AC-5: 応答中の指示的文言が表示のみで、自動動作に接続しない（コードレビュー＋テストで確認）。
- [x] AC-6: 「自動確定なし」（取り込み直後に文書が変化しない）がテストで固定される。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 パーサ＋検証＋サニタイズ（unit/golden）。
- [x] T2 種別→既存面への変換（taskId グルーピング・孤立提案保持）。※「既存面」が実際には2種別（island_title・critique/opposing_viewpoint）に存在しないことが判明したため、新規の統一レビューパネルで代替。下記「完了記録」参照。
- [x] T3 staleness（署名照合・conflict/rediff 接続・冪等）。
- [x] T4 取込 UI＋結果サマリ＋i18n。
- [x] T5 監査（recordProposalDecision で代替。context-audit は不適合。下記「完了記録」参照）＋integration/e2e 一式。

## 7) 検証計画 / Validation plan

- `cd 03_Implement/frontend && npm run typecheck && npm test && npx playwright test`（模擬応答フィクスチャで書き出し→取込→採用→取消のラウンドトリップ）

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（取込は明示操作の面のみ） / 保留操作の距離=不変（提案の保留=held は既存決定語彙で1操作） / 取り消し導線=あり（採用は ⌘Z・patch はロールバック・取込自体は文書を変えない）

## Traceability

- Related: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`, `02_Architecture/external_agent_collaboration_spec.md`（§4/§5/§6）
- Related: `01_Plans/issues/issue-EXT-AGENT-01-agent-task-package-export.md`, `issue-CE3-patch-workspace-presets.md`, `issue-QA-MONKEY-01-safemode-export-boundary.md`
- Related: `01_Plans/issues/issue-GENAI-GOV-01-generative-ai-lane-boundary-and-readiness.md`（Lane C: 外部エージェント成果物連携）, `02_Architecture/value_traceability.md` §2.9
- Derived-from: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`

## 完了記録 2026-07-09（Claude Code）

### スコープ判断1: 「既存面」が実在しない2種別（island_title・critique/opposing_viewpoint）は新規の統一レビューパネルで受ける

実装前の調査で、spec §4.3 が前提とする「既存の候補提示 UI」は5種別のうち3種別にしか実在しないことが判明した。

- `merge_candidate` → `MergeSuggestionsPanel`（`mergeSuggestions` state）: 実在。ただし単一プロデューサ・置き換え専用で、他ソースからの追加（append）経路は無かった。
- `narrative_draft` → `document.narratives`: 実在。追記専用（append-only）で、そのまま流用可能。
- `island_title` → **実在しない**。既存の `IslandSummaryProposal` は `island.summaryText`（要約）を対象とし、`title`（タイトル）ではない。単数（1島につき1件のみ）で複数候補の提示機構もない。
- `opposing_viewpoint`/`critique` → **実在しない**。`CritiqueInput` は `card.critique`/`critiqueTags` から都度導出される派生値で、それに先立つ「候補」というステージング概念自体が存在しない。

「既存面に出現する」を文字どおり実装しようとすると、存在しない機構への配線が必要になる。そこで、5種別すべてを**1つの新規レビューサーフェス**（`AgentResponseImportPanel`、WorkModePanel と同じ専用ダイアログパターン）で受け、種別ごとに以下の実際の宛先へ「取り込む」（1操作=1 `applyDocumentChange`、⌘Zで取消可）:

- `island_title`: `island.title` に設定＋`titleReviewed: false`（既存の `handleIslandTitleChange` と同じ形、ただし未レビューとして記録）。
- `critique`/`opposing_viewpoint`: `card.critique` または `island.critique` に設定（既存の `handleCardCritiqueChange` と同じ経路）。
- `narrative_draft`: `document.narratives` に追記（既存の `handleGenerateNarrativeFromReadingOrder` と同じ経路）。
- `merge_candidate`: `mergeSuggestions` state に追加（既存の `MergeSuggestionsPanel` へ出現し、そのパネル自身の採否フローで最終決定）。
- `patch`: 署名一致＋lintエラー無しの場合のみ、既存の `applyPatchWithResolutionsDetailed`/`appendPatchApplyLog` で直接適用。署名不一致の場合は下記スコープ判断3を参照。

### スコープ判断2: 「孤立提案」は新規概念として設計（既存コードに前例なし）

`targetRef` が現在の文書で解決できない提案は、破棄せず `orphaned: true` としてパネル内に保持表示する（AC-3）。全コードベースを検索したが「参照先が消えても保持表示する」という前例は皆無だった（"孤立"を含む既存コードは全て KJ図解上の「孤立カード」概念で、無関係）。パネル自身のエフェメラルな状態としてフラグを持たせる、シンプルな実装で対応した。

### スコープ判断3: patch の baseDocSignature 不一致は既存ファイルベース競合解決フローへ誘導（新規競合UIは作らない）

調査により、`PatchWorkspacePanel` の `CandidateItem` には `PatchV1` を運べる型が無く（プレビューテキストのみ）、実際に文書へ適用する機構（lint→conflict検出→適用）は**別の**、ファイル読み込みベースの既存パイプライン（`handleLoadPatchFile`/`handleLoadPatchBaselineFile`/`patchConflictReport`）にあることが判明した。この2つは互いに配線されていない。

`patch_lint.ts` の署名不一致チェックは `warn`（ブロックしない）であり、既存コードの既定動作としては署名不一致でも適用をブロックしない。しかし AC-3 は「黙って適用されず conflict/rediff 経路に乗る」ことを求めているため、**本Issueの取込フロー独自に**、署名不一致の場合はワンクリック適用を提供せず、「パッチファイルとして書き出す」ボタンのみを提供し、既存のファイルベース競合解決フローへ委ねる設計とした（新しい競合UIを重複実装しない）。署名が一致し lint エラーが無い場合のみ、ワンクリック適用（`applyPatchWithResolutionsDetailed`＋`appendPatchApplyLog`）を許可する。

### スコープ判断4: 監査は `context-audit` ではなく既存の `recordProposalDecision`（`/ai/proposals/audit`）を再利用

Issue本文は「取り込みイベントを context-audit（operation=proposal）へ記録」と書いているが、調査の結果、`context-audit`（`/docs/{id}/context-audit`）は CE1/CE4 自身の `query→bundle→proposal→apply` 監査チェーン専用で、`equivalenceKey`/`bundleHash` 等 CE1 特有のフィールドを要求し、`operation=proposal` は `command="proposal-diff"` のみを許可する closed-world 契約になっている。外部から貼り付けられた応答にはこれらの実在する相関ハッシュが無く、無理に埋めれば捏造データになる。加えて、この経路をそのまま使うには **バックエンド側のコマンド許可リスト変更が必要**（本Issueのスコープ外）。

代わりに、既存の汎用エンドポイント `recordProposalDecision`（`/ai/proposals/audit`、island-summary の adopt/hold/reject で既に使用中）を全5種別の採用・破棄判断の記録に再利用した。バックエンド変更ゼロ・新エンドポイント無し・既存の一般的な「AI由来提案への人間の決定」記録という用途に完全に一致する。EXT-AGENT-01 が CE1 スタブの代わりにローカルハッシュ計算を選んだのと同じ種類の判断。

### 実装

- `03_Implement/frontend/src/import/agent_response_import.ts`（新規）: フェンス付きJSON抽出、agent-response.v1 スキーマ検証（厳格/寛容）、禁止フィールド（score/rank/confidence/priority）の破棄＋警告（厳格=拒否）、根拠欠落の「(根拠未記載)」ラベル付与（厳格=拒否）、`markdown_sanitize` による全文字列サニタイズ、`ZIP_MAX_TEXT_FILE_BYTES` 相当の容量制限、patch.ops の `PatchOpKind` ホワイトリスト（非ホワイトリストは破棄＋警告、厳格=拒否）＋delete系操作の警告フラグ。
- `03_Implement/frontend/src/ui/AgentResponseImportPanel.tsx`（新規）: 貼付け欄・厳格モード切替・解析ボタン・エラー/警告表示・提案カード一覧（種別・対象・内容・根拠・孤立/署名不一致の注記・取り込む/破棄するボタン）。WorkModePanel と同じフォーカストラップ・Escape・focus-return実装。
- `03_Implement/frontend/src/App.tsx`: 「詳細」ON時のみ出現するトリガーボタン（`data-ui-core-action` 非付与で既存7件カウント非回帰）＋パネルマウント＋種別別の取り込みハンドラ（`computeAgentProposalReviewFlags` で孤立/署名不一致を事前計算）。
- i18n: `agent_response_import.*`＋`app.history.agent_response.*` を ja/en 両ロケールに追加。

### 検証

- typecheck 0 / vitest **985 passed**（187 files。パーサ単体テスト14件＋regression anchor 1件を追加）。
- e2e 新規4件 passed: `agent_response_import.spec.ts`（トリガーが「詳細」の背後にあること／解析だけでは文書が変化せず・クリーンな提案の取り込みは1操作=1 ⌘Z 復帰・孤立提案は保持表示され取り込みボタンが出ないこと・署名不一致patchはファイル書き出しのみ提供されること／5種別すべての取り込み経路が正常動作すること／同一応答の再貼り付けが重複を作らないこと）。
- 既存e2e 11件（`agent_task_export`・`pre_share_summary_gate`・`complexity_budget_foregrounding`）で非回帰確認。
- 全て `nix develop`（Node 20 devShell）+ Docker Playwright (`mcr.microsoft.com/playwright:v1.58.2-jammy`) 経由で実行。

### 残課題（スコープ外・別issue候補）

- `mergeSuggestions` state の「1件決定で全件消える」既存の副作用（`applyDocumentChange` が無条件に空配列化）は本Issue導入前からの既存挙動であり、取り込んだ merge_candidate 提案もこの制約を継承する。修正は別issueの対象（既存機能への広い変更のため本Issueのスコープ外とした）。
- `context-audit` へ本イベントを載せる場合は、バックエンド側で `_CE4_OPERATION_TO_COMMANDS["proposal"]` にコマンドを追加するADRレベルの決定が必要（本Issueでは行わない）。
