# ADR-<NNNN>: <短いタイトル>

- Status: Proposed
- Date: YYYY-MM-DD
- Deciders: <Project Maintainers / Team / Individual>
- Scope: `<directory_or_layer>`

## Context

- 何が問題か（現状）
- なぜ今この判断が必要か（背景）
- 比較した主要選択肢（必要なら）

## Decision

- 採用する方針（1文で要約）
- 採用理由（トレードオフを明示）
- 非目標（このADRで扱わない範囲）

## Three-Element Verification（ADR-0067。全ADRで必須）

このADRの判断は以下の三要素整合を満たす。三者が揃わない場合は起票前に補正する。

| 次元 | このADRでの主張 | 他次元への制約 |
|------|----------------|---------------|
| **業務設計** | <誰が・何のために・どの順序で行うか> | <機能・データへの要求> |
| **データ設計** | <何が保存/表示され・何が境界を越えるか> | <業務・機能への制約> |
| **機能設計** | <誰が・どのAPIで・どの状態遷移か> | <業務・データへの制約> |

## Measurement Integrity（昇格判定ADRで必須。案B: DOGFOOD-METRIC-01）

自律性の昇格判定に定量指標を用いたADRは、次の欄を記録する（判定根拠の正確化のため。判定の取消しではない）。

- 使用した指標とその正本（スクリプト/文書/記録）
- 判定期間中に**測定器が変更されたか**: 有無と、その変更内容（正規化・除外・テンプレート変更など）
- **測定器変更に由来する指標変化**と**対象修正に由来する指標変化**の分離（変更がない場合は「なし」と明記）

## Consequences

- 期待される効果
- 想定される副作用/制約
- 移行時に必要な対応（必要なら）

## Traceability

- Related: `<docs/spec/source>`
- Supersedes: `<old ADR path>`（必要時）
- Superseded by: `<new ADR path>`（必要時）
- Derived-from: `<parent ADR path>`（分割時）

---
