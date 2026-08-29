# Cognitive Dogfood Execution Plan

- Status: Prepared
- Date: 2026-08-30
- Scope: PR #2805 cognitive dogfood / product-value validation workstream
- Related issue memos: `COGNITIVE-DOGFOOD-01`, `COGNITIVE-EVAL-01`, `PRODUCT-POSITION-01`, `VALUE-REALNESS-01`, `PRACTICE-CULTURE-01`, `DOMAIN-W-ITERATION-01`
- Related ADR: `ADR-0047`（execution-first / ADR再起票条件）

## 1. この文書の役割

既存issue memoは「何を検証するか」、operator packは「各armをどう実行するか」を定義している。本書はその間を埋め、**どの順序で、どの証拠が揃ったら次へ進むか**だけを管理する。

本書を新しい意思決定の正本にはしない。長期的な判断はADR、実行課題はissue memo、各runの事実はrun record、製品上の探究状態はInquiryJourneyを正本とする。

## 2. 上位原則

1. **計画を先に固定し、その後にdogfoodする。** 実行結果を見てから問い・ケース・評価軸・資料集合を都合よく変えない。
2. **実在する開発課題を使う。** ベンチマークのためだけの人工問題を主対象にしない。
3. **比較可能性を守る。** A〜Dへ同じ問い・同じ製品資料を与え、方法差以外の情報差を作らない。
4. **KJ操作を成功条件にしない。** 新しい所見、反証、訂正、根拠接地、再訪可能性、意思決定の改善がなければ増分なしとする。
5. **機能不足とAI不足を混同しない。** 手動中核で操作できない問題は、まずbug / UX / domain gapとして扱う。
6. **外部現実へ開く。** internal dogfoodの成功を第三者価値の証明にしない。最終的に `VALUE-REALNESS-01` へ接続する。
7. **ADRを先回りしない。** `ADR-0047` R-1〜R-4のいずれかを実証したときだけADRを起票する。

## 3. 実行フェーズとゲート

### P0 — 計画凍結

目的: Case 001を結果依存で動かせない状態へする。

完了条件:

- [x] Case 001〜003の固定問いを事前登録した。
- [x] Case 001のRound 1製品snapshotを `main@2232b3bb26647e5c4a083f55bdbf83c161698649` に固定した。
- [x] B/Dのskill snapshotを `cultural-substrate-weaving@3988e12e5f7f316f377d3391e9486c8467a111d5` に固定した。
- [x] Round 2外部資料manifestをRound 1より前に固定した。
- [x] M1〜M9、自然発生conflict tests T1〜T3、run record、invalid条件を固定した。
- [x] InquiryJourney Phase 2実使用 / T9横断ゲートを固定した。
- [x] Case 001 arm実行順を固定した。

### Case 001 arm execution order

固定snapshot文字列

```text
case-001|2232b3bb26647e5c4a083f55bdbf83c161698649|3988e12e5f7f316f377d3391e9486c8467a111d5
```

のSHA-256先頭64bitをseedとしてA〜Dをshuffleした結果を事前登録し、**C → D → B → A** の順で実行する。

順序は優劣を意味しない。各armは別コンテキストで開始し、前armの出力を渡さない。

P0 exit gate:

- 計画変更が必要になった場合、Case 001出力を見る前なら本書を更新してよい。
- 最初のarm raw output保存後は、問い・M1〜M9・T1〜T3・Round 1 source snapshot・arm treatmentを変更しない。
- 実験不能な欠陥だけはdeviationとして記録し、比較結果と混ぜない。

---

### P1 — Case 001 / Round 1 実行

目的: 内部repository資料だけで4arm比較を成立させる。

実行単位:

1. Arm C — KJ Atlas + ordinary AI
2. Arm D — KJ Atlas + cultural-substrate-weaving
3. Arm B — ordinary document + cultural-substrate-weaving
4. Arm A — ordinary AI / ordinary document

各arm完了条件:

- raw artifactを未編集で保存する。
- required outputを保存する。
- proposal ledgerを保存する。
- M1〜M9を「測れない」を含め記録する。
- T1〜T3はrun終了後に評価する。
- C/DはKJ Atlas document / InquiryJourney参照を保存する。
- C/DはT9 manual-friction欄を埋める。
- contamination / deviationを明記する。

P1 exit gate:

- 有効armが4件揃う。
- 無効armがあれば、そのarmだけを同一条件で再実行する。
- 4armが揃う前に「勝者」を決めない。

---

### P2 — Blind review / Round 1統合

目的: 方法名への期待ではなく、成果物自体を比較する。

実施:

- arm名と方法説明を外したblind packageを作る。
- primary job、反証、現在価値、未実証仮説、次の検証、保留を比較する。
- M1の論点数だけでなく、M2/M3/M4/M5/M6の失敗を優先して読む。
- 各armでしか生存しなかった所見を元証拠へ戻す。
- C/Dでだけ発生した有益/無益な認知摩擦を分ける。

P2 exit gate:

次を区別して記録できること。

1. 通常AIだけでも十分だった所見。
2. cultural-substrate-weaving単体で増えた所見。
3. KJ Atlas外部表象で増えた所見。
4. Dでのみ生じた相互作用。
5. 方法を増やしたことで悪化した所見。
6. どのarmでも証拠不足だった点。

この時点ではCase 001単独から製品価値・skill価値を確定しない。

---

### P3 — Case 001 / Round 2 外部反証

目的: Round 1で固有だと思った価値を、既存製品・研究・隣接実践で積極的に剥がす。

- 事前登録manifestだけを共通追加資料として使用する。
- Miro / ATLAS.ti / Dovetail等で既に満たされる価値は固有価値から除く。
- local-first / Design Justice / CARE / human-AI cognition研究は、対象を分類する体系ではなく反証・遺漏防止の資料として使う。
- 新しい外部資料が必要になった場合はcandidate source requestへ置き、当該armだけへ追加しない。

P3 exit gate:

- 「KJ Atlas固有候補」と「業界で既に一般化している価値」を分離できる。
- primary job仮説を維持・修正・棄却のいずれかへ更新できる。
- `PRODUCT-POSITION-01` / `VALUE-REALNESS-01` へ返す具体的証拠がある。

---

### P4 — Case 001 finding triage

目的: 観察を無差別にissue/ADR化しない。

#### F0 — Run record / KJ cardのまま保持

次は原則F0に留める。

- 単一runだけの違和感。
- 反証可能だが再現していない仮説。
- 外部証拠待ちの候補。
- 「便利そう」だけの機能案。
- cultural-substrate-weavingの一回限りのframework所見。

#### F1 — 既存issueへ戻す

次を満たす場合は、新issueを作らず既存memoへ証拠追記する。

- 既存受入条件やT9等が明示的にその実使用証拠を待っている。
- 既存Decisionの範囲内で実装・UX・検証を直せる。
- 同じproblem statementを別名で重複起票するだけになる。

代表例: InquiryJourneyの実使用摩擦 → `DOMAIN-W-ITERATION-01` T9 / 関連既存issue。

#### F2 — 新issue memo

次をすべて満たす場合に起票する。

- 現実のrun / evidenceで再現可能な課題がある。
- 既存issueの受入条件では被覆できない。
- 実行可能な変更または検証を具体化できる。
- acceptance criteriaとverification levelを書ける。
- 長期Decisionを新たに固定しなくても着手できる。

issue化した後も、生カード・run evidenceへの参照を残す。

#### F3 — ADR candidate

`ADR-0047` の次のいずれかを証拠付きで満たす場合のみ候補にする。

- R-1: 実使用摩擦が設計trade-offを要求する。
- R-2: 外部協力者/実利用者の継続参加等で段階が変わる。
- R-3: 既存非機能予算・不変条件を越える。
- R-4: schema version gateを越える破壊的契約変更が必要。

「価値がありそう」「思想的に重要」「複数issueへ影響するかもしれない」だけではADRにしない。

P4 exit gate:

- 各findingにF0/F1/F2/F3のいずれかを付ける。
- F2/F3は元run evidenceがないものを起票しない。
- F3候補はADRを書く前に、既存ADRで本当に未被覆か再確認する。

---

### P5 — Case 002 / 003

Case 001の勝敗にかかわらず、事前登録順を維持する。

- Case 002: AI proposalと人間判断・認知摩擦の境界。
- Case 003: local/offline/self-hostとcollaborationの製品境界。

各ケースでP1〜P4を繰り返す。

3ケース終了後に初めて、次を横断判定する。

- KJ Atlas増分の再現性。
- cultural-substrate-weaving増分の再現性。
- Dの正/負の相互作用。
- M1増分に対するM9コスト。
- M2/M5/M6の認知制御改善。
- skill変更候補の再現性。
- InquiryJourney T9 Phase 3 AI支援ゲートの成立/不成立。

---

### P6 — 第三者価値実在へ接続

internal cognitive dogfoodで得たprimary job / switch reasonは、第三者検証へ渡す**仮説**であり結論ではない。

`VALUE-REALNESS-01` では、実利用者/協力者が自分の資料を持ち込んだときに次を見る。

- 使う理由。
- 使わない理由。
- 既存workflowへ戻る理由。
- 実際に価値を感じた瞬間。
- evidence / dissent / revisitのどれが不要だったか。
- KJ Atlas内部では重要と思った価値が外部では価値にならない反例。

外部現実と内部dogfoodが衝突した場合、外部を「理解不足」として捨てず、衝突自体を次のKJ材料にする。

## 4. 計画文書変更の扱い

実行開始後も計画文書は変更できるが、比較の正当性を守るため次を分ける。

### 比較条件を変えない修正

- typo / broken link / source path補正。
- 実行記録の不足欄追加。
- product/skill/experiment帰属を明確化する注記。
- 実験結果とは無関係なrunbook改善。

これは通常commitで修正する。

### 比較条件を変える修正

- 固定問いの変更。
- arm treatment変更。
- M1〜M9の定義変更。
- source snapshot差し替え。
- 成功条件/issue化閾値変更。

最初のraw run後に必要になった場合、既存revisionを上書きせず「なぜ旧設計では測れなかったか」を残し、次ケース/次revisionから適用する。

## 5. 現時点のADR / issue起票判断

本計画を整備した時点では、新しいADR triggerは確認していない。

また、認知dogfood実行順・blind review・finding triageは `COGNITIVE-DOGFOOD-01` / `COGNITIVE-EVAL-01` の実行手順を具体化したものであり、独立した新issueを要しない。

次に起票判断を行うのは、Case 001の実測findingがP4へ到達した時点とする。
