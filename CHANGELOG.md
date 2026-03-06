# Changelog

このファイルは kj-atlas の変更履歴を記録します。

フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) を参考にし、
バージョンは [Semantic Versioning](https://semver.org/lang/ja/)（SemVer）に従います。

## [Unreleased]

### Added
- （未記入）

### Changed
- 環境変数契約を `KJ_ATLAS_*` 専用へ統一し、旧キー（`DATABASE_URL` 等）の受理を停止。

### Fixed
- strict mode例外Runbook（AUTH-OPS-03）のQ1〜Q10を確定し、停止条件/復旧条件の文書整合を修正。

## [0.1.0] - 2026-02-12

### Added
- リリース運用の最小ドキュメントを追加（`CHANGELOG.md`, `04_Documentation/release.md`）。
