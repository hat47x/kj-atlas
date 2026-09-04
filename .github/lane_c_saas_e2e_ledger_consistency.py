from pathlib import Path

AUTH = Path("01_Plans/issues/issue-AUTH-ONE-TIME-JWT-01-request-token-supply-contract.md")
QA = Path("01_Plans/issues/issue-QA-E2E-SAAS-01-tenant-session-coverage-gap.md")

auth = AUTH.read_text(encoding="utf-8")
old = "- 比較判断の正本は`ADR-0074`へ集約した。同ADRはactive tenant正本化とtoken replay露出縮小を同じserver-owned session境界で解く案Bを採用候補としている。DPoPを別系統で並行実装せず、ADRがAcceptedになるまで現行Bearer保証を超えて表明しない。"
new = "- 比較判断は`ADR-0074`へ集約し、2026-08-13にAcceptedとなった。同ADRはactive tenant正本化とtoken replay露出縮小を同じserver-owned session境界で解く案B（server-owned BFF session）を採用した。DPoPを別系統で並行実装せず、BFF採択後もBearer access token自体へ未実装のreplay防御があるかのようには表明しない。"
if auth.count(old) != 1:
    raise RuntimeError(f"AUTH adoption paragraph match count: {auth.count(old)}")
auth = auth.replace(old, new, 1)
AUTH.write_text(auth, encoding="utf-8")

qa = QA.read_text(encoding="utf-8")
old = "- [ ] 実frontendと実backendを結ぶ縦断E2Eの担当Issueを明示し、本Issueの完了時に未検証領域を「E2E済み」と表明しない。"
new = "- [x] 実frontendと実backendを結ぶ縦断E2Eの担当Issueを`AUTH-ONE-TIME-JWT-01`として明示し、本Issueの完了時に未検証領域を「E2E済み」と表明しない。"
if qa.count(old) != 1:
    raise RuntimeError(f"QA ownership acceptance match count: {qa.count(old)}")
qa = qa.replace(old, new, 1)
QA.write_text(qa, encoding="utf-8")
