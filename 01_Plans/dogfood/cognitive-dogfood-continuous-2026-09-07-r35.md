# 継続dogfood R35 — 実行可能な文書契約では意味比較の前に表現が読めなければならない

Date: 2026-09-07
Canvas: `doc_kj_atlas_dogfood_r35.json`

## 1. Trigger

R34統合直後のmainで、PR #3035〜#3037が公開設定文書の追加driftを修正した。

- #3035は `KJ_ATLAS_LLM_TASK_MODEL_MAP` のdefaultがBackend Settingsでは空文字、runtime registryでも「未設定（空文字）」なのに、利用者向けconfigurationだけ「未設定」となっていた。これはR29/R34で既に整理したscalar/default contractの再発である。
- #3037はfrontend/runtime registryが `saas-multitenant` を「予約中」と残していた一方、現行Backend/Frontendは4 named profileを正式処理していた。これはR34で整理したcurrent profile/state contractの再発である。
- 一方 #3036 は異なる。`KJ_ATLAS_DEEPSEEK_THINKING_MODE` の意味上の許容集合は実装と文書意図の双方で `{disabled, enabled}` と一致していた。それでもruntime registryのMarkdown表では `` `disabled|enabled` `` と1つのcode span内へraw `|` を置いたため、表の列区切りとして解釈され得て、enum監査でもPurpose cellが ``DeepSeek ... `disabled`` までで切断された。

つまり#3036では、値の意味がdriftしていたのではなく、**意味を運ぶ文書表現そのものが構造的に読めなくなっていた**。

## 2. KJで分けて見えたもの

### A. semantic correctnessだけではexecutable contractにならない

#3036以前も、Settingsの受理集合は `disabled` / `enabled` であり、registryの執筆意図も同じ2値だった。したがって人が文字列だけを見れば「意味は合っている」と判断できる。

しかしMarkdown tableのcell delimiterと値表現に使ったraw `|` が衝突したため、表を構造として読む側には別の列境界が見えた。静的監査ではPurpose cellが途中で切れ、必要な値を完全には取得できなかった。

ここではsemantic equality以前に、contract carrierが安定してparseできることが前提になる。

### B. 修正は意味を変えず、carrierを曖昧でない形へ戻した

#3036は値集合を変更していない。registry表現を `` `disabled|enabled` `` から `` `disabled` / `enabled` `` へ変え、Markdown tableのdelimiterと値の区切り記法を分離した。

同時に既存のpublic enum contractを拡張し、Settingsの `{disabled, enabled}` と利用者向けconfigurationの有限集合を厳密比較し、runtime registry Backend settings行にも両値が明示され続けることを確認するようにした。

同じraw-pipe表崩れを戻すと、registryの値欠落として既存focused contractが検出できる。新しいrepository-wide Markdown linterを追加する必要はなかった。

### C. R34のshape-aware conformanceには前段がある

R34ではscalar/default、finite enum、delivery surface、wiring state、ADR factual premiseというcontract shapeごとに、対応する実行可能な正本照合を選ぶと整理した。

R35で加わるのは、その比較より一段前である。finite enumを集合として比較するにしても、public tableから集合を安定して取り出せなければ集合比較へ到達できない。

したがって実行可能な文書契約は、少なくとも次の二段として扱うのがよい。

1. **representation / carrier integrity** — 対象surfaceを一意にparseでき、必要なcell・値を欠落なく取得できること。
2. **semantic conformance** — 取得したdefault・enum集合・delivery集合・wiring fact等が対応する実装正本と一致すること。

表現は単なる見た目ではなく、機械照合の対象になったsurfaceではcontract transportの一部になる。

### D. ただしMarkdown全体を機械契約へ変えない

#3036から「repository内の全Markdown表を厳密parserで固定する」へ進むのは過剰である。

厳密なcarrier integrityが必要なのは、R34でいうcurrent contractを公開し、かつfocused testがその構造を実際に読み取る狭いsurfaceである。歴史説明、自由記述、KJカード本文、通常の設計解説まで同じgrammarへ押し込めない。

今回も新しいgeneric guardは作らず、既存public enum contractの読み取り経路でraw-pipe再導入を意味欠落として検出できる状態へ戻した。

## 3. 中心所見

**実行可能な文書契約では、意味が正しいだけでは足りない。その意味を運ぶ表現が一意に読めて初めて、shape-awareな正本照合へ進める。**

R34が「何をどう比較するか」を分けたのに対し、R35は「比較対象を正しく取り出せるか」をその前提として分離する。

## 4. R34との境界

- R34: current contractのshapeに応じて、scalar値・finite set・delivery set・wiring dataflow・ADR factual premiseなど、適切な正本と比較方法を選ぶ。
- R35: そのshapeを文書surfaceから抽出するcarrier自体が、delimiter衝突等なく安定して読めることを先に保証する。

したがってR35はR34を置き換えない。**carrier integrity → semantic conformance** の順でつなぐ。

## 5. Finding triage

- F0: PR #3036で実際に観測された、意味集合は正しいがMarkdown table carrierがraw `|` により構造的に壊れ、enum監査でもcellが切断された陽性。
- F1: 既存 `test_public_configuration_enum_contract.py` のfocused contractへ所見を戻す。raw-pipe再導入時は値欠落として検出できる。
- F2: 新Issueなし。repository-wide Markdown parser/linterを追加しない。
- F3: 新ADRなし。文書contractの検査責務の補足でありarchitecture decision変更ではない。

#3035/#3037はR34の既存shape分類で説明できるため、R35の独立triggerには数えない。

## 6. 非主張

R35はcontinuous/internal dogfoodであり、Case 001〜003のformal cognitive comparison、AI-IR named-provider evidence、第三者product-value validationを代替しない。

formal P1の現在地は変わらない。次の正式工程はfresh isolated context + frozen KJ Atlas UIでのCase 001 Arm C実走である。
