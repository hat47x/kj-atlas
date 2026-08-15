# Issue Draft: AI-OPPOSE-01 反対視点・根拠不足のproposal-only提案

- Type: Feature request / AI capability
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `00_Prompt/ai_cognitive_externalization_requirements.md`（M4）, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/domain/`
- Related ADR/Spec: `00_Prompt/ai_cognitive_externalization_requirements.md` §M4, `02_Architecture/value_traceability.md` §2.1（V1/V3）, `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`
- Expected verification level: `e2e`

## 課題

`00_Prompt/ai_cognitive_externalization_requirements.md` §M4 は「contradiction / evidence 構造をもとに、未検討論点や根拠不足箇所を提案」するAI能力を要件として定義しているが、これを実装する専用issueが存在しない。`CE2-low-risk-ai-assist` は proposal-only 基盤を完了したが、M4固有の「反対視点の提案」「根拠不足の仮説抽出」は未分割のままである。

この能力は `value_traceability.md` V1（外在化）と V3（レビュー）の価値、すなわち「保留・違和感・根拠不足を作業状態として残し、AIが人間の判断を先取りしない」ことを直接強化する。プロダクト価値実現の高価値要件であり、単独issueとして要件・境界・検証を固定する必要がある。

## 要件

- AIは contradiction / evidence 構造をもとに、未検討論点と根拠不足箇所を候補として提案する。
- 提案は proposal-only で、`human_reviewed` を自動昇格しない（`value_traceability.md` §2.5 共通不変条件）。
- 根拠不足として保留する提案は、既存の hold / 保留 状態へ非破壊に接続する。
- 提案が島タイトル等の確定フィールドに触れる場合は、書き直し案を示すだけで確定しない（`qualitative_card_quality_requirements.md` §5）。
- `KJ_ATLAS_LLM_PROVIDER=none` でも中核操作（保留・矛盾の記録）が成立する。

## 受入条件

- [ ] 反対視点・根拠不足の提案が、contradiction / evidence 構造から生成され、proposal-onlyで表示される。
- [ ] 提案は `human_reviewed` を自動昇格しない（非後退）。
- [ ] 根拠不足の提案を保留へ接続でき、元の違和感・矛盾に戻れる。
- [ ] 提案が確定フィールドへ自動適用されない（書き直し案のみ）。
- [ ] `provider=none` で中核操作（記録・保留・参照）が成立する。
- [ ] E2Eでマウス・キーボード・390pxで操作できる。

## 検証計画

- `cd 03_Implement/frontend && npx vitest run`（proposal-only境界の回帰）
- Playwright E2E（提案表示・採用・保留・非適用）
- `python 01_Plans/docs_check.py`

## 補足

- 本issueは要件固定を目的とし、実装は `CE2` の基盤を再利用する。
- AI有効時のみ提案し、無効時は中核操作を変更しない（`ADR-0040` 段階開示）。

## 具体スコープ（2026-08-15・計画起票）

### 既存インフラのマッピング

| M4 要件 | 既存資産 | ギャップ |
|---------|---------|---------|
| contradiction 構造からの提案 | `detect-contradiction`（AIルート・`_reject_unreviewed_cards` 適用済み）・`contradictionSignalDecisions`（domain） | **proposal-only の UI 表面が無い**（判定は表示されるが「反対視点の候補」として提案されない） |
| evidence 構造からの根拠不足 | `evidenceLinks`（domain types・文書スキーマ） | 根拠不足の**仮説抽出**（証拠の無いカードを候補化）は未実装 |
| proposal-only・非自動適用 | CE2 proposal 基盤・`human_reviewed` 不変条件（value_traceability §2.5） | 反対視点を proposal として取り込む経路が無い |
| hold/保留への非破壊接続 | hold / 保留状態（DOMAIN-EXPR-02） | 根拠不足の提案を保留へ接続する導線が無い |

### 実装の積み順（提案・仮承認）

1. **R1（backend）**: `POST /ai/proposals/opposing-viewpoint`（新規）— contradiction / evidenceLinks 構造から反対視点・根拠不足を提案（proposal-only・CE2 envelop 再利用・`_assert_model_allowed` 適用）。detect-contradiction は判定のみ・本ルートは**提案**を担う。
2. **R2（frontend）**: contradiction 判定結果を「反対視点の候補」として proposal 表面に表示（proposal-only・採否のみ・自動適用なし）。根拠不足カードを hold/保留へ接続する導線。
3. **検証**: `test_ai_oppose.py`（backend・提案スキーマ・proposal-only 境界）＋ E2E（提案表示・採否・保留接続・非適用）。

### 判断保留

- 反対視点の自動トリガー（判定→自動提案）はしない（人間が「反対視点を提案」を明示操作したときのみ）。
- 根拠不足の判定はエビデンス重み付けを導入しない（反スコアリング不変条件・既存の evidenceLinks の有無のみで候補化）。
