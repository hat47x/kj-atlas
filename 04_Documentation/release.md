# リリース手順（最小）

> DOC-OPS-05 Classification: **Improve external**
> Audience: メンテナ・リリース担当者
> Goal: 最小リリース手順を公開し再現可能性を担保する。
> Non-goal: 組織内部の承認会議ログ・秘密鍵運用手順・未公開インシデント情報は扱わない。
> Public boundary: 内部承認履歴は除外し、公開可能な手順とチェックのみを残す。
> Next action: DOC-OPS-05 issueの分類固定に従い、Move internal は移設PR、Improve external は公開品質改善PRを後続で実施。
> Outcome: 外部読者が最小リリース手順と公開チェックを単独で追従できる。
> Related: `01_Plans/documentation_quality.md`, `.github/workflows/release.yml`, `01_Plans/issues/issue-doc-ops-05-12-04doc-release.md`

このドキュメントは、kj-atlas の最小リリース運用（バージョニング、タグ作成、リリースノート）を定義します。

## 1. バージョニング方針（SemVer）

バージョンは `MAJOR.MINOR.PATCH` 形式（例: `0.2.3`）を使います。

- `MAJOR`:
  - 互換性を壊す変更を含むとき
- `MINOR`:
  - 後方互換を保った機能追加
- `PATCH`:
  - 後方互換を保ったバグ修正・文言修正

## 1.5 公開ドキュメントの位置づけ（04_Documentation / Gist）

`04_Documentation/` は、対外的なユーザ/開発者向けの公開技術文書として Gist にリリースできる前提で扱います。

- 内部計画メモや未承認方針は `04_Documentation/` の既定読者に含めません。
- Gistへ公開する文書は、内部基準 `01_Plans/documentation_quality.md` の Mandatory（QG-1〜QG-6）を満たしてから出します。
- 04の文書は「公開運用文書」であり、設計の正本を書き換える場所ではありません。必要な設計根拠は `01_Plans/` / `02_Architecture/` を参照します。

## 2. リリース前チェック

タグ作成前に、最低限次のチェックを通してください。

- Backend テストが成功すること
- Frontend テストが成功すること
- Frontend ビルドが成功すること
- Gist公開対象の `04_Documentation/*.md` が `01_Plans/documentation_quality.md` の Mandatory（QG-1〜QG-6）を満たすこと

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

## 8. main ブランチの Required checks 設定（回帰防止）

`FB-RM-SEC-03` の運用として、GitHub の Branch protection rules で以下を **Required** に設定します。

- `Frontend regression guards (import/serialization/shape)`
- `Frontend lint + test`
- `Backend lint + test`

設定手順（GitHub UI）:

1. `Settings` → `Branches` → `Branch protection rules`
2. `main` 向けルールを作成/編集
3. `Require status checks to pass before merging` を有効化
4. 上記3ジョブ名を Required checks に追加して保存

> ジョブ名を変更した場合、Required checks の設定も更新が必要です。

## 9. Publishing metadata リリース注意（FB-RM-PUB-01）

- `view.json` / `packs/index.json` の `visibility` は `Public | Unlisted | Org | Restricted` のみを許容します。
- 互換読込では欠損値を次の既定値で補完します。
  - `view.json`: `Restricted`
  - `packs/index.json` の各 pack entry: `Public`
- enum 外値（例: `FriendsOnly`）は互換対象にせず、validator が拒否することをリリース前テストで確認してください。
- `visibility` は公開範囲のメタデータであり、権限制御の切替スイッチではありません。SafeMode 既定ON / read-only 公開 / share-export 制御は従来通り優先されます。
- 運用責務の境界:
  - 製品側: metadata 正規化・検証（import/export/validate）と既定値補完。
  - 運用側: `visibility` の意味づけ（公開ポリシー）を組織ルールへマッピングし、配布先アクセス制御（CDN/SSO/ネットワーク境界）を別途担保。

## 10. 04_Documentation の Gist 公開チェック

`04_Documentation/` を Gist へ切り出して公開する場合、タグリリースとは別に次を確認します。

1. 公開対象ファイルを確定する。
2. `01_Plans/documentation_quality.md` の Mandatory（QG-1〜QG-6）を確認する。
3. Markdown preview で表示崩れを確認する。
4. 外部読者が読んでも成立するよう、Audience / Goal / Non-goal / Outcome が読めることを確認する。
5. コマンド例がある場合は、前提条件・実行場所・期待結果が記載されていることを確認する。
6. 公開判定の記録を PR本文、release note、または同等の監査可能な場所に残す。

> QG未充足の文書は、Gist公開を見送り、修正後に再判定してください。


## DOC-OPS-05 セット1 実行記録（Phase 1〜6）

### AC（Acceptance Criteria）

- AC-1: 対外公開可能なリリース手順として Classification（Improve external）が明示される。
- AC-2: SemVer・事前チェック・タグ作成・タグ後確認の流れが維持される。
- AC-3: 内部基準参照（documentation_quality）と公開手順の境界が明確である。
- AC-4: 変更は Docs only とし、CI設定や実装フローを変更しない。

### DoD（Definition of Done）

- DoD-1: Phase 1〜6 が文書内に記録され、再実行可能な状態。
- DoD-2: docs-check コマンドが定義され、差分検証可能。
- DoD-3: Proceed判定（Ready/Hold/Needs-decision）が明記される。

### Phase 1 Read

- リリース前後チェック、CI導線、公開境界を確認。

### Phase 2 Plan

- 方針: 最小再現可能手順を維持し、内部承認フロー詳細は持ち込まない。

### Phase 3 Execute

- AC/DoD とPhase記録を追加し、運用判定を固定。

### Phase 4 Verify

- 推奨コマンド:
  - `rg -n "DOC-OPS-05 セット1|AC（Acceptance Criteria）|DoD（Definition of Done）" 04_Documentation/release.md`
  - `git diff --check`

### Phase 5 Proceed 判定

- 状態: **Ready**（公開リリースガイドとして継続改善可能）。

### Phase 6 Proceed（引き継ぎ）

- 次アクション: リリース自動化範囲を拡張する場合は `.github/workflows/release.yml` と同時整合で更新。
