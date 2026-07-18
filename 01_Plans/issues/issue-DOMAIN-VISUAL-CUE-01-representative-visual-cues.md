# Issue: DOMAIN-VISUAL-CUE-01 島・情報集合の代表視覚手掛かり

- Type: Feature request / UX / AI / Data governance
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: Codex / Maintainer
- Scope: `00_Prompt/representative_visual_cue_requirements.md`, `00_Prompt/domain.md`, `00_Prompt/ai_cognitive_externalization_requirements.md`, `01_Plans/adr/ADR-0059-representative-visual-cue-source-boundary.md`, `02_Architecture/architecture.md`, `02_Architecture/representative_visual_cue_evaluation.md`, `02_Architecture/data_model_operations_overview.md`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/export/`, `03_Implement/frontend/src/import/`
- Related Backlog: `DOMAIN-VISUAL-CUE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0059-representative-visual-cue-source-boundary.md`, `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`, `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`, `00_Prompt/representative_visual_cue_requirements.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: DOMAIN-VISUAL-CUE-01
- RequirementStatement: 島または利用者が選んだ情報集合に、内容を代表する任意の小さな視覚手掛かりを文字と併記し、意味を早く確定したり外部へ情報を暗黙に共有したりせず、目的のまとまりを見つけ直す負担を下げる。
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=利用者が多数の島を含む文書を開いている / 操作=島を選び、手描き・基本図形・撮影写真・絵文字・プリセット・権利確認済み外部素材・生成候補から任意の手掛かりを確認して採用する / 期待結果=表札と手掛かりを併用して島を見つけ直せ、画像なしへ戻せ、一次資料と識別画像を区別でき、外部通信と権利条件を事前確認できる / 除外=自動分類、自動採用、画像だけの意味伝達、装飾目的の常設画像。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export / import-sanitize / public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0059`

## 1) 課題 / Problem statement

島が増えると、利用者は表札を順に読んで目的のまとまりを探す必要がある。内容と関連する小さな絵文字や画像は再認識を助ける可能性があるが、装飾画像は注意を奪い、断定的な画像は曖昧さや対立を隠し得る。また、外部素材と生成画像は通信、権利、保存、共有の責任が異なる。

現状の設計は「画像生成（将来）」とだけ記載し、標準KJ法のシンボルマークや図解記号、写真KJ法、フィールド写真、簡易な手描き・汎用図形との連続性を扱っていない。また、目的、対象、各供給経路、SafeMode、権利表示、アクセシビリティ、削除を定義していない。

## 2) 提案する解決策 / Proposed solution

- 正本要件 `00_Prompt/representative_visual_cue_requirements.md` に、視覚手掛かりを表札・本文・根拠の代替ではない任意の再認識補助として定義する。
- 供給経路を A: 手描き/基本図形/利用者画像、B: Unicode絵文字/同梱プリセット、C: 権利確認済み外部素材、D: proposal-only画像生成に分離する。
- Phase 1では、紙のシンボルマークや写真ラベルから自然に移れる通信不要の作成・選択・解除・非表示を検証し、既定画面と既存操作を変えない。
- B/Cは、外部通信前確認、SafeMode、出所・ライセンス・生成来歴、共有前確認、削除を実装条件とする。
- 画像なしとの比較で再発見の時間・見誤り・主観的負担が改善または非悪化であることを確認する。

### 複雑性予算

初期表示の常設要素を増やさず、島または選択集合の詳細から一段深く開く。画像なしを既定として維持し、外部素材と生成画像は高度機能でのみ提示する。

## 3) 受入条件 / Acceptance criteria

- [x] AC-1: 目的、対象、非目標、表札・本文・根拠との意味境界が要件に定義されている。
- [x] AC-2: 絵文字、同梱プリセット、外部素材、生成画像が別経路として比較されている。
- [x] AC-3: SafeMode、外部通信前確認、権利・出所、生成来歴、共有・削除の要件が定義されている。
- [x] AC-4: 代替テキスト、文字との併記、非表示、固定寸法、キーボード操作の要件が定義されている。
- [x] AC-4a: 手描きシンボル、基本図形、写真ラベル、フィールド写真、図解記号との連続性と意味の違いが定義されている。
- [ ] AC-5: `ADR-0059` の供給経路、許容ライセンス、保存境界が受理されている。
- [ ] AC-6: Phase 0 fixtureで、画像なし・手描き・基本図形・撮影写真・絵文字・プリセットの再発見時間、見誤り、主観的負担を比較している。
- [ ] AC-7: Phase 1のオフライン選択をマウス、キーボード、390px、スクリーンリーダー相当で検証している。
- [ ] AC-8: 外部素材を導入する場合、原典確認、クレジット、キャッシュ、削除、API停止をintegration/e2eで検証している。
- [ ] AC-9: 生成画像を導入する場合、明示送信、proposal-only、SafeMode、provider固定、来歴をintegration/e2eで検証している。
- [ ] AC-10: 代表規模でレイアウト移動、メモリ、保存容量、読み込み時間が予算内である。

## 4) タスク / Tasks

- [x] T1 認知負荷、関連画像と装飾画像、画像・文字の再認記憶に関する研究を確認する。
- [x] T1a 標準KJ法のシンボルマーク・図解化、写真KJ法、フィールド写真、紙とペンを保つデジタル支援を調査する。
- [x] T2 要件正本、ドメイン語彙、AI原則、価値トレーサビリティを同期する。
- [x] T3 供給経路と未決定の保存・権利境界を `ADR-0059` として提案する。
- [x] T4a 具体・抽象・対立・機微情報・記号衝突を含み、手描き印・基本図形・写真ラベル・一次視覚資料を区別するPhase 0の機械可読fixtureと評価手順を固定する。
- [ ] T4b C0からC4の非製品プロトタイプ表示を作り、3人以上の代表利用者による小規模pilotまたは予備操作確認を実施する。
- [ ] T5 Unicode絵文字と固定画像セットについて、OS間表示、アクセシビリティ、ライセンス、配布容量を比較する。
- [ ] T6 採用参照、権利情報、画像本体、サムネイルの保存候補を比較し、ADRを受理または更新する。
- [ ] T7 Phase 1を、手描き/基本図形、利用者画像切り抜き、絵文字/プリセットの小さなPRへ分割して実装し、E2Eと実画面評価を行う。
- [ ] T8 実利用で不足が確認された場合だけ、外部素材と生成画像をそれぞれ別issueへ分割する。

## 5) 検証計画 / Validation plan

- 要件段階: `python 01_Plans/issues/validate_active_issue_memos.py`、`python -m unittest 01_Plans.issues.tests.test_validate_active_issue_memos`、`python 01_Plans/docs_check.py`
- 実装段階: frontend unit test、Playwright E2E、Chrome実画面、代表規模性能計測、外部provider契約test。
- UX評価: `02_Architecture/representative_visual_cue_evaluation.md` と `02_Architecture/design/representative_visual_cue/phase0_scenarios.json` を用い、同じ目的の島を探す課題を文字のみ・手描き・基本図形・写真・絵文字/プリセットで比較する。時間、誤選択、意味誤認、原資料遡及、主観的負担を記録し、見栄えや利用時間だけでは採択しない。
- Stop条件: 関連性を説明できない候補、画像だけによる意味伝達、意図しない外部通信、権利情報欠落、SafeMode回避、初期表示の複雑化のいずれかを確認した場合は実装を昇格しない。

## 6) 依存関係 / Dependencies

- `01_Plans/adr/ADR-0059-representative-visual-cue-source-boundary.md`
- `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`
- `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`

## 7) ADR判定

ADRが必要。画像の意味、供給経路、外部通信、権利、保存、共有の境界は複数モジュールと公開物へ影響し、UIだけの局所判断ではないため `ADR-0059` で提案する。ADR受理前は、要件とfixture検証を進められるが、永続スキーマや外部providerを固定しない。
