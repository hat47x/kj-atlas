# Issue Draft: DOC-OPS-02 人間意思決定知見に基づく文書横断改善計画

- Type: Process
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Platform Architecture Owner + Security Officer
- Scope: `01_Plans/`, `02_Architecture/`, `04_Documentation/`, `AGENTS.md`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0001`, `ADR-0021`, `02_Architecture/strict_mode_exception_approval_flow.md`, `04_Documentation/security.md`, `04_Documentation/security_operational_guidelines.md`
- Dependencies: N/A
- Expected verification level: `docs-check`

## 1) 課題 / Problem statement

- 人間判断（ENV-ARCH-01、AUTH-OPS-03）により運用プロファイルの選択肢が具体化した一方、文書間で記述粒度と表現（必須/推奨）が揺れている。
- 「設計文書（02）」と「運用文書（04）」で同じ概念を説明する際、登場人物定義や判断ポイントの置き場所が一定でないため、初見読者の理解コストが高い。
- 今後の変更で再びドキュメントがドリフトするリスクがある。

## 2) 背景 / Context

- strict/non-strict の二重プロファイル運用を許容する判断が確定済み。
- `security.md` と `strict_mode_exception_approval_flow.md` に可読性改善は入ったが、関連ドキュメント（operations / enterprise_architecture / issues）まで含めた同期運用計画は未整理。
- AGENTSのProject Mapに新規文書は追記済みだが、横断改善の実施順序と完了判定が未定義。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 意思決定の再利用性（同じ議論を繰り返さない）と運用再現性を向上する。
- 安全（THREAT_MODEL / SafeMode）: 表現揺れにより運用者が誤解した場合、strict運用・監査運用の実施品質が低下する。
- 企業・行政要件（enterprise_architecture）: 役割分離・監査説明責任を文書で一貫提示する必要がある。
- 後方互換（schemas）: スキーマ変更を伴わず、文書整合のみでリスク低く実施できる。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs only（横断改善計画の明文化）。
- 変更の最小単位:
  - フェーズ1: 用語・役割定義の共通化（Security Officer/System Owner/Platform Operator）。
  - フェーズ2: strict/non-strict プロファイル記述の表現統一（必須化→ガイドライン参照）。
  - フェーズ3: 参照導線（02⇄04⇄01）の監査と不足リンク補完。
  - フェーズ4: 文書差分レビュー用チェックリストを issue に固定。
- 非目標:
  - backend/frontend のコード変更。
  - 認可判定ロジックやAPI契約の変更。
  - 新たな運用役職の追加。

## 5) 受入条件 / Acceptance criteria

- [x] 役割定義の参照元が `04_Documentation/security_operational_guidelines.md` を起点に統一される。
- [x] strict/non-strict の表現で「強制」ではなく「ガイドライン参照」であることが 01/02/04 の対象文書に反映される。
- [x] `enterprise_architecture.md` / `strict_mode_exception_approval_flow.md` / `security.md` / `operations.md` の参照リンク整合が確認できる。
- [x] 文書横断レビューのチェックリスト（用語、役割、導線、表現）を本issueに保持できる。
- [x] docs-check 検証結果が再現可能なコマンドで記録される。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: 横断対象文書（01/02/04/AGENTS）を確定し、改善観点マトリクスを作成する。
- [x] T2: 登場人物定義の先出し方針を文書別に適用し、重複/矛盾を解消する。
- [x] T3: strict/non-strict 記述を「ガイドライン参照」へ統一する。
- [x] T4: 参照導線（相互リンク）を監査し、不足リンクを補完する。
- [x] T5: 横断レビュー用チェックリストを本issueの Additional context に固定する。


### Improvement matrix（確定）

| 対象 | 観点 | 更新方針 |
|---|---|---|
| `01_Plans/issues/*` | 運用DoD/停止条件 | Q1〜Q10確定値を明記し、停止条件を「固定値逸脱」に統一 |
| `02_Architecture/*` | 責務境界/役割 | IAP委譲・AuthContext正規化・RACI境界を明示 |
| `04_Documentation/*` | strict/non-strict運用粒度 | ガイドライン参照と必須チェック項目を統一 |
| `AGENTS.md` | 横断導線 | Read Order/Project Map の参照先を維持しドリフト監視 |

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "Security Officer|System Owner|Platform Operator|運用ガイドライン|公開運用プロファイル" 01_Plans/issues 02_Architecture 04_Documentation AGENTS.md`
- 期待結果:
  - issue memo 検証が成功し、対象文書に横断キーワードが存在することを確認できる。
- 未実施時の理由・代替検証:
  - Python未導入環境では `rg` と `git diff --check` を代替として記録する。

## 8) 代替案 / Alternatives considered

- 代替案A: 個別修正を継続し、横断計画を作らない。
  - 却下理由: 変更のたびに同種レビューが再発し、ドリフトを防げない。
- 代替案B: 02_Architecture のみ更新し、04_Documentation を追随しない。
  - 却下理由: 運用者向け導線が断絶し、実務での誤読リスクが残る。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 計画が抽象的すぎて実行タスクに落ちない。
- 影響範囲: 文書整合レビュー、運用手順の理解コスト。
- ロールバック手順: フェーズを最小単位へ再分割し、対象文書を1グループずつ見直す。

## 10) Additional context

- 関連Issue/PR/議論ログ: N/A
- ADR化が必要になる条件: strict/non-strict 運用プロファイル自体の選択基準を仕様として固定する必要が出た場合。

### Cross-doc review checklist（初版）

- [x] 用語定義が先に置かれている（登場人物・運用プロファイル）。
- [x] 「必須」「推奨」「参考」のレベルが明確で、文書間で矛盾しない。
- [x] 02の設計文書と04の運用文書が相互参照で辿れる。
- [x] issue側のタスク分解が、実際の文書更新順序に対応している。
- [x] Q1〜Q10固定値（AUTH-OPS-03）と strict/non-strict 記述が矛盾しない。
- [x] 環境変数記述が `KJ_ATLAS_*` 契約のみを参照している。


### 実施順序（固定）

1. AUTH-OPS-03 正本（`strict_mode_exception_approval_flow.md`）の固定値を参照基準にする。
2. 02（`enterprise_architecture.md`）へ責務境界/停止条件/復旧条件を同期する。
3. 04（`operations.md` / `security.md`）へRunbookと最小監査項目を同期する。
4. 01（dashboard/decision-pack/issues README）へ状態遷移とDecision Queue反映を同期する。
5. AGENTS.md の導線・ドリフト検知項目を更新し、以後の再発を防止する。

### ドリフト検知項目（固定）

- [x] 用語ドリフト: Security Officer / System Owner / Platform Operator の定義が一致している。
- [x] 役割ドリフト: 2者承認責務と実行責務分離が一致している。
- [x] 導線ドリフト: 02→04→01 の相互リンクが有効。
- [x] 運用値ドリフト: D1〜D4 固定値（4h, tenant/2h, 代理承認なし, 48h+15m/60m）が一致している。

## 13) Stream G同期ログ（2026-04-30）

- Phase 1 Read同期: `strict_mode_exception_approval_flow.md` を起点に `enterprise_architecture.md` → `operations.md` → `security.md` → `decision-pack-2026-03-human-judgement.md` → 本issue の順で再読。
- Phase 2 Plan: AC/DoD の不足がないことを確認し、未完チェックボックスのみを最小更新対象に固定。
- Phase 3 Sync: DOC-OPS-02固定順序（`02_Architecture -> 04_Documentation -> 01_Plans -> AGENTS.md`）への適合を再確認し、本issueの未完チェックを完了状態へ同期。
- Phase 4 Verify: 用語（Security Officer/System Owner/Platform Operator）・役割分離・導線・固定値D1〜D4（4h / tenant+2h / 代理承認なし / 48h+15m/60m）の一致を確認。
- Phase 5 Proceed: 自己修復は 0/3 回で完了。次回同期時も同4観点を必須チェックとして継続。


## 12) 完了報告（2026-03-08）

- 実施順序（固定）: `02_Architecture -> 04_Documentation -> 01_Plans -> AGENTS.md`。
- ドリフト検知4観点（用語/役割/導線/固定値D1〜D4）をゼロ差分で確認。
- AGENTS の 4.4 節へ同期順序と固定値確認観点を保持し、再発防止の入口を維持。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。


## 14) Stream C governance lock record (2026-05-20)

### Context
- 対象は AUTH ガバナンス関連の文書同期のみ（`02_Architecture/strict_mode_exception_approval_flow.md` / `02_Architecture/enterprise_architecture.md` / AUTH系issue）。
- 用語は `Security Officer / System Owner / Platform Operator` を単一語彙として維持し、別名導入を禁止する。
- 固定値は AUTH-OPS-03 の D1〜D4（4h / tenant+2h / 代理承認なし / 48h+15m/60m）を正本参照で扱う。

### Decision
- DOC-OPS-02 同期順序は `02_Architecture（strict_mode_exception_approval_flow → enterprise_architecture） -> 04_Documentation -> 01_Plans -> AGENTS.md` を採択し固定する。
- 2者承認（Security Officer + System Owner）と実行責務（Platform Operator）の分離を、AUTH関連メモで再定義せず参照維持する。
- `Plan -> Execute -> Verify -> Proceed` を必須化し、自己修復は 3 回上限（超過時は `StoppedForClarification`）を維持する。

### Consequences
- Auth Governance の更新は Architecture 正本を先行し、下流文書の先行確定を防止できる。
- 用語・役割・導線・D1〜D4 の4観点でドリフト検知を再利用できる。
- SafeMode既定ONとshare/export保護を崩す変更は、AUTH関連の文書更新でも禁止のまま維持される。

## Stream G documentation/public boundary pass (2026-06-13)

### Plan
- 対象: `cross-document drift`。
- Scope: Docs-only。`03_Implement/` と `02_Architecture/` は編集しない。
- Acceptance: 公開/保守/開発者/内部計画の分類が追跡でき、SafeMode・share/export・AI提案レビューの安全境界が後退しない。

### Execute
- RequirementID `DOC-OPS-02` の公開境界を再確認。
- Decision: 今回の04文書更新は02層を変更せず、公開文書側で役割・導線・安全境界を同期する範囲に限定した。

### Verify
- docs-check 対象として issue memo metadata、Markdown整形、リンク導線、公開不可情報の混入有無を確認する。
- Self-correction budget: 0/3 から開始し、4回目相当は停止する。

### Proceed
- 判定: Ready for verification。
- 残課題: 実ファイル移動や開発者向け正本の再配置が必要な場合は、別PRで allowlist と移動先を明示して扱う。
