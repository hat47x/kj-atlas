# Issue: AI-MODEL-UX-01 利用可能modelが空の理由を利用者画面で判別できない

- Type: UX / Operability
- Status: Open
- Source Issue: 管理UI・API・MCP協調モンキーテスト（2026-08-16）
- Priority: P2
- Owner: Maintainer
- Scope: `/ai/available-models`, frontend `ModelSelector`, admin model/provider status UI
- Related Issue: `AI-MODEL-GOVERNANCE-03`
- Related ADR/Spec: `ADR-0065`, `AI-MODEL-GOVERNANCE-01`, `02_Architecture/api.md` §2.11
- Expected verification level: `e2e`

## 課題

`/ai/available-models`は実効集合だけを返すため、空配列が「active modelなし」「tenant allowlistで全除外」「実行provider transport不一致」「provider設定不足」のどれによるものか利用者画面で判別できない。今回、空状態に管理設定・AI接続設定を確認する案内を追加したが、利用者は管理者へ伝えるべき原因や復旧操作を特定できない。

## 対応方針

- 秘密情報や他tenantのmodel名を漏らさない、列挙型の`unavailableReason`または集約診断をAPI契約へ追加する。
- 利用者画面は権限に応じて「管理者へ連絡」と「管理画面で確認」を出し分ける。
- 管理画面はprovider lifecycle、runtime transport、tenant allowlistの交差結果を、実行可否と同じresolverから説明表示する。
- API応答と表示文言は、model/providerの状態変更後にも同一session・tenant条件で整合させる。

## 受入条件

- [ ] 空集合の主要原因を、情報漏えいしない安定したreason codeで区別できる。
- [ ] 一般利用者には管理権限を前提としない次の行動が表示される。
- [ ] 管理者には原因に対応する設定箇所が表示される。
- [ ] provider不一致、allowlist空、active modelなしをAPI・Edge E2Eで固定する。

## 検出記録（2026-08-16）

Edge実画面でprovider `none`・利用可能model空を再現し、selectorのdisabled状態と汎用案内は確認できた。一方、現行APIには原因情報がなく、UIだけではこれ以上具体化できないため継続課題として起票した。
