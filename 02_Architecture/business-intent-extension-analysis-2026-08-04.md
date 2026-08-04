# 業務意図基盤化提案の分析と段階計画（2026-08-04）

区分: 分析・計画（非正本）。外部提案「kj-atlasを生成AI企業の業務意図形成基盤へ拡張するための機能要件案」（2026-08-04、非正本）を、実装コードと既存ADR/issueへ突き合わせて評価し、実行可能な段階計画へ落としたもの。採否そのものはMaintainer判断であり、本書はその判断材料である。

検証範囲: `03_Implement/frontend/src`（型・エクスポート・SafeMode・探究）、`03_Implement/backend/src`、`02_Architecture/schemas.md`、`02_Architecture/value_traceability.md`、`01_Plans/adr/`（ADR-0039/0041/0043/0047/0048/0049/0054/0056/0057/0058）、関連issue。提案の「新規」主張は額面で受けず、実コードに当てて再判定した。

## 1. 結論

提案の**方向は既存資産と整合し、中核部分は取り組む価値がある**。ただし提案が想定する規模で着手するのは不適切であり、次の3点で形を変えるべきである。

1. **新規ADRは5本ではなく1本に集約する。** ADR-0047（Accepted）は設計判断ADRの新規起票を停止し、再起票基準R-1〜R-4のいずれかが成立した場合のみ許す。さらに非目標で「既存ADRの再掲・分割のための新規採番」を明示的に禁じている。提案の5本のうち4本は境界判断1本の帰結であり、分割起票はこの非目標に触れる。
2. **新規の永続集約は当面ゼロで始める。** 提案は5つの新規集約を想定するが、`InquiryJourneyV1`の前例（独立集約・DocumentV1非搭載・サーバ非永続・`L0: Planned`のまま長期滞留）が、永続集約の実コストを示している。Business Intent Packageは**review packと同じ「派生エクスポート」**として始められる。永続化は価値検証後に判断する。
3. **最初の一歩はコード0行の価値検証にする。** これは慎重さのためではなく、**ADR-0047のR-1トリガーを正当に成立させるため**である。実使用の摩擦を得る前にADRを起票すれば、それは同ADRが禁じる「念のため」の起票になる。ドッグフードを先に回すことが、後続の設計判断を authorize する唯一の筋道である。

## 2. 既存資産で既に満たされている部分（実測）

提案が新規契約として挙げた項目のうち、実際には既存の機構が大半を担っている。

| 提案項目 | 実際の状況 |
|---|---|
| Intent Packageの SafeMode秘匿・未レビュー除外・出力範囲プレビュー・パッケージハッシュ・schema version | **すべて既存機構として存在**。`domain/policy/safe_mode.ts`のSafeModePolicy、共有前確認ゲート、bundle export、review pack、`utils/fnv1a_hash.ts`。新規に作るのではなく再利用する対象である |
| 元カードへの系譜 | 既存。`EvidenceLink`、`Card.meta`（DOMAIN-TRACE-01、通し番号・原データ遡及、schemas.md §15）、`RoundSnapshotV1` DAG、ADR-0056がカード来歴メタデータの境界を既に固定 |
| W型ラウンドR1〜R6→意図出力の対応（提案§6.11） | ADR-0057の反復的探究モデルが既に同じ構造を持つ。**新規要件ではなく既存モデルへの索引付け** |
| Runtime Feedback Package（提案§6.8, Phase 4） | **EXT-CONN-02（Draft）とほぼ同一機構**。「外部エージェントの観察を`agent-response.v1`互換payloadでHTTP受信し、提案カード（未レビュー・自動確定なし・個別undo可）としてのみ着地させる」— 輸送と着地規律は既に契約済み。新規輸送ではなくpayload意味論の加算で足りる |
| 外部コンパイラ連携（提案§6.9, Phase 3） | 既存の`AgentTaskPackage/AgentResponse v1`（`export/agent_task_export.ts`・`import/agent_response_import.ts`）が実装済み。proposal-only着地・反スコアリング（`score/rank/confidence/priority`拒否）・サニタイズ・stale検知・orphaned保持まで動いている。**新規タスク種別の加算**で収まる |
| 意図差分レビュー（提案§6.10） | 差分基盤は既存（`diff/document_diff.ts`、`ReviewDiffPanel`、PatchWorkspace）。意味レベル差分という観点は新しいが、基盤は再利用可 |
| 業務概念辞書（提案§6.2） | ADR-0048がKJ語彙（claimType・関係種別・違和感タグ・holdState）をコード/ADR固定の非ユーザー編集語彙として確定済み。提案も同じ線を引いており衝突しない。ただし業務概念辞書そのものは新規 |

**Lane帰属の確認**: 提案の外部コンパイラ連携は GENAI-GOV-01 の **Lane C（外部エージェント成果物連携）** に収まり、Lane D（将来の直接連携）を開かない。既存ガバナンス構造の内側に留まる設計であり、この点は提案の強みである。

## 3. 真の差分（新規性があり、取り組む価値がある部分）

| # | 差分 | なぜkj-atlas固有の価値になるか |
|---|---|---|
| D1 | **Acceptance Example / 反例の第一級化** | `acceptanceExample`に相当する構造はフロントエンド全体に存在しない（grep確認）。自然言語を正本にする際の曖昧さを具体例で補う機構であり、既存の「観察と解釈を混同しない」原則の自然な延長 |
| D2 | **意図の型付き集約**（purpose / protectedValues / invariants / decisionCandidates / unresolvedQuestions） | カード・島は「意味の断片」を扱うが、「守るべきこと・未解決なこと」を項目単位でレビュー可能な単位として束ねる型は無い |
| D3 | **意味レベルの版差分** | 文書差分ではなく「意味上の約束の変化」を見る。業務変更の追跡という新しい用途 |
| D4 | **実行成果物への参照レジストリ** | 意図versionと外部生成物の対応。成果物本体は持たず参照だけを持つという境界設定が重要 |
| D5 | **未解決点を保持したまま外部へ渡せる出力形式** | これが提案全体の核心。既存のreview packは「読者向け成果物」だが、意図パッケージは「外部エージェント向けの実行前入力」であり、未解決・反証・保留を落とさずに渡す点が独自性 |

**最も価値が高いのはD5とD1**である。「曖昧さを保持したまま外部の実行系へ渡す」ことは、既存のどのエクスポート面もやっていない。D2/D3/D4はD5を成立させるための構造であり、単独では価値が薄い。

## 4. 衝突・前提（ガバナンスゲート）

| ゲート | 現状 | 提案への影響 |
|---|---|---|
| **ADR-0047 ADRモラトリアム** | Accepted。R-1〜R-4のみ起票許可。非目標で分割採番を禁止 | 5本→1本へ集約。R-3（既存予算・不変条件で覆えない境界の超過）が唯一の誠実なトリガー。ADR-0049が自身のContextで「ADR-0047のR-1に該当」と明示引用しており、これが正しい前例 |
| **GENAI-GOV-01（value_traceability.md §2.9）** | 「SafeMode、`human_reviewed`、外部共有条件、自動適用に触れる変更は、実装PRでなくADRまたは内部issueで先に扱う」 | 提案は外部共有条件と`human_reviewed`意味論の双方に触れる。**ADR先行はモラトリアムとは独立にこのルールからも要求される**。境界ADRの必要性はここで裏付けられる |
| **VR系列（value_traceability.md:112,114）** | 「新規作業はVR4とVR5に限定」、かつVR4/VR5はADR-0039により activation 延期中 | 提案Phase 5（組織・企業間）はVR5領域＝延期対象。提案自身も「実ユーザー・協力組織が得られるまで着手しない」としており整合 |
| **schemas.md version gate** | `DocumentV1`(version:1)がADR-0058により唯一の永続契約。加算原則（全optional）ならversion維持、非互換変更はversion:2＋別ADR先行が必須 | 提案の「DocumentV1へ入れない」判断は正しい。ADR-0057の前例（schemas.md:8）が「現行DocumentV1の型・version gate・保存契約へ履歴キーを追加しない」と明記。**R-4は成立しない**（加算で足りる） |
| **ADR-0043 複雑性予算 CB-1〜CB-4** | 初期表示への純増禁止、追加は置換・包含・モード分離、保留操作を遠くしない | 提案§8.1（企業機能は明示選択時のみ、通常キャンバス不変）が既に整合。issue本文に1行の自己申告が必要 |
| **CVI-1 の砦が挙動ベースでない** | `core_value_guard.test.ts`は`readSource(...)`＋`toContain(...)`でテストファイルの文字列を検査するのみ（実装確認済み） | **これが最大の残存リスク**。新しいエクスポート面（Intent Package MD+JSON）を追加しても、redaction忘れがあってもテストは緑のまま通る |
| SEC-EXPORT-BUNDLE-01（document.jsonのSafeMode迂回） | **Done**（P0、解消済み） | 当初懸念していた「P0未解消のまま新エクスポート面を追加する」問題は既に解消。ただしCVI-1の砦の弱さは残る |
| ADR-0049（外部エージェント連携） | **Status: Proposed**（Acceptedでない） | 提案Phase 3はこの契約の拡張に依存する。**未充足の前提**。Phase 3着手前にADR-0049のAccept判断が必要 |
| EXT-CONN-02 | Draft。ゲート＝EXT-CONN-01の運用実績＋D3 admin認可の実装/検証 | 提案Phase 4はこのゲートを継承する。別途landing済みの活性化シナリオ文書のT2-A（MCP外部頭脳クエリのドッグフード）がこのゲートを解除する最短経路 |

## 5. 落とす / 形を変えるべきもの

- **9段階の承認ラダー（提案§6.4）は内蔵しない。** 既存語彙は`reviewState: "unreviewed" | "human_reviewed"`と`HoldState`のみ。`agreed_for_trial`・`approved_for_compilation`・`approved_for_production`をkj-atlas内部状態にすると、OSS本体が組織承認の意味論を抱えることになる。提案自身も「OSS既定では正式な組織承認機構を内蔵しない」と述べており、**外部承認参照（ID・署名・外部システム参照）に限定**するのが一貫する。
- **実行方式比較（提案§6.5、11方式×12観点）は表形式にしない。** 12観点の一覧比較は事実上のスコアカードに退化しやすく、反スコアリング不変条件と緊張する。`decisionCandidates`に定性的なトレードオフ記述として添える形に留め、方式選択の理由を文章で残す。「システムを作らない案」を常に含める点は提案どおり維持する。
- **インターフェース投影候補（提案§6.12）は現段階では扱わない。** 実ユーザー不在での投影方式検討は予測に基づく設計になる。
- **組織・企業間関係表現（§6.13）と組織共有境界（§6.14）はVR5ゲート待ち。** 実利用事例が前提。
- **新規永続集約5つは当面作らない。** 派生エクスポートで始め、永続化はドッグフードが要求したときに判断する。

## 6. 段階計画

### Step 0: 価値検証（コード0行・最優先）

既存の実探究1件を題材に、意図パッケージを**手書きMarkdownで**作成し、既存のLane C手動経路（AgentTaskPackageの手動授受）で外部コーディングエージェントへ渡す。評価するのは生成物の質ではなく次の5点（提案§19.8）: 意図が伝わったか / 未解決事項が保持されたか / 前提が明示されたか / 元カードへ戻れたか / 人がレビュー可能だったか。

- 新規実装なし。既存のエクスポートと手動授受のみを使う。
- 成果物: ドッグフード記録（摩擦点の列挙）。
- **この記録がADR-0047のR-1トリガーを成立させ、Step 1以降の設計判断を authorize する。** 逆に、ここで価値が確認できなければ以降に進まない判断が正当化される。
- 提案§19.7（UIを作る前にMarkdown手動運用で価値検証する）と同じ主張であり、ADR-0042のドッグフード枠組みに乗る。

### Step 0.5: CVI-1の砦を挙動ベースへ格上げ（Step 2の前提）

新しいエクスポート面を追加する前に、全エクスポート面（bundle・review pack・inquiry bundle・将来の意図パッケージ）に対し「番兵秘密が生成物のどのファイルにも現れない」ことを挙動で検査する回帰を入れる。現状のソース文字列照合では、新面のredaction忘れを検出できない。

- 既存のアーキ整合性分析（`architecture-coherence-synthesis-2026-07-23.md`）の推奨項目と同一。
- Step 2の安全前提であり、Step 0とは並行可能。

### Step 1: 境界ADR 1本（Step 0の記録を根拠に）

内容: kj-atlasを意味の制御面に限定し実行面を持たない / 意図パッケージは派生エクスポートであり既存SafeMode・共有前確認に従う / 新規モデルはDocumentV1へ入れない / `human_reviewed`を超える承認は外部参照に限る / 非目標一覧。

- R-3を明示引用する（既存予算・不変条件で覆えない境界の超過）。ADR-0049の引用形式に倣う。
- GENAI-GOV-01 §2.9のADR先行ルールも根拠として記す。
- 代表ユースケースを**1件に絞る**（提案§19.2）。

### Step 2: 最小の意図パッケージ（派生エクスポート）

提案§18の最小実装に対応。目的・守る価値・不変条件・関係者・未解決事項・Acceptance Exampleの6項目のみ。各項目に元カード参照。項目単位の人間レビュー。Markdown＋JSON出力。

- 再利用: SafeModePolicy、共有前確認ゲート、既存の参照型（EvidenceLink・Card.meta）、ハッシュ、既存レビュー語彙。
- 新規: 6項目の型（派生のみ・非永続）、Acceptance Example、最小パネル1面（CB-3準拠で置換・包含）。
- AI無効（Lane A）で完結すること。AI候補はStep 3。

### Step 3: AI候補と意味差分（Lane B/C・proposal-only）

意図候補のAI提案（項目単位で採否）、複数案の並立、意味レベルの版差分。すべて未レビュー着地。

### Step 4: 外部コンパイラ連携（**ADR-0049のAccept待ち**）

既存AgentTaskPackageへ新タスク種別を加算する形で実装。応答は非信頼入力。元意図との逸脱差分。stale検知。kj-atlas内でコード実行しない。

### Step 5: Runtime Feedback（**EXT-CONN-01運用実績＋D3認可待ち**）

EXT-CONN-02の輸送・着地規律の上に、runtime-feedback意味論のpayloadを加算する。新規輸送は作らない。

### Step 6: 組織・企業間プロファイル（**VR5活性化待ち＝実ユーザー前提**）

着手しない。抽象契約の定義のみ先行可。

## 7. 優先順位（提案§14への対案）

| 優先 | 項目 | 提案との差分 |
|---|---|---|
| P0 | Step 0 ドッグフード（コード0行） | 提案はPhase 0を文書整備としたが、**実使用の記録を最優先**にする。R-1成立の前提 |
| P0 | Step 0.5 CVI-1砦の挙動化 | 提案に無い。新エクスポート面追加の安全前提 |
| P0 | 境界ADR 1本 | 提案の5本を1本へ集約 |
| P1 | 最小意図パッケージ（派生・非永続） | 提案は永続集約前提。派生から始める |
| P1 | Acceptance Example | 提案どおりP1。真の差分D1 |
| P2 | AI候補・意味差分 | 提案どおり |
| P2 | 外部コンパイラ契約 | ADR-0049 Accept が前提（提案は前提を明示していない） |
| P3 | Runtime Feedback | EXT-CONN-02のゲート継承 |
| 着手外 | 組織承認・企業間主体・実行方式比較表・インターフェース投影 | VR5延期／反スコアリング緊張／時期尚早 |

## 8. 評価指標

提案§17を支持する。件数・自動化率で評価しない。特に次を回帰で固定する。

- 元観察へ戻れる割合（系譜の完全性）
- 未解決事項が出力後も消失していないこと
- AI提案と人間合意が出力上で区別可能なこと
- SafeModeを迂回する出力経路が増えていないこと（Step 0.5の番兵検査で機械化）
- 通常KJ法利用の初期表示が純増していないこと（CB-1/CB-3の自己申告）

## 9. 判断待ち（Maintainer）

1. **この方向を採るか。** 本書は採否を決めない。Step 0はコード0行・既存機構のみで実施でき、採否判断の材料を最小コストで得られる設計にしてある。
2. **代表ユースケースを1件どれにするか。** 提案§15は新規事業の初回業務形成と既存業務のシステム剪定の2件を挙げる。後者は既存の実装済み機能に対する観察から始められるため、ドッグフードの題材としては着手しやすい。
3. **派生エクスポートで始める方針（本書§1-2）を受けるか。** 提案の永続集約前提を変更する提案であり、明示的な同意が要る。

## Traceability

- Related: 外部提案「kj-atlasを生成AI企業の業務意図形成基盤へ拡張するための機能要件案」（2026-08-04、非正本、リポジトリ外）
- Related: `01_Plans/adr/ADR-0047-design-decision-adr-saturation-and-execution-first.md`（ADRモラトリアムと再起票基準R-1..R-4）
- Related: `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`（過剰ガバナンス回避・再導入トリガー）
- Related: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`（Status: Proposed、Phase相当Step 4の前提）
- Related: `01_Plans/adr/ADR-0057-w-type-cumulative-inquiry-model.md`（独立集約の前例）
- Related: `01_Plans/adr/ADR-0058-document-contract-v1-rebaseline.md`（DocumentV1唯一契約）
- Related: `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`（CB-1..4）
- Related: `01_Plans/adr/ADR-0041-core-value-invariants-single-guard.md`（CVI-1..7）
- Related: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（KJ語彙の固定）
- Related: `01_Plans/adr/ADR-0056-card-provenance-metadata-boundary.md`（カード来歴メタデータ境界）
- Related: `02_Architecture/schemas.md`（version gate・加算原則）
- Related: `02_Architecture/value_traceability.md`（VR0..VR5、GENAI-GOV-01 Lane A..D）
- Related: `02_Architecture/external_agent_collaboration_spec.md`（AgentTaskPackage/AgentResponse v1）
- Related: `02_Architecture/architecture-coherence-synthesis-2026-07-23.md`（CVI-1砦の弱点）
- Related: `02_Architecture/activation-scenarios-requirements-2026-07-23.md`（T2-AがEXT-CONN-02ゲートを解除する経路）
- Related issues: `issue-EXT-CONN-01-readonly-mcp-server.md`, `issue-EXT-CONN-02-webhook-proposal-ingest.md`, `issue-SEC-EXPORT-BUNDLE-01-document-json-bypasses-safemode-redaction.md`（Done）, `issue-DOMAIN-W-ITERATION-01-w-type-cumulative-inquiry-support.md`
