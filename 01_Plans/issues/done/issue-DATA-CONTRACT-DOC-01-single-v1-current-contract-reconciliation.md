# Issue: DATA-CONTRACT-DOC-01 単一DocumentV1の現行契約文書を再整合する

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、既に採択・実装された単一V1契約の文書回帰だけを是正する。

- Type: Bug / Documentation
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer / Data contract contributor
- Scope: `02_Architecture/schemas.md`, `02_Architecture/contract_reading_guide.md`, `02_Architecture/contract_consolidation_inventory.md`, `02_Architecture/api.md`, `02_Architecture/data_model_operations_overview.html`, `03_Implement/frontend/e2e/card_quality_assistance.spec.ts`, `03_Implement/frontend/src/import/zip_import.test.ts`, `01_Plans/issues/issue-DATA-CONTRACT-RESET-01-document-v1-rebaseline.md`, `01_Plans/docs_contract_checks.py`, `01_Plans/tests/test_docs_contract_checks.py`
- Related ADR/Spec: `01_Plans/adr/ADR-0058-document-contract-v1-rebaseline.md`, `02_Architecture/schemas.md`, `02_Architecture/api.md`, `02_Architecture/data_model_operations_overview.html`
- Expected verification level: integration

## Requirement meta I/F（共通キー）

- RequirementID: DATA-CONTRACT-DOC-01
- RequirementStatement: ADR-0058で採択・実装された唯一の完全な`DocumentV1`契約へcurrent architecture文書と現行fixtureを同期し、旧`DocumentV2`/version 2/Legacy読込契約の再混入を`DC-ARC-001`で防止する。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=単一V1実装とADR-0058がmainへ統合済み / 操作=current architectureと現行fixtureを読み、docs-checkと契約testを実行する / 期待結果=永続Documentの型・版・必須key・support levelが単一V1で一致し、旧V2入力は負例だけに残る / 除外=過去ADR・Done issue・historyに記録された当時のDocumentV2表記、将来の明示的DocumentV2導入。
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: import-sanitize / SafeMode / share-export

## 課題

ADR-0058と`DATA-CONTRACT-RESET-01`は、旧最小V1と旧V2を廃止し、現行の完全な構造を唯一の`DocumentV1` / `version: 1`へ再基線化した。frontend/backendの主要実装はV1へ変更され、API文書とデータ運用俯瞰もV1を説明する。一方、2026-07-15のlatest mainを横断監査すると、完了宣言と矛盾する残存が見つかった。

- `schemas.md`には`DocumentV2` / version 2 / version 3 /旧Legacy読込/mock dv2に該当する行が29行残る。
- §3.4は旧最小`DocumentV1`（cards/edgesだけ）を定義し、§3.5は現在の完全構造を`DocumentV2` / `version: 2`として別定義するため、同一current文書内でADR-0058と正反対の二重契約になっている。
- §6.1は`version: 1`または欠落をLegacyとしてV2へ正規化すると記すが、現実装は数値`version: 1`と`islands`等の現行必須構造を要求し、旧V1・version 2・版欠落をfail-closedで拒否する。
- `contract_reading_guide.md`と、current契約値ではないものの保守作業の入力となる`contract_consolidation_inventory.md`も旧V2を現行合成型として案内する。
- `card_quality_assistance.spec.ts`の成功系fixtureが`version: 2`を返す。これは`validate.test.ts`が明示的に拒否する版であり、E2Eが実行されると開始文書の読込契約と衝突する。
- `zip_import.test.ts`の「supported files」fixtureにも`"version":2`が残る。ZIP輸送層だけのテストでも、成功例として残すDocument JSONは現在の公開契約へ合わせ、旧版は拒否を検証する負例だけに限定する必要がある。
- `DATA-CONTRACT-RESET-01`はT1「現行正本文書を新V1へ同期」をDoneとしているため、未処理作業が既存キューから見えない。

影響は文言の古さに留まらない。実装者が`schemas.md`を正本として旧V2を再導入する、import移行を誤って実装する、optional fieldの保存保証やSafeMode/share-export境界を旧版へ結び付ける危険がある。`DX-DOC-02`の`DC-ARC-001`はこのclean baselineがないため有効化できない。

## 対応方針

実施すること:

1. `schemas.md` §3.4/§3.5を、現在の完全構造を持つ単一`DocumentV1` / `version: 1`定義へ統合する。`islands`は必須、その他の現行optional fieldと安全注記は失わない。
2. current節の永続Document参照、polygon/階層/shelf/矛盾決定/外部接続加算、mock schema識別子、versioning/support levelをV1へ同期する。
3. 旧V1→V2正規化、version 2 Full/Partial、version 3以降という現行でない移行規範を削除し、未知版・欠落・旧最小構造を拒否する現行gateと、将来の破壊的変更は明示的な次versionと移行判断を要することを記す。
4. `contract_reading_guide.md`を単一V1の合成型へ同期する。`contract_consolidation_inventory.md`は履歴/作業inventoryであることを維持しつつ、現在値として読まれる旧V2表現を「ADR-0058前の形成対象」と明示するかhistoryへ移す。
5. `card_quality_assistance.spec.ts`と`zip_import.test.ts`の成功系fixtureを`version: 1`へ同期し、旧version 2は`validate.test.ts`等の明示的負例だけに残す。
6. `DATA-CONTRACT-RESET-01`の完了記録へ本follow-upを追記し、Doneを過去の実装完了記録として保ったまま、文書回帰を隠さない。
7. clean baseline後、`DC-ARC-001`へ少なくとも「単一Document型定義」「version 1」「旧Legacy規範なし」「APIのDocumentV1」「DocumentV1支援表」の決定論的検査と負例fixtureを追加する。

実施しないこと:

- 過去ADR、Done issue本文、`02_Architecture/history/`に記録された当時の`DocumentV2`という事実の削除。
- runtimeの再設計、DB正規化、個別CRUD追加、optional fieldのsupport level変更。
- 将来の`DocumentV2`を先回りして定義すること。
- 文字列一括置換だけで型名を変え、旧最小V1と完全型を二重定義したままにすること。

## 実行順序と分担境界

1. Data contract contributorが実装型とvalidatorを基準に、`schemas.md`の単一合成型と版規範を直す。
2. 同じ担当者が`api.md`、運用俯瞰、reading guide、inventoryを突き合わせる。任意fieldや安全注記の欠落があれば先へ進まない。
3. Frontend contributorが2つの成功系fixtureをV1へ直し、旧版拒否testを維持する。
4. Documentation quality contributorが`DC-ARC-001`を有効化し、正常/負例fixtureとdiagnosticを追加する。
5. MaintainerがDone issueへのfollow-up導線、全検証結果、SafeMode/share-export非回帰を確認する。

各段階を別PRに分けてもよいが、後段は前段のclean baselineを前提とする。`DC-ARC-001`だけを先行して既知の失敗を全PRへ波及させない。

## 受入条件

- [x] `schemas.md`で永続Documentのexport型定義が完全な`DocumentV1` 1件だけで、`version: 1`と必須`islands`を持つ。
- [x] current architecture 4文書が永続Documentを単一V1として説明し、API/schemaの版と必須keyが一致する。
- [x] current規範から旧V1→V2正規化、version 2 Full/Partial、version 3前提、mock dv2がなくなる。
- [x] optional field、polygon、階層、shelf、矛盾決定、外部接続、安全境界の意味とsupport levelが再基線化前後で欠落しない。
- [x] `contract_reading_guide.md`がV1合成型へ案内し、inventoryの旧V2記録はcurrent値と誤認できない。
- [x] `card_quality_assistance.spec.ts`と`zip_import.test.ts`の成功系がversion 1を使い、version 2拒否の負例testは残る。
- [x] `DC-ARC-001`の正常/負例fixtureがあり、現行repositoryでfinding 0となる。
- [x] SafeMode、share/export、proposal-only、`human_reviewed`人手限定を緩めない。
- [x] `DATA-CONTRACT-RESET-01`から本follow-upへ到達できる。

### 実装証跡（2026-07-16）

- `schemas.md`: §3.4/§3.5の二重`Document`定義（旧最小`DocumentV1`と`DocumentV2`）を単一の`DocumentV1`（`version: 1`、`islands`必須、全optional fieldとsafety注記を保持）へ統合した。§6.0.1/§6.1のversion運用ルールを、Full/Partial/Legacy 3区分・`version: 3`以降の拡張余地という記述から、「`version: 1`以外はすべてfail-closedで拒否し、旧版正規化経路は存在しない」という現行実装どおりの記述へ書き換えた。`mockSchemaVersion`を`mock-2026-05-19-dv2`から`mock-2026-07-16-v1`へ更新した。残る19箇所の`DocumentV2`/`version: 2`本文参照（§7A、§14、§16-18等）をすべて`DocumentV1`/`version: 1`へ更新した。DOMAIN-KJ-01のEdge型語彙version（§3.3、無関係な別概念）は変更していない。
- `contract_reading_guide.md`: §4のCard/Document合成型参照を`DocumentV2`/§3.5から`DocumentV1`/§3.4へ更新した。
- `contract_consolidation_inventory.md`: 冒頭に注記を追加し、本書内の`DocumentV2`/§3.5表記がADR-0058前の形成対象を指すpre-rebaseline名称であることを明示した（本書自体はStatus: Informative working inventoryのため、Conflict inventory表の値自体は変更していない）。
- `api.md`、`02_Architecture/data_model_operations_overview.html`: 事前確認の結果、既にV1で記述済みであり変更不要だった（実装者は既に移行済みで、文書側の2ファイルのみが取り残されていた）。
- `card_quality_assistance.spec.ts`（T7で新規作成した本issueとは別のe2e spec）・`zip_import.test.ts`: 成功系fixtureの`version: 2`を`version: 1`へ修正した。`validate.test.ts`の拒否負例（`version: 2`が拒否されることを確認するテスト）はそのまま維持した。
- `01_Plans/docs_contract_checks.py`: `DC-ARC-001`（`check_document_contract_baseline`）を新規実装した。(a) `schemas.md`内の永続Document型定義が1件のみであること、(b) その型が`DocumentV1`/`version: 1`であること、(c) `DocumentV2`/`Legacy`という語がcurrent文書に再出現しないこと、(d) `api.md`/`02_Architecture/data_model_operations_overview.html`が`DocumentV1`を参照し`DocumentV2`を参照しないこと、を検証する。`01_Plans/tests/test_docs_contract_checks.py`に正常系1件・負例4件（型重複、DocumentV2/Legacy再混入、誤った型名・version、api/data-model側の参照欠落）を追加した。
- `01_Plans/issues/issue-DATA-CONTRACT-RESET-01-document-v1-rebaseline.md`: Follow-upセクションを追記し、T1-T5のDone記録を過去の実装完了記録として保ったまま、文書側の回帰是正を本issueへ切り出したことを明記した。

検証結果:
- `python 01_Plans/tests/test_docs_contract_checks.py`（unittest経由）: 14/14 pass（新規5件含む）。
- `check_document_contract_baseline` / `check_current_history_headings` を現行repositoryへ直接実行: 0 findings。
- `rg -n "DocumentV2|version: 2|version: 3|mock-2026-05-19-dv2|Legacy.*version" schemas.md contract_reading_guide.md`: 残存4件はすべて非規範（Edge型語彙version 1件、および本issueが追加した「V2/Legacyは存在しない」という説明文3件）で、current値としては0。
- `rg -n "\bDocumentV2\b|version\s*:\s*2|\"version\"\s*:\s*2" 03_Implement`: 残存1件は`validate.test.ts`の明示的拒否負例のみ。成功系fixtureは0。
- `04_Documentation`にも`DocumentV2`残存がないことを確認した（issueのScope外だが追加確認）。
- frontend: `npm run typecheck`クリーン、`npx vitest run` 1063/1063 pass（既存の無関係な1ファイル失敗はリポジトリルート非同梱の副作用、T4-T7と同じ）。
- backendのroundtrip/API contract testは本セッションでは未実行（環境上Python側のpytestランナーが利用できず、unittestで代替検証した範囲に留まる）。

### Maintainer完了確認（2026-07-16）

- `python 01_Plans/docs_check.py` が成功し、Active memo 25件・追跡Markdown 377件で文書契約違反がないことを確認した。
- backendのデータ運用・Document往復契約は31 passed / 21 skipped、frontendのV1 validator・ZIP import契約は26/26 passedだった。
- `DC-ARC-001`、Done issueへのfollow-up導線、単一V1成功系、旧version 2のfail-closed負例を再確認した。SafeMode、share/export、proposal-only、`human_reviewed`人手限定の変更はない。
- 全受入条件と段階5のMaintainer確認を満たしたため、本issueをDoneとする。

## 検証計画

- `rg -n "DocumentV2|version: 2|version: 3|mock-2026-05-19-dv2|Legacy.*version" 02_Architecture/schemas.md 02_Architecture/contract_reading_guide.md`
  - 期待結果: current値としては0。過去形成の説明を残す場合は、非規範であることを同じ段落に明示する。
- `rg -n "\\bDocumentV2\\b|version\\s*:\\s*2|\\\"version\\\"\\s*:\\s*2" 03_Implement --glob '!**/node_modules/**' --glob '!**/.venv/**'`
  - 期待結果: 明示的な拒否負例だけ。成功系fixtureは0。
- `python 01_Plans/docs_check.py`
  - 期待結果: `DC-ARC-001`を含め0終了し、対象ファイル/rule ID/修正先を表示できる。
- frontendの`validate.test.ts`、`zip_import.test.ts`、`card_quality_assistance.spec.ts`、backend roundtrip/API contract tests。
  - 期待結果: 単一V1の成功系と旧版fail-closedが両方成功する。

## 補足

- 新規ADRは不要。採択済みADR-0058の実装・文書同期漏れであり、判断を変えない。
- rollbackは本issueの文書変更だけを戻すのではなく、ADR-0058全体を再検討する場合に限る。旧二重契約へ部分的に戻さない。
- `DC-ARC-001`はこのissueのclean passまで未有効を維持し、既知の失敗をCI blockingへ昇格して他のdocs変更を全面停止しない。
