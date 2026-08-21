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

# 3b. 読戻し（保存確認）＋ 階層島 parentIslandId の往復保持（DOGFOOD-32 / schemas.md §9）。
get_code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$DOC_ID")
HIER_DOC='{"version":1,"id":"biz-hier","title":"階層","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[],"edges":[],"islands":[{"id":"h1","cardIds":[]},{"id":"h2","cardIds":[],"parentIslandId":"h1"}],"readingOrder":["h1"]}'
curl -s -o /dev/null -X PUT "$BASE_URL/docs/biz-hier" -H 'Content-Type: application/json' -d "$HIER_DOC"
hier_back=$(curl -s "$BASE_URL/docs/biz-hier")
hier_ok=$(echo "$hier_back" | grep -cF '"parentIslandId":"h1"')
if [ "$get_code" = "200" ] && [ "$hier_ok" -ge 1 ]; then
  echo "  PASS: GET document (読戻し) + parentIslandId 往復保持"
  PASS=$((PASS+1))
else
  echo "  FAIL: GET document (読戻し) + parentIslandId (get=$get_code hier=$hier_back)"
  FAIL=$((FAIL+1))
fi

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

# 3d. 島の表札AI提案（suggest-island-summary、メンバーカードのみ grounding。
#     ADR-0077: 複数候補（candidates）を返し、その候補[0]の接地 = メンバーカード。
#     DOGFOOD-34: 違和感（critiqueText）を渡すと候補に反映される（壁打ち往復）。
summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$DOC,\"islandId\":\"i1\"}")
summary_crit=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$DOC,\"islandId\":\"i1\",\"critiqueText\":\"表現が強すぎる\"}")
if echo "$summary" | grep -qF '"candidates":[' \
   && echo "$summary" | grep -qF '"groundingIds":["c1","c2","c3"]' \
   && echo "$summary_crit" | grep -qF '違和感を反映'; then
    echo "  PASS: suggest-island-summary candidates + groundingIds + 壁打ち"
    PASS=$((PASS+1))
else
    echo "  FAIL: suggest-island-summary (summary=$summary crit=$summary_crit)"
    FAIL=$((FAIL+1))
fi

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
  *'"groundingIds":["w1","w2","w3","w4"]'*)
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
echo "--- シナリオ33: 通信・IT・サポート問い合わせの分析 ---"
# 業態: 通信・ITサービス
# 想定人物: サポート品質マネージャー（問い合わせを分析）
# 業務領域: サポート問い合わせのKJ整理と対応課題の検出
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
# 注意事項: 利用者の声は逐語（refineで変えない）。矛盾する報告は表面化する。
IT_ID="biz-flow-it-support"
IT_DOC='{"version":1,"id":"'$IT_ID'","title":"サポート問い合わせ分析","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"i1","text":"ログインが頻繁に失敗する","x":0,"y":0,"textReviewed":true},{"id":"i2","text":"応答速度は満足","x":10,"y":0,"textReviewed":true},{"id":"i3","text":"設定画面が分かりにくい","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"it-i","cardIds":["i1","i2","i3"]}],"readingOrder":["it-i"]}'

it_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$IT_ID" \
  -H 'Content-Type: application/json' -d "$IT_DOC")
check "IT PUT document (作成)" "200" "$it_put"

# ① AI束ね
it_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"i1","text":"ログインが頻繁に失敗する","textReviewed":true},{"id":"i2","text":"応答速度は満足","textReviewed":true},{"id":"i3","text":"設定画面が分かりにくい","textReviewed":true}]}')
case "$it_groups" in *'"groups":'*) echo "  PASS: IT ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: IT ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
it_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$IT_DOC,\"islandId\":\"it-i\"}")
case "$it_summary" in *'"groundingIds":["i1","i2","i3"]'*) echo "  PASS: IT ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: IT ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（ログイン失敗 vs 応答速度満足）
it_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"i1","text":"ログインが頻繁に失敗する","textReviewed":true},"cardB":{"id":"i2","text":"応答速度は満足","textReviewed":true}}')
case "$it_contra" in *'"hasContradiction"'*) echo "  PASS: IT ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: IT ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
it_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$IT_DOC}")
case "$it_narr" in *'"basedOnReadingOrder":["it-i"]'*) echo "  PASS: IT ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: IT ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
it_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$IT_ID")
check "IT 読戻し (200)" "200" "$it_read"

echo ""
echo "--- シナリオ34: エネルギー・設備点検レポートの整理 ---"
# 業態: エネルギー・インフラ
# 想定人物: 設備点検リーダー（点検レポートを整理）
# 業務領域: 設備点検レポートのKJ整理と異常の優先順位付けの基礎
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 島間関係要約(summarize-island-relation) -> タイトル提案(suggest-document-title)
# 注意事項: 点検記録は逐語（refineで変えない）。異常の因果は提案のみ。
EN_ID="biz-flow-energy"
EN_DOC='{"version":1,"id":"'$EN_ID'","title":"設備点検レポート","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"e1","text":"冷却系の温度が高い","x":0,"y":0,"textReviewed":true},{"id":"e2","text":"振動が大きくなっている","x":10,"y":0,"textReviewed":true},{"id":"e3","text":"潤滑油の量が少ない","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"en-a","cardIds":["e1","e2"]},{"id":"en-b","cardIds":["e3"]}],"readingOrder":["en-a","en-b"]}'

en_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$EN_ID" \
  -H 'Content-Type: application/json' -d "$EN_DOC")
check "EN PUT document (作成)" "200" "$en_put"

# ① AI束ね
en_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"e1","text":"冷却系の温度が高い","textReviewed":true},{"id":"e2","text":"振動が大きくなっている","textReviewed":true},{"id":"e3","text":"潤滑油の量が少ない","textReviewed":true}]}')
case "$en_groups" in *'"groups":'*) echo "  PASS: EN ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: EN ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
en_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$EN_DOC,\"islandId\":\"en-a\"}")
case "$en_summary" in *'"groundingIds":["e1","e2"]'*) echo "  PASS: EN ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: EN ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 島間関係の要約（潤滑油不足 → 振動・温度上昇 の因果）
en_rel=$(curl -s -X POST "$BASE_URL/ai/summarize-island-relation" -H 'Content-Type: application/json' \
  -d "{\"doc\":$EN_DOC,\"islandAId\":\"en-b\",\"islandBId\":\"en-a\",\"relationType\":\"causal\",\"derived\":false,\"groundingCardIds\":[\"e1\"],\"groundingEdgeIds\":[],\"cardTexts\":[{\"id\":\"e1\",\"text\":\"冷却系の温度が高い\"}]}")
case "$en_rel" in *'"text"'*) echo "  PASS: EN ③島間関係の要約 (causal)"; PASS=$((PASS+1));; *) echo "  FAIL: EN ③関係要約 (${en_rel:0:100})"; FAIL=$((FAIL+1));; esac

# ④ タイトル提案
en_title=$(curl -s -X POST "$BASE_URL/ai/suggest-document-title" -H 'Content-Type: application/json' \
  -d '{"islandTitles":["設備"],"cardTexts":["冷却系の温度が高い","振動が大きくなっている","潤滑油の量が少ない"],"textReviewed":true}')
case "$en_title" in *'"candidates"'*) echo "  PASS: EN ④タイトル提案"; PASS=$((PASS+1));; *) echo "  FAIL: EN ④タイトル提案"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
en_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$EN_ID")
check "EN 読戻し (200)" "200" "$en_read"

echo ""
echo "--- シナリオ35: 農業・生産者レポートの整理 ---"
# 業態: 農業・アグリテック
# 想定人物: 営農アドバイザー（生産者レポートを分析）
# 業務領域: 圃場レポートのKJ整理と栽培課題の検出
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
# 注意事項: 生産者の声は逐語（refineで変えない）。矛盾する報告は表面化する。
AG_ID="biz-flow-agriculture"
AG_DOC='{"version":1,"id":"'$AG_ID'","title":"圃場レポート分析","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"a1","text":"収量が昨年より増えた","x":0,"y":0,"textReviewed":true},{"id":"a2","text":"病害が広がっている","x":10,"y":0,"textReviewed":true},{"id":"a3","text":"灌漑設備が十分機能する","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"ag-i","cardIds":["a1","a2","a3"]}],"readingOrder":["ag-i"]}'

ag_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$AG_ID" \
  -H 'Content-Type: application/json' -d "$AG_DOC")
check "AG PUT document (作成)" "200" "$ag_put"

# ① AI束ね
ag_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"a1","text":"収量が昨年より増えた","textReviewed":true},{"id":"a2","text":"病害が広がっている","textReviewed":true},{"id":"a3","text":"灌漑設備が十分機能する","textReviewed":true}]}')
case "$ag_groups" in *'"groups":'*) echo "  PASS: AG ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: AG ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
ag_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$AG_DOC,\"islandId\":\"ag-i\"}")
case "$ag_summary" in *'"groundingIds":["a1","a2","a3"]'*) echo "  PASS: AG ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: AG ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（収量増 vs 病害拡大）
ag_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"a1","text":"収量が昨年より増えた","textReviewed":true},"cardB":{"id":"a2","text":"病害が広がっている","textReviewed":true}}')
case "$ag_contra" in *'"hasContradiction"'*) echo "  PASS: AG ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: AG ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
ag_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$AG_DOC}")
case "$ag_narr" in *'"basedOnReadingOrder":["ag-i"]'*) echo "  PASS: AG ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: AG ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
ag_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$AG_ID")
check "AG 読戻し (200)" "200" "$ag_read"

echo ""
echo "--- シナリオ36: 物流・配送現場報告の整理 ---"
# 業態: 物流・配送
# 想定人物: 配送管理者（現場報告を分析）
# 業務領域: 配送現場報告のKJ整理と配送課題の検出
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> タイトル提案(suggest-document-title)
# 注意事項: 現場の声は逐語（refineで変えない）。矛盾する報告は表面化する。
LG2_ID="biz-flow-logistics"
LG2_DOC='{"version":1,"id":"'$LG2_ID'","title":"配送現場の報告","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"l1","text":"配送時間が守られている","x":0,"y":0,"textReviewed":true},{"id":"l2","text":"荷物の破損が増えている","x":10,"y":0,"textReviewed":true},{"id":"l3","text":"ルートの最適化が進む","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"lg2-i","cardIds":["l1","l2","l3"]}],"readingOrder":["lg2-i"]}'

lg2_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$LG2_ID" \
  -H 'Content-Type: application/json' -d "$LG2_DOC")
check "LG2 PUT document (作成)" "200" "$lg2_put"

# ① AI束ね
lg2_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"l1","text":"配送時間が守られている","textReviewed":true},{"id":"l2","text":"荷物の破損が増えている","textReviewed":true},{"id":"l3","text":"ルートの最適化が進む","textReviewed":true}]}')
case "$lg2_groups" in *'"groups":'*) echo "  PASS: LG2 ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: LG2 ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
lg2_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$LG2_DOC,\"islandId\":\"lg2-i\"}")
case "$lg2_summary" in *'"groundingIds":["l1","l2","l3"]'*) echo "  PASS: LG2 ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: LG2 ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（時間厳守 vs 破損増加）
lg2_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"l1","text":"配送時間が守られている","textReviewed":true},"cardB":{"id":"l2","text":"荷物の破損が増えている","textReviewed":true}}')
case "$lg2_contra" in *'"hasContradiction"'*) echo "  PASS: LG2 ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: LG2 ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ タイトル提案
lg2_title=$(curl -s -X POST "$BASE_URL/ai/suggest-document-title" -H 'Content-Type: application/json' \
  -d '{"islandTitles":["配送"],"cardTexts":["配送時間が守られている","荷物の破損が増えている","ルートの最適化が進む"],"textReviewed":true}')
case "$lg2_title" in *'"candidates"'*) echo "  PASS: LG2 ④タイトル提案"; PASS=$((PASS+1));; *) echo "  FAIL: LG2 ④タイトル提案"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
lg2_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$LG2_ID")
check "LG2 読戻し (200)" "200" "$lg2_read"

echo ""
echo "--- シナリオ37: 食品・飲食・メニュー改善の顧客声分析 ---"
# 業態: 食品・飲食
# 想定人物: メニュー開発担当（顧客の声を分析）
# 業務領域: メニュー改善の顧客声KJ整理と改善課題の検出
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
# 注意事項: 顧客の声は逐語（refineで変えない）。矛盾する評価は表面化する。
FD_ID="biz-flow-food"
FD_DOC='{"version":1,"id":"'$FD_ID'","title":"メニュー改善の分析","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"d1","text":"味付けは好評","x":0,"y":0,"textReviewed":true},{"id":"d2","text":"提供時間が長い","x":10,"y":0,"textReviewed":true},{"id":"d3","text":"価格は妥当","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"fd-i","cardIds":["d1","d2","d3"]}],"readingOrder":["fd-i"]}'

fd_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$FD_ID" \
  -H 'Content-Type: application/json' -d "$FD_DOC")
check "FD PUT document (作成)" "200" "$fd_put"

# ① AI束ね
fd_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"d1","text":"味付けは好評","textReviewed":true},{"id":"d2","text":"提供時間が長い","textReviewed":true},{"id":"d3","text":"価格は妥当","textReviewed":true}]}')
case "$fd_groups" in *'"groups":'*) echo "  PASS: FD ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: FD ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
fd_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$FD_DOC,\"islandId\":\"fd-i\"}")
case "$fd_summary" in *'"groundingIds":["d1","d2","d3"]'*) echo "  PASS: FD ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: FD ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（味好評 vs 提供時間長い）
fd_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"d1","text":"味付けは好評","textReviewed":true},"cardB":{"id":"d2","text":"提供時間が長い","textReviewed":true}}')
case "$fd_contra" in *'"hasContradiction"'*) echo "  PASS: FD ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: FD ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
fd_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$FD_DOC}")
case "$fd_narr" in *'"basedOnReadingOrder":["fd-i"]'*) echo "  PASS: FD ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: FD ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
fd_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$FD_ID")
check "FD 読戻し (200)" "200" "$fd_read"

echo ""
echo "--- シナリオ38: 編集者・ナラティブA/B不整合の検出 ---"
# 業態: 出版・報道（シナリオ5のA/B不整合検出の拡張）
# 想定人物: 編集者（ナラティブと図解の不整合を検出）
# 業務領域: ナラティブのA/B照合で不整合の方向と件数を報告
# 操作内容: 文書作成 -> check-narrative（A/B不整合の検出・direction/counts）
# 注意事項: 不整合は「カードにない主張（b_missing_in_a）」と「触れていない島
#          （a_missing_in_b）」を方向で報告。件数（counts）は報告の正本。
AB_ID="biz-flow-ab-mismatch"
AB_DOC='{"version":1,"id":"'$AB_ID'","title":"A/B照合検証","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"c1","text":"事実A","x":0,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"i1","cardIds":["c1"],"summaryText":"s"}],"readingOrder":["i1"]}'

ab_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$AB_ID" \
  -H 'Content-Type: application/json' -d "$AB_DOC")
check "AB PUT document (作成)" "200" "$ab_put"

# A/B不整合の検出（モックは marker「未検証の主張」で a_missing_in_b を報告）。
ab_narr=$(curl -s -X POST "$BASE_URL/ai/check-narrative" -H 'Content-Type: application/json' \
  -d "{\"doc\":$AB_DOC,\"narrativeText\":\"（草稿）事実Aに加えて、未検証の主張が含まれている。\",\"basedOnReadingOrder\":[\"i1\"]}")
case "$ab_narr" in
  *'"direction":"a_missing_in_b"'*)
    echo "  PASS: AB ①A/B不整合の方向（a_missing_in_b）"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: AB ①A/B不整合の方向（got ${ab_narr:0:150}）"
    FAIL=$((FAIL+1))
    ;;
esac
case "$ab_narr" in
  *'"counts"'*'"bMissingInA":0'*'"aMissingInB":1'*)
    echo "  PASS: AB ②A/B件数（counts: bMissingInA=0/aMissingInB=1）"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: AB ②A/B件数（got ${ab_narr:0:150}）"
    FAIL=$((FAIL+1))
    ;;
esac

echo ""
echo "--- シナリオ39: スポーツ・コーチング・選手フィードバックの整理 ---"
# 業態: スポーツ・コーチング
# 想定人物: コーチ（選手フィードバックを整理）
# 業務領域: 選手フィードバックのKJ整理と強化課題の検出
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
# 注意事項: 選手の声は逐語（refineで変えない）。矛盾する評価は表面化する。
SP_ID="biz-flow-sports"
SP_DOC='{"version":1,"id":"'$SP_ID'","title":"チーム強化の分析","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"s1","text":"フィジカルが向上している","x":0,"y":0,"textReviewed":true},{"id":"s2","text":"戦術理解が不足している","x":10,"y":0,"textReviewed":true},{"id":"s3","text":"連携は良好","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"sp-i","cardIds":["s1","s2","s3"]}],"readingOrder":["sp-i"]}'

sp_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$SP_ID" \
  -H 'Content-Type: application/json' -d "$SP_DOC")
check "SP PUT document (作成)" "200" "$sp_put"

# ① AI束ね
sp_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"s1","text":"フィジカルが向上している","textReviewed":true},{"id":"s2","text":"戦術理解が不足している","textReviewed":true},{"id":"s3","text":"連携は良好","textReviewed":true}]}')
case "$sp_groups" in *'"groups":'*) echo "  PASS: SP ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: SP ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
sp_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$SP_DOC,\"islandId\":\"sp-i\"}")
case "$sp_summary" in *'"groundingIds":["s1","s2","s3"]'*) echo "  PASS: SP ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: SP ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（フィジカル向上 vs 戦術理解不足）
sp_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"s1","text":"フィジカルが向上している","textReviewed":true},"cardB":{"id":"s2","text":"戦術理解が不足している","textReviewed":true}}')
case "$sp_contra" in *'"hasContradiction"'*) echo "  PASS: SP ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: SP ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
sp_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$SP_DOC}")
case "$sp_narr" in *'"basedOnReadingOrder":["sp-i"]'*) echo "  PASS: SP ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: SP ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
sp_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$SP_ID")
check "SP 読戻し (200)" "200" "$sp_read"

echo ""
echo "--- シナリオ40: 研究開発・製薬・治験データの整理 ---"
# 業態: 研究開発・製薬
# 想定人物: 治験データアナリスト（治験結果を整理）
# 業務領域: 治験データのKJ整理と安全性シグナルの検出
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> タイトル提案(suggest-document-title)
# 注意事項: 治験データは逐語（refineで変えない）。矛盾する安全性シグナルは表面化する。
RD_ID="biz-flow-pharma"
RD_DOC='{"version":1,"id":"'$RD_ID'","title":"治験データの整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"p1","text":"有効性は高い","x":0,"y":0,"textReviewed":true},{"id":"p2","text":"有害事象が報告されている","x":10,"y":0,"textReviewed":true},{"id":"p3","text":"服薬コンプライアンスは良好","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"rd-i","cardIds":["p1","p2","p3"]}],"readingOrder":["rd-i"]}'

rd_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$RD_ID" \
  -H 'Content-Type: application/json' -d "$RD_DOC")
check "RD PUT document (作成)" "200" "$rd_put"

# ① AI束ね
rd_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"p1","text":"有効性は高い","textReviewed":true},{"id":"p2","text":"有害事象が報告されている","textReviewed":true},{"id":"p3","text":"服薬コンプライアンスは良好","textReviewed":true}]}')
case "$rd_groups" in *'"groups":'*) echo "  PASS: RD ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: RD ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
rd_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$RD_DOC,\"islandId\":\"rd-i\"}")
case "$rd_summary" in *'"groundingIds":["p1","p2","p3"]'*) echo "  PASS: RD ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: RD ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（有効性 vs 有害事象 — 安全性シグナル）
rd_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"p1","text":"有効性は高い","textReviewed":true},"cardB":{"id":"p2","text":"有害事象が報告されている","textReviewed":true}}')
case "$rd_contra" in *'"hasContradiction"'*) echo "  PASS: RD ③安全性シグナルの矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: RD ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ タイトル提案
rd_title=$(curl -s -X POST "$BASE_URL/ai/suggest-document-title" -H 'Content-Type: application/json' \
  -d '{"islandTitles":["治験"],"cardTexts":["有効性は高い","有害事象が報告されている","服薬コンプライアンスは良好"],"textReviewed":true}')
case "$rd_title" in *'"candidates"'*) echo "  PASS: RD ④タイトル提案"; PASS=$((PASS+1));; *) echo "  FAIL: RD ④タイトル提案"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
rd_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$RD_ID")
check "RD 読戻し (200)" "200" "$rd_read"

echo ""
echo "--- シナリオ41: 保険・事故・請求データの分析 ---"
# 業態: 保険・損害保険
# 想定人物: 保険査定担当（事故・請求データを分析）
# 業務領域: 事故・請求データのKJ整理とリスク要因の検出
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
# 注意事項: 請求データは逐語（refineで変えない）。矛盾する報告は表面化する。
IN_ID="biz-flow-insurance"
IN_DOC='{"version":1,"id":"'$IN_ID'","title":"事故・請求データ分析","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"n1","text":"事故の報告が減少している","x":0,"y":0,"textReviewed":true},{"id":"n2","text":"保険金請求が増えている","x":10,"y":0,"textReviewed":true},{"id":"n3","text":"対応プロセスは円滑","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"in-i","cardIds":["n1","n2","n3"]}],"readingOrder":["in-i"]}'

in_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$IN_ID" \
  -H 'Content-Type: application/json' -d "$IN_DOC")
check "IN PUT document (作成)" "200" "$in_put"

# ① AI束ね
in_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"n1","text":"事故の報告が減少している","textReviewed":true},{"id":"n2","text":"保険金請求が増えている","textReviewed":true},{"id":"n3","text":"対応プロセスは円滑","textReviewed":true}]}')
case "$in_groups" in *'"groups":'*) echo "  PASS: IN ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: IN ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
in_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$IN_DOC,\"islandId\":\"in-i\"}")
case "$in_summary" in *'"groundingIds":["n1","n2","n3"]'*) echo "  PASS: IN ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: IN ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（事故減少 vs 請求増加）
in_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"n1","text":"事故の報告が減少している","textReviewed":true},"cardB":{"id":"n2","text":"保険金請求が増えている","textReviewed":true}}')
case "$in_contra" in *'"hasContradiction"'*) echo "  PASS: IN ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: IN ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
in_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$IN_DOC}")
case "$in_narr" in *'"basedOnReadingOrder":["in-i"]'*) echo "  PASS: IN ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: IN ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
in_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$IN_ID")
check "IN 読戻し (200)" "200" "$in_read"

echo ""
echo "--- シナリオ42: 環境・環境影響評価の整理 ---"
# 業態: 環境・コンサルティング
# 想定人物: 環境影響評価担当（環境評価データを整理）
# 業務領域: 環境影響評価のKJ整理と影響要因の検出
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
# 注意事項: 調査データは逐語（refineで変えない）。矛盾する影響要因は表面化する。
EV_ID="biz-flow-env"
EV_DOC='{"version":1,"id":"'$EV_ID'","title":"環境影響評価の整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"e1","text":"水質は基準を満たす","x":0,"y":0,"textReviewed":true},{"id":"e2","text":"騒音の苦情が増えている","x":10,"y":0,"textReviewed":true},{"id":"e3","text":"植生は保全されている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"ev-i","cardIds":["e1","e2","e3"]}],"readingOrder":["ev-i"]}'

ev_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$EV_ID" \
  -H 'Content-Type: application/json' -d "$EV_DOC")
check "EV PUT document (作成)" "200" "$ev_put"

# ① AI束ね
ev_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"e1","text":"水質は基準を満たす","textReviewed":true},{"id":"e2","text":"騒音の苦情が増えている","textReviewed":true},{"id":"e3","text":"植生は保全されている","textReviewed":true}]}')
case "$ev_groups" in *'"groups":'*) echo "  PASS: EV ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: EV ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
ev_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$EV_DOC,\"islandId\":\"ev-i\"}")
case "$ev_summary" in *'"groundingIds":["e1","e2","e3"]'*) echo "  PASS: EV ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: EV ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（水質基準充足 vs 騒音苦情増加）
ev_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"e1","text":"水質は基準を満たす","textReviewed":true},"cardB":{"id":"e2","text":"騒音の苦情が増えている","textReviewed":true}}')
case "$ev_contra" in *'"hasContradiction"'*) echo "  PASS: EV ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: EV ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
ev_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$EV_DOC}")
case "$ev_narr" in *'"basedOnReadingOrder":["ev-i"]'*) echo "  PASS: EV ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: EV ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
ev_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$EV_ID")
check "EV 読戻し (200)" "200" "$ev_read"

echo ""
echo "--- シナリオ43: 建設・施工現場進捗の整理 ---"
# 業態: 建設・施工
# 想定人物: 現場監督（施工進捗を整理）
# 業務領域: 施工現場報告のKJ整理と工程課題の検出
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
# 注意事項: 現場報告は逐語（refineで変えない）。矛盾する工程報告は表面化する。
CS_ID="biz-flow-construction"
CS_DOC='{"version":1,"id":"'$CS_ID'","title":"施工進捗の整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"c1","text":"基礎工事は予定通り","x":0,"y":0,"textReviewed":true},{"id":"c2","text":"資材の納入が遅れている","x":10,"y":0,"textReviewed":true},{"id":"c3","text":"安全対策は徹底されている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"cs-i","cardIds":["c1","c2","c3"]}],"readingOrder":["cs-i"]}'

cs_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$CS_ID" \
  -H 'Content-Type: application/json' -d "$CS_DOC")
check "CS PUT document (作成)" "200" "$cs_put"

# ① AI束ね
cs_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"c1","text":"基礎工事は予定通り","textReviewed":true},{"id":"c2","text":"資材の納入が遅れている","textReviewed":true},{"id":"c3","text":"安全対策は徹底されている","textReviewed":true}]}')
case "$cs_groups" in *'"groups":'*) echo "  PASS: CS ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: CS ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
cs_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$CS_DOC,\"islandId\":\"cs-i\"}")
case "$cs_summary" in *'"groundingIds":["c1","c2","c3"]'*) echo "  PASS: CS ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: CS ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（基礎工事順調 vs 資材納入遅延）
cs_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"c1","text":"基礎工事は予定通り","textReviewed":true},"cardB":{"id":"c2","text":"資材の納入が遅れている","textReviewed":true}}')
case "$cs_contra" in *'"hasContradiction"'*) echo "  PASS: CS ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: CS ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
cs_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$CS_DOC}")
case "$cs_narr" in *'"basedOnReadingOrder":["cs-i"]'*) echo "  PASS: CS ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: CS ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
cs_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$CS_ID")
check "CS 読戻し (200)" "200" "$cs_read"

echo ""
echo "--- シナリオ44: 通信・キャリア・ネットワーク障害分析 ---"
# 業態: 通信・キャリア
# 想定人物: ネットワーク運用担当（障害報告を整理）
# 業務領域: ネットワーク障害報告のKJ整理と障害要因の検出
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
# 注意事項: 障害報告は逐語（refineで変えない）。矛盾する報告は表面化する。
TC_ID="biz-flow-telecom"
TC_DOC='{"version":1,"id":"'$TC_ID'","title":"ネットワーク障害の整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"t1","text":"光回線は安定している","x":0,"y":0,"textReviewed":true},{"id":"t2","text":"モバイル網で遅延が増えている","x":10,"y":0,"textReviewed":true},{"id":"t3","text":"サポート対応は迅速","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"tc-i","cardIds":["t1","t2","t3"]}],"readingOrder":["tc-i"]}'

tc_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$TC_ID" \
  -H 'Content-Type: application/json' -d "$TC_DOC")
check "TC PUT document (作成)" "200" "$tc_put"

# ① AI束ね
tc_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"t1","text":"光回線は安定している","textReviewed":true},{"id":"t2","text":"モバイル網で遅延が増えている","textReviewed":true},{"id":"t3","text":"サポート対応は迅速","textReviewed":true}]}')
case "$tc_groups" in *'"groups":'*) echo "  PASS: TC ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: TC ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
tc_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$TC_DOC,\"islandId\":\"tc-i\"}")
case "$tc_summary" in *'"groundingIds":["t1","t2","t3"]'*) echo "  PASS: TC ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: TC ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（光回線安定 vs モバイル網遅延）
tc_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"t1","text":"光回線は安定している","textReviewed":true},"cardB":{"id":"t2","text":"モバイル網で遅延が増えている","textReviewed":true}}')
case "$tc_contra" in *'"hasContradiction"'*) echo "  PASS: TC ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: TC ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
tc_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$TC_DOC}")
case "$tc_narr" in *'"basedOnReadingOrder":["tc-i"]'*) echo "  PASS: TC ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: TC ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
tc_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$TC_ID")
check "TC 読戻し (200)" "200" "$tc_read"

echo ""
echo "--- シナリオ45: 教育・大学・研究プロジェクトの振り返り整理 ---"
# 業態: 教育・大学（研究プロジェクト）
# 想定人物: 研究プロジェクトリーダー（プロジェクト振り返りを整理）
# 業務領域: 研究プロジェクトの振り返りのKJ整理と課題の検出
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
# 注意事項: メンバーの声は逐語（refineで変えない）。矛盾する報告は表面化する。
UV_ID="biz-flow-university"
UV_DOC='{"version":1,"id":"'$UV_ID'","title":"研究プロジェクト振り返り","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"u1","text":"成果は計画通り","x":0,"y":0,"textReviewed":true},{"id":"u2","text":"人員が不足している","x":10,"y":0,"textReviewed":true},{"id":"u3","text":"国際連携は進んでいる","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"uv-i","cardIds":["u1","u2","u3"]}],"readingOrder":["uv-i"]}'

uv_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$UV_ID" \
  -H 'Content-Type: application/json' -d "$UV_DOC")
check "UV PUT document (作成)" "200" "$uv_put"

# ① AI束ね
uv_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"u1","text":"成果は計画通り","textReviewed":true},{"id":"u2","text":"人員が不足している","textReviewed":true},{"id":"u3","text":"国際連携は進んでいる","textReviewed":true}]}')
case "$uv_groups" in *'"groups":'*) echo "  PASS: UV ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: UV ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
uv_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$UV_DOC,\"islandId\":\"uv-i\"}")
case "$uv_summary" in *'"groundingIds":["u1","u2","u3"]'*) echo "  PASS: UV ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: UV ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（成果計画通り vs 人員不足）
uv_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"u1","text":"成果は計画通り","textReviewed":true},"cardB":{"id":"u2","text":"人員が不足している","textReviewed":true}}')
case "$uv_contra" in *'"hasContradiction"'*) echo "  PASS: UV ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: UV ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
uv_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$UV_DOC}")
case "$uv_narr" in *'"basedOnReadingOrder":["uv-i"]'*) echo "  PASS: UV ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: UV ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
uv_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$UV_ID")
check "UV 読戻し (200)" "200" "$uv_read"

echo ""
echo "--- シナリオ46: 医療・診断・診断確定前の反対視点レビュー（保留接続） ---"
# 業態: 医療・診断（診断確定前レビュー）
# 想定人物: 診断医（確定前に反対視点・根拠不足をレビューし、保留する）
# 業務領域: 診断カルテのKJ整理と、確定前の反対視点・根拠不足の検出・保留接続
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 反対視点提案(propose-opposing-viewpoint) -> 保留接続(holdState=held)
#          -> ナラティブ(generate-narrative) -> 読戻し（非自動適用の確認）
# 注意事項: 反対視点はproposal-only（status=proposed・reviewState=unreviewed・自動適用なし）。
#          AI提案はカード文面を書き換えない。人間が「保留して再確認」で holdState=held に
#          接続し、違和感・根拠不足を作業状態として残す（AI-OPPOSE-01 R2・非破壊接続）。
DX_ID="biz-flow-diagnosis"
DX_DOC='{"version":1,"id":"'$DX_ID'","title":"診断確定前レビュー","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"dx1","text":"検査値は基準範囲内","x":0,"y":0,"textReviewed":true},{"id":"dx2","text":"症状は軽症で経過観察が妥当","x":10,"y":0,"textReviewed":true},{"id":"dx3","text":"問診で夜間の呼吸困難を訴えている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"dx-i","cardIds":["dx1","dx2","dx3"]}],"readingOrder":["dx-i"]}'
# 人間の「保留して再確認」を文書へ反映した版（dx2 を holdState=held へ・文面は不変）
DX_DOC_HELD='{"version":1,"id":"'$DX_ID'","title":"診断確定前レビュー","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"dx1","text":"検査値は基準範囲内","x":0,"y":0,"textReviewed":true},{"id":"dx2","text":"症状は軽症で経過観察が妥当","x":10,"y":0,"textReviewed":true,"holdState":"held"},{"id":"dx3","text":"問診で夜間の呼吸困難を訴えている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"dx-i","cardIds":["dx1","dx2","dx3"]}],"readingOrder":["dx-i"]}'

dx_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$DX_ID" \
  -H 'Content-Type: application/json' -d "$DX_DOC")
check "DX PUT document (作成)" "200" "$dx_put"

# ① AI束ね
dx_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"dx1","text":"検査値は基準範囲内","textReviewed":true},{"id":"dx2","text":"症状は軽症で経過観察が妥当","textReviewed":true},{"id":"dx3","text":"問診で夜間の呼吸困難を訴えている","textReviewed":true}]}')
case "$dx_groups" in *'"groups":'*) echo "  PASS: DX ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: DX ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
dx_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$DX_DOC,\"islandId\":\"dx-i\"}")
case "$dx_summary" in *'"groundingIds":["dx1","dx2","dx3"]'*) echo "  PASS: DX ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: DX ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 反対視点提案（AI-OPPOSE-01: 軽症判断への反対視点・根拠不足・proposal-only境界）
dx_oppose=$(curl -s -X POST "$BASE_URL/ai/proposals/opposing-viewpoint" -H 'Content-Type: application/json' \
  -d "{\"doc\":$DX_DOC,\"targetCardId\":\"dx2\"}")
case "$dx_oppose" in
  *'"status":"proposed"'*'"reviewState":"unreviewed"'*) echo "  PASS: DX ③反対視点提案(proposal-only)"; PASS=$((PASS+1));;
  *) echo "  FAIL: DX ③反対視点提案(proposal-only)"; FAIL=$((FAIL+1));; esac
case "$dx_oppose" in
  *'"opposingText"'*'"evidenceGap":true'*'"rationale"'*) echo "  PASS: DX ③b根拠不足(evidenceGap)"; PASS=$((PASS+1));;
  *) echo "  FAIL: DX ③b根拠不足(evidenceGap)"; FAIL=$((FAIL+1));; esac

# ④ 保留接続（人間の「保留して再確認」を文書へ反映・AI-OPPOSE-01 R2 非破壊接続）
dx_hold=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$DX_ID" \
  -H 'Content-Type: application/json' -d "$DX_DOC_HELD")
check "DX ④保留接続 (holdState=held を反映)" "200" "$dx_hold"

# ⑤ ナラティブ
dx_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$DX_DOC_HELD}")
case "$dx_narr" in *'"basedOnReadingOrder":["dx-i"]'*) echo "  PASS: DX ⑤ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: DX ⑤ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し：保留状態が永続し、カード文面が自動適用で書き換わらない（非自動適用）
dx_read=$(curl -s "$BASE_URL/docs/$DX_ID")
case "$dx_read" in *'"holdState":"held"'*) echo "  PASS: DX ⑥保留状態が永続"; PASS=$((PASS+1));; *) echo "  FAIL: DX ⑥保留状態が永続"; FAIL=$((FAIL+1));; esac
case "$dx_read" in
  *'"text":"症状は軽症で経過観察が妥当"'*) echo "  PASS: DX ⑥b非自動適用（文面不変）"; PASS=$((PASS+1));;
  *) echo "  FAIL: DX ⑥b非自動適用（文面不変）"; FAIL=$((FAIL+1));; esac

echo ""
echo "--- シナリオ47: AI運用・ITガバナンスのモデル選択とテナント許容制限 ---"
# 業態: AI運用・ITガバナンス
# 想定人物: AI機能利用者（業務ユーザーがモデルを選択）
# 業務領域: 文書整理AIのモデル選択とテナント許容制限の適用
# 操作内容: 文書作成 -> モデル一覧取得(GET /ai/available-models・R2データ源)
#          -> 許容モデル明示選択で生成(generate-narrative+model)
#          -> テナント許容リスト設定(admin) -> 一覧が制限を反映
#          -> 非許容モデルは403(model_not_allowed・R3 fail-closed)
# 注意事項: モデル選択はテナント許容リストに制限される（空=プラットフォーム既定=全許可）。
#          非許容モデルは LLM 呼び出し前に fail-closed(403) で遮断される（自動降格しない）。
MG_ID="biz-flow-model-gov"
MG_DOC='{"version":1,"id":"'$MG_ID'","title":"モデル選択検証","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"m1","text":"モデルAの要約精度は高い","x":0,"y":0,"textReviewed":true},{"id":"m2","text":"モデルBはコストが低い","x":10,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"mg-i","cardIds":["m1","m2"]}],"readingOrder":["mg-i"]}'

mg_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$MG_ID" \
  -H 'Content-Type: application/json' -d "$MG_DOC")
check "MG PUT document (作成)" "200" "$mg_put"

# ① モデル一覧取得（AI-MODEL-GOVERNANCE R2: モデルセレクタのデータ源）
mg_models=$(curl -s "$BASE_URL/ai/available-models")
MG_MODEL_ID=$(printf '%s' "$mg_models" | sed -n 's/.*"id":"\([^"]*\)".*/\1/p' | head -1)
case "$mg_models" in
  *'"models":['*)
    if [ -n "$MG_MODEL_ID" ]; then echo "  PASS: MG ①モデル一覧取得 (id=$MG_MODEL_ID)"; PASS=$((PASS+1));
    else echo "  FAIL: MG ①モデル一覧取得 (models 空)"; FAIL=$((FAIL+1)); fi;;
  *) echo "  FAIL: MG ①モデル一覧取得"; FAIL=$((FAIL+1));; esac

# ② 許容モデル明示選択で生成（R2: 操作単位モデル上書き・有効モデルは 200）
mg_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' \
  -d "{\"doc\":$MG_DOC,\"model\":\"$MG_MODEL_ID\"}")
case "$mg_narr" in *'"basedOnReadingOrder":["mg-i"]'*) echo "  PASS: MG ②許容モデル明示選択(200)"; PASS=$((PASS+1));; *) echo "  FAIL: MG ②許容モデル明示選択"; FAIL=$((FAIL+1));; esac

# ②b 未登録モデルIDはプラットフォーム既定でも 403（AI-MODEL-GOVERNANCE-02:
#     空allowlist=active登録済みのみ許可・未登録は LLM 呼び出し前に遮断）
mg_bogus=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' \
  -d "{\"doc\":$MG_DOC,\"model\":\"totally-bogus-model\"}")
mg_bogus_code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/ai/generate-narrative" \
  -H 'Content-Type: application/json' -d "{\"doc\":$MG_DOC,\"model\":\"totally-bogus-model\"}")
check "MG ②b未登録モデル -> 403 (model_not_registered)" "403" "$mg_bogus_code"
case "$mg_bogus" in *'"model_not_registered"'*) echo "  PASS: MG ②b code=model_not_registered"; PASS=$((PASS+1));; *) echo "  FAIL: MG ②b code=model_not_registered"; FAIL=$((FAIL+1));; esac

# ③ 許容リストで default を除外するため、2つ目の登録済みモデル（restricted）を admin API で登録
#    （DOGFOOD-24 追従: 許容リスト強化後は登録済み活性モデルのみ許容・未登録/非活性は 422。
#      providerId は local E2E の seed が常に "local" を登録するため固定）
mg_reg=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/admin/provision/models" \
  -H 'Content-Type: application/json' \
  -d '{"id":"restricted","providerId":"local","displayName":"Restricted","capabilities":"generate"}')
check "MG ③モデル登録(restricted)" "201" "$mg_reg"

# ④ テナント許容リストを [restricted] に制限（default を除外・local-dev の control-plane は無キーで開放）
mg_allow=$(curl -s -o /dev/null -w '%{http_code}' -X PUT \
  "$BASE_URL/admin/provision/models/tenants/local-default/allowlist" \
  -H 'Content-Type: application/json' -d '{"modelIds":["restricted"]}')
check "MG ④テナント許容リスト設定(制限)" "200" "$mg_allow"

# ⑤ 一覧が制限を反映（default は選択候補から消え・restricted のみ残る）
mg_models2=$(curl -s "$BASE_URL/ai/available-models")
case "$mg_models2" in
  *'"id":"'$MG_MODEL_ID'"'*) echo "  FAIL: MG ⑤制限反映（$MG_MODEL_ID が残存）"; FAIL=$((FAIL+1));;
  *'"id":"restricted"'*) echo "  PASS: MG ⑤制限反映（default除外・restricted のみ）"; PASS=$((PASS+1));;
  *) echo "  FAIL: MG ⑤制限反映（restricted が見えない）"; FAIL=$((FAIL+1));; esac

# ⑤b 非許容モデル（default）は 403（R3 fail-closed・LLM 呼び出し前に遮断・code=model_not_allowed）
mg_block=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' \
  -d "{\"doc\":$MG_DOC,\"model\":\"$MG_MODEL_ID\"}")
mg_block_code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/ai/generate-narrative" \
  -H 'Content-Type: application/json' -d "{\"doc\":$MG_DOC,\"model\":\"$MG_MODEL_ID\"}")
check "MG ⑤b非許容モデル -> 403 (model_not_allowed)" "403" "$mg_block_code"
case "$mg_block" in *'"model_not_allowed"'*) echo "  PASS: MG ⑤b code=model_not_allowed"; PASS=$((PASS+1));; *) echo "  FAIL: MG ⑤b code=model_not_allowed"; FAIL=$((FAIL+1));; esac

# ⑥ 許容リストをプラットフォーム既定（空=active登録済み全許可）へ復元。
#    scenario 47 の制限が後続シナリオのモデル検査（card-groups/refine 等）を
#    汚染しないよう、状態を後片付けする（admin での空リスト設定=既定復帰）。
mg_restore=$(curl -s -o /dev/null -w '%{http_code}' -X PUT \
  "$BASE_URL/admin/provision/models/tenants/local-default/allowlist" \
  -H 'Content-Type: application/json' -d '{"modelIds":[]}')
check "MG ⑥許容リスト復元(空=既定)" "200" "$mg_restore"

echo ""
echo "--- シナリオ48: 文化・芸術・美術館の展示企画（来場者声の整理と統合） ---"
# 業態: 文化・芸術（美術館・展示企画）
# 想定人物: キュレーター（展示企画者）
# 業務領域: 来場者フィードバックのKJ整理と、展示コンセプトの統合
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 文面整え(refine-card-text)
#          -> 島間関係要約(summarize-island-relation) -> 統合提案(suggest-merges)
#          -> 読戻し
# 注意事項: refine は来場者の声を逐語で保持（意図を変えない・ADR-0064）。
#          島間関係は示唆（確証でなく・proposal-only）。統合提案は提案（人間が採否）。
MU_ID="biz-flow-museum"
MU_DOC='{"version":1,"id":"'$MU_ID'","title":"展示企画フィードバック","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"cu1","text":"静寂な空間が好評だった","x":0,"y":0,"textReviewed":true},{"id":"cu2","text":"音声ガイドの案内が多すぎるとの声","x":10,"y":0,"textReviewed":true},{"id":"cu3","text":"順路が分かりにくい","x":20,"y":0,"textReviewed":true},{"id":"cu4","text":"企画展のテーマは共感を呼んだ","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"m-1","cardIds":["cu1","cu2"]},{"id":"m-2","cardIds":["cu3","cu4"]}],"readingOrder":["m-1","m-2"]}'

mu_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$MU_ID" \
  -H 'Content-Type: application/json' -d "$MU_DOC")
check "MU PUT document (作成)" "200" "$mu_put"

# ① AI束ね
mu_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"cu1","text":"静寂な空間が好評だった","textReviewed":true},{"id":"cu2","text":"音声ガイドの案内が多すぎるとの声","textReviewed":true},{"id":"cu3","text":"順路が分かりにくい","textReviewed":true},{"id":"cu4","text":"企画展のテーマは共感を呼んだ","textReviewed":true}]}')
case "$mu_groups" in *'"groups":'*) echo "  PASS: MU ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: MU ①束ね"; FAIL=$((FAIL+1));; esac

# ② 文面整え（refine-card-text・逐語性を保持・ADR-0064）
mu_refined=$(curl -s -X POST "$BASE_URL/ai/refine-card-text" -H 'Content-Type: application/json' \
  -d '{"cardText":"音声ガイドの案内が多すぎるとの声","context":"展示鑑賞環境","textReviewed":true}')
case "$mu_refined" in *'"refinedText"'*) echo "  PASS: MU ②文面整え(refine)"; PASS=$((PASS+1));; *) echo "  FAIL: MU ②文面整え(refine)"; FAIL=$((FAIL+1));; esac

# ③ 島間関係要約（summarize-island-relation・モックは下書き示唆＋warnings空）
mu_relation=$(curl -s -X POST "$BASE_URL/ai/summarize-island-relation" -H 'Content-Type: application/json' \
  -d "{\"doc\":$MU_DOC,\"islandAId\":\"m-1\",\"islandBId\":\"m-2\",\"relationType\":\"causal\",\"derived\":false,\"groundingCardIds\":[\"cu2\"],\"groundingEdgeIds\":[],\"cardTexts\":[{\"id\":\"cu2\",\"text\":\"音声ガイドの案内が多すぎるとの声\"}]}")
case "$mu_relation" in
  *'"text"'*'"warnings":[]'*) echo "  PASS: MU ③島間関係要約"; PASS=$((PASS+1));;
  *) echo "  FAIL: MU ③島間関係要約"; FAIL=$((FAIL+1));; esac

# ④ 統合提案（suggest-merges・モックは空提案・人間が採否）
mu_merges=$(curl -s -X POST "$BASE_URL/ai/suggest-merges" -H 'Content-Type: application/json' \
  -d "{\"doc\":$MU_DOC}")
case "$mu_merges" in *'"suggestions"'*) echo "  PASS: MU ④統合提案(merges)"; PASS=$((PASS+1));; *) echo "  FAIL: MU ④統合提案(merges)"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
mu_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$MU_ID")
check "MU 読戻し (200)" "200" "$mu_read"

echo ""
echo "--- シナリオ49: IT運用・AIサービス監視（プロバイダ状態とLLM呼び出し量の確認） ---"
# 業態: IT運用・AIサービス監視
# 想定人物: AI運用担当（サービスのAI状態・コストを監視）
# 業務領域: AIプロバイダの状態確認とLLM呼び出し量（コスト指標）の確認
# 操作内容: 文書作成 -> プロバイダ状態取得(GET /ai/provider-status・前)
#          -> AI操作実行(generate-narrative) -> プロバイダ状態取得(後)
#          -> 読戻し
# 注意事項: provider-status は read-only エコー（ADR-0050 D1・稼働中スイッチなし）。
#          LLM呼び出し回数（OPS-LLM-COST-01）は実呼び出し後にインクリメントされる。
SV_ID="biz-flow-supervise"
SV_DOC='{"version":1,"id":"'$SV_ID'","title":"AIサービス監視","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"sv1","text":"AI要約の利用頻度が高い","x":0,"y":0,"textReviewed":true},{"id":"sv2","text":"モデル呼び出し量の監視が必要","x":10,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"sv-i","cardIds":["sv1","sv2"]}],"readingOrder":["sv-i"]}'

sv_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$SV_ID" \
  -H 'Content-Type: application/json' -d "$SV_DOC")
check "SV PUT document (作成)" "200" "$sv_put"

# ① プロバイダ状態（前）: read-only エコー（providerKind=local）+ callCounts 存在
sv_before=$(curl -s "$BASE_URL/ai/provider-status")
case "$sv_before" in
  *'"providerKind":"local"'*'"callCounts"'*) echo "  PASS: SV ①プロバイダ状態(前)"; PASS=$((PASS+1));;
  *) echo "  FAIL: SV ①プロバイダ状態(前)"; FAIL=$((FAIL+1));; esac

# ② AI操作実行（LLM実呼び出し・コスト指標の分母）
sv_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$SV_DOC}")
case "$sv_narr" in *'"basedOnReadingOrder":["sv-i"]'*) echo "  PASS: SV ②AI操作実行"; PASS=$((PASS+1));; *) echo "  FAIL: SV ②AI操作実行"; FAIL=$((FAIL+1));; esac

# ③ プロバイダ状態（後）: LLM呼び出し回数が増加（OPS-LLM-COST-01）
sv_after=$(curl -s "$BASE_URL/ai/provider-status")
# callCounts の "total":N を抽出（[0-9]+ 必須）。provider-status が tokenUsage の
# "total":{"input":..} も返すため、[0-9]* だと tokenUsage 側の空キャプチャで破綻する。
sv_before_total=$(printf '%s' "$sv_before" | sed -n 's/.*"total":\([0-9][0-9]*\).*/\1/p')
sv_after_total=$(printf '%s' "$sv_after" | sed -n 's/.*"total":\([0-9][0-9]*\).*/\1/p')
if [ -n "$sv_before_total" ] && [ -n "$sv_after_total" ] && [ "$sv_after_total" -gt "$sv_before_total" ]; then
  echo "  PASS: SV ③呼び出し回数が増加 ($sv_before_total -> $sv_after_total)"
  PASS=$((PASS+1))
else
  echo "  FAIL: SV ③呼び出し回数が増加 (before=$sv_before_total after=$sv_after_total)"
  FAIL=$((FAIL+1))
fi

# ④ 読戻し
sv_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$SV_ID")
check "SV 読戻し (200)" "200" "$sv_read"

echo ""
echo "--- シナリオ50: 小売・ECの返品クレーム根本原因分析 ---"
# 業態: 小売・EC（通販・カスタマーサービス）
# 想定人物: ECカスタマーサポートチームリーダー
# 業務領域: 返品・クレームのKJ分類と根本原因の検出
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> レイアウト(suggest-layout)
#          -> ナラティブ(generate-narrative) -> 読戻し
# 注意事項: クレームは逐語で保持。多数意見（最多理由）に埋もれる少数・急増シグナル
#          （商品説明ギャップ）を矛盾検出で表面化する（少数意見の外在化・V2）。
EC_ID="biz-flow-ec"
EC_DOC='{"version":1,"id":"'$EC_ID'","title":"返品クレーム分析","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"ec1","text":"返品理由で最も多いのはサイズ不一致","x":0,"y":0,"textReviewed":true},{"id":"ec2","text":"商品説明と実物のギャップを指摘する声が急増","x":10,"y":0,"textReviewed":true},{"id":"ec3","text":"配送遅延による返品は減少傾向","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"ec-i","cardIds":["ec1","ec2","ec3"]}],"readingOrder":["ec-i"]}'

ec_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$EC_ID" \
  -H 'Content-Type: application/json' -d "$EC_DOC")
check "EC PUT document (作成)" "200" "$ec_put"

# ① AI束ね
ec_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"ec1","text":"返品理由で最も多いのはサイズ不一致","textReviewed":true},{"id":"ec2","text":"商品説明と実物のギャップを指摘する声が急増","textReviewed":true},{"id":"ec3","text":"配送遅延による返品は減少傾向","textReviewed":true}]}')
case "$ec_groups" in *'"groups":'*) echo "  PASS: EC ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: EC ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
ec_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$EC_DOC,\"islandId\":\"ec-i\"}")
case "$ec_summary" in *'"groundingIds":["ec1","ec2","ec3"]'*) echo "  PASS: EC ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: EC ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（最多理由 vs 急増シグナル・少数意見の表面化）
ec_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"ec1","text":"返品理由で最も多いのはサイズ不一致","textReviewed":true},"cardB":{"id":"ec2","text":"商品説明と実物のギャップを指摘する声が急増","textReviewed":true}}')
case "$ec_contra" in *'"hasContradiction"'*) echo "  PASS: EC ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: EC ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ レイアウト（配置提案・モックはグリッド配置）
ec_layout=$(curl -s -X POST "$BASE_URL/ai/suggest-layout" -H 'Content-Type: application/json' \
  -d "{\"doc\":$EC_DOC}")
case "$ec_layout" in *'"transform"'*'"cards"'*) echo "  PASS: EC ④レイアウト"; PASS=$((PASS+1));; *) echo "  FAIL: EC ④レイアウト"; FAIL=$((FAIL+1));; esac

# ⑤ ナラティブ
ec_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$EC_DOC}")
case "$ec_narr" in *'"basedOnReadingOrder":["ec-i"]'*) echo "  PASS: EC ⑤ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: EC ⑤ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
ec_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$EC_ID")
check "EC 読戻し (200)" "200" "$ec_read"

echo ""
echo "--- シナリオ51: ゲーム・エンタメ運営のプレイヤー声整理（バグ/要望分離と修正優先の反対視点） ---"
# 業態: ゲーム・エンタメ（オンラインゲーム運営）
# 想定人物: ゲーム運営プロデューサー（プレイヤー声の整理と修正優先判断）
# 業務領域: プレイヤーのバグ報告・要望・不満のKJ分類と、修正優先の判断材料
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> 反対視点提案(propose-opposing-viewpoint)
#          -> ナラティブ(generate-narrative) -> 読戻し
# 注意事項: バグ報告と要望・不満を混在させず分離する。修正優先への反対視点（既存
#          機能の安定性）を proposal-only で提案し、人間が採否する（AIは先取りしない）。
GM_ID="biz-flow-game"
GM_DOC='{"version":1,"id":"'$GM_ID'","title":"プレイヤー声整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"gm1","text":"サーバー遅延でログインできない報告が多い","x":0,"y":0,"textReviewed":true},{"id":"gm2","text":"新マップ追加を望む声がある","x":10,"y":0,"textReviewed":true},{"id":"gm3","text":"既存機能の安定性を優先すべきとの意見","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"gm-i","cardIds":["gm1","gm2","gm3"]}],"readingOrder":["gm-i"]}'

gm_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$GM_ID" \
  -H 'Content-Type: application/json' -d "$GM_DOC")
check "GM PUT document (作成)" "200" "$gm_put"

# ① AI束ね
gm_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"gm1","text":"サーバー遅延でログインできない報告が多い","textReviewed":true},{"id":"gm2","text":"新マップ追加を望む声がある","textReviewed":true},{"id":"gm3","text":"既存機能の安定性を優先すべきとの意見","textReviewed":true}]}')
case "$gm_groups" in *'"groups":'*) echo "  PASS: GM ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: GM ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
gm_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$GM_DOC,\"islandId\":\"gm-i\"}")
case "$gm_summary" in *'"groundingIds":["gm1","gm2","gm3"]'*) echo "  PASS: GM ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: GM ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（バグ修正優先 vs 既存安定優先・修正判断の相克）
gm_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"gm1","text":"サーバー遅延でログインできない報告が多い","textReviewed":true},"cardB":{"id":"gm3","text":"既存機能の安定性を優先すべきとの意見","textReviewed":true}}')
case "$gm_contra" in *'"hasContradiction"'*) echo "  PASS: GM ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: GM ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ 反対視点提案（新マップ要望への反対視点・proposal-only境界）
gm_oppose=$(curl -s -X POST "$BASE_URL/ai/proposals/opposing-viewpoint" -H 'Content-Type: application/json' \
  -d "{\"doc\":$GM_DOC,\"targetCardId\":\"gm2\"}")
case "$gm_oppose" in
  *'"status":"proposed"'*'"reviewState":"unreviewed"'*) echo "  PASS: GM ④反対視点提案(proposal-only)"; PASS=$((PASS+1));;
  *) echo "  FAIL: GM ④反対視点提案(proposal-only)"; FAIL=$((FAIL+1));; esac

# ⑤ ナラティブ
gm_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$GM_DOC}")
case "$gm_narr" in *'"basedOnReadingOrder":["gm-i"]'*) echo "  PASS: GM ⑤ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: GM ⑤ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
gm_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$GM_ID")
check "GM 読戻し (200)" "200" "$gm_read"

echo ""
echo "--- シナリオ52: 介護施設のヒヤリハット報告のKJ分析（A/B照合で取りこぼし防止） ---"
# 業態: 介護・ヘルスケア（介護施設運営）
# 想定人物: 介護施設の安全管理者（インシデント報告を整理）
# 業務領域: ヒヤリハット（事故寸前）報告のKJ分類と、重大事故化の防止
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> A/B照合(check-narrative) -> 読戻し
# 注意事項: ヒヤリハット報告は逐語で保持（報告者の意図を変えない）。ナラティブが
#          重要な報告を取りこぼしていないかを A/B照合（KJ-AB-CROSS-CHECK-01）で確認。
HH_ID="biz-flow-care"
HH_DOC='{"version":1,"id":"'$HH_ID'","title":"ヒヤリハット報告分析","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"hh1","text":"転倒の報告が今月増えている","x":0,"y":0,"textReviewed":true},{"id":"hh2","text":"夜間帯にベッドからの転落が発生しやすい","x":10,"y":0,"textReviewed":true},{"id":"hh3","text":"軽微な事例は記録されない傾向がある","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"hh-i","cardIds":["hh1","hh2","hh3"]}],"readingOrder":["hh-i"]}'

hh_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$HH_ID" \
  -H 'Content-Type: application/json' -d "$HH_DOC")
check "HH PUT document (作成)" "200" "$hh_put"

# ① AI束ね
hh_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"hh1","text":"転倒の報告が今月増えている","textReviewed":true},{"id":"hh2","text":"夜間帯にベッドからの転落が発生しやすい","textReviewed":true},{"id":"hh3","text":"軽微な事例は記録されない傾向がある","textReviewed":true}]}')
case "$hh_groups" in *'"groups":'*) echo "  PASS: HH ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: HH ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
hh_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$HH_DOC,\"islandId\":\"hh-i\"}")
case "$hh_summary" in *'"groundingIds":["hh1","hh2","hh3"]'*) echo "  PASS: HH ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: HH ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（転倒報告の増加 vs 軽微事例の未記録・記録体制の相克）
hh_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"hh1","text":"転倒の報告が今月増えている","textReviewed":true},"cardB":{"id":"hh3","text":"軽微な事例は記録されない傾向がある","textReviewed":true}}')
case "$hh_contra" in *'"hasContradiction"'*) echo "  PASS: HH ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: HH ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
hh_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$HH_DOC}")
case "$hh_narr" in *'"basedOnReadingOrder":["hh-i"]'*) echo "  PASS: HH ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: HH ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ A/B照合（check-narrative・ナラティブが重要報告を取りこぼさない）
HH_NARR_TEXT="（草稿）転倒報告が増えており、夜間帯のベッド転落が一因とみられる。軽微な事例の記録漏れが課題である。"
hh_check=$(curl -s -X POST "$BASE_URL/ai/check-narrative" -H 'Content-Type: application/json' \
  -d "{\"doc\":$HH_DOC,\"narrativeText\":\"$HH_NARR_TEXT\",\"basedOnReadingOrder\":[\"hh-i\"]}")
case "$hh_check" in
  *'"issues":[]'*) echo "  PASS: HH ⑤A/B照合(取りこぼしなし)"; PASS=$((PASS+1));;
  *) echo "  FAIL: HH ⑤A/B照合(取りこぼしなし)"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
hh_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$HH_ID")
check "HH 読戻し (200)" "200" "$hh_read"

echo ""
echo "--- シナリオ53: 交通・インフラの運行トラブル分析（複合要因の表面化と矮小化への反対視点） ---"
# 業態: 交通・インフラ（公共交通・鉄道/バス運営）
# 想定人物: 運行管理担当（ダイヤ乱れの原因整理と再発防止）
# 業務領域: 運行トラブル（遅延・運休）のKJ整理と、複合要因の表面化
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> 反対視点提案(propose-opposing-viewpoint)
#          -> ナラティブ(generate-narrative) -> 読戻し
# 注意事項: 運行トラブルの原因を単一に矮小化しない（信号・気象・点検の複合要因を
#          表面化）。単一原因への反対視点を proposal-only で提案し、人間が判断。
TR_ID="biz-flow-transit"
TR_DOC='{"version":1,"id":"'$TR_ID'","title":"運行トラブル分析","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"tr1","text":"信号故障が主因と発表された","x":0,"y":0,"textReviewed":true},{"id":"tr2","text":"強風と大雨が重なった時間帯に遅延が集中した","x":10,"y":0,"textReviewed":true},{"id":"tr3","text":"乗客報告で車両点検の遅れが指摘された","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"tr-i","cardIds":["tr1","tr2","tr3"]}],"readingOrder":["tr-i"]}'

tr_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$TR_ID" \
  -H 'Content-Type: application/json' -d "$TR_DOC")
check "TR PUT document (作成)" "200" "$tr_put"

# ① AI束ね
tr_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"tr1","text":"信号故障が主因と発表された","textReviewed":true},{"id":"tr2","text":"強風と大雨が重なった時間帯に遅延が集中した","textReviewed":true},{"id":"tr3","text":"乗客報告で車両点検の遅れが指摘された","textReviewed":true}]}')
case "$tr_groups" in *'"groups":'*) echo "  PASS: TR ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: TR ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
tr_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$TR_DOC,\"islandId\":\"tr-i\"}")
case "$tr_summary" in *'"groundingIds":["tr1","tr2","tr3"]'*) echo "  PASS: TR ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: TR ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（単一原因 vs 複合要因・矮小化の防止）
tr_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"tr1","text":"信号故障が主因と発表された","textReviewed":true},"cardB":{"id":"tr2","text":"強風と大雨が重なった時間帯に遅延が集中した","textReviewed":true}}')
case "$tr_contra" in *'"hasContradiction"'*) echo "  PASS: TR ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: TR ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ 反対視点提案（単一原因発表への反対視点・複合要因の指摘・proposal-only）
tr_oppose=$(curl -s -X POST "$BASE_URL/ai/proposals/opposing-viewpoint" -H 'Content-Type: application/json' \
  -d "{\"doc\":$TR_DOC,\"targetCardId\":\"tr1\"}")
case "$tr_oppose" in
  *'"status":"proposed"'*'"reviewState":"unreviewed"'*) echo "  PASS: TR ④反対視点提案(proposal-only)"; PASS=$((PASS+1));;
  *) echo "  FAIL: TR ④反対視点提案(proposal-only)"; FAIL=$((FAIL+1));; esac

# ⑤ ナラティブ
tr_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$TR_DOC}")
case "$tr_narr" in *'"basedOnReadingOrder":["tr-i"]'*) echo "  PASS: TR ⑤ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: TR ⑤ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
tr_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$TR_ID")
check "TR 読戻し (200)" "200" "$tr_read"

echo ""
echo "--- シナリオ54: ファッション・アパレルのトレンド分析（イノベーターの少数先行シグナル） ---"
# 業態: ファッション・アパレル（ブランド運営）
# 想定人物: ブランド企画担当（トレンドを読み取る）
# 業務領域: 顧客声・バイヤー意見のKJ分類と、次シーズンの方向性
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> タイトル提案(suggest-document-title) -> 読戻し
# 注意事項: トレンド先行者（イノベーター）の少数の声と多数の後追いの声を区別し、
#          少数の先行シグナルを矛盾検出で表面化（V2・少数意見の外在化がトレンド検出の鍵）。
#          タイトル候補は proposal（自動確定しない）。
FS_ID="biz-flow-fashion"
FS_DOC='{"version":1,"id":"'$FS_ID'","title":"トレンド分析（仮）","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"fs1","text":"少数の先行購入者が生地の質感の変化を指摘","x":0,"y":0,"textReviewed":true},{"id":"fs2","text":"売れ筋は定番のベーシックアイテムが大半","x":10,"y":0,"textReviewed":true},{"id":"fs3","text":"SNSでビンテージ調スタイルへの関心が高まり始めている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"fs-i","cardIds":["fs1","fs2","fs3"]}],"readingOrder":["fs-i"]}'

fs_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$FS_ID" \
  -H 'Content-Type: application/json' -d "$FS_DOC")
check "FS PUT document (作成)" "200" "$fs_put"

# ① AI束ね
fs_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"fs1","text":"少数の先行購入者が生地の質感の変化を指摘","textReviewed":true},{"id":"fs2","text":"売れ筋は定番のベーシックアイテムが大半","textReviewed":true},{"id":"fs3","text":"SNSでビンテージ調スタイルへの関心が高まり始めている","textReviewed":true}]}')
case "$fs_groups" in *'"groups":'*) echo "  PASS: FS ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: FS ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
fs_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$FS_DOC,\"islandId\":\"fs-i\"}")
case "$fs_summary" in *'"groundingIds":["fs1","fs2","fs3"]'*) echo "  PASS: FS ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: FS ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（少数先行シグナル vs 多数後追い・イノベーターの声の表面化）
fs_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"fs1","text":"少数の先行購入者が生地の質感の変化を指摘","textReviewed":true},"cardB":{"id":"fs2","text":"売れ筋は定番のベーシックアイテムが大半","textReviewed":true}}')
case "$fs_contra" in *'"hasContradiction"'*) echo "  PASS: FS ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: FS ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
fs_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$FS_DOC}")
case "$fs_narr" in *'"basedOnReadingOrder":["fs-i"]'*) echo "  PASS: FS ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: FS ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ タイトル提案（分析レポートのタイトル候補・proposalで自動確定しない）
fs_title=$(curl -s -X POST "$BASE_URL/ai/suggest-document-title" -H 'Content-Type: application/json' \
  -d '{"islandTitles":["トレンド動向"],"cardTexts":["少数の先行購入者が生地の質感の変化を指摘","売れ筋は定番のベーシックアイテムが大半","SNSでビンテージ調スタイルへの関心が高まり始めている"],"currentTitle":"トレンド分析（仮）","textReviewed":true}')
case "$fs_title" in *'"candidates"'*) echo "  PASS: FS ⑤タイトル提案"; PASS=$((PASS+1));; *) echo "  FAIL: FS ⑤タイトル提案"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
fs_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$FS_ID")
check "FS 読戻し (200)" "200" "$fs_read"

echo ""
echo "--- シナリオ55: NGO・国際協力の人道支援ニーズ整理（発言力の非対称性の表面化） ---"
# 業態: NGO・国際協力（人道支援）
# 想定人物: 支援調整員（被災地・コミュニティのニーズを整理）
# 業務領域: 支援ニーズのKJ分類と、支援優先の判断（リソース配分）
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 声の大きい主体（大口ドナー）と声の小さな受益者のニーズを区別し、
#          発言力の非対称性を矛盾検出で表面化（少数意見の外在化・V2）。支援計画は
#          受益者視点を欠落させない。
NG_ID="biz-flow-ngo"
NG_DOC='{"version":1,"id":"'$NG_ID'","title":"支援ニーズ整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"ng1","text":"大口ドナーの要望が支援計画に強く反映されている","x":0,"y":0,"textReviewed":true},{"id":"ng2","text":"現地の小規模コミュニティは安全な水へのニーズを訴えている","x":10,"y":0,"textReviewed":true},{"id":"ng3","text":"物流コストの高騰で支援物資の到達が遅れている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"ng-i","cardIds":["ng1","ng2","ng3"]}],"readingOrder":["ng-i"]}'

ng_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$NG_ID" \
  -H 'Content-Type: application/json' -d "$NG_DOC")
check "NG PUT document (作成)" "200" "$ng_put"

# ① AI束ね
ng_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"ng1","text":"大口ドナーの要望が支援計画に強く反映されている","textReviewed":true},{"id":"ng2","text":"現地の小規模コミュニティは安全な水へのニーズを訴えている","textReviewed":true},{"id":"ng3","text":"物流コストの高騰で支援物資の到達が遅れている","textReviewed":true}]}')
case "$ng_groups" in *'"groups":'*) echo "  PASS: NG ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: NG ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
ng_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$NG_DOC,\"islandId\":\"ng-i\"}")
case "$ng_summary" in *'"groundingIds":["ng1","ng2","ng3"]'*) echo "  PASS: NG ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: NG ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（大口ドナー優先 vs 声の小さな受益者のニーズ・発言力の非対称性）
ng_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"ng1","text":"大口ドナーの要望が支援計画に強く反映されている","textReviewed":true},"cardB":{"id":"ng2","text":"現地の小規模コミュニティは安全な水へのニーズを訴えている","textReviewed":true}}')
case "$ng_contra" in *'"hasContradiction"'*) echo "  PASS: NG ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: NG ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
ng_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$NG_DOC}")
case "$ng_narr" in *'"basedOnReadingOrder":["ng-i"]'*) echo "  PASS: NG ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: NG ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
ng_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$NG_ID")
check "NG 読戻し (200)" "200" "$ng_read"

echo ""
echo "--- シナリオ56: 自治体・行政窓口の市民問い合わせ整理（頻出/ロングテールの島分離） ---"
# 業態: 自治体・行政（市民窓口）
# 想定人物: 窓口サービス改善担当
# 業務領域: 市民からの問い合わせのKJ分類と、FAQ・窓口改善の根拠
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 島間関係要約(summarize-island-relation) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 頻出問い合わせ（手続き案内の分かりにくさ）とロングテール問い合わせ
#          （個別の複合事情）を島として分離し、島間関係を整理して改善の全体像を見る。
CM_ID="biz-flow-citizen"
CM_DOC='{"version":1,"id":"'$CM_ID'","title":"市民問い合わせ整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"cm1","text":"住民票の取得手続きの案内が分かりにくい","x":0,"y":0,"textReviewed":true},{"id":"cm2","text":"窓口が混雑していて待ち時間が長い","x":10,"y":0,"textReviewed":true},{"id":"cm3","text":"相続に伴う手続きが複数絡み合って分からない","x":20,"y":0,"textReviewed":true},{"id":"cm4","text":"引っ越しに伴う住所変更の一括手続きを知りたい","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"cm-1","cardIds":["cm1","cm2"]},{"id":"cm-2","cardIds":["cm3","cm4"]}],"readingOrder":["cm-1","cm-2"]}'

cm_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$CM_ID" \
  -H 'Content-Type: application/json' -d "$CM_DOC")
check "CM PUT document (作成)" "200" "$cm_put"

# ① AI束ね
cm_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"cm1","text":"住民票の取得手続きの案内が分かりにくい","textReviewed":true},{"id":"cm2","text":"窓口が混雑していて待ち時間が長い","textReviewed":true},{"id":"cm3","text":"相続に伴う手続きが複数絡み合って分からない","textReviewed":true},{"id":"cm4","text":"引っ越しに伴う住所変更の一括手続きを知りたい","textReviewed":true}]}')
case "$cm_groups" in *'"groups":'*) echo "  PASS: CM ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: CM ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約（頻出問い合わせの島）
cm_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$CM_DOC,\"islandId\":\"cm-1\"}")
case "$cm_summary" in *'"groundingIds":["cm1","cm2"]'*) echo "  PASS: CM ②島要約(頻出)"; PASS=$((PASS+1));; *) echo "  FAIL: CM ②島要約(頻出)"; FAIL=$((FAIL+1));; esac

# ③ 島間関係要約（頻出 vs ロングテール・改善の全体像）
cm_relation=$(curl -s -X POST "$BASE_URL/ai/summarize-island-relation" -H 'Content-Type: application/json' \
  -d "{\"doc\":$CM_DOC,\"islandAId\":\"cm-1\",\"islandBId\":\"cm-2\",\"relationType\":\"causal\",\"derived\":false,\"groundingCardIds\":[\"cm3\"],\"groundingEdgeIds\":[],\"cardTexts\":[{\"id\":\"cm3\",\"text\":\"相続に伴う手続きが複数絡み合って分からない\"}]}")
case "$cm_relation" in
  *'"text"'*'"warnings":[]'*) echo "  PASS: CM ③島間関係要約"; PASS=$((PASS+1));;
  *) echo "  FAIL: CM ③島間関係要約"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
cm_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$CM_DOC}")
case "$cm_narr" in *'"basedOnReadingOrder":["cm-1","cm-2"]'*) echo "  PASS: CM ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: CM ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
cm_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$CM_ID")
check "CM 読戻し (200)" "200" "$cm_read"

echo ""
echo "--- シナリオ57: スポーツチーム運営のファン声分析（勝敗と独立した体験の声と統合提案） ---"
# 業態: スポーツ・チーム運営（プロスポーツクラブ）
# 想定人物: マーケティング責任者（ファンエンゲージメントを分析）
# 業務領域: ファンからの声（満足・不満・要望）のKJ分類と、エンゲージメント施策の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> 統合提案(suggest-merges)
#          -> ナラティブ(generate-narrative) -> 読戻し
# 注意事項: 重複するファンの要望を統合提案で整理（人間が採否・自動適用しない）。
#          試合結果（勝敗）に左右されないスタジアム体験の声を矛盾検出で表面化。
SP_ID="biz-flow-sports"
SP_DOC='{"version":1,"id":"'$SP_ID'","title":"ファン声分析","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"sp1","text":"試合に勝ってもスタジアムの混雑が不満","x":0,"y":0,"textReviewed":true},{"id":"sp2","text":"チケットの再販システムを導入してほしい","x":10,"y":0,"textReviewed":true},{"id":"sp3","text":"試合に負けたときの雰囲気が沈むのは仕方ない","x":20,"y":0,"textReviewed":true},{"id":"sp4","text":"スタジアムの案内表示が分かりにくい","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"sp-i","cardIds":["sp1","sp2","sp3","sp4"]}],"readingOrder":["sp-i"]}'

sp_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$SP_ID" \
  -H 'Content-Type: application/json' -d "$SP_DOC")
check "SP PUT document (作成)" "200" "$sp_put"

# ① AI束ね
sp_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"sp1","text":"試合に勝ってもスタジアムの混雑が不満","textReviewed":true},{"id":"sp2","text":"チケットの再販システムを導入してほしい","textReviewed":true},{"id":"sp3","text":"試合に負けたときの雰囲気が沈むのは仕方ない","textReviewed":true},{"id":"sp4","text":"スタジアムの案内表示が分かりにくい","textReviewed":true}]}')
case "$sp_groups" in *'"groups":'*) echo "  PASS: SP ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: SP ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
sp_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$SP_DOC,\"islandId\":\"sp-i\"}")
case "$sp_summary" in *'"groundingIds":["sp1","sp2","sp3","sp4"]'*) echo "  PASS: SP ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: SP ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（勝敗と独立した体験の不満 vs 勝敗依存の許容）
sp_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"sp1","text":"試合に勝ってもスタジアムの混雑が不満","textReviewed":true},"cardB":{"id":"sp3","text":"試合に負けたときの雰囲気が沈むのは仕方ない","textReviewed":true}}')
case "$sp_contra" in *'"hasContradiction"'*) echo "  PASS: SP ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: SP ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ 統合提案（重複する要望の整理・人間が採否）
sp_merges=$(curl -s -X POST "$BASE_URL/ai/suggest-merges" -H 'Content-Type: application/json' \
  -d "{\"doc\":$SP_DOC}")
case "$sp_merges" in *'"suggestions"'*) echo "  PASS: SP ④統合提案(merges)"; PASS=$((PASS+1));; *) echo "  FAIL: SP ④統合提案(merges)"; FAIL=$((FAIL+1));; esac

# ⑤ ナラティブ
sp_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$SP_DOC}")
case "$sp_narr" in *'"basedOnReadingOrder":["sp-i"]'*) echo "  PASS: SP ⑤ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: SP ⑤ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
sp_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$SP_ID")
check "SP 読戻し (200)" "200" "$sp_read"

echo ""
echo "--- シナリオ58: ソフトウェア開発チームのスプリント振り返り（個人の声と全体の認識の乖離） ---"
# 業態: IT・ソフトウェア開発（開発チーム）
# 想定人物: スクラムマスター／開発チームリーダー（スプリント振り返り）
# 業務領域: スプリントの振り返り（良かった点・課題）のKJ整理と、改善アクションの検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 個人の懸念（コードレビューの形式化など・心理的安全性）とチーム全体の
#          認識（計画通り）の乖離を矛盾検出で表面化（少数意見の外在化・V2）。
SW_ID="biz-flow-sprint"
SW_DOC='{"version":1,"id":"'$SW_ID'","title":"スプリント振り返り","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"sw1","text":"スプリントは計画通りに進んでいる","x":0,"y":0,"textReviewed":true},{"id":"sw2","text":"コードレビューが形式的で品質が下がっていると感じる","x":10,"y":0,"textReviewed":true},{"id":"sw3","text":"デプロイ後に不具合が増えた","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"sw-i","cardIds":["sw1","sw2","sw3"]}],"readingOrder":["sw-i"]}'

sw_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$SW_ID" \
  -H 'Content-Type: application/json' -d "$SW_DOC")
check "SW PUT document (作成)" "200" "$sw_put"

# ① AI束ね
sw_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"sw1","text":"スプリントは計画通りに進んでいる","textReviewed":true},{"id":"sw2","text":"コードレビューが形式的で品質が下がっていると感じる","textReviewed":true},{"id":"sw3","text":"デプロイ後に不具合が増えた","textReviewed":true}]}')
case "$sw_groups" in *'"groups":'*) echo "  PASS: SW ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: SW ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
sw_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$SW_DOC,\"islandId\":\"sw-i\"}")
case "$sw_summary" in *'"groundingIds":["sw1","sw2","sw3"]'*) echo "  PASS: SW ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: SW ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（チーム全体の認識 vs 個人の懸念・心理的安全性）
sw_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"sw1","text":"スプリントは計画通りに進んでいる","textReviewed":true},"cardB":{"id":"sw2","text":"コードレビューが形式的で品質が下がっていると感じる","textReviewed":true}}')
case "$sw_contra" in *'"hasContradiction"'*) echo "  PASS: SW ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: SW ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
sw_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$SW_DOC}")
case "$sw_narr" in *'"basedOnReadingOrder":["sw-i"]'*) echo "  PASS: SW ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: SW ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
sw_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$SW_ID")
check "SW 読戻し (200)" "200" "$sw_read"

echo ""
echo "--- シナリオ59: 言語サービス・翻訳レビューの用語一貫性管理 ---"
# 業態: 言語サービス（翻訳・ローカライゼーション）
# 想定人物: 翻訳レビュアー（品質管理）
# 業務領域: 翻訳レビューコメントのKJ整理と、用語・文体の一貫性確認
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 用語の揺れ（表記不統一）を矛盾検出で表面化し、用語集（グロッサリー）の
#          統一根拠にする。原文の意図は逐語で保持する（翻訳で変えない）。
TRL_ID="biz-flow-translation"
TRL_DOC='{"version":1,"id":"'$TRL_ID'","title":"翻訳レビュー整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"t1","text":"製品マニュアルの訳語が担当者ごとに異なる","x":0,"y":0,"textReviewed":true},{"id":"t2","text":"公開文書の用語は用語集で統一されている","x":10,"y":0,"textReviewed":true},{"id":"t3","text":"新規製品の用語追加が用語集に反映されていない","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"tr-i","cardIds":["t1","t2","t3"]}],"readingOrder":["tr-i"]}'

trl_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$TRL_ID" \
  -H 'Content-Type: application/json' -d "$TRL_DOC")
check "TRL PUT document (作成)" "200" "$trl_put"

# ① AI束ね
trl_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"t1","text":"製品マニュアルの訳語が担当者ごとに異なる","textReviewed":true},{"id":"t2","text":"公開文書の用語は用語集で統一されている","textReviewed":true},{"id":"t3","text":"新規製品の用語追加が用語集に反映されていない","textReviewed":true}]}')
case "$trl_groups" in *'"groups":'*) echo "  PASS: TRL ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: TRL ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
trl_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$TRL_DOC,\"islandId\":\"tr-i\"}")
case "$trl_summary" in *'"groundingIds":["t1","t2","t3"]'*) echo "  PASS: TRL ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: TRL ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（内部マニュアルの訳語の揺れ vs 公開文書の統一・品質管理の相克）
trl_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"t1","text":"製品マニュアルの訳語が担当者ごとに異なる","textReviewed":true},"cardB":{"id":"t2","text":"公開文書の用語は用語集で統一されている","textReviewed":true}}')
case "$trl_contra" in *'"hasContradiction"'*) echo "  PASS: TRL ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: TRL ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
trl_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$TRL_DOC}")
case "$trl_narr" in *'"basedOnReadingOrder":["tr-i"]'*) echo "  PASS: TRL ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: TRL ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
trl_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$TRL_ID")
check "TRL 読戻し (200)" "200" "$trl_read"

echo ""
echo "--- シナリオ60: 自動車・モビリティの新型車ユーザー評価整理（世代間乖離と共通課題の分離） ---"
# 業態: 自動車・モビリティ（自動車メーカー）
# 想定人物: 商品企画担当（ユーザー評価を整理）
# 業務領域: 新型車のユーザー評価・市場フィードバックのKJ分類と、改良ポイントの検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 年齢・地域による評価の偏り（世代間の評価乖離）と、全世代に共通する
#          課題を区別し、改良の優先度を決める（セグメントと共通課題の分離）。
AU_ID="biz-flow-auto"
AU_DOC='{"version":1,"id":"'$AU_ID'","title":"新型車ユーザー評価","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"au1","text":"若年層はデジタル機能を評価している","x":0,"y":0,"textReviewed":true},{"id":"au2","text":"高齢層は操作が複雑と感じている","x":10,"y":0,"textReviewed":true},{"id":"au3","text":"燃費性能の不満が全世代に共通している","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"au-i","cardIds":["au1","au2","au3"]}],"readingOrder":["au-i"]}'

au_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$AU_ID" \
  -H 'Content-Type: application/json' -d "$AU_DOC")
check "AU PUT document (作成)" "200" "$au_put"

# ① AI束ね
au_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"au1","text":"若年層はデジタル機能を評価している","textReviewed":true},{"id":"au2","text":"高齢層は操作が複雑と感じている","textReviewed":true},{"id":"au3","text":"燃費性能の不満が全世代に共通している","textReviewed":true}]}')
case "$au_groups" in *'"groups":'*) echo "  PASS: AU ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: AU ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
au_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$AU_DOC,\"islandId\":\"au-i\"}")
case "$au_summary" in *'"groundingIds":["au1","au2","au3"]'*) echo "  PASS: AU ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: AU ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（世代間の評価乖離・デジタル機能 vs 操作複雑）
au_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"au1","text":"若年層はデジタル機能を評価している","textReviewed":true},"cardB":{"id":"au2","text":"高齢層は操作が複雑と感じている","textReviewed":true}}')
case "$au_contra" in *'"hasContradiction"'*) echo "  PASS: AU ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: AU ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
au_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$AU_DOC}")
case "$au_narr" in *'"basedOnReadingOrder":["au-i"]'*) echo "  PASS: AU ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: AU ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
au_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$AU_ID")
check "AU 読戻し (200)" "200" "$au_read"

echo ""
echo "--- シナリオ61: 美容・ヘルスケアの顧客フィードバック整理（主観評価と客観指標の乖離） ---"
# 業態: 美容・ヘルスケア（美容サロン運営）
# 想定人物: サロン店長（顧客フィードバックを整理）
# 業務領域: 施術満足・スタッフ対応・価格への顧客声のKJ分類と、サービス改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 施術効果の主観評価（満足度）と客観指標（再来店率）の乖離を矛盾検出で
#          表面化し、改善の根拠にする（主観と行動のギャップ）。
BE_ID="biz-flow-beauty"
BE_DOC='{"version":1,"id":"'$BE_ID'","title":"顧客フィードバック整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"be1","text":"施術満足度は高いという声が多い","x":0,"y":0,"textReviewed":true},{"id":"be2","text":"再来店率は横ばい","x":10,"y":0,"textReviewed":true},{"id":"be3","text":"価格が高いとの声が一部にある","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"be-i","cardIds":["be1","be2","be3"]}],"readingOrder":["be-i"]}'

be_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$BE_ID" \
  -H 'Content-Type: application/json' -d "$BE_DOC")
check "BE PUT document (作成)" "200" "$be_put"

# ① AI束ね
be_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"be1","text":"施術満足度は高いという声が多い","textReviewed":true},{"id":"be2","text":"再来店率は横ばい","textReviewed":true},{"id":"be3","text":"価格が高いとの声が一部にある","textReviewed":true}]}')
case "$be_groups" in *'"groups":'*) echo "  PASS: BE ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: BE ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
be_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$BE_DOC,\"islandId\":\"be-i\"}")
case "$be_summary" in *'"groundingIds":["be1","be2","be3"]'*) echo "  PASS: BE ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: BE ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（主観満足 vs 再来店率横ばい・主観と行動のギャップ）
be_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"be1","text":"施術満足度は高いという声が多い","textReviewed":true},"cardB":{"id":"be2","text":"再来店率は横ばい","textReviewed":true}}')
case "$be_contra" in *'"hasContradiction"'*) echo "  PASS: BE ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: BE ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
be_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$BE_DOC}")
case "$be_narr" in *'"basedOnReadingOrder":["be-i"]'*) echo "  PASS: BE ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: BE ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
be_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$BE_ID")
check "BE 読戻し (200)" "200" "$be_read"

echo ""
echo "--- シナリオ62: セキュリティ・SOCのインシデント対応振り返り（封じ込めと証拠保全の相克） ---"
# 業態: セキュリティ・SOC（セキュリティ運用センター）
# 想定人物: セキュリティアナリスト（インシデント対応の振り返り）
# 業務領域: セキュリティインシデント対応の記録整理と、再発防止の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: インシデント対応では封じ込め（即時遮断）と証拠保全（調査継続）の相克を
#          矛盾検出で表面化し、判断の根拠を残す。タイムライン記録の欠落も指摘。
CY_ID="biz-flow-soc"
CY_DOC='{"version":1,"id":"'$CY_ID'","title":"インシデント対応振り返り","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"cy1","text":"被害拡大を防ぐため即時遮断を主張する声","x":0,"y":0,"textReviewed":true},{"id":"cy2","text":"証拠保全のため調査を続けるべきとの意見","x":10,"y":0,"textReviewed":true},{"id":"cy3","text":"初動のタイムライン記録に欠落がある","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"cy-i","cardIds":["cy1","cy2","cy3"]}],"readingOrder":["cy-i"]}'

cy_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$CY_ID" \
  -H 'Content-Type: application/json' -d "$CY_DOC")
check "CY PUT document (作成)" "200" "$cy_put"

# ① AI束ね
cy_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"cy1","text":"被害拡大を防ぐため即時遮断を主張する声","textReviewed":true},{"id":"cy2","text":"証拠保全のため調査を続けるべきとの意見","textReviewed":true},{"id":"cy3","text":"初動のタイムライン記録に欠落がある","textReviewed":true}]}')
case "$cy_groups" in *'"groups":'*) echo "  PASS: CY ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: CY ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
cy_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$CY_DOC,\"islandId\":\"cy-i\"}")
case "$cy_summary" in *'"groundingIds":["cy1","cy2","cy3"]'*) echo "  PASS: CY ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: CY ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（封じ込め vs 証拠保全・対応判断の相克）
cy_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"cy1","text":"被害拡大を防ぐため即時遮断を主張する声","textReviewed":true},"cardB":{"id":"cy2","text":"証拠保全のため調査を続けるべきとの意見","textReviewed":true}}')
case "$cy_contra" in *'"hasContradiction"'*) echo "  PASS: CY ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: CY ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
cy_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$CY_DOC}")
case "$cy_narr" in *'"basedOnReadingOrder":["cy-i"]'*) echo "  PASS: CY ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: CY ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
cy_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$CY_ID")
check "CY 読戻し (200)" "200" "$cy_read"

echo ""
echo "--- シナリオ63: オンラインコミュニティ運営（発言の自由度と健全性のバランス） ---"
# 業態: オンラインコミュニティ運営
# 想定人物: コミュニティマネージャー（運営フィードバックを整理）
# 業務領域: メンバーからの運営フィードバックのKJ分類と、運営ポリシー改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 発言の自由度（少数意見の保護）と健全性（荒らし対策）のバランスを
#          矛盾検出で表面化し、運営ポリシーの根拠にする（少数意見の外在化・V2）。
COM_ID="biz-flow-community"
COM_DOC='{"version":1,"id":"'$COM_ID'","title":"コミュニティ運営フィードバック","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"co1","text":"少数の批判的な声も削除せず残すべき","x":0,"y":0,"textReviewed":true},{"id":"co2","text":"荒らしや誹謗中傷は即時削除すべき","x":10,"y":0,"textReviewed":true},{"id":"co3","text":"運営ルールが複雑で分かりにくい","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"com-i","cardIds":["co1","co2","co3"]}],"readingOrder":["com-i"]}'

com_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$COM_ID" \
  -H 'Content-Type: application/json' -d "$COM_DOC")
check "COM PUT document (作成)" "200" "$com_put"

# ① AI束ね
com_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"co1","text":"少数の批判的な声も削除せず残すべき","textReviewed":true},{"id":"co2","text":"荒らしや誹謗中傷は即時削除すべき","textReviewed":true},{"id":"co3","text":"運営ルールが複雑で分かりにくい","textReviewed":true}]}')
case "$com_groups" in *'"groups":'*) echo "  PASS: COM ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: COM ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
com_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$COM_DOC,\"islandId\":\"com-i\"}")
case "$com_summary" in *'"groundingIds":["co1","co2","co3"]'*) echo "  PASS: COM ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: COM ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（発言の自由度 vs 健全性・表現とモデレーションのバランス）
com_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"co1","text":"少数の批判的な声も削除せず残すべき","textReviewed":true},"cardB":{"id":"co2","text":"荒らしや誹謗中傷は即時削除すべき","textReviewed":true}}')
case "$com_contra" in *'"hasContradiction"'*) echo "  PASS: COM ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: COM ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
com_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$COM_DOC}")
case "$com_narr" in *'"basedOnReadingOrder":["com-i"]'*) echo "  PASS: COM ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: COM ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
com_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$COM_ID")
check "COM 読戻し (200)" "200" "$com_read"

echo ""
echo "--- シナリオ64: 銀行・資産運用の運用レビュー整理（短期の顧客心理と長期の方針） ---"
# 業態: 銀行・資産運用（プライベートバンク）
# 想定人物: ファイナンシャルアドバイザー（運用レビューを整理）
# 業務領域: 顧客の運用レビュー（リスク・リターン・方針）のKJ分類と、見直し提案
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 短期的な損失への不安（顧客心理）と長期的な運用方針の相克を矛盾検出で
#          表面化し、運用見直しの根拠にする（市場下落時の心理と方針の乖離）。
BK_ID="biz-flow-wealth"
BK_DOC='{"version":1,"id":"'$BK_ID'","title":"運用レビュー整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"bk1","text":"市場下落で損失が出ており、不安を訴える声","x":0,"y":0,"textReviewed":true},{"id":"bk2","text":"長期運用方針は変えずに保有を継続すべきとの意見","x":10,"y":0,"textReviewed":true},{"id":"bk3","text":"リスク許容度の見直しが必要との指摘","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"bk-i","cardIds":["bk1","bk2","bk3"]}],"readingOrder":["bk-i"]}'

bk_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$BK_ID" \
  -H 'Content-Type: application/json' -d "$BK_DOC")
check "BK PUT document (作成)" "200" "$bk_put"

# ① AI束ね
bk_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"bk1","text":"市場下落で損失が出ており、不安を訴える声","textReviewed":true},{"id":"bk2","text":"長期運用方針は変えずに保有を継続すべきとの意見","textReviewed":true},{"id":"bk3","text":"リスク許容度の見直しが必要との指摘","textReviewed":true}]}')
case "$bk_groups" in *'"groups":'*) echo "  PASS: BK ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: BK ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
bk_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$BK_DOC,\"islandId\":\"bk-i\"}")
case "$bk_summary" in *'"groundingIds":["bk1","bk2","bk3"]'*) echo "  PASS: BK ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: BK ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（短期の損失不安 vs 長期の方針継続・市場下落時の心理と方針の乖離）
bk_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"bk1","text":"市場下落で損失が出ており、不安を訴える声","textReviewed":true},"cardB":{"id":"bk2","text":"長期運用方針は変えずに保有を継続すべきとの意見","textReviewed":true}}')
case "$bk_contra" in *'"hasContradiction"'*) echo "  PASS: BK ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: BK ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
bk_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$BK_DOC}")
case "$bk_narr" in *'"basedOnReadingOrder":["bk-i"]'*) echo "  PASS: BK ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: BK ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
bk_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$BK_ID")
check "BK 読戻し (200)" "200" "$bk_read"

echo ""
echo "--- シナリオ65: 教育・学校運営の保護者アンケート整理（期待と実態の乖離） ---"
# 業態: 教育・学校運営（小中学校）
# 想定人物: 教頭／学校事務（保護者アンケートを整理）
# 業務領域: 保護者からのフィードバック（教育内容・安全・連絡）のKJ分類と、学校運営改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 保護者の期待（教育内容の拡充）と学校の実態（教員負担・リソース）の乖離を
#          矛盾検出で表面化し、運営改善の根拠にする（期待と実態のギャップ）。
SC_ID="biz-flow-school"
SC_DOC='{"version":1,"id":"'$SC_ID'","title":"保護者アンケート整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"sc1","text":"保護者は英語教育の拡充を期待している","x":0,"y":0,"textReviewed":true},{"id":"sc2","text":"教員の負担が増えており現場は疲弊している","x":10,"y":0,"textReviewed":true},{"id":"sc3","text":"安全対策の強化を求める声が強い","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"sc-i","cardIds":["sc1","sc2","sc3"]}],"readingOrder":["sc-i"]}'

sc_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$SC_ID" \
  -H 'Content-Type: application/json' -d "$SC_DOC")
check "SC PUT document (作成)" "200" "$sc_put"

# ① AI束ね
sc_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"sc1","text":"保護者は英語教育の拡充を期待している","textReviewed":true},{"id":"sc2","text":"教員の負担が増えており現場は疲弊している","textReviewed":true},{"id":"sc3","text":"安全対策の強化を求める声が強い","textReviewed":true}]}')
case "$sc_groups" in *'"groups":'*) echo "  PASS: SC ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: SC ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
sc_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$SC_DOC,\"islandId\":\"sc-i\"}")
case "$sc_summary" in *'"groundingIds":["sc1","sc2","sc3"]'*) echo "  PASS: SC ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: SC ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（保護者の期待 vs 教員の負担・期待と実態の乖離）
sc_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"sc1","text":"保護者は英語教育の拡充を期待している","textReviewed":true},"cardB":{"id":"sc2","text":"教員の負担が増えており現場は疲弊している","textReviewed":true}}')
case "$sc_contra" in *'"hasContradiction"'*) echo "  PASS: SC ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: SC ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
sc_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$SC_DOC}")
case "$sc_narr" in *'"basedOnReadingOrder":["sc-i"]'*) echo "  PASS: SC ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: SC ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
sc_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$SC_ID")
check "SC 読戻し (200)" "200" "$sc_read"

echo ""
echo "--- シナリオ66: 建築・不動産開発の完工プロジェクトレビュー（工期と品質のトレードオフ） ---"
# 業態: 建築・不動産開発（デベロッパー）
# 想定人物: プロジェクトマネージャー（完工レビューを整理）
# 業務領域: 完工プロジェクトの振り返り（工程・品質・コスト）のKJ分類と、次プロジェクトの改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 工期短縮（並行施工）と品質確保（手直し防止）のトレードオフを矛盾検出で
#          表面化し、次プロジェクトの改善根拠にする（スケジュールと品質の相克）。
AR_ID="biz-flow-architect"
AR_DOC='{"version":1,"id":"'$AR_ID'","title":"完工プロジェクトレビュー","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"ar1","text":"工期を短縮するために並行施工を増やした","x":0,"y":0,"textReviewed":true},{"id":"ar2","text":"仕上げの手直しが発生し品質に課題が残った","x":10,"y":0,"textReviewed":true},{"id":"ar3","text":"サプライヤーとの調整不足がコスト超過の要因","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"ar-i","cardIds":["ar1","ar2","ar3"]}],"readingOrder":["ar-i"]}'

ar_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$AR_ID" \
  -H 'Content-Type: application/json' -d "$AR_DOC")
check "AR PUT document (作成)" "200" "$ar_put"

# ① AI束ね
ar_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"ar1","text":"工期を短縮するために並行施工を増やした","textReviewed":true},{"id":"ar2","text":"仕上げの手直しが発生し品質に課題が残った","textReviewed":true},{"id":"ar3","text":"サプライヤーとの調整不足がコスト超過の要因","textReviewed":true}]}')
case "$ar_groups" in *'"groups":'*) echo "  PASS: AR ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: AR ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
ar_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$AR_DOC,\"islandId\":\"ar-i\"}")
case "$ar_summary" in *'"groundingIds":["ar1","ar2","ar3"]'*) echo "  PASS: AR ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: AR ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（工期短縮 vs 品質課題・スケジュールと品質の相克）
ar_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"ar1","text":"工期を短縮するために並行施工を増やした","textReviewed":true},"cardB":{"id":"ar2","text":"仕上げの手直しが発生し品質に課題が残った","textReviewed":true}}')
case "$ar_contra" in *'"hasContradiction"'*) echo "  PASS: AR ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: AR ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
ar_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$AR_DOC}")
case "$ar_narr" in *'"basedOnReadingOrder":["ar-i"]'*) echo "  PASS: AR ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: AR ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
ar_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$AR_ID")
check "AR 読戻し (200)" "200" "$ar_read"

echo ""
echo "--- シナリオ67: アグリ・食品製造の品質トレーサビリティ（コストと品質のトレードオフ） ---"
# 業態: 食品製造・アグリフード（加工食品メーカー）
# 想定人物: 品質保証責任者（品質クレームを整理）
# 業務領域: 品質クレーム・原材料トレーサビリティ報告のKJ分類と、再発防止
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: コスト削減（原材料調達の切り替え）と品質保証（トレーサビリティ）の
#          トレードオフを矛盾検出で表面化し、再発防止の根拠にする（調達と品質の相克）。
AG_ID="biz-flow-agrifood"
AG_DOC='{"version":1,"id":"'$AG_ID'","title":"品質クレーム整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"ag1","text":"コスト削減のため原材料の調達先を切り替えた","x":0,"y":0,"textReviewed":true},{"id":"ag2","text":"切り替え後の原材料で品質クレームが発生した","x":10,"y":0,"textReviewed":true},{"id":"ag3","text":"ロットの追跡に時間がかかり原因特定が遅れた","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"ag-i","cardIds":["ag1","ag2","ag3"]}],"readingOrder":["ag-i"]}'

ag_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$AG_ID" \
  -H 'Content-Type: application/json' -d "$AG_DOC")
check "AG PUT document (作成)" "200" "$ag_put"

# ① AI束ね
ag_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"ag1","text":"コスト削減のため原材料の調達先を切り替えた","textReviewed":true},{"id":"ag2","text":"切り替え後の原材料で品質クレームが発生した","textReviewed":true},{"id":"ag3","text":"ロットの追跡に時間がかかり原因特定が遅れた","textReviewed":true}]}')
case "$ag_groups" in *'"groups":'*) echo "  PASS: AG ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: AG ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
ag_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$AG_DOC,\"islandId\":\"ag-i\"}")
case "$ag_summary" in *'"groundingIds":["ag1","ag2","ag3"]'*) echo "  PASS: AG ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: AG ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（調達コスト削減 vs 品質クレーム・調達と品質の相克）
ag_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"ag1","text":"コスト削減のため原材料の調達先を切り替えた","textReviewed":true},"cardB":{"id":"ag2","text":"切り替え後の原材料で品質クレームが発生した","textReviewed":true}}')
case "$ag_contra" in *'"hasContradiction"'*) echo "  PASS: AG ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: AG ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
ag_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$AG_DOC}")
case "$ag_narr" in *'"basedOnReadingOrder":["ag-i"]'*) echo "  PASS: AG ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: AG ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
ag_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$AG_ID")
check "AG 読戻し (200)" "200" "$ag_read"

echo ""
echo "--- シナリオ68: 航空・運輸の旅客サービス改善（定時運航と顧客体験のトレードオフ） ---"
# 業態: 航空・運輸（航空会社）
# 想定人物: 顧客体験マネージャー（旅客フィードバックを整理）
# 業務領域: 旅客からのフィードバック（機内サービス・遅延対応・予約）のKJ分類と、顧客体験改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 定時運航（オペレーション効率）と丁寧な遅延対応（顧客体験）のトレードオフを
#          矛盾検出で表面化し、改善の根拠にする（定時性と顧客体験の相克）。
AV_ID="biz-flow-aviation"
AV_DOC='{"version":1,"id":"'$AV_ID'","title":"旅客サービス改善","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"av1","text":"定時運航の維持を最優先にすべきとの声","x":0,"y":0,"textReviewed":true},{"id":"av2","text":"遅延時の案内が不十分で顧客が不満","x":10,"y":0,"textReviewed":true},{"id":"av3","text":"機内サービスの充実を求める声がある","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"av-i","cardIds":["av1","av2","av3"]}],"readingOrder":["av-i"]}'

av_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$AV_ID" \
  -H 'Content-Type: application/json' -d "$AV_DOC")
check "AV PUT document (作成)" "200" "$av_put"

# ① AI束ね
av_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"av1","text":"定時運航の維持を最優先にすべきとの声","textReviewed":true},{"id":"av2","text":"遅延時の案内が不十分で顧客が不満","textReviewed":true},{"id":"av3","text":"機内サービスの充実を求める声がある","textReviewed":true}]}')
case "$av_groups" in *'"groups":'*) echo "  PASS: AV ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: AV ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
av_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$AV_DOC,\"islandId\":\"av-i\"}")
case "$av_summary" in *'"groundingIds":["av1","av2","av3"]'*) echo "  PASS: AV ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: AV ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（定時運航優先 vs 遅延対応の不満・定時性と顧客体験の相克）
av_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"av1","text":"定時運航の維持を最優先にすべきとの声","textReviewed":true},"cardB":{"id":"av2","text":"遅延時の案内が不十分で顧客が不満","textReviewed":true}}')
case "$av_contra" in *'"hasContradiction"'*) echo "  PASS: AV ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: AV ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
av_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$AV_DOC}")
case "$av_narr" in *'"basedOnReadingOrder":["av-i"]'*) echo "  PASS: AV ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: AV ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
av_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$AV_ID")
check "AV 読戻し (200)" "200" "$av_read"

echo ""
echo "--- シナリオ69: 出版・メディアの雑誌特集企画会議（読者ニーズと商業性の相克） ---"
# 業態: 出版・メディア（雑誌編集）
# 想定人物: 編集長（特集企画を整理）
# 業務領域: 特集企画案・読者反応・ライター提案のKJ分類と、号の構成決定
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 読者の求めるテーマと広告主の意向の相克を矛盾検出で表面化し、編集判断の
#          根拠にする（編集の独立と商業性のバランス）。
PU_ID="biz-flow-publishing"
PU_DOC='{"version":1,"id":"'$PU_ID'","title":"特集企画会議","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"pu1","text":"読者アンケートでは生活情報系の特集が人気","x":0,"y":0,"textReviewed":true},{"id":"pu2","text":"広告主からは美容・健康系の特集を期待する声","x":10,"y":0,"textReviewed":true},{"id":"pu3","text":"ライターからは深掘り調査系の企画提案がある","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"pu-i","cardIds":["pu1","pu2","pu3"]}],"readingOrder":["pu-i"]}'

pu_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$PU_ID" \
  -H 'Content-Type: application/json' -d "$PU_DOC")
check "PU PUT document (作成)" "200" "$pu_put"

# ① AI束ね
pu_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"pu1","text":"読者アンケートでは生活情報系の特集が人気","textReviewed":true},{"id":"pu2","text":"広告主からは美容・健康系の特集を期待する声","textReviewed":true},{"id":"pu3","text":"ライターからは深掘り調査系の企画提案がある","textReviewed":true}]}')
case "$pu_groups" in *'"groups":'*) echo "  PASS: PU ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: PU ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
pu_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$PU_DOC,\"islandId\":\"pu-i\"}")
case "$pu_summary" in *'"groundingIds":["pu1","pu2","pu3"]'*) echo "  PASS: PU ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: PU ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（読者ニーズ vs 広告主の意向・編集の独立と商業性の相克）
pu_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"pu1","text":"読者アンケートでは生活情報系の特集が人気","textReviewed":true},"cardB":{"id":"pu2","text":"広告主からは美容・健康系の特集を期待する声","textReviewed":true}}')
case "$pu_contra" in *'"hasContradiction"'*) echo "  PASS: PU ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: PU ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
pu_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$PU_DOC}")
case "$pu_narr" in *'"basedOnReadingOrder":["pu-i"]'*) echo "  PASS: PU ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: PU ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
pu_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$PU_ID")
check "PU 読戻し (200)" "200" "$pu_read"

echo ""
echo "--- シナリオ70: 医療・クリニックの患者フィードバックと外来運営（丁寧さと効率の相克） ---"
# 業態: 医療・診療（クリニック運営）
# 想定人物: クリニック院長（患者フィードバックを整理）
# 業務領域: 患者からのフィードバック（診療・待ち時間・対応）のKJ分類と、外来運営改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 診療の丁寧さ（時間をかける）と待ち時間（効率）のトレードオフを矛盾検出で
#          表面化し、外来運営の根拠にする（丁寧さと効率の相克）。
CL_ID="biz-flow-clinic"
CL_DOC='{"version":1,"id":"'$CL_ID'","title":"患者フィードバック整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"cl1","text":"患者は診察時間が短いと感じている","x":0,"y":0,"textReviewed":true},{"id":"cl2","text":"待ち時間が長いという不満が多い","x":10,"y":0,"textReviewed":true},{"id":"cl3","text":"オンライン予約の導入で混雑が減った","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"cl-i","cardIds":["cl1","cl2","cl3"]}],"readingOrder":["cl-i"]}'

cl_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$CL_ID" \
  -H 'Content-Type: application/json' -d "$CL_DOC")
check "CL PUT document (作成)" "200" "$cl_put"

# ① AI束ね
cl_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"cl1","text":"患者は診察時間が短いと感じている","textReviewed":true},{"id":"cl2","text":"待ち時間が長いという不満が多い","textReviewed":true},{"id":"cl3","text":"オンライン予約の導入で混雑が減った","textReviewed":true}]}')
case "$cl_groups" in *'"groups":'*) echo "  PASS: CL ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: CL ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
cl_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$CL_DOC,\"islandId\":\"cl-i\"}")
case "$cl_summary" in *'"groundingIds":["cl1","cl2","cl3"]'*) echo "  PASS: CL ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: CL ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（診察時間が短い vs 待ち時間が長い・丁寧さと効率の相克）
cl_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"cl1","text":"患者は診察時間が短いと感じている","textReviewed":true},"cardB":{"id":"cl2","text":"待ち時間が長いという不満が多い","textReviewed":true}}')
case "$cl_contra" in *'"hasContradiction"'*) echo "  PASS: CL ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: CL ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
cl_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$CL_DOC}")
case "$cl_narr" in *'"basedOnReadingOrder":["cl-i"]'*) echo "  PASS: CL ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: CL ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
cl_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$CL_ID")
check "CL 読戻し (200)" "200" "$cl_read"

echo ""
echo "--- シナリオ71: 環境・サステナビリティの脱炭素戦略（外部要求と内部コストの相克） ---"
# 業態: 環境・サステナビリティ（ESG/CSR）
# 想定人物: サステナビリティ責任者（ESG要求を整理）
# 業務領域: ステークホルダーからのESG要求・社内課題のKJ分類と、脱炭素戦略の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 短期的な収益（事業拡大）と長期的な環境負荷（脱炭素投資）のトレードオフを
#          矛盾検出で表面化し、戦略判断の根拠にする（外部要求と内部コストの相克）。
ES_ID="biz-flow-esg"
ES_DOC='{"version":1,"id":"'$ES_ID'","title":"脱炭素戦略検討","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"es1","text":"投資家は脱炭素目標の開示を求めている","x":0,"y":0,"textReviewed":true},{"id":"es2","text":"脱炭素投資は短期的な収益を圧迫するという懸念","x":10,"y":0,"textReviewed":true},{"id":"es3","text":"再生可能エネルギーへの切替でコスト低減の余地がある","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"es-i","cardIds":["es1","es2","es3"]}],"readingOrder":["es-i"]}'

es_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$ES_ID" \
  -H 'Content-Type: application/json' -d "$ES_DOC")
check "ES PUT document (作成)" "200" "$es_put"

# ① AI束ね
es_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"es1","text":"投資家は脱炭素目標の開示を求めている","textReviewed":true},{"id":"es2","text":"脱炭素投資は短期的な収益を圧迫するという懸念","textReviewed":true},{"id":"es3","text":"再生可能エネルギーへの切替でコスト低減の余地がある","textReviewed":true}]}')
case "$es_groups" in *'"groups":'*) echo "  PASS: ES ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: ES ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
es_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$ES_DOC,\"islandId\":\"es-i\"}")
case "$es_summary" in *'"groundingIds":["es1","es2","es3"]'*) echo "  PASS: ES ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: ES ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（脱炭素目標の開示要求 vs 短期的な収益圧迫・外部要求と内部コストの相克）
es_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"es1","text":"投資家は脱炭素目標の開示を求めている","textReviewed":true},"cardB":{"id":"es2","text":"脱炭素投資は短期的な収益を圧迫するという懸念","textReviewed":true}}')
case "$es_contra" in *'"hasContradiction"'*) echo "  PASS: ES ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: ES ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
es_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$ES_DOC}")
case "$es_narr" in *'"basedOnReadingOrder":["es-i"]'*) echo "  PASS: ES ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: ES ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
es_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$ES_ID")
check "ES 読戻し (200)" "200" "$es_read"

echo ""
echo "--- シナリオ72: コンサルティングの組織変革プロジェクト振り返り（経営層の期待と現場の受容） ---"
# 業態: コンサルティング（組織変革支援）
# 想定人物: コンサルタント／プロジェクトリード（変革プロジェクトの振り返り）
# 業務領域: 組織変革プロジェクトの振り返り（成果・課題・抵抗）のKJ分類と、次の展開
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 経営層の期待（スピード）と現場の準備（変革への抵抗）の乖離を矛盾検出で
#          表面化し、展開の根拠にする（期待と受容の乖離）。
CS_ID="biz-flow-consulting"
CS_DOC='{"version":1,"id":"'$CS_ID'","title":"組織変革プロジェクト振り返り","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"cs1","text":"経営層は変革のスピードアップを求めている","x":0,"y":0,"textReviewed":true},{"id":"cs2","text":"現場では新しい業務プロセスへの抵抗がある","x":10,"y":0,"textReviewed":true},{"id":"cs3","text":"初期の成果は一部部門で出始めている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"cs-i","cardIds":["cs1","cs2","cs3"]}],"readingOrder":["cs-i"]}'

cs_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$CS_ID" \
  -H 'Content-Type: application/json' -d "$CS_DOC")
check "CS PUT document (作成)" "200" "$cs_put"

# ① AI束ね
cs_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"cs1","text":"経営層は変革のスピードアップを求めている","textReviewed":true},{"id":"cs2","text":"現場では新しい業務プロセスへの抵抗がある","textReviewed":true},{"id":"cs3","text":"初期の成果は一部部門で出始めている","textReviewed":true}]}')
case "$cs_groups" in *'"groups":'*) echo "  PASS: CS ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: CS ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
cs_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$CS_DOC,\"islandId\":\"cs-i\"}")
case "$cs_summary" in *'"groundingIds":["cs1","cs2","cs3"]'*) echo "  PASS: CS ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: CS ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（スピードアップ要求 vs 現場の抵抗・期待と受容の乖離）
cs_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"cs1","text":"経営層は変革のスピードアップを求めている","textReviewed":true},"cardB":{"id":"cs2","text":"現場では新しい業務プロセスへの抵抗がある","textReviewed":true}}')
case "$cs_contra" in *'"hasContradiction"'*) echo "  PASS: CS ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: CS ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
cs_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$CS_DOC}")
case "$cs_narr" in *'"basedOnReadingOrder":["cs-i"]'*) echo "  PASS: CS ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: CS ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
cs_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$CS_ID")
check "CS 読戻し (200)" "200" "$cs_read"

echo ""
echo "--- シナリオ73: スポーツ・フィットネスのジム運営（設備投資と会員料金の相克） ---"
# 業態: スポーツ・フィットネス（ジム/スポーツクラブ運営）
# 想定人物: クラブマネージャー（会員フィードバックを整理）
# 業務領域: 会員の継続・退会理由のKJ分類と、会員満足・継続率改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 設備投資（施設拡充）と会員料金（値上げへの抵抗）のトレードオフを矛盾検出で
#          表面化し、運営判断の根拠にする（設備と料金の相克）。
GY_ID="biz-flow-gym"
GY_DOC='{"version":1,"id":"'$GY_ID'","title":"会員フィードバック整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"gy1","text":"会員は施設の混雑・機器不足を不満に感じている","x":0,"y":0,"textReviewed":true},{"id":"gy2","text":"設備拡充には会員料金の値上げが必要との声","x":10,"y":0,"textReviewed":true},{"id":"gy3","text":"初心者向けプログラムの満足度が高い","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"gy-i","cardIds":["gy1","gy2","gy3"]}],"readingOrder":["gy-i"]}'

gy_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$GY_ID" \
  -H 'Content-Type: application/json' -d "$GY_DOC")
check "GY PUT document (作成)" "200" "$gy_put"

# ① AI束ね
gy_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"gy1","text":"会員は施設の混雑・機器不足を不満に感じている","textReviewed":true},{"id":"gy2","text":"設備拡充には会員料金の値上げが必要との声","textReviewed":true},{"id":"gy3","text":"初心者向けプログラムの満足度が高い","textReviewed":true}]}')
case "$gy_groups" in *'"groups":'*) echo "  PASS: GY ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: GY ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
gy_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$GY_DOC,\"islandId\":\"gy-i\"}")
case "$gy_summary" in *'"groundingIds":["gy1","gy2","gy3"]'*) echo "  PASS: GY ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: GY ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（設備不足の不満 vs 料金値上げの必要性・設備と料金の相克）
gy_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"gy1","text":"会員は施設の混雑・機器不足を不満に感じている","textReviewed":true},"cardB":{"id":"gy2","text":"設備拡充には会員料金の値上げが必要との声","textReviewed":true}}')
case "$gy_contra" in *'"hasContradiction"'*) echo "  PASS: GY ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: GY ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
gy_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$GY_DOC}")
case "$gy_narr" in *'"basedOnReadingOrder":["gy-i"]'*) echo "  PASS: GY ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: GY ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
gy_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$GY_ID")
check "GY 読戻し (200)" "200" "$gy_read"

echo ""
echo "--- シナリオ74: ペット・動物病院の飼い主フィードバック整理（主観報告と客観所見の乖離） ---"
# 業態: ペット・動物病院（動物病院運営）
# 想定人物: 獣医師／動物病院スタッフ（飼い主の声を整理）
# 業務領域: 飼い主からの症状報告・治療満足・受付対応の声のKJ分類と、再診・受付改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 飼い主が語る症状の主観（見た目の印象）と診療記録の客観所見（検査値）の
#          乖離を矛盾検出で表面化し、飼い主への説明と再診率改善の根拠にする
#          （代理報告の限界）。
VT_ID="biz-flow-vet"
VT_DOC='{"version":1,"id":"'$VT_ID'","title":"飼い主フィードバック整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"vt1","text":"飼い主は元気そうと話すが、検査では炎症値が高い","x":0,"y":0,"textReviewed":true},{"id":"vt2","text":"治療費の負担で再診を控える声がある","x":10,"y":0,"textReviewed":true},{"id":"vt3","text":"待ち時間は短く、スタッフの説明は丁寧と評価されている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"vt-i","cardIds":["vt1","vt2","vt3"]}],"readingOrder":["vt-i"]}'

vt_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$VT_ID" \
  -H 'Content-Type: application/json' -d "$VT_DOC")
check "VT PUT document (作成)" "200" "$vt_put"

# ① AI束ね
vt_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"vt1","text":"飼い主は元気そうと話すが、検査では炎症値が高い","textReviewed":true},{"id":"vt2","text":"治療費の負担で再診を控える声がある","textReviewed":true},{"id":"vt3","text":"待ち時間は短く、スタッフの説明は丁寧と評価されている","textReviewed":true}]}')
case "$vt_groups" in *'"groups":'*) echo "  PASS: VT ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: VT ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
vt_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$VT_DOC,\"islandId\":\"vt-i\"}")
case "$vt_summary" in *'"groundingIds":["vt1","vt2","vt3"]'*) echo "  PASS: VT ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: VT ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（主観の見た目 vs 客観の検査値・代理報告の限界）
vt_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"vt1","text":"飼い主は元気そうと話すが、検査では炎症値が高い","textReviewed":true},"cardB":{"id":"vt2","text":"治療費の負担で再診を控える声がある","textReviewed":true}}')
case "$vt_contra" in *'"hasContradiction"'*) echo "  PASS: VT ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: VT ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
vt_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$VT_DOC}")
case "$vt_narr" in *'"basedOnReadingOrder":["vt-i"]'*) echo "  PASS: VT ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: VT ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
vt_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$VT_ID")
check "VT 読戻し (200)" "200" "$vt_read"

echo ""
echo "--- シナリオ75: 生命保険の営業提案振り返り（顧客ニーズと販売目標の乖離） ---"
# 業態: 生命保険（営業・提案）
# 想定人物: 営業マネージャー（営業提案の振り返り）
# 業務領域: 営業提案の成否・顧客反応・商品要望のKJ分類と、提案力改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 顧客の求める保障（商品ニーズ）と営業の売りたい商品（販売目標）の乖離を
#          矛盾検出で表面化し、提案改善の根拠にする（ニーズと目標の乖離）。
IN_ID="biz-flow-insurance"
IN_DOC='{"version":1,"id":"'$IN_ID'","title":"営業提案振り返り","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"in1","text":"顧客は保障内容の柔軟性を重視している","x":0,"y":0,"textReviewed":true},{"id":"in2","text":"営業は販売目標達成のため主力商品を優先している","x":10,"y":0,"textReviewed":true},{"id":"in3","text":"契約後のフォローが不十分という声がある","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"in-i","cardIds":["in1","in2","in3"]}],"readingOrder":["in-i"]}'

in_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$IN_ID" \
  -H 'Content-Type: application/json' -d "$IN_DOC")
check "IN PUT document (作成)" "200" "$in_put"

# ① AI束ね
in_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"in1","text":"顧客は保障内容の柔軟性を重視している","textReviewed":true},{"id":"in2","text":"営業は販売目標達成のため主力商品を優先している","textReviewed":true},{"id":"in3","text":"契約後のフォローが不十分という声がある","textReviewed":true}]}')
case "$in_groups" in *'"groups":'*) echo "  PASS: IN ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: IN ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
in_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$IN_DOC,\"islandId\":\"in-i\"}")
case "$in_summary" in *'"groundingIds":["in1","in2","in3"]'*) echo "  PASS: IN ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: IN ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（顧客ニーズ vs 販売目標・ニーズと目標の乖離）
in_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"in1","text":"顧客は保障内容の柔軟性を重視している","textReviewed":true},"cardB":{"id":"in2","text":"営業は販売目標達成のため主力商品を優先している","textReviewed":true}}')
case "$in_contra" in *'"hasContradiction"'*) echo "  PASS: IN ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: IN ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
in_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$IN_DOC}")
case "$in_narr" in *'"basedOnReadingOrder":["in-i"]'*) echo "  PASS: IN ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: IN ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
in_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$IN_ID")
check "IN 読戻し (200)" "200" "$in_read"

echo ""
echo "--- シナリオ76: 人材・採用の中途採用選考フィードバック整理（直感とスコアの相克） ---"
# 業態: 人材・採用（中途採用）
# 想定人物: 人事・採用担当（選考フィードバックを整理）
# 業務領域: 面接官フィードバック・応募者体験・採用判断の声のKJ分類と、採用プロセス改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 面接官の直感的評価（主観・採用に前向き）と、選考スコアの客観評価
#          （能力面の懸念）の乖離を矛盾検出で表面化し、採用判断の根拠と基準の
#          一貫性を高める（直感とスコアの相克）。
HC_ID="biz-flow-hiring"
HC_DOC='{"version":1,"id":"'$HC_ID'","title":"中途採用選考フィードバック","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"hc1","text":"面接官は人柄が良いと直感で前向きに評価した","x":0,"y":0,"textReviewed":true},{"id":"hc2","text":"選考スコアでは専門スキルに懸念が残る","x":10,"y":0,"textReviewed":true},{"id":"hc3","text":"応募者の志望動機は明確で、自社への関心は高い","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"hc-i","cardIds":["hc1","hc2","hc3"]}],"readingOrder":["hc-i"]}'

hc_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$HC_ID" \
  -H 'Content-Type: application/json' -d "$HC_DOC")
check "HC PUT document (作成)" "200" "$hc_put"

# ① AI束ね
hc_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"hc1","text":"面接官は人柄が良いと直感で前向きに評価した","textReviewed":true},{"id":"hc2","text":"選考スコアでは専門スキルに懸念が残る","textReviewed":true},{"id":"hc3","text":"応募者の志望動機は明確で、自社への関心は高い","textReviewed":true}]}')
case "$hc_groups" in *'"groups":'*) echo "  PASS: HC ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: HC ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
hc_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$HC_DOC,\"islandId\":\"hc-i\"}")
case "$hc_summary" in *'"groundingIds":["hc1","hc2","hc3"]'*) echo "  PASS: HC ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: HC ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（直感の前向き評価 vs 選考スコアの懸念・直感とスコアの相克）
hc_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"hc1","text":"面接官は人柄が良いと直感で前向きに評価した","textReviewed":true},"cardB":{"id":"hc2","text":"選考スコアでは専門スキルに懸念が残る","textReviewed":true}}')
case "$hc_contra" in *'"hasContradiction"'*) echo "  PASS: HC ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: HC ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
hc_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$HC_DOC}")
case "$hc_narr" in *'"basedOnReadingOrder":["hc-i"]'*) echo "  PASS: HC ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: HC ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
hc_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$HC_ID")
check "HC 読戻し (200)" "200" "$hc_read"

echo ""
echo "--- シナリオ77: 介護・在宅支援のケアプラン見直し（ケアの質と家族負担のバランス） ---"
# 業態: 介護・在宅支援（訪問介護/在宅ケア）
# 想定人物: ケアマネージャー（家族の声を整理）
# 業務領域: 在宅ケア利用者・家族からのフィードバックのKJ分類と、ケアプラン改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: ケアの質の維持（訪問頻度）と家族の介護負担（精神的・経済的）のバランスを
#          矛盾検出で表面化し、ケアプラン見直しの根拠にする（質と負担のバランス）。
ZT_ID="biz-flow-homecare"
ZT_DOC='{"version":1,"id":"'$ZT_ID'","title":"在宅ケア家族フィードバック","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"zt1","text":"訪問頻度を増やしてケアの質を高めるべきとの声","x":0,"y":0,"textReviewed":true},{"id":"zt2","text":"家族の介護負担が大きく、精神的・経済的に疲弊している","x":10,"y":0,"textReviewed":true},{"id":"zt3","text":"デイサービスの利用で家族の負担が軽減された","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"zt-i","cardIds":["zt1","zt2","zt3"]}],"readingOrder":["zt-i"]}'

zt_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$ZT_ID" \
  -H 'Content-Type: application/json' -d "$ZT_DOC")
check "ZT PUT document (作成)" "200" "$zt_put"

# ① AI束ね
zt_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"zt1","text":"訪問頻度を増やしてケアの質を高めるべきとの声","textReviewed":true},{"id":"zt2","text":"家族の介護負担が大きく、精神的・経済的に疲弊している","textReviewed":true},{"id":"zt3","text":"デイサービスの利用で家族の負担が軽減された","textReviewed":true}]}')
case "$zt_groups" in *'"groups":'*) echo "  PASS: ZT ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: ZT ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
zt_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$ZT_DOC,\"islandId\":\"zt-i\"}")
case "$zt_summary" in *'"groundingIds":["zt1","zt2","zt3"]'*) echo "  PASS: ZT ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: ZT ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（訪問頻度増加 vs 家族負担・質と負担のバランス）
zt_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"zt1","text":"訪問頻度を増やしてケアの質を高めるべきとの声","textReviewed":true},"cardB":{"id":"zt2","text":"家族の介護負担が大きく、精神的・経済的に疲弊している","textReviewed":true}}')
case "$zt_contra" in *'"hasContradiction"'*) echo "  PASS: ZT ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: ZT ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
zt_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$ZT_DOC}")
case "$zt_narr" in *'"basedOnReadingOrder":["zt-i"]'*) echo "  PASS: ZT ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: ZT ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
zt_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$ZT_ID")
check "ZT 読戻し (200)" "200" "$zt_read"

echo ""
echo "--- シナリオ78: 保育・子育ての保護者アンケートと保育観察の整理（代理報告の限界） ---"
# 業態: 保育・子育て（保育園運営）
# 想定人物: 主任保育士（保護者アンケートと保育観察を整理）
# 業務領域: 保護者アンケート・保育士の観察記録・保育方針への声のKJ分類と、保育運営改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 保護者が語る子どもの様子（主観・「家ではよく食べる」）と、保育士の
#          観察記録（客観・給食の残量が多い）の乖離を矛盾検出で表面化し、保護者
#          との情報共有と保育運営の根拠にする（代理報告の限界・子どもの本人は語れない）。
HO_ID="biz-flow-daycare"
HO_DOC='{"version":1,"id":"'$HO_ID'","title":"保護者アンケートと保育観察","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"ho1","text":"保護者は家ではよく食べると話すが、保育所では給食の残量が多い","x":0,"y":0,"textReviewed":true},{"id":"ho2","text":"保護者から送迎時の連絡不足の声がある","x":10,"y":0,"textReviewed":true},{"id":"ho3","text":"クラス活動への参加意欲は高く、遊びは活発だと保育士は評価している","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"ho-i","cardIds":["ho1","ho2","ho3"]}],"readingOrder":["ho-i"]}'

ho_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$HO_ID" \
  -H 'Content-Type: application/json' -d "$HO_DOC")
check "HO PUT document (作成)" "200" "$ho_put"

# ① AI束ね
ho_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"ho1","text":"保護者は家ではよく食べると話すが、保育所では給食の残量が多い","textReviewed":true},{"id":"ho2","text":"保護者から送迎時の連絡不足の声がある","textReviewed":true},{"id":"ho3","text":"クラス活動への参加意欲は高く、遊びは活発だと保育士は評価している","textReviewed":true}]}')
case "$ho_groups" in *'"groups":'*) echo "  PASS: HO ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: HO ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
ho_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$HO_DOC,\"islandId\":\"ho-i\"}")
case "$ho_summary" in *'"groundingIds":["ho1","ho2","ho3"]'*) echo "  PASS: HO ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: HO ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（保護者の主観報告 vs 保育士の客観観察・代理報告の限界）
ho_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"ho1","text":"保護者は家ではよく食べると話すが、保育所では給食の残量が多い","textReviewed":true},"cardB":{"id":"ho2","text":"保護者から送迎時の連絡不足の声がある","textReviewed":true}}')
case "$ho_contra" in *'"hasContradiction"'*) echo "  PASS: HO ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: HO ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
ho_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$HO_DOC}")
case "$ho_narr" in *'"basedOnReadingOrder":["ho-i"]'*) echo "  PASS: HO ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: HO ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
ho_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$HO_ID")
check "HO 読戻し (200)" "200" "$ho_read"

echo ""
echo "--- シナリオ79: 観光・地域振興の来訪者声と住民受容の整理（賑わいと暮らしのバランス） ---"
# 業態: 観光・地域振興（観光協会）
# 想定人物: 観光協会スタッフ（来訪者と住民の声を整理）
# 業務領域: 観光客の声・地域住民の声・観光施策へのフィードバックのKJ分類と、観光振興のバランス
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 観光客の期待（賑わい・新たな体験）と、地域住民の受容（混雑・生活への
#          影響）の乖離を矛盾検出で表面化し、持続可能な観光振興の根拠にする
#          （賑わいと暮らしのバランス）。
TO_ID="biz-flow-tourism"
TO_DOC='{"version":1,"id":"'$TO_ID'","title":"来訪者声と住民受容の整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"to1","text":"観光客は新しい体験を求めて賑わいを歓迎する声が多い","x":0,"y":0,"textReviewed":true},{"id":"to2","text":"地域住民からは混雑と生活への影響を懸念する声がある","x":10,"y":0,"textReviewed":true},{"id":"to3","text":"土産物店の売上は伸び、経済効果は実感されている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"to-i","cardIds":["to1","to2","to3"]}],"readingOrder":["to-i"]}'

to_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$TO_ID" \
  -H 'Content-Type: application/json' -d "$TO_DOC")
check "TO PUT document (作成)" "200" "$to_put"

# ① AI束ね
to_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"to1","text":"観光客は新しい体験を求めて賑わいを歓迎する声が多い","textReviewed":true},{"id":"to2","text":"地域住民からは混雑と生活への影響を懸念する声がある","textReviewed":true},{"id":"to3","text":"土産物店の売上は伸び、経済効果は実感されている","textReviewed":true}]}')
case "$to_groups" in *'"groups":'*) echo "  PASS: TO ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: TO ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
to_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$TO_DOC,\"islandId\":\"to-i\"}")
case "$to_summary" in *'"groundingIds":["to1","to2","to3"]'*) echo "  PASS: TO ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: TO ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（観光客の賑わい歓迎 vs 住民の混雑懸念・賑わいと暮らしの相克）
to_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"to1","text":"観光客は新しい体験を求めて賑わいを歓迎する声が多い","textReviewed":true},"cardB":{"id":"to2","text":"地域住民からは混雑と生活への影響を懸念する声がある","textReviewed":true}}')
case "$to_contra" in *'"hasContradiction"'*) echo "  PASS: TO ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: TO ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
to_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$TO_DOC}")
case "$to_narr" in *'"basedOnReadingOrder":["to-i"]'*) echo "  PASS: TO ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: TO ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
to_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$TO_ID")
check "TO 読戻し (200)" "200" "$to_read"

echo ""
echo "--- シナリオ80: 教育・資格試験の受講生フィードバック整理（期待と結果の乖離） ---"
# 業態: 教育・資格試験（資格取得スクール）
# 想定人物: スクール運営者（受講生フィードバックを整理）
# 業務領域: カリキュラム・講師・試験対策への受講生の声のKJ分類と、講座改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 受講生の学習への期待（合格・スキル向上）と、試験結果・実践での実感
#          （実態）の乖離を矛盾検出で表面化し、講座・カリキュラム改善の根拠にする
#          （期待と結果の乖離）。
EX_ID="biz-flow-exam"
EX_DOC='{"version":1,"id":"'$EX_ID'","title":"受講生フィードバック整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"ex1","text":"受講生は合格とスキル向上への期待を語っている","x":0,"y":0,"textReviewed":true},{"id":"ex2","text":"実践では知識が定着せず、試験結果に反映されていないという声がある","x":10,"y":0,"textReviewed":true},{"id":"ex3","text":"講師の説明は分かりやすいと評価されている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"ex-i","cardIds":["ex1","ex2","ex3"]}],"readingOrder":["ex-i"]}'

ex_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$EX_ID" \
  -H 'Content-Type: application/json' -d "$EX_DOC")
check "EX PUT document (作成)" "200" "$ex_put"

# ① AI束ね
ex_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"ex1","text":"受講生は合格とスキル向上への期待を語っている","textReviewed":true},{"id":"ex2","text":"実践では知識が定着せず、試験結果に反映されていないという声がある","textReviewed":true},{"id":"ex3","text":"講師の説明は分かりやすいと評価されている","textReviewed":true}]}')
case "$ex_groups" in *'"groups":'*) echo "  PASS: EX ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: EX ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
ex_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$EX_DOC,\"islandId\":\"ex-i\"}")
case "$ex_summary" in *'"groundingIds":["ex1","ex2","ex3"]'*) echo "  PASS: EX ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: EX ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（学習への期待 vs 試験結果・実践での実感・期待と結果の乖離）
ex_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"ex1","text":"受講生は合格とスキル向上への期待を語っている","textReviewed":true},"cardB":{"id":"ex2","text":"実践では知識が定着せず、試験結果に反映されていないという声がある","textReviewed":true}}')
case "$ex_contra" in *'"hasContradiction"'*) echo "  PASS: EX ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: EX ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
ex_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$EX_DOC}")
case "$ex_narr" in *'"basedOnReadingOrder":["ex-i"]'*) echo "  PASS: EX ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: EX ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
ex_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$EX_ID")
check "EX 読戻し (200)" "200" "$ex_read"

echo ""
echo "--- シナリオ81: 銀行・窓口の相談記録と営業提案の整理（対応と提案の乖離） ---"
# 業態: 銀行（窓口・リテール）
# 想定人物: 支店長／窓口担当（相談記録を整理）
# 業務領域: 顧客の相談内容・窓口対応・商品提案への反応のKJ分類と、営業方針改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 窓口の親切対応（体験の満足）と、商品提案の一方的さ（顧客ニーズとの
#          乖離）を矛盾検出で表面化し、顧客本位の営業方針の根拠にする（対応と提案の乖離）。
BK_ID="biz-flow-bank"
BK_DOC='{"version":1,"id":"'$BK_ID'","title":"窓口相談記録の整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"bk1","text":"窓口の対応は丁寧で待ち時間も短いと評価されている","x":0,"y":0,"textReviewed":true},{"id":"bk2","text":"商品の提案が一方的で、顧客の状況を聞いてもらえていないとの声がある","x":10,"y":0,"textReviewed":true},{"id":"bk3","text":"定期預金の金利への関心が高く、相談は増えている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"bk-i","cardIds":["bk1","bk2","bk3"]}],"readingOrder":["bk-i"]}'

bk_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$BK_ID" \
  -H 'Content-Type: application/json' -d "$BK_DOC")
check "BK PUT document (作成)" "200" "$bk_put"

# ① AI束ね
bk_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"bk1","text":"窓口の対応は丁寧で待ち時間も短いと評価されている","textReviewed":true},{"id":"bk2","text":"商品の提案が一方的で、顧客の状況を聞いてもらえていないとの声がある","textReviewed":true},{"id":"bk3","text":"定期預金の金利への関心が高く、相談は増えている","textReviewed":true}]}')
case "$bk_groups" in *'"groups":'*) echo "  PASS: BK ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: BK ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
bk_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$BK_DOC,\"islandId\":\"bk-i\"}")
case "$bk_summary" in *'"groundingIds":["bk1","bk2","bk3"]'*) echo "  PASS: BK ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: BK ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（親切対応 vs 一方的な提案・対応と提案の乖離）
bk_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"bk1","text":"窓口の対応は丁寧で待ち時間も短いと評価されている","textReviewed":true},"cardB":{"id":"bk2","text":"商品の提案が一方的で、顧客の状況を聞いてもらえていないとの声がある","textReviewed":true}}')
case "$bk_contra" in *'"hasContradiction"'*) echo "  PASS: BK ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: BK ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
bk_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$BK_DOC}")
case "$bk_narr" in *'"basedOnReadingOrder":["bk-i"]'*) echo "  PASS: BK ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: BK ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
bk_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$BK_ID")
check "BK 読戻し (200)" "200" "$bk_read"

echo ""
echo "--- シナリオ82: 電子・家電の製品サポートとユーザー評価の整理（一次解決と根本原因の乖離） ---"
# 業態: 電子・家電（家電メーカー）
# 想定人物: サポート品質担当（問い合わせと評価を整理）
# 業務領域: サポート問い合わせ・ユーザー評価・製品改善要望のKJ分類と、製品・対応改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: サポートでの一次解決（手順どおり・対応満足）と、同じ使いにくさが繰り返し
#          発生する根本原因（未解決）の乖離を矛盾検出で表面化し、製品改善の根拠に
#          する（一次解決と根本原因の乖離）。
EL_ID="biz-flow-electronics"
EL_DOC='{"version":1,"id":"'$EL_ID'","title":"製品サポートとユーザー評価","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"el1","text":"サポートは手順どおり案内し、一次対応で解決したと報告されている","x":0,"y":0,"textReviewed":true},{"id":"el2","text":"同じ使いにくさの問い合わせが繰り返し発生し、根本原因が残っている","x":10,"y":0,"textReviewed":true},{"id":"el3","text":"新製品の評判は良く、購入検討は増えている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"el-i","cardIds":["el1","el2","el3"]}],"readingOrder":["el-i"]}'

el_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$EL_ID" \
  -H 'Content-Type: application/json' -d "$EL_DOC")
check "EL PUT document (作成)" "200" "$el_put"

# ① AI束ね
el_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"el1","text":"サポートは手順どおり案内し、一次対応で解決したと報告されている","textReviewed":true},{"id":"el2","text":"同じ使いにくさの問い合わせが繰り返し発生し、根本原因が残っている","textReviewed":true},{"id":"el3","text":"新製品の評判は良く、購入検討は増えている","textReviewed":true}]}')
case "$el_groups" in *'"groups":'*) echo "  PASS: EL ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: EL ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
el_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$EL_DOC,\"islandId\":\"el-i\"}")
case "$el_summary" in *'"groundingIds":["el1","el2","el3"]'*) echo "  PASS: EL ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: EL ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（一次解決 vs 根本原因の残存・一次解決と根本原因の乖離）
el_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"el1","text":"サポートは手順どおり案内し、一次対応で解決したと報告されている","textReviewed":true},"cardB":{"id":"el2","text":"同じ使いにくさの問い合わせが繰り返し発生し、根本原因が残っている","textReviewed":true}}')
case "$el_contra" in *'"hasContradiction"'*) echo "  PASS: EL ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: EL ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
el_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$EL_DOC}")
case "$el_narr" in *'"basedOnReadingOrder":["el-i"]'*) echo "  PASS: EL ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: EL ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
el_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$EL_ID")
check "EL 読戻し (200)" "200" "$el_read"

echo ""
echo "--- シナリオ83: 広告・マーケティングのキャンペーン効果検証（感性と成果の乖離） ---"
# 業態: 広告・マーケティング（広告代理店）
# 想定人物: アカウントプランナー（キャンペーン振り返りを整理）
# 業務領域: クライアント要望・クリエイティブ評価・効果指標への声のKJ分類と、次期キャンペーン改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: クリエイティブの主観評価（社内の好き嫌い）と、広告効果の客観指標（成果）
#          の乖離を矛盾検出で表面化し、次期キャンペーンの判断根拠にする（感性と成果の乖離）。
AD_ID="biz-flow-advertising"
AD_DOC='{"version":1,"id":"'$AD_ID'","title":"キャンペーン効果検証","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"ad1","text":"社内ではクリエイティブの評価が分かれ、好き嫌いで議論になった","x":0,"y":0,"textReviewed":true},{"id":"ad2","text":"配信後の効果指標では、特定セグメントに反響が集中している","x":10,"y":0,"textReviewed":true},{"id":"ad3","text":"クライアントはブランド認知向上を期待し、即効的な売上を求めていない","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"ad-i","cardIds":["ad1","ad2","ad3"]}],"readingOrder":["ad-i"]}'

ad_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$AD_ID" \
  -H 'Content-Type: application/json' -d "$AD_DOC")
check "AD PUT document (作成)" "200" "$ad_put"

# ① AI束ね
ad_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"ad1","text":"社内ではクリエイティブの評価が分かれ、好き嫌いで議論になった","textReviewed":true},{"id":"ad2","text":"配信後の効果指標では、特定セグメントに反響が集中している","textReviewed":true},{"id":"ad3","text":"クライアントはブランド認知向上を期待し、即効的な売上を求めていない","textReviewed":true}]}')
case "$ad_groups" in *'"groups":'*) echo "  PASS: AD ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: AD ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
ad_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$AD_DOC,\"islandId\":\"ad-i\"}")
case "$ad_summary" in *'"groundingIds":["ad1","ad2","ad3"]'*) echo "  PASS: AD ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: AD ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（社内の好き嫌い vs 効果指標・感性と成果の乖離）
ad_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"ad1","text":"社内ではクリエイティブの評価が分かれ、好き嫌いで議論になった","textReviewed":true},"cardB":{"id":"ad2","text":"配信後の効果指標では、特定セグメントに反響が集中している","textReviewed":true}}')
case "$ad_contra" in *'"hasContradiction"'*) echo "  PASS: AD ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: AD ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
ad_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$AD_DOC}")
case "$ad_narr" in *'"basedOnReadingOrder":["ad-i"]'*) echo "  PASS: AD ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: AD ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
ad_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$AD_ID")
check "AD 読戻し (200)" "200" "$ad_read"

echo ""
echo "--- シナリオ84: 化学・素材のSDS・規制対応（迅速さと正確さの相克） ---"
# 業態: 化学・素材（化学品メーカー）
# 想定人物: 安全・規制担当（SDS・規制対応を整理）
# 業務領域: 安全データシート（SDS）・規制要求・顧客照会のKJ分類と、安全・コンプライアンス改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 顧客の迅速な対応要求（SDS提供）と正確な安全情報の提供（規制再検証）の
#          トレードオフを矛盾検出で表面化し、対応プロセス改善の根拠にする（迅速さと正確さの相克）。
CH_ID="biz-flow-chemical"
CH_DOC='{"version":1,"id":"'$CH_ID'","title":"SDS・規制対応整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"ch1","text":"顧客はSDSの迅速な提供を求めている","x":0,"y":0,"textReviewed":true},{"id":"ch2","text":"規制変更に伴うSDSの再検証に時間がかかっている","x":10,"y":0,"textReviewed":true},{"id":"ch3","text":"誤ったSDS提供がクレームにつながった事例がある","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"ch-i","cardIds":["ch1","ch2","ch3"]}],"readingOrder":["ch-i"]}'

ch_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$CH_ID" \
  -H 'Content-Type: application/json' -d "$CH_DOC")
check "CH PUT document (作成)" "200" "$ch_put"

# ① AI束ね
ch_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"ch1","text":"顧客はSDSの迅速な提供を求めている","textReviewed":true},{"id":"ch2","text":"規制変更に伴うSDSの再検証に時間がかかっている","textReviewed":true},{"id":"ch3","text":"誤ったSDS提供がクレームにつながった事例がある","textReviewed":true}]}')
case "$ch_groups" in *'"groups":'*) echo "  PASS: CH ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: CH ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
ch_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$CH_DOC,\"islandId\":\"ch-i\"}")
case "$ch_summary" in *'"groundingIds":["ch1","ch2","ch3"]'*) echo "  PASS: CH ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: CH ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（SDS迅速提供 vs 規制再検証・迅速さと正確さの相克）
ch_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"ch1","text":"顧客はSDSの迅速な提供を求めている","textReviewed":true},"cardB":{"id":"ch2","text":"規制変更に伴うSDSの再検証に時間がかかっている","textReviewed":true}}')
case "$ch_contra" in *'"hasContradiction"'*) echo "  PASS: CH ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: CH ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
ch_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$CH_DOC}")
case "$ch_narr" in *'"basedOnReadingOrder":["ch-i"]'*) echo "  PASS: CH ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: CH ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
ch_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$CH_ID")
check "CH 読戻し (200)" "200" "$ch_read"

echo ""
echo "--- シナリオ85: IT・SaaSのカスタマーサクセス（新機能開発と既存顧客の安定運用のトレードオフ） ---"
# 業態: IT・SaaS（クラウドサービス）
# 想定人物: カスタマーサクセスマネージャー（顧客の解約・継続を分析）
# 業務領域: 顧客の利用状況・解約リスク・要望のKJ分類と、継続率改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 新機能の開発（ロードマップ）と既存顧客の安定運用（サポート）のトレードオフを
#          矛盾検出で表面化し、リソース配分の根拠にする（開発と安定のトレードオフ）。
SA_ID="biz-flow-saas"
SA_DOC='{"version":1,"id":"'$SA_ID'","title":"カスタマーサクセス分析","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"sa1","text":"新機能の開発に注力してほしいとの要望が多い","x":0,"y":0,"textReviewed":true},{"id":"sa2","text":"既存機能の安定運用・サポートを優先すべきとの声","x":10,"y":0,"textReviewed":true},{"id":"sa3","text":"一部顧客で利用頻度が低下しており解約リスクが高い","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"sa-i","cardIds":["sa1","sa2","sa3"]}],"readingOrder":["sa-i"]}'

sa_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$SA_ID" \
  -H 'Content-Type: application/json' -d "$SA_DOC")
check "SA PUT document (作成)" "200" "$sa_put"

# ① AI束ね
sa_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"sa1","text":"新機能の開発に注力してほしいとの要望が多い","textReviewed":true},{"id":"sa2","text":"既存機能の安定運用・サポートを優先すべきとの声","textReviewed":true},{"id":"sa3","text":"一部顧客で利用頻度が低下しており解約リスクが高い","textReviewed":true}]}')
case "$sa_groups" in *'"groups":'*) echo "  PASS: SA ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: SA ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
sa_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$SA_DOC,\"islandId\":\"sa-i\"}")
case "$sa_summary" in *'"groundingIds":["sa1","sa2","sa3"]'*) echo "  PASS: SA ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: SA ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（新機能開発 vs 既存安定・開発と安定のトレードオフ）
sa_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"sa1","text":"新機能の開発に注力してほしいとの要望が多い","textReviewed":true},"cardB":{"id":"sa2","text":"既存機能の安定運用・サポートを優先すべきとの声","textReviewed":true}}')
case "$sa_contra" in *'"hasContradiction"'*) echo "  PASS: SA ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: SA ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
sa_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$SA_DOC}")
case "$sa_narr" in *'"basedOnReadingOrder":["sa-i"]'*) echo "  PASS: SA ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: SA ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
sa_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$SA_ID")
check "SA 読戻し (200)" "200" "$sa_read"

echo ""
echo "--- シナリオ86: 人材派遣のスタッフ声と派遣先評価の整理（働きやすさと成果の乖離） ---"
# 業態: 人材派遣（派遣会社）
# 想定人物: 営業・派遣コーディネーター（スタッフと派遣先の声を整理）
# 業務領域: 派遣スタッフの声・派遣先の評価・契約更新の判断材料のKJ分類と、派遣マッチング改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 派遣スタッフの働きやすさ（主観・職場環境）と、派遣先の評価（客観・業務成果）
#          の乖離を矛盾検出で表面化し、派遣マッチングと契約更新の判断根拠にする
#          （働きやすさと成果の乖離）。
DP_ID="biz-flow-dispatch"
DP_DOC='{"version":1,"id":"'$DP_ID'","title":"スタッフ声と派遣先評価","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"dp1","text":"派遣スタッフは職場の雰囲気は良いと話すが、業務内容に不満がある","x":0,"y":0,"textReviewed":true},{"id":"dp2","text":"派遣先からは業務成果の評価が高いが、コミュニケーションに課題があるとの声","x":10,"y":0,"textReviewed":true},{"id":"dp3","text":"契約更新の判断がスタッフと派遣先で分かれている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"dp-i","cardIds":["dp1","dp2","dp3"]}],"readingOrder":["dp-i"]}'

dp_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$DP_ID" \
  -H 'Content-Type: application/json' -d "$DP_DOC")
check "DP PUT document (作成)" "200" "$dp_put"

# ① AI束ね
dp_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"dp1","text":"派遣スタッフは職場の雰囲気は良いと話すが、業務内容に不満がある","textReviewed":true},{"id":"dp2","text":"派遣先からは業務成果の評価が高いが、コミュニケーションに課題があるとの声","textReviewed":true},{"id":"dp3","text":"契約更新の判断がスタッフと派遣先で分かれている","textReviewed":true}]}')
case "$dp_groups" in *'"groups":'*) echo "  PASS: DP ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: DP ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
dp_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$DP_DOC,\"islandId\":\"dp-i\"}")
case "$dp_summary" in *'"groundingIds":["dp1","dp2","dp3"]'*) echo "  PASS: DP ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: DP ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（働きやすさ vs 業務成果・働きやすさと成果の乖離）
dp_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"dp1","text":"派遣スタッフは職場の雰囲気は良いと話すが、業務内容に不満がある","textReviewed":true},"cardB":{"id":"dp2","text":"派遣先からは業務成果の評価が高いが、コミュニケーションに課題があるとの声","textReviewed":true}}')
case "$dp_contra" in *'"hasContradiction"'*) echo "  PASS: DP ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: DP ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
dp_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$DP_DOC}")
case "$dp_narr" in *'"basedOnReadingOrder":["dp-i"]'*) echo "  PASS: DP ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: DP ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
dp_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$DP_ID")
check "DP 読戻し (200)" "200" "$dp_read"

echo ""
echo "--- シナリオ87: 自治体・健康増進の市民の声整理（効果と実感の乖離） ---"
# 業態: 自治体・健康増進（市の健康施策）
# 想定人物: 保健師・健康増進担当（市民の声を整理）
# 業務領域: 健康診査・健康教室・健康相談への市民の声のKJ分類と、健康施策改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 健康施策の効果（客観・健診結果の改善）と、市民の実感（主観・参加の
#          負担感）の乖離を矛盾検出で表面化し、健康施策の改善根拠にする（効果と実感の乖離）。
HW_ID="biz-flow-health"
HW_DOC='{"version":1,"id":"'$HW_ID'","title":"市民の健康施策の声","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"hw1","text":"健診の受診率は上がり、要指導者の早期発見が増えている","x":0,"y":0,"textReviewed":true},{"id":"hw2","text":"健康教室の参加負担（時間・場所）を理由に参加を控える声がある","x":10,"y":0,"textReviewed":true},{"id":"hw3","text":"健康相談は丁寧だと評価され、リピート利用は増えている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"hw-i","cardIds":["hw1","hw2","hw3"]}],"readingOrder":["hw-i"]}'

hw_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$HW_ID" \
  -H 'Content-Type: application/json' -d "$HW_DOC")
check "HW PUT document (作成)" "200" "$hw_put"

# ① AI束ね
hw_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"hw1","text":"健診の受診率は上がり、要指導者の早期発見が増えている","textReviewed":true},{"id":"hw2","text":"健康教室の参加負担（時間・場所）を理由に参加を控える声がある","textReviewed":true},{"id":"hw3","text":"健康相談は丁寧だと評価され、リピート利用は増えている","textReviewed":true}]}')
case "$hw_groups" in *'"groups":'*) echo "  PASS: HW ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: HW ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
hw_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$HW_DOC,\"islandId\":\"hw-i\"}")
case "$hw_summary" in *'"groundingIds":["hw1","hw2","hw3"]'*) echo "  PASS: HW ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: HW ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（施策の効果 vs 市民の実感・効果と実感の乖離）
hw_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"hw1","text":"健診の受診率は上がり、要指導者の早期発見が増えている","textReviewed":true},"cardB":{"id":"hw2","text":"健康教室の参加負担（時間・場所）を理由に参加を控える声がある","textReviewed":true}}')
case "$hw_contra" in *'"hasContradiction"'*) echo "  PASS: HW ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: HW ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
hw_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$HW_DOC}")
case "$hw_narr" in *'"basedOnReadingOrder":["hw-i"]'*) echo "  PASS: HW ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: HW ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
hw_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$HW_ID")
check "HW 読戻し (200)" "200" "$hw_read"

echo ""
echo "--- シナリオ88: 食品スーパーの店舗運営と顧客声の整理（効率と体験の乖離） ---"
# 業態: 食品スーパー（スーパーマーケット運営）
# 想定人物: 店長（店舗運営と顧客声を整理）
# 業務領域: レジ・品揃え・店舗レイアウトへの顧客の声のKJ分類と、店舗運営改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 店舗の効率運営（客単価・レジ回転）と、顧客の買いやすさ（体験・ゆっくり
#          選びたい）の乖離を矛盾検出で表面化し、店舗運営の改善根拠にする（効率と体験の乖離）。
SM_ID="biz-flow-supermarket"
SM_DOC='{"version":1,"id":"'$SM_ID'","title":"店舗運営と顧客声","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"sm1","text":"レジの回転は速く、混雑時の待ち時間は短いと運営は評価している","x":0,"y":0,"textReviewed":true},{"id":"sm2","text":"顧客からはゆっくり選びたいが、レイアウトが分かりにくいという声がある","x":10,"y":0,"textReviewed":true},{"id":"sm3","text":"生鮮食品の鮮度は高く、リピート購入は増えている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"sm-i","cardIds":["sm1","sm2","sm3"]}],"readingOrder":["sm-i"]}'

sm_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$SM_ID" \
  -H 'Content-Type: application/json' -d "$SM_DOC")
check "SM PUT document (作成)" "200" "$sm_put"

# ① AI束ね
sm_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"sm1","text":"レジの回転は速く、混雑時の待ち時間は短いと運営は評価している","textReviewed":true},{"id":"sm2","text":"顧客からはゆっくり選びたいが、レイアウトが分かりにくいという声がある","textReviewed":true},{"id":"sm3","text":"生鮮食品の鮮度は高く、リピート購入は増えている","textReviewed":true}]}')
case "$sm_groups" in *'"groups":'*) echo "  PASS: SM ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: SM ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
sm_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$SM_DOC,\"islandId\":\"sm-i\"}")
case "$sm_summary" in *'"groundingIds":["sm1","sm2","sm3"]'*) echo "  PASS: SM ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: SM ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（効率運営 vs 買いやすさ・効率と体験の乖離）
sm_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"sm1","text":"レジの回転は速く、混雑時の待ち時間は短いと運営は評価している","textReviewed":true},"cardB":{"id":"sm2","text":"顧客からはゆっくり選びたいが、レイアウトが分かりにくいという声がある","textReviewed":true}}')
case "$sm_contra" in *'"hasContradiction"'*) echo "  PASS: SM ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: SM ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
sm_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$SM_DOC}")
case "$sm_narr" in *'"basedOnReadingOrder":["sm-i"]'*) echo "  PASS: SM ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: SM ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
sm_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$SM_ID")
check "SM 読戻し (200)" "200" "$sm_read"

echo ""
echo "--- シナリオ89: 証券・投資の顧客相談と商品推奨の整理（推奨とリスク許容の乖離） ---"
# 業態: 証券・投資（証券会社）
# 想定人物: 証券営業・相談担当（顧客相談を整理）
# 業務領域: 投資相談・商品推奨・リスク説明への顧客の声のKJ分類と、顧客本位の営業改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 営業の商品推奨（販売目標・手数料）と、顧客のリスク許容（安全志向・
#          損失回避）の乖離を矛盾検出で表面化し、顧客本位の営業の根拠にする
#          （推奨とリスク許容の乖離）。
SC_ID="biz-flow-securities"
SC_DOC='{"version":1,"id":"'$SC_ID'","title":"顧客相談と商品推奨","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"sc1","text":"営業は高利回り商品の販売目標を重視している","x":0,"y":0,"textReviewed":true},{"id":"sc2","text":"顧客は損失を恐れ、元本確保を優先したいという声がある","x":10,"y":0,"textReviewed":true},{"id":"sc3","text":"投資相談は丁寧で、相談後の安心感は高いと評価されている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"sc-i","cardIds":["sc1","sc2","sc3"]}],"readingOrder":["sc-i"]}'

sc_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$SC_ID" \
  -H 'Content-Type: application/json' -d "$SC_DOC")
check "SC PUT document (作成)" "200" "$sc_put"

# ① AI束ね
sc_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"sc1","text":"営業は高利回り商品の販売目標を重視している","textReviewed":true},{"id":"sc2","text":"顧客は損失を恐れ、元本確保を優先したいという声がある","textReviewed":true},{"id":"sc3","text":"投資相談は丁寧で、相談後の安心感は高いと評価されている","textReviewed":true}]}')
case "$sc_groups" in *'"groups":'*) echo "  PASS: SC ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: SC ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
sc_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$SC_DOC,\"islandId\":\"sc-i\"}")
case "$sc_summary" in *'"groundingIds":["sc1","sc2","sc3"]'*) echo "  PASS: SC ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: SC ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（販売目標 vs リスク許容・推奨とリスク許容の乖離）
sc_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"sc1","text":"営業は高利回り商品の販売目標を重視している","textReviewed":true},"cardB":{"id":"sc2","text":"顧客は損失を恐れ、元本確保を優先したいという声がある","textReviewed":true}}')
case "$sc_contra" in *'"hasContradiction"'*) echo "  PASS: SC ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: SC ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
sc_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$SC_DOC}")
case "$sc_narr" in *'"basedOnReadingOrder":["sc-i"]'*) echo "  PASS: SC ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: SC ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
sc_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$SC_ID")
check "SC 読戻し (200)" "200" "$sc_read"

echo ""
echo "--- シナリオ90: 不動産管理の賃貸入居者対応（入居者満足とオーナー収益のトレードオフ） ---"
# 業態: 不動産管理（賃貸オーナー/管理会社）
# 想定人物: 物件管理担当（入居者フィードバックを整理）
# 業務領域: 入居者からのクレーム・要望・契約更新の声のKJ分類と、物件管理改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 入居者満足（維持管理への投資）とオーナーの収益（修繕コスト）のトレードオフを
#          矛盾検出で表面化し、管理判断の根拠にする（満足と収益のトレードオフ）。
PM_ID="biz-flow-property"
PM_DOC='{"version":1,"id":"'$PM_ID'","title":"賃貸入居者対応整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"pm1","text":"入居者は設備の老朽化への対応を求めている","x":0,"y":0,"textReviewed":true},{"id":"pm2","text":"オーナーは修繕コストを抑えたいと考えている","x":10,"y":0,"textReviewed":true},{"id":"pm3","text":"入居者の契約更新率が低下している","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"pm-i","cardIds":["pm1","pm2","pm3"]}],"readingOrder":["pm-i"]}'

pm_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$PM_ID" \
  -H 'Content-Type: application/json' -d "$PM_DOC")
check "PM PUT document (作成)" "200" "$pm_put"

# ① AI束ね
pm_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"pm1","text":"入居者は設備の老朽化への対応を求めている","textReviewed":true},{"id":"pm2","text":"オーナーは修繕コストを抑えたいと考えている","textReviewed":true},{"id":"pm3","text":"入居者の契約更新率が低下している","textReviewed":true}]}')
case "$pm_groups" in *'"groups":'*) echo "  PASS: PM ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: PM ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
pm_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$PM_DOC,\"islandId\":\"pm-i\"}")
case "$pm_summary" in *'"groundingIds":["pm1","pm2","pm3"]'*) echo "  PASS: PM ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: PM ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（老朽化対応の要求 vs 修繕コスト抑制・満足と収益のトレードオフ）
pm_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"pm1","text":"入居者は設備の老朽化への対応を求めている","textReviewed":true},"cardB":{"id":"pm2","text":"オーナーは修繕コストを抑えたいと考えている","textReviewed":true}}')
case "$pm_contra" in *'"hasContradiction"'*) echo "  PASS: PM ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: PM ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
pm_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$PM_DOC}")
case "$pm_narr" in *'"basedOnReadingOrder":["pm-i"]'*) echo "  PASS: PM ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: PM ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
pm_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$PM_ID")
check "PM 読戻し (200)" "200" "$pm_read"

echo ""
echo "--- シナリオ91: イベント・興行の来場者声と集客目標の整理（集客と体験の乖離） ---"
# 業態: イベント・興行（イベント運営）
# 想定人物: イベントプロデューサー（来場者アンケートを整理）
# 業務領域: チケット販売・会場運営・来場者体験への声のKJ分類と、次回イベント改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 企画側の集客目標（チケット完売・収益）と、来場者の体験（混雑・待ち時間・
#          満足）の乖離を矛盾検出で表面化し、次回イベントの企画根拠にする（集客と体験の乖離）。
EV_ID="biz-flow-event"
EV_DOC='{"version":1,"id":"'$EV_ID'","title":"来場者声と集客目標","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"ev1","text":"チケットは完売し、集客目標は達成された","x":0,"y":0,"textReviewed":true},{"id":"ev2","text":"来場者からは会場の混雑と待ち時間に不満の声がある","x":10,"y":0,"textReviewed":true},{"id":"ev3","text":"ステージ演出は好評で、次回の参加意向は高い","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"ev-i","cardIds":["ev1","ev2","ev3"]}],"readingOrder":["ev-i"]}'

ev_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$EV_ID" \
  -H 'Content-Type: application/json' -d "$EV_DOC")
check "EV PUT document (作成)" "200" "$ev_put"

# ① AI束ね
ev_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"ev1","text":"チケットは完売し、集客目標は達成された","textReviewed":true},{"id":"ev2","text":"来場者からは会場の混雑と待ち時間に不満の声がある","textReviewed":true},{"id":"ev3","text":"ステージ演出は好評で、次回の参加意向は高い","textReviewed":true}]}')
case "$ev_groups" in *'"groups":'*) echo "  PASS: EV ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: EV ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
ev_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$EV_DOC,\"islandId\":\"ev-i\"}")
case "$ev_summary" in *'"groundingIds":["ev1","ev2","ev3"]'*) echo "  PASS: EV ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: EV ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（集客目標 vs 来場者体験・集客と体験の乖離）
ev_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"ev1","text":"チケットは完売し、集客目標は達成された","textReviewed":true},"cardB":{"id":"ev2","text":"来場者からは会場の混雑と待ち時間に不満の声がある","textReviewed":true}}')
case "$ev_contra" in *'"hasContradiction"'*) echo "  PASS: EV ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: EV ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
ev_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$EV_DOC}")
case "$ev_narr" in *'"basedOnReadingOrder":["ev-i"]'*) echo "  PASS: EV ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: EV ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
ev_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$EV_ID")
check "EV 読戻し (200)" "200" "$ev_read"

echo ""
echo "--- シナリオ92: ホテル・旅館の宿泊体験と料金設定の整理（体験と料金の乖離） ---"
# 業態: ホテル・旅館（宿泊施設運営）
# 想定人物: ホテル支配人（宿泊客の声を整理）
# 業務領域: 客室・接客・料金への宿泊客の声のKJ分類と、リピート率改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 宿泊客の体験満足（主観・客室・接客）と、料金設定（客観・単価・稼働率）
#          の乖離を矛盾検出で表面化し、料金戦略とサービス改善の根拠にする（体験と料金の乖離）。
HT_ID="biz-flow-hotel"
HT_DOC='{"version":1,"id":"'$HT_ID'","title":"宿泊体験と料金設定","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"ht1","text":"宿泊客は客室の清潔さと接客の丁寧さを高く評価している","x":0,"y":0,"textReviewed":true},{"id":"ht2","text":"料金が高いとの声があり、リピートをためらう客がいる","x":10,"y":0,"textReviewed":true},{"id":"ht3","text":"朝食の満足度は高く、口コミで予約が増えている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"ht-i","cardIds":["ht1","ht2","ht3"]}],"readingOrder":["ht-i"]}'

ht_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$HT_ID" \
  -H 'Content-Type: application/json' -d "$HT_DOC")
check "HT PUT document (作成)" "200" "$ht_put"

# ① AI束ね
ht_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"ht1","text":"宿泊客は客室の清潔さと接客の丁寧さを高く評価している","textReviewed":true},{"id":"ht2","text":"料金が高いとの声があり、リピートをためらう客がいる","textReviewed":true},{"id":"ht3","text":"朝食の満足度は高く、口コミで予約が増えている","textReviewed":true}]}')
case "$ht_groups" in *'"groups":'*) echo "  PASS: HT ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: HT ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
ht_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$HT_DOC,\"islandId\":\"ht-i\"}")
case "$ht_summary" in *'"groundingIds":["ht1","ht2","ht3"]'*) echo "  PASS: HT ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: HT ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（体験満足 vs 料金抵抗・体験と料金の乖離）
ht_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"ht1","text":"宿泊客は客室の清潔さと接客の丁寧さを高く評価している","textReviewed":true},"cardB":{"id":"ht2","text":"料金が高いとの声があり、リピートをためらう客がいる","textReviewed":true}}')
case "$ht_contra" in *'"hasContradiction"'*) echo "  PASS: HT ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: HT ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
ht_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$HT_DOC}")
case "$ht_narr" in *'"basedOnReadingOrder":["ht-i"]'*) echo "  PASS: HT ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: HT ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
ht_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$HT_ID")
check "HT 読戻し (200)" "200" "$ht_read"

echo ""
echo "--- シナリオ93: 通信キャリアの料金プランと解約理由（価格競争とネットワーク投資のトレードオフ） ---"
# 業態: 通信キャリア（携帯/固定通信）
# 想定人物: マーケティング責任者（解約理由を分析）
# 業務領域: 解約・乗り換え理由のKJ分類と、料金プラン・サービス改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 低価格競争（料金プランの値下げ）とネットワーク投資（品質維持）のトレードオフを
#          矛盾検出で表面化し、プラン改定の根拠にする（価格と品質のトレードオフ）。
TP_ID="biz-flow-telco"
TP_DOC='{"version":1,"id":"'$TP_ID'","title":"料金プラン・解約分析","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"tp1","text":"競合の低価格プランへの乗り換えが増えている","x":0,"y":0,"textReviewed":true},{"id":"tp2","text":"ネットワーク品質の維持には投資が必要という社内意見","x":10,"y":0,"textReviewed":true},{"id":"tp3","text":"解約理由は価格だけでなくサポート対応も指摘されている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"tp-i","cardIds":["tp1","tp2","tp3"]}],"readingOrder":["tp-i"]}'

tp_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$TP_ID" \
  -H 'Content-Type: application/json' -d "$TP_DOC")
check "TP PUT document (作成)" "200" "$tp_put"

# ① AI束ね
tp_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"tp1","text":"競合の低価格プランへの乗り換えが増えている","textReviewed":true},{"id":"tp2","text":"ネットワーク品質の維持には投資が必要という社内意見","textReviewed":true},{"id":"tp3","text":"解約理由は価格だけでなくサポート対応も指摘されている","textReviewed":true}]}')
case "$tp_groups" in *'"groups":'*) echo "  PASS: TP ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: TP ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
tp_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$TP_DOC,\"islandId\":\"tp-i\"}")
case "$tp_summary" in *'"groundingIds":["tp1","tp2","tp3"]'*) echo "  PASS: TP ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: TP ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（低価格競争 vs ネットワーク投資・価格と品質のトレードオフ）
tp_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"tp1","text":"競合の低価格プランへの乗り換えが増えている","textReviewed":true},"cardB":{"id":"tp2","text":"ネットワーク品質の維持には投資が必要という社内意見","textReviewed":true}}')
case "$tp_contra" in *'"hasContradiction"'*) echo "  PASS: TP ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: TP ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
tp_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$TP_DOC}")
case "$tp_narr" in *'"basedOnReadingOrder":["tp-i"]'*) echo "  PASS: TP ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: TP ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
tp_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$TP_ID")
check "TP 読戻し (200)" "200" "$tp_read"

echo ""
echo "--- シナリオ94: 鉄道・駅の混雑と利用者声の整理（混雑と快適のトレードオフ） ---"
# 業態: 鉄道・駅（鉄道会社）
# 想定人物: 駅務・設備担当（利用者の声を整理）
# 業務領域: 混雑・駅施設・バリアフリーへの利用者の声のKJ分類と、駅務・設備改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 混雑緩和への投資（輸送力増強・コスト）と、利用者の快適性（体験・待ち時間）
#          のトレードオフを矛盾検出で表面化し、設備投資の判断根拠にする（混雑と快適のトレードオフ）。
RW_ID="biz-flow-railway"
RW_DOC='{"version":1,"id":"'$RW_ID'","title":"混雑と利用者声","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"rw1","text":"通勤時間帯の混雑が激しく、乗降に時間がかかるという声がある","x":0,"y":0,"textReviewed":true},{"id":"rw2","text":"輸送力増強には設備投資が必要で、運賃改定への懸念がある","x":10,"y":0,"textReviewed":true},{"id":"rw3","text":"駅のバリアフリー化は評価され、利用者満足は高い","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"rw-i","cardIds":["rw1","rw2","rw3"]}],"readingOrder":["rw-i"]}'

rw_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$RW_ID" \
  -H 'Content-Type: application/json' -d "$RW_DOC")
check "RW PUT document (作成)" "200" "$rw_put"

# ① AI束ね
rw_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"rw1","text":"通勤時間帯の混雑が激しく、乗降に時間がかかるという声がある","textReviewed":true},{"id":"rw2","text":"輸送力増強には設備投資が必要で、運賃改定への懸念がある","textReviewed":true},{"id":"rw3","text":"駅のバリアフリー化は評価され、利用者満足は高い","textReviewed":true}]}')
case "$rw_groups" in *'"groups":'*) echo "  PASS: RW ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: RW ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
rw_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$RW_DOC,\"islandId\":\"rw-i\"}")
case "$rw_summary" in *'"groundingIds":["rw1","rw2","rw3"]'*) echo "  PASS: RW ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: RW ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（混雑緩和投資 vs 運賃懸念・混雑と快適のトレードオフ）
rw_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"rw1","text":"通勤時間帯の混雑が激しく、乗降に時間がかかるという声がある","textReviewed":true},"cardB":{"id":"rw2","text":"輸送力増強には設備投資が必要で、運賃改定への懸念がある","textReviewed":true}}')
case "$rw_contra" in *'"hasContradiction"'*) echo "  PASS: RW ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: RW ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
rw_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$RW_DOC}")
case "$rw_narr" in *'"basedOnReadingOrder":["rw-i"]'*) echo "  PASS: RW ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: RW ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
rw_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$RW_ID")
check "RW 読戻し (200)" "200" "$rw_read"

echo ""
echo "--- シナリオ95: タクシー・モビリティの配車と乗務員の声整理（効率と稼働のトレードオフ） ---"
# 業態: タクシー・モビリティ（配車サービス）
# 想定人物: 配車サービス運営（利用者と運転手の声を整理）
# 業務領域: 配車待ち・料金・ドライバー対応への利用者の声のKJ分類と、サービス改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 配車の速さ（アルゴリズム・効率）と、運転手の稼働（労働・収入）の
#          トレードオフを矛盾検出で表面化し、配車アルゴリズムと乗務員施策の根拠に
#          する（効率と稼働のトレードオフ）。
TX_ID="biz-flow-taxi"
TX_DOC='{"version":1,"id":"'$TX_ID'","title":"配車と乗務員の声","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"tx1","text":"配車の速さは評価され、待ち時間は短いという声がある","x":0,"y":0,"textReviewed":true},{"id":"tx2","text":"運転手からは長時間勤務と収入の不安があるという声がある","x":10,"y":0,"textReviewed":true},{"id":"tx3","text":"料金の明確さは評価され、クレームは減っている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"tx-i","cardIds":["tx1","tx2","tx3"]}],"readingOrder":["tx-i"]}'

tx_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$TX_ID" \
  -H 'Content-Type: application/json' -d "$TX_DOC")
check "TX PUT document (作成)" "200" "$tx_put"

# ① AI束ね
tx_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"tx1","text":"配車の速さは評価され、待ち時間は短いという声がある","textReviewed":true},{"id":"tx2","text":"運転手からは長時間勤務と収入の不安があるという声がある","textReviewed":true},{"id":"tx3","text":"料金の明確さは評価され、クレームは減っている","textReviewed":true}]}')
case "$tx_groups" in *'"groups":'*) echo "  PASS: TX ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: TX ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
tx_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$TX_DOC,\"islandId\":\"tx-i\"}")
case "$tx_summary" in *'"groundingIds":["tx1","tx2","tx3"]'*) echo "  PASS: TX ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: TX ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（配車の速さ vs 乗務員の稼働・効率と稼働のトレードオフ）
tx_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"tx1","text":"配車の速さは評価され、待ち時間は短いという声がある","textReviewed":true},"cardB":{"id":"tx2","text":"運転手からは長時間勤務と収入の不安があるという声がある","textReviewed":true}}')
case "$tx_contra" in *'"hasContradiction"'*) echo "  PASS: TX ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: TX ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
tx_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$TX_DOC}")
case "$tx_narr" in *'"basedOnReadingOrder":["tx-i"]'*) echo "  PASS: TX ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: TX ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
tx_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$TX_ID")
check "TX 読戻し (200)" "200" "$tx_read"

echo ""
echo "--- シナリオ96: B2B・商社の貿易・輸出入（コスト削減と為替リスクのトレードオフ） ---"
# 業態: B2B・商社（貿易・輸出入）
# 想定人物: 貿易担当（輸出入の課題を整理）
# 業務領域: 輸出入・通関・為替・物流の課題のKJ分類と、貿易オペレーション改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: コスト削減（為替ヘッジの縮小）と取引の安定性（為替変動リスク）のトレードオフを
#          矛盾検出で表面化し、貿易戦略の根拠にする（コストとリスクのトレードオフ）。
TR_ID="biz-flow-trade"
TR_DOC='{"version":1,"id":"'$TR_ID'","title":"輸出入オペレーション整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"tr1","text":"コスト削減のため為替ヘッジを縮小したいとの意見","x":0,"y":0,"textReviewed":true},{"id":"tr2","text":"為替変動で取引の収益が不安定になっている","x":10,"y":0,"textReviewed":true},{"id":"tr3","text":"輸出入の通関手続きに時間がかかり納期に影響している","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"tr-i","cardIds":["tr1","tr2","tr3"]}],"readingOrder":["tr-i"]}'

tr_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$TR_ID" \
  -H 'Content-Type: application/json' -d "$TR_DOC")
check "TR PUT document (作成)" "200" "$tr_put"

# ① AI束ね
tr_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"tr1","text":"コスト削減のため為替ヘッジを縮小したいとの意見","textReviewed":true},{"id":"tr2","text":"為替変動で取引の収益が不安定になっている","textReviewed":true},{"id":"tr3","text":"輸出入の通関手続きに時間がかかり納期に影響している","textReviewed":true}]}')
case "$tr_groups" in *'"groups":'*) echo "  PASS: TR ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: TR ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
tr_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$TR_DOC,\"islandId\":\"tr-i\"}")
case "$tr_summary" in *'"groundingIds":["tr1","tr2","tr3"]'*) echo "  PASS: TR ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: TR ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（為替ヘッジ縮小 vs 為替変動リスク・コストとリスクのトレードオフ）
tr_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"tr1","text":"コスト削減のため為替ヘッジを縮小したいとの意見","textReviewed":true},"cardB":{"id":"tr2","text":"為替変動で取引の収益が不安定になっている","textReviewed":true}}')
case "$tr_contra" in *'"hasContradiction"'*) echo "  PASS: TR ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: TR ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
tr_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$TR_DOC}")
case "$tr_narr" in *'"basedOnReadingOrder":["tr-i"]'*) echo "  PASS: TR ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: TR ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
tr_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$TR_ID")
check "TR 読戻し (200)" "200" "$tr_read"

echo ""
echo "--- シナリオ97: 製薬・ヘルスケアのMR医療営業（情報の質と営業効率のトレードオフ） ---"
# 業態: 製薬・ヘルスケア（MR・医療営業）
# 想定人物: MR（医薬情報担当者）
# 業務領域: 医師・医療機関からのフィードバック（製品情報・学術・価格）のKJ分類と、営業・情報提供改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 製品の学術情報提供（エビデンスの正確性）と営業効率（訪問回数・コスト）の
#          トレードオフを矛盾検出で表面化し、情報提供戦略の根拠にする（情報の質と効率のトレードオフ）。
MR_ID="biz-flow-mr"
MR_DOC='{"version":1,"id":"'$MR_ID'","title":"MR医療営業フィードバック","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"mr1","text":"医師は最新の臨床データに基づく情報提供を求めている","x":0,"y":0,"textReviewed":true},{"id":"mr2","text":"営業効率のため訪問回数の見直しを検討する社内意見","x":10,"y":0,"textReviewed":true},{"id":"mr3","text":"医師からは医薬品の安全性に関する質問が増えている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"mr-i","cardIds":["mr1","mr2","mr3"]}],"readingOrder":["mr-i"]}'

mr_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$MR_ID" \
  -H 'Content-Type: application/json' -d "$MR_DOC")
check "MR PUT document (作成)" "200" "$mr_put"

# ① AI束ね
mr_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"mr1","text":"医師は最新の臨床データに基づく情報提供を求めている","textReviewed":true},{"id":"mr2","text":"営業効率のため訪問回数の見直しを検討する社内意見","textReviewed":true},{"id":"mr3","text":"医師からは医薬品の安全性に関する質問が増えている","textReviewed":true}]}')
case "$mr_groups" in *'"groups":'*) echo "  PASS: MR ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: MR ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
mr_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$MR_DOC,\"islandId\":\"mr-i\"}")
case "$mr_summary" in *'"groundingIds":["mr1","mr2","mr3"]'*) echo "  PASS: MR ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: MR ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（臨床データの情報提供 vs 訪問回数の見直し・情報の質と効率のトレードオフ）
mr_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"mr1","text":"医師は最新の臨床データに基づく情報提供を求めている","textReviewed":true},"cardB":{"id":"mr2","text":"営業効率のため訪問回数の見直しを検討する社内意見","textReviewed":true}}')
case "$mr_contra" in *'"hasContradiction"'*) echo "  PASS: MR ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: MR ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
mr_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$MR_DOC}")
case "$mr_narr" in *'"basedOnReadingOrder":["mr-i"]'*) echo "  PASS: MR ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: MR ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
mr_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$MR_ID")
check "MR 読戻し (200)" "200" "$mr_read"

echo ""
echo "--- シナリオ98: 物流・倉庫の配送オペレーション（配送スピードと配送コストのトレードオフ） ---"
# 業態: 物流・倉庫（配送/3PL）
# 想定人物: 物流マネージャー（配送オペレーションを整理）
# 業務領域: 配送・在庫・倉庫オペレーションの課題のKJ分類と、改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 配送スピード（即日配達）と配送コスト（トラック積載率）のトレードオフを
#          矛盾検出で表面化し、オペレーション改善の根拠にする（スピードとコストのトレードオフ）。
LG_ID="biz-flow-logistics"
LG_DOC='{"version":1,"id":"'$LG_ID'","title":"配送オペレーション整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"lg1","text":"即日配達への期待が高まり配送スピードを求められている","x":0,"y":0,"textReviewed":true},{"id":"lg2","text":"トラック積載率が低く配送コストが膨らんでいる","x":10,"y":0,"textReviewed":true},{"id":"lg3","text":"在庫の欠品・過剰在庫のバランスに課題がある","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"lg-i","cardIds":["lg1","lg2","lg3"]}],"readingOrder":["lg-i"]}'

lg_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$LG_ID" \
  -H 'Content-Type: application/json' -d "$LG_DOC")
check "LG PUT document (作成)" "200" "$lg_put"

# ① AI束ね
lg_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"lg1","text":"即日配達への期待が高まり配送スピードを求められている","textReviewed":true},{"id":"lg2","text":"トラック積載率が低く配送コストが膨らんでいる","textReviewed":true},{"id":"lg3","text":"在庫の欠品・過剰在庫のバランスに課題がある","textReviewed":true}]}')
case "$lg_groups" in *'"groups":'*) echo "  PASS: LG ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: LG ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
lg_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$LG_DOC,\"islandId\":\"lg-i\"}")
case "$lg_summary" in *'"groundingIds":["lg1","lg2","lg3"]'*) echo "  PASS: LG ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: LG ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（即日配達 vs 配送コスト・スピードとコストのトレードオフ）
lg_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"lg1","text":"即日配達への期待が高まり配送スピードを求められている","textReviewed":true},"cardB":{"id":"lg2","text":"トラック積載率が低く配送コストが膨らんでいる","textReviewed":true}}')
case "$lg_contra" in *'"hasContradiction"'*) echo "  PASS: LG ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: LG ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
lg_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$LG_DOC}")
case "$lg_narr" in *'"basedOnReadingOrder":["lg-i"]'*) echo "  PASS: LG ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: LG ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
lg_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$LG_ID")
check "LG 読戻し (200)" "200" "$lg_read"

echo ""
echo "--- シナリオ99: 図書館・読書振興の利用者声と蔵書構成の整理（蔵書と出会いの乖離） ---"
# 業態: 図書館・読書振興（公共図書館）
# 想定人物: 図書館員（利用者と非利用者の声を整理）
# 業務領域: 蔵書・貸出・読書イベントへの利用者の声のKJ分類と、読書振興施策改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 蔵書の充実（新刊購入・コスト）と、利用者の読みたい本への出会い（体験・
#          検索性）の乖離を矛盾検出で表面化し、蔵書構成と読書振興の根拠にする
#          （蔵書と出会いの乖離）。
LB_ID="biz-flow-library"
LB_DOC='{"version":1,"id":"'$LB_ID'","title":"利用者声と蔵書構成","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"lb1","text":"蔵書は充実し、新刊の購入が続いていると運営は評価している","x":0,"y":0,"textReviewed":true},{"id":"lb2","text":"利用者からは読みたい本を見つけにくいという声がある","x":10,"y":0,"textReviewed":true},{"id":"lb3","text":"子ども向けの読み聞かせは人気で、家族連れの利用は増えている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"lb-i","cardIds":["lb1","lb2","lb3"]}],"readingOrder":["lb-i"]}'

lb_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$LB_ID" \
  -H 'Content-Type: application/json' -d "$LB_DOC")
check "LB PUT document (作成)" "200" "$lb_put"

# ① AI束ね
lb_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"lb1","text":"蔵書は充実し、新刊の購入が続いていると運営は評価している","textReviewed":true},{"id":"lb2","text":"利用者からは読みたい本を見つけにくいという声がある","textReviewed":true},{"id":"lb3","text":"子ども向けの読み聞かせは人気で、家族連れの利用は増えている","textReviewed":true}]}')
case "$lb_groups" in *'"groups":'*) echo "  PASS: LB ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: LB ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
lb_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$LB_DOC,\"islandId\":\"lb-i\"}")
case "$lb_summary" in *'"groundingIds":["lb1","lb2","lb3"]'*) echo "  PASS: LB ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: LB ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（蔵書充実 vs 出会いにくさ・蔵書と出会いの乖離）
lb_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"lb1","text":"蔵書は充実し、新刊の購入が続いていると運営は評価している","textReviewed":true},"cardB":{"id":"lb2","text":"利用者からは読みたい本を見つけにくいという声がある","textReviewed":true}}')
case "$lb_contra" in *'"hasContradiction"'*) echo "  PASS: LB ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: LB ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
lb_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$LB_DOC}")
case "$lb_narr" in *'"basedOnReadingOrder":["lb-i"]'*) echo "  PASS: LB ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: LB ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
lb_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$LB_ID")
check "LB 読戻し (200)" "200" "$lb_read"

echo ""
echo "--- シナリオ100: カフェ・喫茶チェーンの店舗オペレーションと顧客体験の整理（回転と滞在の乖離） ---"
# 業態: カフェ・喫茶チェーン（カフェチェーン運営）
# 想定人物: 店舗運営担当（顧客の声を整理）
# 業務領域: メニュー・店舗・接客への顧客の声のKJ分類と、店舗運営改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 店舗の回転率（客単価・席回転）と、顧客の滞在体験（ゆっくり過ごしたい・
#          作業したい）の乖離を矛盾検出で表面化し、店舗運営と席構成の根拠にする
#          （回転と滞在の乖離）。
CF_ID="biz-flow-cafe"
CF_DOC='{"version":1,"id":"'$CF_ID'","title":"店舗オペレーションと顧客体験","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"cf1","text":"席の回転は速く、客単価の向上は順調だと運営は評価している","x":0,"y":0,"textReviewed":true},{"id":"cf2","text":"顧客からはゆっくり過ごしたいが、席の滞在時間を気にしてしまうという声がある","x":10,"y":0,"textReviewed":true},{"id":"cf3","text":"季節限定メニューは好評で、新規客の来店は増えている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"cf-i","cardIds":["cf1","cf2","cf3"]}],"readingOrder":["cf-i"]}'

cf_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$CF_ID" \
  -H 'Content-Type: application/json' -d "$CF_DOC")
check "CF PUT document (作成)" "200" "$cf_put"

# ① AI束ね
cf_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"cf1","text":"席の回転は速く、客単価の向上は順調だと運営は評価している","textReviewed":true},{"id":"cf2","text":"顧客からはゆっくり過ごしたいが、席の滞在時間を気にしてしまうという声がある","textReviewed":true},{"id":"cf3","text":"季節限定メニューは好評で、新規客の来店は増えている","textReviewed":true}]}')
case "$cf_groups" in *'"groups":'*) echo "  PASS: CF ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: CF ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
cf_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$CF_DOC,\"islandId\":\"cf-i\"}")
case "$cf_summary" in *'"groundingIds":["cf1","cf2","cf3"]'*) echo "  PASS: CF ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: CF ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（回転率 vs 滞在体験・回転と滞在の乖離）
cf_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"cf1","text":"席の回転は速く、客単価の向上は順調だと運営は評価している","textReviewed":true},"cardB":{"id":"cf2","text":"顧客からはゆっくり過ごしたいが、席の滞在時間を気にしてしまうという声がある","textReviewed":true}}')
case "$cf_contra" in *'"hasContradiction"'*) echo "  PASS: CF ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: CF ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
cf_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$CF_DOC}")
case "$cf_narr" in *'"basedOnReadingOrder":["cf-i"]'*) echo "  PASS: CF ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: CF ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
cf_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$CF_ID")
check "CF 読戻し (200)" "200" "$cf_read"

echo ""
echo "--- シナリオ101: 教育・学習塾の運営（指導の質と料金のトレードオフ） ---"
# 業態: 教育・学習塾（進学塾/塾）
# 想定人物: 塾長（保護者・生徒の声を整理）
# 業務領域: 保護者・生徒からのフィードバック（指導・進路・料金）のKJ分類と、塾運営改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 指導の質の向上（少人数・個別指導）と料金（保護者の負担感）のトレードオフを
#          矛盾検出で表面化し、塾運営の根拠にする（質と料金のトレードオフ）。
JU_ID="biz-flow-juku"
JU_DOC='{"version":1,"id":"'$JU_ID'","title":"塾運営フィードバック","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"ju1","text":"保護者は少人数・個別指導を求めている","x":0,"y":0,"textReviewed":true},{"id":"ju2","text":"個別指導の拡充には料金改定が必要との意見","x":10,"y":0,"textReviewed":true},{"id":"ju3","text":"生徒の志望校合格実績が集客につながっている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"ju-i","cardIds":["ju1","ju2","ju3"]}],"readingOrder":["ju-i"]}'

ju_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$JU_ID" \
  -H 'Content-Type: application/json' -d "$JU_DOC")
check "JU PUT document (作成)" "200" "$ju_put"

# ① AI束ね
ju_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"ju1","text":"保護者は少人数・個別指導を求めている","textReviewed":true},{"id":"ju2","text":"個別指導の拡充には料金改定が必要との意見","textReviewed":true},{"id":"ju3","text":"生徒の志望校合格実績が集客につながっている","textReviewed":true}]}')
case "$ju_groups" in *'"groups":'*) echo "  PASS: JU ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: JU ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
ju_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$JU_DOC,\"islandId\":\"ju-i\"}")
case "$ju_summary" in *'"groundingIds":["ju1","ju2","ju3"]'*) echo "  PASS: JU ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: JU ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（個別指導の要望 vs 料金改定・質と料金のトレードオフ）
ju_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"ju1","text":"保護者は少人数・個別指導を求めている","textReviewed":true},"cardB":{"id":"ju2","text":"個別指導の拡充には料金改定が必要との意見","textReviewed":true}}')
case "$ju_contra" in *'"hasContradiction"'*) echo "  PASS: JU ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: JU ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
ju_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$JU_DOC}")
case "$ju_narr" in *'"basedOnReadingOrder":["ju-i"]'*) echo "  PASS: JU ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: JU ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
ju_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$JU_ID")
check "JU 読戻し (200)" "200" "$ju_read"

echo ""
echo "--- シナリオ102: コンタクトセンターの通話品質管理（効率と品質のトレードオフ） ---"
# 業態: コンタクトセンター（BPO/インハウス）
# 想定人物: 品質管理担当（通話品質を分析）
# 業務領域: 通話記録・顧客満足・オペレーター評価のKJ分類と、品質改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 応対時間の短縮（効率・コスト）と丁寧な対応（顧客満足・品質）のトレードオフを
#          矛盾検出で表面化し、品質基準の根拠にする（効率と品質のトレードオフ）。
CC_ID="biz-flow-callcenter"
CC_DOC='{"version":1,"id":"'$CC_ID'","title":"通話品質分析","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"cc1","text":"オペレーターの応対時間が長くコストがかかっている","x":0,"y":0,"textReviewed":true},{"id":"cc2","text":"顧客は丁寧な説明を評価しているが待ち時間が長い","x":10,"y":0,"textReviewed":true},{"id":"cc3","text":"解決率が低下しており再問い合わせが増えている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"cc-i","cardIds":["cc1","cc2","cc3"]}],"readingOrder":["cc-i"]}'

cc_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$CC_ID" \
  -H 'Content-Type: application/json' -d "$CC_DOC")
check "CC PUT document (作成)" "200" "$cc_put"

# ① AI束ね
cc_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"cc1","text":"オペレーターの応対時間が長くコストがかかっている","textReviewed":true},{"id":"cc2","text":"顧客は丁寧な説明を評価しているが待ち時間が長い","textReviewed":true},{"id":"cc3","text":"解決率が低下しており再問い合わせが増えている","textReviewed":true}]}')
case "$cc_groups" in *'"groups":'*) echo "  PASS: CC ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: CC ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
cc_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$CC_DOC,\"islandId\":\"cc-i\"}")
case "$cc_summary" in *'"groundingIds":["cc1","cc2","cc3"]'*) echo "  PASS: CC ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: CC ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（応対時間の長さ vs 丁寧さの評価・効率と品質のトレードオフ）
cc_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"cc1","text":"オペレーターの応対時間が長くコストがかかっている","textReviewed":true},"cardB":{"id":"cc2","text":"顧客は丁寧な説明を評価しているが待ち時間が長い","textReviewed":true}}')
case "$cc_contra" in *'"hasContradiction"'*) echo "  PASS: CC ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: CC ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
cc_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$CC_DOC}")
case "$cc_narr" in *'"basedOnReadingOrder":["cc-i"]'*) echo "  PASS: CC ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: CC ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
cc_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$CC_ID")
check "CC 読戻し (200)" "200" "$cc_read"

echo ""
echo "--- シナリオ103: 自治体・上下水道の水道事業運営（安全確保と利用者負担のトレードオフ） ---"
# 業態: 自治体・上下水道（水道事業）
# 想定人物: 水道事業担当（水質・料金・老朽化の課題を整理）
# 業務領域: 水質・料金・施設老朽化・給水停止の課題のKJ分類と、事業運営改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 水質の安全確保（検査・設備投資）と料金（利用者の負担感）のトレードオフを
#          矛盾検出で表面化し、事業計画の根拠にする（安全と負担のトレードオフ）。
WS_ID="biz-flow-watersupply"
WS_DOC='{"version":1,"id":"'$WS_ID'","title":"水道事業課題整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"ws1","text":"老朽化した水道管の更新投資が必要との技術的見解","x":0,"y":0,"textReviewed":true},{"id":"ws2","text":"水道料金の値上げは利用者の負担が大きいという懸念","x":10,"y":0,"textReviewed":true},{"id":"ws3","text":"水質検査の基準は維持し安全を確保すべきとの意見","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"ws-i","cardIds":["ws1","ws2","ws3"]}],"readingOrder":["ws-i"]}'

ws_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$WS_ID" \
  -H 'Content-Type: application/json' -d "$WS_DOC")
check "WS PUT document (作成)" "200" "$ws_put"

# ① AI束ね
ws_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"ws1","text":"老朽化した水道管の更新投資が必要との技術的見解","textReviewed":true},{"id":"ws2","text":"水道料金の値上げは利用者の負担が大きいという懸念","textReviewed":true},{"id":"ws3","text":"水質検査の基準は維持し安全を確保すべきとの意見","textReviewed":true}]}')
case "$ws_groups" in *'"groups":'*) echo "  PASS: WS ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: WS ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
ws_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$WS_DOC,\"islandId\":\"ws-i\"}")
case "$ws_summary" in *'"groundingIds":["ws1","ws2","ws3"]'*) echo "  PASS: WS ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: WS ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（老朽化更新投資 vs 料金値上げの負担・安全と負担のトレードオフ）
ws_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"ws1","text":"老朽化した水道管の更新投資が必要との技術的見解","textReviewed":true},"cardB":{"id":"ws2","text":"水道料金の値上げは利用者の負担が大きいという懸念","textReviewed":true}}')
case "$ws_contra" in *'"hasContradiction"'*) echo "  PASS: WS ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: WS ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
ws_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$WS_DOC}")
case "$ws_narr" in *'"basedOnReadingOrder":["ws-i"]'*) echo "  PASS: WS ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: WS ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
ws_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$WS_ID")
check "WS 読戻し (200)" "200" "$ws_read"

echo ""
echo "--- シナリオ104: 通信・OTTのメッセージングアプリ運用（収益化とユーザー体験のトレードオフ） ---"
# 業態: 通信・OTT（メッセージング/SNSプラットフォーム）
# 想定人物: プラットフォーム運営担当（コミュニティ・収益化を整理）
# 業務領域: ユーザー行動・収益化・信頼性の課題のKJ分類と、プラットフォーム改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 収益化（広告・課金）とユーザー体験（プライバシー・快適性）のトレードオフを
#          矛盾検出で表面化し、プラットフォーム運営の根拠にする（収益と体験のトレードオフ）。
OT_ID="biz-flow-ott"
OT_DOC='{"version":1,"id":"'$OT_ID'","title":"プラットフォーム運営整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"ot1","text":"広告収益を増やすため表示を増やしたいとの意見","x":0,"y":0,"textReviewed":true},{"id":"ot2","text":"広告表示の増加でユーザー体験が悪化し離脱が増えている","x":10,"y":0,"textReviewed":true},{"id":"ot3","text":"プライバシー保護の強化を求めるユーザーの声が強い","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"ot-i","cardIds":["ot1","ot2","ot3"]}],"readingOrder":["ot-i"]}'

ot_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$OT_ID" \
  -H 'Content-Type: application/json' -d "$OT_DOC")
check "OT PUT document (作成)" "200" "$ot_put"

# ① AI束ね
ot_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"ot1","text":"広告収益を増やすため表示を増やしたいとの意見","textReviewed":true},{"id":"ot2","text":"広告表示の増加でユーザー体験が悪化し離脱が増えている","textReviewed":true},{"id":"ot3","text":"プライバシー保護の強化を求めるユーザーの声が強い","textReviewed":true}]}')
case "$ot_groups" in *'"groups":'*) echo "  PASS: OT ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: OT ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
ot_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$OT_DOC,\"islandId\":\"ot-i\"}")
case "$ot_summary" in *'"groundingIds":["ot1","ot2","ot3"]'*) echo "  PASS: OT ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: OT ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（広告収益の増加 vs ユーザー体験の悪化・収益と体験のトレードオフ）
ot_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"ot1","text":"広告収益を増やすため表示を増やしたいとの意見","textReviewed":true},"cardB":{"id":"ot2","text":"広告表示の増加でユーザー体験が悪化し離脱が増えている","textReviewed":true}}')
case "$ot_contra" in *'"hasContradiction"'*) echo "  PASS: OT ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: OT ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
ot_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$OT_DOC}")
case "$ot_narr" in *'"basedOnReadingOrder":["ot-i"]'*) echo "  PASS: OT ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: OT ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
ot_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$OT_ID")
check "OT 読戻し (200)" "200" "$ot_read"

echo ""
echo "--- シナリオ105: 自治体・消防の救急出動分析（迅速な出動と適切な搬送のトレードオフ） ---"
# 業態: 自治体・消防（消防/救急）
# 想定人物: 消防署長／救急運用担当（救急出動を分析）
# 業務領域: 救急出動記録・通報内容・対応課題のKJ分類と、救急運用改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 迅速な出動（レスポンスタイム）と適切な医療搬送（搬送先選定・トリアージ）の
#          トレードオフを矛盾検出で表面化し、救急運用の根拠にする（迅速性と適切性のトレードオフ）。
FD_ID="biz-flow-fire"
FD_DOC='{"version":1,"id":"'$FD_ID'","title":"救急出動分析","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"fd1","text":"救急要請が増加し迅速な出動が難しくなっている","x":0,"y":0,"textReviewed":true},{"id":"fd2","text":"搬送先の選定に時間がかかり病院到着が遅れている","x":10,"y":0,"textReviewed":true},{"id":"fd3","text":"軽症の救急要請が増えており現場の負担が増大している","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"fd-i","cardIds":["fd1","fd2","fd3"]}],"readingOrder":["fd-i"]}'

fd_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$FD_ID" \
  -H 'Content-Type: application/json' -d "$FD_DOC")
check "FD PUT document (作成)" "200" "$fd_put"

# ① AI束ね
fd_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"fd1","text":"救急要請が増加し迅速な出動が難しくなっている","textReviewed":true},{"id":"fd2","text":"搬送先の選定に時間がかかり病院到着が遅れている","textReviewed":true},{"id":"fd3","text":"軽症の救急要請が増えており現場の負担が増大している","textReviewed":true}]}')
case "$fd_groups" in *'"groups":'*) echo "  PASS: FD ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: FD ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
fd_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$FD_DOC,\"islandId\":\"fd-i\"}")
case "$fd_summary" in *'"groundingIds":["fd1","fd2","fd3"]'*) echo "  PASS: FD ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: FD ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（迅速な出動 vs 適切な搬送・迅速性と適切性のトレードオフ）
fd_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"fd1","text":"救急要請が増加し迅速な出動が難しくなっている","textReviewed":true},"cardB":{"id":"fd2","text":"搬送先の選定に時間がかかり病院到着が遅れている","textReviewed":true}}')
case "$fd_contra" in *'"hasContradiction"'*) echo "  PASS: FD ③矛盾検出"; PASS=$((PASS+1));; *) echo "  FAIL: FD ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
fd_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$FD_DOC}")
case "$fd_narr" in *'"basedOnReadingOrder":["fd-i"]'*) echo "  PASS: FD ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: FD ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
fd_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$FD_ID")
check "FD 読戻し (200)" "200" "$fd_read"

echo ""
echo "--- シナリオ106: 警察・公安の地域防犯計画（防犯強化と住民のプライバシーのトレードオフ） ---"
# 業態: 警察・公安（警察署・地域安全）
# 想定人物: 地域安全担当（防犯係・パトロール計画立案者）
# 業務領域: 住民の防犯情報・パトロール報告・地域安全の声のKJ分類と、パトロール配置・防犯施策の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> 島間関係要約(summarize-island-relation)
#          -> ナラティブ(generate-narrative) -> 読戻し
# 注意事項: 防犯強化（重点配備・カメラ増設による抑止）と住民の安心・プライバシー（過度な監視への
#          懸念・住民主体の見守り）のトレードオフを矛盾検出で表面化し、施策の根拠にする。
#          関係要約は提案のみ（自動適用なし）。
PL_ID="biz-flow-police"
PL_DOC='{"version":1,"id":"'$PL_ID'","title":"地域防犯計画の整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"p1","text":"夜間の犯罪多発地区へのパトロール重点配備を求める声（防犯強化と住民のプライバシーはトレードオフ）","x":0,"y":0,"textReviewed":true},{"id":"p2","text":"防犯カメラの増設は犯罪抑止に効果的との指摘","x":10,"y":0,"textReviewed":true},{"id":"p3","text":"過度な監視への不安や、住民の見守り活動の重要性を訴える声","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"pl-a","cardIds":["p1","p2"]},{"id":"pl-b","cardIds":["p3"]}],"readingOrder":["pl-a","pl-b"]}'

pl_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$PL_ID" \
  -H 'Content-Type: application/json' -d "$PL_DOC")
check "PL PUT document (作成)" "200" "$pl_put"

# ① AI束ね
pl_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"p1","text":"夜間の犯罪多発地区へのパトロール重点配備を求める声（防犯強化と住民のプライバシーはトレードオフ）","textReviewed":true},{"id":"p2","text":"防犯カメラの増設は犯罪抑止に効果的との指摘","textReviewed":true},{"id":"p3","text":"過度な監視への不安や、住民の見守り活動の重要性を訴える声","textReviewed":true}]}')
case "$pl_groups" in *'"groups":'*) echo "  PASS: PL ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: PL ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約（防犯強化・抑止の島）
pl_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$PL_DOC,\"islandId\":\"pl-a\"}")
case "$pl_summary" in *'"groundingIds":["p1","p2"]'*) echo "  PASS: PL ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: PL ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（防犯強化・重点配備 vs 監視への不安・防犯強化とプライバシーのトレードオフ）
pl_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"p1","text":"夜間の犯罪多発地区へのパトロール重点配備を求める声（防犯強化と住民のプライバシーはトレードオフ）","textReviewed":true},"cardB":{"id":"p3","text":"過度な監視への不安や、住民の見守り活動の重要性を訴える声","textReviewed":true}}')
case "$pl_contra" in *'"hasContradiction":true'*) echo "  PASS: PL ③矛盾検出（防犯強化とプライバシーのトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: PL ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ 島間関係の要約（重点配備・カメラ増設の強化 → 住民の監視不安 の因果）
pl_rel=$(curl -s -X POST "$BASE_URL/ai/summarize-island-relation" -H 'Content-Type: application/json' \
  -d "{\"doc\":$PL_DOC,\"islandAId\":\"pl-a\",\"islandBId\":\"pl-b\",\"relationType\":\"causal\",\"derived\":false,\"groundingCardIds\":[\"p3\"],\"groundingEdgeIds\":[],\"cardTexts\":[{\"id\":\"p3\",\"text\":\"過度な監視への不安や、住民の見守り活動の重要性を訴える声\"}]}")
case "$pl_rel" in *'"text"'*) echo "  PASS: PL ④島間関係の要約 (causal)"; PASS=$((PASS+1));; *) echo "  FAIL: PL ④関係要約 (${pl_rel:0:100})"; FAIL=$((FAIL+1));; esac

# ⑤ ナラティブ
pl_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$PL_DOC}")
case "$pl_narr" in *'"basedOnReadingOrder":["pl-a","pl-b"]'*) echo "  PASS: PL ⑤ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: PL ⑤ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
pl_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$PL_ID")
check "PL 読戻し (200)" "200" "$pl_read"

echo ""
echo "--- シナリオ107: データセンター運用（省電力化と信頼性のトレードオフ） ---"
# 業態: IT・データセンター（データセンター運営）
# 想定人物: データセンター運用マネージャー／施設管理担当
# 業務領域: 設備点検・障害対応・テナント要求のKJ分類と、運用改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction) -> ナラティブ(generate-narrative)
#          -> A/B照合(check-narrative) -> 読戻し
# 注意事項: 省電力化（PUE・コスト）と信頼性・可用性（SLA・冗長構成）のトレードオフを矛盾検出
#          （正パス）で表面化し、運用方針の根拠にする。ナラティブはA/B照合で島の取りこぼしを
#          検出（check-narrative の正パスは島IDに依存しない・DOGFOOD-12）。
DC_ID="biz-flow-datacenter"
DC_DOC='{"version":1,"id":"'$DC_ID'","title":"データセンター運用改善の整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"dc1","text":"省電力化のため冷却設備の稼働を抑えたい","x":0,"y":0,"textReviewed":true},{"id":"dc2","text":"冷却抑制はサーバー停止リスクとトレードオフになるため冗長構成は外せない","x":10,"y":0,"textReviewed":true},{"id":"dc3","text":"テナントからは稼働率保証(SLA)の維持を求められている","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"dc-i","cardIds":["dc1","dc2","dc3"]}],"readingOrder":["dc-i"]}'

dc_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$DC_ID" \
  -H 'Content-Type: application/json' -d "$DC_DOC")
check "DC PUT document (作成)" "200" "$dc_put"

# ① AI束ね
dc_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"dc1","text":"省電力化のため冷却設備の稼働を抑えたい","textReviewed":true},{"id":"dc2","text":"冷却抑制はサーバー停止リスクとトレードオフになるため冗長構成は外せない","textReviewed":true},{"id":"dc3","text":"テナントからは稼働率保証(SLA)の維持を求められている","textReviewed":true}]}')
case "$dc_groups" in *'"groups":'*) echo "  PASS: DC ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: DC ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
dc_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$DC_DOC,\"islandId\":\"dc-i\"}")
case "$dc_summary" in *'"groundingIds":["dc1","dc2","dc3"]'*) echo "  PASS: DC ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: DC ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（省電力化 vs 冗長維持・省電力と信頼性のトレードオフ・正パス）
dc_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"dc1","text":"省電力化のため冷却設備の稼働を抑えたい","textReviewed":true},"cardB":{"id":"dc2","text":"冷却抑制はサーバー停止リスクとトレードオフになるため冗長構成は外せない","textReviewed":true}}')
case "$dc_contra" in *'"hasContradiction":true'*) echo "  PASS: DC ③矛盾検出（省電力と信頼性のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: DC ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
dc_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$DC_DOC}")
case "$dc_narr" in *'"basedOnReadingOrder":["dc-i"]'*) echo "  PASS: DC ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: DC ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ A/B照合（ナラティブが島dc-iに触れていない・a_missing_in_b・島ID非依存の正パス）
dc_ab=$(curl -s -X POST "$BASE_URL/ai/check-narrative" -H 'Content-Type: application/json' \
  -d "{\"doc\":$DC_DOC,\"narrativeText\":\"（草稿）省電力化と信頼性の両立を検討し運用改善を進める。ただし冷却最適化には未検証の主張が含まれる。\",\"basedOnReadingOrder\":[\"dc-i\"]}")
case "$dc_ab" in *'ナラティブが島dc-iに触れていない'*'"aMissingInB":1'*) echo "  PASS: DC ⑤A/B照合（島dc-iの取りこぼし・a_missing_in_b・島ID非依存）"; PASS=$((PASS+1));; *) echo "  FAIL: DC ⑤A/B照合（${dc_ab:0:150}）"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
dc_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$DC_ID")
check "DC 読戻し (200)" "200" "$dc_read"

echo ""
echo "--- シナリオ108: 自治体・廃棄物処理（3R推進と住民負担のトレードオフ） ---"
# 業態: 自治体・廃棄物処理（ごみ処理・3R）
# 想定人物: 廃棄物管理担当（クリーンセンター／ごみ行政担当）
# 業務領域: 収集・分別・処理の課題と住民の声のKJ分類と、3R施策の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary・4カード島の全接地)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> A/B照合(check-narrative) -> 読戻し
# 注意事項: 3R推進（分別徹底・リサイクル拡大による環境負荷削減）と住民の負担・処理コスト
#          （分別ルールの複雑化・施設老朽化）のトレードオフを矛盾検出（正パス）で表面化し、
#          施策の根拠にする。島要約は4カード島の全接地（DOGFOOD-13）で固定。
WM_ID="biz-flow-wastemgmt"
WM_DOC='{"version":1,"id":"'$WM_ID'","title":"廃棄物処理・3R施策の整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"w1","text":"分別徹底とリサイクル拡大で埋立量を減らしたい（3R・環境負荷削減）","x":0,"y":0,"textReviewed":true},{"id":"w2","text":"分別の徹底は住民の手間・負担とトレードオフになる（分別ルールの複雑化で不満）","x":10,"y":0,"textReviewed":true},{"id":"w3","text":"処理施設の老朽化で改修費用が必要（処理コスト）","x":20,"y":0,"textReviewed":true},{"id":"w4","text":"生ごみ・食品ロスの減量で処理量を抑えたい（発生抑制）","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"wm-i","cardIds":["w1","w2","w3","w4"]}],"readingOrder":["wm-i"]}'

wm_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$WM_ID" \
  -H 'Content-Type: application/json' -d "$WM_DOC")
check "WM PUT document (作成)" "200" "$wm_put"

# ① AI束ね
wm_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"w1","text":"分別徹底とリサイクル拡大で埋立量を減らしたい（3R・環境負荷削減）","textReviewed":true},{"id":"w2","text":"分別の徹底は住民の手間・負担とトレードオフになる（分別ルールの複雑化で不満）","textReviewed":true},{"id":"w3","text":"処理施設の老朽化で改修費用が必要（処理コスト）","textReviewed":true},{"id":"w4","text":"生ごみ・食品ロスの減量で処理量を抑えたい（発生抑制）","textReviewed":true}]}')
case "$wm_groups" in *'"groups":'*) echo "  PASS: WM ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: WM ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約（4カード島の全接地・DOGFOOD-13）
wm_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$WM_DOC,\"islandId\":\"wm-i\"}")
case "$wm_summary" in *'"groundingIds":["w1","w2","w3","w4"]'*) echo "  PASS: WM ②島要約（4カード島の全接地・DOGFOOD-13）"; PASS=$((PASS+1));; *) echo "  FAIL: WM ②島要約（${wm_summary:0:150}）"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（3R推進 vs 住民負担・3Rと負担のトレードオフ・正パス）
wm_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"w1","text":"分別徹底とリサイクル拡大で埋立量を減らしたい（3R・環境負荷削減）","textReviewed":true},"cardB":{"id":"w2","text":"分別の徹底は住民の手間・負担とトレードオフになる（分別ルールの複雑化で不満）","textReviewed":true}}')
case "$wm_contra" in *'"hasContradiction":true'*) echo "  PASS: WM ③矛盾検出（3Rと住民負担のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: WM ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
wm_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$WM_DOC}")
case "$wm_narr" in *'"basedOnReadingOrder":["wm-i"]'*) echo "  PASS: WM ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: WM ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ A/B照合（ナラティブが島wm-iに触れていない・a_missing_in_b）
wm_ab=$(curl -s -X POST "$BASE_URL/ai/check-narrative" -H 'Content-Type: application/json' \
  -d "{\"doc\":$WM_DOC,\"narrativeText\":\"（草稿）3R推進と住民負担のバランスを検討する。ただし発生抑制策には未検証の主張が含まれる。\",\"basedOnReadingOrder\":[\"wm-i\"]}")
case "$wm_ab" in *'ナラティブが島wm-iに触れていない'*'"aMissingInB":1'*) echo "  PASS: WM ⑤A/B照合（島wm-iの取りこぼし・a_missing_in_b）"; PASS=$((PASS+1));; *) echo "  FAIL: WM ⑤A/B照合（${wm_ab:0:150}）"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
wm_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$WM_ID")
check "WM 読戻し (200)" "200" "$wm_read"

echo ""
echo "--- シナリオ109: 放送局・番組編成（商業性と公共性のトレードオフ） ---"
# 業態: 放送・メディア（テレビ局・番組編成）
# 想定人物: 編成担当／プロデューサー（番組編成方針を分析）
# 業務領域: 視聴率・番組評価・視聴者からの声のKJ分類と、編成方針の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary・4カード島の全接地)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> A/B照合(check-narrative・b_missing_in_a) -> 読戻し
# 注意事項: 商業性（広告収益・高視聴率番組への集中投資）と公共性（教養・報道番組の維持）の
#          トレードオフを矛盾検出（正パス）で表面化し、編成方針の根拠にする。ナラティブが
#          カードの根拠を欠く主張を含む場合は A/B照合で b_missing_in_a を報告（DOGFOOD-14・
#          双方向の正パス固定）。
BC_ID="biz-flow-broadcast"
BC_DOC='{"version":1,"id":"'$BC_ID'","title":"番組編成方針の整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"b1","text":"若年層のテレビ離れが進み視聴率が低下している（視聴率・若年層）","x":0,"y":0,"textReviewed":true},{"id":"b2","text":"広告収益を支える高視聴率番組への集中投資は編成の自由とトレードオフになる（商業性）","x":10,"y":0,"textReviewed":true},{"id":"b3","text":"公共放送として教養・報道番組の維持を求める声（公共性・使命）","x":20,"y":0,"textReviewed":true},{"id":"b4","text":"視聴者からは番組編成のマンネリ化への不満がある（編成・マンネリ）","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"bcast-i","cardIds":["b1","b2","b3","b4"]}],"readingOrder":["bcast-i"]}'

bc_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$BC_ID" \
  -H 'Content-Type: application/json' -d "$BC_DOC")
check "BC PUT document (作成)" "200" "$bc_put"

# ① AI束ね
bc_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"b1","text":"若年層のテレビ離れが進み視聴率が低下している（視聴率・若年層）","textReviewed":true},{"id":"b2","text":"広告収益を支える高視聴率番組への集中投資は編成の自由とトレードオフになる（商業性）","textReviewed":true},{"id":"b3","text":"公共放送として教養・報道番組の維持を求める声（公共性・使命）","textReviewed":true},{"id":"b4","text":"視聴者からは番組編成のマンネリ化への不満がある（編成・マンネリ）","textReviewed":true}]}')
case "$bc_groups" in *'"groups":'*) echo "  PASS: BC ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: BC ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約（4カード島の全接地）
bc_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$BC_DOC,\"islandId\":\"bcast-i\"}")
case "$bc_summary" in *'"groundingIds":["b1","b2","b3","b4"]'*) echo "  PASS: BC ②島要約（4カード島の全接地）"; PASS=$((PASS+1));; *) echo "  FAIL: BC ②島要約（${bc_summary:0:150}）"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（商業性 vs 公共性・商業と公共のトレードオフ・正パス）
bc_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"b2","text":"広告収益を支える高視聴率番組への集中投資は編成の自由とトレードオフになる（商業性）","textReviewed":true},"cardB":{"id":"b3","text":"公共放送として教養・報道番組の維持を求める声（公共性・使命）","textReviewed":true}}')
case "$bc_contra" in *'"hasContradiction":true'*) echo "  PASS: BC ③矛盾検出（商業性と公共性のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: BC ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
bc_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$BC_DOC}")
case "$bc_narr" in *'"basedOnReadingOrder":["bcast-i"]'*) echo "  PASS: BC ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: BC ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ A/B照合（ナラティブがカードの根拠を欠く主張を含む・b_missing_in_a・DOGFOOD-14）
bc_ab=$(curl -s -X POST "$BASE_URL/ai/check-narrative" -H 'Content-Type: application/json' \
  -d "{\"doc\":$BC_DOC,\"narrativeText\":\"（草稿）若年層離れに対応するため若者向け番組を強化する。なお視聴者満足度が過去最高を記録したという根拠のない主張も含まれる。\",\"basedOnReadingOrder\":[\"bcast-i\"]}")
case "$bc_ab" in *'"direction":"b_missing_in_a"'*'"bMissingInA":1'*) echo "  PASS: BC ⑤A/B照合（根拠のない主張・b_missing_in_a・双方向の正パス）"; PASS=$((PASS+1));; *) echo "  FAIL: BC ⑤A/B照合（${bc_ab:0:150}）"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
bc_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$BC_ID")
check "BC 読戻し (200)" "200" "$bc_read"

echo ""
echo "--- シナリオ110: 水族館・動物園の運営（体験価値と運営コストのトレードオフ） ---"
# 業態: レジャー・動物園（水族館／動物園運営）
# 想定人物: 施設運営責任者／飼育担当マネージャー
# 業務領域: 来園者の声・展示・動物福祉・運営コストのKJ分類と、施設運営方針の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> 島間関係要約(summarize-island-relation・接地エコー)
#          -> ナラティブ(generate-narrative) -> 読戻し
# 注意事項: 体験価値（体験型展示・動物福祉の充実）と運営コスト（入園料・改修投資）のトレードオフを
#          矛盾検出（正パス）で表面化し、施設運営方針の根拠にする。島間関係要約は接地カード
#          （groundingCardIds）が保全されることを固定（DOGFOOD-15）。
ZO_ID="biz-flow-zoo"
ZO_DOC='{"version":1,"id":"'$ZO_ID'","title":"動物園運営方針の整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"z1","text":"来園者は体験型展示と動物とのふれあいを求めている（来園者体験）","x":0,"y":0,"textReviewed":true},{"id":"z2","text":"動物福祉のため展示環境の改善は必要（動物福祉）","x":10,"y":0,"textReviewed":true},{"id":"z3","text":"入園料の値上げは来場者減につながりかねない（料金・集客）","x":20,"y":0,"textReviewed":true},{"id":"z4","text":"体験価値と施設投資はトレードオフの関係にあり改修費の捻出が課題（運営コスト）","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"zoo-a","cardIds":["z1","z2"]},{"id":"zoo-b","cardIds":["z3","z4"]}],"readingOrder":["zoo-a","zoo-b"]}'

zo_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$ZO_ID" \
  -H 'Content-Type: application/json' -d "$ZO_DOC")
check "ZO PUT document (作成)" "200" "$zo_put"

# ① AI束ね
zo_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"z1","text":"来園者は体験型展示と動物とのふれあいを求めている（来園者体験）","textReviewed":true},{"id":"z2","text":"動物福祉のため展示環境の改善は必要（動物福祉）","textReviewed":true},{"id":"z3","text":"入園料の値上げは来場者減につながりかねない（料金・集客）","textReviewed":true},{"id":"z4","text":"体験価値と施設投資はトレードオフの関係にあり改修費の捻出が課題（運営コスト）","textReviewed":true}]}')
case "$zo_groups" in *'"groups":'*) echo "  PASS: ZO ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: ZO ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約（体験・福祉の島）
zo_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$ZO_DOC,\"islandId\":\"zoo-a\"}")
case "$zo_summary" in *'"groundingIds":["z1","z2"]'*) echo "  PASS: ZO ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: ZO ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（体験価値 vs 運営コスト・体験とコストのトレードオフ・正パス）
zo_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"z1","text":"来園者は体験型展示と動物とのふれあいを求めている（来園者体験）","textReviewed":true},"cardB":{"id":"z4","text":"体験価値と施設投資はトレードオフの関係にあり改修費の捻出が課題（運営コスト）","textReviewed":true}}')
case "$zo_contra" in *'"hasContradiction":true'*) echo "  PASS: ZO ③矛盾検出（体験価値と運営コストのトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: ZO ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ 島間関係要約（体験・福祉の充実 → 運営コストの制約 の因果・接地エコー）
zo_rel=$(curl -s -X POST "$BASE_URL/ai/summarize-island-relation" -H 'Content-Type: application/json' \
  -d "{\"doc\":$ZO_DOC,\"islandAId\":\"zoo-a\",\"islandBId\":\"zoo-b\",\"relationType\":\"causal\",\"derived\":false,\"groundingCardIds\":[\"z4\"],\"groundingEdgeIds\":[],\"cardTexts\":[{\"id\":\"z4\",\"text\":\"体験価値と施設投資はトレードオフの関係にあり改修費の捻出が課題（運営コスト）\"}]}")
case "$zo_rel" in *'"groundingCardIds":["z4"]'*) echo "  PASS: ZO ④島間関係要約（接地カードが保全・DOGFOOD-15）"; PASS=$((PASS+1));; *) echo "  FAIL: ZO ④島間関係要約（${zo_rel:0:150}）"; FAIL=$((FAIL+1));; esac

# ⑤ ナラティブ
zo_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$ZO_DOC}")
case "$zo_narr" in *'"basedOnReadingOrder":["zoo-a","zoo-b"]'*) echo "  PASS: ZO ⑤ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: ZO ⑤ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
zo_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$ZO_ID")
check "ZO 読戻し (200)" "200" "$zo_read"

echo ""
echo "--- シナリオ111: 半導体製造（品質と効率のトレードオフ） ---"
# 業態: 製造・半導体（半導体工場・生産管理）
# 想定人物: 工場生産管理担当／品質管理エンジニア
# 業務領域: 歩留まり・生産効率・品質不良・設備稼働のKJ分類と、生産改善
# 操作内容: 文書作成 -> 文面整え(refine-card-text・raw現場報告の明確化) -> AI束ね(suggest-card-groups)
#          -> 島要約(suggest-island-summary・4カード島の全接地) -> 矛盾検出(detect-contradiction・正パス)
#          -> ナラティブ(generate-narrative) -> 読戻し
# 注意事項: 品質（歩留まり・良品率）と効率（サイクルタイム・生産性）のトレードオフを矛盾検出
#          （正パス）で表面化し、生産改善の根拠にする。文面整えは**元の意味（キーフレーズ）を保持**
#          することを固定（DOGFOOD-16・refineの操作カバー拡大）。
SM_ID="biz-flow-semi"
SM_DOC='{"version":1,"id":"'$SM_ID'","title":"半導体工場の生産改善","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"s1","text":"歩留まり向上のため設備調整とレシピ見直しを徹底したい（品質・歩留まり）","x":0,"y":0,"textReviewed":true},{"id":"s2","text":"生産効率を上げるためサイクルタイムを短縮したい（効率・生産性）","x":10,"y":0,"textReviewed":true},{"id":"s3","text":"検査工程の短縮は歩留まりとトレードオフになり不良の流出につながる（品質・効率）","x":20,"y":0,"textReviewed":true},{"id":"s4","text":"設備の稼働率を下げずに予防保全の時間を確保したい（設備・保全）","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"semi-i","cardIds":["s1","s2","s3","s4"]}],"readingOrder":["semi-i"]}'

sm_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$SM_ID" \
  -H 'Content-Type: application/json' -d "$SM_DOC")
check "SM PUT document (作成)" "200" "$sm_put"

# ① 文面整え（raw現場報告を明確化・元の意味を保持）
sm_refined=$(curl -s -X POST "$BASE_URL/ai/refine-card-text" -H 'Content-Type: application/json' \
  -d '{"cardText":"歩留まりが下がってロット廃棄が増えた","context":"半導体工場・前工程","textReviewed":true}')
case "$sm_refined" in *'"refinedText"'*'歩留まり'*) echo "  PASS: SM ①文面整え（元の意味を保持・DOGFOOD-16）"; PASS=$((PASS+1));; *) echo "  FAIL: SM ①文面整え（${sm_refined:0:150}）"; FAIL=$((FAIL+1));; esac

# ② AI束ね
sm_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"s1","text":"歩留まり向上のため設備調整とレシピ見直しを徹底したい（品質・歩留まり）","textReviewed":true},{"id":"s2","text":"生産効率を上げるためサイクルタイムを短縮したい（効率・生産性）","textReviewed":true},{"id":"s3","text":"検査工程の短縮は歩留まりとトレードオフになり不良の流出につながる（品質・効率）","textReviewed":true},{"id":"s4","text":"設備の稼働率を下げずに予防保全の時間を確保したい（設備・保全）","textReviewed":true}]}')
case "$sm_groups" in *'"groups":'*) echo "  PASS: SM ②束ね"; PASS=$((PASS+1));; *) echo "  FAIL: SM ②束ね"; FAIL=$((FAIL+1));; esac

# ③ 島要約（4カード島の全接地）
sm_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$SM_DOC,\"islandId\":\"semi-i\"}")
case "$sm_summary" in *'"groundingIds":["s1","s2","s3","s4"]'*) echo "  PASS: SM ③島要約（4カード島の全接地）"; PASS=$((PASS+1));; *) echo "  FAIL: SM ③島要約（${sm_summary:0:150}）"; FAIL=$((FAIL+1));; esac

# ④ 矛盾検出（効率 vs 品質・品質と効率のトレードオフ・正パス）
sm_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"s2","text":"生産効率を上げるためサイクルタイムを短縮したい（効率・生産性）","textReviewed":true},"cardB":{"id":"s3","text":"検査工程の短縮は歩留まりとトレードオフになり不良の流出につながる（品質・効率）","textReviewed":true}}')
case "$sm_contra" in *'"hasContradiction":true'*) echo "  PASS: SM ④矛盾検出（品質と効率のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: SM ④矛盾検出"; FAIL=$((FAIL+1));; esac

# ⑤ ナラティブ
sm_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$SM_DOC}")
case "$sm_narr" in *'"basedOnReadingOrder":["semi-i"]'*) echo "  PASS: SM ⑤ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: SM ⑤ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
sm_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$SM_ID")
check "SM 読戻し (200)" "200" "$sm_read"

echo ""
echo "--- シナリオ112: 訪問看護（ケアの質と訪問効率のトレードオフ） ---"
# 業態: 医療・在宅ケア（訪問看護ステーション）
# 想定人物: 訪問看護管理者／ケアマネジャー
# 業務領域: 訪問看護のケア記録・利用者・家族からの声のKJ分類と、ケア提供体制の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary・4カード島の全接地)
#          -> 矛盾検出(detect-contradiction・正パス) -> 反対視点提案(propose-opposing-viewpoint・対象主張を参照)
#          -> ナラティブ(generate-narrative) -> 読戻し
# 注意事項: ケアの質（手厚い看護）と訪問効率（処置時間・訪問件数）のトレードオフを矛盾検出
#          （正パス）で表面化し、ケア提供体制の根拠にする。反対視点は proposal-only で
#          対象カードの主張（訪問件数）に応答することを固定（DOGFOOD-17）。
VN_ID="biz-flow-visiting"
VN_DOC='{"version":1,"id":"'$VN_ID'","title":"訪問看護ケア体制の整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"v1","text":"利用者宅での処置時間が長く訪問件数をこなせない（訪問効率・件数）","x":0,"y":0,"textReviewed":true},{"id":"v2","text":"一人暮らしの高齢者への見守りニーズが増えている（利用者ニーズ・見守り）","x":10,"y":0,"textReviewed":true},{"id":"v3","text":"看護師の残業が増え離職者が続出している（人材・疲弊）","x":20,"y":0,"textReviewed":true},{"id":"v4","text":"ケアの質と訪問回数はトレードオフの関係にあり手厚いケアは効率を下げる（質と効率）","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"visit-i","cardIds":["v1","v2","v3","v4"]}],"readingOrder":["visit-i"]}'

vn_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$VN_ID" \
  -H 'Content-Type: application/json' -d "$VN_DOC")
check "VN PUT document (作成)" "200" "$vn_put"

# ① AI束ね
vn_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"v1","text":"利用者宅での処置時間が長く訪問件数をこなせない（訪問効率・件数）","textReviewed":true},{"id":"v2","text":"一人暮らしの高齢者への見守りニーズが増えている（利用者ニーズ・見守り）","textReviewed":true},{"id":"v3","text":"看護師の残業が増え離職者が続出している（人材・疲弊）","textReviewed":true},{"id":"v4","text":"ケアの質と訪問回数はトレードオフの関係にあり手厚いケアは効率を下げる（質と効率）","textReviewed":true}]}')
case "$vn_groups" in *'"groups":'*) echo "  PASS: VN ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: VN ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約（4カード島の全接地）
vn_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$VN_DOC,\"islandId\":\"visit-i\"}")
case "$vn_summary" in *'"groundingIds":["v1","v2","v3","v4"]'*) echo "  PASS: VN ②島要約（4カード島の全接地）"; PASS=$((PASS+1));; *) echo "  FAIL: VN ②島要約（${vn_summary:0:150}）"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（訪問効率 vs ケアの質・質と効率のトレードオフ・正パス）
vn_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"v1","text":"利用者宅での処置時間が長く訪問件数をこなせない（訪問効率・件数）","textReviewed":true},"cardB":{"id":"v4","text":"ケアの質と訪問回数はトレードオフの関係にあり手厚いケアは効率を下げる（質と効率）","textReviewed":true}}')
case "$vn_contra" in *'"hasContradiction":true'*) echo "  PASS: VN ③矛盾検出（ケアの質と訪問効率のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: VN ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ 反対視点提案（proposal-only・対象カードの主張「訪問件数」を参照・DOGFOOD-17）
vn_opp=$(curl -s -X POST "$BASE_URL/ai/proposals/opposing-viewpoint" -H 'Content-Type: application/json' \
  -d "{\"doc\":$VN_DOC,\"targetCardId\":\"v1\"}")
case "$vn_opp" in *'"status":"proposed"'*'"opposingText"'*'訪問件数'*) echo "  PASS: VN ④反対視点提案（proposal-only・対象主張に応答・DOGFOOD-17）"; PASS=$((PASS+1));; *) echo "  FAIL: VN ④反対視点（${vn_opp:0:150}）"; FAIL=$((FAIL+1));; esac

# ⑤ ナラティブ
vn_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$VN_DOC}")
case "$vn_narr" in *'"basedOnReadingOrder":["visit-i"]'*) echo "  PASS: VN ⑤ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: VN ⑤ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
vn_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$VN_ID")
check "VN 読戻し (200)" "200" "$vn_read"

echo ""
echo "--- シナリオ113: 書店（品揃えと在庫コストのトレードオフ） ---"
# 業態: サービス・小売（書店・ブックストア）
# 想定人物: 書店オーナー／仕入れ担当
# 業務領域: 売上・在庫・顧客の声・書店イベントのKJ分類と、品揃え・売場づくりの検討
# 操作内容: 文書作成 -> タイトル提案(suggest-document-title・文書テーマを参照) -> AI束ね(suggest-card-groups)
#          -> 島要約(suggest-island-summary・4カード島の全接地) -> 矛盾検出(detect-contradiction・正パス)
#          -> ナラティブ(generate-narrative) -> 読戻し
# 注意事項: 品揃え（ニッチな要望に応える棚づくり）と在庫コスト（仕入れ・在庫の偏り）のトレードオフを
#          矛盾検出（正パス）で表面化し、品揃え・売場づくりの根拠にする。タイトル提案は**文書の
#          テーマ（島ラベル）に接地**することを固定（DOGFOOD-18）。
BK_ID="biz-flow-bookstore"
BK_DOC='{"version":1,"id":"'$BK_ID'","title":"書店の棚づくりと在庫戦略","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"b1","text":"ベストセラーの大量仕入れで売り切れを防ぎたい（売上・在庫回転）","x":0,"y":0,"textReviewed":true},{"id":"b2","text":"読者のニッチな要望に応える棚づくりをしたい（品揃え・ニッチ）","x":10,"y":0,"textReviewed":true},{"id":"b3","text":"在庫の偏りは仕入れコストとトレードオフの関係にありバランスが難しい（在庫・コスト）","x":20,"y":0,"textReviewed":true},{"id":"b4","text":"書店イベントやフェアで来店動機を高めたい（集客・イベント）","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"book-i","cardIds":["b1","b2","b3","b4"]}],"readingOrder":["book-i"]}'

bk_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$BK_ID" \
  -H 'Content-Type: application/json' -d "$BK_DOC")
check "BK PUT document (作成)" "200" "$bk_put"

# ① タイトル提案（文書のテーマに接地・DOGFOOD-18）
bk_title=$(curl -s -X POST "$BASE_URL/ai/suggest-document-title" -H 'Content-Type: application/json' \
  -d '{"islandTitles":["書店の棚づくりと品揃え戦略"],"cardTexts":["ベストセラーの大量仕入れで売り切れを防ぎたい","読者のニッチな要望に応える棚づくりをしたい","在庫の偏りは仕入れコストとトレードオフの関係にありバランスが難しい","書店イベントやフェアで来店動機を高めたい"],"textReviewed":true}')
case "$bk_title" in *'"candidates"'*'棚づくり'*) echo "  PASS: BK ①タイトル提案（文書テーマに接地・DOGFOOD-18）"; PASS=$((PASS+1));; *) echo "  FAIL: BK ①タイトル提案（${bk_title:0:150}）"; FAIL=$((FAIL+1));; esac

# ② AI束ね
bk_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"b1","text":"ベストセラーの大量仕入れで売り切れを防ぎたい（売上・在庫回転）","textReviewed":true},{"id":"b2","text":"読者のニッチな要望に応える棚づくりをしたい（品揃え・ニッチ）","textReviewed":true},{"id":"b3","text":"在庫の偏りは仕入れコストとトレードオフの関係にありバランスが難しい（在庫・コスト）","textReviewed":true},{"id":"b4","text":"書店イベントやフェアで来店動機を高めたい（集客・イベント）","textReviewed":true}]}')
case "$bk_groups" in *'"groups":'*) echo "  PASS: BK ②束ね"; PASS=$((PASS+1));; *) echo "  FAIL: BK ②束ね"; FAIL=$((FAIL+1));; esac

# ③ 島要約（4カード島の全接地）
bk_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$BK_DOC,\"islandId\":\"book-i\"}")
case "$bk_summary" in *'"groundingIds":["b1","b2","b3","b4"]'*) echo "  PASS: BK ③島要約（4カード島の全接地）"; PASS=$((PASS+1));; *) echo "  FAIL: BK ③島要約（${bk_summary:0:150}）"; FAIL=$((FAIL+1));; esac

# ④ 矛盾検出（ニッチ棚づくり vs 在庫コスト・品揃えと在庫コストのトレードオフ・正パス）
bk_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"b2","text":"読者のニッチな要望に応える棚づくりをしたい（品揃え・ニッチ）","textReviewed":true},"cardB":{"id":"b3","text":"在庫の偏りは仕入れコストとトレードオフの関係にありバランスが難しい（在庫・コスト）","textReviewed":true}}')
case "$bk_contra" in *'"hasContradiction":true'*) echo "  PASS: BK ④矛盾検出（品揃えと在庫コストのトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: BK ④矛盾検出"; FAIL=$((FAIL+1));; esac

# ⑤ ナラティブ
bk_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$BK_DOC}")
case "$bk_narr" in *'"basedOnReadingOrder":["book-i"]'*) echo "  PASS: BK ⑤ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: BK ⑤ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
bk_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$BK_ID")
check "BK 読戻し (200)" "200" "$bk_read"

echo ""
echo "--- シナリオ114: 税理士・会計事務所（顧客サービスと料金・業務量のトレードオフ） ---"
# 業態: 金融・法務・専門サービス（税理士・会計事務所）
# 想定人物: 税理士／会計担当パートナー
# 業務領域: 顧客の決算・申告・経理相談の声のKJ分類と、業務効率化・顧客サービスの検討
# 操作内容: 文書作成 -> 統合提案(suggest-merges・同カテゴリのカード対) -> AI束ね(suggest-card-groups)
#          -> 島要約(suggest-island-summary・4カード島の全接地) -> 矛盾検出(detect-contradiction・正パス)
#          -> ナラティブ(generate-narrative) -> 読戻し
# 注意事項: 顧客サービス（経営相談への期待）と料金・業務量（受注の取捨）のトレードオフを矛盾検出
#          （正パス）で表面化し、業務改善の根拠にする。統合提案は同カテゴリのカード対
#          （業務効率・a1/a2）をマージ候補として提示することを固定（DOGFOOD-19）。
TX_ID="biz-flow-tax"
TX_DOC='{"version":1,"id":"'$TX_ID'","title":"税理士事務所の業務改善","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"a1","text":"決算書の作成に時間がかかり繁忙期に残業が増える（業務効率）","x":0,"y":0,"textReviewed":true},{"id":"a2","text":"電子帳簿保存法への対応が進まず手作業が残る（業務効率）","x":10,"y":0,"textReviewed":true},{"id":"a3","text":"顧客からは経営相談に乗ってほしいという声がある（顧客サービス）","x":20,"y":0,"textReviewed":true},{"id":"a4","text":"料金交渉と業務量はトレードオフの関係にあり受注の取捨が難しい（料金・受注）","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"tax-i","cardIds":["a1","a2","a3","a4"]}],"readingOrder":["tax-i"]}'

tx_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$TX_ID" \
  -H 'Content-Type: application/json' -d "$TX_DOC")
check "TX PUT document (作成)" "200" "$tx_put"

# ① 統合提案（同カテゴリのカード対 a1/a2 をマージ候補として提示・DOGFOOD-19）
tx_merges=$(curl -s -X POST "$BASE_URL/ai/suggest-merges" -H 'Content-Type: application/json' \
  -d "{\"doc\":$TX_DOC}")
case "$tx_merges" in *'"suggestions"'*'a1'*'a2'*) echo "  PASS: TX ①統合提案（業務効率カード対をマージ候補に提示・DOGFOOD-19）"; PASS=$((PASS+1));; *) echo "  FAIL: TX ①統合提案（${tx_merges:0:150}）"; FAIL=$((FAIL+1));; esac

# ② AI束ね
tx_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"a1","text":"決算書の作成に時間がかかり繁忙期に残業が増える（業務効率）","textReviewed":true},{"id":"a2","text":"電子帳簿保存法への対応が進まず手作業が残る（業務効率）","textReviewed":true},{"id":"a3","text":"顧客からは経営相談に乗ってほしいという声がある（顧客サービス）","textReviewed":true},{"id":"a4","text":"料金交渉と業務量はトレードオフの関係にあり受注の取捨が難しい（料金・受注）","textReviewed":true}]}')
case "$tx_groups" in *'"groups":'*) echo "  PASS: TX ②束ね"; PASS=$((PASS+1));; *) echo "  FAIL: TX ②束ね"; FAIL=$((FAIL+1));; esac

# ③ 島要約（4カード島の全接地）
tx_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$TX_DOC,\"islandId\":\"tax-i\"}")
case "$tx_summary" in *'"groundingIds":["a1","a2","a3","a4"]'*) echo "  PASS: TX ③島要約（4カード島の全接地）"; PASS=$((PASS+1));; *) echo "  FAIL: TX ③島要約（${tx_summary:0:150}）"; FAIL=$((FAIL+1));; esac

# ④ 矛盾検出（顧客サービス vs 料金・業務量・サービスと料金のトレードオフ・正パス）
tx_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"a3","text":"顧客からは経営相談に乗ってほしいという声がある（顧客サービス）","textReviewed":true},"cardB":{"id":"a4","text":"料金交渉と業務量はトレードオフの関係にあり受注の取捨が難しい（料金・受注）","textReviewed":true}}')
case "$tx_contra" in *'"hasContradiction":true'*) echo "  PASS: TX ④矛盾検出（顧客サービスと料金・業務量のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: TX ④矛盾検出"; FAIL=$((FAIL+1));; esac

# ⑤ ナラティブ
tx_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$TX_DOC}")
case "$tx_narr" in *'"basedOnReadingOrder":["tax-i"]'*) echo "  PASS: TX ⑤ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: TX ⑤ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
tx_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$TX_ID")
check "TX 読戻し (200)" "200" "$tx_read"

echo ""
echo "--- シナリオ115: コンビニエンスストア本部（商品品質と廃棄コストのトレードオフ） ---"
# 業態: 小売・コンビニ（コンビニエンスストア・FC本部）
# 想定人物: コンビニ本部・運営担当
# 業務領域: 店舗運営・商品・オペレーション・加盟店の声のKJ分類と、本部施策の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups・カテゴリ別の同グループ化) -> 島要約(suggest-island-summary・4カード島の全接地)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative) -> A/B照合(check-narrative) -> 読戻し
# 注意事項: 商品品質向上（お弁当・総菜の差別化）と廃棄コスト（新商品の売れ残り）のトレードオフを
#          矛盾検出（正パス）で表面化し、本部施策の根拠にする。AI束ねは**テーマ（カテゴリ）類似性**
#          による同グループ化（c1/c3=オペレーション・c2/c4=商品戦略）を固定（DOGFOOD-20）。
CV_ID="biz-flow-cvs"
CV_DOC='{"version":1,"id":"'$CV_ID'","title":"コンビニ本部施策の整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"c1","text":"24時間営業の見直しで人手不足に対応したい（オペレーション）","x":0,"y":0,"textReviewed":true},{"id":"c2","text":"お弁当・総菜の品質向上で他店との差別化を図りたい（商品戦略）","x":10,"y":0,"textReviewed":true},{"id":"c3","text":"レジ待ち時間の短縮など店舗オペレーションを改善したい（オペレーション）","x":20,"y":0,"textReviewed":true},{"id":"c4","text":"新商品の投入と売れ残り廃棄はトレードオフの関係にあり在庫管理が難しい（商品戦略）","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"cvs-i","cardIds":["c1","c2","c3","c4"]}],"readingOrder":["cvs-i"]}'

cv_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$CV_ID" \
  -H 'Content-Type: application/json' -d "$CV_DOC")
check "CV PUT document (作成)" "200" "$cv_put"

# ① AI束ね（カテゴリ別の同グループ化・c1/c3=オペレーション・c2/c4=商品戦略・DOGFOOD-20）
cv_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"c1","text":"24時間営業の見直しで人手不足に対応したい（オペレーション）","textReviewed":true},{"id":"c2","text":"お弁当・総菜の品質向上で他店との差別化を図りたい（商品戦略）","textReviewed":true},{"id":"c3","text":"レジ待ち時間の短縮など店舗オペレーションを改善したい（オペレーション）","textReviewed":true},{"id":"c4","text":"新商品の投入と売れ残り廃棄はトレードオフの関係にあり在庫管理が難しい（商品戦略）","textReviewed":true}]}')
case "$cv_groups" in *'c1","c3'*'c2","c4'*) echo "  PASS: CV ①AI束ね（テーマ類似性で同グループ化・DOGFOOD-20）"; PASS=$((PASS+1));; *) echo "  FAIL: CV ①AI束ね（${cv_groups:0:150}）"; FAIL=$((FAIL+1));; esac

# ② 島要約（4カード島の全接地）
cv_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$CV_DOC,\"islandId\":\"cvs-i\"}")
case "$cv_summary" in *'"groundingIds":["c1","c2","c3","c4"]'*) echo "  PASS: CV ②島要約（4カード島の全接地）"; PASS=$((PASS+1));; *) echo "  FAIL: CV ②島要約（${cv_summary:0:150}）"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（商品品質 vs 廃棄コスト・品質とコストのトレードオフ・正パス）
cv_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"c2","text":"お弁当・総菜の品質向上で他店との差別化を図りたい（商品戦略）","textReviewed":true},"cardB":{"id":"c4","text":"新商品の投入と売れ残り廃棄はトレードオフの関係にあり在庫管理が難しい（商品戦略）","textReviewed":true}}')
case "$cv_contra" in *'"hasContradiction":true'*) echo "  PASS: CV ③矛盾検出（商品品質と廃棄コストのトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: CV ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
cv_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$CV_DOC}")
case "$cv_narr" in *'"basedOnReadingOrder":["cvs-i"]'*) echo "  PASS: CV ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: CV ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ A/B照合（ナラティブが島cvs-iに触れていない・a_missing_in_b）
cv_ab=$(curl -s -X POST "$BASE_URL/ai/check-narrative" -H 'Content-Type: application/json' \
  -d "{\"doc\":$CV_DOC,\"narrativeText\":\"（草稿）本部施策を検討する。ただし新規施策には未検証の主張が含まれる。\",\"basedOnReadingOrder\":[\"cvs-i\"]}")
case "$cv_ab" in *'ナラティブが島cvs-iに触れていない'*'"aMissingInB":1'*) echo "  PASS: CV ⑤A/B照合（島cvs-iの取りこぼし・a_missing_in_b）"; PASS=$((PASS+1));; *) echo "  FAIL: CV ⑤A/B照合（${cv_ab:0:150}）"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
cv_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$CV_ID")
check "CV 読戻し (200)" "200" "$cv_read"

echo ""
echo "--- シナリオ116: ドラッグストア（調剤サービスと運営コストのトレードオフ） ---"
# 業態: 小売・ドラッグストア（調剤併設）
# 想定人物: ドラッグストア店長／本部運営担当
# 業務領域: 医薬品・調剤・一般品・顧客の声のKJ分類と、店舗運営・品揃えの検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary・4カード島の全接地)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative・読み順の島を本文で参照)
#          -> A/B照合(check-narrative) -> 読戻し
# 注意事項: 調剤サービス（待ち時間短縮・顧客満足）と運営コスト（在庫管理・人員配置）のトレードオフを
#          矛盾検出（正パス）で表面化し、店舗運営の根拠にする。ナラティブは**読み順の島（drg-i）を
#          本文で参照**することを固定（DOGFOOD-21）。
DG_ID="biz-flow-drugstore"
DG_DOC='{"version":1,"id":"'$DG_ID'","title":"ドラッグストア店舗運営の整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"d1","text":"調剤待ち時間の短縮で顧客満足を高めたい（調剤・サービス）","x":0,"y":0,"textReviewed":true},{"id":"d2","text":"OTC医薬品と化粧品・日用品の売場を分けたい（売場・品揃え）","x":10,"y":0,"textReviewed":true},{"id":"d3","text":"薬剤師の在庫管理と一般品の陳列はトレードオフの関係にあり優先順位が難しい（運営・コスト）","x":20,"y":0,"textReviewed":true},{"id":"d4","text":"処方箋応需と一般販売の両立で人員配置に悩む（人員・オペレーション）","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"drg-i","cardIds":["d1","d2","d3","d4"]}],"readingOrder":["drg-i"]}'

dg_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$DG_ID" \
  -H 'Content-Type: application/json' -d "$DG_DOC")
check "DG PUT document (作成)" "200" "$dg_put"

# ① AI束ね（カテゴリ別の同グループ化）
dg_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"d1","text":"調剤待ち時間の短縮で顧客満足を高めたい（調剤・サービス）","textReviewed":true},{"id":"d2","text":"OTC医薬品と化粧品・日用品の売場を分けたい（売場・品揃え）","textReviewed":true},{"id":"d3","text":"薬剤師の在庫管理と一般品の陳列はトレードオフの関係にあり優先順位が難しい（運営・コスト）","textReviewed":true},{"id":"d4","text":"処方箋応需と一般販売の両立で人員配置に悩む（人員・オペレーション）","textReviewed":true}]}')
case "$dg_groups" in *'"groups":'*) echo "  PASS: DG ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: DG ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約（4カード島の全接地）
dg_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$DG_DOC,\"islandId\":\"drg-i\"}")
case "$dg_summary" in *'"groundingIds":["d1","d2","d3","d4"]'*) echo "  PASS: DG ②島要約（4カード島の全接地）"; PASS=$((PASS+1));; *) echo "  FAIL: DG ②島要約（${dg_summary:0:150}）"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（調剤サービス vs 運営コスト・サービスとコストのトレードオフ・正パス）
dg_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"d1","text":"調剤待ち時間の短縮で顧客満足を高めたい（調剤・サービス）","textReviewed":true},"cardB":{"id":"d3","text":"薬剤師の在庫管理と一般品の陳列はトレードオフの関係にあり優先順位が難しい（運営・コスト）","textReviewed":true}}')
case "$dg_contra" in *'"hasContradiction":true'*) echo "  PASS: DG ③矛盾検出（調剤サービスと運営コストのトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: DG ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ（読み順の島を本文で参照・DOGFOOD-21）
dg_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$DG_DOC}")
case "$dg_narr" in *'読み順（drg-i）'*'"basedOnReadingOrder":["drg-i"]'*) echo "  PASS: DG ④ナラティブ（読み順の島を本文で参照・DOGFOOD-21）"; PASS=$((PASS+1));; *) echo "  FAIL: DG ④ナラティブ（${dg_narr:0:150}）"; FAIL=$((FAIL+1));; esac

# ⑤ A/B照合（ナラティブが島drg-iに触れていない・a_missing_in_b）
dg_ab=$(curl -s -X POST "$BASE_URL/ai/check-narrative" -H 'Content-Type: application/json' \
  -d "{\"doc\":$DG_DOC,\"narrativeText\":\"（草稿）店舗運営を検討する。ただし新施策には未検証の主張が含まれる。\",\"basedOnReadingOrder\":[\"drg-i\"]}")
case "$dg_ab" in *'ナラティブが島drg-iに触れていない'*'"aMissingInB":1'*) echo "  PASS: DG ⑤A/B照合（島drg-iの取りこぼし・a_missing_in_b）"; PASS=$((PASS+1));; *) echo "  FAIL: DG ⑤A/B照合（${dg_ab:0:150}）"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
dg_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$DG_ID")
check "DG 読戻し (200)" "200" "$dg_read"

echo ""
echo "--- シナリオ117: ホームセンター（品揃えと在庫スペースのトレードオフ） ---"
# 業態: 小売・ホームセンター（DIY・住まい）
# 想定人物: ホームセンター店長／仕入れ担当
# 業務領域: 品揃え・売場・DIY需要・顧客の声のKJ分類と、品揃え・販促の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary・4カード島の全接地)
#          -> 矛盾検出(detect-contradiction・正パス) -> CE4提案(proposals/island-summary・提案の接地を保持)
#          -> ナラティブ(generate-narrative) -> 読戻し
# 注意事項: 品揃え（売場の両立・DIY需要）と在庫スペース（拡充と優先順位）のトレードオフを矛盾検出
#          （正パス）で表面化し、品揃え・販促の根拠にする。CE4提案は**proposal-only かつ
#          diff.groundingIds が島の全カード**であることを固定（DOGFOOD-22）。
HC_ID="biz-flow-homecenter"
HC_DOC='{"version":1,"id":"'$HC_ID'","title":"ホームセンター品揃えの整理","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"h1","text":"DIY人気で木材・工具の需要が伸びている（DIY需要）","x":0,"y":0,"textReviewed":true},{"id":"h2","text":"季節商品と日用品の売場を両立させたい（売場・品揃え）","x":10,"y":0,"textReviewed":true},{"id":"h3","text":"品揃えの拡充と在庫スペースはトレードオフの関係にあり優先順位が難しい（在庫・スペース）","x":20,"y":0,"textReviewed":true},{"id":"h4","text":"ネット通販との価格競争で利益率が下がっている（価格・競争）","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"hc-i","cardIds":["h1","h2","h3","h4"]}],"readingOrder":["hc-i"]}'
HC_HASH="$(printf 'b%.0s' $(seq 1 64))"

hc_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$HC_ID" \
  -H 'Content-Type: application/json' -d "$HC_DOC")
check "HC PUT document (作成)" "200" "$hc_put"

# ① AI束ね（カテゴリ別の同グループ化）
hc_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"h1","text":"DIY人気で木材・工具の需要が伸びている（DIY需要）","textReviewed":true},{"id":"h2","text":"季節商品と日用品の売場を両立させたい（売場・品揃え）","textReviewed":true},{"id":"h3","text":"品揃えの拡充と在庫スペースはトレードオフの関係にあり優先順位が難しい（在庫・スペース）","textReviewed":true},{"id":"h4","text":"ネット通販との価格競争で利益率が下がっている（価格・競争）","textReviewed":true}]}')
case "$hc_groups" in *'"groups":'*) echo "  PASS: HC ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: HC ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約（4カード島の全接地）
hc_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$HC_DOC,\"islandId\":\"hc-i\"}")
case "$hc_summary" in *'"groundingIds":["h1","h2","h3","h4"]'*) echo "  PASS: HC ②島要約（4カード島の全接地）"; PASS=$((PASS+1));; *) echo "  FAIL: HC ②島要約（${hc_summary:0:150}）"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（品揃え vs 在庫スペース・品揃えと在庫のトレードオフ・正パス）
hc_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"h2","text":"季節商品と日用品の売場を両立させたい（売場・品揃え）","textReviewed":true},"cardB":{"id":"h3","text":"品揃えの拡充と在庫スペースはトレードオフの関係にあり優先順位が難しい（在庫・スペース）","textReviewed":true}}')
case "$hc_contra" in *'"hasContradiction":true'*) echo "  PASS: HC ③矛盾検出（品揃えと在庫スペースのトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: HC ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ CE4提案（proposal-only・提案の接地を保持・DOGFOOD-22）
hc_prop=$(curl -s -X POST "$BASE_URL/ai/proposals/island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$HC_DOC,\"islandId\":\"hc-i\",\"sourceBundleHash\":\"$HC_HASH\"}")
case "$hc_prop" in *'"status":"proposed"'*'"groundingIds":["h1","h2","h3","h4"]'*) echo "  PASS: HC ④CE4提案（proposal-only・提案の接地を保持・DOGFOOD-22）"; PASS=$((PASS+1));; *) echo "  FAIL: HC ④CE4提案（${hc_prop:0:200}）"; FAIL=$((FAIL+1));; esac

# ⑤ ナラティブ
hc_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$HC_DOC}")
case "$hc_narr" in *'"basedOnReadingOrder":["hc-i"]'*) echo "  PASS: HC ⑤ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: HC ⑤ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
hc_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$HC_ID")
check "HC 読戻し (200)" "200" "$hc_read"

echo ""
echo "--- シナリオ118: 百貨店（外商接客と売場効率のトレードオフ） ---"
# 業態: 小売・百貨店（デパート・外商・売場）
# 想定人物: 百貨店外商担当／売場マネージャー
# 業務領域: 外商顧客・売場・売上・顧客の声のKJ分類と、接客・販促の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary・4カード島の全接地)
#          -> 矛盾検出(detect-contradiction・正パス) -> 配置提案(suggest-layout・全カード保持)
#          -> ナラティブ(generate-narrative) -> 読戻し
# 注意事項: 外商接客（個別ニーズへの対応）と売場効率（人員配置・手厚さ）のトレードオフを矛盾検出
#          （正パス）で表面化し、接客・販促の根拠にする。配置提案は**全カード（d1〜d4）が座標付きで
#          保持される**ことを固定（DOGFOOD-23）。
DP_ID="biz-flow-dept"
DP_DOC='{"version":1,"id":"'$DP_ID'","title":"百貨店の接客・売場戦略","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"d1","text":"外商顧客の個別ニーズに応える接客を強化したい（外商・接客）","x":0,"y":0,"textReviewed":true},{"id":"d2","text":"若年層を呼び込む売場づくりを進めたい（売場・集客）","x":10,"y":0,"textReviewed":true},{"id":"d3","text":"接客の手厚さと売場の効率はトレードオフの関係にあり人員配置が難しい（接客・効率）","x":20,"y":0,"textReviewed":true},{"id":"d4","text":"催事やイベントで集客を高めたい（催事・販促）","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"dep-i","cardIds":["d1","d2","d3","d4"]}],"readingOrder":["dep-i"]}'

dp_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$DP_ID" \
  -H 'Content-Type: application/json' -d "$DP_DOC")
check "DP PUT document (作成)" "200" "$dp_put"

# ① AI束ね（カテゴリ別の同グループ化）
dp_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"d1","text":"外商顧客の個別ニーズに応える接客を強化したい（外商・接客）","textReviewed":true},{"id":"d2","text":"若年層を呼び込む売場づくりを進めたい（売場・集客）","textReviewed":true},{"id":"d3","text":"接客の手厚さと売場の効率はトレードオフの関係にあり人員配置が難しい（接客・効率）","textReviewed":true},{"id":"d4","text":"催事やイベントで集客を高めたい（催事・販促）","textReviewed":true}]}')
case "$dp_groups" in *'"groups":'*) echo "  PASS: DP ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: DP ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約（4カード島の全接地）
dp_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$DP_DOC,\"islandId\":\"dep-i\"}")
case "$dp_summary" in *'"groundingIds":["d1","d2","d3","d4"]'*) echo "  PASS: DP ②島要約（4カード島の全接地）"; PASS=$((PASS+1));; *) echo "  FAIL: DP ②島要約（${dp_summary:0:150}）"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（外商接客 vs 売場効率・接客と効率のトレードオフ・正パス）
dp_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"d1","text":"外商顧客の個別ニーズに応える接客を強化したい（外商・接客）","textReviewed":true},"cardB":{"id":"d3","text":"接客の手厚さと売場の効率はトレードオフの関係にあり人員配置が難しい（接客・効率）","textReviewed":true}}')
case "$dp_contra" in *'"hasContradiction":true'*) echo "  PASS: DP ③矛盾検出（外商接客と売場効率のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: DP ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ 配置提案（全カードが座標付きで保持・DOGFOOD-23）
dp_layout=$(curl -s -X POST "$BASE_URL/ai/suggest-layout" -H 'Content-Type: application/json' \
  -d "{\"doc\":$DP_DOC}")
case "$dp_layout" in *'"suggestedDoc"'*'d1'*'d2'*'d3'*'d4'*) echo "  PASS: DP ④配置提案（全カードが保持・DOGFOOD-23）"; PASS=$((PASS+1));; *) echo "  FAIL: DP ④配置提案（${dp_layout:0:200}）"; FAIL=$((FAIL+1));; esac

# ⑤ ナラティブ
dp_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$DP_DOC}")
case "$dp_narr" in *'"basedOnReadingOrder":["dep-i"]'*) echo "  PASS: DP ⑤ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: DP ⑤ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
dp_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$DP_ID")
check "DP 読戻し (200)" "200" "$dp_read"

echo ""
echo "--- シナリオ119: 精肉・鮮魚（鮮度維持とロス削減のトレードオフ） ---"
# 業態: 小売・精肉鮮魚（専門小売・精肉/鮮魚店）
# 想定人物: 精肉・鮮魚店店主／仕入れ担当
# 業務領域: 仕入れ・鮮度管理・売場・顧客の声のKJ分類と、品揃え・鮮度施策の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> A/B照合(check-narrative・複数島の取りこぼし) -> 読戻し
# 注意事項: 鮮度維持（仕入れ・当日完売）とロス削減（廃棄との兼ね合い）のトレードオフを矛盾検出
#          （正パス）で表面化し、鮮度施策の根拠にする。A/B照合は**複数島（meat-i/fish-i）の
#          取りこぼし**（aMissingInB:2・先頭島以外を含む報告）を固定（DOGFOOD-25）。
MF_ID="biz-flow-meatfish"
MF_DOC='{"version":1,"id":"'$MF_ID'","title":"精肉・鮮魚店の鮮度戦略","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"m1","text":"仕入れの鮮度を最優先し当日完売を目指したい（鮮度・品質）","x":0,"y":0,"textReviewed":true},{"id":"m2","text":"季節の食材を使った提案で売場を差別化したい（品揃え・提案）","x":10,"y":0,"textReviewed":true},{"id":"m3","text":"鮮度維持とロス削減はトレードオフの関係にあり廃棄との兼ね合いが難しい（鮮度・ロス）","x":20,"y":0,"textReviewed":true},{"id":"m4","text":"量り売りとパック売りの売場をどう分けるか悩む（売場・オペレーション）","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"meat-i","cardIds":["m1","m2"]},{"id":"fish-i","cardIds":["m3","m4"]}],"readingOrder":["meat-i","fish-i"]}'

mf_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$MF_ID" \
  -H 'Content-Type: application/json' -d "$MF_DOC")
check "MF PUT document (作成)" "200" "$mf_put"

# ① AI束ね（カテゴリ別の同グループ化）
mf_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"m1","text":"仕入れの鮮度を最優先し当日完売を目指したい（鮮度・品質）","textReviewed":true},{"id":"m2","text":"季節の食材を使った提案で売場を差別化したい（品揃え・提案）","textReviewed":true},{"id":"m3","text":"鮮度維持とロス削減はトレードオフの関係にあり廃棄との兼ね合いが難しい（鮮度・ロス）","textReviewed":true},{"id":"m4","text":"量り売りとパック売りの売場をどう分けるか悩む（売場・オペレーション）","textReviewed":true}]}')
case "$mf_groups" in *'"groups":'*) echo "  PASS: MF ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: MF ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約（鮮度・品揃えの島）
mf_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$MF_DOC,\"islandId\":\"meat-i\"}")
case "$mf_summary" in *'"groundingIds":["m1","m2"]'*) echo "  PASS: MF ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: MF ②島要約（${mf_summary:0:150}）"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（鮮度 vs ロス・鮮度とロスのトレードオフ・正パス）
mf_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"m1","text":"仕入れの鮮度を最優先し当日完売を目指したい（鮮度・品質）","textReviewed":true},"cardB":{"id":"m3","text":"鮮度維持とロス削減はトレードオフの関係にあり廃棄との兼ね合いが難しい（鮮度・ロス）","textReviewed":true}}')
case "$mf_contra" in *'"hasContradiction":true'*) echo "  PASS: MF ③矛盾検出（鮮度維持とロス削減のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: MF ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
mf_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$MF_DOC}")
case "$mf_narr" in *'"basedOnReadingOrder":["meat-i","fish-i"]'*) echo "  PASS: MF ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: MF ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ A/B照合（複数島の取りこぼし・aMissingInB:2・先頭島以外を含む報告・DOGFOOD-25）
mf_ab=$(curl -s -X POST "$BASE_URL/ai/check-narrative" -H 'Content-Type: application/json' \
  -d "{\"doc\":$MF_DOC,\"narrativeText\":\"（草稿）仕入れ鮮度を最優先し、季節の食材で売場を差別化したい。ただしロス削減策には未検証の主張が含まれる。\",\"basedOnReadingOrder\":[\"meat-i\",\"fish-i\"]}")
case "$mf_ab" in *'ナラティブが島meat-i, fish-iに触れていない'*'"aMissingInB":2'*) echo "  PASS: MF ⑤A/B照合（複数島の取りこぼし・aMissingInB:2・DOGFOOD-25）"; PASS=$((PASS+1));; *) echo "  FAIL: MF ⑤A/B照合（${mf_ab:0:200}）"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
mf_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$MF_ID")
check "MF 読戻し (200)" "200" "$mf_read"

echo ""
echo "--- シナリオ120: アミューズメント（集客と維持のトレードオフ） ---"
# 業態: レジャー・アミューズメント（ゲームセンター・アーケード）
# 想定人物: アミューズメント施設運営マネージャー
# 業務領域: ゲーム機・売上・客層・オペレーションのKJ分類と、施設運営・集客の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> タイトル提案(suggest-document-title・全体テーマ)
#          -> ナラティブ(generate-narrative) -> 読戻し
# 注意事項: 集客（新作ゲーム機の導入）と維持（筐体メンテナンスと稼働率）のトレードオフを矛盾検出
#          （正パス）で表面化し、施設運営の根拠にする。タイトル提案は**複数島の文書で全体テーマ
#          （両方の島ラベル）を反映**することを固定（DOGFOOD-26）。
AM_ID="biz-flow-amuse"
AM_DOC='{"version":1,"id":"'$AM_ID'","title":"アミューズメント施設の運営戦略","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"a1","text":"新作ゲーム機の導入で集客を増やしたい（集客・新規）","x":0,"y":0,"textReviewed":true},{"id":"a2","text":"子供向けエリアと大人向けエリアを分けたい（客層・ゾーニング）","x":10,"y":0,"textReviewed":true},{"id":"a3","text":"筐体のメンテナンスと稼働率はトレードオフの関係にあり優先順位が難しい（維持・稼働）","x":20,"y":0,"textReviewed":true},{"id":"a4","text":"クレーンゲームの景品原価と利益率のバランスに悩む（景品・利益）","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"amu-grow","cardIds":["a1","a2"]},{"id":"amu-ops","cardIds":["a3","a4"]}],"readingOrder":["amu-grow","amu-ops"]}'

am_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$AM_ID" \
  -H 'Content-Type: application/json' -d "$AM_DOC")
check "AM PUT document (作成)" "200" "$am_put"

# ① AI束ね（カテゴリ別の同グループ化）
am_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"a1","text":"新作ゲーム機の導入で集客を増やしたい（集客・新規）","textReviewed":true},{"id":"a2","text":"子供向けエリアと大人向けエリアを分けたい（客層・ゾーニング）","textReviewed":true},{"id":"a3","text":"筐体のメンテナンスと稼働率はトレードオフの関係にあり優先順位が難しい（維持・稼働）","textReviewed":true},{"id":"a4","text":"クレーンゲームの景品原価と利益率のバランスに悩む（景品・利益）","textReviewed":true}]}')
case "$am_groups" in *'"groups":'*) echo "  PASS: AM ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: AM ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約（集客・客層の島）
am_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$AM_DOC,\"islandId\":\"amu-grow\"}")
case "$am_summary" in *'"groundingIds":["a1","a2"]'*) echo "  PASS: AM ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: AM ②島要約（${am_summary:0:150}）"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（集客 vs 維持・集客と維持のトレードオフ・正パス）
am_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"a1","text":"新作ゲーム機の導入で集客を増やしたい（集客・新規）","textReviewed":true},"cardB":{"id":"a3","text":"筐体のメンテナンスと稼働率はトレードオフの関係にあり優先順位が難しい（維持・稼働）","textReviewed":true}}')
case "$am_contra" in *'"hasContradiction":true'*) echo "  PASS: AM ③矛盾検出（集客と維持のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: AM ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ タイトル提案（複数島の全体テーマ・両島ラベルを反映・DOGFOOD-26）
am_title=$(curl -s -X POST "$BASE_URL/ai/suggest-document-title" -H 'Content-Type: application/json' \
  -d '{"islandTitles":["アミューズメントの集客・客層戦略","ゲーム機の維持・景品利益"],"cardTexts":["新作ゲーム機の導入で集客を増やしたい","子供向けエリアと大人向けエリアを分けたい","筐体のメンテナンスと稼働率はトレードオフの関係にあり優先順位が難しい","クレーンゲームの景品原価と利益率のバランスに悩む"],"textReviewed":true}')
case "$am_title" in *'"candidates"'*'アミューズメントの集客・客層戦略'*'ゲーム機の維持・景品利益'*) echo "  PASS: AM ④タイトル提案（複数島の全体テーマを反映・DOGFOOD-26）"; PASS=$((PASS+1));; *) echo "  FAIL: AM ④タイトル提案（${am_title:0:200}）"; FAIL=$((FAIL+1));; esac

# ⑤ ナラティブ
am_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$AM_DOC}")
case "$am_narr" in *'"basedOnReadingOrder":["amu-grow","amu-ops"]'*) echo "  PASS: AM ⑤ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: AM ⑤ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
am_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$AM_ID")
check "AM 読戻し (200)" "200" "$am_read"

echo ""
echo "--- シナリオ121: 温浴・スパ（衛生管理と運営コストのトレードオフ） ---"
# 業態: レジャー・温浴（温泉・スパ・日帰り入浴）
# 想定人物: 温浴施設支配人／運営担当
# 業務領域: 施設運営・客層・清掃・料金のKJ分類と、集客・サービス改善の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary・4カード島の全接地)
#          -> 矛盾検出(detect-contradiction・正パス・説明文がカード対を参照) -> ナラティブ(generate-narrative)
#          -> A/B照合(check-narrative) -> 読戻し
# 注意事項: 衛生管理（清掃・再来訪）と運営コスト（改修の優先順位）のトレードオフを矛盾検出（正パス）で
#          表面化し、施設運営の根拠にする。矛盾検出の**説明文がカード対（衛生・品質 / 快適・コスト）を
#          参照**することを固定（DOGFOOD-27）。
SP_ID="biz-flow-spa"
SP_DOC='{"version":1,"id":"'$SP_ID'","title":"温浴施設の運営戦略","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"s1","text":"源泉の質や雰囲気を売りに集客を高めたい（集客・魅力）","x":0,"y":0,"textReviewed":true},{"id":"s2","text":"清掃と衛生管理を徹底し再来訪につなげたい（衛生・品質）","x":10,"y":0,"textReviewed":true},{"id":"s3","text":"施設の快適さと運営コストはトレードオフの関係にあり改修の優先順位が難しい（快適・コスト）","x":20,"y":0,"textReviewed":true},{"id":"s4","text":"混雑時の待ち時間と客の満足度のバランスに悩む（混雑・満足）","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"spa-i","cardIds":["s1","s2","s3","s4"]}],"readingOrder":["spa-i"]}'

sp_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$SP_ID" \
  -H 'Content-Type: application/json' -d "$SP_DOC")
check "SP PUT document (作成)" "200" "$sp_put"

# ① AI束ね（カテゴリ別の同グループ化）
sp_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"s1","text":"源泉の質や雰囲気を売りに集客を高めたい（集客・魅力）","textReviewed":true},{"id":"s2","text":"清掃と衛生管理を徹底し再来訪につなげたい（衛生・品質）","textReviewed":true},{"id":"s3","text":"施設の快適さと運営コストはトレードオフの関係にあり改修の優先順位が難しい（快適・コスト）","textReviewed":true},{"id":"s4","text":"混雑時の待ち時間と客の満足度のバランスに悩む（混雑・満足）","textReviewed":true}]}')
case "$sp_groups" in *'"groups":'*) echo "  PASS: SP ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: SP ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約（4カード島の全接地）
sp_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$SP_DOC,\"islandId\":\"spa-i\"}")
case "$sp_summary" in *'"groundingIds":["s1","s2","s3","s4"]'*) echo "  PASS: SP ②島要約（4カード島の全接地）"; PASS=$((PASS+1));; *) echo "  FAIL: SP ②島要約（${sp_summary:0:150}）"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（衛生 vs コスト・説明文がカード対を参照・DOGFOOD-27）
sp_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"s2","text":"清掃と衛生管理を徹底し再来訪につなげたい（衛生・品質）","textReviewed":true},"cardB":{"id":"s3","text":"施設の快適さと運営コストはトレードオフの関係にあり改修の優先順位が難しい（快適・コスト）","textReviewed":true}}')
case "$sp_contra" in *'"hasContradiction":true'*'清掃と衛生管理を徹底し再来訪につなげたい'*'施設の快適さと運営コストはトレードオフ'*) echo "  PASS: SP ③矛盾検出（説明文がカード対を参照・DOGFOOD-27）"; PASS=$((PASS+1));; *) echo "  FAIL: SP ③矛盾検出（${sp_contra:0:200}）"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
sp_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$SP_DOC}")
case "$sp_narr" in *'"basedOnReadingOrder":["spa-i"]'*) echo "  PASS: SP ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: SP ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ A/B照合（ナラティブが島spa-iに触れていない・a_missing_in_b）
sp_ab=$(curl -s -X POST "$BASE_URL/ai/check-narrative" -H 'Content-Type: application/json' \
  -d "{\"doc\":$SP_DOC,\"narrativeText\":\"（草稿）施設運営を検討する。ただし新施策には未検証の主張が含まれる。\",\"basedOnReadingOrder\":[\"spa-i\"]}")
case "$sp_ab" in *'ナラティブが島spa-iに触れていない'*'"aMissingInB":1'*) echo "  PASS: SP ⑤A/B照合（島spa-iの取りこぼし・a_missing_in_b）"; PASS=$((PASS+1));; *) echo "  FAIL: SP ⑤A/B照合（${sp_ab:0:150}）"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
sp_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$SP_ID")
check "SP 読戻し (200)" "200" "$sp_read"

echo ""
echo "--- シナリオ122: 映画館（集客と稼働のトレードオフ） ---"
# 業態: レジャー・映画（映画館・シネマコンプレックス）
# 想定人物: シネマコンプレックス支配人／興行担当
# 業務領域: 上映作品・客層・座席稼働・映画館運営のKJ分類と、編成・集客の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> 島間関係要約(summarize-island-relation・島A/Bを本文で参照)
#          -> ナラティブ(generate-narrative) -> 読戻し
# 注意事項: 集客（話題作の同時上映）と稼働（座席稼働率と上映回数）のトレードオフを矛盾検出（正パス）で
#          表面化し、編成・集客の根拠にする。島間関係要約は**本文が島A/B（cine-sched/cine-ops）を参照**
#          することを固定（DOGFOOD-28）。
CN_ID="biz-flow-cinema"
CN_DOC='{"version":1,"id":"'$CN_ID'","title":"シネマコンプレックス編成戦略","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"f1","text":"話題作の同時上映で集客を高めたい（集客・編成）","x":0,"y":0,"textReviewed":true},{"id":"f2","text":"客層に合わせたレイトショーや特別上映を組んで差別化したい（編成・客層）","x":10,"y":0,"textReviewed":true},{"id":"f3","text":"座席稼働率と上映回数はトレードオフの関係にあり回数調整が難しい（稼働・コスト）","x":20,"y":0,"textReviewed":true},{"id":"f4","text":"人気作品の長期上映と新作の投入のバランスに悩む（編成・新作）","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"cine-sched","cardIds":["f1","f2"]},{"id":"cine-ops","cardIds":["f3","f4"]}],"readingOrder":["cine-sched","cine-ops"]}'

cn_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$CN_ID" \
  -H 'Content-Type: application/json' -d "$CN_DOC")
check "CN PUT document (作成)" "200" "$cn_put"

# ① AI束ね（カテゴリ別の同グループ化）
cn_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"f1","text":"話題作の同時上映で集客を高めたい（集客・編成）","textReviewed":true},{"id":"f2","text":"客層に合わせたレイトショーや特別上映を組んで差別化したい（編成・客層）","textReviewed":true},{"id":"f3","text":"座席稼働率と上映回数はトレードオフの関係にあり回数調整が難しい（稼働・コスト）","textReviewed":true},{"id":"f4","text":"人気作品の長期上映と新作の投入のバランスに悩む（編成・新作）","textReviewed":true}]}')
case "$cn_groups" in *'"groups":'*) echo "  PASS: CN ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: CN ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約（集客・編成の島）
cn_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$CN_DOC,\"islandId\":\"cine-sched\"}")
case "$cn_summary" in *'"groundingIds":["f1","f2"]'*) echo "  PASS: CN ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: CN ②島要約（${cn_summary:0:150}）"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（集客 vs 稼働・集客と稼働のトレードオフ・正パス）
cn_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"f1","text":"話題作の同時上映で集客を高めたい（集客・編成）","textReviewed":true},"cardB":{"id":"f3","text":"座席稼働率と上映回数はトレードオフの関係にあり回数調整が難しい（稼働・コスト）","textReviewed":true}}')
case "$cn_contra" in *'"hasContradiction":true'*) echo "  PASS: CN ③矛盾検出（集客と稼働のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: CN ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ 島間関係要約（本文が島A/Bを参照・DOGFOOD-28）
cn_rel=$(curl -s -X POST "$BASE_URL/ai/summarize-island-relation" -H 'Content-Type: application/json' \
  -d "{\"doc\":$CN_DOC,\"islandAId\":\"cine-sched\",\"islandBId\":\"cine-ops\",\"relationType\":\"causal\",\"derived\":false,\"groundingCardIds\":[\"f3\"],\"groundingEdgeIds\":[],\"cardTexts\":[{\"id\":\"f3\",\"text\":\"座席稼働率と上映回数はトレードオフの関係にあり回数調整が難しい（稼働・コスト）\"}]}")
case "$cn_rel" in *'"text"'*'島cine-schedと島cine-ops'*) echo "  PASS: CN ④島間関係要約（本文が島A/Bを参照・DOGFOOD-28）"; PASS=$((PASS+1));; *) echo "  FAIL: CN ④島間関係要約（${cn_rel:0:200}）"; FAIL=$((FAIL+1));; esac

# ⑤ ナラティブ
cn_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$CN_DOC}")
case "$cn_narr" in *'"basedOnReadingOrder":["cine-sched","cine-ops"]'*) echo "  PASS: CN ⑤ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: CN ⑤ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
cn_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$CN_ID")
check "CN 読戻し (200)" "200" "$cn_read"

echo ""
echo "--- シナリオ123: 自転車店（サービスと在庫・レイアウトのトレードオフ） ---"
# 業態: 小売・自転車（サイクルショップ・修理販売）
# 想定人物: 自転車店店主／店舗運営担当
# 業務領域: 販売・修理・部品在庫・顧客の声のKJ分類と、品揃え・サービス改善の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary・表札がテーマを参照)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> A/B照合(check-narrative) -> 読戻し
# 注意事項: サービス（修理納期短縮・試乗体験）と在庫・レイアウト（拡充とスペース）のトレードオフを
#          矛盾検出（正パス）で表面化し、品揃え・サービス改善の根拠にする。島要約の**表札が島の
#          テーマ（顧客サービス）を参照**することを固定（DOGFOOD-29）。
BK_ID="biz-flow-bike"
BK_DOC='{"version":1,"id":"'$BK_ID'","title":"自転車店の品揃え・サービス戦略","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"b1","text":"サイズ合わせや試乗体験を充実させたい（顧客サービス）","x":0,"y":0,"textReviewed":true},{"id":"b2","text":"修理の納期を短縮し顧客満足を高めたい（顧客サービス）","x":10,"y":0,"textReviewed":true},{"id":"b3","text":"在庫の拡充と修理スペースはトレードオフの関係にあり店舗レイアウトが難しい（在庫・レイアウト）","x":20,"y":0,"textReviewed":true},{"id":"b4","text":"e-bikeやクロスバイクの需要に応える品揃えを検討したい（品揃え・新カテゴリ）","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"bike-i","cardIds":["b1","b2","b3","b4"]}],"readingOrder":["bike-i"]}'

bk_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$BK_ID" \
  -H 'Content-Type: application/json' -d "$BK_DOC")
check "BK PUT document (作成)" "200" "$bk_put"

# ① AI束ね（カテゴリ別の同グループ化）
bk_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"b1","text":"サイズ合わせや試乗体験を充実させたい（顧客サービス）","textReviewed":true},{"id":"b2","text":"修理の納期を短縮し顧客満足を高めたい（顧客サービス）","textReviewed":true},{"id":"b3","text":"在庫の拡充と修理スペースはトレードオフの関係にあり店舗レイアウトが難しい（在庫・レイアウト）","textReviewed":true},{"id":"b4","text":"e-bikeやクロスバイクの需要に応える品揃えを検討したい（品揃え・新カテゴリ）","textReviewed":true}]}')
case "$bk_groups" in *'"groups":'*) echo "  PASS: BK ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: BK ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約（表札が島のテーマを参照・DOGFOOD-29）
bk_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$BK_DOC,\"islandId\":\"bike-i\"}")
case "$bk_summary" in *'"summaryText"'*'顧客サービス'*) echo "  PASS: BK ②島要約（表札が島のテーマを参照・DOGFOOD-29）"; PASS=$((PASS+1));; *) echo "  FAIL: BK ②島要約（${bk_summary:0:200}）"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（サービス vs 在庫・レイアウト・サービスと在庫のトレードオフ・正パス）
bk_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"b2","text":"修理の納期を短縮し顧客満足を高めたい（顧客サービス）","textReviewed":true},"cardB":{"id":"b3","text":"在庫の拡充と修理スペースはトレードオフの関係にあり店舗レイアウトが難しい（在庫・レイアウト）","textReviewed":true}}')
case "$bk_contra" in *'"hasContradiction":true'*) echo "  PASS: BK ③矛盾検出（サービスと在庫・レイアウトのトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: BK ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
bk_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$BK_DOC}")
case "$bk_narr" in *'"basedOnReadingOrder":["bike-i"]'*) echo "  PASS: BK ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: BK ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ A/B照合（ナラティブが島bike-iに触れていない・a_missing_in_b）
bk_ab=$(curl -s -X POST "$BASE_URL/ai/check-narrative" -H 'Content-Type: application/json' \
  -d "{\"doc\":$BK_DOC,\"narrativeText\":\"（草稿）店舗運営を検討する。ただし新施策には未検証の主張が含まれる。\",\"basedOnReadingOrder\":[\"bike-i\"]}")
case "$bk_ab" in *'ナラティブが島bike-iに触れていない'*'"aMissingInB":1'*) echo "  PASS: BK ⑤A/B照合（島bike-iの取りこぼし・a_missing_in_b）"; PASS=$((PASS+1));; *) echo "  FAIL: BK ⑤A/B照合（${bk_ab:0:150}）"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
bk_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$BK_ID")
check "BK 読戻し (200)" "200" "$bk_read"

echo ""
echo "--- シナリオ124: フラワーショップ（ギフト需要と仕入れロスのトレードオフ） ---"
# 業態: 小売・生花（フラワーショップ・花屋）
# 想定人物: 生花店店主／フローリスト
# 業務領域: 仕入れ・花の在庫・アレンジメント・顧客の声のKJ分類と、品揃え・サービス改善の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> 配置提案(suggest-layout・島・読み順を保持)
#          -> ナラティブ(generate-narrative) -> 読戻し
# 注意事項: ギフト需要（冠婚葬祭・リピーター）と仕入れロス（発注バランス・廃棄）のトレードオフを
#          矛盾検出（正パス）で表面化し、品揃え・サービス改善の根拠にする。配置提案は**島・読み順
#          （flr-gift/flr-ops）を保持**することを固定（DOGFOOD-30）。
FL_ID="biz-flow-flower"
FL_DOC='{"version":1,"id":"'$FL_ID'","title":"フラワーショップの品揃え・サービス戦略","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"f1","text":"冠婚葬祭やギフト需要に応える品揃えを整えたい（ギフト需要）","x":0,"y":0,"textReviewed":true},{"id":"f2","text":"アレンジメント教室や定期宅配でリピーターを増やしたい（ギフト需要）","x":10,"y":0,"textReviewed":true},{"id":"f3","text":"仕入れ量と売れ残りの廃棄はトレードオフの関係にあり発注のバランスが難しい（仕入れ・ロス）","x":20,"y":0,"textReviewed":true},{"id":"f4","text":"鮮度管理と花の廃棄ロスを減らしたい（仕入れ・ロス）","x":30,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"flr-gift","cardIds":["f1","f2"]},{"id":"flr-ops","cardIds":["f3","f4"]}],"readingOrder":["flr-gift","flr-ops"]}'

fl_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$FL_ID" \
  -H 'Content-Type: application/json' -d "$FL_DOC")
check "FL PUT document (作成)" "200" "$fl_put"

# ① AI束ね（カテゴリ別の同グループ化）
fl_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"f1","text":"冠婚葬祭やギフト需要に応える品揃えを整えたい（ギフト需要）","textReviewed":true},{"id":"f2","text":"アレンジメント教室や定期宅配でリピーターを増やしたい（ギフト需要）","textReviewed":true},{"id":"f3","text":"仕入れ量と売れ残りの廃棄はトレードオフの関係にあり発注のバランスが難しい（仕入れ・ロス）","textReviewed":true},{"id":"f4","text":"鮮度管理と花の廃棄ロスを減らしたい（仕入れ・ロス）","textReviewed":true}]}')
case "$fl_groups" in *'"groups":'*) echo "  PASS: FL ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: FL ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約（ギフト需要の島）
fl_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$FL_DOC,\"islandId\":\"flr-gift\"}")
case "$fl_summary" in *'"groundingIds":["f1","f2"]'*) echo "  PASS: FL ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: FL ②島要約（${fl_summary:0:150}）"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（ギフト需要 vs 仕入れロス・需要とロスのトレードオフ・正パス）
fl_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"f1","text":"冠婚葬祭やギフト需要に応える品揃えを整えたい（ギフト需要）","textReviewed":true},"cardB":{"id":"f3","text":"仕入れ量と売れ残りの廃棄はトレードオフの関係にあり発注のバランスが難しい（仕入れ・ロス）","textReviewed":true}}')
case "$fl_contra" in *'"hasContradiction":true'*) echo "  PASS: FL ③矛盾検出（ギフト需要と仕入れロスのトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: FL ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ 配置提案（島・読み順を保持・DOGFOOD-30）
fl_layout=$(curl -s -X POST "$BASE_URL/ai/suggest-layout" -H 'Content-Type: application/json' \
  -d "{\"doc\":$FL_DOC}")
case "$fl_layout" in *'"suggestedDoc"'*'"islands"'*'"readingOrder":["flr-gift","flr-ops"]'*) echo "  PASS: FL ④配置提案（島・読み順を保持・DOGFOOD-30）"; PASS=$((PASS+1));; *) echo "  FAIL: FL ④配置提案（${fl_layout:0:200}）"; FAIL=$((FAIL+1));; esac

# ⑤ ナラティブ
fl_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$FL_DOC}")
case "$fl_narr" in *'"basedOnReadingOrder":["flr-gift","flr-ops"]'*) echo "  PASS: FL ⑤ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: FL ⑤ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑥ 読戻し
fl_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$FL_ID")
check "FL 読戻し (200)" "200" "$fl_read"

echo ""
echo "--- シナリオ125: 水産・漁業（資源保護と生計維持のトレードオフ） ---"
# 業態: 水産・漁業（漁協・水産加工）
# 想定人物: 漁協組合長／水産加工場責任者
# 業務領域: 漁獲量・資源管理・市場価格・加工現場の声のKJ分類と、持続可能な漁業と水産振興の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 資源保護（漁獲規制・休漁）と生計維持（漁獲量・雇用・価格）のトレードオフを
#          矛盾検出（正パス）で表面化し、持続可能な漁業と水産振興の根拠にする
#          （資源と生計の相克・漁業の担い手不足という構造課題も指摘）。
FIS_ID="biz-flow-fishery"
FIS_DOC='{"version":1,"id":"'$FIS_ID'","title":"水産資源と生計の両立","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"h1","text":"資源保護のため漁獲量の規制強化や休漁期間の設定を求める声","x":0,"y":0,"textReviewed":true},{"id":"h2","text":"規制強化は漁師の生計や雇用を圧迫し、資源保護と生計維持のトレードオフを招くという懸念","x":10,"y":0,"textReviewed":true},{"id":"h3","text":"鮮度保持のための加工・流通体制の整備と漁業の担い手育成が重要との指摘","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"hs-i","cardIds":["h1","h2","h3"]}],"readingOrder":["hs-i"]}'

fis_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$FIS_ID" \
  -H 'Content-Type: application/json' -d "$FIS_DOC")
check "FIS PUT document (作成)" "200" "$fis_put"

# ① AI束ね
fis_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"h1","text":"資源保護のため漁獲量の規制強化や休漁期間の設定を求める声","textReviewed":true},{"id":"h2","text":"規制強化は漁師の生計や雇用を圧迫し、資源保護と生計維持のトレードオフを招くという懸念","textReviewed":true},{"id":"h3","text":"鮮度保持のための加工・流通体制の整備と漁業の担い手育成が重要との指摘","textReviewed":true}]}')
case "$fis_groups" in *'"groups":'*) echo "  PASS: FIS ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: FIS ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
fis_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$FIS_DOC,\"islandId\":\"hs-i\"}")
case "$fis_summary" in *'"groundingIds":["h1","h2","h3"]'*) echo "  PASS: FIS ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: FIS ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（資源保護・規制 vs 生計維持・雇用・資源と生計のトレードオフ・正パス）
fis_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"h1","text":"資源保護のため漁獲量の規制強化や休漁期間の設定を求める声","textReviewed":true},"cardB":{"id":"h2","text":"規制強化は漁師の生計や雇用を圧迫し、資源保護と生計維持のトレードオフを招くという懸念","textReviewed":true}}')
case "$fis_contra" in *'"hasContradiction":true'*) echo "  PASS: FIS ③矛盾検出（資源保護と生計維持のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: FIS ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
fis_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$FIS_DOC}")
case "$fis_narr" in *'"basedOnReadingOrder":["hs-i"]'*) echo "  PASS: FIS ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: FIS ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
fis_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$FIS_ID")
check "FIS 読戻し (200)" "200" "$fis_read"

echo ""
echo "--- シナリオ126: 郵便・郵便局（ユニバーサルサービスと経営効率化のトレードオフ） ---"
# 業態: 郵便・郵便局（郵便ネットワーク・集配）
# 想定人物: 郵便局長／郵便ネットワーク計画担当
# 業務領域: 集配・郵便局窓口・配達網への声のKJ分類と、ユニバーサルサービス維持と経営効率化の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 全国一律の郵便・郵便局網の維持（ユニバーサルサービス）と経営効率化
#          （集配網縮小・料金改定）のトレードオフを矛盾検出（正パス）で表面化し、
#          郵便ネットワークの持続可能性の根拠にする（公共性と効率の相克・デジタル化と
#          荷物取扱拡大という新たな価値の模索も指摘）。
PST_ID="biz-flow-postal"
PST_DOC='{"version":1,"id":"'$PST_ID'","title":"郵便ネットワークの持続可能性","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"p1","text":"過疎地を含む全国一律の郵便・郵便局網の維持を求める声（ユニバーサルサービス）","x":0,"y":0,"textReviewed":true},{"id":"p2","text":"集配網の維持はコストがかさみ、合理化と料金見直しのトレードオフを迫るという懸念（経営効率化）","x":10,"y":0,"textReviewed":true},{"id":"p3","text":"デジタル化と荷物取扱の拡大で郵便ネットワークの新たな価値を模索する動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"pst-i","cardIds":["p1","p2","p3"]}],"readingOrder":["pst-i"]}'

pst_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$PST_ID" \
  -H 'Content-Type: application/json' -d "$PST_DOC")
check "PST PUT document (作成)" "200" "$pst_put"

# ① AI束ね
pst_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"p1","text":"過疎地を含む全国一律の郵便・郵便局網の維持を求める声（ユニバーサルサービス）","textReviewed":true},{"id":"p2","text":"集配網の維持はコストがかさみ、合理化と料金見直しのトレードオフを迫るという懸念（経営効率化）","textReviewed":true},{"id":"p3","text":"デジタル化と荷物取扱の拡大で郵便ネットワークの新たな価値を模索する動き","textReviewed":true}]}')
case "$pst_groups" in *'"groups":'*) echo "  PASS: PST ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: PST ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
pst_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$PST_DOC,\"islandId\":\"pst-i\"}")
case "$pst_summary" in *'"groundingIds":["p1","p2","p3"]'*) echo "  PASS: PST ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: PST ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（ユニバーサルサービス vs 経営効率化・公共性と効率のトレードオフ・正パス）
pst_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"p1","text":"過疎地を含む全国一律の郵便・郵便局網の維持を求める声（ユニバーサルサービス）","textReviewed":true},"cardB":{"id":"p2","text":"集配網の維持はコストがかさみ、合理化と料金見直しのトレードオフを迫るという懸念（経営効率化）","textReviewed":true}}')
case "$pst_contra" in *'"hasContradiction":true'*) echo "  PASS: PST ③矛盾検出（ユニバーサルサービスと経営効率化のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: PST ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
pst_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$PST_DOC}")
case "$pst_narr" in *'"basedOnReadingOrder":["pst-i"]'*) echo "  PASS: PST ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: PST ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
pst_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$PST_ID")
check "PST 読戻し (200)" "200" "$pst_read"

echo ""
echo "--- シナリオ127: 葬儀・斎場（遺族への丁寧な対応と費用の透明性のトレードオフ） ---"
# 業態: 葬儀・斎場（葬祭サービス）
# 想定人物: 葬儀ディレクター／葬祭コーディネーター
# 業務領域: 葬儀プラン・遺族の要望・費用・アフターケアの声のKJ分類と、葬祭サービスの改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 故人・遺族への丁寧な対応（グリーフケア・カスタムセレモニー）と費用の明確化
#          （見積もりの透明性・負担感）のトレードオフを矛盾検出（正パス）で表面化し、
#          葬祭サービスの信頼性の根拠にする（心の寄り添いと価格の相克・アフターケアで
#          遺族との長い関係を築く動きも指摘）。
FUN_ID="biz-flow-funeral"
FUN_DOC='{"version":1,"id":"'$FUN_ID'","title":"葬祭サービスの信頼性","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"f1","text":"故人への丁寧な対応と遺族の気持ちに寄り添うカスタムセレモニーを重視する声（グリーフケア）","x":0,"y":0,"textReviewed":true},{"id":"f2","text":"葬儀費用の見積もりが不透明で、丁寧な対応と費用のトレードオフに悩む声（費用の透明性）","x":10,"y":0,"textReviewed":true},{"id":"f3","text":"アフターケアや法要の案内で遺族との長い関係を築く動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"fun-i","cardIds":["f1","f2","f3"]}],"readingOrder":["fun-i"]}'

fun_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$FUN_ID" \
  -H 'Content-Type: application/json' -d "$FUN_DOC")
check "FUN PUT document (作成)" "200" "$fun_put"

# ① AI束ね
fun_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"f1","text":"故人への丁寧な対応と遺族の気持ちに寄り添うカスタムセレモニーを重視する声（グリーフケア）","textReviewed":true},{"id":"f2","text":"葬儀費用の見積もりが不透明で、丁寧な対応と費用のトレードオフに悩む声（費用の透明性）","textReviewed":true},{"id":"f3","text":"アフターケアや法要の案内で遺族との長い関係を築く動き","textReviewed":true}]}')
case "$fun_groups" in *'"groups":'*) echo "  PASS: FUN ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: FUN ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
fun_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$FUN_DOC,\"islandId\":\"fun-i\"}")
case "$fun_summary" in *'"groundingIds":["f1","f2","f3"]'*) echo "  PASS: FUN ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: FUN ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（丁寧な対応 vs 費用の透明性・心の寄り添いと価格の相克・正パス）
fun_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"f1","text":"故人への丁寧な対応と遺族の気持ちに寄り添うカスタムセレモニーを重視する声（グリーフケア）","textReviewed":true},"cardB":{"id":"f2","text":"葬儀費用の見積もりが不透明で、丁寧な対応と費用のトレードオフに悩む声（費用の透明性）","textReviewed":true}}')
case "$fun_contra" in *'"hasContradiction":true'*) echo "  PASS: FUN ③矛盾検出（遺族への丁寧な対応と費用の透明性のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: FUN ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
fun_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$FUN_DOC}")
case "$fun_narr" in *'"basedOnReadingOrder":["fun-i"]'*) echo "  PASS: FUN ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: FUN ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
fun_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$FUN_ID")
check "FUN 読戻し (200)" "200" "$fun_read"

echo ""
echo "--- シナリオ128: 演劇・舞台芸術（芸術性と興行の維持のトレードオフ） ---"
# 業態: 演劇・舞台芸術（劇場・劇団運営）
# 想定人物: 劇場支配人／芸術監督
# 業務領域: 演目の企画・観客の声・チケット販売・運営の声のKJ分類と、劇場運営の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 芸術性の追求（実験的演目・新人登用・質の維持）と集客・収益（興行の維持・
#          チケット価格）のトレードオフを矛盾検出（正パス）で表面化し、劇場運営の
#          持続可能性の根拠にする（創造性と経営の相克・常連ファンと地域とのつながりで
#          観客を育てる動きも指摘）。
TH_ID="biz-flow-theater"
TH_DOC='{"version":1,"id":"'$TH_ID'","title":"劇場運営の持続可能性","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"t1","text":"芸術性の高い実験的な演目や新人の登用を重視する声（芸術性）","x":0,"y":0,"textReviewed":true},{"id":"t2","text":"客席稼働率を高めるための集客・チケット価格戦略とのトレードオフに悩む声（収益・集客）","x":10,"y":0,"textReviewed":true},{"id":"t3","text":"常連のファンや地域とのつながり、ワークショップで観客を育てる動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"th-i","cardIds":["t1","t2","t3"]}],"readingOrder":["th-i"]}'

th_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$TH_ID" \
  -H 'Content-Type: application/json' -d "$TH_DOC")
check "TH PUT document (作成)" "200" "$th_put"

# ① AI束ね
th_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"t1","text":"芸術性の高い実験的な演目や新人の登用を重視する声（芸術性）","textReviewed":true},{"id":"t2","text":"客席稼働率を高めるための集客・チケット価格戦略とのトレードオフに悩む声（収益・集客）","textReviewed":true},{"id":"t3","text":"常連のファンや地域とのつながり、ワークショップで観客を育てる動き","textReviewed":true}]}')
case "$th_groups" in *'"groups":'*) echo "  PASS: TH ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: TH ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
th_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$TH_DOC,\"islandId\":\"th-i\"}")
case "$th_summary" in *'"groundingIds":["t1","t2","t3"]'*) echo "  PASS: TH ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: TH ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（芸術性 vs 集客・収益・創造性と経営の相克・正パス）
th_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"t1","text":"芸術性の高い実験的な演目や新人の登用を重視する声（芸術性）","textReviewed":true},"cardB":{"id":"t2","text":"客席稼働率を高めるための集客・チケット価格戦略とのトレードオフに悩む声（収益・集客）","textReviewed":true}}')
case "$th_contra" in *'"hasContradiction":true'*) echo "  PASS: TH ③矛盾検出（芸術性と興行の維持のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: TH ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
th_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$TH_DOC}")
case "$th_narr" in *'"basedOnReadingOrder":["th-i"]'*) echo "  PASS: TH ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: TH ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
th_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$TH_ID")
check "TH 読戻し (200)" "200" "$th_read"

echo ""
echo "--- シナリオ129: 酒類・醸造（伝統・品質と経営効率のトレードオフ） ---"
# 業態: 酒類・醸造（ワイナリー・酒蔵）
# 想定人物: 蔵元／製造責任者
# 業務領域: 醸造・品質・販路・後継者への声のKJ分類と、蔵の持続的経営の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 伝統的な製法と原料へのこだわり・品質と熟成の重視（伝統・品質）と生産量拡大や
#          価格競争への対応（経営効率）のトレードオフを矛盾検出（正パス）で表面化し、
#          蔵の持続的経営の根拠にする（品質と経営の相克・蔵の見学や体験型イベントで
#          ファンと後継者を育てる動きも指摘）。
BRW_ID="biz-flow-brewery"
BRW_DOC='{"version":1,"id":"'$BRW_ID'","title":"蔵の持続的経営","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"b1","text":"伝統的な製法と原料へのこだわりを守り、品質と熟成を重視する声（伝統・品質）","x":0,"y":0,"textReviewed":true},{"id":"b2","text":"生産量の拡大や価格競争への対応など、品質と経営のトレードオフに悩む声（経営効率）","x":10,"y":0,"textReviewed":true},{"id":"b3","text":"蔵の見学や体験型イベントでファンと後継者を育てる動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"brw-i","cardIds":["b1","b2","b3"]}],"readingOrder":["brw-i"]}'

brw_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$BRW_ID" \
  -H 'Content-Type: application/json' -d "$BRW_DOC")
check "BRW PUT document (作成)" "200" "$brw_put"

# ① AI束ね
brw_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"b1","text":"伝統的な製法と原料へのこだわりを守り、品質と熟成を重視する声（伝統・品質）","textReviewed":true},{"id":"b2","text":"生産量の拡大や価格競争への対応など、品質と経営のトレードオフに悩む声（経営効率）","textReviewed":true},{"id":"b3","text":"蔵の見学や体験型イベントでファンと後継者を育てる動き","textReviewed":true}]}')
case "$brw_groups" in *'"groups":'*) echo "  PASS: BRW ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: BRW ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
brw_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$BRW_DOC,\"islandId\":\"brw-i\"}")
case "$brw_summary" in *'"groundingIds":["b1","b2","b3"]'*) echo "  PASS: BRW ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: BRW ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（伝統・品質 vs 経営効率・品質と経営の相克・正パス）
brw_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"b1","text":"伝統的な製法と原料へのこだわりを守り、品質と熟成を重視する声（伝統・品質）","textReviewed":true},"cardB":{"id":"b2","text":"生産量の拡大や価格競争への対応など、品質と経営のトレードオフに悩む声（経営効率）","textReviewed":true}}')
case "$brw_contra" in *'"hasContradiction":true'*) echo "  PASS: BRW ③矛盾検出（伝統・品質と経営効率のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: BRW ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
brw_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$BRW_DOC}")
case "$brw_narr" in *'"basedOnReadingOrder":["brw-i"]'*) echo "  PASS: BRW ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: BRW ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
brw_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$BRW_ID")
check "BRW 読戻し (200)" "200" "$brw_read"

echo ""
echo "--- シナリオ130: 旅行代理店（顧客満足と販売効率のトレードオフ） ---"
# 業態: 旅行代理店（旅行業）
# 想定人物: 旅行コンサルタント／支店長
# 業務領域: 旅行プラン・顧客の声・トラブル対応・手配の声のKJ分類と、店舗・販売戦略の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 顧客一人ひとりに合わせた丁寧な旅行提案とトラブル時の寄り添い（顧客満足）と
#          オンライン化・手数料収入の減少への対応（販売効率）のトレードオフを矛盾検出
#          （正パス）で表面化し、店舗・販売戦略の改善根拠にする（丁寧さと効率の相克・
#          リピーターと地域密着のファンづくり・アフターフォローで関係を深める動きも指摘）。
TRAV_ID="biz-flow-travel"
TRAV_DOC='{"version":1,"id":"'$TRAV_ID'","title":"旅行代理店の販売戦略","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"t1","text":"顧客一人ひとりに合わせた丁寧な旅行提案とトラブル時の寄り添いを重視する声（顧客満足）","x":0,"y":0,"textReviewed":true},{"id":"t2","text":"オンライン予約の拡大で手数料収入が減り、丁寧な接客と販売効率のトレードオフに悩む声（販売効率）","x":10,"y":0,"textReviewed":true},{"id":"t3","text":"リピーターや地域密着のファンづくり、アフターフォローで関係を深める動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"trav-i","cardIds":["t1","t2","t3"]}],"readingOrder":["trav-i"]}'

trav_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$TRAV_ID" \
  -H 'Content-Type: application/json' -d "$TRAV_DOC")
check "TRAV PUT document (作成)" "200" "$trav_put"

# ① AI束ね
trav_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"t1","text":"顧客一人ひとりに合わせた丁寧な旅行提案とトラブル時の寄り添いを重視する声（顧客満足）","textReviewed":true},{"id":"t2","text":"オンライン予約の拡大で手数料収入が減り、丁寧な接客と販売効率のトレードオフに悩む声（販売効率）","textReviewed":true},{"id":"t3","text":"リピーターや地域密着のファンづくり、アフターフォローで関係を深める動き","textReviewed":true}]}')
case "$trav_groups" in *'"groups":'*) echo "  PASS: TRAV ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: TRAV ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
trav_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$TRAV_DOC,\"islandId\":\"trav-i\"}")
case "$trav_summary" in *'"groundingIds":["t1","t2","t3"]'*) echo "  PASS: TRAV ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: TRAV ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（顧客満足 vs 販売効率・丁寧さと効率の相克・正パス）
trav_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"t1","text":"顧客一人ひとりに合わせた丁寧な旅行提案とトラブル時の寄り添いを重視する声（顧客満足）","textReviewed":true},"cardB":{"id":"t2","text":"オンライン予約の拡大で手数料収入が減り、丁寧な接客と販売効率のトレードオフに悩む声（販売効率）","textReviewed":true}}')
case "$trav_contra" in *'"hasContradiction":true'*) echo "  PASS: TRAV ③矛盾検出（顧客満足と販売効率のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: TRAV ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
trav_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$TRAV_DOC}")
case "$trav_narr" in *'"basedOnReadingOrder":["trav-i"]'*) echo "  PASS: TRAV ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: TRAV ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
trav_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$TRAV_ID")
check "TRAV 読戻し (200)" "200" "$trav_read"

echo ""
echo "--- シナリオ131: クリーニング（仕上がり品質と処理効率のトレードオフ） ---"
# 業態: クリーニング（クリーニング店・宅配クリーニング）
# 想定人物: クリーニング店経営者／品質管理担当
# 業務領域: 仕上がり品質・受け渡し・料金・スタッフの声のKJ分類と、店舗・サービスの改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 仕上がりの品質と丁寧な検品・仕上げへのこだわり（顧客満足・品質）と短納期の処理や
#          価格競争への対応（処理効率・コスト）のトレードオフを矛盾検出（正パス）で表面化し、
#          店舗・サービスの改善根拠にする（品質と効率の相克・宅配クリーニングや定期利用で
#          顧客との長い関係を築く動きも指摘）。
CLN_ID="biz-flow-cleaner"
CLN_DOC='{"version":1,"id":"'$CLN_ID'","title":"クリーニング店のサービス改善","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"c1","text":"仕上がりの品質と丁寧な検品・仕上げへのこだわりを重視する声（品質・丁寧さ）","x":0,"y":0,"textReviewed":true},{"id":"c2","text":"短納期の処理や価格競争への対応など、品質と処理効率のトレードオフに悩む声（処理効率）","x":10,"y":0,"textReviewed":true},{"id":"c3","text":"宅配クリーニングや定期的な利用で顧客との長い関係を築く動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"cln-i","cardIds":["c1","c2","c3"]}],"readingOrder":["cln-i"]}'

cln_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$CLN_ID" \
  -H 'Content-Type: application/json' -d "$CLN_DOC")
check "CLN PUT document (作成)" "200" "$cln_put"

# ① AI束ね
cln_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"c1","text":"仕上がりの品質と丁寧な検品・仕上げへのこだわりを重視する声（品質・丁寧さ）","textReviewed":true},{"id":"c2","text":"短納期の処理や価格競争への対応など、品質と処理効率のトレードオフに悩む声（処理効率）","textReviewed":true},{"id":"c3","text":"宅配クリーニングや定期的な利用で顧客との長い関係を築く動き","textReviewed":true}]}')
case "$cln_groups" in *'"groups":'*) echo "  PASS: CLN ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: CLN ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
cln_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$CLN_DOC,\"islandId\":\"cln-i\"}")
case "$cln_summary" in *'"groundingIds":["c1","c2","c3"]'*) echo "  PASS: CLN ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: CLN ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（品質・丁寧さ vs 処理効率・品質と効率の相克・正パス）
cln_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"c1","text":"仕上がりの品質と丁寧な検品・仕上げへのこだわりを重視する声（品質・丁寧さ）","textReviewed":true},"cardB":{"id":"c2","text":"短納期の処理や価格競争への対応など、品質と処理効率のトレードオフに悩む声（処理効率）","textReviewed":true}}')
case "$cln_contra" in *'"hasContradiction":true'*) echo "  PASS: CLN ③矛盾検出（仕上がり品質と処理効率のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: CLN ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
cln_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$CLN_DOC}")
case "$cln_narr" in *'"basedOnReadingOrder":["cln-i"]'*) echo "  PASS: CLN ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: CLN ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
cln_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$CLN_ID")
check "CLN 読戻し (200)" "200" "$cln_read"

echo ""
echo "--- シナリオ132: 林業・木材（森林保全と林業の採算のトレードオフ） ---"
# 業態: 林業・木材（森林経営・製材）
# 想定人物: 森林組合リーダー／林業経営者
# 業務領域: 森林保全・伐採・木材利用・担い手への声のKJ分類と、持続可能な林業の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 森林の保全（水源涵養・生物多様性）と林業の採算（伐採・木材価格・担い手不足）の
#          トレードオフを矛盾検出（正パス）で表面化し、持続可能な林業の根拠にする
#          （環境と生業の相克・林業体験や木材利用の促進で地域と山をつなぎ担い手を育てる動きも指摘）。
FOR_ID="biz-flow-forestry"
FOR_DOC='{"version":1,"id":"'$FOR_ID'","title":"持続可能な林業","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"fo1","text":"森林の保全や水源涵養・生物多様性を守る間伐や持続可能な経営を重視する声（環境・保全）","x":0,"y":0,"textReviewed":true},{"id":"fo2","text":"木材価格の低迷や担い手不足など、森林保全と林業の採算のトレードオフに悩む声（採算・担い手）","x":10,"y":0,"textReviewed":true},{"id":"fo3","text":"林業体験や木材利用の促進で地域と山をつなぎ、担い手を育てる動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"for-i","cardIds":["fo1","fo2","fo3"]}],"readingOrder":["for-i"]}'

for_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$FOR_ID" \
  -H 'Content-Type: application/json' -d "$FOR_DOC")
check "FOR PUT document (作成)" "200" "$for_put"

# ① AI束ね
for_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"fo1","text":"森林の保全や水源涵養・生物多様性を守る間伐や持続可能な経営を重視する声（環境・保全）","textReviewed":true},{"id":"fo2","text":"木材価格の低迷や担い手不足など、森林保全と林業の採算のトレードオフに悩む声（採算・担い手）","textReviewed":true},{"id":"fo3","text":"林業体験や木材利用の促進で地域と山をつなぎ、担い手を育てる動き","textReviewed":true}]}')
case "$for_groups" in *'"groups":'*) echo "  PASS: FOR ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: FOR ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
for_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$FOR_DOC,\"islandId\":\"for-i\"}")
case "$for_summary" in *'"groundingIds":["fo1","fo2","fo3"]'*) echo "  PASS: FOR ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: FOR ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（森林保全 vs 林業の採算・環境と生業の相克・正パス）
for_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"fo1","text":"森林の保全や水源涵養・生物多様性を守る間伐や持続可能な経営を重視する声（環境・保全）","textReviewed":true},"cardB":{"id":"fo2","text":"木材価格の低迷や担い手不足など、森林保全と林業の採算のトレードオフに悩む声（採算・担い手）","textReviewed":true}}')
case "$for_contra" in *'"hasContradiction":true'*) echo "  PASS: FOR ③矛盾検出（森林保全と林業の採算のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: FOR ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
for_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$FOR_DOC}")
case "$for_narr" in *'"basedOnReadingOrder":["for-i"]'*) echo "  PASS: FOR ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: FOR ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
for_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$FOR_ID")
check "FOR 読戻し (200)" "200" "$for_read"

echo ""
echo "--- シナリオ133: 信用金庫・地域金融（地域密着支援と健全経営のトレードオフ） ---"
# 業態: 信用金庫・地域金融（地域金融機関）
# 想定人物: 融資担当／地域金融コーディネーター
# 業務領域: 融資・地域貢献・事業支援・預金への声のKJ分類と、地域金融の在り方の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 地域の中小企業や個人事業主への丁寧な伴走支援と地域貢献（地域密着・支援）と
#          収益性・融資の健全性を守る審査強化（健全性・収益）のトレードオフを矛盾検出
#          （正パス）で表面化し、地域金融の在り方の根拠にする（支援と健全性の相克・
#          地域の事業者との長い付き合いや金融教育で信頼を築く動きも指摘）。
SB_ID="biz-flow-shinkin"
SB_DOC='{"version":1,"id":"'$SB_ID'","title":"地域金融の在り方","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"s1","text":"地域の中小企業や個人事業主への丁寧な伴走支援と地域貢献を重視する声（地域密着・支援）","x":0,"y":0,"textReviewed":true},{"id":"s2","text":"収益性や融資の健全性を守るための審査強化など、地域支援と健全経営のトレードオフに悩む声（健全性・収益）","x":10,"y":0,"textReviewed":true},{"id":"s3","text":"地域の事業者との長い付き合いや金融教育で信頼を築く動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"sb-i","cardIds":["s1","s2","s3"]}],"readingOrder":["sb-i"]}'

sb_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$SB_ID" \
  -H 'Content-Type: application/json' -d "$SB_DOC")
check "SB PUT document (作成)" "200" "$sb_put"

# ① AI束ね
sb_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"s1","text":"地域の中小企業や個人事業主への丁寧な伴走支援と地域貢献を重視する声（地域密着・支援）","textReviewed":true},{"id":"s2","text":"収益性や融資の健全性を守るための審査強化など、地域支援と健全経営のトレードオフに悩む声（健全性・収益）","textReviewed":true},{"id":"s3","text":"地域の事業者との長い付き合いや金融教育で信頼を築く動き","textReviewed":true}]}')
case "$sb_groups" in *'"groups":'*) echo "  PASS: SB ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: SB ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
sb_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$SB_DOC,\"islandId\":\"sb-i\"}")
case "$sb_summary" in *'"groundingIds":["s1","s2","s3"]'*) echo "  PASS: SB ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: SB ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（地域密着支援 vs 健全経営・支援と健全性の相克・正パス）
sb_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"s1","text":"地域の中小企業や個人事業主への丁寧な伴走支援と地域貢献を重視する声（地域密着・支援）","textReviewed":true},"cardB":{"id":"s2","text":"収益性や融資の健全性を守るための審査強化など、地域支援と健全経営のトレードオフに悩む声（健全性・収益）","textReviewed":true}}')
case "$sb_contra" in *'"hasContradiction":true'*) echo "  PASS: SB ③矛盾検出（地域密着支援と健全経営のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: SB ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
sb_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$SB_DOC}")
case "$sb_narr" in *'"basedOnReadingOrder":["sb-i"]'*) echo "  PASS: SB ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: SB ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
sb_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$SB_ID")
check "SB 読戻し (200)" "200" "$sb_read"

echo ""
echo "--- シナリオ134: 港・海運（港湾の効率運用と環境・地域のトレードオフ） ---"
# 業態: 港・海運（港湾・物流基地）
# 想定人物: 港湾管理者／物流オペレーション責任者
# 業務領域: 港湾施設・貨物取扱・環境・地域雇用への声のKJ分類と、港湾と地域の共存の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: コンテナ処理の自動化や24時間運用による港湾の効率（効率・自動化）と騒音・環境負荷・
#          雇用への影響（環境・労働）のトレードオフを矛盾検出（正パス）で表面化し、港湾と
#          地域の共存の根拠にする（効率と環境の相克・地域雇用や物流の要としての港湾の位置づけも指摘）。
HAB_ID="biz-flow-harbor"
HAB_DOC='{"version":1,"id":"'$HAB_ID'","title":"港湾と地域の共存","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"h1","text":"コンテナ処理の自動化や24時間運用で港湾の効率を高めるべきとの声（効率・自動化）","x":0,"y":0,"textReviewed":true},{"id":"h2","text":"24時間運用や自動化は騒音・環境負荷・雇用への影響など、効率と環境・労働のトレードオフに悩む声（環境・労働）","x":10,"y":0,"textReviewed":true},{"id":"h3","text":"地域雇用や物流の要として、港湾と地域の共存を目指す動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"hab-i","cardIds":["h1","h2","h3"]}],"readingOrder":["hab-i"]}'

hab_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$HAB_ID" \
  -H 'Content-Type: application/json' -d "$HAB_DOC")
check "HAB PUT document (作成)" "200" "$hab_put"

# ① AI束ね
hab_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"h1","text":"コンテナ処理の自動化や24時間運用で港湾の効率を高めるべきとの声（効率・自動化）","textReviewed":true},{"id":"h2","text":"24時間運用や自動化は騒音・環境負荷・雇用への影響など、効率と環境・労働のトレードオフに悩む声（環境・労働）","textReviewed":true},{"id":"h3","text":"地域雇用や物流の要として、港湾と地域の共存を目指す動き","textReviewed":true}]}')
case "$hab_groups" in *'"groups":'*) echo "  PASS: HAB ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: HAB ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
hab_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$HAB_DOC,\"islandId\":\"hab-i\"}")
case "$hab_summary" in *'"groundingIds":["h1","h2","h3"]'*) echo "  PASS: HAB ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: HAB ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（効率・自動化 vs 環境・労働・効率と環境の相克・正パス）
hab_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"h1","text":"コンテナ処理の自動化や24時間運用で港湾の効率を高めるべきとの声（効率・自動化）","textReviewed":true},"cardB":{"id":"h2","text":"24時間運用や自動化は騒音・環境負荷・雇用への影響など、効率と環境・労働のトレードオフに悩む声（環境・労働）","textReviewed":true}}')
case "$hab_contra" in *'"hasContradiction":true'*) echo "  PASS: HAB ③矛盾検出（港湾の効率運用と環境・地域のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: HAB ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
hab_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$HAB_DOC}")
case "$hab_narr" in *'"basedOnReadingOrder":["hab-i"]'*) echo "  PASS: HAB ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: HAB ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
hab_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$HAB_ID")
check "HAB 読戻し (200)" "200" "$hab_read"

echo ""
echo "--- シナリオ135: 理美容・ヘアサロン（施術の質と回転率のトレードオフ） ---"
# 業態: 理美容・ヘアサロン（理美容室）
# 想定人物: サロンオーナー／スタイリスト
# 業務領域: 施術・カウンセリング・価格・スタッフ育成への声のKJ分類と、サロン運営の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 丁寧なカウンセリングと一人ひとりに合わせた施術の質（顧客満足・時間）と予約の
#          回転率や価格競争への対応（収益・効率）のトレードオフを矛盾検出（正パス）で表面化し、
#          サロン運営の改善根拠にする（施術の質と収益の相克・スタイリストの育成や技術向上への
#          投資・リピーターづくりで信頼を築く動きも指摘）。
SALON_ID="biz-flow-salon"
SALON_DOC='{"version":1,"id":"'$SALON_ID'","title":"サロン運営の改善","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"sa1","text":"丁寧なカウンセリングと一人ひとりに合わせた施術の質を重視する声（施術の質・丁寧さ）","x":0,"y":0,"textReviewed":true},{"id":"sa2","text":"予約の回転率や価格競争への対応など、施術の質と収益・効率のトレードオフに悩む声（収益・回転）","x":10,"y":0,"textReviewed":true},{"id":"sa3","text":"スタイリストの育成や技術向上への投資、リピーターづくりで信頼を築く動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"salon-i","cardIds":["sa1","sa2","sa3"]}],"readingOrder":["salon-i"]}'

salon_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$SALON_ID" \
  -H 'Content-Type: application/json' -d "$SALON_DOC")
check "SALON PUT document (作成)" "200" "$salon_put"

# ① AI束ね
salon_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"sa1","text":"丁寧なカウンセリングと一人ひとりに合わせた施術の質を重視する声（施術の質・丁寧さ）","textReviewed":true},{"id":"sa2","text":"予約の回転率や価格競争への対応など、施術の質と収益・効率のトレードオフに悩む声（収益・回転）","textReviewed":true},{"id":"sa3","text":"スタイリストの育成や技術向上への投資、リピーターづくりで信頼を築く動き","textReviewed":true}]}')
case "$salon_groups" in *'"groups":'*) echo "  PASS: SALON ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: SALON ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
salon_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$SALON_DOC,\"islandId\":\"salon-i\"}")
case "$salon_summary" in *'"groundingIds":["sa1","sa2","sa3"]'*) echo "  PASS: SALON ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: SALON ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（施術の質 vs 収益・効率・施術の質と収益の相克・正パス）
salon_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"sa1","text":"丁寧なカウンセリングと一人ひとりに合わせた施術の質を重視する声（施術の質・丁寧さ）","textReviewed":true},"cardB":{"id":"sa2","text":"予約の回転率や価格競争への対応など、施術の質と収益・効率のトレードオフに悩む声（収益・回転）","textReviewed":true}}')
case "$salon_contra" in *'"hasContradiction":true'*) echo "  PASS: SALON ③矛盾検出（施術の質と回転率のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: SALON ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
salon_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$SALON_DOC}")
case "$salon_narr" in *'"basedOnReadingOrder":["salon-i"]'*) echo "  PASS: SALON ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: SALON ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
salon_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$SALON_ID")
check "SALON 読戻し (200)" "200" "$salon_read"

echo ""
echo "--- シナリオ136: 出版社・書籍出版（内容・編集と売上・採算のトレードオフ） ---"
# 業態: 出版社・書籍出版（出版・書店流通）
# 想定人物: 編集者／出版企画担当
# 業務領域: 出版企画・著者・販売・読者への声のKJ分類と、持続可能な出版の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 質の高い書籍の刊行（内容・編集・文化）と出版不況への対応（売上・電子化・在庫）の
#          トレードオフを矛盾検出（正パス）で表面化し、持続可能な出版の根拠にする
#          （内容と採算の相克・書店や読書イベントとの連携・電子書籍と紙の共存で読者との
#          関係を築く動きも指摘）。
PUB_ID="biz-flow-publisher"
PUB_DOC='{"version":1,"id":"'$PUB_ID'","title":"持続可能な出版","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"p1","text":"質の高い内容と丁寧な編集にこだわり、文化や知の蓄積を担う出版を重視する声（内容・編集）","x":0,"y":0,"textReviewed":true},{"id":"p2","text":"出版不況や電子化への対応など、質の高い出版と売上・採算のトレードオフに悩む声（売上・採算）","x":10,"y":0,"textReviewed":true},{"id":"p3","text":"書店や読書イベントとの連携、電子書籍と紙の共存で読者との関係を築く動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"pub-i","cardIds":["p1","p2","p3"]}],"readingOrder":["pub-i"]}'

pub_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$PUB_ID" \
  -H 'Content-Type: application/json' -d "$PUB_DOC")
check "PUB PUT document (作成)" "200" "$pub_put"

# ① AI束ね
pub_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"p1","text":"質の高い内容と丁寧な編集にこだわり、文化や知の蓄積を担う出版を重視する声（内容・編集）","textReviewed":true},{"id":"p2","text":"出版不況や電子化への対応など、質の高い出版と売上・採算のトレードオフに悩む声（売上・採算）","textReviewed":true},{"id":"p3","text":"書店や読書イベントとの連携、電子書籍と紙の共存で読者との関係を築く動き","textReviewed":true}]}')
case "$pub_groups" in *'"groups":'*) echo "  PASS: PUB ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: PUB ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
pub_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$PUB_DOC,\"islandId\":\"pub-i\"}")
case "$pub_summary" in *'"groundingIds":["p1","p2","p3"]'*) echo "  PASS: PUB ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: PUB ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（内容・編集 vs 売上・採算・内容と採算の相克・正パス）
pub_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"p1","text":"質の高い内容と丁寧な編集にこだわり、文化や知の蓄積を担う出版を重視する声（内容・編集）","textReviewed":true},"cardB":{"id":"p2","text":"出版不況や電子化への対応など、質の高い出版と売上・採算のトレードオフに悩む声（売上・採算）","textReviewed":true}}')
case "$pub_contra" in *'"hasContradiction":true'*) echo "  PASS: PUB ③矛盾検出（内容・編集と売上・採算のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: PUB ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
pub_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$PUB_DOC}")
case "$pub_narr" in *'"basedOnReadingOrder":["pub-i"]'*) echo "  PASS: PUB ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: PUB ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
pub_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$PUB_ID")
check "PUB 読戻し (200)" "200" "$pub_read"

echo ""
echo "--- シナリオ137: 医療機器（安全性・品質と市場投入スピードのトレードオフ） ---"
# 業態: 医療機器（医療機器メーカー・販売）
# 想定人物: 医療機器営業／マーケティング責任者
# 業務領域: 製品開発・臨床現場の声・品質・規制への声のKJ分類と、医療機器開発の在り方の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 患者安全のための品質・安全性と規制対応の確保（安全性・品質）と開発期間の短縮や
#          コスト削減への圧力（スピード・コスト）のトレードオフを矛盾検出（正パス）で表面化し、
#          医療機器開発の在り方の根拠にする（安全性とスピードの相克・臨床現場の声を製品開発に
#          活かし医療現場とともに歩む動きも指摘）。
MED_ID="biz-flow-meddevice"
MED_DOC='{"version":1,"id":"'$MED_ID'","title":"医療機器開発の在り方","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"m1","text":"患者安全のための品質・安全性と規制対応を最優先する声（安全性・品質）","x":0,"y":0,"textReviewed":true},{"id":"m2","text":"開発期間の短縮やコスト削減への圧力など、安全性と市場投入スピードのトレードオフに悩む声（スピード・コスト）","x":10,"y":0,"textReviewed":true},{"id":"m3","text":"臨床現場の声を製品開発に活かし、医療現場とともに歩む動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"med-i","cardIds":["m1","m2","m3"]}],"readingOrder":["med-i"]}'

med_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$MED_ID" \
  -H 'Content-Type: application/json' -d "$MED_DOC")
check "MED PUT document (作成)" "200" "$med_put"

# ① AI束ね
med_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"m1","text":"患者安全のための品質・安全性と規制対応を最優先する声（安全性・品質）","textReviewed":true},{"id":"m2","text":"開発期間の短縮やコスト削減への圧力など、安全性と市場投入スピードのトレードオフに悩む声（スピード・コスト）","textReviewed":true},{"id":"m3","text":"臨床現場の声を製品開発に活かし、医療現場とともに歩む動き","textReviewed":true}]}')
case "$med_groups" in *'"groups":'*) echo "  PASS: MED ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: MED ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
med_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$MED_DOC,\"islandId\":\"med-i\"}")
case "$med_summary" in *'"groundingIds":["m1","m2","m3"]'*) echo "  PASS: MED ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: MED ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（安全性・品質 vs スピード・コスト・安全性とスピードの相克・正パス）
med_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"m1","text":"患者安全のための品質・安全性と規制対応を最優先する声（安全性・品質）","textReviewed":true},"cardB":{"id":"m2","text":"開発期間の短縮やコスト削減への圧力など、安全性と市場投入スピードのトレードオフに悩む声（スピード・コスト）","textReviewed":true}}')
case "$med_contra" in *'"hasContradiction":true'*) echo "  PASS: MED ③矛盾検出（安全性・品質と市場投入スピードのトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: MED ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
med_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$MED_DOC}")
case "$med_narr" in *'"basedOnReadingOrder":["med-i"]'*) echo "  PASS: MED ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: MED ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
med_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$MED_ID")
check "MED 読戻し (200)" "200" "$med_read"

echo ""
echo "--- シナリオ138: 石油・ガス（供給の安定・保安と料金・効率のトレードオフ） ---"
# 業態: 石油・ガス（エネルギー供給・販売）
# 想定人物: エネルギー供給責任者／営業所長
# 業務領域: 供給・保安・料金・顧客への声のKJ分類と、エネルギー供給の在り方の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 供給の安定と保安（ガス漏れ防止・点検・停供防止）の確保（安定・保安）と料金競争や
#          コスト削減への対応（料金・効率）のトレードオフを矛盾検出（正パス）で表面化し、
#          エネルギー供給の在り方の根拠にする（安定・保安と効率の相克・省エネや機器の提案、
#          脱炭素対応を模索する動きも指摘）。
ENER_ID="biz-flow-energy-supply"
ENER_DOC='{"version":1,"id":"'$ENER_ID'","title":"エネルギー供給の在り方","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"g1","text":"供給の安定と保安（ガス漏れ防止・点検）を最優先する声（安定・保安）","x":0,"y":0,"textReviewed":true},{"id":"g2","text":"料金競争やコスト削減への対応など、保安・安定と料金・効率のトレードオフに悩む声（料金・効率）","x":10,"y":0,"textReviewed":true},{"id":"g3","text":"省エネや機器の提案など、顧客との長い関係と脱炭素対応を模索する動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"ener-i","cardIds":["g1","g2","g3"]}],"readingOrder":["ener-i"]}'

ener_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$ENER_ID" \
  -H 'Content-Type: application/json' -d "$ENER_DOC")
check "ENER PUT document (作成)" "200" "$ener_put"

# ① AI束ね
ener_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"g1","text":"供給の安定と保安（ガス漏れ防止・点検）を最優先する声（安定・保安）","textReviewed":true},{"id":"g2","text":"料金競争やコスト削減への対応など、保安・安定と料金・効率のトレードオフに悩む声（料金・効率）","textReviewed":true},{"id":"g3","text":"省エネや機器の提案など、顧客との長い関係と脱炭素対応を模索する動き","textReviewed":true}]}')
case "$ener_groups" in *'"groups":'*) echo "  PASS: ENER ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: ENER ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
ener_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$ENER_DOC,\"islandId\":\"ener-i\"}")
case "$ener_summary" in *'"groundingIds":["g1","g2","g3"]'*) echo "  PASS: ENER ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: ENER ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（安定・保安 vs 料金・効率・安定・保安と効率の相克・正パス）
ener_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"g1","text":"供給の安定と保安（ガス漏れ防止・点検）を最優先する声（安定・保安）","textReviewed":true},"cardB":{"id":"g2","text":"料金競争やコスト削減への対応など、保安・安定と料金・効率のトレードオフに悩む声（料金・効率）","textReviewed":true}}')
case "$ener_contra" in *'"hasContradiction":true'*) echo "  PASS: ENER ③矛盾検出（供給の安定・保安と料金・効率のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: ENER ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
ener_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$ENER_DOC}")
case "$ener_narr" in *'"basedOnReadingOrder":["ener-i"]'*) echo "  PASS: ENER ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: ENER ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
ener_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$ENER_ID")
check "ENER 読戻し (200)" "200" "$ener_read"

echo ""
echo "--- シナリオ139: 家電量販店（接客・アフターと価格・売上のトレードオフ） ---"
# 業態: 家電量販店（家電小売・販売）
# 想定人物: 店長／販売責任者
# 業務領域: 商品・接客・価格・アフターサービスへの声のKJ分類と、店舗運営の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 商品の丁寧な説明とアフターサービス・相談に乗る接客（顧客満足・信頼）とネット通販や
#          価格競争への対応（価格・売上）のトレードオフを矛盾検出（正パス）で表面化し、
#          店舗運営の改善根拠にする（接客と価格の相克・家電の設置や修理・買い替え相談で
#          顧客との長い関係を築く動きも指摘）。
ELEC_ID="biz-flow-electronics"
ELEC_DOC='{"version":1,"id":"'$ELEC_ID'","title":"家電量販店の店舗運営","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"e1","text":"商品の丁寧な説明とアフターサービス・相談に乗る接客を重視する声（接客・アフター）","x":0,"y":0,"textReviewed":true},{"id":"e2","text":"ネット通販や価格競争への対応など、接客の質と売上・価格のトレードオフに悩む声（価格・売上）","x":10,"y":0,"textReviewed":true},{"id":"e3","text":"家電の設置や修理、買い替え相談で顧客との長い関係を築く動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"elec-i","cardIds":["e1","e2","e3"]}],"readingOrder":["elec-i"]}'

elec_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$ELEC_ID" \
  -H 'Content-Type: application/json' -d "$ELEC_DOC")
check "ELEC PUT document (作成)" "200" "$elec_put"

# ① AI束ね
elec_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"e1","text":"商品の丁寧な説明とアフターサービス・相談に乗る接客を重視する声（接客・アフター）","textReviewed":true},{"id":"e2","text":"ネット通販や価格競争への対応など、接客の質と売上・価格のトレードオフに悩む声（価格・売上）","textReviewed":true},{"id":"e3","text":"家電の設置や修理、買い替え相談で顧客との長い関係を築く動き","textReviewed":true}]}')
case "$elec_groups" in *'"groups":'*) echo "  PASS: ELEC ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: ELEC ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
elec_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$ELEC_DOC,\"islandId\":\"elec-i\"}")
case "$elec_summary" in *'"groundingIds":["e1","e2","e3"]'*) echo "  PASS: ELEC ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: ELEC ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（接客・アフター vs 価格・売上・接客と価格の相克・正パス）
elec_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"e1","text":"商品の丁寧な説明とアフターサービス・相談に乗る接客を重視する声（接客・アフター）","textReviewed":true},"cardB":{"id":"e2","text":"ネット通販や価格競争への対応など、接客の質と売上・価格のトレードオフに悩む声（価格・売上）","textReviewed":true}}')
case "$elec_contra" in *'"hasContradiction":true'*) echo "  PASS: ELEC ③矛盾検出（接客・アフターと価格・売上のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: ELEC ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
elec_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$ELEC_DOC}")
case "$elec_narr" in *'"basedOnReadingOrder":["elec-i"]'*) echo "  PASS: ELEC ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: ELEC ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
elec_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$ELEC_ID")
check "ELEC 読戻し (200)" "200" "$elec_read"

echo ""
echo "--- シナリオ140: 宝飾・ジュエリー（品質・信頼と価格・採算のトレードオフ） ---"
# 業態: 宝飾・ジュエリー（宝石・貴金属小売）
# 想定人物: ジュエリーショップ店長／バイヤー
# 業務領域: 商品・接客・価格・信頼への声のKJ分類と、ジュエリー店の運営改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 品質の保証と生涯のアフターケア・丁寧な接客による信頼（品質・信頼）と仕入れコストや
#          流行への対応（価格・採算）のトレードオフを矛盾検出（正パス）で表面化し、ジュエリー店の
#          運営改善根拠にする（品質と採算の相克・婚約・記念日などの特別な場面を支え長く付き合う
#          顧客との関係を築く動きも指摘）。
JEW_ID="biz-flow-jewelry"
JEW_DOC='{"version":1,"id":"'$JEW_ID'","title":"ジュエリー店の運営改善","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"j1","text":"品質の保証と生涯のアフターケア、丁寧な接客で信頼を築くことを重視する声（品質・信頼）","x":0,"y":0,"textReviewed":true},{"id":"j2","text":"仕入れコストや流行への対応など、品質・信頼と価格・採算のトレードオフに悩む声（価格・採算）","x":10,"y":0,"textReviewed":true},{"id":"j3","text":"婚約・記念日などの特別な場面を支え、長く付き合う顧客との関係を築く動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"jew-i","cardIds":["j1","j2","j3"]}],"readingOrder":["jew-i"]}'

jew_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$JEW_ID" \
  -H 'Content-Type: application/json' -d "$JEW_DOC")
check "JEW PUT document (作成)" "200" "$jew_put"

# ① AI束ね
jew_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"j1","text":"品質の保証と生涯のアフターケア、丁寧な接客で信頼を築くことを重視する声（品質・信頼）","textReviewed":true},{"id":"j2","text":"仕入れコストや流行への対応など、品質・信頼と価格・採算のトレードオフに悩む声（価格・採算）","textReviewed":true},{"id":"j3","text":"婚約・記念日などの特別な場面を支え、長く付き合う顧客との関係を築く動き","textReviewed":true}]}')
case "$jew_groups" in *'"groups":'*) echo "  PASS: JEW ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: JEW ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
jew_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$JEW_DOC,\"islandId\":\"jew-i\"}")
case "$jew_summary" in *'"groundingIds":["j1","j2","j3"]'*) echo "  PASS: JEW ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: JEW ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（品質・信頼 vs 価格・採算・品質と採算の相克・正パス）
jew_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"j1","text":"品質の保証と生涯のアフターケア、丁寧な接客で信頼を築くことを重視する声（品質・信頼）","textReviewed":true},"cardB":{"id":"j2","text":"仕入れコストや流行への対応など、品質・信頼と価格・採算のトレードオフに悩む声（価格・採算）","textReviewed":true}}')
case "$jew_contra" in *'"hasContradiction":true'*) echo "  PASS: JEW ③矛盾検出（品質・信頼と価格・採算のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: JEW ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
jew_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$JEW_DOC}")
case "$jew_narr" in *'"basedOnReadingOrder":["jew-i"]'*) echo "  PASS: JEW ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: JEW ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
jew_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$JEW_ID")
check "JEW 読戻し (200)" "200" "$jew_read"

echo ""
echo "--- シナリオ141: 引越し（丁寧さ・期日厳守と作業効率のトレードオフ） ---"
# 業態: 引越し（引越会社・運送）
# 想定人物: 引越支店長／運営責任者
# 業務領域: 引越し作業・料金・スタッフ・顧客への声のKJ分類と、引越サービスの改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 荷物の丁寧な梱包・搬送と期日厳守（顧客満足・信頼）と繁忙期の人手不足・料金競争への
#          対応（効率・人手）のトレードオフを矛盾検出（正パス）で表面化し、引越サービスの改善
#          根拠にする（丁寧さと効率の相克・作業スタッフの育成や定着・地域密着の営業で信頼を
#          築く動きも指摘）。
MOV_ID="biz-flow-moving"
MOV_DOC='{"version":1,"id":"'$MOV_ID'","title":"引越サービスの改善","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"m1","text":"荷物の丁寧な梱包・搬送と期日厳守へのこだわりを重視する声（丁寧さ・期日厳守）","x":0,"y":0,"textReviewed":true},{"id":"m2","text":"繁忙期の人手不足や料金競争など、丁寧さと作業効率のトレードオフに悩む声（効率・人手）","x":10,"y":0,"textReviewed":true},{"id":"m3","text":"作業スタッフの育成や定着、地域密着の営業で信頼を築く動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"mov-i","cardIds":["m1","m2","m3"]}],"readingOrder":["mov-i"]}'

mov_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$MOV_ID" \
  -H 'Content-Type: application/json' -d "$MOV_DOC")
check "MOV PUT document (作成)" "200" "$mov_put"

# ① AI束ね
mov_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"m1","text":"荷物の丁寧な梱包・搬送と期日厳守へのこだわりを重視する声（丁寧さ・期日厳守）","textReviewed":true},{"id":"m2","text":"繁忙期の人手不足や料金競争など、丁寧さと作業効率のトレードオフに悩む声（効率・人手）","textReviewed":true},{"id":"m3","text":"作業スタッフの育成や定着、地域密着の営業で信頼を築く動き","textReviewed":true}]}')
case "$mov_groups" in *'"groups":'*) echo "  PASS: MOV ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: MOV ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
mov_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$MOV_DOC,\"islandId\":\"mov-i\"}")
case "$mov_summary" in *'"groundingIds":["m1","m2","m3"]'*) echo "  PASS: MOV ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: MOV ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（丁寧さ・期日厳守 vs 効率・人手・丁寧さと効率の相克・正パス）
mov_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"m1","text":"荷物の丁寧な梱包・搬送と期日厳守へのこだわりを重視する声（丁寧さ・期日厳守）","textReviewed":true},"cardB":{"id":"m2","text":"繁忙期の人手不足や料金競争など、丁寧さと作業効率のトレードオフに悩む声（効率・人手）","textReviewed":true}}')
case "$mov_contra" in *'"hasContradiction":true'*) echo "  PASS: MOV ③矛盾検出（丁寧さ・期日厳守と作業効率のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: MOV ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
mov_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$MOV_DOC}")
case "$mov_narr" in *'"basedOnReadingOrder":["mov-i"]'*) echo "  PASS: MOV ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: MOV ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
mov_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$MOV_ID")
check "MOV 読戻し (200)" "200" "$mov_read"

echo ""
echo "--- シナリオ142: カメラ・写真（品質・思い出と効率・コストのトレードオフ） ---"
# 業態: カメラ・写真（カメラ店・写真館）
# 想定人物: カメラ店店長／写真館オーナー
# 業務領域: 商品・撮影サービス・プリント・顧客への声のKJ分類と、店舗・サービスの改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 七五三や成人式など大切な場面の撮影を丁寧に・仕上がりの品質にこだわる（品質・思い出）と
#          機材投資や撮影時間・価格競争への対応（効率・コスト）のトレードオフを矛盾検出（正パス）
#          で表面化し、店舗・サービスの改善根拠にする（品質と効率の相克・プリントやアルバム・
#          データ納品の多様化で顧客との長い関係を築く動きも指摘）。
CAM_ID="biz-flow-camera"
CAM_DOC='{"version":1,"id":"'$CAM_ID'","title":"カメラ店・写真館のサービス改善","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"c1","text":"七五三や成人式など大切な場面の撮影を丁寧に、仕上がりの品質にこだわる声（品質・思い出）","x":0,"y":0,"textReviewed":true},{"id":"c2","text":"機材投資や撮影時間・価格競争など、品質と効率・コストのトレードオフに悩む声（効率・コスト）","x":10,"y":0,"textReviewed":true},{"id":"c3","text":"プリントやアルバム、データ納品の多様化で顧客との長い関係を築く動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"cam-i","cardIds":["c1","c2","c3"]}],"readingOrder":["cam-i"]}'

cam_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$CAM_ID" \
  -H 'Content-Type: application/json' -d "$CAM_DOC")
check "CAM PUT document (作成)" "200" "$cam_put"

# ① AI束ね
cam_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"c1","text":"七五三や成人式など大切な場面の撮影を丁寧に、仕上がりの品質にこだわる声（品質・思い出）","textReviewed":true},{"id":"c2","text":"機材投資や撮影時間・価格競争など、品質と効率・コストのトレードオフに悩む声（効率・コスト）","textReviewed":true},{"id":"c3","text":"プリントやアルバム、データ納品の多様化で顧客との長い関係を築く動き","textReviewed":true}]}')
case "$cam_groups" in *'"groups":'*) echo "  PASS: CAM ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: CAM ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
cam_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$CAM_DOC,\"islandId\":\"cam-i\"}")
case "$cam_summary" in *'"groundingIds":["c1","c2","c3"]'*) echo "  PASS: CAM ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: CAM ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（品質・思い出 vs 効率・コスト・品質と効率の相克・正パス）
cam_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"c1","text":"七五三や成人式など大切な場面の撮影を丁寧に、仕上がりの品質にこだわる声（品質・思い出）","textReviewed":true},"cardB":{"id":"c2","text":"機材投資や撮影時間・価格競争など、品質と効率・コストのトレードオフに悩む声（効率・コスト）","textReviewed":true}}')
case "$cam_contra" in *'"hasContradiction":true'*) echo "  PASS: CAM ③矛盾検出（品質・思い出と効率・コストのトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: CAM ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
cam_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$CAM_DOC}")
case "$cam_narr" in *'"basedOnReadingOrder":["cam-i"]'*) echo "  PASS: CAM ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: CAM ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
cam_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$CAM_ID")
check "CAM 読戻し (200)" "200" "$cam_read"

echo ""
echo "--- シナリオ143: 医薬品卸（安定供給・品質と効率・コストのトレードオフ） ---"
# 業態: 医薬品卸（医薬品卸売・配送）
# 想定人物: 卸売営業／配送責任者
# 業務領域: 在庫・配送・医療機関との関係・規制への声のKJ分類と、医薬品供給の在り方の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 医薬品の安定供給と安全管理（温度管理・期限管理・品質）の確保（安定供給・品質）と
#          配送効率や在庫コストへの圧力（効率・コスト）のトレードオフを矛盾検出（正パス）で
#          表面化し、医薬品供給の在り方の根拠にする（供給と効率の相克・医療機関との密な連携や
#          薬剤師の支援で信頼を築く動きも指摘）。
WHOL_ID="biz-flow-wholesale"
WHOL_DOC='{"version":1,"id":"'$WHOL_ID'","title":"医薬品供給の在り方","createdAt":"2026-08-16T00:00:00Z","updatedAt":"2026-08-16T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"w1","text":"医薬品の安定供給と安全管理（温度管理・期限管理）を最優先する声（安定供給・品質）","x":0,"y":0,"textReviewed":true},{"id":"w2","text":"配送効率や在庫コストへの圧力など、安定供給と効率・コストのトレードオフに悩む声（効率・コスト）","x":10,"y":0,"textReviewed":true},{"id":"w3","text":"医療機関との密な連携や薬剤師の支援で信頼を築く動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"whol-i","cardIds":["w1","w2","w3"]}],"readingOrder":["whol-i"]}'

whol_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$WHOL_ID" \
  -H 'Content-Type: application/json' -d "$WHOL_DOC")
check "WHOL PUT document (作成)" "200" "$whol_put"

# ① AI束ね
whol_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"w1","text":"医薬品の安定供給と安全管理（温度管理・期限管理）を最優先する声（安定供給・品質）","textReviewed":true},{"id":"w2","text":"配送効率や在庫コストへの圧力など、安定供給と効率・コストのトレードオフに悩む声（効率・コスト）","textReviewed":true},{"id":"w3","text":"医療機関との密な連携や薬剤師の支援で信頼を築く動き","textReviewed":true}]}')
case "$whol_groups" in *'"groups":'*) echo "  PASS: WHOL ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: WHOL ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
whol_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$WHOL_DOC,\"islandId\":\"whol-i\"}")
case "$whol_summary" in *'"groundingIds":["w1","w2","w3"]'*) echo "  PASS: WHOL ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: WHOL ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（安定供給・品質 vs 効率・コスト・供給と効率の相克・正パス）
whol_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"w1","text":"医薬品の安定供給と安全管理（温度管理・期限管理）を最優先する声（安定供給・品質）","textReviewed":true},"cardB":{"id":"w2","text":"配送効率や在庫コストへの圧力など、安定供給と効率・コストのトレードオフに悩む声（効率・コスト）","textReviewed":true}}')
case "$whol_contra" in *'"hasContradiction":true'*) echo "  PASS: WHOL ③矛盾検出（安定供給・品質と効率・コストのトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: WHOL ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
whol_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$WHOL_DOC}")
case "$whol_narr" in *'"basedOnReadingOrder":["whol-i"]'*) echo "  PASS: WHOL ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: WHOL ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
whol_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$WHOL_ID")
check "WHOL 読戻し (200)" "200" "$whol_read"

echo ""
echo "--- シナリオ144: スポーツ用品・アウトドア（専門性・アドバイスと価格・売上のトレードオフ） ---"
# 業態: スポーツ用品・アウトドア（スポーツ用品店）
# 想定人物: 店長／商品バイヤー
# 業務領域: 商品・試着・アドバイス・価格への声のKJ分類と、店舗運営の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: スポーツやアウトドアの専門知識に基づくアドバイスと試着・調整（顧客満足・専門性）と
#          ネット通販や価格競争への対応（価格・売上）のトレードオフを矛盾検出（正パス）で表面化し、
#          店舗運営の改善根拠にする（専門性と価格の相克・イベントやレッスン・用品の修理・調整で
#          顧客との長い関係を築く動きも指摘）。
SPORT_ID="biz-flow-sports"
SPORT_DOC='{"version":1,"id":"'$SPORT_ID'","title":"スポーツ用品店の店舗運営","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"s1","text":"スポーツやアウトドアの専門知識に基づくアドバイスと試着・調整を重視する声（専門性・アドバイス）","x":0,"y":0,"textReviewed":true},{"id":"s2","text":"ネット通販や価格競争への対応など、専門性と価格・売上のトレードオフに悩む声（価格・売上）","x":10,"y":0,"textReviewed":true},{"id":"s3","text":"イベントやレッスン、用品の修理・調整で顧客との長い関係を築く動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"sport-i","cardIds":["s1","s2","s3"]}],"readingOrder":["sport-i"]}'

sport_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$SPORT_ID" \
  -H 'Content-Type: application/json' -d "$SPORT_DOC")
check "SPORT PUT document (作成)" "200" "$sport_put"

# ① AI束ね
sport_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"s1","text":"スポーツやアウトドアの専門知識に基づくアドバイスと試着・調整を重視する声（専門性・アドバイス）","textReviewed":true},{"id":"s2","text":"ネット通販や価格競争への対応など、専門性と価格・売上のトレードオフに悩む声（価格・売上）","textReviewed":true},{"id":"s3","text":"イベントやレッスン、用品の修理・調整で顧客との長い関係を築く動き","textReviewed":true}]}')
case "$sport_groups" in *'"groups":'*) echo "  PASS: SPORT ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: SPORT ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
sport_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$SPORT_DOC,\"islandId\":\"sport-i\"}")
case "$sport_summary" in *'"groundingIds":["s1","s2","s3"]'*) echo "  PASS: SPORT ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: SPORT ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（専門性・アドバイス vs 価格・売上・専門性と価格の相克・正パス）
sport_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"s1","text":"スポーツやアウトドアの専門知識に基づくアドバイスと試着・調整を重視する声（専門性・アドバイス）","textReviewed":true},"cardB":{"id":"s2","text":"ネット通販や価格競争への対応など、専門性と価格・売上のトレードオフに悩む声（価格・売上）","textReviewed":true}}')
case "$sport_contra" in *'"hasContradiction":true'*) echo "  PASS: SPORT ③矛盾検出（専門性・アドバイスと価格・売上のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: SPORT ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
sport_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$SPORT_DOC}")
case "$sport_narr" in *'"basedOnReadingOrder":["sport-i"]'*) echo "  PASS: SPORT ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: SPORT ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
sport_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$SPORT_ID")
check "SPORT 読戻し (200)" "200" "$sport_read"

echo ""
echo "--- シナリオ145: コンサート・ライブ運営（音楽の質・体験と集客・収益のトレードオフ） ---"
# 業態: コンサート・ライブ運営（ライブハウス・興行）
# 想定人物: ライブハウス支配人／イベントプロデューサー
# 業務領域: 出演者・観客・音響・集客への声のKJ分類と、ライブ運営の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: アーティストの表現と観客の体験（音響・ステージ・雰囲気）を大切にする（音楽の質・体験）と
#          チケット販売や運営コストへの対応（集客・収益）のトレードオフを矛盾検出（正パス）で
#          表面化し、ライブ運営の改善根拠にする（音楽の質と集客の相克・若手アーティストの育成や
#          地域コミュニティとの連携で文化を育てる動きも指摘）。
LIVE_ID="biz-flow-live"
LIVE_DOC='{"version":1,"id":"'$LIVE_ID'","title":"ライブ運営の改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"l1","text":"アーティストの表現と観客の体験（音響・ステージ・雰囲気）を大切にする声（音楽の質・体験）","x":0,"y":0,"textReviewed":true},{"id":"l2","text":"チケット販売や運営コストへの対応など、音楽の質と集客・収益のトレードオフに悩む声（集客・収益）","x":10,"y":0,"textReviewed":true},{"id":"l3","text":"若手アーティストの育成や地域コミュニティとの連携で文化を育てる動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"live-i","cardIds":["l1","l2","l3"]}],"readingOrder":["live-i"]}'

live_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$LIVE_ID" \
  -H 'Content-Type: application/json' -d "$LIVE_DOC")
check "LIVE PUT document (作成)" "200" "$live_put"

# ① AI束ね
live_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"l1","text":"アーティストの表現と観客の体験（音響・ステージ・雰囲気）を大切にする声（音楽の質・体験）","textReviewed":true},{"id":"l2","text":"チケット販売や運営コストへの対応など、音楽の質と集客・収益のトレードオフに悩む声（集客・収益）","textReviewed":true},{"id":"l3","text":"若手アーティストの育成や地域コミュニティとの連携で文化を育てる動き","textReviewed":true}]}')
case "$live_groups" in *'"groups":'*) echo "  PASS: LIVE ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: LIVE ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
live_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$LIVE_DOC,\"islandId\":\"live-i\"}")
case "$live_summary" in *'"groundingIds":["l1","l2","l3"]'*) echo "  PASS: LIVE ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: LIVE ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（音楽の質・体験 vs 集客・収益・音楽の質と集客の相克・正パス）
live_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"l1","text":"アーティストの表現と観客の体験（音響・ステージ・雰囲気）を大切にする声（音楽の質・体験）","textReviewed":true},"cardB":{"id":"l2","text":"チケット販売や運営コストへの対応など、音楽の質と集客・収益のトレードオフに悩む声（集客・収益）","textReviewed":true}}')
case "$live_contra" in *'"hasContradiction":true'*) echo "  PASS: LIVE ③矛盾検出（音楽の質・体験と集客・収益のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: LIVE ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
live_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$LIVE_DOC}")
case "$live_narr" in *'"basedOnReadingOrder":["live-i"]'*) echo "  PASS: LIVE ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: LIVE ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
live_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$LIVE_ID")
check "LIVE 読戻し (200)" "200" "$live_read"

echo ""
echo "--- シナリオ146: 神社・寺（伝統・信仰と運営・収支のトレードオフ） ---"
# 業態: 神社・寺（宗教施設・寺院運営）
# 想定人物: 宮司／住職（寺院運営）
# 業務領域: 参拝者・檀家・行事・維持管理への声のKJ分類と、宗教施設の持続的運営の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 伝統的な儀式や文化・信仰の継承・檀家・氏子との関係を大切にする（伝統・信仰）と
#          建物の維持管理コストや人手不足への対応（運営・収支）のトレードオフを矛盾検出（正パス）
#          で表面化し、宗教施設の持続的運営の根拠にする（伝統と運営の相克・参拝者や観光客への
#          おもてなし・体験イベントで地域に開かれた場をつくる動きも指摘）。
SHRI_ID="biz-flow-shrine"
SHRI_DOC='{"version":1,"id":"'$SHRI_ID'","title":"宗教施設の持続的運営","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"sh1","text":"伝統的な儀式や文化・信仰の継承、檀家・氏子との関係を大切にする声（伝統・信仰）","x":0,"y":0,"textReviewed":true},{"id":"sh2","text":"建物の維持管理コストや人手不足など、伝統の維持と運営・収支のトレードオフに悩む声（運営・収支）","x":10,"y":0,"textReviewed":true},{"id":"sh3","text":"参拝者や観光客へのおもてなし、体験イベントで地域に開かれた場をつくる動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"shri-i","cardIds":["sh1","sh2","sh3"]}],"readingOrder":["shri-i"]}'

shri_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$SHRI_ID" \
  -H 'Content-Type: application/json' -d "$SHRI_DOC")
check "SHRI PUT document (作成)" "200" "$shri_put"

# ① AI束ね
shri_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"sh1","text":"伝統的な儀式や文化・信仰の継承、檀家・氏子との関係を大切にする声（伝統・信仰）","textReviewed":true},{"id":"sh2","text":"建物の維持管理コストや人手不足など、伝統の維持と運営・収支のトレードオフに悩む声（運営・収支）","textReviewed":true},{"id":"sh3","text":"参拝者や観光客へのおもてなし、体験イベントで地域に開かれた場をつくる動き","textReviewed":true}]}')
case "$shri_groups" in *'"groups":'*) echo "  PASS: SHRI ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: SHRI ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
shri_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$SHRI_DOC,\"islandId\":\"shri-i\"}")
case "$shri_summary" in *'"groundingIds":["sh1","sh2","sh3"]'*) echo "  PASS: SHRI ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: SHRI ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（伝統・信仰 vs 運営・収支・伝統と運営の相克・正パス）
shri_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"sh1","text":"伝統的な儀式や文化・信仰の継承、檀家・氏子との関係を大切にする声（伝統・信仰）","textReviewed":true},"cardB":{"id":"sh2","text":"建物の維持管理コストや人手不足など、伝統の維持と運営・収支のトレードオフに悩む声（運営・収支）","textReviewed":true}}')
case "$shri_contra" in *'"hasContradiction":true'*) echo "  PASS: SHRI ③矛盾検出（伝統・信仰と運営・収支のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: SHRI ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
shri_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$SHRI_DOC}")
case "$shri_narr" in *'"basedOnReadingOrder":["shri-i"]'*) echo "  PASS: SHRI ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: SHRI ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
shri_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$SHRI_ID")
check "SHRI 読戻し (200)" "200" "$shri_read"

echo ""
echo "--- シナリオ147: 学校給食（栄養・安全とコスト・効率のトレードオフ） ---"
# 業態: 学校給食（給食センター・給食運営）
# 想定人物: 栄養士／給食センター責任者
# 業務領域: 献立・栄養・食の安全・子どもへの声のKJ分類と、給食運営の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 子どもの栄養バランスと食の安全（アレルギー対応・衛生管理）を最優先する（安全・栄養）と
#          食材費や人員への圧力（コスト・効率）のトレードオフを矛盾検出（正パス）で表面化し、
#          給食運営の改善根拠にする（安全・栄養とコストの相克・食育や地産地消で子どもたちの食への
#          興味を育てる動きも指摘）。
SCHOOL_ID="biz-flow-school-lunch"
SCHOOL_DOC='{"version":1,"id":"'$SCHOOL_ID'","title":"学校給食の運営改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"sl1","text":"子どもの栄養バランスと食の安全（アレルギー対応・衛生管理）を最優先する声（安全・栄養）","x":0,"y":0,"textReviewed":true},{"id":"sl2","text":"食材費や人員への圧力など、栄養・安全とコスト・効率のトレードオフに悩む声（コスト・効率）","x":10,"y":0,"textReviewed":true},{"id":"sl3","text":"食育や地産地消、子どもたちの食への興味を育てる動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"school-i","cardIds":["sl1","sl2","sl3"]}],"readingOrder":["school-i"]}'

school_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$SCHOOL_ID" \
  -H 'Content-Type: application/json' -d "$SCHOOL_DOC")
check "SCHOOL PUT document (作成)" "200" "$school_put"

# ① AI束ね
school_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"sl1","text":"子どもの栄養バランスと食の安全（アレルギー対応・衛生管理）を最優先する声（安全・栄養）","textReviewed":true},{"id":"sl2","text":"食材費や人員への圧力など、栄養・安全とコスト・効率のトレードオフに悩む声（コスト・効率）","textReviewed":true},{"id":"sl3","text":"食育や地産地消、子どもたちの食への興味を育てる動き","textReviewed":true}]}')
case "$school_groups" in *'"groups":'*) echo "  PASS: SCHOOL ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: SCHOOL ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
school_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$SCHOOL_DOC,\"islandId\":\"school-i\"}")
case "$school_summary" in *'"groundingIds":["sl1","sl2","sl3"]'*) echo "  PASS: SCHOOL ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: SCHOOL ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（安全・栄養 vs コスト・効率・安全・栄養とコストの相克・正パス）
school_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"sl1","text":"子どもの栄養バランスと食の安全（アレルギー対応・衛生管理）を最優先する声（安全・栄養）","textReviewed":true},"cardB":{"id":"sl2","text":"食材費や人員への圧力など、栄養・安全とコスト・効率のトレードオフに悩む声（コスト・効率）","textReviewed":true}}')
case "$school_contra" in *'"hasContradiction":true'*) echo "  PASS: SCHOOL ③矛盾検出（栄養・安全とコスト・効率のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: SCHOOL ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
school_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$SCHOOL_DOC}")
case "$school_narr" in *'"basedOnReadingOrder":["school-i"]'*) echo "  PASS: SCHOOL ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: SCHOOL ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
school_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$SCHOOL_ID")
check "SCHOOL 読戻し (200)" "200" "$school_read"

echo ""
echo "--- シナリオ148: 陶磁器・工芸品（技法・品質と効率・販路のトレードオフ） ---"
# 業態: 陶磁器・工芸品（陶磁器メーカー・工房）
# 想定人物: 陶芸家／工房オーナー
# 業務領域: 製作・販売・後継者・伝統への声のKJ分類と、工房の持続的運営の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 伝統的な技法と手仕事の品質・一つひとつの作品へのこだわり（技法・品質）と生産効率や
#          販路・価格への圧力（効率・販路）のトレードオフを矛盾検出（正パス）で表面化し、
#          工房の持続的運営の根拠にする（技法と効率の相克・後継者の育成や体験教室・現代の暮らしに
#          合うデザインで伝統をつなぐ動きも指摘）。
CRAFT_ID="biz-flow-craft"
CRAFT_DOC='{"version":1,"id":"'$CRAFT_ID'","title":"工房の持続的運営","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"cr1","text":"伝統的な技法と手仕事の品質、一つひとつの作品へのこだわりを重視する声（技法・品質）","x":0,"y":0,"textReviewed":true},{"id":"cr2","text":"生産効率や販路・価格への圧力など、技法・品質と効率・販路のトレードオフに悩む声（効率・販路）","x":10,"y":0,"textReviewed":true},{"id":"cr3","text":"後継者の育成や体験教室、現代の暮らしに合うデザインで伝統をつなぐ動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"craft-i","cardIds":["cr1","cr2","cr3"]}],"readingOrder":["craft-i"]}'

craft_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$CRAFT_ID" \
  -H 'Content-Type: application/json' -d "$CRAFT_DOC")
check "CRAFT PUT document (作成)" "200" "$craft_put"

# ① AI束ね
craft_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"cr1","text":"伝統的な技法と手仕事の品質、一つひとつの作品へのこだわりを重視する声（技法・品質）","textReviewed":true},{"id":"cr2","text":"生産効率や販路・価格への圧力など、技法・品質と効率・販路のトレードオフに悩む声（効率・販路）","textReviewed":true},{"id":"cr3","text":"後継者の育成や体験教室、現代の暮らしに合うデザインで伝統をつなぐ動き","textReviewed":true}]}')
case "$craft_groups" in *'"groups":'*) echo "  PASS: CRAFT ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: CRAFT ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
craft_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$CRAFT_DOC,\"islandId\":\"craft-i\"}")
case "$craft_summary" in *'"groundingIds":["cr1","cr2","cr3"]'*) echo "  PASS: CRAFT ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: CRAFT ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（技法・品質 vs 効率・販路・技法と効率の相克・正パス）
craft_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"cr1","text":"伝統的な技法と手仕事の品質、一つひとつの作品へのこだわりを重視する声（技法・品質）","textReviewed":true},"cardB":{"id":"cr2","text":"生産効率や販路・価格への圧力など、技法・品質と効率・販路のトレードオフに悩む声（効率・販路）","textReviewed":true}}')
case "$craft_contra" in *'"hasContradiction":true'*) echo "  PASS: CRAFT ③矛盾検出（技法・品質と効率・販路のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: CRAFT ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
craft_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$CRAFT_DOC}")
case "$craft_narr" in *'"basedOnReadingOrder":["craft-i"]'*) echo "  PASS: CRAFT ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: CRAFT ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
craft_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$CRAFT_ID")
check "CRAFT 読戻し (200)" "200" "$craft_read"

echo ""
echo "--- シナリオ149: 牧場・酪農（品質・動物福祉と採算・人手のトレードオフ） ---"
# 業態: 牧場・酪農（酪農家・牧場経営）
# 想定人物: 酪農家／牧場経営者
# 業務領域: 牛の健康・搾乳・飼料・経営・後継者への声のKJ分類と、酪農の持続的経営の検討
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 牛の健康と福祉・安全で高品質な乳製品へのこだわり（品質・動物福祉）と飼料コストや
#          人手不足（採算・人手）のトレードオフを矛盾検出（正パス）で表面化し、酪農の持続的経営の
#          根拠にする（福祉と採算の相克・牧場体験や加工品の販売・後継者の育成で地域と酪農をつなぐ
#          動きも指摘）。
DAIRY_ID="biz-flow-dairy"
DAIRY_DOC='{"version":1,"id":"'$DAIRY_ID'","title":"酪農の持続的経営","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"d1","text":"牛の健康と福祉、安全で高品質な乳製品へのこだわりを重視する声（品質・動物福祉）","x":0,"y":0,"textReviewed":true},{"id":"d2","text":"飼料コストや人手不足など、品質・福祉と経営効率のトレードオフに悩む声（採算・人手）","x":10,"y":0,"textReviewed":true},{"id":"d3","text":"牧場体験や加工品の販売、後継者の育成で地域と酪農をつなぐ動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"dairy-i","cardIds":["d1","d2","d3"]}],"readingOrder":["dairy-i"]}'

dairy_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$DAIRY_ID" \
  -H 'Content-Type: application/json' -d "$DAIRY_DOC")
check "DAIRY PUT document (作成)" "200" "$dairy_put"

# ① AI束ね
dairy_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"d1","text":"牛の健康と福祉、安全で高品質な乳製品へのこだわりを重視する声（品質・動物福祉）","textReviewed":true},{"id":"d2","text":"飼料コストや人手不足など、品質・福祉と経営効率のトレードオフに悩む声（採算・人手）","textReviewed":true},{"id":"d3","text":"牧場体験や加工品の販売、後継者の育成で地域と酪農をつなぐ動き","textReviewed":true}]}')
case "$dairy_groups" in *'"groups":'*) echo "  PASS: DAIRY ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: DAIRY ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
dairy_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$DAIRY_DOC,\"islandId\":\"dairy-i\"}")
case "$dairy_summary" in *'"groundingIds":["d1","d2","d3"]'*) echo "  PASS: DAIRY ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: DAIRY ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（品質・動物福祉 vs 採算・人手・福祉と採算の相克・正パス）
dairy_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"d1","text":"牛の健康と福祉、安全で高品質な乳製品へのこだわりを重視する声（品質・動物福祉）","textReviewed":true},"cardB":{"id":"d2","text":"飼料コストや人手不足など、品質・福祉と経営効率のトレードオフに悩む声（採算・人手）","textReviewed":true}}')
case "$dairy_contra" in *'"hasContradiction":true'*) echo "  PASS: DAIRY ③矛盾検出（品質・動物福祉と採算・人手のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: DAIRY ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
dairy_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$DAIRY_DOC}")
case "$dairy_narr" in *'"basedOnReadingOrder":["dairy-i"]'*) echo "  PASS: DAIRY ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: DAIRY ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
dairy_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$DAIRY_ID")
check "DAIRY 読戻し (200)" "200" "$dairy_read"

echo ""
echo "--- シナリオ150: 墓地・霊園（供養・永続性と運営・費用のトレードオフ） ---"
# 業態: 墓地・霊園（霊園運営・墓苑）
# 想定人物: 霊園管理者／墓苑スタッフ
# 業務領域: 墓地の維持・供養・遺族の声・費用への声のKJ分類と、霊園運営の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 故人への丁寧な供養と遺族の気持ちに寄り添う対応・永続的な管理（供養・永続性）と
#          墓地の維持管理コストや料金への対応（運営・費用）のトレードオフを矛盾検出（正パス）で
#          表面化し、霊園運営の改善根拠にする（供養と運営の相克・樹木葬や散骨など多様な供養の
#          選択肢・オンライン供養で時代に合う形を模索する動きも指摘）。
CEMY_ID="biz-flow-cemetery"
CEMY_DOC='{"version":1,"id":"'$CEMY_ID'","title":"霊園運営の改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"cy1","text":"故人への丁寧な供養と遺族の気持ちに寄り添う対応、永続的な管理を重視する声（供養・永続性）","x":0,"y":0,"textReviewed":true},{"id":"cy2","text":"墓地の維持管理コストや料金への対応など、供養・永続性と運営・費用のトレードオフに悩む声（運営・費用）","x":10,"y":0,"textReviewed":true},{"id":"cy3","text":"樹木葬や散骨など多様な供養の選択肢、オンライン供養で時代に合う形を模索する動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"cemy-i","cardIds":["cy1","cy2","cy3"]}],"readingOrder":["cemy-i"]}'

cemy_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$CEMY_ID" \
  -H 'Content-Type: application/json' -d "$CEMY_DOC")
check "CEMY PUT document (作成)" "200" "$cemy_put"

# ① AI束ね
cemy_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"cy1","text":"故人への丁寧な供養と遺族の気持ちに寄り添う対応、永続的な管理を重視する声（供養・永続性）","textReviewed":true},{"id":"cy2","text":"墓地の維持管理コストや料金への対応など、供養・永続性と運営・費用のトレードオフに悩む声（運営・費用）","textReviewed":true},{"id":"cy3","text":"樹木葬や散骨など多様な供養の選択肢、オンライン供養で時代に合う形を模索する動き","textReviewed":true}]}')
case "$cemy_groups" in *'"groups":'*) echo "  PASS: CEMY ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: CEMY ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
cemy_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$CEMY_DOC,\"islandId\":\"cemy-i\"}")
case "$cemy_summary" in *'"groundingIds":["cy1","cy2","cy3"]'*) echo "  PASS: CEMY ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: CEMY ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（供養・永続性 vs 運営・費用・供養と運営の相克・正パス）
cemy_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"cy1","text":"故人への丁寧な供養と遺族の気持ちに寄り添う対応、永続的な管理を重視する声（供養・永続性）","textReviewed":true},"cardB":{"id":"cy2","text":"墓地の維持管理コストや料金への対応など、供養・永続性と運営・費用のトレードオフに悩む声（運営・費用）","textReviewed":true}}')
case "$cemy_contra" in *'"hasContradiction":true'*) echo "  PASS: CEMY ③矛盾検出（供養・永続性と運営・費用のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: CEMY ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
cemy_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$CEMY_DOC}")
case "$cemy_narr" in *'"basedOnReadingOrder":["cemy-i"]'*) echo "  PASS: CEMY ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: CEMY ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
cemy_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$CEMY_ID")
check "CEMY 読戻し (200)" "200" "$cemy_read"

echo ""
echo "--- シナリオ151: 公営競技（公正性・信頼と収益・集客のトレードオフ） ---"
# 業態: 公営競技（競馬・競輪・競艇場運営）
# 想定人物: 場長／運営責任者
# 業務領域: 運営・観客・公正性・収益への声のKJ分類と、公営競技の運営改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 勝敗の公正性とファンが安心して楽しめる運営（公正性・信頼）と売上・集客への圧力
#          （収益・集客）のトレードオフを矛盾検出（正パス）で表面化し、公営競技の運営改善根拠に
#          する（公正性と収益の相克・若年層や初心者向けのイベント・地域の観光資源としての活用を
#          模索する動きも指摘）。
BET_ID="biz-flow-racing"
BET_DOC='{"version":1,"id":"'$BET_ID'","title":"公営競技の運営改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"bt1","text":"勝敗の公正性とファンが安心して楽しめる運営を重視する声（公正性・信頼）","x":0,"y":0,"textReviewed":true},{"id":"bt2","text":"売上や集客への圧力など、公正性と収益・集客のトレードオフに悩む声（収益・集客）","x":10,"y":0,"textReviewed":true},{"id":"bt3","text":"若年層や初心者向けのイベント、地域の観光資源としての活用を模索する動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"bet-i","cardIds":["bt1","bt2","bt3"]}],"readingOrder":["bet-i"]}'

bet_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$BET_ID" \
  -H 'Content-Type: application/json' -d "$BET_DOC")
check "BET PUT document (作成)" "200" "$bet_put"

# ① AI束ね
bet_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"bt1","text":"勝敗の公正性とファンが安心して楽しめる運営を重視する声（公正性・信頼）","textReviewed":true},{"id":"bt2","text":"売上や集客への圧力など、公正性と収益・集客のトレードオフに悩む声（収益・集客）","textReviewed":true},{"id":"bt3","text":"若年層や初心者向けのイベント、地域の観光資源としての活用を模索する動き","textReviewed":true}]}')
case "$bet_groups" in *'"groups":'*) echo "  PASS: BET ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: BET ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
bet_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$BET_DOC,\"islandId\":\"bet-i\"}")
case "$bet_summary" in *'"groundingIds":["bt1","bt2","bt3"]'*) echo "  PASS: BET ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: BET ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（公正性・信頼 vs 収益・集客・公正性と収益の相克・正パス）
bet_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"bt1","text":"勝敗の公正性とファンが安心して楽しめる運営を重視する声（公正性・信頼）","textReviewed":true},"cardB":{"id":"bt2","text":"売上や集客への圧力など、公正性と収益・集客のトレードオフに悩む声（収益・集客）","textReviewed":true}}')
case "$bet_contra" in *'"hasContradiction":true'*) echo "  PASS: BET ③矛盾検出（公正性・信頼と収益・集客のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: BET ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
bet_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$BET_DOC}")
case "$bet_narr" in *'"basedOnReadingOrder":["bet-i"]'*) echo "  PASS: BET ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: BET ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
bet_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$BET_ID")
check "BET 読戻し (200)" "200" "$bet_read"

echo ""
echo "--- シナリオ152: 税関・通関（コンプライアンス・正確性とスピード・効率のトレードオフ） ---"
# 業態: 税関・通関（通関業・貿易手続き）
# 想定人物: 通関士／通関業務責任者
# 業務領域: 通関手続き・規制対応・顧客（輸出入業者）への声のKJ分類と、通関業務の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 法令順守と正確な申告・規制対応（コンプライアンス・正確性）と迅速な通関やコスト削減への
#          圧力（スピード・効率）のトレードオフを矛盾検出（正パス）で表面化し、通関業務の改善根拠に
#          する（正確性とスピードの相克・デジタル手続きの活用や顧客（輸出入業者）への丁寧なサポート
#          で信頼を築く動きも指摘）。
CUST_ID="biz-flow-customs"
CUST_DOC='{"version":1,"id":"'$CUST_ID'","title":"通関業務の改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"cu1","text":"法令順守と正確な申告・規制対応を最優先する声（コンプライアンス・正確性）","x":0,"y":0,"textReviewed":true},{"id":"cu2","text":"迅速な通関やコスト削減への圧力など、正確性とスピード・効率のトレードオフに悩む声（スピード・効率）","x":10,"y":0,"textReviewed":true},{"id":"cu3","text":"デジタル手続きの活用や顧客（輸出入業者）への丁寧なサポートで信頼を築く動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"cust-i","cardIds":["cu1","cu2","cu3"]}],"readingOrder":["cust-i"]}'

cust_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$CUST_ID" \
  -H 'Content-Type: application/json' -d "$CUST_DOC")
check "CUST PUT document (作成)" "200" "$cust_put"

# ① AI束ね
cust_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"cu1","text":"法令順守と正確な申告・規制対応を最優先する声（コンプライアンス・正確性）","textReviewed":true},{"id":"cu2","text":"迅速な通関やコスト削減への圧力など、正確性とスピード・効率のトレードオフに悩む声（スピード・効率）","textReviewed":true},{"id":"cu3","text":"デジタル手続きの活用や顧客（輸出入業者）への丁寧なサポートで信頼を築く動き","textReviewed":true}]}')
case "$cust_groups" in *'"groups":'*) echo "  PASS: CUST ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: CUST ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
cust_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$CUST_DOC,\"islandId\":\"cust-i\"}")
case "$cust_summary" in *'"groundingIds":["cu1","cu2","cu3"]'*) echo "  PASS: CUST ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: CUST ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（コンプライアンス・正確性 vs スピード・効率・正確性とスピードの相克・正パス）
cust_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"cu1","text":"法令順守と正確な申告・規制対応を最優先する声（コンプライアンス・正確性）","textReviewed":true},"cardB":{"id":"cu2","text":"迅速な通関やコスト削減への圧力など、正確性とスピード・効率のトレードオフに悩む声（スピード・効率）","textReviewed":true}}')
case "$cust_contra" in *'"hasContradiction":true'*) echo "  PASS: CUST ③矛盾検出（コンプライアンス・正確性とスピード・効率のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: CUST ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
cust_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$CUST_DOC}")
case "$cust_narr" in *'"basedOnReadingOrder":["cust-i"]'*) echo "  PASS: CUST ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: CUST ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
cust_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$CUST_ID")
check "CUST 読戻し (200)" "200" "$cust_read"

echo ""
echo "--- シナリオ153: ガソリンスタンド（安全・信頼と価格・効率のトレードオフ） ---"
# 業態: ガソリンスタンド（給油所・エネルギー小売）
# 想定人物: 店長／地域密着経営者
# 業務領域: 給油・点検・販売・顧客への声のKJ分類と、給油所運営の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 安全な給油と車検・点検など丁寧なサービスで地域の安全を支える（安全・信頼）と
#          ガソリン価格競争や販売量への圧力（価格・効率）のトレードオフを矛盾検出（正パス）で
#          表面化し、給油所運営の改善根拠にする（安全と価格の相克・EV充電やカー用品販売・地域の
#          見守り拠点としての役割を模索する動きも指摘）。
GAS_ID="biz-flow-gas-station"
GAS_DOC='{"version":1,"id":"'$GAS_ID'","title":"給油所運営の改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"gs1","text":"安全な給油と車検・点検など丁寧なサービスで地域の安全を支えることを重視する声（安全・信頼）","x":0,"y":0,"textReviewed":true},{"id":"gs2","text":"ガソリン価格競争や販売量への圧力など、安全・サービスと価格・効率のトレードオフに悩む声（価格・効率）","x":10,"y":0,"textReviewed":true},{"id":"gs3","text":"EV充電やカー用品販売、地域の見守り拠点としての役割を模索する動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"gas-i","cardIds":["gs1","gs2","gs3"]}],"readingOrder":["gas-i"]}'

gas_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$GAS_ID" \
  -H 'Content-Type: application/json' -d "$GAS_DOC")
check "GAS PUT document (作成)" "200" "$gas_put"

# ① AI束ね
gas_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"gs1","text":"安全な給油と車検・点検など丁寧なサービスで地域の安全を支えることを重視する声（安全・信頼）","textReviewed":true},{"id":"gs2","text":"ガソリン価格競争や販売量への圧力など、安全・サービスと価格・効率のトレードオフに悩む声（価格・効率）","textReviewed":true},{"id":"gs3","text":"EV充電やカー用品販売、地域の見守り拠点としての役割を模索する動き","textReviewed":true}]}')
case "$gas_groups" in *'"groups":'*) echo "  PASS: GAS ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: GAS ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
gas_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$GAS_DOC,\"islandId\":\"gas-i\"}")
case "$gas_summary" in *'"groundingIds":["gs1","gs2","gs3"]'*) echo "  PASS: GAS ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: GAS ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（安全・信頼 vs 価格・効率・安全と価格の相克・正パス）
gas_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"gs1","text":"安全な給油と車検・点検など丁寧なサービスで地域の安全を支えることを重視する声（安全・信頼）","textReviewed":true},"cardB":{"id":"gs2","text":"ガソリン価格競争や販売量への圧力など、安全・サービスと価格・効率のトレードオフに悩む声（価格・効率）","textReviewed":true}}')
case "$gas_contra" in *'"hasContradiction":true'*) echo "  PASS: GAS ③矛盾検出（安全・信頼と価格・効率のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: GAS ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
gas_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$GAS_DOC}")
case "$gas_narr" in *'"basedOnReadingOrder":["gas-i"]'*) echo "  PASS: GAS ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: GAS ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
gas_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$GAS_ID")
check "GAS 読戻し (200)" "200" "$gas_read"

echo ""
echo "--- シナリオ154: カジノ・IR（健全性・責任と収益・集客のトレードオフ） ---"
# 業態: カジノ・IR（統合型リゾート・カジノ運営）
# 想定人物: カジノ運営責任者／IR施設マネージャー
# 業務領域: 運営・来場者・健全性・収益への声のKJ分類と、IR施設の運営改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 依存症対策や入場制限など、健全で責任ある運営（健全性・責任）と売上や集客への圧力
#          （収益・集客）のトレードオフを矛盾検出（正パス）で表面化し、IR施設の運営改善根拠にする
#          （健全性と収益の相克・カジノ以外のエンタメ・文化・MICE誘致で地域経済への波及を目指す動きも指摘）。
IR_ID="biz-flow-casino-ir"
IR_DOC='{"version":1,"id":"'$IR_ID'","title":"IR施設の運営改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"ir1","text":"依存症対策や入場制限など、健全で責任ある運営を重視する声（健全性・責任）","x":0,"y":0,"textReviewed":true},{"id":"ir2","text":"売上や集客への圧力など、健全性と収益・集客のトレードオフに悩む声（収益・集客）","x":10,"y":0,"textReviewed":true},{"id":"ir3","text":"カジノ以外のエンタメ・文化・MICE誘致で地域経済への波及を目指す動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"ir-i","cardIds":["ir1","ir2","ir3"]}],"readingOrder":["ir-i"]}'

ir_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$IR_ID" \
  -H 'Content-Type: application/json' -d "$IR_DOC")
check "IR PUT document (作成)" "200" "$ir_put"

# ① AI束ね
ir_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"ir1","text":"依存症対策や入場制限など、健全で責任ある運営を重視する声（健全性・責任）","textReviewed":true},{"id":"ir2","text":"売上や集客への圧力など、健全性と収益・集客のトレードオフに悩む声（収益・集客）","textReviewed":true},{"id":"ir3","text":"カジノ以外のエンタメ・文化・MICE誘致で地域経済への波及を目指す動き","textReviewed":true}]}')
case "$ir_groups" in *'"groups":'*) echo "  PASS: IR ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: IR ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
ir_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$IR_DOC,\"islandId\":\"ir-i\"}")
case "$ir_summary" in *'"groundingIds":["ir1","ir2","ir3"]'*) echo "  PASS: IR ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: IR ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（健全性・責任 vs 収益・集客・健全性と収益の相克・正パス）
ir_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"ir1","text":"依存症対策や入場制限など、健全で責任ある運営を重視する声（健全性・責任）","textReviewed":true},"cardB":{"id":"ir2","text":"売上や集客への圧力など、健全性と収益・集客のトレードオフに悩む声（収益・集客）","textReviewed":true}}')
case "$ir_contra" in *'"hasContradiction":true'*) echo "  PASS: IR ③矛盾検出（健全性・責任と収益・集客のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: IR ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
ir_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$IR_DOC}")
case "$ir_narr" in *'"basedOnReadingOrder":["ir-i"]'*) echo "  PASS: IR ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: IR ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
ir_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$IR_ID")
check "IR 読戻し (200)" "200" "$ir_read"

echo ""
echo "--- シナリオ155: ネイル・エステサロン（品質・衛生と効率・収益のトレードオフ） ---"
# 業態: ネイル・エステ（ネイルサロン運営）
# 想定人物: サロンオーナー／ネイリスト
# 業務領域: 施術・技術・衛生・価格への声のKJ分類と、サロン運営の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 技術と衛生管理・丁寧なカウンセリングによる施術の質（品質・衛生）と予約の回転率や
#          価格競争への対応（効率・収益）のトレードオフを矛盾検出（正パス）で表面化し、サロン運営の
#          改善根拠にする（品質・衛生と効率の相克・ネイリストの育成や技術向上への投資・リピーター
#          づくりで信頼を築く動きも指摘）。
NAIL_ID="biz-flow-nail"
NAIL_DOC='{"version":1,"id":"'$NAIL_ID'","title":"ネイルサロンの運営改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"na1","text":"技術と衛生管理・丁寧なカウンセリングによる施術の質を重視する声（品質・衛生）","x":0,"y":0,"textReviewed":true},{"id":"na2","text":"予約の回転率や価格競争への対応など、品質・衛生と効率・収益のトレードオフに悩む声（効率・収益）","x":10,"y":0,"textReviewed":true},{"id":"na3","text":"ネイリストの育成や技術向上への投資、リピーターづくりで信頼を築く動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"nail-i","cardIds":["na1","na2","na3"]}],"readingOrder":["nail-i"]}'

nail_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$NAIL_ID" \
  -H 'Content-Type: application/json' -d "$NAIL_DOC")
check "NAIL PUT document (作成)" "200" "$nail_put"

# ① AI束ね
nail_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"na1","text":"技術と衛生管理・丁寧なカウンセリングによる施術の質を重視する声（品質・衛生）","textReviewed":true},{"id":"na2","text":"予約の回転率や価格競争への対応など、品質・衛生と効率・収益のトレードオフに悩む声（効率・収益）","textReviewed":true},{"id":"na3","text":"ネイリストの育成や技術向上への投資、リピーターづくりで信頼を築く動き","textReviewed":true}]}')
case "$nail_groups" in *'"groups":'*) echo "  PASS: NAIL ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: NAIL ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
nail_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$NAIL_DOC,\"islandId\":\"nail-i\"}")
case "$nail_summary" in *'"groundingIds":["na1","na2","na3"]'*) echo "  PASS: NAIL ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: NAIL ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（品質・衛生 vs 効率・収益・品質・衛生と効率の相克・正パス）
nail_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"na1","text":"技術と衛生管理・丁寧なカウンセリングによる施術の質を重視する声（品質・衛生）","textReviewed":true},"cardB":{"id":"na2","text":"予約の回転率や価格競争への対応など、品質・衛生と効率・収益のトレードオフに悩む声（効率・収益）","textReviewed":true}}')
case "$nail_contra" in *'"hasContradiction":true'*) echo "  PASS: NAIL ③矛盾検出（品質・衛生と効率・収益のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: NAIL ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
nail_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$NAIL_DOC}")
case "$nail_narr" in *'"basedOnReadingOrder":["nail-i"]'*) echo "  PASS: NAIL ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: NAIL ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
nail_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$NAIL_ID")
check "NAIL 読戻し (200)" "200" "$nail_read"

echo ""
echo "--- シナリオ156: ペンション・民宿（おもてなし・地域と効率・収益のトレードオフ） ---"
# 業態: ペンション・民宿（民宿・民泊経営）
# 想定人物: 民宿オーナー／経営者
# 業務領域: 宿泊・食事・おもてなし・地域への声のKJ分類と、民宿経営の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 手作りの料理と温かいおもてなし・地域の魅力を伝える（おもてなし・地域）と人手不足や
#          稼働率への対応（効率・収益）のトレードオフを矛盾検出（正パス）で表面化し、民宿経営の
#          改善根拠にする（おもてなしと効率の相克・地域の素材や文化・農家・職人との連携で民宿ならではの
#          体験をつくる動きも指摘）。
MINSHUKU_ID="biz-flow-minshuku"
MINSHUKU_DOC='{"version":1,"id":"'$MINSHUKU_ID'","title":"民宿経営の改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"ms1","text":"手作りの料理と温かいおもてなし、地域の魅力を伝えることを重視する声（おもてなし・地域）","x":0,"y":0,"textReviewed":true},{"id":"ms2","text":"人手不足や稼働率への対応など、おもてなしと効率・収益のトレードオフに悩む声（効率・収益）","x":10,"y":0,"textReviewed":true},{"id":"ms3","text":"地域の素材や文化、農家・職人との連携で民宿ならではの体験をつくる動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"m-i","cardIds":["ms1","ms2","ms3"]}],"readingOrder":["m-i"]}'

m_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$MINSHUKU_ID" \
  -H 'Content-Type: application/json' -d "$MINSHUKU_DOC")
check "M PUT document (作成)" "200" "$m_put"

# ① AI束ね
m_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"ms1","text":"手作りの料理と温かいおもてなし、地域の魅力を伝えることを重視する声（おもてなし・地域）","textReviewed":true},{"id":"ms2","text":"人手不足や稼働率への対応など、おもてなしと効率・収益のトレードオフに悩む声（効率・収益）","textReviewed":true},{"id":"ms3","text":"地域の素材や文化、農家・職人との連携で民宿ならではの体験をつくる動き","textReviewed":true}]}')
case "$m_groups" in *'"groups":'*) echo "  PASS: M ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: M ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
m_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$MINSHUKU_DOC,\"islandId\":\"m-i\"}")
case "$m_summary" in *'"groundingIds":["ms1","ms2","ms3"]'*) echo "  PASS: M ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: M ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（おもてなし・地域 vs 効率・収益・おもてなしと効率の相克・正パス）
m_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"ms1","text":"手作りの料理と温かいおもてなし、地域の魅力を伝えることを重視する声（おもてなし・地域）","textReviewed":true},"cardB":{"id":"ms2","text":"人手不足や稼働率への対応など、おもてなしと効率・収益のトレードオフに悩む声（効率・収益）","textReviewed":true}}')
case "$m_contra" in *'"hasContradiction":true'*) echo "  PASS: M ③矛盾検出（おもてなし・地域と効率・収益のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: M ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
m_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$MINSHUKU_DOC}")
case "$m_narr" in *'"basedOnReadingOrder":["m-i"]'*) echo "  PASS: M ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: M ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
m_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$MINSHUKU_ID")
check "M 読戻し (200)" "200" "$m_read"

echo ""
echo "--- シナリオ157: 酒場・バー（質・雰囲気と集客・収益のトレードオフ） ---"
# 業態: 酒場・バー（バー・居酒屋運営）
# 想定人物: 店主／バーテンダー
# 業務領域: ドリンク・接客・雰囲気・価格への声のKJ分類と、バー運営の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: オリジナルのドリンクや丁寧な接客・居心地のよい雰囲気づくり（質・雰囲気）と集客や価格設定
#          への対応（集客・収益）のトレードオフを矛盾検出（正パス）で表面化し、バー運営の改善根拠に
#          する（質と集客の相克・常連との関係づくりやイベント・クラフトビールやカクテルの提案で
#          個性を出す動きも指摘）。
BAR_ID="biz-flow-bar"
BAR_DOC='{"version":1,"id":"'$BAR_ID'","title":"バー運営の改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"br1","text":"オリジナルのドリンクや丁寧な接客、居心地のよい雰囲気づくりを重視する声（質・雰囲気）","x":0,"y":0,"textReviewed":true},{"id":"br2","text":"集客や価格設定への対応など、質・雰囲気と集客・収益のトレードオフに悩む声（集客・収益）","x":10,"y":0,"textReviewed":true},{"id":"br3","text":"常連との関係づくりやイベント、クラフトビールやカクテルの提案で個性を出す動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"bar-i","cardIds":["br1","br2","br3"]}],"readingOrder":["bar-i"]}'

bar_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$BAR_ID" \
  -H 'Content-Type: application/json' -d "$BAR_DOC")
check "BAR PUT document (作成)" "200" "$bar_put"

# ① AI束ね
bar_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"br1","text":"オリジナルのドリンクや丁寧な接客、居心地のよい雰囲気づくりを重視する声（質・雰囲気）","textReviewed":true},{"id":"br2","text":"集客や価格設定への対応など、質・雰囲気と集客・収益のトレードオフに悩む声（集客・収益）","textReviewed":true},{"id":"br3","text":"常連との関係づくりやイベント、クラフトビールやカクテルの提案で個性を出す動き","textReviewed":true}]}')
case "$bar_groups" in *'"groups":'*) echo "  PASS: BAR ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: BAR ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
bar_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$BAR_DOC,\"islandId\":\"bar-i\"}")
case "$bar_summary" in *'"groundingIds":["br1","br2","br3"]'*) echo "  PASS: BAR ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: BAR ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（質・雰囲気 vs 集客・収益・質と集客の相克・正パス）
bar_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"br1","text":"オリジナルのドリンクや丁寧な接客、居心地のよい雰囲気づくりを重視する声（質・雰囲気）","textReviewed":true},"cardB":{"id":"br2","text":"集客や価格設定への対応など、質・雰囲気と集客・収益のトレードオフに悩む声（集客・収益）","textReviewed":true}}')
case "$bar_contra" in *'"hasContradiction":true'*) echo "  PASS: BAR ③矛盾検出（質・雰囲気と集客・収益のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: BAR ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
bar_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$BAR_DOC}")
case "$bar_narr" in *'"basedOnReadingOrder":["bar-i"]'*) echo "  PASS: BAR ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: BAR ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
bar_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$BAR_ID")
check "BAR 読戻し (200)" "200" "$bar_read"

echo ""
echo "--- シナリオ158: 音楽教室・カルチャースクール（教育の質・成長と効率・収益のトレードオフ） ---"
# 業態: 音楽教室・カルチャースクール（音楽教室運営）
# 想定人物: 教室長／講師
# 業務領域: レッスン・生徒の成長・講師・運営への声のKJ分類と、教室運営の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 一人ひとりの成長に寄り添う丁寧な指導と音楽の楽しさを伝える（教育の質・成長）と
#          レッスン枠や集客への圧力（効率・収益）のトレードオフを矛盾検出（正パス）で表面化し、
#          教室運営の改善根拠にする（教育の質と効率の相克・発表会やアンサンブル・大人の学び直しの場
#          として地域に開かれた教室を目指す動きも指摘）。
MUSIC_ID="biz-flow-music-school"
MUSIC_DOC='{"version":1,"id":"'$MUSIC_ID'","title":"音楽教室の運営改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"mu1","text":"一人ひとりの成長に寄り添う丁寧な指導と音楽の楽しさを伝えることを重視する声（教育の質・成長）","x":0,"y":0,"textReviewed":true},{"id":"mu2","text":"レッスン枠や集客への圧力など、教育の質と運営効率・収益のトレードオフに悩む声（効率・収益）","x":10,"y":0,"textReviewed":true},{"id":"mu3","text":"発表会やアンサンブル、大人の学び直しの場として地域に開かれた教室を目指す動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"music-i","cardIds":["mu1","mu2","mu3"]}],"readingOrder":["music-i"]}'

music_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$MUSIC_ID" \
  -H 'Content-Type: application/json' -d "$MUSIC_DOC")
check "MUSIC PUT document (作成)" "200" "$music_put"

# ① AI束ね
music_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"mu1","text":"一人ひとりの成長に寄り添う丁寧な指導と音楽の楽しさを伝えることを重視する声（教育の質・成長）","textReviewed":true},{"id":"mu2","text":"レッスン枠や集客への圧力など、教育の質と運営効率・収益のトレードオフに悩む声（効率・収益）","textReviewed":true},{"id":"mu3","text":"発表会やアンサンブル、大人の学び直しの場として地域に開かれた教室を目指す動き","textReviewed":true}]}')
case "$music_groups" in *'"groups":'*) echo "  PASS: MUSIC ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: MUSIC ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
music_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$MUSIC_DOC,\"islandId\":\"music-i\"}")
case "$music_summary" in *'"groundingIds":["mu1","mu2","mu3"]'*) echo "  PASS: MUSIC ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: MUSIC ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（教育の質・成長 vs 効率・収益・教育の質と効率の相克・正パス）
music_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"mu1","text":"一人ひとりの成長に寄り添う丁寧な指導と音楽の楽しさを伝えることを重視する声（教育の質・成長）","textReviewed":true},"cardB":{"id":"mu2","text":"レッスン枠や集客への圧力など、教育の質と運営効率・収益のトレードオフに悩む声（効率・収益）","textReviewed":true}}')
case "$music_contra" in *'"hasContradiction":true'*) echo "  PASS: MUSIC ③矛盾検出（教育の質・成長と効率・収益のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: MUSIC ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
music_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$MUSIC_DOC}")
case "$music_narr" in *'"basedOnReadingOrder":["music-i"]'*) echo "  PASS: MUSIC ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: MUSIC ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
music_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$MUSIC_ID")
check "MUSIC 読戻し (200)" "200" "$music_read"

echo ""
echo "--- シナリオ159: ペットケア（動物の福祉・安全と効率・収益のトレードオフ） ---"
# 業態: ペットケア（トリミング・ペットシッター）
# 想定人物: トリマー／ペットケア事業者
# 業務領域: トリミング・預かり・健康管理・飼い主への声のKJ分類と、ペットケアの改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 動物の福祉と安全を最優先し緊張に寄り添う丁寧なトリミングや預かり（福祉・安全）と
#          施術の回転や価格設定への対応（効率・収益）のトレードオフを矛盾検出（正パス）で表面化し、
#          ペットケアの改善根拠にする（福祉と効率の相克・飼い主への健康相談やしつけの支援・長く
#          付き合う関係を築く動きも指摘）。
PETCARE_ID="biz-flow-petcare"
PETCARE_DOC='{"version":1,"id":"'$PETCARE_ID'","title":"ペットケアの改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"pc1","text":"動物の福祉と安全を最優先し、緊張に寄り添う丁寧なトリミングや預かりを重視する声（福祉・安全）","x":0,"y":0,"textReviewed":true},{"id":"pc2","text":"施術の回転や価格設定への対応など、福祉・安全と効率・収益のトレードオフに悩む声（効率・収益）","x":10,"y":0,"textReviewed":true},{"id":"pc3","text":"飼い主への健康相談やしつけの支援、長く付き合う関係を築く動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"pet-i","cardIds":["pc1","pc2","pc3"]}],"readingOrder":["pet-i"]}'

petcare_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$PETCARE_ID" \
  -H 'Content-Type: application/json' -d "$PETCARE_DOC")
check "PETCARE PUT document (作成)" "200" "$petcare_put"

# ① AI束ね
petcare_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"pc1","text":"動物の福祉と安全を最優先し、緊張に寄り添う丁寧なトリミングや預かりを重視する声（福祉・安全）","textReviewed":true},{"id":"pc2","text":"施術の回転や価格設定への対応など、福祉・安全と効率・収益のトレードオフに悩む声（効率・収益）","textReviewed":true},{"id":"pc3","text":"飼い主への健康相談やしつけの支援、長く付き合う関係を築く動き","textReviewed":true}]}')
case "$petcare_groups" in *'"groups":'*) echo "  PASS: PETCARE ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: PETCARE ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
petcare_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$PETCARE_DOC,\"islandId\":\"pet-i\"}")
case "$petcare_summary" in *'"groundingIds":["pc1","pc2","pc3"]'*) echo "  PASS: PETCARE ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: PETCARE ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（福祉・安全 vs 効率・収益・福祉と効率の相克・正パス）
petcare_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"pc1","text":"動物の福祉と安全を最優先し、緊張に寄り添う丁寧なトリミングや預かりを重視する声（福祉・安全）","textReviewed":true},"cardB":{"id":"pc2","text":"施術の回転や価格設定への対応など、福祉・安全と効率・収益のトレードオフに悩む声（効率・収益）","textReviewed":true}}')
case "$petcare_contra" in *'"hasContradiction":true'*) echo "  PASS: PETCARE ③矛盾検出（動物の福祉・安全と効率・収益のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: PETCARE ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
petcare_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$PETCARE_DOC}")
case "$petcare_narr" in *'"basedOnReadingOrder":["pet-i"]'*) echo "  PASS: PETCARE ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: PETCARE ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
petcare_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$PETCARE_ID")
check "PETCARE 読戻し (200)" "200" "$petcare_read"

echo ""
echo "--- シナリオ160: フードトラック・移動販売（品質・衛生と出店・収益のトレードオフ） ---"
# 業態: フードトラック・移動販売（移動販売・屋台）
# 想定人物: フードトラックオーナー／移動販売業者
# 業務領域: メニュー・出店場所・衛生・顧客への声のKJ分類と、移動販売の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 料理の質と衛生管理・地域のイベントでの提供を大切にする（品質・衛生）と出店場所や天候依存
#          （出店・収益）のトレードオフを矛盾検出（正パス）で表面化し、移動販売の改善根拠にする
#          （品質と出店の相克・SNSでの情報発信やリピーターづくり・地域の食の担い手としての役割を
#          模索する動きも指摘）。
FOODTRUCK_ID="biz-flow-foodtruck"
FOODTRUCK_DOC='{"version":1,"id":"'$FOODTRUCK_ID'","title":"移動販売の改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"ft1","text":"料理の質と衛生管理、地域のイベントでの提供を大切にする声（品質・衛生）","x":0,"y":0,"textReviewed":true},{"id":"ft2","text":"出店場所や天候依存など、品質と出店機会・収益のトレードオフに悩む声（出店・収益）","x":10,"y":0,"textReviewed":true},{"id":"ft3","text":"SNSでの情報発信やリピーターづくり、地域の食の担い手としての役割を模索する動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"ft-i","cardIds":["ft1","ft2","ft3"]}],"readingOrder":["ft-i"]}'

foodtruck_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$FOODTRUCK_ID" \
  -H 'Content-Type: application/json' -d "$FOODTRUCK_DOC")
check "FOODTRUCK PUT document (作成)" "200" "$foodtruck_put"

# ① AI束ね
foodtruck_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"ft1","text":"料理の質と衛生管理、地域のイベントでの提供を大切にする声（品質・衛生）","textReviewed":true},{"id":"ft2","text":"出店場所や天候依存など、品質と出店機会・収益のトレードオフに悩む声（出店・収益）","textReviewed":true},{"id":"ft3","text":"SNSでの情報発信やリピーターづくり、地域の食の担い手としての役割を模索する動き","textReviewed":true}]}')
case "$foodtruck_groups" in *'"groups":'*) echo "  PASS: FOODTRUCK ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: FOODTRUCK ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
foodtruck_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$FOODTRUCK_DOC,\"islandId\":\"ft-i\"}")
case "$foodtruck_summary" in *'"groundingIds":["ft1","ft2","ft3"]'*) echo "  PASS: FOODTRUCK ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: FOODTRUCK ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（品質・衛生 vs 出店・収益・品質と出店の相克・正パス）
foodtruck_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"ft1","text":"料理の質と衛生管理、地域のイベントでの提供を大切にする声（品質・衛生）","textReviewed":true},"cardB":{"id":"ft2","text":"出店場所や天候依存など、品質と出店機会・収益のトレードオフに悩む声（出店・収益）","textReviewed":true}}')
case "$foodtruck_contra" in *'"hasContradiction":true'*) echo "  PASS: FOODTRUCK ③矛盾検出（品質・衛生と出店・収益のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: FOODTRUCK ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
foodtruck_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$FOODTRUCK_DOC}")
case "$foodtruck_narr" in *'"basedOnReadingOrder":["ft-i"]'*) echo "  PASS: FOODTRUCK ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: FOODTRUCK ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
foodtruck_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$FOODTRUCK_ID")
check "FOODTRUCK 読戻し (200)" "200" "$foodtruck_read"

echo ""
echo "--- シナリオ161: 介護・福祉用具（利用者本位・適合と効率・収益のトレードオフ） ---"
# 業態: 介護・福祉用具（福祉用具レンタル・販売）
# 想定人物: 福祉用具専門相談員／事業者
# 業務領域: 用具の提案・レンタル・調整・利用者への声のKJ分類と、福祉用具事業の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 利用者一人ひとりに合った福祉用具の提案と丁寧な調整（利用者本位・適合）と在庫管理や
#          コストへの圧力（効率・収益）のトレードオフを矛盾検出（正パス）で表面化し、福祉用具事業の
#          改善根拠にする（利用者本位と効率の相克・介護する家族への相談支援や地域のケアマネとの連携
#          で支える動きも指摘）。
WELFARE_ID="biz-flow-welfare"
WELFARE_DOC='{"version":1,"id":"'$WELFARE_ID'","title":"福祉用具事業の改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"wl1","text":"利用者一人ひとりに合った福祉用具の提案と丁寧な調整を重視する声（利用者本位・適合）","x":0,"y":0,"textReviewed":true},{"id":"wl2","text":"在庫管理やコストへの圧力など、利用者本位と効率・収益のトレードオフに悩む声（効率・収益）","x":10,"y":0,"textReviewed":true},{"id":"wl3","text":"介護する家族への相談支援や地域のケアマネとの連携で支える動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"welf-i","cardIds":["wl1","wl2","wl3"]}],"readingOrder":["welf-i"]}'

welfare_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$WELFARE_ID" \
  -H 'Content-Type: application/json' -d "$WELFARE_DOC")
check "WELFARE PUT document (作成)" "200" "$welfare_put"

# ① AI束ね
welfare_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"wl1","text":"利用者一人ひとりに合った福祉用具の提案と丁寧な調整を重視する声（利用者本位・適合）","textReviewed":true},{"id":"wl2","text":"在庫管理やコストへの圧力など、利用者本位と効率・収益のトレードオフに悩む声（効率・収益）","textReviewed":true},{"id":"wl3","text":"介護する家族への相談支援や地域のケアマネとの連携で支える動き","textReviewed":true}]}')
case "$welfare_groups" in *'"groups":'*) echo "  PASS: WELFARE ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: WELFARE ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
welfare_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$WELFARE_DOC,\"islandId\":\"welf-i\"}")
case "$welfare_summary" in *'"groundingIds":["wl1","wl2","wl3"]'*) echo "  PASS: WELFARE ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: WELFARE ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（利用者本位・適合 vs 効率・収益・利用者本位と効率の相克・正パス）
welfare_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"wl1","text":"利用者一人ひとりに合った福祉用具の提案と丁寧な調整を重視する声（利用者本位・適合）","textReviewed":true},"cardB":{"id":"wl2","text":"在庫管理やコストへの圧力など、利用者本位と効率・収益のトレードオフに悩む声（効率・収益）","textReviewed":true}}')
case "$welfare_contra" in *'"hasContradiction":true'*) echo "  PASS: WELFARE ③矛盾検出（利用者本位・適合と効率・収益のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: WELFARE ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
welfare_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$WELFARE_DOC}")
case "$welfare_narr" in *'"basedOnReadingOrder":["welf-i"]'*) echo "  PASS: WELFARE ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: WELFARE ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
welfare_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$WELFARE_ID")
check "WELFARE 読戻し (200)" "200" "$welfare_read"

echo ""
echo "--- シナリオ162: シェアオフィス・コワーキング（環境・コミュニティと稼働率・収益のトレードオフ） ---"
# 業態: シェアオフィス・コワーキング（ワークスペース運営）
# 想定人物: 施設運営マネージャー
# 業務領域: 設備・コミュニティ・会員・運営への声のKJ分類と、ワークスペース運営の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 快適な設備と交流のあるコミュニティづくり・会員の成長支援（環境・コミュニティ）と稼働率や
#          会費設定への対応（稼働率・収益）のトレードオフを矛盾検出（正パス）で表面化し、ワークスペース
#          運営の改善根拠にする（環境・コミュニティと稼働率の相克・イベントや勉強会・スタートアップ支援
#          で会員同士のつながりを育てる動きも指摘）。
COWORK_ID="biz-flow-coworking"
COWORK_DOC='{"version":1,"id":"'$COWORK_ID'","title":"ワークスペース運営の改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"co1","text":"快適な設備と交流のあるコミュニティづくり、会員の成長支援を重視する声（環境・コミュニティ）","x":0,"y":0,"textReviewed":true},{"id":"co2","text":"稼働率や会費設定への対応など、環境・コミュニティと稼働率・収益のトレードオフに悩む声（稼働率・収益）","x":10,"y":0,"textReviewed":true},{"id":"co3","text":"イベントや勉強会、スタートアップ支援で会員同士のつながりを育てる動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"cowork-i","cardIds":["co1","co2","co3"]}],"readingOrder":["cowork-i"]}'

cowork_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$COWORK_ID" \
  -H 'Content-Type: application/json' -d "$COWORK_DOC")
check "COWORK PUT document (作成)" "200" "$cowork_put"

# ① AI束ね
cowork_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"co1","text":"快適な設備と交流のあるコミュニティづくり、会員の成長支援を重視する声（環境・コミュニティ）","textReviewed":true},{"id":"co2","text":"稼働率や会費設定への対応など、環境・コミュニティと稼働率・収益のトレードオフに悩む声（稼働率・収益）","textReviewed":true},{"id":"co3","text":"イベントや勉強会、スタートアップ支援で会員同士のつながりを育てる動き","textReviewed":true}]}')
case "$cowork_groups" in *'"groups":'*) echo "  PASS: COWORK ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: COWORK ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
cowork_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$COWORK_DOC,\"islandId\":\"cowork-i\"}")
case "$cowork_summary" in *'"groundingIds":["co1","co2","co3"]'*) echo "  PASS: COWORK ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: COWORK ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（環境・コミュニティ vs 稼働率・収益・環境・コミュニティと稼働率の相克・正パス）
cowork_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"co1","text":"快適な設備と交流のあるコミュニティづくり、会員の成長支援を重視する声（環境・コミュニティ）","textReviewed":true},"cardB":{"id":"co2","text":"稼働率や会費設定への対応など、環境・コミュニティと稼働率・収益のトレードオフに悩む声（稼働率・収益）","textReviewed":true}}')
case "$cowork_contra" in *'"hasContradiction":true'*) echo "  PASS: COWORK ③矛盾検出（環境・コミュニティと稼働率・収益のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: COWORK ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
cowork_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$COWORK_DOC}")
case "$cowork_narr" in *'"basedOnReadingOrder":["cowork-i"]'*) echo "  PASS: COWORK ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: COWORK ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
cowork_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$COWORK_ID")
check "COWORK 読戻し (200)" "200" "$cowork_read"

echo ""
echo "--- シナリオ163: ドローン事業（安全・法令と業務効率・収益のトレードオフ） ---"
# 業態: ドローン事業（ドローンスクール・空撮・測量）
# 想定人物: ドローン事業責任者／パイロット
# 業務領域: 空撮・測量・点検・安全管理・規制への声のKJ分類と、ドローン事業の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 安全運航と法令順守（飛行許可・操縦資格）を最優先する（安全・法令）と受注やコストへの圧力
#          （効率・収益）のトレードオフを矛盾検出（正パス）で表面化し、ドローン事業の改善根拠にする
#          （安全と効率の相克・農業・インフラ点検・災害対応など新しい活用法を開拓する動きも指摘）。
DRONE_ID="biz-flow-drone"
DRONE_DOC='{"version":1,"id":"'$DRONE_ID'","title":"ドローン事業の改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"dr1","text":"安全運航と法令順守（飛行許可・操縦資格）を最優先する声（安全・法令）","x":0,"y":0,"textReviewed":true},{"id":"dr2","text":"受注やコストへの圧力など、安全・法令と業務効率・収益のトレードオフに悩む声（効率・収益）","x":10,"y":0,"textReviewed":true},{"id":"dr3","text":"農業・インフラ点検・災害対応など新しい活用法を開拓する動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"drone-i","cardIds":["dr1","dr2","dr3"]}],"readingOrder":["drone-i"]}'

drone_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$DRONE_ID" \
  -H 'Content-Type: application/json' -d "$DRONE_DOC")
check "DRONE PUT document (作成)" "200" "$drone_put"

# ① AI束ね
drone_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"dr1","text":"安全運航と法令順守（飛行許可・操縦資格）を最優先する声（安全・法令）","textReviewed":true},{"id":"dr2","text":"受注やコストへの圧力など、安全・法令と業務効率・収益のトレードオフに悩む声（効率・収益）","textReviewed":true},{"id":"dr3","text":"農業・インフラ点検・災害対応など新しい活用法を開拓する動き","textReviewed":true}]}')
case "$drone_groups" in *'"groups":'*) echo "  PASS: DRONE ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: DRONE ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
drone_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$DRONE_DOC,\"islandId\":\"drone-i\"}")
case "$drone_summary" in *'"groundingIds":["dr1","dr2","dr3"]'*) echo "  PASS: DRONE ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: DRONE ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（安全・法令 vs 効率・収益・安全と効率の相克・正パス）
drone_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"dr1","text":"安全運航と法令順守（飛行許可・操縦資格）を最優先する声（安全・法令）","textReviewed":true},"cardB":{"id":"dr2","text":"受注やコストへの圧力など、安全・法令と業務効率・収益のトレードオフに悩む声（効率・収益）","textReviewed":true}}')
case "$drone_contra" in *'"hasContradiction":true'*) echo "  PASS: DRONE ③矛盾検出（安全・法令と業務効率・収益のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: DRONE ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
drone_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$DRONE_DOC}")
case "$drone_narr" in *'"basedOnReadingOrder":["drone-i"]'*) echo "  PASS: DRONE ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: DRONE ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
drone_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$DRONE_ID")
check "DRONE 読戻し (200)" "200" "$drone_read"

echo ""
echo "--- シナリオ164: パン屋・ベーカリー（こだわり・品質と効率・売上のトレードオフ） ---"
# 業態: パン屋・ベーカリー（パン製造・ベーカリー店）
# 想定人物: ベーカリーオーナー／パン職人
# 業務領域: 製パン・商品・衛生・販売への声のKJ分類と、ベーカリー運営の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: こだわりの製パンと焼きたての品質・素材へのこだわり（こだわり・品質）と生産効率や販売への
#          対応（効率・売上）のトレードオフを矛盾検出（正パス）で表面化し、ベーカリー運営の改善根拠に
#          する（こだわりと効率の相克・季節の商品や地域の素材・子ども向けの体験で地域に愛される店を
#          目指す動きも指摘）。
BAKERY_ID="biz-flow-bakery"
BAKERY_DOC='{"version":1,"id":"'$BAKERY_ID'","title":"ベーカリー運営の改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"bk1","text":"こだわりの製パンと焼きたての品質、素材へのこだわりを重視する声（こだわり・品質）","x":0,"y":0,"textReviewed":true},{"id":"bk2","text":"生産効率や販売への対応など、こだわり・品質と効率・売上のトレードオフに悩む声（効率・売上）","x":10,"y":0,"textReviewed":true},{"id":"bk3","text":"季節の商品や地域の素材、子ども向けの体験で地域に愛される店を目指す動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"bakery-i","cardIds":["bk1","bk2","bk3"]}],"readingOrder":["bakery-i"]}'

bakery_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$BAKERY_ID" \
  -H 'Content-Type: application/json' -d "$BAKERY_DOC")
check "BAKERY PUT document (作成)" "200" "$bakery_put"

# ① AI束ね
bakery_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"bk1","text":"こだわりの製パンと焼きたての品質、素材へのこだわりを重視する声（こだわり・品質）","textReviewed":true},{"id":"bk2","text":"生産効率や販売への対応など、こだわり・品質と効率・売上のトレードオフに悩む声（効率・売上）","textReviewed":true},{"id":"bk3","text":"季節の商品や地域の素材、子ども向けの体験で地域に愛される店を目指す動き","textReviewed":true}]}')
case "$bakery_groups" in *'"groups":'*) echo "  PASS: BAKERY ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: BAKERY ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
bakery_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$BAKERY_DOC,\"islandId\":\"bakery-i\"}")
case "$bakery_summary" in *'"groundingIds":["bk1","bk2","bk3"]'*) echo "  PASS: BAKERY ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: BAKERY ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（こだわり・品質 vs 効率・売上・こだわりと効率の相克・正パス）
bakery_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"bk1","text":"こだわりの製パンと焼きたての品質、素材へのこだわりを重視する声（こだわり・品質）","textReviewed":true},"cardB":{"id":"bk2","text":"生産効率や販売への対応など、こだわり・品質と効率・売上のトレードオフに悩む声（効率・売上）","textReviewed":true}}')
case "$bakery_contra" in *'"hasContradiction":true'*) echo "  PASS: BAKERY ③矛盾検出（こだわり・品質と効率・売上のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: BAKERY ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
bakery_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$BAKERY_DOC}")
case "$bakery_narr" in *'"basedOnReadingOrder":["bakery-i"]'*) echo "  PASS: BAKERY ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: BAKERY ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
bakery_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$BAKERY_ID")
check "BAKERY 読戻し (200)" "200" "$bakery_read"

echo ""
echo "--- シナリオ165: ゴルフ場・練習場（品質・サービスとコスト・稼働のトレードオフ） ---"
# 業態: ゴルフ場・ゴルフ練習場（ゴルフ場運営）
# 想定人物: ゴルフ場支配人／コース管理担当
# 業務領域: コース管理・接客・会員・運営への声のKJ分類と、ゴルフ場運営の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: コースのメンテナンスと接客・おもてなし・快適なラウンド体験（品質・サービス）とコスト削減や
#          稼働率への圧力（コスト・稼働）のトレードオフを矛盾検出（正パス）で表面化し、ゴルフ場運営の
#          改善根拠にする（品質とコストの相克・初心者や若年層向けのプラン・地域のコミュニティとしての
#          活用を模索する動きも指摘）。
GOLF_ID="biz-flow-golf"
GOLF_DOC='{"version":1,"id":"'$GOLF_ID'","title":"ゴルフ場運営の改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"go1","text":"コースのメンテナンスと接客・おもてなし、快適なラウンド体験を重視する声（品質・サービス）","x":0,"y":0,"textReviewed":true},{"id":"go2","text":"コスト削減や稼働率への圧力など、品質・サービスとコスト・稼働のトレードオフに悩む声（コスト・稼働）","x":10,"y":0,"textReviewed":true},{"id":"go3","text":"初心者や若年層向けのプラン、地域のコミュニティとしての活用を模索する動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"golf-i","cardIds":["go1","go2","go3"]}],"readingOrder":["golf-i"]}'

golf_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$GOLF_ID" \
  -H 'Content-Type: application/json' -d "$GOLF_DOC")
check "GOLF PUT document (作成)" "200" "$golf_put"

# ① AI束ね
golf_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"go1","text":"コースのメンテナンスと接客・おもてなし、快適なラウンド体験を重視する声（品質・サービス）","textReviewed":true},{"id":"go2","text":"コスト削減や稼働率への圧力など、品質・サービスとコスト・稼働のトレードオフに悩む声（コスト・稼働）","textReviewed":true},{"id":"go3","text":"初心者や若年層向けのプラン、地域のコミュニティとしての活用を模索する動き","textReviewed":true}]}')
case "$golf_groups" in *'"groups":'*) echo "  PASS: GOLF ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: GOLF ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
golf_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$GOLF_DOC,\"islandId\":\"golf-i\"}")
case "$golf_summary" in *'"groundingIds":["go1","go2","go3"]'*) echo "  PASS: GOLF ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: GOLF ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（品質・サービス vs コスト・稼働・品質とコストの相克・正パス）
golf_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"go1","text":"コースのメンテナンスと接客・おもてなし、快適なラウンド体験を重視する声（品質・サービス）","textReviewed":true},"cardB":{"id":"go2","text":"コスト削減や稼働率への圧力など、品質・サービスとコスト・稼働のトレードオフに悩む声（コスト・稼働）","textReviewed":true}}')
case "$golf_contra" in *'"hasContradiction":true'*) echo "  PASS: GOLF ③矛盾検出（品質・サービスとコスト・稼働のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: GOLF ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
golf_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$GOLF_DOC}")
case "$golf_narr" in *'"basedOnReadingOrder":["golf-i"]'*) echo "  PASS: GOLF ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: GOLF ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
golf_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$GOLF_ID")
check "GOLF 読戻し (200)" "200" "$golf_read"

echo ""
echo "--- シナリオ166: 漫画喫茶・ネットカフェ（環境・サービスと稼働・コストのトレードオフ） ---"
# 業態: 漫画喫茶・ネットカフェ（複合カフェ運営）
# 想定人物: 店長／運営責任者
# 業務領域: 設備・滞在環境・サービス・価格への声のKJ分類と、複合カフェ運営の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 静かで清潔な個室環境と充実したサービス（環境・サービス）と稼働率や人件費への圧力
#          （稼働・コスト）のトレードオフを矛盾検出（正パス）で表面化し、複合カフェ運営の改善根拠に
#          する（環境・サービスと稼働の相克・仕事や休憩・滞在の多様な使い方に応える柔軟な料金や
#          プランを模索する動きも指摘）。
NETKAFE_ID="biz-flow-netkafe"
NETKAFE_DOC='{"version":1,"id":"'$NETKAFE_ID'","title":"複合カフェ運営の改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"nk1","text":"静かで清潔な個室環境と充実したサービス（ドリンク・設備）を重視する声（環境・サービス）","x":0,"y":0,"textReviewed":true},{"id":"nk2","text":"稼働率や人件費への圧力など、環境・サービスと稼働・コストのトレードオフに悩む声（稼働・コスト）","x":10,"y":0,"textReviewed":true},{"id":"nk3","text":"仕事や休憩、滞在の多様な使い方に応える柔軟な料金やプランを模索する動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"nk-i","cardIds":["nk1","nk2","nk3"]}],"readingOrder":["nk-i"]}'

nk_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$NETKAFE_ID" \
  -H 'Content-Type: application/json' -d "$NETKAFE_DOC")
check "NK PUT document (作成)" "200" "$nk_put"

# ① AI束ね
nk_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"nk1","text":"静かで清潔な個室環境と充実したサービス（ドリンク・設備）を重視する声（環境・サービス）","textReviewed":true},{"id":"nk2","text":"稼働率や人件費への圧力など、環境・サービスと稼働・コストのトレードオフに悩む声（稼働・コスト）","textReviewed":true},{"id":"nk3","text":"仕事や休憩、滞在の多様な使い方に応える柔軟な料金やプランを模索する動き","textReviewed":true}]}')
case "$nk_groups" in *'"groups":'*) echo "  PASS: NK ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: NK ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
nk_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$NETKAFE_DOC,\"islandId\":\"nk-i\"}")
case "$nk_summary" in *'"groundingIds":["nk1","nk2","nk3"]'*) echo "  PASS: NK ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: NK ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（環境・サービス vs 稼働・コスト・環境・サービスと稼働の相克・正パス）
nk_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"nk1","text":"静かで清潔な個室環境と充実したサービス（ドリンク・設備）を重視する声（環境・サービス）","textReviewed":true},"cardB":{"id":"nk2","text":"稼働率や人件費への圧力など、環境・サービスと稼働・コストのトレードオフに悩む声（稼働・コスト）","textReviewed":true}}')
case "$nk_contra" in *'"hasContradiction":true'*) echo "  PASS: NK ③矛盾検出（環境・サービスと稼働・コストのトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: NK ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
nk_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$NETKAFE_DOC}")
case "$nk_narr" in *'"basedOnReadingOrder":["nk-i"]'*) echo "  PASS: NK ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: NK ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
nk_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$NETKAFE_ID")
check "NK 読戻し (200)" "200" "$nk_read"

echo ""
echo "--- シナリオ167: 眼鏡店・コンタクト（目の健康・適合と効率・価格のトレードオフ） ---"
# 業態: 眼鏡店・コンタクト（眼鏡・コンタクトレンズ販売）
# 想定人物: 眼鏡店店長／認定コンタクト・補聴器担当
# 業務領域: 商品・フィッティング・検眼・アフターへの声のKJ分類と、眼鏡店運営の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 丁寧な検眼とフィッティング・目の健康を考えた提案（目の健康・適合）と価格競争やネット通販への
#          対応（効率・価格）のトレードオフを矛盾検出（正パス）で表面化し、眼鏡店運営の改善根拠にする
#          （目の健康と効率の相克・定期検診やメンテナンスの案内・長く安心して使える関係を築く動きも指摘）。
EYEWEAR_ID="biz-flow-eyewear"
EYEWEAR_DOC='{"version":1,"id":"'$EYEWEAR_ID'","title":"眼鏡店運営の改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"eg1","text":"丁寧な検眼とフィッティング、目の健康を考えた提案を重視する声（目の健康・適合）","x":0,"y":0,"textReviewed":true},{"id":"eg2","text":"価格競争やネット通販への対応など、目の健康・適合と効率・価格のトレードオフに悩む声（効率・価格）","x":10,"y":0,"textReviewed":true},{"id":"eg3","text":"定期検診やメンテナンスの案内、長く安心して使える関係を築く動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"eye-i","cardIds":["eg1","eg2","eg3"]}],"readingOrder":["eye-i"]}'

eyewear_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$EYEWEAR_ID" \
  -H 'Content-Type: application/json' -d "$EYEWEAR_DOC")
check "EYEWEAR PUT document (作成)" "200" "$eyewear_put"

# ① AI束ね
eyewear_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"eg1","text":"丁寧な検眼とフィッティング、目の健康を考えた提案を重視する声（目の健康・適合）","textReviewed":true},{"id":"eg2","text":"価格競争やネット通販への対応など、目の健康・適合と効率・価格のトレードオフに悩む声（効率・価格）","textReviewed":true},{"id":"eg3","text":"定期検診やメンテナンスの案内、長く安心して使える関係を築く動き","textReviewed":true}]}')
case "$eyewear_groups" in *'"groups":'*) echo "  PASS: EYEWEAR ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: EYEWEAR ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
eyewear_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$EYEWEAR_DOC,\"islandId\":\"eye-i\"}")
case "$eyewear_summary" in *'"groundingIds":["eg1","eg2","eg3"]'*) echo "  PASS: EYEWEAR ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: EYEWEAR ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（目の健康・適合 vs 効率・価格・目の健康と効率の相克・正パス）
eyewear_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"eg1","text":"丁寧な検眼とフィッティング、目の健康を考えた提案を重視する声（目の健康・適合）","textReviewed":true},"cardB":{"id":"eg2","text":"価格競争やネット通販への対応など、目の健康・適合と効率・価格のトレードオフに悩む声（効率・価格）","textReviewed":true}}')
case "$eyewear_contra" in *'"hasContradiction":true'*) echo "  PASS: EYEWEAR ③矛盾検出（目の健康・適合と効率・価格のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: EYEWEAR ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
eyewear_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$EYEWEAR_DOC}")
case "$eyewear_narr" in *'"basedOnReadingOrder":["eye-i"]'*) echo "  PASS: EYEWEAR ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: EYEWEAR ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
eyewear_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$EYEWEAR_ID")
check "EYEWEAR 読戻し (200)" "200" "$eyewear_read"

echo ""
echo "--- シナリオ168: 建築設計事務所（デザイン・品質とコスト・工期のトレードオフ） ---"
# 業態: 建築設計事務所（建築設計・監理）
# 想定人物: 建築家／設計事務所代表
# 業務領域: 設計・監理・クライアント・コストへの声のKJ分類と、設計事務所の運営改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 設計の質とこだわり・住まい手の想いを形にする（デザイン・品質）とコストや工期への圧力
#          （コスト・工期）のトレードオフを矛盾検出（正パス）で表面化し、設計事務所の運営改善根拠に
#          する（デザインとコストの相克・地域の景観や既存建物の再生・住民との対話を大切にする動きも指摘）。
ARCH_ID="biz-flow-architecture"
ARCH_DOC='{"version":1,"id":"'$ARCH_ID'","title":"設計事務所の運営改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"ar1","text":"設計の質とこだわり、住まい手の想いを形にすることを重視する声（デザイン・品質）","x":0,"y":0,"textReviewed":true},{"id":"ar2","text":"コストや工期への圧力など、設計の質とコスト・工期のトレードオフに悩む声（コスト・工期）","x":10,"y":0,"textReviewed":true},{"id":"ar3","text":"地域の景観や既存建物の再生、住民との対話を大切にする動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"arch-i","cardIds":["ar1","ar2","ar3"]}],"readingOrder":["arch-i"]}'

arch_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$ARCH_ID" \
  -H 'Content-Type: application/json' -d "$ARCH_DOC")
check "ARCH PUT document (作成)" "200" "$arch_put"

# ① AI束ね
arch_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"ar1","text":"設計の質とこだわり、住まい手の想いを形にすることを重視する声（デザイン・品質）","textReviewed":true},{"id":"ar2","text":"コストや工期への圧力など、設計の質とコスト・工期のトレードオフに悩む声（コスト・工期）","textReviewed":true},{"id":"ar3","text":"地域の景観や既存建物の再生、住民との対話を大切にする動き","textReviewed":true}]}')
case "$arch_groups" in *'"groups":'*) echo "  PASS: ARCH ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: ARCH ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
arch_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$ARCH_DOC,\"islandId\":\"arch-i\"}")
case "$arch_summary" in *'"groundingIds":["ar1","ar2","ar3"]'*) echo "  PASS: ARCH ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: ARCH ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（デザイン・品質 vs コスト・工期・デザインとコストの相克・正パス）
arch_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"ar1","text":"設計の質とこだわり、住まい手の想いを形にすることを重視する声（デザイン・品質）","textReviewed":true},"cardB":{"id":"ar2","text":"コストや工期への圧力など、設計の質とコスト・工期のトレードオフに悩む声（コスト・工期）","textReviewed":true}}')
case "$arch_contra" in *'"hasContradiction":true'*) echo "  PASS: ARCH ③矛盾検出（デザイン・品質とコスト・工期のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: ARCH ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
arch_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$ARCH_DOC}")
case "$arch_narr" in *'"basedOnReadingOrder":["arch-i"]'*) echo "  PASS: ARCH ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: ARCH ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
arch_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$ARCH_ID")
check "ARCH 読戻し (200)" "200" "$arch_read"

echo ""
echo "--- シナリオ169: クルーズ・観光船（安全・サービスと収益・効率のトレードオフ） ---"
# 業態: クルーズ・観光船（クルーズ運航・旅客船）
# 想定人物: クルーズ船運航責任者／船長
# 業務領域: 航路・サービス・安全・乗客への声のKJ分類と、クルーズ運航の改善
# 操作内容: 文書作成 -> AI束ね(suggest-card-groups) -> 島要約(suggest-island-summary)
#          -> 矛盾検出(detect-contradiction・正パス) -> ナラティブ(generate-narrative)
#          -> 読戻し
# 注意事項: 安全運航と乗客の快適さ・思い出に残る船旅の提供（安全・サービス）と運航コストや収益への圧力
#          （収益・効率）のトレードオフを矛盾検出（正パス）で表面化し、クルーズ運航の改善根拠にする
#          （安全・サービスと収益の相克・地域の観光や寄港地との連携・新しい航路や体験を開拓する動きも指摘）。
CRUISE_ID="biz-flow-cruise"
CRUISE_DOC='{"version":1,"id":"'$CRUISE_ID'","title":"クルーズ運航の改善","createdAt":"2026-08-17T00:00:00Z","updatedAt":"2026-08-17T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"cr1","text":"安全運航と乗客の快適さ、思い出に残る船旅の提供を重視する声（安全・サービス）","x":0,"y":0,"textReviewed":true},{"id":"cr2","text":"運航コストや収益への圧力など、安全・サービスと収益・効率のトレードオフに悩む声（収益・効率）","x":10,"y":0,"textReviewed":true},{"id":"cr3","text":"地域の観光や寄港地との連携、新しい航路や体験を開拓する動き","x":20,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"cruise-i","cardIds":["cr1","cr2","cr3"]}],"readingOrder":["cruise-i"]}'

cruise_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$CRUISE_ID" \
  -H 'Content-Type: application/json' -d "$CRUISE_DOC")
check "CRUISE PUT document (作成)" "200" "$cruise_put"

# ① AI束ね
cruise_groups=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' \
  -d '{"cards":[{"id":"cr1","text":"安全運航と乗客の快適さ、思い出に残る船旅の提供を重視する声（安全・サービス）","textReviewed":true},{"id":"cr2","text":"運航コストや収益への圧力など、安全・サービスと収益・効率のトレードオフに悩む声（収益・効率）","textReviewed":true},{"id":"cr3","text":"地域の観光や寄港地との連携、新しい航路や体験を開拓する動き","textReviewed":true}]}')
case "$cruise_groups" in *'"groups":'*) echo "  PASS: CRUISE ①束ね"; PASS=$((PASS+1));; *) echo "  FAIL: CRUISE ①束ね"; FAIL=$((FAIL+1));; esac

# ② 島要約
cruise_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$CRUISE_DOC,\"islandId\":\"cruise-i\"}")
case "$cruise_summary" in *'"groundingIds":["cr1","cr2","cr3"]'*) echo "  PASS: CRUISE ②島要約"; PASS=$((PASS+1));; *) echo "  FAIL: CRUISE ②島要約"; FAIL=$((FAIL+1));; esac

# ③ 矛盾検出（安全・サービス vs 収益・効率・安全・サービスと収益の相克・正パス）
cruise_contra=$(curl -s -X POST "$BASE_URL/ai/detect-contradiction" -H 'Content-Type: application/json' \
  -d '{"cardA":{"id":"cr1","text":"安全運航と乗客の快適さ、思い出に残る船旅の提供を重視する声（安全・サービス）","textReviewed":true},"cardB":{"id":"cr2","text":"運航コストや収益への圧力など、安全・サービスと収益・効率のトレードオフに悩む声（収益・効率）","textReviewed":true}}')
case "$cruise_contra" in *'"hasContradiction":true'*) echo "  PASS: CRUISE ③矛盾検出（安全・サービスと収益・効率のトレードオフを正パスで表面化）"; PASS=$((PASS+1));; *) echo "  FAIL: CRUISE ③矛盾検出"; FAIL=$((FAIL+1));; esac

# ④ ナラティブ
cruise_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$CRUISE_DOC}")
case "$cruise_narr" in *'"basedOnReadingOrder":["cruise-i"]'*) echo "  PASS: CRUISE ④ナラティブ"; PASS=$((PASS+1));; *) echo "  FAIL: CRUISE ④ナラティブ"; FAIL=$((FAIL+1));; esac

# ⑤ 読戻し
cruise_read=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/docs/$CRUISE_ID")
check "CRUISE 読戻し (200)" "200" "$cruise_read"

echo ""
echo "--- シナリオ170: 高度ドッグフーディング・第1ラウンド200枚（実物大のカード化→束ね→島統合→叙述化） ---"
# 業態: ソフトウェア開発組織（kj-atlas プロダクト改善）
# 想定人物: プロダクトオーナー（kj-atlas自身の改善観察を200枚にカード化）
# 業務領域: 第1ラウンドで200枚のカードを作り、実物大のキャンバスで束ね・島統合・叙述化・A/B照合まで行う
# 操作内容: 文書作成(200枚・丁寧な実観察カード) -> 読戻し(200枚保持)
#          -> card-groups(200枚→10領域) -> 島要約(接地10件キャップ) -> ナラティブ -> A/B照合
# 注意事項: kj_technique.md §1「数百枚は正常」。card-groups は DOGFOOD-31 で100→1000枚へ緩和済み。
#          接地は10件上限（品質ガード）で、モックが代表10件へキャップする。
BIG_ID="biz-flow-200cards"
# 200枚の丁寧な実観察カードを生成スクリプトから読み込む（kj-atlas自身の改善機会・10領域×20枚）。
BIG_DOC="$("$VENV_PYTHON" "$SCRIPT_DIR/generate_kj_atlas_improvement_cards.py")"

# ① 文書作成（200枚）
big_put=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$BASE_URL/docs/$BIG_ID" \
  -H 'Content-Type: application/json' -d "$BIG_DOC")
check "BIG PUT document 200枚 (作成)" "200" "$big_put"

# ② 読戻し（200枚保持）
big_read=$(curl -s "$BASE_URL/docs/$BIG_ID")
big_card_count=$(echo "$big_read" | "$VENV_PYTHON" -c "import json,sys; print(len(json.load(sys.stdin)['cards']))")
check "BIG 読戻し 200枚保持" "200" "$big_card_count"

# ③ card-groups 200枚 → 10領域（DOGFOOD-31 緩和後・全カードを欠落なく束ねる）
big_cards=$(echo "$BIG_DOC" | "$VENV_PYTHON" -c "import json,sys; d=json.load(sys.stdin); print(json.dumps({'cards':[{'id':c['id'],'text':c['text'],'textReviewed':True} for c in d['cards']]}, ensure_ascii=False))")
big_grp=$(curl -s -X POST "$BASE_URL/ai/suggest-card-groups" -H 'Content-Type: application/json' -d "$big_cards")
big_grp_count=$(echo "$big_grp" | "$VENV_PYTHON" -c "import json,sys; d=json.load(sys.stdin); g=d.get('groups',[]); print(len(g))" 2>/dev/null)
big_grp_total=$(echo "$big_grp" | "$VENV_PYTHON" -c "import json,sys; d=json.load(sys.stdin); print(sum(len(x.get('cardIds',[])) for x in d.get('groups',[])))" 2>/dev/null)
check "BIG ③card-groups 200枚 → 10領域" "10" "$big_grp_count"
check "BIG ③b 束ね総カード数 200（欠落なし）" "200" "$big_grp_total"

# ④ 島要約（200枚島・接地10件キャップで成立）
big_summary=$(curl -s -X POST "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' \
  -d "{\"doc\":$BIG_DOC,\"islandId\":\"all-i\"}")
case "$big_summary" in *'"summaryText"'*'"groundingIds"'*) echo "  PASS: BIG ④島要約（200枚島・接地キャップ）"; PASS=$((PASS+1));; *) echo "  FAIL: BIG ④島要約（${big_summary:0:150}）"; FAIL=$((FAIL+1));; esac

# ⑤ ナラティブ（200枚規模で読み順を叙述）
big_narr=$(curl -s -X POST "$BASE_URL/ai/generate-narrative" -H 'Content-Type: application/json' -d "{\"doc\":$BIG_DOC}")
case "$big_narr" in *'"basedOnReadingOrder":["all-i"]'*) echo "  PASS: BIG ⑤ナラティブ（200枚規模）"; PASS=$((PASS+1));; *) echo "  FAIL: BIG ⑤ナラティブ（${big_narr:0:120}）"; FAIL=$((FAIL+1));; esac

# ⑥ A/B照合（200枚規模で島の取りこぼしを検出）
big_ab=$(curl -s -X POST "$BASE_URL/ai/check-narrative" -H 'Content-Type: application/json' \
  -d "{\"doc\":$BIG_DOC,\"narrativeText\":\"（草稿）200枚のカードを束ね、kj-atlasの改善を検討する。ただし新施策には未検証の主張が含まれる。\",\"basedOnReadingOrder\":[\"all-i\"]}")
case "$big_ab" in *'"direction":"a_missing_in_b"'*'"aMissingInB":1'*) echo "  PASS: BIG ⑥A/B照合（200枚規模・a_missing_in_b）"; PASS=$((PASS+1));; *) echo "  FAIL: BIG ⑥A/B照合（${big_ab:0:150}）"; FAIL=$((FAIL+1));; esac

echo ""
echo "=== Result: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ]
