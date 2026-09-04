from pathlib import Path


def replace_exact(text: str, old: str, new: str, *, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def update_operations() -> None:
    path = Path("04_Documentation/operations.md")
    text = path.read_text(encoding="utf-8")
    start_marker = "### SaaSの複数プロセス構成"
    end_marker = "\n## 起動"
    start = text.index(start_marker)
    end = text.index(end_marker, start)

    replacement = """### SaaSの複数API instance構成

`saas-multitenant`では、BFFの認証session正本をPostgreSQLの`saas_auth_sessions`で共有します。各行は、server側でhash化した認証session識別子に対してprincipal、issuer、subject、active tenant、`tenantSessionVersion`、作成時刻、最終利用時刻、失効時刻を保持します。API instanceを増やしても同じPostgreSQLを参照するため、sticky sessionを正しさの前提にしてはいけません。

BFF Cookie経路では、次を運用上の前提とします。

- 同じ認証sessionを別のAPI instanceが処理しても、active tenantと`tenantSessionVersion`は同じ共有行から解決します。同じprincipalでも別login sessionは別行なので、一方のtenant切替やlogoutで他方を失効させません。
- tenant切替は期待した`tenantSessionVersion`とのCASで更新します。古いversionのrequestは409で拒否し、clientは新tenantへ自動再送せず、最新のsession contextを読み直してから利用者の操作として再試行します。
- logout、absolute expiry、idle expiryは共有DB上の認証sessionへ反映されるため、どのAPI instanceへ次requestが到達しても同じ失効状態を見ます。
- unsafe methodをBFF Cookieで認証する場合は、Origin / Host一致とsession-bound CSRF tokenを検証します。CSRF tokenやraw session IDをログへ出してはいけません。
- 共有認証表が未migration、または起動時にDBへ接続できない場合、SaaS APIは起動を拒否します。稼働中にDBを失った場合も、session解決やtenant切替をin-memory状態へfallbackせずfail-closedにします。
- JWKS cacheはinstanceごとで構いません。安全境界は共有しませんが、instance数に応じてBrokerへの取得回数が増えるため、取得失敗や集中が疑われる場合はBroker側の状態も確認します。

現行実装では、request処理用のDB sessionを保持している間に、認証session storeが別のDB sessionを開く経路があります。実PostgreSQLの複数app検証では、1 instanceあたり`pool_size=1`かつ`max_overflow=0`まで絞ると、共有sessionの解決前にconnection pool timeoutとなり503へfail-closedすることを確認しました。本番では「1 requestにつき常に1接続」と仮定せず、API replica数と同時request数に対して接続poolへ余力を持たせてください。pool timeoutが見えた場合は、DB停止だけでなくpool枯渇も切り分け対象です。

### SaaSのmigrationとrolling restart

更新は次の順で行います。

1. 新しいAPI revisionを起動する前にmigrationを適用し、`saas_auth_sessions`を含む必要schemaが揃っていることを`/readyz`で確認します。
2. rolling restart中の全API instanceで、同じ認証session hash keyを使います。keyが揃っていれば、新しく起動したinstanceも既存Cookieから同じ共有sessionを解決できます。
3. API instanceを一つずつ更新し、各instanceがreadyになってから次へ進みます。可能なら同じ認証sessionを旧instanceと新instanceの双方へ到達させ、active tenantとversionが一致することを確認します。
4. 認証session hash keyを変更すると、旧keyで発行されたCookieは新keyのinstanceでは別hashとなり、既存sessionを解決できません。現行実装は旧keyへのfallbackや推測を行わないため、key rotationは既存sessionの再loginを伴う計画変更として扱い、rolling restartの途中でinstanceごとに異なるkeyを混在させないでください。
5. `saas_auth_sessions`を削除するdowngradeは既存BFF sessionを維持できません。新しいschemaを必要とするinstanceが残っている間はdowngradeせず、rollback時はsession失効と再loginを利用者影響として明示します。

実PostgreSQLの回帰テスト`test_saas_auth_session_postgres_multi_instance.py`は、migrationのupgrade→downgrade→head再upgradeに加え、別engineを持つ複数FastAPI appから同じsessionを処理し、tenant/version共有、stale CAS拒否、別login非干渉、logout失効、idle expiry、再起動後の継続、hash key変更時のfail-closedを確認します。

### SaaS session障害時の初動

- `session_context_unavailable`や503が増えた場合は、まず`/readyz`、PostgreSQL到達性、connection pool timeoutを確認します。DBやpoolの問題をin-memory fallbackで隠さないでください。
- `tenant_session_changed`（409）はstale requestです。最新contextを再取得し、利用者の操作なしにtenant切替requestを別tenantへ自動再送しません。
- `session_invalid`（401）がkey rotationやdeployment直後に増えた場合は、API instance間でsession hash keyが一致しているかを確認します。意図したrotationなら再loginを案内します。
- logout・expiry・revocation後のsessionを復活させるためにDB行を書き戻したり、別sessionの状態を流用したりしません。
- 障害調査ではraw auth-session Cookie、CSRF token、Bearer token、server keyをログ・Issue・Documentへ転記しません。
"""
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


def update_ops_issue() -> None:
    path = Path("01_Plans/issues/issue-OPS-SAAS-SCALE-01-in-process-state-blocks-horizontal-scaling.md")
    text = path.read_text(encoding="utf-8")
    text = replace_exact(text, "- Status: Open", "- Status: In Progress", label="OPS status")

    start = text.index("## 現在の課題")
    end = text.index("\n## Bearer replay防御との境界", start)
    current = """## 現在の課題

当初はtenant session versionがprocess内にあり、その後のPostgreSQL共有化も`principal_id`単位のversion共有に留まっていた。`SAAS-TENANT-SESSION-BINDING-01`とADR-0074の実装により、現在のBFF Cookie経路では`saas_auth_sessions`が認証session単位の正本となり、active tenant、`tenantSessionVersion`、期限、失効を同一行で扱う。

2026-09-04の再監査では、従来の「2 worker」証拠が同一SQLite DBへ向けた2つのstore objectであり、本issueのAC-7が明示する実PostgreSQL・複数app HTTP境界を満たしていないことが分かった。そこで隔離PostgreSQLへ実migrationを適用し、別々のSQLAlchemy engineを持つ複数FastAPI appから同じBFF sessionをHTTPで処理する回帰テストを追加した。

この実証により、session正本の水平共有そのものは確認できた。残る主な課題は、DB切断時にtenant-scoped resource lookupより前で確実に停止することと、clientが失敗したtenant切替を別tenantへ自動再送しないことを一続きの障害テストで固定する点である。

また、実証用engineを`pool_size=1 / max_overflow=0`へ絞ると、request用DB sessionを保持したまま認証session storeが別sessionを開く現行経路でpool timeoutとなることも観測した。これは共有正本の誤りではないが、水平スケール時の接続pool設計に必要な運用条件として`operations.md`へ反映する。
"""
    text = text[:start] + current + text[end:]

    old_acceptance = """- [ ] AC-4: `ADR-0074`で採択された認証session正本を最低2 worker／2 app instanceが共有し、active tenant、version、期限、失効を一貫して解決する。
- [ ] AC-5: 同一sessionの複数tabはworkerをまたいでもversionを共有し、同じprincipalの別sessionは切替・logout・idle expiryで相互干渉しない。
- [ ] AC-6: DB切断、CAS競合、rolling restart、key rotation中に旧tenant requestをresource lookup前に拒否し、新tenantへ自動再送しない。
- [ ] AC-7: migration upgrade/downgradeと、最低2 workerのHTTP integration testをCIで固定する。単に2つのrepository objectを同じSQLite DBへ向けるtestで代替しない。
- [ ] AC-8: `04_Documentation/operations.md`にdeployment topology、migration順序、rolling restart、session失効、障害時runbookを記載する。"""
    new_acceptance = """- [x] AC-4: `ADR-0074`で採択された認証session正本を最低2 worker／2 app instanceが共有し、active tenant、version、期限、失効を一貫して解決する。
  - 2026-09-04: `test_saas_auth_session_postgres_multi_instance.py`で、別engineを持つ2 FastAPI appが同じPostgreSQL上のBFF sessionをHTTPで共有し、tenant/version、logout失効、idle expiryを同じ正本から解決することを確認した。
- [x] AC-5: 同一sessionの複数tabはworkerをまたいでもversionを共有し、同じprincipalの別sessionは切替・logout・idle expiryで相互干渉しない。
  - 2026-09-04: app Aで切り替えたversionをapp Bが直後に観測し、app Bから旧versionを送ると409となること、同一principalの別loginはtenant/versionを維持し、一方のlogout後も継続することを確認した。
- [ ] AC-6: DB切断、CAS競合、rolling restart、key rotation中に旧tenant requestをresource lookup前に拒否し、新tenantへ自動再送しない。
  - 2026-09-04進捗: CAS競合、別engineで作り直したappへのrolling restart相当、hash key変更時の401 fail-closedは実PostgreSQLで確認済み。DB切断をtenant-scoped resource lookupと組み合わせたHTTP障害テスト、およびclient側の非自動再送の一続きの証拠が残る。
- [x] AC-7: migration upgrade/downgradeと、最低2 workerのHTTP integration testをCIで固定する。単に2つのrepository objectを同じSQLite DBへ向けるtestで代替しない。
  - 2026-09-04: committed PostgreSQL testで`20260813_0027`へのupgrade、`0026`へのdowngrade、`head`への再upgradeと複数app HTTP matrixを固定し、branch-only GitHub Actions Run `33864904968`（PostgreSQL 16）で成功を確認した。常設workflowを置かないrepository運用とは分離し、テスト本体をCIから再利用できる形で保持する。
- [x] AC-8: `04_Documentation/operations.md`にdeployment topology、migration順序、rolling restart、session失効、障害時runbookを記載する。
  - 2026-09-04: PostgreSQL共有session正本、sticky session非依存、migration/rollback順序、hash key rotation、DB/pool障害、409/401/503時の初動を現行実装へ同期した。"""
    text = replace_exact(text, old_acceptance, new_acceptance, label="OPS acceptance block")

    old_verify = """- PostgreSQL、最低2 API worker、同一session／別sessionのHTTP matrix
- migration upgrade → downgrade → upgrade"""
    new_verify = """- `KJ_ATLAS_RUN_PG_TESTS=1 KJ_ATLAS_TEST_POSTGRES_CONTAINER=<container> KJ_ATLAS_DATABASE_URL=<postgresql-url> python -m pytest -m postgres tests/test_saas_auth_session_postgres_multi_instance.py -q`
- PostgreSQL 16 branch-only GitHub Actions Run `33864904968`: 上記実証 `1 passed`、関連session/CSRF回帰 `50 passed`
- migration `20260813_0027` upgrade → `20260813_0026` downgrade → `head` upgradeを同じ隔離DBで確認"""
    text = replace_exact(text, old_verify, new_verify, label="OPS verification block")

    history = "- 共有化後の再監査で、principal単位version共有と認証session単位のactive tenant正本は別要件だと判明したため、本issueを後者の複数worker運用検証へ再基準化した。"
    history_with_d4 = history + "\n- D4: 2026-09-04、SQLite上の2 store objectをcluster-level証拠とは扱わず、実PostgreSQL＋複数FastAPI appのHTTP実証へ置き換えた。実証中に観測したconnection pool余力も水平スケールの運用条件として記録した。"
    text = replace_exact(text, history, history_with_d4, label="OPS history")
    path.write_text(text, encoding="utf-8")


def update_done_issue_evidence() -> None:
    path = Path("01_Plans/issues/done/issue-SAAS-TENANT-SESSION-BINDING-01-principal-keyed-session-state.md")
    text = path.read_text(encoding="utf-8")
    anchor = "  — 2026-08-22。4項目とも既存・新規のtestで個別に確認済み（単一の統合テストではなく、各項目を最も直接に検証するテストへ分担）: migration upgrade/downgradeは`test_saas_auth_sessions_migration.py`（2026-08-13）、複数worker CASは本checkpointで追加した`test_two_worker_instances_share_and_atomically_rotate_active_tenant`、tenant切替→次requestは`test_session_context_routes.py`のAC-3/4統合テスト、別session分離は`test_rotate_active_tenant_on_one_session_does_not_affect_another_of_the_same_principal`と`test_oauth_bff_logout_revocation.py`。"
    note = anchor + "\n  - 2026-09-04補足: 上記の「複数worker CAS」は同一SQLite DBへ向けた2 store objectによるcomponent-level確認であり、実PostgreSQL上のcluster-level証拠とは扱わない。後者は`OPS-SAAS-SCALE-01`の`test_saas_auth_session_postgres_multi_instance.py`で別engineの複数FastAPI appを使って確認する。"
    path.write_text(replace_exact(text, anchor, note, label="Done issue AC-7 evidence"), encoding="utf-8")


if __name__ == "__main__":
    update_operations()
    update_ops_issue()
    update_done_issue_evidence()
