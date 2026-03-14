# Issue Draft: HIL-RS-02 A2 Frontend 可逆統合フロー適用

- Type: Implementation
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: TBD
- Priority: P1
- Owner: Frontend Owner
- Scope: `03_Implement/frontend/`, `04_Documentation/`
- Related Backlog: `HIL-RS-02`
- Related ADR/Spec: `ADR-0027`, `ADR-0026`, `02_Architecture/architecture.md`, `02_Architecture/schemas.md`
- Expected verification level: `unit`

## 1) 背景

- HIL-RS-02の実装フェーズで、可逆差分の提示と人間確定UIを契約準拠で導入する必要がある。

## 2) 目的

- A1契約を変更せず、候補比較と手動確定のUI導線を実装する。

## 3) スコープ

- frontendの候補比較UI、差分表示、確定操作の監査イベント出力。

## 4) 非スコープ

- 自動確定、ランキング、単一正解提示。
- SafeMode default OFF化。

## 5) 受入条件

- AC-1: SafeMode既定ONでの動作が維持される。
- AC-2: 確定操作は人間操作時のみ発火する。
- AC-3: 回帰テスト（unit）を追加し、既存機能の破壊がない。

## 6) 検証方法

- `npm --prefix 03_Implement/frontend test -- --runInBand`
- `npm --prefix 03_Implement/frontend run lint`

## 7) 依存関係

- `issue-HIL-RS-02-A1-governance-contract-hardening.md` 完了

## 8) リスク

- UI導線の追加で既存レビュー機能と競合する可能性。

## 9) 着手順

1. 契約参照実装
2. UI導線追加
3. unit検証
