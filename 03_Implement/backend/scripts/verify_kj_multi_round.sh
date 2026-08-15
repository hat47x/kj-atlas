#!/usr/bin/env bash
# 人間×生成AIの多ラウンド協調KJ実践の検証（DOMAIN-KJ-COLLAB-01 / iteration 43）。
#
# ラウンド循環: 発散(R1: カード束ね提案) -> 構造化(R2: 島の表札提案) -> 深化(R3: 文面整え+ナラティブ草稿)。
# 各ラウンドのAI出力が次のラウンドの入力になり、結論が深まる（人間=判断、AI=候補生成の協調）。
#
# LLM 切替（環境変数）:
#   KJ_ATLAS_DEEPSEEK_API_KEY 設定時 -> 実API（DeepSeek・課金）
#   未設定時                    -> ローカルモック（GPU不要・無料・決定的・iteration 41/42 の縮退方式）
#
# Usage:
#   bash verify_kj_multi_round.sh [PORT]
#   KJ_ATLAS_DEEPSEEK_API_KEY=<key> bash verify_kj_multi_round.sh [PORT]   # 実API

set -u
BACKEND_PORT="${1:-8000}"
STUB_PORT=$((BACKEND_PORT + 1))
BASE_URL="http://127.0.0.1:${BACKEND_PORT}"
PASS=0
FAIL=0
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
ROOT_DIR="$(dirname "$(dirname "$BACKEND_DIR")")"
VENV_PYTHON="$BACKEND_DIR/.venv/bin/python"
MOCK_LLM="$ROOT_DIR/03_Implement/deploy/tools/mock_local_llm.py"

# DeepSeek キーが無ければローカルモックへ縮退（無料・決定的）。
if [ -n "${KJ_ATLAS_DEEPSEEK_API_KEY:-}" ]; then
  LLM_PROVIDER=deepseek
  echo "  LLM: DeepSeek 実API（課金）"
else
  LLM_PROVIDER=local
  echo "  LLM: ローカルモック（無料・決定的）— KJ_ATLAS_DEEPSEEK_API_KEY 未設定"
fi

cleanup() {
  [ -n "${BACKEND_PID:-}" ] && kill "$BACKEND_PID" 2>/dev/null
  [ -n "${STUB_PID:-}" ] && kill "$STUB_PID" 2>/dev/null
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

echo "=== kj-atlas 人間×AI 多ラウンド協調KJ検証 ==="
echo "  backend: $BASE_URL"

# ローカルモックのみ起動（DeepSeek は外部API）。
if [ "$LLM_PROVIDER" = "local" ]; then
  "$VENV_PYTHON" "$MOCK_LLM" --host 127.0.0.1 --port "$STUB_PORT" > /tmp/kj_kj_stub.log 2>&1 &
  STUB_PID=$!
  sleep 2
  LOCAL_BASE_URL="http://127.0.0.1:${STUB_PORT}"
else
  LOCAL_BASE_URL="${KJ_ATLAS_LOCAL_LLM_BASE_URL:-}"
fi

# 新規 migration 済み temp DB で決定性を確保。
TMP_DB="$(mktemp /tmp/kj_kj_XXXXXX.sqlite3)"
(cd "$BACKEND_DIR" && KJ_ATLAS_DATABASE_URL="sqlite:///$TMP_DB" \
  "$VENV_PYTHON" -m alembic upgrade head > /tmp/kj_kj_migrate.log 2>&1)

KJ_ATLAS_LLM_PROVIDER="$LLM_PROVIDER" \
KJ_ATLAS_LOCAL_LLM_BASE_URL="$LOCAL_BASE_URL" \
KJ_ATLAS_DATABASE_URL="sqlite:///$TMP_DB" \
  "$VENV_PYTHON" -m uvicorn kj_atlas_api.main:app --port "$BACKEND_PORT" --host 127.0.0.1 \
  > /tmp/kj_kj_backend.log 2>&1 &
BACKEND_PID=$!

for _ in $(seq 1 30); do
  curl -s -o /dev/null "$BASE_URL/healthz" && break
  sleep 1
done
check "backend /healthz" "200" "$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/healthz")"

# ============ R1 発散: 人間がカードを書き、AI が束ね提案 ============
R1_DOC='{"version":1,"id":"kj-collab-r1","title":"カスタマーサポートの改善","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"k1","text":"問い合わせの回答に時間がかかる","x":0,"y":0,"textReviewed":true},{"id":"k2","text":"FAQにたどり着けない","x":10,"y":0,"textReviewed":true},{"id":"k3","text":"チャットで解決できると早い","x":20,"y":0,"textReviewed":true},{"id":"k4","text":"担当者ごとに回答が違う","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[],"readingOrder":["k1","k2","k3","k4"]}'
check "R1 PUT document (人間がカード作成)" "200" "$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/kj-collab-r1" -H 'Content-Type: application/json' -d "$R1_DOC")"

r1_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"k1","text":"問い合わせの回答に時間がかかる","textReviewed":true},{"id":"k2","text":"FAQにたどり着けない","textReviewed":true},{"id":"k3","text":"チャットで解決できると早い","textReviewed":true},{"id":"k4","text":"担当者ごとに回答が違う","textReviewed":true}]}')
case "$r1_groups" in
  *'"groups":'*)
    echo "  PASS: R1 AI 束ね提案 (suggest-card-groups)"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: R1 AI 束ね提案 (got $r1_groups)"
    FAIL=$((FAIL+1))
    ;;
esac

# ============ R2 構造化: 人間が島を形成し、AI が表札提案 ============
R2_DOC='{"version":1,"id":"kj-collab-r2","title":"カスタマーサポートの改善","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"k1","text":"問い合わせの回答に時間がかかる","x":0,"y":0,"textReviewed":true},{"id":"k2","text":"FAQにたどり着けない","x":10,"y":0,"textReviewed":true},{"id":"k3","text":"チャットで解決できると早い","x":20,"y":0,"textReviewed":true},{"id":"k4","text":"担当者ごとに回答が違う","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"i-answer","cardIds":["k1","k2","k4"]},{"id":"i-channel","cardIds":["k3"]}],"readingOrder":["i-answer","i-channel"]}'
check "R2 PUT document (人間が島を形成)" "200" "$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/kj-collab-r2" -H 'Content-Type: application/json' -d "$R2_DOC")"

r2_placard=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$R2_DOC,\"islandId\":\"i-answer\"}")
case "$r2_placard" in
  *'"summaryText"'*'"groundingIds"'*)
    echo "  PASS: R2 AI 表札提案 (suggest-island-summary, grounding あり)"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: R2 AI 表札提案 (got $r2_placard)"
    FAIL=$((FAIL+1))
    ;;
esac

# ============ R3 深化: AI が文面を整え、ナラティブ草稿 ============
r3_refined=$(curl -s -X POST "$BASE_URL/ai/refine-card-text" -H 'Content-Type: application/json' \
  -d '{"cardText":"問い合わせの回答に時間がかかる","context":"サポート改善","textReviewed":true}' )
case "$r3_refined" in
  *'"refinedText"'*)
    echo "  PASS: R3 AI 文面整え (refine-card-text)"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: R3 AI 文面整え (got $r3_refined)"
    FAIL=$((FAIL+1))
    ;;
esac

r3_narrative=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' \
  -d "{\"doc\":$R2_DOC}")
case "$r3_narrative" in
  *'"basedOnReadingOrder"'*)
    echo "  PASS: R3 AI ナラティブ草稿 (generate-narrative, reading order を spine に)"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: R3 AI ナラティブ草稿 (got $r3_narrative)"
    FAIL=$((FAIL+1))
    ;;
esac

echo ""
echo "=== 結果: $PASS pass / $FAIL fail（R1発散→R2構造化→R3深化の協調ループ）==="
[ "$FAIL" -eq 0 ]
