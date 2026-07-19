# Issue: DX-CI-TIMEOUT-01 全CIジョブにtimeout-minutesが未設定

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `.github/workflows/ci.yml`, `.github/workflows/release.yml`
- Related ADR/Spec: N/A
- Expected verification level: `docs-check`

## 課題

- 現在の問題: `.github/workflows/ci.yml`（11ジョブ）と`.github/workflows/release.yml`（2ジョブ）のいずれのジョブにも`timeout-minutes`が設定されていない（`grep -n "timeout-minutes"`で両ファイルとも0件）。GitHub Actionsのデフォルトのジョブタイムアウトは360分（6時間）で、ハングしたステップ（`pip install`/`npm ci`のネットワーク停滞、テストのフリーズ、Dockerビルドの詰まり等）が発生した場合、ジョブあたり最大6時間CI時間を消費し続ける可能性がある。
- 利用者または開発への影響: 実害が顕在化したことはまだ無いが、CI時間の浪費、および他のPRのCIキューを塞ぐリスクがある。

## 対応方針

- 実施すること: ジョブごとに適切な`timeout-minutes`値（例: lint/typecheckは10分、backend/Postgresを使うジョブは20-30分等）をMaintainerが決定する。
- 実施しないこと: 具体的な数値の設定そのもの。両ファイルとも既存の`timeout-minutes`設定例が一切無く、コピー元となる社内標準値が存在しないため、各ジョブの実行時間実態を踏まえた判断が必要。

## 受入条件

- [ ] 各ジョブに妥当な`timeout-minutes`が設定される。
- [ ] 設定後、既存のCI実行時間の実績値を超えない範囲であることを確認する（誤って正常なジョブを打ち切らないため）。

## 検証計画

- 実行する確認: 設定後、実際にPRを作成してCIを実行し、全ジョブが設定したタイムアウト内に正常完了することを確認する。
- 期待結果: 通常のCI実行がタイムアウトで打ち切られない。

## 補足

- 発見経緯: 第11ラウンドの棚卸し（CIワークフロー設定観点）で発見。同じ観点で見つかったフロントエンドjobの`cache-dependency-path`ハードコード問題（`package-lock.json`固定、pnpm/yarnへの切替時にキャッシュが不整合になる）は、既存の「Detect package manager」ステップのパターンをそのまま拡張するだけの機械的な修正だったため、本ラウンドで直接修正済み。
