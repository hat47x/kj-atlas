# Issue: FB-RM-UX-01 公開パック読込のロケール解決がstale closureで古い値を参照

- Type: Bug
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/App.tsx`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題

- 現在の問題: `App.tsx`の`loadPublicPack`（useCallback）は本体内で`applyResolvedLocaleForView`を呼ぶが、その依存配列には`applyResolvedLocaleForView`自体が含まれていない。`applyResolvedLocaleForView`は`isReadOnly`/`locationSearch`（いずれも変化しうる値）に依存する別のuseCallbackであり、`loadPublicPack`が再生成されないままそれらが変化すると、公開パック読込時のロケール解決が古い`isReadOnly`/`locationSearch`の値に基づいて実行される可能性がある。
- 判断が必要な理由: `loadPublicPack`自体が、マウント時専用のeffect（`applyImportedViewMetadata`/`loadDocument`とともに依存配列に含まれる）の依存対象になっている。単純に`applyResolvedLocaleForView`を`loadPublicPack`の依存配列へ追加すると、`loadPublicPack`の参照が`isReadOnly`/`locationSearch`の変化のたびに再生成され、それを依存に持つマウント時専用effectが意図せず再実行されてしまう可能性がある。安全な修正には、最新の`applyResolvedLocaleForView`をrefで保持して参照するパターンなど、発火頻度を変えない設計が必要。
- 利用者または開発への影響: 公開パックを読み込んだ直後に`isReadOnly`/`locationSearch`が変化しているタイミングでは、ロケール解決が一時的に古い値を使う可能性がある。実害の頻度・深刻度は未確認。

## 対応方針

- 実施すること: refベースの「最新のコールバックを常に参照する」パターン（既存の`pendingCardDragSnapshotRef`等と同様の手法）を使い、マウント時専用effectの発火頻度を変えずにstale closureを解消する設計をMaintainerが決定する。
- 実施しないこと: 依存配列への単純な追加。マウント時専用effectの意図しない再実行を招くリスクがある。

## 受入条件

- [ ] `loadPublicPack`のロケール解決が最新の`isReadOnly`/`locationSearch`を参照するよう修正される。
- [ ] マウント時専用effect（`loadDocument`/`loadPublicPack`を依存に持つ）の発火頻度が変わらないことを確認する。

## 検証計画

- 実行する確認: 対応後、`npm run test`（frontend、該当のマウント/公開パック読込関連テスト）。
- 期待結果: 既存のマウント時動作に回帰がなく、ロケール解決が最新の状態を参照する。

## 補足

- 発見経緯: 第13ラウンドの棚卸し（stale closure観点）で発見。同じ観点で見つかった`downloadViewMetadata`（LOD/根拠オーバーレイ関連6値の依存漏れ）・`handleExportBundleZip`（`reviewEvents`依存漏れ）・`handleLoadViewMetadataFile`（`viewMode`依存漏れ）は、いずれも依存対象のコールバックがeffectの依存になっていないことを確認済みで、依存配列への追加だけで安全に直せたため本ラウンドで直接修正済み。本issueのみ、マウント時専用effectとの結合があるため機械的な追加が安全でないと判断した。
