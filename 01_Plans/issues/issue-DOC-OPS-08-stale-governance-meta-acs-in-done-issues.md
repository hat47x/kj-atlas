# Issue Draft: DOC-OPS-08 Done issueに残る廃止済みガバナンスmeta-AC

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `01_Plans/issues/issue-PRODUCT-UX-01/02/03/04-*.md`, `01_Plans/issues/issue-REQ-DEF-01/02/03-*.md`
- Related ADR/Spec: `01_Plans/lean_operations_inventory.md`（P1）, `AGENTS.md` §4・§6
- Expected verification level: `docs-check`

## 課題

Done statusの7 issueに、**廃止済みのOpenゲート礼式に由来するmeta-AC** が合計37件、未チェックのまま残っている。

対象パターン:

- `DecisionStatus=Fixed` の要求のみでACが評価可能（PendingはDecision Queueへ退避済み）
- 依存が `契約依存` と `実装依存` に分離されている
- Validation plan のコマンドがこのIssue本文だけで再実行可能
- O-OPEN-01〜04（Owner確定 / 依存1:1明示 / ACとValidation一致 / docs-only範囲外混入なし）

発生箇所（7 issue × 3〜7件）:

| Issue | 残meta-AC数 |
|---|---|
| PRODUCT-UX-01 first-run-document-entry | 7 |
| PRODUCT-UX-02 workspace-information-architecture | 7 |
| PRODUCT-UX-03 safe-share-export-flow | 7 |
| PRODUCT-UX-04 responsive-large-document-operability | 7 |
| REQ-DEF-01 value-realization-requirements-baseline | 3 |
| REQ-DEF-02 responsibility-boundary-and-contract-checkpoints | 3 |
| REQ-DEF-03 acceptance-scenarios-and-issue-splitting | 3 |
| CE4-api-cli-audit-integration | 20/60件が同パターン（G1-G4、Open化条件、tri-state、後退ゼロ等） |

**なぜこれらは永遠にチェックされないか**: これらのmeta-ACは、`AGENTS.md` §4（固定5フェーズ・RACI更新不要）と§6（2者承認・Decision Queue・RACI・KPIは既定で使わない）で廃止された礼式の一部である。`lean_operations_inventory.md` P1 は `DecisionStatus: Fixed` のissue本文書き写しを「撤去対象」と明記し、`AGENTS.md` §6 は「決定済みの参照はADR側Statusが正本、二重管理は取りやめ」と定めている。O-OPEN-* チェックはOpenゲート判定の残骸であり、issueが既にDoneへ到達した時点で判定済み（または礼式廃止で不要）である。

**実施状況**: PRODUCT-UX-01/02/03/04、REQ-DEF-01/02/03 の37件は2026-08-07に削除済み（`0883f476`）。CE0（4件）・CE2（21件契約項目）・CE4（28件契約項目）は証跡付きチェックオフ済み。CE2の4件（O-items）・CE4の32件はOpen化礼式scaffoldとして注記済み（Open未到達・Proceed=Holdの実態を反映）。CE1の3件はStop Conditions（fail-safe、発動しなかった条件）として維持。

**関連する同型パターン（追加確認 2026-08-07）**:
- `issue-doc-ops-05-01..14` シリーズは DOC-OPS-05 Set1 の固定5フェーズprotocol（AGENTS.md §4で廃止）に由来する AC/DoD テンプレートを含む。`05-01` は10件done/5件unchecked、他は大部分0件done。ただし `Status:` 形式が異なるため、Done判定自体の妥当性を含めて個別精査が必要（本issueでは追跡のみ）。
- `issue-doc-ops-05-01` のDone判定は、対象 `canonicalization.md` に `Move internal` / `Improve external` 語彙が見当たらず（grep 0件）、Done statusと実体の乖離が疑われた。→ **DOC-OPS-09で調査完了（2026-08-07）**: 5件の「未チェック」はStream G共通ACテンプレのテンプレ定義であり本issueのACではない。実体の7 ACは全て`[x]`でDone判定は妥当。`Move internal`推奨は実際の配置判断で「対外改善（公開候補）」へ上書きされている。
- `issue-doc-ops-05-01` の「Open化準備リスト」（5件）は廃止済み5-phase礼式の残骸と判断し、2026-08-07に撤去した（`411632b9`）。実AC（§5）と完了T1..T7で担保済み。
- `issue-doc-ops-05-02..14`（12件）は同型の ceremony AC/DoD テンプレートを含み、かつ各issueが固有の分類決定（Move internal / Improve external）を本文に持つ。→ **DOC-OPS-10で解決済み（2026-08-07）**: 全14件（05-01..14）の未チェック0件へ整理。§5テンプレAC・T1-T3は証跡付き`[x]`、RG/H/U/AC-R/DoD-R/Open化準備リストは注記へ変換、分類決定は維持。

## 対応方針（案）

- (a) 各Done issueの受入条件セクションから、上記パターンのmeta-AC行を **`- [x]` にせず「廃止」と明示して削除**する。Done issueの受入条件は実装ACのみを残す。
- (b) または、Done issueごとに「本セクションは廃止済み礼式の残骸」と注記し、未チェックのまま残す。
- いずれも機械的な置換ではなく、各issueのDone判定に実装ACが残ることを確認してから行う。

## 受入条件

- [ ] 7 issueから廃止済みmeta-ACを削除または注記する。
- [ ] 各issueの実装AC（claimType表示、SafeMode、レスポンシブ等）は影響を受けず、残る。
- [ ] `python 01_Plans/docs_check.py` が通る。

## 検証計画

- `python 01_Plans/docs_check.py`
- `git diff --check`
