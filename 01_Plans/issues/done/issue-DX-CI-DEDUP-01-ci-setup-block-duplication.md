# Issue: DX-CI-DEDUP-01 CIジョブ間で重複するsetup/base_commit解決ブロック

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `.github/workflows/ci.yml`, `.github/actions/setup-frontend/action.yml`
- Related ADR/Spec: N/A
- Expected verification level: `docs-check`

## 課題

`ci.yml` 内に、機械的に同一のブロックが複数ジョブへ重複している。

**Node/パッケージマネージャ検出＋install（57行、完全一致）**

`frontend-typecheck` と `frontend-test` の両ジョブが、"Detect Node version" → "Detect package manager"（npm/pnpm/yarn判定） → "Setup Node.js" → "Enable corepack" → "Install dependencies"（3回リトライ）を一字一句同一に持つ。`diff` で確認済み、差分ゼロ。`release.yml` は判定なしの `npm ci` のみで、実際に使われているパッケージマネージャは npm 単独（`03_Implement/frontend` に `package-lock.json` のみ存在。`pnpm-lock.yaml`/`yarn.lock` は過去に導入を試みて `c34a7ae1` で取り消し済み、`issue-DX-CI-PNPM-01` が現在も未解消のまま残る）。

**base_commit解決ブロック（2種類、最大3変種）**

`change-scope` ジョブと `backend` ジョブの "Detect auth boundary changes" ステップが、"diffのベースコミットを何にするか"（pull_request時はmerge-base、push時はgithub.event.before、フォールバックはリポジトリ初回コミット）を独立に再計算しており、11行が完全一致。`docs-contract` ジョブの whitespace-check ステップにも同種の14行（elif分岐が1つ多い変種）がある。`change-scope` は既にこの値を算出しjob outputとして公開しているため、他の2箇所は論理的に一度で済む値を再導出している。

## 論点（人的判断が必要な理由）

- Node/PM検出ブロックの切り出し先（`.github/actions/setup-frontend/action.yml` のようなcomposite action）を作る場合、GitHub Actions のcomposite action入出力配線を新規に設計する必要があり、CI自体を変更するため、変更後に実際にCIを走らせて壊れていないことを確認する一手間がある。
- base_commit解決を`change-scope`のjob outputへ統合する場合、`backend`・`docs-contract`ジョブの`needs`グラフに`change-scope`を追加する必要があり、ジョブの依存構造が変わる。
- 費用対効果として、CI設定のリファクタリングは「無駄な儀礼の削除」より一段リスクが高く、専用のPRで検証しながら進める方が安全と判断し、今回の一括削減パスでは実施を見送った。

## 影響

現状はCI実行に問題を起こしていない（重複が動作を壊しているわけではない）。整理すれば `.github/workflows/ci.yml` の行数削減と、setup手順を変更する際の同期漏れリスクの低減が見込める。

**状態追記（2026-08-07）**: `mcp` ジョブが追加され（`6f13f62d`）、`actions/setup-node` を直接使うため、frontendの `setup-frontend` composite action と並ぶNodeセットアップの別系統が生まれた。base_commit解決は `ci.yml:68` のNOTEどおり change-scope と docs-contract で意図的に別挙動（`github.event.before` vs 再解決）のため、無条件の統合はできない。統合する場合は、各ジョブの base_commit 仕様の一致を確認してから行う。

## Acceptance

- [x] Node/PM検出＋installブロックが1箇所（composite actionまたは等価な仕組み）に集約されている。
- [x] base_commit解決ロジックが1箇所に集約されているか、各箇所の重複が正当化されている。
- [x] リファクタリング後もCIの実行結果（各ジョブの成否）が変わらないことを実際のPRで確認する。

## Validation

- リファクタリング後のPRで全CIジョブがpassすることを確認する。

## 対応記録（2026-09-05）

本Issueの実装は PR #2727 `ci: 重複setupを共通化しCI差異を最小化` で 2026-08-06 に既に完了していたが、Issueメモ側の状態更新が追随していなかったため、現行履歴からAcceptanceを再検証してDoneへ正規化した。

- frontendの重複setupは `.github/actions/setup-frontend/action.yml` へ集約され、`frontend-test` と `frontend-typecheck` が同一composite actionを利用する形へ変更された。
- backend側のbase_commit再導出は削除され、`change-scope` が算出した値を利用する形へ整理された。
- docs-contract側のbase_commit解決は、独立実行時の仕様差があるため統合せず、意図的な別契約として残す判断がPR内で明記された。したがってAcceptance第2項の「各箇所の重複が正当化されている」を満たす。
- PR #2727 のhead commit `f3ec8ce6c054a2f9796e0f40944a79bd67a09cbf` に対する GitHub Actions `CI` Run `31062823717` は `success`。`Frontend test + build` と `Frontend typecheck` の双方で `Setup frontend toolchain` が成功し、backend・docs-contract・change-scopeを含む同runの各ジョブも成功した。これをAcceptance第3項の実CI証拠とする。

その後、常設GitHub Actions workflow自体は別の運用判断で意図的に無効化・削除され、`DOC-CI-DRIFT-01` で現行文書／検査もworkflow不在の構成へ同期された。本Issueの完了は、その後のworkflow無効化を取り消したり、`.github/workflows/ci.yml` の復活を要求するものではない。ここでは #2727 実施時点のCI契約に対して重複整理が完了し、実CIで成立したという履歴証拠を保存する。

## 配置の整理（2026-09-05）

- 本Issueは実装・実CI検証とも完了済みであり、active rootに残すべき未解決作業はない。
- 既存のIssueライフサイクル契約に従い、`01_Plans/issues/` から `01_Plans/issues/done/` へ移動する。
