# Dogfooding 検証マニフェスト（一か所集約）

- **目的**: ドッグフーディングの既存記録を一か所に集約し、**後から別の生成AIが検証できる**構造で提供する。
- **検証方法（2段階）**:
  1. **構造照合**: `bash 01_Plans/dogfood/verify_dogfood_records.sh` — 本マニフェストの構造的主張（ファイル存在・数値・算術・課題状態）をリポジトリ実体と自動照合する。
  2. **再現実行**: 本マニフェスト §2 の検証層コマンドを実行し、各層の期待結果を確認する（業務フローE2E・CIハーネス・単体テスト・UI E2E・計画文書整合）。

---

## 1. 現状サマリ（2026-08-16・iteration 175 時点）

| 指標 | 値 | 検証方法 |
|------|----|---------|
| 総シナリオ数（シナリオ1〜105） | 105 | §2.1 実走行＋`business-flow-e2e-scenarios-2026-08-15.md` |
| 業務フローE2Eスクリプトのシナリオヘッダ数 | 103 | verify script（シナリオ1=初期フロー・ヘッダechoなし / シナリオ4=別スクリプト`verify_admin_ops_flow_e2e.sh`） |
| カバー業態数 | 105 | シナリオドキュメント「カバレッジ集約」 |
| 業務フローE2Eチェック数 | 615 | §2.1 実走行 → `Result: 615 passed, 0 failed` |
| 総チェック数（check 10） | **657** | = 615（業務フロー）＋ 12（admin ops）＋ 7（kj multi-round）＋ 8（MCP CE-4 audit）＋ 15（CLI CE-4 audit）— 算術を verify script で照合 |
| 発行済み課題 | 2（AI-MODEL-GOVERNANCE-02 / OPS-LLM-COST-02・**両方 Done**） | verify script |
| 検証層 | backend単体・frontend単体・frontend UI E2E・業務フローE2E・計画文書整合 | §2 |

> 注記: 総チェック数は**業務フローE2Eのチェック数（615）とは別**。CIハーネス `verify_all.sh` check 10 は5自己完結E2E（業務フロー・admin ops・kj multi-round・MCP CE-4 audit・CLI CE-4 audit）を実行するため、総数 = 657。以前の進捗報告で総数が誤記されていた差分（-10）は、本マニフェストの算術照合により検出・訂正された。

---

## 2. 検証ハーネス（別の生成AIが再現実行する手順）

### 2.1 業務フローE2E（決定性モックLLM・課金なし）
```bash
cd 03_Implement/backend
bash scripts/verify_business_flow_e2e.sh 8005   # 期待: "Result: 615 passed, 0 failed"（シナリオ1〜105）
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
| `03_Implement/backend/scripts/verify_business_flow_e2e.sh` | 業務フローE2E（シナリオ1〜105・615 checks） | §2.1 |
| `03_Implement/backend/scripts/verify_admin_ops_flow_e2e.sh` | 管理者CLI/API運用フロー（シナリオ4・12 checks・自前スクリプト経路を含む） | §2.2 |
| `03_Implement/backend/scripts/verify_kj_multi_round.sh` | 人間×AI多ラウンド協調（7 checks） | §2.2 |
| `03_Implement/backend/scripts/verify_mcp_ce4_audit_e2e.py` | MCP read→CE-4監査（channel=mcp）→HTTPシンク到達の自己完結E2E（8 checks） | §2.2 |
| `03_Implement/backend/scripts/verify_cli_ce4_audit_e2e.py` | `kj` CLI→CE-4監査（channel=cli）→HTTPシンク到達の自己完結E2E（15 checks・全CE4ライフサイクル＋resolve-bundle） | §2.2 |
| `03_Implement/backend/verify_all.sh` | CIハーネス（check 10 配線） | §2.2 |
| `03_Implement/deploy/tools/mock_local_llm.py` | 決定性モックLLM（GPU不要） | §2.1 前提 |
| `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md` | シナリオ定義・カバレッジ集約（シナリオ105・チェック615） | §2.1 数値照合 |
| `01_Plans/dogfood/README.md` | イテレーション履歴ログ（iteration 1〜127） | 目視 / verify script |
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
