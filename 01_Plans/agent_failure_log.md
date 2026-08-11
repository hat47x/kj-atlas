# AIエージェント失敗事例ログ

区分: Internal / Log（`agent_failure_lessons.md` の実記録）

Updated: 2026-08-03

## 2026-08-06: WSL backend pytest runner unavailable

- 事象: `python3 -m pytest` で Inquiry bundle backend tests の実行を試みたが、`No module named pytest` で開始できなかった。
- 原因: 現在利用可能な WSL Python 環境に backend の test extra が導入されていない。Windows 側の Python launcher も実体環境を提供していない。
- 対応: `~/kj-backend-venv` の既存仮想環境を発見し、そこで対象テストを実行する経路へ切り替えた。
- 再発防止: backend の検証開始前に `python3 -m pytest --version` と既存仮想環境を確認し、依存がなければ未実行として明記する。

## 2026-08-06: 新migration追加後のAlembic head固定テスト失敗

- 事象: Inquiry bundle migration追加後、`test_alembic_has_single_head` が旧head `20260720_0013` を期待して失敗した。
- 原因: migration graphは線形のまま新headへ進んだが、テストの固定期待値を追随していなかった。
- 対応: 期待headを `20260806_0014` へ更新して対象テストを再実行する。
- 再発防止: 新migration追加時はAlembic lineage testのhead期待値を同じ変更単位で確認する。

## 2026-08-06: 新規repository testのruff未使用import

- 事象: Inquiry bundle repository testに `Session` の未使用importがあり、ruffが失敗した。
- 原因: test fixtureの型注釈を簡略化した後にimportだけが残った。
- 対応: 未使用importを削除し、対象ファイルのruffを再実行する。
- 再発防止: テスト追加後は対象Pythonファイルにruffを実行する。

記録形式・対象・参照タイミングは `01_Plans/agent_failure_lessons.md` を参照。末尾へ追記する。

## 2026-08-03: CI trailing whitespace check が複数回失敗（CRLF行末混入）

- 事象: `git diff --check` が、コミットしたPython/TypeScriptファイルの「追加行」に trailing whitespace があるとしてCIが失敗。`models_context.py`・`test_context_bundle_routes.py`・`issue-DOMAIN-EXPR-01` の3回発生。
- 原因: WSL上の作業でCRLF→LF変換が走る際、行末に空白が残った。日本語長文のissue更新時は、編集ツール由来の行末空白が入りやすい。
- 対応: `sed -i 's/[[:space:]]*$//'` で該当ファイルの末尾空白を一括除去し、`git diff -U0 | grep '^+'` で追加行だけを検査してからコミット。
- 再発防止: コミット前に必ず `git diff --check`（または追加行のみの末尾空白grep）を実行する。日本語長文の編集後は特に行末を確認する。

## 2026-08-02: esbuild version mismatch で vitest が起動不能

- 事象: `vitest run` が `Cannot start service: Host version "0.28.1" does not match binary version "0.21.5"` で起動失敗。i18nテスト・対象モジュールテストが実行不能になった。
- 原因: pnpm移行がrevert（`DX-CI-PNPM-01`）された後に残った `.pnpm/` 配下の古い `esbuild@0.28.1` エントリと、アクティブな `esbuild@0.21.5` の混在。`.pnpm/esbuild@0.28.1` のバイナリが欠落していた。
- 対応: `rm -rf node_modules/.pnpm/esbuild@0.28.1 node_modules/.pnpm/@esbuild+win32-x64@0.28.1` で古いエントリを除去 → vitest正常起動（233 files / 1372 tests pass）。
- 再発防止: esbuild系の起動エラーはまず `.pnpm/` 配下のバージョン重複を確認する。pnpm関連ファイルがrevertされた後のnode_modules操作には注意する。
- **再発（2026-08-03）**: 同じ `.pnpm/esbuild@0.28.1` が再生成されており再発。pnpm installが走るたびに0.28.1が復活する可能性が高い。除去コマンドはその場で再実行する。根本解決は `node_modules` をクリーンに再構築するか、pnpm移行を正式に完了するか、`.pnpm` 配下のesbuildを0.21に固定する運用の検討が必要。
- **根本原因の特定（2026-08-07）**: `node_modules` が npm/pnpm混在状態（`.pnpm/` 74エントリ + `.modules.yaml`）であることを確認。`issue-DX-ENV-01-mixed-npm-pnpm-node-modules-state.md` として起票し、クリーン再構築を推奨。
- **ビルドも壊れる（2026-08-07）**: stale `.pnpm/rollup@4.62.3` が `vite build` を `Source phase import "vite/modulepreload-polyfill" must be external` で失敗させる。`rm -rf node_modules/.pnpm/rollup@4.62.3 ...` で解消。混在node_modulesはesbuild（vitest）だけでなくrollup（vite build）も壊すため、`vite build` 実行前に `.pnpm/` 配下のrollup/esbuild重複を確認する。

## 2026-08-02: 作業ディレクトリ依存のgit pathspecエラー

- 事象: `git add 03_Implement/frontend/...` が `warning: could not open directory '03_Implement/frontend/03_Implement/frontend/'` で失敗。作業ディレクトリが `03_Implement/frontend/` にある状態でリポジトリルート基準のパスを渡した。
- 原因: 前のコマンドで `cd` したディレクトリが残っており、相対パスが二重化した。
- 対応: `git -C /mnt/d/GIT/kj-atlas` でリポジトリルートを明示するか、ルート基準の相対パスを使う。
- 再発防止: git操作は `git -C /mnt/d/GIT/kj-atlas` 形式で統一する。cd後の相対パスgitコマンドは避ける。

## 2026-07-30: 手動マージ後のtest-results/ が未追跡で残る

- 事象: Playwright実行の `test-results/` ディレクトリがuntrackedとして残り、毎回 `git status` を汚した。
- 原因: `.gitignore` に `**/test-results/` が無かった。
- 対応: `.gitignore` に `**/test-results/` を追加（`.claude/worktrees/` も同時に追加）。
- 再発防止: 実行成果物（テスト結果、キャッシュ、一時ファイル）は生成時に.gitignoreへ追加する。

## 2026-07-20: roundブランチのマージでindex.lock残存による失敗

- 事象: `git merge` が `Unable to write index` で失敗し、`index.lock` が残って後続のgit操作が全て失敗した。
- 原因: 並行プロセス（別エージェントのgit操作）との競合、または中断されたマージの残骸。
- 対応: `rm -f .git/index.lock` でロックを除去してから再試行。マージ中は連続で複数ブランチをマージしない。
- 再発防止: git操作が `Unable to write index` / `index.lock` で失敗したら、まずロックファイルを確認・除去する。複数ブランチの連続マージは1つずつ確認しながら進める。

## 2026-08-06: 削除対象コードを `src/` だけで検索して統合テストの参照を見落とした

- 事象: `deterministic_tiebreak_worker_adapter.ts` を「未使用」と判定して削除。実際は `tests/tiebreak/deterministic_tie_break.integration.test.ts` が参照しており、`npx vitest run --config tests/tiebreak/vitest.config.tiebreak.ts` が壊れるところだった。
- 原因: デッドコード判定のgrepを `src/` 配下に限定した。このadapterは `tests/tiebreak/vitest.config.tiebreak.ts`（`include: ["tests/tiebreak/**/*.test.ts"]` の別設定）で実行される統合テストだけが参照しており、通常の `vitest run` には現れなかった。作業ツリー上に残っていた別worktreeのテストが検出の手掛かりになった。
- 対応: `git show 62dca731~1:<path>` から復元し、`tests/tiebreak/vitest.config.tiebreak.ts` で3 tests passを確認。DX-CLEANUP-08（番号衝突のため08へ再番号、旧07）を「参照源がsrc外に偏在」の検討対象として訂正した。
- 再発防止: 「削除対象か」の判定は **`src/` だけでなく `tests/`・`e2e/`・別vitest設定・build設定を含めたリポジトリ全体** で参照を検索する。特に `vitest.config.*.ts` が複数ある場合は、別設定のテストがどのファイルを include するかを確認してから削除判断する。コミット前に `git grep` をリポジトリルート基準で実行する。

## 2026-08-09: Active issue validatorの配置場所を取り違えた

- 事象: `python 01_Plans/validate_active_issue_memos.py`を実行し、ファイル未存在で検証が開始しなかった。
- 原因: validatorが`01_Plans/issues/`配下にあることを確認せず、記憶したパスを使用した。
- 対応: `rg --files`で実体を確認し、`python 01_Plans/issues/validate_active_issue_memos.py`で再実行する。
- 再発防止: リポジトリ内スクリプトは実行前に`rg --files`で現在の配置を確認する。

## 2026-08-09: Python 3.10で`StrEnum`を使用して新規テスト収集に失敗

- 事象: 永続列分類テストが`ImportError: cannot import name 'StrEnum'`で収集失敗した。初回実行ではpytestのcapture一時ファイル消失も重なり、原因が表示されなかった。
- 原因: 開発時にPython 3.11追加の`enum.StrEnum`を選び、backendのPython 3.10互換性を確認していなかった。
- 対応: `class DataShape(str, Enum)`へ変更し、captureを無効化して再実行して3件passを確認した。
- 再発防止: backendの新規標準ライブラリAPIはPython 3.10で利用可能か確認し、不可なら互換表現を使う。pytest capture自体が失敗した場合は`-s`で本来の収集エラーを確認する。

## 2026-08-09: migrationテストがPATH上の`alembic`を見つけられなかった

- 事象: 新規migrationテスト2件が`FileNotFoundError: alembic`で停止した。
- 原因: pytestをvenvのPythonで起動しても、subprocessのPATHへvenvの`bin`が追加されるとは限らないのに、bare command名へ依存した。
- 対応: subprocessを`sys.executable -m alembic`で起動し、pytestと同じPython環境を使うよう変更した。
- 再発防止: Python CLIをテストから起動するときはbare commandでなく`sys.executable -m <module>`を優先する。

## 2026-08-09: benchmark一時directoryの即時削除が安全制約で拒否された

- 事象: 世代圧縮benchmarkの末尾に一時directory削除を含めたため、コマンド全体が実行前に拒否された。
- 原因: `mktemp`で対象を限定していても、実行環境の破壊操作制約に反する削除を同一コマンドへ含めた。
- 対応: 削除操作を外し、OS管理の一時directoryへ生成して計測だけを実行した。
- 再発防止: 一時benchmarkは削除をコマンドへ含めず、OSの一時領域回収へ委ねる。

## 2026-08-10: delta復元negative testがfull snapshotを選択した

- 事象: wrong-base拒否テストが例外を発生させず失敗した。
- 原因: 単一文字の反復データはfull gzipが極端に小さくなり、codecが意図通りfull snapshotを選んだ。
- 対応: 複数カードの局所変更fixtureへ置換し、delta選択を明示assertしてからnegative pathを検証した。
- 再発防止: adaptive codecの分岐テストではrepresentation選択も前提条件としてassertする。

## 2026-08-10: pytest capture一時ファイル消失でテスト開始前に停止

- 事象: AI生成lineageの対象テスト実行が、pytest終了処理の`FileNotFoundError`で停止し、テストは未実行だった。
- 原因: 実行環境上でpytestのcapture用一時ファイルが途中で消失した。実装コード起因の失敗ではない。
- 対応: captureを無効化する`-s`を付け、同一テスト群を再実行する。
- 再発防止: この環境でcaptureの一時ファイル消失が再発した場合は、初回から`-s`を使用して本来の結果を取得する。

## 2026-08-10: backendテストをシステムPythonで起動して収集失敗

- 事象: capture無効化後の対象テストが`sqlalchemy`および`alembic.config`不足で収集失敗した。
- 原因: PATH上のpytestがシステムPythonを使用し、backendの`.venv`を使用していなかった。
- 対応: `03_Implement/backend/.venv/bin/python -m pytest`で再実行する。
- 再発防止: backendのPython検証は仮想環境のPythonを明示して起動する。

## 2026-08-10: AI lineageテストfixtureの親子insert順序が未確定

- 事象: SQLiteで外部キーを有効化した新規テスト2件が、tenantとcontent blobの同一flush時に外部キー違反となった。
- 原因: ORM relationshipを持たないfixtureで親子rowを同一flushへ積み、tenantのinsert完了を明示していなかった。
- 対応: tenantを先にcommitし、その後documentとblobを登録する順序へ変更した。
- 再発防止: relationshipなしの外部キーfixtureでは、親レコードをflushまたはcommitしてから子を追加する。

## 2026-08-10: issue validatorで仮想環境の相対pathを誤指定

- 事象: Ruff成功後、repository rootから`.venv/bin/python`を指定したためissue validatorだけが起動しなかった。
- 原因: backend配下の仮想環境pathを、作業directory変更後も同じ相対pathで参照した。
- 対応: `03_Implement/backend/.venv/bin/python`をrepository rootから明示して再実行する。
- 再発防止: 複数directoryを跨ぐ検証では実行前に仮想環境pathを基準directoryに合わせる。

## 2026-08-10: 並行作業の未完成issueが全体memo検証を停止

- 事象: active issue memo全体検証が、今回の対象外である新規`issue-DOMAIN-TITLE-01`の必須項目不足を検出して停止した。
- 原因: validatorは作業ツリー内の全active memoを対象とし、並行作業中の未完成ファイルも検査する。
- 対応: 対象外ファイルは変更せず、同じvalidator関数で`issue-DATA-GENERATION-01`だけを個別検証する。
- 再発防止: 並行作業がある場合は全体検証の失敗対象を確認し、対象issueの個別検証を併記する。

## 2026-08-10: GC監査テストがautoflush無効sessionで未flush rowを検索

- 事象: revision削除成功後の監査行確認が`None`となり、対象テスト1件が失敗した。
- 原因: repositoryは監査rowをsessionへ追加していたが、既存fixtureは`autoflush=False`であり、`Session.get`前にINSERTされていなかった。
- 対応: repositoryのcommit責務は変更せず、永続化を確認するテスト側で明示的にflushする。
- 再発防止: `autoflush=False`のrepositoryテストでは、追加rowをqueryする前にflushする。

## 2026-08-10: backend内からmigrationのrepository相対pathを重複指定

- 事象: 最終回帰コマンドが先頭の`chmod`で対象なしとなり、テスト開始前に停止した。
- 原因: working directoryが既に`03_Implement/backend`であるのに、同じprefixをpathへ再度付けた。
- 対応: backend基準の`alembic/versions/...`へ修正して同じ検証を再実行する。
- 再発防止: 長い検証コマンドではworking directoryと最初の対象pathを実行前に照合する。

## 2026-08-10: backend基準の検査でrepository prefix重複を再発

- 事象: reachability保持テスト追加後の確認が、先頭の`sed`対象なしで停止した。
- 原因: working directoryをbackendへ指定しながら、repository root基準pathを再度使用した。
- 対応: この作業単位の以後の検証pathをbackend基準へ統一する。
- 再発防止: working directoryを固定した連続検証では、コマンド内pathの基準を混在させない。

## 2026-08-10: reachability保持テストでSQLAlchemy select importを欠落

- 事象: Ruffが新規テスト内2箇所の`select`を未定義として検出した。
- 原因: query assertion追加時に既存importへ`select`を追加していなかった。
- 対応: `sqlalchemy.select`を明示importした。
- 再発防止: 新しいquery構築APIをテストへ追加した直後に対象ファイルのRuffを実行する。

## 2026-08-10: reachability GCがSQLite FK cascade無効時に祖先削除を停止

- 事象: branch保持テストで新しい側の候補を削除後、残存parent edgeが古い候補を保護し`GenerationGcConflict`となった。
- 原因: candidate revision削除時の親edge除去をDBの`ON DELETE CASCADE`だけに依存し、テスト接続ではSQLite外部キー処理が無効だった。
- 対応: retention pruning transaction内でcandidate自身の親edgeを明示削除してからrevisionを条件付き削除する。
- 再発防止: GCの進行順序に必要なcleanupは、接続別のcascade有効化だけへ依存させない。

## 2026-08-10: tenant-key migrationテストがbare Alembicへ依存

- 事象: portable text migration回帰のうち既存tenant-key migrationテスト2件が`FileNotFoundError: alembic`で停止した。他7件は通過した。
- 原因: 同テストだけが`sys.executable -m alembic`ではなくPATH上のbare commandを起動していた。
- 対応: pytestと同じ仮想環境のPython moduleとしてAlembicを起動するよう統一した。
- 再発防止: migration subprocessはPATH上のconsole scriptへ依存せず、`sys.executable -m alembic`を使う。

## 2026-08-10: MySQL 8.4 fresh migrationがlower式indexで停止

- 事象: 検証専用にcandidate guardを迂回したMySQL 8.4 fresh migrationがrevision 0005でSQL構文エラーとなった。
- 原因: SQLite/PostgreSQL向けの`CREATE UNIQUE INDEX ... (lower(provider), lower(external_uid))`形式をMySQLへそのまま発行した。
- 対応: MySQL familyでは対象列を明示的なcase-insensitive collationにし、既存のraw composite unique constraintで同じ一意性を担保して式indexを省略する。
- 再発防止: expression indexはmigration strategyの方言matrixで実DB検証し、共通DDLと仮定しない。

## 2026-08-10: SQLite batch型変更が式unique indexを消失

- 事象: portable text migration後のSQLite schemaからcase-insensitive identity unique indexが消え、既存migrationテストが失敗した。
- 原因: SQLiteのtable rebuild時にAlembic reflectionが式indexを復元できなかった。
- 対応: 0020のupgrade／downgrade双方で既知の式index存在を確認し、欠落時に明示再作成する。
- 再発防止: SQLite batch migration後は列型だけでなく、unique／expression indexの実schemaも回帰確認する。

## 2026-08-10: MySQL identity provider複合uniqueが最大key byte数を超過

- 事象: MySQL 8.4 fresh migrationがrevision 0006の`issuer + audience` unique constraintで3072-byte上限を超えて停止した。
- 原因: URI一般上限2048とaudience 512を、そのままutf8mb4複合索引列へ適用していた。
- 対応: OIDC lookup契約をissuer 512、audience 255、非索引JWKS URI 2048へ分離し、API境界でも同じ上限を拒否する。
- 再発防止: 複合index列は文字数だけでなく対象charsetの最大byte数合計を実DB gateで検証する。

## 2026-08-10: MySQLがdefault付きTEXT追加列を拒否

- 事象: MySQL 8.4 fresh migrationがrevision 0006の`documents.tenant_id TEXT NOT NULL DEFAULT`で停止した。
- 原因: portable create-table hookは`op.add_column`へ作用せず、履歴migrationの追加identifier列がTEXTのままだった。
- 対応: 過去migration内の全`add_column(Text)`を棚卸しし、tenant/internal ID 128、external subject 512、state 32、URI 2048の分類済みString型へ修正した。
- 再発防止: fresh migrationのportable型検査はcreate tableとadd/alter columnを別々に実DBで通す。

## 2026-08-10: tenant document key migrationがMySQL strategy未登録で停止

- 事象: MySQL fresh migrationはrevision 0007まで進んだ後、0008の明示的なunsupported dialect guardで停止した。
- 原因: 0008はSQLite rebuildとPostgreSQL named-constraint DDLだけを許可し、同じnamed-constraint操作が可能なMySQL familyを未検証のまま除外していた。
- 対応: PostgreSQL固有ではない処理をconstraint-DDL strategyへ改名し、MySQL/MariaDB familyを同じ経路へ追加して実DBで継続検証する。
- 再発防止: migration分岐はbackend名の列挙より、実際に必要なmigration strategy単位で共有する。

## 2026-08-10: MySQL inspectorが主キーconstraint名を返さず停止

- 事象: 0008をconstraint-DDL経路へ追加後、主キー名必須検査でMySQL migrationが停止した。
- 原因: MySQL inspectorのprimary key nameは`None`だが、DDL上は予約名`PRIMARY`でdropする仕様差を未吸収だった。
- 対応: MySQL/MariaDB familyだけ欠落名を`PRIMARY`へ正規化し、PostgreSQLのnamed constraint検査は維持する。
- 再発防止: constraint reflectionの名前有無も実DB family matrixの検証項目に含める。

## 2026-08-10: portable text downgradeがMySQL索引列をTEXTへ戻して停止

- 事象: MySQL headから0007へのdowngradeが0020で`ai_run_id TEXT`への変更を拒否され停止した。
- 原因: MySQL fresh schemaは履歴DDL hookにより0019時点でもbounded型だが、SQLite/PostgreSQL既存DB向けのTEXT復元を一律実行した。
- 対応: MySQL/MariaDBでは0020 downgradeを物理no-opとし、履歴上の0019 portable schemaを維持する。
- 再発防止: downgradeの目標物理schemaは、各familyのfresh migrationで実際に生成される直前revisionと照合する。

## 2026-08-10: MySQL downgradeが外部キー利用中indexの明示dropを拒否

- 事象: 0019 downgradeでtenant外部キーが利用する複合indexをtableより先にdropしようとしてMySQLが停止した。
- 原因: 直後にtableをdropするにもかかわらず、Alembic生成形の明示index dropを残していた。MySQLは外部キー補助indexとして利用中のため単独dropを拒否する。
- 対応: table削除直前の冗長なindex dropを関連6 migrationから除去し、table dropによるindex自動削除へ統一した。
- 再発防止: downgrade順序はindex、foreign key、tableの依存を実DBで確認し、tableと同時消滅するindexを先行dropしない。

## 2026-08-10: MySQLがIdP外部キー補助に利用中のunique削除を拒否

- 事象: 0014 downgradeで`tenant_identity_providers(identity_provider_id, external_tenant_ref)` uniqueをdropできなかった。
- 原因: MySQLがuniqueを`identity_provider_id`外部キーの補助indexとして選び、代替indexが存在しなかった。
- 対応: downgrade前に単列補助indexを作り、re-upgradeでuniqueを復元した後に補助indexを除去する対称処理を追加した。
- 再発防止: MySQLのconstraint downgradeでは、明示DDLだけでなくDBが選択した外部キー補助index依存も検証する。

## 2026-08-10: membership user index downgradeがMySQL外部キー依存で停止

- 事象: 0013 downgradeで`tenant_memberships.user_id` indexをdropできなかった。
- 原因: MySQLが同indexをusers外部キーの補助として利用しており、0012相当の代替indexがなかった。
- 対応: downgrade時だけ保持用単列indexへ切り替え、re-upgradeで正規indexを復元後に保持用indexを除去する。
- 再発防止: index追加migrationのroundtripでは、MySQLが外部キー補助へ採用した場合の対称操作も検証する。

## 2026-08-10: MySQL TEXTが1 MiB inline content roundtripを拒否

- 事象: head migration後のMySQL 8.4へ1 MiB超の`documents.payload_json`を保存すると`Data too long`となった。
- 原因: SQLAlchemyの汎用TextがMySQLでは最大約64 KiBのTEXTへコンパイルされ、content object要件に不足した。
- 対応: content object 3列だけをMySQL/MariaDBではLONGTEXTへ写像し、SQLite/PostgreSQLでは無制限Textを維持するvariantと履歴DDL hookを追加した。
- 再発防止: inline LOB promotion gateに1 MiB超の実roundtripを含め、単なるText型コンパイル成功で対応判定しない。

## 2026-08-10: pytestの出力キャプチャ一時fileが消失

- 事象: SQLite回帰suiteのcollection中にpytestのキャプチャ用一時fileが消失し、testを1件も実行せず`FileNotFoundError`で終了した。
- 原因: test対象の失敗ではなく、実行環境のpytest global captureと一時directoryの競合と判定した。
- 対応: `-s`でglobal captureを無効化し、同一suiteを再実行する。
- 再発防止: 並行agent環境で同事象が出た場合は、test変更前にcapture無効化で環境要因を切り分ける。

## 2026-08-10: PostgreSQLのtenant backfillでparameter型推論が衝突

- 事象: PostgreSQL fresh migrationのrevision 0006で、tenant membership backfillが`text versus character varying`の`AmbiguousParameter`で停止した。
- 原因: `tenant_id`の物理型を`VARCHAR(128)`へ変更した一方、同じbind parameterを過去の`TEXT`列と新規`VARCHAR`列で比較するraw SQLに型指定がなかった。
- 対応: migrationの`tenant_id` bind parameterを`String(128)`と明示した。
- 再発防止: 歴史migrationの列型をDDL hookで変換する場合、同一parameterを異なる物理型に使うbackfillもfresh PostgreSQLで検証する。

## 2026-08-10: PostgreSQL RLS policyが列型変更を防止

- 事象: portable text revision 0020で`tenant_id`を`VARCHAR`へ変更する際、同列を参照するRLS policy依存によりPostgreSQLがDDLを拒否した。
- 原因: indexとforeign keyのみをmigration依存として考慮し、PostgreSQL policy expressionの列依存を考慮していなかった。
- 対応: 0020が対象tableのpolicy定義を`pg_policies`から保存し、型変更中だけ解除した後に同一定義を復元するようにした。
- 再発防止: PostgreSQLの列型migrationはRLS policyの保存とfresh・downgrade・re-upgradeの実DB検証を必須とする。

## 2026-08-10: Alembicがpercent-encoded DB URLを設定展開と誤認

- 事象: SQL Server検証の記号入りpasswordをpercent-encodeしたURLで、Alembicがengine生成前に`invalid interpolation syntax`で停止した。
- 原因: Alembicの`set_main_option`がConfigParserのpercent interpolationを使うのに、URLの`%`をescapeせず設定していた。
- 対応: 正規化後URLをAlembic設定に入れる直前だけ`%`を`%%`へescapeし、SQLAlchemyが受け取る値は元のURLに戻るようにした。
- 再発防止: migration testにpercent-encoded passwordを含むURLのAlembic設定契約を追加する。

## 2026-08-10: identity duplicate probeのLIMITがSQL Serverで停止

- 事象: SQL Server 2022 fresh migrationのrevision 0005で、case-insensitive duplicate検査の`LIMIT 1`が構文エラーになった。
- 原因: migrationの読取queryを汎用SQLAlchemy式ではなくSQLite/PostgreSQL/MySQL系のraw SQLで書いていた。
- 対応: duplicate probeをSQLAlchemy Coreの`select().group_by().having().limit()`へ変更し、dialectに`TOP`または`LIMIT`をコンパイルさせる。SQL ServerではDBのCI collation付き元unique制約を利用する。
- 再発防止: migration内の一般DMLはrawな件数制限構文を避け、SQLAlchemy Core式を優先する。

## 2026-08-10: SQL ServerがON DELETE RESTRICTを拒否

- 事象: SQL Server 2022 fresh migrationのrevision 0007で、foreign keyの`ON DELETE RESTRICT`が構文エラーになった。
- 原因: SQL Serverは同じ参照中削除拒否の意味に`NO ACTION`を使い、`RESTRICT`キーワードを受理しない。
- 対応: 非遅延foreign keyで同じ振る舞いになる`NO ACTION`へORMとmigrationを統一した。
- 再発防止: 参照中削除拒否の共通DDLは、全verified/candidate DBが受理する`NO ACTION`を用いる。

## 2026-08-10: pymssql dialectがunique constraint reflectionを未実装

- 事象: SQL Server 2022 fresh migrationのrevision 0007で、`Inspector.get_unique_constraints()`が`NotImplementedError`を返した。
- 原因: SQLAlchemyのpymssql dialectはこのoptional reflection APIを実装しておらず、unique indexは`get_indexes()`側で取得する構成だった。
- 対応: optional reflectorが未実装の場合は空集合とし、従来から併用しているindex reflectionで判定を継続する。
- 再発防止: Inspectorのoptional APIをmigration gateに使う場合は、未実装dialectでも代替reflectionが成立するようにする。

## 2026-08-10: tenant-key整合性probeのLIMITがSQL Serverで停止

- 事象: SQL Server 2022 fresh migrationのrevision 0008で、orphan・tenant mismatch・duplicate検査のraw `LIMIT 1`が構文エラーになった。
- 原因: revision 0005と同種の件数制限SQLが、tenant-keyとadmin audit FKの事前検査にも残っていた。
- 対応: outer join・group by・havingを含む全4probeをSQLAlchemy Core式へ変更し、dialect別の件数制限はcompilerへ委譲した。
- 再発防止: Alembic migration内の`LIMIT`を静的検索し、対応DBに依存するraw構文を残さない。

## 2026-08-10: tenant-key migration strategyがSQL Serverを未登録

- 事象: SQL Server 2022 fresh migrationのrevision 0008で、実行可能なnamed constraint DDLを持つにもかかわらず`Unsupported database dialect`で停止した。
- 原因: MySQL family昇格時にconstraint DDL strategyの許可集合を個別backend名で更新し、次候補のSQL Serverを未登録のままにしていた。
- 対応: SQL Serverを同じnamed constraint DDL strategyに追加した。
- 再発防止: 後続でdialect名の直接集合をcapability-based migration helperへ置き換え、registryと実行strategyの二重管理を解消する。

## 2026-08-10: SQL Server check constraintがlength関数を拒否

- 事象: SQL Server 2022 fresh migrationのrevision 0010で、check constraint内の`length(trim(...))`が未知の関数として停止した。
- 原因: CheckConstraintがraw SQL文字列であり、SQLAlchemyの関数compilerを経由せず、SQL Serverが必要とする`LEN`へ変換されなかった。
- 対応: 歴史create-table用の集約DDL hookでSQL Serverのみ`length(`を`len(`へ変換した。content objectも同じ集約点で`VARCHAR(MAX)`へ写像した。
- 再発防止: 型・照合順序・check式のDDL差分は個々のmodel/migrationではなくportable DDL hookに集約する。

## 2026-08-10: SQL Server check constraintがIS TRUEを拒否

- 事象: SQL Server 2022 fresh migrationのrevision 0018で、BIT型の`safe_mode IS TRUE`制約が構文エラーになった。
- 原因: SQL Serverはboolean literalと`IS TRUE/FALSE`構文を持たず、BIT列は1/0と比較する必要がある。
- 対応: portable DDL hookでSQL Serverのcheck式だけ`IS TRUE/FALSE`を`= 1/0`へ変換する。
- 再発防止: raw CheckConstraintの論理値表現もportable DDL変換のテスト対象に含める。

## 2026-08-10: SQL Server portable text downgradeがPK依存で停止

- 事象: SQL Server 2022の0020 downgradeが、primary key依存中のidentifierを`VARCHAR(MAX)`へ変更しようとして停止した。
- 原因: SQL Server fresh schemaは歴史DDL hookにより0019時点で既にbounded型だが、0020 downgradeがSQLite/PostgreSQLの履歴的`TEXT`形状へ一律に戻そうとした。
- 対応: MySQL familyと同様、SQL Serverの0020 downgradeを物理no-opとし、実際の0019 fresh shapeを維持する。
- 再発防止: migration downgradeの目標型は論理revisionだけでなく、対象familyのfresh DDL hook適用後形状と照合する。

## 2026-08-10: SQL Serverの自動命名default constraintがcolumn dropを防止

- 事象: SQL Server 2022 downgradeのrevision 0014で、server default付き`protocol`列の削除が、自動命名されたdefault constraint依存により停止した。
- 原因: SQL Serverはdefaultを列属性ではなく独立constraintとして作成し、列削除前の明示削除が必要だった。
- 対応: Alembicの`mssql_drop_default=True`を付け、カタログから実constraint名を解決して先に削除する。
- 再発防止: server default付き列をdowngradeで削除するmigrationはSQL Serverのdefault dependencyも検証する。

## 2026-08-10: admin audit migration testがbare Alembicへ依存

- 事象: `NO ACTION`回帰のSQLite migration test 4件が、PATH上に`alembic`実行fileがなくtest本体前に停止した。
- 原因: 当該testが他の修正済みmigration testと異なり、bare command名を残していた。
- 対応: `sys.executable -m alembic`でpytestと同じPython環境を使うように統一した。
- 再発防止: migration testのsubprocess起動にbare `alembic`が残っていないことを静的検索する。

## 2026-08-10: CockroachDBのschema lockがtenant-key migrationを防止

- 事象: CockroachDB v26.2.3 fresh migrationのrevision 0008で、`documents` primary key変更が`schema_locked = true`により拒否された。
- 原因: CockroachDB v26.2が新規tableをschema lock付きで作成し、同じAlembic lineageの後続revisionも明示的にunlockしない限り変更できなかった。
- 対応: portable DDL hookの`after_create`でCockroachDB tableだけ`schema_locked = false`とし、後続migrationと将来upgradeを可能にした。
- 再発防止: CockroachDB promotion matrixでfreshだけでなく、列・PK・FKを変えるdowngrade/re-upgradeを必須とする。

## 2026-08-10: CockroachDBがprimary keyの分割置換を拒否

- 事象: schema lock解除後のrevision 0008で、primary keyを先にdropし、次のstatementで新primary keyをaddするDDLが未実装機能として拒否された。
- 原因: CockroachDBはprimary keyのdrop/addを同一transactionまたは同一`ALTER TABLE`内で行うことを必要とするが、従来のAlembic operationは2 statementに分割していた。
- 対応: `atomic_primary_key_replacement`能力をDBレジストリに追加し、必要なDBだけdrop/addを1つの`ALTER TABLE`へコンパクトにした。
- 再発防止: backend名で分岐せず、schema変更の必要能力をレジストリから選択する。

## 2026-08-10: CockroachDBの式indexが冗長な列型変更を防止

- 事象: fresh migrationのrevision 0020で`external_uid`を既に同じ上限の`VARCHAR`へ変更しようとし、`lower(external_uid)`式indexの内部computed column依存により拒否された。
- 原因: CockroachDB fresh schemaは歴史DDL hookにより対象列が既にbounded型だが、履歴上の型変更を再実行していた。
- 対応: CockroachDBでは0020のupgrade/downgradeを物理no-opとし、歴史DDL hookが作った同一形状を維持する。
- 再発防止: fresh DDL変換で将来revisionの目標形状を先取りするDBは、同revisionの冗長DDLと式index依存を実DBで検証する。

## 2026-08-10: Oracleが明示的なON DELETE NO ACTIONを拒否

- 事象: Oracle AI Database Free 23.26.2 fresh migrationのrevision 0007で、foreign keyの`ON DELETE NO ACTION`が`ORA-02000`となった。
- 原因: Oracleは参照中削除拒否を既定動作として提供するが、DDL上の明示的な`NO ACTION`句を受理しない。
- 対応: 論理model/migrationの削除動作は維持し、Oracle向けforeign key compilerだけが`NO ACTION`句を省略する。
- 再発防止: 同じ参照動作でもDDL keywordの受理差がある場合は、repositoryや各migrationではなくdialect compiler境界へ閉じ込める。

## 2026-08-10: Oracle Data Pumpのremap先事前作成が警告終了を発生

- 事象: schema restore testでremap先userを先に作成したため、`impdp`は全tableを正常復元しながら`ORA-31684`を記録して終了code 5を返した。
- 原因: schema exportにはuser作成metadataも含まれ、restore helperによる同名userの事前作成と競合した。
- 対応: restore前は対象userをdropするだけにし、user・grant・tableの再作成をData Pumpへ一貫して委ねた。
- 再発防止: backup/restore testはrow照合だけでなくutility終了codeも成功条件とし、警告付き部分成功を受理しない。

## 2026-08-11: KJ demoが既存mock processを新規起動成功と誤認

- 事象: `kj_canvas_demo.py`実行前からport 8001にtest mockが残り、新規mockはbind失敗したが既存processのhealth応答で起動成功と判定した。
- 原因: `_start_mock()`がHTTP到達だけを確認し、生成した子processの生存を確認していなかった。demo終了時の子process cleanupもなかった。
- 対応: 子processの早期終了を起動失敗として扱い、demo所有processを`finally`でterminate/waitする。script pathもcheckout相対で解決した。
- 再発防止: local service harnessはhealth確認と同時に「自分が起動したprocessが生存していること」を検証し、所有processだけを必ず終了する。

## 2026-08-11: system Pythonでpytestを起動して検証環境を誤った

- 事象: SaaS共有認証状態の対象testをsystem Pythonで起動し、最初はpytest captureの`FileNotFoundError`、一時directory固定後はSQLAlchemy/Alembic欠損で収集失敗した。
- 原因: repositoryに既存`.venv`があるのに、汎用の`python -m pytest`を使った。system側pytest環境は依存関係も一時領域もproject検証条件を満たしていなかった。
- 対応: repositoryの`.venv/bin/python -m pytest`と専用`TMPDIR`へ切り替えた。
- 再発防止: backend検証は最初にproject venvの存在を確認し、以後すべて同じinterpreterへ固定する。

## 2026-08-11: access tokenのjtiを要求単位nonceと誤認

- 事象: `jti`必須化でE2E 16件が失敗し、fixtureへ`jti`を足すと同じBearer tokenを使う2要求目が`token_replayed`になった。
- 原因: RFC 7519のaccess-token `jti`をRFC 9449の要求単位DPoP proof `jti`と混同し、通常のOAuth Bearer tokenをone-time credentialへ変更した。
- 対応: access tokenのunique-insert replay ledgerと一回使用契約を撤回し、有効期限内の通常再利用を復元した。sender-constrained replay防御は方式決定issueへ分離した。
- 再発防止: security claimを「防御に使える」と読むだけで実装せず、credential種別、正規clientの再利用契約、sender bindingの有無をRFCとE2Eで先に確認する。

## 2026-08-11: 並行作業のissue metadata不備でdocs-checkが停止

- 事象: LLM cost policyの文書整合後に`docs_check.py`を実行すると、対象外の`AI-EVAL-01`で`Source Issue`欠損と`Expected verification level: manual`不許可の2件が失敗した。
- 原因: 並行作業で追加されたActive issueが、docs-checkの必須metadata契約を満たしていなかった。
- 対応: 利用者の並行変更は編集せず、本変更のHTML構造・対象issue metadata・diffを個別検証する。全体gate未通過は明記する。
- 再発防止: docs-check失敗時は対象差分との因果をpath単位で確認し、無関係な並行変更を勝手に修正しない。

## 2026-08-11: 完了issueへ非canonicalなResolved statusを使用

- 事象: `DX-TRIAGE-ADR-GATE-01`を`Status: Resolved`で起票し、triageがinvalid statusとして停止した。
- 原因: 既存の古いissue表現を踏襲し、現行canonical status一覧を起票前に確認しなかった。
- 対応: 完了状態を`Done`へ修正し、triageとdocs-checkを再実行した。
- 再発防止: 新規issueは`issue_memo_status.py`のcanonical statusを確認し、作成直後にtriageを通す。
## 2026-08-11: backend venv形式と既知pytest capture制約の確認漏れ

- 事象: `/mnt/d/GIT/kj-atlas`で`./.venv/Scripts/python.exe`を実行して実行体なしで失敗し、WSL venvへ直した再実行もpytest capture一時file消失でtest開始前に停止した。
- 原因: 過去の別checkoutのWindows venv構成を確認なしに当てはめ、失敗ログ検索も実行体名だけに狭めたため、既記録のcapture制約を見落とした。
- 対応: `.venv`の実体を確認し、`03_Implement/backend/.venv/bin/python`、専用`TMPDIR`、capture無効の`-s`で再実行した。
- 再発防止: checkoutごとにvenv実体を確認し、pytest失敗時は例外文字列でも失敗ログを再検索する。この環境ではproject venv＋専用`TMPDIR`＋`-s`を既定にする。
## 2026-08-11: shell検索文字列のbacktickを未保護で実行

- 事象: `rg`の二重引用符内にMarkdownのbacktick付き`jti`を置き、shellが`jti`をcommand substitutionとして実行して`command not found`を出した。
- 原因: 検索語をshell構文として解釈される引用方式で渡した。
- 対応: 出力に秘密情報や状態変更がないことを確認し、以後の検索語は単一引用符またはbacktickを含まない表現にする。
- 再発防止: shellへ渡す検索文字列にbacktick、`$()`、変数展開がないか実行前に確認し、Markdown断片は原則として単一引用符で囲む。
