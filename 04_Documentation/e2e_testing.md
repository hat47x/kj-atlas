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
- readOnly + SafeMode の安全境界（編集抑止と表示ラベル）
- visibility（view/pack）の編集・再読込保持
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

- `e2e/polygon_import_validation.spec.ts`（自己交差polygon importのフォールバック確認）
- `e2e/diagnostics_structural_metrics.spec.ts`（構造メトリクスがbundle diagnosticsへ反映され、連続exportで決定論を維持することを確認）

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
- `npm run e2e -- e2e/diagnostics_structural_metrics.spec.ts`
- `npm run e2e -- e2e/pub_visibility_i18n_readonly_flow.spec.ts`
- `curl http://localhost:8000/healthz`
- `curl http://localhost:4173/api/healthz`

---

## 6. 非目標

- E2Eのみで品質を担保しない（unit/integration/typecheckは必須）
- すべてのUI差分をフルシナリオで網羅しない（重要導線優先）

## 7. 利用者向けドキュメント整合要件（必須）

E2Eはアプリケーション動作に関する利用者向けドキュメントと**完全整合**していなければなりません。

1. `04_Documentation/e2e_testing.md` をE2E手順の正本（single source of truth）とする。
2. `04_Documentation/installation.md` / `04_Documentation/operations.md` / `CONTRIBUTING.md` / `01_Plans/coding_standards.md` にあるE2E関連記述は、本書と同じコマンド・同じ受入基準・同じ代替経路を保つ。
3. E2Eの実行方法・受入基準・対象フローを変更したPRでは、上記文書を同一PRで更新する。
4. PR本文に、更新したE2E関連文書一覧を明記する。
5. 利用者向けドキュメントとの間で不足・不整合が見つかった場合は、まず「あるべき状態（期待挙動・受入基準・コマンド）」を明文化し、正本に合わせて同期更新する。
6. どちらが正かを容易に判断できない場合は、Issueを起票して論点・候補案・影響範囲を管理し、合意後に文書を更新する。



## 8. FB-RM-RS-02 追記（E2E未実装理由の分析と是正）

### 8.1 未実装だった理由

- FB-RM-RS-02 初回実装では、`structural_metrics.test.ts` と `worker_golden.test.ts` で計算式・決定論を固定できたため、レビュー時に「worker/unit で十分」と判断してしまった。
- 一方で実際のユーザーフロー（Share Panel から bundle export → `diagnostics.md` 取得）を通す E2E が欠けており、`04_Documentation/e2e_testing.md` の「UIを伴う変更はE2E追加」を満たしていなかった。

### 8.2 是正内容

- `e2e/diagnostics_structural_metrics.spec.ts` を追加し、以下をブラウザ経路で検証する。
  1. `document.json` 差し替え後の bundle export に新規構造メトリクス行（`isolationRate`, `connectivityScore`, `degreeSkewRatio`）が含まれる。
  2. 同一入力で 2 回 export した `diagnostics.md` が一致する（決定論）。

### 8.3 再発防止

- diagnostics の表示/出力へ新規指標を追加するPRでは、unit/workerテストに加え、export経路を通すE2Eを必須チェック項目とする。
- PR本文の「未実施項目」に E2E省略理由を記載する場合は、次回是正タスク（Issueまたは同PR内追補）を必ず紐づける。
