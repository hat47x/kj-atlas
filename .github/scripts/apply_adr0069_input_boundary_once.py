from pathlib import Path


def replace_once(path: str, before: str, after: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(before)
    if count != 1:
        raise SystemExit(f"{path}: expected one match, found {count}: {before[:140]!r}")
    p.write_text(text.replace(before, after, 1), encoding="utf-8")


adr = "01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md"
stage5 = "01_Plans/issues/issue-AI-IR-STAGE5-SCOPE-01-classify-remaining-ai-input-paths.md"
projection = "01_Plans/issues/issue-AI-IR-PROJECTION-01-llm-input-ir-as-ai-input-path.md"

replace_once(
    adr,
    "- Status: Accepted（2026-08-29、D1=B・D3=A・D4=A 仮承認。利用者からの委譲に基づく暫定決定であり、特別に重大な安全境界変更を伴わないため実行フェーズへ移行。D2は2026-08-13に別途採択済み）",
    "- Status: Accepted（2026-08-29、D1=B・D3=A・D4=A 仮承認。D2は2026-08-13に別途採択済み。2026-09-03にD5=Aを追補し、generic Document IRとtask-local structured inputの適用境界を明確化）",
)

marker = (
    "**決定（2026-08-29・仮承認）**: **D4=A を採択**。サーバ側（Python）にIRビルダーを実装し、"
    "`test_ts_python_contract_drift.py` の対象へ投影ロジックを追加する。\n\n### 仕様バージョンについて"
)
d5 = """**決定（2026-08-29・仮承認）**: **D4=A を採択**。サーバ側（Python）にIRビルダーを実装し、`test_ts_python_contract_drift.py` の対象へ投影ロジックを追加する。

### D5: generic Document IR と task-local structured input の適用境界

Stage 5の棚卸しで、残存経路には次の3種類が混在することが分かった。

1. `DocumentV1` 由来の構造そのものをAIの判断材料にする経路。
2. `DocumentV1` は受け取るが、呼出側がAIへ渡してよいgrounding集合を先に限定している経路。
3. Documentを受け取らず、単一本文や選択済みの概要情報だけを扱う経路。

ここで「すべての `/ai/*` をgeneric Document IRへ通す」ことを目的化すると、2ではgrounding境界を広げ、3では架空IDや疑似Documentを作る逆効果が生じる。したがって、**AI入力を構造化された実経路へ揃えるという原則**と、**`llm_input_ir_spec.md` のgeneric Document IRを使う条件**を分けて決める。

| 案 | 内容 | 評価 |
|---|---|---|
| **A（採択）** | AI入力の構造化・実経路化は全AI経路に要求するが、generic Document IRはDocument由来の構造を仕事上必要とする経路に適用する。限定grounding/no-doc経路はtask-local structured inputを正式な入力契約として認める | 仕事上の意味と安全境界を保ったまま、IR利用そのものを目的化しない |
| B | すべてのAI経路をgeneric Document IRへ統一する | 形式は揃うが、限定groundingを広げたり、no-doc経路へ虚偽の識別子を作る必要が生じる |
| C | 各経路を個別実装のままにし、共通原則を置かない | 実入力の迂回やSafeMode・最小化のばらつきを再び許す |

**決定（2026-09-03・追補）**: **D5=A を採択**。以下を不変条件とする。

- **Document-backed structured task**: 文書のカード・島・relation・evidenceなど、`DocumentV1` 由来の構造が仕事上の判断材料になる経路は、generic Document IRまたはそのroute固有投影をprovider実入力の正本とする。Document生値から同じ意味をpromptへ迂回させない。
- **Caller-limited grounding task**: 呼出側が `groundingCardIds` / `groundingEdgeIds` などで許可集合を明示する経路では、そのallowlistを安全境界の正本とする。generic Document IRを検査・正規化に併用してもよいが、最終promptや `LLMRequest.inputs` の実効意味集合をallowlistより広げてはならない。
- **No-document task**: Documentや実在IDを持たない経路では、generic Document IRへ合わせるための疑似Document・架空カードID・架空島IDを作らない。明示的なtask-local structured inputを正式なAI入力契約とし、provider promptはその構造化入力から描画する。
- **共通の安全境界**: generic Document IRを使わない経路も、レビュー状態、SafeMode、PII最小化、structured-text-only、決定論的な入力上限など、その入力型に適用可能な境界保護から免除されない。必要な保護はAPI境界またはtask-local入力ビルダーでfail-closedにする。
- **契約変更時の再判定**: no-doc経路が将来 `DocumentV1` を受け取る仕事へ変わる場合は、既存の例外を暗黙に継承せず、request契約の変更時点でgeneric Document IR適用を再判定する。
- **完了指標**: 11/11をgeneric Document IRへ揃えること自体を完了条件にしない。各AI経路について「何がproviderの実入力正本か」「何を送らないか」「どの境界でfail-closedにするか」が明示され、promptがその契約を迂回しないことを完了条件とする。

この追補により、`summarize-island-relation` はcaller-limited grounding task、`refine-card-text` と `suggest-document-title` はno-document taskとして扱う。これらは「未移行だから放置する経路」ではなく、**generic Document IRを適用しないこと自体が意味保存のための明示的な設計判断**である。

### 仕様バージョンについて"""
replace_once(adr, marker, d5)

replace_once(
    adr,
    "| **機能設計** | 既存の4投影層（island_edge_aggregate/abstract_map_export/ContextBundle/LLMRequest.inputs IR）のうちIRを実装してAI経路へ接続。`POST /ai/*`はIRを経由し、直渡し経路にエンドポイントを積み上げない | 業務: 採点API（assess-card-importance）は廃止済み（issue-AI-IMPORTANCE-SCORING-01）。データ: 座標はsuggest-layoutの出力に限定し、島を矩形でなく関係の集合として提示 |",
    "| **機能設計** | Document由来の構造を扱うAI経路はgeneric Document IRを実入力へ接続する。caller-limited grounding/no-doc経路はtask-local structured inputを正式契約とし、provider promptがその構造化入力を迂回しないようにする | 業務: 経路ごとの仕事に必要な意味と許可範囲を先に固定する。データ: 座標は必要な経路だけに限定し、限定groundingやno-doc入力をgeneric IRの都合で広げない |",
)
replace_once(
    adr,
    "- 既存の `/ai/*` 呼び出し側（フロントエンド、`kj_canvas_demo.py`）に改修が要る。",
    "- generic Document IRの対象となる既存AI経路では呼び出し側やprompt構築の改修が要る。task-local structured inputを採る経路では、既存の限定入力を広げず、実際にproviderへ送る内容との一致を回帰で固定する必要がある。",
)
replace_once(
    adr,
    "将来的に IR 経路が全 `/ai/*` を覆った段階で、`ADR-0068` 由来の実装を退役させるかどうかは別途判断する（本ADRの実装時点では判断しない）。",
    "将来的にすべてのAI経路がgeneric Document IRまたは明示的なtask-local structured inputの実経路で覆われた段階で、`ADR-0068` 由来のAPI境界実装を退役させるかどうかは別途判断する。本ADRの実装時点では二層防御を維持する。",
)
replace_once(
    adr,
    "3. `/ai/*` の各エンドポイントを IR 経由へ切り替える。段階適用の場合は論理関係が効く順（`detect-contradiction` → `suggest-card-groups` → `generate-narrative` → `suggest-layout`）を推奨する。",
    "3. 各AI経路をD5の3分類へ当てはめる。Document由来の構造を扱う経路はgeneric Document IRへ、caller-limited grounding/no-doc経路は明示的なtask-local structured inputへ揃える。いずれもprovider promptが宣言済み入力契約を迂回しないことを回帰で固定する。",
)
replace_once(
    adr,
    "- Related: `01_Plans/issues/issue-AI-IR-PROJECTION-01-llm-input-ir-as-ai-input-path.md`（本ADR採択後の実装課題）",
    "- Related: `01_Plans/issues/issue-AI-IR-PROJECTION-01-llm-input-ir-as-ai-input-path.md`（本ADR採択後の実装課題）\n- Related: `01_Plans/issues/issue-AI-IR-STAGE5-SCOPE-01-classify-remaining-ai-input-paths.md`（D5追補の根拠となった経路棚卸し）",
)

replace_once(
    stage5,
    "### ADR-0069の適用範囲を確認してから扱う\n\n5. `summarize-island-relation`\n6. `refine-card-text`\n7. `suggest-document-title`\n\nこれらをgeneric document IRへ無理に寄せず、明示的な例外またはtask-local structured inputを許すかをADR-0069側で確認する。特にno-doc 2経路へ疑似Documentを作る実装は採らない。",
    "### task-local structured inputとして境界確定\n\n5. `summarize-island-relation` — caller-limited grounding task。`groundingCardIds` / `groundingEdgeIds` のallowlistを実効入力の上限とし、generic Document IRを併用しても最終promptを広げない。\n6. `refine-card-text` — no-document task。疑似Documentや架空IDを作らず、単一本文＋任意contextのtask-local structured inputを正式契約とする。\n7. `suggest-document-title` — no-document task。呼出側が選んだ島タイトル・本文サンプルのtask-local structured inputを正式契約とし、generic Document IRへ偽装しない。\n\nADR-0069 D5=Aの追補により、この3経路はgeneric Document IRの「未移行」ではなく、別の構造化入力契約を使うことが設計上の正解と確定した。SafeModeやレビュー状態などの共通境界保護は引き続き必要である。",
)
replace_once(
    stage5,
    "3. **次: `summarize-island-relation` / no-doc 2経路について、ADR-0069の適用範囲を短い追補で明確にする。**\n4. `suggest-merges` の利用仕事と受入条件を決める。",
    "3. **完了: `summarize-island-relation` / no-doc 2経路の適用境界をADR-0069 D5=Aで確定した。** generic Document IRを目的化せず、限定groundingはallowlistを維持し、no-doc経路はtask-local structured inputを正式契約とする。\n4. **次: `suggest-merges` の利用仕事と受入条件を決める。**",
)
replace_once(
    stage5,
    "- [ ] ADR-0069にDocument IRの適用範囲とtask-local structured inputの扱いを追補する。",
    "- [x] ADR-0069にDocument IRの適用範囲とtask-local structured inputの扱いを追補する。— D5=Aとして、Document-backed / caller-limited grounding / no-documentの3分類と実入力境界を確定した。",
)

replace_once(
    projection,
    "> **進捗（2026-09-03）: Stage 1〜4は完了し、Stage 5へ着手済み。** `suggest-island-summary` をStage 5の第1経路、`propose-opposing-viewpoint` を第2経路として移行し、現在は11件のLLMRequestのうち6経路がIR経由、残り5経路である。Stage 5では件数を機械的に減らさず、`AI-IR-STAGE5-SCOPE-01` で経路ごとの仕事と入力契約を確認してから移行する。次は限定grounding経路とno-doc経路についてADR-0069の適用範囲を明確にする。AC-7 は Stage 4 で完了し、AC-10は `AI-IR-SCALE-01` へ切り出して継続している。詳細は末尾の各Stage結果を参照。`Status` メタデータの語彙は `Draft` / `Open` / `In Progress` / `Done` に固定されている（`01_Plans/issues/issue_memo_status.py`）ため、段階情報はここに書く。",
    "> **進捗（2026-09-03）: Stage 1〜4は完了し、Stage 5へ着手済み。** `suggest-island-summary` と `propose-opposing-viewpoint` までgeneric Document IRの実入力化を完了し、11件中6経路がDocument IR経由である。残る5経路のうち3経路はADR-0069 D5=Aによりtask-local structured inputを正式契約とする境界が確定したため、「11/11をgeneric Document IRへ揃える」ことは完了条件ではない。未決の実装判断は `suggest-merges` の意味論と `check-narrative` のscale方式である。AC-7 は Stage 4 で完了し、AC-10は `AI-IR-SCALE-01` へ切り出して継続している。詳細は末尾の各Stage結果を参照。`Status` メタデータの語彙は `Draft` / `Open` / `In Progress` / `Done` に固定されている（`01_Plans/issues/issue_memo_status.py`）ため、段階情報はここに書く。",
)
replace_once(
    projection,
    "**2026-09-03更新**: `suggest-island-summary` と `propose-opposing-viewpoint` をStage 5の第1・第2経路としてIRへ移行し、IR経由は6件、未移行は5件になった。未移行経路の分類と次の順序は `AI-IR-STAGE5-SCOPE-01` を正本とする。",
    "**2026-09-03更新**: `suggest-island-summary` と `propose-opposing-viewpoint` をStage 5の第1・第2経路としてgeneric Document IRへ移行し、Document IR経由は6件になった。残る5経路のうち `summarize-island-relation` / `refine-card-text` / `suggest-document-title` はADR-0069 D5=Aでtask-local structured inputを正式契約とする境界を確定した。残る実装判断は `suggest-merges` と `check-narrative` であり、分類と順序は `AI-IR-STAGE5-SCOPE-01` を正本とする。",
)

print("ADR-0069 D5 and Stage 5 input-boundary docs synchronized")
