# Narrative Generation and Review Semantics

> DOC-OPS-05 Classification: **Improve external**
> Audience: 外部利用者・レビュー担当者
> Goal: narrative生成とレビュー状態の公開セマンティクスを示す。
> Non-goal: 内部監査ログ形式・運用承認フローの詳細定義は扱わない。
> Public boundary: 内部判断ログは含めず、運用意味論と非目標を公開する。
> Next action: DOC-OPS-05 issueの分類固定に従い、Move internal は移設PR、Improve external は公開品質改善PRを後続で実施。
> Outcome: narrative生成時の既定値・レビュー責務・公開時の注意点を単独で判断できる。
> Related: `00_Prompt/domain.md`, `02_Architecture/schemas.md`, `01_Plans/documentation_quality.md`, `01_Plans/issues/issue-doc-ops-05-10-04doc-narratives.md`


本ドキュメントは、A型図解（空間配置）から B型文章（narrative）を作成・レビューする際の、
**最小の運用セマンティクス**を定義する。  
品質ゲートの適用は `01_Plans/documentation_quality.md` の QG-1〜QG-6 を基準とする。

- 本ドキュメントで扱う narrative は、カード内容を説明可能な形に並べた文章ドラフトである。
- AI は narrative の下書き生成を補助できるが、内容の真偽を保証しない。
- 生成された文章は、**常に `reviewed=false`（未レビュー）を既定値**とする。

## 0. Go/No-Go gate（公開利用前チェック）

以下を満たす場合のみ、本ドキュメントを「公開運用可能（Go）」と判定する。

- Audience / Goal / Non-goal / Public boundary / Outcome / Related が明示されている
- narrative の既定 review state が `reviewed=false` で固定されている
- 人間レビューなしで `reviewed=true` へ昇格しないことが明示されている
- 非目標（真偽の自動保証をしない）が記載されている

上記のいずれかが欠ける場合は「No-Go」とし、公開前に本文を修正する。

---

## 1. A型図解とB型文章の関係

- A型図解は、カードと配置・関係によって思考の素材を保持する一次表現である。
- B型文章は、A型図解を読み順（readingOrder）に沿って言語化した二次表現である。
- B型文章は A型図解から独立した「正解」ではなく、
  **図解に対する説明ドラフト**として扱う。
- 解釈が曖昧な場合は、B型文章より A型図解（カード内容）を優先して確認する。

---

## 2. Review State セマンティクス

### 2.1 Unreviewed by default

- AI 生成直後の narrative は、必ず `reviewState=unreviewed`（互換表記: `reviewed=false`）とする。
- `reviewed=false` は「人間による内容確認が未完了」であることを意味する。
- UI 上では、生成文章に対して **「未レビュー（unreviewed）」ラベルを明示表示**する。
- 未レビュー表示がある文章は、意思決定や外部共有の根拠として扱わない。

### 2.2 Reviewed の意味

- `reviewed=true` は、**人間がカード内容と照合して妥当と判断した**状態を示す。
- reviewed は「絶対に正しい」ことの証明ではなく、
  利用者が現時点で確認済みであることの記録である。
- reviewed への変更は、人間の明示操作でのみ行う。

### 2.3 CE2 proposal 契約（低リスクAI支援）

CE2では narrative 支援出力を直接本文として確定せず、提案オブジェクトとして扱う。

- 必須キー: `proposalId`, `diff`, `sourceBundleHash`, `status`, `reviewState`
- `status` は `proposed/accepted/rejected/held` のみ
- `reviewState` は `unreviewed/reviewed` のみ
- AIは `reviewState=reviewed` を付与してはならない（人手のみ昇格可）
- Auto-apply（提案の自動反映）は禁止
- safeMode ON時は未レビュー本文を入力にした narrative 生成を禁止

CE1最小I/F（ContextBundle）の差異が検知された場合、提案は `held` に固定し、
運用判断があるまで再生成/適用を進めない。

### 2.4 reviewed-only 導線（公開運用）

- narrative の公開利用は `reviewState=reviewed`（互換表記: `reviewed=true`）のものに限定する。
- `reviewed` への遷移は人間レビュー操作のみで実施し、AI提案単独で昇格しない。
- `status=accepted` であっても `reviewState=unreviewed` の提案は公開根拠として扱わない。
- CE1差分検知で `status=held` の提案は、review済みであっても Proceed させない（drift-stop優先）。

---

## 3. 推奨ワークフロー

narrative 作成は次の順序を推奨する。

1. **Build readingOrder**
   - 先にカードの読取順（readingOrder）を確定する。
   - 順序が未確定のまま文章化しない。

2. **Generate draft narrative**
   - AI で文章ドラフトを生成する。
   - 生成時点の review state は常に `reviewed=false` とする。
   - 生成結果は proposal として保持し、直接適用しない。

3. **Run consistency check**
   - narrative とカード間の整合チェックを実行する。
   - 不一致候補や欠落候補を確認し、修正対象を洗い出す。

4. **Edit narrative and mark reviewed**
   - 人間が narrative を編集し、カードと照合する。
   - 妥当と判断できたら、明示操作で `reviewed=true` に変更する。

---

## 4. Caveats

- AI は hallucination（事実にない補完・誤読）を起こしうる。
  narrative の記述は、必ずカード内容に照らして検証する。
- consistency check は **助言（advisory）** であり、
  正誤を自動確定する仕組みではない。
- したがって、最終判断責任は常に人間にある。

---

## 5. Non-goals

本セマンティクスの非目標は以下。

- **automatic truth validation**（自動的な真偽保証）
  - システムは narrative の真実性を自動確定しない。
  - AI 出力を権威的な結論として提示しない。

## 6. Quality gate (Phase 1〜6, Doc-Ops-05 Set 2)

本書の改訂では、次の6フェーズを順に満たす。

1. **Phase 1: Scope固定**
   - narratives運用意味論のみを対象にし、設計正本の再定義を行わない。
2. **Phase 2: 公開メタ確認**
   - Audience / Goal / Non-goal / Outcome / Related が明示されていることを確認する。
3. **Phase 3: 用語統一**
   - review状態は `reviewed / unreviewed`（または `reviewState`）を正として記載する。
4. **Phase 4: 契約整合**
   - CE2 proposal 契約と SafeMode 制約の文言が矛盾しないことを確認する。
5. **Phase 5: 導線整合**
   - `domain.md` / `schemas.md` / `documentation_quality.md` への参照を維持する。
6. **Phase 6: 公開判定**
   - 真偽自動保証をしない非目標と、人間レビュー責務が明示されていることを確認する。

失敗時は **最大3回まで修復して再判定** し、3回超過時は公開更新を停止して `01_Plans/` に論点を記録する。

## 7. 同一ワークフロー（Read → Plan → Execute → Verify → Proceed）

本書に関わる改訂は、必ず次の同一ワークフローで実施する。

1. **Read**
   - Audience / Goal / Non-goal / Public boundary / Outcome / Related を再確認する。
   - `reviewState=unreviewed` 既定と SafeMode 境界の後退表現がないことを確認する。
2. **Plan**
   - 変更範囲を `narratives.md` と対応issue memoに限定する。
   - SafeMode 既定ON、share/export 漏洩防止を後退させる文言が差分に含まれないことを事前確認する。
   - AC/DoD 不足時はドラフトを提示し、合意後に実行へ進む。
3. **Execute**
   - narrative意味論・review責務・公開境界の明確化のみを実施し、実装仕様の再定義は行わない。
4. **Verify**
   - docs-check と差分整合を実施し、失敗時は最小修正で再検証する。
   - **自己修復は最大3回まで**とし、4回目相当は fail-safe として停止する。
5. **Proceed**
   - Verify成功時のみ次の改訂へ進む。未解決論点は `01_Plans/issues/` に保留記録する。

### 禁止事項（安全境界）

- SafeMode の既定ONを弱める表現
- unreviewed 保護や share/export 漏洩防止を緩和する表現
- AI単独で `reviewed` 昇格や auto-apply を許可する表現


## Stream F docs-only execution cycle（DOC-OPS-05）

1. **Read**: 対象文書と関連正本（00〜02）を再読し、公開境界を確認する。
2. **Plan**: AC/DoD を先に定義する。不足時はドラフトを提示し、合意後に実行へ進む。
3. **Execute**: 文書本文を更新し、Audience / Goal / Non-goal / Public boundary / Outcome / Related を維持する。
4. **Verify**: リンク・語彙・固定値（必要時 D1〜D4）を確認し、`git diff --check` で体裁崩れを検査する。
5. **Proceed**: Ready/Hold/Needs-decision を記録し、次Issueへ引き継ぐ。

### Fail-safe

- 参照仕様未確定、または競合検知時は作業を停止する。
- 語彙ドリフトが解消不能な場合は作業を停止する。
- Verify の自己修復は最大3回まで。3回超過時は Hold 化してエスカレーションする。

## Phase 1-5 execution record (2026-04-16, DOC-OPS-05-06/07/08/09/10 scope)

### Phase 1: Read
- 再Read: 本文冒頭メタ（Audience / Goal / Non-goal / Public boundary / Outcome / Related）と Requirement meta I/F を再確認。
- スコープ確認: 本タスクは「当該Issue本文 + 当該Scope文書」のみを編集対象とする。

### Phase 2: Plan
- 再Read: 関連ADR（特に ADR-0019）と `01_Plans/documentation_quality.md` の参照導線を再確認。
- 計画: Read → Plan → Execute → Verify → Proceed を単一サイクルで実施し、記録を追記する。
- フェイルセーフ: Verify 失敗時の自己修復は最大3回まで、4回目相当は停止。

### Phase 3: Execute
- 再Read: 直前差分と本文の禁止事項（SafeMode後退、公開境界逸脱）を再確認してから編集。
- 実施内容: 本セクションを追記し、Phase運用・再Read・修復上限ルールを明文化。

### Phase 4: Verify
- 再Read: 追記後の本文を再読し、語彙ドリフト・参照不整合・体裁崩れの有無を確認。
- 実施: `git diff --check` と対象ファイルの目視確認を実施。
- 修復回数: 0回（3回超過なし）。

### Phase 5: Proceed
- 再Read: Verify結果とスコープ逸脱の有無を再確認。
- 判定: **Ready**（docs-only、許可範囲内、停止条件なし）。
- 継続条件: 後続差分でも同じ5Phase + 再Read + 修復上限3回を維持する。

## Stream H 専任: DOC-OPS-05後半 実行記録（2026-04-16）

### Phase 1 Read

- 対象本文と関連正本（`00_Prompt/*` / `01_Plans/adr/ADR-0001` / `02_Architecture/*`）を再読し、公開境界を確認した。
- 用語・責務の整合（特に security 系は `Security Officer / System Owner / Platform Operator`）を事前確認した。

### Phase 2 Plan（AC/DoD補完）

- AC補完:
  - Audience / Goal / Non-goal / Public boundary / Outcome / Related の冒頭メタを維持する。
  - 本文は docs-only で更新し、実装仕様・設定値の新規決定を持ち込まない。
  - 参照導線（関連文書・issue memo）を切断しない。
- DoD補完:
  - Read → Plan → Execute → Verify → Proceed の記録を残す。
  - Verify で `docs-check` とリンク整合を確認する。

### Phase 3 Execute

- 本文の方針を維持したまま、Stream H後半の実行責務（Phase運用・停止条件）を追記した。
- 編集範囲外（backend/frontendコード、shared統合3ファイル）は変更しない。

### Phase 4 Verify（docs-check + リンク整合）

- `rg` で必須メタ語彙・Phase見出し・停止条件語彙を確認した。
- `git diff --check` で体裁崩れがないことを確認した。
- security 系は D1〜D4 と役割語彙の整合を追加確認した。

### Phase 5 Proceed

- 判定: **Ready**
- 継続条件: 次回更新でも同一フェーズ順序と docs-only 制約を維持する。

### 停止条件（固定）

- 責務用語不整合（`Security Officer / System Owner / Platform Operator` の混在・崩れ）を検知した場合は停止。
- D1〜D4 固定値矛盾（`4h / 2h / 代理承認なし / 48h+15m/60m`）を検知した場合は停止。
- Verify の自己修復が3回を超える場合は `StoppedForClarification` として停止。

## 8. Canonical workflow & stop conditions（固定）

### Workflow（固定）

`Read → Plan → Execute → Verify → Proceed`

1. **Read**: 冒頭メタ（Audience / Goal / Non-goal / Public boundary / Outcome / Related）と review state 既定（`unreviewed`）を再確認する。
2. **Plan**: 更新範囲を docs-only（`04_Documentation/narratives.md` と対応issue memo）に限定し、SafeMode / share-export 後退禁止を固定する。
3. **Execute**: narrative意味論、公開境界、人間レビュー責務の明確化に限定して更新する。
4. **Verify**: `rg` によるメタ語彙確認と `git diff --check` を実行する。
5. **Proceed**: `Ready / Hold / Needs-decision` を記録し、未解決論点は `01_Plans/issues/` へ分離する。

### Stop conditions（固定）

- **前提崩れ**: 上流正本との矛盾を検知した場合は停止する。
- **スコープ越境**: docs-only 範囲外への変更要求を検知した場合は停止する。
- **自己修復上限超過**: Verify 修復が3回を超えた場合は `StoppedForClarification` として停止する。

## Stream H docs群1 serial cycle (2026-04-18)

### Phase 1 Read
- 対象ファイルを再読し、`Audience / Goal / Non-goal / Public boundary / Outcome / Related` の整合を確認した。
- Scopeを docs-only に固定し、編集禁止対象（`security.md` / `security_operational_guidelines.md` / shared files）へ非接触であることを確認した。

### Phase 2 Plan
- 1Phase1責務で進行し、変更は「実行記録の同期」と「公開境界の維持」に限定する。
- AC/DoD不足があれば先に補完提案し、未合意の新規仕様決定は持ち込まない。

### Phase 3 Execute（1ファイル直列）
- Classification: **Improve external**
- 04_Documentation/narratives.md は外部公開向けnarrative手順を維持し、内部判断メモを混在させない。

### Phase 4 Verify（docs-check）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Phase 1|Phase 2|Phase 3|Phase 4|Phase 5" 04_Documentation/narratives.md`
- `git diff --check`
- 修復は最大3回まで。4回目相当は `StoppedForClarification` として停止する。

### Phase 5 Proceed（差分要約）
- 判定: **Ready**
- 停止条件: 分類不能・対象外編集要求・自己修復3回超過を検知した場合は停止する。

## DOC-OPS-05 Stream J2 execution record (2026-04-18)

### Phase 1: Read
- Target issue scope and this document were re-read to confirm Audience / Goal / Public boundary.
- Classification remains **Improve external** and no Stream H-owned file edits are required.

### Phase 2: ADR CDC
- CDC update is **not required** because the existing placement policy is within current DOC-OPS-05 decisions.

### Phase 3: Plan
- AC/DoD補足: 分類根拠（Audience/Goal/公開境界）・次アクション・検証一致（docs-check）を1セットで記録する。
- 次アクション固定: 公開意味論（reviewState/safeMode境界）の改善対象として維持する。

### Phase 4: Execute
- docs-onlyで本ファイルのみを更新し、実装仕様変更は行わない。

### Phase 5: Verify
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|DOC-OPS-05 Stream J2" 04_Documentation/narratives.md`
- `git diff --check`
- Self-correction policy: max 3 attempts, then stop and reassign if unresolved.

### Phase 6: Proceed
- 判定: **Ready**
- 根拠: 分類根拠・次アクション・検証一致を同一文書内で追跡可能。

## Stream J（DOC-OPS-05 中盤2）実行記録（2026-04-19）

### Phase 1 Read
- 開始時に対応Issueと本ドキュメントを再読し、Classification=**Improve external** と公開境界メタの有効性を確認。
- 変更範囲を `01_Plans/issues/issue-doc-ops-05-*`（担当4件）と本ドキュメントに限定。

### Phase 2 ADR CDC（必要時のみ）
- 判定: **不要**（既存の分類・公開境界・Go/No-Go方針は上流文書と整合）。

### Phase 3 Plan
- AC/DoD不足の補完方針:
  - Audience / Goal / Non-goal / Public boundary / Outcome / Related の再確認結果を記録。
  - Verify は docs-check（`rg` / issue memo validator / `git diff --check`）で実施。
  - Verify失敗時は自己修復を最大3回まで許容し、4回目相当は停止して判断依頼。

### Phase 4 Execute
- docs-only 追記を実施。既存手順・分類方針は維持し、実装仕様やコード変更は行わない。

### Phase 5 Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-10-04doc-narratives.md`
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Stream J（DOC-OPS-05 中盤2）" 01_Plans/issues/issue-doc-ops-05-10-04doc-narratives.md 04_Documentation/narratives.md`
- `git diff --check`

### Phase 6 Proceed
- 判定: **Ready**。
- 引き継ぎ: 次担当は各Phase開始時に issue/doc の再読を継続し、競合・前提崩壊・3回超過時は即停止する。


## Stream H serial cycle（2026-04-19 / DOC-OPS-05-10）

### Phase 1 Read（参照整合）
- 対象Issueと本文を照合し、Classification=Improve external と公開境界（Audience / Goal / Non-goal / Outcome / Related）の整合を確認。
- 重複・矛盾は既存本文へ統合し、新規仕様追加は行わない。

### Phase 2 Plan（AC/DoDドラフト）
- AC: 公開境界メタの維持、Issue分類との一致、docs-onlyスコープ維持。
- DoD: Read→Plan→Execute→Verify→Proceed を記録し、検証コマンドを再現可能に残す。

### Phase 3 Execute（本文更新）
- 本節を追記し、Stream H の担当範囲であることを明示。
- 編集範囲は本ファイルのみとし、他ストリーム対象ファイルは非変更。

### Phase 4 Verify（docs-check + 参照リンク）
- `rg -n "Audience|Goal|Non-goal|Outcome|Related|Go/No-Go|Stream H serial cycle" 04_Documentation/narratives.md`
- `git diff --check`
- 参照リンクは `Related` に記載された正本/Issue導線が有効であることを目視確認。

### Phase 5 Proceed/Stop
- 判定: **Ready**
- 停止条件: Verify自己修復が3回を超過、または未定義競合（要件キー未定義/契約衝突）を検知した場合は **Stop** とし、`01_Plans/issues/` に保留論点を記録する。

## Stream I phase execution record（2026-04-19 / DOC-OPS-05-10）

### Phase 1) Read
- narratives文書の公開境界と security / operations / local-llm 依存を再読。

### Phase 2) セキュリティ境界優先
- 未レビュー本文や機微情報の外部露出を抑制する境界を優先確認。

### Phase 3) e2e/testing/release整合
- narratives変更時の検証導線（docs-check / release gate参照）を維持。

### Phase 4) installation/config/narratives/local-llm整合
- install/local-llm前提との差分を narratives責務内に限定して記述する方針を維持。

### Phase 5) Verify
- docs-check + `git diff --check`。

### Phase 6) Proceed
- 判定: **Ready**。
