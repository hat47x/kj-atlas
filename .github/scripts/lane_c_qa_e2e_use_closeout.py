from pathlib import Path

OLD = Path("01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md")
DONE = Path("01_Plans/issues/done/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md")
CONTRACT = Path("03_Implement/backend/tests/test_qa_e2e_doc_contract.py")

text = OLD.read_text(encoding="utf-8")
if "- Status: Open\n" not in text:
    raise SystemExit("expected current Status: Open")
if "## Final closeout（2026-09-07）" in text:
    raise SystemExit("closeout already present")

text = text.replace("- Status: Open\n", "- Status: Done\n", 1)
text = text.replace("- Open Readiness: Prepared\n- Execution: Ready\n", "", 1)
text = text.replace("- Owner: Stream H（QA P0 Hold解除準備）\n", "- Owner: Stream H（QA E2E）\n", 1)
text = text.rstrip() + """

## Final closeout（2026-09-07）

`QA-E2E-USE-01` の親スコープは、既存の実利用journey資産を現在の標準Compose経路で再検証し、再現可能な証跡をmainlineへ固定したため完了とする。前節までのDraft / Hold / Pending記述は各時点の判断履歴であり、closeoutに合わせて遡及的に書き換えない。

### 最終証跡

- mainline実装・runbook証跡: PR #3054 / commit `c84c1128a50da8e7d6bb7de0d6ba65095e69cd89`。
- GitHub Actions run `34065343063` で、標準Docker Compose（PostgreSQL + API + web）をclean stateから起動し、`/api/healthz` を確認した。
- ADR-0019の保存経路preflightは、固定seed文書の存在に依存せず、一意な合成DocumentV1を frontend proxy 経由で `PUT -> GET` し、payloadとETagの一致を確認した。
- frontend `typecheck` はgreen、full Vitestは **256/256 files・1634/1634 tests pass**。
- `realistic_user_journey_expansion.spec.ts` は同一Compose stackに対して **2/2 pass**。既存2 testで S1〜S3 と S4 を覆っているため、重複するjourney specは追加しなかった。
- planning/docs guardも同一検証treeでgreen。PR #3054では製品挙動・SafeMode契約・S1〜S4 spec自体を変更していない。

### 失敗履歴の扱い

直前run `34060045607` ではstorage roundtrip自体は成功した一方、検証用containerへfrontend subtreeだけをコピーしたため、repository-relativeなbackend / architecture / documentation fixtureがENOENTとなりfull Vitestが停止した。これはproduct defectやflakyとして再実行で握り潰さず、検証ハーネスのrepository layout欠陥として切り分けた。run `34065343063` ではrepository tree全体を保持して同じsuiteを再実行し、上記全件greenを確認した。

### Doneの境界

このDoneは **QA-E2E-USE-01が担当する実利用journeyのテスト資産・標準Compose実行証跡・traceability** の完了を表す。`PRODUCT-QA-01` 等のrelease decision、実利用者によるUX受入、release screenshot bundle、全製品面の品質保証、将来追加されるjourneyまでの網羅を意味しない。これらを本issueの完了条件へ後付けせず、別の品質・release gateの責務として維持する。
""" + "\n"

DONE.parent.mkdir(parents=True, exist_ok=True)
DONE.write_text(text, encoding="utf-8")
OLD.unlink()

contract = CONTRACT.read_text(encoding="utf-8")
old_ref = 'QA_ISSUE = ROOT / "01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md"'
new_ref = 'QA_ISSUE = ROOT / "01_Plans/issues/done/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md"'
if old_ref not in contract:
    raise SystemExit("expected QA_ISSUE active-root reference")
CONTRACT.write_text(contract.replace(old_ref, new_ref, 1), encoding="utf-8")

print(f"moved {OLD} -> {DONE}")
print(f"updated canonical contract reference in {CONTRACT}")
