# Phase 3: Review Governance (Plan)

本フェーズは MVP 後の拡張であり、レビュー運用（責任所在・共有・監査）を整える。  
実装は段階的に進める。セキュリティ/プライバシを優先する。

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
