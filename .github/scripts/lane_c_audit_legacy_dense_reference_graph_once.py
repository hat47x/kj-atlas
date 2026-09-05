from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ISSUES_ROOT = Path("01_Plans/issues")
MANIFEST = ISSUES_ROOT / "legacy_done_at_root_r18.json"
SELF = Path(".github/scripts/lane_c_audit_legacy_dense_reference_graph_once.py")
TARGET_RE = re.compile(r"^issue-(DOGFOOD-\d+|QA-MONKEY-\d+)-")


def grep_files(needle: str) -> list[str]:
    completed = subprocess.run(
        ["git", "grep", "-Il", "-F", needle, "--", f":!{SELF.as_posix()}"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode not in (0, 1):
        raise SystemExit(completed.stderr.strip() or f"git grep failed for {needle!r}")
    return sorted(line for line in completed.stdout.splitlines() if line)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    targets: dict[str, Path] = {}
    for name in manifest["paths"]:
        match = TARGET_RE.match(name)
        path = ISSUES_ROOT / name
        if match and path.exists():
            body = path.read_text(encoding="utf-8")
            if "- Status: Done" not in body:
                raise SystemExit(f"legacy dense target is no longer Done: {path}")
            targets[match.group(1)] = path

    if len(targets) != 39:
        raise SystemExit(f"expected 39 dense legacy targets, found {len(targets)}")

    texts = {issue_id: path.read_text(encoding="utf-8") for issue_id, path in targets.items()}
    edges: dict[str, set[str]] = {issue_id: set() for issue_id in targets}
    for source_id, body in texts.items():
        for target_id in targets:
            if target_id != source_id and target_id in body:
                edges[source_id].add(target_id)

    undirected = {issue_id: set() for issue_id in targets}
    for source_id, peers in edges.items():
        for peer in peers:
            undirected[source_id].add(peer)
            undirected[peer].add(source_id)

    components: list[list[str]] = []
    unseen = set(targets)
    while unseen:
        root = min(unseen)
        stack = [root]
        component: set[str] = set()
        while stack:
            current = stack.pop()
            if current in component:
                continue
            component.add(current)
            stack.extend(undirected[current] - component)
        unseen -= component
        components.append(sorted(component, key=lambda value: (value.split("-")[0], int(value.rsplit("-", 1)[1]))))

    rows = []
    target_paths = {path.as_posix() for path in targets.values()}
    for issue_id, path in sorted(targets.items(), key=lambda item: (item[0].split("-")[0], int(item[0].rsplit("-", 1)[1]))):
        full_path_refs = [p for p in grep_files(path.as_posix()) if p != path.as_posix()]
        id_refs = [p for p in grep_files(issue_id) if p != path.as_posix()]
        external_id_refs = [p for p in id_refs if p not in target_paths and not p.endswith("legacy_done_at_root_r18.json")]
        title = texts[issue_id].splitlines()[0].removeprefix("# Issue:").strip()
        rows.append(
            {
                "id": issue_id,
                "title": title,
                "outgoingPeerIds": sorted(edges[issue_id]),
                "fullPathRefs": full_path_refs,
                "externalIdRefCount": len(external_id_refs),
                "externalIdRefs": external_id_refs,
            }
        )

    print("=== COMPONENTS ===")
    for index, component in enumerate(sorted(components, key=lambda c: (len(c), c)), start=1):
        print(json.dumps({"component": index, "size": len(component), "ids": component}, ensure_ascii=False))

    print("=== ROWS ===")
    for row in rows:
        print(json.dumps(row, ensure_ascii=False))

    print("=== SUMMARY ===")
    print(
        json.dumps(
            {
                "targetCount": len(targets),
                "componentCount": len(components),
                "isolatedCount": sum(1 for component in components if len(component) == 1),
                "dogfoodCount": sum(1 for issue_id in targets if issue_id.startswith("DOGFOOD-")),
                "qaMonkeyCount": sum(1 for issue_id in targets if issue_id.startswith("QA-MONKEY-")),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
