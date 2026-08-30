# Cognitive Dogfood Blind Review Protocol

- Status: Prepared before first valid Case 001 raw run
- Scope: `COGNITIVE-EVAL-01` P2 blind review
- Applies to: Case 001〜003 unless a case preregistration explicitly narrows it
- Related: `cognitive-dogfood-execution-plan.md`, `cognitive-dogfood-run-record-template.md`, `cognitive-dogfood-case-portfolio-preregistration.md`, `cognitive-dogfood-case-portfolio-freeze.md`

## 1. 目的

4armの比較で、reviewerが「KJ Atlasを使った」「cultural-substrate-weavingを使った」と知ったこと自体から期待・反感・方法論バイアスを持ち込むのを減らす。

blind reviewは完全な臨床試験型blindを意味しない。成果物の文体や構造からmethodを推測できる可能性はある。したがって目的は **arm identityとmethod metadataを直接教えないこと**、および **成果の根拠・反証・訂正可能性を先に読むこと** である。

## 2. 公開repoでの情報漏洩境界

KJ Atlas repoは公開されているため、A/B/C/Dを明記したraw record、canvas、InquiryJourney参照、skill execution recordをblind verdict前に同じ公開branchへcommitすると、reviewerがrepoを探索するだけでunblindできる。

したがってCases 001〜003 Round 1では次を守る。

1. raw/result/record/canvas/inquiry-refとarm↔alias mappingは、blind verdict凍結まではreviewerへ見えないoperator workspaceに保持する。
2. GitHubへ先に保存する必要がある場合は、blind reviewerをrepo閲覧不可のfresh contextに限定し、blind package以外のrepository browsing/tool利用を禁止する。ただし原則は1を優先する。
3. blind verdict凍結後に、raw evidence・record・mapping・blind verdictを一緒にrepositoryへ保存して再現可能性を回復する。
4. invalid runもblind review後に削除せず保存する。

「blindを守るためraw evidenceを永久に隠す」ことはしない。blind期間だけ可視性を遅らせる。

## 3. Alias assignment

aliasはA/B/C/Dと意味的に無関係な中立文字列を使う。

- arm execution orderはportfolioで固定した **C → D → B → A** を変更しない。
- alias mappingは最初のblind package生成前にoperator workspaceで作る。
- mappingはblind reviewerへ渡さない。
- mappingはblind verdict凍結後に公開する。
- alias選択は成果の内容を見て意味のある名称を付けない。

例: `opal-17`, `cedar-42`, `linen-08`, `quartz-31` のような無意味な識別子。例示名そのものを固定割当には使わない。

## 4. Blind packageに含めるもの

packageはcase固有のcommon required outputを比較するために必要なものへ限定する。

含める:

- Case ID / Round / neutral alias。
- fixed question。
- §6 Required outputの内容。
- 主要主張のsource path / stable identifier / evidence time。
- counterevidence / uncertainty / deferred points。
- Candidate source requests。
- caseごとに事前登録されたconflict/correction checkについてrunが提示したinterpretation。`T1` / `C2-T1` / `C3-T1`等のexperimenter test IDはpackage生成時に `source-check-N` へ中立化する。
- raw artifactへ戻すためのoperator-only reference ID。ただしreviewerから直接開けない形式にする。

原則として含めない:

- Arm A/B/C/D。
- KJ Atlas canvasを使ったかどうかというtreatment metadata。
- cultural-substrate-weavingを使ったかどうか、framework名、activation判定。
- model/provider名。ただしarm間でmodelが異なるdeviationがある場合はblind reviewの前にrun validityで処理し、package上で説明して比較を歪めない。
- KJカード枚数、島数、操作回数。
- M1〜M9のrun自己評価。
- T9 / InquiryJourney method-friction記録。
- operatorの感想や「このrunは良かった」等の評価語。
- preregistered test IDやexperimenter-onlyの「何を見つけるべきか」という説明。

method固有の自己言及がrequired output本文へ混ざっている場合は、意味を変えずに削除できる範囲だけpackage化時に除く。削除で主張の意味が変わる場合は改変せず、`method identity may be inferable` とだけ記録する。

## 5. Package integrity

blind packageはraw resultの内容を都合よく改善してはならない。

operatorはpackageごとに次を記録する。

- source result artifact ID。
- package生成日時。
- included section一覧。
- method-identity redaction一覧。
- その他の編集: `none` が原則。
- package digest（SHA-256推奨）。

主張、根拠、反証、confidence、deferを言い換えてはいけない。format整形とmethod metadata / preregistered test IDの除去だけを許容する。

## 6. Review stage BR1 — independent package review

各packageを**別fresh reviewer context**で個別評価する。他packageを見せない。

reviewerへは次だけを渡す。

- fixed common source bundle、または同じsnapshotへ戻れる資料集合。
- 1つのblind package。
- `cognitive-dogfood-blind-review-template.md` の評価指示。

BR1では相対順位を付けない。

見るのは主に次である。

- 主要主張がsourceへ戻れるか。
- 古い状態・訂正済み状態・条件付き設計・未実装契約を誤って現在の確定状態として採用していないか。
- 反証が形だけでなく結論を本当に変え得るか。
- 不確実性と保留が適切か。
- unsupported leap / important omissionがないか。
- fixed questionに対する境界案と次の検証が、実証不足に対応しているか。

## 7. Review stage BR2 — cross-package synthesis

4件のBR1が揃った後、別のfresh reviewer contextでcross-package reviewを行う。

入力:

- 4つのblind package。
- 4つのBR1 review。
- 同一のcommon source bundle。
- arm mappingなし。

BR2では初めて差分を見る。

最低限、次を区別する。

1. 全packageに共通して生存した所見。
2. 一部packageだけにあり、sourceへ戻って生存した所見。
3. 一部packageだけにあるunsupported/overclaim。
4. temporal/contract correction、dissent、uncertainty保持の差。
5. fixed questionへの中核回答・境界が実質同じで表現だけ違うケース。
6. 結論は同じでも、decision/revisit可能性に差があるケース。
7. 方法上の追加工程があっても、成果物上の増分が見えないケース。

BR2でもまだA/B/C/Dへunblindしない。

## 8. Verdict freeze and unblinding

BR2のverdictをartifactとして保存し、内容を凍結した後にarm mappingを開示する。

unblind後に行うこと:

- BR2差分をA/B/C/Dへ対応させる。
- M1〜M9のrun recordと照合する。
- KJ Atlas increment、skill increment、D interaction、method-induced harmの候補を分類する。
- C/DのM9/T9を初めて成果差と併読する。
- findingをF0/F1/F2/F3へtriageする。

unblind後にBR1/BR2の元verdictを書き換えない。追加解釈は`post-unblind synthesis`として別に残す。

## 9. Blind review invalidation / limitation

次はblind limitationとして記録する。

- reviewerがarm mapping、raw record、PR #2805の比較仮説を先に見た。
- package固有のmethod名が大量に残り、armがほぼ自明だった。
- packageごとに異なるsource集合を与えた。
- BR1 reviewerが他packageを知っていた。
- BR2前にarm mappingを開示した。
- reviewerへpreregistered conflict/correction testの説明を先に見せ、特定findingを探すよう誘導した。

この場合もreviewを削除しない。`partial blind` / `unblinded` として残し、証拠強度を下げる。

## 10. このprotocolが測らないもの

blind reviewは、KJ AtlasのUI操作性、cultural-substrate-weavingの実行コスト、InquiryJourneyの認知摩擦を直接評価しない。それらはrun recordのM9/T9およびproduct finding triageで扱う。

blind reviewerの好みを「認知能力」の点数へ変換しない。成果物が対象証拠へどれだけ耐えるかを見るための一層である。