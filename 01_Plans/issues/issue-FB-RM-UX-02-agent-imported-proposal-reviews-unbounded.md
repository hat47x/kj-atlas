# Issue: FB-RM-UX-02 エージェント取込レビュー一覧が無制限に蓄積

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/ui/AgentResponseImportPanel.tsx`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題

- 現在の問題: `App.tsx:1160`の`agentImportedProposalReviews`（`useState<ImportedProposalReview[]>([])`）は、`handleParseAgentResponse`（`App.tsx:8654`）が外部エージェントの`agent-response.v1`をペースト・解析するたびに`setAgentImportedProposalReviews((previous) => [...previous, ...newReviews])`で末尾追加される。同一パース内では`proposalId`で重複排除されるが、パースを繰り返すたびに既存エントリ（`adopted`/`rejected`済みも含む）が消えることはなく、`setAgentImportedProposalReviews([])`のようなリセットもファイル内に一切存在しない。`AgentResponseImportPanel.tsx:198-200`はこの配列全体を無条件に`.map()`描画するため、DOMノード数もJSヒープと同様に増え続ける。パネルを閉じる操作（`onClose`）も一覧を消去しない。
- 判断が必要な理由: 各エントリは`status: "pending" | "adopted" | "rejected"`を持ち、`pending`はユーザーが未処理のレビュー対象である。単純に「最新N件だけ残す」という既存の`HISTORY_LIMIT`型のトリムを機械的に適用すると、まだ未対応の`pending`レビューを誤って切り捨てる恐れがある。正しい方針（解決済みエントリのみ上限を設ける、全体に上限を設けつつpendingは除外する、手動の「解決済みをクリア」導線を用意する等）は製品判断が必要。
- 利用者または開発への影響: 外部エージェントとの連携（EXT-AGENT-02）を1セッション内で繰り返し使うユーザーほど、解決済みも含めて全レビューが蓄積し続ける。

## 対応方針

- 実施すること: 上記のいずれかの排出（eviction）方針をMaintainerが決定する。
- 実施しないこと: 単純な件数上限によるトリム。未対応の`pending`エントリを誤って失うリスクがある。

## 受入条件

- [ ] 排出方針が決定される。
- [ ] 決定した方針に沿って実装される。

## 検証計画

- 実行する確認: 実装後、`npm run test`（frontend、AgentResponseImportPanel関連）。
- 期待結果: `pending`状態のレビューが誤って失われないことを確認する。

## 補足

- 発見経緯: 第14ラウンドの棚卸し（フロントエンドの無制限配列成長観点）で発見。同じ観点で見つかった`proposalAuditTrail`（島サマリー提案のadopt/reject/hold監査ログ、末尾1件しか参照されない）は、既存の`HISTORY_LIMIT`型のトリムパターンをそのまま複製するだけの機械的な修正だったため、本ラウンドで直接対応済み。
