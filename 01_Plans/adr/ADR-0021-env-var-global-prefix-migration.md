# ADR-0021: 環境変数のグローバルプレフィックス移行方針

- Status: Accepted
- Date: 2026-03-05
- Deciders: Project Maintainers
- Scope: `02_Architecture/`, `03_Implement/backend/`, `03_Implement/deploy/`, `04_Documentation/`

## Context

同一サーバ上で複数アプリが共存する運用では、`DATABASE_URL` や `API_KEY` のような一般名キーが他アプリと衝突し得る。

この衝突は次の実害を生む。

- 誤った環境値の注入（誤接続・誤送信・誤認可）
- デプロイ自動化時の変数上書き
- 運用監査時の識別困難（どのアプリの値か判別不能）

主要選択肢:

1. 段階移行（旧キー互換あり）
2. **一括移行（互換なし）**（採用）
3. 互換を無期限維持

## Decision

**全ランタイム環境変数は `KJ_ATLAS_*` のみを正規契約として受理する。**

### 長期的に維持する契約

1. 正規キーは `KJ_ATLAS_*` のみ受理する。
2. 旧キー（プレフィックスなし）は受理しない。
3. 新旧同時指定は不正設定として扱う。
4. 旧キー互換・警告・猶予期限（deprecation date）は採用しない。

### 非目標

- 互換期間の運用や旧キー延命のための暫定フラグ。
- プレフィックス方針以外の設定体系再設計。
- 既存安全契約（SafeMode優先、PII最小化、監査最小化）の変更。

## Consequences

期待効果:

- 設定契約の単純化（運用ミス余地の削減）。
- 旧キー由来の衝突リスクの排除。
- 参照ドキュメントの命名規約統一。

副作用/制約:

- 旧キー依存環境は起動失敗する。
- 設定変更は関連ドキュメント・実装・テストの同時更新を要する。

## Separation of concerns（ADRとIssueの役割分離）

- 本ADRは「長期的に維持する意思決定（What/Why）」のみを保持する。
- 実装順序、進捗、受入条件、具体タスク管理（How/When）は `ENV-ARCH-01` issue memo で管理する。
- 進捗状態・未完タスクは本ADRへ追記しない。

### ADRに書かない内容（Issueへ委譲）

- 実装チェックリスト（`[ ]` 形式の作業項目）
- 期日・担当者アサイン・進捗率
- テスト実行ログ、PR単位の作業メモ、日次の運用記録

## Traceability

- Policy SSOT: `02_Architecture/runtime_parameter_registry.md`
- Execution tracking: `01_Plans/issues/issue-ENV-ARCH-01-global-env-prefix-migration.md`
- Derived-from: `01_Plans/adr/ADR-0001-value-to-requirements.md`
