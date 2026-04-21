# リリース手順（最小）

> Audience: メンテナ・リリース担当者
> Purpose: 監査可能な最小リリース手順を提供する。
> This document decides: SemVer、リリース前チェック、タグ作成、タグ後確認、公開記録。
> This document does not decide: 組織内部の承認会議ログ、秘密鍵詳細運用、未公開インシデント対応。
> Related: `01_Plans/documentation_quality.md`, `.github/workflows/release.yml`, `04_Documentation/local_llm_ops_guide.md`

## 1. SemVer 方針

バージョンは `MAJOR.MINOR.PATCH` を使用します。

- MAJOR: 互換性を壊す変更
- MINOR: 後方互換な機能追加
- PATCH: 後方互換な修正（不具合・文書）

## 2. リリース前チェック（監査可能性の最小要件）

前提条件:

- 実行環境に Python / Node.js / npm が存在する。
- `03_Implement/backend` と `03_Implement/frontend` の依存解決が済んでいる。

必須チェック:

1. Backend テストが成功。
2. Frontend テストが成功。
3. Frontend ビルドが成功。
4. 公開文書が `01_Plans/documentation_quality.md` の Mandatory（QG-1〜QG-6）を満たす。
5. strict mode例外運用を含む変更では、D1〜D4 と役割語彙が関連文書間で一致。

実行例:

```bash
# backend
cd 03_Implement/backend
python -m pytest

# frontend
cd ../frontend
npm test
npm run build
```

失敗時対応:

- テスト失敗時は、失敗コマンド・失敗ログ要点・再現手順を記録してから修正する。
- 前提未充足で実行できない場合は、未実施理由をリリース記録へ残す。

## 3. バージョン更新

1. `CHANGELOG.md` の `## [Unreleased]` に変更点を追加。
2. リリース時に対象変更を新バージョン見出しへ移動。
3. 比較リンクを使う運用ならリンク定義も更新。

## 4. タグ作成（例: v0.1.1）

```bash
git checkout main
git pull

git add CHANGELOG.md 04_Documentation/release.md
git commit -m "docs: prepare release v0.1.1"

git tag -a v0.1.1 -m "Release v0.1.1"
git push origin main
git push origin v0.1.1
```

## 5. タグ後確認（GitHub Actions）

`vX.Y.Z` タグ push 後、GitHub Actions の Releaseジョブを確認します。

- Backend Docker build（no push）が成功。
- Frontend dist build + artifact が成功。
- `frontend-dist-vX.Y.Z` artifact が生成。

## 6. リリースノートと公開記録

- GitHub Release本文は `CHANGELOG.md` の対象節を基に作成。
- 区分は `Added / Changed / Fixed` を基本とする。
- 公開判定（Go/No-Go）と未実施項目は、PR本文またはリリースノートに記録する。

## 7. Go/No-Go gate（公開判定）

Go 条件:

1. 本文に Audience / decides / does not decide がある。
2. リリース前チェック結果を追跡できる。
3. 実行できなかったチェックは理由が記録される。

No-Go 条件:

- テスト未実施かつ理由記録なし。
- 監査導線（CHANGELOG、タグ、リリースノート）が欠落。
- SafeMode/strict mode関連の整合未確認。

## 8. Verify

```bash
rg -n "Audience|This document decides|This document does not decide|SemVer|Go/No-Go|CHANGELOG|tag|Release" 04_Documentation/release.md
git diff --check
```

## 9. 実行フェーズ固定（Read → Plan → Execute → Verify → Proceed）

リリース作業は次の順序を固定し、順序入れ替えや省略を行わない。

1. **Read**: 本書、`CHANGELOG.md`、関連runbook（`operations.md`）を再読し、今回の対象範囲を明確化する。
2. **Plan**: リリース対象、実施コマンド、Go/No-Go判定観点、未実施時の記録先を先に固定する。
3. **Execute**: 前節の手順（テスト・ビルド・タグ作成）を実行し、実行ログを残す。
4. **Verify**: 本節の `rg` / `git diff --check` を含めて整合確認する。
5. **Proceed**: 判定（Go / No-Go）と未解決項目を記録し、次アクションへ進む。

フェイルセーフ:

- Verify で不整合が出た場合の自己修復は **最大3回** まで。
- 3回で収束しない場合は `StoppedForClarification` として停止し、判断要求を記録する。
