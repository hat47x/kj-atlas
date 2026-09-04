# Issue: COGNITIVE-DOGFOOD-01 KJ Atlas自身の発展議論をキャンバス上で行い、認知環境としての価値を検証する

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Process
- Status: In Progress
- Source Issue: N/A
- Priority: P0
- Owner: Maintainer
- Scope: `01_Plans/dogfood/`, `01_Plans/issues/`, `04_Documentation/`
- Related ADR/Spec: `ADR-0032`, `ADR-0042`, `ADR-0047`, `ADR-0057`, `00_Prompt/kj_technique.md`, `00_Prompt/w_type_iterative_inquiry_requirements.md`, `01_Plans/issues/issue-DOMAIN-W-ITERATION-01-w-type-cumulative-inquiry-support.md`
- Expected verification level: docs-check

## 課題

- 現在の問題:
  - 現行dogfoodは、KJ Atlasを実際に操作してAPI/UI/大規模データ/AI提案の不備を発見するデバッグ・実規模検証として大きな成果を上げている。
  - 同時に、`doc_kj_atlas_dogfood_r1.json`〜`r5.json` では、**R1 問題提起 → R2 現状把握 → R3 本質追求 → R4 構想 → R5 具体策**として、KJ Atlas自身の開発プロセスをキャンバスで検討する試行が既に存在する。設計原理の硬直、文書ドリフト、AI協働、自律性など、単なるUIデバッグを超える題材も扱っている。
  - ただしR1〜R5は、通常チャット等との比較対照、認知制御の失敗指標、`cultural-substrate-weaving` との要因分離を持たないため、「キャンバスを使ったことが思考の質をどれだけ変えたか」は独立に評価できない。
  - 生成AIとの長いチャットだけでも大量の設計案は生成できるが、文脈の流れに引かれた早期収束、過去論点の埋没、もっともらしい分類、異論や少数カードの消失、根拠からの遊離を検出しにくい。
  - 一方、長期再訪・分岐・不変成果・カード系譜を支える基盤を本issueのために新設する必要はない。`DOMAIN-W-ITERATION-01` では `InquiryJourneyV1`、不変 `RoundSnapshotV1`、`RoundHandoffV1`、`CardLineageEdgeV1`、自己完結bundle、比較、分岐、再開、backend保存まで実装・検証が進み、2026-08-25時点でAC-1〜AC-13は全件完了している。
  - `DOMAIN-W-ITERATION-01` に残るT9は「Phase 2の実使用後にPhase 3 proposal-only AI支援を別issueへ分割するか判断する」であり、現時点の停止理由は実使用フィードバック不足である。認知dogfoodは、この判断へ実在する利用摩擦を供給できる候補である。
- 利用者または開発への影響:
  - KJ Atlasが自らの開発において継続的に有用なら、単なる「KJ法のデジタル実装」ではなく、人間と生成AIが長期に複雑な問題を考えるための認知環境として価値を持つ可能性がある。
  - 逆に、通常チャットや文書・issue管理に対して実質的増分がないなら、その方向へプロダクト価値を過大拡張すべきではない。
  - InquiryJourneyの手動中核で実務を回せる/回せない箇所を観察できれば、T9を「AIがあると便利そう」という設計想像ではなく、現実の不足から判断できる。

## 既存dogfood資産の位置づけ

R1〜R5は新レーン以前の**探索的ケース0**として扱う。後から都合よく成功例へ読み替えないため、元JSONを変更せず次を監査する。

- R1で立った問題がR2〜R5でどう生存・変形・消失したか。
- 元カードの出所から最終具体策へ戻れるか。
- 孤立、対立、保留、不確実性が途中で消えていないか。
- キャンバスでなければ発見しにくかった所見と、通常の段階的問題解決でも得られた所見を分けられるか。
- R1〜R5から実際に生じたADR/issue/実装のうち、後に維持・訂正・撤回されたものは何か。

ケース0は比較armを後付けして完全な実験へ変換しない。既存成果の観察記録として使い、正式比較は新規ケースで行う。

## 検証仮説

> KJ Atlasのキャンバスを、実在するソフトウェア開発課題の探索・統合・意思決定に用いると、通常の生成AIチャットだけの場合より、根拠接地、異論保持、探索範囲、再訪性、訂正可能性が改善し、早すぎる収束と文脈依存の忘却が減る。

価値は「回答文が長い」「案の数が多い」ではなく、後から検証可能な認知成果で判定する。

## 既存 InquiryJourney との責任分界

認知dogfoodは、長期履歴・分岐・系譜の別schemaを作らない。

- **KJ Atlas製品上の長期探究状態**: `InquiryJourneyV1` / `RoundSnapshotV1` / `RoundHandoffV1` / `CardLineageEdgeV1` を使用する。
- **比較実験の再現条件**: `cognitive-dogfood-run-record-template.md` の source snapshot / model / arm / proposal ledger / blind review を使用する。

この二つは目的が異なる。

- Git commit SHAで固定する「experiment source snapshot」は、A〜Dが同じ入力を読んだことを再現するための実験条件であり、利用者向けInquiryJourneyの代替ではない。
- `RoundSnapshotV1` は、人が意味を確認した探究上の節目を非破壊で残す製品機能であり、モデルversionやarm割当等の実験メタデータを背負わせない。

また、Case 001の **experiment Round 1 / Round 2**（内部資料のみ / 外部資料追加）をW型 `RoundStage` と機械的に対応させない。資料追加後も同じ「現状把握」を続けるなら同段階の反復になり得るし、問いの意味が変わったと人間が判断した場合だけ別stageへ進む。実験都合で6段階を固定ウィザード化しない。

## 対応方針

- 実施すること:
  1. R1〜R5を探索的ケース0として監査し、既存の認知dogfoodが何を既に達成/未検証か整理する。
  2. KJ Atlas自身の未解決かつ開いた問題を新規dogfood題材にする。Case portfolioで、プロダクト価値、AI支援境界、local/offline/self-hostとcollaborationの3種類を事前登録する。
  3. GitHub上のADR/issue/コード/dogfood観察/外部リサーチを生材料としてカード化し、出典を保持する。
  4. C/D armでは、現行InquiryJourneyの手動中核を可能な範囲で実際に使い、人が確認した意味上の節目をsnapshotとして残す。比較実験の便宜だけでstageを進めない。
  5. 生成AIはカード化、探索質問、束ね候補、表札候補、反対視点、空白探索、B型叙述などをproposalとして支援するが、人間の確定操作を置き換えない。
  6. 既存の分類体系・ADR構造へ最初からカードを押し込まず、生カード→束ね→表札→配置→空白→追加探索の順序を守る。
  7. 最終成果をissue/ADR/実装候補へ変換した後、元カード・根拠・保留・異論へ戻れるかを確認する。
  8. 同じ問題を通常AI＋通常文書でも扱い、`COGNITIVE-EVAL-01` の4arm指標で比較する。
  9. InquiryJourney手動中核で「AI支援がないため反復的に困った」場面を、T9用フィードバックとして別に記録する。AIがあれば便利そうという推測だけでは不足扱いしない。
  10. T9候補になった不足は、少なくとも `operation / manual burden / cognitive risk / existing non-AI workaround / proposal-only benefit / automation risk` を記録し、Phase 3の別issue化が必要か判断できる材料へする。
- 実施しないこと:
  - KJ Atlasを使ったという事実だけで方法の優位性を認定すること。
  - R1〜R5を後知恵で実験成功例に作り替えること。
  - 認知dogfood専用の新しい履歴/provenance schemaを作ること。
  - Case 001のexperiment roundをW型stageへ自動対応させること。
  - dogfood中に見つかった全論点をKJ Atlasの機能要求へ変換すること。
  - AIが生成した分類・表札・意思決定を自動確定すること。
  - T9を満たすためにAI支援不足を探しに行くこと。手動中核で不足が出なければ「別issue不要」が正当な結果である。
  - T10の常設メニュー配置を認知dogfoodだけで確定すること。外部デザインレビュー待ちという元の境界を維持する。
  - デバッグdogfoodを廃止すること。認知dogfoodは別レーンとして併存する。

## Dogfoodラウンドの最小構造

1. **問い固定**: 今回何を決めずに探索するのか、終了時に何が分かればよいかを記録する。
2. **材料投入**: 実在するGitHub資料、観察、外部資料、反証材料をカード化する。
3. **未編成保持**: 初期分類を避け、孤立カード・違和感カードを残す。
4. **KJ統合**: 束ね、表札、配置、対立、空白を作る。
5. **追加探索**: 空白や反対視点から必要資料を取りに行く。
6. **節目確認**: C/Dでは意味上の節目ならInquiryJourney snapshot/handoffとして残す。単なる実験Round切替では節目とみなさない。
7. **決定への変換**: issue/ADR/実装/保留へ変換する。
8. **戻し検査**: 決定を元カードへ戻し、未説明・過剰一般化・消えた異論を検査する。
9. **比較記録**: 通常文書との差分と、KJ Atlas固有の摩擦を記録する。
10. **T9フィードバック抽出**: 手動中核のどの反復作業でproposal-only AIが実用上必要/不要だったかを抽出する。

## 受入条件

- [x] R1〜R5をケース0として監査し、既存試行の生存所見・評価不能点・実際の後続変更を記録した。`cognitive-dogfood-case-000-r1-r5-audit.md` を正本とする。
- [x] 3件の新規実在開発課題をCase 001〜003として、Case 001実行前に事前登録した。
- [ ] Case 001〜003で認知dogfoodラウンドを完遂する。
- [ ] C/Dの長期探究状態を、別履歴schemaを作らず既存InquiryJourneyで保持できるか実使用で確認する。
- [ ] 各ラウンドで、最終決定または保留が元資料・カードへ追跡できる。
- [ ] 各ラウンドで、最初の問題設定にはなかった新しい問い/関係/反証/空白のいずれかを記録し、それが対象側で生存するか確認する。
- [ ] 4arm比較でKJ Atlasの増分と摩擦を両方記録する。
- [ ] 「AIがもっともらしくまとめたため見落とした」事例があれば失敗として保存し、隠さない。
- [ ] InquiryJourney手動中核について、T9の判断材料を `AI支援が必要 / 現行手動で十分 / 条件付き / 未判定` のいずれかとして、具体的摩擦とともに記録する。
- [ ] T9でAI支援の不足が再現した場合だけPhase 3別issue候補へ変換し、再現しない場合は起票しない。
- [ ] dogfood由来の製品課題は、実使用摩擦として再現できるものだけ個別issue化する。
- [ ] 横断的・長期的・破壊的な契約変更が必要と確認された場合だけ `ADR-0047` に従いADR候補へ昇格する。

## 検証計画

- 実行する確認:
  - ラウンドごとに `Question / Source snapshot / Raw cards / Emergent structure / Gaps / Counterevidence / Decisions / Rejected proposals / Product friction / Revisit result` を保存する。
  - C/DではInquiryJourneyのsnapshot/handoff/lineageを可能な範囲で使用し、実験記録とは別責務で保持する。
  - 最終成果だけでなく途中の棄却・保留・孤立カードを保持する。
  - `COGNITIVE-EVAL-01` に定義する比較指標を使用する。
  - T9用には、AI不在が実際の障害になった操作だけを抽出し、現行の手動回避策とproposal-only化した場合のriskを併記する。
- 期待結果:
  - KJ Atlasが、少なくとも一部の開いたソフトウェア課題で通常文書より再現可能な認知上の増分を示す、または示さない領域を明確化できる。
  - 長期認知dogfoodが既存InquiryJourneyを重複設計なく利用できるか確認できる。
  - `DOMAIN-W-ITERATION-01` T9を、想像ではなく実使用フィードバックから前進または「現時点ではAI支援不要」と判断できる。

## 補足

- 本issueはデバッグdogfoodの上位互換ではない。目的が異なるため、バグ検出件数を主指標にしない。
- 成果が良くても、利用者一般への価値は `VALUE-REALNESS-01` の第三者検証で別途確認する。
- `DOMAIN-W-ITERATION-01` のACは2026-08-25時点で全件完了している。本issueが狙うのは基盤の再実装ではなく、残るT9へ実使用証拠を返すことである。

### Formal Case package preflight hardening（2026-09-05）

- F1として、正式Case 001〜003を実行する前のassembled arm package検証を強化した。これはCase結果やarm内の推論には触れず、fresh-context比較へ渡す凍結入力の同一性だけを守るpreflightである。
- `validate_cognitive_arm_packages.py` は、従来のtop-level構成・SHA-256・starter空状態に加え、arm別`launch.md`の凍結packetとの完全一致、product/skillのrepository・commit・manifest ID、事前登録source path＋Git blob SHA、実ファイルから再計算したGit blob SHAをfail-closedで照合する。
- Run `33916954615` でdogfood tooling unit test 32件、Cases 001〜003のlaunch treatment equivalence、凍結product source（20/18/18件）とskill canonical source 12件から実組立した全12 arm package、dogfood構造検査、active Issue検査を通過した。
- このcheckpointは「3ケースの正式比較を完了した」証拠ではない。未完受入条件はそのまま維持し、正式armは引き続き別fresh sessionで実行する。
