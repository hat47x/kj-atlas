#!/usr/bin/env bash
# Dogfooding 記録の構造照合（別の生成AIが再現実行できる自己検証）
#
# DOGFOODING_MANIFEST.md の構造的主張（ファイル存在・数値・算術・課題状態）を
# リポジトリ実体と自動照合する。実行は高速で、バックエンド起動や E2E 実走行は
# 行わない（それらはマニフェスト §2 の検証ハーネスコマンドで再現実行する）。
#
# Usage: bash 01_Plans/dogfood/verify_dogfood_records.sh

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PASS=0
FAIL=0

check() {
  if [ "$2" = "$3" ]; then
    echo "  PASS: $1"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $1 (got '$2' expected '$3')"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== Dogfooding 記録の構造照合 ==="

# 1. 業務フローE2Eスクリプトのシナリオヘッダ数（マニフェスト主張: 84）
#    シナリオ1=初期フロー（ヘッダechoなし）・シナリオ4=別スクリプトのため、
#    総シナリオ86 とは一致しない（マニフェスト §1 に注記）。
EXPECT_HEADERS=84
ACTUAL_HEADERS=$(grep -c -e "--- シナリオ" "$ROOT/03_Implement/backend/scripts/verify_business_flow_e2e.sh")
check "業務フローE2E シナリオヘッダ数 == $EXPECT_HEADERS" "$ACTUAL_HEADERS" "$EXPECT_HEADERS"

# 2. シナリオドキュメントのカバレッジ集約ヘッダ（シナリオ86・チェック501）
if grep -q -e "シナリオ86・チェック501" "$ROOT/01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md"; then
  check "シナリオドキュメント カバレッジ集約 (シナリオ86・チェック501)" "ok" "ok"
else
  echo "  FAIL: シナリオドキュメント カバレッジ集約 (シナリオ86・チェック501)"
  FAIL=$((FAIL + 1))
fi

# 3. シナリオドキュメントの状態リストにシナリオ86 が含まれる
if grep -q -e "シナリオ86（iteration 156" "$ROOT/01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md"; then
  check "状態リストにシナリオ86 (iteration 156)" "ok" "ok"
else
  echo "  FAIL: 状態リストにシナリオ86 (iteration 156)"
  FAIL=$((FAIL + 1))
fi

# 4. 発行済み課題の存在と Status: Done
for issue in \
  "issue-AI-MODEL-GOVERNANCE-02-unregistered-model-rejected-under-platform-default.md" \
  "issue-OPS-LLM-COST-02-llm-call-counts-ui-visibility.md"; do
  if [ -f "$ROOT/01_Plans/issues/$issue" ] && grep -q "^\- Status: Done" "$ROOT/01_Plans/issues/$issue"; then
    check "課題 $issue" "Done" "Done"
  else
    echo "  FAIL: 課題 $issue (存在しない or Status != Done)"
    FAIL=$((FAIL + 1))
  fi
done

# 5. 主要な frontend ドッグフーディング E2E の存在
for spec in \
  ce4_island_summary_proposal \
  opposing_viewpoint_proposal \
  narrative_ab_check \
  review_pack_state_preservation \
  ai_provider_status \
  island_title_warning; do
  if [ -f "$ROOT/03_Implement/frontend/e2e/$spec.spec.ts" ]; then
    check "UI E2E $spec.spec.ts" "exists" "exists"
  else
    echo "  FAIL: UI E2E $spec.spec.ts"
    FAIL=$((FAIL + 1))
  fi
done

# 6. CIハーネス verify_all.sh の check 10 配線（3自己完結E2E）
for entry in \
  "verify_business_flow_e2e.sh" \
  "verify_admin_ops_flow_e2e.sh" \
  "verify_kj_multi_round.sh"; do
  if grep -q "$entry" "$ROOT/03_Implement/backend/verify_all.sh"; then
    check "check 10 配線: $entry" "wired" "wired"
  else
    echo "  FAIL: check 10 配線: $entry"
    FAIL=$((FAIL + 1))
  fi
done

# 7. 総チェック数の算術照合（マニフェスト主張: 543 = 501 + 12 + 7 + 8 + 15）
BUSINESS_CHECKS=501
ADMIN_CHECKS=12
MULTI_ROUND_CHECKS=7
MCP_CE4_CHECKS=8
CLI_CE4_CHECKS=15
TOTAL=$((BUSINESS_CHECKS + ADMIN_CHECKS + MULTI_ROUND_CHECKS + MCP_CE4_CHECKS + CLI_CE4_CHECKS))
check "総チェック算術 (501+12+7+8+15)" "$TOTAL" "543"

# 8. マニフェスト自身の存在
if [ -f "$SCRIPT_DIR/DOGFOODING_MANIFEST.md" ]; then
  check "DOGFOODING_MANIFEST.md" "exists" "exists"
else
  echo "  FAIL: DOGFOODING_MANIFEST.md"
  FAIL=$((FAIL + 1))
fi

echo ""
echo "=== Dogfooding 記録構造照合: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ]
