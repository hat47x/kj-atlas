# Screenshots

このディレクトリには、利用者向け文書に掲載する画面例を置きます。

撮影条件:

- サンプル文書: `doc_phase1_canvas`
- UI locale: `ja`
- API: `http://127.0.0.1:8000`
- frontend: `http://127.0.0.1:4173/?locale=ja`
- LLM provider: `KJ_ATLAS_LLM_PROVIDER=none`
- 秘密情報、API key、組織固有の承認履歴、顧客データは含めない

ファイル:

| ファイル | 内容 |
| --- | --- |
| `start-document-entry.png` | 起動直後の「作業を開始」パネル |
| `app-canvas-overview.png` | 起動直後のキャンバス、ヘッダー、右側パネル |
| `selection-context-card.png` | カード選択後、右側パネルの先頭に現在の選択とレビュー状態が表示される状態 |
| `share-export-safe-mode.png` | 「共有と再現」パネルの SafeMode と export/share 前チェック |
| `view-controls-safe-mode.png` | `View` パネルの表示設定と SafeMode |
| `diagnostics-quality-report.png` | diagnostics 実行後の品質レポート |
| `mobile-toolbar-smoke-390.png` | 390px viewport のヘッダーと主要操作 |

## Regeneration

Use the frontend screenshot capture script when the visible UI changes:

```powershell
cd 03_Implement/frontend
C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\scripts\capture_release_screenshots.mjs
```

The script starts a temporary Vite server when port 4173 is free, uses deterministic sample data, hides the transient status message for stable public images, captures the public-documentation screenshots, and stops the server when it started it.

Optional environment variables:

- `KJ_ATLAS_SCREENSHOT_OUTPUT_DIR`: output directory. Defaults to `04_Documentation/assets/screenshots`.
- `KJ_ATLAS_SCREENSHOT_BASE_URL`: target URL. Defaults to `http://127.0.0.1:4173/?locale=ja`.
- `KJ_ATLAS_SCREENSHOT_HOST`: Vite host. Defaults to `127.0.0.1`.
- `KJ_ATLAS_SCREENSHOT_PORT`: Vite port. Defaults to `4173`.
