# 認知dogfood ナビゲーション索引

- 状態: 保守者・操作者向けの案内文書
- 日付: 2026-08-30
- 対象: PR #2805 における認知dogfood / プロダクト価値検証
- Arm入力: **使用しない** — この文書をCase 001〜003のA/B/C/Dへ渡さない。

## 1. この索引の役割

認知dogfoodに関する文書が増えてきたため、「意思決定の正本」「実行条件」「回顧監査」「実験入力」「実行結果」を混同しないための案内をまとめる。

この索引自体は、新しい判断や実験条件を定義しない。記述が食い違った場合は、次の順序で正本へ戻る。

1. 長期的な設計判断: ADR。
2. 実行課題・受入条件: issue memo。
3. Caseの問い・比較条件: case contract / preregistration / freeze register。
4. 各runで実際に起きたこと: raw artifact / run record / KJ Atlas InquiryJourney。
5. 本文書: 案内のみ。

## 2. 現在地

### P0 — 完了

Case 001〜003について、次を凍結済み。

- 問い。
- product snapshot。
- skill snapshot。
- A/B/C/Dのtreatment。
- required output。

また、次の事前検証も完了している。

- launch treatmentの同値性。
- product manifestと実blobの一致。
- product bundleの再生成。
- canonical skill sourceのblob一致。
- Case 001〜003 × A〜D、計12件の独立したActions artifact生成。

各artifactの境界は次のとおり。

- 全Arm: 同一Caseのproduct evidence + 自Arm専用`launch.md`。
- B/Dのみ: skill bundleを追加。
- C/Dのみ: 空のstarter documentを追加。

### P1 — Case 001 Arm C 実行準備済み / raw run未取得

- 実行順は **C → D → B → A**。
- 現在の設計者チャットは既知の仮説や評価意図を含むため、Arm実行には使用しない。

### P2以降 — 未開始

有効なraw runが得られるまでは、比較結果を作らない。

## 3. 最初に読む文書

### 全体の進め方

- `cognitive-dogfood-execution-plan.md`
  - P0〜P6の順序と各exit gate。
- `cognitive-dogfood-case-portfolio-preregistration.md`
  - Case 001〜003を結果を見る前に選定した理由と、横断的な評価方法。
- `cognitive-dogfood-case-portfolio-freeze.md`
  - 実行入力の凍結状態、pre-run correction、CI検証の記録。

### 評価方法

- `../issues/issue-COGNITIVE-EVAL-01-factorial-human-ai-cognitive-control-evaluation.md`
  - A〜Dの4ArmとM1〜M9。
- `cognitive-dogfood-run-record-template.md`
  - 各runの共通記録様式。
- `cognitive-dogfood-blind-review-protocol.md`
- `cognitive-dogfood-blind-review-template.md`
  - BR1 / BR2 / unblindの進め方。

### KJ Atlasの操作

- `cognitive-dogfood-cd-ui-runbook.md`
  - C/Dで共通して使用するUI操作手順の正本。
- `../issues/issue-DOMAIN-W-ITERATION-01-w-type-cumulative-inquiry-support.md`
  - InquiryJourney Phase 2の手動中核とT9。

## 4. Case 000 — 回顧監査であり、対照実験ではない

- `cognitive-dogfood-case-000-r1-r5-audit.md`
  - R1〜R5を探索的なCase 0として監査した記録。
- `cognitive-dogfood-case-000-outcome-trace.md`
  - 代表論点が、その後のissue / ADR / 実装へどう変換されたかを追跡した記録。
- `doc_kj_atlas_dogfood_r1.json` 〜 `doc_kj_atlas_dogfood_r5.json`
  - 元のdogfood資料。Case 001のArmへ答えとして渡さない。

Case 000から、KJ Atlasの認知的優位性を因果的に主張しない。比較対照、AI proposal ledger、fresh-context条件を持たないためである。

## 5. Case 001 — 存在目的と一次利用仕事

### 問い・入力の正本

- `cognitive-dogfood-case-001-product-purpose.md`
- `cognitive-dogfood-case-001-round1-source-manifest.json`
- `cognitive-dogfood-case-001-skill-manifest.json`
- `cognitive-dogfood-case-001-contamination-exclusions.md`

### Launch packet

- A: `cognitive-dogfood-case-001-launch-ordinary.md`
- B: `cognitive-dogfood-case-001-launch-skill.md`
- C: `cognitive-dogfood-case-001-launch-atlas.md`
- D: `cognitive-dogfood-case-001-launch-atlas-skill.md`

### C/D用starter

- `doc_cognitive_case_001_starter.json`
  - cards / islands / evidenceLinks / readingOrder / narratives を空のまま開始する。

### Round 2

- `cognitive-dogfood-case-001-round2-external-manifest.md`
  - Round 1の結果を見る前に、外部比較資料を事前登録済み。

## 6. Case 002 / 003 — Case 001の結果に依存して選ばない

### Case 002 — AI提案と人間判断の境界

- `cognitive-dogfood-case-002-ai-human-boundary.md`
- `cognitive-dogfood-case-002-round1-source-manifest.json`
- `doc_cognitive_case_002_starter.json`
- `cognitive-dogfood-case-002-launch-*.md`
- Actions artifact: `cognitive-dogfood-case-002-arm-a` 〜 `arm-d`

### Case 003 — local / offline / self-host と collaboration の境界

- `cognitive-dogfood-case-003-local-collaboration-boundary.md`
- `cognitive-dogfood-case-003-round1-source-manifest.json`
- `doc_cognitive_case_003_starter.json`
- `cognitive-dogfood-case-003-launch-*.md`
- Actions artifact: `cognitive-dogfood-case-003-arm-a` 〜 `arm-d`

Case 002/003のartifactを先に生成していても、実行順はCase 001 → 002 → 003を維持する。artifactが準備済みであることは、Caseの前倒し実行を意味しない。

## 7. 実験用ツール

以下はKJ Atlas本体の機能ではなく、比較条件と実験記録を保つためのハーネスである。

- `validate_cognitive_launch_packets.py`
  - 固定問い、required output、treatment差をfail-closedで確認する。
- `prepare_cognitive_frozen_source_bundle.py`
  - product snapshotから、Armへ見せてよいproduct evidenceだけを抽出する。
- `prepare_cognitive_case001_skill_bundle.py`
  - B/Dへ渡すcanonical `src/ja-JP`だけを抽出する。skill snapshotは3Case共通。
- `validate_cognitive_run_records.py`
  - raw runの必須記録と比較可能性を検査する。
- `build_cognitive_blind_package.py`
  - static intakeを通過したrunから、Arm / method情報を外したblind packageを生成する。
- `.github/workflows/cognitive-dogfood-freeze.yml`
  - frozen inputのpreflightと、Case 001〜003のA〜D、計12個の新規コンテキスト用artifact生成を行う。

実験ハーネスの不足を、そのままKJ Atlas製品の機能不足へ読み替えない。

## 8. Findingの振り分け

詳細は`cognitive-dogfood-execution-plan.md`のP4を正本とする。

- F0: run / cardとして保持する。
- F1: 既存issueへ証拠を戻す。
- F2: 既存issueで扱えない、再現可能な実行課題だけを新しいissue memoにする。
- F3: `ADR-0047`の実使用トリガーを満たした場合だけADR候補にする。

特にInquiryJourneyのAI支援候補は、Case 001〜003の少なくとも2つで同型の手動摩擦が再現するまで、T9から先へ進めない。

## 9. 外部現実への接続

内部の認知dogfoodだけでは、第三者にとっての価値を証明できない。

関連する正本は次のとおり。

- `../issues/issue-VALUE-REALNESS-01-third-party-beachhead-validation.md`
- `../issues/issue-PRODUCT-POSITION-01-primary-job-and-switch-reason.md`
- `../issues/issue-PRACTICE-CULTURE-01-cultural-fit-and-product-invariants.md`
- `third-party-value-validation-execution-plan.md`
- `third-party-value-session-record-template.md`
- `third-party-value-publication-boundary.md`
- `third-party-value-analysis-plan.md`

Case 001〜003で得た価値、switch reason、認知増分は、第三者が自分の実資料を持ち込んだときに、支持・修正・縮小・棄却され得る**仮説**として外部検証へ渡す。

## 10. 変更してはならない境界

最初の有効なCase 001 raw runを保存した後は、その結果に合わせて次を変更しない。

- fixed question。
- Round 1 source manifest。
- product / skill snapshot。
- A/B/C/D treatment。
- required output。

実験を継続できない欠陥、破損、重大な安全上・権限上の理由がある場合でも、既存条件を上書きしない。deviationとして履歴を残し、必要なら別revisionとして扱う。