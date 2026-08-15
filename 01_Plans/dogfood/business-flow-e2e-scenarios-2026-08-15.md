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
| 注意事項 | 矛盾検出は「単なる意見の相違」と「論理的矛盾」を区別する（後者のみ報告）。証言の文面は refine 等で変更しない（現場の完全性・evidence としての位置づけ）。SafeMode の未レビュー境界(422)は島要約・ナラティブ等の doc 文脈ルートで効き、detect-contradiction は doc 文脈を持たない（→ 起票済み issue） |

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
- [ ] UI 層 E2E（フロントエンド AI 操作・CE4 proposal 連鎖）
- [ ] さらに別業態のシナリオ追加（イテレーション毎に拡大）
