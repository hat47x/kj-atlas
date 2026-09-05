from pathlib import Path

path = Path("01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md")
s = path.read_text(encoding="utf-8")
assert "## R26 — layout C provider usage を明示opt-inで測定可能にする" not in s
s += r'''

## R26 — layout C provider usage を明示opt-inで測定可能にする

R25で `suggest-layout` の階層C候補を30 local + 1 globalの31 requestとして具体化した。一方、R20/R24のnamed provider計測ハーネスは既定で6比較だけを送る契約であり、C候補を無条件に加えると、実測時のprovider call数・費用・待ち時間を6件から37件へ黙って増やしてしまう。そこで、C実測は**追加の明示opt-in**として接続した。

- `build_representative_requests()` / `measure()` は `include_layout_c=False` を既定とし、通常のdry-run/executeはR24の6比較を変えない。
- CLIへ `--include-layout-c` を追加した。このflagを指定した場合だけ `suggest-layout-c-local-01..30` と `suggest-layout-c-global` の31 requestを追加し、全体で37 requestになる。
- 外部送信には従来どおり `--execute` と `KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1` が必要であり、Cについてはさらに `--include-layout-c` を明示しなければ送られない。provider名/model id一致確認、fallback禁止、合成データ限定も維持する。
- Cの各requestはR25のmeasurement-only promptをそのまま使う。provider transportが送るのはpromptだけであり、この経路をproduction IR contractとして扱わない。
- `layout_c_summary` は、Cを含めた場合のrequest数、最大単一prompt bytes、全C prompt bytes合計を診断値として返す。dry-runではR25と同じ **31 request / 最大7,486 bytes / 合計87,705 bytes** を再現した。
- 実provider実行時の `aggregate_input_tokens` / `max_single_input_tokens` は、31件すべてが `input_tokens` をprovider-reported usageとして返した場合だけ集計する。1件でもusageが欠ければ両値を `None` のままにし、byte数から補完しない。

回帰では、既定6 requestが増えないこと、C付きだけ37 requestになること、direct CLI dry-runがnetwork-freeであること、fake providerのreported usageだけからC集計値を作ること、usage欠落時に未完了のまま止めることを固定した。R25/R23回帰を含む22 test、ruff、`git diff --check` はGitHub Actions run `33940160064` で成功した。

**非主張**: R26でも外部providerは呼んでいない。Cの31 requestに対する実token数、総費用、latency、failure rate、local/global出力を合成した最終配置品質は未測定である。A2/B/Cの採択はnamed provider/modelのprovider-reported usageを得た後に行う。
'''
path.write_text(s, encoding="utf-8")
