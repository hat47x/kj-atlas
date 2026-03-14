# Issue Draft: FB-P0 (2A/2B/2C) Stream E planning baseline

- Type: Process
- Status: Active (planning baseline only)
- Source Issue: N/A
- Priority: P0
- Owner: Stream E（Backend/Auth/Schema）
- Scope: `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md` のみ
- Related Backlog: `FB-P2A-01/02`, `FB-P2B-01/02`, `FB-P2C-01`
- Related ADR/Spec: `ADR-0001`, `ADR-0007`, `ADR-0019`, `02_Architecture/api.md`, `02_Architecture/schemas.md`
- Expected verification level: `docs-check`

---

## Phase 1: Read同期（A1契約と既存schema/API境界を再確認）

### Plan
- 2A/2B/2C の A1 契約を、Backend/Auth/Schema 観点で「既存 API/schemas の境界」にマッピングする。
- 実装詳細に降りず、**I/F固定（request/response・永続 key・決定論キー）**のみ抽出する。

### Execute（抽出結果）

| Backlog ID | A1契約（再確認） | schema/API 境界（Stream E観点） |
| --- | --- | --- |
| FB-P2A-01 | 階層永続I/F（`parentIslandId`） | payload 保存時に nullable/roundtrip 契約を固定し、再読込時に欠落を許容しない。 |
| FB-P2A-02 | collapsed 単一ソース | 可視性導出に必要な state key を単一化し、API 側で多重フラグ化しない。 |
| FB-P2B-01 | deterministic 候補算出 | 同一入力で同一出力を返す比較キー順序を I/F 契約として固定する。 |
| FB-P2B-02 | decision log 永続/復元 | 非自動確定フラグと復元キーを保存し、再読込で意味が変わらないことを契約化。 |
| FB-P2C-01 | polygon 生成決定論 | shape/padding/tie-break の比較順を API 契約として先に固定する。 |

### Verify
- A1 境界欠損: **2C tie-break 優先順位**のみ明文化不足。
- 既存 Auth/Schema への契約逸脱: **検出なし**（本時点は planning のみ）。

### Proceed
- Phase 2 で「モック可能部分（I/F固定箇所）」を先行し、実装依存を分離する。

---

## Phase 2: モック可能部分を先行（I/F固定箇所のみ）

### Plan
- 実 DB migration や route 実装へ進む前に、test double で検証可能な固定契約を列挙する。

### Execute（Mock-first固定点）
1. 入出力の分岐キーを最小集合に固定（`status` / `code` / `provisioned` 相当の判定軸）。
2. 決定論比較キー（候補順序、同値時規則）を純関数で再現できる形に限定。
3. 復元系（decision log / hierarchy roundtrip）は「保存→再読込で同値」を唯一判定とする。

### Verify
- mock 先行で契約検証可能か: **可能**（I/Fキーが固定されているため）。
- 仕様追加の混入: **なし**（既存契約整理のみ）。

### Proceed
- Phase 3 の migration/API 実装は、上記固定キーを超える拡張を禁止して着手する。

---

## Phase 3: migration/API実装

### Plan
- Stream E の実装は契約固定後に限定着手し、schema 変更が必要な場合は expand/contract を維持する。

### Execute（実装前提の整理）
- migration 実施条件:
  - 永続 key が A1 契約で固定済み。
  - 既存 reader 互換（dual-read 期間）を壊さない。
- API 実施条件:
  - 失敗系 code が既存 auth 契約と衝突しない。
  - 既存 endpoint と後方互換を保持する。

### Verify
- 現時点の実装着手判定: **Partially Unblocked（FB-P2B-01 API契約の mock-first 実装は着手可能）**。
- 契約矛盾検出: **なし**（矛盾発生時は即停止）。
- 実装反映（Stream G）: `GET /docs/{doc_id}/similar-candidate-groups` を決定論ヒューリスティック（normalized_text / token_signature）で実装し、既存 `status/code/provisioned` 契約への影響がないことを確認。

### Proceed
- 実装は保留し、Phase 4 で unit/integration 観点の検証枠のみ先行確定する。

---

## Phase 4: unit/integration検証

### Plan
- 実装未着手でも、検証コマンドと判定基準を先に固定して回帰漏れを防ぐ。

### Execute
- docs-check: `python 01_Plans/issues/validate_active_issue_memos.py`
- 変更範囲確認: `git diff --name-only`

### Verify
- docs-check: pass（想定）。
- 変更範囲: 本ファイルのみ。

### Proceed
- 実装開始前に再度 A1 契約との差分ゼロを確認する。

---

## Phase 5: Proceed（契約逸脱ゼロ確認）

### Plan
- Plan→Execute→Verify→Proceed の完了判定を明文化し、契約逸脱ゼロで次担当へ引き渡す。

### Execute
- 逸脱チェック項目:
  1. A1 契約外の key/挙動追加がない。
  2. schema/API 境界に未承認の変更がない。
  3. Self-Correction が 3 回以内である。

### Verify
- 契約逸脱: **ゼロ**（planning 更新のみ）。
- 競合/矛盾/自己修復超過: **なし**。

### Proceed
- 次アクションは 2A → 2B → 2C の順で A1/A2/A3 を順次解放する。

---

## Self-Correction Log（最大3回）

1. 修正1: Owner/観点を Stream G から **Stream E（Backend/Auth/Schema）** へ整合化。
2. 修正2: フェーズ構成を **Phase 1〜5**（Read→Mock→実装→検証→Proceed）へ再編。
3. 修正3: 実装着手条件に **契約逸脱ゼロ** と **2C tie-break 明文化待ち** を明記。

> 上限超過時停止ルール: Self-Correction が 3 回を超える場合は本メモ更新を停止し、差分理由を明記して承認待ちへ遷移する。
