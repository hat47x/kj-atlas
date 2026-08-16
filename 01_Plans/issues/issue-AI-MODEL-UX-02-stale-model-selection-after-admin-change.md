# Issue: AI-MODEL-UX-02 管理変更後も利用者画面が古いmodel選択を保持する

- Type: Correctness / UX
- Status: Done
- Source Issue: 管理UI・CLI・API・MCP協調モンキーテスト（2026-08-16）
- Priority: P1
- Owner: Maintainer
- Scope: frontend tenant-scoped API wrapper, `ModelSelector`, model governance E2E
- Related Issue: `AI-MODEL-GOVERNANCE-03`, `AI-MODEL-UX-01`
- Related ADR/Spec: `ADR-0065`, `AI-MODEL-GOVERNANCE-01`
- Expected verification level: `e2e`

## 課題

利用者画面はmountまたはtenant session変更時にだけ`/ai/available-models`を取得する。管理者が別経路からmodelを無効化、providerを利用不能化、tenant allowlistを変更しても、開いている画面は古いmodel IDを選択肢とstateに保持し続ける。実行APIは403/503で安全に拒否するが、利用者は同じ失敗を繰り返し、管理変更が反映されたか判断できない。

## 対応

- `model_not_allowed`、`model_not_registered`、`model_provider_unavailable`を受けたtenant-scoped requestは、元のエラーを表示しつつ利用可能model一覧を再取得する。
- 再取得自体もtenant generation guardを通し、tenant切替後の古い結果をcommitしない。
- 更新後一覧に存在しない選択値を各`ModelSelector`が空文字（自動）へ戻す。
- 再取得失敗時は空状態へ閉じ、古い選択肢を残さない。
- 実効modelが0件なら生成ボタンを出さず、拒否理由はbackendの生文言ではなくlocale対応の復旧案内として表示する。

## 受入条件

- [x] 管理変更後のmodel拒否を契機に一覧を同一tenant条件で再取得する。
- [x] 除外された選択modelが自動選択へ戻る。
- [x] tenant切替中の古い再取得結果を画面へ反映しない。
- [x] Edge実画面で拒否後にselectorが空・disabled状態へ遷移する。
- [x] 空状態で生成操作を再試行できず、管理変更と再読込をlocale対応文言で説明する。
