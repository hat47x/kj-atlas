# 継続dogfood R28 — navigationは可変状態の第二正本を持たない

- Date: 2026-09-06
- Scope: 日常開発の自己分析。Case 001〜003の統制比較には含めない。
- Question: 文書・ADR・Issueへの索引が、リンクだけでなく可変な状態値まで複製したとき、どこで陳腐化を止めるべきか。
- Observation baseline: `main@49f99a0c0793b53dcdf9e4a547bd780610248b92`
- Trigger: PR #3011 / merge commit `a5f41294868a3e48302a88d7825cb857866d5b28`
- Result class: current repositoryの実docs driftを修正した運用上の陽性。formal Case、第三者価値実証、AI-IR named-provider測定の結果には数えない。

## 1. 実際に観測したずれ

`02_Architecture/README.md` は認証関連ADRとテナント関連Issueへの入口を持っていたが、入口だけでなく各行に `Accepted` / `Draft` / `Done` / `In Progress` などの状態も複製していた。

このうち `QA-E2E-SAAS-01` はPR #2959で既に `01_Plans/issues/done/` へ移動済みだった一方、Architecture索引では `Draft` のまま残っていた。正本側のlifecycleは進んだが、navigation側のコピーが追随しなかったためである。

PR #3011は単に `Draft -> Done` と値を同期するのではなく、ADR・Issue一覧から状態列そのものを外した。Architecture索引はIDとtopicへの入口を持ち、decision stateはADR本文、Issue lifecycleは `01_Plans/issues/` / `01_Plans/issues/done/` を正本として確認する構造へ戻した。

## 2. なぜ値の同期だけでは足りないか

今回の誤りは `Draft` という一語が古かったことではない。可変状態の所有者が二つ存在していたことが原因である。

もし今回 `Draft` を `Done` に直すだけなら、その瞬間は一致する。しかし次のlifecycle変更では同じ追随作業が必要になる。索引の目的が「どこを見るか」を示すことなのに、「現在どういう状態か」まで複製すると、navigationが暗黙の第二正本になる。

一方で、状態語を文書全体から排除するのも違う。履歴説明、snapshot、評価結果、固定された過去状態には状態値そのものが意味を持つ。今回の境界は、**current stateの権威を持たないnavigation文書が、権威を持つ正本の可変状態をコピーしない**ことにある。

## 3. KJ統合で立った中心構造

今回の中心は次にまとまる。

> **navigationが持つべきなのは「何がどこにあるか」であり、「いま何状態か」の権威ではない。**

これは索引を情報量の少ない文書にするという話ではない。索引はtopic、ID、関係、読む順序、正本への導線を十分に持てる。ただし、別文書が所有する可変なdecision/lifecycle stateをコピーしてしまうと、更新責務まで引き受けることになる。

R14で継続dogfoodの索引を「導線」として扱った境界とも整合する。今回の事例は、その原則がArchitecture索引にも具体的に必要だったことを示す一件である。ただし一例だけを根拠にrepository-wideな「索引に状態語禁止」guardへ一般化しない。

## 4. Finding triage

### F0 — 生の観察として保持

- `QA-E2E-SAAS-01` は正本ではDoneへ移動済みだったが、`02_Architecture/README.md` では `Draft` と表示され続けた。
- 同索引はADRの `Accepted` やIssueの複数lifecycle値も表形式で複製していた。
- PR #3011は状態値を同期するのではなく、状態列を削除して正本への導線へ戻した。

### F1 — 既存文書の責務境界へ返す

- Architecture索引はnavigationを所有する。
- ADRの採択・置換等は各ADR本文を正本とする。
- Issueのactive/done・完了根拠・残条件はIssue正本を参照する。
- topic、ID、リンク、関係説明は索引に残してよい。

### F2 — 新Issueなし

実際のdriftはPR #3011で修正済みであり、現時点で独立した未完作業を持たない。類似例を先回りして全repositoryへ機械的禁止するIssueも作らない。

### F3 — ADRなし

新しいアーキテクチャ判断ではなく、既存の文書所有境界とsingle-source-of-truthを実運用で回復した修正である。

## 5. guardを増やさない理由

今回の一例から `README` や索引文書の `Status` / `状態` 文字列を一律禁止すると、historical snapshotや固定評価結果まで誤検知し得る。R24〜R27で得た教訓と同様、文字列だけで意味を決めない。

再発が複数のnavigation文書で観測され、共通した構造判定が可能になった時点で初めてguard候補を検討する。それまでは、正本とnavigationの責務をreview時に確認する。

## 6. 実証境界と次工程

R28はcurrent repositoryのdocs driftから得た内部所見であり、formal Case 001 Arm Cの結果ではない。第三者価値実証、AI-IR named-provider evidenceにも加算しない。

この記録を理由に新しいpreflight、KPI、実験スキーマは追加しない。formal mainlineは引き続き、既知仮説から隔離したfresh contextとfrozen KJ Atlas UIでのCase 001 Arm C実走である。
