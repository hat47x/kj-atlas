# Issue: DOGFOOD-30 配置提案（suggest-layout）が島・読み順を保持することをE2Eで検証できない

- Type: Process / Verification gap（ドッグフーディング観察）
- Status: Done
- Source Issue: ドッグフーディング iteration 194（シナリオ124・フラワーショップ 実装時の実走行観察）。`suggest-layout` のE2Eアサーションは DOGFOOD-23 以降**全カード保持**のみを確認し、**配置提案が島・読み順も保持しているか**を検証していない。実走行では `suggestedDoc` が島（flr-gift/flr-ops）・読み順（`["flr-gift","flr-ops"]`）を保持していたが、E2Eはそれを検証しない。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（シナリオ124）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`
- Related ADR/Spec: `00_Prompt/kj_technique.md` §3（島形成・空間配置）, `02_Architecture/api.md`（suggest-layout 契約・suggestedDoc）, `01_Plans/issues/done/issue-DOGFOOD-23-layout-card-preservation-unverified.md`（全カード保持）, `01_Plans/issues/done/issue-DOGFOOD-21-narrative-text-not-grounded-in-reading-order.md`（読み順）
- Expected verification level: `e2e`

## 課題

業務フローE2E の `suggest-layout`（配置提案）は DOGFOOD-23 で**全カード保持**を固定したが、**島・読み順の保持**は検証していない。既存の layout シナリオ（11/50/60系・118）のアサーションは `"transform"`+`"cards"`（または全カードID）だけを確認し、**配置提案が島構成・読み順を失わないか**は assert しない:

```bash
case "$dp_layout" in *'"suggestedDoc"'*'d1'*'d2'*'d3'*'d4'*)  # 全カードのみ
```

したがって:

- **配置提案が島を落とす/読み順を変える回帰**が起きても、業務フローE2E は全部 pass する。
- 配置（レイアウト）は島形成の前段として**島・読み順を保持**しながら空間へ置くことが重要（kj_technique.md §3）。その保全が未検証。

実機再現（iteration 194）:

```text
# suggest-layout の応答: suggestedDoc が islands=["flr-gift","flr-ops"]・readingOrder=["flr-gift","flr-ops"] を保持
# → 既存E2Eは全カードIDのみを検証し、島・読み順を確認しない
```

### なぜ問題か

- **配置の構造保全（島・読み順）が未検証**: 配置提案が島を落とすと、その後のナラティブ（読み順に沿う）の前提が崩れる。
- **検証深度の偏り**: 全カード保持（DOGFOOD-23）は固定されたが、島・読み順の保持は未固定。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者は**島・読み順を保持したまま**全カードを空間へ配置する提案を得たい。配置で島が落ちると分析構造が壊れる | 配置は **proposal 相当（read-only の提案）** のまま。自動適用しない |
| **データ設計** | 配置応答の `suggestedDoc` は島・読み順を含む完全な文書を返すため、**島ID・読み順が保持されている**ことを検証できる | 既存の `"suggestedDoc"`+カードID assert は、島・読み順のassertを追加しても成立（非後退） |
| **機能設計** | シナリオ124の配置チェックで **`suggestedDoc` かつ `islands` かつ `readingOrder`（島ID保持）** を assert する。API契約（`SuggestLayoutResponse`）は不変 | バックエンド実装・API契約は変更しない（既に島・読み順を保持）。モック変更不要 |

## 対応方針

- 実施すること:
  1. シナリオ124（フラワーショップ・2島 flr-gift/flr-ops）に **suggest-layout（配置提案）** を操作内容へ追加し、配置チェックで **`suggestedDoc` かつ `islands` かつ `readingOrder`（島ID保持）** を assert する（配置の構造保全を固定）。
- 実施しないこと:
  - suggest-layout の**バックエンド実装・API契約・モックの変更**（既に島・読み順を保持）。
  - 既存シナリオ（11/50/60系・118）のアサーションの変更（非後退）。

## 受入条件

- [x] シナリオ124の配置チェックが `suggestedDoc` かつ `islands` かつ `readingOrder:["flr-gift","flr-ops"]` を assert（実走行で確認）。
- [x] 既存シナリオ（118・全カード保持 assert）は非後退。
- [x] 業務フローE2E が **748/748 pass**（並行編集によるMGシナリオの干渉がない場合）。
- [x] `verify_dogfood_records.sh`・`docs_check.py` が pass。

## 検証計画

- `cd 03_Implement/backend && bash scripts/verify_business_flow_e2e.sh <PORT>` → 748/748（シナリオ124の FL ⑤配置提案が島・読み順を保持）
- `bash 01_Plans/dogfood/verify_dogfood_records.sh` → 構造照合 pass
- `python 01_Plans/docs_check.py` → docs-check passed

## 補足

- 配置の構造保全（島・読み順）は、バックエンドが既に `suggestedDoc` で完全な文書を返すためモック変更は不要。本issueは**検証深度の向上**（DOGFOOD-23 の全カード保持に加え、島・読み順の保持を固定）。
- ドッグフーディング観察起点（2026-08-16・iteration 194）: フラワーショップ（2島 flr-gift/flr-ops）で suggest-layout を実行し、`suggestedDoc` が島・読み順を保持している一方、業務フローE2E が全カードIDのみを検証して島・読み順を確認しないことを特定した。


## 配置の整理（2026-09-05）

- 本Issueは、reading order を単なるID宣言ではなく、生成本文または配置提案の構造として実際に保持・反映することをE2Eで固定した verification harness 改善として `Done` となっていた。
- `DOGFOOD-21` はナラティブ本文の読み順接地、`DOGFOOD-30` は layout 提案の島・readingOrder構造保全を固定しており、reading-order invariant の意味側と構造側をなす小さなまとまりとして同時に正規配置へ移した。
- `LEGACY_DONE_AT_ROOT_BASELINE` は27から25へ縮小し、R18 identity manifestは不変の歴史境界として維持する。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
