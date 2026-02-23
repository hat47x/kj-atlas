# English Summary
This document specifies a deterministic Local-first escalation policy: local generation is default, escalation is opt-in and disabled by default, with explicit trigger conditions and outbound allowlist controls.

# llm_escalation_policy — Local-first + Escalation方針（02_Architecture）

本仕様は、コスト抑制と品質維持を両立するための **Local-first + Escalation** の運用ルールを定義する。

---

## 1. 運用原則

- デフォルト経路は **LocalProvider**。
- エスカレーションは例外処理であり、常用経路にしない。
- 外部強モデルへの送信は、明示設定がある場合のみ許可する。

---

## 2. デフォルト設定

- `escalation.enabled = false`（既定: 無効）
- 明示的に `true` へ変更しない限り、外部送信は行わない。
- 設定変更には運用責任者の承認と監査ログ記録を要する。

---

## 3. 決定論的エスカレーショントリガ

以下はいずれも**LLM不要で判定可能**であること。

1. schema validation failure  
2. 重要セクションが空、または最小長未満  
3. contradiction edge（否定関係）が存在するのに、出力に矛盾/反証セクションが欠落  
4. 閾値超過（カード数・クラスタ数・negation edge数など）  
5. ルーブリックスコアが閾値未満（Layer B利用時）

> トリガは仕様書で固定し、恣意的判定を避ける。

---

## 4. ルーティングパターン

### 4.1 無効時（既定）

- ローカル再試行（prompt圧縮・入力分割など）を行う。
- 失敗時は「要人手確認」ステータスで返却。

### 4.2 有効時（明示opt-in）

- 許可された送信先へのみ転送（allowlist-only outbound）。
- 送信前にsafeMode/赤線化ポリシーを適用。
- 送信データは最小化し、不要メタデータを含めない。

---

## 5. コスト制御

- 月次または環境別の外部呼び出し上限（回数/トークン）を定義する。
- 上限到達時は自動でローカル専用モードに降格する。
- 運用ダッシュボードで、ローカル成功率・エスカレーション率・失敗率を監視する。

---

## 6. セキュリティ・プライバシー整合

- safeMode ON時は、禁止対象の生カード文面を外部送信しない。
- エスカレーションログは理由コードを保持し、本文は最小化またはハッシュ化する。
- 送信経路・承認履歴・モデル識別子を監査可能にする。

