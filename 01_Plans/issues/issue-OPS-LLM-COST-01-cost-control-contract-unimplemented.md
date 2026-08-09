# Issue: OPS-LLM-COST-01 LLMコスト統制とレート制限が文書のみで未実装

- Type: Operations / Process
- Status: Open
- Source Issue: N/A
- Priority: P2
- Owner: Unassigned
- Scope: `02_Architecture/llm_escalation_policy.html`, `03_Implement/backend/src/kj_atlas_api/llm/provider.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/settings.py`, `04_Documentation/operations.md`
- Related ADR/Spec: `02_Architecture/llm_escalation_policy.html`, `01_Plans/adr/ADR-0009-local-llm-integration.md`, `01_Plans/adr/ADR-0050-llm-provider-observability-and-contract-fidelity.md`
- Expected verification level: `unit`

## 課題

`02_Architecture/llm_escalation_policy.html` §03（コスト制御）はこう定めている。

> 月次または環境別の外部呼び出し上限（回数/トークン）を定義する。上限到達時は**自動でローカル専用モードに降格**する。運用ダッシュボードで、ローカル成功率・エスカレーション率・失敗率を監視する。

**この契約は一切実装されていない。**

- 呼び出し回数カウンタ: 無し
- トークン計上: 無し（`grep -n "token_count\|usage\|quota\|budget" llm/provider.py` → 該当なし）
- 上限到達時の自動降格: 無し
- 監視用メトリクス: 無し

さらに、**システム全体にレート制限が存在しない**。

```
$ grep -rn "rate.limit\|RateLimit\|slowapi\|throttl" --include="*.py" 03_Implement/backend/src/
(該当なし)
```

認証エンドポイント・LLM エンドポイント・文書 API のいずれも無制限に呼び出せる。

## 影響

- **予算統制**: 外部LLM（`KJ_ATLAS_LLM_PROVIDER=large-scale`）は従量課金である。上限が無いため、暴走クライアント・ループ・意図的濫用のいずれでもコストが青天井になる。企業・行政の調達では、コスト上限が技術的に担保されていることが要件になる場合がある。
- **可用性**: レート制限が無いため、認証エンドポイントへの総当たりや LLM エンドポイントへの大量投入を抑制できない。`SEC-AUTH-REPLAY-01` 制約3（jti キャッシュの O(n) 走査）と組み合わさると、認証系の性能劣化が起きやすい。
- **文書の信頼性**: 「上限到達時は自動でローカル専用モードに降格する」と読んだ運用担当者は、そのガードが働くと期待して外部LLMを有効化する。実際には働かない。

## 対応方針（実装者向け）

本issueは範囲が広いため、**分割して段階実施**することを推奨する。文書の記述が過大である点だけでも先に解消できる。

### 段階1（低コスト・先行可能）: 文書と実態の整合

`llm_escalation_policy.html` §03 を、実装済みの内容と未実装の計画に区別して書き分ける。「自動降格する」という断定を、未実装であれば計画として明示する。**これだけでも運用者の誤解は防げる。**

### 段階2: 計測

- LLM 呼び出し回数・トークン数（provider が返す場合）を計上する。
- `ADR-0050` D1 が導入した provider 可視化と接続する余地がある。

### 段階3: 上限と降格

- 上限値の設定キー（`KJ_ATLAS_*` 命名規約に従う）を定義し、`02_Architecture/runtime_parameter_registry.md` へ登録する。
- 上限到達時の挙動を決める。「ローカル専用へ降格」は `llm_fallback_to_none` / provider 切替との関係整理が要る。降格が SafeMode や proposal-only の境界を弱めないこと。

### 段階4: レート制限

- 対象（認証・LLM・文書API）と単位（IP / 主体 / テナント）を決める。SaaS ではテナント単位が要る。
- 前段（リバースプロキシ / API Gateway）へ委譲するか、アプリで持つかは設計判断。`ADR-0020` の「認証は外部委譲」と同じ論法で前段委譲もありうるが、その場合は**運用文書に必須要件として明記**すること（`SEC-ADMIN-PLANE-01` と同じ論点）。

段階3・4 は設計判断を含むため、着手前に ADR 要否を判断すること。

## 受入条件

- [ ] AC-1（段階1）: `llm_escalation_policy.html` §03 の記述が、実装済み機能と未実装の計画を区別している。未実装の断定表現が残っていない。
- [ ] AC-2（段階2以降）: 外部LLM呼び出しの回数が計測され、参照可能である。
- [ ] AC-3（段階3以降）: 上限設定と到達時挙動が実装され、テストで固定されている。降格時も SafeMode / proposal-only 境界が維持される。
- [ ] AC-4（段階4以降）: レート制限の責務境界（アプリ / 前段）が決定され、前段委譲の場合は運用文書に必須要件として記載されている。
- [ ] AC-5: 新規設定キーが `02_Architecture/runtime_parameter_registry.md` と同期している。

## 検証

- `python -m pytest tests/ -k "llm or provider" -q`
- `python 01_Plans/docs_check.py`
