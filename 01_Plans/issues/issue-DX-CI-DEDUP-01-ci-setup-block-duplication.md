# Issue Draft: DX-CI-DEDUP-01 CIジョブ間で重複するsetup/base_commit解決ブロック

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `.github/workflows/ci.yml`
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

## Acceptance

- [ ] Node/PM検出＋installブロックが1箇所（composite actionまたは等価な仕組み）に集約されている。
- [ ] base_commit解決ロジックが1箇所に集約されているか、各箇所の重複が正当化されている。
- [ ] リファクタリング後もCIの実行結果（各ジョブの成否）が変わらないことを実際のPRで確認する。

## Validation

- リファクタリング後のPRで全CIジョブがpassすることを確認する。
