from pathlib import Path

SCALE = Path("01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md")
STAGE5 = Path("01_Plans/issues/issue-AI-IR-STAGE5-SCOPE-01-classify-remaining-ai-input-paths.md")

scale = SCALE.read_text(encoding="utf-8")
stage5 = STAGE5.read_text(encoding="utf-8")

old = """## R21: 上限引上げ・ルート別投影・分割処理の比較\n"""
insert = """### `check-narrative` を加えたdry-run基準（2026-09-04）

Stage 5で最後に残る `check-narrative` を、R20のprovider token計測ハーネスへ第3の比較対象として追加した。現行production routeをそのまま再現し、IRへ縮約せず、Narrative本文・reading order・30島・300カードを全量promptへ載せる。合成Narrativeは30島を各1行で言及する決定論的な短文とし、Narrative本文だけを恣意的に膨らませない。

外部providerを呼ばないdry-runでは、同じ300カード・30島の代表入力について次の診断値になった。

| route | Unicode文字数 | UTF-8 bytes | 入力方式 |
| --- | ---: | ---: | --- |
| `suggest-layout` | 117,389 | 117,389 | Document + IR構造文脈 |
| `generate-narrative` | 89,321 | 89,322 | reading order + IR論理骨格 |
| `check-narrative` | 168,905 | 171,426 | 現行の全量prompt |

この表は**token数ではない**。文字数・byte数はprompt規模の診断情報としてのみ使い、model固有token数へ換算しない。正確な入力token数は、named provider/modelが返す `usage` だけを採用するというR20の境界を維持する。

`check-narrative` は末尾の `c299` と `i29` までpromptへ含み、現行方式では300カード・30島のcoverageを切り落としていない。一方、dry-runのUTF-8 byte数は比較3ルート中で最大だった。したがって、Stage 5完了のために固定IR上限へ無理に押し込むのではなく、named provider/modelで実token数を測ったうえで、全量を保つA2と、全体被覆を壊さない分割・階層処理Cを主な比較対象とする。実測前にproduction上限や `check-narrative` の入力方式は変更しない。

計測スクリプトはIssue本文に記載した直接CLI形式でも動くよう修正し、直接実行のdry-runを回帰テストへ追加した。外部送信には引き続き `--execute` と `KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1` の二重opt-inを要求する。

## R21: 上限引上げ・ルート別投影・分割処理の比較
"""
if scale.count(old) != 1:
    raise SystemExit(f"AI-IR-SCALE-01 insertion marker count={scale.count(old)}")
scale = scale.replace(old, insert, 1)
SCALE.write_text(scale, encoding="utf-8")

stage_marker = """## 受入条件\n"""
stage_insert = """## 2026-09-04: `check-narrative` のtoken計測基準を追加

`AI-IR-SCALE-01` のR20ハーネスへ `check-narrative` を追加し、`suggest-layout` / `generate-narrative` / `check-narrative` を同じ300カード・30島の合成入力で比較できるようにした。

現行 `check-narrative` はIRを介さず全300カード・全30島をprovider promptへ載せており、dry-runでは末尾要素までcoverageが残ることを確認した。ただしpromptのUTF-8 byte数は171,426で、比較3ルートの中で最大だった。この値はtoken数ではない。named provider/modelの `usage` による正確な入力token実測が終わるまでは、全量方式が安全に収まるとも、分割が必要とも断定しない。

したがって本Issueの未完境界は変わらない。`check-narrative` を形式的にgeneric IRへ移すのではなく、`AI-IR-SCALE-01` で実token予算を確認し、A/B双方向の全体照合を失わない方式を選んだ後に実装する。

## 受入条件
"""
if stage5.count(stage_marker) != 1:
    raise SystemExit(f"AI-IR-STAGE5-SCOPE-01 insertion marker count={stage5.count(stage_marker)}")
stage5 = stage5.replace(stage_marker, stage_insert, 1)
STAGE5.write_text(stage5, encoding="utf-8")

print("check-narrative token baseline docs synchronized")
