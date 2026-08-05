# Issue Draft: DX-CI-TEST-01 frontend unit suiteが `03_Implement/frontend` 外を参照する

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/domain/representative_visual_cue_prototype.test.ts`, `03_Implement/frontend/src/import/external_agent_workflow_doc.test.ts`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題

`representative_visual_cue_prototype.test.ts` と `external_agent_workflow_doc.test.ts` が、`03_Implement/frontend` の外（`02_Architecture/`、`04_Documentation/`）にあるファイルを相対パスで読み込んでいる。

本リポジトリの確立された検証手順は「WSL-native側へ `03_Implement/frontend` のみをrsyncしてvitestを実行する」（DrvFsがnode_modulesを壊すため）。この手順では上記2ファイルが対象パスを解決できず、`ENOENT`で失敗する。フルリポジトリのcheckout（CI環境）では問題なく通るため、CI自体は壊れていない。

SAAS-TENANT-01のフロントエンド側監査（2026-08-06）で、変更が無関係であることを証明するために比較実行が必要になり、この非隔離性が発覚した。

## 論点（人的判断が必要な理由）

- 対象2ファイルが親ディレクトリを参照する意図（fixtureをリポジトリの正本から直接読むことで二重管理を避けている）は理解できるが、これは「frontendディレクトリだけの独立したcheckoutでは緑にならない」という代償を払っている。
- 対応案は複数ある: (a) 該当fixtureを`03_Implement/frontend`内へ複製し同期をテストで検証する、(b) テストをリポジトリルート基準の絶対パス解決に変え、CI/ローカル双方で動くようにする、(c) 現状を許容し、WSL-native検証時は該当2ファイルを除外する運用を明文化する。
- どれを選ぶかはfixture管理方針の判断であり、機械的な修正ではない。

## 影響

低リスク。CI自体は壊れていないため実害はないが、frontend単体の検証環境（本リポジトリの標準的な検証手順）が常にこの2ファイルの失敗を含み、実際の回帰との区別に注意力を要する。

## Acceptance

- [ ] 上記(a)/(b)/(c)のいずれかを選択し適用する。
- [ ] `03_Implement/frontend`のみをWSL-native側へrsyncしたvitest実行が、全ファイルgreenになるか、除外方針が明文化される。

## Validation

- WSL-native `~/kjnative-fe`等へ`03_Implement/frontend/src`のみをrsyncし、`npx vitest run`が対象2ファイルを含めて成功することを確認する。
