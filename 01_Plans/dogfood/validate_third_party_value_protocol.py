#!/usr/bin/env python3
"""Fail-closed checks for the third-party value-validation protocol.

This validator does not score product value or participant outcomes. It only
protects protocol invariants that must remain true before third-party sessions:
neutral baseline capture, stopping/no-use as valid outcomes, runtime data-path
disclosure, and the public-Git publication boundary.
"""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent

FILES = {
    "execution": ROOT / "third-party-value-validation-execution-plan.md",
    "launch": ROOT / "third-party-value-session-launch-checklist.md",
    "session": ROOT / "third-party-value-session-record-template.md",
    "publication": ROOT / "third-party-value-publication-boundary.md",
    "participant": ROOT / "third-party-value-participant-brief.md",
    "analysis": ROOT / "third-party-value-analysis-plan.md",
}

REQUIRED_SNIPPETS = {
    "execution": [
        "Baseline before product-value vocabulary",
        "No-use reason",
        "Stop conditions",
        "Privacy / data handling",
        "support / modify / narrow / reject / unresolved",
    ],
    "launch": [
        "最初の実資料をKJ Atlasへ入力する前に",
        "AI provider / endpoint actually used",
        "Material sent outside the KJ Atlas process/device",
        "GO-WITH-REDUCTION",
        "STOP-DATA-BOUNDARY",
        "検証を完遂するためにdata-control条件を緩めない",
        "Launch verdictが空欄",
    ],
    "session": [
        "Public / private record boundary",
        "Session launch checklist reference",
        "Runtime data path actually used",
        "Runtime data path disclosed before first material entry",
        "Existing-workflow sufficiency hypothesis",
        "Stop / withdrawal",
        "No-use reason",
        "Session validity verdict: valid / partial / invalid",
    ],
    "publication": [
        "raw material、raw transcript、識別可能なartifactはpublic repositoryへcommitしない",
        "1項目でも不明ならcommitしない",
        "public Gitへ公開した情報はrepositoryから削除できても",
        "sanitized validation evidence",
    ],
    "participant": [
        "良い評価をもらうこと",
        "既存の方法で十分",
        "途中で止められます",
        "AI・ネットワーク・保存経路について",
        "検証を続けるために、資料の安全条件を緩める必要はありません",
        "セッションへの参加とpublic Gitへの公開は別の判断です",
        "元資料や識別可能な記録をそのままpublic Gitへ掲載することは既定では行いません",
    ],
    "analysis": [
        "最初の分析単位はparticipantではなく",
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
            errors.append(f"missing protocol file: {path.relative_to(ROOT)}")
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
