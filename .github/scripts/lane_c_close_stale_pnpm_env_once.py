from __future__ import annotations

from pathlib import Path
import subprocess

ISSUES_ROOT = Path("01_Plans/issues")
DONE_ROOT = ISSUES_ROOT / "done"
SCRIPT_PATH = Path(".github/scripts/lane_c_close_stale_pnpm_env_once.py")
TARGETS = (
    "issue-DX-CI-PNPM-01-incomplete-pnpm-migration-reverted.md",
    "issue-DX-ENV-01-mixed-npm-pnpm-node-modules-state.md",
)


def replace_exact_reference(old: Path, new: Path) -> list[str]:
    completed = subprocess.run(
        [
            "git",
            "grep",
            "-Il",
            "-F",
            old.as_posix(),
            "--",
            f":!{SCRIPT_PATH.as_posix()}",
            f":!{new.as_posix()}",
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode not in (0, 1):
        raise SystemExit(completed.stderr.strip() or f"git grep failed: {old}")

    updated: list[str] = []
    for name in [line for line in completed.stdout.splitlines() if line]:
        path = Path(name)
        body = path.read_text(encoding="utf-8")
        replaced = body.replace(old.as_posix(), new.as_posix())
        if replaced == body:
            raise SystemExit(f"旧パス引用の置換が空振りしました: {name}")
        path.write_text(replaced, encoding="utf-8")
        updated.append(name)
    return updated


def close_memo(path: Path) -> None:
    body = path.read_text(encoding="utf-8")
    if body.count("- Status: Draft") != 1:
        raise SystemExit(f"Draft statusを一意に特定できません: {path}")
    body = body.replace("- Status: Draft", "- Status: Done", 1)

    if path.name.startswith("issue-DX-CI-PNPM-01"):
        body += """

## 完了確認（2026-09-05）

本Issueが記録した共有CI破損は、当時のpnpm導入をrevertした時点で解消しており、現在のmainでは再現条件そのものが存在しないことを再確認した。

- `03_Implement/frontend/` のversioned package-manager正本は `package-lock.json` のみで、`pnpm-lock.yaml` / `pnpm-workspace.yaml` / `yarn.lock` は存在しない。
- `package.json` にpnpmを選択する `packageManager` 契約はなく、現行frontendはnpm契約である。
- 当時問題になった `.github/workflows/ci.yml` を含む常設workflow群は、その後の運用判断で撤去済みであり、pnpm lockfileの有無でCIが自動的にpnpmへ切り替わる経路も現在は存在しない。
- したがって「revertした移行をいつ再開するか」は本Issueの未解決障害ではない。将来pnpmを採用する場合は、その時点のNode/CI/供給網方針を前提に新しい明示的な移行Issueとして扱う。

この判断はpnpm採用を恒久的に禁止するものではなく、**過去の失敗した移行試行をactive backlogとして残し続けない**ためのライフサイクル整理である。
"""
    elif path.name.startswith("issue-DX-ENV-01"):
        body += """

## 完了確認（2026-09-05）

本Issueが観測した `.pnpm/` / `.modules.yaml` 混在は、versioned repository stateではなく、revert前後の操作で残ったローカル `node_modules/` の汚染だった。現在の正本境界を再確認し、本Issueをrepo backlogとしては完了扱いとする。

- root `.gitignore` は `node_modules/` を明示的に除外しており、ローカル依存木は正本データではない。
- `03_Implement/frontend/` のversioned dependency契約は `package-lock.json` + npmで、pnpm lock/workspace設定は存在しない。
- fresh checkoutで `npm ci` を実行した検証では `node_modules/.pnpm/` と `node_modules/.modules.yaml` が生成されないことを確認し、frontend test / buildも同じclean installから成功させる。
- 既存ワークスペースに古いpnpm残骸が残っている場合は、`node_modules` を削除して正本lockfileから `npm ci` で再構築するローカル復旧問題であり、新たなrepository defectを意味しない。

この完了判断は個々の開発端末の現在状態が必ずcleanであるとは主張しない。repositoryから再現できる混在原因が残っていないことを境界とする。
"""
    else:
        raise SystemExit(f"unexpected target: {path}")

    path.write_text(body, encoding="utf-8")


def main() -> None:
    moved: list[tuple[Path, Path]] = []
    for name in TARGETS:
        old = ISSUES_ROOT / name
        new = DONE_ROOT / name
        if not old.exists() or new.exists():
            raise SystemExit(f"移動境界が不正です: {old} -> {new}")
        close_memo(old)
        subprocess.run(["git", "mv", old.as_posix(), new.as_posix()], check=True)
        moved.append((old, new))

    for old, new in moved:
        refs = replace_exact_reference(old, new)
        print(f"{old.name}: updated references={len(refs)}")
        for ref in refs:
            print(f"  - {ref}")


if __name__ == "__main__":
    main()
