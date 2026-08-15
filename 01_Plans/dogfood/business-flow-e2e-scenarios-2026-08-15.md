# 標準業務フローの E2E 固定とローカルLLM縮退（ドッグフーディング iteration 41）

## 目的

ドッグフーディングのシナリオ（業態・想定人物・業務領域・操作内容・注意事項）をイテレーションごとに
拡大していき、**固定したい標準的な業務フローは E2E として固定**する。その E2E は
**課金要素のないローカルLLM（モック）へ縮退可能**な構成にする（DeepSeek 等の課金APIに依存しない）。

## 標準業務フロー（初回固定・定性調査アナリスト）

| 軸 | 内容 |
|----|------|
| 業態 | 調査会社（定性調査） |
| 想定人物 | 定性調査アナリスト |
| 業務領域 | インタビュー発言の KJ 法による島化・表札・ナラティブ |
| 操作内容 | 文書作成 → カード確認（レビュー済み化）→ 文面整え（refine）→ 島の表札 AI 提案 → ナラティブ草稿 → 読戻し |
| 注意事項 | SafeMode で未レビュー文は LLM へ送られない（422）。AI 使用前にカードをレビュー済みにする |

次回以降のイテレーションで、この表を軸に**別の業態・人物・領域・操作・注意事項**を追加していく。

### シナリオ2（iteration 42 追加・新規事業企画ワークショップ）

| 軸 | 内容 |
|----|------|
| 業態 | 事業企画コンサルティング |
| 想定人物 | ファシリテーター（新規事業ワークショップ） |
| 業務領域 | 参加者のアイデア発言を KJ 法で構造化（カード→グループ→島） |
| 操作内容 | 文書作成 → 発言カード化 → **suggest-card-groups（発言の束ね提案）** → 島の表札（island-summary） |
| 注意事項 | refine 等の文面変更で参加者の意図を変えない（モックは元文面を保持） |

シナリオ1（定性調査アナリスト）は refine/island-summary/narrative を、シナリオ2（ファシリテーター）は
suggest-card-groups を追加で固定しており、**AI 操作のカバー領域もシナリオ毎に拡大**している。

### シナリオ3（iteration 44 追加・カスタマーサポート品質管理）

| 軸 | 内容 |
|----|------|
| 業態 | カスタマーサポートセンター（製造業の品質管理） |
| 想定人物 | サポート品質マネージャー（クレーム・現場証言の真因分析） |
| 業務領域 | クレームと現場証言の KJ 整理、矛盾する証言の検出による真因分析 |
| 操作内容 | 文書作成 → 証言カード化（レビュー済み） → **detect-contradiction（証言間の論理的矛盾を AI 検出）** → 島の表札（island-summary） → 読戻し |
| 注意事項 | 矛盾検出は「単なる意見の相違」と「論理的矛盾」を区別する（後者のみ報告）。証言の文面は refine 等で変更しない（現場の完全性・evidence としての位置づけ）。文書非依存ルートも `textReviewed` で未レビュー本文を 422 拒否する（SEC-AI-SAFEMODE-02、iteration 45 で実装） |

シナリオ1〜3で **refine / island-summary / narrative / suggest-card-groups / detect-contradiction** と
AI 操作のカバー領域を拡大しており、業態・想定人物も調査会社→事業企画コンサル→品質管理へ広がっている。

### シナリオ4（iteration 45 追加・個人OSS管理者のCLI/API運用）

| 軸 | 内容 |
|----|------|
| 業態 | 個人OSSソフトウェア運用 |
| 想定人物 | 運用管理者（自前スクリプトを書く） |
| 業務領域 | 文書ライフサイクルと管理面の API 運用（Web を介さない CLI/API 経路） |
| 操作内容 | 文書一覧(GET /docs) → 文書作成(PUT) → アーカイブ(POST archive) → アーカイブ中書込の **423** 確認 → 解除(unarchive) → 解除後書込 → 管理面監査の照会(GET /admin/provision/audit) → **キー分離**の確認 |
| 注意事項 | 管理面（/admin/*）は業務キー（X-API-Key）では到達不可。専用キー（X-Admin-Api-Key）で control-plane 認可を通す。アーカイブ文書は読み取り専用（PUT 423・GET 可）。監査は fail-open で記録され control-plane 認可でのみ照会できる |

シナリオ4は **非Web経路（管理者が自前スクリプトで CLI/API を利用）** を業務フローとして固定した点で、
シナリオ1〜3（Web を想定した AI 操作）と並ぶ 4 本目の固定である。`verify_admin_ops_flow_e2e.sh` が
業務キー＋管理キー両方設定の実バックエンド上で **11/11 pass**。文書ライフサイクル（第2反復・ADR-0073）と
管理面監査（SEC-ADMIN-PLANE-03）・キー分離（SEC-ADMIN-PLANE-02）を一気通貫で検証する。

### シナリオ5（iteration 46 追加・報道・編集のナラティブA/B照合）

| 軸 | 内容 |
|----|------|
| 業態 | 報道・メディア（論説・編集） |
| 想定人物 | 編集者（ナラティブの正確性を検証） |
| 業務領域 | カード（事実）とナラティブ草稿の A/B 照合による整合性検証 |
| 操作内容 | 文書作成 → カードレビュー済み化 → ナラティブ草稿（generate-narrative） → **check-narrative（A/B照合: カードにない主張・触れていない島を検出）** → 読戻し |
| 注意事項 | ナラティブはカードの事実を超える主張をしない。check-narrative は `direction`（b_missing_in_a / a_missing_in_b）で不整合を報告する。未レビューカードを含む文書はナラティブ経路で 422（SafeMode） |

シナリオ5は **check-narrative（A/B照合）** を固定した点で、AI 操作のカバー領域を
**refine / island-summary / narrative / card-groups / detect-contradiction / check-narrative** の 6 操作に
拡大した。業態・人物も調査会社→コンサル→品質管理→OSS管理者→報道編集へ広がっている。
**19/19 pass**。

### シナリオ6（iteration 47 追加・調査研究員のW型探究）

| 軸 | 内容 |
|----|------|
| 業態 | 調査・研究（社会科学 / 市場調査） |
| 想定人物 | 調査研究員（W型探究でラウンドを重ねる） |
| 業務領域 | 複数ラウンドの探究ジャーニー（問いの深化）の保存・継続・並行編集の保護 |
| 操作内容 | ジャーニー開始(POST If-None-Match:*) → 読戻し(GET) → **ラウンド深化(POST If-Match 更新)** → **並行編集の検出(古い If-Match → 409)** → 破棄(DELETE If-Match) |
| 注意事項 | inquiry-bundle は **CAS（If-Match/If-None-Match）で楽観的並行制御**。前条件なしは 428、並行更新は 409、**破棄も現在の ETag が必要**。ラウンドの不変条件（iteration 単調）はクライアント責務 |

シナリオ6は **W型探究（DOMAIN-W-ITERATION-01・アプリの差別化価値）** を業務フローとして固定した。
`verify_api_inquiry_journey.sh`（機械的な opaque round-trip）とは別に、**探究の進行＝ラウンド追加の更新**と
**並行編集の保護（409）・破棄のCAS** を一気通貫で検証する。**26/26 pass**（シナリオ1〜6）。

### シナリオ7（iteration 48 追加・学術研究の概念関係要約）

| 軸 | 内容 |
|----|------|
| 業態 | 学術研究 / ナレッジマネジメント |
| 想定人物 | 研究者（概念間の関係を構造化する） |
| 業務領域 | 複数概念（島）間の関係の要約・根拠付き接続 |
| 操作内容 | 文書作成 → 島形成 → **summarize-island-relation（島間関係の要約）** → 読戻し |
| 注意事項 | 関係種別は5語彙（related/negate/causal/mutual/equivalence）。derived=false は根拠ある関係のみ要約。未レビューカードは 422（SafeMode） |

シナリオ7は **summarize-island-relation** を固定。E2E 実走行で本ルートが SafeMode ゲート未配線（doc文脈なのに `_reject_unreviewed_text` なし）であることを発見し、SEC-AI-SAFEMODE-02 拡張として修正・**全コンテンツAIルートのカバレッジカナリア**を追加（詳細は dogfood README）。

### シナリオ8（iteration 49 追加・ナレッジベース管理者のタイトル命名）

| 軸 | 内容 |
|----|------|
| 業態 | ナレッジマネジメント / 図書館情報学 |
| 想定人物 | ナレッジベース管理者（文書の検索性を確保する） |
| 業務領域 | 文書タイトルの命名・改名（検索・整理の要） |
| 操作内容 | 文書作成 → 島・カード確認 → **suggest-document-title（タイトル候補のAI提案）** → 読戻し |
| 注意事項 | タイトル候補は proposal であり自動確定しない。未レビュー入力は textReviewed fail-closed で 422（SEC-AI-SAFEMODE-02） |

シナリオ8は **suggest-document-title**（最後の未固定 AI 操作）を固定。モックLLMに `suggest_document_title` 応答を追加。
これで **AI 操作 8 種（refine / card-groups / island-summary / narrative / detect-contradiction / check-narrative / island-relation / document-title）を全カバー**。
**32/32 pass**（シナリオ1〜8・8業態）。

### シナリオ9（iteration 50 追加・人事マネージャーのAI提案レビュー）

| 軸 | 内容 |
|----|------|
| 業態 | 人事・人材開発 |
| 想定人物 | 人事マネージャー（360度評価のとりまとめ） |
| 業務領域 | AI提案（島要約）のレビューと採択/保留決定（value_traceability V3） |
| 操作内容 | 文書作成 → **propose-island-summary（AI提案・proposal-only）** → 提案の受領 → **record-decision（採択・idempotencyKey）** → 再送の冪等確認 → 未登録提案への決定が 404 → **文書が自動適用されない**ことを確認 |
| 注意事項 | 提案は **proposal-only（自動適用なし・人間の決定が必須）**。決定は idempotencyKey で再送しても重複記録しない（ただし **理由まで同一ペイロード** を要求・409で検出）。未登録 proposal への決定は 404。レビューアは認証済み identity（`x-forwarded-user`＋JIT）で server が解決 |

シナリオ9は **CE4 proposal 連鎖（proposal-only → 人間決定 → 監査）** を固定。`value_traceability.md` V3（レビュー価値）の中核 =「AI が人間の判断を先取りしない」を E2E で保証する。
実走行で **`mock:` プレフィックス付き bundle hash の契約不整合**（API は許可・DB は拒否）を発見し `DATA-CONTRACT-02` を起票。
**39/39 pass**（シナリオ1〜9・9業態）。

### シナリオ10（iteration 52 追加・フィールドワーカーのW型探究 × AI支援）

| 軸 | 内容 |
|----|------|
| 業態 | 社会調査・フィールドワーク |
| 想定人物 | フィールドワーカー（現地調査） |
| 業務領域 | フィールドノートの KJ 整理と探究ジャーニー（W型）への保存 |
| 操作内容 | ノートをカード化(PUT) → **AI束ね(suggest-card-groups)** → **島要約(suggest-island-summary)** → **ジャーニー保存(inquiry-bundle create)** → 読戻し → 破棄 |
| 注意事項 | ノートは逐語（refine で変えない）。ジャーニーは CAS（If-Match/If-None-Match）で並行編集を保護。未レビューカードは AI 経路で 422（SafeMode） |

シナリオ10は **AI 支援（束ね・島要約）と W型探究ジャーニー保存を組み合わせた複合フロー**を固定した。
フィールドノートを AI で整理 → その整理済み文書を snapshot として inquiry-bundle に保存、という
実際の調査ワークフローを一気通貫で検証する（アプリの二つの差別化価値の統合）。**45/45 pass**（シナリオ1〜10・10業態）。

### シナリオ11（iteration 53 追加・会議ファシリテーターの配置・統合提案）

| 軸 | 内容 |
|----|------|
| 業態 | オンライン会議ファシリテーション |
| 想定人物 | ファシリテーター（多人数の議事を整理） |
| 業務領域 | 議事カードの配置提案（suggest-layout）と島統合提案（suggest-merges） |
| 操作内容 | 文書作成 → **suggest-layout（配置のAI提案）** → **suggest-merges（島統合のAI提案）** → 読戻し |
| 注意事項 | 配置・統合は提案であり自動適用しない。未レビューカードは 422（SafeMode） |

シナリオ11は最後の未固定 AI 操作 **suggest-layout / suggest-merges** を固定し、**AI タスク全10種**（re_layout / suggest_merges / island-summary / island-relation / narrative / check-narrative / refine / card-groups / detect-contradiction / document-title）を E2E で全カバーした。**49/49 pass**（シナリオ1〜11・11業態）。

### シナリオ12（iteration 56 追加・ライブラリアンのコレクション管理）

| 軸 | 内容 |
|----|------|
| 業態 | ナレッジベース・図書館（コレクション管理） |
| 想定人物 | ライブラリアン（文書コレクションの管理者） |
| 業務領域 | 複数文書の作成・一覧・作成者絞り込み・アーカイブ管理 |
| 操作内容 | 複数文書作成(PUT ×N) → 一覧(GET /docs) → **自分の文書で絞り込み(GET /docs?createdBy=)** → アーカイブ → 一覧に反映確認 |
| 注意事項 | 一覧はメタデータのみ（カード本文非露出）。`created_by` は JIT 解決された **UUID**（ヘッダー値ではない）。アーカイブ文書は読み取り専用（PUT 423） |

シナリオ12は **複数文書のコレクション運用**（一覧・`createdBy` 絞り込み・アーカイブ反映）を固定。シナリオ4（単一文書のライフサイクル＋管理面）とは異なり、**文書集合の管理**を検証する。`created_by` が JIT 解決 UUID であることを実走行で確認し、「自分の文書」セマンティクス（frontend の principalId 相当）を固定。**55/55 pass**（シナリオ1〜12・12業態）。

### シナリオ13（iteration 58 追加・共同編集者の楽観的並行制御）

| 軸 | 内容 |
|----|------|
| 業態 | コンサルティングファーム（共同編集） |
| 想定人物 | 共同編集者A/B（同一文書を並行編集） |
| 業務領域 | 文書の並行編集と競合検出（lost-update 防止・ADR-0076 サーバ権威 LWW+CAS） |
| 操作内容 | 文書作成 → GET(ETag取得) → Aが編集PUT(If-Match) → Bが古いETagで編集PUT → **409(競合検出)** → 最新ETag再取得 → Bが再編集PUT → 200 |
| 注意事項 | ETag/If-Match で楽観的並行制御。stale な保存は 409 で拒否（部分保存なし）。競合検出後も文書は最新状態を保持 |

シナリオ13は **共同編集の楽観的並行制御（ETag/If-Match）** を業務フローとして固定。`verify_api_write.sh` の機械的チェックとは別に、**複数編集者の並行作業における lost-update 防止**を一気通貫で検証する（ADR-0076 のサーバ権威 LWW + 既存 CAS の実地）。**61/61 pass**（シナリオ1〜13・13業態）。

### シナリオ14（iteration 59 追加・出版・コンテンツQAの内容上限検証）

| 軸 | 内容 |
|----|------|
| 業態 | 出版・コンテンツ制作（QA） |
| 想定人物 | コンテンツ品質担当（校正者） |
| 業務領域 | コンテンツ上限の検証と品質ゲート（DOMAIN-CARD-TEXT-01） |
| 操作内容 | カード本文2001文字→**422(上限違反)** → 2000文字で保存(200) → タイトル501文字→**422** → 500文字で保存(200) → 上限違反が構造化A1エラーで返ることを確認 |
| 注意事項 | 上限は API 境界で強制（カード本文2000・タイトル500・島要約2000）。違反は `errorEnvelope` の構造化 A1 エラーで返る |

シナリオ14は **コンテンツ上限の API 境界強制**（`verify_api_write.sh` の機械的チェックを業務フロー化）を、校正者による品質ゲートとして固定。**66/66 pass**（シナリオ1〜14・14業態）。

### シナリオ15（iteration 60 追加・編集者の統合決定ガバナンス）

| 軸 | 内容 |
|----|------|
| 業態 | 出版・編集（ナレッジ統合） |
| 想定人物 | 編集者（AIの統合提案を採否する） |
| 業務領域 | マージ提案の決定記録（traceability・監査）と復元ログ参照 |
| 操作内容 | 文書作成 → 統合決定を記録(POST merge-decision-logs) → **グループ別ログ確認(GET by-group)** → **復元ログ参照(GET restore)** → 重複決定が409 |
| 注意事項 | 決定は append のみ（更新不可・traceability の正本）。同一 `decisionId` は 409。action は accept/partial/reject/defer の enum |

シナリオ15は **マージ決定のガバナンス（記録・グループ別参照・復元ログ・決定の唯一性）** を固定。AI の統合提案（suggest-merges）に対する**人間の採否を append 専用ログとして残す** traceability の実地。**71/71 pass**（シナリオ1〜15・15業態）。

## E2E の固定方法

### バックエンド全層フロー（初回・curl ベース）

`03_Implement/backend/scripts/verify_business_flow_e2e.sh` が、モックLLM＋バックエンドを起動し、
上記業務フローをアサーション付きで実走行する（`bash scripts/verify_business_flow_e2e.sh [PORT]`）。

```
モックLLM(mock_local_llm.py) → バックエンド(KJ_ATLAS_LLM_PROVIDER=local) → フロー実走行
  PUT 文書 → GET 読戻し → refine-card-text → suggest-island-summary → generate-narrative
  → 未レビュー境界 422 の確認（SafeMode）
```

### UI 層 E2E（将来拡張）

フロントエンドの AI 操作は CE4 proposal 連鎖（query→bundle→proposal）を持つため、UI 層 E2E での
固定は将来のイテレーションで追加する。その際も `KJ_ATLAS_LLM_PROVIDER=local` のモックで駆動する。

## ローカルLLM縮退スイッチ

バックエンドの LLM プロバイダは設定で切り替える（DeepSeek 課金API → ローカルモック → 実ローカルLLM）。

| 設定 | 値 | 効果 |
|------|----|------|
| `KJ_ATLAS_LLM_PROVIDER` | `deepseek` | 課金API（`KJ_ATLAS_DEEPSEEK_API_KEY` 必須） |
| `KJ_ATLAS_LLM_PROVIDER` | `local` | ローカル/モック（`KJ_ATLAS_LOCAL_LLM_BASE_URL` で宛先指定） |
| `KJ_ATLAS_LLM_PROVIDER` | `none` | AI 無効（fail-closed） |

- **モック（GPU不要・決定的・無料）**: `deploy/tools/mock_local_llm.py` — `/generate` 契約で
  per-task の schema 準拠 canned 応答を返す。E2E の決定性に最適。
- **実ローカルLLM（例: Ollama）**: `KJ_ATLAS_LOCAL_LLM_BASE_URL` を差し替えるだけでよい
  （`/generate` 契約は同一・OpenAI 互換。小さい CPU モデルは strict JSON が不安定なため
  実業務ではモック/検証用途で利用）。

## 実行方法

```bash
# バックエンドの venv を使用
cd 03_Implement/backend
bash scripts/verify_business_flow_e2e.sh 8000   # 7 チェック（作成/読戻し/refine/表札/ナラティブ/未レビュー境界）
```

## 状態

- [x] バックエンド全層の標準業務フロー E2E を固定（**シナリオ1+2 で 10/10 pass**・モックLLM）
- [x] 別業態のシナリオ追加（iteration 42: 新規事業企画ワークショップ・suggest-card-groups を追加）
- [x] シナリオ3〜6（iteration 44〜47: 品質管理・detect-contradiction / 管理者CLI/API・文書ライフサイクル/監査/キー分離 / 報道編集・check-narrative / 調査研究員・W型探究 CAS）を追加
- [x] シナリオ7〜9（iteration 48〜50: 学術研究・summarize-island-relation / ナレッジベース管理者・suggest-document-title / 人事マネージャー・CE4 proposal 連鎖）を追加
- [x] シナリオ10〜14（iteration 52〜59: フィールドワーカー・W型×AI / 会議ファシリテーター・layout/merge / ライブラリアン・コレクション / 共同編集者・並行制御 / コンテンツQA・上限検証）・シナリオ15（iteration 60: 編集者・統合決定ガバナンス）を追加 — **シナリオ1〜15 で 71/71 pass・AI タスク全10種＋CE4＋W型×AI＋コレクション＋並行制御＋内容上限＋統合ガバナンスをカバー**
- [ ] UI 層 E2E（フロントエンド AI 操作・CE4 proposal 連鎖）
- [ ] さらに別業態のシナリオ追加（イテレーション毎に拡大）
