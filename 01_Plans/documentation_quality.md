# 対外文書作成品質基準（内部運用 / AIエージェント向け）

> Classification: **Move internal**（内部運用文書として維持）
> Public boundary: 本書は公開本文ではなく、`04_Documentation/*` の公開判定基準のみを扱う。組織固有の承認記録・機密情報は扱わない。
> Go/No-Go: QG-1〜QG-6 と章16の統一判定手順を満たす場合のみ Go。未充足は No-Go。

このドキュメントは、AIエージェントやメンテナが **対外公開するユーザ/開発者向け技術文書** を作成・更新する際の、内部向け品質管理基準を定義します。公開文書そのものではなく、`01_Plans/` に置く内部運用ルールとして扱います。

## 0. 文書の位置づけ（Normative / Informative）

- 本書は **内部品質基準（Normative）** であり、公開用ガイド本文ではありません。
- `04_Documentation/` は外部読者向け本文、`01_Plans/documentation_quality.md` はその公開前判定基準です。
- 本書内の規定のうち、章 `5. 最低限の公開品質基準（Mandatory）`、`7. Gist リリース判定チェックリスト`、`8. 配置境界`、`16. 統一判定手順（AC/DoD・レビュー・停止条件）` を **優先適用** します。
- Stream別の実行ログや履歴セクションは監査のための **Informative（参考記録）** であり、Normative規定と矛盾する場合は Normative を優先します。

## 1. Audience

- 外部ユーザ
- 外部開発者
- 初見の運用担当者

## 2. Goal

- `04_Documentation/` に置く公開候補文書を、**公開しても安全で、初読でも追従でき、手順として再現可能** な状態で保つ。
- Gist へ切り出したときでも、文書単体で最低限の文脈を維持できるようにする。

## 3. Non-goal

- 社内限定Runbookや未確定メモの公開。
- `01_Plans/` や `02_Architecture/` の全内容を `04_Documentation/` に複製すること。
- 実装やCIの全品質保証を文書だけで代替すること。

## 4. Outcome

読者は、対象文書を読んだだけで次を判断できる状態を目標とします。

1. **誰向けの文書か**。
2. **何ができる/わかるようになるか**。
3. **前提条件と手順**。
4. **成功時の期待結果**。
5. **詳細な正本や関連資料の参照先**。

## 5. 最低限の公開品質基準（Mandatory）

Gist や公開配布物へ出す `04_Documentation/*.md` は、少なくとも次を満たしてください。

### QG-1 公開安全性

- 機密情報（鍵、トークン、個人情報、内部URL、未公開顧客情報）を含めない。
- 一時ファイル名、個人環境依存パス、社内固有チャネル名、未公開障害メモを残さない。
- 内部判断中の仮説や未承認方針は、公開文書へ既成事実として書かない。

### QG-2 文書メタの明示

文書冒頭または冒頭近辺で、最低限次を読者が判別できるようにする。

- 対象読者（Audience）
- 文書の目的（Goal）
- 範囲外（Non-goal）
- 読後の到達状態（Outcome）

ADR-0023 の RBL-1〜RBL-4 を `04_Documentation/` 向けに具体化した基準とみなします。

### QG-3 単体読解性

Gist 単体で読まれても理解できるよう、最低限次を含めます。

- 1〜3文の導入要約
- 前提条件または適用範囲
- 手順・ルール・判断基準のいずれか
- 必要に応じた用語補足（略語初出展開など）

### QG-4 再現可能性

コマンドや操作手順を書く場合、次を満たします。

- コピー可能なコードブロックで示す
- 実行ディレクトリや前提依存を明記する
- 成功時の期待結果、または確認方法を最低1つ示す
- 実行不能な場合は代替手段または制約理由を書く

### QG-5 正本導線

- 上流の正本（ADR / Architecture / runtime parameter registry 等）を必要に応じてリンクする。
- `04_Documentation/` 側では「利用・運用のための説明」に留め、設計の正本を勝手に上書きしない。
- 実装依存の説明は、必要に応じて関連する `03_Implement/` の場所を参照できるようにする。

### QG-6 公開品質チェック記録

Gist リリース前に、少なくとも次を記録する。

1. Markdown 表示崩れがないことの確認
2. リンク切れの簡易確認
3. コードブロック/コマンドの目視確認
4. 公開不可情報が混入していないことの確認

記録は PR本文、release checklist、または同等の監査可能な場所に残す。

## 6. 推奨基準（Warning）

必須ではないが、公開品質を安定させるため次を推奨します。

- 図や表を使う場合は、代替テキストまたは要点説明を併記する。
- 長い手順は「準備 / 実行 / 確認 / トラブルシュート」に分割する。
- 1文を過度に長くしない。箇条書きで判断条件を分離する。
- サンプル値と本番値を見分けられるようにする（例: `change-me`, `<doc_id>`）。
- 文書末尾に関連資料（Related）をまとめる。

## 7. Gist リリース判定チェックリスト

`04_Documentation/` を Gist へ出す前に、以下を順に確認します。

1. **Scope確認**: 今回公開する文書が `04_Documentation/` のみで完結している。
2. **公開安全性確認**: QG-1 を満たす。
3. **可読性確認**: QG-2 / QG-3 を満たす。
4. **再現性確認**: 手順がある文書は QG-4 を満たす。
5. **正本導線確認**: QG-5 を満たす。
6. **記録確認**: QG-6 の結果を残す。

いずれかが未充足なら、Gist 公開は **見送り** にします。

## 8. 配置境界

- `01_Plans/` は内部判断・計画の正本であり、公開Gistの主対象にしない。
- `02_Architecture/` は設計の正本であり、公開文書は必要な範囲だけ参照する。
- 本基準自体は内部文書のため `01_Plans/` に置き、`04_Documentation/` へは配置しない。
- `04_Documentation/` は外部読者向けに編集し、内部検討メモを混在させない。


## 8.1 公開境界分類（DOC-PUBLIC）

| 区分 | 主な文書 | 品質判定 |
| --- | --- | --- |
| 一般利用者向け公開 | `04_Documentation/public_index.md`, `installation.md`, `configuration.md`, `data_handling.md`, `operations.md`, `security.md`, `security_operational_guidelines.md`, `acceptance_check.md`, `diagnostics.md`, `canonicalization.md`, `ce2_low_risk_ai_assist.md`, `local_llm_ops_guide.md`, `narratives.md` | QG-1〜QG-6 を満たし、実装済み事実と安全境界だけを書く |
| 04文書保守者向け | `04_Documentation/README.md`, `04_Documentation/release.md` | 公開準備・除外方針・リリース確認を扱い、Gist本文には原則含めない |
| 開発者/AI運用向け | `04_Documentation/codex_skill_operations.md`, `04_Documentation/e2e_verification_log_2026-03-03.md`, `03_Implement/frontend/docs/e2e_testing.md` | 一般利用者向け公開入口から直接誘導しない。必要な場合は開発者向け入口から参照する |
| 内部計画/判断ログ | `00_Prompt/`, `01_Plans/`, `02_Architecture/` | 公開文書へ混ぜず、利用者に必要な確定済み事実だけを04文書へ要約する |

公開利用ガイドへ出す前に、SafeMode既定ON、share/export前確認、未レビュー本文・AI提案の人間レビュー、external provider/escalation既定OFFの説明が後退していないことを確認する。

## 9. AIエージェント運用メモ

- 本基準は **公開文書の本文ではなく、公開前レビューの内部チェックリスト** として使う。
- `04_Documentation/` の文書を更新したPRでは、必要に応じて本基準の QG-1〜QG-6 を PR本文または検証ログへ転記する。
- 対外文書に内部判断途中の論点が残る場合は、公開改善ではなく `01_Plans/` / `02_Architecture/` への移設を優先する。

## 10. 関連文書

- `01_Plans/adr/ADR-0023-doc-ops-04-readability-baseline.md`
- `01_Plans/adr/ADR-0024-doc-ops-04-quality-gates-boundary.md`
- `04_Documentation/release.md`
- `02_Architecture/runtime_parameter_registry.md`

## 11. Doc-Ops-05 Set 2 統合品質ゲート（Phase 1〜6）

次の文書を同時更新する場合、以下の6フェーズを固定順序で適用する。

- `04_Documentation/diagnostics.md`
- `04_Documentation/narratives.md`
- `04_Documentation/codex_skill_operations.md`
- `01_Plans/documentation_quality.md`（本書）

### Phase 1: Scope固定

- 変更対象を上記4ファイルに限定する。
- Docs-only 原則を維持し、`03_Implement/` の変更を行わない。

### Phase 2: メタ要件確認

- 対外文書（04層）に Audience / Goal / Non-goal / Public boundary / Outcome / Related が明示されていることを確認する。
- 内部文書（01層）は品質判定基準と運用責務が追跡可能であることを確認する。

### Phase 3: 用語統一

- review状態は `reviewed / unreviewed` を正規語彙とし、`reviewed=true/false` は互換注記に限定する。
- 安全境界は `SafeMode` / `share/export` の表記に統一する。

### Phase 4: 相互リンク確認

- 04層文書から本書（`01_Plans/documentation_quality.md`）への導線を持つ。
- narratives は `00_Prompt/domain.md` / `02_Architecture/schemas.md` を参照する。
- diagnostics は worker 実装パスおよび関連契約への参照を維持する。
- codex skill 運用文書は `00_Prompt/codex_gsd_skill_ops.md` への導線を維持する。

### Phase 5: 検証・記録

- Markdown表示崩れ、リンク切れ、コマンドブロック、公開不可情報混入を確認し、実行/確認ログを残す。
- 可能な場合は docs-check コマンドを実行し、結果を記録する。

### Phase 6: Go/No-Go 判定

- QG-1〜QG-6 と本セクション Phase 1〜5 がすべて満たされれば Go。
- いずれか未充足なら No-Go として公開/統合を停止し、欠落点を列挙する。

### 修復ポリシー（必須）

- 品質ゲート失敗時は **最大3回まで修復して再判定** する。
- 3回を超える場合は作業を停止し、`01_Plans/issues/` にブロッカーを記録して人間判断へエスカレーションする。

## 12. DOC-OPS-05 Stream I 運用固定（non-conflict docs）

Stream I では対象Issueで明示された文書のみを編集対象とする。既定では Stream H 専有（operations / security）は編集しない。利用者向けの `acceptance_check.md` と開発者向けの `03_Implement/frontend/docs/e2e_testing.md` は、対象Issueで明示された場合のみ例外的に編集可能とする。

- `04_Documentation/canonicalization.md`
- `04_Documentation/codex_skill_operations.md`
- `04_Documentation/configuration.md`
- `04_Documentation/diagnostics.md`
- `04_Documentation/installation.md`
- `04_Documentation/local_llm_ops_guide.md`
- `04_Documentation/narratives.md`
- `04_Documentation/release.md`
- `04_Documentation/e2e_verification_log_2026-03-03.md`

### Stream I Phase運用（固定順序）

1. Phase 1 Read
2. Phase 2 Plan（品質ゲート宣言）
3. Phase 3 Execute（局所更新）
4. Phase 4 Verify（リンク/語彙/整形）
5. Phase 5 Proceed（残課題明示）

### AC/DoD不足時の扱い

- AC/DoDに不足がある場合は、実編集前に「ドラフト提案」を issue 本文へ追記して合意扱いにする。
- 合意前提が崩れた場合は Execute を止め、論点を `01_Plans/issues/` に分離する。

### 自己修復上限

- Verify失敗時の自己修復は最大3回まで。
- 4回目相当は停止し、ブロッカーとして記録して Proceed を保留化する。


## 13. 共通ワークフローとフェイルセーフ（統一運用）

対象文書（`diagnostics.md` / `acceptance_check.md` / `03_Implement/frontend/docs/e2e_testing.md` / `e2e_verification_log_2026-03-03.md` / `codex_skill_operations.md` / 本書）は、同一の5Phaseワークフロー（Read→Plan→Execute→Verify→Proceed）を適用する。

- Verify 失敗時の自己修復は最大3回まで。
- 4回目相当は停止し、`01_Plans/issues/` にブロッカーを記録して人間判断へエスカレーションする。
- Stream G フェイルセーフ: テスト方針矛盾または監査要件未達を検知した場合は Execute を停止し、Proceed で残課題を明示する。

## 14. DOC-OPS-05 Stream H Draft群整理プロトコル（01〜14）

本節は `issue-doc-ops-05-01` 〜 `issue-doc-ops-05-14` の Draft整理に適用する固定プロトコル。

### Phase 1 Read（14 Draftの共通テンプレ差分抽出）

- 共通テンプレ（Requirement meta I/F / Acceptance criteria / Validation plan / Authoring Checklist）の有無を確認する。
- 差分は `Scope` / `Related ADR/Spec` / `推奨アクション` / `SecurityGateImpact` に限定して抽出する。

### Phase 2 ADR CDC必要性判定

- 既存ADR/Specへの参照で根拠追跡が可能な場合は **追加ADRを作成しない**。
- 追加ADRが必要になる条件（例: 仕様境界の新規導入、既存正本の衝突）がある場合のみ CDC を ADR化する。

### Phase 3 Plan（優先順）

1. 分類決定（Move internal / Improve external）の固定。
2. 公開境界（Audience / Goal / Non-goal / Public boundary / Outcome / Related）の検証。
3. docs-check 実行と修復計画（最大3回）の確定。

### Phase 4 Execute（文書配置見直し）

- Move internal: 公開文書を最小スタブ化し、内部正本への導線を残す。
- Improve external: 公開文書としての単体読解性と再現可能性を改善する。
- いずれも docs-only で実施し、`03_Implement/**` は変更しない。

### Phase 5 Verify（リンク・見出し・品質ゲート）

- 見出し整合、内部リンク、有効なRelated参照、QG-1〜QG-6 を確認する。
- 失敗時は **最大3回まで修復**。4回目相当は停止し、`01_Plans/issues/` にブロッカーを記録して人間判断へ移行する。

## DOC-OPS-05 追加実行記録（2026-04-16 / Target 05-01..05）

### Phase 1 Read（再Read）
- 本書と関連Issueを再Readし、公開境界とdocs-onlyスコープを確認。

### Phase 2 Plan（再Read）
- 5Phase（Read→Plan→Execute→Verify→Proceed）で進行し、対象外文書へは非接触とする。

### Phase 3 Execute（再Read）
- 本書の既存分類・公開境界メタを維持しつつ、05-01..05セットの実行記録を追記。

### Phase 4 Verify（再Read）

## 15. DQ-CONTRACT-v1（Stream F: Quality/E2E/Diagnostics）

本契約は Stream F（Quality/E2E/Diagnostics docs）が `01_Plans/documentation_quality.md` / `04_Documentation/acceptance_check.md` / `03_Implement/frontend/docs/e2e_testing.md` / `04_Documentation/e2e_verification_log_2026-03-03.md` / `04_Documentation/diagnostics.md` を直列フェーズで更新する際の、**最小品質判定I/F** を定義する。

### 15.1 Contract scope（固定）

- 編集許可対象は上記4ファイルのみ。
- docs-only を維持し、`03_Implement/**` を変更しない。
- 上流正本（ADR/Architecture）との矛盾を検知した場合は、下流文書の独断更新を停止する。

### 15.2 品質判定軸（DQ-A1〜A6）

- **DQ-A1: Meta completeness**
  Audience / Goal / Non-goal / Public boundary / Outcome / Related を読者が判別できる。
- **DQ-A2: Reproducibility**
  docs-checkコマンド（`rg` / `git diff --check` / 必要時validator）が再実行可能な形で記録される。
- **DQ-A3: Cross-link integrity**
  `documentation_quality.md` ↔ `acceptance_check.md` ↔ `03_Implement/frontend/docs/e2e_testing.md` ↔ `e2e_verification_log_2026-03-03.md` ↔ `diagnostics.md` の参照導線が維持される。
- **DQ-A4: Safety boundary**
  SafeMode既定ON・share/export漏えい防止を後退させる記述を追加しない。
- **DQ-A5: Terminology consistency**
  review語彙は `reviewed / unreviewed` を正とし、他表現は互換注記に限定する。
- **DQ-A6: Fail-safe discipline**
  Verify失敗時は最大3回まで自己修復し、4回目相当は Stop として Proceedを保留化する。

### 15.3 Go/No-Go 判定

- **Go**: DQ-A1〜A6 をすべて満たし、docs-checkが成功。
- **No-Go**: いずれか1つでも未充足。未充足項目と再開条件を verification log に記録する。

### 15.4 Stopper（強制停止条件）

- 承認前の規約確定禁止: 本契約を上位正本（ADR/Architecture）へ昇格する変更は行わない。
- 競合・前提崩壊（上位文書との矛盾、定義済み語彙の衝突）を検知した場合は即停止する。
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 01_Plans/documentation_quality.md 01_Plans/documentation_quality.md`
- `git diff --check`
- 修復は最大3回まで。3回超過は停止（Hold）。

### Phase 5 Proceed（再Read）
- 判定: **Ready**
- 次アクション: 同一セット内Issue本文とScope本文の整合を維持して進行。

## DOC-OPS-05 Stream J2 execution record (2026-04-18)

### Phase 1: Read
- Target issue scope and this document were re-read to confirm Audience / Goal / Public boundary.
- Classification remains **Move internal** and no Stream H-owned file edits are required.

### Phase 2: ADR CDC
- CDC update is **not required** because the existing placement policy is within current DOC-OPS-05 decisions.

### Phase 3: Plan
- AC/DoD補足: 分類根拠（Audience/Goal/公開境界）・次アクション・検証一致（docs-check）を1セットで記録する。
- 次アクション固定: 内部品質基準として01_Plans配置を維持し、04_Documentationへの再配置は行わない。

### Phase 4: Execute
- docs-onlyで本ファイルのみを更新し、実装仕様変更は行わない。

### Phase 5: Verify
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|DOC-OPS-05 Stream J2" 01_Plans/documentation_quality.md`
- `git diff --check`
- Self-correction policy: max 3 attempts, then stop and reassign if unresolved.

### Phase 6: Proceed
- 判定: **Ready**
- 根拠: 分類根拠・次アクション・検証一致を同一文書内で追跡可能。

## 15. Stream I mid-1 execution record（2026-04-19, DOC-OPS-05-05）

### Phase 1 Read（対象再読）
- 本文と対応Issue（DOC-OPS-05-05）を再読し、内部品質基準文書としての境界を再確認。

### Phase 2 ADR CDC（対象再読）
- Context: 本書は公開手順ではなく、公開判定を行うための内部品質基準である。
- Decision: 本書の分類は **Move internal** 相当の内部正本として固定し、公開文書からは参照導線で利用する。
- Consequences: 対外手順本文への直接混入を防ぎ、判定基準の重複記述を抑制する。

### Phase 3 Plan（対象再読）
- AC: QG-1〜QG-6 と DOC-OPS-05 のメタ項目が追跡できること。
- DoD: 6Phase運用と自己修復上限（3回）を継続適用すること。

### Phase 4 Execute（対象再読）
- 本節を追記し、Stream I mid-1 の運用固定を明文化。

### Phase 5 Verify（対象再読）
- `rg -n "Stream I mid-1|Phase 1 Read|Phase 2 ADR CDC|Phase 6 Proceed" 01_Plans/documentation_quality.md`
- `git diff --check`

### Phase 6 Proceed（対象再読）
- 判定: **Ready**（内部品質基準としての役割を維持）。


## Stream H serial cycle（2026-04-19 / DOC-OPS-05-05）

### Phase 1 Read（参照整合）
- 対象Issueと本文を照合し、Classification=Move internal (01_Plans internal policy) と公開境界（Audience / Goal / Non-goal / Outcome / Related）の整合を確認。
- 重複・矛盾は既存本文へ統合し、新規仕様追加は行わない。

### Phase 2 Plan（AC/DoDドラフト）
- AC: 公開境界メタの維持、Issue分類との一致、docs-onlyスコープ維持。
- DoD: Read→Plan→Execute→Verify→Proceed を記録し、検証コマンドを再現可能に残す。

### Phase 3 Execute（本文更新）
- 本節を追記し、Stream H の担当範囲であることを明示。
- 編集範囲は本ファイルのみとし、他ストリーム対象ファイルは非変更。

### Phase 4 Verify（docs-check + 参照リンク）
- `rg -n "Audience|Goal|Non-goal|Outcome|Related|Go/No-Go|Stream H serial cycle" 01_Plans/documentation_quality.md`
- `git diff --check`
- 参照リンクは `Related` に記載された正本/Issue導線が有効であることを目視確認。

### Phase 5 Proceed/Stop
- 判定: **Ready**
- 停止条件: Verify自己修復が3回を超過、または未定義競合（要件キー未定義/契約衝突）を検知した場合は **Stop** とし、`01_Plans/issues/` に保留論点を記録する。


## DOC-OPS-05-05 serial run log（2026-04-19）

### Phase 1 Read
- Read対象: `01_Plans/documentation_quality.md` と対応Issue `01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`。
- 公開境界/内部境界と `VerificationLevel=docs-check` を再確認。

### Phase 2 Plan
- 本ファイルは docs-only で局所更新し、対象外（05-06以降・共有統合3ファイル・コード）へ非接触。

### Phase 3 Execute
- 既存分類 `Internal quality standard` と Audience/Goal/Non-goal/Public boundary/Outcome/Related を維持したまま、2026-04-19 実行ログを追記。

### Phase 4 Verify
- `rg -n "DOC-OPS-05-05 serial run log|Phase 1 Read|Phase 2 Plan|Phase 3 Execute|Phase 4 Verify|Phase 5 Proceed" 01_Plans/documentation_quality.md 01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`
- `git diff --check`

### Phase 5 Proceed
- 状態: **Ready**
- 次アクション: 本セット（05-01..05）内での整合維持を継続。

## Stream D execution log（2026-04-20 / DOC-OPS-05-05）

### Phase 1 Read
- 対象: `01_Plans/documentation_quality.md` と対応Issueの Requirement meta I/F を再読し、docs-only 境界を確認。
- 判定: Classification=`Internal standard` を維持し、編集禁止範囲（README / dashboard / decision-pack / 実装コード）へ非接触。

### Phase 2 Plan（AC/DoD不足補完）
- AC補完: Audience / Goal / Non-goal / Public boundary / Outcome / Related と Go/No-Go 判定導線が追跡可能であること。
- DoD補完: Read → Plan → Execute → Verify → Proceed の5Phase記録を残し、Verifyは docs-check 手順を明示すること。

### Phase 3 Execute
- 既存の分類方針と公開境界メタを維持し、DOC-OPS-05前半（01〜05）の同期記録を本節へ追加。
- 非目標を維持し、仕様正本（00〜02）の上書き・実装変更は行わない。

### Phase 4 Verify（docs-check）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Stream D execution log" 01_Plans/documentation_quality.md 01_Plans/documentation_quality.md`
- `git diff --check`
- 失敗時は自己修復を最大3回まで。4回目相当は停止して Hold とする。

### Phase 5 Proceed（残課題記録）
- 状態: **Ready**
- 残課題: DOC-OPS-05後半対象文書にも同一の5Phase運用と自己修復上限3回を適用する。


## 16. 統一判定手順（AC/DoD・レビュー・停止条件）

本章は、公開前レビュー時に参照する **最小手順の正本** です。

### 16.1 AC（Acceptance Criteria）

- AC-1: 対象が `04_Documentation/` の外部向け文書であることを確認し、本書自体は内部基準として扱う。
- AC-2: QG-1〜QG-6 の必須項目がすべて判定可能である。
- AC-3: 文書メタ（Audience / Goal / Non-goal / Outcome）と正本導線（QG-5）が追跡可能である。
- AC-4: 公開境界（内部判断・未承認方針・機密情報の除外）が保たれている。

### 16.2 DoD（Definition of Done）

- DoD-1: 判定結果（Go / No-Go）と根拠（どのQGを満たしたか）を監査可能な場所に記録した。
- DoD-2: `git diff --check` により体裁崩れがないことを確認した。
- DoD-3: 未充足項目がある場合、公開を停止し、再開条件を明記した。

### 16.3 レビュー手順（固定順序）

1. Scope確認（内部基準と外部本文の境界確認）
2. QG-1〜QG-6 判定
3. Go/No-Go 決定
4. 判定記録の保存

### 16.4 停止条件（Fail-safe）

次のいずれかを検知した場合は **即停止（No-Go）** とします。

- self-correction が3回を超過した場合
- 未定義競合（上位正本と矛盾する規約追加、定義語彙衝突）
- 前提崩壊（適用範囲や公開境界が判定不能）

停止時は、未充足項目と再開条件を記録し、人間判断へエスカレーションします。

## 17. DOC-OPS Track 4 sync baseline（2026-04-22）

- 対象順序は `05-05 → 05-11 → 05-13 → 05-14` で固定する。
- 各Phase開始時に Read同期（AGENTS / 対象Issue / 対象文書）を行う。
- ADRタスクは **Context / Decision / Consequences を先に明文化し、DecisionStatus承認確認後に Execute** する。
- Verify失敗時は自己修復を最大3回までとし、4回目相当は停止（Hold / StoppedForClarification）。
- 同期必須観点: 用語（Security Officer / System Owner / Platform Operator）、役割（2者承認+実行責務分離）、導線（architecture→security→guidelines→e2e + operations照合）、固定値（D1〜D4）。

## 18. DOC-OPS Track 4 follow-up cycle（2026-04-22 / 05-05 ownership）

### Phase 1 Read（再同期）
- `AGENTS.md` / `01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md` / 本書を再読し、`Move internal` の分類を維持。
- docs-only / 指定外ファイル非編集 / 自己修復上限3回を再確認。

### Phase 2 Plan（判定境界固定）
- Plan-1: QG-1〜QG-6 を公開前判定の最小I/Fとして維持。
- Plan-2: `04_Documentation/*`（外部本文）と `01_Plans/*`（内部判定基準）の責務境界を維持。
- Plan-3: Verifyは docs-check（`rg` + `git diff --check`）で再現可能に記録する。

### Phase 3 Execute
- Track 4 follow-up の5Phase記録を追記し、内部基準正本としての運用境界を明文化。

### Phase 4 Verify
- `rg -n "DOC-OPS Track 4 follow-up cycle|Phase 1 Read|Phase 2 Plan|Phase 3 Execute|Phase 4 Verify|Phase 5 Proceed" 01_Plans/documentation_quality.md`
- `git diff --check`

### Phase 5 Proceed
- 判定: **Ready**
- フェイルセーフ: Verify失敗時の自己修復は最大3回。超過時は **Hold** として停止。


## 19. Stream K serial completion record（2026-04-26）

### Phase 1 Read
- 本書と `issue-doc-ops-05-05-04doc-documentation-quality.md` を再読し、Move internal分類とdocs-check要件を確認。

### Phase 2 ADR/CDC
- Context: 本書は内部Normative基準。
- Decision: 公開本文へ複製せず、公開判定基準として維持。
- Consequences: 公開境界と判定責務を一意に追跡できる。

### Phase 3 Plan
- AC/DoD不足を補完し、Classification/Public boundary/Go-NoGoを冒頭で読める状態にする。

### Phase 4 Execute
- 冒頭メタと本節をdocs-only最小差分で追記。

### Phase 5 Verify
- `rg -n "Classification|Public boundary|Go/No-Go|QG-1|QG-6" 01_Plans/documentation_quality.md`
- `git diff --check`

### Phase 6 Proceed
- 判定: **Ready**（自己修復0/3）。

## Stream H Open化準備 run（2026-04-28）

### Phase 1 Read（issue + 対応docペア確認）
- 対応Issueと対象文書のペアを再読し、公開境界・分類・停止条件の整合を確認。

### Phase 2 Plan（Draft→Openゲート明文化）
- Open化ゲートを次の4点で固定。
  1. 必須メタ（Audience/Goal/Non-goal/Public boundary/Outcome または Requirement meta I/F）が追跡可能。
  2. AC/DoD/Validationが docs-check 前提で再現可能。
  3. 未承認事項の確定化を行わない（DecisionStatus=Fixed の範囲外は承認待ち）。
  4. self-repair は最大3回、4回目相当で停止。

### Phase 3 Execute（不足メタ/AC/Validation/Stop条件補完）
- 本セクションを追記し、Open化判定に必要な最小メタ（ゲート、検証、停止条件、Proceed判定）を明示。

### Phase 4 Verify（ゲート到達判定 + docs-check）
- `python3 01_Plans/issues/validate_active_issue_memos.py`
- `rg -n "Stream H Open化準備 run（2026-04-28）|Phase 1 Read|Phase 2 Plan|Phase 3 Execute|Phase 4 Verify|Phase 5 Proceed|Open化可否" 01_Plans/documentation_quality.md`
- `git diff --check`
- self-repair: 0/3（4回目相当は停止）。

### Phase 5 Proceed（Open化可否）
- Open化可否: **Yes**。
- 判定理由: Draft→Openの最小ゲート（メタ、AC/DoD、検証、停止条件）を満たし、docs-only境界を維持。
