# 認知dogfood 実行計画

- 状態: P0完了、P1実行準備済み
- 日付: 2026-08-30
- 対象: PR #2805 における認知dogfood / プロダクト価値検証
- 関連issue memo: `COGNITIVE-DOGFOOD-01`, `COGNITIVE-EVAL-01`, `PRODUCT-POSITION-01`, `VALUE-REALNESS-01`, `PRACTICE-CULTURE-01`, `DOMAIN-W-ITERATION-01`
- 関連ADR: `ADR-0047`（execution-first / ADR再起票条件）

## 1. この文書の役割

既存のissue memoは「何を検証するか」を、各Caseの実行資料は「各Armをどう実行するか」を定義している。本書はその間をつなぎ、**どの順序で進め、どの証拠が揃ったら次の段階へ移るか**を管理する。

本書を新しい意思決定の正本にはしない。長期的な判断はADR、実行課題はissue memo、各runで実際に起きたことはrun record、製品上の探究状態はInquiryJourneyを正本とする。

## 2. 上位原則

1. **計画を先に固定し、その後にdogfoodする。** 実行結果を見てから、問い、Case、評価軸、資料集合を都合よく変更しない。
2. **実在する開発課題を使う。** ベンチマークのためだけに作った人工問題を主対象にしない。
3. **比較可能性を守る。** A〜Dへ同じ問いと同じ製品資料を与え、方法以外の情報差を作らない。
4. **KJ操作そのものを成功条件にしない。** 新しい所見、反証、訂正、根拠への接地、再訪可能性、意思決定の改善がなければ、認知上の増分があったとは扱わない。
5. **製品機能の不足とAI支援の不足を混同しない。** 手動中核で操作できない問題は、まずbug / UX / domain gapとして扱う。
6. **外部現実へ開く。** 内部dogfoodの成功を第三者価値の証明にしない。最終的に`VALUE-REALNESS-01`へ接続する。
7. **ADRを先回りして増やさない。** `ADR-0047`のR-1〜R-4のいずれかを実使用で確認した場合だけADR候補にする。

## 3. 実行フェーズと移行条件

### P0 — 計画と入力の凍結

目的は、Case 001〜003の比較条件を、結果に応じて後から動かせない状態にすることである。

完了済みの項目:

- [x] Case 001〜003の固定問いを事前登録した。
- [x] Round 1の製品snapshotを`main@2232b3bb26647e5c4a083f55bdbf83c161698649`に固定した。
- [x] B/Dで使用するskill snapshotを`cultural-substrate-weaving@3988e12e5f7f316f377d3391e9486c8467a111d5`に固定した。
- [x] Round 2の外部資料manifestをRound 1開始前に固定した。
- [x] M1〜M9、自然発生した訂正・時点差チェック、run record、invalid条件を固定した。
- [x] InquiryJourney Phase 2の実使用と、T9の横断判定条件を固定した。
- [x] Case 001のArm実行順を固定した。
- [x] Case 001〜003 × A〜D、計12件のActions artifactを同一ハーネスから生成できるようにした。
- [x] launch packet、frozen source、skill source、starter documentの整合をCIで検証するようにした。
- [x] raw runのstatic intakeとblind package生成をfail-closedにした。

### Case 001のArm実行順

固定snapshot文字列

```text
case-001|2232b3bb26647e5c4a083f55bdbf83c161698649|3988e12e5f7f316f377d3391e9486c8467a111d5
```

のSHA-256先頭64bitをseedとしてA〜Dをshuffleした結果を、実行前に登録した。実行順は **C → D → B → A** とする。

この順序はArmの優劣を意味しない。各Armは独立した新規コンテキストで開始し、先に実行したArmの出力を後のArmへ渡さない。

P0の終了条件:

- 現在は**完了**として扱う。
- 最初の有効なraw runを保存した後は、問い、M1〜M9、訂正・時点差チェック、Round 1 source snapshot、Arm treatment、required outputを変更しない。
- 実験を継続できない欠陥が見つかった場合は、既存条件を上書きせずdeviationとして記録する。

---

### P1 — Case 001 / Round 1 実行

目的は、内部repository資料だけを用いて4Arm比較を成立させることである。

実行順:

1. Arm C — KJ Atlas + ordinary AI
2. Arm D — KJ Atlas + cultural-substrate-weaving
3. Arm B — ordinary document + cultural-substrate-weaving
4. Arm A — ordinary AI / ordinary document

各Armは、`Cognitive dogfood freeze` workflowが生成した、そのCase・Arm専用のActions artifactを入力として使用する。実際に使用したartifactについて、name / workflow head SHA / digestをrun recordへ残す。

各Armの完了条件:

- raw artifactを、評価前の状態のまま保存する。
- required outputをすべて保存する。
- AI提案を用いた場合はproposal ledgerを残す。
- M1〜M9について、観察内容または「測定できない」とその理由を記録する。
- 訂正・時点差チェックはrun終了後に評価し、単なる検出フラグだけでなく解釈本文を残す。
- C/DではKJ Atlas document / InquiryJourneyへの参照を保存する。
- C/DではT9に関係する手動摩擦を記録する。
- contamination / deviationの有無と内容を明示する。
- `validate_cognitive_run_records.py`のstatic intakeに合格する。

P1の終了条件:

- 有効なArmが4件揃う。
- 無効なArmがあれば、そのArmだけを同じ条件で再実行する。
- 4Armが揃う前に、どの方法が優れていたかを決めない。
- static intakeに合格していないrunをblind reviewへ送らない。

---

### P2 — Blind review / Round 1統合

目的は、方法名への期待や先入観ではなく、成果物そのものを比較することである。

実施内容:

- static intakeに合格したrunから、Arm名と方法説明を外したblind packageを作る。
- builder自身もrun validatorを実行し、invalid / contaminated / incompleteなrecordからblind packageを生成しない。
- primary job、反証、現在実現できている価値、未実証仮説、次の検証、保留事項を比較する。
- M1の論点数だけでなく、M2 / M3 / M4 / M5 / M6の失敗を優先して読む。
- 特定のArmだけで生き残った所見は、元の証拠まで戻って確認する。
- C/Dにだけ生じた摩擦を、有益な認知的強制と無益な操作負担に分ける。

P2の終了条件は、少なくとも次を区別して記録できることである。

1. 通常AIだけでも十分に得られた所見。
2. cultural-substrate-weaving単体で増えた所見。
3. KJ Atlasの外部表象によって増えた所見。
4. Dでのみ生じた相互作用。
5. 方法を増やしたことで悪化した所見。
6. どのArmでも証拠が不足していた点。

この段階では、Case 001だけを根拠に製品価値やskill価値を確定しない。

---

### P3 — Case 001 / Round 2 外部反証

目的は、Round 1でKJ Atlas固有だと思えた価値を、既存製品、研究、隣接実践との比較によって積極的に削り、残るものを確かめることである。

- 事前登録済みmanifestに含まれる資料だけを、全Arm共通の追加資料として使用する。
- Miro / ATLAS.ti / Dovetail等ですでに満たされる価値は、KJ Atlas固有の価値候補から外す。
- local-first / Design Justice / CARE / human-AI cognition研究は、対象を分類する正解表としてではなく、反証や遺漏防止の資料として使う。
- 追加資料が必要になった場合はcandidate source requestへ置き、一部のArmだけに追加しない。

P3の終了条件:

- 「KJ Atlasに固有である可能性が残る価値」と「業界ですでに一般化している価値」を分離できる。
- primary job仮説を、維持・修正・棄却のいずれかへ更新できる。
- `PRODUCT-POSITION-01` / `VALUE-REALNESS-01`へ戻せる具体的な証拠がある。

---

### P4 — Case 001 findingの振り分け

目的は、観察結果を無差別にissueやADRへ変換しないことである。

#### F0 — Run record / KJ cardのまま保持

原則として次はF0に留める。

- 単一runだけで生じた違和感。
- 反証可能だが、まだ再現していない仮説。
- 外部証拠を待っている候補。
- 「便利そう」という印象だけの機能案。
- cultural-substrate-weavingを一度使っただけで得たframework上の所見。

#### F1 — 既存issueへ戻す

次を満たす場合、新しいissueを作らず、既存memoへ実使用証拠を戻す。

- 既存の受入条件やT9等が、その種類の実使用証拠を明示的に待っている。
- 既存Decisionの範囲内で実装・UX・検証を改善できる。
- 新しいissueを作っても、同じproblem statementを別名で重複させるだけになる。

代表例: InquiryJourneyの実使用摩擦 → `DOMAIN-W-ITERATION-01` T9 / 関連する既存issue。

#### F2 — 新しいissue memo

次をすべて満たす場合にだけ起票する。

- 実際のrun / evidenceで再現可能な課題がある。
- 既存issueの受入条件では扱えない。
- 実行可能な変更または検証を具体化できる。
- acceptance criteriaとverification levelを書ける。
- 長期Decisionを新たに固定しなくても着手できる。

issue化した後も、生カードやrun evidenceへの参照を残す。

#### F3 — ADR候補

`ADR-0047`に定めた次のトリガーのいずれかを、証拠付きで満たす場合だけ候補にする。

- R-1: 実使用摩擦によって設計trade-offの判断が必要になった。
- R-2: 外部協力者や実利用者の継続参加などにより、プロダクトの段階が変わった。
- R-3: 既存の非機能予算・不変条件を越える必要が生じた。
- R-4: schema version gateを越える破壊的契約変更が必要になった。

「価値がありそう」「思想的に重要」「複数issueに影響しそう」という理由だけではADRにしない。

P4の終了条件:

- 各findingにF0 / F1 / F2 / F3のいずれかを付ける。
- 元のrun evidenceがないF2 / F3は起票しない。
- F3候補はADRを書く前に、既存ADRで本当に扱えないかを再確認する。

---

### P5 — Case 002 / 003

Case 001の結果にかかわらず、事前登録したCase順を維持する。

- Case 002: AI proposalと人間判断・認知摩擦の境界。
- Case 003: local / offline / self-host と collaboration の製品境界。

各CaseでP1〜P4に相当する実行・比較・振り分けを行う。

3Caseが終了した後に初めて、次を横断的に判定する。

- KJ Atlasによる増分の再現性。
- cultural-substrate-weavingによる増分の再現性。
- Dにおける正または負の相互作用。
- M1の増分に対するM9の負担。
- M2 / M5 / M6に関する認知制御の改善。
- skill変更候補の再現性。
- InquiryJourney T9におけるPhase 3 AI支援ゲートの成立・不成立。

---

### P6 — 第三者価値の実在確認へ接続

内部の認知dogfoodで得たprimary job / switch reasonは、第三者検証へ渡す**仮説**であり、結論ではない。

`VALUE-REALNESS-01`では、実利用者または協力者が自分の資料を持ち込んだときに、少なくとも次を観察する。

- 使う理由。
- 使わない理由。
- 既存workflowへ戻る理由。
- 実際に価値を感じた瞬間。
- evidence / dissent / revisitのうち、実利用では不要だったもの。
- KJ Atlas内部では重要だと考えていた価値が、外部では価値にならない反例。

外部現実と内部dogfoodが衝突した場合、外部側を「理解不足」として退けない。その衝突自体を、次のKJ材料として扱う。

## 4. 計画文書を変更するときの扱い

実行開始後も計画文書の修正自体は禁止しない。ただし、比較の正当性を守るため、次の2種類を明確に分ける。

### 比較条件を変えない修正

- 誤字脱字や不自然な日本語の修正。
- broken link / source pathの補正。
- 実行記録に不足していた欄の追加。
- product / skill / experimentの帰属を明確にする注記。
- 実験結果と無関係なrunbook改善。
- 重複した旧toolや旧手順への参照の撤去。

これらは通常のcommitとして修正する。ただし、Armへ渡す凍結済みlaunch packetやsource集合を変更してはならない。

### 比較条件を変える修正

- 固定問いの変更。
- Arm treatmentの変更。
- M1〜M9の定義変更。
- source snapshotの差し替え。
- required outputの変更。
- 成功条件やissue化閾値の変更。

最初の有効なraw run後に必要になった場合、既存revisionを上書きしない。「なぜ旧設計では測れなかったか」を残し、次のCaseまたは次revisionから適用する。

## 5. 現時点のADR / issue起票判断

現時点では、新しいADRトリガーは確認していない。

また、認知dogfoodの実行順、blind review、finding triage、実験用bundle生成、static intake等は、`COGNITIVE-DOGFOOD-01` / `COGNITIVE-EVAL-01`の実行手順を具体化したものである。これらだけを理由に、独立した新issueを作らない。

次に新しいissue / ADRの起票判断を行うのは、Case 001の実測findingがP4へ到達した時点とする。