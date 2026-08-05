# Issue Memo: ENV-PROFILE-01 Runtime profile guidance

- Type: Documentation quality / Process
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex
- Scope: `02_Architecture/`, `04_Documentation/`
- Related Backlog: `ENV-CONFIG-DRIFT-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0021-env-var-global-prefix-migration.md`, `01_Plans/adr/ADR-0029-third-party-runtime-env-boundary.md`, `02_Architecture/runtime_parameter_registry.md`, `02_Architecture/deployment.md`, `02_Architecture/enterprise_architecture.md`
- Dependencies: `01_Plans/issues/issue-ENV-CONFIG-DRIFT-01-runtime-configuration-contract-alignment.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: ENV-PROFILE-01
- RequirementStatement: 実行環境ごとの推奨設定プロファイルを明示し、既定値と本番推奨値の見え方を分離する。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=公開環境変数はすべて `KJ_ATLAS_` で始まる; 操作=runtime registry と deployment/enterprise docs を読む; 期待結果=local-dev/evaluation/enterprise-production の違いを判断できる; 除外=実装既定値の変更。
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / public-exposure

## 1) 課題 / Problem statement

`KJ_ATLAS_ALLOW_JIT_PROVISIONING` は実装既定値として `true` だが、企業・行政運用では strict profile として `false` が推奨される。この関係は矛盾ではないが、初見では「本番でも true が推奨なのか」と誤読される可能性がある。

また、LLM provider、audit HTTP、access control などの設定は、local-dev / evaluation / enterprise-production で推奨値が異なる。既定値、評価用設定、本番推奨を分けて示すことで、運用判断の負荷を下げられる。

## 2) 背景 / Context

- `runtime_parameter_registry.md` は公開環境変数の単一正本である。
- 04文書ではすべての公開環境変数を記載する方針が確定している。
- `enterprise_architecture.md` は strict mode を本番標準として扱う。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 導入者が小さく始めつつ、安全な本番運用へ移行しやすくなる。
- 安全（THREAT_MODEL / SafeMode）: 誤った既定値理解による公開・認証・外部連携リスクを下げる。
- 企業・行政要件（enterprise_architecture）: strict profile の説明可能性が上がる。
- 後方互換（schemas）: 実装既定値を変更しない限り互換影響はない。

## 4) 提案する解決策 / Proposed solution

- `runtime_parameter_registry.md` に profile guidance を追加する。
- local-dev / evaluation / enterprise-production の推奨設定差分を表で示す。
- 実装既定値と本番推奨値が異なる項目は、その理由と安全境界を明記する。
- `deployment.md` と `enterprise_architecture.md` から profile guidance へ導線を追加する。

Non-goals:

- 実装既定値を変更しない。
- `KJ_ATLAS_ALLOW_JIT_PROVISIONING` の既定値変更は本issueでは扱わない。
- サードパーティコンテナ内部環境変数の設計判断は ADR-0029 に委ねる。

## 5) 受入条件 / Acceptance criteria

- [x] `runtime_parameter_registry.md` に実行プロファイル表が追加される。
- [x] `KJ_ATLAS_ALLOW_JIT_PROVISIONING=true` の実装既定と enterprise production の `false` 推奨が区別される。
- [x] `deployment.md` と `enterprise_architecture.md` からプロファイル表へ辿れる。
- [x] 公開設定キーはすべて `KJ_ATLAS_` で始まる方針を維持する。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: `runtime_parameter_registry.md` に profile guidance を追加する。
- [x] T2: `deployment.md` に評価/本番プロファイル参照を追加する。
- [x] T3: `enterprise_architecture.md` に strict profile 参照を追加する。
- [x] T4: 00/02の環境変数例に非 `KJ_ATLAS_` が混入していないことを確認する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `git diff --check`
  - `rg --pcre2 -n 'export (?!KJ_ATLAS_)[A-Z][A-Z0-9_]*=' 00_Prompt 02_Architecture`
  - `rg --pcre2 -n '\\$env:(?!KJ_ATLAS_)[A-Z][A-Z0-9_]*=' 00_Prompt 02_Architecture`
  - `rg -n "Runtime profile|KJ_ATLAS_ALLOW_JIT_PROVISIONING|enterprise-production" 02_Architecture`
- 期待結果:
  - 実行プロファイルと導線が確認できる。
  - 公開環境変数例は `KJ_ATLAS_` 接頭辞に揃う。

## 8) 代替案 / Alternatives considered

- 実装既定値を `false` に変更する:
  - 保留。導入互換性と本番安全性のトレードオフがあるため ADR 判断が必要。
- 04文書だけに profile を置く:
  - 却下。runtime registry が単一正本であり、04は運用説明として追随すべき。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: profile 表が実装値と乖離する。
- 影響範囲: runtime registry, deployment, enterprise architecture, configuration docs。
- ロールバック手順: profile guidance と導線追加を revert する。実装既定値は変更しない。

## 10) Additional context

- 本件で実装既定値を変更しないため、ADRは不要と判断する。
- 既定値変更、missing endpoint fail-fast化、または vendor env 完全排除を行う場合は別ADRを起票する。

## 11) Closeout

- Completed by: PR #2131 `[codex] Align 00 and 02 value documentation`
- Result: `runtime_parameter_registry.md` に `local-dev` / `evaluation` / `enterprise-production` の profile guidance を追加し、`deployment.md` と `enterprise_architecture.md` から導線を張った。
- Validation: `git diff --check`, active issue memo validator, validator unit tests, 非 `KJ_ATLAS_` 公開環境変数例の `rg` 確認。


## Stream D update (2026-05-20)

### Phase 1) Read同期

- `runtime_parameter_registry.md` をSSOTとして再読し、公開キー集合・既定値・profile差分を固定した。
- 関連issue（ENV-ARCH-01 / ENV-CONFIG-DRIFT-01 / ENV-PROFILE-01）の `Status / Priority / Dependencies / Related ADR` を同一セッションで再確認した。

### Phase 2) Context / Decision / Consequences

- Context: backendは `KJ_ATLAS_*` 単独契約で移行完了。deploy/frontendは公開契約と内部adapter境界の明文化が主課題。
- Decision: 公開契約は `KJ_ATLAS_*` のみを維持し、互換は private layer（third-party env / frontend shim）に閉じ込める。
- Consequences: 旧キー再導入や prefix例外は本streamで実施しない。必要時は新規ADRでGo/No-Goを先行確定する。

### Phase 3) グローバルprefix移行と互換レイヤ設計

- Public layer: 利用者入力は `KJ_ATLAS_*` のみ受理。
- Private layer: `POSTGRES_*` は third-party container内部名、`VITE_API_BASE` は非公開互換shimとして限定運用。
- Exit条件: 命名/既定値/境界/profile の4観点が同時に満たされること。

### Phase 4) Plan → Execute → Verify → Proceed

- Plan: 4観点ゲートを固定。
- Execute: 契約文書（02）→ issue運用（01）の順で同期。
- Verify: docs-check中心で差分検証し、実装契約との不整合がないことを確認。
- Proceed: 不整合なしのため継続可能。追加の実装変更は不要。

### Phase 5) 3回失敗で停止

- 本更新では Verify失敗 0回。
- 以後、同一論点で Verify が3回連続失敗した場合は Stop し、再開条件と要判断事項をissueに追記する。

## Stream F note (2026-05-20)

- Profile guidance の運用明確化として、`runtime_parameter_registry.md` に既定値/推奨値対比表を追加した。
- `configuration.md` と `security_operational_guidelines.md` の profile 節を同時同期し、`KJ_ATLAS_ALLOW_JIT_PROVISIONING` と `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE` の判断点を一致させた。
- 命名規約（`KJ_ATLAS_*`）・既定値・互換方針（旧キー再導入なし）に変更はない。
