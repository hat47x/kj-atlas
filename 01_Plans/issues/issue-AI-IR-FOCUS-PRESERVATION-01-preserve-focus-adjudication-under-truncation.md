# Issue: AI-IR-FOCUS-PRESERVATION-01 切り詰め時も対象カードと人間の確定判断を保持する

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug / AI Input Projection
- Status: In Progress
- Source Issue: `AI-IR-SCALE-01`, `AI-IR-PROJECTION-01`
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/llm_input_ir.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/tests/test_ai_detect_contradiction_ir.py`, `02_Architecture/llm_input_ir_spec.md`
- Related ADR/Spec: `ADR-0069`, `02_Architecture/llm_input_ir_spec.md` §2.2B / §5, `AI-IR-PROJECTION-01` AC-1, `AI-IR-SCALE-01`
- Expected verification level: integration

## 課題

R16で定めた「routeごとに必要な意味集合を先に確認する」という基準で `detect-contradiction` を見直すと、300枚規模でAC-1を破り得る切り詰め経路がある。

`detect-contradiction` のAC-1は、人間がすでに `confirmed` / `held` とした矛盾を新規発見として再提示しないことを要求している。この抑止は、対象2カードに対応する `evidence_links` / `contradiction_state` がIRに残り、`adjudicated_contradiction()` が検出できることに依存する。

しかし修正前の `_detect_contradiction_ir()` は、`cardA` / `cardB` が `doc.cards` にすでに存在すると、その2枚を通常のDocumentカードと同じ扱いで `build_llm_input_ir()` へ渡していた。`_apply_truncation()` は `MAX_CARDS=200` を超えると全カードの中心性順位だけで200枚を選び、選外カードを参照するrelation / island membership / evidence linkを `_prune_references()` で除去するため、対象2カードが選外になると、人間が確定した矛盾状態だけがIRから失われ得た。

## 決定論的な再現条件

外部LLMは不要で、既存の300枚代表規模と同じ考え方で再現できる。

1. `c000`〜`c299` の300カードを作る。
2. 全カードの中心性が同順位になるようring relationを作る。
3. `cardA=c250`、`cardB=c251` とする。
4. `c250 -> c251` に `type="contradicts"`、`contradictionState="confirmed"` または `"held"` のevidence linkを置く。
5. `doc` 付きで `_detect_contradiction_ir()` を実行する。

修正前の順位規則では同順位時にcard id昇順となるため、`MAX_CARDS=200` では `c000`〜`c199` が残り、`c250` / `c251` は選外になった。両端点が消えるため当該evidence linkもIRから除外され、`adjudicated_contradiction()` が人間の確定判断を見つけられない状態を作れた。

## なぜP1か

これは「IRに存在する全情報を全routeへ渡したい」という一般化とは異なる。

`detect-contradiction` にとって対象2カードと、その2枚に対する `confirmed` / `held` の矛盾状態は、`AI-IR-PROJECTION-01` AC-1が明示した**route固有の必要意味**である。これを規模上限で失うと、人間がすでに下した判断をAIが新規提案として再提示し得る。

KJ Atlasのproposal-only / human-in-the-loop境界に直接関わるため、token予算全体の最終決定を待たず、対象カードの保持方法を先に固定する。

## 対応方針

IRビルダーへ、route契約上どうしても保持しなければならないカードを明示する `required_card_ids` を追加する。

- `detect-contradiction` は `cardA.id` / `cardB.id` をrequired cardとして渡す。
- `MAX_CARDS` 超過時はrequired cardを先に確保し、残り枠を既存の中心性順位で埋める。
- required card同士を結ぶevidence / relationは、参照整合の範囲で保持する。
- required cardがDocument外から追加された既存互換経路も維持する。
- required指定が無い場合、従来の決定論的投影結果を変えない。
- `MAX_TEXT_CHARS` のため追加のカード除外が必要な場合も、required cardは除外候補にしない。required cardだけで予算を超える場合は、意味を黙って落とさず `required_card_budget_exceeded` でfail-closedする。
- global `MAX_CARDS` / `MAX_RELATIONS` / `MAX_TEXT_CHARS` 自体は本Issueでは変更しない。

`required_card_ids` は「重要そうなカード」をAIが選ぶ機構ではない。route契約が対象を明示できる場合だけ使う入力専用の制約であり、IRへ新しいフィールドとして直列化しない。

## 実装結果（2026-09-03）

R18で共有IRビルダーへ `required_card_ids` と回帰テストを導入し、commit `3ba7fb06149b7713cd6be248c01087317408a0f9` でmainへ統合した。その後、`/ai/detect-contradiction` が `cardA.id` / `cardB.id` を実際に渡す配線と300カード規模のintegration regressionを PR #2827 で追加し、commit `efa55e25ff72c5e115fdbc1368366a295efc7431` としてmainへ統合した。

実装上は次を満たしている。

- required指定なしと `required_card_ids=()` は同一IR SHA-256になることを固定した。
- `c298` / `c299` のように通常の上位200枚から外れる対象pairでも、required指定により両方を保持する。
- 両端点が残ることで `confirmed` / `held` の `evidence_links` も参照整合を保ったまま残る。
- `confirmed` / `held` は `/ai/detect-contradiction` からLLMへ再送せず、`alreadyRecorded=true` として返す。
- `unconfirmed` / `resolved` は従来どおりLLMへ進み、その場合も対象pairとevidenceをIR / promptに保持する。
- Document外からroute入力として渡された対象カードをIR sourceへ補完する既存互換経路も維持する。
- required集合の順序を入れ替えても同一IR SHA-256を得る決定性を固定した。

回帰の主な所在は次のとおり。

- `03_Implement/backend/tests/test_llm_input_ir_required_cards.py`
- `03_Implement/backend/tests/test_ai_detect_contradiction_ir_scale.py`
- `03_Implement/backend/tests/test_ai_route_required_meaning_scale.py`

GitHub Actionsは現在リポジトリ側で無効化されており、merge commitにもstatus checkは付いていない。このため、本Issueでは「テストコードがmainへ統合された」ことと「CIで実行成功した」ことを混同しない。外部CIの再有効化を本Issueの完了条件には追加しないが、実行可能な環境で当該integration regressionを一度通した記録は完了記録へ残す。

## 仕様への反映（2026-09-03）

`02_Architecture/llm_input_ir_spec.md` §5.2 / §5.2.1 に、実装済みの `required_card_ids` 契約を規範として反映した。あわせて §7.4 に「入力専用制約でありIRの直列化スキーマを変えないため `ir_version=1.2` を維持する」こと、§8 に本Issueへのトレーサビリティを追記した。反映commitは `6fffa38ab2469e53a7fdfcc587799e7d86cde278`。

仕様では次を固定した。

1. callerはroute契約上必須のカードID集合を入力専用の `required_card_ids` としてIRビルダーへ渡してよい。これはIRの直列化フィールドではない。
2. required集合は正規化済みカード集合の部分集合でなければならず、欠落時は `required_card_missing` でfail-closedする。
3. required集合の件数が `MAX_CARDS` を超える場合は `required_card_budget_exceeded` でfail-closedする。
4. `MAX_CARDS` 超過時はrequired集合を先に保持し、残りの `MAX_CARDS - len(required)` 枠を、切り詰め前に一度だけ計算した `centrality.rank` の昇順で埋める。
5. required指定が空の場合は従来の `rank <= MAX_CARDS` と同じ結果を得る。
6. `MAX_TEXT_CHARS` の固定240文字化後になおカード除外が必要な場合、required cardはvictimに選ばない。required cardだけでtext予算を超える場合は `required_card_budget_exceeded` とし、required意味を黙って削除しない。
7. カード除外後のrelation / island membership / evidence linkの参照整合規則は従来どおり適用する。required card同士を結ぶ参照は両端点が残る限り保持される。
8. `required_card_ids` は入力専用でIR schemaを変更しないため、この規則追加だけでは `ir_version` を繰り上げない。

## 受入条件

- [x] 300カード規模で `cardA` / `cardB` が通常の中心性選択では200枚の外に出る場合でも、2枚がIRに残る。
- [x] 上記2枚を結ぶ `contradicts + confirmed` / `contradicts + held` がIRに残り、`adjudicated_contradiction()` が検出できる投影を固定する。
- [x] `/ai/detect-contradiction` は上記ケースでLLMを呼ばず、`alreadyRecorded=true` を返すintegration regressionを備える。
- [x] `unconfirmed` / `resolved` は従来どおりLLMへ進むintegration regressionを備える。
- [x] required指定が無いIR生成では、従来投影と同一SHA-256になる回帰を備える。
- [x] `MAX_CARDS`、SafeMode二層、PII最小化、structured-text-onlyを変更しない。
- [x] 同一入力と同一required集合から同一IRを得る決定性を維持する。
- [x] `llm_input_ir_spec.md` §5に、task-required cardを切り詰めより先に保持する規則、残り枠の決定方法、text予算に収まらない場合のfail-closedを明記する。
- [x] backend integration testで300枚規模の再発を防止するテストケースをmainへ統合する。
- [ ] 実行可能な環境で、共有IR回帰と `/ai/detect-contradiction` の300カードintegration regressionが成功することを記録する。

## 完了境界

本Issueは `detect-contradiction` の対象カードと、その対象に対する人間の確定判断が切り詰めで失われないところまでを扱う。

300枚全体の意味保存戦略、named providerのtoken予算、`suggest-card-groups` / `suggest-layout` / `generate-narrative` の全scale remediationは `AI-IR-SCALE-01` に残す。
