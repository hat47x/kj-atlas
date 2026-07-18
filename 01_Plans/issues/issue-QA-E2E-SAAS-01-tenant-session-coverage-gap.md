# Issue: QA-E2E-SAAS-01 TenantSession UIのE2Eカバレッジがゼロ

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/e2e/`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `01_Plans/issues/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md`
- Expected verification level: `e2e`

## 課題

- 現在の問題: `03_Implement/frontend/src/ui/TenantSessionControl.tsx`、`TenantSessionRuntimeGate.tsx`、`TenantSessionBootstrapGate.tsx`はいずれも実装・unit testを持ち、`main.tsx`から実際に配線されている（`TenantSessionBlockedView`/`TenantSessionRuntimeGate`を6-7, 24, 32行目で使用）。しかし`03_Implement/frontend/e2e/`配下62本のspecファイルを`TenantSession`、`tenant-session`、`activeTenant`、`runtime_activation`、大文字小文字を無視した`tenant`/`saas`で検索しても一致は0件だった。`ADR-0019`は「UIを伴う変更ではPlaywrightベースのE2E追加/更新を原則必須とする」と定めている。
- 利用者または開発への影響: `issue-SAAS-TENANT-01`自身のcheckpointが繰り返し認めている通り（「実ブラウザE2Eは未完了のため...AC-6/8/10/12とSaaS起動拒否を継続する」）、これは既知の未完了事項であり新規発見のバグではない。ただし、この棚卸しの時点で改めて確認し、独立したissueとして追跡できるようにする。

## 対応方針

- 実施すること: `issue-SAAS-TENANT-01`のAC-6/8/10/12が解消し、trusted auth edge・session persister・tenant switch POST/transition/hard replacementの実配線が完了した後に、tenant A/B間の越境防止を確認するE2Eシナリオ（例:「tenant Aからtenant Bへ切替後、tenant Aのcanvasが表示されない」）を追加する。
- 実施しないこと: 現時点でのE2E spec追加。`main.tsx`は`saas-multitenant`プロファイル以外ではSaaS経路を有効化せず、backend設定もSaaS起動を引き続き拒否しているため、今テストを書いても実際のuser journeyを検証できない。どのシナリオを最初に固定するかは、残りの配線が完了してから決めるMaintainer判断とする。

## 受入条件

- [ ] `issue-SAAS-TENANT-01`のAC-6/8/10/12解消後、少なくとも1本のtenant切替E2Eシナリオが追加される。
- [ ] 既存specの回帰がない。

## 検証計画

- 実行する確認: 配線完了後、`npx playwright test <対象spec>`。
- 期待結果: tenant切替後に他tenantの文書・状態が残存しないことを確認する。

## 補足

- 発見経緯: SaaSテナント対応マージ後の広範な棚卸し（第3ラウンド）で発見。`issue-SAAS-TENANT-01`自身が既に認識している既知のギャップを、独立issueとして明示的に追跡できる形にした。
