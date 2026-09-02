# Issue: VALUE-REALNESS-01 第三者の実資料でプロダクト価値の実在を検証する

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Process
- Status: Open
- Source Issue: N/A
- Priority: P0
- Owner: Maintainer
- Scope: `01_Plans/issues/`, `01_Plans/dogfood/`, `04_Documentation/`
- Related ADR/Spec: `ADR-0032`, `ADR-0042`, `ADR-0047`, `ADR-0057`, `00_Prompt/kj_technique.md`, `COGNITIVE-DOGFOOD-01`
- Execution protocol: `third-party-value-validation-execution-plan.md`, `third-party-value-participant-brief.md`, `third-party-value-session-launch-checklist.md`, `third-party-value-session-record-template.md`, `third-party-value-publication-boundary.md`, `third-party-value-analysis-plan.md`
- Expected verification level: docs-check

## 課題

- 現在の問題:
  - `ADR-0032` で価値ループ、`ADR-0042` で価値実在の検証条件、`ADR-0057` で累積的なW型探求モデルまで定義されている一方、第三者が自分の題材を持ち込んだ実利用で「この道具を使い続けたい理由」が生じるかは未検証である。
  - 現行のdogfood/E2Eは契約・回帰・実規模の成立性を強く検証できるが、既存手段からKJ Atlasへ切り替える理由、学習負荷、方法適合、成果物の説明可能性を第三者視点で観測するものではない。
  - KJ Atlas自身をKJ Atlasで分析する認知dogfoodは、内部設計の改善には有力でも、`dogfood → issue/ADR/実装 → 次のdogfood` という自己参照的な改善循環を強め得る。外部利用者の現実入力が弱いまま内部整合性だけが高まる可能性は、現時点では**リスク仮説**として検証が必要である。
  - 後続の `VALUE-MEASURE-01/02`、`VR-ROADMAP-01`、`SOCIAL-DIFFUSION-*` は real-user/cooperator milestone を待つ設計であり、本issueがその入口になる。
- 利用者または開発への影響:
  - 価値論と実装が成熟しても、利用者が感じる便益の実在を確認しないままでは、README・初回導線・優先順位・社会普及仮説を確定できない。
  - 内部dogfoodの成功だけで価値仮説を強化すると、「製品が自分自身を上手に分析できる」ことと「社会の第三者が使う理由がある」ことを取り違える可能性がある。

## 仮説

KJ Atlas の初期価値仮説を次のように置き、第三者利用で反証可能にする。

> インタビュー、観察、自由記述、議論メモなどの雑多な定性資料を、出典・異論・保留・人間の判断権・過去への戻り道を失わずに、共同で検証可能な構造と成果へ育てられることに価値がある。

初期の beachhead 候補は、定性/UXリサーチ、デザインリサーチ、調査を伴うプロダクト企画など、既に affinity mapping・質的分析・AI要約を使う実践とする。これは確定ターゲットではなく、比較対象と課題密度が明瞭な検証入口である。

### 第三者検証の二つの役割

1. **Product-value validation**: 実際に切替理由、再利用理由、成果上の便益が生じるかを見る。
2. **External-reality grounding**: 内部dogfood/設計文書/AIが作る自己参照的な認識循環へ、製品外から反証・違和感・不要判断を入れる。

後者は「第三者の意見が正しい」という意味ではない。内部で立てた価値仮説が、外から来た材料によって実際に変更・縮小・棄却可能な状態を保つための入力である。

## 現在の実行準備状態

このissueの検証手順は、第三者の反応を見る前にリポジトリ上で準備済みである。したがって、現時点の未完了を「検証protocolがまだない」ことと混同しない。

準備済みの正本・補助資産は次のとおり。

- `01_Plans/dogfood/third-party-value-validation-execution-plan.md`
  - V0〜V4の実行順、参加条件、観察単位、停止条件、finding triageを定める。
- `01_Plans/dogfood/third-party-value-participant-brief.md`
  - 参加者へ目的、資料条件、AI・network・保存経路、公開境界、中止可能性を平易に説明する。
- `01_Plans/dogfood/third-party-value-session-launch-checklist.md`
  - 最初の実資料を投入する前にruntime data pathを確認し、`GO / GO-WITH-REDUCTION / STOP-*` を記録する。
- `01_Plans/dogfood/third-party-value-session-record-template.md`
  - baseline、raw observation、artifact evidence、friction、no-use、counterevidence、停止理由、事後説明を同じsession記録に残す。
- `01_Plans/dogfood/third-party-value-publication-boundary.md`
  - raw material、識別可能なartifact、public Gitへ残せるsanitized evidenceを分離する。
- `01_Plans/dogfood/third-party-value-analysis-plan.md`
  - 結果を見る前に分析順序を固定し、内部仮説へ `support / modify / narrow / reject / unresolved` で戻す。
- `01_Plans/dogfood/validate_third_party_value_protocol.py`
  - 中立なbaseline、停止/no-useの保持、runtime data pathの開示、public Git境界などのprotocol不変条件をfail-closedで検査する。
- `.github/workflows/third-party-value-protocol.yml`
  - 上記validatorをGitHub Actionsで実行する。

### 現在残っている外部入力

リポジトリ側のprotocol整備と、実際の価値実証を分ける。

現時点で本issueを完了できない主な理由は、**第三者協力者またはそれに準ずる外部評価機会で、本人の実資料・本人が妥当と認める匿名化資料・現実的な代替資料のいずれかを使ったsessionを、まだ実行していないこと**である。

また、AI/provider/network/storage等のruntime data pathは、実際に使う環境と資料条件に依存するため、リポジトリ上の一般論だけで事前確定しない。各sessionの実資料投入前に `third-party-value-session-launch-checklist.md` で確認する。

このため、協力者がいない間に次を追加しても、本issueの主要な不確実性は減らない。

- 新しい価値KPI。
- 個人追跡テレメトリ。
- 第三者実証専用の新しいproduct schema/API。
- 既存protocolと重複する同意・観察・分析文書。
- 内部dogfoodだけを用いた第三者価値の代替判定。

### session開始時の入口

第三者協力者または外部評価機会が得られたら、次の順で開始する。

1. operatorは `third-party-value-validation-execution-plan.md` を正本として確認する。
2. 参加者には `third-party-value-participant-brief.md` の範囲を説明し、KJ Atlasの価値仮説を先に教えてbaselineを誘導しない。
3. 最初の実資料投入前に `third-party-value-session-launch-checklist.md` を埋め、runtime data pathと保存範囲が不明なまま進めない。
4. `GO` または妥当な `GO-WITH-REDUCTION` の場合だけsessionを進め、`third-party-value-session-record-template.md` に生の観察を記録する。
5. session後の公開可否は参加同意と分け、`third-party-value-publication-boundary.md` に従う。
6. V1/V2の材料が得られた後、`third-party-value-analysis-plan.md` の順序でKJ統合し、結果を本issue、`PRODUCT-POSITION-01`、必要に応じて `PRACTICE-CULTURE-01` へ戻す。

`STOP-DATA-BOUNDARY`、`STOP-PARTICIPANT`、既存手段で十分という判断も有効な結果である。完遂を目的化しない。

## 対応方針

- 実施すること:
  1. 第三者協力者が、自分の実資料または本人が妥当と認める匿名化資料を用いて、素材投入→カード化→束ね/表札→配置→保留/異論→叙述/共有確認までの一連を実施する。
  2. 利用前に、同じ仕事を現在どの道具・手順で行っているか、何が負担かを記録する。KJ Atlasの価値語彙を先に教えて誘導しない。
  3. 利用中は、価値が立ち上がった瞬間だけでなく、混乱、違和感、余計な操作、既存手段の方が良い場面も生カードとして保存する。
  4. 利用後に「成果へ戻って根拠を辿れるか」「保留/異論が消えていないか」「再編成しやすいか」「次回も使う理由があるか」を、成果物と本人の説明の双方から確認する。
  5. 最初の候補文脈と、異なる実践文化の文脈を少なくとも1つ比較し、価値が特定文化の作法に依存していないかを確認する。
  6. 「使わない」「既存手段で十分」「この方法自体が合わない」という判断を、改善要求へ自動変換せず、そのまま反証カードとして保持する。
  7. 内部dogfoodで強く支持された価値仮説ほど、第三者観察で同じ言葉を誘導せず、独立に現れるかを確認する。
  8. 第三者観察を既存ADR/KJ/価値分類へ直ちに収容せず、生材料として一度保持してから統合する。
  9. 観察結果は個人追跡テレメトリではなく、同意を得た匿名化メモ・成果物差分・本人の評価理由として保持する。
- 実施しないこと:
  - 利用者行動の常時収集、個人スコアリング、無断テレメトリ。
  - 「KJ法として正しいか」を利用者評価の代わりにすること。
  - 価値仮説に合わない観察を失敗データとして捨てること。
  - 利用拒否/離脱をすべて「UIを直せば採用される」という機能要求へ読み替えること。
  - 実利用前に新ADRを増やして価値仮説を固定すること。

## 受入条件

- [ ] 主たる beachhead 候補の第三者が、自分の題材で一連の意味探索を完遂または明確な停止理由を記録する。
- [ ] 異なる実践文化の第三者または同等の比較ケースを1件以上含め、共通価値と文化依存の摩擦を分けて記録する。
- [ ] 「価値があった」という感想だけでなく、どの素材・操作・成果物に対して何が変わったかを追跡できる証拠が残る。
- [ ] 既存手段を使い続ける方がよい理由、切替理由が生じなかった場面も同じ粒度で残る。
- [ ] 少なくとも1つの内部価値仮説について、第三者材料が `support / modify / narrow / reject / unresolved` のどれを要求するか判定できる。
- [ ] 第三者の「不要/不適合」判断を改善issueへ変換せず保持できるケースを、存在する場合はそのまま残す。
- [ ] 結果から `PRODUCT-POSITION-01` の一次利用仕事・switch reason を支持/修正/棄却できる。
- [ ] `COGNITIVE-DOGFOOD-01` で得た内部所見と第三者所見が衝突する場合、内部dogfoodを優先せず矛盾として保持する。
- [ ] 実使用摩擦が `ADR-0047` のADRトリガーに該当する場合だけ、別途ADR候補を起票する。

## 検証計画

- 実行する確認:
  - `python 01_Plans/dogfood/validate_third_party_value_protocol.py` でprotocol不変条件を確認する。
  - 実利用セッションごとに `Context / Existing workflow / Raw observations / Artifact evidence / Friction / Value moment / Reuse intent / Counterevidence / No-use reason` を記録する。
  - 観察カードはあらかじめ用意した分類へ押し込まず、`00_Prompt/kj_technique.md` に従って訴えの類似性から束ねる。
  - 文化的体系はカード分類器ではなく、調べ落とし（権威、合意、匿名性、根拠、再現性、時間軸、アクセシビリティ等）を補う探索レンズとして使う。
  - 内部dogfood由来の価値仮説と第三者由来の観察を別provenanceで保持し、統合時にどちらから出たかを消さない。
- 期待結果:
  - KJ Atlasを使う実在の理由が少なくとも1つ具体的な利用仕事と結び付く、または価値仮説を縮小/修正すべき反証が得られる。
  - 内部自己改善循環に対して、第三者観察が実際に判断を変更し得る外部入力として機能するかを確認できる。
  - 成功・不成功のどちらでも、次に何を実装/文書化/停止すべきかをissueへ変換できる。ただし「何もしない/その市場を狙わない」も正当な結果として許容する。

## 補足

- 依存: 第三者協力者またはそれに準ずる外部評価機会。
- リポジトリ側の準備: 第三者sessionの実行・記録・公開境界・分析protocolとvalidatorは準備済み。これらの存在だけでは受入条件を満たさない。
- 停止基準: 協力者がいない段階でKPIを固定しない。実利用証拠なしにVR4/VR5を前倒ししない。
- 認識上の停止基準: 第三者観察が既存仮説の言い換えだけになり、独立した反証可能性を失った場合は検証設計を見直す。
- ADR候補化条件: 実使用で、データ契約・権限・安全境界・共有意味論・不可逆なワークフロー契約を横断的に変更する必要が生じた場合だけ `ADR-0047` に従って起票する。