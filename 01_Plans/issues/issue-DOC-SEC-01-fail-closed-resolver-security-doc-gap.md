# Issue: DOC-SEC-01 新規resolverのfail-closed挙動がsecurity.mdへ未反映

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Documentation
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `04_Documentation/security.md`
- Related ADR/Spec: `02_Architecture/runtime_parameter_registry.md`
- Expected verification level: `docs-check`

## 課題

- 現在の問題: `04_Documentation/security.md`は`KJ_ATLAS_ACCESS_CONTROL_ADAPTER`について「`external_http`を指定しても接続先（endpoint）が未設定の場合、現行実装は`noop`にフォールバックします」と明記している（149行目付近）。一方、SaaSテナント対応で新設された`KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER`と`KJ_ATLAS_TENANT_CAPABILITY_RESOLVER`は、`02_Architecture/runtime_parameter_registry.md`の192-193行目で「`external_http`ではendpointを必須とし...`none`でHTTP設定だけを残すことも拒否します」「不明値・不完全設定はfail-closedにします」と、正反対の挙動（起動時拒否）が定められている。security.mdはこの2キーに一切言及しておらず、既存の`ACCESS_CONTROL_ADAPTER`の「フォールバック」記述だけを読んだ運用者が、新しい2 resolverも同様に静かにフォールバックすると誤解する余地がある。
- 利用者または開発への影響: 誤解した運用者が、bindingやcapability resolverの設定不備を起動失敗ではなく「静かにnoneへ後退する」ものと想定し、意図せず起動失敗に遭遇する、または逆に「fail-closedだから安全」という前提を確認せずに運用してしまう可能性がある。実装側の挙動自体（fail-closed）はより安全な既定であり、セキュリティ上のバグではない。純粋にsecurity.mdの説明範囲の抜けである。

## 対応方針

- 実施すること: security.mdの該当箇所（アクセス制御アダプタの節、またはSaaS関連の記述箇所）に、`KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER`/`KJ_ATLAS_TENANT_CAPABILITY_RESOLVER`が既存の`ACCESS_CONTROL_ADAPTER`とは異なりfail-closed（起動拒否）であることを追記するか、runtime_parameter_registry.mdへの参照を明示して両者の挙動差を運用者が誤読しない形にする。
- 実施しないこと: 実装挙動（fail-closed vs フォールバック）自体の変更。どちらの挙動をsecurity.mdの記述対象に含めるか（新設resolverの詳細まで書くか、registryへの参照だけに留めるか）はMaintainer判断とし、本issueでは判断・記述内容を先取りしない。

## 受入条件

- [ ] security.mdを読むだけで、新設2 resolverの不完全設定時の挙動（fail-closed）が`ACCESS_CONTROL_ADAPTER`のフォールバック挙動と異なることが分かる。
- [ ] 実装挙動・SafeMode・公開APIは変更しない。
- [ ] `python3 01_Plans/docs_check.py`が通過する。

## 検証計画

- 実行する確認: `python3 01_Plans/docs_check.py`、`git diff --check -- 04_Documentation/security.md`。
- 期待結果: 追記後も既存の文書契約チェックが通過し、新旧resolverの挙動差が本文から読み取れる。

## 補足

- 発見経緯: SaaSテナント対応の大規模マージ後の棚卸しで発見。実装・テストは既に完了しており、本issueはsecurity.mdの記述範囲をどう広げるかというMaintainer判断待ちのdocs-only issue。
