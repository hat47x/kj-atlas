# 対外文書作成品質基準（内部運用 / AIエージェント向け）

このドキュメントは、AIエージェントやメンテナが **対外公開するユーザ/開発者向け技術文書** を作成・更新する際の、内部向け品質管理基準を定義します。公開文書そのものではなく、`01_Plans/` に置く内部運用ルールとして扱います。

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

Stream I では対象Issueで明示された文書のみを編集対象とする。既定では Stream H 専有（operations / security）は編集しない。`e2e_testing.md` は対象Issueで明示された場合のみ例外的に編集可能とする。

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

対象文書（`diagnostics.md` / `e2e_testing.md` / `e2e_verification_log_2026-03-03.md` / `codex_skill_operations.md` / 本書）は、同一の5Phaseワークフロー（Read→Plan→Execute→Verify→Proceed）を適用する。

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
