#!/usr/bin/env python3
"""Fail-closed checks for the third-party value-validation protocol.

This validator does not score product value or participant outcomes. It only
protects protocol invariants that must remain true before third-party sessions:
neutral baseline capture, stopping/no-use as valid outcomes, runtime data-path
disclosure, the public-Git publication boundary, and discoverability from the
canonical VALUE-REALNESS-01 issue.
"""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PLANS_ROOT = ROOT.parent

FILES = {
    "issue": PLANS_ROOT / "issues" / "issue-VALUE-REALNESS-01-third-party-beachhead-validation.md",
    "execution": ROOT / "third-party-value-validation-execution-plan.md",
    "launch": ROOT / "third-party-value-session-launch-checklist.md",
    "session": ROOT / "third-party-value-session-record-template.md",
    "publication": ROOT / "third-party-value-publication-boundary.md",
    "participant": ROOT / "third-party-value-participant-brief.md",
    "analysis": ROOT / "third-party-value-analysis-plan.md",
}

REQUIRED_SNIPPETS = {
    "issue": [
        "現在の実行準備状態",
        "現在残っている外部入力",
        "セッション開始時の入口",
        "third-party-value-validation-execution-plan.md",
        "third-party-value-participant-brief.md",
        "third-party-value-session-launch-checklist.md",
        "third-party-value-session-record-template.md",
        "third-party-value-publication-boundary.md",
        "third-party-value-analysis-plan.md",
        "validate_third_party_value_protocol.py",
    ],
    "execution": [
        "S0 — 価値語彙を提示する前のbaseline",
        "No-use reason",
        "停止条件",
        "privacy / data handling",
        "support / modify / narrow / reject / unresolved",
    ],
    "launch": [
        "最初の実資料をKJ Atlasへ入力する前に",
        "AI provider / endpoint actually used",
        "KJ Atlasのprocess / device外へ資料が送られるか",
        "GO-WITH-REDUCTION",
        "STOP-DATA-BOUNDARY",
        "検証を完遂するために、資料統制の条件を緩めない",
        "Launch verdictが空欄",
    ],
    "session": [
        "Public / private record boundary",
        "Session開始前チェックリスト参照",
        "実際に使用したruntime data path",
        "最初の実資料入力前に、AI / network / storage経路を説明した",
        "現在のworkflowで十分な条件",
        "停止・撤回",
        "No-use reason",
        "Session validity verdict: valid / partial / invalid",
    ],
    "publication": [
        "raw material、raw transcript、識別可能なartifactはpublic repositoryへcommitしない",
        "1項目でも不明ならcommitしない",
        "public Gitへ公開した情報は、repositoryから削除できても",
        "sanitized validation evidence",
    ],
    "participant": [
        "良い評価をもらうこと",
        "既存の方法で十分",
        "途中で止められます",
        "AI・ネットワーク・保存経路について",
        "検証を続けるために、資料の安全条件を緩める必要はありません",
        "sessionへの参加とpublic Gitへの公開は別の判断です",
        "元資料や識別可能な記録を、そのままpublic Gitへ掲載することは既定では行いません",
    ],
    "analysis": [
        "最初の分析単位は参加者そのものではなく",
        "no-use / stop / existing-workflow sufficiency",
        "support",
        "modify",
        "narrow",
        "reject",
        "unresolved",
        "third-party-value-publication-boundary.md",
    ],
}

FORBIDDEN_SNIPPETS = {
    "participant": [
        "KJ Atlasなら根拠を残せます",
        "KJ Atlasなら異論を保持できます",
        "KJ Atlasなら再訪できます",
    ],
}


def main() -> int:
    errors: list[str] = []

    for key, path in FILES.items():
        if not path.is_file():
            errors.append(f"missing protocol file: {path.relative_to(PLANS_ROOT)}")
            continue

        text = path.read_text(encoding="utf-8")

        for snippet in REQUIRED_SNIPPETS.get(key, []):
            if snippet not in text:
                errors.append(f"{path.name}: missing required protocol text: {snippet!r}")

        for snippet in FORBIDDEN_SNIPPETS.get(key, []):
            if snippet in text:
                errors.append(f"{path.name}: participant-leading value claim found: {snippet!r}")

    if errors:
        print("Third-party value protocol validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Third-party value protocol validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
