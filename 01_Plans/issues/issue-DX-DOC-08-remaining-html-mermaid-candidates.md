# Issue Draft: DX-DOC-08 HTML+Mermaid化の残り候補（中〜高リスク4件）

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `02_Architecture/strict_mode_exception_approval_flow.md`, `02_Architecture/enterprise_architecture.md`, `02_Architecture/architecture.md`, `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Related ADR/Spec: `AGENTS.md` §3「文書の形式」
- Expected verification level: `docs-check`

## 課題

`AGENTS.md` §3 の方針に基づき、設計文書へのHTML+Mermaidビュー追加を継続する探索を行った。低リスクの2件（`external_agent_collaboration_spec.md`、`phase6-public-documentation-architecture.md`）は既に実施済み（別PR）。残る4件は、いずれも図解化の価値はあるが、被参照数・保守コスト・既存候補との重複のいずれかで判断が必要なため起票のみとする。

### 候補1: `strict_mode_exception_approval_flow.md` §4 承認状態機械（中リスク）

`` ```text``` ``フェンス内に手書きの状態機械（DraftRequest→ApprovalPending→Approved→ActiveException→RollbackPending→Closed、任意状態からのStoppedForClarification/Rejectedへのエスケープ）を持つ。§8.4に「両方同時発生時はrecovery実行がstop記録に優先する」という非自明な優先順位規則もあり、これも決定図として描ける。この文書は `AUTH-OPS-03` の正本であり、`enterprise_architecture.md`・`review_attribution.md`・`schemas_review_attribution.md` からD1〜D4固定値の変更のたびに再同期される。被参照20ファイル。**図を追加すると、これらの同期のたびに図も更新する継続的な保守コストが生じる。**

### 候補2: `enterprise_architecture.md` §4 公開クラス×配信方式×アクセス制御フォールバック（中リスク）

可視性4区分（Public/Unlisted/Org/Restricted）×配信方式3種（方式A静的/方式B認証/方式Cハイブリッド）のマッピングと、AccessControlAdapterの優先順位（SafeMode→readOnly→AccessDecision→visibility、散文のみで記述）＋4分岐フェイルセーフ表を持つ。被参照30ファイル。**候補1（`strict_mode_exception_approval_flow.md`）と対象領域が重複する**（本セクションは実際の承認状態機械を候補1文書へ委譲している）。候補1を先に作り、なお本セクションが必要か再評価すべき。

### 候補3: `architecture.md` §7A 三層グラフの責務・データフロー境界（高リスク）

WorkingGraph / ContextProjectionGraph / Consensus Graphの許可されたデータフロー（Working→Consensusはpatch+approval経由のみ、Working→ContextProjectionは読取専用投影のみ）を、箇条書き＋契約IDテーブルのみで表現している。アーキテクチャ全体で最も図解価値が高い一方、**被参照71ファイルと `02_Architecture` 内で最多**、かつCE-0/CE-1のストリームログによって頻繁に改訂される、全候補中最も改訂頻度が高い文書。追加すれば同期漏れリスクが候補中最大。

### 候補4: `hil_rs_01_a1_minimum_interface_contract.md` Governance Gate / Decision Queue（低〜中リスク、ただし別種の対応が適切）

約600行にわたる「Stream A」フェーズログの反復記載の下に、4契約I/F（A1-CRITIQUE-IF/REDIFF-IF/ATTR-IF/ERROR-IF）のゲート条件と、厳格な2状態Decision Queue（Pending→Approved | Pending→Rejected、他遷移禁止）という実質的な構造がある。被参照7ファイルと最少で図追加自体のリスクは低い。**ただしこの文書の主要な問題は「図解不足」ではなく「反復するボイラープレートの過多」であり、Markdown本体の重複セクション整理が図追加より優先度の高い対応である可能性が高い。**

## 論点（人的判断が必要な理由）

- 候補1・2は保守コスト（同期対象の増加）と図解価値のトレードオフであり、`AUTH-OPS-03`/D1-D4値の変更頻度を知るメンテナの判断が必要。
- 候補2は候補1との重複解消順序の判断を要する。
- 候補3は本セッションで最も価値が高いと分かった箇所だが、最も改訂頻度が高い箇所でもあり、着手順序は他の作業（CE-0/CE-1ストリームの落ち着き具合）を踏まえた判断が必要。
- 候補4は「図を足す」のではなく「Markdown自体をやせさせる」方が正しい対応である可能性が高く、これはHTML化ではなく別種のドキュメント整理issueとして扱うべきかの判断を要する。

## 影響

低リスク（追加ビューが無くても既存Markdownは正本として機能する）。着手すれば設計文書の可読性が向上する。

## Acceptance

- [ ] 候補1〜4について、着手する/しない、および着手順序をメンテナが決定する。
- [ ] 着手する場合、`AGENTS.md` §3の文書形式ルールに従う（Markdownを正本として残す）。
- [ ] 候補4については、HTML化ではなくMarkdown本体の重複整理を先行させるかを判断する。

## Validation

- 実施した候補について、Mermaid図がCDN経由でエラーなく描画されることをheadlessブラウザで確認する。
- `python 01_Plans/docs_check.py` が新規HTMLに対しても通過することを確認する（DX-DOC-07で追加された検査）。
