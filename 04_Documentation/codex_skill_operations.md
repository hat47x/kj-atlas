# Codex Skill Operations

> Audience: 外部コントリビュータ（参照のみ）/ 内部運用担当者（正本利用）
> Purpose: 本文書を公開stubとして維持し、内部正本への導線を固定する。
> Outcome: 分類結果を **Move internal（運用正本は00_Prompt）** に固定し、公開境界の誤読を防ぐ。
> Public boundary: 公開文書は方針サマリと参照導線のみを保持し、内部手順・秘密情報・組織依存設定は保持しない。
> This document decides: 公開stubとして残す最小要素（分類結果、正本リンク、Go/No-Go、停止条件）。
> This document does not decide: skill詳細運用、内部監査詳細、環境固有の実行秘密、仕様の新規決定。
> Related: `00_Prompt/codex_gsd_skill_ops.md`, `00_Prompt/agent_handover.md`, `01_Plans/documentation_quality.md`

## 1. 分類結果（DOC-OPS-05-02）

- Classification: **Move internal**
- 公開配置方針: `04_Documentation/codex_skill_operations.md` は **stub（参照窓口）** としてのみ維持する。
- 内部正本: `00_Prompt/codex_gsd_skill_ops.md`
- 次アクション: 内部運用変更は `00_Prompt/codex_gsd_skill_ops.md` を更新し、本書はリンク整合のみ追随する。

## 2. 位置づけ（責務境界）

- skill は「実行補助」であり、仕様の正本ではありません。
- 仕様の正本は `00_Prompt` / `01_Plans` / `02_Architecture` です。
- 本書は「どう参照し、どう安全に運用するか」を定義します。

## 3. Go/No-Go gate（公開判定）

次を満たす場合のみ公開運用を Go とします。

1. Audience / decides / does not decide が明示されている。
2. 内部手順（秘密情報・組織依存設定）を本文に混在させていない。
3. SafeMode既定ON・share/export境界を後退させる記述がない。

未充足時は No-Go として内部文書側で修正してから再判定します。

## 4. 内部正本への導線

- 運用方針（詳細）: `00_Prompt/codex_gsd_skill_ops.md`
- タスク実行テンプレ / DoD: `00_Prompt/agent_handover.md`
- 公開品質ゲート: `01_Plans/documentation_quality.md`

## 5. 最小運用ルール

1. 作業開始前に `AGENTS.md` の Read Order を確認する。
2. docs-only タスクではコード変更を行わない。
3. 上流文書（00〜02）と矛盾が見つかった場合、実装を止めて論点化する。
4. Verify の自己修復は最大3回。3回超過は `StoppedForClarification`。

## 6. 環境依存手順の前提

skill導入/実行コマンドを使う場合は、前提条件を必ず明記します。

- Codex実行環境が利用可能であること。
- `$CODEX_HOME/skills` が参照可能であること。
- 組織ポリシー上、外部取得が許可されていること（必要時）。

> 環境が満たせない場合は、コマンド実行を省略し「未実施理由」を記録してください。

## 7. Verify

```bash
rg -n "Audience|This document decides|This document does not decide|Go/No-Go|SafeMode|StoppedForClarification" 04_Documentation/codex_skill_operations.md
git diff --check
```


## DOC-OPS user-requested serial execution（2026-04-22 / Issue 05-02）

### Phase 1 Read
- Phase開始時再Read: `04_Documentation/codex_skill_operations.md` と対応Issueを再読。

### Phase 2 Plan
- Phase開始時再Read: Audience/Purpose/Public boundary/decides節を再読。
- AC/DoD不足判定: 不足なし。公開stub運用を維持。

### Phase 3 Execute
- Phase開始時再Read: Go/No-Go節を再読。
- 実施: 本直列実行ログを追記（Classification=Move internal を維持）。

### Phase 4 Verify
- Phase開始時再Read: Verify節を再読。
- 実行: `rg -n "DOC-OPS user-requested serial execution|Phase 1 Read|Phase 2 Plan|Phase 3 Execute|Phase 4 Verify|Phase 5 Proceed" 04_Documentation/codex_skill_operations.md`。
- 自己修復回数: 0/3。

### Phase 5 Proceed
- 判定: **Ready**（内部正本導線を維持）。
