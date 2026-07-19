# Issue: DX-CLEANUP-05 DeterministicTieBreakの固定順序がフロント/バックエンドで二重定義

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/domain/validate_doc.ts`, `03_Implement/backend/src/kj_atlas_api/models.py`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題

- 現在の問題: `DeterministicTieBreak.order`の固定4要素順序（`padding_compliance`, `self_intersection_avoidance`, `minimum_area_delta`, `minimum_vertex_count`）が、フロントエンド（`validate_doc.ts:80-85`のTS配列、`:982-992`で位置ごとに検証）とバックエンド（`models.py:670-674`のPydantic `Literal`のタプル型）に、それぞれ独立にハードコードされている。現時点では両者は完全に一致しているため、現在アクティブなバグではない。
- 利用者または開発への影響: 実害は無い。ただし、この順序が将来変更される場合（例: 5つ目のtie-break規則が追加される場合）、TSの配列とPythonのタプル型の両方を手動で同期させる必要があり、どちらか一方だけ更新されても検知する仕組みが無い（往復するテストがたまたま失敗する以外に検知経路が無い）。

## 対応方針

- 実施すること: 単一の正本（例: `02_Architecture/schemas.md`側に順序を明記し、両実装がそこから生成/参照する、またはコード生成ステップを設ける等）に統合するかどうかをMaintainerが判断する。
- 実施しないこと: 統合そのもの。フロント/バックエンドが別言語であるため、共有ソースを設ける場合は生成ステップや契約テストの追加が必要になり、規模のある設計判断を伴う。

## 受入条件

- [ ] 二重定義を許容し続けるか、単一の正本に統合するかの方針が決定される。
- [ ] 統合する場合、既存の往復（round-trip）テストが引き続き通過することを確認する。

## 検証計画

- 実行する確認: 対応する場合、frontend/backendそれぞれの`DeterministicTieBreak`関連テスト。
- 期待結果: 既存のtie-break順序検証テストに影響がないことを確認する。

## 補足

- 発見経緯: 第10ラウンドの棚卸し（フロント/バックエンド間のロジック重複観点）で発見。同じ観点で見つかった`reviewerRef`/`ownerRef`のopaque判定ルールの乖離（フロントが`@`のみチェックし、バックエンドの`sso:`/`oidc:`/`saml:`/`provider:`プレフィックスチェックを欠いていた）は、実際に乖離していた（機械的に修正可能）ため本ラウンドで直接修正済み。
