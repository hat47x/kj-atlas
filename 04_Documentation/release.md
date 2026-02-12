# リリース手順（最小）

このドキュメントは、kj-atlas の最小リリース運用（バージョニング、タグ作成、リリースノート）を定義します。

## 1. バージョニング方針（SemVer）

バージョンは `MAJOR.MINOR.PATCH` 形式（例: `0.2.3`）を使います。

- `MAJOR`:
  - 互換性を壊す変更を含むとき
- `MINOR`:
  - 後方互換を保った機能追加
- `PATCH`:
  - 後方互換を保ったバグ修正・文言修正

## 2. リリース前チェック

タグ作成前に、最低限次のチェックを通してください。

- Backend テストが成功すること
- Frontend テストが成功すること
- Frontend ビルドが成功すること

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

> CI を利用している場合は、上記に相当するチェックが green であることを確認してください。
> 本リポジトリではタグ push 後に `.github/workflows/release.yml` が実行され、backend Docker build（no push）と frontend dist artifact 作成が走ります。

## 3. バージョン更新（手動）

1. `CHANGELOG.md` の `## [Unreleased]` に変更点を追記する
2. リリース時に `Unreleased` の内容を新しいバージョン見出しへ移動する
   - 例: `## [0.1.1] - 2026-02-13`
3. 必要に応じて、比較リンクを使う運用ならリンク定義も更新する

## 4. タグ作成手順（vX.Y.Z）

例として `0.1.1` をリリースする場合:

```bash
git checkout main
git pull

# 必要ならリリース準備コミットを作成
git add CHANGELOG.md 04_Documentation/release.md
git commit -m "docs: prepare release v0.1.1"

git tag -a v0.1.1 -m "Release v0.1.1"
git push origin main
git push origin v0.1.1
```

## 5. リリースノートの作り方

- GitHub Release の本文は `CHANGELOG.md` の対象バージョン節をそのまま転記します。
- 基本は次の3区分で十分です。
  - `Added`
  - `Changed`
  - `Fixed`

## 6. 運用ルール（最小）

- 自動 publish（レジストリへの配布）は行わない
- まずは「タグを切れること」「変更履歴を追えること」を優先する
- 運用が固まるまで手順はシンプルに保つ


## 7. タグ後の確認（GitHub Actions）

`vX.Y.Z` タグを push したら、GitHub Actions の **Release Build** を確認します。

- `Backend Docker build (no push)` が成功していること
- `Frontend dist build + artifact` が成功していること
- Artifacts に `frontend-dist-vX.Y.Z` が生成されていること
