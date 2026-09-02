# Issue: AI-IR-SCALE-01 大規模ラウンドでも意味を失わないLLM入力投影を設計する

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Architecture / Feature / Verification
- Status: Open
- Source Issue: `AI-IR-PROJECTION-01` AC-10
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/llm_input_ir.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/scripts/`, `03_Implement/backend/tests/`, `02_Architecture/llm_input_ir_spec.md`
- Related ADR/Spec: `ADR-0069`, `ADR-0047`, `02_Architecture/llm_input_ir_spec.md` §5, `issue-DOGFOOD-31-two-hundred-card-scale-exceeds-ai-operation-limits.md`
- Expected verification level: backend unit + representative-scale measurement + named-provider token observation

## 課題

KJ Atlasは、数百枚のカードを扱うKJ実践を正常な利用規模としている。`DOGFOOD-31` では200枚の第1ラウンドを実走し、`suggest-card-groups` のリクエスト上限を100枚から1000枚へ緩和した。

一方、`AI-IR-PROJECTION-01` が導入したLLM入力IRには、現在次の全体上限がある。

- `MAX_CARDS = 200`
- `MAX_RELATIONS = 400`
- `MAX_TEXT_CHARS = 12000`

Stage 5へIR経由を広げる前のAC-10計測として、300カード・30島・300 relation の決定論的な代表入力を作り、現行投影を実行した。その結果、`MAX_CARDS` により次が再現した。

- 300カードのうち200カードだけがIRへ残り、100カードがIRの構造文脈から外れる。
- 30島そのものは保持されるが、後半10島はIR上で全メンバーを失って空島になる。
- ring状の300 relationはIR上で199 relationへ減る。
- `truncation.reason_codes` には `MAX_CARDS` が残るため、切り詰めが発生した事実は分かる。しかし、どの意味領域・島・異論・保留・根拠が失われたかまでは消費側から判断できない。

これは `DOGFOOD-31` の再発ではない。リクエスト自体は200枚超を受けられるようになっているが、その後のIR投影層に別のcoverage境界がある。

### IR coverage と実prompt coverageを分ける

IRから100カードが外れたことを、すべてのrouteで「provider promptから100カードが完全に消えた」と読み替えてはいけない。現在の移行済みrouteには、互換性や出力契約のためDocument由来情報を別経路でも描画しているものがある。

- `suggest-card-groups` は、IR内のカードから実際の候補カード列を描画するため、IRのcard coverageが候補集合へ直接影響する。
- `suggest-layout` は、全カードのid/text/現在座標を従来の `Cards:` 節へ残しつつ、IRから相対配置・relation・島構造を追加している。ここでのIR切り詰めは、カードの存在そのものより**構造文脈のcoverage**を失わせる。
- `generate-narrative` もreading order自体はDocument由来で保持する一方、card-to-cardの論理構造をIRから受ける。したがって失われる情報の種類は `suggest-card-groups` と同じではない。

このため、scale remediationはIR単体の件数だけでなく、**routeごとの最終promptで何が残り、何が欠けるか**を測って判断する。

### 2026-09-03 route別の最終prompt計測

PR #2820で、300カード・30島の同じ代表入力を、移行済み3 routeの実際のprompt builderへ通した。外部LLMは呼ばず、providerへ送られる描画済みpromptを決定論的に比較した。

| route | card text | 完全な島membership | typed relation | 相対座標 |
| --- | ---: | ---: | ---: | ---: |
| `suggest-card-groups` | 200/300 | 20/30 | 199/300 | 対象外 |
| `suggest-layout` | 300/300 | 30/30 | 199/300 | 200/300 |
| `generate-narrative` | 300/300 | 30/30 | 199/300 | 対象外 |

この結果から、全カード本文が最終promptに残るrouteでも、relationや相対配置などの構造文脈は共有IRの上限を受けることが確認できた。単一の「カードが何枚見えるか」だけでは、AIへ届く意味のcoverageを評価できない。

さらに、各島に1件ずつ計30件のheld contradiction evidence linkを加えた副シナリオでは、共有IRに20件が残った。その20件について最終promptを測ると次の差があった。

| route | source evidence | IRに残る | 最終promptで見える |
| --- | ---: | ---: | ---: |
| `suggest-card-groups` | 30 | 20 | **0** |
| `suggest-layout` | 30 | 20 | **0** |
| `generate-narrative` | 30 | 20 | **20** |

ここでは `30 -> 20` が規模上限によるcoverage lossであり、`suggest-card-groups` / `suggest-layout` の `20 -> 0` はprompt rendererによる追加欠落である。後者は規模・token判断から分離し、`AI-IR-PROMPT-EVIDENCE-01` としてP1で修正する。

renderer欠落を直しても、`MAX_CARDS` による20/30のcoverage lossは残る。本Issueは引き続きOpenとし、named providerのtoken観測と意味保存型投影戦略の判断を継続する。

### なぜ問題か

KJ Atlasの一次価値は、根拠・異論・保留・人間の判断を途中で失わず、後から判断の経路へ戻れる理解へ育てることにある。

現在のIR切り詰めは中心性順位を使うため決定論的ではあるが、300枚規模で「IRの3分の1を外し、島を空にする」ことを許す。中心性が低いカードが、少数意見、未決事項、反証、周辺観察である可能性はあるため、単に順序が決定論的であるだけでは意味保存を保証できない。

さらに、routeによってはカード本文を別経路で残していても、relation、evidence、hold、島membershipなどIRが担う構造が欠ければ、AIは「カードを知っているが、人間が与えた意味のつながりを知らない」状態になり得る。

また、上限を300や1000へ機械的に引き上げればよいとも限らない。provider transportが実際に送るのは描画済みpromptであり、正確なinput token数はmodel/provider固有である。IRのJSON bytesだけから共通の安全なtoken上限を決めることはできない。

## 三要素分析

| 次元 | 分析 | 他次元への制約 |
| --- | --- | --- |
| 業務設計 | 数百枚の生カードから少数意見・保留・残差を含む構造を育てる。大規模だから周辺の意味文脈を黙って捨てる運用は一次価値と衝突する | 速度や一回のprompt完結を、意味保存より上位に置かない |
| データ設計 | IRは全Documentの複製ではなくLLMへ渡す構造投影である。切り詰め後も「何を代表し、何を落としたか」が追える必要がある | island/evidence/hold等の人間確定情報を、中心性だけで無差別に消さない |
| 機能設計 | routeごとに従来promptとIRの役割分担が異なる。global cap引上げ、task別投影、島ごとの代表抽出、batch/hierarchical処理など複数方式がある | provider/modelのtoken予算とSafeMode、決定性、proposal-only境界を維持する |

## 対応方針

### 先に測ること

1. 300カード・30島の代表入力について、移行済みrouteの最終prompt coverageを比較する。**完了。PR #2820で決定論的な測定を追加した。**
   - `suggest-card-groups`: IR truncationが候補集合へどう反映されるか。
   - `suggest-layout`: 全カード節を残したまま、IR由来のrelation/island/relative-placement coverageがどこまで失われるか。
   - `generate-narrative`: reading orderとIR由来の論理構造のcoverage差。
2. 少なくとも次をnamed model/providerで実測する。
   - `suggest-layout` 相当: 座標・島・関係を含む最重量prompt。
   - 座標を使わない代表route。
3. 正確なinput token数は、既存のprovider-reported usageを用いてmodel名とともに記録する。IR bytesから架空のtoken数を推定しない。
4. model/providerがusageを返さない場合は、その事実を記録し、別tokenizer導入を自動的な前提にしない。

### 検討する方式

次を比較し、最初から一案へ固定しない。

- **A: global capを引き上げる**
  - 実測token予算に余裕があり、主要modelで安全に扱える場合。
- **B: task別・意味保存型の投影へする**
  - 各非空島から少なくとも代表カードを残す。
  - `hold_state`、根拠/矛盾リンク、少数・反対所見など保護すべき情報を、各taskの意味に応じた明示規則で残す。
- **C: batch / hierarchical projection**
  - 全量を一度にpromptへ入れず、島/ラウンド単位で分割し、最終提案へ統合する。

方式B/Cを採る場合でも、AIが勝手に「重要でないカード」を確定削除する設計にはしない。投影上の省略と、DocumentV1上の資料保持は別である。

## 受入条件

- [ ] 300カード・30島の代表規模について、少なくとも1つのnamed model/providerでprovider-reported input token数を記録できる。
- [ ] `suggest-layout` 相当の最重量promptと、座標を使わない代表routeのtoken/coverage差を記録できる。
- [x] `suggest-card-groups` / `suggest-layout` / `generate-narrative` について、IR切り詰めが最終promptのどの情報を失わせるかを区別して記録できる。
- [ ] 300枚規模で、非空だった島がglobal selectionだけを理由にIR上で黙って空島へ変わらない。空になる場合は、消費側がcoverage lossを明示的に判断できる契約を持つ。
- [ ] 保留・根拠・矛盾・少数/反対所見など、人間が意味を与えた情報を中心性順位だけで無差別に落とさない規則、またはそれらを確実に処理するbatch規則を仕様化する。
- [ ] 切り詰め時に、単なる `MAX_CARDS` だけでなく、少なくともcoverageの欠落を後から検証できる情報を残す。
- [ ] 同一入力から同一投影/分割結果を得られる決定性を維持する。
- [ ] SafeMode二層、防PII、structured-text-only、proposal-onlyの既存境界を弱めない。
- [x] 300カード規模の回帰テストをCIで固定する。
- [ ] 上限値の変更を行う場合、named model/providerの実測根拠を記録する。

## 検証計画

- 自動確認:
  - `scripts/measure_llm_input_ir_scale.py`
  - `scripts/measure_ai_route_prompt_coverage.py`
  - `tests/test_llm_input_ir_scale.py`
  - `tests/test_ai_route_prompt_coverage.py`
  - IR単体テスト、移行対象route統合テスト、backend全体回帰。
- 実使用/外部依存確認:
  - 明示的に選んだnamed model/providerで1回以上の代表規模requestを行い、provider-reported usageを保存する。
  - 外部LLMを呼ばない通常CIでは、exact token countを捏造せず構造・prompt coverageだけを決定論的に検査する。

## 完了境界

本Issueの最低限の安全な投影戦略とtoken予算判断が得られるまで、`AI-IR-PROJECTION-01` Stage 5を7経路へ一括展開しない。

ただし、Stage 5の各route調査や、IRを使わない現行経路のbug修正を止めるものではない。`AI-IR-PROMPT-EVIDENCE-01` のように、IRへ残った意味がrendererでさらに失われる不具合は、この規模判断を待たずに修正する。

## 補足

- 本Issueは `AI-IR-PROJECTION-01` AC-10が明示していた「上限値が現行規模に合わない場合は別issueへ切り出す」を実行したもの。
- route別最終prompt計測はPR #2820で追加し、R15継続dogfoodで `AI-IR-PROMPT-EVIDENCE-01` への分離まで行った。
- 現時点では長期アーキテクチャ判断を確定しないため、新ADRは起票しない。task別投影やbatchingが複数境界を横断する長期契約へ発展した場合にのみ `ADR-0047` のトリガーを評価する。
