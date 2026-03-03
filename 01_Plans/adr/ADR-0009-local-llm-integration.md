# ADR-0009-local-llm-integration: ローカルLLM統合計画

- Status: Accepted
- Date: 2026-02-24
- Deciders: Project Maintainers
- Scope: `01_Plans/`
- Migrated-from: `01_Plans/phaseX_local_llm_integration.md`

## Context

`phaseX_local_llm_integration.md` で管理していた計画・要件・受入条件を、ADR運用へ移管する。

## Decision

以下を本ADRの正本として採用する。

# English Summary
This is a phased checklist plan for local LLM integration in kj-atlas, covering provider abstraction, runtime constraints, evaluation gates, escalation, and operations readiness without introducing code.

# phaseX_local_llm_integration — ローカルLLM統合計画（チェックリスト）

本書は、LFM2.5等の軽量ローカルLLMを主軸にした運用へ移行するための計画書である。  
実装コードは含まず、完了条件を明示した進行管理チェックリストとして扱う。

---

## 0. ゴール

- Provider Interfaceにより、local/openai/fixture を設定で切替可能にする。
- CIの既定を fixture + rule checks に固定し、再現性を担保する。
- 本番は Local-first を基本とし、必要時のみ deterministic trigger でエスカレーションする。
- safeModeおよび漏えい防止を、評価ゲートと運用手順の両面で満たす。

---

## 1. Phase A: 仕様固定

- [x] `llm_provider_spec.md` のI/F定義をレビュー確定。  
- [x] `llm_runtime_constraints.md` の通信制約（in-process/IPC優先）をレビュー確定。  
- [x] `llm_quality_strategy.md` の二層評価基準をレビュー確定。  
- [x] `llm_escalation_policy.md` の既定無効・opt-in条件をレビュー確定。

**完了条件**
- 4文書の用語整合（provider, safeMode, escalation）に矛盾がない。

---

## 2. Phase B: データ/IR整備

- [ ] KJ入力の正規化項目（cards, coordinates, relations, meta）を固定。  
- [ ] 非LLM前処理（クラスタ候補、中心性、連結成分、矛盾サブグラフ）を仕様化。  
- [ ] LLM投入IRのJSON schema（必須/任意、サイズ上限、切り詰め規則）を確定。

**完了条件**
- IR仕様だけでFixtureProviderの回帰データを生成できる状態になる。

---

## 3. Phase C: テスト戦略適用

- [ ] Unit: schema/post-processing/safeMode検証項目を確定。  
- [ ] Regression: fixture snapshot/golden運用手順を確定。  
- [ ] Integration: 強モデルの curatedセット（小規模）と夜間実行方針を確定。

**完了条件**
- 「PR必須テスト」と「定期監査テスト」の境界が文書化されている。

---

## 4. Phase D: エスカレーション運用準備

- [ ] deterministic trigger一覧を運用設定に反映可能な形式で整理。  
- [ ] escalation無効時のフォールバック（再試行/人手確認）を定義。  
- [ ] 有効時のallowlist-only outbound要件をインフラ手順へ連携。

**完了条件**
- 「外部送信なしで成立する標準運用」と「有効化時手順」が分離記述される。

---

## 5. Phase E: 運用移行判定

- [ ] LocalProvider成功率の目標値を定義。  
- [ ] エスカレーション率上限を定義。  
- [ ] 失敗時の手動オペレーション（再実行/レビュー/保留）を整備。  
- [ ] 最小ログ・赤線化方針を運用ガイドへ反映。

**完了条件**
- Offline / Intranet / Enterprise の3運用形態で必要手順が欠落なく揃う。

---

## 6. 非機能・制約チェック（横断）

- [ ] ベンダロックイン表現がない。  
- [ ] 個人情報・秘匿情報を仕様に含めない。  
- [ ] safeMode既定ONの原則が全関連文書で一貫している。  
- [ ] 添付入力は「構造化テキストのみ」で統一されている。



## Consequences

- 旧文書 `phaseX_local_llm_integration.md` は廃止し、本ADRへ参照を統一する。
- 既存リンクは `01_Plans/adr/ADR-0009-local-llm-integration.md` へ更新する。

## Traceability

- Source: `01_Plans/phaseX_local_llm_integration.md`
- Supersedes: `01_Plans/phaseX_local_llm_integration.md`
