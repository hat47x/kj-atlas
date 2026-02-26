# ADR-0018: シンプル・セキュア規約とバッドスメル是正方針

- Status: Accepted
- Date: 2026-02-25
- Deciders: Project Maintainers
- Scope: `03_Implement/frontend`, `03_Implement/backend`, `01_Plans/coding_standards.md`
- Derived-from: コードベース観測（2026-02-25）

## Context

コードベースの保守性・安全性を継続的に担保するため、再発しやすいバッドスメルを
「観測メモ」ではなく、意思決定（ADR）と運用規約へ昇格させる必要がある。

観測した主な課題:

1. Frontend で巨大ファイル化（例: `App.tsx`）が進み、責務境界が曖昧。
2. インラインスタイルや色コード重複が多く、UI変更時の一貫性が崩れやすい。
3. Backend で `except Exception` の広域捕捉が散見され、障害解析性が低い。
4. Frontend CI は型検査中心で、可読性・安全性ルールの自動検知が限定的。

## Decision

1. **バッドスメルの管理先を ADR + 規約へ一本化**する。
   - 観測事項は本ADRに記録し、実務ルールは `01_Plans/coding_standards.md` に集約する。
   - 規約文書からは「現在のコードの観測一覧」を削除し、ルール本文に集中させる。

2. **是正方針を以下に固定**する。
   - 巨大ファイル: 機能追加時に責務抽出（component/hook/util）を必須化。
   - スタイル重複: トークン/定数へ集約し、重複追加を禁止。
   - 広域例外: 期待例外型での狭い捕捉へ置換。
   - 静的検知: Frontend lint 強化（例: ESLint）を段階導入。

3. **PRレビューでの統制**を明文化する。
   - 規約チェックリストにより、複雑性・安全性・テスト有無を毎回確認する。

## Consequences

- ルールと背景の責務分離により、規約文書は短く運用可能になる。
- バッドスメルの再発時に「既知課題か」「新規課題か」をADR単位で追跡できる。
- 将来の規約改定時は、本ADRを起点に更新履歴を残せる。

## Follow-up Actions

- [x] Frontend lint 強化案（ESLint導入方針）を `ADR-0002-internal-roadmap.md` へ反映する。（2026-02-26 完了）
- [ ] `App.tsx` 分割の優先順（状態管理 / 描画 / import-export）を別ADRまたはIssueで計画化する。
- [ ] Backend の `except Exception` 使用箇所を段階的に解消する。

## Traceability

- Implements: `01_Plans/coding_standards.md`
- Related: `.github/workflows/ci.yml`, `CONTRIBUTING.md`
