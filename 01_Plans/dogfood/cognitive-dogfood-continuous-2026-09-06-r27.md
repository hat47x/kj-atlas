# 継続dogfood R27 — 例外は追加するときだけでなく、不要になったときにも消えなければならない

- Date: 2026-09-06
- Scope: 日常開発の自己分析。Case 001〜003の統制比較には含めない。
- Question: historical exception allow-listが、参照消滅後も残ることでguardの意味を徐々に弱める状態をどう防ぐか。
- Canvas: `doc_kj_atlas_dogfood_r27.json`
- Observation baseline: `main@d2349cc7014bf5e63dc6ea169a4d6ca66b5339bd`
- Trigger: R26 verification run `34023966836` のrepository-wide planning suiteで得た次の陽性failure。
- Result class: 既存guardが自分自身のstale exceptionを検出した運用証拠。formal Case、第三者価値実証、AI-IR named-provider測定の結果には数えない。

## 1. R26で最初のfailureを消すと、次のbaselineが見えた

R26では、R25で見つかった成功済みone-shot workflowを退役させた。R26 verification run `34023966836` ではfocused retired-one-shot guardがgreenとなり、R25で観測していたQA-E2E-SAASの旧active-root参照failureは消えた。

その状態でrepository-wide `01_Plans/tests` を続けると、legacy Done-root reference guardが別の1 failureを返した。

今回は「新しい旧path参照が増えた」のではない。逆に、`EXTERNAL_HISTORICAL_EXCEPTIONS` に期待値として残っていた6件のうち5件が、実際の `git grep` ではもう観測されなかった。

消えていたのは次の5件である。

- `doc_kj_atlas_dogfood_r15.json` × `AI-IR-PROMPT-EVIDENCE-01`
- `doc_kj_atlas_dogfood_r18.json` × `DOC-ISSUE-LIFECYCLE-01`
- `doc_kj_atlas_dogfood_r2.json` × `DX-CI-MCP-01`
- `core-value-realization-priorities-2026-07-18.md` × `MVP-EXIT-01`
- `mvp-exit-01-human-acceptance-handoff.md` × `MVP-EXIT-01`

一方、`phase-exit-evaluation-ENV-ARCH-01-2026-03-11.md` × `ENV-ARCH-01` は期待setとの差分に出ておらず、現時点で観測されているhistorical exceptionとして残る。

## 2. guardは壊れたのではなく、正しくfailした

`test_no_unreviewed_external_file_references_any_done_memo_at_retired_root` は、実際に観測したhistorical exceptionsと、明示allow-list `EXTERNAL_HISTORICAL_EXCEPTIONS` が完全一致することを要求している。

この契約には二つの向きがある。

1. allow-listにない新しい旧path参照が現れたらfailする。
2. allow-listにある参照が消えたのに例外だけ残ってもfailする。

後者が今回実際に発火した。

したがって新しい検出器を追加する必要はない。むしろ既存guardが「例外の追加」だけでなく「例外の縮退」も強制できることが実運用で確認された。

## 3. なぜstale exceptionを放置してはいけないか

例外は、guardの適用範囲に穴を開ける。その穴に現実の参照がある間は、歴史的provenanceを保つための意味がある。

しかし参照自体が消えたあとも例外だけ残ると、将来同じ `(source_path, memo_name)` の組が意図せず再出現したとき、それを「既に承認済みのhistorical provenance」と誤認して通す余地になる。

つまりallow-listは「過去に一度レビューしたものの永久免許」ではない。**現在も例外理由が実体として存在している間だけ有効な、縮退可能な契約**である。

## 4. 今回の最小修正

`EXTERNAL_HISTORICAL_EXCEPTIONS` から、R26 full planning runで観測されなくなった5件だけを削除する。

残すのは、同runでまだ観測されていたENV-ARCHの1件だけである。

同時にコメントへ、equality assertionがstale exceptionの削除も要求することを明記する。

以下は行わない。

- historical exception機構そのものを削除しない。
- structured frozen source coordinatesをこのallow-listへ統合しない。R24/R25で別契約として分離済みである。
- `EXTERNAL_HISTORICAL_EXCEPTIONS`を空にすること自体を目標化しない。実在するhistorical provenanceまで現在pathへ書き換えない。
- 新しいIssueやADRを作らない。

## 5. R24/R25との関係

R24では、current live referenceとfrozen historical coordinateを文字列だけで混同しないようにした。

R25では、そのhistorical coordinateを含むfrozen manifest自身がcurrent lifecycleへ追随して書き換わらないよう、manifest identityを独立に固定した。

R27はさらに別の層である。structured frozen manifestではなく、少数のunstructured historical provenanceに対する明示allow-listについて、**例外理由が消えたらallow-listも縮む**ことを守る。

三者を一つの巨大な例外機構へまとめない。意味の違うものを分けたまま、それぞれの寿命を管理する。

## 6. KJ統合で立った中心構造

> **例外は「一度許したから残す」のではなく、現在も例外である理由が存在する間だけ残す。**

例外管理は追加の審査だけでは閉じない。削除の審査も同じくらい重要である。

今回のguardは `observed == expected` を要求していたため、期待より多い場合だけでなく期待より少ない場合もfailureにした。この対称性が、allow-listを時間とともに自然に縮ませる圧力として働いた。

## 7. Finding triage

### F0 — 生の観察として保持

- R26 run `34023966836` でfocused R26 guardはgreenになった。
- repository-wide planning suiteは136 tests中1 failureを返した。
- failureは5件の「観測されなくなったhistorical exception」を具体的に列挙した。
- ENV-ARCHの1件は差分に現れず、現行exceptionとして残った。

### F1 — 既存guardへ返す

- 観測されなくなった5件を `EXTERNAL_HISTORICAL_EXCEPTIONS` から削除する。
- ENV-ARCHの1件は維持する。
- repository-wide planning suiteを再実行し、例外集合が現在観測と一致するか確認する。

### F2 — 新Issueなし

既存guardが意図どおり検出したstale allow-list cleanupであり、新しい長期作業単位を必要としない。

### F3 — ADRなし

新しいアーキテクチャ判断ではなく、既存の明示例外契約を現在観測へ同期する運用補正だからである。

## 8. 実証境界と次工程

R27は内部planning guardの運用証拠であり、formal cognitive dogfoodのArm結果ではない。Case 001 Arm Cの生実行、第三者価値実証、AI-IR named-provider evidenceへ加算しない。

R27でrepository-wide planning baselineがgreenになり、その先に新しい具体的failureが現れなければ、これ以上のpreflightを増やさずformal mainlineへ戻る。次はfresh context + frozen KJ Atlas UIでのCase 001 Arm C実走である。
