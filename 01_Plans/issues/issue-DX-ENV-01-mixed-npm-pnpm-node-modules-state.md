# Issue Draft: DX-ENV-01 frontend node_modules がnpm/pnpm混在状態でesbuildが再発する

- Type: Process / Tooling
- Status: Draft
- Source Issue: `01_Plans/issues/issue-DX-CI-PNPM-01-incomplete-pnpm-migration-reverted.md`
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/node_modules/`, `03_Implement/frontend/package.json`, `03_Implement/frontend/vite.config.ts`
- Related ADR/Spec: `01_Plans/issues/issue-DX-CI-PNPM-01-incomplete-pnpm-migration-reverted.md`
- Expected verification level: `docs-check`

## 課題

`node_modules/` が npm と pnpm の**混在状態**にあり、ローカル開発で esbuild のバージョン不整合が繰り返し発生する。

- `node_modules/.pnpm/`（74エントリ）と `.modules.yaml`（pnpmマーカー）が、npmでインストールされた依存と共存している。
- pnpm移行がrevert（`DX-CI-PNPM-01`）された後に `.pnpm/esbuild@0.28.1` が残り、アクティブな `esbuild@0.21.5`（vite 5が要求）と混在して `vitest run` が `Cannot start service: Host version "0.28.1" does not match binary version "0.21.5"` で起動不能になる。
- 2026-08-02〜08-07の間に **3回** 発生し、毎回 `rm -rf node_modules/.pnpm/esbuild@0.28.1 node_modules/.pnpm/@esbuild+win32-x64@0.28.1` で復旧した。pnpm関連操作や依存再インストールが走ると再発する。
- **ビルドも壊れる（2026-08-07確認）**: stale `.pnpm/rollup@4.62.3`（rootの正しいrollupは4.57.1）がviteのrollupプラグインに解決され、`vite build` が `Source phase import "vite/modulepreload-polyfill" in "index.html" must be external` で失敗する。`rm -rf node_modules/.pnpm/rollup@4.62.3 ...` で解消し、build成功（28s）。
- CIは影響を受けない（`ci.yml`はnpmモードで動き、`include: ["src/**/*.test.ts"]` でe2eを除外しているため）が、ローカル開発・ビルドの両方が被る。

## 対応方針（案）

- (a) `node_modules` をクリーンに再構築する（`rm -rf node_modules` + 再インストール）。混在が解消し、`esbuild@0.28.1` の再出現が止まる。ただし再インストールに時間がかかる。
- (b) pnpm移行を正式に完了するか、完全に捨てるかを `DX-CI-PNPM-01` で決定してから、node_modulesを整理する。混在の根本原因は「revertしたのに `.pnpm/` が残った」こと。
- (c) 暫定回避として、`.pnpm/esbuild@0.28.1` の再発を防止するスクリプトまたはCIチェックを追加する。

## 受入条件

- [ ] `node_modules` が単一のパッケージマネージャ状態になる（`.pnpm/` と `.modules.yaml` が消える、または pnpm を正式採用）。
- [ ] `vitest run` が esbuild version mismatch なしで起動する。
- [ ] `cd 03_Implement/frontend && npx vitest run` が全テスト通る。

## 検証計画

- `ls 03_Implement/frontend/node_modules/.modules.yaml`（存在しないことを確認）
- `cd 03_Implement/frontend && npx vitest run`
- `python 01_Plans/docs_check.py`
