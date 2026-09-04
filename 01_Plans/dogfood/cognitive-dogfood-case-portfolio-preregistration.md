# 認知dogfood Case Portfolio — 事前登録

- 状態: Case 001実行前に事前登録済み
- 日付: 2026-08-29
- 関連: `COGNITIVE-DOGFOOD-01`, `COGNITIVE-EVAL-01`

## 1. 目的

`COGNITIVE-EVAL-01`では、性質の異なる少なくとも3つの開発課題について4Arm比較を行う。

Case 001の結果を見た後で、KJ Atlasまたはcultural-substrate-weavingが有利になりそうな課題だけをCase 002/003として選ぶことを防ぐため、**Case 001を実行する前に、3Caseの問いと選定理由を固定する。**

各Caseの詳細なsource manifestは、そのCaseを開始する前にsnapshotとして固定する。ただし、問いの中心を先行Caseの結果に応じて差し替えない。

## 2. Case Portfolioの構成

| Case | 主領域 | 問題の性質 | 他Caseとの違い |
|---|---|---|---|
| 001 | Product / value | 存在目的・一次利用仕事 | 市場、利用仕事、価値仮説を扱う |
| 002 | AI governance / product behavior | AI提案と人間判断の境界 | 操作単位、誤り、自動化、認知摩擦を扱う |
| 003 | Architecture / operations / adoption | local/offline/self-hostとcollaborationの境界 | データ所有、同期、運用、導入条件のtrade-offを扱う |

3Caseはいずれもopen problemだが、すべてを同じ種類の「プロダクト戦略」問題へ寄せない。

---

## 3. Case 001 — 存在目的と一次利用仕事

### Fixed question

> KJ Atlasは、既存のAIチャット、ホワイトボード、質的分析ツール、文書/issue管理では十分に満たしにくい、どの利用仕事のために存在するべきか。現在の設計・実装・dogfoodは、その価値をどこまで実現し、何をまだ実証できていないか。

### 主な不確実性

- KJ Atlasに固有のswitch reasonが本当に存在するか。
- 内部で重要だと考えて設計してきた価値が、第三者にとっての価値と一致するか。

### 選定理由

製品の存在理由そのものを扱うため、最初のCaseとする。

一方で抽象度が高く、広い探索を得意とする方法に有利な課題でもあり得る。そのためCase 002/003では、より具体的な製品挙動や技術・運用上のtrade-offを扱い、同種の課題だけで方法を評価しない。

---

## 4. Case 002 — AI提案と人間判断の境界

### Fixed question

> KJ Atlasのカード化、束ね、表札、反対視点、空白探索、配置、叙述などのAI支援について、どこまでを提案・自動化し、どこで人間の判断・確認・有益な摩擦を必須とするべきか。現在のproposal-only原則は、操作ごとの誤り方と利用価値に対して粗すぎないか、または十分に一般的な安全境界か。

### 主な不確実性

- `proposal-only`をすべてのAI操作へ一律に適用することが最善か。
- AIが比較的安全に担える操作と、意味を確定するため人間へ残すべき操作をどう分けるか。
- human final authorityを、単なるUI上の最終クリックではなく、適切な依存校正として成立させるには何が必要か。
- 判断を守るためのforcing frictionと、認知価値を生まない使いにくさをどう区別するか。

### 想定する証拠の種類

詳細なmanifestはCase 002開始前に固定するが、少なくとも次の種類を含める。

- KJ AtlasのAI API / model / proposal契約。
- DOGFOOD-17 / 20等で生じた意味接地の失敗と修正。
- proposal-only / review state / human final authorityに関するADR・仕様。
- 実際のAI操作について残っている誤り・訂正履歴。
- cognitive forcing / appropriate reliance等の外部研究はRound 2候補とする。

### 選定理由

Case 001のような市場・利用仕事の探索ではなく、**具体的な製品動作と統治境界**を扱う。

KJ法や文化体系を使うことで論点を広げられるだけで、具体的な操作差や失敗モードへ戻れないのであれば、このCaseでは方法上の増分が出にくい。そこを意図的に検証する。

### 反証圧力

- 通常のrisk analysis / HCI / API契約レビューだけで十分な結論が得られるなら、skill / KJの増分は小さい。
- 「人間が大切」「AIは補助」といった一般論しか残らなければ、このCaseでは十分な成果とみなさない。

---

## 5. Case 003 — local/offline/self-hostとcollaborationの製品境界

### Fixed question

> KJ Atlasはoffline/local/self-hostによるデータ統制と、共同分析・共有・組織導入に必要な同期/collaborationをどの境界で両立するべきか。local-firstを中核価値、配備オプション、安全境界、または特定利用ケース向け要件のどれとして扱うべきか。

### 主な不確実性

- offline / self-hostは利用者がKJ Atlasへ切り替える理由なのか、それとも特定導入環境における必要条件なのか。
- sensitive / unfinishedな定性資料のcontrolと、共同作業の即時性をどう両立するか。
- local-first / CRDT等の技術方向へ進む価値を、実利用証拠がない段階で過大評価していないか。
- enterprise / public-sectorのself-host要求と、個人・小規模チームの簡便な利用を、同じ製品境界で扱えるか。

### 想定する証拠の種類

詳細なmanifestはCase 003開始前に固定するが、少なくとも次の種類を含める。

- KJ Atlas README / ROADMAPのoffline / self-host / share / collaboration方針。
- security / data boundary / schema / transportに関するADR。
- public sharing / export / SafeMode / tenant / collaborationに関する実装・dogfood。
- 実運用上のdeployment friction。
- local-first研究 / data governanceはRound 2候補とする。

### 選定理由

Case 001/002とは異なり、**アーキテクチャ、運用、導入、データ所有のtrade-off**が中心となる。

技術的制約と社会的価値を同時に扱う必要はあるが、最終的な結論は具体的なdeployment / data boundaryへ戻らなければならない。

### 反証圧力

- 「local-firstはユーザー主体で望ましい」といった価値一般論だけでは不十分。
- 運用コスト、同期競合、権限、障害、migration、share / export等の具体的な制約へ戻れなければ、方法上の増分として数えない。
- cloud-firstが一部利用者に明確に優れる可能性も、最初から除外しない。

---

## 6. Case選定に関する不変条件

Case 001の結果にかかわらず、原則として **001 → 002 → 003** の順で実施する。

次の理由だけではCaseを差し替えない。

- Case 001でKJ Atlasが良く見えた、または悪く見えた。
- cultural-substrate-weavingの増分が出た、または出なかった。
- Case 002/003が特定の方法に不利そうだと感じた。

Caseの差し替えを許すのは、次の場合に限る。

- 問いがすでに実装または意思決定によって閉じている。
- source snapshotを成立させられない。
- 重大な安全上・権限上の理由により実験できない。

差し替える場合も旧Caseを削除しない。`not executable`と理由を残し、代替Caseは結果を見る前に新しいrevisionとして登録する。

## 7. InquiryJourney Phase 2実使用とT9判定

Case 001〜003のArm C/Dは、認知比較のtreatmentであると同時に、`DOMAIN-W-ITERATION-01` Phase 2手動中核の実使用ケースとして扱う。

目的はInquiryJourneyを成功扱いすることではない。実際の複雑な開発課題で、次を観測する。

- snapshot / handoff / resume / compare / lineage / branchが、判断状態の保持、訂正、再開に実際に役立ったか。
- どの操作で、人間が同じ種類の手作業を繰り返したか。
- その摩擦が有益な立ち止まりなのか、認知価値を生まない反復作業なのか。
- AI提案が必要に見えた場合でも、現行の非AI機能で十分に処理できなかったか。

### T9の判断を結果後に動かさないための事前条件

`DOMAIN-W-ITERATION-01` T9からPhase 3の別issueへ進むのは、原則として次を**すべて**満たした場合だけとする。

1. 同じ種類の手動摩擦が、Case 001〜003のうち**少なくとも2つの異なるCase**のC/D実使用で再現する。
2. その摩擦がM6 / M7 / M9等に実際の悪影響を与え、単なる「あると便利」ではない。
3. 現行の非AI workaroundでは、同じ目的を妥当な認知負荷で達成できない。
4. proposal-only AI支援として、何を候補提示し、何を人間へ残すかを具体化できる。
5. 自動化によって、早期収束、異論の消失、古い根拠への回帰等を強めるriskを記述できる。

### 単一Caseで重大な問題が出た場合

1つのCaseで手動中核の操作自体を完了できない、データを失う、誤った系譜を作る等の重大な問題が出ても、それをPhase 3 AI支援の根拠にはしない。

まず手動中核のbug / UX / domain gapとして切り分ける。AIで回避できるという理由で、基礎となる欠陥を隠さない。

### T9の終了条件

- Case 001〜003の有効なC/D実使用が揃い、上の5条件を満たす反復摩擦がある → Phase 3 proposal-only AI支援の別issue化を検討し、T9へ証拠を戻す。
- 3Caseを通して同型摩擦が再現しない、または非AI手段で十分 → `manual core sufficient under observed cases`を証拠付きでT9へ返し、AI issueを作らずT9を完了候補とする。
- runが汚染、無効、中途失敗等により比較できない → 結論を出さず、理由を残して必要なrunだけ再実行する。

この閾値はAI機能を抑制するための点数規則ではない。**実使用より前にfeature pressureを固定しておくための、反証可能なgate**である。

## 8. 3Case終了後の横断評価

3Caseが終了して初めて、次を横断的に判定する。

1. KJ Atlasによる増分が、特定の抽象的なテーマにだけ現れたか。
2. cultural-substrate-weavingによる増分が、特定の文化体系や領域にだけ依存したか。
3. Arm Dに正の相互作用があるか、あるいは方法過多による負の相互作用があるか。
4. M1の増加がM9の摩擦増加に見合うか。
5. M2 / M5 / M6の認知制御が、単なる論点数の増加よりも再現して改善したか。
6. skill変更候補が複数Caseで再現したか。
7. InquiryJourneyのmanual coreが複数領域で、再訪、系譜、分岐に実効性を持ったか。
8. T9のAI支援候補が、複数Caseで同型の実使用摩擦として再現したか。

単一Caseの勝敗だけを、製品価値、skill価値、Phase 3 AI支援の必要性の結論にしない。