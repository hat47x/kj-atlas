# Issue Draft: CARD-META-UI-01 カード起票者・出典メタデータUI境界

- Type: Feature request / Security / UX
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD (Productization Program Owner / Security Officer / UX Lead)
- Scope: `02_Architecture/schemas.md`, `02_Architecture/data_model_operations_overview.md`, `02_Architecture/review_attribution.md`, `03_Implement/frontend/src/domain/types.ts`, `03_Implement/frontend/src/canvas/CardView.tsx`, `03_Implement/frontend/src/ui/SidePanel.tsx`, `03_Implement/frontend/src/export/`, `04_Documentation/`
- Related Backlog: `CARD-META-UI-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0056-card-provenance-metadata-boundary.md`（本Issueの境界提案、Accepted 2026-07-16）, `02_Architecture/schemas.md`（`Card.meta` 将来拡張）, `02_Architecture/data_model_operations_overview.md`, `02_Architecture/review_attribution.md`, `01_Plans/issues/issue-DOMAIN-TRACE-01-serial-number-and-source-provenance.md`, `01_Plans/adr/ADR-0033-mvp-data-support-and-maintenance-boundary.md`, `01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: CARD-META-UI-01
- RequirementStatement: カードの状態メタデータ（主張種別・保留・違和感・レビュー状態）と、起票者・作成者・出典・更新者などの provenance/accountability メタデータを混同せず、利用者が必要な情報を自然に確認・入力でき、共有/export/SafeMode/個人情報境界を誤解しないUI方針を確定する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=利用者がカードを作成または選択している / 操作=カード本体・右側詳細パネル・共有前確認を見る / 期待結果=カード本文の状態メタと、起票者/出典/作成日時などの責任主体メタが区別して表示され、未設定時も「未設定」または非表示方針が一貫する。個人を特定し得る値は既定で共有物へ含まれず、含める場合は明示確認とredaction方針がある / 除外=管理者本文閲覧、横断検索、所有者移管、カード個別CRUD API、実名/メールの既定保存。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export / import-sanitize / public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Fixed（`ADR-0056` Accepted 2026-07-16）
- DecisionQueueRef（未確定時の参照先）: Resolved（`ADR-0056` の決定案1〜5で固定）

## Draft→Open 2026-07-16: ADR-0056 Accepted

`ADR-0056` がMaintainer代理裁可によりAcceptedとなった（受理記録は同ADR参照）。本Issueの唯一のDecision Queueゲートが解消したため、Open化する。次の作業はT3（UI仕様案作成）〜T5（フィールド命名・表示責務の調整）であり、それらが完了するまでT6（実装）へは進まない。

## 1) 課題 / Problem statement

カードのUIでは、現在すでに次の状態メタデータが表示される。

- `claimType`: 事実 / 主張 / 仮説。
- `holdState`: 保留 / 未整理 / 棚上げ。
- `critique` / `critiqueTags`: 違和感メモとタグ。
- `textReviewed`: 未レビュー状態の表示。
- `repOf` / `sources`: 統合元や代表カードの補助情報。

一方、カードの起票者・作成者・出典・更新者・取り込み元などの provenance/accountability メタデータは、`schemas.md` で将来拡張 `Card.meta` として残っているが、MVPの標準UI・永続型・共有時の扱いが未確定である。

このままUIだけを先行すると、次の問題が起きる。

- 「レビューした人」と「起票した人」を混同する。
- 共有/export時に、起票者名・メール・組織内識別子などが意図せず含まれる。
- 起票者を変更できるUIが、所有者移管や監査証跡のような高権限操作に見えてしまう。
- カード本文の信頼性、出典の有無、責任主体、レビュー済み状態が同じ表示に混ざり、利用者が判断しづらい。

## 2) 背景 / Context

- `CardView.tsx` には通常フローの meta-row があり、状態バッジはカード本文の上に表示される。
- `SidePanel.tsx` では選択カードの本文、レビュー状態、主張種別、保留、違和感、根拠リンクを確認できる。
- `review_attribution.md` は「レビューした人/いつ」の設計であり、「カードを起票した人/作った人」の設計ではない。
- `schemas.md` は最小 `DocumentV1` では出自情報を持たないと明記し、将来拡張として `Card.meta`（出自情報、タグ、引用元など）を挙げている。
- `data_model_operations_overview.md` は Card を L2 embedded-only とし、個別カードCRUDや個別カード管理UIをMVP標準とはしていない。
- `DOMAIN-TRACE-01` は通し番号と原データ遡及（`seq` / `source`）の実装候補を管理している。本Issueはその上位境界として、起票者・作成者・最終更新者などの個人/組織識別に関わるUI、保存、redaction、ADR要否を扱う。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 誰が何を起票し、何が未確認かを見分けられることは、曖昧さを保った共同作業に必要。
- 安全（THREAT_MODEL / SafeMode）: 起票者や出典は個人情報・組織情報になり得る。共有/exportの既定除外と明示同梱が必要。
- 企業・行政要件（enterprise_architecture）: 組織内では責任主体の把握が重要だが、公開・支援・レビュー共有では最小化が必要。
- 後方互換（schemas）: `Document.version` を据え置いて破壊的に `Card` 必須フィールドを追加しない。optional / view-scoped / artifact-scoped の選択を先に決める。

## 4) 提案する解決策 / Proposed solution

### 4.1 メタデータ分類を先に固定する

| 分類 | 例 | UIの基本方針 | 保存境界候補 |
|---|---|---|---|
| 状態メタ | `claimType`, `holdState`, `critiqueTags`, `textReviewed` | カード上の小さなバッジと詳細パネルに表示 | `DocumentV1.cards[]` 内に既存保存 |
| provenanceメタ | 起票者、作成日時、取り込み元、引用元、外部source id | カード上には常設しない。選択時の詳細パネルで確認し、共有前確認で同梱可否を明示 | `Card.meta` / view-scoped / import artifact のいずれかを要判断 |
| accountabilityメタ | 最終更新者、レビュー者、承認者、所有者 | review attribution / audit / ownerRef と混同しない。編集UIは高権限操作へ見えるため別判断 | `reviewAttribution`, audit log, future owner policy |
| 公開説明用メタ | 「利用者入力」「インポート由来」「AI提案由来」など | 個人を出さずに出所種別を表示する | optional enum / derived label |

### 4.2 UI方針（初期案）

- カード本体: 状態メタだけを短いバッジで表示する。起票者名や識別子はカード上に常設しない。
- 右側詳細パネル: 「カード情報」セクションを設け、起票者・作成日時・出典・取り込み元・最終更新などを表示する。未設定は未設定として扱い、推測補完しない。
- 編集: 起票者や出典を利用者が直接編集できるかは別ゲートにする。初期は表示/非表示と共有前確認を優先する。
- 共有/export: provenanceメタは既定で除外または匿名化する。含める場合は共有前確認で明示し、SafeMode ON時の扱いを固定する。
- import: 外部データから provenanceメタが入る場合、非信頼データとして検証・サニタイズし、指示や権限として扱わない。

### 4.3 ADR化が必要な判断

次のいずれかを行う場合は、実装PRではなくADRまたは本IssueのDecision Queueを先に更新する。

- `Card.meta` を永続スキーマとして追加し、起票者・作成者・出典を保存する。
- 起票者/所有者/作成者を認証主体や `ownerRef` と接続する。
- 実名、メール、外部IdP subject、組織IDを保存またはexportする。
- 起票者編集、所有者移管、監査上の責任主体変更をUIから可能にする。
- 起票者や出典を検索、絞り込み、管理者閲覧、サポート閲覧の標準機能にする。
- SafeModeやshare/exportの既定除外を緩める。

### 4.4 MVPで実装する記録情報の範囲（2026-07-10）

現行スキーマで実装可能な範囲を、責任主体メタデータの決定とは切り離して先行する。

- 右側詳細パネルの折りたたみ式「記録情報」に、カードID、代表カード/出典カードの区別、ドキュメントの作成日時・更新日時を表示する。
- `Card.meta.seq` / `Card.meta.source` は既存の遡及情報エディタで扱う。カードIDや `Card.sources`（統合元カードID）と、文書外部の原データ参照である `Card.meta.source` は別の意味として表示する。
- カード本体には、起票者名、メール、組織ID、所有者、レビュー者を表示しない。
- 現行データモデルに起票者・作成者・最終更新者・レビュー者の主体情報がないため、記録情報内では「提供していない」と明示する。レビュー済みチェックは、誰がレビューしたかを示すものではない。
- この実装ではスキーマ、importの受理キー、共有/exportの既定値、SafeModeの境界を変更しない。主体メタデータの保存・編集・共有は本IssueのDecision Queueに残す。

## 5) 受入条件 / Acceptance criteria

- [x] AC-1: 状態メタ、provenanceメタ、accountabilityメタ、公開説明用メタの分類が `02_Architecture` と本Issueで一致する。
- [x] AC-2: 起票者などの個人・組織識別情報をカード本体に常設表示しない方針、または常設表示する場合の理由とredaction方針が決まっている。
- [x] AC-3: 右側詳細パネルで表示するカードメタ項目、未設定時の表示、編集可否、キーボード操作、フォーカス順が定義されている。
- [x] AC-4: 共有/export/review pack/外部エージェント依頼パッケージに provenanceメタを含めるかどうかの既定値と確認文言が定義されている。
- [x] AC-5: import 由来の provenanceメタは非信頼データとして扱われ、権限・レビュー済み・所有権の根拠にならない。
- [x] AC-6: 実装へ進む場合、代表fixtureでマウス選択・キーボード選択・共有前確認の e2e が通る。
- [x] AC-3a: 現行MVPの実装範囲として、記録情報の折りたたみ表示、未提供の責任主体メタデータの明示、既存の遡及情報エディタとの役割分担が定義され、E2Eで確認できる。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 `schemas.md` と `data_model_operations_overview.md` で `Card.meta` の扱いを「未確定・本Issue管理」に接続する。
- [x] T2 `review_attribution.md` に、レビュー帰属とカード起票者/provenanceメタを混同しない注記を追加する。
- [x] T3 UI仕様案を作る（カード本体、SidePanel、共有前確認、import警告）。
- [x] T4 永続先候補を比較し、Acceptedの`ADR-0056`により主体メタデータをMVPでは永続化しない境界に固定する。
- [x] T5 `DOMAIN-TRACE-01` の `seq` / `source` と衝突しないフィールド命名・表示責務を決める。
- [x] T6 主体メタデータを追加しないMVP境界のもとで、既存の `Card` 型、fixtures、SidePanel、i18n、share/export、import validationを確認し、必要なE2Eだけを追加する。
- [x] T3a 現行MVPの安全な表示範囲（カードID、記録の種類、ドキュメント作成/更新日時、責任主体メタデータ未提供）をSidePanelへ実装し、キーボードで展開できる折りたたみUIとした。
- [x] T6a `card_trace_meta.spec.ts` に、マウスで記録情報を展開し、責任主体メタデータを推測しないことを確認するE2Eを追加した。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans.issues.tests.test_validate_active_issue_memos`
  - `rg -n "CARD-META-UI-01|Card.meta|起票者|provenance|review attribution" 01_Plans 02_Architecture`
- 実装へ進む場合:
  - `cd 03_Implement/frontend && npm run typecheck && npm test && npx playwright test e2e/card_meta_row.spec.ts`
- 期待結果:
  - Draft段階ではdocs-checkが通り、実装許可と誤読されない。
  - 実装段階ではカード選択、詳細パネル確認、共有前確認がマウス/キーボードで検証される。
- 未実施時の理由・代替検証:
  - 起票時点ではUI境界の未確定を記録するため、実装系テストは未実施でよい。実装Issueへ分割する際にe2eを必須化する。

## ADR提案との関係（2026-07-15）

`ADR-0056` を本Issueの境界提案として起票した。提案では、MVPの標準UI・保存・import・共有/exportに主体メタデータを追加せず、既存の非主体メタデータとレビュー帰属を分離する。Decidersの受理までは `DecisionStatus: Pending` と `Status: Draft` を維持し、主体メタデータの実装へは進まない。

## 完了記録（2026-07-16）

- Acceptedの `ADR-0056` に従い、起票者・作成者・所有者等の主体メタデータをMVPでは保存・編集・推測しない境界を維持した。境界変更がないため、新しいADRは起票していない。
- `data_model_operations_overview.md` に、状態、非主体の遡及情報、レビュー帰属、責任主体、公開説明用出所の分類と、表示・操作・共有境界を追加した。
- `schemas.md` に残っていたPending表記をAccepted判断へ更新し、旧 `DocumentV2` 表記を現行の `DocumentV1` へ修正した。
- SidePanelの記録日時を画面言語に合う形式で表示し、元のISO日時は `time` 要素の `dateTime` として保持した。
- `card_trace_meta.spec.ts` でマウス選択、キーボード選択と展開、共有前確認を含む6件が成功した。`pnpm typecheck` とブラウザでの日本語表示確認も成功した。

## 8) 代替案 / Alternatives considered

- 代替案A: `Card.meta` をすぐに追加する。
  - 不採用理由: PII、共有/export、review attribution、所有者移管との境界が未確定。
- 代替案B: review attribution の `ownerRef` をカード起票者として流用する。
  - 不採用理由: `ownerRef` はレビュー/所有責任の補助であり、カード作成・出典・取り込み元を表すものではない。
- 代替案C: カード本体に起票者名を常時表示する。
  - 不採用理由: 初期表示の認知負荷と個人情報露出が増える。必要なら詳細パネルまたは明示モードに置く。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 起票者メタがレビュー済み・所有者・承認者と混同される。
- 影響範囲: `Card` スキーマ、SidePanel、CardView、share/export、review pack、external agent package、import validation、SafeMode、public documentation。
- ロールバック手順: 実装前なら本IssueをDraft維持し、`Card.meta` を将来拡張扱いへ戻す。実装後に問題が出た場合は、UI表示とexport同梱をfeature flagまたはSafeMode policyで無効化し、永続データはoptionalとして無視できるようにする。

## 10) Additional context

初期判断:

- 既存の `CardView` meta-row は状態表示の置き場所として維持する。
- 起票者などのprovenanceメタは、カード本体ではなくSidePanelの「カード情報」候補として扱う。
- 現行MVPでは、SidePanelの「記録情報」に既存ID・記録種別・ドキュメント日時だけを表示し、起票者などは未提供と明示する。
- 共有/exportでは、個人・組織識別情報を既定で含めない。
- `Card.meta` を導入するか、view-scopedにするかは未確定。ここが本Issueの主要Decision Queueである。

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（カード本体に起票者を常設しない初期案） / 保留操作の距離=不変 / 取り消し導線=実装時に必要（編集可能にする場合はundo対象）。

## Traceability

- Related: `02_Architecture/schemas.md`（`Card.meta` 将来拡張）
- Related: `02_Architecture/data_model_operations_overview.md`（CardはL2 embedded-only、個別CRUDなし）
- Related: `02_Architecture/review_attribution.md`（レビュー帰属と起票者メタの分離）
- Related: `01_Plans/issues/issue-DOMAIN-TRACE-01-serial-number-and-source-provenance.md`（通し番号・原データ出典の具体実装候補）
- Related: `03_Implement/frontend/e2e/card_meta_row.spec.ts`（状態メタ行の既存UI証跡）
- Derived-from: 2026-07-06 ユーザー指摘「カードの起票者などのメタデータについてのUIが未確定」
