# Issue: AI-IR-CHECK-NARRATIVE-RELATIONS-01 `check-narrative` でA型のrelation構造を失わない

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Architecture / AI Integration
- Status: Done
- Source Issue: `AI-IR-STAGE5-SCOPE-01`, `AI-IR-SCALE-01`
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/tests/test_ai_prompt.py`, `03_Implement/backend/scripts/measure_ai_route_provider_tokens.py`, `02_Architecture/api.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`, `00_Prompt/kj_technique.md` §5–§6, `AI-IR-SCALE-01`, `AI-IR-STAGE5-SCOPE-01`
- Expected verification level: integration

## 課題

`POST /ai/check-narrative` はA型図解とB型文章の双方向照合を行う。現行promptはNarrative本文、reading order、全Island、全Cardをproviderへ渡しており、300カード・30島の代表入力でも末尾までcoverageを保っている。

一方、A型図解の `Edge` はprovider promptへ渡していない。このため、カードと島がすべて見えていても、A型に記録された `causal` / `negate` / `mutual` / `equivalence` / `related` 等の論理接続をAIが参照できない。

`00_Prompt/kj_technique.md` §5はA型/B型を両方向に照合することを要求し、§6の `KJT-SIGN-09` は「B型がA型より論理的に整いすぎている（図にない接続詞で補っている）」ことを失敗徴候として扱う。したがって、relation graphは「IRに存在するから全部渡す」という理由ではなく、**B型がA型にない因果・対立・同値等を作っていないかを判定するためのroute-required meaning**である。

この欠落はscale問題とは分けて扱う。固定上限へ縮約する前に、現行の全Card・全Island coverageを保ったまま、A型の明示的なrelationをproviderへ届ける。

## route-required meaning

### 必須

- Narrative本文
- `basedOnReadingOrder` またはDocumentの `readingOrder`
- 全Cardの `id` と本文
- 全Islandの `id`、title、member card ID
- Documentに明示された全 `Edge`
  - `id`
  - `type`
  - `fromKind` / `fromId`
  - `toKind` / `toId`

`fromKind` / `toKind` が旧Document互換のため未指定の場合は、現行domain契約と同じくcard endpointとして解釈する。prompt上では解釈後のkindを明示し、曖昧なendpointをprovider側へ委ねない。

### 今回は必須扱いしない

- 座標
- critique
- `evidenceLinks`

`evidenceLinks`、特に `contradicts` は意味保存上重要だが、A型/B型の論理構造照合における必須性は `Edge` と同一ではない。今回のrelation欠落修正へ便乗して契約を広げず、必要性を別に判定する。

## 実装方針

1. 現行promptの全Card・全Island・reading orderを維持する。
2. `Relations:` 節を追加し、Documentの全Edgeを決定論的な順序・形式で描画する。
3. prompt指示に、Narrativeの因果・対立・同値等をA型のrelation graphと照合し、図にない接続を `b_missing_in_a` として検討することを明示する。
4. response schema、`counts`、reference validationは変更しない。
5. generic Document IRの200カード上限へはまだ移さない。全体被覆を維持する方式は `AI-IR-SCALE-01` のnamed provider/model実測後に決める。
6. relation追加後にtoken計測dry-runを再実行し、文字数/UTF-8 byte数を診断値として更新する。これをtoken数へ換算しない。
7. 内容確定後、自然な日本語としてIssue/API文書を読み直す。

## 受入条件

- [x] `check-narrative` promptに全EdgeのID、type、endpoint kind、endpoint IDが含まれる。
- [x] card→cardだけでなく、island→island / card→island等の明示Edgeも同じ契約で保持する。
- [x] kind未指定のlegacy edgeはcard endpointとして決定論的に描画する。
- [x] promptがA/B双方向照合にrelation graphを使うことを明示する。
- [x] 既存のNarrative、reading order、全Card、全Island coverageを維持する。
- [x] response形、direction counts、reference validationを変更しない。
- [x] relation追加後のprovider token計測dry-runを更新し、診断値を `AI-IR-SCALE-01` へ同期する。
- [x] `02_Architecture/api.md` と `AI-IR-STAGE5-SCOPE-01` を実装結果へ同期する。
- [x] SafeMode、proposal-only、provider kill switch等の既存境界を変更しない。
- [x] 最終成果物を、意味を変えず自然な日本語として全文を読み直す。

## 完了境界

このIssueは `check-narrative` をgeneric IRへ形式的に移行することを目的にしない。

**A型図解の全体被覆を保ったまま、その論理接続もB型文章との照合対象へ含め、図にない因果・対立等を検出するための必要意味がprovider手前で失われないことを回帰で固定するところまで**を完了条件とする。

## 対応記録（2026-09-05・Done）

`03_Implement/backend/src/kj_atlas_api/routes/ai.py` の `_build_narrative_check_prompt()` へ `Relations:` 節を追加した。`payload.doc.edges` の全件を、`fromKind`/`toKind` 未指定時はcard端点として解釈したうえで決定論的に描画し、prompt指示へ「narrative-vs-diagramの論理接続照合にrelation graphを使う」ことを明記した。既存のNarrative本文・reading order・全Card・全Islandの各節は変更していない。

検証:

```
.venv\Scripts\python.exe -m pytest tests/test_ai_check_narrative_required_meaning.py tests/test_ai_prompt.py -q
32 passed

.venv\Scripts\python.exe -m pytest tests/ -k "check_narrative or narrative" -q
59 passed
```

移植した回帰テストの一部（card/island本文をリテラルな日本語で照合するassert）は、`json.dumps` の既定ASCIIエスケープと矛盾しており、本体実装とは無関係に元から誤っていた。`json.dumps(...)` を使って実際のエスケープ形式へ合わせて修正した。

変異検査: `relation_lines` を一時的に空リストへ差し替え、`test_check_narrative_prompt_preserves_full_diagram_relation_graph` が期待どおり失敗することを確認し、復元後に再度全件passを確認した。

`scripts/measure_ai_route_provider_tokens.py --provider deepseek --model deepseek-chat` のdry-runで `check-narrative` のUTF-8 bytesが171,426→198,083へ増えたことを確認し、`AI-IR-SCALE-01`・`02_Architecture/api.md`・`AI-IR-STAGE5-SCOPE-01` へ同期した。SafeMode二層、response schema、`counts`、reference validation、provider kill switchはいずれも変更していない。