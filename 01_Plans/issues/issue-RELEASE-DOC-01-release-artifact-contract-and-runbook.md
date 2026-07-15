# Issue: RELEASE-DOC-01 リリース成果物契約とタグ実行手順を一致させる

> 現行のタグworkflowは検証用ビルドであり、インストール可能な製品一式を公開する処理ではない。この境界を先に明示し、未配布のものを「リリース済み」と誤認させない。

- Type: Bug / Documentation / Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer / Release contributor
- Scope: `04_Documentation/release.md`, `.github/workflows/release.yml`, `CHANGELOG.md`, `01_Plans/issues/issue-MVP-EXIT-01-productization-readiness.md`, `01_Plans/docs_contract_checks.py`, `01_Plans/tests/test_docs_contract_checks.py`
- Related Backlog: `MVP-EXIT-01`, `PRODUCT-QA-01`, `DOC-OPS-05-12`, `DX-DOC-04`
- Related ADR/Spec: `.github/workflows/release.yml`, `04_Documentation/release.md`, `CHANGELOG.md`, `01_Plans/issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`
- Expected verification level: integration

## Requirement meta I/F（共通キー）

- RequirementID: RELEASE-DOC-01
- RequirementStatement: タグを作る前提、同一commitの品質判定、workflowが生成・保持・公開する成果物、生成しない成果物、失敗時の停止と記録を、手順書・workflow・変更履歴で一貫したリリース契約として示す。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=maintainerが候補commitを出荷しようとしている / 操作=release手順に従って候補を判定しタグを作る / 期待結果=同じSHAの品質証跡、タグ形式、生成物、取得場所、保持境界、非生成物、rollback判断を事前に理解でき、workflow結果と記録を対応付けられる / 除外=本Issueだけでcontainer registry、package registry、自動deploy、署名基盤を新設すること。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export / public-exposure / supply-chain
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 課題

`04_Documentation/release.md`は品質確認を説明する一方、実際にタグを作った後の成果物契約を説明していない。現行`.github/workflows/release.yml`との照合で、少なくとも次の欠落がある。

1. workflowは`v*.*.*`タグのpushで起動するが、手順書にタグ形式、作成位置、事前確認、再タグ禁止がない。
2. backendは`kj-atlas-api:<tag>`としてbuildするだけで`push: false`であり、image archive、registry、GitHub Releaseのいずれにも配布しない。
3. frontendだけが`frontend-dist-<tag>`というGitHub Actions artifactになるが、取得場所、保持期間、対象SHA、検証方法を手順書が示さない。
4. workflowはfrontend test、backend test、docs check、E2Eを再実行しない。`PRODUCT-QA-01`は候補commitの証跡を要求するが、タグ対象SHAと成功したCIを結び付ける手順がない。
5. checksum、provenance、SBOM、署名、version manifestは生成しない。この状態で一時artifactを正式な公開配布物と呼ぶと、利用者が完全性と再取得可能性を過大評価する。
6. `CHANGELOG.md`はSemVerを宣言するが、`[Unreleased]`から版を切る条件とタグ・日付・成果物の対応を説明しない。
7. 手順書は2026-03-03のE2Eログを関連文書として直接参照し、末尾にDOC-OPS作業プロセスと自己修復回数を含む。過去証跡と文書保守者向け工程が、現在の出荷手順に見える。

この欠落は単なる説明不足ではない。タグpushは取り消しにくい外部状態変更であり、担当者が「backendも配布された」「release pageが作られた」「タグ時点で全ゲートを再検証した」と誤認できる。MVPの正式出荷をNo-Goとしている`MVP-EXIT-01`にも、実際に何を出荷するかという出口条件が不足する。

## 対応方針

### Phase A: 現行を検証用タグビルドとして正確にする

まず、新しい配布方式を追加せず、現行挙動を正本化する。

- `release.md`に「タグ前」「タグ作成」「workflow確認」「記録」「失敗・取消」の順で再現可能な手順を書く。
- タグはSemVer形式の`vX.Y.Z`、対象は検証済みcommit SHAとし、同じSHAの必須CIと人間確認が揃うまでpushしない。
- 現行成果物をfrontend Actions artifactだけと明記し、backend imageはbuild検証のみ、GitHub Release・registry image・installer・source archive以外の追加配布物は作らないと明記する。
- Actions artifactの名前、取得場所、GitHub側の実際の保持設定、対象tag/SHA、再取得不能になった場合の扱いを記録する。
- release記録を最低でも`tag / commit SHA / CI run / release workflow run / gate decision / artifact name / retention or expiry / known limitations / rollback or withdrawal`にする。
- `CHANGELOG.md`の版確定手順をタグと対応させ、未確定の`[Unreleased]`をそのまま版済みとして扱わない。
- dated E2Eログは過去証跡としてcurrent手順から分離し、DOC-OPSの工程・自己修復回数・Hold規則はIssue/履歴へ移す。

### Phase B: 公開配布を始める場合だけ別判断へ分離する

利用者へ継続配布することを決めた場合は、公開channel、artifact構成、保持期間、checksum/provenance/SBOM/署名、backend imageのregistry、GitHub Release、撤回方法を別IssueまたはADRで決める。それまではPhase Aのartifactを「検証用」と呼び、READMEやinstallationで一般利用可能な正式配布物として案内しない。

Phase Bは複数の永続的な公開・供給網契約を選ぶため、本Issueの担当者が便宜的にregistryや署名方式を決めない。実利用要求と脅威評価が揃った時点で、ADR-0047の再起票基準に照らす。

## 実施しないこと

- 認証情報を追加してcontainer/package registryへ自動pushすること。
- CI成功だけで人間のGo/No-Goを自動確定すること。
- 既存タグを強制更新すること。
- 一時artifactの保持期間を確認せず、永続配布または復旧元と表現すること。
- SafeMode、share/export、import sanitize、provider=`none`、AI proposal-onlyの既定を変更すること。
- 過去のdated検証ログを現在候補の合格証跡として再利用すること。

## 実行順序と担当境界

1. Release contributorがworkflowのtrigger、permissions、job、生成物、保持設定、非生成物をinventory化する。
2. QA contributorが`PRODUCT-QA-01`のG0〜G7と価値ゲートから、タグ対象SHAに必要な証跡を指定する。
3. Documentation contributorが`release.md`を現行契約と操作手順だけに再編し、形成履歴を分離する。
4. MaintainerがPhase Aの呼称、タグ命名、release記録、再タグ禁止、No-Go時の停止を確認する。
5. DX contributorがworkflowのtag pattern、artifact名、backend `push: false`と手順書の対応を小さな契約テストで固定する。

`DX-DOC-04`はコマンド名・option・pathの実在性を担当し、本Issueはworkflowが意味する成果物と出荷判断を担当する。`DOC-OPS-05-12`の「Improve external」という分類は維持し、完了済み分類Issueを再オープンしない。

## 受入条件

- [ ] `release.md`だけで、候補SHA固定から`vX.Y.Z`タグ、workflow確認、記録、No-Go時の停止までを順に実行できる。
- [ ] タグ対象SHAについて、必須CIと`PRODUCT-QA-01`の人間確認をどのURL/記録で照合するか分かる。
- [ ] frontend Actions artifactの名前、内容、取得場所、対象tag/SHA、保持・失効境界が明記される。
- [ ] backend imageはbuild検証のみで配布されないこと、GitHub Release/registry/installer等を生成しないことが明記される。
- [ ] `CHANGELOG.md`の版・日付・タグ・対象SHAが一意に対応し、`[Unreleased]`の切り出し手順がある。
- [ ] release記録にtag、SHA、CI run、release run、gate decision、artifact、保持境界、既知制限、rollback/withdrawalを残せる。
- [ ] `release.md`からdated E2Eログを現在候補の証跡として使う導線と、DOC-OPS工程・自己修復回数が除かれる。
- [ ] contract testが少なくともtag pattern、frontend artifact名、backend no-push境界の文書driftを検出し、`docs_check.py`から実行される。
- [ ] workflowが変わらないPhase Aでもテストが通り、将来workflowを変える場合は文書との同一PR更新を要求する。
- [ ] SafeMode、share/export、import sanitize、provider=`none`、AI proposal-only、人間の最終判断を後退させない。
- [ ] Phase Bを実施しない限り、公開文書が一時Actions artifactを正式な一般配布物として案内しない。

## 検証計画

- 静的照合:
  - `.github/workflows/release.yml`のtag pattern、artifact name、backend `push`、upload/publish stepを構造的に取得する。
  - `release.md`に同じ値と生成しない成果物の境界が記載されることを確認する。
- 負例fixture:
  - tag patternの変更、artifact名の変更、backend push有効化、publish step追加、文書側の旧値を各々検出する。
- 文書境界:
  - `rg -n "e2e_verification_log_2026-03-03|DOC-OPS-05|自己修復|4回目相当" 04_Documentation/release.md`
  - 期待結果: 0件。
- 統合:
  - `python 01_Plans/docs_check.py`
  - `python -m pytest 01_Plans/tests/test_docs_contract_checks.py -q`
  - `git diff --check`

## リスクとロールバック

- workflowだけを先に変更すると、手順書が再び誤る。成果物境界に関わる変更はworkflow・文書・契約テストを同じPRにする。
- backend配布が必要でもPhase Aでは追加しない。必要性を記録し、Phase Bの判断へ戻す。
- 手順改訂が誤っていた場合はタグや成果物を強制置換せず、該当候補をNo-Go/withdrawnとして記録し、新しいversionで再実行する。

## 完了条件

Phase Aの現行契約が手順書・workflow・変更履歴・契約テストで一致し、maintainerが検証用タグビルドと正式配布の境界を説明できた時点でDoneとする。Phase Bの公開配布基盤は本IssueのDone条件に含めない。
