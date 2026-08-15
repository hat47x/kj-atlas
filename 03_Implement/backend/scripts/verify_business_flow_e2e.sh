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

echo ""
echo "=== Result: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ]
