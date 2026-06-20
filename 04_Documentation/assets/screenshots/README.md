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

## Product Value Evidence Screenshots

The following screenshots are generated from deterministic Product Value fixtures and are intended for public documentation or release-evidence review. They show representative states only; they do not by themselves approve Product Value gates or final release shipment.

| File | Purpose |
| --- | --- |
| `product-value-first-island.png` | PV01: first meaningful grouping after opening a sample, selecting two cards, and creating an island. |
| `product-value-first-island-share-preflight.png` | PV01: the first island carried into Share & Reproduce with SafeMode and remaining review signals visible. |
| `product-value-ambiguity-state.png` | PV02: an unresolved/ambiguous claim selected in a grouped context, with review state visible in the side panel. |
| `product-value-ambiguity-share-preflight.png` | PV02: Share & Reproduce preflight showing unresolved signals and SafeMode exclusion of unreviewed drafts. |
| `product-value-review-pack-trace.png` | PV03: the Share & Reproduce panel with selected-card traces included at detail granularity. |
| `product-value-review-pack-readonly.png` | PV03: a review-pack fixture inspected in read-only mode with review state and disabled edit actions visible. |

Regenerate these screenshots when Product Value fixtures, Japanese UI labels, canvas layout, or Share & Reproduce controls change:

```powershell
cd 03_Implement/frontend
C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\scripts\capture_product_value_screenshots.mjs
```

The script starts a temporary Vite server when `KJ_ATLAS_SCREENSHOT_PORT` is free, loads the app with `?locale=ja`, injects deterministic fixture data through Playwright routes, captures the six PNG files above, and stops the server when it started it.
