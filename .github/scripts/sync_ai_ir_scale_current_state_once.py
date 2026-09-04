from pathlib import Path

SCALE = Path("01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md")
STAGE5 = Path("01_Plans/issues/issue-AI-IR-STAGE5-SCOPE-01-classify-remaining-ai-input-paths.md")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


scale = SCALE.read_text(encoding="utf-8")
scale = replace_once(
    scale,
    "| `generate-narrative` | `readingOrder` の完全な順序、および叙述の論理骨格となるcard-to-cardの `causal` / `negate`。明示されたisland-to-island edgeも従来文脈として維持する | `readingOrder` とisland edgeはDocumentからpromptへ。card relationはIRからpromptへ入り、`causal` / `negate` はreading-order上の位置へ写像する | **未解消。** 末尾島はreading orderに残る一方、そのカード間の `causal` / `negate` がIRで落ち、provider手前でも骨格が消える |",
    "| `generate-narrative` | `readingOrder` の完全な順序、および叙述の論理骨格となるcard-to-cardの `causal` / `negate`。明示されたisland-to-island edgeも従来文脈として維持する | `readingOrder` とisland edgeはDocumentからpromptへ。card relationはIRからpromptへ入り、`causal` / `negate` はreading-order上の位置へ写像する | **必要な論理骨格は解消済み。** `AI-IR-NARRATIVE-SPINE-01` / PR #2887で、正規化可能なcard-to-card `causal` / `negate` の両端をrequired cardとして保護し、300カードの末尾関係までIRと最終promptへ残す回帰を固定した。required cardだけで上限を超える場合はfail-closedする。`MAX_RELATIONS` を超える規模やtoken予算は本Issueに残る |",
    "generate-narrative R19 row",
)

scale = replace_once(
    scale,
    "3. 少なくとも次をnamed model/providerで実測する。**R20で実測ハーネスを用意した。実providerでの測定値そのものは未取得。**",
    "3. 少なくとも次をnamed model/providerで実測する。**R20で実測ハーネスを用意した。2026-09-04にGitHub Actionsの認証情報有無だけを確認したが、`KJ_ATLAS_DEEPSEEK_API_KEY` は未設定だったため、外部送信は行わず、実providerでの測定値そのものは未取得のままである。**",
    "measurement prerequisite",
)

scale = replace_once(
    scale,
    "## R21: 上限引上げ・ルート別投影・分割処理の比較",
    "## 2026-09-04: named provider実測の実行可能性確認\n\nR20のハーネスを実際のnamed providerへ送れるか確認するため、branch-onlyのGitHub Actions Run `33875031314` で `KJ_ATLAS_DEEPSEEK_API_KEY` の**有無だけ**を検査した。secretの値は取得・出力していない。結果は未設定だった。\n\nこのため、合成データであっても外部providerへのrequestは送っていない。provider-reported usageもまだ得られていないので、上記の文字数・UTF-8 byte数をtoken数へ読み替えず、最初の2つの受入条件は未完了のまま維持する。probe用workflowは同じ成功run内で削除した。\n\n次に実測を行う条件は、計測対象として明示したprovider/modelの認証情報が安全な実行環境へ設定されていることである。その条件が満たされた後も、既存の `--execute` と `KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1` の二重opt-inを維持し、利用者データではなく決定論的な合成データだけを送る。\n\n## R21: 上限引上げ・ルート別投影・分割処理の比較",
    "provider probe section",
)

scale = replace_once(
    scale,
    "3. `generate-narrative` は、必要な `causal` / `negate` の両端をBで十分小さく保護できるかを確認し、文書規模へ膨らむ場合はCを比較する。",
    "3. `generate-narrative` の `causal` / `negate` 両端保護は `AI-IR-NARRATIVE-SPINE-01` で完了した。今後はrequired relationが `MAX_RELATIONS` を超える規模やtoken予算まで含めて、A2/B/Cのどれが必要かを実測後に判断する。",
    "next decision narrative step",
)
SCALE.write_text(scale, encoding="utf-8")

stage5 = STAGE5.read_text(encoding="utf-8")
stage5 = replace_once(
    stage5,
    "したがって本Issueの未完境界は変わらない。`check-narrative` を形式的にgeneric IRへ移すのではなく、`AI-IR-SCALE-01` で実token予算を確認し、A/B双方向の全体照合を失わない方式を選んだ後に実装する。",
    "2026-09-04には、R20ハーネスをnamed providerへ実送信できるか確認するため、branch-onlyのGitHub Actions Run `33875031314` で `KJ_ATLAS_DEEPSEEK_API_KEY` の有無だけを検査した。secret値は取得・表示しておらず、結果は未設定だった。このため外部送信とprovider-reported usage取得は行っていない。byte数からtoken数を推定する代替も採らない。\n\nしたがって本Issueの未完境界は変わらない。`check-narrative` を形式的にgeneric IRへ移すのではなく、`AI-IR-SCALE-01` でnamed provider/modelの実token予算を確認し、A/B双方向の全体照合を失わない方式を選んだ後に実装する。",
    "stage5 provider probe note",
)
STAGE5.write_text(stage5, encoding="utf-8")

print("AI IR scale/current Stage 5 documentation synchronized")
