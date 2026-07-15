# Issue: DOMAIN-CARD-QUALITY-01 定性情報カードの品質支援

- Type: Feature request / UX / Domain quality
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer / UX contributor / Domain expert
- Scope: `00_Prompt/qualitative_card_quality_requirements.md`, `00_Prompt/domain.md`, `01_Plans/adr/ADR-0001-value-to-requirements.md`, `02_Architecture/schemas.md`, `02_Architecture/value_traceability.md`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/domain/`, `03_Implement/frontend/e2e/`
- Related Backlog: `DOMAIN-CARD-QUALITY-01`
- Related ADR/Spec: `00_Prompt/qualitative_card_quality_requirements.md`, `01_Plans/adr/ADR-0001-value-to-requirements.md` P-08, `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`, `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`, `01_Plans/adr/ADR-0047-design-decision-adr-saturation-and-execution-first.md`, `02_Architecture/schemas.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: DOMAIN-CARD-QUALITY-01
- RequirementStatement: 利用者が本文だけですぐカードを保存できる操作性を保ちながら、元の意味への忠実性、一枚一中心、必要な文脈、元記録への遡及、観察と解釈の区別、少数・矛盾情報の保持を、保存後または要求時の任意提案で支援する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=利用者が定性情報をカードへ記録する、AIは無効でもよい / 操作=本文を保存し、必要に応じて品質支援を開き、一件ずつ提案を採用・見送り・保留する / 期待結果=保存は遮断されず、採用前の本文は変わらず、元の意味・少数意見・矛盾が保持され、マウスとキーボードで本文へ戻れる / 除外=研究品質の認定、事実確認の自動化、品質スコア、全メタデータの必須化。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

現行の要件は、カードを作った後の保留、違和感、根拠、矛盾、分類、共有を詳しく扱う一方、構造化の入力となるカード本文の品質を定義していない。

定義がないまま支援を追加すると、次の問題が起きる。

- 短文化だけを重視し、語り手の意図や必要な文脈を失う。
- 一枚に複数の内容が混在し、グループ編成時に何を比較しているか分からなくなる。
- 観察、引用、解釈、仮説が同じ事実のように扱われる。
- 元記録へ戻れず、要約やAI提案を検証できない。
- 少数意見や矛盾が「品質が低い」「ノイズ」として消される。
- 品質確保のために必須欄や警告を増やし、利用者が記録自体を諦める。

この課題は、カード作成の速さと定性情報の信頼性を二者択一にせず、**記録を先に完了し、整える作業を後から任意に行える**設計で解く必要がある。

## 2) 背景 / Context

- KJ法の実践文献では、一つのラベルへ一つの中心的主張を入れる単位化が用いられている。
- KJ法を用いた質的研究では、文脈や語り手の意図を損なわない圧縮と、ほかとまとまらないラベルの保持が重視される。
- AHRQ の回答負担調査では、長い・曖昧・頻繁な質問を避け、必要最小限の質問、読みやすさ、適切なタイミング、必要時の支援が負担軽減策とされる。
- 現行 `Card` は、本文 `text`、`claimType`、`meta.source`、`holdState`、`critique` を持ち、初期要件は新しい必須スキーマなしで表現できる。
- `ADR-0043` は初期表示の純増と保留までの距離を抑えるため、品質支援を常設フォームや保存ゲートにしないことを求める。

調査根拠と要件の正本は `00_Prompt/qualitative_card_quality_requirements.md` に集約する。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: カードの元の意味が失われると、後続の配置、保留、違和感、AI提案、共有を正しくレビューできない。P-08として中核価値へ追加する。
- 安全（THREAT_MODEL / SafeMode）: 出典や文脈は個人情報・機密情報を含み得る。実名の要求や外部AIへの暗黙送信を行わず、既存SafeModeを維持する。
- 企業・行政要件（enterprise_architecture）: 組織ごとに必要な記録責任は異なる。MVPで一律の必須欄・承認責任を導入せず、将来の組織ワークフローは別判断とする。
- 後方互換（schemas）: 初期実装は既存のoptional情報を利用し、`Document.version`、import受理キー、共有契約を変更しない。

## 4) 提案する解決策 / Proposed solution

### 4.1 Phase A: 要件と代表fixtureを固定する

- `qualitative_card_quality_requirements.md` をNormative正本とする。
- `domain.md`、`ADR-0001` P-08、`schemas.md`、`value_traceability.md` を同期する。
- 次の代表fixtureを固定する: 一中心、複数中心、文脈不足、引用と解釈の混在、少数・矛盾、出典不明。

### 4.2 Phase B: AI不要の自己確認支援を実装する

- 本文の保存を先に完了する。
- 選択中のカード詳細から「カードを整える」に到達できるようにし、初回画面やカード面へチェックリストを常設しない。
- 一度に表示する問いは一つとし、中心的内容、文脈、出典、観察と解釈の順に確認できる。
- 各問いには「なぜ役立つか」と、「整える」「このまま保存」「今は保留」を表示する。
- 自動判定を断定として使わない。AIなしでは自己確認を中心とし、本文やメタデータを自動変更しない。

### 4.3 Phase C: proposal-onlyの文脈別提案を追加する

- LLMProviderまたは交換可能な支援ロジックは、分割案、確認質問、差分を提案できる。
- 提案は既存のAIレーン、SafeMode、Context Query、proposal-only、人手昇格境界に従う。
- `KJ_ATLAS_LLM_PROVIDER=none` ではPhase Bがそのまま利用でき、機能欠落として扱わない。

### 非目標

- 品質点数、ランキング、合否、赤黄緑の総合評価。
- 保存・配置・共有前確認を品質確認で遮断すること。
- 研究の妥当性、事実性、組織承認の認定。
- 起票者、確認担当者、確認期限の永続スキーマ化。
- 少数意見、外れ値、矛盾の自動削除・自動統合。

## 5) 受入条件 / Acceptance criteria

- [x] AC-1: 定性情報カードの品質次元と、品質が点数・合否ではないことがNormative文書に定義されている。
- [x] AC-2: P-08、ドメイン定義、スキーマ境界、価値トレーサビリティが同じ要件を参照している。
- [ ] AC-3: 本文以外の必須入力なしに、一回の保存操作でカードを作成できる。
- [ ] AC-4: 品質支援は保存後または要求時に非モーダルで開き、一件ずつ採用・見送り・保留できる。
- [ ] AC-5: 提案の採用前に本文、`claimType`、出典、レビュー状態が変更されない。
- [ ] AC-6: 少数意見または矛盾するカードが、低品質として自動削除・統合・降格されない。
- [ ] AC-7: 分割または言い換えの前後を比較し、元本文へ戻れる。
- [ ] AC-8: マウスとキーボードで支援の開始、採用、見送り、保留、本文へのフォーカス復帰を完了できる。
- [ ] AC-9: 日本語と英語で同じ意味と選択肢を提供し、390px幅で本文や主要操作を覆わない。
- [ ] AC-10: SafeMode既定ON、proposal-only、`human_reviewed`人手昇格、`KJ_ATLAS_LLM_PROVIDER=none` の回帰テストが通る。
- [ ] AC-11: E2E証跡が6種の代表fixtureを含み、誤検知時にも保存と見送りが可能である。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 KJ法、定性研究の信頼性、回答負担、人間中心設計の一次・公的情報を調査する。
- [x] T2 カード品質のNormative要件を作成し、上流・設計文書へ反映する。
- [x] T3 新規スキーマとADRが現時点では不要であること、およびADR昇格条件を明記する。
- [x] T4 6種の代表fixtureと、本文保存を先行する品質支援の状態遷移をテストで固定する。
- [x] T5 Phase Bの自己確認UI、i18n、キーボード操作、フォーカス復帰を実装する。
- [ ] T6 提案採用前の不変条件、少数・矛盾保持、SafeMode、provider noneをunit/integrationで固定する。
- [ ] T7 390px/desktop、マウス/キーボードのE2Eとスクリーンショットを取得する。
- [ ] T8 Phase Cの必要性をPhase Bの使用証跡から判断し、必要な場合だけ別issueへ分割する。

### T4 実装証跡（2026-07-15）

- `src/domain/card_quality.ts`: `DocumentV2`/`Card` へ新規フィールドを追加せず、質問4種（unit/context/trace/status、§4.2の固定順）、決定3種（apply/keep_as_is/hold_for_now）、状態遷移関数 `openCardQualityAssist`/`answerCardQualityQuestion` を独立定義した。決定・質問関数はいずれも assist state のみを入出力とし、`Card` を読み書きできないため、採用前不変（CQ-REV-01, AC-5）は型・実装レベルで保証される。
- `src/domain/card_quality.fixture.ts`: §7の6種代表fixture（single_center / multi_center / context_poor / quote_interpretation_mixed / minority_or_contradiction / unknown_source）を固定した。
- `src/domain/card_quality.test.ts`: 全fixtureで質問順が同一であること（少数・矛盾fixtureを特別扱いしないこと)、4問すべて回答するまでresolvedにならないこと、Card凍結下でも状態遷移が本文を変更しないこと、見送り済み質問が本文未変更のセッション内では再提示されないこと（QUX-HUMAN-01）、`CARD_QUALITY_DECISIONS` に評価・スコア語が含まれないこと（CQ-DIVERSE-01）を検証する。
- 検証結果: 対象8 tests作成（frontend全体テストは検証計画のコマンドで実行）。UI・永続化・i18n・provider統合は未実装であり、T5以降の対象とする。

### T5 実装証跡（2026-07-15）

- `src/ui/SidePanel.tsx`: 選択中カード詳細の「このカードを表示」ボタン直後に「カードを整える」トリガーと非モーダルの自己確認ブロックを追加した。既存の島サマリー提案ブロック（採用/保留/見送りの3ボタン構成）と同じ視覚パターンを踏襲し、`currentCardQualityQuestion`/`answerCardQualityQuestion`（T4）を呼び出すだけの薄いpresentation層とした。閉じるボタンはトリガーへ`setTimeout(...).focus()`でフォーカスを戻す（既存`WorkModePanel`等のフォーカス復帰慣用句を非モーダル向けに簡略化）。全ボタンは標準`<button>`要素のため、追加のキーボード配線なしにTab/Enterで操作できる。
- `src/App.tsx`: `cardQualityAssistByCardId`（カードIDをキーとするセッション内のみの状態、文書へは永続化しない）と`openCardQualityAssistCardId`を追加し、4つのハンドラ（open/answer/close/open-text-editor）を`selectedCard`宣言後に配置した。「本文を編集する」ボタンは既存の`editingCardId`編集モード（Canvas側のカード本文textarea）を再利用する。
- `src/i18n/locales/{en,ja}.json`: `side_panel.card_quality.*`（トリガー/完了/決定3種/閉じる/本文編集）と`cardQuality.question.{unit,context,trace,status}.{prompt,rationale}`をen/ja両方に追加した（キー総数1555件で一致を確認）。文言は要求文書§4.2の推奨例に基づく自己確認の問いとして書き直した（AIによる断定ではなく「〜していますか」形式）。
- 検証結果: `npm run typecheck`、`npx vitest run`（1055/1055 pass、既存の無関係な1ファイル失敗は`~/kjnative-fe`がリポジトリルート非同梱の副作用でT5と無関係）。**ブラウザでの手動確認は本環境のBrowser Preview toolがWSL側dev server(localhost)に到達できず実施できなかった** — キーボード操作・フォーカス復帰・390px幅表示の実機確認はT7のE2E証跡に委ねる。AC-4/AC-5/AC-6は構造的に成立するが、チェックボックスの更新はT6のunit/integration固定を待つ。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans.issues.tests.test_validate_active_issue_memos`
  - `rg -n "P-08|DOMAIN-CARD-QUALITY-01|qualitative_card_quality_requirements" AGENTS.md 00_Prompt 01_Plans 02_Architecture`
  - 実装後: `cd 03_Implement/frontend && npm run typecheck && npm test`
  - 実装後: `cd 03_Implement/frontend && npx playwright test e2e/card_quality_assistance.spec.ts`
- 期待結果:
  - 文書参照、issueメタ、要件IDが整合する。
  - 本文保存の先行、任意提案、採用前不変、少数・矛盾保持、マウス/キーボード、390pxを再現できる。
- 未実施時の理由・代替検証:
  - 本変更セットはPhase Aの要件確定までを対象とする。FrontendテストはT4以降の実装変更セットで必須とする。

## 8) 代替案 / Alternatives considered

- 代替案A: 出典、話者、日時、分類をすべて必須入力にする。
  - 不採用理由: 探索初期の記録負担が高く、不明な情報の推測入力を誘発する。
- 代替案B: AIが品質を採点し、閾値未満のカードを保存させない。
  - 不採用理由: 定性情報の価値を単一尺度へ収束させ、少数意見を抑圧し、AIなしの主要価値を壊す。
- 代替案C: AIが自動的に分割・言い換え・補足する。
  - 不採用理由: 語り手の意図と原文を失い、proposal-onlyと可逆性に反する。
- 代替案D: 文書要件だけを作り、UI支援を行わない。
  - 不採用理由: 方法論を知らない利用者へ品質確保の負担を転嫁する。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 提案が頻繁または評価的で記録を妨げる、誤検知を利用者がエラーと誤解する、出典入力で機密情報が増える。
- 影響範囲: カード作成・編集、SidePanel、i18n、AI支援、SafeMode、共有前確認。
- ロールバック手順: 自動的な提案表示を停止し、本文保存と要求時の自己確認だけを残す。追加データを導入しないため、Phase A/Bは既存文書形式へ破壊的影響なく戻せる。

## 10) Additional context

### ADR化が必要になる条件

`ADR-0047` の再起票基準に従い、次のいずれかが必要になった場合だけADRを起票する。

- 品質確認結果、見送り状態、担当者、期限を永続化する。
- 品質確認を保存、共有、レビュー、承認の必須ゲートにする。
- AIが本文またはメタデータを自動更新する権限を持つ。
- SafeMode、外部Provider、共有物への出典同梱の既定値を変更する。
- 組織横断の品質責任、承認フロー、監査責任を導入する。

現時点では、既存のproposal-only、SafeMode、複雑性予算、UI/UX品質基準の範囲で実装できるため、新規ADRは起票しない。

## 複雑性予算（ADR-0043 自己申告）

初期表示への純増=なし / カード保存までの追加必須操作=0 / 保留までの距離=支援内1操作 / 取り消し導線=提案採用時に必須 / 常設パネル=追加しない。

## Traceability

- Normative: `00_Prompt/qualitative_card_quality_requirements.md`
- Value: `01_Plans/adr/ADR-0001-value-to-requirements.md` P-08
- Domain: `00_Prompt/domain.md` §3.1
- Schema boundary: `02_Architecture/schemas.md` §1.0
- Coverage: `02_Architecture/value_traceability.md` §2 / §2.4
- Derived-from: 2026-07-15 ユーザー要求「KJ法のカードに記述すべき定性情報の品質についてリサーチ・熟考し、その品質確保を要件として取り込む。ユーザ負担を小さくし、人的対応も対応したいと思えるUXにする」
