# 認知dogfood Case 001 — KJ Atlasの存在目的と一次利用仕事

- 状態: 準備済み / 入力凍結済み
- 準備日: 2026-08-29
- KJ Atlas product snapshot: `main@2232b3bb26647e5c4a083f55bdbf83c161698649`
- B/D用cultural-substrate-weaving method snapshot: `main@3988e12e5f7f316f377d3391e9486c8467a111d5`
- 関連する実験統治: `COGNITIVE-DOGFOOD-01`, `COGNITIVE-EVAL-01`

## 1. 固定する問い

> KJ Atlasは、既存のAIチャット、ホワイトボード、質的分析ツール、文書/issue管理では十分に満たしにくい、どの利用仕事のために存在するべきか。現在の設計・実装・dogfoodは、その価値をどこまで実現し、何をまだ実証できていないか。

このCaseでは、最初から「KJ Atlasは認知環境である」「KJ法市場を狙う」「offline / self-hostが主な価値である」といった結論を固定しない。

## 2. 実験入力と評価資料を分離する

### 2.1 全Armへ渡す製品資料

全Armへ、KJ Atlas `main@2232b3bb26647e5c4a083f55bdbf83c161698649`の同一資料を渡す。実際の入力の正本は`cognitive-dogfood-case-001-round1-source-manifest.json`とする。

固定済みの20資料は次のとおり。

- `README.md`
- `ROADMAP.md`
- `00_Prompt/kj_technique.md`
- `01_Plans/adr/ADR-0032-product-value-realization-model.md`
- `01_Plans/adr/ADR-0042-value-realness-validation-and-notice-exit.md`
- `01_Plans/adr/ADR-0047-design-decision-adr-saturation-and-execution-first.md`
- `01_Plans/adr/ADR-0057-w-type-cumulative-inquiry-model.md`
- `01_Plans/issues/TEMPLATE.md`
- `01_Plans/issues/issue-VALUE-MEASURE-01-measurement-harness-and-evidence-artifacts.md`
- `01_Plans/issues/issue-VR-ROADMAP-01-value-to-social-goal-phase-baseline.md`
- `01_Plans/issues/issue-DOMAIN-W-ITERATION-01-w-type-cumulative-inquiry-support.md`
- `01_Plans/dogfood/doc_kj_atlas_dogfood_r1.json`
- `01_Plans/dogfood/doc_kj_atlas_dogfood_r2.json`
- `01_Plans/dogfood/doc_kj_atlas_dogfood_r3.json`
- `01_Plans/dogfood/doc_kj_atlas_dogfood_r4.json`
- `01_Plans/dogfood/doc_kj_atlas_dogfood_r5.json`
- `01_Plans/issues/done/issue-DOGFOOD-17-opposing-viewpoint-ignores-target-claim.md`
- `01_Plans/issues/done/issue-DOGFOOD-20-card-groups-not-theme-based.md`
- `01_Plans/issues/done/issue-DOGFOOD-31-two-hundred-card-scale-exceeds-ai-operation-limits.md`
- `01_Plans/issues/done/issue-DOGFOOD-32-one-line-heading-hierarchy-missing-for-large-canvases.md`

### 2.2 Armへ渡さない資料

次は今回の問いに対する仮説や評価設計を含み、答えを先に教える可能性があるため、Armの分析入力から除外する。

- PR #2805で追加した`PRODUCT-POSITION-01`。
- `VALUE-REALNESS-01`。
- `PRACTICE-CULTURE-01`。
- `COGNITIVE-DOGFOOD-01`。
- `COGNITIVE-EVAL-01`。
- `cognitive-dogfood-case-000-r1-r5-audit.md`。
- `cognitive-dogfood-case-000-outcome-trace.md`。
- 本Case文書の評価節・判定基準。
- cultural-substrate-weaving PR #5の評価protocol。

これらは実験の操作者・評価者だけが参照し、Armの分析内容へ混入させない。詳細な除外条件は`cognitive-dogfood-case-001-contamination-exclusions.md`を正本とする。

### 2.3 B/Dだけが使用する方法資料

Arm B/Dには、`cultural-substrate-weaving main@3988e12e5f7f316f377d3391e9486c8467a111d5`を方法条件として使用させる。

これは製品について追加の事実を与える資料ではなく、探索とKJ統合の方法条件である。A/Cには見せない。

## 3. 二段階で資料を投入する

### Round 1 — 内部証拠だけを使う

固定済みのKJ Atlas repository snapshotだけで分析する。

目的は次の2点である。

- 外部の市場カテゴリや競合の言い回しに先に引かれず、KJ Atlas自身の設計、実装、dogfoodから利用仕事を立ち上げられるかを見る。
- repository内に共存する時間差、訂正、矛盾を適切に扱えるかを見る。

### Round 2 — 全Armへ同じ外部資料を追加する

Round 1のraw resultを全Armで固定した後、競合、研究、実践知の共通manifestを全Armへ同じ条件で追加する。

目的は次の2点である。

- Round 1で生じた内部仮説が、外部比較によって維持・修正・棄却されるかを見る。
- 外部資料を最初から与えることで、市場カテゴリへ早期に固定される影響を避ける。

あるArmだけが新しい外部資料の必要性に気づいた場合、そのArmの結論へ即時に混ぜない。`Candidate source request`として保留し、次のcommon roundで全Armへ同じsnapshotを追加する候補とする。

Round 2の外部資料manifestは、Round 1開始前に`cognitive-dogfood-case-001-round2-external-manifest.md`として事前登録済みである。

## 4. 自然発生した矛盾・旧情報を評価資源として使う

固定snapshotには、後から訂正された主張が実際の開発履歴として含まれている。これを、AI依存校正、時間的推論、根拠接地を観察する自然な確認材料として使う。

### T1 — 三要素チェック

- R3には、「三要素牽制設計法はあるがissue templateに三要素チェック欄がない」という当時の問題提起がある。
- 同じsnapshotの現在の`01_Plans/issues/TEMPLATE.md`には、`ADR-0067`を参照する三要素整合欄が存在する。

評価時には、次を区別する。

- R3の過去カードを現在の未解決課題としてそのまま採用した場合は、temporal / provenance failureとする。
- 「当時は問題だったが、現在は契約へ反映済み」と時点を分けられた場合は、正の証拠とする。

### T2 — 大規模階層UI

- `DOGFOOD-32`は初期記述で、階層UI / workflowを未実装と評価した。
- 同issueの後段では、`summaryView`、`hierarchyLevel`、`abstractMapView`等がすでに実装済みであり、初回評価は過大だったと訂正されている。

評価時には、次を区別する。

- issueタイトルや前半だけを読み、「現在も未実装」と結論した場合はanchoring / stale-evidence failureとする。
- 訂正を反映し、残課題を1000枚実規模E2E等へ縮小できた場合は、M2 / M4 / M5の正の証拠とする。

### T3 — grounding全件化案と10件の品質ガード

- `DOGFOOD-31`の初期対応案には、大規模な島で全メンバーへgroundingを広げる案がある。
- 後段の実施結果では、10件上限を品質ガードとして維持し、代表的な根拠への接地へ方針を修正している。

評価時には、初期案を現在の契約として扱わず、経緯を「要求 → 検討 → 修正された判断」として扱えるかを見る。

T1〜T3は、偽情報を人工的に注入したテストではない。実開発の訂正履歴を利用して、時点差とAI校正を観察するためのconflict-bearing sourceである。

## 5. 4つのArm

### Arm A — 通常AI + 通常文書

- KJ Atlasキャンバスを使わない。
- `cultural-substrate-weaving`を使わない。
- 共通資料から問いへ回答し、課題、価値、提案をまとめる。
- 一般的な分析用の見出しやメモは使用してよい。ただし、KJ固有のカード、束ね、表札手順を実験者側から要求しない。

### Arm B — 通常AI + cultural-substrate-weaving

- KJ Atlasキャンバスを使わない。
- `cultural-substrate-weaving`を明示的に適用する。
- 体系由来の所見はremoval / substitution等を通し、対象側で生き残ったものだけを最終成果へ残す。

### Arm C — KJ Atlas + 通常AI

- KJ Atlas上で、生カード、束ね、表札、関係、空白、反対視点を扱う。
- `cultural-substrate-weaving`は使わない。
- AI提案はproposal-onlyとし、人間が採否を確定する。

### Arm D — KJ Atlas + cultural-substrate-weaving

- Arm Cの外部表象に加えて、`cultural-substrate-weaving`を適用する。
- 文化的体系をカードの分類器には使わず、探索対象、空白、関係候補を広げるために使う。
- 体系語を除去した後も対象側で生き残る所見だけを最終成果へ残す。

## 6. 実行時の入力汚染を防ぐ

- 各Armは独立したfresh contextで開始する。
- 他Armの中間成果を見せない。
- Armを実行するmodelには、PR #2805で作成した価値仮説を渡さない。
- 新しい外部資料が必要になった場合、そのArmだけで結論まで使い切らず、追加資料候補として記録する。次のcommon roundで全Armへ同じ条件で追加する。
- Case 001の実行順は、事前登録済みの **C → D → B → A** を維持する。
- 最終成果を比較するreviewerにはArm名を伏せる。
- 操作者が既存仮説を知っていることによる期待効果を避けるため、blind reviewerには「どの答えが既存のPRODUCT-POSITION仮説に近いか」を評価させない。

## 7. 全Arm共通の成果物

各Armは、少なくとも次を返す。

1. KJ Atlasが解こうとしている利用者の仕事。
2. 既存手段で十分な領域と、不十分になり得る領域。
3. 現在のKJ Atlasがすでに実現している価値。
4. まだ実証されていない価値仮説。
5. 最も重要な反証、または「KJ Atlasが不要かもしれない条件」。
6. 次に実施すべき検証 / issue。
7. 主張ごとの主要根拠と、その根拠の時点。
8. 読んだ資料の中で、訂正、矛盾、旧情報と判断した箇所。
9. 判断を保留した箇所と、追加で必要な証拠。

Arm C/Dでは加えて、最終成果から元カードへ戻れる状態を保持する。

## 8. AI提案の記録

M5を測定できるよう、各Armで少なくとも次を保存する。

- `proposal`: AIが提示した主張、分類、比較、判断。
- `evidence`: その提案が参照した資料。
- `human_action`: accept / modify / reject / defer。
- `reason`: 採否理由。
- `later_verdict`: 後続資料またはblind reviewで確認された妥当性。

通常チャットでも、最終成果だけでなく、重要な中間提案をこの形式へ抽出する。

## 9. 評価

`COGNITIVE-EVAL-01`のM1〜M9を使用する。

Case 001では、特に次を重視する。

- M1 生存所見: 基準線にはなく、対象へ戻しても残る重要所見。
- M2 根拠接地: 価値主張が実装、ADR、dogfood観察へ接地し、時点を区別しているか。
- M3 異論・残差保持: 「KJ Atlasは不要かもしれない」という材料を保持できるか。
- M4 早期収束耐性: 既存の価値原則、issueタイトル、初期記述を前提に結論を固定していないか。
- M5 AI依存校正: T1〜T3を含む古い・訂正済み主張を適切に棄却・更新できるか。
- M6 再訪・訂正可能性: 後の第三者実利用結果によって価値定義を修正できるか。
- M8 決定への変換品質: 実行可能な価値検証やissueへ変換できるか。

## 10. Case 0との関係

R1〜R5は、既存の探索的なCase 0として`cognitive-dogfood-case-000-r1-r5-audit.md`で監査する。

Case 0の結果を、Case 001の正解表として使用しない。Case 0から引き継ぐのは、対照条件、棄却履歴、不変provenance、摩擦観察が不足していたという**実験設計上の教訓**だけである。

## 11. 完了条件

- [x] KJ Atlas共通sourceのcommit SHAを固定した。
- [x] B/D用cultural-substrate-weavingのcommit SHAを固定した。
- [x] Arm入力からPR #2805の回答仮説を除外した。
- [x] repository内の自然な訂正履歴をT1〜T3として事前登録した。
- [x] Round 2の外部資料manifestを、Round 1開始前に全Arm共通条件として固定した。
- [ ] Round 1のA〜Dを独立して実行した。
- [ ] Round 1のraw resultとAI提案ログを保存した。
- [ ] Arm名を伏せた比較reviewを実施した。
- [ ] Round 2を実行し、内部仮説の維持・修正・棄却を比較した。
- [ ] M1〜M9について、測定可否と結果を記録した。
- [ ] product / skill / caller-domain / model-experimentの帰属を行った。
- [ ] 増分なし・悪化を含む結果を、そのまま保存した。
- [ ] 新しいADRは、`ADR-0047`のトリガーが成立した場合だけ起票した。