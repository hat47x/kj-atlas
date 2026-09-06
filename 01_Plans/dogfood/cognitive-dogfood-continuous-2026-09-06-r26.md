# 継続dogfood R26 — one-shotは成功した時点ではなく、退役まで終えて初めて完了する

- Date: 2026-09-06
- Scope: 日常開発の自己分析。Case 001〜003の統制比較には含めない。
- Question: 一回限りのworkflowが目的を達成したあともcurrent mainへ残り、後からstale current referenceを作る状態をどう防ぐか。
- Canvas: `doc_kj_atlas_dogfood_r26.json`
- Observation baseline: `main@66f6e3bcbf654cdb601341eb95c751bca193c7bb`
- Trigger: R25 verification run `34023506343` のrepository-wide planning suiteで得た陽性failure。
- Result class: 実運用で観測したretirement漏れ。formal Case、第三者価値実証、AI-IR named-provider測定の結果には数えない。

## 1. R25の検証が別の陽性を露呈した

R25のPR eventでrepository-wide `01_Plans/tests` を実行したところ、R25自身の2 testsはgreenだった一方、legacy Done-root reference guardが1件のbaseline failureを返した。

失敗対象は `.github/workflows/lane-c-sync-qa-e2e-saas-child-status-once.yml` であり、Doneへ移った `QA-E2E-SAAS-01` を旧active-root pathで2箇所参照していた。

このworkflowはcurrent main向けの常設CIではない。triggerは2026-09-05の専用branch `docs/lane-c-close-saas-tenant-e2e-instrumentation-20260905` だけで、さらに特定のhead commit messageで一度だけ更新処理を走らせる設計だった。

## 2. 「まだ必要か」を実行履歴で確認した

workflow名はone-shotでも、未実行なら削除すべきとは限らない。そのためbranch条件だけで退役を決めず、Actions履歴を確認した。

Run `33940736612` は2026-09-05にこのworkflowを実行し、`conclusion=success` で完了していた。すなわち今回の対象は「将来使うかもしれない一時資産」ではなく、実際に目的を達成済みのexecution assetである。

にもかかわらずworkflow file自体はmainへ残った。その後、対象IssueがDoneへ移動したことで、workflow内部のcurrent referenceだけが過去のactive-rootを指すようになった。

## 3. 既存guardが捕捉しなかった理由

`01_Plans/tests/test_retired_one_shot_assets.py` は既に退役したone-shot assetsの再出現を防いでいる。ただし意図的にexact path allow/deny listであり、既にretiredと判断された資産だけを列挙する。

この方式は、現在進行中の一時workflowを `*-once.yml` という名前だけで一律禁止しない点で正しい。一方、新しく役目を終えたone-shotをretired listへ移す工程が抜ければ、そのfileはmainへ残り続ける。

したがって欠けていたのは「one-shot一般を自動禁止する規則」ではなく、**成功後のretirementをexecution lifecycleの一部として扱うこと**だった。

## 4. 今回の最小修正

- `.github/workflows/lane-c-sync-qa-e2e-saas-child-status-once.yml` を削除する。
- 同pathを `RETIRED_ONE_SHOT_PATHS` へ追加し、後続のstale branch merge等で再出現したらplanning testでfailさせる。
- 他の `*-once.yml` は一括削除・一括禁止しない。個々の実行状態と目的を確認せず退役判定を一般化しない。

これにより、今回の陽性だけを閉じつつ、一時的な検証資産を必要な間は利用できる。

## 5. R22/R23との関係

R23では、stale-state診断について「作った / 再利用された / 実事故を捕捉した」を分け、positive hitまたは繰り返すfalse positiveが出るまでrequired check化を先回りしないとした。

今回positive evidenceは得られたが、直接捕捉したのはR22のmerge-base診断ではなくrepository-wide planning testである。また原因も「古いbranchが削除済みpathを再導入した」ことではなく、「一度使ったexecution assetをmainから退役させなかった」ことだった。

したがって、この1件を根拠にR22 diagnosticをrequired checkへ昇格させるのは論理が飛ぶ。陽性証拠は保持するが、検出機構と原因クラスを同一視しない。

## 6. KJ統合で立った中心構造

> **one-shotはrunが成功しただけでは完了せず、current mainから退役し、再出現を防げる状態まで含めてライフサイクルが閉じる。**

一回限りの資産は、実行前には必要であり、実行後には負債へ性質が変わり得る。名前や作成時点だけで区別するのではなく、実行結果と現在の役割によって「active temporary asset」から「retired asset」へ状態を移す必要がある。

## 7. Finding triage

### F0 — 生の観察として保持

- R25 full planning runで実際に旧active-root参照2件がfailureになった。
- 対象workflowは専用branch向けone-shotで、Run `33940736612` がsuccess済みだった。
- 役目を終えたworkflowがcurrent mainに残り続けたことが、後日のIssue lifecycle moveと衝突した。

### F1 — 既存lifecycle guardへ返す

- 成功済みone-shot workflowを削除する。
- exact pathを既存retired-one-shot regression listへ追加する。
- repository-wide planning suiteを再実行し、R25で見えていたbaseline failureが消えるか確認する。

### F2 — 新Issueなし

既存のretired-one-shot guardとplanning lifecycleの範囲で閉じる具体的な退役漏れであり、新しい長期作業単位を必要としない。

### F3 — ADRなし

新しいアーキテクチャ判断ではなく、既存execution assetのライフサイクル完了条件を実例から補正するものだからである。

## 8. 実証境界と次工程

R26は内部運用の陽性証拠であり、formal cognitive dogfoodのArm結果ではない。Case 001 Arm Cの生実行、第三者価値実証、AI-IR named-provider evidenceへ加算しない。

R26の修正後にplanning baselineがgreenになっても、それを理由にさらに新しいR27準備を作らない。新しい具体的な欠陥がなければ、本来のformal mainlineはfresh context + frozen KJ Atlas UIでのCase 001 Arm C実走へ戻る。
