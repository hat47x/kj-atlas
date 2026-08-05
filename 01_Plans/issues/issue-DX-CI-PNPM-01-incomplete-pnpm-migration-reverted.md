# Issue Draft: DX-CI-PNPM-01 未完了のpnpm移行をrevertした記録と再開時の論点

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `.github/workflows/ci.yml`, `03_Implement/frontend/pnpm-lock.yaml`（revert済み）, `03_Implement/frontend/pnpm-workspace.yaml`（revert済み）, `.nvmrc`
- Related ADR/Spec: N/A
- Expected verification level: `docs-check`

## 課題

コミット `94120c7c` で `03_Implement/frontend/pnpm-lock.yaml` と `pnpm-workspace.yaml` が追加され、`ci.yml` のパッケージマネージャ自動検出（`if [ -f pnpm-lock.yaml ]; then manager=pnpm...`）がpnpmモードへ切り替わった。これにより全フロントエンドCIジョブが即座に失敗（CI run `30375196882`、6ジョブ全て`Setup Node.js`ステップで`Unable to locate executable file: pnpm`）したため、両ファイルをrevertした（本Issueと同じ変更セットで）。

原因は独立した3点で、いずれも単純な機械的修正では済まない。

1. **`ci.yml`のステップ順序バグ**: `Enable corepack`（pnpmを利用可能にする）が`Setup Node.js`（`cache: pnpm`オプションが事前にPATH上のpnpmを要求する）より**後**に実行される。この順序は元から誤っていたが、リポジトリに`pnpm-lock.yaml`が存在しなかったため一度も顕在化していなかった。
2. **pnpmとNodeのバージョン非互換**: ローカルでDocker検証したところ、順序を直しても、corepackが解決する最新pnpm（11.17.0）は Node >=22.13 を要求する。本リポジトリの`.nvmrc`はNode 20を固定しており、`package.json`に`packageManager`フィールドによる互換pnpmバージョンの固定もないため、`ERR_UNKNOWN_BUILTIN_MODULE`（`node:sqlite`）でインストール開始前にクラッシュする。
3. **`pnpm-workspace.yaml`の内容が未完成のプレースホルダ**: `allowBuilds.esbuild: set this to true or false` — 実際のbooleanではなく、人間が埋めるべき指示文がそのまま入っている。

## 論点（人的判断が必要な理由）

pnpmへの移行を実際に完了させるかどうか、完了させる場合の対象pnpm/Nodeバージョン、`esbuild`のbuild-script承認方針（true/false）は、いずれも製品/インフラ判断であり、機械的に決められない。

- 移行を進める場合: (a) `ci.yml`のステップ順序修正、(b) `package.json`への`packageManager`フィールド追加によるpnpmバージョン固定（Node 20と互換のバージョン選定）、(c) `pnpm-workspace.yaml`の`allowBuilds.esbuild`に実際のbooleanを設定、(d) 移行後にnpmベースのlockfile/設定を整理、が必要。
- 移行を進めない場合: 両ファイルはrevert済みのまま維持する。

## 影響

revert前は全フロントエンドCIジョブが恒久的に失敗する状態にあった（このリポジトリで作業する全員に影響する共有状態の破損）。revertにより解消済み。
