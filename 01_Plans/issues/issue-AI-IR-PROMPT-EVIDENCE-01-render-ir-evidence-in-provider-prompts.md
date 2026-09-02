# Issue: AI-IR-PROMPT-EVIDENCE-01 IRに残った根拠をprovider promptへ渡す

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug / AI Input Projection
- Status: Open
- Source Issue: `AI-IR-SCALE-01`, `AI-IR-PROJECTION-01`
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/tests/test_ai_route_prompt_coverage.py`, `03_Implement/backend/scripts/measure_ai_route_prompt_coverage.py`
- Related ADR/Spec: `ADR-0069`, `02_Architecture/llm_input_ir_spec.md`, `issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md`
- Expected verification level: unit

## 課題

`AI-IR-SCALE-01` の代表規模計測を、共有LLM入力IRだけでなくproviderへ実際に送る最終promptまで進めたところ、`suggest-card-groups` と `suggest-layout` で別種のcoverage lossを確認した。

300カード・30島に、各島1件ずつ計30件の `contradicts` evidence linkを置いた決定論的な入力では、`MAX_CARDS=200` によりIRへ残るevidence linkは20件だった。

この20件について最終promptを測ると、次の差がある。

| route | source | IRに残る | 最終promptで見える |
| --- | ---: | ---: | ---: |
| `suggest-card-groups` | 30 | 20 | **0** |
| `suggest-layout` | 30 | 20 | **0** |
| `generate-narrative` | 30 | 20 | **20** |

最初の `30 -> 20` は `AI-IR-SCALE-01` が扱う規模上限の問題である。一方、`suggest-card-groups` / `suggest-layout` の `20 -> 0` は、IRに保持できた情報をprompt rendererがproviderへ渡していない経路欠落であり、規模上限とは分けて直せる。

provider transportが送信する本体は `LLMRequest.prompt` であり、`LLMRequest.inputs` にevidenceが存在するだけではモデルへ意味が届いたことにならない。

## なぜP1か

KJ Atlasの一次利用仕事では、カード本文だけでなく、根拠、矛盾、保留、異論など、人間が後から与えた意味のつながりを失わないことを中核価値としている。

`generate-narrative` はすでにIRのevidence linkをtyped relationとして最終promptへ描画している。したがって必要なのは新しいスキーマや新しい判断体系ではなく、移行済みroute間でproviderへの意味伝達を揃える小さな修正である。

この欠落を残したままStage 5を広げると、「`inputs=` が付いているからIR移行済み」という構造上の判定と、実際にproviderへ意味が届くかが乖離する。そのため、Stage 5の拡大より先に修正する。

## 対応方針

- `suggest-card-groups` のIR contextへ、IRに残った `evidence_links` を明示的に描画する。
- `suggest-layout` の構造contextへ、IRに残った `evidence_links` を明示的に描画する。
- 表現は `generate-narrative` がすでに用いているtyped evidence表現と意味を揃える。
  - `from_card_id`
  - evidence `type`
  - `to_card_id`
  - `contradiction_state` がある場合はその状態
- `LLMRequest.inputs`、SafeMode、proposal-only境界、出力スキーマは変更しない。
- `_MAX_*` 上限は本Issueでは変更しない。`30 -> 20` の規模coverage lossは `AI-IR-SCALE-01` に残す。
- Stage 5の残る7経路は本Issueで移行しない。

## 受入条件

- [ ] evidenceを含む代表入力で、`suggest-card-groups` の最終promptに、IRへ残ったevidence linkがすべてtyped evidenceとして現れる。
- [ ] evidenceを含む代表入力で、`suggest-layout` の最終promptに、IRへ残ったevidence linkがすべてtyped evidenceとして現れる。
- [ ] `generate-narrative` の既存evidence描画を壊さない。
- [ ] 30件のsource evidenceのうちIRへ20件だけ残る代表規模では、3 routeすべてが「source 30 / IR 20 / prompt 20」となり、規模上限による欠落とrendererによる追加欠落を区別できる。
- [ ] `MAX_CARDS`、token予算、Stage 5対象routeを変更しない。
- [ ] SafeMode二層、structured-text-only、proposal-onlyの既存境界を弱めない。
- [ ] backend unit / lint / DB matrixを含む通常CIが成功する。

## 検証計画

- `03_Implement/backend/tests/test_ai_route_prompt_coverage.py` のevidence scenarioを回帰契約にする。
- `03_Implement/backend/scripts/measure_ai_route_prompt_coverage.py` でsource / IR / final promptの3層を再計測する。
- 既存backend全体CIを通す。

## 完了境界

本Issueはrendererの追加欠落 `20 -> 0` の解消だけでDoneにする。`MAX_CARDS` による `30 -> 20` を同時に解決したことにはしない。

named providerの正確なtoken観測と、大規模入力での意味保存型投影戦略は引き続き `AI-IR-SCALE-01` の未完事項である。
