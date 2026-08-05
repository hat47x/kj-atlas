# Issue Draft: FB-RM-I18N-02 locale JSON format and fallback order contract

- Type: Feature request (enhancement)
- Status: Done
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P1
- Owner: Codex (local execution)
- Scope: `03_Implement/frontend/src/i18n/`, `03_Implement/frontend/src/ui/`, `04_Documentation/configuration.md`
- Related Backlog: `FB-RM-I18N-02` (`01_Plans/adr/ADR-0007-future-backlog.md`)
- Related ADR/Spec: `01_Plans/adr/ADR-0001-value-to-requirements.md`, `01_Plans/adr/ADR-0007-future-backlog.md`, `02_Architecture/design/architecture.html`
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


## Stream H realignment (2026-05-04)

### Phase 1: Read同期（依存/優先度再評価）
- 系列依存の再評価: `I18N -> MID -> RS -> SEC` を基本順とし、`FB-RM-I18N-02-locale-json-fallback-order` はこの順序に従って前後の成果物契約を参照する。
- 優先度再評価: reversible synthesis の実装引き渡し観点で、**決定論（reproducibility）** と **監査可能性（auditability）** を同列最優先とする。

### Phase 2: Plan（A1/A2 契約）
- A1（実装契約依存点）: downstream 実装は本メモの `Acceptance criteria` と `Validation plan` を満たす I/F を維持する。
- A2（モック先行可能点）: deterministic 候補生成・監査出力フォーマット・固定フィクスチャを先行モック化して検証可能。

### Phase 3: Execute（I/F・出力・監査証跡・Proceed条件）
- 入力I/F: Document/locale/query/export context など、本メモで規定済みの入力契約を採用。
- 期待出力: 同一入力で同一順序/同一内容の出力を返す（非決定挙動を禁止）。
- 監査証跡: 実行コマンド、判定結果、失敗理由、再試行回数を issue memo に記録する。
- Proceed条件: AC/DoD が満たされ、依存系列の受入条件と矛盾しないこと。

### Phase 4: Verify（欠落検査 + 自己修復）
- 決定論要件と監査要件の欠落をチェックし、欠落時は最大3回まで自己修復を試行する。
- 3回で是正不可の場合はフェイルセーフ停止（非決定仕様混入 / 監査要件欠落 / 依存矛盾）。

### Phase 5: Proceed（実装引き渡し優先度）
- Frontend/Backend 実装への引き渡しは、`I18N-02 -> MID-01 -> MID-02 -> MID-03 -> MID-05 -> RS-02 -> SEC-02 -> I18N-03` の優先バックログ順を基準とする。

## Stream F independent pass (2026-05-06)

### Phase 1 Read同期
- `AGENTS.md` の Stream F 対象境界を再確認し、本メモの編集範囲を QA/I18N/RM の独立検証記録に限定した。
- 上流方針（`ADR-0019`, SafeMode既定ON, share/export fail-closed）との整合を再確認した。

### Phase 2 依存確認（モック契約基準）
- 依存 I/F は contract-first とし、内部実装詳細ではなく観測可能な入出力・状態遷移を判定対象に固定した。
- 先行依存（I18N→MID→RS→SEC / PUB境界）に矛盾がないかを確認し、矛盾時は Proceed せず Stop する条件を維持した。

### Phase 3 Plan / Execute / Verify / Proceed
- Plan: AC/DoD/Go-NoGo と検証コマンドの対応を再点検した。
- Execute: docs-only で判定文面を整備し、実装コード変更は行わない方針を維持した。
- Verify: 本メモ記載の証跡形式（Command/Result/Decision/Next action）で再実行可能性を確認した。
- Proceed: 依存未解決・環境制約・境界後退のいずれかがある場合は Hold/Stop を優先する。

### Phase 4 Self-Correction（最大3回）
- 自己修復上限を `3回` に固定し、4回目相当が必要な場合は Fail-safe 停止を適用する。
- 修復時は「欠落AC補完 → 判定再確認 → 証跡更新」の順で最小差分更新のみ許容する。

### Phase 5 Stopper
- 停止トリガー: 依存矛盾、SafeMode境界後退、GoNoGo未充足、または自己修復上限超過。
- 停止時は未達項目と再開前提（必要I/F・実行環境・判定根拠）を本メモへ追記して引き継ぐ。

## Stream G pass (2026-05-10)

### Phase 1: Interface Read固定
- domain/worker/export の既存I/F境界（入力契約・出力順序・型）を再確認し、今回の変更は **issue memo更新のみ** に限定する。
- 決定論優先順位を P1 とし、乱数・非安定ソート・時刻依存を新規導入しない。

### Phase 2: ADR明文化（Context/Decision/Consequences）
- Context: MID/I18N/RS/SEC 系列は既に実装済みで、現在は運用上の受入境界を明文化する段階。
- Decision: 「人間の最終判断を残す」「決定論を壊さない」「監査可能な証跡を維持する」を共通規範として固定。
- Consequences: 後続streamは同一AC/DoDを参照可能になり、衝突なく局所改善できる。

### Phase 3-6: Execute/Verify要点
- Deterministic化: 既存比較キー・ソート規約の維持を前提化（仕様追加なし）。
- 監査: manual intervention は audit log/export へ残す方針を再確認。
- i18n/worker: fallback順序・worker fail-safe（fallback/cancel）を受入境界として再固定。
- 構造メトリクス: locale非依存・再現可能出力の維持を受入条件として明記。

### Phase 7: 完了判定
- 判定: ✅ Done維持（docs整合）。
- 根拠: 決定論 / 監査性 / 後方互換 / 最小E2E観点が既存AC/DoDと矛盾しない。
- Stop条件: 依存矛盾またはAC欠落が観測された場合は3回自己修復後にFail-safe停止。
