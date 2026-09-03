from pathlib import Path
import re

ROOT = Path("01_Plans/issues")
PARENT = ROOT / "issue-AI-MERGE-SEMANTICS-01-define-card-merge-semantics.md"
PARTIAL = ROOT / "issue-AI-MERGE-PARTIAL-01-define-partial-merge-selection-contract.md"
PARTIAL_DONE = ROOT / "done" / PARTIAL.name
METHOD = ROOT / "issue-AI-MERGE-METHOD-TRACE-01-track-merge-method-through-decision-audit.md"

parent = PARENT.read_text(encoding="utf-8")

old = "- Status: Done"
if parent.count(old) != 1:
    raise SystemExit(f"parent status replacement count={parent.count(old)}")
parent = parent.replace(old, "- Status: In Progress", 1)

old = "- Related ADR/Spec: `ADR-0069`, `AI-IR-PROJECTION-01`, `AI-IR-STAGE5-SCOPE-01`, `AI-MERGE-APPLY-01`, `AI-MERGE-PARTIAL-01`"
new = "- Related ADR/Spec: `ADR-0069`, `AI-IR-PROJECTION-01`, `AI-IR-STAGE5-SCOPE-01`, `AI-MERGE-APPLY-01`, `AI-MERGE-PARTIAL-01`, `AI-MERGE-METHOD-TRACE-01`"
if parent.count(old) != 1:
    raise SystemExit(f"parent related replacement count={parent.count(old)}")
parent = parent.replace(old, new, 1)

old = """### 方法を固定しない

04ステップを常に先に使う、核融合法を常に先に使う、と固定しない。カードの関係を見て、意味保存性、残差の少なさ、元カードへの戻しやすさが高い方法を選ぶ。

現在は方式によって実適用のデータ変換が分岐しないため、`mergeMethod` を機械可読の必須フィールドにはしない。方式名をAIに自己申告させるだけでは正本として弱い。将来、方式ごとにUI、戻し検査、適用規則が実際に変わる場合に別Issueで契約化する。
"""
new = """### 方法を固定しない

04ステップを常に先に使う、核融合法を常に先に使う、と固定しない。カードの関係を見て、意味保存性、残差の少なさ、元カードへの戻しやすさが高い方法を選ぶ。

一方、継続dogfood R18では、promptが二つの方法を区別していても、現行 `MergeSuggestion` からは**どちらの方法で提案したかが判断時点で失われる**ことを残差として確認した。実適用のデータ変換が同じでも、人間が後から採用理由へ戻るための判断文脈として方式には追跡価値がある。

このため、方式をAIの自由記述だけへ埋めず、proposal → decision → audit まで機械的に追跡できる最小契約を `AI-MERGE-METHOD-TRACE-01` で定める。方式によって実適用規則を自動分岐させることは、同Issueの目的には含めない。
"""
if parent.count(old) != 1:
    raise SystemExit(f"parent method section replacement count={parent.count(old)}")
parent = parent.replace(old, new, 1)

old = "- [x] `mergeMethod` は実際に適用挙動が分岐するまで必須化しない。"
new = "- [ ] 04ステップ型／核融合法型の方式を、proposal → decision → audit まで機械的に追跡できる最小契約を固定する（`AI-MERGE-METHOD-TRACE-01`）。"
if parent.count(old) != 1:
    raise SystemExit(f"parent method AC replacement count={parent.count(old)}")
parent = parent.replace(old, new, 1)

old = """## 完了境界

04ステップと核融合法を意味保存の考え方として使い分けつつ、元カード、人間判断、矛盾、来歴を失わず、AI提案から実適用・保存・再読込まで戻れることを回帰で固定した。

AIが自動的にmergeを確定・適用する経路は設けていない。部分採用も人間の明示選択を必須とした。以上をもって、本Issueを完了とする。"""
new = """## R18後に残る作業 — 方式の追跡性

`partial` を含む意味保存・人間判断・実適用・保存／再読込の本流は回帰で固定できた。一方、R18で、04ステップ型の近接整理として出た提案なのか、核融合法型の意味核統合として出た提案なのかが、provider応答後の共通契約から失われることを確認した。

これは実適用の変換を変えるためではなく、人間が「なぜこの統合を採ったか」を後からたどるための判断文脈である。`AI-MERGE-METHOD-TRACE-01` で、後方互換を保ちながらproposal・判断ログ・監査へ同じ方式を通す。

独立した自由記述 `residuals` は追加しない。残差の一次記録は、削除されず残るsourceカードそのものとする。

## 完了境界

04ステップと核融合法を意味保存の考え方として使い分け、元カード、人間判断、矛盾、来歴を失わず、AI提案から実適用・保存・再読込まで戻れる本流は実装済みである。部分採用も人間の明示選択を必須として完了した。

親Issueは、R18で残った**merge方式の追跡性**を `AI-MERGE-METHOD-TRACE-01` で閉じるまで `In Progress` とする。AIが自動的にmergeを確定・適用する経路は引き続き設けない。"""
if parent.count(old) != 1:
    raise SystemExit(f"parent completion replacement count={parent.count(old)}")
parent = parent.replace(old, new, 1)
PARENT.write_text(parent, encoding="utf-8")

partial = PARTIAL.read_text(encoding="utf-8")
pattern = re.compile(r"## `mergeMethod` と残差の扱い\n.*?\n## 実装結果（2026-09-03）", re.S)
replacement = """## merge方式と残差の扱い

本Issueの責務は、人間が `partial` で選んだ真部分集合を判断・監査・実適用・保存／再読込まで同じ集合として保つことである。04ステップ型／核融合法型の**方式そのものをどう追跡するか**は、継続dogfood R18で独立した残差として確認したため、`AI-MERGE-SEMANTICS-01` と `AI-MERGE-METHOD-TRACE-01` へ分離する。

一方、自由記述の `residuals` は本Issueでも追加しない。統合本文へ入り切らなかった意味の一次記録は、削除されず残るsourceカードそのものとする。

## 実装結果（2026-09-03）"""
partial, count = pattern.subn(replacement, partial, count=1)
if count != 1:
    raise SystemExit(f"partial method section replacement count={count}")

old = "- [x] `mergeMethod` は実適用の意味が分岐するまで必須契約にしない。"
new = "- [x] merge方式の追跡性を本Issueの完了条件へ混ぜず、`AI-MERGE-SEMANTICS-01` / `AI-MERGE-METHOD-TRACE-01` へ分離する。"
if partial.count(old) != 1:
    raise SystemExit(f"partial method AC replacement count={partial.count(old)}")
partial = partial.replace(old, new, 1)
PARTIAL.write_text(partial, encoding="utf-8")

if PARTIAL_DONE.exists():
    raise SystemExit(f"destination already exists: {PARTIAL_DONE}")
PARTIAL_DONE.parent.mkdir(parents=True, exist_ok=True)
PARTIAL.replace(PARTIAL_DONE)

if METHOD.exists():
    raise SystemExit(f"method issue already exists: {METHOD}")
METHOD.write_text(
    """# Issue: AI-MERGE-METHOD-TRACE-01 merge方式を判断・監査まで追跡可能にする

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Feature / Domain Integrity / AI Integration
- Status: Open
- Source Issue: `AI-MERGE-SEMANTICS-01`
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/frontend/src/api/client.ts`, `03_Implement/frontend/src/domain/merge_suggestion_decisions.ts`, `03_Implement/frontend/src/domain/merge/decision_audit_events.ts`, `03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx`, `02_Architecture/api.md`
- Related ADR/Spec: `ADR-0069`, `AI-MERGE-SEMANTICS-01`, `AI-MERGE-PARTIAL-01`, `AI-MERGE-APPLY-01`, 継続dogfood R18
- Expected verification level: backend/frontend contract → decision/audit integration → UI regression

## 課題

現在のmerge promptは、近接カードを整理する04ステップ型と、複数カードから共通の意味核を立てる核融合法型を区別して使うようAIへ要求している。しかし共通 `MergeSuggestion` は `groupId` / `cardIds` / `mergedTextDraft` / `rationale` だけであり、**どちらの方法で提案したかがprovider応答から人間判断へ渡る途中で失われる**。

継続dogfood R18では、意味保存型mergeの主要経路をbackendから保存・再読込まで横断して確認し、この方式情報を次の残差として特定した。

方式によって現在の実merge変換を自動分岐させる必要はない。それでも、人間が後から「これは近接整理として採ったのか、意味核を立てる統合として採ったのか」を判断理由と一緒にたどれることには価値がある。

## 方針

新しく生成するmerge提案には、次のどちらかを機械可読に持たせる方向で実装する。

- `near_duplicate`: 04ステップ型の近接整理。重要な差を残したまま、別々に保持する増分が小さいカードを整理する。
- `kernel_fusion`: 核融合法型。完全な重複ではない複数カードから、各カードへ戻れる共通の意味核を立てる。

フィールド名は `mergeMethod` を第一候補とする。backend・frontendの既存保存データとの後方互換を壊さないため、永続／decoder上は旧データを受けられる形を保ちつつ、**新しいprovider提案と決定論的ローカル候補では方式を欠落させない**。

方式はAIの自由記述へ埋めず、proposal → 人間のdecision snapshot → decision auditまで同じ値を通す。UIでは判断時に方式を確認できるようにする。

## remote AI提案とローカルfallbackの境界

PR #2853で、remote/common `MergeSuggestion` と決定論的ローカル候補のStream B派生契約を分離した。この境界は崩さない。

- remote AI提案: backendの正式schema/promptから `mergeMethod` を返す。
- 決定論的ローカル候補: 現在のnormalized-text中心の候補生成が04ステップ型の近接整理に相当することを、テストで確認したうえで `near_duplicate` を付与する。
- score、reason code、snapshotVersionなどStream B固有メタデータをremote AI契約へ再び必須化しない。

## 残差との関係

自由記述の `residuals` フィールドは追加しない。

現行applyは元カードを削除せず、代表カードから `repOf` / `sources` を通じてsourceへ戻れる。統合本文へ入り切らなかった条件、感触、異論、例外の一次記録は元カードそのものである。

方式追跡は、このsource-card traceabilityを置き換えるものではなく、「どの統合の考え方で代表文を提案・採用したか」という判断文脈を補う。

## 受入条件

- [ ] 04ステップ型／核融合法型の2方式を、既存語彙と衝突しない機械可読値として確定する。
- [ ] backendの新規provider提案が方式を返し、未知方式・欠落方式を新規応答で黙って採用しない。
- [ ] frontendのremote/common契約と決定論ローカル派生契約の分離を維持したまま方式を受け渡す。
- [ ] ローカルfallbackの方式を実際の候補生成規則から決定し、AI提案用の値を捏造しない。
- [ ] 人間のdecision snapshotへ提案時の方式を保存する。
- [ ] decision auditへ同じ方式を保存し、proposal → decision → auditで値が一致する。
- [ ] UIで判断前と判断後に方式を確認できる。
- [ ] accept / partial の実mergeは、方式ラベルだけを理由に異なるデータ変換へ自動分岐しない。
- [ ] 旧Document・旧provider fixture・旧decision logとの後方互換を回帰で確認する。
- [ ] 自由記述 `residuals` を追加せず、元カードへのtraceabilityを残差の一次記録として維持する。
- [ ] API文書・`AI-MERGE-SEMANTICS-01`・継続dogfood索引を実装結果へ同期する。
- [ ] 最終成果物を、意味を変えず自然な日本語として全文を読み直す。

## 完了境界

`mergeMethod` を表示用ラベルとして足すだけでは完了しない。新しい提案で方式を欠落させず、remote/commonとlocal派生の契約境界を壊さず、proposalから人間判断・監査まで同じ方式を追跡できることを回帰で固定した時点で完了とする。
""",
    encoding="utf-8",
)

print("R18 reconciliation prepared")
