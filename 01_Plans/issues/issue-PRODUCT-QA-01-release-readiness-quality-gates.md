# Issue: PRODUCT-QA-01 製品化リリース準備の品質ゲート定義

- Type: Process
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P0
- Owner: Maintainer / QA contributor
- Scope: `01_Plans/`, `03_Implement/frontend/`, `03_Implement/backend/`, `04_Documentation/`
- Related Backlog: `PRODUCT-QA-01`, `MVP-EXIT-01`
- Related ADR/Spec: `01_Plans/issues/issue-MVP-EXIT-01-productization-readiness.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`
- Expected verification level: `integration`

## 目的

製品化候補を感覚で出荷せず、安全、主要操作、表示品質、公開文書、診断、回帰を同じ基準で判定できるようにする。本Issueはゲート定義の正本であり、リリース候補ごとの実行ログはCI、PR、releaseへ残す。

## 適用範囲

- リリース候補ではG0〜G7を評価する。
- 通常PRでは変更に関係するゲートだけを検証し、全ゲートの記録を要求しない。
- 未達が実際の製品・テスト・文書の欠陥なら、修正可能な単位で内部issueへ戻す。
- 実行結果の転記だけを目的とするissue、ADR、手書きdashboard更新は作らない。

非目標:

- 将来機能をすべて完成させること。
- CI合格だけで人間による出荷判断を代替すること。
- 画面差分がない変更でスクリーンショットを再取得すること。

## 品質ゲート

| Gate | 判定対象 | 区分 | Go条件 | No-Go条件 | 主な証跡 |
| --- | --- | --- | --- | --- | --- |
| G0 計画整合 | issue / ADR / 依存関係 | 必須 | 実装課題と長期判断が分かれ、未解決依存が追跡できる | 未確定の安全・互換判断を実装だけで確定する | triage、対象issue |
| G1 安全既定 | SafeMode / 取り込み / 共有 | 必須 | SafeMode既定ON、import sanitize、共有前確認が画面・文書・テストで一致する | 未レビュー情報の共有やSafeMode OFFが既定になる | safety tests、対象E2E |
| G2 主要操作 | 開始 / 選択 / 編集 / 保存 / 共有 | 必須 | マウスとキーボードで主要操作へ到達し、結果と戻り方が分かる | 操作不能、見切れ、選択対象不明、復帰不能がある | Playwright、representative user-operation evidence lane |
| G3 日本語UI | i18n / 表記 / 用語 | 必須 | 一般利用者向け主要UIに未翻訳や不自然な用語がない | 主要ボタン、警告、状態に英語や内部語が残る | i18n tests、目視確認 |
| G4 画面耐性 | 小画面 / 大文書 / 待機・失敗 | 必須 | 代表viewportで見切れず、待機、失敗、復帰が理解できる | 安全情報や主要操作が隠れる | viewport E2E、必要時の画像 |
| G5 公開文書 | 公開index / 操作説明 / 画像 / link | 必須 | 使い方に集中し、実装と一致し、内部管理情報を含まない | 内部issue・ADR進捗や古いUIを公開する | docs check、リンク確認 |
| G6 診断とサポート | エラー / 診断 / 復旧 | 推奨 | 次の行動が分かり、機微情報を不用意に共有させない | エラー後の復旧不能、過剰な診断情報共有がある | diagnostics、復旧演習 |
| G7 ビルドと回帰 | frontend / backend / docs | 必須 | 変更リスクに対応するtypecheck、unit、integration、E2Eが成功する | 必須失敗が未分類、または代替検証の根拠がない | CI、ローカル検証 |

## 価値ゲート

| Value Gate | Go条件 | No-Go条件 | 戻し先 |
| --- | --- | --- | --- |
| V0/V1 初回価値実感 | 最初の意味あるカード配置と保留点へ到達できる | 次の操作が分からず外在化を始められない | `PRODUCT-VALUE-01` |
| V2 保留・違和感 | 未確定、違和感、根拠不足を作業状態として残せる | 未確定情報が消える、または確定扱いになる | `PRODUCT-VALUE-02` |
| V3 人間レビュー | AI提案を比較、部分採用、保留、破棄できる | auto-applyやAIによる `human_reviewed` 昇格がある | `PRODUCT-VALUE-02`, `CE-*` |
| V4 レビュー可能な成果物 | 確定点、保留点、根拠への戻り方が共有物で分かる | 読みやすさと引き換えに根拠や未確定点が失われる | `PRODUCT-VALUE-03` |
| V4a メタデータ境界 | 出典と主体メタを区別し、主体メタを既定共有しない | 起票者等が出典トグルだけで共有物へ混入する | `DOMAIN-TRACE-01`, `CARD-META-UI-01` |
| LLM任意性 | `KJ_ATLAS_LLM_PROVIDER=none` でも主要価値が成立する | LLM接続なしでは基本操作を完了できない | `PRODUCT-VALUE-01`, `PRODUCT-VALUE-02` |

## 判定方法

1. 候補commitと変更範囲を固定する。
2. リリース候補では必須ゲートをすべて、通常PRでは影響するゲートを実行する。
3. 結果を `result / evidence / owner / due` でPRまたはreleaseへ記録する。
4. 失敗を `product defect / test defect / environment limitation` に分類する。
5. BlockerはNo-Go、未解消Majorは原則No-Go、Minorはownerと期限を記録してConditional Goを選べる。
6. 最終判断を `Go / Conditional Go / No-Go` から選ぶ。

重大度:

- **Blocker**: データ損失、安全境界違反、主要操作不能、必須テストの説明不能な失敗。
- **Major**: 主要経路の大きな摩擦、復旧困難、一般利用者が判断を誤る表示。
- **Minor**: 回避可能で安全・データ・主要価値を損なわない問題。

自己修復は同じ原因に対して3回までとし、4回目相当は停止して再開条件を記録する。

## Gate Recordテンプレート

```md
## Productization Gate Record

- Candidate: <PR / release / commit>
- Scope:
- Result:
  - G0..G7: Go / Conditional Go / No-Go / N/A
  - V0..V4: Go / Conditional Go / No-Go / N/A
- Evidence: <CI / E2E / review link>
- Remaining Blocker / Major / Minor:
- Required follow-up issue:
- Decision: Go / Conditional Go / No-Go
```

このテンプレートはPRまたはreleaseへ一度だけ記録する。本Issueへ候補ごとのGate Recordを追記しない。

## 現在のベースライン

2026-07-15の最終記録では、次を確認した。

- frontend typecheck成功、Vitest 190 files / 1,034 tests成功。
- Playwright full suite 165 / 165成功。
- SafeMode、共有、取り込みの安全境界に変更なし。
- `ADR-0052`のcanvas card / menu form移行と関連accessibility issueを完了。
- Composeによる新規DB migration、保存往復、再起動永続性を確認。
- バックアップ、別DBへの復元、API停止・保存失敗・Web停止からの復旧を確認。

この結果は当時の候補に対する証跡であり、将来候補の合格を保証しない。詳細な過去Gate RecordはGit履歴で参照する。

現在も出荷時に人間が判断する項目:

- 最終プログラム承認。
- 物理キーボードとスクリーンリーダーによる受入確認。
- 公開文書に掲載するリリース画面の確認。
- 組織導入時にのみ必要な組織内承認。

`DATA-MAINT-04`のscope選択や外部接続の将来レーンは、それぞれのissueで扱い、本ゲート定義の未完了には数えない。

## 受入条件

- [x] UI/UX、i18n、安全、import/export、E2E、文書、診断のGo/No-Go基準がある。
- [x] 各ゲートに判定条件と証跡種別がある。
- [x] 未達を既存issueまたは新しい欠陥issueへ戻せる。
- [x] スクリーンショットは公開文書、視覚回帰、重要動線の確認に限定される。
- [x] 環境変数、安全、共有、取り込み、公開範囲の不変条件を含む。
- [x] 既存データの互換性と復旧可能性をG1/G6/G7で評価できる。
- [x] 候補ごとの反復ログを本Issueへ追記しない運用が明記されている。

## 検証

- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py 01_Plans/tests/test_triage_actionable_plans.py`
- `cd 03_Implement/backend && python -m pytest tests/test_qa_e2e_doc_contract.py -q`
- `git diff --check`

リリース候補の実検証は `03_Implement/frontend/docs/e2e_testing.md` とCIを使用する。環境制約で実行できない項目は、対象scenario、失敗分類、代替証跡、再開条件を記録し、未実施を成功扱いしない。

## 完了判断

品質ゲート、重大度、証跡形式、戻し先、停止条件を定義済みのため、本IssueはDoneとする。実リリースの可否は `MVP-EXIT-01` と候補PR/releaseで判断する。

新ADRは起票しない。本変更はAccepted済みの `ADR-0039` に従い、反復運用ログを正本から外す整理であり、安全・互換・公開境界を変更しない。
