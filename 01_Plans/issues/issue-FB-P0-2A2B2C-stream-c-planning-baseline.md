# Issue Draft: FB-P0 (2A/2B/2C) Stream E planning baseline

- Type: Process
- Status: Active (Stream E planning orchestrator)
- Source Issue: N/A
- Priority: P0
- Owner: Stream E（P0 issue memo planning）
- Scope: `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md` のみ
- Related Backlog: `FB-P2A-01/02`, `FB-P2B-01/02`, `FB-P2C-01`
- Related ADR/Spec: `ADR-0001`, `ADR-0007`, `ADR-0019`, `02_Architecture/api.md`, `02_Architecture/schemas.md`
- Expected verification level: `docs-check`

---

## Phase 1: Read（Status / Priority / 依存関係の再確認）

### Plan
- 対象メモ（P2A/P2B/P2C の A1→A2→A3）を再読し、`Status`/`Priority`/`Owner`/依存リンクを一覧化する。
- 依存循環の有無と、他ストリーム範囲との競合を検知する。

### Execute

| Backlog | A1 | A2 | A3 | Priority | 依存順序 | 所見 |
| --- | --- | --- | --- | --- | --- | --- |
| FB-P2A-01 | Ready | Ready | Ready | P0 | A1→A2→A3 | 順序固定済み |
| FB-P2A-02 | Ready | Ready | Ready | P0 | A1→A2→A3 | 順序固定済み |
| FB-P2B-01 | Ready | In Progress | In Progress | P0 | A1→A2→A3 | A2/A3進行中 |
| FB-P2B-02 | Ready | Open | Open | P0 | A1→A2→A3 | Stream E主担当 |
| FB-P2C-01 | Done | Done | Ready | P0 | A1→A2→A3 | A3引き渡し待ち |

- 依存循環チェック: A1→A2→A3の直列依存のみで**循環なし**。
- 範囲競合チェック: 本更新は baseline ファイル単独更新のため**競合なし**。

### Verify
- `Priority=P0` は全対象で一致。
- `A1→A2→A3` の順序崩れは未検出。
- フェイルセーフ条件（循環/競合/3回超過失敗）未該当。

### Proceed
- Phase 2 で、各 Backlog の AC/DoD 不足を補完提案として固定する。

---

## Phase 2: Plan（A1→A2→A3固定 + AC/DoD不足補完）

### Plan
- 各 Backlog に対して A1/A2/A3 の受入境界を再定義し、抜けている AC/DoD をドラフト提案する。

### Execute

| Backlog | A1（契約固定） | A2（mock検証） | A3（handoff条件） | AC/DoD補完ドラフト |
| --- | --- | --- | --- | --- |
| FB-P2A-01 | `IslandHierarchyContractV1` | root/多段/不正参照/循環 | 契約逸脱ゼロで実装レーンへ | DoDに「roundtrip同値判定キー」を明記 |
| FB-P2A-02 | visibility contract 固定 | collapsed導出の分岐検証 | 既存表示互換を前提にhandoff | ACに「単一ソース原則」追記 |
| FB-P2B-01 | candidate group 契約ID固定 | 同一入力同一順序の検証 | 比較キー固定でhandoff | DoDに「tie時の順序キー」明記 |
| FB-P2B-02 | decision log 契約ID固定 | 保存/復元/手動確定フラグ検証 | rollback条件付きhandoff | ACに「非自動確定の保持」追記 |
| FB-P2C-01 | tie-break順序承認済み | deterministic検証完了 | A3開始条件のみ管理 | DoDに「順序追加禁止」を明記 |

### Verify
- 全Backlogで `A1→A2→A3` の固定順序を維持。
- AC/DoD補完は既存ADR範囲内（新方針追加なし）。

### Proceed
- Phase 3 で I/F依存点を stub/fixture 前提に分離する。

---

## Phase 3: Mock設計（I/F依存点のstub/fixture分離）

### Plan
- 実装コード前提を排除し、A2検証に必要な I/F だけを stub/fixture へ落とし込む。

### Execute
- 共通 stub I/F:
  - `contractVersion`
  - `mockCaseId`
  - `inputHash`
  - `expectedDeterministicOrder`
  - `validationResult`
  - `ownerOfFix`（A1/A2/A3）
- 共通 fixture 方針:
  1. 入力固定（seed固定・時刻非依存）
  2. 比較キー固定（hash/順位/roundtrip同値）
  3. 失敗時責務分離（契約不備= A1、検証不備= A2、反映不備= A3）

### Verify
- I/F依存点は planning レベルで閉じており、`03_Implement/**` 非依存。
- mock-only で検証可能な境界に分離済み。

### Proceed
- Phase 4 でメタ整合（validator想定）を確認する。

---

## Phase 4: Verify（メタ整合 / validator想定整合）

### Plan
- issue memo validator を基準に、命名/メタ/リンク整合を点検する。

### Execute
- 実行コマンド: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 変更範囲確認: `git diff --name-only`

### Verify
- validator で active memo の整合を確認。
- 変更範囲は Stream E 許可範囲内（baseline ファイルのみ）。

### Proceed
- Phase 5 で B/C/D へ渡す実行順序表を確定する。

---

## Phase 5: Handoff（B/C/D向け実行順序表）

### Plan
- 各ストリームが衝突せずに前進できるよう、Backlog単位で直列順序を明示する。

### Execute

| 実行順位 | Backlog | 実行順 | 受け渡し先 | Go条件 | Stop条件 |
| --- | --- | --- | --- | --- | --- |
| 1 | FB-P2A-01 | A1完了 → A2確認 → A3引渡し | Stream B/C | 契約ID一致 | 契約キー追加要求 |
| 2 | FB-P2A-02 | A1完了 → A2確認 → A3引渡し | Stream B/C | 可視性単一ソース維持 | 多重フラグ化要求 |
| 3 | FB-P2B-01 | A1完了 → A2進行完了 → A3完了 | Stream D | deterministic順序固定 | tie-break再定義要求 |
| 4 | FB-P2B-02 | A1完了 → A2着手 → A3着手 | Stream E主担当 | decision log保持 | 非自動確定喪失 |
| 5 | FB-P2C-01 | A1/A2完了 → A3着手判定のみ | Stream B/F | Gate承認+比較キー継承 | 承認済順序の変更 |

### Verify
- 依存循環なし。
- 他ストリーム編集範囲への直接編集なし。
- フェイルセーフ発動条件未該当。

### Proceed
- Stream E planning baseline として本版を固定し、実装レーンは各A3メモの開始条件に従って進行する。

---

## ADRルール適用記録

- 判定: **ADR変更不要**。
- 理由: 本更新は既存ADR範囲内の planning 整理（順序固定・検証境界の明文化）であり、
  新規の Context / Decision / Consequences 追加を伴わない。
- 追跡: 将来、契約キー追加や tie-break 変更が必要になった場合のみ ADR 起票を行い、承認待ちへ遷移する。

## Self-Correction Log（最大3回）

1. 修正1: Phase名をユーザー指定の5段（Read/Plan/Mock設計/Verify/Handoff）に統一。
2. 修正2: A1→A2→A3 の順序を Backlog別の表で固定化。
3. 修正3: AC/DoD不足補完をドラフト提案として明示し、既成事実化を回避。

> 上限超過時停止ルール: Self-Correction が 3 回を超える場合は更新を停止し、競合一覧を提出する。
