# Dogfooding 検証マニフェスト（一か所集約）

- **目的**: ドッグフーディングの既存記録を一か所に集約し、**後から別の生成AIが検証できる**構造で提供する。
- **検証方法（2段階）**:
  1. **構造照合**: `bash 01_Plans/dogfood/verify_dogfood_records.sh` — 本マニフェストの構造的主張（ファイル存在・数値・算術・課題状態）をリポジトリ実体と自動照合する。
  2. **再現実行**: 本マニフェスト §2 の検証層コマンドを実行し、各層の期待結果を確認する（業務フローE2E・CIハーネス・単体テスト・UI E2E・計画文書整合）。

---

## 1. 現状サマリ（2026-08-16・iteration 197 時点）

| 指標 | 値 | 検証方法 |
|------|----|---------|
| 総シナリオ数（シナリオ1〜127） | 127 | §2.1 実走行＋`business-flow-e2e-scenarios-2026-08-15.md` |
| 業務フローE2Eスクリプトのシナリオヘッダ数 | 125 | verify script（シナリオ1=初期フロー・ヘッダechoなし / シナリオ4=別スクリプト`verify_admin_ops_flow_e2e.sh`） |
| カバー業態数 | 127 | シナリオドキュメント「カバレッジ集約」 |
| 業務フローE2Eチェック数 | 767 | §2.1 実走行 → `Result: 767 passed, 0 failed` |
| 総チェック数（check 10） | **818** | = 767（業務フロー）＋ 20（admin ops）＋ 7（kj multi-round）＋ 9（MCP CE-4 audit）＋ 15（CLI CE-4 audit）— 算術を verify script で照合 |
| 発行済み課題 | 21（AI-MODEL-GOVERNANCE-02 / OPS-LLM-COST-02 / DOGFOOD-11 / DOGFOOD-12 / DOGFOOD-13 / DOGFOOD-14 / DOGFOOD-15 / DOGFOOD-16 / DOGFOOD-17 / DOGFOOD-18 / DOGFOOD-19 / DOGFOOD-20 / DOGFOOD-21 / DOGFOOD-22 / DOGFOOD-23 / DOGFOOD-25 / DOGFOOD-26 / DOGFOOD-27 / DOGFOOD-28 / DOGFOOD-29 / DOGFOOD-30・**すべて Done**） | verify script |
| 検証層 | backend単体・frontend単体・frontend UI E2E・業務フローE2E・計画文書整合 | §2 |

> 注記: 総チェック数は**業務フローE2Eのチェック数（767）とは別**。CIハーネス `verify_all.sh` check 10 は5自己完結E2E（業務フロー・admin ops・kj multi-round・MCP CE-4 audit・CLI CE-4 audit）を実行するため、総数 = 818。以前の進捗報告で総数が誤記されていた差分（-10）は、本マニフェストの算術照合により検出・訂正された。iteration 195 の実走行照合で、並行編集者が拡張した admin ops（12→20・CLIモデルレジストリ運用追加）と MCP CE-4 audit（8→9）を実チェック数へ同期した。

---

## 2. 検証ハーネス（別の生成AIが再現実行する手順）

### 2.1 業務フローE2E（決定性モックLLM・課金なし）
```bash
cd 03_Implement/backend
bash scripts/verify_business_flow_e2e.sh 8005   # 期待: "Result: 767 passed, 0 failed"（シナリオ1〜127）
```
- 起点: `mock_local_llm.py`（GPU不要・決定的・`/generate` 契約）
- 固定対象: 業態×人物×領域×操作×注意事項の標準業務フロー

### 2.2 CIハーネス check 10（CI相当・専用ポート）
```bash
bash 03_Implement/backend/verify_all.sh
# check 10 ブロック: business-flow 8005 / admin ops 8006 / kj multi-round 8007
```

### 2.3 backend 単体テスト
```bash
cd 03_Implement/backend && .venv/bin/python -m pytest tests/ -q
# 期待（前回実走行）: 1160 passed, 36 skipped, 8 deselected
```

### 2.4 frontend 単体テスト
```bash
cd 03_Implement/frontend && npx vitest run
# 期待（前回実走行）: 1456 passed
```

### 2.5 frontend UI E2E（ドッグフーディングで固定した主要表面）
```bash
cd 03_Implement/frontend && npx playwright test \
  e2e/ce4_island_summary_proposal.spec.ts \
  e2e/opposing_viewpoint_proposal.spec.ts \
  e2e/narrative_ab_check.spec.ts \
  e2e/review_pack_state_preservation.spec.ts \
  e2e/ai_provider_status.spec.ts \
  e2e/island_title_warning.spec.ts
```

### 2.6 計画文書整合（docs_check）
```bash
python 01_Plans/docs_check.py   # 期待: "docs-check passed"
```

---

## 3. 成果物インデックス

| 成果物 | 役割 | 検証コマンド |
|--------|------|-------------|
| `03_Implement/backend/scripts/verify_business_flow_e2e.sh` | 業務フローE2E（シナリオ1〜127・767 checks） | §2.1 |
| `03_Implement/backend/scripts/verify_admin_ops_flow_e2e.sh` | 管理者CLI/API運用フロー（シナリオ4・20 checks・自前スクリプト＋CLIモデルレジストリ運用を含む） | §2.2 |
| `03_Implement/backend/scripts/verify_kj_multi_round.sh` | 人間×AI多ラウンド協調（7 checks） | §2.2 |
| `03_Implement/backend/scripts/verify_mcp_ce4_audit_e2e.py` | MCP read→CE-4監査（channel=mcp）→HTTPシンク到達の自己完結E2E（9 checks） | §2.2 |
| `03_Implement/backend/scripts/verify_cli_ce4_audit_e2e.py` | `kj` CLI→CE-4監査（channel=cli）→HTTPシンク到達の自己完結E2E（15 checks・全CE4ライフサイクル＋resolve-bundle） | §2.2 |
| `03_Implement/backend/verify_all.sh` | CIハーネス（check 10 配線） | §2.2 |
| `03_Implement/deploy/tools/mock_local_llm.py` | 決定性モックLLM（GPU不要） | §2.1 前提 |
| `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md` | シナリオ定義・カバレッジ集約（シナリオ127・チェック767） | §2.1 数値照合 |
| `01_Plans/dogfood/README.md` | イテレーション履歴ログ（iteration 1〜194） | 目視 / verify script |
| `01_Plans/dogfood/verify_dogfood_records.sh` | **本マニフェストの構造照合スクリプト** | 直接実行 |
| `03_Implement/frontend/e2e/ce4_island_summary_proposal.spec.ts` | CE4 proposal 連鎖のUI固定 | §2.5 |
| `03_Implement/frontend/e2e/opposing_viewpoint_proposal.spec.ts` | 反対視点・保留接続のUI固定 | §2.5 |
| `03_Implement/frontend/e2e/narrative_ab_check.spec.ts` | ナラティブA/B照合のUI固定 | §2.5 |
| `03_Implement/frontend/e2e/review_pack_state_preservation.spec.ts` | レビューパック作業状態保存（SOCIAL-DIFFUSION-01 土台） | §2.5 |
| `03_Implement/frontend/e2e/ai_provider_status.spec.ts` | プロバイダ状態・LLM呼び出し量のUI固定 | §2.5 |
| `03_Implement/frontend/e2e/island_title_warning.spec.ts` | 島タイトル警告のUI固定 | §2.5 |

---

## 4. 発行済み課題（ドッグフーディング観察由来）

| 課題 | 状態 | 観察起点 | 検証 |
|------|------|---------|------|
| `issue-AI-MODEL-GOVERNANCE-02-unregistered-model-rejected-under-platform-default.md` | **Done** | scenario 47 実装時の実走行（iteration 110） | `tests/test_model_governance.py` ＋ scenario 47 ②b（未登録→403 `model_not_registered`） |
| `issue-OPS-LLM-COST-02-llm-call-counts-ui-visibility.md` | **Done** | scenario 49 実装時の観察（iteration 114） | `e2e/ai_provider_status.spec.ts`（callCounts 表示） |
| `issue-DOGFOOD-11-contradiction-detection-lacks-deterministic-positive-path.md` | **Done** | scenario 106 実装時の実走行（iteration 176） | `mock_local_llm.py` の決定的正パス ＋ scenario 106 ③（矛盾検出 → `hasContradiction:true`） |
| `issue-DOGFOOD-12-check-narrative-positive-path-hardcodes-island-i1.md` | **Done** | scenario 107 実装時の実走行（iteration 177） | `mock_local_llm.py` の島ID動的解決 ＋ scenario 107 ⑤（A/B照合 → 島`dc-i`・`a_missing_in_b`） |
| `issue-DOGFOOD-13-island-summary-grounding-capped-at-three-cards.md` | **Done** | scenario 108 実装時の実走行（iteration 178） | `mock_local_llm.py` の全接地 ＋ scenario 108 ②（島要約 → `groundingIds:["w1","w2","w3","w4"]`） |
| `issue-DOGFOOD-14-check-narrative-lacks-b-missing-in-a-positive-path.md` | **Done** | scenario 109 実装時の実走行（iteration 179） | `mock_local_llm.py` の b_missing_in_a 正パス ＋ scenario 109 ⑤（A/B照合 → `direction:"b_missing_in_a"`・`bMissingInA:1`） |
| `issue-DOGFOOD-15-island-relation-summary-grounding-always-empty.md` | **Done** | scenario 110 実装時の実走行（iteration 180） | `mock_local_llm.py` の接地エコー ＋ scenario 110 ④（島間関係要約 → `groundingCardIds:["z4"]`） |
| `issue-DOGFOOD-16-refine-card-text-meaning-preservation-unverifiable.md` | **Done** | scenario 111 実装時の実走行（iteration 181） | `mock_local_llm.py` の入力埋め込み ＋ scenario 111 ①（文面整え → 元の意味「歩留まり」保持） |
| `issue-DOGFOOD-17-opposing-viewpoint-ignores-target-claim.md` | **Done** | scenario 112 実装時の実走行（iteration 182） | `mock_local_llm.py` の対象カード埋め込み ＋ scenario 112 ④（反対視点 → proposal-only・「訪問件数」参照） |
| `issue-DOGFOOD-18-title-suggestion-not-grounded-in-canvas-content.md` | **Done** | scenario 113 実装時の実走行（iteration 183） | `mock_local_llm.py` の島ラベル埋め込み ＋ scenario 113 ①（タイトル提案 → 文書テーマ「棚づくり」参照） |
| `issue-DOGFOOD-19-merge-suggestions-lack-deterministic-positive-path.md` | **Done** | scenario 114 実装時の実走行（iteration 184） | `mock_local_llm.py` の同カテゴリマージ提案 ＋ scenario 114 ①（統合提案 → カード対 a1/a2） |
| `issue-DOGFOOD-20-card-groups-not-theme-based.md` | **Done** | scenario 115 実装時の実走行（iteration 185） | `mock_local_llm.py` のカテゴリ別グループ化 ＋ scenario 115 ①（AI束ね → c1/c3・c2/c4 の同グループ化） |
| `issue-DOGFOOD-21-narrative-text-not-grounded-in-reading-order.md` | **Done** | scenario 116 実装時の実走行（iteration 186） | `mock_local_llm.py` の読み順島ID埋め込み ＋ scenario 116 ④（ナラティブ → 本文で「読み順（drg-i）」参照） |
| `issue-DOGFOOD-22-ce4-proposal-grounding-unverified.md` | **Done** | scenario 117 実装時の実走行（iteration 187） | scenario 117 ④（CE4提案 → proposal-only・`groundingIds:["h1","h2","h3","h4"]`） |
| `issue-DOGFOOD-23-layout-card-preservation-unverified.md` | **Done** | scenario 118 実装時の実走行（iteration 188） | scenario 118 ④（配置提案 → `suggestedDoc`・全カード d1〜d4 保持） |
| `issue-DOGFOOD-25-check-narrative-multi-island-omission.md` | **Done** | scenario 119 実装時の実走行（iteration 189） | `mock_local_llm.py` の全島報告 ＋ scenario 119 ⑤（A/B照合 → `aMissingInB:2`・fish-i 含む） |
| `issue-DOGFOOD-26-title-suggestion-first-island-bias.md` | **Done** | scenario 120 実装時の実走行（iteration 190） | `mock_local_llm.py` の全島ラベル埋め込み ＋ scenario 120 ④（タイトル提案 → 両島ラベル参照） |
| `issue-DOGFOOD-27-contradiction-explanation-not-grounded-in-pair.md` | **Done** | scenario 121 実装時の実走行（iteration 191） | `mock_local_llm.py` のカード対埋め込み ＋ scenario 121 ③（矛盾検出 → 説明文が両カード参照） |
| `issue-DOGFOOD-28-relation-summary-text-not-grounded-in-islands.md` | **Done** | scenario 122 実装時の実走行（iteration 192） | `mock_local_llm.py` の島A/B埋め込み ＋ scenario 122 ④（関係要約 → 本文が島cine-sched/cine-ops参照） |
| `issue-DOGFOOD-29-island-placard-text-not-grounded-in-theme.md` | **Done** | scenario 123 実装時の実走行（iteration 193） | `mock_local_llm.py` のテーマ抽出（\uXXXXデコード） ＋ scenario 123 ②（島要約 → 表札が顧客サービス参照） |
| `issue-DOGFOOD-30-layout-island-and-reading-order-preservation-unverified.md` | **Done** | scenario 124 実装時の実走行（iteration 194） | scenario 124 ④（配置提案 → `suggestedDoc`・islands・readingOrder 保持） |

---

## 5. イテレーション履歴（サマリ・詳細は README.md）

| 範囲 | 主な成果 |
|------|---------|
| iteration 107-109 | シナリオ45-47（教育・医療診断・モデルガバナンス）→ 259/259 |
| iteration 110 | **AI-MODEL-GOVERNANCE-02**（未登録モデル拒否・起票＋実装）→ 261/261 |
| iteration 111 | CE4 proposal 連鎖のUI層E2E → UI E2E 5/5 |
| iteration 112-113 | シナリオ48-49（美術館・IT運用監視）→ 273/273 |
| iteration 114 | **OPS-LLM-COST-02**（LLM呼び出し量UI可視化）→ frontend 1456 pass |
| iteration 115-119 | シナリオ50-54（小売EC・ゲーム・介護ヒヤリハット・交通・ファッション）→ 308/308 |
| iteration 120-125 | シナリオ55-59（NGO・自治体窓口・スポーツ・開発チーム・翻訳）→ 339/339 |
| iteration 121, 126 | UI E2E（ナラティブA/B照合・レビューパック状態保存） |
| iteration 127 | シナリオ60（自動車・モビリティ）→ 345/345 |
| iteration 128 | **ドッグフーディング記録の一か所集約**（DOGFOODING_MANIFEST.md・verify_dogfood_records.sh） |
| iteration 129 | シナリオ61（美容・ヘルスケア）→ 351/351 |
| iteration 130 | シナリオ62（セキュリティ・SOC）→ 357/357 |
| iteration 131 | シナリオ63（オンラインコミュニティ）→ 363/363 |
| iteration 132 | シナリオ64（銀行・資産運用）→ 369/369 |
| iteration 133 | **管理者自前スクリプトのCLI/API経路をE2E固定**（admin ops 12/12・並行作業） |
| iteration 134 | シナリオ65（教育・学校運営）→ 375/375 |
| iteration 135 | **MCP read→CE-4監査→監査シンク到達をE2E固定**（MCP CE-4 audit 8/8・並行作業） |
| iteration 136 | シナリオ66（建築・不動産開発）→ 381/381 |
| iteration 137 | シナリオ67（アグリ・食品製造）→ 387/387 |
| iteration 138 | シナリオ68（航空・運輸）→ 393/393 |
| iteration 139 | シナリオ69（出版・メディア）→ 399/399 |
| iteration 140 | シナリオ70（医療・クリニック）→ 405/405 |
| iteration 141 | シナリオ71（環境・サステナビリティ）→ 411/411 |
| iteration 142 | シナリオ72（コンサルティング）→ 417/417 |
| iteration 143 | シナリオ73（スポーツ・フィットネス）→ 423/423 |
| iteration 144 | シナリオ74（ペット・動物病院）→ 429/429 |
| iteration 145 | シナリオ75（生命保険）→ 435/435 |
| iteration 146 | シナリオ76（人材・採用）→ 441/441 |
| iteration 147 | シナリオ77（介護・在宅支援）→ 447/447 |
| iteration 148 | シナリオ78（保育・子育て）→ 453/453 |
| iteration 149 | シナリオ79（観光・地域振興）→ 459/459 |
| iteration 150 | シナリオ80（教育・資格試験）→ 465/465 |
| iteration 151 | シナリオ81（銀行・窓口）→ 471/471 |
| iteration 152 | シナリオ82（電子・家電）→ 477/477 |
| iteration 153 | シナリオ83（広告・マーケティング）→ 483/483 |
| iteration 154 | シナリオ84（化学・素材）→ 489/489 |
| iteration 155 | シナリオ85（IT・SaaS）→ 495/495 |
| iteration 156 | シナリオ86（人材派遣）→ 501/501 |
| iteration 157 | シナリオ87（自治体・健康増進）→ 507/507 |
| iteration 158 | シナリオ88（食品スーパー）→ 513/513 |
| iteration 159 | シナリオ89（証券・投資）→ 519/519 |
| iteration 160 | シナリオ90（不動産管理）→ 525/525 |
| iteration 161 | シナリオ91（イベント・興行）→ 531/531 |
| iteration 162 | シナリオ92（ホテル・旅館）→ 537/537 |
| iteration 163 | シナリオ93（通信キャリア）→ 543/543 |
| iteration 164 | シナリオ94（鉄道・駅）→ 549/549 |
| iteration 165 | シナリオ95（タクシー・モビリティ）→ 555/555 |
| iteration 166 | シナリオ96（B2B・商社）→ 561/561 |
| iteration 167 | シナリオ97（製薬・MR）→ 567/567 |
| iteration 168 | シナリオ98（物流・倉庫）→ 573/573 |
| iteration 169 | シナリオ99（図書館・読書振興）→ 579/579 |
| iteration 170 | シナリオ100（カフェ・喫茶チェーン）→ 585/585 |
| iteration 171 | シナリオ101（教育・学習塾）→ 591/591 |
| iteration 172 | シナリオ102（コンタクトセンター）→ 597/597 |
| iteration 173 | シナリオ103（自治体・上下水道）→ 603/603 |
| iteration 174 | シナリオ104（通信・OTT）→ 609/609 |
| iteration 175 | シナリオ105（自治体・消防）→ 615/615 |
| iteration 176 | シナリオ106（警察・公安・抑止とプライバシーの相克・島間関係要約を追加）→ 622/622 |
| iteration 177 | シナリオ107（IT・データセンター・省電力と信頼性のトレードオフ・A/B照合を追加）→ 629/629 |
| iteration 178 | シナリオ108（自治体・廃棄物処理・環境と負担のトレードオフ・4カード島の全接地を追加）→ 636/636 |
| iteration 179 | シナリオ109（放送局・番組編成・商業と公共のトレードオフ・b_missing_in_aを追加）→ 643/643 |
| iteration 180 | シナリオ110（水族館・動物園・体験とコストのトレードオフ・島間関係の接地保全を追加）→ 650/650 |
| iteration 181 | シナリオ111（半導体製造・品質と効率のトレードオフ・文面整えの意味保持を追加）→ 657/657 |
| iteration 182 | シナリオ112（訪問看護・質と効率のトレードオフ・反対視点の対象主張応答を追加）→ 664/664 |
| iteration 183 | シナリオ113（書店・品揃えと在庫のトレードオフ・タイトル提案の文書テーマ接地を追加）→ 671/671 |
| iteration 184 | シナリオ114（税理士・会計事務所・サービスと料金のトレードオフ・統合提案の正パスを追加）→ 678/678 |
| iteration 185 | シナリオ115（コンビニ・品質とコストのトレードオフ・AI束ねのテーマ類似性を追加）→ 685/685 |
| iteration 186 | シナリオ116（ドラッグストア・サービスとコストのトレードオフ・ナラティブの読み順接地を追加）→ 692/692 |
| iteration 187 | シナリオ117（ホームセンター・品揃えと在庫のトレードオフ・CE4提案の接地保持を追加）→ 699/699 |
| iteration 188 | シナリオ118（百貨店・接客と効率のトレードオフ・配置提案のカード保持を追加）→ 706/706 |
| iteration 189 | シナリオ119（精肉・鮮魚・鮮度とロスのトレードオフ・A/B複数島の取りこぼしを追加）→ 713/713 |
| iteration 190 | シナリオ120（アミューズメント・集客と維持のトレードオフ・タイトル全体テーマ反映を追加）→ 720/720 |
| iteration 191 | シナリオ121（温浴・スパ・衛生とコストのトレードオフ・矛盾説明の接地を追加）→ 727/727 |
| iteration 192 | シナリオ122（映画館・集客と稼働のトレードオフ・関係要約の島ペア参照を追加）→ 734/734 |
| iteration 193 | シナリオ123（自転車店・サービスと在庫のトレードオフ・表札のテーマ参照を追加）→ 741/741 |
| iteration 194 | シナリオ124（フラワーショップ・需要とロスのトレードオフ・配置の島・読み順保持を追加）→ 749/749 |
| iteration 195 | シナリオ125（水産・漁業・資源と生計の相克・矛盾検出の正パスを追加）→ 755/755 |
| iteration 196 | シナリオ126（郵便・郵便局・公共性と効率の相克・矛盾検出の正パスを追加）→ 761/761 |
| iteration 197 | シナリオ127（葬儀・斎場・心の寄り添いと価格の相克・矛盾検出の正パスを追加）→ 767/767 |

---

## 6. 検証対象の不変条件（業務フローE2Eが固定している契約）

- **proposal-only**: AI提案は `status=proposed`・`reviewState=unreviewed` のまま自動適用しない（CE4・AI-OPPOSE-01）。
- **SafeMode fail-closed**: 未レビュー文は LLM へ送らない（422・SEC-AI-SAFEMODE-01/02）。
- **モデルガバナンス**: 許容リスト外→403 `model_not_allowed`・未登録→403 `model_not_registered`（R3 fail-closed）。
- **保留接続**: 反対視点提案→人間の「保留して再確認」→ `holdState=held`（非破壊・文面不変）。
- **A/B照合**: ナラティブが島を省略→ `a_missing_in_b`（方向＋件数・KJ-AB-CROSS-CHECK-01）。
- **再現性**: レビューパックのエクスポートが確定/保留/未レビューを作業状態のまま保存（SOCIAL-DIFFUSION-01 土台）。
- **並行制御**: 古いETagでの編集→409（ADR-0076 サーバ権威 LWW+CAS）。
- **文書ライフサイクル**: アーカイブ中は書込→423（ADR-0073 D2=A）。
