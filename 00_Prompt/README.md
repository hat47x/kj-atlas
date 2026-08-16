# 00_Prompt — 憲法層の索引

- Status: Informative

本書は `00_Prompt/` に**何があるか**を示す索引である。**いつ読むか**の読み順は `AGENTS.md` の表を正とする。役割が異なるので両方が要る。

---

## 1. 二つの種別

`00_Prompt` には**権威も変更頻度も異なる二種類**の文書がある。同じ階層に置かれているが、扱いは同じではない。

| | **製品憲法** | **エージェント運用** |
|---|---|---|
| 何を定めるか | 製品が何であるか。侵してはならない不変条件 | AIエージェントがどう働くか |
| 読者 | 製品を作る人間とAI | AIエージェント |
| 変更 | **思想変更に相当する。** 理由と影響範囲の記録を要する（`domain.md` §9） | 道具の変化に追随してよい |
| 実装との関係 | **実装が憲法へ合わせる。** 実装都合で憲法を変えない | 実務に合わせて更新する |

**この区別は物理的なディレクトリ分割では表現していない。** 分割すると全リポジトリの参照が壊れ、利得に見合わないためである（`00-prompt-improvement-program-2026-08-15.md` P4）。

---

## 2. 製品憲法

| 文書 | Status | 定めるもの | 識別子 |
|---|---|---|---|
| [domain.md](domain.md) | Normative | **概念の憲法。** 保留・違和感・可逆性・非序列化、AIの役割、共有要件 | `DOM-CORE-*` `DOM-AI-*` `DOM-AIOK-*` `DOM-CRIT-*` `DOM-SHARE-*` |
| [kj_technique.md](kj_technique.md) | Normative | KJ法の手順と**検査**、失敗の徴候 | `KJT-INSPECT-*` `KJT-SIGN-*` |
| [cognitive_frame_and_evolution_criteria.md](cognitive_frame_and_evolution_criteria.md) | Normative | **存在理由と進化の判断基準。** 提案が適応か価値創出か逸脱かを判定する | — |
| [ai_cognitive_externalization_requirements.md](ai_cognitive_externalization_requirements.md) | Normative | 認知外在化の原則とIR要件 | 部分的（`MMR-*` 等） |
| [ai_kj_execution_procedures.md](ai_kj_execution_procedures.md) | Normative | KJ操作のAI実行手順と停止条件 | — |
| [qualitative_card_quality_requirements.md](qualitative_card_quality_requirements.md) | Normative | カードの定性情報品質 | 部分的 |
| [representative_visual_cue_requirements.md](representative_visual_cue_requirements.md) | Normative | 代表視覚手掛かりの要件と非目標 | 部分的 |
| [w_type_iterative_inquiry_requirements.md](w_type_iterative_inquiry_requirements.md) | Normative | W型累積KJ法の反復探究 | `WIR-01`〜`WIR-09` |

**最初に読むのは `domain.md`。** 他はすべてその上に載る。

---

## 3. エージェント運用

| 文書 | Status | 定めるもの |
|---|---|---|
| [system_prompt.md](system_prompt.md) | Normative | 開発支援AIの最上位行動規範 |
| [agent_collaboration.md](agent_collaboration.md) | Normative | 三エージェント協働の責務分担（`ADR-0045`） |
| [handoff.md](handoff.md) | Informative | 企画から開発への申し送り。実務上の読み替え |
| [codex_skill_operations.md](codex_skill_operations.md) | Informative | AIエージェント作業時の最小ルール |
| [agent_handover.md](agent_handover.md) | On-demand | 引き継ぎ補足。通常の作業開始時には読まない |

---

## 4. Status の語彙

`DC-NORM-004` が統制する。全文書に**ちょうど1つ**必要である。

| 値 | 意味 |
|---|---|
| `Normative` | 拘束する規則を定める |
| `Informative` | 方向づけと背景。拘束する規則は他所にある |
| `On-demand` | 必要になったときだけ読む |
| `Superseded` | 履歴として残す。従ってはならない |

**追跡情報を Status に混ぜない。** ADR番号や実装issueは `- Tracked-by:` へ書く。以前は `Normative（ADR-0057 Accepted、実装は…で追跡）` のように混在しており、値として使えなかった。

---

## 5. 識別子の使い方

**他層から憲法層を参照するときは、ファイル名だけでなく識別子で指す。**

```
✅ `DOM-CORE-02`（違和感は説明責任を伴わない）
✅ `KJT-INSPECT-02` 戻し検査
❌ `00_Prompt/domain.md`（どの規範か分からない）
❌ ファイル名にコロンと行番号を続ける形式（編集で腐る。DC-NORM-003 が禁止）
```

行番号参照が禁止されているのは理屈ではなく実績による。`domain.md` へ識別子を追記した際、既存の行番号参照はすべてずれ、引用文と指し先が食い違った。

### 検証

| 規則 | 内容 |
|---|---|
| `DC-NORM-001` | 識別子は `00_Prompt` 全体で一意。**再利用しない** |
| `DC-NORM-002` | 他層からの参照が実在する定義へ解決する |
| `DC-NORM-003` | 憲法層への行番号参照を禁止 |
| `DC-NORM-004` | Status が統制語彙のちょうど1つ |

`DC-NORM-002` が中核である。識別子を作るだけでは「あるが誰も使わない」状態になる。**参照を検証して初めて機構として成立する。**

### 計画側の `Norms:` 欄

issue と ADR のテンプレートに `- Norms:` がある。依拠または抵触する憲法層の識別子を書く。

**必須ではなく任意である。** 憲法層に触れない変更のほうが多く、必須にすると `TBD` で埋まる欄が増える。
書かれた場合は `DC-NORM-002` が実在を検証する。**書かない自由はあるが、嘘を書く自由はない。**

### 逆引き

```bash
python 01_Plans/norm_impact.py DOM-CORE-04
```

ある規範を変更したとき影響を受ける計画を列挙する。**この問いに答えられることが、本施策の効果の指標である**
（`00-prompt-improvement-program-2026-08-15.md` §6）。識別子の数ではない。

---

## 6. 変更するとき

- **製品憲法**: `domain.md` §9 に従う。理由と影響範囲を記録する。`domain.md` は §10 変更記録を持つ。
- **識別子**: **追記のみ。** 一度与えた番号を再利用しない。廃止する場合は項目を残して廃止と明記する。
- **提案が適応か逸脱か迷ったら**: `cognitive_frame_and_evolution_criteria.md` §3 の判定手順を使う。

---

## 7. 既知の課題

憲法層自身の未解決事項を隠さない（`DOM-SHARE-04`）。

- **`ai_cognitive_externalization_requirements.md` に実装詳細が入り込んでいる。** §7 以降は `02_Architecture` の粒度であり、憲法が実装変更のたびに触られる状態になっている（`00-prompt-improvement-program-2026-08-15.md` P5、未着手）。
- **識別子が部分的な文書が3件ある。** `ai_cognitive_externalization_requirements` / `representative_visual_cue_requirements` / `qualitative_card_quality_requirements`。体系が揃っていない。
- **逆引きの網羅率が低い。** `Norms:` 欄と `01_Plans/norm_impact.py` により逆引きは成立したが、**憲法層の定義56件のうち追跡中は12件**である。残りは「その規範に依拠する計画がまだ無い」のか「書かれていないだけ」なのかを区別できない。欄が任意である以上この曖昧さは残る。網羅率を上げるには、既存 issue への遡及配線が要る。
