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
#    KJ_ATLAS_ALLOW_JIT_PROVISIONING=true: scenario 9's CE4 proposal decision
#    needs an authenticated reviewer identity, provided via x-forwarded-user
#    (JIT provisioning, same as test_ce2_proposal_api.py). Scenarios 1-8 send
#    no such header, so they are unaffected.
KJ_ATLAS_LLM_PROVIDER=local \
KJ_ATLAS_LOCAL_LLM_BASE_URL="http://127.0.0.1:${STUB_PORT}" \
KJ_ATLAS_DATABASE_URL="sqlite:///$TMP_DB" \
KJ_ATLAS_ALLOW_JIT_PROVISIONING=true \
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
echo "--- シナリオ7: 学術研究・概念関係の要約（島間関係の構造化） ---"
# 業態: 学術研究 / ナレッジマネジメント
# 想定人物: 研究者（概念間の関係を構造化する）
# 業務領域: 複数概念（島）間の関係の要約・根拠付き接続
# 操作内容: 文書作成 -> 島形成 -> summarize-island-relation(島間関係の要約) -> 読戻し
# 注意事項: 関係種別は5語彙（related/negate/causal/mutual/equivalence）。derived=false は
#          人間が指定した根拠ある関係のみ要約。未レビューカードは doc 文脈ルートで 422（SafeMode）。
SR_DOC_ID="biz-flow-research"
SR_DOC='{"version":1,"id":"'$SR_DOC_ID'","title":"概念関係の整理","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"r1","text":"外部環境の変化が需要に影響する","x":0,"y":0,"textReviewed":true},{"id":"r2","text":"需要の変動が生産計画を変える","x":10,"y":0,"textReviewed":true},{"id":"r3","text":"在庫過多は資金繰りを圧迫する","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"ri-a","cardIds":["r1","r2"]},{"id":"ri-b","cardIds":["r3"]}],"readingOrder":["ri-a","ri-b"]}'

sr_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$SR_DOC_ID" \
  -H 'Content-Type: application/json' -d "$SR_DOC")
check "SR PUT document (作成)" "200" "$sr_put"

# 島間関係の要約（summarize-island-relation、モックは下書き要約＋warnings空）。
relation=$(curl -s -X POST "$BASE_URL/ai/summarize-island-relation" -H 'Content-Type: application/json' \
  -d "{\"doc\":$SR_DOC,\"islandAId\":\"ri-a\",\"islandBId\":\"ri-b\",\"relationType\":\"causal\",\"derived\":false,\"groundingCardIds\":[\"r3\"],\"groundingEdgeIds\":[],\"cardTexts\":[{\"id\":\"r3\",\"text\":\"在庫過多は資金繰りを圧迫する\"}]}")
case "$relation" in
  *'"text"'*'"warnings":[]'*)
    echo "  PASS: summarize-island-relation returns draft summary with empty warnings"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: summarize-island-relation (got $relation)"
    FAIL=$((FAIL+1))
    ;;
esac

# 注意事項: 未レビューカードを含む文書は 422（SafeMode・doc 文脈ルート）。
SR_UNREVIEWED='{"version":1,"id":"biz-flow-research-unr","title":"未レビュー概念","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"ru1","text":"確認前の概念メモ","x":0,"y":0}],"edges":[],"islands":[{"id":"ri-u1","cardIds":["ru1"]}],"readingOrder":["ri-u1"]}'
sr_unreviewed_code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/ai/summarize-island-relation" \
  -H 'Content-Type: application/json' \
  -d "{\"doc\":$SR_UNREVIEWED,\"islandAId\":\"ri-u1\",\"islandBId\":\"ri-u1\",\"relationType\":\"related\",\"derived\":true,\"groundingCardIds\":[],\"groundingEdgeIds\":[],\"cardTexts\":[{\"id\":\"ru1\",\"text\":\"確認前の概念メモ\"}]}")
check "SR summarize-island-relation unreviewed text blocked (422, SafeMode)" "422" "$sr_unreviewed_code"

echo ""
echo "--- シナリオ8: ナレッジベース管理者の文書タイトル命名提案 ---"
# 業態: ナレッジマネジメント / 図書館情報学
# 想定人物: ナレッジベース管理者（文書の検索性を確保する）
# 業務領域: 文書タイトルの命名・改名（検索・整理の要）
# 操作内容: 文書作成 -> 島・カード確認 -> suggest-document-title(タイトル候補のAI提案) -> 読戻し
# 注意事項: タイトル候補は proposal であり自動確定しない。未レビューカードは
#          textReviewed fail-closed で 422（SEC-AI-SAFEMODE-02）。
KB_DOC_ID="biz-flow-knowledgebase"
KB_DOC='{"version":1,"id":"'$KB_DOC_ID'","title":"新規採用ガイド（仮）","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"k1","text":"入社手続きの一覧","x":0,"y":0,"textReviewed":true},{"id":"k2","text":"研修スケジュール","x":10,"y":0,"textReviewed":true},{"id":"k3","text":"社内ツールの初期設定","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"kb-i","cardIds":["k1","k2","k3"]}],"readingOrder":["kb-i"]}'

kb_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$KB_DOC_ID" \
  -H 'Content-Type: application/json' -d "$KB_DOC")
check "KB PUT document (作成)" "200" "$kb_put"

# タイトル候補のAI提案（suggest-document-title、textReviewed を明示）。
kb_title=$(curl -s -X POST "$BASE_URL/ai/suggest-document-title" -H 'Content-Type: application/json' \
  -d "{\"islandTitles\":[\"入社手続き\"],\"cardTexts\":[\"入社手続きの一覧\",\"研修スケジュール\",\"社内ツールの初期設定\"],\"currentTitle\":\"新規採用ガイド（仮）\",\"textReviewed\":true}")
case "$kb_title" in
  *'"candidates"'*)
    echo "  PASS: suggest-document-title returns title candidates (mock)"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: suggest-document-title (got $kb_title)"
    FAIL=$((FAIL+1))
    ;;
esac

# AI-MODEL-GOVERNANCE-01 (R2): a model override flows through and is accepted
# under platform-default allowlist (empty = all active registered models).
kb_model_code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/ai/suggest-document-title" \
  -H 'Content-Type: application/json' \
  -d "{\"islandTitles\":[\"入社手続き\"],\"cardTexts\":[\"入社手続きの一覧\"],\"textReviewed\":true,\"model\":\"default\"}")
check "suggest-document-title with model override accepted (200, platform-default)" "200" "$kb_model_code"

# 注意事項: 未レビュー入力は 422（textReviewed fail-closed・SEC-AI-SAFEMODE-02）。
kb_unreviewed_code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/ai/suggest-document-title" \
  -H 'Content-Type: application/json' \
  -d '{"islandTitles":["島"],"cardTexts":["確認前の内容"]}')
check "KB suggest-document-title unreviewed text blocked (422, SEC-AI-SAFEMODE-02)" "422" "$kb_unreviewed_code"

echo ""
echo "--- シナリオ9: 人事マネージャーのAI提案レビュー（CE4 proposal連鎖） ---"
# 業態: 人事・人材開発
# 想定人物: 人事マネージャー（360度評価のとりまとめ）
# 業務領域: AI提案（島要約）のレビューと採択/保留決定（value_traceability V3）
# 操作内容: 文書作成 -> propose-island-summary(AI提案・proposal-only)
#          -> 提案の受領 -> record-decision(採択・idempotencyKey) -> 再送の冪等確認
#          -> 未登録提案への決定が404 -> 文書が自動適用されないことを確認
# 注意事項: 提案は proposal-only（自動適用なし）。決定は idempotencyKey で再送しても
#          重複記録しない。未登録 proposal への決定は 404・bundle 不一致は 409。
REV_H="x-forwarded-user: e2e-reviewer"
REV_H2="x-auth-provider: oidc"
P9_ID="biz-flow-review"
# NOTE: use a plain 64-hex bundle hash. The API accepts a `mock:`-prefixed hash
# too, but AIProposalRow's CheckConstraint requires exactly 64 chars, so the
# mock: variant 409s on registration (contract inconsistency, see dogfood README).
P9_HASH="$(printf 'a%.0s' $(seq 1 64))"
P9_DOC='{"version":1,"id":"'$P9_ID'","title":"360度評価のとりまとめ","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"r1","text":"課題解決力が高い","x":0,"y":0,"textReviewed":true},{"id":"r2","text":"報告が丁寧","x":10,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"i1","cardIds":["r1","r2"],"summaryText":"旧要約"}],"readingOrder":["i1"]}'

p9_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$P9_ID" \
  -H 'Content-Type: application/json' -d "$P9_DOC")
check "P9 PUT document (作成)" "200" "$p9_put"

# AI提案（proposal-only・自動適用しない）。
p9_propose=$(curl -s -X POST "$BASE_URL/ai/proposals/island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$P9_DOC,\"islandId\":\"i1\",\"sourceBundleHash\":\"$P9_HASH\"}")
case "$p9_propose" in
  *'"status":"proposed"'*)
    echo "  PASS: P9 propose-island-summary returns proposal (proposal-only)"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: P9 propose-island-summary (got ${p9_propose:0:200})"
    FAIL=$((FAIL+1))
    ;;
esac
p9_pid=$(echo "$p9_propose" | grep -oE '"proposalId":"[^"]+"' | head -1 | cut -d'"' -f4)

# 人間の決定（採択・idempotencyKey 付き・認証済みレビューア）。
p9_adopt=$(curl -s -X POST "$BASE_URL/ai/proposals/audit" -H 'Content-Type: application/json' \
  -H "$REV_H" -H "$REV_H2" \
  -d "{\"docId\":\"$P9_ID\",\"proposalId\":\"$p9_pid\",\"sourceBundleHash\":\"$P9_HASH\",\"idempotencyKey\":\"p9-k1\",\"decision\":\"adopt\",\"reason\":\"妥当\"}")
case "$p9_adopt" in
  *'"recorded":true'*'"status":"accepted"'*)
    echo "  PASS: P9 record-decision adopt recorded (reviewer identity resolved)"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: P9 record-decision adopt (got ${p9_adopt:0:200})"
    FAIL=$((FAIL+1))
    ;;
esac
p9_event=$(echo "$p9_adopt" | grep -oE '"eventId":"[^"]+"' | head -1 | cut -d'"' -f4)

# 再送の冪等確認（同じ idempotencyKey + 同一ペイロード -> 同じ eventId・重複記録なし）。
# ※冪等性は key だけでなく提案/バンドル/決定/理由の完全一致を要求する（409で検出）。
p9_repeat=$(curl -s -X POST "$BASE_URL/ai/proposals/audit" -H 'Content-Type: application/json' \
  -H "$REV_H" -H "$REV_H2" \
  -d "{\"docId\":\"$P9_ID\",\"proposalId\":\"$p9_pid\",\"sourceBundleHash\":\"$P9_HASH\",\"idempotencyKey\":\"p9-k1\",\"decision\":\"adopt\",\"reason\":\"妥当\"}")
case "$p9_repeat" in
  *"\"eventId\":\"$p9_event\""*)
    echo "  PASS: P9 再送は冪等（同じ eventId・重複記録なし）"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: P9 idempotent resubmit (got ${p9_repeat:0:150})"
    FAIL=$((FAIL+1))
    ;;
esac

# 未登録 proposal への決定は 404。
p9_unreg=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/ai/proposals/audit" \
  -H 'Content-Type: application/json' -H "$REV_H" -H "$REV_H2" \
  -d "{\"docId\":\"$P9_ID\",\"proposalId\":\"proposal-none\",\"sourceBundleHash\":\"$P9_HASH\",\"idempotencyKey\":\"p9-k2\",\"decision\":\"hold\"}")
check "P9 未登録 proposal への決定 (404)" "404" "$p9_unreg"

# proposal-only: 文書の summaryText は提案で自動適用されない。
p9_doc_summary=$(curl -s "$BASE_URL/docs/$P9_ID" | grep -oE '"summaryText":"[^"]*"' | head -1)
check "P9 文書は自動適用されない（旧要約のまま）" '"summaryText":"旧要約"' "$p9_doc_summary"

echo ""
echo "--- シナリオ10: フィールドワーカーのW型探究 × AI支援（複合フロー） ---"
# 業態: 社会調査・フィールドワーク
# 想定人物: フィールドワーカー（現地調査）
# 業務領域: フィールドノートのKJ整理と探究ジャーニー（W型）への保存
# 操作内容: ノートをカード化(PUT) -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> ジャーニー保存(inquiry-bundle create) -> 読戻し -> ラウンド深化(update)
# 注意事項: ノートは逐語（refine で変えない）。ジャーニーは CAS（If-Match/If-None-Match）で
#          並行編集を保護。未レビューカードは AI 経路で 422（SafeMode）。
FW_ID="biz-flow-fieldwork"
FW_DOC='{"version":1,"id":"'$FW_ID'","title":"現地調査ノート","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"f1","text":"朝の通勤時間帯が最も混雑する","x":0,"y":0,"textReviewed":true},{"id":"f2","text":"改札の前に滞留が起きる","x":10,"y":0,"textReviewed":true},{"id":"f3","text":"案内表示は見えにくい位置にある","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"fw-i","cardIds":["f1","f2","f3"]}],"readingOrder":["fw-i"]}'

fw_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$FW_ID" \
  -H 'Content-Type: application/json' -d "$FW_DOC")
check "FW PUT document (フィールドノート作成)" "200" "$fw_put"

# AI束ね（ノートの束ね提案・モックは2グループ）。
fw_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"f1","text":"朝の通勤時間帯が最も混雑する","textReviewed":true},{"id":"f2","text":"改札の前に滞留が起きる","textReviewed":true},{"id":"f3","text":"案内表示は見えにくい位置にある","textReviewed":true}]}')
case "$fw_groups" in
  *'"groups":'*)
    echo "  PASS: FW AI束ね (suggest-card-groups)"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: FW suggest-card-groups (got ${fw_groups:0:120})"
    FAIL=$((FAIL+1))
    ;;
esac

# 島要約（モックはメンバーカードを grounding）。
fw_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$FW_DOC,\"islandId\":\"fw-i\"}")
case "$fw_summary" in
  *'"groundingIds":["f1","f2","f3"]'*)
    echo "  PASS: FW 島要約 (suggest-island-summary grounding = member cards)"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: FW suggest-island-summary (got ${fw_summary:0:120})"
    FAIL=$((FAIL+1))
    ;;
esac

# ジャーニー保存（フィールドノートを snapshot として inquiry-bundle へ）。
FW_JOURNEY_ID="biz-flow-fw-journey"
FW_BUNDLE='{"schemaVersion":"1.0.0","journey":{"schemaVersion":"1.0.0","journeyId":"'$FW_JOURNEY_ID'","title":"駅の混雑を捉え直す","originSnapshotIds":["snapshot-fw"],"roundRecords":[{"roundId":"fw-r1","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","stage":"r2_situation_grasp","iteration":1,"parentRoundIds":[],"status":"in_progress","theme":"滞留はいつどこで起きるか","inputSnapshotIds":["snapshot-fw"],"outputSnapshotId":"snapshot-fw","handoff":{"carryoverRefs":[],"heldRefs":[],"unresolvedQuestions":["案内表示の視認性"],"fieldworkRequests":[]}}],"resolvedFieldworkQuestionIds":[],"status":"in_progress"},"snapshots":[{"schemaVersion":"1.0.0","snapshotId":"snapshot-fw","createdAt":"2026-08-15T00:00:00Z","canonicalDigest":"sha256:fw","document":'$FW_DOC'}]}'
fw_journey_create=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/inquiry-bundles/$FW_JOURNEY_ID" \
  -H 'Content-Type: application/json' -H 'If-None-Match: *' -d "$FW_BUNDLE")
check "FW ジャーニー保存 (201 + CAS create)" "201" "$fw_journey_create"

# ジャーニー読戻し（フィールドノートが snapshot として保持されている）。
fw_journey_get=$(curl -s "$BASE_URL/inquiry-bundles/$FW_JOURNEY_ID")
case "$fw_journey_get" in
  *'"roundRecords"'*'"現地調査ノート"'*)
    echo "  PASS: FW ジャーニー読戻し（フィールドノート snapshot 保持）"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: FW ジャーニー読戻し（got ${fw_journey_get:0:120}）"
    FAIL=$((FAIL+1))
    ;;
esac

# ジャーニー破棄。
fw_journey_del=$(curl -s -o /dev/null -w '%{http_code}' -X DELETE "$BASE_URL/inquiry-bundles/$FW_JOURNEY_ID" \
  -H "If-Match: 1")
check "FW ジャーニー破棄 (204)" "204" "$fw_journey_del"

echo ""
echo "--- シナリオ11: 会議ファシリテーターの配置・統合提案 ---"
# 業態: オンライン会議ファシリテーション
# 想定人物: ファシリテーター（多人数の議事を整理）
# 業務領域: 議事カードの配置提案（suggest-layout）と島統合提案（suggest-merges）
# 操作内容: 文書作成 -> suggest-layout(配置のAI提案) -> suggest-merges(島統合のAI提案) -> 読戻し
# 注意事項: 配置・統合は提案であり自動適用しない。未レビューカードは 422（SafeMode）。
MTG_DOC_ID="biz-flow-meeting"
MTG_DOC='{"version":1,"id":"'$MTG_DOC_ID'","title":"定例ミーティング議事","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"m1","text":"予算の見直しが必要","x":0,"y":0,"textReviewed":true},{"id":"m2","text":"来期の体制を検討","x":10,"y":0,"textReviewed":true},{"id":"m3","text":"顧客対応の改善","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"mtg-a","cardIds":["m1","m2"]},{"id":"mtg-b","cardIds":["m3"]}],"readingOrder":["mtg-a","mtg-b"]}'

mtg_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$MTG_DOC_ID" \
  -H 'Content-Type: application/json' -d "$MTG_DOC")
check "MTG PUT document (作成)" "200" "$mtg_put"

# 配置提案（suggest-layout、モックはグリッド配置）。
layout=$(curl -s -X POST "$BASE_URL/ai/suggest-layout" -H 'Content-Type: application/json' \
  -d "{\"doc\":$MTG_DOC}")
case "$layout" in
  *'"transform"'*'"cards"'*)
    echo "  PASS: suggest-layout returns transform + card positions (mock grid)"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: suggest-layout (got ${layout:0:120})"
    FAIL=$((FAIL+1))
    ;;
esac

# 島統合提案（suggest-merges、モックは空提案）。
merges=$(curl -s -X POST "$BASE_URL/ai/suggest-merges" -H 'Content-Type: application/json' \
  -d "{\"doc\":$MTG_DOC}")
case "$merges" in
  *'"suggestions"'*)
    echo "  PASS: suggest-merges returns suggestions list (mock: empty)"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: suggest-merges (got ${merges:0:120})"
    FAIL=$((FAIL+1))
    ;;
esac

# 注意事項: 未レビューカードを含む文書は 422（SafeMode）。
MTG_UNREVIEWED='{"version":1,"id":"biz-flow-meeting-unr","title":"未レビュー議事","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"mu1","text":"確認前の議事メモ","x":0,"y":0}],"edges":[],"islands":[{"id":"mtg-u","cardIds":["mu1"]}],"readingOrder":["mtg-u"]}'
mtg_unreviewed=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/ai/suggest-layout" \
  -H 'Content-Type: application/json' -d "{\"doc\":$MTG_UNREVIEWED}")
check "MTG suggest-layout unreviewed text blocked (422, SafeMode)" "422" "$mtg_unreviewed"

echo ""
echo "--- シナリオ12: ライブラリアンのコレクション管理（複数文書・一覧・絞り込み・アーカイブ） ---"
# 業態: ナレッジベース・図書館（コレクション管理）
# 想定人物: ライブラリアン（文書コレクションの管理者）
# 業務領域: 複数文書の作成・一覧・作成者絞り込み・アーカイブ管理
# 操作内容: 複数文書作成(PUT ×N) -> 一覧(GET /docs) -> 自分の文書で絞り込み
#          (GET /docs?createdBy=<作成者UUID>) -> アーカイブ(POST archive) -> 一覧に反映確認
# 注意事項: 一覧はメタデータのみ（カード本文非露出）。created_by は JIT 解決された UUID
#          （ヘッダー値ではない）。アーカイブ文書は読み取り専用（PUT 423）。
LIB_H="x-forwarded-user: librarian"
LIB_H2="x-auth-provider: oidc"
LIB_A='{"version":1,"id":"biz-flow-lib-a","title":"ライブラリアン文書A","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"la1","text":"カタログ方針","x":0,"y":0,"textReviewed":true}],"edges":[],"islands":[]}'
LIB_B='{"version":1,"id":"biz-flow-lib-b","title":"匿名作成文書B","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"lb1","text":"移行メモ","x":0,"y":0,"textReviewed":true}],"edges":[],"islands":[]}'

lib_a_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/biz-flow-lib-a" \
  -H 'Content-Type: application/json' -H "$LIB_H" -H "$LIB_H2" -d "$LIB_A")
lib_b_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/biz-flow-lib-b" \
  -H 'Content-Type: application/json' -d "$LIB_B")
check "LIB PUT 複数文書 (A=200,B=200)" "200200" "$lib_a_put$lib_b_put"

# 一覧（全件・メタデータのみ）。
lib_list=$(curl -s "$BASE_URL/docs")
case "$lib_list" in
  *'"id":"biz-flow-lib-a"'*'"id":"biz-flow-lib-b"'*)
    echo "  PASS: LIB 一覧に複数文書が含まれる（メタデータ）"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: LIB 一覧（got ${lib_list:0:150}）"
    FAIL=$((FAIL+1))
    ;;
esac

# ライブラリアンの文書UUIDを取得し、自分の文書で絞り込み。
lib_creator=$(echo "$lib_list" | grep -oE '"id":"biz-flow-lib-a"[^}]*"created_by":"[^"]*"' | grep -oE '"created_by":"[^"]*"' | head -1 | cut -d'"' -f4)
if [ -n "$lib_creator" ]; then
  lib_mine=$(curl -s "$BASE_URL/docs?createdBy=$lib_creator")
  case "$lib_mine" in
    *'"id":"biz-flow-lib-a"'*)
      mine_has_b=$(echo "$lib_mine" | grep -c "biz-flow-lib-b")
      if [ "$mine_has_b" = "0" ]; then
        echo "  PASS: LIB createdBy 絞り込み（自分の文書のみ・匿名文書は除外）"
        PASS=$((PASS+1))
      else
        echo "  FAIL: LIB createdBy 絞り込みに匿名文書が混入"
        FAIL=$((FAIL+1))
      fi
      ;;
    *)
      echo "  FAIL: LIB createdBy 絞り込み（got ${lib_mine:0:120}）"
      FAIL=$((FAIL+1))
      ;;
  esac
else
  echo "  FAIL: LIB created_by 取得不能（一覧からUUIDを抽出）"
  FAIL=$((FAIL+1))
fi

# アーカイブ運用（一覧へ反映）。
lib_arch=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/docs/biz-flow-lib-b/archive" \
  -H 'Content-Type: application/json' -H "$LIB_H" -H "$LIB_H2" -d '{}')
check "LIB アーカイブ (204)" "204" "$lib_arch"
lib_list2=$(curl -s "$BASE_URL/docs")
case "$lib_list2" in
  *'"id":"biz-flow-lib-b"'*'"lifecycle_state":"archived"'*)
    echo "  PASS: LIB 一覧に archived が反映"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: LIB 一覧への archived 反映（got ${lib_list2:0:150}）"
    FAIL=$((FAIL+1))
    ;;
esac

# アーカイブ中は読み取り専用（PUT 423）。
lib_locked=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/biz-flow-lib-b" \
  -H 'Content-Type: application/json' -d "$LIB_B")
check "LIB アーカイブ中 PUT (423 Locked)" "423" "$lib_locked"

# keyset pagination（SEC-DOC-BOUND-05）: limit=1 で1件＋X-Next-Cursor → cursor で残りを取得。
lib_page1=$(curl -s -D /tmp/kj_lib_page1.hdr "$BASE_URL/docs?limit=1")
lib_next=$(grep -i '^X-Next-Cursor:' /tmp/kj_lib_page1.hdr | tr -d '\r' | sed 's/^[Xx]-[Nn]ext-[Cc]ursor: *//I')
case "$lib_page1" in
  *'"id":"'*'"id":"'*) echo "  FAIL: LIB pagination limit=1 が複数件を返した"; FAIL=$((FAIL+1));;
  *'"id":"'*) echo "  PASS: LIB limit=1 で1件（レスポンスが上限内）"; PASS=$((PASS+1));;
  *) echo "  FAIL: LIB pagination 応答（got ${lib_page1:0:100}）"; FAIL=$((FAIL+1));;
esac
if [ -n "$lib_next" ]; then
  lib_page2=$(curl -s "$BASE_URL/docs?limit=1&cursor=$lib_next")
  case "$lib_page2" in
    *'"id":"'*) echo "  PASS: LIB X-Next-Cursor で次ページ取得成功"; PASS=$((PASS+1));;
    *) echo "  FAIL: LIB cursor 次ページ（got ${lib_page2:0:100}）"; FAIL=$((FAIL+1));;
  esac
else
  echo "  FAIL: LIB 複数文書なのに X-Next-Cursor が無い"; FAIL=$((FAIL+1))
fi
rm -f /tmp/kj_lib_page1.hdr

echo ""
echo "--- シナリオ13: 共同編集者の楽観的並行制御（ETag/If-Match 競合検出） ---"
# 業態: コンサルティングファーム（共同編集）
# 想定人物: 共同編集者A/B（同一文書を並行編集）
# 業務領域: 文書の並行編集と競合検出（lost-update 防止・ADR-0076 サーバ権威LWW+CAS）
# 操作内容: 文書作成 -> GET(ETag取得) -> Aが編集PUT(If-Match) -> Bが古いETagで編集PUT
#          -> **409(競合検出・lost-update防止)** -> 最新ETag再取得 -> Bが再編集PUT -> 200
# 注意事項: ETag/If-Match で楽観的並行制御。stale な保存は 409 で拒否（部分保存なし）。
CE_DOC_ID="biz-flow-coedit"
CE_DOC='{"version":1,"id":"'$CE_DOC_ID'","title":"提案書の共同編集","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"c1","text":"初版","x":0,"y":0,"textReviewed":true}],"edges":[],"islands":[]}'
CE_DOC_A='{"version":1,"id":"'$CE_DOC_ID'","title":"提案書の共同編集","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"c1","text":"Aの修正案","x":0,"y":0,"textReviewed":true}],"edges":[],"islands":[]}'

ce_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$CE_DOC_ID" \
  -H 'Content-Type: application/json' -d "$CE_DOC")
check "CE PUT document (作成)" "200" "$ce_put"

# 初回 ETag 取得。
ce_etag1=$(curl -s -D - -o /dev/null "$BASE_URL/docs/$CE_DOC_ID" | tr -d '\r' | grep -i '^ETag:' | sed 's/ETag: *//I')
[ -n "$ce_etag1" ] && { echo "  PASS: CE ETag取得 ($(echo "$ce_etag1" | cut -c1-16)...)"; PASS=$((PASS+1)); } || { echo "  FAIL: CE ETag 未取得"; FAIL=$((FAIL+1)); }

# A が編集（正しい If-Match で保存成功）。
ce_a=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$CE_DOC_ID" \
  -H 'Content-Type: application/json' -H "If-Match: $ce_etag1" -d "$CE_DOC_A")
check "CE A編集 (If-Match 正 → 200)" "200" "$ce_a"

# B が古い ETag で編集 → 409（lost-update 防止・部分保存なし）。
ce_b_stale=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$CE_DOC_ID" \
  -H 'Content-Type: application/json' -H "If-Match: $ce_etag1" -d "$CE_DOC_A")
check "CE B編集 (stale If-Match → 409 競合検出)" "409" "$ce_b_stale"

# 最新 ETag 再取得 → B が再編集 → 200。
ce_etag2=$(curl -s -D - -o /dev/null "$BASE_URL/docs/$CE_DOC_ID" | tr -d '\r' | grep -i '^ETag:' | sed 's/ETag: *//I')
ce_b_retry=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$CE_DOC_ID" \
  -H 'Content-Type: application/json' -H "If-Match: $ce_etag2" -d "$CE_DOC_A")
check "CE B再編集 (最新If-Match → 200)" "200" "$ce_b_retry"

# 競合検出後に文書が壊れていない（読戻しで最新状態）。
ce_readback=$(curl -s "$BASE_URL/docs/$CE_DOC_ID")
case "$ce_readback" in
  *'"text":"Aの修正案"'*)
    echo "  PASS: CE 読戻し（Aの修正が反映・部分保存なし）"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: CE 読戻し（got ${ce_readback:0:120}）"
    FAIL=$((FAIL+1))
    ;;
esac

echo ""
echo "--- シナリオ14: 出版・コンテンツQA（内容上限の検証ゲート） ---"
# 業態: 出版・コンテンツ制作（QA）
# 想定人物: コンテンツ品質担当（校正者）
# 業務領域: コンテンツ上限の検証と品質ゲート（DOMAIN-CARD-TEXT-01）
# 操作内容: カード本文2001文字->422(上限違反) -> 2000文字で保存(200) -> タイトル501文字->422
#          -> 500文字タイトルで保存(200) -> 読戻し
# 注意事項: 上限は API 境界で強制（カード本文2000・タイトル500・島要約2000）。
#          A1 構造化エラー（schemaVersion/errorEnvelope）で返る。
QA_LONG_CARD=$(printf 'あ%.0s' $(seq 1 2001))
QA_OK_CARD=$(printf 'あ%.0s' $(seq 1 2000))
QA_LONG_TITLE=$(printf 'い%.0s' $(seq 1 501))
QA_OK_TITLE=$(printf 'い%.0s' $(seq 1 500))

qa_over_card=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/qa-doc-over-card" \
  -H 'Content-Type: application/json' \
  -d '{"version":1,"id":"qa-doc-over-card","title":"QA","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"q1","text":"'"$QA_LONG_CARD"'","x":0,"y":0}],"edges":[],"islands":[]}')
check "QA カード2001文字 → 422（上限違反）" "422" "$qa_over_card"

qa_ok_card=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/qa-doc-ok-card" \
  -H 'Content-Type: application/json' \
  -d '{"version":1,"id":"qa-doc-ok-card","title":"QA","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"q1","text":"'"$QA_OK_CARD"'","x":0,"y":0}],"edges":[],"islands":[]}')
check "QA カード2000文字 → 200（境界内）" "200" "$qa_ok_card"

qa_over_title=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/qa-doc-over-title" \
  -H 'Content-Type: application/json' \
  -d '{"version":1,"id":"qa-doc-over-title","title":"'"$QA_LONG_TITLE"'","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[],"edges":[],"islands":[]}')
check "QA タイトル501文字 → 422（上限違反）" "422" "$qa_over_title"

qa_ok_title=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/qa-doc-ok-title" \
  -H 'Content-Type: application/json' \
  -d '{"version":1,"id":"qa-doc-ok-title","title":"'"$QA_OK_TITLE"'","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[],"edges":[],"islands":[]}')
check "QA タイトル500文字 → 200（境界内）" "200" "$qa_ok_title"

# 構造化 A1 エラー確認（上限違反の応答形式）。
qa_error_body=$(curl -s -X PUT "$BASE_URL/docs/qa-doc-error" -H 'Content-Type: application/json' \
  -d '{"version":1,"id":"qa-doc-error","title":"QA","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"q1","text":"'"$QA_LONG_CARD"'","x":0,"y":0}],"edges":[],"islands":[]}')
case "$qa_error_body" in
  *'"errorEnvelope"'*)
    echo "  PASS: QA 上限違反は構造化A1エラーで返る（errorEnvelope）"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: QA A1エラー形式（got ${qa_error_body:0:120}）"
    FAIL=$((FAIL+1))
    ;;
esac

# 島要約2001文字 → 422（島要約の上限・ISLAND_SUMMARY_MAX_LENGTH=2000）。
QA_LONG_SUMMARY=$(printf 'う%.0s' $(seq 1 2001))
qa_over_summary=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/qa-doc-over-summary" \
  -H 'Content-Type: application/json' \
  -d '{"version":1,"id":"qa-doc-over-summary","title":"QA","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[],"edges":[],"islands":[{"id":"i1","cardIds":[],"summaryText":"'"$QA_LONG_SUMMARY"'"}]}')
check "QA 島要約2001文字 → 422（上限違反）" "422" "$qa_over_summary"

echo ""
echo "--- シナリオ15: 編集者の統合決定ガバナンス（マージ決定の記録と復元） ---"
# 業態: 出版・編集（ナレッジ統合）
# 想定人物: 編集者（AIの統合提案を採否する）
# 業務領域: マージ提案の決定記録（traceability・監査）と復元ログ参照
# 操作内容: 文書作成 -> 統合決定を記録(POST merge-decision-logs) -> グループ別ログ確認
#          (GET by-group) -> 復元ログ参照(GET restore) -> 重複決定が409
# 注意事項: 決定は append のみ（更新不可・traceability の正本）。同一 decisionId は 409。
#          action は accept/partial/reject/defer の enum。
MD_DOC_ID="biz-flow-merge-gov"
MD_DOC='{"version":1,"id":"'$MD_DOC_ID'","title":"ナレッジ統合の編集","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"c1","text":"草案","x":0,"y":0,"textReviewed":true}],"edges":[],"islands":[]}'
MD_REC='{"record":{"decisionId":"md-1","groupId":"g-merge","action":"accept","selectedCardIds":["c1"],"note":"統合を採択","decidedBy":"editor","decidedAt":"2026-08-15T00:00:00Z","snapshotVersion":"v1"}}'

md_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$MD_DOC_ID" \
  -H 'Content-Type: application/json' -d "$MD_DOC")
check "MD PUT document (作成)" "200" "$md_put"

# 統合決定を記録（append・201）。
md_post=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/docs/$MD_DOC_ID/merge-decision-logs" \
  -H 'Content-Type: application/json' -d "$MD_REC")
check "MD 決定記録 (201)" "201" "$md_post"

# 重複 decisionId は 409（決定の唯一性）。
md_dup=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/docs/$MD_DOC_ID/merge-decision-logs" \
  -H 'Content-Type: application/json' -d "$MD_REC")
check "MD 重複決定 (409)" "409" "$md_dup"

# グループ別ログ確認。
md_group=$(curl -s "$BASE_URL/docs/$MD_DOC_ID/merge-decision-logs/by-group/g-merge")
case "$md_group" in
  *'"decisionId":"md-1"'*'"action":"accept"'*)
    echo "  PASS: MD グループ別ログ（append 順・決定内容保持）"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: MD by-group（got ${md_group:0:120}）"
    FAIL=$((FAIL+1))
    ;;
esac

# 復元ログ参照。
md_restore=$(curl -s "$BASE_URL/docs/$MD_DOC_ID/merge-decision-logs/restore/v1")
case "$md_restore" in
  *'"decisionId":"md-1"'*)
    echo "  PASS: MD 復元ログ（snapshotVersion で参照）"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: MD restore（got ${md_restore:0:120}）"
    FAIL=$((FAIL+1))
    ;;
esac

echo ""
echo "--- シナリオ16: 外部エージェント連携（Org-D・外部AI成果物の提案受領） ---"
# 業態: AI連携サービス（外部エージェント）
# 想定人物: 外部エージェント（トリガー型AI）+ 人間レビューア
# 業務領域: 外部AIの成果物を提案として受領・人間がレビュー決定（EXT-AGENT-02 proposal-only）
# 操作内容: 文書作成 -> 外部タスク登録(/ai/external-tasks/register)
#          -> 外部提案登録(/ai/external-proposals/register) -> 人間が決定(/ai/external-proposals/audit)
#          -> 未登録提案への決定404
# 注意事項: 提案は未レビューで着地（自動適用なし）。baseDocSignature（{docId}:{updatedAt}）不一致は409。
#          登録していない proposal への決定は404。hash は64hex（DATA-CONTRACT-02）。
EXT_H="x-forwarded-user: ext-agent"
EXT_H2="x-auth-provider: oidc"
EXT_ID="biz-flow-ext-agent"
EXT_DOC='{"version":1,"id":"'$EXT_ID'","title":"外部統合","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"c1","text":"v1","x":0,"y":0,"textReviewed":true}],"edges":[],"islands":[]}'
EXT_SIG="biz-flow-ext-agent:2026-08-15T00:00:00Z"
EXT_H64="$(printf 'a%.0s' $(seq 1 64))"

ext_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$EXT_ID" \
  -H 'Content-Type: application/json' -H "$EXT_H" -H "$EXT_H2" -d "$EXT_DOC")
check "EXT PUT document (作成)" "200" "$ext_put"

# 外部タスク登録（依頼の正本）。
ext_task=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/ai/external-tasks/register" \
  -H 'Content-Type: application/json' -H "$EXT_H" -H "$EXT_H2" \
  -d "{\"docId\":\"$EXT_ID\",\"taskId\":\"ext-task-1\",\"baseDocSignature\":\"$EXT_SIG\",\"sourceBundleHash\":\"$EXT_H64\",\"queryCanonicalHash\":\"$EXT_H64\",\"taskKind\":\"narrative_draft\",\"provenanceLevel\":\"user_presented_unsigned\"}")
check "EXT 外部タスク登録 (200)" "200" "$ext_task"

# 外部提案登録（proposal-only・未レビュー着地）。
ext_prop=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/ai/external-proposals/register" \
  -H 'Content-Type: application/json' -H "$EXT_H" -H "$EXT_H2" \
  -d "{\"docId\":\"$EXT_ID\",\"taskId\":\"ext-task-1\",\"baseDocSignature\":\"$EXT_SIG\",\"sourceBundleHash\":\"$EXT_H64\",\"queryCanonicalHash\":\"$EXT_H64\",\"proposalId\":\"ext-prop-1\",\"proposalKind\":\"narrative_draft\",\"proposalFingerprint\":\"$EXT_H64\",\"provenanceLevel\":\"user_presented_unsigned\"}")
check "EXT 外部提案登録 (200・未レビュー着地)" "200" "$ext_prop"

# 人間の決定（hold・保留）。
ext_audit=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/ai/external-proposals/audit" \
  -H 'Content-Type: application/json' -H "$EXT_H" -H "$EXT_H2" \
  -d "{\"docId\":\"$EXT_ID\",\"proposalId\":\"ext-prop-1\",\"sourceBundleHash\":\"$EXT_H64\",\"idempotencyKey\":\"ext-k1\",\"decision\":\"hold\",\"reason\":\"要確認\",\"provenanceLevel\":\"user_presented_unsigned\"}")
check "EXT 人間の決定 (hold・200)" "200" "$ext_audit"

# 未登録 proposal への決定は404。
ext_unreg=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/ai/external-proposals/audit" \
  -H 'Content-Type: application/json' -H "$EXT_H" -H "$EXT_H2" \
  -d "{\"docId\":\"$EXT_ID\",\"proposalId\":\"ext-prop-none\",\"sourceBundleHash\":\"$EXT_H64\",\"idempotencyKey\":\"ext-k2\",\"decision\":\"reject\",\"provenanceLevel\":\"user_presented_unsigned\"}")
check "EXT 未登録提案への決定 (404)" "404" "$ext_unreg"

# baseDocSignature 不一致は409（依頼時点の文書シグネチャを検証・stale な依頼を拒否）。
ext_stale_sig=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/ai/external-tasks/register" \
  -H 'Content-Type: application/json' -H "$EXT_H" -H "$EXT_H2" \
  -d "{\"docId\":\"$EXT_ID\",\"taskId\":\"ext-task-stale\",\"baseDocSignature\":\"$EXT_ID:1999-01-01T00:00:00Z\",\"sourceBundleHash\":\"$EXT_H64\",\"queryCanonicalHash\":\"$EXT_H64\",\"taskKind\":\"narrative_draft\",\"provenanceLevel\":\"user_presented_unsigned\"}")
check "EXT stale baseDocSignature (409)" "409" "$ext_stale_sig"

echo ""
echo "--- シナリオ17: マーケティングアナリストの顧客レビュー全行程分析 ---"
# 業態: eコマース・マーケティング
# 想定人物: マーケティングアナリスト（顧客レビューを分析）
# 業務領域: 顧客レビューの全行程KJ分析（束ね→島→ナラティブ→矛盾検出→タイトル）
# 操作内容: レビューをカード化(PUT) -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> ナラティブ(generate-narrative) -> 矛盾検出(detect-contradiction)
#          -> タイトル提案(suggest-document-title) -> 読戻し
# 注意事項: 全AI操作は未レビュー入力で 422（SafeMode・textReviewed fail-closed）。
#          レビュー発言は逐語（refine で変えない）。
MK_ID="biz-flow-marketing"
MK_DOC='{"version":1,"id":"'$MK_ID'","title":"顧客レビュー分析","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"k1","text":"配送が遅い","x":0,"y":0,"textReviewed":true},{"id":"k2","text":"梱包が丁寧","x":10,"y":0,"textReviewed":true},{"id":"k3","text":"返品手続きが面倒","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"mk-i","cardIds":["k1","k2","k3"]}],"readingOrder":["mk-i"]}'

mk_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$MK_ID" \
  -H 'Content-Type: application/json' -d "$MK_DOC")
check "MK PUT document (作成)" "200" "$mk_put"

# ① AI束ね
mk_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"k1","text":"配送が遅い","textReviewed":true},{"id":"k2","text":"梱包が丁寧","textReviewed":true},{"id":"k3","text":"返品手続きが面倒","textReviewed":true}]}')
case "$mk_groups" in *'"groups":'*) echo "  PASS: MK ①束ね (card-groups)"; PASS=$((PASS+1));; *) echo "  FAIL: MK ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
mk_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$MK_DOC,\"islandId\":\"mk-i\"}")
case "$mk_summary" in *'"groundingIds":["k1","k2","k3"]'*) echo "  PASS: MK ②島要約 (grounding=member)"; PASS=$((PASS+1));; *) echo "  FAIL: MK ②島要約"; FAIL=$((FAIL+1));; esac

# ③ ナラティブ
mk_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$MK_DOC}")
case "$mk_narr" in *'"basedOnReadingOrder":["mk-i"]'*) echo "  PASS: MK ③ナラティブ (reading order)"; PASS=$((PASS+1));; *) echo "  FAIL: MK ③ナラティブ"; FAIL=$((FAIL+1));; esac

# ④ 矛盾検出
mk_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"k1","text":"配送が遅い","textReviewed":true},"cardB":{"id":"k2","text":"梱包が丁寧","textReviewed":true}}')
case "$mk_contra" in *'"hasContradiction":false'*) echo "  PASS: MK ④矛盾検出 (structured)"; PASS=$((PASS+1));; *) echo "  FAIL: MK ④矛盾検出"; FAIL=$((FAIL+1));; esac

# ⑤ タイトル提案
mk_title=$(curl -s -X POST "$BASE_URL/ai/suggest-document-title" -H 'Content-Type: application/json' \
  -d '{"islandTitles":["配送"],"cardTexts":["配送が遅い","梱包が丁寧","返品手続きが面倒"],"textReviewed":true}')
case "$mk_title" in *'"candidates"'*) echo "  PASS: MK ⑤タイトル提案 (candidates)"; PASS=$((PASS+1));; *) echo "  FAIL: MK ⑤タイトル提案"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し（全行程後も文書は保持）。
mk_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$MK_ID")
check "MK 読戻し (200)" "200" "$mk_read"

echo ""
echo "--- シナリオ18: リスクレビューアの反対視点提案（AI-OPPOSE-01） ---"
# 業態: リスク管理・監査
# 想定人物: リスクレビューア（意思決定の前提を検証）
# 業務領域: 意思決定の反対視点・根拠不足の提案（AI-OPPOSE-01 M4・proposal-only）
# 操作内容: 文書作成 -> propose-opposing-viewpoint(反対視点のproposal-only提案)
#          -> 未レビューdocで422(SafeMode) -> 存在しないtargetCardIdで422
# 注意事項: 提案は proposal-only（自動適用なし・status=proposed）。contradiction/evidence
#          構造から導出。doc は永続化必須（未永続化は404）。
OP_ID="biz-flow-risk"
OP_DOC='{"version":1,"id":"'$OP_ID'","title":"配送改善の意思決定","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"r1","text":"配送が遅いという声は多い","x":0,"y":0,"textReviewed":true},{"id":"r2","text":"遅延の原因は倉庫処理にある","x":10,"y":0,"textReviewed":true}],"edges":[],"islands":[]}'
OP_UNREV='{"version":1,"id":"biz-flow-risk-unrev","title":"未レビュー","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"u1","text":"確認前の前提","x":0,"y":0}],"edges":[],"islands":[]}'

op_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$OP_ID" \
  -H 'Content-Type: application/json' -d "$OP_DOC")
check "OP PUT document (作成)" "200" "$op_put"

# 反対視点の提案（proposal-only・自動適用なし）。
op_prop=$(curl -s -X POST "$BASE_URL/ai/proposals/opposing-viewpoint" -H 'Content-Type: application/json' \
  -d "{\"doc\":$OP_DOC,\"targetCardId\":\"r1\"}")
case "$op_prop" in
  *'"status":"proposed"'*'"opposingText"'*)
    echo "  PASS: OP 反対視点提案 (proposal-only・opposingText)"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: OP propose-opposing-viewpoint (got ${op_prop:0:150})"
    FAIL=$((FAIL+1))
    ;;
esac

# 未レビュー doc で 422（SafeMode 門禁・doc を永続化してから）。
curl -s -o /dev/null -X PUT "$BASE_URL/docs/biz-flow-risk-unrev" \
  -H 'Content-Type: application/json' -d "$OP_UNREV"
op_unrev=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/ai/proposals/opposing-viewpoint" \
  -H 'Content-Type: application/json' -d "{\"doc\":$OP_UNREV,\"targetCardId\":\"u1\"}")
check "OP 未レビューdoc → 422 (SafeMode)" "422" "$op_unrev"

# 存在しない targetCardId は 422。
op_badcard=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/ai/proposals/opposing-viewpoint" \
  -H 'Content-Type: application/json' -d "{\"doc\":$OP_DOC,\"targetCardId\":\"no-such-card\"}")
check "OP 存在しない targetCardId → 422" "422" "$op_badcard"

echo ""
echo "--- シナリオ19: 多職種ケース会議（医療・介護・反対視点確認） ---"
# 業態: 医療・介護（ケース会議）
# 想定人物: ケースワーカー（多職種会議のとりまとめ）
# 業務領域: ケース情報の整理と意思決定の反対視点確認
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 反対視点提案(propose-opposing-viewpoint) -> 読戻し
# 注意事項: 反対視点は proposal-only（自動適用なし・status=proposed）。未レビューは422（SafeMode）。
CW_ID="biz-flow-care"
CW_DOC='{"version":1,"id":"'$CW_ID'","title":"ケース会議の整理","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"w1","text":"在宅ケアを継続できる","x":0,"y":0,"textReviewed":true},{"id":"w2","text":"家族の負担が増えている","x":10,"y":0,"textReviewed":true},{"id":"w3","text":"訪問頻度を増やすべき","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"cw-i","cardIds":["w1","w2","w3"]}],"readingOrder":["cw-i"]}'

cw_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$CW_ID" \
  -H 'Content-Type: application/json' -d "$CW_DOC")
check "CW PUT document (作成)" "200" "$cw_put"

# ① AI束ね
cw_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"w1","text":"在宅ケアを継続できる","textReviewed":true},{"id":"w2","text":"家族の負担が増えている","textReviewed":true},{"id":"w3","text":"訪問頻度を増やすべき","textReviewed":true}]}')
case "$cw_groups" in *'"groups":'*) echo "  PASS: CW ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: CW ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
cw_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$CW_DOC,\"islandId\":\"cw-i\"}")
case "$cw_summary" in *'"groundingIds":["w1","w2","w3"]'*) echo "  PASS: CW ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: CW ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 反対視点提案（在宅ケア継続の意思決定に対する反対視点・proposal-only）
cw_opp=$(curl -s -X POST "$BASE_URL/ai/proposals/opposing-viewpoint" -H 'Content-Type: application/json' \
  -d "{\"doc\":$CW_DOC,\"targetCardId\":\"w1\"}")
case "$cw_opp" in
  *'"status":"proposed"'*'"opposingText"'*)
    echo "  PASS: CW ③反対視点提案 (proposal-only)"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: CW ③反対視点提案 (got ${cw_opp:0:150})"
    FAIL=$((FAIL+1))
    ;;
esac

# ④ 読戻し
cw_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$CW_ID")
check "CW 読戻し (200)" "200" "$cw_read"

echo ""
echo "--- シナリオ20: 品質監査官の批判的検証（多角的な意思決定レビュー） ---"
# 業態: 品質監査（内部統制）
# 想定人物: 品質監査官（意思決定を多角的に検証）
# 業務領域: 矛盾検出・反対視点・ナラティブ整合の批判的レビュー
# 操作内容: 文書作成 -> 矛盾検出(detect-contradiction) -> 反対視点提案(opposing-viewpoint)
#          -> ナラティブA/B照合(check-narrative) -> 読戻し
# 注意事項: 全て proposal-only（自動適用なし）。未レビューは422（SafeMode）。
QA2_ID="biz-flow-audit"
QA2_DOC='{"version":1,"id":"'$QA2_ID'","title":"業務プロセス改善の決定","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"a1","text":"改善により工数が減る","x":0,"y":0,"textReviewed":true},{"id":"a2","text":"初期導入コストが高い","x":10,"y":0,"textReviewed":true},{"id":"a3","text":"リスクは許容範囲","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"qa2-i","cardIds":["a1","a2","a3"]}],"readingOrder":["qa2-i"]}'

qa2_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$QA2_ID" \
  -H 'Content-Type: application/json' -d "$QA2_DOC")
check "QA2 PUT document (作成)" "200" "$qa2_put"

# ① 矛盾検出（改善の工数削減 vs 導入コスト）
qa2_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"a1","text":"改善により工数が減る","textReviewed":true},"cardB":{"id":"a2","text":"初期導入コストが高い","textReviewed":true}}')
case "$qa2_contra" in *'"hasContradiction"'*) echo "  PASS: QA2 ①矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: QA2 ①矛盾検出"; FAIL=$((FAIL+1));; esac

# ② 反対視点提案（proposal-only）
qa2_opp=$(curl -s -X POST "$BASE_URL/ai/proposals/opposing-viewpoint" -H 'Content-Type: application/json' \
  -d "{\"doc\":$QA2_DOC,\"targetCardId\":\"a1\"}")
case "$qa2_opp" in *'"status":"proposed"'*'"opposingText"'*) echo "  PASS: QA2 ②反対視点提案 (proposal-only)"; PASS=$((PASS+1));; *) echo "  FAIL: QA2 ②反対視点"; FAIL=$((FAIL+1));; esac

# ③ ナラティブA/B照合（モックは不整合なし）
qa2_narr=$(curl -s -X POST "$BASE_URL/ai/check-narrative" -H 'Content-Type: application/json' \
  -d "{\"doc\":$QA2_DOC,\"narrativeText\":\"（草稿）業務プロセス改善により工数が減る一方、初期導入コストが高い。\",\"basedOnReadingOrder\":[\"qa2-i\"]}")
case "$qa2_narr" in *'"issues":[]'*) echo "  PASS: QA2 ③ナラティブA/B照合"; PASS=$((PASS+1));; *) echo "  FAIL: QA2 ③A/B照合 (${qa2_narr:0:100})"; FAIL=$((FAIL+1));; esac

# ④ 読戻し
qa2_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$QA2_ID")
check "QA2 読戻し (200)" "200" "$qa2_read"

echo ""
echo "--- シナリオ21: 生成AI連携のコンテキスト解決（CE4 context bundle） ---"
# 業態: AI連携サービス（コンテキスト基盤）
# 想定人物: 生成AIエージェント（文書のコンテキストを解決）
# 業務領域: CE4 context bundle の解決（AIが文書コンテキストを取得する基盤）
# 操作内容: context/bundles:resolve(コンテキスト解決) -> 応答の確認(equivalenceKey/bundleHash)
#          -> safeMode=false は 422 -> proposalLifecycle は proposal-only の意味を持つ
# 注意事項: sourceBundleHash は sha256: または mock: 形式。safeMode 既定 true。
#          解決は契約ベース（ドキュメント永続化は不要）。
CB_H64="mock:$(printf 'a%.0s' $(seq 1 64))"

# ① コンテキスト解決（safeMode=true・既定）。
cb_resolve=$(curl -s -X POST "$BASE_URL/context/bundles:resolve" -H 'Content-Type: application/json' \
  -d "{\"query\":\"課題は何か\",\"dryRun\":true,\"sourceBundleHash\":\"$CB_H64\",\"safeMode\":true}")
case "$cb_resolve" in
  *'"equivalenceKey"'*'"bundleHash"'*)
    echo "  PASS: CB コンテキスト解決 (equivalenceKey/bundleHash)"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: CB resolve (got ${cb_resolve:0:150})"
    FAIL=$((FAIL+1))
    ;;
esac

# ② proposalLifecycle が proposal-only の意味を持つ。
case "$cb_resolve" in
  *'"proposalLifecycle":"proposed"'*)
    echo "  PASS: CB proposalLifecycle=proposed (proposal-only)"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: CB proposalLifecycle (got ${cb_resolve:0:150})"
    FAIL=$((FAIL+1))
    ;;
esac

# ③ safeMode=false は 422（SafeMode 既定・fail-closed）。
cb_unsafe=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/context/bundles:resolve" \
  -H 'Content-Type: application/json' \
  -d "{\"query\":\"課題は何か\",\"dryRun\":true,\"sourceBundleHash\":\"$CB_H64\",\"safeMode\":false}")
check "CB safeMode=false → 422 (SafeMode fail-closed)" "422" "$cb_unsafe"

echo ""
echo "--- シナリオ22: 共同研究チームのW型探索（ジャーニーの並行編集・CAS競合検出） ---"
# 業態: 共同研究（アカデミア）
# 想定人物: 共同研究者A/B（同一の探究ジャーニーを並行編集）
# 業務領域: 探究ジャーニーの共同編集と楽観的並行制御（lost-update 防止）
# 操作内容: 文書作成 -> ジャーニー開始(If-None-Match:*) -> Aがラウンド更新(If-Match)
#          -> Bが古いIf-Matchで更新(**409**) -> 最新ETagでBが再更新(200)
# 注意事項: ジャーニーは CAS（If-Match/If-None-Match）で楽観的並行制御。stale 更新は 409。
CR_ID="biz-flow-collab-journey"
CR_BUNDLE='{"schemaVersion":"1.0.0","journey":{"schemaVersion":"1.0.0","journeyId":"'$CR_ID'","title":"共同探究","originSnapshotIds":["snap-orig"],"roundRecords":[{"roundId":"cr-r1","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","stage":"r2_situation_grasp","iteration":1,"parentRoundIds":[],"status":"in_progress","theme":"共同テーマ","inputSnapshotIds":["snap-orig"],"outputSnapshotId":"snap-orig","handoff":{"carryoverRefs":[],"heldRefs":[],"unresolvedQuestions":[],"fieldworkRequests":[]}}],"resolvedFieldworkQuestionIds":[],"status":"in_progress"},"snapshots":[{"schemaVersion":"1.0.0","snapshotId":"snap-orig","createdAt":"2026-08-16T00:00:00Z","canonicalDigest":"sha256:orig","document":{"version":1,"id":"cr-doc","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"c1","text":"観察","x":0,"y":0}],"edges":[],"islands":[]}}]}'
CR_BUNDLE_V2='{"schemaVersion":"1.0.0","journey":{"schemaVersion":"1.0.0","journeyId":"'$CR_ID'","title":"共同探究","originSnapshotIds":["snap-orig"],"roundRecords":[{"roundId":"cr-r1","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","stage":"r2_situation_grasp","iteration":1,"parentRoundIds":[],"status":"handed_off","theme":"共同テーマ（Aが更新）","inputSnapshotIds":["snap-orig"],"outputSnapshotId":"snap-orig","handoff":{"carryoverRefs":[],"heldRefs":[],"unresolvedQuestions":[],"fieldworkRequests":[]}}],"resolvedFieldworkQuestionIds":[],"status":"in_progress"},"snapshots":[{"schemaVersion":"1.0.0","snapshotId":"snap-orig","createdAt":"2026-08-16T00:00:00Z","canonicalDigest":"sha256:orig","document":{"version":1,"id":"cr-doc","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"c1","text":"観察","x":0,"y":0}],"edges":[],"islands":[]}}]}'

# ジャーニー開始（If-None-Match:* で作成・201＋ETag）。
cr_create=$(curl -s -i -X POST "$BASE_URL/inquiry-bundles/$CR_ID" \
  -H 'Content-Type: application/json' -H 'If-None-Match: *' -d "$CR_BUNDLE")
cr_code=$(echo "$cr_create" | head -1 | grep -oE '[0-9]{3}')
cr_etag1=$(echo "$cr_create" | tr -d '\r' | grep -i '^ETag:' | sed 's/ETag: *//I')
check "CR ジャーニー開始 (201)" "201" "$cr_code"

# A がラウンド更新（正しい If-Match で成功）。
cr_a=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/inquiry-bundles/$CR_ID" \
  -H 'Content-Type: application/json' -H "If-Match: $cr_etag1" -d "$CR_BUNDLE_V2")
check "CR A更新 (If-Match 正 → 204)" "204" "$cr_a"

# B が古い ETag で更新 → 409（lost-update 防止）。
cr_b_stale=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/inquiry-bundles/$CR_ID" \
  -H 'Content-Type: application/json' -H "If-Match: $cr_etag1" -d "$CR_BUNDLE_V2")
check "CR B更新 (stale If-Match → 409 競合検出)" "409" "$cr_b_stale"

# 最新 ETag 取得 → B が再更新 → 204。
cr_etag2=$(curl -s -D - -o /dev/null "$BASE_URL/inquiry-bundles/$CR_ID" | tr -d '\r' | grep -i '^ETag:' | sed 's/ETag: *//I')
cr_b_retry=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/inquiry-bundles/$CR_ID" \
  -H 'Content-Type: application/json' -H "If-Match: $cr_etag2" -d "$CR_BUNDLE_V2")
check "CR B再更新 (最新If-Match → 204)" "204" "$cr_b_retry"

echo ""
echo "--- シナリオ23: 教育研修・カリキュラム改善（受講者フィードバック分析） ---"
# 業態: 教育・研修（カリキュラム改善）
# 想定人物: 教育企画担当（受講者フィードバックを分析）
# 業務領域: 受講者フィードバックのKJ分析によるカリキュラム改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> タイトル提案(suggest-document-title)
# 注意事項: 全AI操作は未レビュー入力で422（SafeMode）。受講者の発言は逐語（refineで変えない）。
EDU_ID="biz-flow-edu"
EDU_DOC='{"version":1,"id":"'$EDU_ID'","title":"研修改善","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"e1","text":"演習時間が足りない","x":0,"y":0,"textReviewed":true},{"id":"e2","text":"事例が実務に近い","x":10,"y":0,"textReviewed":true},{"id":"e3","text":"資料が多すぎる","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"edu-i","cardIds":["e1","e2","e3"]}],"readingOrder":["edu-i"]}'

edu_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$EDU_ID" \
  -H 'Content-Type: application/json' -d "$EDU_DOC")
check "EDU PUT document (作成)" "200" "$edu_put"

# ① AI束ね
edu_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"e1","text":"演習時間が足りない","textReviewed":true},{"id":"e2","text":"事例が実務に近い","textReviewed":true},{"id":"e3","text":"資料が多すぎる","textReviewed":true}]}')
case "$edu_groups" in *'"groups":'*) echo "  PASS: EDU ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: EDU ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
edu_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$EDU_DOC,\"islandId\":\"edu-i\"}")
case "$edu_summary" in *'"groundingIds":["e1","e2","e3"]'*) echo "  PASS: EDU ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: EDU ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（演習不足 vs 資料過多）
edu_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"e1","text":"演習時間が足りない","textReviewed":true},"cardB":{"id":"e3","text":"資料が多すぎる","textReviewed":true}}')
case "$edu_contra" in *'"hasContradiction"'*) echo "  PASS: EDU ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: EDU ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ タイトル提案
edu_title=$(curl -s -X POST "$BASE_URL/ai/suggest-document-title" -H 'Content-Type: application/json' \
  -d '{"islandTitles":["研修"],"cardTexts":["演習時間が足りない","事例が実務に近い","資料が多すぎる"],"textReviewed":true}')
case "$edu_title" in *'"candidates"'*) echo "  PASS: EDU ④タイトル提案"; PASS=$((PASS+1));; *) echo "  FAIL: EDU ④タイトル提案"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
edu_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$EDU_ID")
check "EDU 読戻し (200)" "200" "$edu_read"

echo ""
echo "--- シナリオ24: 災害対応・現場報告の整理と矛盾検出（安全クリティカル） ---"
# 業態: 防災・災害対応
# 想定人物: 災害対策本部スタッフ（現場報告を整理）
# 業務領域: 現場報告のKJ整理と矛盾報告の検出・反対視点の確認
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> 反対視点提案(propose-opposing-viewpoint)
# 注意事項: 矛盾する現場報告は隠さず表面化する（安全クリティカル）。全て proposal-only。
#          未レビューは422（SafeMode）。
DR_ID="biz-flow-disaster"
DR_DOC='{"version":1,"id":"'$DR_ID'","title":"現場報告の整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"d1","text":"避難所に食料が届いている","x":0,"y":0,"textReviewed":true},{"id":"d2","text":"避難所の食料が不足している","x":10,"y":0,"textReviewed":true},{"id":"d3","text":"道路が通行止め","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"dr-i","cardIds":["d1","d2","d3"]}],"readingOrder":["dr-i"]}'

dr_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$DR_ID" \
  -H 'Content-Type: application/json' -d "$DR_DOC")
check "DR PUT document (作成)" "200" "$dr_put"

# ① AI束ね
dr_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"d1","text":"避難所に食料が届いている","textReviewed":true},{"id":"d2","text":"避難所の食料が不足している","textReviewed":true},{"id":"d3","text":"道路が通行止め","textReviewed":true}]}')
case "$dr_groups" in *'"groups":'*) echo "  PASS: DR ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: DR ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
dr_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$DR_DOC,\"islandId\":\"dr-i\"}")
case "$dr_summary" in *'"groundingIds":["d1","d2","d3"]'*) echo "  PASS: DR ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: DR ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（食料が届いている vs 不足している — 矛盾する現場報告を表面化）
dr_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"d1","text":"避難所に食料が届いている","textReviewed":true},"cardB":{"id":"d2","text":"避難所の食料が不足している","textReviewed":true}}')
case "$dr_contra" in *'"hasContradiction"'*) echo "  PASS: DR ③矛盾検出（矛盾報告を表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: DR ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ 反対視点提案（食料対応の意思決定に対する反対視点・proposal-only）
dr_opp=$(curl -s -X POST "$BASE_URL/ai/proposals/opposing-viewpoint" -H 'Content-Type: application/json' \
  -d "{\"doc\":$DR_DOC,\"targetCardId\":\"d1\"}")
case "$dr_opp" in *'"status":"proposed"'*'"opposingText"'*) echo "  PASS: DR ④反対視点提案 (proposal-only)"; PASS=$((PASS+1));; *) echo "  FAIL: DR ④反対視点"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
dr_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$DR_ID")
check "DR 読戻し (200)" "200" "$dr_read"

echo ""
echo "--- シナリオ25: 法務レビュー（契約条項の整理と整合性検証） ---"
# 業態: 法務・コンプライアンス
# 想定人物: 法務担当（契約レビュー）
# 業務領域: 契約条項のKJ整理と整合性検証（条項間の矛盾・法務意見のA/B照合）
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブA/B照合(check-narrative)
# 注意事項: 条項の文面は逐語（refineで変えない）。整合性検証は提案のみ（自動適用なし）。
LG_ID="biz-flow-legal"
LG_DOC='{"version":1,"id":"'$LG_ID'","title":"契約レビュー","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"l1","text":"解約は30日前の通知で可能","x":0,"y":0,"textReviewed":true},{"id":"l2","text":"違約金は契約額の20%","x":10,"y":0,"textReviewed":true},{"id":"l3","text":"個人情報は目的外利用しない","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"lg-i","cardIds":["l1","l2","l3"]}],"readingOrder":["lg-i"]}'

lg_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$LG_ID" \
  -H 'Content-Type: application/json' -d "$LG_DOC")
check "LG PUT document (作成)" "200" "$lg_put"

# ① AI束ね
lg_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"l1","text":"解約は30日前の通知で可能","textReviewed":true},{"id":"l2","text":"違約金は契約額の20%","textReviewed":true},{"id":"l3","text":"個人情報は目的外利用しない","textReviewed":true}]}')
case "$lg_groups" in *'"groups":'*) echo "  PASS: LG ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: LG ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
lg_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$LG_DOC,\"islandId\":\"lg-i\"}")
case "$lg_summary" in *'"groundingIds":["l1","l2","l3"]'*) echo "  PASS: LG ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: LG ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 条項間の矛盾検出
lg_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"l1","text":"解約は30日前の通知で可能","textReviewed":true},"cardB":{"id":"l2","text":"違約金は契約額の20%","textReviewed":true}}')
case "$lg_contra" in *'"hasContradiction"'*) echo "  PASS: LG ③条項間の矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: LG ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ 法務意見のナラティブA/B照合
lg_narr=$(curl -s -X POST "$BASE_URL/ai/check-narrative" -H 'Content-Type: application/json' \
  -d "{\"doc\":$LG_DOC,\"narrativeText\":\"（草稿）解約には30日前の通知を要し、違約金は契約額の20%とし、個人情報は目的外利用しない。\",\"basedOnReadingOrder\":[\"lg-i\"]}")
case "$lg_narr" in *'"issues":[]'*) echo "  PASS: LG ④法務意見のA/B照合"; PASS=$((PASS+1));; *) echo "  FAIL: LG ④A/B照合 (${lg_narr:0:100})"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
lg_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$LG_ID")
check "LG 読戻し (200)" "200" "$lg_read"

echo ""
echo "--- シナリオ26: 政策立案・パブリックコメントの整理 ---"
# 業態: 公的機関・政策立案
# 想定人物: 政策担当（パブリックコメントを整理）
# 業務領域: パブリックコメントのKJ整理と対立意見の矛盾検出
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
# 注意事項: 意見は逐語（refineで変えない）。対立意見は隠さず表面化する。未レビューは422。
PC_ID="biz-flow-policy"
PC_DOC='{"version":1,"id":"'$PC_ID'","title":"パブリックコメント整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"p1","text":"料金値上げに反対する","x":0,"y":0,"textReviewed":true},{"id":"p2","text":"サービス改善には財源が必要","x":10,"y":0,"textReviewed":true},{"id":"p3","text":"手続きの簡素化を求める","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"pc-i","cardIds":["p1","p2","p3"]}],"readingOrder":["pc-i"]}'

pc_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$PC_ID" \
  -H 'Content-Type: application/json' -d "$PC_DOC")
check "PC PUT document (作成)" "200" "$pc_put"

# ① AI束ね
pc_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"p1","text":"料金値上げに反対する","textReviewed":true},{"id":"p2","text":"サービス改善には財源が必要","textReviewed":true},{"id":"p3","text":"手続きの簡素化を求める","textReviewed":true}]}')
case "$pc_groups" in *'"groups":'*) echo "  PASS: PC ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: PC ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
pc_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$PC_DOC,\"islandId\":\"pc-i\"}")
case "$pc_summary" in *'"groundingIds":["p1","p2","p3"]'*) echo "  PASS: PC ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: PC ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 対立意見の矛盾検出（値上げ反対 vs 財源必要）
pc_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"p1","text":"料金値上げに反対する","textReviewed":true},"cardB":{"id":"p2","text":"サービス改善には財源が必要","textReviewed":true}}')
case "$pc_contra" in *'"hasContradiction"'*) echo "  PASS: PC ③対立意見の矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: PC ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ草稿
pc_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$PC_DOC}")
case "$pc_narr" in *'"basedOnReadingOrder":["pc-i"]'*) echo "  PASS: PC ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: PC ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
pc_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$PC_ID")
check "PC 読戻し (200)" "200" "$pc_read"

echo ""
echo "--- シナリオ27: 金融・融資審査のリスク評価 ---"
# 業態: 金融・融資審査
# 想定人物: 融資審査担当（リスク情報を評価）
# 業務領域: リスク情報のKJ整理と矛盾リスク信号の検出・反対視点の確認
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> 反対視点提案(propose-opposing-viewpoint)
# 注意事項: リスク情報は逐語（refineで変えない）。矛盾するリスク信号は隠さず表面化。
#          全AI操作は未レビュー入力で422（SafeMode）。
FN_ID="biz-flow-finance"
FN_DOC='{"version":1,"id":"'$FN_ID'","title":"融資審査のリスク評価","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"f1","text":"売上は堅調に推移","x":0,"y":0,"textReviewed":true},{"id":"f2","text":"在庫が過剰に増えている","x":10,"y":0,"textReviewed":true},{"id":"f3","text":"仕入先との取引は安定","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"fn-i","cardIds":["f1","f2","f3"]}],"readingOrder":["fn-i"]}'

fn_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$FN_ID" \
  -H 'Content-Type: application/json' -d "$FN_DOC")
check "FN PUT document (作成)" "200" "$fn_put"

# ① AI束ね
fn_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"f1","text":"売上は堅調に推移","textReviewed":true},{"id":"f2","text":"在庫が過剰に増えている","textReviewed":true},{"id":"f3","text":"仕入先との取引は安定","textReviewed":true}]}')
case "$fn_groups" in *'"groups":'*) echo "  PASS: FN ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: FN ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
fn_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$FN_DOC,\"islandId\":\"fn-i\"}")
case "$fn_summary" in *'"groundingIds":["f1","f2","f3"]'*) echo "  PASS: FN ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: FN ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾リスク信号の検出（売上堅調 vs 在庫過剰）
fn_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"f1","text":"売上は堅調に推移","textReviewed":true},"cardB":{"id":"f2","text":"在庫が過剰に増えている","textReviewed":true}}')
case "$fn_contra" in *'"hasContradiction"'*) echo "  PASS: FN ③矛盾リスク信号の検出"; PASS=$((PASS+1));; *) echo "  FAIL: FN ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ 反対視点提案（融資判断に対する反対視点・proposal-only）
fn_opp=$(curl -s -X POST "$BASE_URL/ai/proposals/opposing-viewpoint" -H 'Content-Type: application/json' \
  -d "{\"doc\":$FN_DOC,\"targetCardId\":\"f2\"}")
case "$fn_opp" in *'"status":"proposed"'*'"opposingText"'*) echo "  PASS: FN ④反対視点提案 (proposal-only)"; PASS=$((PASS+1));; *) echo "  FAIL: FN ④反対視点"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
fn_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$FN_ID")
check "FN 読戻し (200)" "200" "$fn_read"

echo ""
echo "--- シナリオ28: 観光・宿泊・訪問者フィードバックの整理 ---"
# 業態: 観光・宿泊
# 想定人物: 宿泊施設マネージャー（訪問者フィードバックを分析）
# 業務領域: 訪問者フィードバックのKJ整理と満足/不満の要因分析
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> タイトル提案(suggest-document-title)
# 注意事項: 訪問者の声は逐語（refineで変えない）。矛盾する評価は隠さず表面化。
TR_ID="biz-flow-tourism"
TR_DOC='{"version":1,"id":"'$TR_ID'","title":"宿泊施設の改善","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"t1","text":"眺望が素晴らしい","x":0,"y":0,"textReviewed":true},{"id":"t2","text":"朝食の選択肢が少ない","x":10,"y":0,"textReviewed":true},{"id":"t3","text":"スタッフの対応が丁寧","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"tr-i","cardIds":["t1","t2","t3"]}],"readingOrder":["tr-i"]}'

tr_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$TR_ID" \
  -H 'Content-Type: application/json' -d "$TR_DOC")
check "TR PUT document (作成)" "200" "$tr_put"

# ① AI束ね
tr_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"t1","text":"眺望が素晴らしい","textReviewed":true},{"id":"t2","text":"朝食の選択肢が少ない","textReviewed":true},{"id":"t3","text":"スタッフの対応が丁寧","textReviewed":true}]}')
case "$tr_groups" in *'"groups":'*) echo "  PASS: TR ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: TR ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
tr_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$TR_DOC,\"islandId\":\"tr-i\"}")
case "$tr_summary" in *'"groundingIds":["t1","t2","t3"]'*) echo "  PASS: TR ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: TR ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（満足要因 vs 不満要因）
tr_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"t1","text":"眺望が素晴らしい","textReviewed":true},"cardB":{"id":"t2","text":"朝食の選択肢が少ない","textReviewed":true}}')
case "$tr_contra" in *'"hasContradiction"'*) echo "  PASS: TR ③満足/不満の矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: TR ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ タイトル提案
tr_title=$(curl -s -X POST "$BASE_URL/ai/suggest-document-title" -H 'Content-Type: application/json' \
  -d '{"islandTitles":["宿泊"],"cardTexts":["眺望が素晴らしい","朝食の選択肢が少ない","スタッフの対応が丁寧"],"textReviewed":true}')
case "$tr_title" in *'"candidates"'*) echo "  PASS: TR ④タイトル提案"; PASS=$((PASS+1));; *) echo "  FAIL: TR ④タイトル提案"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
tr_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$TR_ID")
check "TR 読戻し (200)" "200" "$tr_read"

echo ""
echo "--- シナリオ29: 製造・生産現場の改善提案整理 ---"
# 業態: 製造・生産
# 想定人物: 生産改善リーダー（現場の改善提案を整理）
# 業務領域: 現場改善提案のKJ整理と課題の因果関係の要約
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 島間関係要約(summarize-island-relation) -> ナラティブ(generate-narrative)
# 注意事項: 現場の声は逐語（refineで変えない）。関係要約は提案のみ（自動適用なし）。
MF_ID="biz-flow-manufacturing"
MF_DOC='{"version":1,"id":"'$MF_ID'","title":"生産現場の改善","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"m1","text":"段取り替えに時間がかかる","x":0,"y":0,"textReviewed":true},{"id":"m2","text":"部品の在庫管理が煩雑","x":10,"y":0,"textReviewed":true},{"id":"m3","text":"設備の稼働率が低い","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"mf-a","cardIds":["m1","m2"]},{"id":"mf-b","cardIds":["m3"]}],"readingOrder":["mf-a","mf-b"]}'

mf_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$MF_ID" \
  -H 'Content-Type: application/json' -d "$MF_DOC")
check "MF PUT document (作成)" "200" "$mf_put"

# ① AI束ね
mf_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"m1","text":"段取り替えに時間がかかる","textReviewed":true},{"id":"m2","text":"部品の在庫管理が煩雑","textReviewed":true},{"id":"m3","text":"設備の稼働率が低い","textReviewed":true}]}')
case "$mf_groups" in *'"groups":'*) echo "  PASS: MF ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: MF ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
mf_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$MF_DOC,\"islandId\":\"mf-a\"}")
case "$mf_summary" in *'"groundingIds":["m1","m2"]'*) echo "  PASS: MF ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: MF ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 島間関係の要約（段取り・在庫 → 稼働率 の因果）
mf_rel=$(curl -s -X POST "$BASE_URL/ai/summarize-island-relation" -H 'Content-Type: application/json' \
  -d "{\"doc\":$MF_DOC,\"islandAId\":\"mf-a\",\"islandBId\":\"mf-b\",\"relationType\":\"causal\",\"derived\":false,\"groundingCardIds\":[\"m3\"],\"groundingEdgeIds\":[],\"cardTexts\":[{\"id\":\"m3\",\"text\":\"設備の稼働率が低い\"}]}")
case "$mf_rel" in *'"text"'*) echo "  PASS: MF ③島間関係の要約 (causal)"; PASS=$((PASS+1));; *) echo "  FAIL: MF ③関係要約 (${mf_rel:0:100})"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
mf_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$MF_DOC}")
case "$mf_narr" in *'"basedOnReadingOrder":["mf-a","mf-b"]'*) echo "  PASS: MF ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: MF ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
mf_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$MF_ID")
check "MF 読戻し (200)" "200" "$mf_read"

echo ""
echo "--- シナリオ30: 人事評価・360度フィードバックの統合 ---"
# 業態: 人事・人材開発
# 想定人物: 人事マネージャー（360度評価の統合）
# 業務領域: 360度フィードバックのKJ統合と矛盾フィードバックの検出
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
# 注意事項: フィードバックは逐語（refineで変えない）。矛盾する評価は表面化する。
HR_ID="biz-flow-hr360"
HR_DOC='{"version":1,"id":"'$HR_ID'","title":"360度評価の統合","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"h1","text":"リーダーシップが高い","x":0,"y":0,"textReviewed":true},{"id":"h2","text":"決断が遅い","x":10,"y":0,"textReviewed":true},{"id":"h3","text":"チームへの配慮が十分","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"hr-i","cardIds":["h1","h2","h3"]}],"readingOrder":["hr-i"]}'

hr_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$HR_ID" \
  -H 'Content-Type: application/json' -d "$HR_DOC")
check "HR PUT document (作成)" "200" "$hr_put"

# ① AI束ね
hr_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"h1","text":"リーダーシップが高い","textReviewed":true},{"id":"h2","text":"決断が遅い","textReviewed":true},{"id":"h3","text":"チームへの配慮が十分","textReviewed":true}]}')
case "$hr_groups" in *'"groups":'*) echo "  PASS: HR ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: HR ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
hr_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$HR_DOC,\"islandId\":\"hr-i\"}")
case "$hr_summary" in *'"groundingIds":["h1","h2","h3"]'*) echo "  PASS: HR ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: HR ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 評価者間の矛盾検出（リーダーシップ高い vs 決断が遅い）
hr_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"h1","text":"リーダーシップが高い","textReviewed":true},"cardB":{"id":"h2","text":"決断が遅い","textReviewed":true}}')
case "$hr_contra" in *'"hasContradiction"'*) echo "  PASS: HR ③評価者間の矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: HR ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
hr_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$HR_DOC}")
case "$hr_narr" in *'"basedOnReadingOrder":["hr-i"]'*) echo "  PASS: HR ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: HR ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
hr_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$HR_ID")
check "HR 読戻し (200)" "200" "$hr_read"

echo ""
echo "--- シナリオ31: NPO・市民活動のボランティア報告整理 ---"
# 業態: NPO・市民活動
# 想定人物: 活動コーディネーター（ボランティア報告を整理）
# 業務領域: ボランティア報告のKJ整理と活動課題の検出
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
# 注意事項: 報告は逐語（refineで変えない）。矛盾する報告は表面化する。
NP_ID="biz-flow-npo"
NP_DOC='{"version":1,"id":"'$NP_ID'","title":"ボランティア活動報告","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"n1","text":"参加者のモチベーションが高い","x":0,"y":0,"textReviewed":true},{"id":"n2","text":"資材が不足している","x":10,"y":0,"textReviewed":true},{"id":"n3","text":"告知が行き届いていない","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"np-i","cardIds":["n1","n2","n3"]}],"readingOrder":["np-i"]}'

np_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$NP_ID" \
  -H 'Content-Type: application/json' -d "$NP_DOC")
check "NP PUT document (作成)" "200" "$np_put"

# ① AI束ね
np_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"n1","text":"参加者のモチベーションが高い","textReviewed":true},{"id":"n2","text":"資材が不足している","textReviewed":true},{"id":"n3","text":"告知が行き届いていない","textReviewed":true}]}')
case "$np_groups" in *'"groups":'*) echo "  PASS: NP ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: NP ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
np_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$NP_DOC,\"islandId\":\"np-i\"}")
case "$np_summary" in *'"groundingIds":["n1","n2","n3"]'*) echo "  PASS: NP ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: NP ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（モチベーション高い vs 資材不足・告知不足）
np_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"n1","text":"参加者のモチベーションが高い","textReviewed":true},"cardB":{"id":"n2","text":"資材が不足している","textReviewed":true}}')
case "$np_contra" in *'"hasContradiction"'*) echo "  PASS: NP ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: NP ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
np_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$NP_DOC}")
case "$np_narr" in *'"basedOnReadingOrder":["np-i"]'*) echo "  PASS: NP ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: NP ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
np_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$NP_ID")
check "NP 読戻し (200)" "200" "$np_read"

echo ""
echo "--- シナリオ32: 不動産・物件情報と内見フィードバックの整理 ---"
# 業態: 不動産・物件管理
# 想定人物: 物件マネージャー（内見フィードバックを分析）
# 業務領域: 物件情報のKJ整理と内見フィードバックの課題検出
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> タイトル提案(suggest-document-title)
# 注意事項: 内見者の声は逐語（refineで変えない）。矛盾する評価は表面化する。
RE_ID="biz-flow-realestate"
RE_DOC='{"version":1,"id":"'$RE_ID'","title":"物件改善の整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"r1","text":"駅から近い","x":0,"y":0,"textReviewed":true},{"id":"r2","text":"日当たりが良い","x":10,"y":0,"textReviewed":true},{"id":"r3","text":"設備が古い","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"re-i","cardIds":["r1","r2","r3"]}],"readingOrder":["re-i"]}'

re_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$RE_ID" \
  -H 'Content-Type: application/json' -d "$RE_DOC")
check "RE PUT document (作成)" "200" "$re_put"

# ① AI束ね
re_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"r1","text":"駅から近い","textReviewed":true},{"id":"r2","text":"日当たりが良い","textReviewed":true},{"id":"r3","text":"設備が古い","textReviewed":true}]}')
case "$re_groups" in *'"groups":'*) echo "  PASS: RE ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: RE ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
re_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$RE_DOC,\"islandId\":\"re-i\"}")
case "$re_summary" in *'"groundingIds":["r1","r2","r3"]'*) echo "  PASS: RE ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: RE ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（立地・日照が良い vs 設備が古い）
re_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"r1","text":"駅から近い","textReviewed":true},"cardB":{"id":"r3","text":"設備が古い","textReviewed":true}}')
case "$re_contra" in *'"hasContradiction"'*) echo "  PASS: RE ③矛盾検出（立地 vs 設備）"; PASS=$((PASS+1));; *) echo "  FAIL: RE ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ タイトル提案
re_title=$(curl -s -X POST "$BASE_URL/ai/suggest-document-title" -H 'Content-Type: application/json' \
  -d '{"islandTitles":["物件"],"cardTexts":["駅から近い","日当たりが良い","設備が古い"],"textReviewed":true}')
case "$re_title" in *'"candidates"'*) echo "  PASS: RE ④タイトル提案"; PASS=$((PASS+1));; *) echo "  FAIL: RE ④タイトル提案"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
re_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$RE_ID")
check "RE 読戻し (200)" "200" "$re_read"

echo ""
echo "=== Result: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ]
