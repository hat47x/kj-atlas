# Issue: OPS-ADMIN-UX-01 管理APIを安全に扱う正式CLIと管理コンソールがない

- Type: Operations / UX
- Status: Open
- Source Issue: 管理UI・CLI・利用者UIの協調モンキーテスト（2026-08-16）
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/cli.py`, new admin frontend or separately deployed console, operator documentation
- Related ADR/Spec: `ADR-0072`, `SEC-ADMIN-PLANE-03`, `AI-MODEL-GOVERNANCE-01`
- Expected verification level: `e2e`

## 課題

管理面APIはcontrol-plane認可・監査・モデルallowlistまで備える一方、正式な`kj_atlas_api.cli`はCE4監査操作だけで、モデル、tenant、IdP、監査照会を扱えない。`scripts/examples/admin_lifecycle.py`はキー分離の良い実例だが、文書ライフサイクルと監査照会に限られ、管理APIの入力検証や安全な確認操作を一貫して提供する運用品質のCLIではない。利用者SPAにも管理導線はなく、今回の実画面確認でも管理ラベル・管理資格情報入力面は0件だった。

このため管理者はcurlや自作scriptへ依存し、tenant/model IDの誤入力、秘密値のshell履歴・process引数露出、変更前後差分の見落としが起きやすい。利用者SPAへ管理キーを持たせる解決は不可であり、管理面は別origin・別配備・短時間sessionを前提にする必要がある。

## 対応方針

- 正式CLIへ`admin models list/register/disable`、`admin tenants model-allowlist get/set`、`admin audit list`を追加する。
- 管理キーは環境変数またはOS secret入力からのみ受け、command line引数、標準出力、error本文へ出さない。
- write操作は既定で差分表示＋確認、automation向けに明示的`--yes`とJSON出力を用意する。
- 管理コンソールを作る場合は利用者SPAとbundle・origin・認証sessionを分離し、`tenant.provision` capabilityを通常経路、静的admin keyをbootstrap専用にする。
- CLI変更後に利用者APIの`/ai/available-models`と実画面へ反映される一連のE2Eを固定する。

## 受入条件

- [ ] 管理者が秘密値を引数へ書かずにモデル一覧・登録・無効化・tenant allowlist更新・監査照会を実施できる。
- [ ] 業務キーでは全管理commandが失敗し、管理キーは業務APIへ横滑りしない。
- [ ] CLIの無効tenant/model/重複入力は安定したcodeと非0終了で説明され、秘密値を表示しない。
- [ ] 管理変更が利用者APIと実ブラウザのモデル表示へ反映されるE2Eがある。
- [ ] 管理コンソール採用時は利用者SPAへ管理credentialを保存・配送しない設計がADR化される。

## 検出記録（2026-08-16）

管理API、管理者example script、利用者SPAを同時に動かしたモンキーテストで検出。example scriptはキー分離を10/10通過し、利用者画面のlocal/session storageと本文に両キーが存在しないことをEdgeで確認した一方、管理UIと正式な管理CLI commandは存在しなかった。
