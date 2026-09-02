# Issue: AI-IR-PROMPT-EVIDENCE-01 route別promptのevidence差を仕様へ戻って再判定する

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Investigation / AI Input Projection
- Status: Done
- Source Issue: `AI-IR-SCALE-01`, `AI-IR-PROJECTION-01`
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/tests/test_ai_route_prompt_coverage.py`, `03_Implement/backend/scripts/measure_ai_route_prompt_coverage.py`, `02_Architecture/llm_input_ir_spec.md`
- Related ADR/Spec: `ADR-0069`, `02_Architecture/llm_input_ir_spec.md`, `issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md`
- Expected verification level: docs-check

## 結論

PR #2820で観測した数値は有効だが、R15で行った「`suggest-card-groups` / `suggest-layout` の evidence 20→0 はprompt rendererの不具合である」という判定は撤回する。

`llm_input_ir_spec.md` と `AI-IR-PROJECTION-01` の受入条件を再確認すると、LLM入力IRは全フィールドを全routeのpromptへ機械的に複製する契約ではない。各routeは、そのタスクに必要な意味構造をIRから利用する。

- `detect-contradiction` は `evidenceLinks` / `contradictionState` を判断材料として要求する。
- `suggest-card-groups` は既存の島・階層・relation・`holdState` を使い、人間が保留したカードを新規グループへ入れないことを要求する。
- `generate-narrative` は `causal` / `negate` など叙述に必要な論理関係を要求する。
- `suggest-layout` は正規化座標・relation・島構造を要求する。

したがって、IRに `evidence_links` が存在するという理由だけで、`suggest-card-groups` と `suggest-layout` のpromptにも全件を描画すべきだとは言えない。必要性を別途示さずに描画すると、token消費を増やし、route固有の判断材料を曖昧にする可能性もある。

## 観測として残すこと

300カード・30島に各島1件ずつ、計30件のheld contradiction evidence linkを置いた決定論的入力では、次を再現した。

| route | source evidence | IRに残る | 最終promptで見える |
| --- | ---: | ---: | ---: |
| `suggest-card-groups` | 30 | 20 | 0 |
| `suggest-layout` | 30 | 20 | 0 |
| `generate-narrative` | 30 | 20 | 20 |

この表は削除しない。ただし、示しているのは**routeごとのprompt投影差**であり、それ自体は欠陥判定ではない。

一方、`30 -> 20` は `MAX_CARDS=200` によってIRそのものから参照可能な構造が減った結果であり、route固有の必要意味まで失う可能性がある。この規模問題は `AI-IR-SCALE-01` に残す。

## R15で誤った点

R15では、KJ Atlasの一次価値である「根拠・異論・保留・人間の判断を失わない」を重視するあまり、次の二つを暗黙に同一視した。

1. Document/IRに意味情報を保持すること。
2. その全情報を、すべてのAI taskのprovider promptへ描画すること。

前者は中核価値に直接関わるが、後者はtask設計の問題であり自動的には導けない。情報を保持することと、特定の推論taskへ入力することは別の境界である。

この区別を欠いたため、「promptに0件」という測定値から「意味を失わせる実装不具合」へ一段飛躍した。

## 今後のcoverage判定

最終promptのcoverageは、IRの全フィールドとの一致率ではなく、**routeごとに契約上必要な意味集合**に対して評価する。

最低限、次の順序を守る。

1. routeの業務目的と既存ACから、判断に必要な意味フィールドを特定する。
2. source Document → IR → final prompt の各段で、その必要意味がどれだけ保持されるかを測る。
3. 必要意味が落ちたときだけ、不具合またはscale remediation候補として扱う。
4. IRに存在するが当該taskに不要なフィールドがpromptへ現れないことは、単独では欠陥としない。
5. 新たにevidenceが必要だと判断する場合は、先にrouteの意味契約・ACを更新してからrendererを変更する。

## 受入結果

- [x] `30 -> 20 -> 0` の測定値が再現可能な観測として残っている。
- [x] `llm_input_ir_spec.md` と `ADR-0069`、`AI-IR-PROJECTION-01` のroute別契約を再確認した。
- [x] `suggest-card-groups` / `suggest-layout` にevidence描画を要求する現行ACがないことを確認した。
- [x] 「IRに存在する全フィールドを全routeへ描画する」という暗黙要件を採用しないことを明確化した。
- [x] rendererのコード変更を行わない判断へ戻した。
- [x] 規模上限による意味coverageの問題は `AI-IR-SCALE-01` に残した。
- [x] R16継続dogfoodで誤判定の経緯と補正を記録する。

## 完了境界

本Issueは「evidenceをgroups/layoutへ描画する実装」が完了したためDoneなのではない。**追加描画を要求する根拠が現行仕様にはなく、R15での不具合判定を撤回したためDone**とする。

将来、実使用やtask設計から `suggest-card-groups` / `suggest-layout` にevidenceが必要だと示された場合は、このIssueを再利用せず、その利用仕事と必要意味を明示した新しい課題として起票する。
