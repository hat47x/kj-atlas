# Value Traceability

この文書は、kj-atlas の価値判断が、設計要素、受入条件、検証観点へどのように接続するかを示す対応表です。

`00_Prompt` は価値・用語・禁止事項の上流、`02_Architecture` は実装可能な構造と責務境界の層です。設計や実装が上流の価値からずれている場合は、文書だけで吸収せず、内部 issue または ADR で修正方針を起票します。

`02_Architecture` の各文書で、現行契約と履歴ログのどちらを読んでいるか迷った場合は [contract_reading_guide.md](contract_reading_guide.md) を参照します。

---

## 1. 読み方

- **価値判断**: プロジェクトが守りたい利用者価値や判断軸。
- **利用者に見える成果**: 一般利用者が体験として受け取る状態。
- **上流文書**: 価値・用語・要求の正本。
- **設計への落とし込み**: `02_Architecture` で固定する構造や境界。
- **検証観点**: 受入条件、レビュー、テストで確認する観点。

---

## 2. 価値トレーサビリティ

| 価値判断 | 利用者に見える成果 | 上流文書 | 設計への落とし込み | 検証観点 |
|---|---|---|---|---|
| 意味を急いで確定しない | 未整理・違和感・保留を失敗として扱わず、考え途中の状態を保存できる | `00_Prompt/domain.md`, `00_Prompt/ai_cognitive_externalization_requirements.md` | `WorkingGraph` と `ContextProjectionGraph` を `Consensus Graph` から分離する | AI提案や表示が `Consensus Graph` を直接更新しない |
| 人間の判断を優先する | AIは候補を出すが、採否やレビュー済み化は人間が決める | `00_Prompt/domain.md`, `01_Plans/adr/ADR-0001-value-to-requirements.md` | proposal-only、`patch + approval`、`human_reviewed` の人手昇格 | auto-apply、AIによる `human_reviewed` 自動付与がない |
| 可逆性を守る | 配置、分類、共有前確認をやり直せる | `00_Prompt/domain.md` | snapshot / diff / dry-run / readOnly 境界を維持する | `dryRun=true` で副作用が発生しない |
| 安全に共有できる | export/share 時に未レビュー本文や意図しない情報が混ざらない | `THREAT_MODEL.md`, `02_Architecture/schemas.md` | SafeMode既定ON、share/export policy、`visibility` はラベル用途に限定 | SafeMode / readOnly / visibility の優先順位が崩れない |
| Local-first で小さく始められる | LLMや外部サービスなしでも導入・検証できる | `02_Architecture/runtime_parameter_registry.md`, `02_Architecture/deployment.md` | `KJ_ATLAS_LLM_PROVIDER=none` を既定にし、SQLite / PostgreSQL を切替可能にする | 既定構成で外部 LLM にデータを渡さない |
| 生成AI経路を混同しない | AIなし、LLMProvider、外部エージェント成果物連携を選べるが、それぞれのデータ境界と人間レビュー境界を誤解しない | `ADR-0009`, `ADR-0028`, `ADR-0049`, `02_Architecture/external_agent_collaboration_spec.md` | Lane A（AI無効）/B（LLMProvider）/C（外部エージェント成果物連携）/D（将来の直接連携）を分け、proposal-only・SafeMode・監査・暗黙エスカレーション禁止を共通不変条件にする | 新規生成AIissueが対象Lane、データ境界、Go/No-Go、ADR要否を宣言している |
| 企業・行政運用に接続できる | 組織の認証、認可、監査基盤へ安全に接続できる | `02_Architecture/enterprise_architecture.md` | AuthContext、AccessControlAdapter、audit transport をアプリ本体から分離する | アプリ本体に role/group 判定ロジックを持ち込まない |
| 環境変数の混乱を防ぐ | 利用者が設定すべきキーを迷わない | `02_Architecture/runtime_parameter_registry.md` | 公開設定キーは例外なく `KJ_ATLAS_*` に統一する | 04文書、Compose、runbook が正本と同期している |
| データ運用境界を誤解させない | MVPで保守できるデータと将来契約を区別できる | `02_Architecture/data_model_operations_overview.md`, `ADR-0033` | 物理ER、論理ER、CRUD表、ステークホルダー別保守責任を分けて示す | 型の存在を標準CRUD対応と誤読させない |
| 定性情報の意味を損なわない | 本文だけですぐ記録でき、後から一中心・文脈・出典・認識上の位置づけを任意に整えられる | `00_Prompt/qualitative_card_quality_requirements.md`, `ADR-0001` P-08 | `Card.text` を正本とし、品質支援を保存後のproposal-onlyにする。少数意見・矛盾は保持する | 必須追加入力、品質採点、自動書換え、自動削除がなく、元本文へ戻れる |
| ラウンド間で思考を深める | 問題提起から手順化までを反復・分岐し、中間成果と問いの変化を失わず再開できる | `00_Prompt/w_type_iterative_inquiry_requirements.md`, `ADR-0057`（Accepted）, `02_Architecture/inquiry_journey_model.md` | 可変 `DocumentV1` と独立探究・不変成果DAGを分離し、明示的引継ぎ、現場への問い、カード系譜を任意の高度機能として扱う | 通常利用非回帰、同段階反復、前段階分岐、自己完結bundle、provider none、SafeModeを検証する |
| カードメタデータを混同しない | 状態、出典、起票者、レビュー者を別々の意味として確認できる | `02_Architecture/schemas.md`, `02_Architecture/review_attribution.md`, `CARD-META-UI-01`, `DOMAIN-TRACE-01` | `Card.meta` 系は通し番号/出典と主体メタを分離し、起票者などの個人・組織識別はSidePanel/共有前確認/redaction境界を先に決める | 出典参照トグルと主体メタ同梱が別ゲートで、review attribution や所有者移管と混同されない |
| 価値を裏切らない（不変条件の保護） | 機能が増えても保留/proposal-only/人手昇格/SafeModeが崩れない | `02_Architecture/value_traceability.md` §2.5, `ADR-0041` | 散在する非後退テストを CVI-1..7 として単一の砦へ索引化する | CVI 横断テストが赤になる変更を検知できる |
| 思考を雑にしない（認知負荷の予算） | 機能が増えても初期の静けさと保留の容易さが保たれる | `00_Prompt/domain.md`, `ADR-0043`, `ADR-0030` | 複雑性予算（CB-1..4）で初期表示の純増と保留距離を抑える | UI追加issueで複雑性予算を申告し悪化時にゲート確認 |
| 待たされて思考が途切れない（性能予算） | 大規模文書でも対話操作が即応し、重い処理は待機表示される | `02_Architecture/architecture.md`, `ADR-0046` | 性能予算（PB-1..5）で代表規模・worker化基準（100ms超）・劣化可視化を固定 | 代表規模fixtureの最小性能アサーション＋性能影響issueの予算申告 |

---

## 2.1 プロダクト価値実現ループ

`ADR-0032-product-value-realization-model.md` は、上記の価値判断を製品化の実行単位へ落とすため、次の5ループを定義します。

| Loop | 利用者価値 | 02層で守る設計責務 | 主な検証観点 | 対応issue |
|---|---|---|---|---|
| V0: 開始 | 迷わず作業を始められる | 文書入口、SafeMode表示、import-sanitize境界をUI Shellの責務として扱う | 初回起動、サンプル、文書読み込み、SafeMode確認が同じ導線で説明できる | `PRODUCT-UX-01`, `PRODUCT-VALUE-01` |
| V1: 外在化 | メモや違和感を置ける | Raw Note、Card、Hold、Critiqueを削除や失敗ではなく作業状態として扱う | カード作成、保留、違和感が理由なしで記録できる | `PRODUCT-VALUE-01`, `PRODUCT-VALUE-02` |
| V2: 構造化 | まとまり、関係、未整理を同時に扱える | Island、Relation、Pending、View stateを内容削除と分離する | 俯瞰、詳細、保留、関係が往復可能で、表示制御がデータ破壊にならない | `PRODUCT-UX-02`, `PRODUCT-VALUE-02` |
| V3: レビュー | AI候補や要約を人間が採否判断できる | ContextProjectionGraph、proposal-only、patch + approval、reviewStateを分離する | auto-applyなし、`human_reviewed` 自動昇格なし、sourceBundleHash追跡あり | `PRODUCT-VALUE-02`, `CE-*` |
| V4: 共有と学習 | 読者が確定点、保留点、根拠を理解できる | Narrative、Review Pack、SafeMode、review attribution、source traceを共有前確認へ接続する | 共有物に未レビュー情報、保留点、根拠参照、安全状態が明示される | `PRODUCT-UX-03`, `PRODUCT-VALUE-03` |

### 2.1.1 実装状態（2026-07-02 更新）

| 設計観点 | 状態 | 実装証跡 | 残課題 | 起票先 |
|---|---|---|---|---|
| 初回価値実感 | ✅ 実装完了 / H-PV1代理承認済み | StartPanel value proposition, DomainStateSummary, CardView badges, E2E (mouse+kb, first_run, share_preflight), docs sync | 実機アクセシビリティ、release screenshot approval、Compose/環境リハーサル、最終program approval | `PRODUCT-VALUE-01` |
| 保留・違和感の日常操作 | ✅ Phase 1 完了 / H-PV2代理承認済み | DOMAIN-EXPR-01 Done (readonly state surfacing). DOMAIN-EXPR-03: critique types→domain.md 5種, SidePanel reproposal diff preview, Open Reproposal button. AI review-boundary guard (CE2+HIL). ContextBundle constraint-preservation proof. | Hold/Shelf 第一級化 (DOMAIN-EXPR-02, schema判断待ち). AI有効時再提案生成証跡. 実データソース parity、実機アクセシビリティ、最終program approval. | `PRODUCT-VALUE-02`, `DOMAIN-EXPR-01` (Done), `DOMAIN-EXPR-03` (In Progress), `DOMAIN-EXPR-02` (deferred) |
| 根拠・主張・反対意見の追跡 | ✅ Phase 1 完了（矛盾状態管理・矛盾シグナルレビュー含む） | Evidence/Contradiction Links in narrative export. SharePanel domain expression summary (evidence/contradiction/hold/critique counts). SidePanel evidence link display + contradiction report. `EvidenceLink.contradictionState`（unconfirmed/confirmed/held/resolved）。`analyzeContradictions()` 検出シグナルへの人間レビュー決定（採用/保留/却下、CE2-PROPOSAL-IF語彙を再利用、新規AI権限なし、DOMAIN-EXPR-04 2026-07-09）。 | review pack/成果物契約への矛盾情報の反映は `PRODUCT-VALUE-03`/`PRODUCT-QA-01` が所有（本issueスコープ外）。E2E証跡拡充。 | `PRODUCT-VALUE-02`, `DOMAIN-EXPR-04` (Done) |
| 成果物化 | ✅ 実装完了 / H-PV3代理承認済み | Narrative grounding: claimType+reviewState in export + in-app. Share preflight domain summary. Read-only reviewer inspection E2E. Review-pack trace export E2E. | package public contract、署名/承認workflow、実機アクセシビリティ、最終program approval | `PRODUCT-VALUE-03` |
| 価値実現ゲート | ✅ ゲート定義完了 / H-PV委任判断反映済み | PRODUCT-QA-01 gate record (G0-G7 + V0-V4 + 横断 LLM任意性). Gate records 2026-06-24 / 2026-06-29: Conditional Go. | 全ゲート Conditional Go→Go には Compose/環境リハーサル、サポートリハーサル、実機アクセシビリティ、最終program approval が必要 | `PRODUCT-QA-01`, `MVP-EXIT-01` |

### テスト健全性（2026-06-24）
- フロントエンド全ユニットテスト: 173 files, 826 tests passed
- 回帰ガード: i18n hardcode (13), UX operability (6), HIL-RS contract (4), safe_mode (2) — 全pass
- TypeScript: clean（App.tsx MenuButton pre-existing issueを除く）

---

## 2.2 Product value evidence route（2026-07-02 更新）

`PRODUCT-VALUE-01..03` は In Progress（現行証跡packetに対する H-PV1/H-PV2/H-PV3 代理承認は反映済み、最終出荷ゲートは継続）。この表は各価値ゲートの証跡状態を示す。

| Value gate | Representative user action | Evidence packet | Stop condition |
| --- | --- | --- | --- |
| `PRODUCT-VALUE-01` first meaningful map | sample or short memoから3枚以上のカードを作り、少なくとも1つのまとまり・関係・保留点へ進む | scenario fixture, mouse trace, keyboard trace, SafeMode/import validation screenshot, decision record | 初回利用者が内部文書を読まないと価値到達できない、またはSafeMode状態が共有前に確認できない |
| `PRODUCT-VALUE-02` ambiguity/evidence workflow | 保留、あいまいさ、根拠不足、反対意見を作業状態として残し、共有前に確認する | state fixture, review-boundary proof, share/export proof, AI-input constraint proof, decision record | 未確定状態が解決済み主張へ変換される、またはAI/worker/APIが`human_reviewed`を自動付与できる |
| `PRODUCT-VALUE-03` reviewable outcome package | narrativeまたはreview packで、要約・根拠・未解決点・SafeMode結果・参照元を確認できる | package fixture, pre-share confirmation, trace-back proof, read-only review proof, decision record | 成果物が最終回答のように読める一方で、未レビュー情報や根拠不足が見えない |
| `PRODUCT-QA-01` value gate intake | 上記3つの証跡をG0..G7とV0..V4の判断材料へ戻す | gate record, evidence links, blocker owner, re-decision date | 証跡がissue本文だけに残り、再実行可能なfixture/trace/screenshotに接続されない |
| `MVP-EXIT-01` program decision | product value、SafeMode、E2E/viewport、Compose startupをまとめてGo/No-Go判断する | program gate record with explicit No-Go or Conditional Go reason | data-contract closeoutやplanning convergenceを、出荷承認と誤って扱う |

Open 化前の共通条件:

1. `ADR-0032` がAcceptedになる、またはProductization Program Ownerが対象issue単位の暫定実行を明示承認する。
2. 代表fixture名、保存場所、期待される画面状態、取得するscreenshot/traceがissue本文に固定される。
3. mouse操作とkeyboard操作の両方で、代表アクションに到達できることを検証対象に含める。
4. SafeMode、share/export、import sanitize、review attributionへの影響が`PRODUCT-QA-01`へ戻せる。
5. 追加の永続schema、review semantics、署名、組織承認workflowが必要になった場合は、実装PRではなくissue/ADRを先行する。

2026-07-02追補: 条件1は `ADR-0032` Accepted と 2026-06-29 の H-PV 委任判断により、現行証跡packetの範囲では解消済みとして扱う。これは製品出荷承認、実機キーボード/スクリーンリーダー受入、Compose/環境リハーサル、サポートリハーサル、正式な組織承認、package public contract の承認を代替しない。

同日再確認: ADR/issue層の人間判断待ちは、現行証跡packetでは残0。残る項目は出荷ゲートまたは実行証跡であり、設計判断ADRではなく `PRODUCT-QA-01` / `MVP-EXIT-01` の条件付きゲートとして追跡する。

---

## 2.3 社会的目標への接続（VR0–VR5）

`01_Plans/adr/ADR-0036-value-to-social-goal-realization-roadmap.md` は、上記の価値ループ V0–V4 を社会的目標まで一直線に並べた実現フェーズ系列 VR0–VR5 を定義します。社会的目標は「散らばった暗黙知・主観・多様な意見を early collapse させずに、レビュー可能・可逆・説明可能な形へ構造化し、人間と生成AIが協働して説明可能で見直し可能な合意形成を行える場を社会へ広げること」です（`README.md` / `00_Prompt/domain.md` / `00_Prompt/ai_cognitive_externalization_requirements.md` の統合表現）。

| Phase | 価値→社会の接続 | 設計責務（02層） | 検証観点 | 担当issue |
|---|---|---|---|---|
| VR0 安全基盤 | 安全・可逆・監査の既定が崩れない土台 | SafeMode既定ON、proposal-only、patch+approval、`provider=none`既定 | 非後退の回帰固定 | `CE0`, safe_mode policy |
| VR1 価値活性化 | 最初の意味ある配置へ到達 | UI Shell入口、import-sanitize境界 | 初回経路E2E | `PRODUCT-VALUE-01`, `PRODUCT-UX-01` |
| VR2 曖昧さネイティブ作業 | 保留/違和感/根拠不足/反対意見を作業状態化 | Hold/Critique/Evidence/Contradiction、ContextBundle制約 | 4状態の付与・絞り込み・共有前確認 | `PRODUCT-VALUE-02`, `DOMAIN-EXPR-01..04`（`ADR-0040`）, `CE1`, `CE2` |
| VR3 レビュー可能成果物 | 読者が確定/保留/根拠を理解 | Narrative、Review Pack、review attribution、source trace | 成果物最小6要素 + 安全共有 | `PRODUCT-VALUE-03`, `PRODUCT-UX-03`, `CE3` |
| VR4 価値観測と製品化ゲート | 価値実感を再現可能に観測 | 観測ハーネス、二軸スコアカード（`ADR-0037`） | 証拠再現性、Go/No-Go追跡 | `VALUE-MEASURE-01/02`, `MVP-EXIT-01`, `PRODUCT-QA-01` |
| VR5 社会的普及 | 説明可能な合意が再現・見直し・安全配布される | 複数レビュア再現性、経時的見直し、証拠定着配布、非監視シグナル（`ADR-0038`） | 再現性/再オープン/配布安全/非監視の各観点 | `SOCIAL-DIFFUSION-01..04`, `CE4` |

VR系列は既存フェーズ体系（CE/FB/PRODUCT-UX）を置換せず、価値軸で再配置する索引です。新規作業は VR4（`ADR-0037`）と VR5（`ADR-0038`）に限定されます。

なお VR4/VR5 は `ADR-0039`（ガバナンス適正化）により activation を延期し、個人OSS・プレリリース段階では direction として保持します（VR0–VR3 と安全不変条件は active）。

---

## 2.4 要件被覆マトリクス（プロダクト価値 / UI/UX / ドメイン表現）

社会的目標の達成に必要な「プロダクト価値・UI/UX・ドメイン表現」要件が、フェーズ（VR）と担当issue/ADRへ過不足なく接続されていることを確認する被覆表です。**未接続セルが0件であることを「要件を上げ切った」状態の定義とします。** 新規起票は、この表に新しい行（本物の穴）が現れたときのみ行い、物量での追加はしません（`ADR-0039` 適正化方針）。

| 観点 | 要件の核 | 上流 | 担当（issue / ADR） | 状態 |
|---|---|---|---|---|
| 価値: 開始 | 迷わず最初の意味ある配置へ | `ADR-0032` V0/V1 | `PRODUCT-UX-01`(Done), `PRODUCT-VALUE-01` | 被覆 |
| 価値: 外在化 | メモ・違和感をカード化 | `ADR-0032` V1 | `PRODUCT-VALUE-01`, `DOMAIN-EXPR-01` | 被覆 |
| 価値: 定性情報の品質 | 意味・意図を保ち、一枚一中心、再文脈化・遡及可能なカードを低負担で作る | `qualitative_card_quality_requirements.md`, `ADR-0001` P-08 | `DOMAIN-CARD-QUALITY-01` | 被覆（自己確認、前後比較、原文復元を実装・E2E確認済み） |
| 価値: 反復的探究 | 6ラウンドを経験と思考の往復として扱い、中間成果・引継ぎ・分岐を保持する | `w_type_iterative_inquiry_requirements.md`, `ADR-0057`, `inquiry_journey_model.md` | `DOMAIN-W-ITERATION-01`, `PERF-INQUIRY-01` | 被覆（現在文書からの開始、反復snapshot、ローカルファイル保存・再開、代表容量を検証済み。比較・引継ぎ・読込非ブロッキング化はL0/未実装） |
| 価値: 構造化 | まとまり・関係・未整理の同時保持 | `ADR-0032` V2 | `PRODUCT-UX-02`(Done), `PRODUCT-VALUE-02` | 被覆 |
| 価値: レビュー | AI候補の人間採否・proposal-only | `ADR-0032` V3 | `PRODUCT-VALUE-02`, `CE2`, `CE3` | 被覆 |
| 価値: 成果物化と共有 | 確定/保留/根拠/未レビューを束ねた成果物 | `ADR-0032` V4 | `PRODUCT-UX-03`(Done), `PRODUCT-VALUE-03` | 被覆 |
| 価値: 観測と社会的普及 | 価値の再現観測・説明可能な合意の普及 | `ADR-0036`/`0037`/`0038` | `VALUE-MEASURE-01/02`, `SOCIAL-DIFFUSION-01..04` | 被覆（VR4/VR5は延期保持） |
| UI/UX: 初回導線 | 文書入口・SafeMode可視 | `ADR-0031` | `PRODUCT-UX-01`(Done) | 被覆 |
| UI/UX: 画面情報設計 | 選択コンテキスト・作業モード分離 | `ADR-0031` | `PRODUCT-UX-02`(Done), `UX-NAV-01`(Done), `UX-OPERABILITY-03/05` | 被覆 |
| UI/UX: 視点制御 | 俯瞰↔詳細・折りたたみ・focus・preset | `ADR-0001` P-06 | `ViewControlsPanel.tsx` ほか実装済み, `CE3` presets | 被覆（実装済み） |
| UI/UX: 操作性 | ポインタ/キーボード・パネル離脱・焦点 | `ADR-0030` | `UX-OPERABILITY-01..05`(Done系) | 被覆 |
| UI/UX: 共有導線 | 共有前確認・公開範囲・SafeMode | `ADR-0031` | `PRODUCT-UX-03`(Done) | 被覆 |
| UI/UX: 応答性/規模 | 小画面・大規模文書・低速環境 | `ADR-0031` | `PRODUCT-UX-04`(Done) | 被覆 |
| ドメイン: 状態の可視化 | claimType/reviewState/根拠/違和感の読取 | `domain.md`, `ADR-0040` | `DOMAIN-EXPR-01`（Phase 1, schema非依存） | 被覆 |
| ドメイン: 保留・未統合 | HoldState / Pending-Shelf の第一級化 | `domain.md`, `ADR-0001` P-01 | `DOMAIN-EXPR-02`（Phase 2, 加算schema） | 被覆 |
| ドメイン: 違和感→再提案 | Critique入力と再提案差分 | `domain.md`, `ADR-0001` P-04 | `DOMAIN-EXPR-03`（Phase 3） | 被覆 |
| ドメイン: 根拠・主張・矛盾 | Evidence/ClaimType/Contradictionのレビュー | `ai_cognitive_externalization_requirements.md` | `DOMAIN-EXPR-04`（Phase 4） | 被覆 |
| ドメイン: 出典・主体メタ | 通し番号/原データ遡及と、起票者/作成者などの主体メタを区別する | `schemas.md`, `review_attribution.md`, `ADR-0048` | `DOMAIN-TRACE-01`（通し番号・出典）, `CARD-META-UI-01`（起票者などのUI/保存/redaction境界） | 被覆（主体メタはDraft境界。実装時はADR要否を再確認） |
| ドメイン: 可逆性 | 配置やり直し・履歴・差分 | `domain.md`（可逆性） | snapshot/diff（`ADR-0032`基盤）, `summary_history_ops`, HIL-RS, `CE3` | 被覆（MVPはsnapshot基盤。汎用undoは`architecture.md`§10非目標） |
| ドメイン: 用語整合 | 00↔02語彙同期 | `domain.md` | `DOMAIN-ALIGN-01`(Done) | 被覆 |

**判定（2026-06-02）**: 全観点が担当issue/ADRへ接続済み（未接続=0件）。プロダクト価値・UI/UX・ドメイン表現の要件は VR0–VR5 のフェーズへ落とし込み済みであり、新規起票すべき本物の穴は無い。実装順序は DOMAIN-EXPR は Phase 1→4、VR4/VR5 は実ユーザー/協力者参加まで延期（`ADR-0039`）。

**更新（2026-07-15）**: カード作成後の構造化は被覆されていた一方、構造化の入力となる定性情報そのものの品質と、品質確保時の利用者負担が未定義だった。この穴を P-08 と `DOMAIN-CARD-QUALITY-01` へ接続し、未接続=0件へ戻した。

**更新（2026-07-18）**: `DOMAIN-CARD-QUALITY-01` は、本文だけの一回保存、非モーダルな自己確認、編集前後の比較、原文復元を実装し、マウス・キーボード・390pxを含むE2Eで確認してDoneとした。LLMによるPhase C提案は、手動編集の負担が継続利用を妨げる実利用証跡が得られるまで追加しない。

**更新（2026-07-15・反復的探究）**: 一つの文書内での構造化は被覆されていた一方、6ラウンド累積KJ法で中間成果を累積し、現場と往復し、前段階へ分岐する長期探究は未定義だった。広域比較の結果、`ADR-0057` は独立 `InquiryJourneyV1` + 不変 `RoundSnapshotV1` DAG + 自己完結bundleを採択した。要件・設計判断は確定したが、実装・移行・運用CRUDは `L0: Planned` であり、`DOMAIN-W-ITERATION-01` のfixture・操作模型検証を経ずにbackend永続化へ進まない。

**更新（2026-07-18・ローカルbundle）**: `DOMAIN-W-ITERATION-01` は自己完結bundleのstrict export/importと内容由来digest検証を実装した。これはローカル成果物のI/O境界を固定するもので、保存・再読込、画面操作、保持・削除、SafeMode派生共有は未実装のため、support levelは`L0: Planned`を維持する。

**更新（2026-07-18・保存と再開）**: 高度機能内で現在文書から正式な探究bundleを開始し、反復ごとの不変snapshotと低負担なカード系譜を記録し、JSONファイルへ保存・再読込できるようにした。この時点では比較、再開ブリーフ、引継ぎ、容量計測、SafeMode派生共有が未実装であったため、support levelは`L0: Planned`を維持した。

**更新（2026-07-18・代表容量）**: 300カード・30島・6ラウンドの1成果は73,955 bytes、探究manifestは2,161 bytes、自己完結bundleは1,460,390 bytesで、JSON集約の容量は5MiB回帰上限以内だった。画面読込の最大長時間タスクは243から273ms（それ以前の実行294ms）で100ms目安を超えたため、`PERF-INQUIRY-01`の非ブロッキング化をPhase 3への停止条件とし、support levelは`L0: Planned`を維持する。

---

## 2.5 根幹価値の不変条件（CVI）正本対応表（`ADR-0041`）

機能が出揃った段階で根幹価値を守るため、非後退の不変条件を ID 付きで固定する。本表を CVI の正本とし、`ADR-0041` の「単一の砦」テスト（`CORE-VALUE-GUARD-01`）は各 CVI をこの表へ参照づける（実装の散在テストを索引化し、欠落のみ新規カバー）。

| CVI ID | 不変条件 | 主な担保（既存テスト/契約） |
|---|---|---|
| CVI-1 | SafeMode 既定ON・共有/exportで未レビュー本文を漏らさない | `domain/policy/safe_mode.test.ts`, `ui/safe_mode_status.test.ts` |
| CVI-2 | proposal-only（auto-apply/confirm/publish 禁止） | `domain/ce2_proposal_only.test.ts`, backend `test_ce2_proposal_api.py` |
| CVI-3 | `human_reviewed` 昇格は人手のみ（AI/worker/API 自動禁止） | `domain/ce2_suggestion_candidates.test.ts`, `hil_rs_contract.test.ts` |
| CVI-4 | Consensus 直接更新禁止（`patch + approval` のみ） | CE0 契約テスト群（`ce0_core_graph_repositioning`） |
| CVI-5 | `dryRun=true` 無副作用（永続化/共有/昇格なし） | backend `test_audit.py`, `routes/context.py` 契約 |
| CVI-6 | `KJ_ATLAS_LLM_PROVIDER=none` 既定でも主要価値が成立 | provider `NoneProvider` + 既定構成E2E |
| CVI-7 | 保留/違和感の非破壊・表示制御と内容削除の分離 | collapse/visibility テスト, `state_filter`（hidden≠delete） |

## 2.6 認知負荷を守る複雑性予算（`ADR-0043`）

機能追加が根幹価値（思考を雑にしない）を侵さないための予算。詳細は `ADR-0043`。

- CB-1 既定の静けさ（初期表示の主要操作を限定、高度機能は progressive disclosure 背後）。
- CB-2 保留の容易さ最優先（保留/違和感が確定操作より遠くならない）。
- CB-3 追加は置換/包含/モード分離で（初期表示の常設要素を純増させない）。
- CB-4 可逆の明示（取り消し導線が同じ文脈に）。
- UI系issueは「複雑性予算」1行を自己申告し、悪化時は価値ゲート（`PRODUCT-QA-01`）で確認する。

---

## 2.7 UI/UX品質次元（UQ）正本対応表（`ADR-0044`）

UI/UX 品質を次元（UQ）で定義し、各次元の担保（既存テスト）と充足度を索引化する。本表を UQ の正本とし、薄い／未の次元のみを改善 issue 化する（物量網羅はしない、`ADR-0039`）。

| UQ ID | 品質次元 | 主な担保（既存テスト） | 充足度 |
|---|---|---|---|
| UQ-1 | 操作到達性（ポインタ/キーボード両対応・フォーカス順序） | `ui/ux_operability_regression.test.ts`, e2e `canvas_focus_order` / `keyboard_release_candidate_flow` | おおむね充足 |
| UQ-2 | アクセシビリティ（role/aria/ラベル） | `canvas/IslandView.accessibility.test.ts` + `canvas/CardView.accessibility.test.ts` + `ui/DomainStateSummary.accessibility.test.ts` + `ui/ShelfPanel.accessibility.test.ts` + `ui/StartPanel.accessibility.test.ts`（計5ファイル, 28 tests） | **改善中**（2026-06-21: 1→5ファイル, `UI-QUALITY-A11Y-01` 追跡中） |
| UQ-3 | 国際化等価性（ja/enキー一致・ハードコード無・未訳ゼロ） | `src/i18n/` 9テスト＋`ui/i18n_equivalence.integration.test.ts` | 充足 |
| UQ-4 | レイアウト堅牢性（代表viewport・大規模文書） | e2e `header_toolbar_layout` / `large_document_operability` | おおむね充足 |
| UQ-5 | 状態の可視性（待機/読取専用/SafeMode/選択対象） | `ui/safe_mode_status.test.ts`, selection-context contract | おおむね充足 |
| UQ-6 | 認知負荷の節度（初期の静けさ・保留の容易さ） | 複雑性予算（§2.6, `ADR-0043`）＋UX回帰アンカー | 運用で担保 |

**判定（2026-06-10）**: UQ-3 充足、UQ-1/4/5/6 はおおむね充足。**UQ-2（a11y）が薄い**＝UI/UX品質の最優先改善対象（`UI-QUALITY-A11Y-01` 候補）。UI を増やす issue は触れる UQ 次元を明記し、`ADR-0043` 複雑性予算1行と合わせて自己申告する。

**更新（2026-06-21）**: UQ-2 改善中。a11yテスト 1ファイル（IslandViewのみ）→ 5ファイル（+CardView, DomainStateSummary, ShelfPanel, StartPanel）、21→28 tests。`UI-QUALITY-A11Y-01` issueで追跡継続中。

**更新（2026-07-09）**: `UI-QUALITY-A11Y-01` の既存面拡充に続き、`UI-QUALITY-A11Y-02`（新設面への画面別a11y仕様適用）で選択コンテキスト（`aria-live=polite`＋読み上げ順 型→保持系→確認→根拠）と共有前確認（出典参照トグルの`aria-describedby`関連付け）を対応。一括操作バーは既存のグローバルホットキー機構（Escapeで選択解除）で仕様を充足済みと確認（コード変更なし）。e2e `a11y_selection_and_share_gate.spec.ts`（2 tests）を追加。凡例・作業モードタブの2面は対象外（凡例=並行編集中のため、作業モードタブ=`role=tablist`導入は`UX-NAV-01`が明示的に対象外とした設計判断を覆すためADR待ち）。`UI-QUALITY-A11Y-02` issueで残課題（凡例対応・作業モードタブのADR判断）を追跡継続中。

**更新（2026-07-10）**: 凡例は並行編集の完了を待つ必要がなくなったため、既存の `role="dialog"`・名称・Escape時フォーカス復帰を検証し、`a11y_axe_smoke.spec.ts` の検査対象へ追加した（8/8 passed）。作業モードタブの `role=tablist` 導入要否は、`UX-NAV-01`の完了方針と設計正本の差分を整理したうえで判断する。ADR-0052はキャンバス選択ロールとメニュー内フォームの意味付けに限定される。

**更新（2026-07-15）**: 作業モードタブは、5つの同格面を1つずつ表示するmanual-activation `role=tablist` として `ADR-0055` で受理した。`UX-NAV-02` の実装により、manual activation、Home/End、段階Escape、inactive panel状態保持、390px横スクロールをE2Eで確認済み。`ADR-0052` はキャンバスカードをbutton系操作へ移す判断と、メニュー内フォームをmenu外へ分離する判断としてAcceptedした。

---

## 2.8 応答性の性能予算（PB）（`ADR-0046`）

計算負荷の歯止め。`ADR-0043`（認知負荷の複雑性予算）と対をなし、根幹価値「思考を雑にしない（待たされて途切れない）」を計算軸で守る。詳細は `ADR-0046`。

- PB-1 代表規模（カード約300・島約30、超過しても degrade gracefully）。
- PB-2 初期表示は待機表示なしで数秒以内、超える場合は待機可視化。
- PB-3 メインスレッドを長時間（目安100ms超）ブロックしない＝worker化の判断基準。
- PB-4 対話操作（選択/パン/ズーム/フィルタ/保留トグル）は即応、重い再計算は debounce/メモ化/worker。
- PB-5 大規模・低速時は「反応なし」に見せず待機/進捗/キャンセルを提示（UQ-4/UQ-5 と一体）。
- 性能影響 issue は「性能予算」1行を申告し、悪化・100ms超未worker化は `PRODUCT-QA-01` で確認。代表規模fixtureで最小の性能アサーションを置く（回帰検知が目的）。

## 2.9 生成AIレーン境界（`GENAI-GOV-01`）

生成AI関連の作業は、ひとつの機能群としてではなく、データ境界と人間レビュー境界が異なるレーンとして扱う。新しいADR/issue/実装提案は、少なくとも次のどれに触れるかを明記する。

| Lane | 名前 | 主な正本 | 判断の要点 |
|---|---|---|---|
| A | 手動中核 / AI無効 | `ADR-0041`, 本書 CVI-6 | `KJ_ATLAS_LLM_PROVIDER=none` で開始、外在化、構造化、共有前確認の主要価値が成立することを守る。 |
| B | LLMProvider 経路 | `ADR-0009`, `llm_provider_spec.md`, `llm_escalation_policy.md` | kj-atlas 内部の provider 抽象で生成補助を行う。opt-in、proposal-only、暗黙の外部provider遷移禁止を守る。 |
| C | 外部エージェント成果物連携 | `ADR-0049`, `external_agent_collaboration_spec.md` | 人間が依頼パッケージを共有し、応答を import 境界で取り込む。kj-atlas は Tier 0/1 で外部エージェントを直接呼ばない。 |
| D | 将来の直接API/Agent連携 | `ADR-0049` Tier 2 予約, AUTH-* 系 | 認証、到達性、tenant境界、監査、費用制御、失敗時動作を決める新ADRなしに実装しない。 |

レーン横断で守る不変条件は次の通り。

- AI出力は提案であり、採用・確定・公開・`human_reviewed` 昇格は人間操作でのみ行う。
- SafeMode 既定ON、未レビュー本文の既定保護、共有前確認、import-sanitize 境界を後退させない。
- `queryCanonicalHash`、`bundleHash`、`baseDocSignature`、`proposalId`、`taskId` などの相関キーを監査連鎖へ接続する。
- 外部由来テキストに含まれる指示は、自動動作ではなく表示データとして扱う。
- `score` / `rank` / `confidence` / `priority` などの数値評価を、採否・レビュー済み化・優先度判断の正本にしない。
- 暗黙のエスカレーションを禁止する。Lane A/B の失敗が、設定や人間操作なしに外部provider、外部エージェント、直接API連携へ遷移してはならない。
- モデル品質評価、外部共有の許可、出力の採用、レビュー済み化は別々の判断であり、相互に代替しない。

この節は新しいAI経路を許可するものではない。生成AI関連の新規issueが対象Lane、データ境界、Go/No-Go、ADR要否を宣言できるようにするための索引である。Lane D、外部共有条件、provider fallback、SafeMode、`human_reviewed`、自動適用に触れる変更は、実装PRではなくADRまたは内部issueで先に扱う。

## 3. 設計判断の扱い

設計文書は、価値判断を再定義する場所ではありません。新しい要件や価値判断が必要になった場合は、先に `00_Prompt` または ADR で扱います。

一方で、既存の設計や実装が上流の価値に合っていない場合は、次の順で扱います。

1. 乖離箇所を内部 issue に記録する。
2. 要件や大方針に影響する場合は ADR を起票する。
3. 文書修正だけで整合できる場合は、正本と参照先を同じ PR で同期する。

---

## 4. 更新ルール

- 新しい主要設計文書を追加した場合は、`AGENTS.md` と本表を同期します。
- 価値判断を変える変更は、`02_Architecture` だけで完結させません。
- 受入条件を追加した場合は、検証観点にも対応する行を追加します。
