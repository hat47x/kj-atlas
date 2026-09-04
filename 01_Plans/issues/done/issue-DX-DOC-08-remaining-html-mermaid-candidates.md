# Issue Draft: DX-DOC-08 HTML+Mermaid化の残り候補（中〜高リスク4件）

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `02_Architecture/strict_mode_exception_approval_flow.html`, `02_Architecture/enterprise_architecture.html`, `02_Architecture/architecture.html`, `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Related ADR/Spec: `AGENTS.md` §3「文書の形式」
- Expected verification level: `docs-check`

## 課題（起票時点）

`AGENTS.md` §3 の方針に基づき、設計文書へのHTML+Mermaidビュー追加を継続する探索を行った。低リスクの2件（`external_agent_collaboration_spec.md`、`phase6-public-documentation-architecture.md`）は既に実施済み（別PR）。残る4件は、いずれも図解化の価値はあるが、被参照数・保守コスト・既存候補との重複のいずれかで判断が必要なため起票のみとした。

### 候補1: `strict_mode_exception_approval_flow.md` §4 承認状態機械（中リスク）

`` ```text``` ``フェンス内に手書きの状態機械（DraftRequest→ApprovalPending→Approved→ActiveException→RollbackPending→Closed、任意状態からのStoppedForClarification/Rejectedへのエスケープ）を持つ。§8.4に「両方同時発生時はrecovery実行がstop記録に優先する」という非自明な優先順位規則もあり、これも決定図として描ける。この文書は `AUTH-OPS-03` の正本であり、`enterprise_architecture.md`・`review_attribution.md`・`schemas_review_attribution.md` からD1〜D4固定値の変更のたびに再同期される。被参照20ファイル。図を追加すると、これらの同期のたびに図も更新する継続的な保守コストが生じる。

### 候補2: `enterprise_architecture.md` §4 公開クラス×配信方式×アクセス制御フォールバック（中リスク）

可視性4区分（Public/Unlisted/Org/Restricted）×配信方式3種（方式A静的/方式B認証/方式Cハイブリッド）のマッピングと、AccessControlAdapterの優先順位（SafeMode→readOnly→AccessDecision→visibility、散文のみで記述）＋4分岐フェイルセーフ表を持つ。被参照30ファイル。候補1（`strict_mode_exception_approval_flow.md`）と対象領域が重複する（本セクションは実際の承認状態機械を候補1文書へ委譲している）。

### 候補3: `architecture.md` §7A 三層グラフの責務・データフロー境界（高リスク）

WorkingGraph / ContextProjectionGraph / Consensus Graphの許可されたデータフロー（Working→Consensusはpatch+approval経由のみ、Working→ContextProjectionは読取専用投影のみ）を、箇条書き＋契約IDテーブルのみで表現している。アーキテクチャ全体で最も図解価値が高い一方、被参照71ファイルと `02_Architecture` 内で最多、かつCE-0/CE-1のストリームログによって頻繁に改訂される、全候補中最も改訂頻度が高い文書。追加すれば同期漏れリスクが候補中最大。

### 候補4: `hil_rs_01_a1_minimum_interface_contract.md` Governance Gate / Decision Queue（低〜中リスク、ただし別種の対応が適切）

約600行にわたる「Stream A」フェーズログの反復記載の下に、4契約I/F（A1-CRITIQUE-IF/REDIFF-IF/ATTR-IF/ERROR-IF）のゲート条件と、厳格な2状態Decision Queue（Pending→Approved | Pending→Rejected、他遷移禁止）という実質的な構造がある。被参照7ファイルと最少で図追加自体のリスクは低い。ただしこの文書の主要な問題は「図解不足」ではなく「反復するボイラープレートの過多」であり、Markdown本体の重複セクション整理が図追加より優先度の高い対応である可能性が高い。

## 解決（2026-08-22、ユーザー承認により全4件着手）

利用者から4件すべてに着手する明示的な承認を得て、着手順に検証した。

- **候補1・候補2・候補3は着手前から既に解決済みだった。** コミット `736f80ad`（2026-08-06 07:29、本issueの起票コミット `ccbaa068` から約7時間後）が `architecture.md` / `enterprise_architecture.md` / `strict_mode_exception_approval_flow.md` を含む7件をHTML+Mermaidへ変換し、旧Markdownを退役させていた。本issueは起票後にこの変換が行われたにもかかわらず更新されず、内容が陳腐化していた。
  - 候補1: `strict_mode_exception_approval_flow.html` に承認状態機械の `stateDiagram-v2`（`StoppedForClarification`/`Rejected`のエスケープ遷移込み）と、§8.4の優先順位規則を明示するハイライト済み散文注記（"非矛盾ルール（§8.4）"）が存在することを確認した。優先順位規則自体を独立したMermaid図に追加する変更は行っていない（既存の散文注記が§番号付きで明示されており、新規図追加は保守コスト増に対して価値が薄いと判断）。
  - 候補2: `enterprise_architecture.html` に visibility×配信方式の `flowchart`、AccessControlAdapterの判定フロー `sequenceDiagram`（`SafeMode → readOnly` の先行評価を含む）、4分岐フェイルセーフ表（§4.4）が存在することを確認した。
  - 候補3: `architecture.html`（旧§7Aに相当する現行セクション「05 CE-0 責務・信頼境界」、`id="ce0-boundary"`）に WorkingGraph / ContextProjectionGraph / ConsensusGraph の許可データフローを表す `flowchart`（禁止経路を赤破線で明示）が存在することを確認した。既存の図・表・散文には変更を加えていない（最多被参照・最高頻度改訂ファイルであるため、既存内容の再解釈や上書きを避けた）。
  - 上記3件について、変換自体はやり直さず、変換に伴う参照更新の**取り残し**のみを修正した: `strict_mode_exception_approval_flow.html`（3箇所）と `external_agent_collaboration_spec.html`（1箇所）に残っていたバッククォート引用 `enterprise_architecture.md` を `enterprise_architecture.html` へ修正した（`[text](path)` 形式ではないコードスパン引用のため、変換当時の `git grep` 洗い出しが対象にしていなかったと見られる。同種の問題は `issue-DX-DOC-09-backtick-path-citations-unchecked-by-link-checker.md` がリポジトリ全体で追跡している）。
- **候補4は判断のうえHTML化を見送った。** ファイルを全文確認した結果、実質的な契約定義（§2 Contract Matrix、§4 Governance Gate、Decision Queueの2状態遷移）は文書の一部に過ぎず、残り大半（§7が3回、§9が5回出現する）は同一の凍結値・Go/NoGo式を日付を変えて反復する「Stream A」フェーズログのボイラープレートだった。この状態でHTML+Mermaid化を行うと、反復するボイラープレートをそのままHTMLへ持ち込むだけで、AGENTS.md §3が変換の目的とする「認知負荷の低減」に寄与しない。図が効くのは§2・§4の契約構造だけであり、文書の主要な問題（ボイラープレートの重複）は図の追加では解決しない。**Markdown側の重複セクション整理を先行させるべきという本issueの当初の懸念を、全文確認により裏付けたため、HTML化を見送り、Markdownを正本のまま維持する。**別issueとしてボイラープレート整理を提案する（本セッションでbackground taskとして起票済み）。

### 追加で発見した事項（本issueの範囲外、参考記録）

- issue ID `DX-DOC-08` が本issueと `01_Plans/issues/done/issue-DX-DOC-08-api-md-endpoint-coverage-gap.md`（無関係な既存Done issue）で重複している。ファイル名は異なるため実害はないが、ID重複自体はADRで過去に扱われた既知の再発パターン（ADR番号重複と同種）。本issueでは対応しない。

## Acceptance

- [x] 候補1〜4について、着手する/しない、および着手順序をメンテナ（利用者）が決定した（全4件着手を承認）。
- [x] 着手した候補（1・2・3、着手前から解決済みと判明）について、`AGENTS.md` §3の文書形式ルールに従っていることを確認した（HTML+Mermaidが正本、旧Markdownは退役済み）。取り残されていた参照（バッククォート引用4箇所）を修正した。
- [x] 候補4については、HTML化ではなくMarkdown本体の重複整理を先行させるべきと判断し、HTML化を見送った。

## Validation

- `python 01_Plans/docs_check.py` — 実施済み（結果は本issueをコミットするPRの記録を参照）。
- `python 03_Implement/backend/scripts/check_design_consistency.py` — 実施済み（同上）。
- 実施した候補（1・2・3）は着手前から本文にMermaid `flowchart`/`sequenceDiagram`が存在し、`mermaid.min.js`（UMD版）を classic `<script>` で読み込む既存パターンに従っていることを目視確認した。ヘッドレスブラウザでの再描画確認は本セッションでは実施していない（既存の変換パターンを流用した既存ファイルであり、新規追加ではないため）。


## 配置の整理（2026-09-05）

- 本Issueは内容上すべての受入条件を満たして `Done` となっていた一方、R18以前からの経緯により、完了済みのまま作業中Issueと同じルートへ残るlegacy集合に含まれていた。
- 既存のライフサイクル契約は、このlegacy集合を恒久的に残すものではない。移行のたびに `LEGACY_DONE_AT_ROOT_BASELINE` を同じ変更で下げ、完了済みIssueを `01_Plans/issues/done/` へ移す単調減少のラチェットである。
- 本変更では文書系の完了済みIssue 3件をまとめて正規配置へ移し、baselineを57から54へ縮小した。R18時点のidentity manifestは、新しいDone-at-rootの混入を防ぐ歴史境界なので変更しない。
- 旧rootパスを引用していた箇所は、現在の `done/` パスへ同時に更新した。
