#!/usr/bin/env bash
# Standard business-flow E2E: 定性調査アナリストのKJ法整理フローを、ローカルLLM
# （課金なし）へ縮退した状態で固定する（ドッグフーディング iteration 41）。
#
# 業態: 調査会社（定性調査）
# 想定人物: 定性調査アナリスト
# 業務領域: インタビュー発言のKJ法による島化・表札・ナラティブ
# 操作内容: 文書作成 -> カード確認(レビュー済み) -> 文面整え(refine) ->
#          島の表札AI提案(island-summary) -> ナラティブ草稿(narrative) -> 読戻し
# 注意事項: SafeMode で未レビュー文は LLM へ送られない(422)。カードはレビュー済み
#          にしてからAIを使用する。
#
# LLM縮退（課金なし・決定的）: scripts/stub_local_llm.py が KJ_ATLAS_LLM_PROVIDER=
# local の /generate 契約に canned 応答を返す。DeepSeek 等の課金APIは不要。
# 実ローカルLLM（例: Ollama）へ切り替えるには KJ_ATLAS_LOCAL_LLM_BASE_URL を
# 差し替えるだけでよい（/generate 契約は同一）。
#
# Usage:
#   ./verify_business_flow_e2e.sh [PORT]
#     PORT  default 8000 (backend). Stub LLM uses PORT+1 to avoid collisions.
#
# Requires the backend venv (KJ_ATLAS_DATABASE_URL default sqlite) and ports free.

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

MOCK_LLM="$ROOT_DIR/03_Implement/deploy/tools/mock_local_llm.py"

echo "=== kj-atlas standard business-flow E2E (local LLM mock) ==="
echo "  backend : $BASE_URL"
echo "  mock LLM: http://127.0.0.1:${STUB_PORT} ($MOCK_LLM)"

# 1. Start the deterministic, GPU-free mock local LLM (free / no billing).
"$VENV_PYTHON" "$MOCK_LLM" --host 127.0.0.1 --port "$STUB_PORT" > /tmp/kj_biz_stub.log 2>&1 &
STUB_PID=$!
sleep 2

# 2. Fresh migrated DB (deterministic run, independent of local state).
TMP_DB="$(mktemp /tmp/kj_biz_XXXXXX.sqlite3)"
(cd "$BACKEND_DIR" && KJ_ATLAS_DATABASE_URL="sqlite:///$TMP_DB" \
  "$VENV_PYTHON" -m alembic upgrade head > /tmp/kj_biz_migrate.log 2>&1)

# 3. Start the backend with KJ_ATLAS_LLM_PROVIDER=local pointed at the mock.
KJ_ATLAS_LLM_PROVIDER=local \
KJ_ATLAS_LOCAL_LLM_BASE_URL="http://127.0.0.1:${STUB_PORT}" \
KJ_ATLAS_DATABASE_URL="sqlite:///$TMP_DB" \
  "$VENV_PYTHON" -m uvicorn kj_atlas_api.main:app --port "$BACKEND_PORT" --host 127.0.0.1 \
  > /tmp/kj_biz_backend.log 2>&1 &
BACKEND_PID=$!

for _ in $(seq 1 30); do
  curl -s -o /dev/null "$BASE_URL/healthz" && break
  sleep 1
done
check "backend /healthz" "200" "$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/healthz")"

# 3. Standard business flow.
DOC_ID="biz-flow-survey"
DOC='{"version":1,"id":"'$DOC_ID'","title":"インタビュー発言の整理","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"c1","text":"待ち時間が長いと感じた","x":0,"y":0,"textReviewed":true},{"id":"c2","text":"接客は丁寧だった","x":10,"y":0,"textReviewed":true},{"id":"c3","text":"また利用したい","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"i1","cardIds":["c1","c2","c3"]}],"readingOrder":["i1"]}'

# 3a. 文書作成（アナリストがインタビュー発言をカード化して島に束ねる）。
put_code=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$DOC_ID" \
  -H 'Content-Type: application/json' -d "$DOC")
check "PUT document (作成)" "200" "$put_code"

# 3b. 読戻し（保存確認）。
get_code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$DOC_ID")
check "GET document (読戻し)" "200" "$get_code"

# 3c. 文面整え（refine-card-text、ローカルLLM経由）。
refined=$(curl -s -X POST "$BASE_URL/ai/refine-card-text" -H 'Content-Type: application/json' \
  -d '{"cardText":"待ち時間が長いと感じた","context":"店舗","textReviewed":true}' )
case "$refined" in
  *'"refinedText"'*)
    echo "  PASS: refine-card-text via local LLM"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: refine-card-text (got $refined)"
    FAIL=$((FAIL+1))
    ;;
esac

# 3d. 島の表札AI提案（suggest-island-summary、メンバーカードのみ grounding）。
summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$DOC,\"islandId\":\"i1\"}")
case "$summary" in
  *'"groundingIds":["c1","c2","c3"]'*)
    echo "  PASS: suggest-island-summary groundingIds = member cards"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: suggest-island-summary (got $summary)"
    FAIL=$((FAIL+1))
    ;;
esac

# 3e. ナラティブ草稿（generate-narrative、reading order を spine に）。
narrative=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' \
  -d "{\"doc\":$DOC}")
case "$narrative" in
  *'"basedOnReadingOrder":["i1"]'*)
    echo "  PASS: generate-narrative basedOnReadingOrder = reading order"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: generate-narrative (got $narrative)"
    FAIL=$((FAIL+1))
    ;;
esac

# 3f. 注意事項: 未レビューカードを含む文書は LLM 経路で 422（SafeMode 境界）。
UNREVIEWED='{"version":1,"id":"biz-unreviewed","title":"未レビュー","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"u1","text":"未レビュー発言","x":0,"y":0}],"edges":[],"islands":[{"id":"u-i","cardIds":["u1"]}],"readingOrder":["u-i"]}'
curl -s -o /dev/null -X PUT "$BASE_URL/docs/biz-unreviewed" -H 'Content-Type: application/json' -d "$UNREVIEWED"
unreviewed_code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/ai/suggest-island-summary" \
  -H 'Content-Type: application/json' -d "{\"doc\":$UNREVIEWED,\"islandId\":\"u-i\"}")
check "unreviewed text blocked (422, SafeMode)" "422" "$unreviewed_code"

echo ""
echo "--- シナリオ2: 新規事業企画ワークショップ（ファシリテーター） ---"
# 業態: 事業企画コンサルティング / 想定人物: ファシリテーター
# 業務領域: 参加者のアイデア発言を KJ 法で構造化（カード→グループ→島）
# 操作内容: 文書作成 -> 発言カード化 -> suggest-card-groups(発言の束ね提案)
#           -> suggest-island-summary(島の表札) -> generate-narrative
# 注意事項: refine 等で参加者の意図を変えない（mock は元文面を保持）
WS_DOC_ID="biz-flow-workshop"
WS_DOC='{"version":1,"id":"'$WS_DOC_ID'","title":"新規事業アイデア出し","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"w1","text":"顧客の待ち時間を可視化する","x":0,"y":0,"textReviewed":true},{"id":"w2","text":"予約の空き状況を通知する","x":10,"y":0,"textReviewed":true},{"id":"w3","text":"スタッフの負荷を平準化する","x":20,"y":0,"textReviewed":true},{"id":"w4","text":"再来店を促す施策を打つ","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"ws-i","cardIds":["w1","w2","w3","w4"]}],"readingOrder":["ws-i"]}'

ws_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$WS_DOC_ID" \
  -H 'Content-Type: application/json' -d "$WS_DOC")
check "WS PUT document (作成)" "200" "$ws_put"

# 発言の束ね提案（suggest-card-groups、モックは2グループに分割）。
groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"w1","text":"顧客の待ち時間を可視化する","textReviewed":true},{"id":"w2","text":"予約の空き状況を通知する","textReviewed":true},{"id":"w3","text":"スタッフの負荷を平準化する","textReviewed":true},{"id":"w4","text":"再来店を促す施策を打つ","textReviewed":true}]}')
case "$groups" in
  *'"groups":'*'"cardIds":["w1","w2"]'*'"cardIds":["w3","w4"]'*)
    echo "  PASS: suggest-card-groups splits all 4 cards into 2 groups"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: suggest-card-groups (got $groups)"
    FAIL=$((FAIL+1))
    ;;
esac

# 島の表札（モックはメンバーカードを grounding）。
ws_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$WS_DOC,\"islandId\":\"ws-i\"}")
case "$ws_summary" in
  *'"groundingIds":["w1","w2","w3"]'*)
    echo "  PASS: WS suggest-island-summary groundingIds = member cards"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: WS suggest-island-summary (got $ws_summary)"
    FAIL=$((FAIL+1))
    ;;
esac

echo ""
echo "--- シナリオ3: カスタマーサポート品質管理（クレーム真因分析） ---"
# 業態: カスタマーサポートセンター（製造業の品質管理）
# 想定人物: サポート品質マネージャー
# 業務領域: クレーム・現場証言のKJ整理と、矛盾する証言の検出による真因分析
# 操作内容: 文書作成 -> 証言カード化(レビュー済み) -> detect-contradiction(証言間の
#          論理的矛盾をAI検出) -> suggest-island-summary(島の表札) -> 読戻し
# 注意事項: 矛盾検出は「単なる意見の相違」と「論理的矛盾」を区別する（後者のみ報告）。
#          証言の文面は refine 等で変更しない（現場の完全性・evidence としての位置づけ）。
#          SafeMode の未レビュー境界(422)は島要約・ナラティブ等の doc 文脈ルートで効き、
#          detect-contradiction は doc 文脈を持たない（issue 参照）。
QM_DOC_ID="biz-flow-claim-analysis"
QM_DOC='{"version":1,"id":"'$QM_DOC_ID'","title":"クレーム証言の真因分析","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"q1","text":"受注後に納期変更の連絡が来た","x":0,"y":0,"textReviewed":true},{"id":"q2","text":"営業は納期を守ると言った","x":10,"y":0,"textReviewed":true},{"id":"q3","text":"サポートは謝罪のみで原因を説明しなかった","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"qm-i","cardIds":["q1","q2","q3"]}],"readingOrder":["qm-i"]}'

qm_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$QM_DOC_ID" \
  -H 'Content-Type: application/json' -d "$QM_DOC")
check "QM PUT document (作成)" "200" "$qm_put"

qm_get=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$QM_DOC_ID")
check "QM GET document (読戻し)" "200" "$qm_get"

# 証言間の論理的矛盾をAI検出（detect-contradiction、モックは矛盾なしと応答）。
contradiction=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"q1","text":"受注後に納期変更の連絡が来た","textReviewed":true},"cardB":{"id":"q2","text":"営業は納期を守ると言った","textReviewed":true}}')
case "$contradiction" in
  *'"hasContradiction":false'*)
    echo "  PASS: detect-contradiction returns structured result (mock: no contradiction)"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: detect-contradiction (got $contradiction)"
    FAIL=$((FAIL+1))
    ;;
esac

# 島の表札（モックはメンバーカードを grounding）。
qm_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$QM_DOC,\"islandId\":\"qm-i\"}")
case "$qm_summary" in
  *'"groundingIds":["q1","q2","q3"]'*)
    echo "  PASS: QM suggest-island-summary groundingIds = member cards"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: QM suggest-island-summary (got $qm_summary)"
    FAIL=$((FAIL+1))
    ;;
esac

# 注意事項（SEC-AI-SAFEMODE-02）: 文書非依存AIルートも未レビュー本文を
# 422 で拒否する（textReviewed は fail-closed 既定で未指定=未レビュー扱い）。
unreviewed_contradiction=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/ai/detect-contradiction" \
  -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"q-u1","text":"確認前の証言","textReviewed":false},"cardB":{"id":"q-u2","text":"別の確認前証言","textReviewed":true}}')
check "QM detect-contradiction unreviewed text blocked (422, SEC-AI-SAFEMODE-02)" "422" "$unreviewed_contradiction"

echo ""
echo "--- シナリオ5: 報道・編集（ナラティブのA/B照合検証） ---"
# 業態: 報道・メディア（論説・編集）
# 想定人物: 編集者（ナラティブの正確性を検証）
# 業務領域: カード（事実）とナラティブ草稿の A/B 照合による整合性検証
# 操作内容: 文書作成 -> カードレビュー済み化 -> ナラティブ草稿(generate-narrative)
#          -> check-narrative(A/B照合: カードにない主張・触れていない島を検出) -> 読戻し
# 注意事項: ナラティブはカードの事実を超える主張をしない。check-narrative は
#          direction（b_missing_in_a / a_missing_in_b）で不整合を報告する。
#          未レビューカードを含む文書はナラティブ経路で 422（SafeMode）。
ED_DOC_ID="biz-flow-editorial"
ED_DOC='{"version":1,"id":"'$ED_DOC_ID'","title":"市議会補正予算の記事草稿","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"e1","text":"市議会は補正予算案を可決した","x":0,"y":0,"textReviewed":true},{"id":"e2","text":"財源には予備費を充てる","x":10,"y":0,"textReviewed":true},{"id":"e3","text":"委員長は賛成の立場を表明した","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"ed-i","cardIds":["e1","e2","e3"]}],"readingOrder":["ed-i"]}'

ed_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$ED_DOC_ID" \
  -H 'Content-Type: application/json' -d "$ED_DOC")
check "ED PUT document (作成)" "200" "$ed_put"

# ナラティブ草稿（モックは reading order を spine に）。
ed_narrative=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' \
  -d "{\"doc\":$ED_DOC}")
case "$ed_narrative" in
  *'"basedOnReadingOrder":["ed-i"]'*)
    echo "  PASS: ED generate-narrative basedOnReadingOrder = reading order"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: ED generate-narrative (got $ed_narrative)"
    FAIL=$((FAIL+1))
    ;;
esac

# A/B照合（check-narrative、モックは不整合なしと応答）。
ED_NARR_TEXT="（草稿）市議会は補正予算案を可決し、財源には予備費を充てる。委員長は賛成の立場を表明した。"
narrative_check=$(curl -s -X POST "$BASE_URL/ai/check-narrative" -H 'Content-Type: application/json' \
  -d "{\"doc\":$ED_DOC,\"narrativeText\":\"$ED_NARR_TEXT\",\"basedOnReadingOrder\":[\"ed-i\"]}")
case "$narrative_check" in
  *'"issues":[]'*)
    echo "  PASS: check-narrative A/B照合 returns no issues (mock)"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: check-narrative (got $narrative_check)"
    FAIL=$((FAIL+1))
    ;;
esac

# 注意事項: 未レビューカードを含む文書は check-narrative で 422（SafeMode）。
ED_UNREVIEWED='{"version":1,"id":"biz-flow-editorial-unr","title":"未レビュー記事","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"eu1","text":"確認前の事実メモ","x":0,"y":0}],"edges":[],"islands":[{"id":"ed-u","cardIds":["eu1"]}],"readingOrder":["ed-u"]}'
ed_unreviewed_code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/ai/check-narrative" \
  -H 'Content-Type: application/json' \
  -d "{\"doc\":$ED_UNREVIEWED,\"narrativeText\":\"$ED_NARR_TEXT\"}")
check "ED check-narrative unreviewed text blocked (422, SafeMode)" "422" "$ed_unreviewed_code"

echo ""
echo "--- シナリオ6: 調査研究員のW型探究（多ラウンドジャーニーの保存・継続） ---"
# 業態: 調査・研究（社会科学 / 市場調査）
# 想定人物: 調査研究員（W型探究でラウンドを重ねる）
# 業務領域: 複数ラウンドの探究ジャーニー（問いの深化）の保存・継続・並行編集の保護
# 操作内容: ジャーニー開始(POST If-None-Match:*) -> 読戻し(GET) ->
#          ラウンド深化(POST If-Match 更新) -> 並行編集の検出(古いIf-Match->409) -> 破棄(DELETE)
# 注意事項: inquiry-bundle は CAS（If-Match/If-None-Match）で楽観的並行制御。
#          前条件なしは 428・並行更新は 409。ラウンドの不変条件（iteration 単調）はクライアント責務。
WT_ID="biz-flow-wtype"
WT_BUNDLE='{"schemaVersion":"1.0.0","journey":{"schemaVersion":"1.0.0","journeyId":"'$WT_ID'","title":"窓口待ち時間を捉え直す","originSnapshotIds":["snapshot-origin"],"roundRecords":[{"roundId":"r1","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","stage":"r2_situation_grasp","iteration":1,"parentRoundIds":[],"status":"handed_off","theme":"来庁者は何を見て待つか","inputSnapshotIds":["snapshot-origin"],"outputSnapshotId":"snapshot-r1","handoff":{"carryoverRefs":[],"heldRefs":[],"unresolvedQuestions":["案内表示を読むか"],"fieldworkRequests":[{"fieldworkRequestId":"fw-1","question":"注視状況を観察する"}]}}],"resolvedFieldworkQuestionIds":[],"status":"in_progress"},"snapshots":[{"schemaVersion":"1.0.0","snapshotId":"snapshot-origin","createdAt":"2026-08-15T00:00:00Z","canonicalDigest":"sha256:origin","document":{"version":1,"id":"doc-wtype","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"obs-1","text":"観察メモ","x":0,"y":0}],"edges":[],"islands":[]}}]}'
# ラウンド2を追加した更新版（探究の深化）。
WT_BUNDLE_V2='{"schemaVersion":"1.0.0","journey":{"schemaVersion":"1.0.0","journeyId":"'$WT_ID'","title":"窓口待ち時間を捉え直す","originSnapshotIds":["snapshot-origin"],"roundRecords":[{"roundId":"r1","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","stage":"r2_situation_grasp","iteration":1,"parentRoundIds":[],"status":"handed_off","theme":"来庁者は何を見て待つか","inputSnapshotIds":["snapshot-origin"],"outputSnapshotId":"snapshot-r1","handoff":{"carryoverRefs":[],"heldRefs":[],"unresolvedQuestions":["案内表示を読むか"],"fieldworkRequests":[{"fieldworkRequestId":"fw-1","question":"注視状況を観察する"}]}},{"roundId":"r2","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","stage":"r3_essence_pursuit","iteration":2,"parentRoundIds":["r1"],"status":"in_progress","theme":"負担の正体を捉える","inputSnapshotIds":["snapshot-r1"],"outputSnapshotId":"snapshot-r2","handoff":{"carryoverRefs":[],"heldRefs":[],"unresolvedQuestions":[],"fieldworkRequests":[]}}],"resolvedFieldworkQuestionIds":["fw-1"],"status":"in_progress"},"snapshots":[{"schemaVersion":"1.0.0","snapshotId":"snapshot-origin","createdAt":"2026-08-15T00:00:00Z","canonicalDigest":"sha256:origin","document":{"version":1,"id":"doc-wtype","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"obs-1","text":"観察メモ","x":0,"y":0}],"edges":[],"islands":[]}},{"schemaVersion":"1.0.0","snapshotId":"snapshot-r1","createdAt":"2026-08-15T00:00:00Z","canonicalDigest":"sha256:r1","document":{"version":1,"id":"doc-wtype-r1","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[],"edges":[],"islands":[]}}]}'

# 6a. ジャーニー開始（If-None-Match: * で作成、201 + ETag）。
wt_create=$(curl -s -i -X POST "$BASE_URL/inquiry-bundles/$WT_ID" \
  -H 'Content-Type: application/json' -H 'If-None-Match: *' -d "$WT_BUNDLE")
wt_create_code=$(echo "$wt_create" | head -1 | grep -oE '[0-9]{3}')
wt_etag=$(echo "$wt_create" | tr -d '\r' | grep -i '^ETag:' | sed 's/ETag: *//I')
check "WT ジャーニー開始 (201 + ETag)" "201" "$wt_create_code"
[ -n "$wt_etag" ] && { echo "  PASS: WT ETag acquired ($wt_etag)"; PASS=$((PASS+1)); } || { echo "  FAIL: WT ETag missing"; FAIL=$((FAIL+1)); }

# 6b. 読戻し（ジャーニー構造が保持されている）。
wt_get=$(curl -s -X GET "$BASE_URL/inquiry-bundles/$WT_ID")
case "$wt_get" in
  *'"roundRecords"'*'"theme":"来庁者は何を見て待つか"'*)
    echo "  PASS: WT 読戻し（roundRecords 保持）"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: WT 読戻し（got ${wt_get:0:120}）"
    FAIL=$((FAIL+1))
    ;;
esac

# 6c. ラウンド深化（If-Match で更新、204 + ETag 繰り上げ）。
wt_update=$(curl -s -i -X POST "$BASE_URL/inquiry-bundles/$WT_ID" \
  -H 'Content-Type: application/json' -H "If-Match: $wt_etag" -d "$WT_BUNDLE_V2")
wt_update_code=$(echo "$wt_update" | head -1 | grep -oE '[0-9]{3}')
check "WT ラウンド深化 (204)" "204" "$wt_update_code"
wt_etag2=$(echo "$wt_update" | tr -d '\r' | grep -i '^ETag:' | sed 's/ETag: *//I')

# 6d. 並行編集の検出（古い ETag で更新 -> 409）。
wt_stale_code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/inquiry-bundles/$WT_ID" \
  -H 'Content-Type: application/json' -H "If-Match: $wt_etag" -d "$WT_BUNDLE_V2")
check "WT 並行編集を検出 (古いIf-Match -> 409)" "409" "$wt_stale_code"

# 6e. 前条件なしは 428（CAS 必須）。
wt_no_precond=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/inquiry-bundles/$WT_ID" \
  -H 'Content-Type: application/json' -d "$WT_BUNDLE_V2")
check "WT 前条件なし (428)" "428" "$wt_no_precond"

# 6f. 破棄（DELETe も CAS: 現在の ETag が必要）。
wt_del=$(curl -s -o /dev/null -w '%{http_code}' -X DELETE "$BASE_URL/inquiry-bundles/$WT_ID" \
  -H "If-Match: $wt_etag2")
check "WT ジャーニー破棄 (204, If-Match)" "204" "$wt_del"

echo ""
echo "=== Result: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ]
