# Issue: EXT-AGENT-AUDIT-01 外部取込proposal判断の由来を監査連鎖へ接続する

- Type: Architecture / Security / Data
- Status: In Progress
- Source Issue: EXT-AGENT-02
- Priority: P2
- Owner: Maintainer
- Scope: agent task export, `agent-response.v1`, response import review, proposal decision audit
- Related ADR/Spec: `ADR-0049`, `EXT-AGENT-01`, `EXT-AGENT-02`, `CE2-AUDIT-CONTRACT-01`
- Expected verification level: `integration`

## 課題

外部から貼り付けた`agent-response.v1`は`taskId`を持つが、元のexportで計算した`bundleHash`を応答契約に返さない。従来frontendはCE2用`/ai/proposals/audit`へactorとproposalIdだけを送り、由来を検証できないまま監査済みに見せていた。CE2監査を`tenant + document + proposal + sourceBundleHash`へ強化したため、この流用は廃止した。

## 対応方針

- export時の`taskId/baseDocSignature/bundleHash`相関情報を、取込時に検証可能な形で応答へechoする契約を決定する。
- clipboard貼付だけで真正性を主張しない。署名なし応答は「利用者が提示した外部成果物」として由来levelを明示する。
- adopt/rejectを記録する専用endpointまたは共通audit envelopeを設計し、CE2のsource hash欄へ捏造値を入れない。
- 判断記録が失敗した場合にDocument適用を成功扱いしない順序・補償契約を定義する。

## 受入条件

- [ ] task exportからresponse import、proposal判断まで同一の相関chainを検証できる。※ export→importのローカル検証まで完了。判断監査endpointは未実装。
- [ ] document・tenant越境、stale base、taskId再利用、bundleHash不一致を拒否する。※ tenant-scoped local ledger、document/stale/hash照合は完了。server側のtask消費記録は未実装。
- [ ] 署名なしclipboard応答の由来強度をUIと監査eventで過大表示しない。※ UI表示は完了。監査eventは未実装。
- [ ] idempotentなadopt/rejectと、監査失敗時に適用済みと表示しない順序をtestする。
- [x] CE2 endpointへ外部取込用の架空sourceBundleHashを送らない。

## 2026-08-11 実装チェックポイント

- export成功時に、完全相関をテナント・利用者スコープのブラウザ台帳へ最大100件保持する。
- responseは相関ブロック全体をechoする。取込時にtaskId、document、base signature、bundle/query hash、task kindを台帳と照合する。
- 旧responseはlenient modeだけで受け入れ、由来を`unverified-legacy`と表示する。strict modeでは完全相関を必須とする。
- 提案の画面内識別子を`taskId + proposalId`へ変更し、別タスク間のproposalId衝突を除去した。
- 残作業は、署名なしという由来強度を保持する外部提案専用のserver registry / decision eventと、監査成功後にだけ適用済みへ遷移させる順序制御である。
