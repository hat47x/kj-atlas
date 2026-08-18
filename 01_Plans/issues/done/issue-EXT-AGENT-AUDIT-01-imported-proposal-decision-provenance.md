# Issue: EXT-AGENT-AUDIT-01 外部取込proposal判断の由来を監査連鎖へ接続する

- Type: Architecture / Security / Data
- Status: Done
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

- [x] task exportからresponse import、proposal判断まで同一の相関chainを検証できる。
- [x] document・tenant越境、stale base、taskId再利用、bundleHash不一致を拒否する。
- [x] 署名なしclipboard応答の由来強度をUIと監査eventで過大表示しない。
- [x] idempotentなadopt/rejectと、監査失敗時に適用済みと表示しない順序をtestする。
- [x] CE2 endpointへ外部取込用の架空sourceBundleHashを送らない。

## 2026-08-11 実装チェックポイント

- export成功時に、完全相関をテナント・利用者スコープのブラウザ台帳へ最大100件保持する。
- responseは相関ブロック全体をechoする。取込時にtaskId、document、base signature、bundle/query hash、task kindを台帳と照合する。
- 旧responseはlenient modeだけで受け入れ、由来を`unverified-legacy`と表示する。strict modeでは完全相関を必須とする。
- 提案の画面内識別子を`taskId + proposalId`へ変更し、別タスク間のproposalId衝突を除去した。
- server側へcontent-freeな`external_agent_tasks`台帳を追加し、taskIdをテナント内一意として相関全体を固定する。出力は登録失敗時にfail-closedとする。
- 外部提案は正規化後の内容指紋だけを共通proposal台帳へ登録し、本文・根拠は保存しない。由来は`external_agent / user_presented_unsigned`として判断eventにも固定する。
- 採用・破棄は外部専用endpointへ冪等記録してからUI状態またはDocumentを変更する。監査失敗時は未適用のまま維持する。
- 旧responseは表示のみ可能とし、完全相関がないため採用・破棄操作を無効化する。
