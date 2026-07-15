# 対外文書作成品質基準

- Classification: Move internal
- Status: Normative for public-document review
- Last verified: 2026-07-15 JST
- Upstream: `01_Plans/adr/ADR-0023-doc-ops-04-readability-baseline.md`, `01_Plans/adr/ADR-0024-doc-ops-04-quality-gates-boundary.md`
- Downstream: `04_Documentation/README.md`, public Gist / release review

## Audience

`04_Documentation/` の公開候補を作成・更新・レビューするMaintainer、Contributor、生成AIを対象とする。

## Goal

公開文書を、機密を含まず、初読で理解でき、操作を再現でき、上流正本へ辿れる状態に保つ。

## Non-goal

- `01_Plans/` や `02_Architecture/` の内部判断を公開本文へ複製すること。
- 文書reviewだけでruntime、security、E2Eの品質保証を代替すること。
- 主観的な文体や好みをmerge blockingにすること。
- 未実装・未承認の仕様を将来像の説明だけで確定扱いすること。

## Outcome

読者は公開文書だけで、対象読者、目的、前提、手順、期待結果、安全な停止方法、詳細正本への導線を判断できる。ReviewerはQG-1〜QG-6を順に判定し、Go / No-Goと根拠を再現できる。

## Normative priority

1. Security / SafeMode / share-export / import-sanitizeの上流正本。
2. ADR-0023のReadability Baseline。
3. ADR-0024のdocs-check境界。
4. 本書のQG-1〜QG-6と統一判定手順。
5. 推奨基準。

上位文書と衝突する場合は公開を止め、上流を先に直す。本書は内部品質基準であり、公開Gist本文へ含めない。

## Mandatory quality gates

### QG-1 公開安全性

- 鍵、token、個人情報、内部URL、顧客情報、private logを含めない。
- 個人環境の絶対path、一時file名、社内channel名、未公開障害memoを残さない。
- 内部issue、作業進捗、承認待ち、AIの推測を利用者向けの確定事実として書かない。
- screenshot、diagnostics、sample exportも本文と同じ公開安全性で確認する。
- SafeModeやredactionで除外される内容を、例示や画像の都合で復元しない。

### QG-2 文書メタ

大幅改訂または新規文書は、冒頭付近から次を判別できるようにする。

- Audience
- Goal
- Non-goal
- Outcome
- 必要なUpstream / Related導線

見出し名は文書の読みやすさに合わせて言い換えてよいが、意味を欠落させない。

### QG-3 単体読解性

- 1〜3文の導入要約を置く。
- 前提条件、適用範囲、対象versionまたは確認日を必要に応じて示す。
- 手順、rule、判断基準のいずれかを明示する。
- 略語やproject固有語は初出で説明するか、最小用語集へリンクする。
- 内部directory構造を知らない利用者にも意味が通る表現にする。

### QG-4 再現可能性

操作やcommandを含む文書は次を満たす。

- commandはcopy可能なcode blockにする。
- 実行directory、依存、必要な環境変数を明記する。
- 期待結果または確認方法を最低1つ示す。
- 失敗時の停止条件、dataを壊さない回復方法、再開地点を示す。
- 実行できない検証は、理由・代替確認・再開条件を記録する。

### QG-5 正本導線と境界

- 設計値はADR / Architecture、runtime値はparameter registry、実装事実は対象source / testを参照する。
- `04_Documentation/` は利用・運用の説明に留め、上流契約を再定義しない。
- 現行手順と形成履歴、利用者向け説明と開発者向け検証を混在させない。
- Superseded文書は短い案内だけを残し、反対の規範や古いcommandを保持しない。
- Link先が存在し、公開bundleへ含まれない内部linkは読者に必須の手順にしない。

### QG-6 検証記録

公開またはrelease前に、最低限次をPR本文、release checklist、または同等の監査可能な場所へ記録する。

1. Markdown表示と見出し構造。
2. 相対linkと画像参照。
3. command / code blockの目視または実行結果。
4. 公開不可情報がないこと。
5. Go / No-Go、未実施項目、再開条件。

UI catalogやscreenshotを更新する場合は、source revision、確認日、locale、provider、SafeMode、fixture、viewport、capture方法、目視結果も記録する。

## Public boundary

分類の正本は `04_Documentation/README.md` とし、公開時点で同期する。

| Classification | Examples | Rule |
|---|---|---|
| Public entry | `04_Documentation/public_index.md` | 外部共有の先頭。管理情報を含めない |
| Public user / operator docs | `getting_started.md`, `installation.md`, `configuration.md`, `data_handling.md`, `operations.md`, `security.md`, `acceptance_check.md`, `ui_catalog.md`, `diagnostics.md`, `narratives.md`, `external_agent_workflow.md` | QG-1〜QG-6必須。実装済み事実と安全境界に限定 |
| Documentation maintainer | `04_Documentation/README.md`, `release.md` | 公開準備用。Gist本文には原則含めない |
| Developer / AI operations | `03_Implement/frontend/docs/e2e_testing.md`, `04_Documentation/codex_skill_operations.md`, E2E log | 一般利用者向けbundleへ含めない |
| Internal decisions | `00_Prompt/`, `01_Plans/`, `02_Architecture/` | 利用者に必要な確定事実だけを04へ要約する |

`04_Documentation/e2e_testing.md` はSuperseded案内であり、E2E実務手順の正本ではない。

## Check applicability

| Changed surface | Required review | Current automation boundary |
|---|---|---|
| Public `04_Documentation/*.md` | QG-1〜QG-6、link、公開境界 | ADR-0024 Boundary-1。release blocking |
| `01_Plans/adr/*.md` / `issues/*.md` / dashboard | 必須meta、Status、traceability、current/history | ADR-0024 Boundary-1。issue validator / triageを使用 |
| Root OSS docs | 公開安全性、入口整合、link | 変更scopeに応じたdocs-check |
| Current `02_Architecture/*.md` | 契約SSOT、同名型、history分離 | 統合checkerは `DX-DOC-02` で未実装。手動照合を省略しない |
| Developer docs under `03_Implement/` | 実行commandと実装の一致 | 対象subsystemのtestと併用 |

自動checkが未実装の行を「適用外」とみなさない。現行は手動証拠を残し、`DX-DOC-02` の導入後に同じrule IDへ移行する。

## Unified review procedure

### 1. Scope

- 公開対象と除外対象を列挙する。
- 変更がDocsだけか、runtime / schema / securityへ波及するかを確認する。
- 公開bundleの入口を `public_index.md` に固定する。

### 2. Gate review

QG-1からQG-6まで順番に `Pass / Fail / N/A` を判定する。N/Aには理由を書く。QG-1、QG-5、安全不変条件は、対象に関係する限りN/Aにしない。

### 3. Mechanical checks

最低限、変更scopeに応じて次を実行する。

```bash
python 01_Plans/issues/validate_active_issue_memos.py
python 01_Plans/triage_actionable_plans.py
git diff --check
```

相対link、画像、command、対象subsystemのtestは変更内容に応じて追加する。

### 4. Decision

- **Go**: Mandatory gateが全てPassし、必要検証が成功し、未実施項目がrelease blockerでない。
- **No-Go**: Mandatory gateが1つでもFail、公開境界が不明、安全正本と矛盾、必要検証が未実施。

### 5. Record

次を1つの記録へ残す。

```text
Docs quality decision: Go | No-Go
Scope:
Source revision / verified date:
QG-1..QG-6:
Commands and results:
Visual review:
Not executed and reason:
Resume condition:
Reviewer:
```

## Definition of Done

- QG-1〜QG-6の結果を記録した。
- Audience / Goal / Non-goal / Outcomeと正本導線が読める。
- link、画像、command、Markdown体裁を変更scopeに応じて確認した。
- 公開対象外の管理情報、履歴log、未承認方針が混入していない。
- SafeMode、share/export、provider=none、proposal-only、人手reviewの説明が後退していない。
- 未実施検証には理由と再開条件があり、必要ならNo-Goを維持した。

## Fail-safe and recovery

次のいずれかで即No-Goとする。

- 機密または個人情報の混入が疑われる。
- 上位正本との未定義競合、用語衝突、契約値の異義定義がある。
- 公開対象と内部対象を判別できない。
- 必須link、fixture、source revision、検証環境を特定できない。
- self-correctionが3回を超えても収束しない。

停止時は公開物を更新せず、失敗したQG、影響範囲、暫定回避、再開条件をissue memoへ記録する。安全境界を緩めてGoにしない。

## Recommended practices

- 長い手順は「準備 / 実行 / 確認 / 回復」に分ける。
- sample値は `<doc_id>`、`change-me` など本番値と区別する。
- 図表には代替textまたは本文要約を付ける。
- 同じ事実を複数文書へ複製せず、正本と利用者向け要約を分ける。
- screenshotは決定的fixtureから再生成し、古くなる条件をledgerへ書く。

## History policy

過去のStream実行ログ、自己修復cycle、旧判定件数はgit履歴へ委譲し、本書のNormative手順へ再掲しない。gitだけでは失われる一次証拠をarchiveする場合は、`Informative`、対象期間、Retention reason、本書への逆linkを必須とする。
