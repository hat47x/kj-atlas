# Cognitive Dogfood Case Portfolio — Pre-registration

- Status: Pre-registered before Case 001 execution
- Date: 2026-08-29
- Related: `COGNITIVE-DOGFOOD-01`, `COGNITIVE-EVAL-01`

## 目的

`COGNITIVE-EVAL-01` は少なくとも3つの異なる開発課題で4arm比較する。

Case 001の結果を見てから、KJ Atlasまたはcultural-substrate-weavingが有利になりそうな課題だけをCase 002/003へ選ぶことを防ぐため、**Case 001実行前にケース群の問いと選定理由を固定する。**

詳細なsource manifestは各ケース開始時にsnapshotを固定するが、問いの中心を結果に応じて差し替えない。

## Portfolio design

| Case | 主領域 | 問題の性質 | なぜ異なるか |
|---|---|---|---|
| 001 | Product / value | 存在目的・一次利用仕事 | 市場/利用仕事/価値仮説を扱う |
| 002 | AI governance / product behavior | AI提案と人間判断の境界 | 操作単位・誤り・自動化・認知摩擦を扱う |
| 003 | Architecture / operations / adoption | local/offline/self-hostとcollaborationの境界 | データ所有・同期・運用・導入条件のtrade-offを扱う |

3ケースともopen problemだが、同じ種類の「プロダクト戦略」へ寄せない。

---

## Case 001 — 存在目的と一次利用仕事

### Fixed question

> KJ Atlasは、既存のAIチャット、ホワイトボード、質的分析ツール、文書/issue管理では十分に満たしにくい、どの利用仕事のために存在するべきか。現在の設計・実装・dogfoodは、その価値をどこまで実現し、何をまだ実証できていないか。

### Primary uncertainty

- KJ Atlas固有のswitch reasonが本当にあるか。
- 内部で強く設計された価値が第三者価値と一致するか。

### Selection reason

製品の存在理由そのものを扱うため最優先。ただし抽象度が高く、方法論が広い探索を得意とする場合に有利になり得る。そのためCase 002/003を異質化する。

---

## Case 002 — AI提案と人間判断の境界

### Fixed question

> KJ Atlasのカード化、束ね、表札、反対視点、空白探索、配置、叙述などのAI支援について、どこまでを提案・自動化し、どこで人間の判断・確認・有益な摩擦を必須とするべきか。現在のproposal-only原則は、操作ごとの誤り方と利用価値に対して粗すぎないか、または十分に一般的な安全境界か。

### Primary uncertainty

- `proposal-only` を全AI操作へ一律適用することが最善か。
- AIが得意な低リスク操作と、意味を確定する高リスク操作をどう分けるか。
- human final authorityをUI上の最終クリックだけでなく、適切な依存校正として成立させるには何が必要か。
- forcing frictionが必要な箇所と、単なる使いにくさになる箇所をどう分けるか。

### Expected evidence classes

詳細manifestはCase 002開始時に固定するが、少なくとも次の種類を含める。

- KJ AtlasのAI API/モデル/提案契約。
- DOGFOOD-17/20等の意味接地失敗と修正。
- proposal-only / review state / human final authorityに関するADR/仕様。
- 実際のAI操作の誤り/訂正履歴。
- cognitive forcing / appropriate reliance等の外部研究はRound 2候補。

### Selection reason

Case 001のような市場探索ではなく、**具体的な製品動作と統治境界**を扱う。KJ/文化体系が何でも広く語れるだけなら、具体的な操作差・失敗モードへ接地できず優位性は出にくい。

### Falsification pressure

- 通常のrisk analysis / HCI / API契約レビューだけで十分な結論が出るなら、skill/KJ増分は小さい。
- 「人間が大切」「AIは補助」の一般論しか残らなければ失敗。

---

## Case 003 — local/offline/self-hostとcollaborationの製品境界

### Fixed question

> KJ Atlasはoffline/local/self-hostによるデータ統制と、共同分析・共有・組織導入に必要な同期/collaborationをどの境界で両立するべきか。local-firstを中核価値、配備オプション、安全境界、または特定利用ケース向け要件のどれとして扱うべきか。

### Primary uncertainty

- offline/self-hostは利用者がswitchする理由か、それとも特定導入環境の必要条件か。
- sensitive/unfinished qualitative materialのcontrolと、共同作業の即時性をどう両立するか。
- local-first/CRDT等の技術方向へ進む価値が、実利用証拠なしに過大化していないか。
- enterprise/public-sectorのself-host要求と、個人/小チームの簡便な利用を一つの製品境界で扱えるか。

### Expected evidence classes

詳細manifestはCase 003開始時に固定するが、少なくとも次の種類を含める。

- KJ Atlas README/ROADMAPのoffline/self-host/share/collaboration方針。
- security/data boundary/schema/transport関連ADR。
- public sharing / export / SafeMode / tenant/collaboration関連実装・dogfood。
- 実運用上のdeployment friction。
- local-first research / data governanceはRound 2候補。

### Selection reason

Case 001/002と異なり、**アーキテクチャ、運用、採用、データ所有のtrade-off**が中心。技術的制約と社会的価値を同時に扱うが、結論は具体的なdeployment/data boundaryへ戻る必要がある。

### Falsification pressure

- 「local-firstはユーザー主体で良い」という価値一般論だけでは不十分。
- 運用コスト、同期競合、権限、障害、migration、share/export等の具体的制約へ戻れなければ増分に数えない。
- cloud-firstが一部利用者に明確に優れる可能性も保持する。

---

## Case selection invariants

Case 001の結果にかかわらず、原則として001→002→003を実施する。

次の理由だけではケースを差し替えない。

- Case 001でKJ Atlasが勝った/負けた。
- cultural-substrate-weavingの増分が出た/出なかった。
- Case 002/003で方法に不利そうだと感じた。

差し替えを許すのは、次に限る。

- 問いが既に実装/意思決定により閉じた。
- source snapshotを成立させられない。
- 重大な安全/権限上の理由で実験できない。

差し替え時は、旧ケースを削除せず `not executable` と理由を残し、代替ケースを結果を見る前に新revisionとして登録する。

## InquiryJourney Phase 2 actual-use / T9 decision gate

Case 001〜003のArm C/Dは、認知比較のtreatmentであると同時に、`DOMAIN-W-ITERATION-01` Phase 2手動中核の実使用ケースとして扱う。

目的はInquiryJourneyを成功扱いすることではなく、実際の複雑な開発課題で次を観測することである。

- snapshot / handoff / resume / compare / lineage / branchが、判断状態の保持・訂正・再開へ実際に寄与したか。
- どの操作で人間が同種の手作業を繰り返したか。
- その摩擦が「有益な立ち止まり」か、認知価値を生まない反復作業か。
- AI提案が必要に見えた場合、現行の非AI機能で十分に処理できたか。

### T9判定を結果後に動かさないための事前規則

`DOMAIN-W-ITERATION-01` T9のPhase 3別issue化は、原則として次を**すべて**満たした場合だけ候補とする。

1. 同じ種類の手動摩擦が、Case 001〜003のうち**少なくとも2つの異なるケース**のC/D実使用で再現する。
2. その摩擦がM6/M7/M9等に実際の悪影響を持ち、単なる「あると便利」ではない。
3. 現行の非AI workaroundでは、同じ目的を十分な認知負荷で達成できない。
4. proposal-only AI支援として、何を候補提示し、何を人間へ残すかを具体化できる。
5. 自動化が早期収束、異論消失、古い根拠への回帰等を強めるriskを記録できる。

### 単一ケースで重大な問題が出た場合

一つのケースで手動中核の操作自体が完了できない、データを失う、誤った系譜を作る等の重大な問題が出た場合は、Phase 3 AI支援の根拠にしない。

それはまず、手動中核のbug / UX / domain gapとして切り分ける。AIで回避できることを理由に基礎欠陥を隠さない。

### T9の終了条件

- Case 001〜003の有効なC/D実使用が揃い、上の5条件を満たす反復摩擦がある → Phase 3 proposal-only AI支援の別issue化を検討し、T9へ証拠を戻す。
- 3ケースを通して同型摩擦が再現しない、または非AI手段で十分 → 「manual core sufficient under observed cases」を証拠付きでT9へ返し、AI issueを作らずT9を完了候補とする。
- runが汚染・無効・途中失敗で比較不能 → 結論を出さず、無効理由を残して必要なrunだけ再実行する。

この閾値はAI機能を抑制するための点数規則ではなく、**実使用に先立ってfeature pressureを固定するための反証可能なゲート**である。

## Cross-case evaluation

3ケース終了後に初めて、次を横断判定する。

1. KJ Atlasの増分が特定の抽象的テーマだけに出たか。
2. cultural-substrate-weavingの増分が特定の文化体系/領域だけに依存したか。
3. Arm Dに正の相互作用があるか、方法過多による負の相互作用があるか。
4. M1の増加がM9の摩擦増加に見合うか。
5. M2/M5/M6の認知制御が、単なる論点数増加より再現して改善したか。
6. skill変更候補が複数ケースで再現したか。
7. InquiryJourneyのmanual coreが複数領域で再訪・系譜・分岐に実効性を持ったか。
8. T9のAI支援候補が、複数ケースで同型の実使用摩擦として再現したか。

単一ケースの勝敗を製品価値、スキル価値、またはPhase 3 AI支援の必要性の結論にしない。