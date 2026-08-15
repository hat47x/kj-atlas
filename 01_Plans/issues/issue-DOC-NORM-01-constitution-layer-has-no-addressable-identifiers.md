# Issue: DOC-NORM-01 憲法層の不変条件に識別子が無く、計画から参照・検証・追跡ができない

- Type: Documentation quality
- Status: In Progress
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer
- Scope: `00_Prompt/domain.md`, `00_Prompt/kj_technique.md`, `00_Prompt/ai_kj_execution_procedures.md`, `00_Prompt/qualitative_card_quality_requirements.md`, `00_Prompt/representative_visual_cue_requirements.md`, `01_Plans/docs_contract_checks.py`, `01_Plans/docs_check.py`
- Related ADR/Spec: `01_Plans/00-prompt-improvement-program-2026-08-15.md`（本issueの根拠。P1〜P3に対応）, `00_Prompt/cognitive_frame_and_evolution_criteria.md`
- Expected verification level: `docs-check`

## 課題

### 事実1: 最も参照される憲法文書に識別子が1つも無い

`01_Plans/` と `02_Architecture/` から `00_Prompt/domain.md` への参照は **64件**ある。しかしそのうち約50件は**ファイル名だけの裸参照**で、節も識別子も指していない。

`domain.md` が定める不変条件——保留、違和感（説明責任を伴わない）、可逆性、AIの禁止事項10項目——は、**すべて散文の中にあり、指し示す手段がない。**

| 文書 | 識別子の数 | Status |
|---|---|---|
| `w_type_iterative_inquiry_requirements.md` | WIR-01〜09 | Normative |
| `ai_cognitive_externalization_requirements.md` | 7（部分的） | なし |
| `representative_visual_cue_requirements.md` | 5（部分的） | なし |
| `qualitative_card_quality_requirements.md` | 4（部分的） | Normative |
| **`domain.md`** | **0** | **なし** |
| **`kj_technique.md`** | **0** | Normative |
| **`ai_kj_execution_procedures.md`** | **0** | Normative |

### 事実2: 行番号参照が発生している

識別子が無いため、憲法層のファイルを行番号で指す参照が複数存在する。行番号は編集で腐るため、**無いより悪い参照**である。

**これは仮定ではない。** 本issueの作業で `domain.md` へ識別子を追記した時点で既存の行番号参照はすべてずれ、
引用している文と指し先が食い違う状態になった。`DC-NORM-003` はこの失敗様態そのものを禁じる。

### 事実3: 接続の失敗が実際に表面化した

`01_Plans/product-trajectory-research-2026-08-15.md` は不変条件を参照する必要が生じたとき、**`I1`〜`I5` という識別子をその場で発明せざるを得なかった**。文書内でのみ有効な一時的な識別子であり、他から参照できない。

### 事実4: 憲法層固有の検証が存在しない

`docs_contract_checks.py` は `00_Prompt` をパス集合に含むが、適用されるのは汎用規則（リンク解決等）のみである。**Status の語彙統制も、識別子の一意性検証も、参照の解決検証も無い。**

対照的に、ADR には `DC-ADR-001`（番号重複検出）があり、issue memo には `issue_memo_status.py` による Status 統制と `validate_active_issue_memos.py` による検証がある。**憲法層だけが無統制である。**

### 帰結

> **憲法層は「読まれる」ようには作られているが、「参照され、検証され、追跡される」ようには作られていない。**

具体的な損失は3つある。

1. **不変条件を変更したとき、何が壊れるか分からない。** どの計画がどの不変条件に依拠しているかを機械的に辿れない。
2. **計画が不変条件に違反していても検出されない。**
3. **未実装の規範を一覧化できない。** `kj_technique.md` §6 の失敗の徴候12項目のうち機械化されているのは1項目だけだが、識別子が無いためこの事実を計画側から追跡できない。

`DOMAIN-SCORING-SURFACE-01`（画面に「健全性 N%」が出荷されていた件）はこの帰結の実例である。`domain.md` と `ui_design_handoff.md` が採点を禁じているのに、**禁止と実装を突き合わせる経路が無かった**ため長期間気づかれなかった。

これは `direction-review-2026-08-13.md` §2 が全層で観測した構造——**主張した保護範囲 > 実際の保護範囲**——の憲法層での現れである。

## 対応方針

`00-prompt-improvement-program-2026-08-15.md` の P1〜P3 を実施する。

- **実施すること**:
  1. **P1**: `domain.md` の §2（基本思想3概念）と §7（AIの禁止事項）へ安定識別子を付す。`DOM-` 接頭辞、`WIR-01` 形式に倣う。AIの禁止事項は**1項目1ID**とする。
  2. **P2**: `kj_technique.md`（`KJT-`。特に §3 表札検査・§4 空白の列挙・§5 A/B照合・§6 失敗の徴候12項目）、`ai_kj_execution_procedures.md`（`AKP-`）へ拡張し、部分的にしか持たない3文書の体系を揃える。
  3. **P3**: `docs_check` へ憲法層固有の規則を追加する。(a) Status 語彙の統制（`Normative / Informative / On-demand / Superseded`）、(b) 識別子の一意性、(c) **他層からの識別子参照が実在することの検証**、(d) 行番号参照の禁止。
- **実施しないこと**:
  1. **既存の散文の書き換え。** 識別子の付与に限る。`domain.md` §9 は実装都合での変更を禁じており、本作業は**意味を変えない操作**として実施する。意味の変更が必要と判明した場合は本issueを止め、別途ADRを起こす。
  2. ディレクトリ分割（参照64件超が壊れ、利得に見合わない）
  3. 計画側テンプレートへの `Norms:` 欄の追加（P6。本issue完了後）

## 論点（保守者判断が必要な理由）

- **識別子の粒度。** `domain.md` §7 のAI禁止事項10項目を1項目1IDにすると10個増える。粗くまとめると参照精度が落ちる。**実物を見て決める**方針とし、机上で完全な体系を設計しない。
- **Status 語彙。** 現行は括弧書きで別情報を混ぜている（`Normative（ADR-0057 Accepted、実装はDOMAIN-W-ITERATION-01で追跡）`）。語彙を統制するなら、追跡情報は別フィールド（`Tracked-by:`）へ分離する必要がある。分離するか、括弧書きを許容するかは判断を要する。
- **遡及適用の範囲。** 既存64件の裸参照を識別子付きへ書き換えるか、新規のみ必須とするか。**新規のみを推奨する**——遡及は差分が大きく、かつ `ADR-0075` の教訓（遡及適用は指標を飽和させるが実効を伴わない）が当てはまる。

## 受入条件

- [x] AC-1: `domain.md` の §2 の3概念と §7 の禁止事項に、一意な識別子が付与されている。既存の散文の意味が変わっていない。
- [x] AC-2: `kj_technique.md` の §3・§4・§5・§6 の各検査・各徴候に識別子が付与されている。
- [x] AC-3: `docs_check` が `00_Prompt` の Status 語彙を検証し、統制外の値で落ちる。
- [x] AC-4: `docs_check` が `00_Prompt` 全体で識別子の重複を検出して落ちる。
- [x] AC-5: **他層から `DOM-*` / `KJT-*` 等を参照したとき、実在しない識別子で落ちる。** 存在する識別子では通る。
- [x] AC-6: 行番号参照を検出して落ちる。既存の該当箇所を識別子または節参照へ置換した（実測8件。当初「3件」としたのは計測漏れ）。
- [x] AC-7: **能力カナリア** — 実在しない識別子への参照を意図的に入れると AC-5 が落ちることを、ミューテーションで確認する（`DOGFOOD-METRIC-01` 案A）。

## 検証

```bash
python 01_Plans/docs_check.py
python -m pytest 01_Plans/tests/ -v
python 03_Implement/backend/scripts/check_design_consistency.py --baseline 02_Architecture/design_consistency_baseline.json
git diff --check
```

## 補足

- **AC-5 が本issueの要である。** AC-1〜AC-4 は識別子を**作る**だけで、使われる保証がない。AC-5 は**使われた識別子が正しいことを保証する**。AC-1 だけを実施して完了としないこと。
- **測定について**: 「識別子の数」は存在を数える指標であり、`ADR-0075` の L2 昇格条件②が遡及適用で構造上100%へ飽和した失敗と同じ性質を持つ。効果の指標は次とする——**不変条件を1つ変更したとき、影響を受ける計画文書を機械的に列挙できるか。** これができないうちは、識別子がいくつ増えても接続は成立していない。
- 三要素牽制の観点: 業務設計（憲法層が規範を定める）とデータ設計（規範が識別子を持つ）と機能設計（参照を検証する機構）のうち、**業務設計だけが単独で存在していた**。`OPS-OBSERV-01`（運用手順は詳細だが観測基盤が無い）と同型の不均衡である。
