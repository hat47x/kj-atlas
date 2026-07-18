# コアバリュー実現の優先要件整理（2026-07-18）

- 目的: プロダクトのコアバリューを実現するために早急に実現すべき要件を、既存backlog・ADRへの対応付きで一枚に整理し、実行順序と担当（エージェント代行を含む）を固定する。
- 前提: 2026-07-18時点の `origin/main`（コアバリュー機能群 CE-0〜CE-4・価値ループV0〜V4・CVIガードはすべてDone。[issue-MVP-EXIT-01](issues/issue-MVP-EXIT-01-productization-readiness.md) の判定は「製品機能・自動検証はConditional Go、正式出荷はNo-Go」。価値実在検証は [ADR-0042](adr/ADR-0042-value-realness-validation-and-notice-exit.md) の段階A）。
- 運用方針（本文書の固有前提）: 従来「人間確認」とされてきた判断・検証は、**原則としてClaude CoworkまたはChatGPT Workによる代行を前提**に文書化する（Maintainer指示、2026-07-18）。代行で埋まらない残余は「残余」欄に明示し、Maintainerの確認は「代行結果の受理」1行に縮退させる。
- 非目標: 個別の実装詳細・UI設計・新機能提案。ここに書いた要件の実装ログを本文書へ積み上げること（進捗は各issueへ記録する）。

## 1. コアバリューの定義（正本参照）

> **少ない操作で曖昧さ（保留・違和感）を保持し、可逆かつ人間最終判断（proposal-only / SafeMode既定ON / provider=noneでも成立）のまま、構造化・共有できること。**

- 正本: `00_Prompt/domain.md`（保留・違和感・可逆性）、`README.md`（「違和感・保留・揺らぎを扱うための道具」）、[ADR-0041](adr/ADR-0041-core-value-invariants-single-guard.md)（不変条件CVI-1〜7）、`02_Architecture/value_traceability.md`（原則P-01〜P-09の対応表）。

## 2. 現状認識: ギャップは「機能」ではない

1. コアバリューを実現する機能群は実装完了済み（Vitest 1,034件・Playwright 165件・a11y自動検査を通過）。
2. しかし正式出荷はNo-Go。残るのは人間確認4件＋安全設定の実配送2件。
3. 価値実在検証は段階Aのまま（実利用者ゼロ）。段階B移行の名指しブロッカーだったQA-MONKEY-10（ラベルカリングによる見かけ喪失）は**解消済み（Done）**であり、残る条件は「非開発者1名以上が本番同等環境で5手順を完走」のみ（[dogfood-log-2026-07-10](dogfood-log-2026-07-10.md)）。
4. 凍結中のbacklog群（VALUE-MEASURE系・SOCIAL-DIFFUSION系）は [ADR-0039](adr/ADR-0039-governance-right-sizing-personal-oss.md) により「実利用者が現れるまでactivation延期」。つまり段階B到達がこれらの解凍条件でもある。

**結論: 早急に実現すべきは「信頼欠陥の解消 → 検証・出荷判断の完了 → 実利用の初回獲得」という出荷クリティカルパスであり、新機能開発ではない。**

## 3. 優先要件（R1〜R7）

| # | 要件 | 対応Issue/ADR | 律速 | 残作業（2026-07-18時点） |
|---|---|---|---|---|
| R1 | 設定したつもりの保護がfail-openになる欠陥の解消 | [ENV-COMPOSE-01](issues/issue-ENV-COMPOSE-01-runtime-setting-delivery-and-effective-verification.md) | 実装 | Compose配送allowlist＋機能probe（API key保護・JIT禁止が実際に効くことの確認）。配送面分類（Phase 1）は正本化済み |
| R2 | 評価環境のLAN暗黙公開の停止（loopback既定化） | [DEPLOY-NET-01](issues/issue-DEPLOY-NET-01-loopback-default-and-network-exposure-boundary.md)（PR #2618） | レビュー判断 | 実装済みPRのセキュリティレビューとマージ判断 |
| R3 | 初回実利用の獲得（段階B移行の唯一の残条件） | [ADR-0042](adr/ADR-0042-value-realness-validation-and-notice-exit.md) | 検証実行 | 本番同等環境での5手順完走（§4.3の代行設計を参照） |
| R4 | MVP-EXIT-01の受入確認4件 | [MVP-EXIT-01](issues/issue-MVP-EXIT-01-productization-readiness.md)・[代行ハンドオフ](mvp-exit-01-human-acceptance-handoff.md) | 検証実行 | キーボード確認 / スクリーンリーダー確認 / リリース画像確認 / 出荷判断記録（§4.1〜4.2の代行設計を参照） |
| R5 | QAゲート3件（P0）の軽微ブロッカー解除 | [QA-E2E-USE-01](issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md) / [QA-PUB-01-I18N-03](issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md) / [QA-UNIT-01](issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md) | 意思決定 | 承認は2026-07-16に完了済み。残りは実行経路の1本固定等の軽微決定のみ（[PRODUCT-QA-01](issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md) ゲート証跡に直結） |
| R6 | 定性カード品質支援の完了（原則P-08: 定性情報への忠実性） | [DOMAIN-CARD-QUALITY-01](issues/issue-DOMAIN-CARD-QUALITY-01-qualitative-card-quality-assistance.md) | 完了 | 本文のみの一回保存、前後比較、原文復元をE2Eで確認済み。Phase Cは実利用の要望が得られるまで追加しない |
| R7 | W型累積探究の本体実装（原則P-09: 累積的探究） | [DOMAIN-W-ITERATION-01](issues/issue-DOMAIN-W-ITERATION-01-w-type-cumulative-inquiry-support.md)・[ADR-0057](adr/ADR-0057-w-type-cumulative-inquiry-model.md) | 実装（Codex主担当） | 永続化・UI・再開ブリーフ・E2E（Phase 0のドメイン模型のみ完了） |

### 優先順位の根拠

- **R1・R2が最優先**: コアバリューの核心は「**安全に**曖昧さを外在化できるという信頼」。既知の安全欠陥（保護のfail-open、LAN暗黙公開）は SafeMode既定ON・プライバシーデフォルト（P-07）という価値宣言そのものを裏切るため、初回実利用者（R3）を迎える前に解消する。
- **R3・R4が第2群**: コアバリューは使われて初めて実現する。R3の達成は ADR-0039 で凍結中の価値観測・社会拡散系backlog（約7件）の解凍条件でもある。
- **R6・R7は並行**: 中核原則（P-08/P-09）に直結する進行中機能だが、出荷のブロッカーではない。

## 4. 人間判断のエージェント代行設計（R3〜R5）

従来のハンドオフ文書（[mvp-exit-01-human-acceptance-handoff.md](mvp-exit-01-human-acceptance-handoff.md)）は「人が実機で操作する」前提で書かれている。本文書はMaintainer指示（2026-07-18）に基づき、**Claude CoworkまたはChatGPT Workによる代行を原則**とする実行形へ置き換える。委譲先はどちらでもよく、証跡・記録先の要件は同一とする（[ADR-0045](adr/ADR-0045-agent-division-of-labor-cowork-code-codex.md) の分担では実機検証はCodex主担当・Claude Code補助だが、ここでの代行は「検証の実行と記録」であり同ADRと矛盾しない）。

### 4.1 MVP-EXIT-01 タスク1・2（キーボード / スクリーンリーダー）

| 項目 | 代行方法 | 得られる証跡 | 残余（代行で埋まらないもの） |
|---|---|---|---|
| キーボード操作確認 | エージェントがブラウザ操作でマウス不使用の主要操作（作成→入力→確定→パネル遷移→保存→再読込→トグル）を完走し、各ステップのフォーカス位置・視認性を記録する | 操作ログ＋スクリーンショット＋フォーカス遷移の記述 | 物理キー配列・指の動き・OS/IMEの体感。**本方針により残余として受理する**（IME確定Enterの競合は自動E2Eで検証済みの範囲を明記） |
| スクリーンリーダー確認 | エージェントがaccessibilityツリーを読み取り、「開始・編集・保存・共有前確認」の4操作で読み上げられる名前・ロール・状態変化を、SRの読み上げ順序に沿って書き起こす | 4操作それぞれのa11yツリー書き起こし＋名前なし要素（「ボタン」としか読まれない箇所）の一覧 | NVDA/VoiceOver実機の音声挙動（間・重複読み・ライブリージョン発火タイミング）。**残余として受理する** |

- 合格基準は既存ハンドオフ文書のものをそのまま使う。
- 記録先: [issue-MVP-EXIT-01](issues/issue-MVP-EXIT-01-productization-readiness.md) の該当ACへ「実施日・実行エージェント・環境・結果（問題なし/注意あり/停止）・残余の受理」を1行で追記する。

### 4.2 MVP-EXIT-01 タスク3・4（リリース画像確認 / 出荷判断）

| 項目 | 代行方法 | 得られる証跡 | 残余 |
|---|---|---|---|
| リリース候補画像確認 | 画像認識可能なエージェントが `04_Documentation/` 掲載の全画像を、既存ハンドオフ文書の4観点（内部情報の写り込み / 現行UIとの一致 / 機微情報 / 未翻訳）で判定する | 画像ごとの判定表（確認日・枚数・問題件数） | なし（画像目視は代行で完結する） |
| 最終出荷判断 | エージェントがタスク1〜3の結果・候補commitのCI・[PRODUCT-QA-01](issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md) のG0〜G7を照合し、**Go/No-Go判断書のドラフト**（候補commit SHA・根拠・残余一覧つき）を作成する | 判断書ドラフト | **Go/No-Goの確定はMaintainerの受理1行**（判断根拠の収集・整理・起案まで代行し、署名だけ残す） |

### 4.3 段階B移行（R3: 初回実利用）

- 代行方法: エージェントが本番同等環境（`03_Implement/deploy` のCompose構成）で、[dogfood-log-2026-07-10](dogfood-log-2026-07-10.md) の5手順（作成→束ね→保留→共有前確認→export）を、**開発文脈を持たない初見利用者のペルソナで**完走し、迷った箇所・説明が必要だった箇所を摩擦ログとして記録する。
- 得られる証跡: 完走ログ＋摩擦一覧（VALUE-DOGFOOD-01形式）。
- **残余（重要）**: [ADR-0042](adr/ADR-0042-value-realness-validation-and-notice-exit.md) の段階B条件は現状「**非開発者（人間）1名以上**」と読める。エージェント代行走行は段階B移行の**準備証跡**としては十分だが、条件そのものを「エージェント代行で足りる」と読み替えるのは判定基準の変更であり、**ADR-0042への追記（判定基準の代行許容）をMaintainerが受理してから**段階B宣言を行う。読み替えを行わない場合、代行走行は「摩擦の事前除去」として価値を持ち、人間1名の完走コストを最小化する。

### 4.4 QAゲートの軽微決定（R5）

- 代行方法: エージェントが各issueの残ブロッカー（実行経路の1本固定、ゲート証跡欄の固定、unitプロファイル選択）について、選択肢・トレードオフ・推奨案を1ページで起案し、Maintainerは受理/差戻しのみ行う。
- 記録先: 各issueの該当欄。

### 委譲時の共通ルール

1. 代行結果は必ず該当issueのACへ記録し、本文書へは積み上げない。
2. 「停止」または重大な「注意あり」が出た場合は先へ進まず、再現条件つき個別issueを起票してから判断を仰ぐ。
3. 安全既定（SafeMode既定ON・proposal-only・provider=none既定・share/export境界）を緩める操作は代行範囲外（[ADR-0041](adr/ADR-0041-core-value-invariants-single-guard.md) CVI違反となるため即停止）。
4. 秘密値（API key・token・password）を証跡・ログ・スクリーンショットへ残さない。

## 5. 委譲プロンプト（コピペ用）

以下をClaude CoworkまたはChatGPT Workの新規セッションの最初のメッセージとして使う。

```
kj-atlasリポジトリのコアバリュー実現クリティカルパス（正式出荷までの残作業）のうち、
エージェント代行が前提とされている検証・起案タスクを進めてください。

参照文書（必読・この順で）:
- 01_Plans/core-value-realization-priorities-2026-07-18.md（本文書。R1〜R7と代行設計§4）
- 01_Plans/mvp-exit-01-human-acceptance-handoff.md（タスク1〜4の実施手順・合格基準・記録先）
- 01_Plans/issues/issue-MVP-EXIT-01-productization-readiness.md（親issue）

依頼範囲（§4の代行設計に従う）:
1. §4.1: キーボード操作確認（ブラウザ操作で完走・記録）と、a11yツリーによるスクリーンリーダー相当確認。
2. §4.2: リリース候補画像の4観点判定と、Go/No-Go判断書ドラフトの作成。
3. §4.3: 初見利用者ペルソナでの5手順完走と摩擦ログ（段階B移行の準備証跡）。
4. §4.4: QAゲート3件の残ブロッカーについて選択肢と推奨案の起案。

制約:
- 各結果は該当issueのACへ「実施日・実行エージェント・環境・結果・残余の受理」を1行で記録する。
- 「停止」相当の問題が出たら先へ進まず、個別issueの起票準備をして判断を仰ぐ。
- SafeMode・proposal-only・provider=none等の安全既定を緩めない。秘密値を証跡に残さない。
- Go/No-Goの確定と、段階B判定基準の読み替え（ADR-0042追記）はMaintainerの受理事項として残す。
```

## 6. 急がないもの（意図的凍結・根拠つき）

| 対象 | 凍結根拠 |
|---|---|
| SOCIAL-DIFFUSION-01〜04、VALUE-MEASURE-01/02、VR-ROADMAP-01 | [ADR-0039](adr/ADR-0039-governance-right-sizing-personal-oss.md) により実利用者・協力者の出現までactivation延期。R3の達成がこれらの解凍条件 |
| EXT-CONN-02/03/04（外部エージェント連携の段階2以降） | ADR-0054の段階ゲート（段階1の運用実績待ち） |
| ADR-0051（Bulk Critique理由記録、Proposed未実装） | 依存元issueはDone、実害報告なし |

## 7. Sonnet級エージェント実行計画の所在（2026-07-18追記）

人間判断なしに続行可能な要件は、各issueファイル内の「Sonnet級エージェント実行計画（2026-07-18）」節として詳細化した。いずれも設計選択を計画内で確定済みであり、実行エージェントは選択肢の再検討なしに着手できる。

| 要件 | 計画の所在 | 実行後のマージ規律 |
| --- | --- | --- |
| R1 配送実装・probe・契約テスト | [ENV-COMPOSE-01](issues/issue-ENV-COMPOSE-01-runtime-setting-delivery-and-effective-verification.md) | デプロイ挙動変更のため**人間レビュー保留** |
| R5 QAゲート解除＋初回バッチ | [QA-E2E-USE-01](issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md) / [QA-PUB-01-I18N-03](issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md) / [QA-UNIT-01](issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md) | テスト追加のみ、CI green後マージ可 |
| R6 AC-7（前後比較と原文復帰） | [DOMAIN-CARD-QUALITY-01](issues/issue-DOMAIN-CARD-QUALITY-01-qualitative-card-quality-assistance.md) | 2026-07-18実装・E2E完了 |
| （付随）文書コマンド照合の残り4区分 | [DX-DOC-04](issues/issue-DX-DOC-04-executable-command-contract-checks.md) | docs+tooling-only、CI green後マージ可 |

計画追記を**見送った**もの（理由つき）:

- **R7 [DOMAIN-W-ITERATION-01](issues/issue-DOMAIN-W-ITERATION-01-w-type-cumulative-inquiry-support.md)**: Owner: Codexが本体実装を進行中のため、並行セッションの作業と衝突する計画追記を行わない（ADR-0045 CP-6）。
- **R2 [DEPLOY-NET-01](issues/issue-DEPLOY-NET-01-loopback-default-and-network-exposure-boundary.md)**: 実装済み（PR #2618）。残作業は人間のセキュリティレビューのみで、追加計画の対象がない。
- **[DATA-MODEL-OPS-02](issues/issue-DATA-MODEL-OPS-02-management-plane-data-boundary.md) AC-6**: Round 8デザイン往復が外部ツールで進行中（作業ツリーに未コミットの依頼文・回答素材を確認済み）。受領処理はその往復の完了後であり、いま計画を固定すると進行中の実態と乖離する。
- **R3/R4（検証実行系）**: §4〜§5の代行設計・委譲プロンプトが既に実行計画に相当する。

## Traceability

- Source: Maintainerの整理依頼および代行前提の文書化指示（2026-07-18 チャット）
- Related: [issue-MVP-EXIT-01](issues/issue-MVP-EXIT-01-productization-readiness.md), [mvp-exit-01-human-acceptance-handoff.md](mvp-exit-01-human-acceptance-handoff.md), [ADR-0042](adr/ADR-0042-value-realness-validation-and-notice-exit.md), [ADR-0039](adr/ADR-0039-governance-right-sizing-personal-oss.md), [ADR-0041](adr/ADR-0041-core-value-invariants-single-guard.md), [ADR-0045](adr/ADR-0045-agent-division-of-labor-cowork-code-codex.md), [dogfood-log-2026-07-10](dogfood-log-2026-07-10.md)
