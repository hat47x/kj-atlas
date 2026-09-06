# 継続dogfood R32 — immutabilityはworking-tree表現ではなくcanonical Git objectで守る

- Date: 2026-09-06
- Scope: 日常開発の自己分析。Case 001〜003の統制比較には含めない。
- Question: frozen manifestのimmutability guardがplatform固有の改行表現までidentityとして扱ったとき、正しいrepository内容を破損と誤認しないために何を正本とすべきか。
- Canvas: `doc_kj_atlas_dogfood_r32.json`
- Observation baseline: PR #3022 / merge commit `00f24fc2e6b74d97da72b3537d1b81564198ab99`
- Guard origin: R25 / `test_frozen_dogfood_manifest_identity.py`
- Result class: Windows working treeで実際に観測されたfrozen-manifest guardのfalse positiveを、repository canonicalization後のidentityへ戻す修正。formal Case、第三者価値実証、AI-IR named-provider測定の結果には数えない。

## 1. R25 guardが守ろうとしていたもの

R25では、Case 001〜003 Round 1 source manifest自体がcurrent lifecycleへ追随して書き換わる再発を止めるため、3 manifestのGit blob OIDを固定した。

狙いは正しかった。Round 1 manifestは過去のformal product snapshotを再構成する入力であり、current repositoryのpath移動に追随してはならない。

ただし実装は、working tree上の `Path.read_bytes()` をそのまま `sha1(b"blob <len>\\0" + content)` へ渡していた。Linux CIではworking treeがLFだったため、repositoryに保存されたGit blobと同じOIDになっていた。

## 2. Windowsで起きた見せかけfailure

PR #3022が記録したWindows環境では `core.autocrlf=true` かつrepositoryの `.gitattributes` は `* text=auto` だった。

そのため同じtracked manifestでも、working tree上ではCRLFを含み得る一方、Gitがindex/objectへ入れる際にはclean filterを通してLFへ正規化する。

実際の観測は次のとおりだった。

- Windows native PythonでR25 testを走らせると3 manifestのraw-byte OIDが期待値と不一致になった。
- `git hash-object <path>` は3件とも固定OIDと一致した。
- `git status` / `git diff` はmanifest無変更を示した。
- したがってformal inputは壊れておらず、guardがplatform固有のworking-tree表現をrepository identityと取り違えていた。

これは単なる「Windowsではテストを再実行する」という運用注意だけでは閉じない。immutability guard自身が、守る対象を誤って定義していたためである。

## 3. guardをrepository canonicalizationへ戻す

R32ではmanifestや固定OIDを変更しない。

代わりに、working-tree bytesをGit自身のclean filterへ通したときに得られるblob OIDを比較対象にする。

`git hash-object --stdin --path=<repository-relative-path>` を使うことで、対象pathに対する `.gitattributes` をGit自身に解釈させる。これにより `* text=auto` の改行正規化を含め、repositoryが実際に保存するobject identityを検査できる。

この方法はGit historyを読む必要はない。必要なのはcurrent repositoryのattributesとGit executableであり、R25の「履歴がなくてもfrozen manifest自身のidentityを守る」という責務は維持する。

## 4. 正常化で意味変更を隠さない

改行差を吸収すると、内容変更まで吸収してしまうguardでは意味がない。そのためR32では二方向のcontrolを同じfiltered helperで持つ。

### platform representation control

Case 001 manifestの内容をいったんLFへ揃え、そこから人工的にCRLF版を作る。

- LF bytes → Git clean filter → 固定OIDと一致
- CRLF bytes → Git clean filter → 同じ固定OIDと一致

これによりLinux CI上でもWindows-like working-tree representationを再現し、改行だけの差がfalse positiveにならないことを固定する。

### semantic mutation control

Case 002 manifest内のAI-ROUTE historical pathをcurrent `issues/done/` pathへ置換するnegative controlは残す。

置換後bytesも同じGit clean filterへ通すが、固定OIDとは一致してはならない。つまり表現変換は正規化しても、snapshot意味を書き換える変更は引き続き検出する。

## 5. KJ統合で立った中心構造

今回の中心は次にまとまる。

> **不変性guardが守るべきなのはplatform依存のworking-tree表現ではなく、repositoryが正本として保存するcanonical Git object identityである。**

R25の中心だった「frozen manifest自体を固定する」は撤回しない。補正するのはidentityの観測点である。

- raw working-tree bytes: checkout環境・改行設定で変わり得る表現。
- Git-clean-filtered blob: repository属性を通した保存対象。
- frozen manifest contract: 後者のidentityを固定する。

これはR24の「同じpath文字列でもcurrent referenceとhistorical coordinateは意味が違う」と同型に、同じ内容でも観測層を誤ると意味を取り違える事例である。ただしR32はpath semanticsではなくrepresentation/canonicalizationの境界を扱う。

## 6. Finding triage

### F0 — 生の観察として保持

- Windows `core.autocrlf=true` のworking treeで3 frozen manifestsがR25 test上だけ不一致に見えた。
- Git filtered hash、status、diffはいずれも実データ無変更を示した。
- 原因はraw `Path.read_bytes()` OIDとGit-clean-filtered blob OIDの混同だった。

### F1 — R25 guardへ返す

- frozen manifest identityはGit clean filter適用後のblob OIDで比較する。
- LF/CRLFのsynthetic equivalence regressionを追加する。
- current `done/` pathへのsemantic rewrite negative controlは同じfiltered helperで維持する。

### F2 — 新Issueなし

原因と修正箇所がR25 guardに局所化され、独立した未完作業を持たないため新Issueは作らない。

### F3 — ADRなし

formal experiment architectureを変える判断ではなく、既存immutability contractの観測点をrepository semanticsへ修正する回帰防止である。

## 7. 実証境界と次工程

R32はcurrent repositoryのcross-platform test false positiveから得た内部所見であり、formal Case 001 Arm Cの結果ではない。第三者価値実証、AI-IR named-provider evidenceにも加算しない。

frozen manifestの内容、固定OID、formal product commit、Arm条件は変更しない。この修正を理由に新しいpreflight、KPI、実験スキーマも追加しない。

新しい具体的な陽性が出なければ、formal mainlineは既知仮説から隔離したfresh contextとfrozen KJ Atlas UIでのCase 001 Arm C実走へ戻る。
