# Issue Draft: DOMAIN-VISUAL-CUE-EMOJI-01 絵文字供給経路(kind:"emoji")の採否がP37設計レビューと未整合

- Type: Process / Design decision
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/domain/types.ts`, `03_Implement/frontend/src/domain/validate.ts`, `03_Implement/frontend/src/domain/validate_doc.ts`, `03_Implement/frontend/src/domain/inquiry_bundle_safe_mode.ts`, `02_Architecture/schemas.md` §19, `01_Plans/adr/ADR-0060-representative-visual-cue-source-boundary.md`
- Related Backlog: `DOMAIN-VISUAL-CUE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0060-representative-visual-cue-source-boundary.md`, `01_Plans/issues/issue-DOMAIN-VISUAL-CUE-01-representative-visual-cues.md`
- Expected verification level: `docs-check`

## 課題

`DOMAIN-VISUAL-CUE-01`のT7は「手描き/基本図形、利用者画像切り抜き、絵文字/プリセットの小さなPRへ分割して実装する」と定義しており、前2つは実装済み（チェックポイント2026-08-02複数件）。3つ目の「絵文字/プリセット」を次に実装しようとしたところ、この計画自体が同じissue内の後続記述と整合していないことが分かった。

### 採用側の証跡（絵文字を実装する、という決定）

- T5完了（2026-07-20）: 「Unicode絵文字をPhase 1既定とし、OS間不一致が確認されたcueだけを個別SVG化する」と推奨。`02_Architecture/design/unicode_emoji_os_comparison.md`は具体的に8文字（📍🔎⏳✍️🪪↗️💻⚠️）のキュレート済みセットを比較しており、「自由入力」ではなく最初から固定リストを前提にしている。
- T6完了・`ADR-0060` Accepted（2026-07-20）: §8保存決定で「B（絵文字）は保存不要（OSフォント依存）」と明記。
- T7小PR 1件目（2026-07-29、契約先行）: `types.ts`に`RepresentativeVisualCueKind = "hand_drawn" | "user_image" | "preset_svg" | "emoji"`として`"emoji"`を型・strict validator・tolerant parser・SafeMode redactionの全層へ実装・テスト済み（`validate.test.ts:132-171`等）。UIレンダリングだけが未実装。
- `02_Architecture/schemas.md:1480`（2026-07-29執筆、P37より8日後）: 「Unicode絵文字はissue T7の後続小PRとし、本節の実装済み範囲へ含めない」——絵文字を「まだ実装していないだけで採用は継続」という前提で書かれている。

### 廃止側の証跡（絵文字を廃止する、という決定）

- issue本文35行目（2026-07-21、`3133ad142`、Claude Design P37レビュー反映）: 「単色slate線画（塗りなし・1.5px・currentColor=slate-500）を本文左20×20固定スロットに限定し、型/保持/確認/根拠の4チャネルと色相で競合させない。...供給候補はキュレート済みslate線画セット（場所・人・時間・数・問い・引用等の抽象ピクトグラム）とローカル写真（グレースケール寄りの中立枠）に限り、**自由絵文字入力は廃止する**。」

この一文はT5/ADR-0060 Acceptedの**1日後**に追記されたが、ADR-0060は改訂されておらず、その8日後に書かれた契約実装・`schemas.md`はこの一文に触れずに`"emoji"`を実装・文書化している。

### なぜ人的判断が必要か（コードだけでは解決できない理由）

両者は必ずしも同じことを否定していない可能性がある。T5/ADR-0060の「絵文字」はそもそも自由入力ではなく8文字のキュレート済み固定セットであり、P37が名指しで否定した「自由絵文字入力」とは厳密には別の設計と解釈できる。しかし同時に、P37の理由（単色slate線画・currentColor=slate-500に限定し色相で既存4チャネルと競合させない）は、Unicode絵文字がOS標準でフルカラー・スタイル不可能なグリフである以上、キュレート済みかどうかに関わらずこの視覚言語制約に構造的に反する。つまりP37は「自由入力」だけを問題にしたのではなく、「絵文字という表現形式そのもの」を単色線画の対概念として退けたとも読める。

どちらの読みが正しいかはこのリポジトリのどの記録にも明記されておらず、実装側の判断で選べない。誤って実装すると、(a) 最新の設計レビュー方針（単色線画・色相非競合）に反するUIを本番へ出す、または(b) 既に受理済みのADR-0060・実装済みcontractを無駄にする、のいずれかを引き起こす。

## Acceptance

- [ ] P37の「自由絵文字入力は廃止する」が、(a) ADR-0060/T5のキュレート済み固定セット案も含めて絵文字という表現形式全体を廃止するのか、(b) 「自由入力」という入力方式だけを禁止し、キュレート済み固定セットなら許容されるのか、を明示的に判定する。
- [ ] (a)と判定した場合: `ADR-0060`を改訂し、`kind:"emoji"`をcontract/validator/SafeMode層から計画的に廃止する移行方針を決める（既にテストへ焼き込まれているため単純delete不可）。T7チェックリストの「絵文字/プリセット」を「キュレート済みslate線画ピクトグラムセット」へ書き換える。
- [ ] (b)と判定した場合: `schemas.md §19.4`の「T7後続小PR」を実装対象として復活させ、T5の8文字キュレートセットをUI（`RepresentativeVisualCueMark.tsx`、`SidePanel.tsx`のプリセットピッカー）へ実装する。
- [ ] いずれの場合も、この矛盾が発生した経緯（P37とADR-0060/schemas.mdの記述順序）を`ADR-0060`または本issueへ記録し、将来同種の設計レビュー反映で同じ矛盾を再発させない運用（例: Claude Design反映PRは影響するADR・契約文書の該当節を同一PRで更新する）を検討する。

## Validation

- 判定後: `python 01_Plans/docs_check.py`、`python 01_Plans/issues/validate_active_issue_memos.py`
- (b)実装時: 既存の基本図形E2E（`representative_visual_cue_phase1.spec.ts`）と同水準のPlaywright回帰を追加する。
