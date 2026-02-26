# E2Eテスト方針（Playwright）

本ドキュメントは、`kj-atlas` における End-to-End テストの実施方針を定義します。  
詳細な運用ルールは `ADR-0019` を正本とし、本書では **実装チーム向けの具体手順** を扱います。

---

## 1. 基本方針

1. `03_Implement/*` の変更では、原則として E2E確認を行う。
2. UIを伴う変更（Canvas / SidePanel / Import/Export導線 / SafeMode表示）では、
   **Playwright によるE2Eテスト追加または更新を原則必須** とする。
3. テストは「壊れにくさ」を優先し、以下を重視する。
   - 主要ユーザーフローの成功確認
   - 回帰しやすい安全境界（SafeMode / import / export / docs保存）
   - 環境差分に強い待機戦略（networkidle固定に依存しすぎない）

---

## 2. kj-atlas向け推奨E2Eスコープ

### 2.1 Smoke（毎回実施）

- App起動
- APIヘルス確認
- 初期Document読込

### 2.2 Core Flow（変更影響時に必須）

- Cardの追加・移動・保存
- Islandの作成・collapse/expand
- 再読込後の状態保持

### 2.3 Security/Safety Flow（変更影響時に必須）

- SafeMode ON時の表示/制約
- import（正常/異常）
- export（意図しない漏えい防止）

---

## 3. 実行プロファイル

### 3.1 Compose優先（標準）

`web + api + db` を起動した状態で Playwright を実行する。

### 3.2 Docker未導入時（代替）

`backend(SQLite) + frontend dev server` 構成で Playwright を実行する。

- backend: `:8000`
- frontend: `:4173`（`/api` proxy 経由）

---

## 4. テスト追加ルール（原則）

- 新機能: 1本以上のE2Eシナリオを追加
- バグ修正: 再発防止のE2Eシナリオを追加
- 文言/軽微UIのみ: screenshotベース確認でも可（ただし影響範囲をPRで明記）

命名例:

- `e2e/smoke.spec.ts`
- `e2e/collapse_persistence.spec.ts`
- `e2e/safe_mode_export_guard.spec.ts`
- `e2e/polygon_import_validation.spec.ts`（自己交差polygon importのフォールバック確認）

---

## 5. PR記載ルール

PR本文には最低限以下を記載する。

- 実行環境（Compose / SQLite代替）
- 実行コマンド
- 成否
- 未実施項目（あれば理由）

例:

- `npm run e2e`（Playwright）
- `npm run e2e -- e2e/polygon_import_validation.spec.ts`
- `curl http://localhost:8000/healthz`
- `curl http://localhost:4173/api/healthz`

---

## 6. 非目標

- E2Eのみで品質を担保しない（unit/integration/typecheckは必須）
- すべてのUI差分をフルシナリオで網羅しない（重要導線優先）

