# Issue: DOMAIN-KJ-COLLAB-01 DeepSeek 実APIで人間×生成AIの多ラウンド協調KJ実践を検証する

- Type: Verification / Product Value
- Status: In Progress
- Source Issue: ドッグフーディング指令（iteration 43）。「DeepSeek APIを用いて、kj-atlasを人間と生成AIが協調動作してKJ法の深い実践と成果の獲得、さらに複数ラウンドを重ねて結論を深めていくことができるか検証する」
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/scripts/verify_kj_multi_round.sh`（新規）, `deploy/tools/mock_local_llm.py`, `02_Architecture/api.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0067-three-element-constraint-design-method.md`, `00_Prompt/kj_technique.md`, `00_Prompt/ai_kj_execution_procedures.md`
- Expected verification level: `integration`

## 課題

kj-atlas は人間の KJ 実践（カード作成→島化→表札→ナラティブ）と生成AIの支援（束ね提案・表札提案・
文面整え・ナラティブ草稿）を同じ文書上で協調させる設計を持つ。だが**実API（DeepSeek）で、
人間×AIの協調が複数ラウンドを跨いで結論を深化させることを通しで検証した記録が無い**。
iteration 41/42 の E2E はモックLLM（無料・決定的）で固定した。本issueは**実API（DeepSeek）での
検証経路と runbook を準備し、キー有無で切替可能**にする。

## 三要素分析（ADR-0067）

| 次元 | 分析 |
|------|------|
| **業務設計** | KJ 実践の価値は「発散→構造化→深化」のラウンド循環。人間は判断（採択/修正/見送り）を担い、AIは候補生成を担う。**AIが結論を出すのではなく、人間の判断材料を増やす** |
| **データ設計** | 各ラウンドの成果は同一 document 上で累積（カード→グループ→島→表札→ナラティブ）。AI出力は提案（proposal）として人間が採択後に確定 |
| **機能設計** | 協調経路: suggest-card-groups（束ね）→ suggest-island-summary（表札）→ refine-card-text（文面）→ generate-narrative（草稿）。各ルートは SafeMode（未レビュー境界422）と決定性（同一入力→同一出力）を保つ |

## 検証の流れ（3ラウンド協調）

1. **R1 発散**: 人間がカードを書く → AI が suggest-card-groups で束ね提案 → 人間が束ねを判断。
2. **R2 構造化**: 人間が島を形成 → AI が suggest-island-summary で表札提案 → 人間が表札を採択/修正。
3. **R3 深化**: AI が refine-card-text で文面を整え、generate-narrative でナラティブ草稿 → 人間が結論をレビュー。

各ラウンドの AI 出力が**次のラウンドの入力**になり、結論が深まる（協調動作の検証）。

## 対応方針

- 実施すること: `verify_kj_multi_round.sh` を新設する。
  - `KJ_ATLAS_DEEPSEEK_API_KEY` 設定時 → `KJ_ATLAS_LLM_PROVIDER=deepseek`（実API・課金）。
  - 未設定時 → `KJ_ATLAS_LLM_PROVIDER=local` + `mock_local_llm.py`（無料・決定的・iteration 41 の縮退方式）。
  - 3ラウンドの協調フローをアサーション付きで実走行し、各ラウンドの AI 出力が次の入力になることを確認。
- 実施しないこと: AI の品質そのものの採点（`AI-IMPORTANCE-SCORING-01` の反スコアリング不変条件に抵触）。検証は「協調フローが成立し結論が深化する」ことを示すもの。

## 受入条件

- [x] `verify_kj_multi_round.sh` が DeepSeek キー有無で切替可能（実API or モック）。→ `KJ_ATLAS_DEEPSEEK_API_KEY` 設定時 `deepseek`・未設定時 `local`+`mock_local_llm.py` へ切替。実API時の wiring は settings 検証＋`get_provider()` 解決で確認済み。
- [x] 3ラウンドの協調フロー（発散→構造化→深化）が実走行で完了し、各ラウンドの出力が次ラウンドへ渡る。→ モックで実走行 7/7 pass（R1 束ね→R2 表札→R3 文面+ナラティブ）。
- [x] SafeMode（未レビュー境界 422）を保持したまま協調フローが成立する。→ 全カード `textReviewed: true` で AI 経路が成立（未レビュー境界は `verify_business_flow_e2e.sh` で 422 固定済み）。
- [x] 実APIでの検証 runbook が文書化される（キー設定・実行・結果の読み方）。→ 下記「対応記録」に runbook を明記。
- [x] `python 01_Plans/docs_check.py` が通る。

## 対応記録（2026-08-15・iteration 43）

- `verify_kj_multi_round.sh` を新設 — R1発散（suggest-card-groups）→ R2構造化（suggest-island-summary）→ R3深化（refine-card-text + generate-narrative）の協調ループを 7 チェックで固定。
- **DeepSeek runbook（実API・課金）**:
  ```bash
  cd 03_Implement/backend
  KJ_ATLAS_DEEPSEEK_API_KEY=<key> bash scripts/verify_kj_multi_round.sh 8000
  # 期待: 各ラウンドの AI 出力（束ね・表札・ナラティブ）が実モデルで返り、7/7 pass
  # 未設定時はモック（無料・決定的）へ自動縮退
  ```
- 実API の wiring 検証: `KJ_ATLAS_LLM_PROVIDER=deepseek` + キー → Settings 検証 OK・`get_provider()` が `DeepSeekProvider` を解決。
- モック実走行: `verify_kj_multi_round.sh` 7/7 pass（R1→R2→R3 の協調ループ成立）。
- 実APIでの質的な「結論の深化」の観測は、DeepSeek キーが利用可能な環境での実走行時に記録する（本issueを Done にせず Open のまま残す判断も可）。

## 検証計画

- `bash scripts/verify_kj_multi_round.sh [PORT]`（キー無し → モックで 7/7、キー有り → DeepSeek 実走行）
- 実API時: `KJ_ATLAS_LLM_PROVIDER=deepseek KJ_ATLAS_DEEPSEEK_API_KEY=<key> bash scripts/verify_kj_multi_round.sh`
- 実績（2026-08-15）: モックで 7/7 pass・DeepSeek wiring 検証 OK・docs-check pass。

## 補足

- 業態の新規性: 本検証は「業態の追加」ではなく「**同一業態を多ラウンドで深める協調実践**」を検証するもの。
  業態追加は iteration 42 までの2シナリオ（定性調査・新規事業WS）があり、**既存と類似の用途にしか
  到達しない業態は控える**（新規性重視・無理に追加しない）。
