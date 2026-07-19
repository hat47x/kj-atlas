# Issue: DX-CI-TIMEOUT-01 全CIジョブにtimeout-minutesが未設定

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Process
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `.github/workflows/ci.yml`, `.github/workflows/release.yml`, `01_Plans/docs_contract_checks.py`, `01_Plans/docs_check.py`, `01_Plans/tests/test_docs_contract_checks.py`, `01_Plans/tests/test_docs_check.py`
- Related ADR/Spec: N/A
- Expected verification level: `docs-check`

## 課題

- 現在の問題: `.github/workflows/ci.yml`（現行9ジョブ）と`.github/workflows/release.yml`（2ジョブ）のいずれのジョブにも`timeout-minutes`が設定されていなかった。GitHub Actionsの既定上限360分により、ハング時に長時間CI資源を消費する可能性がある。
- 利用者または開発への影響: 実害が顕在化したことはまだ無いが、CI時間の浪費、および他のPRのCIキューを塞ぐリスクがある。

## 対応方針

- 実施したこと: GitHub Actions APIで直近5回の成功CI run（`29686502789`〜`29691588686`）を確認し、観測最長99秒に対して約18倍の余裕を持つ一律30分を全11ジョブへ設定した。さらに`DC-CI-001`で新規ジョブの設定漏れと1〜360分外の値を検出する。
- 実施しないこと: step単位のtimeout、再試行回数、CIの実行条件、release処理内容の変更。

## 受入条件

- [x] 全11ジョブに`timeout-minutes: 30`を設定する。
- [x] 直近成功CIの最大99秒を十分に上回ることを確認する。

## 検証計画

- 実行する確認: 設定後、実際にPRを作成してCIを実行し、全ジョブが設定したタイムアウト内に正常完了することを確認する。
- 期待結果: 通常のCI実行がタイムアウトで打ち切られない。

## Validation

- `python -m unittest discover -s 01_Plans/tests -p "test_*.py"`
- `python 01_Plans/docs_check.py --root .`
- GitHub Actions APIによる直近5成功runのjob実績確認（最大99秒）

## 補足

- 発見経緯: 第11ラウンドの棚卸し（CIワークフロー設定観点）で発見。同じ観点で見つかったフロントエンドjobの`cache-dependency-path`ハードコード問題（`package-lock.json`固定、pnpm/yarnへの切替時にキャッシュが不整合になる）は、既存の「Detect package manager」ステップのパターンをそのまま拡張するだけの機械的な修正だったため、本ラウンドで直接修正済み。
