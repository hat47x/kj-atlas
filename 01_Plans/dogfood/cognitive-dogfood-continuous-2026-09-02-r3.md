# 継続dogfood記録 — 2026-09-02 第3ラウンド

## 位置づけ

この記録は、KJ Atlas自身を日常的な開発対象としてKJ法で検討する継続dogfoodの第3ラウンドである。

前ラウンドでは、初回サンプルとgetting startedを一次利用仕事へ近づけた。一方で、その改善だけでは第三者価値の実在を証明できないため、次の重心を `VALUE-REALNESS-01` と `COGNITIVE-EVAL-01` に置いた。

今回はそのうち `VALUE-REALNESS-01` を対象にし、「第三者価値実証は、実際には何が不足していて始められていないのか」を確認した。

Case 001〜003の統制比較とは目的が異なる。今回も既知の設計判断を含むため、比較実験の入力には使用しない。生成AIの外部APIも使用していない。

## 今回の問い

> 第三者価値実証を進めるうえで、いま不足しているのは検証手順・計測基盤・製品機能なのか。それとも、実際の第三者と資料という外部入力なのか。

最初から「準備不足」と決めず、正本Issue、第三者実証protocol、validator、workflow、価値測定計画を同じ場に置いて確認した。

## 用いた材料

- `01_Plans/issues/issue-VALUE-REALNESS-01-third-party-beachhead-validation.md`
- `01_Plans/issues/issue-VALUE-MEASURE-01-measurement-harness-and-evidence-artifacts.md`
- `01_Plans/dogfood/third-party-value-validation-execution-plan.md`
- `01_Plans/dogfood/third-party-value-participant-brief.md`
- `01_Plans/dogfood/third-party-value-session-launch-checklist.md`
- `01_Plans/dogfood/third-party-value-session-record-template.md`
- `01_Plans/dogfood/third-party-value-publication-boundary.md`
- `01_Plans/dogfood/third-party-value-analysis-plan.md`
- `01_Plans/dogfood/validate_third_party_value_protocol.py`
- `.github/workflows/third-party-value-protocol.yml`
- `01_Plans/dogfood/cognitive-dogfood-index.md`

## KJキャンバス

正規データは次のDocumentV1に残した。

- `01_Plans/dogfood/doc_kj_atlas_dogfood_r9.json`

今回のカードもAIが作成した提案段階の材料なので、`textReviewed: false` としている。

## 島1 — 実行資産は揃っているが、正本Issueからその準備状態が見えにくかった

`VALUE-REALNESS-01` はP0かつOpenであり、第三者が自分の題材を使った価値実証はまだ完了していない。

一方で、実行計画、参加者向け説明、実資料投入前の開始チェック、session記録、公開境界、事前分析計画はすでに揃っていた。さらに、protocolの重要な不変条件を検査するvalidatorと専用GitHub Actionsも存在する。

つまり、第三者実証が進んでいない理由を「protocolがまだない」と理解するのは正しくない。

問題は別のところにあった。`cognitive-dogfood-index.md` では第三者実証の主要文書へ辿れるが、実行課題の正本である `VALUE-REALNESS-01` からは、それらの準備済み資産へ直接辿れなかった。

Issue単体を読んだ場合、次の二つを判別しにくい状態だった。

- まだ実行手順を設計する必要があるのか。
- 手順は揃っており、実際の第三者sessionを待っているのか。

これは検証設計の不足ではなく、**正本と実行資産の接続不良**とみなした。

## 島2 — 現在の律速は追加計測ではなく、実際の第三者sessionという外部入力にある

第三者実証protocolでは、参加者本人が扱える実資料、匿名化資料、または本人が現実的と認める代替資料を使うことになっている。

したがって、現在残る主要な外部入力は次である。

- 第三者協力者、またはそれに準ずる外部評価機会。
- その人が意味と文脈を説明でき、安全に扱える資料。
- 実際の実行環境におけるAI/provider/network/storageのdata path確認。

最後のdata pathは、リポジトリ上の一般論で確定するものではない。利用するruntimeと資料条件によって変わるため、各sessionの最初の実資料投入前に `third-party-value-session-launch-checklist.md` で確認する。

また、`VALUE-MEASURE-01` はreal-user/cooperator milestone前に重い計測基盤やtelemetryを前倒ししない方針を明示している。

このため、現在の段階で次を増やしても、主要な不確実性はほとんど減らない。

- 新しい価値KPI。
- 個人追跡telemetry。
- 第三者実証専用のproduct schema/API。
- 既存protocolと重複する同意・観察・分析文書。
- 内部dogfoodを追加して第三者実証の代わりにすること。

第三者価値が実在するかどうかは、内部資料をさらに精緻化しても答えられない。

## 島3 — 正本と実行資産をつなぎ、その導線自体をCIで守る

今回、`VALUE-REALNESS-01` に次を追加した。

- 準備済みの第三者実証資産。
- 現在残っている外部入力。
- session開始時に読む文書と実行順。
- protocol準備済みであることと、価値実証完了を混同しない境界。

さらに `validate_third_party_value_protocol.py` を拡張し、正本Issueに実行資産への参照と実行準備状態が残っていることも検査対象にした。

`.github/workflows/third-party-value-protocol.yml` も更新し、`VALUE-REALNESS-01` の変更時に専用validatorが走るようにした。

これにより、「protocol文書は残っているが、正本Issueから入口だけが消える」という退行をCIで検出できる。

## 島4 — 準備完了と価値実証完了を混同しない

今回の改善によって、リポジトリ側の実行準備は見つけやすくなった。しかし、それは `VALUE-REALNESS-01` の受入条件を満たしたことを意味しない。

価値実証の証拠は、実際の第三者sessionから得る必要がある。

また、第三者sessionは完遂や肯定評価を目的にしない。

- `STOP-DATA-BOUNDARY`
- `STOP-PARTICIPANT`
- 既存手段で十分だった。
- KJ Atlasを使う理由がなかった。
- 操作負担が便益を上回った。

これらも有効な外部現実である。

内部dogfoodで価値仮説を補強し続けるより、否定的な結果を含めて外部から実際の材料を受け取れる状態を保つ方が重要である。

## 課題の振り分け

| 観察 | 判定 | 対応 |
| --- | --- | --- |
| 第三者実証の実行資産は揃っている | 解消済みの不確実性 | 新しいprotocol文書を作らない |
| 正本Issueから実行資産へ辿りにくい | F1 | `VALUE-REALNESS-01` に準備状態と実行入口を追加した |
| Issueから実行入口が将来再び消える可能性がある | F1 | protocol validatorと専用workflowで参照関係を検査する |
| 第三者sessionそのものが未実施 | 既存P0の未完 | `VALUE-REALNESS-01` をOpenのまま維持する |
| runtime data pathが事前に一意に定まらない | 設計済みの実行時不確実性 | session開始時のlaunch checklistで確認する |
| real-user前に計測基盤を増やしたくなる | 既存境界 | `VALUE-MEASURE-01` の延期方針を維持する |
| 内部dogfoodで第三者価値を代替したくなる | 既存境界 | 第三者の独立した外部入力を待つ |

## 今回実施した変更

- `VALUE-REALNESS-01` に実行準備状態、外部入力、session開始手順を追記。
- `validate_third_party_value_protocol.py` に正本Issueからの導線検査を追加。
- `third-party-value-protocol.yml` のpathsへ `VALUE-REALNESS-01` を追加。
- 本ラウンドのKJキャンバス `doc_kj_atlas_dogfood_r9.json` を作成。

## 残る未完

R9で新しく製品機能を実装すべきP0欠陥は確認されなかった。

次に `VALUE-REALNESS-01` を実質的に前進させる条件は、第三者協力者または同等の外部評価機会が得られ、実際の資料条件でsessionが発生することである。

その時点では新しいprotocolを設計し直さず、既存の実行計画とlaunch checklistから開始する。sessionが途中で停止した場合も、停止理由を有効な結果として保持する。
