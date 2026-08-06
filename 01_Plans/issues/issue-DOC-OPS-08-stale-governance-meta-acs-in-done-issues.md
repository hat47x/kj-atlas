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

**なぜこれらは永遠にチェックされないか**: これらのmeta-ACは、`AGENTS.md` §4（固定5フェーズ・RACI更新不要）と§6（2者承認・Decision Queue・RACI・KPIは既定で使わない）で廃止された礼式の一部である。`lean_operations_inventory.md` P1 は `DecisionStatus: Fixed` のissue本文書き写しを「撤去対象」と明記し、`AGENTS.md` §6 は「決定済みの参照はADR側Statusが正本、二重管理は取りやめ」と定めている。O-OPEN-* チェックはOpenゲート判定の残骸であり、issueが既にDoneへ到達した時点で判定済み（または礼式廃止で不要）である。

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
