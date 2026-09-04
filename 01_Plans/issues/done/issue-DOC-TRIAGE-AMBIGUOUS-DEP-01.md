# issue-DOC-TRIAGE-AMBIGUOUS-DEP-01 — 同名memoがある依存先を推測で決めない

- Type: Process / Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P1
- Scope: `01_Plans/triage_actionable_plans.py`, `01_Plans/tests/`
- Related ADR/Spec: `ADR-0000`, `DOC-ISSUE-IDENTITY-01`
- Expected verification level: `unit`

## 課題

`triage_actionable_plans.py` は、完了したissue memoが `done/` や `archive/` へ移動した後も既存の依存記述を読めるよう、参照先が見つからない場合にbasenameで補完している。

一方、従来の実装は `basename -> path` の辞書を1つだけ作っていたため、同じbasenameのmemoが複数存在する不正状態では、後から辞書へ入ったpathが暗黙に採用される。通常のrepository検証では `DOC-ISSUE-IDENTITY-01` が同一basenameの共存を拒否するが、triageは単独でも実行できるため、不正状態を読んだときに別のmemoへ静かに結び付けるべきではない。

## 対応

依存先の解決順序を次のように明確化する。

1. 正規化済みの依存pathが実在する場合は、その完全一致を優先する。
2. 完全一致しない場合だけbasenameによる補完を試みる。
3. basenameの候補が1件だけなら、そのpathへ補完する。
4. 候補が複数ある場合は推測せず、依存を未解決のまま保持する。
5. 曖昧な依存は `Ambiguous` blockerとして扱い、候補pathをtriage errorへ列挙する。

この変更はissue memoの重複を許可するものではない。通常の正本では既存validatorが重複自体を拒否し、triage側はその前提が崩れた場合にも誤ったReady判定をしないための第二の防御線を担う。

## 受入条件

- basename補完の候補が複数ある依存はReadyにならない。
- 曖昧な依存の `dependency_stage` は未解決を示す `999` になる。
- triage errorにbasenameと候補pathが示され、どこを直すべきか判断できる。
- 完全一致するpathが存在する場合は、同名memoの存在だけで別pathへすり替えない。
- 候補が1件だけの既存のDone依存補完は維持する。
- 実repositoryのtriage結果に新しい曖昧依存エラーが発生しない。

## 検証

回帰テストでは、`done/` と `archive/` に同名memoがある場合にfail-closedとなることと、完全一致するActive memoがある場合にはそのpathを優先することを確認する。あわせて全triageテスト、実repositoryのtriage、issue memo validator、docs-checkを実行する。
