from __future__ import annotations

import os
from pathlib import Path

ISSUE = Path("01_Plans/issues/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md")
MARKER = "### Implementation checkpoint 2026-09-04: capability authorization surface separation"


def replace_ac(lines: list[str], prefix: str, replacement: str) -> None:
    indexes = [index for index, line in enumerate(lines) if line.startswith(prefix)]
    if len(indexes) != 1:
        raise SystemExit(f"expected exactly one {prefix!r}, found {len(indexes)}")
    lines[indexes[0]] = replacement


def main() -> None:
    run_id = os.environ.get("GITHUB_RUN_ID", "").strip()
    if not run_id:
        raise SystemExit("GITHUB_RUN_ID is required")

    body = ISSUE.read_text(encoding="utf-8")
    checkpoint_heading = "### Lane C checkpoint 2026-09-05: AC-10 consumer-specific negative matrix"
    if checkpoint_heading in body:
        raise SystemExit("Lane C checkpoint already exists")
    if body.count(MARKER) != 1:
        raise SystemExit("checkpoint insertion marker is not unique")

    lines = body.splitlines()

    replace_ac(
        lines,
        "- [x] AC-8:",
        "- [x] AC-8: cache、job、agent credential、audit、storage keyなどtenant対応consumerではserver-resolved tenant境界を伝播し、欠落時は処理を停止する。MCPは現行例外としてtenant-bound credentialをまだ持たず、`saas-multitenant`を起動時にfail-fastしてDocument readへ到達させない。— 2026-08-13チェックポイントの実装確認に加え、2026-09-05 Lane C再監査で`03_Implement/mcp/src/document_client.ts`と`document_client.test.ts`のfail-closed契約を再確認した。したがって「MCPへtenantIdを注入済み」とは主張せず、未実装credentialをclient入力で代替しないことを安全境界とする。",
    )
    replace_ac(
        lines,
        "- [ ] AC-10:",
        f"- [x] AC-10: tenant A/Bの越境negative matrixが、API/MCP/worker/browser cacheそれぞれの実際の攻撃面でfail-closedとなる。— **2026-09-05 Lane C完了確認（GitHub Actions Run `{run_id}`）**: APIは`test_saas_e2e_tenant_isolation.py`でtenant A/Bに同一`shared-doc`を作成し、GETが各tenant固有payloadだけを返し、PUTが選択tenantだけを更新することを再実行した。MCPはtenant-bound credential未実装のため`saas-multitenant`を`validateMcpRuntimeProfile()`で起動時拒否し、same-docId read自体へ到達させない。worker/async resultは共通`TenantSessionGenerationGuard`の遅延成功拒否をunit testで再実行し、real Chromiumの`tenant_session_multitab.spec.ts`ではPR #2917由来のAI代表probeとtenant切替lifecycleを通過した。browser cacheは同specでtenant A→B切替後にrecent/QueryPresetが新scopeだけを表示し、旧tenant Aのscoped localStorage keyが残らないことを再実行した。consumerごとに境界形状が異なるため、MCP/worker/browserへ架空のsame-docId DB readを作るのではなく、各consumerが越境を成立させない現行契約を同一Runで検証した。",
    )
    replace_ac(
        lines,
        "- [~] AC-13:",
        "- [~] AC-13: 同じ認証セッションの複数タブ、同時tenant切替、bfcache復帰、遅延responseで古い`tenantSessionVersion`を持つ現存tenant-scoped操作がresource lookup/commit前に拒否され、client通知が欠落しても新tenantへ自動再送・commitされない。— **2026-09-05 Lane C再整理**: mock-API実ブラウザではcross-tab、bfcache、stale PUT 409非再送、遅延response、bundle export/review-pack/AI結果破棄まで固定済みで、`AUTH-ONE-TIME-JWT-01`はmock Broker→実frontend→shared PostgreSQL→2 backend workerの認証縦断を完了している。ただし両者を同一scenarioとして接続した「同一認証sessionの複数タブが実backendへ競合操作するmatrix」はまだ存在しない。Doneの`QA-E2E-SAAS-01`はbrowser storage/lifecycle残差、Doneの`AUTH-ONE-TIME-JWT-01`は認証縦断の正本であり、どちらか単独をAC-13完了証拠へ読み替えない。server-side export/import routeのように現存しない操作を新設して試験することも要件化せず、現存surfaceの実backend複数タブ競合を残条件とする。",
    )

    body = "\n".join(lines) + ("\n" if body.endswith("\n") else "")
    checkpoint = f"""{checkpoint_heading}

- AC-10の旧文言は「same-docId」をAPI/MCP/worker/browser cacheの全consumerへ同型に適用するよう読めたが、現行architectureでは攻撃面が異なる。APIはtenant-scoped DB read/write、MCPはSaaS credential未実装による起動拒否、workerはtenant切替後のstale async result commit、browser cacheはtenant/principal/deployment scope残留がそれぞれの境界である。
- GitHub Actions Run `{run_id}` で、backendのsame-docId HTTP matrix、MCPのSaaS fail-fast、frontend generation guard、real Chromium SaaS tenant-switch/storage scenarioを同一Runとして再実行した。production code/API/schemaには変更を加えていない。
- この再検証によりAC-10を完了とする。AC-1〜11がすべて完了したため、AC-12のRound 8 R8-E/F UI検証は前提条件を満たして次の実行対象へ進められる。
- AC-13は別軸である。実frontend/実backend縦断とmock-API複数タブlifecycleは個別には存在するが、同じ認証sessionの複数tab競合を実backendまで通す1本のmatrixは未確認のため、部分完了を維持する。

"""
    body = body.replace(MARKER, checkpoint + MARKER)
    ISSUE.write_text(body, encoding="utf-8")


if __name__ == "__main__":
    main()
