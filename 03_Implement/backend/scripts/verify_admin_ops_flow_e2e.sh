#!/usr/bin/env bash
# Standard business-flow E2E: 個人OSS管理者のCLI/API運用（ドッグフーディング iteration 45）。
#
# 業態: 個人OSSソフトウェア運用
# 想定人物: 運用管理者（自前スクリプトを書く）
# 業務領域: 文書ライフサイクルと管理面のAPI運用（Webを介さない CLI/API 経路）
# 操作内容: 文書一覧(GET /docs) -> 文書作成(PUT) -> アーカイブ(POST archive)
#          -> アーカイブ中書込の423確認 -> 解除(unarchive) -> 解除後書込
#          -> 管理面監査の照会(GET /admin/provision/audit) -> キー分離の確認
# 注意事項: 管理面(/admin/*)は業務キー(X-API-Key)では到達不可。専用キー
#          (X-Admin-Api-Key)で control-plane 認可を通す。アーカイブ文書は
#          読み取り専用（PUT 423・GETは可）。監査は fail-open で記録され、
#          control-plane 認可でのみ照会できる。
#
# これは「管理者が自前のスクリプトを書いてCLI/APIを利用する経路」を業務フローとして
# 固定する E2E。verify_api_admin.sh（provisioning面の機械的検証）とは別に、
# 業務キー/管理キーを両方設定した実バックエンド上で一気通貫で検証する。
#
# Usage:
#   ./verify_admin_ops_flow_e2e.sh [PORT]     # PORT default 8500
#
# Requires the backend venv and ports free.

set -u
BACKEND_PORT="${1:-8500}"
BASE_URL="http://127.0.0.1:${BACKEND_PORT}"
BIZ_KEY="biz-test-key-${BACKEND_PORT}"
ADM_KEY="adm-test-key-${BACKEND_PORT}"
PASS=0
FAIL=0
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
ROOT_DIR="$(dirname "$(dirname "$BACKEND_DIR")")"
VENV_PYTHON="$BACKEND_DIR/.venv/bin/python"

cleanup() {
  [ -n "${BACKEND_PID:-}" ] && kill "$BACKEND_PID" 2>/dev/null
  wait 2>/dev/null
}
trap cleanup EXIT

check() {
  local desc="$1" expected="$2" actual="$3"
  if [ "$actual" = "$expected" ]; then
    echo "  PASS: $desc"
    PASS=$((PASS+1))
  else
    echo "  FAIL: $desc (expected $expected, got $actual)"
    FAIL=$((FAIL+1))
  fi
}

echo "=== kj-atlas admin CLI/API ops flow (iteration 45) ==="
echo "  backend: $BASE_URL"

# 1. Fresh migrated DB (deterministic run).
TMP_DB="$(mktemp /tmp/kj_admin_ops_XXXXXX.sqlite3)"
(cd "$BACKEND_DIR" && KJ_ATLAS_DATABASE_URL="sqlite:///$TMP_DB" \
  "$VENV_PYTHON" -m alembic upgrade head > /tmp/kj_admin_ops_migrate.log 2>&1)

# 2. Start the backend with BOTH keys configured (business + control plane).
KJ_ATLAS_API_KEY="$BIZ_KEY" \
KJ_ATLAS_ADMIN_API_KEY="$ADM_KEY" \
KJ_ATLAS_DATABASE_URL="sqlite:///$TMP_DB" \
  "$VENV_PYTHON" -m uvicorn kj_atlas_api.main:app --port "$BACKEND_PORT" --host 127.0.0.1 \
  > /tmp/kj_admin_ops_backend.log 2>&1 &
BACKEND_PID=$!

for _ in $(seq 1 30); do
  curl -s -o /dev/null "$BASE_URL/healthz" && break
  sleep 1
done
check "backend /healthz" "200" "$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/healthz")"

BIZ_H="X-API-Key: $BIZ_KEY"
ADM_H="X-Admin-Api-Key: $ADM_KEY"
DOC_ID="admin-ops-doc"

# --- 文書ライフサイクル（管理者が自前スクリプトで運用） ---

# 3a. 文書一覧（空スタートでも 200）。
list_code=$(curl -s -o /dev/null -w '%{http_code}' -H "$BIZ_H" "$BASE_URL/docs")
check "GET /docs 一覧 (200)" "200" "$list_code"

# 3b. 文書作成（バッチで取り込む）。
DOC='{"version":1,"id":"'$DOC_ID'","title":"運用マニュアル","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"c1","text":"バックアップ手順","x":0,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"i1","cardIds":["c1"]}],"readingOrder":["i1"]}'
put_code=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$DOC_ID" \
  -H "$BIZ_H" -H 'Content-Type: application/json' -d "$DOC")
check "PUT document (管理者が作成)" "200" "$put_code"

# 3c. アーカイブ（第2反復の運用操作・ADR-0073 D2=A）。
arch_code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/docs/$DOC_ID/archive" \
  -H "$BIZ_H" -H 'Content-Type: application/json' -d '{}')
check "POST archive (204)" "204" "$arch_code"

# 3d. アーカイブ中の書込は 423 で拒否（読み取り専用の実効）。
locked_code=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$DOC_ID" \
  -H "$BIZ_H" -H 'Content-Type: application/json' -d "$DOC")
check "PUT archived document (423 Locked)" "423" "$locked_code"

# 3e. アーカイブ解除。
unarch_code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/docs/$DOC_ID/unarchive" \
  -H "$BIZ_H" -H 'Content-Type: application/json' -d '{}')
check "POST unarchive (204)" "204" "$unarch_code"

# 3f. 解除後は書込可能。
rewrite_code=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$DOC_ID" \
  -H "$BIZ_H" -H 'Content-Type: application/json' -d "$DOC")
check "PUT after unarchive (200)" "200" "$rewrite_code"

# --- 管理面監査とキー分離 ---

# 4a. 管理面監査の照会（control-plane 認可・専用キー）。
audit_code=$(curl -s -o /dev/null -w '%{http_code}' -H "$ADM_H" "$BASE_URL/admin/provision/audit")
check "GET /admin/provision/audit with admin key (200)" "200" "$audit_code"

# 4b. 監査を業務キーでは照会できない（キー分離・SEC-ADMIN-PLANE-02）。
audit_biz_code=$(curl -s -o /dev/null -w '%{http_code}' -H "$BIZ_H" "$BASE_URL/admin/provision/audit")
check "GET audit with business key only (401)" "401" "$audit_biz_code"

# 4c. 業務面（/docs）を管理キーでは照会できない（逆方向の分離）。
docs_adm_code=$(curl -s -o /dev/null -w '%{http_code}' -H "$ADM_H" "$BASE_URL/docs")
check "GET /docs with admin key only (401)" "401" "$docs_adm_code"

# 4d. 誤った管理キーは拒否（fail-closed）。
audit_wrong_code=$(curl -s -o /dev/null -w '%{http_code}' \
  -H "X-Admin-Api-Key: wrong-key" "$BASE_URL/admin/provision/audit")
check "GET audit with wrong admin key (401)" "401" "$audit_wrong_code"

# 5. 管理者が自前で書いたスクリプト（stdlib のみ・依存なし）が同じライフサイクルと
#    control-plane 監査・キー分離を実走行できる（iteration 131 追加・非Web経路の拡充）。
#    scripts/examples/admin_lifecycle.py は内部で 10 個のアサーションを自己検証し、
#    失敗時は非ゼロで exit する。これを E2E の 1 チェックとして固定する。
ADMIN_SCRIPT="$SCRIPT_DIR/examples/admin_lifecycle.py"
if KJ_ATLAS_API_BASE_URL="$BASE_URL" \
   KJ_ATLAS_API_KEY="$BIZ_KEY" \
   KJ_ATLAS_ADMIN_API_KEY="$ADM_KEY" \
   "$VENV_PYTHON" "$ADMIN_SCRIPT" "admin-self-script-doc" > /tmp/kj_admin_self_script.log 2>&1; then
  echo "  PASS: admin self-script (lifecycle + audit + key separation, exit 0)"
  PASS=$((PASS+1))
else
  echo "  FAIL: admin self-script (exit non-zero)"
  cat /tmp/kj_admin_self_script.log
  FAIL=$((FAIL+1))
fi

echo ""
echo "=== Result: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ]
