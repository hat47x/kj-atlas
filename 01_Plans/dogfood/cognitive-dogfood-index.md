# Cognitive Dogfood Navigation Index

- Status: Maintainer/operator navigation only
- Date: 2026-09-02
- Scope: cognitive dogfood / product-value validation workstream
- Arm input: **No** — この文書をCase 001〜003のA/B/C/Dへ渡さない。

## 1. この索引の役割

認知dogfood関連文書が増えたため、「意思決定の正本」「実行条件」「回顧監査」「実験入力」「実行結果」を混同しないための導線だけを提供する。

この文書自体は新しい判断を定義しない。矛盾した場合は、次の優先順位で正本へ戻る。

1. 長期判断: ADR。
2. 実行課題・受入条件: issue memo。
3. ケース問い・比較条件: case contract / pre-registration / freeze register。
4. 各runの事実: raw artifact / run record / KJ Atlas InquiryJourney。
5. 本索引: navigation only。

## 2. 現在地

- P0: **完了**。
  - Cases 001〜003の問い、product snapshot、skill snapshot、4arm treatment、required outputを凍結済み。
  - launch treatment equivalence、product manifest/blob、product bundle再生成、skill canonical sourceのblob一致を検証済み。
  - Cases 001〜003のA〜Dを、各arm単独のfresh-session用Actions artifactとして12件すべて生成できる状態。
  - artifact境界は、全arm=同一case product evidence、B/Dのみ=skill、C/Dのみ=empty starter、各artifact=自armのlaunch.mdのみ。
- P1: **Case 001 Arm C ready / raw run未取得**。
  - 実行順は C → D → B → A。
  - 現在の設計者チャットは既知仮説を含むためarmとして使わない。
- P2以降: 未開始。
- 第三者価値実証: **protocol準備済み / 実session未実施**。
  - `VALUE-REALNESS-01` はP0かつOpenのまま。
  - 実行計画、参加者向け説明、開始前checklist、session記録、公開境界、事前分析計画、validator、専用workflowは準備済み。
  - 現在残る主要な外部入力は、第三者協力者または同等の外部評価機会と、その文脈で扱える資料である。
  - protocol準備済みであることを、価値実証完了とみなさない。

## 3. 最初に読む文書

### 全体の順序

- `cognitive-dogfood-execution-plan.md`
  - P0〜P6の順序とexit gate。
- `cognitive-dogfood-case-portfolio-preregistration.md`
  - Case 001〜003を結果を見る前に選んだ理由と横断評価。
- `cognitive-dogfood-case-portfolio-freeze.md`
  - 実行入力の凍結状態、pre-run correction、CI検証証拠。

### 評価方法

- `../issues/issue-COGNITIVE-EVAL-01-factorial-human-ai-cognitive-control-evaluation.md`
  - A〜Dの4armとM1〜M9。
- `cognitive-dogfood-run-record-template.md`
  - runごとの共通記録。
- `cognitive-dogfood-blind-review-protocol.md`
- `cognitive-dogfood-blind-review-template.md`
  - BR1 / BR2 / unblindの順序。

### KJ Atlas操作

- `cognitive-dogfood-cd-ui-runbook.md`
  - C/Dの共通UI操作正本。
- `../issues/issue-DOMAIN-W-ITERATION-01-w-type-cumulative-inquiry-support.md`
  - InquiryJourney Phase 2手動中核とT9。

## 4. Case 000 — 回顧監査であり対照実験ではない

- `cognitive-dogfood-case-000-r1-r5-audit.md`
  - R1〜R5を探索的Case 0として監査。
- `cognitive-dogfood-case-000-outcome-trace.md`
  - 代表論点が後続issue/ADR/実装へどう変換されたかの下流追跡。
- `doc_kj_atlas_dogfood_r1.json` 〜 `doc_kj_atlas_dogfood_r5.json`
  - 元資料。Case 001 armの答えとしては使わない。

Case 000から認知的優位性の因果主張をしない。比較対照、AI proposal ledger、fresh-context条件を持たないためである。

### 継続dogfood — 日常開発の自己分析

Case 001〜003の統制比較とは別に、既知の設計判断を含む日常開発の自己分析を継続dogfoodとして扱う。これらもarm inputにはしない。

- `cognitive-dogfood-continuous-2026-09-02-r2.md`
  - R8。最初の10分と一次利用仕事のずれを分析し、public pack、getting started、同期テストへ戻した記録。
- `doc_kj_atlas_dogfood_r8.json`
  - R8のKJキャンバス。
- `cognitive-dogfood-continuous-2026-09-02-r3.md`
  - R9。第三者価値実証が何を待っているのかを分析し、protocol準備済みと外部session未実施を分離した記録。
- `doc_kj_atlas_dogfood_r9.json`
  - R9のKJキャンバス。

継続dogfoodで得た内部所見を、Case 001〜003の比較結果や第三者価値実証の代替証拠として扱わない。

## 5. Case 001 — 存在目的と一次利用仕事

### 問い・入力正本

- `cognitive-dogfood-case-001-product-purpose.md`
- `cognitive-dogfood-case-001-round1-source-manifest.json`
- `cognitive-dogfood-case-001-skill-manifest.json`
- `cognitive-dogfood-case-001-contamination-exclusions.md`

### Launch packets

- A: `cognitive-dogfood-case-001-launch-ordinary.md`
- B: `cognitive-dogfood-case-001-launch-skill.md`
- C: `cognitive-dogfood-case-001-launch-atlas.md`
- D: `cognitive-dogfood-case-001-launch-atlas-skill.md`

### C/D starter

- `doc_cognitive_case_001_starter.json`
  - cards / islands / evidenceLinks / readingOrder / narratives は空のまま開始する。

### Round 2

- `cognitive-dogfood-case-001-round2-external-manifest.md`
  - Round 1結果を見る前に外部比較資料を事前登録済み。

## 6. Case 002 / 003 — Case 001結果に依存して選ばない

### Case 002: AI提案と人間判断の境界

- `cognitive-dogfood-case-002-ai-human-boundary.md`
- `cognitive-dogfood-case-002-round1-source-manifest.json`
- `doc_cognitive_case_002_starter.json`
- `cognitive-dogfood-case-002-launch-*.md`
- Actions artifact: `cognitive-dogfood-case-002-arm-a` 〜 `arm-d`

### Case 003: local/offline/self-hostとcollaborationの境界

- `cognitive-dogfood-case-003-local-collaboration-boundary.md`
- `cognitive-dogfood-case-003-round1-source-manifest.json`
- `doc_cognitive_case_003_starter.json`
- `cognitive-dogfood-case-003-launch-*.md`
- Actions artifact: `cognitive-dogfood-case-003-arm-a` 〜 `arm-d`

Case 002/003のartifactを先に生成していても、実行順はCase 001→002→003を維持する。artifact準備済みであることは前倒し実行を意味しない。

## 7. Experiment tooling

次はKJ Atlas本体機能ではなく、比較条件を保つための実験ハーネスである。

- `validate_cognitive_launch_packets.py`
  - fixed question / required output / treatment差をfail-closedで確認。
- `prepare_cognitive_frozen_source_bundle.py`
  - product snapshotからarm-visible product evidenceだけを抽出。
- `prepare_cognitive_case001_skill_bundle.py`
  - B/D用canonical `src/ja-JP`だけを抽出。skill snapshotは3ケース共通。
- `validate_cognitive_run_records.py`
  - raw runの必須記録を検査。
- `build_cognitive_blind_package.py`
  - arm/method情報を外したblind packageを生成。
- `.github/workflows/cognitive-dogfood-freeze.yml`
  - frozen input preflightとCases 001〜003のA〜D、計12個のfresh-session artifact生成。

experiment toolingの不足を、直ちにKJ Atlas製品の機能不足へ読み替えない。

## 8. Finding triage

詳細は `cognitive-dogfood-execution-plan.md` P4を正本とする。

- F0: run/cardとして保持。
- F1: 既存issueへ証拠を戻す。
- F2: 既存issueで被覆できない再現可能な実行課題だけ新issue memo化。
- F3: `ADR-0047` の実使用トリガーを満たす場合だけADR候補化。

特にInquiryJourneyのAI支援候補は、Case 001〜003の少なくとも2ケースで同型の手動摩擦が再現するまでT9から先へ進めない。

## 9. 外部現実への接続

internal cognitive dogfoodは第三者価値の証明ではない。

正本は次である。

- `../issues/issue-VALUE-REALNESS-01-third-party-beachhead-validation.md`
- `../issues/issue-PRODUCT-POSITION-01-primary-job-and-switch-reason.md`
- `../issues/issue-PRACTICE-CULTURE-01-cultural-fit-and-product-invariants.md`

第三者sessionを開始するときは、`VALUE-REALNESS-01` の「現在の実行準備状態」「現在残っている外部入力」「session開始時の入口」から次へ進む。

- `third-party-value-validation-execution-plan.md`
- `third-party-value-participant-brief.md`
- `third-party-value-session-launch-checklist.md`
- `third-party-value-session-record-template.md`
- `third-party-value-publication-boundary.md`
- `third-party-value-analysis-plan.md`
- `validate_third_party_value_protocol.py`
- `.github/workflows/third-party-value-protocol.yml`

Case 001〜003で得た価値・switch reason・認知増分は、第三者が自分の実資料を持ち込んだときに支持/修正/縮小/棄却される**仮説**として渡す。

protocol一式が準備済みでも、第三者sessionが未実施なら `VALUE-REALNESS-01` は完了しない。協力者がいない段階で新しいKPI、telemetry、重複protocolを増やして実証の代わりにしない。

## 10. 変更境界

最初のvalid Case 001 raw run保存後は、結果に合わせて次を変更しない。

- fixed question。
- Round 1 source manifest。
- product / skill snapshot。
- A/B/C/D treatment。
- required output。

実験不能な欠陥、破損、重大な安全/権限理由がある場合は旧条件を上書きせず、deviationとして履歴を残す。
