# Issue Draft: CE4 API/CLI/監査統合（Stream E / CE4専任 / contract-only planning）

- Type: Feature request
- Status: Open
- Priority: P2
- Owner: Stream E（CE4専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE4-api-cli-audit-integration.md` のみ
- Related Backlog: `CE-4`
- Related ADR/Spec: `ADR-0028`, `ADR-0008`, `02_Architecture/schemas.md`
- Dependencies: `CE-4`
- Verification: `docs-check`

## Stream E Execution Contract（2026-05-03 / CE4 API/CLI Audit Integration）

フェーズ順序は固定: **Read → Plan → ADR/CDC承認（必要時）→ Execute → Verify（最大3回修復）→ Proceed/Stop**。

### Phase 1 Read
- CE4は API/CLI監査境界の契約固定に限定し、frontend/backend実装差分を要求しない（mock-first）。
- CE0/CE1/CE2は read-only 参照専用とし、契約語彙の再定義・拡張を行わない。
- fixed boundary を再確認する: `equivalenceKey + bundleHash`（AND）, 監査4イベント（`query/bundle/proposal/apply`）, fail-closed。
- proposal-only 原則（auto-apply / auto-confirm / auto-publish 禁止）を開始時に再確認する。

### Phase 2 Plan（proposal-only / non-target明記）
- Planは contract proposal のみを扱い、`accepted/rejected` の最終決定は人間責務とする。
- 非対象（実装コード）は明示的に固定する。
  - `03_Implement/frontend/**`（全実装コード）
  - `03_Implement/backend/**`（全実装コード）
  - `03_Implement/deploy/**`（全実装コード）
  - `02_Architecture/**`（本Issueでは契約参照のみ、更新禁止）
- API I/F（必須入力・必須出力・fail-closed条件）とCLI I/F（必須オプション・出力JSON・終了コード）を mock可能粒度で定義する。
- 監査要件は `query / bundle / proposal / apply + queryCanonicalHash` を必須項目として固定する。

### Phase 3 ADR/CDC承認（必要時のみ）
- ADR/CDCが必要な差分は **Context / Decision / Consequences** を先に明文化し、人手承認まで `status=held` を維持する。
- AC/DoD不足時は契約ドラフトを追記し、推測実装・暗黙決定を禁止する。
- 承認対象は「API責務境界」「CLI責務境界」「監査責務境界」を分離して扱う。

### Phase 4 Execute（contract-only / mock-first）
- Executeは docs上の patch/diff 記録のみ許可し、実装着手・実装確定（implementation commit）を禁止する。
- API/CLI同値判定は `equivalenceKey` と `bundleHash` の **AND成立のみ成功** とし、部分一致成功を禁止する。
- `sourceBundleHash=mock:<hash>` を同値検証参照キーとして許可し、本番hashと同一の fail-closed 条項を適用する。

### Phase 5 Verify（最大3回修復）
- 追跡性: API/CLI双方から同一監査チェーン（4イベント+`queryCanonicalHash`）を辿れること。
- 追跡性(追加): 各監査イベントで `eventType`（`query|bundle|proposal|apply`）と `equivalenceKey` の双方を相関キーとして必須記録し、API/CLIの双方ログから同一実行を往復追跡できること。
- 再現性: 同一入力で `equivalenceKey/bundleHash/queryCanonicalHash` を比較可能であること。
- 安全境界: safeMode既定ON と proposal-only 境界の後退がないこと。
- 修復上限: 検証失敗時の自己修復は `1/3`〜`3/3` まで。`4/3` 相当は fail-safe で即停止し `status=held`。

### Phase 6 Proceed/Stop
- Proceed条件（全件必須）:
  - [ ] proposal-only 境界（自動確定化なし）が明記されている。
  - [ ] API I/F（必須入力・必須出力・fail-closed条件）が固定されている。
  - [ ] CLI I/F（必須オプション・出力JSON・終了コード）が固定されている。
  - [ ] 監査境界（4イベント + `queryCanonicalHash`）欠損時 fail-closed が明記されている。
  - [ ] 監査4点セット（`query/bundle/proposal/apply`）のいずれか欠損時は **No-Go** と明記されている。
  - [ ] `eventType` と `equivalenceKey` の追跡可能性（API/CLI相互追跡）が AC として明記されている。
  - [ ] API/CLI同値判定（`equivalenceKey AND bundleHash`）のみ成功とする契約が固定されている。
  - [ ] 実装隊が mock-first で着手可能な独立契約として参照できる。
- Stop条件（いずれかで即停止）:
  - proposal-only 逸脱（auto-apply/auto-confirm/auto-publish）
  - 監査不能状態（必須監査項目欠損を成功扱い）
  - safeMode後退要求
  - 責務分離崩壊（API/CLI/監査境界の混線）
  - Verify自己修復3回超過（`4/3` 相当）

## CE4 Dependency Cut Contract（mock-first 固定）
- CE4は `equivalenceKey + bundleHash` のI/F契約を mock前提で固定し、他ストリーム実装完了待ちを行わない。
- API/CLI同値判定は AND 条件（`equivalenceKey` かつ `bundleHash`）を唯一の成功条件とする。
- 依存切断の範囲は契約I/Fに限定し、実装詳細・アルゴリズム詳細は記述しない。

## Lane Guard（独立性・停止条件）
- 編集対象は `issue-CE4-api-cli-audit-integration.md` のみに限定する。
- CE4は CE0 SSOT + CE1/CE2 read-only handoff を参照し、CE0/CE1/CE2を更新しない。
- CE4は CE0/CE1/CE2 の契約語彙を再定義しない（read-only参照のみ）。
