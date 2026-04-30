# Issue Draft: FB-RM-I18N-02 locale JSON format and fallback order contract

- Type: Feature request (enhancement)
- Status: Done
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P1
- Owner: Codex (local execution)
- Scope: `03_Implement/frontend/src/i18n/`, `03_Implement/frontend/src/ui/`, `04_Documentation/configuration.md`
- Related Backlog: `FB-RM-I18N-02` (`01_Plans/adr/ADR-0007-future-backlog.md`)
- Related ADR/Spec: `01_Plans/adr/ADR-0001-value-to-requirements.md`, `01_Plans/adr/ADR-0007-future-backlog.md`, `02_Architecture/architecture.md`
- Dependencies: `FB-RM-I18N-02` (`01_Plans/adr/ADR-0007-future-backlog.md`)
- Expected verification level: `unit`

## 1) 課題 / Problem statement

現行i18nは `messages.ts` の単一辞書を `t()` が参照する構成であり、
翻訳リソースのファイル形式契約（JSON）と locale fallback の順序が明文化/固定されていない。
このままでは欠損キー時の挙動が「キー文字列へ直接fallback」に依存し、
既定言語（ja）への復元要件を満たせない。

## 2) 背景 / Context

- `ADR-0007` の `FB-RM-I18N-02` DoD は「欠損キー時に既定言語へフォールバック」。
- 既存実装は `JA_MESSAGES` のみを利用しており、複数localeやJSON契約の検証が未整備。
- `FB-RM-I18N-03`（英語UI等価）へ進む前提として、フォーマットとfallback規則を先に固定する必要がある。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 表示文言の再現性/一貫性を保証し、レビュー体験を安定化できる。
- 安全（THREAT_MODEL / SafeMode）: 文言管理層のみの変更で、外部送信やSafeMode制御には非干渉。
- 企業・行政要件（enterprise_architecture）: 多言語運用時の表示差異説明を可能にする基盤整備。
- 後方互換（schemas）: `document.json` スキーマ変更なし。UI表示ロジックだけを互換維持で更新。

## 4) 提案する解決策 / Proposed solution

- Frontend i18n 層へ locale JSON読み込みを追加し、`requested -> default(ja) -> key` fallbackを固定。
- JSONフォーマット契約を `locale code -> key/value string map` として検証関数を実装。
- 既存 `t(key, values?)` 呼び出しを壊さないよう locale未指定時は既定言語を返す。
- 非目標: 言語切替UI、view単位言語永続化、多言語完全展開（I18N-03/04の範囲）。

## 5) 受入条件 / Acceptance criteria

- [x] locale JSONフォーマットと利用locale定数がコード上で定義される。
- [x] `requested -> default(ja) -> key` の順で解決するテストが追加される。
- [x] placeholder補間と既存UI文言の互換が維持される。
- [x] unitテスト/型検査が成功する。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 locale JSONファイル（ja/en）と辞書ローダーを追加。
- [x] T2 fallback順序を持つ `t()` 実装へ更新。
- [x] T3 translate/safe_mode/ImportPanel/SharePanel の回帰テストを先行追加。
- [x] T4 ドキュメント（i18n設定）と `01_Plans` 進捗を更新。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `npm run test -- src/i18n/translate.test.ts`
  - `npm run test -- src/ui/ImportPanel.test.ts src/ui/SharePanel.test.ts src/ui/safe_mode_status.test.ts`
  - `npm run typecheck`
- 期待結果:
  - fallback順序がテストで固定され、既存UI文言回帰が発生しない。
- 未実施時の理由・代替検証:
  - なし（unitレベル完遂を必須とする）。

## 8) 代替案 / Alternatives considered

- 代替案A: TS辞書のまま locale分岐だけ追加。
  - 却下理由: JSONフォーマット契約を固定できず、I18N-03へ引き継ぎづらい。
- 代替案B: unknown keyは常に key を返す運用を継続。
  - 却下理由: default locale fallback要件（FB-RM-I18N-02）を満たせない。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: JSONキー不整合で一部文言が欠損。
- 影響範囲: i18n利用UI（Import/Share/SafeMode表示）。
- ロールバック手順: 変更コミットをrevertし旧 `messages.ts` 単一辞書に戻す。

## 10) Additional context

- `FB-RM-I18N-03` で英語UI等価提供予定。
- 本タスクでは UI locale切替導線は追加しない。


## 11) Progress log

- 2026-03-01: unitテストを先行拡充し、fallback契約の不足を失敗テストで確認。
- 2026-03-01: locale JSON (`ja`,`en`) と `t()` fallback順序を実装。
- 2026-03-01: `validateLocaleMessages` を追加し、JSON object/string value 契約を固定。
- 2026-03-01: Import/Share/SafeMode 回帰テスト + typecheck で互換を確認。
- 2026-03-01: 本メモを `Done` に更新し、Completed issue memos へ移管。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。
