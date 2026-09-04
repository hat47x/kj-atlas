from pathlib import Path

STAGE5 = Path("01_Plans/issues/issue-AI-IR-STAGE5-SCOPE-01-classify-remaining-ai-input-paths.md")
PROJECTION = Path("01_Plans/issues/issue-AI-IR-PROJECTION-01-llm-input-ir-as-ai-input-path.md")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


stage5 = STAGE5.read_text(encoding="utf-8")
stage5_marker = "\n## 受入条件\n"
if stage5.count(stage5_marker) != 1:
    raise SystemExit(f"stage5 acceptance marker count={stage5.count(stage5_marker)}")
stage5_dependency = """

## Dependencies

- `01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md`
  - `check-narrative` の全体照合を維持できるscale投影方式とnamed provider/modelの実token予算を確定する実証元。
  - `AI-IR-SCALE-01` の結果が出る前に、固定上限への切り捨てや形式的なIR移行で本Issueを完了扱いにしない。
"""
stage5 = stage5.replace(stage5_marker, stage5_dependency + stage5_marker, 1)
STAGE5.write_text(stage5, encoding="utf-8")

projection = PROJECTION.read_text(encoding="utf-8")
projection = replace_once(
    projection,
    "> **進捗（2026-09-03）: Stage 1〜4は完了し、Stage 5へ着手済み。** `suggest-island-summary` と `propose-opposing-viewpoint` までgeneric Document IRの実入力化を完了し、11件中6経路がDocument IR経由である。残る5経路のうち3経路はADR-0069 D5=Aによりtask-local structured inputを正式契約とする境界が確定したため、「11/11をgeneric Document IRへ揃える」ことは完了条件ではない。未決の実装判断は `suggest-merges` の意味論と `check-narrative` のscale方式である。AC-7 は Stage 4 で完了し、AC-10は `AI-IR-SCALE-01` へ切り出して継続している。詳細は末尾の各Stage結果を参照。`Status` メタデータの語彙は `Draft` / `Open` / `In Progress` / `Done` に固定されている（`01_Plans/issues/issue_memo_status.py`）ため、段階情報はここに書く。",
    "> **進捗（2026-09-04）: Stage 1〜4は完了し、Stage 5は `check-narrative` のscale方式だけが未確定。** `suggest-island-summary` / `propose-opposing-viewpoint` / `suggest-merges` はDocument-backed structured inputへ移行済みで、`summarize-island-relation` / `refine-card-text` / `suggest-document-title` はADR-0069 D5=Aによりtask-local structured inputを正式契約とする境界が確定した。「11/11をgeneric Document IRへ揃える」ことは完了条件ではない。残る実装判断は `check-narrative` だけであり、`AI-IR-SCALE-01` のscale方式とnamed provider/modelの実token予算確認を待つ。AC-7 はStage 4で完了し、AC-10は `AI-IR-SCALE-01` へ切り出して継続している。詳細は `AI-IR-STAGE5-SCOPE-01` と末尾の各Stage結果を参照する。`Status` メタデータの語彙は `Draft` / `Open` / `In Progress` / `Done` に固定されている（`01_Plans/issues/issue_memo_status.py`）ため、段階情報はここに書く。",
    "projection progress",
)
projection = replace_once(
    projection,
    "**2026-09-03更新**: `suggest-island-summary` と `propose-opposing-viewpoint` をStage 5の第1・第2経路としてgeneric Document IRへ移行し、Document IR経由は6件になった。残る5経路のうち `summarize-island-relation` / `refine-card-text` / `suggest-document-title` はADR-0069 D5=Aでtask-local structured inputを正式契約とする境界を確定した。残る実装判断は `suggest-merges` と `check-narrative` であり、分類と順序は `AI-IR-STAGE5-SCOPE-01` を正本とする。",
    "**2026-09-04更新**: `suggest-island-summary` / `propose-opposing-viewpoint` / `suggest-merges` はStage 5のDocument-backed structured inputへ移行済みである。`summarize-island-relation` / `refine-card-text` / `suggest-document-title` はADR-0069 D5=Aでtask-local structured inputを正式契約とする境界を確定した。残る実装判断は `check-narrative` だけであり、分類と順序は `AI-IR-STAGE5-SCOPE-01` を正本とする。",
    "projection current stage paragraph",
)
projection_marker = "\n## 課題\n"
if projection.count(projection_marker) != 1:
    raise SystemExit(f"projection issue marker count={projection.count(projection_marker)}")
projection_dependency = """

## Dependencies

- `01_Plans/issues/issue-AI-IR-STAGE5-SCOPE-01-classify-remaining-ai-input-paths.md`
  - 本Issueの残存Stage 5実装判断を集約する正本。現在の未完は `check-narrative` だけである。
  - Stage 5が完了する前に、親Issueを完了扱いにしない。
"""
projection = projection.replace(projection_marker, projection_dependency + projection_marker, 1)
PROJECTION.write_text(projection, encoding="utf-8")

print("AI IR Stage 5 dependency chain synchronized")
