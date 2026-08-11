# Issue: EXT-AGENT-AUDIT-01 外部取込proposal判断の由来を監査連鎖へ接続する

- Type: Architecture / Security / Data
- Status: Draft
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

- [ ] task exportからresponse import、proposal判断まで同一の相関chainを検証できる。
- [ ] document・tenant越境、stale base、taskId再利用、bundleHash不一致を拒否する。
- [ ] 署名なしclipboard応答の由来強度をUIと監査eventで過大表示しない。
- [ ] idempotentなadopt/rejectと、監査失敗時に適用済みと表示しない順序をtestする。
- [ ] CE2 endpointへ外部取込用の架空sourceBundleHashを送らない。
