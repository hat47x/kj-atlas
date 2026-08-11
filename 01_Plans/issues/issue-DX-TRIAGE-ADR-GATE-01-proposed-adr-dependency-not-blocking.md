# Issue: DX-TRIAGE-ADR-GATE-01 未採択ADR依存のissueがReadyに誤分類される

- Type: Developer Experience / Governance
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Codex
- Scope: `01_Plans/triage_actionable_plans.py`, `01_Plans/tests/test_triage_actionable_plans.py`
- Related ADR/Spec: `AGENTS.md` §1.3, `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`
- Expected verification level: `unit`

## 課題

issueの`依存関係`にADRを明記しても、triageはissue fileだけを依存解析し、ADR statusを見ていなかった。このため`AI-REL-VOCAB-DRIFT-01`は`ADR-0069: Proposed`の採択を前提とするのにReadyへ分類され、L1 agentが未採択の推奨案を決定済みと誤認しうる状態だった。

## 受入条件

- [x] `依存関係`／`Dependencies`節のbacktick内からADR IDを抽出する。
- [x] 依存ADRが`Accepted`以外なら`ADR-ID:Status`をblockerとしてissueをBlockedへ分類する。
- [x] 依存ADRが存在しなければtriage stopper errorにする。
- [x] ProposedからAcceptedへの遷移で同じissueがBlockedからReadyへ変わるunit testを持つ。
- [x] 実リポジトリの`AI-REL-VOCAB-DRIFT-01`が`ADR-0069:Proposed`でBlockedになる。

## 検証

- `python -m unittest 01_Plans/tests/test_triage_actionable_plans.py -v`
- `python 01_Plans/triage_actionable_plans.py --format json`

## 解決記録（2026-08-11）

issue依存pathとADR依存IDを別々に保持し、Ready判定時に両方を評価するよう変更した。Related ADR/Specの単なる参照はblockerにせず、明示的な依存節だけをgateとして扱うため、参考ADRによる過剰blockingは発生しない。
