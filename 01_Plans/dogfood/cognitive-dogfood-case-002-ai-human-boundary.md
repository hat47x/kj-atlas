# Cognitive Dogfood Case 002 — AI提案と人間判断の境界

- Status: Prepared / source frozen before first valid Case 001 arm run
- Portfolio: `cognitive-dogfood-case-portfolio-preregistration.md`
- Product snapshot: `hat47x/kj-atlas@2232b3bb26647e5c4a083f55bdbf83c161698649`
- Skill snapshot for B/D: `hat47x/cultural-substrate-weaving@3988e12e5f7f316f377d3391e9486c8467a111d5`
- Round 1 source manifest: `cognitive-dogfood-case-002-round1-source-manifest.json`

## 1. Fixed question

> KJ Atlasのカード化、束ね、表札、反対視点、空白探索、配置、叙述などのAI支援について、どこまでを提案・自動化し、どこで人間の判断・確認・有益な摩擦を必須とするべきか。現在のproposal-only原則は、操作ごとの誤り方と利用価値に対して粗すぎないか、または十分に一般的な安全境界か。

この問いはCase 001の結果にかかわらず変更しない。

## 2. Primary uncertainty

- `proposal-only` を全AI操作へ一律適用することが最善か。
- 低リスクの検査・候補生成と、意味を確定・変更・公開する高リスク操作をどこで分けるべきか。
- human final authorityが「最後にクリックする人がいる」だけの形式要件へ縮退していないか。
- AIの候補数・再生成・批評・自律検査を増やしたとき、適切な依存校正が改善するか、逆に自動化バイアスを強めるか。
- forcing frictionと、価値を生まない単なる操作負担をどう分けるか。

## 3. Round 1 evidence boundary

全armへ、manifestに固定した同一product sourceだけを与える。Round 1では外部Web検索を行わない。

資料は意図的に次を混在させる。

1. 初期のHuman-in-the-loop / reversible synthesis原則。
2. core value / cognitive-load / SafeMode等の横断制約。
3. task complexityに応じたmodel routingと、一部検査のL2自律実行。
4. 実際のdogfoodで起きた意味接地失敗。
5. 島表札の単発候補から複数候補・違和感再生成・選択採用・履歴永続化へ進んだ実装履歴。
6. final judgement unavailable時の`held`遷移など、まだ閉じていない境界。

これにより「AIは補助、人間が大切」という一般論だけでは資料全体を説明できないようにする。

## 4. Natural conflict / correction tests

以下は評価者側の事前登録であり、armへ答えとして教えない。

### C2-T1 — 一律proposal-only と操作別自律性

- `ADR-0026` はAI提案を常に候補とし、確定操作は人間だけが行うという粗い上位境界を置く。
- `ADR-0075` は三要素検査・不整合指摘をL2としてAIが自律実行してよい一方、最終判断は人間に残す。

期待する識別は「自律化する/しない」の二分ではなく、**検査・候補生成・状態変更・公開・不可逆判断で必要な境界が異なる**ことである。

### C2-T2 — 単発提案から対話的な意味形成へ

- `ADR-0077` / `DOGFOOD-33` は島表札を単一回答から複数候補へ変える。
- `DOGFOOD-34` は人間の違和感を入力として再生成する。
- `DOGFOOD-35` は違和感と再提案の履歴を永続化し、「なぜ採用したか」へ戻れるようにする。

単にhuman approvalを1回挟むだけでなく、**人間の違和感がAI提案を変え、その変化自体が監査可能であること**を現在状態として認識できるかを見る。

### C2-T3 — routing設計は安全停止まで完了していない

`AI-ROUTE-01` ではintermediate/final_judgement分離や監査は実装済みだが、final_judgementが利用不能な場合にauto-publishせず`held`へ遷移するMMR-06は未実装である。

「高性能modelへrouteすればfinal judgmentも安全」という飛躍をせず、未閉鎖境界を保持できるかを見る。

### C2-T4 — 改善指標そのものが誤誘導しうる

`ADR-0075` はwarning件数の大幅減少の一部が検出器の正規化/除外による検出能力低下だったことをMeasurement Integrityとして訂正している。

AI自律性の評価で「警告が減った」「採用率が上がった」「修正回数が減った」等を、そのまま品質改善と読まないかを見る。

## 5. Common required output

全armは少なくとも次を返す。

1. AI支援操作を、誤り方・可逆性・意味確定への影響で分けた境界案。
2. 各操作でAIが自律実行してよい部分、proposalに留める部分、人間確認を必須にする部分。
3. 現行KJ Atlasが既に実現している適切な境界と、過剰/不足の可能性。
4. 「有益な摩擦」と「無駄な摩擦」を区別する判断基準。
5. human final authorityが形式化し、automation biasを防げない条件。
6. 最も強い反証。すなわち、現在のproposal-only原則をほぼ維持すべき理由、または逆にもっと自律化すべき理由。
7. 次に検証すべき具体的な操作/issue。新ADRを先に作るのではなく、実使用で観測可能な検証を優先する。
8. 主要主張ごとのsource path / stable identifier / evidence time。
9. 古い状態、後で修正された状態、未実装の契約を区別する。
10. 判断保留と追加で必要な証拠。

## 6. Failure conditions

次ならCase 002としての増分は弱い。

- 「AIは補助」「人間中心」「重要なところだけ確認」の一般論で終わる。
- `proposal-only` を単一のbooleanとして扱い、検査・候補生成・採用・公開等の操作差を扱わない。
- DOGFOOD-17/20等の意味接地失敗を、安全原則の存在だけで打ち消す。
- 複数候補/違和感/再提案履歴を、単なるUI convenienceとしてしか見ない。
- 人間確認の回数を増やすこと自体を安全性と同一視する。
- 実装済み・未実装・訂正済みを混同する。

## 7. Method boundary

4arm、M1〜M9、blind review、contamination、skill attributionは`COGNITIVE-EVAL-01`とCase 001で固定した共通契約を再利用する。

Case 002固有の結論を得るためにcultural-substrate-weavingの正本を変更しない。B/DはCase 001と同じfrozen skill snapshotを使用する。

C/DではKJ Atlasを完成図の清書ではなく分析中の外部表象として使用し、InquiryJourneyの実使用摩擦も同じT9ゲートへ返す。

## 8. Completion

Case 002 Round 1は次を満たすまで結論扱いしない。

- A〜Dが独立fresh contextで実行される。
- 同じfrozen source snapshotを使う。
- raw artifactを先に固定する。
- blind reviewがunblindより前に完了する。
- C2-T1〜T4は答え合わせではなく、見落とし/時間差理解/依存校正の観測資源として評価される。
- negative / no-increment resultを削除しない。
