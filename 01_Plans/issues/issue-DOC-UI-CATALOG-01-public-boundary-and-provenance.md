# Issue: DOC-UI-CATALOG-01 UIカタログの公開境界分離と鮮度証跡

- Type: Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer / Documentation contributor
- Scope: `04_Documentation/ui_catalog.md`, `04_Documentation/assets/screenshots/README.md`, `04_Documentation/README.md`, `04_Documentation/public_index.md`, `02_Architecture/design/`, `03_Implement/frontend/scripts/capture_*screenshots.mjs`（撮影再現性のみ）
- Related Backlog: `DOC-PUBLIC-BOUNDARY-01`
- Related ADR/Spec: `01_Plans/issues/issue-DOC-PUBLIC-BOUNDARY-01-developer-doc-relocation.md`, `01_Plans/adr/ADR-0023-doc-ops-04-readability-baseline.md`, `01_Plans/adr/ADR-0024-doc-ops-04-quality-gates-boundary.md`, `01_Plans/documentation_quality.md`, `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: DOC-UI-CATALOG-01
- RequirementStatement: 公開UIカタログを利用者向けの現行画面説明へ限定し、内部設計ブリーフを物理分離するとともに、スクリーンショットがどの版をいつ検証したものか追跡できるようにする。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=`ui_catalog.md` がGist公開対象である / 操作=一般利用者がUIカタログを読む、保守者が画像台帳を確認する / 期待結果=公開版に内部課題・ADR・進捗が混入せず、画像の対象版と確認日を判定できる / 除外=UI再設計、スクリーンショット差分基盤の新設。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export / public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

`04_Documentation/README.md` は `ui_catalog.md` を一般利用者向け公開文書・Gist対象としている。しかし `ui_catalog.md` は、前半の利用者向けUI一覧と、後半の外部デザイン支援向け内部ブリーフを同居させている。

- `ui_catalog.md` 冒頭で利用者とUI/UX再設計担当者の二重Audienceを宣言している。
- 「設計見直しの前提と受け渡しブリーフ」以降には、内部ADR、issue ID、完了状態、残課題、テスト契約が含まれる。
- これは `04_Documentation/README.md` と `documentation_quality.md` の「内部Issue/ADR詳細を公開本文へ混ぜない」境界に反する。
- 撮影条件はfixture・locale・viewportを持つが、対象release/tag/commitと最終確認日を持たず、「現行UI」という主張の鮮度を検証できない。

完了済み `DOC-PUBLIC-BOUNDARY-01` の後に再発した回帰であり、単なる文言修正ではなく対象読者・公開ライフサイクル・画像証跡を分離する必要がある。

## 2) 背景 / Context

- 公開入口、保守者入口、開発者入口は既に分離済みである。
- `ui_catalog.md` 前半は利用者にも有用だが、後半は設計入力であり、公開版と更新頻度・責任が異なる。
- スクリーンショットは現行UI説明とリリース確認に使われるため、撮影条件だけでなく、対象revisionと確認結果が必要である。
- 本Issueは既存公開境界を実行するもので、新規ADRは不要である。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 初見利用者が内部設計議論に遮られず、実際の操作と状態を理解できる。
- 安全（THREAT_MODEL / SafeMode）: 内部課題・未確定情報の公開混入を防ぎ、SafeMode/共有前確認の説明を検証済み画像と結び付ける。
- 企業・行政要件（enterprise_architecture）: 公開物の版・確認日・生成条件を追跡でき、監査時に説明可能になる。
- 後方互換（schemas）: 文書分割のみ。UI、データ、画像形式は変更しない。

## 4) 提案する解決策 / Proposed solution

1. 公開 `04_Documentation/ui_catalog.md` は、利用者が現行UIの目的・主要状態・安全境界を理解する内容だけに限定する。
2. 現行の「設計見直しの前提と受け渡しブリーフ」以下を `02_Architecture/design/ui_design_handoff.md` へ移し、内部正本・issue・ADRへのリンクを保持する。
3. 公開カタログ冒頭へ `確認対象（release/tag、未リリース時はcommit）` と `最終確認日` を記載する。
4. `assets/screenshots/README.md` を非公開の画像台帳として扱い、各撮影セットに commit SHA、撮影日、fixture、locale、viewport、生成コマンド、検証結果を残す。
5. UIラベル、fixture、主要レイアウト、SafeMode/共有前確認の表示が変わった場合は画像を stale と判定し、再生成または明示的な再確認なしに公開 Go としない。

非目標:

- UI/UXそのものの再設計。
- 画像差分CIやビジュアルリグレッション基盤の導入。
- 過去画像の完全な撮影履歴復元。
- 内部ブリーフや設計制約の削除。

## 5) 受入条件 / Acceptance criteria

- [x] 公開 `ui_catalog.md` のAudienceが一般利用者・評価担当者に限定される。
- [x] 公開版から `00_Prompt`、`01_Plans`、ADR番号、issue ID、進捗状態、内部残課題、Claude Design向け指示が除かれる。
- [x] 内部設計ブリーフが `02_Architecture/design/` へ移り、元の制約・根拠・リンクを欠落なく保持する。
- [x] 公開版に確認対象revisionと最終確認日がある。
- [x] 画像台帳に commit SHA、撮影日、fixture、locale、viewport、生成コマンド、検証結果がある。
- [x] stale判定のトリガーと、公開を再びGoにする条件が明記される。
- [x] `04_Documentation/README.md` のGist対象表・画像対応表・除外対象が新構成と一致する。
- [x] SafeMode状態、通常/詳細表示、共有前確認の説明と画像が分割時に欠落しない。
- [x] 相対リンクと画像参照がすべて有効である。
- [x] アプリUI・schema・SafeModeの挙動を変更していない。capture scriptは現行画面を再現するためのselector修正と任意browser path追加だけに限定した。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 公開版に残す節と内部へ移す節の移動表を作る。
- [x] T2 内部ブリーフを `02_Architecture/design/ui_design_handoff.md` へ移す。
- [x] T3 公開 `ui_catalog.md` を利用者向け内容へ縮約し、revision/確認日を追加する。
- [x] T4 画像台帳に撮影・検証provenanceテンプレートを追加し、現行セットを1件埋める。
- [x] T5 `04_Documentation/README.md` と `public_index.md` の分類・導線を同期する。
- [x] T6 公開不可語、リンク、画像、SafeMode説明、表示ラベルを検証する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "01_Plans|00_Prompt|ADR-|issue-|UX-NAV|UX-COMPLEXITY|Claude Design" 04_Documentation/ui_catalog.md`
  - `rg -n "確認対象|最終確認日|commit|fixture|locale|viewport|生成コマンド|検証結果" 04_Documentation/ui_catalog.md 04_Documentation/assets/screenshots/README.md`
  - `rg -n "SafeMode|共有前|通常|詳細" 04_Documentation/ui_catalog.md`
  - `git diff --check`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 期待結果:
  - 1つ目の検索は公開版で0件。provenance項目と安全境界は所定ファイルに存在する。
- 未実施時の理由・代替検証:
  - スクリーンショット再撮影ができない場合は現行画像を stale と明示し、公開Goを保留する。文書分割だけを完了扱いにしない。

## 8) 代替案 / Alternatives considered

- 公開カタログから後半を単純削除する: 設計制約が失われるため不採用。
- 文書は分けずAudience注記だけ追加する: 公開生成時の混入リスクと更新責任の違いが残るため不採用。
- `ui_catalog.md` 全体を非公開にする: 利用者に有用な現行UI一覧まで失うため不採用。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 分割時に内部制約または公開安全説明を落とす、画像のrevisionを誤記する。
- 影響範囲: Gist公開内容、外部デザイン依頼、リリース時の画面説明。
- ロールバック手順: 分割コミットを戻し、`ui_catalog.md` を公開対象から一時除外する。公開境界違反の状態へ戻して公開しない。
- 再発防止: `DX-DOC-02` で公開不可語・provenance・リンクの決定論的チェックを追加する。

## 10) Additional context

- 本件は `DOC-PUBLIC-BOUNDARY-01` の回帰是正であり、同IssueのDone判定を遡及変更しない。
- ADR化が必要になる条件: `04_Documentation` の公開対象定義やUIカタログの目的そのものを変更する場合。

## 完了記録 2026-07-11

- 公開 `ui_catalog.md` を利用者・運用者・評価担当者向けへ限定し、内部設計ブリーフを `02_Architecture/design/ui_design_handoff.md` へ物理分離した。
- source revision、最終確認日、23状態の撮影結果、stale判定、公開Go条件を追加した。
- release 5状態、Product Value 6状態、UI catalog 12状態を決定論的fixtureから再生成し、代表7画像を目視確認した。
- 再撮影で発見したselector driftは、重複する`島を作成`のうちヘッダーを明示する既存E2Eと同じ修正で解消した。Playwright管理browserが無い環境向けに任意の `KJ_ATLAS_SCREENSHOT_BROWSER_PATH` を追加し、未指定時の挙動は維持した。
- 公開不可語0件、相対リンク/画像切れ0件、script syntax、撮影コマンド、Markdown体裁を確認した。新規ADRは不要。
