# Issue Draft: PRODUCT-VALUE-01 初回価値実感と最初の意味ある配置

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD
- Scope: `03_Implement/frontend/src/`, `03_Implement/frontend/e2e/`, `04_Documentation/installation.md`, `04_Documentation/operations.md`
- Related Backlog: `PRODUCT-VALUE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0032-product-value-realization-model.md`, `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `02_Architecture/value_traceability.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: PRODUCT-VALUE-01
- RequirementStatement: 初回利用者が、サンプルまたは自分のメモから、カード、まとまり、保留点を含む最初の意味ある配置へ迷わず到達できるようにする。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=ブラウザでkj-atlasを初回利用する / 操作=サンプルを開く、または短いメモを入力してカード化し、少なくとも1つのまとまりまたは保留点を作る / 期待結果=「何を置き、何をまだ決めていないか」が画面上で分かる / 除外=高度なAI提案、自動分類、クラウド同期。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / import-sanitize
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0032`

## 1) 課題 / Problem statement

- 現在の製品化issueは画面入口、パネル、共有前確認を扱っているが、利用者が最初に価値を実感する「意味ある配置」までの完了条件が明確でない。
- kj-atlas の価値は、単に文書を開くことではなく、考え途中の素材をカード、まとまり、保留点として扱えることにある。
- 初回成功経路が未定義のままだと、機能説明やサンプル表示はあっても、利用者が次の作業へ進む確信を得にくい。

## 2) 背景 / Context

- `ADR-0031` は開始/文書入口を製品化UIの基本領域にした。
- `ADR-0032` は V0/V1 として、開始と外在化を価値ループに位置づけた。
- `domain.md` は、保留、違和感、可逆性を本プロダクトの中核概念として定義している。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 初回でカードと保留点を作れない場合、意味の保留という価値が体験されない。
- 安全（THREAT_MODEL / SafeMode）: 初回取り込み時に検証とSafeMode状態を見せることで、不正ファイルや意図しない共有を避けやすい。
- 企業・行政要件（enterprise_architecture）: 教育コストを下げ、短い導入説明で標準操作に入れることは組織導入で重要である。
- 後方互換（schemas）: 既存document/view/packを壊さず、開始導線と受入シナリオを追加する。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - 初回開始導線、サンプル、短いメモ入力、カード化、保留点表示、公開文書の導入手順。
- 変更の最小単位:
  - 「最初の意味ある配置」を、カード3件以上、まとまりまたは保留点1件以上、保存または共有前確認へ到達可能な状態として暫定定義する。
  - サンプルまたは入力例から同じ経路を確認できるE2Eを用意する。
- 非目標:
  - AIによる自動分類。
  - 利用者行動の個人追跡。
  - アカウントやクラウド履歴の実装。

## 5) 受入条件 / Acceptance criteria

- [ ] 初回利用者が、サンプルまたは短いメモ入力からカードを作れる。
- [ ] 少なくとも1つのまとまり、関係、または保留点を作る操作が画面上で分かる。
- [ ] まだ決めていないことが、失敗や未完了ではなく作業状態として見える。
- [ ] SafeModeと取り込み検証状態が初回経路の中で確認できる。
- [ ] `Tab` / `Enter` / `Space` で初回経路の主要操作へ到達できる。
- [ ] 公開文書の導入手順が、この初回成功経路と矛盾しない。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 「最初の意味ある配置」の最小状態をUI/データ/文書で定義する。
- [ ] T2 サンプルまたは短い入力例からカード、まとまり、保留点を作るワイヤーフローを作成する。
- [ ] T3 初回経路をキーボード操作と小画面で確認する。
- [ ] T4 Playwrightで代表初回経路をE2E化する。
- [ ] T5 `installation.md` / `operations.md` / `public_index.md` の導入手順と同期する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && node .\\node_modules\\playwright\\cli.js test --reporter=line`
  - `cd 03_Implement/frontend && node .\\node_modules\\typescript\\bin\\tsc --noEmit`
  - `git diff --check -- 01_Plans 02_Architecture 03_Implement/frontend 04_Documentation`
- 期待結果:
  - 初回経路がE2Eで再現でき、サンプルまたは短い入力から最初の意味ある配置へ到達できる。
- 未実施時の理由・代替検証:
  - UI実装前は、Playwright操作計画、スクリーンショット、文書上の受入シナリオで代替する。

## 8) 代替案 / Alternatives considered

- 代替案A: サンプルを表示するだけにする。利用者が自分の素材で価値を得る経路が残らないため採用しない。
- 代替案B: AI自動分類を初回価値にする。LLMなしの既定構成で価値が成立しなくなるため採用しない。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 初回導線が長くなり、利用者が作業面へ入る前に疲れる。
- 影響範囲: frontend shell、sample data、公開文書、E2E。
- ロールバック手順: 初回価値経路をサンプル専用の補助導線へ戻し、既存の文書入口は維持する。

## 10) Additional context

- ADR化が必要になる条件: 初回経路をルーティング、ローカル履歴、ユーザープロファイルの仕様として固定する場合。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
