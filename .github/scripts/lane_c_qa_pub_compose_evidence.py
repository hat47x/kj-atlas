import os
from pathlib import Path

ISSUE = Path("01_Plans/issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md")
MARKER = "## 2026-09-07 current-main Compose 3軸再検証"

text = ISSUE.read_text(encoding="utf-8")
if "- Status: Open" not in text:
    raise SystemExit("QA-PUB-01-I18N-03 must be Open before execution evidence is recorded")
if MARKER in text:
    raise SystemExit("Compose 3-axis evidence section already exists")

tested_sha = os.environ["TESTED_SHA"]
run_id = os.environ["GITHUB_RUN_ID"]
e2e_result = os.environ.get("E2E_RESULT", "Playwright pass")

section = f"""
{MARKER}

`Status: Open / Execution: Ready` へ同期した後、ADR-0019の標準経路をcurrent-mainで再実走した。今回の目的は3軸の機械判定可能部分を**Composeで配信された現在のfrontend**に対して確認し、同じstackのPostgreSQL保存経路も生きていることを確認することである。

- tested baseline: main `{tested_sha}`。検証branchの恒久差分は、本再実走で発見したE2E locator修正と本証跡記録のみで、製品実装差分はない。
- standard runtime: clean `docker compose down -v` → `docker compose up --build -d`、`http://127.0.0.1:8080/api/healthz` を確認。
- storage preflight: `e2e_storage_preflight.mjs --write-base-url http://127.0.0.1:8080/api` で、一意な合成DocumentV1の `PUT -> GET`、payload、ETag をCompose frontend proxy経由で確認。固定seedには依存しない。
- browser target: 一時Playwright configで `baseURL=http://127.0.0.1:8080` とし、Vite dev serverではなくCompose frontendへChromiumを直接接続した。
- public compatibility: `pub_visibility_i18n_readonly_flow.spec.ts` + `public_pack_visibility_compat.spec.ts`。
- I18N flow parity: `pub_visibility_i18n_readonly_flow.spec.ts` + `i18n_locale_query_equivalence.spec.ts` + `i18n_locale_functional_equivalence.spec.ts`。
- readOnly + SafeMode boundary: `pub_visibility_i18n_readonly_flow.spec.ts` のdisabled action、実カード本文commit遮断、カードdrag位置不変、locked redaction contextを含む既存回帰を使用した。
- first product-path run `34068672554`: typecheck、Compose health、実PostgreSQL roundtripはpass。Playwrightは14件中12件pass、2件が`public_pack_visibility_compat.spec.ts`のstrict locator ambiguityでfailした。いずれも期待する公開パックエラー本文自体は画面上の`data-testid="status-message"`へ正しく表示されていたが、Compose本番配信では別の正当なmodel/runtime `role="status"`も存在するため、非限定の`getByRole("status")`が2要素へ一致した。
- triage: **test defect**。製品側の公開パックerror semanticsを変更せず、失敗2箇所だけを既存の専用status surface `getByTestId("status-message")`へ限定した。model/runtime statusを消す、`.first()`で偶然のDOM順へ依存する、または製品コードを変更する修復は採らなかった。
- Playwright rerun result: **{e2e_result}**。`npm run typecheck` もpass。
- final GitHub Actions run: `{run_id}`。

### 判定境界

- 初回Compose実走は、Vite-only経路では顕在化しなかったE2E locatorの過広さを検出した。これは隠さずtest defectとして残し、test-only修正後に同じ標準Compose経路を全件再実行して判定する。
- 最終再実走で、3軸の**機械判定可能部分**について新たなproduct defect / environment limitationは検出されなかった。
- fixture-backed browser testと実PostgreSQL roundtripは役割を分けている。fixtureで公開/I18N/readOnlyのUI状態遷移を固定し、storage preflightで実保存経路を別に確認する。fixtureを実DB証拠へ読み替えない。
- この再実走は翻訳文の自然さ・説明品質などの**人間によるtranslation quality review**、PRODUCT-QA release decision、release screenshot bundleを完了扱いにしない。
- one-shot workflow/helperと一時Playwright configは証拠採取後に削除し、恒久CI面積を増やさない。
"""

ISSUE.write_text(text.rstrip() + "\n\n" + section.strip() + "\n", encoding="utf-8")
print(f"recorded QA-PUB Compose evidence for run {run_id} / {tested_sha}")
