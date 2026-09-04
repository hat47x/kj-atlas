# Issue: AI-IR-FOCUS-PRESERVATION-01 切り詰め時も対象カードと人間の確定判断を保持する

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug / AI Input Projection
- Status: Open
- Source Issue: `AI-IR-SCALE-01`, `AI-IR-PROJECTION-01`
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/llm_input_ir.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/tests/test_ai_detect_contradiction_ir.py`, `02_Architecture/llm_input_ir_spec.md`
- Related ADR/Spec: `ADR-0069`, `02_Architecture/llm_input_ir_spec.md` §2.2B / §5, `AI-IR-PROJECTION-01` AC-1, `AI-IR-SCALE-01`
- Expected verification level: integration

## 課題

R16で定めた「routeごとに必要な意味集合を先に確認する」という基準で `detect-contradiction` を見直すと、300枚規模でAC-1を破り得る切り詰め経路がある。

`detect-contradiction` のAC-1は、人間がすでに `confirmed` / `held` とした矛盾を新規発見として再提示しないことを要求している。この抑止は、対象2カードに対応する `evidence_links` / `contradiction_state` がIRに残り、`adjudicated_contradiction()` が検出できることに依存する。

しかし現行 `_detect_contradiction_ir()` は、`cardA` / `cardB` が `doc.cards` にすでに存在すると、その2枚を通常のDocumentカードと同じ扱いで `build_llm_input_ir()` へ渡す。`_apply_truncation()` は `MAX_CARDS=200` を超えると、全カードの中心性順位だけで200枚を選び、選外カードを参照するrelation / island membership / evidence linkを `_prune_references()` で除去する。

したがって、対象2カードが選外になると、カード本文はrouteの直接入力として残っていても、人間が確定した矛盾状態だけがIRから失われる。

## 決定論的な再現条件

外部LLMは不要で、既存の300枚代表規模と同じ考え方で再現できる。

1. `c000`〜`c299` の300カードを作る。
2. 全カードの中心性が同順位になるようring relationを作る。
3. `cardA=c250`、`cardB=c251` とする。
4. `c250 -> c251` に `type="contradicts"`、`contradictionState="confirmed"` または `"held"` のevidence linkを置く。
5. `doc` 付きで `_detect_contradiction_ir()` を実行する。

現行の順位規則では同順位時にcard id昇順となるため、`MAX_CARDS=200` では `c000`〜`c199` が残り、`c250` / `c251` は選外になる。両端点が消えるため当該evidence linkもIRから除外される。

この状態で `adjudicated_contradiction(ir, "c250", "c251")` は人間の確定判断を見つけられず、routeはLLM呼び出し側へ進み得る。

## なぜP1か

これは「IRに存在する全情報を全routeへ渡したい」というR15の一般化とは異なる。

`detect-contradiction` にとって対象2カードと、その2枚に対する `confirmed` / `held` の矛盾状態は、`AI-IR-PROJECTION-01` AC-1が明示した**route固有の必要意味**である。これを規模上限で失うと、人間がすでに下した判断をAIが新規提案として再提示し得る。

KJ Atlasのproposal-only / human-in-the-loop境界に直接関わるため、token予算全体の最終決定を待たず、対象カードの保持方法を先に固定してよい。

## 対応方針

第一候補は、IRビルダーへ「このtaskで必ず保持する対象カード」を明示できる決定論的な入力を追加することとする。

- `detect-contradiction` は `cardA.id` / `cardB.id` をrequired/focus cardとして渡す。
- `MAX_CARDS` 超過時はrequired/focus cardを先に確保し、残り枠を既存の中心性順位で埋める。
- required/focus card同士を結ぶevidence / relationは、参照整合の範囲で保持する。
- required/focus cardがDocument外から追加された既存互換経路も維持する。
- 通常のrouteでrequired/focus指定が無い場合、現行の決定論的投影結果を変えない。
- global `MAX_CARDS` 自体は本Issueでは変更しない。

汎用引数として実装する場合は、将来ほかのtaskが対象カードを必要とするときにも再利用できる形にする。ただし「重要カード」をAIが選ぶ一般機構へ拡張しない。required/focusはroute契約が明示した対象だけに限定する。

## 受入条件

- [ ] 300カード規模で `cardA` / `cardB` が通常の中心性選択では200枚の外に出る場合でも、2枚がIRに残る。
- [ ] 上記2枚を結ぶ `contradicts + confirmed` / `contradicts + held` がIRに残り、`adjudicated_contradiction()` が検出する。
- [ ] `/ai/detect-contradiction` は上記ケースでLLMを呼ばず、`alreadyRecorded=true` を返す。
- [ ] `unconfirmed` / `resolved` は従来どおりLLMへ進む。
- [ ] required/focus指定が無いIR生成では、既存fixtureのcanonical JSON / SHA-256を変えない。
- [ ] `MAX_CARDS`、SafeMode二層、PII最小化、structured-text-onlyを変更しない。
- [ ] 同一入力と同一focus集合から同一IRを得る決定性を維持する。
- [ ] `llm_input_ir_spec.md` §5に、task-required focusを切り詰めより先に保持する規則と、残り枠の決定方法を明記する。
- [ ] backend integration testで300枚規模の再発を防止する。

## 完了境界

本Issueは `detect-contradiction` の対象カードと、その対象に対する人間の確定判断が切り詰めで失われないところまでを扱う。

300枚全体の意味保存戦略、named providerのtoken予算、`suggest-card-groups` / `suggest-layout` / `generate-narrative` の全scale remediationは `AI-IR-SCALE-01` に残す。
