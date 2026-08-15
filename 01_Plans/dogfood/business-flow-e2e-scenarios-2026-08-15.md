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

次回以降のイテレーションで、この表を軸に**別の業態・人物・領域・操作・注意事項**を追加していく
（例: 新規事業企画の会議ファシリテーション、UXリサーチャーのペルソナ整理、教育現場の振り返り整理など）。

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

- [x] バックエンド全層の標準業務フロー E2E を固定（7/7 pass・モックLLM）
- [ ] UI 層 E2E（フロントエンド AI 操作・CE4 proposal 連鎖）
- [ ] 別業態のシナリオ追加（イテレーション毎に拡大）
