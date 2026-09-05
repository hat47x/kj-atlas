# Issue: DOGFOOD-20 AI束ね（suggest-card-groups）が位置ベースで、テーマ類似性による束ねをE2Eで検証できない

- Type: Process / Verification gap（ドッグフーディング観察）
- Status: Done
- Source Issue: ドッグフーディング iteration 185（シナリオ115・コンビニ/FC本部 実装時の実走行観察）。カテゴリ交互配置のカード（c1/c3=オペレーション・c2/c4=商品戦略）で `suggest-card-groups` を実行しても、モックが**位置ベース（前半/後半）**で c1+c2 / c3+c4 をグループ化し、**テーマ類似性（訴えの類似性）による束ね**を E2E で検証できないことを再現確認した。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/deploy/tools/mock_local_llm.py`, `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（シナリオ115）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`
- Related ADR/Spec: `00_Prompt/kj_technique.md` §2（束ねは「訴えの類似性」に基づく）, `00_Prompt/ai_kj_execution_procedures.md` §2, `02_Architecture/api.md`（suggest-card-groups 契約）, `01_Plans/issues/done/issue-DOGFOOD-19-merge-suggestions-lack-deterministic-positive-path.md`（同カテゴリのマージ提案と同型）
- Expected verification level: `e2e`

## 課題

業務フローE2E で `suggest-card-groups`（AI束ね）は**最も多用される操作（89シナリオ）**だが、全シナリオが `"groups"` **キーの存在**だけを確認している。モックはカードを**位置ベース（前半/後半）**で2分割する:

```python
if task == "suggest_card_groups":
    card_ids = _CARD_LINE.findall(prompt)
    if len(card_ids) >= 2:
        mid = len(card_ids) // 2
        return json.dumps({"groups": [
            {"label": "グループA（モック）", "cardIds": card_ids[:mid], ...},
            {"label": "グループB（モック）", "cardIds": card_ids[mid:], ...},
        ]})
    return json.dumps({"groups": []})
```

したがって:

- **束ねが「訴えの類似性」（kj_technique.md §2）に基づくことを E2E で一切検証できない**。位置ベースの分割はテーマと無関係で、同じテーマのカードが別グループに分かれる。
- バックエンドが束ねを位置ベース/無意味に劣化させる回帰が起きても、業務フローE2E は全部 pass する。
- カテゴリ交互配置（c1/c3=オペレーション・c2/c4=商品戦略）の場合、位置分割は c1+c2 / c3+c4 という**誤グループ化**を返す。

実機再現（iteration 185）:

```text
# c1/c3=オペレーション・c2/c4=商品戦略 を束ねる
# → 位置分割: c1+c2（オペ+商品の誤結合） / c3+c4
```

### なぜ問題か

- **束ねの意味（テーマ類似性）が未検証**: 束ねはKJ法の核となる操作（島形成の前段）であり、その「同テーマのカードをまとめる」性質が検証されない。
- **最も多用される操作の検証深度が最低**: 89シナリオすべてがキー存在のみで、実質的な検証になっていない。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者は**同じテーマ（訴え）のカードが同じグループにまとまる**束ねを期待する。束ねは島形成・表札作成の前提 | 束ねは **proposal（read-only）** のまま。カードの移動・統合は自動適用しない |
| **データ設計** | 束ねプロンプトは `- id="<id>", text="<text>"` のカード行を含むため、モックは**カード本文の（カテゴリ）**を抽出して「同テーマのカードを同じグループ」にできる（DOGFOOD-19 のマージ提案と同型） | 既存の `"groups"` キー assert は、グループ構成が変わっても成立（非後退）。カテゴリ1種以下は位置分割へフォールバックして既存挙動を維持 |
| **機能設計** | `suggest_card_groups` を「2つ以上の（カテゴリ）がある場合、カテゴリ別にグループ化」へ変更し、シナリオ115の束ねチェックで**同テーマ（c1/c3・c2/c4）が同じグループ**になることを assert する。API契約（`SuggestCardGroupsResponse`）は不変 | バックエンド実装・API契約は変更しない。既存シナリオは `"groups"` キー assert のため非後退 |

## 対応方針

- 実施すること:
  1. `mock_local_llm.py` の `suggest_card_groups` で、**2つ以上の（カテゴリ）がある場合はカテゴリ別にグループ化**する（カテゴリ1種以下・カテゴリなしは従来の位置分割へフォールバック）。
  2. シナリオ115（コンビニ・FC本部）のカードを**カテゴリ交互配置**（オペレーション/商品戦略）で設計し、束ねチェックで**同テーマ（c1/c3・c2/c4）が同じグループ**になることを assert する。
- 実施しないこと:
  - suggest-card-groups の**バックエンド実装・API契約の変更**。
  - 既存シナリオ（1〜114）の束ねアサーションの変更（`"groups"` キー assert・非後退）。

## 受入条件

- [x] カテゴリ交互配置（c1/c3=オペレーション・c2/c4=商品戦略）で、c1/c3 と c2/c4 がそれぞれ同じグループになる（実走行で確認）。
- [x] カテゴリ1種以下/カテゴリなしのカード群は従来どおり位置分割（2グループ）を返す（非後退・実走行で確認）。
- [x] シナリオ115の束ねチェックが同テーマ（c1/c3・c2/c4）の同グループを assert し、業務フローE2E が **685/685 pass**。
- [x] `verify_dogfood_records.sh`・`docs_check.py` が pass。

## 検証計画

- `cd 03_Implement/backend && bash scripts/verify_business_flow_e2e.sh <PORT>` → 685/685（シナリオ115の CV ②束ねが同テーマの同グループ化）
- `bash 01_Plans/dogfood/verify_dogfood_records.sh` → 構造照合 pass
- `python 01_Plans/docs_check.py` → docs-check passed

## 補足

- モックのカテゴリ一致は「束ねがテーマ類似性に基づく」ことを検証可能にする決定性表現であり、実LLMの束ね品質とは独立（本issueは検証ハーネスの能力向上）。DOGFOOD-19（マージ提案）と同型の設計。
- ドッグフーディング観察起点（2026-08-16・iteration 185）: コンビニ本部（オペレーション/商品戦略の交互配置）で AI束ね を実行し、位置分割が誤グループ化（c1+c2）を返すことを再現。束ねのテーマ類似性がE2Eで検証不能であることを特定した。


## 配置の整理（2026-09-05）

- 本Issueは、KJのテーマ類似性をE2Eで決定的に検証できるようモック／業務フロー検証を強化し、製品API契約を変えずに `Done` となっていた。
- `DOGFOOD-19` と `DOGFOOD-20` は、同カテゴリの統合候補からテーマ類似性による束ねへ同型の検証設計を継承する小さな連結成分として扱い、2件を同時に `01_Plans/issues/done/` へ移した。
- `LEGACY_DONE_AT_ROOT_BASELINE` は33から31へ縮小し、R18 identity manifestは不変の歴史境界として維持する。
- 旧rootパス引用は現在の `done/` パスへ同時更新した。
