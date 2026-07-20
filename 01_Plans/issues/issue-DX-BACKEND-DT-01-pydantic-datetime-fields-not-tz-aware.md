# Issue: DX-BACKEND-DT-01 Pydantic datetimeフィールドがtimezone-aware強制になっていない

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/models.py`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題

- 現在の問題: `models.py`は`createdAt`/`reviewedAt`/`auditRecordedAt`/`occurredAt`/`decidedAt`/`shelvedAt`/`generatedAt`など約15個のPydanticフィールドを、プレーンな`datetime`型（`AwareDatetime`ではない）として宣言している。これらはクライアントから送られたISO文字列をそのまま受け付けるため、Pydanticはtimezone-naiveな文字列（オフセット無し）も、timezone-awareな文字列（`Z`やオフセット付き）も区別なく受理する。
- 判断が必要な理由: 現時点でこれらのフィールド同士、またはこれらのフィールドと`datetime.now(timezone.utc)`のようなaware値との比較・演算がリポジトリ全体のどこにも存在しないことを確認済み（第14ラウンドの棚卸しで確認）。つまり今すぐ顕在化するバグではないが、将来これらのフィールドを比較・ソート・演算するコードが追加された際に、naive/aware混在によるエラーや誤った結果を引き起こす潜在的な地雷になっている。`AwareDatetime`型への変更が既存の保存済みデータ（naiveな文字列を含む可能性）と互換性があるかは未確認。
- 利用者または開発への影響: 現時点で実害なし。将来の機能追加時に踏み抜かれるリスクを事前に塞ぐかどうかの判断。

## 対応方針

- 実施すること: 該当フィールドを`AwareDatetime`型へ変更するか、現状のプレーン`datetime`のままとする理由を文書化するかをMaintainerが決定する。
- 実施しないこと: 型の変更そのもの。既存の保存済みデータとの互換性確認、および型変更が引き起こしうる既存テストへの影響を精査せずに変更しない。

## 受入条件

- [ ] 該当フィールドの型方針が決定される。

## 検証計画

- 実行する確認: 変更する場合、`python3 -m pytest`（backend、該当モデルを使う全テスト）。
- 期待結果: 既存の保存・読込フローに回帰がないことを確認する。

## 補足

- 発見経緯: 第14ラウンドの棚卸し（timezone-naive datetime観点）で発見。同じ観点で確認した`datetime.now()`/`datetime.utcnow()`（naive呼び出し）はリポジトリ全体で0件、`auth_assurance.py`の唯一の比較/演算箇所は既にnaive→aware正規化を経てから比較しておりクリーンだった。本issueはPydanticフィールド宣言レベルの潜在的ギャップであり、実際のバグではない。
