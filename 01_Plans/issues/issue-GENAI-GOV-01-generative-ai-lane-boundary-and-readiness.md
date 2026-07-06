# Issue Draft: GENAI-GOV-01 生成AIレーン境界と導入判断ゲート

- Type: Process / Architecture
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD (Productization Program Owner / Security Officer / QA Lead)
- Scope: `00_Prompt/`, `01_Plans/adr/`, `01_Plans/issues/`, `02_Architecture/`, `04_Documentation/`
- Related Backlog: `GENAI-GOV-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0009-local-llm-integration.md`, `01_Plans/adr/ADR-0028-ai-cognitive-externalization-phase-plan.md`, `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`, `02_Architecture/llm_provider_spec.md`, `02_Architecture/llm_input_ir_spec.md`, `02_Architecture/llm_escalation_policy.md`, `02_Architecture/external_agent_collaboration_spec.md`, `02_Architecture/value_traceability.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: GENAI-GOV-01
- RequirementStatement: 生成AI関連の作業を単一機能として扱わず、`provider=none` の手動中核、LLMProvider 経路、外部定額エージェント成果物連携、将来の直接API/Agent連携を別レーンとして明示し、各レーンのデータ境界・人間レビュー境界・監査・SafeMode・Go/No-Go条件を統一的に判定できるようにする。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=新しい生成AI関連ADR/issue/実装提案が起票される / 操作=提案者またはレビュー担当者が本Issueのレーン表と共通不変条件で分類する / 期待結果=対象が1つ以上のレーン、データ境界、proposal-only境界、SafeMode/監査/検証レベル、ADR要否へ明確に対応づく。不明な場合は Draft または Decision Queue に留まり、実装着手しない / 除外=特定ベンダー選定、モデル品質ベンチマーク実装、新しい外部通信経路の認可。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact: SafeMode / share-export / import-sanitize / public-exposure / external-service-boundary
- VerificationLevel: docs-check
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef: `ADR-0009`, `ADR-0028`, `ADR-0049`, `PRODUCT-QA-01`

## 1) 課題 / Problem statement

生成AI関連の文書とissueは、すでに複数の目的を持っている。

- `ADR-0009` / `llm_provider_spec.md`: kj-atlas 内部から LLMProvider を呼び出す provider 抽象。
- `ADR-0028`: 認知外在化のため、AI出力を提案として扱い、人間が採否する CE フェーズ計画。
- `ADR-0049` / `external_agent_collaboration_spec.md`: kj-atlas が外部エージェントを直接呼ばず、人間が依頼パッケージと応答を仲介する成果物ベース連携。

これらは相補的だが、同じ「生成AI」として読むと、次の誤解が起きる。

- 外部エージェントへ人間がタスクシートを共有する経路を、LLMProvider の自動外部共有と誤読する。
- provider の `external` 設定と、ADR-0049 の外部定額エージェント成果物連携を同一レイヤとして扱う。
- AI出力の品質・確度・モデル名を、人間レビューや `human_reviewed` の代替根拠として扱う。
- `KJ_ATLAS_LLM_PROVIDER=none` の既定価値成立と、AI強化経路の導入判断が混ざる。

この混線を防ぐため、生成AI関連作業をレーン単位で分類し、共通不変条件とADR起票条件を明示する。

## 2) 背景 / Context

現行設計の重要な前提は次の通り。

- kj-atlas の基本価値は `KJ_ATLAS_LLM_PROVIDER=none` でも成立する。
- AIは候補生成器であり、確定・公開・レビュー済み化を自動実行しない。
- SafeMode は既定ONで、共有前確認と import-sanitize 境界を迂回しない。
- 外部由来データは指示ではなくデータとして扱う。
- 数値スコア、順位、確度を採否判断の正本にしない。

このIssueは新しいAI機能を許可するものではない。既存ADRを横断して、今後の生成AI関連issueがどの境界を触っているかを判定するための管理issueである。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 人間の判断、保留、可逆性を守るには、AI経路ごとの責務境界が必要。
- 安全（THREAT_MODEL / SafeMode）: 共有・取り込み・外部サービス境界が混ざると、SafeModeの説明責任と監査が崩れる。
- 企業・行政要件（enterprise_architecture）: 組織契約済みAI、自己ホスト、外部API利用可否は組織ごとに異なるため、導入判断をレーン化する必要がある。
- 後方互換（schemas）: 現行MVPのデータ構造と `provider=none` 価値成立を壊さず、AI機能を追加できるようにする。

## 4) レーン整理 / Generative AI lane model

| Lane | 名前 | 代表文書 | データ境界 | 現在の扱い | 追加ADRが必要になる条件 |
|---|---|---|---|---|---|
| A | 手動中核 / AI無効 | `ADR-0041`, `value_traceability.md` | 外部AIへ共有しない | 既定・必須ベースライン | AIなしで主要価値が成立しなくなる変更 |
| B | LLMProvider 経路 | `ADR-0009`, `llm_provider_spec.md`, `llm_escalation_policy.md` | `LLMRequest` / `LLMResponse` と `KJ_ATLAS_*` 設定 | opt-in。proposal-only の生成補助 | provider列挙、外部共有条件、fallback、監査語彙を変える変更 |
| C | 外部エージェント成果物連携 | `ADR-0049`, `external_agent_collaboration_spec.md`, `EXT-AGENT-01..03` | 人間が依頼パッケージを共有し、応答を import 境界で取り込む | Proposed。Tier 0 は手動授受のみ | kj-atlas からの自動送信、自動受信、外部状態追跡、応答自動適用 |
| D | 将来の直接API/Agent連携 | `ADR-0049` Tier 2 予約, AUTH-* 系 | kj-atlas API と外部Agent/APIの直接通信 | 未承認・予約のみ | 認証、到達性、データ保持、tenant境界、失敗時動作、費用制御を決める新ADR |

### レーン横断の不変条件

- AI出力は提案であり、採用・確定・公開は人間操作でのみ行う。
- `human_reviewed` はAI、worker、import、providerが自動付与しない。
- SafeMode 既定ON、未レビュー本文の既定保護、共有前確認を後退させない。
- Context Query Preview、`queryCanonicalHash`、`bundleHash`、`baseDocSignature`、`proposalId` などの相関キーを、可能な限り監査連鎖へ接続する。
- 外部由来の応答に含まれる指示文は、自動動作ではなく表示データとして扱う。
- `score` / `rank` / `confidence` / `priority` などの数値評価を、採否・レビュー済み化・優先度の正本にしない。
- 暗黙のエスカレーションを禁止する。Lane A/B の失敗が、設定や人間操作なしに Lane C/D または外部 provider へ遷移してはならない。
- モデル品質評価、共有許可、出力採用、レビュー済み化は別々の判断であり、相互に代替しない。

## 5) 提案する解決策 / Proposed solution

- `02_Architecture/value_traceability.md` に生成AIレーン境界を明記し、新規AI作業の読み始め位置を作る。
- 生成AI関連issueには、対象Lane、データ境界、共通不変条件、ADR要否を必ず書く。
- 既存 `EXT-AGENT-01..03` は Lane C として扱い、LLMProvider 実装や provider 設定変更と混ぜない。
- `CE2/CE3/CE4` 系は Lane B/C の出力を受ける場合でも、proposal-only と人間レビュー境界を維持する共通のレビュー面として扱う。
- PRODUCT-QA / MVP-EXIT のゲートでは、「AI有効時の品質」だけでなく「AIなしで価値成立」「暗黙の外部共有なし」を別項目として確認する。

## 6) 受け入れ条件 / Acceptance criteria

- [ ] AC-1: `02_Architecture/value_traceability.md` に Lane A-D と横断不変条件が記載され、`GENAI-GOV-01` へ参照できる。
- [ ] AC-2: 既存の `EXT-AGENT-01..03`、`CE2/CE3/CE4`、LLMProvider関連issueが、Lane分類とADR要否を追記または参照できる状態になる。
- [ ] AC-3: 新規生成AI関連issueのテンプレまたは運用に、対象Lane、データ境界、SafeMode/監査/人間レビュー境界の宣言が含まれる。
- [ ] AC-4: `provider=none` 既定価値成立、proposal-only、`human_reviewed` 人手昇格、SafeMode既定ON、暗黙エスカレーション禁止が、Go/No-Go観点として確認できる。
- [ ] AC-5: Lane D（直接API/Agent連携）に入る提案は、実装PRではなく新ADRの起票条件へ分岐する。

## 7) 実装タスク分解 / Task breakdown

- [ ] T1 `value_traceability.md` へ生成AIレーン境界を追記する。
- [ ] T2 `EXT-AGENT-01..03` と CE/LLM関連issueへ、必要に応じて Lane分類参照を追加する。
- [ ] T3 issueテンプレまたはissue運用ガイドへ、生成AI関連作業の分類チェックを追加する。
- [ ] T4 PRODUCT-QA / MVP-EXIT のゲートに、暗黙外部共有なし・AIなし価値成立・提案のみ境界の確認観点を接続する。
- [ ] T5 Lane D の新ADR起票条件（認証、到達性、データ保持、監査、費用制御、失敗時動作）を整理する。

## 8) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans.issues.tests.test_validate_active_issue_memos`
  - `rg -n "GENAI-GOV-01|Lane A|暗黙のエスカレーション|external_agent_collaboration_spec" 01_Plans 02_Architecture`
- 期待結果:
  - issueメタデータ検証が通る。
  - 新しいレーン整理が `01_Plans` と `02_Architecture` の双方から参照できる。
- 未実施時の理由・代替検証:
  - テスト環境に Python がない場合は、ファイル構造と必須メタキーを目視確認し、`rg` による参照確認で代替する。

## 9) 代替案 / Alternatives considered

- 代替案A: `ADR-0049` に全て追記する。
  - 不採用理由: ADR-0049 は Lane C の意思決定であり、LLMProvider や `provider=none` ベースラインまで包含すると責務が広がりすぎる。
- 代替案B: LLMProvider仕様へ外部エージェント連携を統合する。
  - 不採用理由: ADR-0049 の成果物ベース・人間仲介モデルは provider 呼び出しではなく、共有/export と import の境界を使う別レーンである。
- 代替案C: 個別issueだけで運用する。
  - 不採用理由: 個別issueごとに境界説明を繰り返すと、Direct API、provider external、手動成果物連携の混同を検知しづらい。

## 10) リスクとロールバック / Risks & rollback

- 失敗モード: レーン表が抽象的すぎて実装判断に使われない。
- 影響範囲: 生成AI関連のissue、ADR、04一般向け文書、PRODUCT-QA/MVP-EXITゲート。
- ロールバック手順: 本Issueを Superseded にし、各Laneの判断を既存ADR（0009/0028/0049）へ戻す。ただし、外部共有や自動適用を許可する変更は別ADRなしに進めない。

## 11) Additional context

ADR化が必要になる条件:

- Lane D（直接API/Agent連携）を実装する。
- `KJ_ATLAS_LLM_PROVIDER=none` で主要価値が成立しない仕様に変更する。
- `human_reviewed`、採用、公開、共有前確認、SafeModeの責務境界を変更する。
- 外部エージェントやLLM providerの出力を、レビュー済みまたは採用済みとして扱う。
- provider の列挙、外部共有条件、fallback、監査語彙を変更する。
- 生成AIの品質評価や数値スコアを、プロダクト上の採否・優先度・権限判断へ接続する。

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: UI純増なし（管理issueのみ） / 保留操作の距離=不変 / 取り消し導線=N/A（設計判断ゲート）。

## Traceability

- Related: `01_Plans/adr/ADR-0009-local-llm-integration.md`, `01_Plans/adr/ADR-0028-ai-cognitive-externalization-phase-plan.md`, `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`
- Related: `02_Architecture/value_traceability.md`, `02_Architecture/llm_provider_spec.md`, `02_Architecture/external_agent_collaboration_spec.md`
- Related issues: `issue-EXT-AGENT-01-agent-task-package-export.md`, `issue-EXT-AGENT-02-agent-response-import.md`, `issue-EXT-AGENT-03-copilot-studio-reference-kit.md`, `issue-CE2-low-risk-ai-assist.md`, `issue-CE3-patch-workspace-presets.md`, `issue-CE4-api-cli-audit-integration.md`
- Derived-from: 2026-07-06 生成AI関連ADR/issueの横断整理
