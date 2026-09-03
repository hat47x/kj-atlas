from pathlib import Path


def replace_once(path: Path, before: str, after: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(before)
    if count != 1:
        raise SystemExit(
            f"{path}: expected exactly one match, found {count}: {before[:140]!r}"
        )
    path.write_text(text.replace(before, after, 1), encoding="utf-8")


adr = Path("01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md")
stage5 = Path("01_Plans/issues/issue-AI-IR-STAGE5-SCOPE-01-classify-remaining-ai-input-paths.md")

adr_marker = "## Three-Element Verification（ADR-0067 遡及適用）\n"
adr_addition = '''## Stage 5での適用範囲（2026-09-03追補）

Stage 5で残存経路を棚卸しした結果、本ADRの「IRをAI入力の実経路とする」は、**すべての `/ai/*` を機械的にDocument IRへ通す**という意味ではないことを明確にする。正本にするべきなのは、その仕事に対して人間または呼出側が確定した**構造化入力契約**であり、Document IRはそのうち `DocumentV1` 由来の構造意味を扱うための契約である。

適用境界を次のように固定する。

1. **Document-backedで、Documentのカード・島・relation・evidence等が仕事上の意味になる経路**
   - `llm_input_ir_spec.md` のDocument IRを実入力経路とする。
   - route-required meaningを保護し、必要意味が投影上限で欠ける場合はprovider呼出前にfail-closedにする。
   - provider transportがpromptのみを送る場合も、IRで正規化・保護した本文や構造をpromptへ描画し、Document生値を同じ意味入力へ迂回させない。

2. **Document-backedだが、呼出側がgrounding集合を明示的に限定している経路**
   - 限定groundingはDocument全体より**強い入力境界**として扱う。generic Document IRを使うことで許可集合を広げてはならない。
   - `summarize-island-relation` はこの型である。現行requestは `groundingCardIds` / `groundingEdgeIds` と、それに対応する `cardTexts` / `edgeTexts` を明示し、応答側も同じallowlistの部分集合だけを許可している。
   - 将来IRを併用する場合はhybridとし、IRはSafeMode・関係語彙・参照整合等の検査に利用してよいが、providerへ渡す内容は呼出側が許可したgrounding集合から広げない。永続edge IDとIR relation ID（`type:from:to`）は別物なので、暗黙に置換しない。
   - 現時点では、構造上の具体的な欠落が観測されていないため、IR使用率を上げる目的だけの改修は行わない。

3. **Documentを入力契約に持たないtask-local変換経路**
   - `refine-card-text` と `suggest-document-title` はDocument IRの適用外とする。
   - IRを使うためだけに疑似Document、架空card ID、架空islandを生成しない。追跡可能性のための識別子へ虚偽の由来を持ち込む方が、本ADRの目的に反する。
   - Pydantic request、入力上限、route側SafeMode、model governance等からなるtask-local structured inputを、その経路の実入力契約として維持する。
   - 複数のno-doc経路で共通の入力ガバナンス不足が実際に観測された場合に限り、Document IRとは別の共通envelopeを検討する。現時点では新しい抽象層を先回りして作らない。

4. **件数は完了指標にしない**
   - 「11経路中何件がDocument IRを持つか」は移行状況の説明には使えるが、品質KPIや完了条件にはしない。
   - 明示的な限定grounding契約やno-doc task-local契約を、形式上の11/11達成のためにDocument IRへ偽装しない。

したがってStage 5以降の「AI入力の実経路」は、**そのrouteで採択された構造化入力契約からprovider-bound contentを描画し、その契約を生入力が迂回しないこと**を共通原則とする。Document IRは重要な実装だが、唯一の入力表現ではない。

'''
replace_once(adr, adr_marker, adr_addition + adr_marker)

replace_once(
    stage5,
    "| `summarize-island-relation` | `DocumentV1` に加え、許可済みgrounding card/edgeとその本文 | 明示された2島、relation type、許可されたgrounding集合 | **別契約またはhybrid候補**。現在の限定済みgrounding集合をgeneric IRで広げない |",
    "| `summarize-island-relation` | `DocumentV1` に加え、許可済みgrounding card/edgeとその本文 | 明示された2島、relation type、許可されたgrounding集合 | **限定grounding契約を維持するhybrid境界（2026-09-03確定）**。generic IRで許可集合を広げない。構造上の具体的欠落が観測されるまでは現行task-local入力を維持 |",
)
replace_once(
    stage5,
    "| `refine-card-text` | 単一カード本文、任意context。Documentなし | 元の意味を保った言い換え、レビュー状態 | **IR例外候補**。現行IRへ入れるには存在しないカードIDや疑似Documentを作る必要がある |",
    "| `refine-card-text` | 単一カード本文、任意context。Documentなし | 元の意味を保った言い換え、レビュー状態 | **Document IR適用外（2026-09-03確定）**。request自体をtask-local structured inputとし、疑似Document・架空IDは作らない |",
)
replace_once(
    stage5,
    "| `suggest-document-title` | 島タイトル列、カード本文サンプル、現在タイトル。Documentなし | 人間側で選ばれた概要情報から複数の同格タイトル候補を作る | **IR例外候補**。現在のtask-localな要約入力をDocument IRへ偽装しない |",
    "| `suggest-document-title` | 島タイトル列、カード本文サンプル、現在タイトル。Documentなし | 人間側で選ばれた概要情報から複数の同格タイトル候補を作る | **Document IR適用外（2026-09-03確定）**。呼出側が選んだ概要情報をtask-local structured inputとして維持し、Document IRへ偽装しない |",
)

replace_once(
    stage5,
    """候補は次の2つに限る。\n\n- **現行のtask-local structured inputを明示的な例外として維持する。**\n- **hybridにする。** IRはSafeMode・関係語彙・参照整合の検査に使うが、最終promptは現在の許可済みgrounding集合だけを描画する。\n\n後者を採る場合も、IRで生成されるrelation idと、入力の永続edge idの対応が必要である。現在のIR relation idは `type:from:to` から生成されるため、`groundingEdgeIds` をそのまま置き換えられない。ここを曖昧にして実装しない。\n""",
    """ADR-0069の2026-09-03追補により、この経路は**限定grounding契約を正本とするhybrid境界**に確定した。\n\n- `groundingCardIds` / `groundingEdgeIds` と対応する `cardTexts` / `edgeTexts` は、Document全体より強いallowlistである。generic IRを使うことで、この集合を広げない。\n- 現行応答がgrounding IDを入力allowlistの部分集合へ制限している境界を維持する。\n- 将来IRを併用する場合も、SafeMode・関係語彙・参照整合等の補助検査に限定し、provider-bound contentは許可済みgrounding集合だけから描画する。\n- IRで生成されるrelation idと永続edge idは同一ではないため、`groundingEdgeIds` をIR relation idへ暗黙置換しない。\n- 現時点では、この限定入力に構造上の具体的欠落が観測されていない。したがってIR使用率を上げるためだけの実装変更は行わない。\n""",
)
replace_once(
    stage5,
    "したがって本経路は、ADR-0069が対象とする「Document由来の構造をAIへ届ける経路」とは性質が異なる。**明示的な例外とするか、document IRとは別のtask-local structured input契約を定義する候補**として扱う。\n",
    "ADR-0069の2026-09-03追補により、本経路は**Document IRの適用外**に確定した。`RefineCardTextRequest` 自体をtask-local structured inputとし、`cardText` / `context` / `textReviewed` / model governanceの現行境界を維持する。IR使用率のために疑似Documentや架空card IDを導入しない。\n",
)
replace_once(
    stage5,
    "この経路も `refine-card-text` と同じく、**明示的な例外またはtask-local structured input候補**とする。もし「タイトル提案でも全Documentの構造を見せたい」という製品要件が生じるなら、先にrequest契約そのものをDocument-backedへ変更するIssueを起票する。\n",
    "ADR-0069の2026-09-03追補により、本経路も**Document IRの適用外**に確定した。現在の `islandTitles` / `cardTexts` / `currentTitle` は呼出側が選んだ概要情報であり、このtask-local structured inputを正本とする。もし「タイトル提案でも全Documentの構造を見せたい」という製品要件が生じるなら、その時点でrequest契約をDocument-backedへ変更するIssueを起票し、IR適用を再判定する。\n",
)

replace_once(
    stage5,
    """### ADR-0069の適用範囲を確認してから扱う\n\n5. `summarize-island-relation`\n6. `refine-card-text`\n7. `suggest-document-title`\n\nこれらをgeneric document IRへ無理に寄せず、明示的な例外またはtask-local structured inputを許すかをADR-0069側で確認する。特にno-doc 2経路へ疑似Documentを作る実装は採らない。\n""",
    """### ADR-0069の適用境界を確定済み\n\n5. `summarize-island-relation` — 限定grounding契約を正本とするhybrid境界。generic Document IRで許可集合を広げない。\n6. `refine-card-text` — Document IR適用外。task-local structured inputを正本とする。\n7. `suggest-document-title` — Document IR適用外。呼出側が選んだ概要情報をtask-local structured inputとして扱う。\n\nこの3経路を形式上のIR移行件数へ含めるためだけの改修は行わない。Stage 5の完了はDocument IRの11/11達成ではなく、各routeで採択された構造化入力契約をprovider-bound contentが迂回しないことによって判断する。\n""",
)
replace_once(
    stage5,
    "3. **次: `summarize-island-relation` / no-doc 2経路について、ADR-0069の適用範囲を短い追補で明確にする。**\n4. `suggest-merges` の利用仕事と受入条件を決める。",
    "3. **完了: `summarize-island-relation` / no-doc 2経路について、ADR-0069の適用範囲を追補した。** 限定groundingはgeneric IRより強い境界として維持し、no-doc 2経路はDocument IR適用外とした。\n4. **次: `suggest-merges` の利用仕事と受入条件を決める。**",
)
replace_once(
    stage5,
    "- [ ] ADR-0069にDocument IRの適用範囲とtask-local structured inputの扱いを追補する。",
    "- [x] ADR-0069にDocument IRの適用範囲とtask-local structured inputの扱いを追補する。— Document-backed構造経路、限定grounding経路、no-doc task-local経路を分け、IR化件数を完了指標にしないことを明記した。",
)

for path, needles in {
    adr: [
        "## Stage 5での適用範囲（2026-09-03追補）",
        "限定groundingはDocument全体より**強い入力境界**",
        "Document IRの適用外",
        "件数は完了指標にしない",
    ],
    stage5: [
        "限定grounding契約を維持するhybrid境界（2026-09-03確定）",
        "Document IR適用外（2026-09-03確定）",
        "ADR-0069の適用境界を確定済み",
        "IR化件数を完了指標にしない",
    ],
}.items():
    body = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in body:
            raise SystemExit(f"post-update assertion failed: {path}: {needle}")

print("ADR-0069 Stage 5 applicability synchronized")
