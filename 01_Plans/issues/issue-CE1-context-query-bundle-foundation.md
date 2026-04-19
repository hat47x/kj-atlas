# Issue Draft: CE1 ContextQuery/ContextBundle Foundation（Stream D / planning-only）

- Type: Feature request
- Status: Open
- Priority: P1
- Owner: Stream D（CE1専属）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Related Backlog: `CE-1`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard（独立性）
- CE1は **I/F凍結のみ**。実装記述（handler/UI/DB/worker）は扱わない。
- モック依存切断: 実装待ちを禁止し、mock hash前提で契約検証を完了させる。
- 未承認決定を確定扱いしない。

## Phase 1) Read同期（ADR-0028整合確認）
### Contract IDs（凍結対象）
- `CE1-CTXQ-IF`（ContextQueryV1）
- `CE1-CTXB-IF`（ContextBundleV1）
- `CE1-HASH-DET-IF`（hash決定論）
- `CE1-PREVIEW-GATE-IF`（preview gate）

### Error semantics（語彙固定）
- `preview_required`
- `unknown_contract_key`
- `nondeterministic_bundle`

### 判定原則
- Query Preview必須: `previewConfirmed=false` は常に `422 preview_required`。
- closed-world: 未定義キーが1つでも存在した場合は常に `400 unknown_contract_key`。
- deterministic hash: 同一 canonical query は再実行しても `queryCanonicalHash` / `bundleHash` が一致。

## Phase 2) CE0参照下でCE1契約凍結（CDC明文化→承認）
- `ContextQueryV1` / `ContextBundleV1` を v1 closed-world として固定（未定義キー追加禁止）。
- CE0 `CE0-CTX-IF` / `CE0-SAFEMODE-IF` を参照し、CE1側でsafeMode既定を再定義しない。
- v1拡張要求は未承認の限り `held` とし、v2再起票まで確定しない。

## Phase 3) CE1/CE2のmock前提I/F分離
- CE2連携キーは `sourceBundleHash === bundleHash` 比較に固定。
- CE2側で ContextQueryV1/BundleV1 を拡張しない（参照のみ）。
- mock hash と本番hashでI/Fを分岐しない（語彙共通）。

## Phase 4) CE4連携契約（API/CLI/Audit）定義
- CE4同値判定へ渡す固定キー: `equivalenceKey`, `queryCanonicalHash`, `bundleHash`。
- API/CLI/GUIで同一 canonical query が同一 `bundleHash` を返すことを前提契約化。
- 監査導線は `query/bundle` をCE1側最小出力として必須化。

## Phase 5) Verify / Proceed
### Acceptance Criteria
- [ ] 同一 canonical query 3回で `queryCanonicalHash` が完全一致
- [ ] 同一 canonical query 3回で `bundleHash` が完全一致
- [ ] `previewConfirmed=false` は常に `422 preview_required`
- [ ] 未定義キー入力は常に `400 unknown_contract_key`
- [ ] `nondeterministic_bundle` は hash不一致時のみ使用

### Definition of Done
- [ ] CE2/CE4 が `sourceBundleHash === bundleHash` 比較で依存可能
- [ ] `ContextQueryV1` / `ContextBundleV1` 語彙が一意
- [ ] v1 closed-world、拡張は v2のみを明文化
- [ ] mock hash 検証手順で実装待機なしを担保

### Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`
- 5 Issue横断レビューで CE1語彙（contract ID / error semantics / hash用語）の衝突数を `0` にする。
- 自己修復は最大3回。4回目相当は停止。

### Proceed（実装ストリーム向けI/F配布）
- `ContextQueryV1`
- `ContextBundleV1`
- Error semantics: `preview_required / unknown_contract_key / nondeterministic_bundle`
