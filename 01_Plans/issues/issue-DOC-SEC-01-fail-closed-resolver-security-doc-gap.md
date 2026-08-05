# Issue: DOC-SEC-01 resolverのfail-closed設定境界を運用文書へ反映する

- Type: Documentation
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `04_Documentation/security.md`
- Related ADR/Spec: `02_Architecture/runtime_parameter_registry.md`
- Expected verification level: `docs-check`

## 課題

運用文書は外部PDP adapterのendpoint欠落時に`noop`へfallbackする挙動を説明していたが、新しいDocument policy binding / tenant capability resolverは不完全設定を起動時に拒否する。この差が記載されず、同じfallbackだと誤読できる状態だった。

## 対応

- Access control節にSaaS用resolverの設定境界を追記した。
- `external_http`でendpointがない場合、`none`でHTTP設定だけが残る場合、不明resolverや安全でないURLをfail-closedで起動拒否することを明記した。
- resolver無効化時はendpointとAPI keyも同時に削除する運用手順を明記した。
- セキュリティ確認チェックリストへresolver設定の確認項目を追加した。
- 実装挙動、SafeMode、公開APIは変更していない。

## Acceptance

- [x] security.mdだけで外部PDP adapterのfallbackと新しい2 resolverの起動拒否の違いが分かる。
- [x] resolverを`none`へ戻す際のHTTP設定除去まで確認できる。
- [x] 実装挙動・SafeMode・公開APIを変更していない。

## Validation

- runtime parameter registryとresolver設定validation testを記載根拠として照合した。
- `python 01_Plans/docs_check.py --root .`: passed（32 active memos）
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`: passed（32 active memos）
