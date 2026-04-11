# Local LLM Operations Guide

> DOC-OPS-05 Classification: **Improve external**
> Audience: 外部運用者（閉域/企業）
> Goal: provider切替と安全運用の最小runbookを提供する。
> Non-goal: 組織固有の承認フロー、秘密情報、内部検討ログの公開。
> Public boundary: 公開可能な設定・確認手順のみを記載し、内部監査詳細は除外する。
> Outcome: provider切替、safeMode境界、最小監査確認を再現できる。
> Related: `02_Architecture/llm_provider_spec.md`, `02_Architecture/runtime_parameter_registry.md`, `01_Plans/documentation_quality.md`, `01_Plans/issues/issue-doc-ops-05-09-04doc-local-llm-ops-guide.md`

> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。

## 1. 運用モード

- Offline: `KJ_ATLAS_LLM_PROVIDER=none`（既定、外部送信なし）
- Intranet: `KJ_ATLAS_LLM_PROVIDER=local`（社内LLMのみ）
- Enterprise: local中心 + 必要時のみ人手承認で外部経路

## 2. 最小設定

```bash
export KJ_ATLAS_LLM_PROVIDER='none'   # default
# local利用時のみ
export KJ_ATLAS_LLM_PROVIDER='local'
export KJ_ATLAS_LOCAL_LLM_BASE_URL='http://localhost:8001'
export KJ_ATLAS_LOCAL_LLM_MODEL='local-model-name'
```

確認:

```bash
curl -fsS http://localhost:8000/healthz
```

## 3. SafeMode / review 境界

- SafeMode既定ONを維持する。
- 未レビュー本文の自動確定を許可しない。
- AI出力は提案として扱い、確定は人手レビューで実施する。

## 4. 最小監査チェック

以下を1セットとして記録する。

- query
- bundle
- proposal
- apply（dry-run推奨）

少なくとも `bundleHash` と `sourceBundleHash` を記録し、ログ欠落を成功扱いしない。

## 5. 障害時

- local provider 障害: 外部送信へ自動フォールバックしない。まず復旧または手動判断。
- 監査欠落: 失敗として扱い、再実行後に再判定。
- 安全境界違反: 出力公開を停止し、設定を是正してから再開。

## 6. Go/No-Go gate（公開判定）

公開「Go」は以下を満たす場合のみ:

1. Audience / Goal / Non-goal / Public boundary / Outcome / Related が明示されている。
2. SafeMode既定ON、未レビュー自動確定禁止が明記されている。
3. 内部専用情報（秘密値・社内限定URL・承認ログ）が含まれていない。

未充足時は「No-Go」として公開更新を停止する。
