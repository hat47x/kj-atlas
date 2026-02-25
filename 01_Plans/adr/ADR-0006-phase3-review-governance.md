# ADR-0006-phase3-review-governance: Phase 3: レビュー・統治

- Status: Accepted
- Date: 2026-02-24
- Deciders: Project Maintainers
- Scope: `01_Plans/`
- Migrated-from: `01_Plans/phase3_review_governance.md`

## Context

`phase3_review_governance.md` で管理していた計画・要件・受入条件を、ADR運用へ移管する。

## Decision

以下を本ADRの正本として採用する。

# Phase 3: Review Governance (Plan)

本フェーズは MVP 後の拡張であり、レビュー運用（責任所在・共有・監査）を整える。  
実装は段階的に進める。セキュリティ/プライバシを優先する。

## Progress update（2026-02-23 確認）

- Overall: **In Progress（部分着手）**
- 判定方針: 03_Implement の実装有無とテスト有無を基準に判定。

| Milestone | Status | 根拠 |
|---|---|---|
| M1: Current reviewer (local) | ⏳ Not started | `reviewerRef` / `Current reviewer` の実装痕跡は未確認。 |
| M2: ReviewEvent append on review toggle | ⏳ Not started | `reviewEvents` データモデル/保存/export-import経路は未確認。 |
| M3: Export redaction | ⏳ Not started | review向け redaction モード（strip-identities / strip-all）は未確認。 |
| M4: Merge audit log integration | 🟡 Partial | `mergeAuditLog` の保存・上限管理は実装済みだが、`reviewEvents` との統合は未実装。 |
| M5: Org deployment hooks (optional) | ⏳ Not started | reviewerRef adapter / SSO subject 連携は未確認。 |
| M6: Optional signing (non-MVP) | ⏳ Not started | detached signature 設計・検証UIは未確認。 |

> 注記: M4 の「部分着手」は `mergeAuditLog` 単体の実装確認に基づく。Phase 3 の DoD 充足には `reviewEvents` 実装と export/import 連携が必要。

## Objectives
- “人間がレビューしたか”を確実に区別できる
- 誰がレビューしたかはオプトイン（匿名ID既定）
- 成果物エクスポート時に適切に削除できる
- 多環境（ローカル/イントラ/自前ホスト）で成立する

## Milestones

### M1: Current reviewer (local)
- [ ] ローカル環境で reviewerRef を生成・保持（localStorage等）
- [ ] UIで “Current reviewer” を設定可能（displayNameは既定OFF）
- Done criteria:
  - 設定した reviewerRef が再起動後も維持される

### M2: ReviewEvent append on review toggle
- [ ] island/card/summary の reviewed を切り替える操作時に ReviewEvent を追記
- [ ] reviewerRef（あれば）と createdAt を記録
- Done criteria:
  - reviewEvents が view.json export/import で保持される

### M3: Export redaction
- [ ] view.json export に redaction モードを実装
- [ ] review pack / bundle export で既定 strip-identities
- Done criteria:
  - 公開用に strip-all を選ぶとレビュー履歴が消える

### M4: Merge audit log integration
- [ ] I29 の mergeAuditLog と reviewEvents の整合（同居・保持上限）
- Done criteria:
  - レビュー運用ログが肥大化しない

### M5: Org deployment hooks (optional)
- [ ] reviewerRef 生成規約の差し替え（adapter interface）
- [ ] SSO subject を reviewerRef にできる
- Done criteria:
  - 認証があっても無くても動く

### M6: Optional signing (non-MVP)
- [ ] detached signature を設計（ファイル単位署名）
- [ ] 署名検証UI（任意）
- Done criteria:
  - 署名が無い場合も通常利用を阻害しない

## Risk notes
- doxxing/個人情報流出は最大リスク。storePII=false を既定にする。
- 改ざん可能性は残るため、“監査証跡”用途は署名まで到達してから。


## Consequences

- 旧文書 `phase3_review_governance.md` は廃止し、本ADRへ参照を統一する。
- 既存リンクは `01_Plans/adr/ADR-0006-phase3-review-governance.md` へ更新する。

## Traceability

- Source: `01_Plans/phase3_review_governance.md`
- Supersedes: `01_Plans/phase3_review_governance.md`
