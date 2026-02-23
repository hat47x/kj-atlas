# English Summary
This document defines runtime constraints for LLM usage in Codex-like sandboxed environments, preferring in-process/IPC paths over localhost HTTP and specifying CI-safe provider patterns.

# llm_runtime_constraints — LLM実行時制約とサンドボックス前提（02_Architecture）

本仕様は、kj-atlas の LLM連携を安全かつ再現可能に運用するため、実行環境制約（特にサンドボックスとネットワーク）を定義する。

---

## 1. 前提: サンドボックスとネットワーク

- Codex系エージェント実行では、**ネットワークが既定で制限される運用**を標準前提とする。
- したがって「外部APIへ常時接続してテストする」運用は標準パスにしない。
- ネットワーク許可が必要な場合は、明示設定と監査可能な運用手順を必須とする。

---

## 2. 推奨通信経路

### 2.1 優先順位

1. **in-process 呼び出し**（最優先）  
2. **IPC**（Unix domain socket / named pipe）  
3. localhost HTTP（最終手段、許可前提）

### 2.2 理由

- in-process/IPCはネットワークポリシー影響を受けにくい。
- localhost HTTP は環境によって loopback 通信扱いが不安定になる可能性がある。
- テストの安定性・再現性を重視し、HTTP依存は避ける。

---

## 3. CIで許容する実行パターン

### 3.1 常時利用可能（必須）

- **FixtureProvider**: 常時有効。ネットワーク不要で決定論的。

### 3.2 任意利用（環境依存）

- **LocalProvider**: 実行ホストにローカルモデル基盤がある場合のみ有効。

### 3.3 定期実行のみ（通常PRでは非必須）

- **External strong-model provider**: 夜間/定期統合テストでのみ実行。
- PRごと必須にしない（コストと接続可用性のため）。

---

## 4. 実行モード定義

- `offline`: fixture + local のみ。外部送信禁止。
- `intranet`: local中心、必要時に社内ゲートウェイ経由。
- `scheduled-integration`: 外部強モデルによる小規模評価セット実行。

---

## 5. 失敗時ポリシー

- LocalProvider未起動時は FixtureProvider へフォールバック可能とする。
- 外部通信不能はテスト警告扱い（ただし通常CIの必須判定から除外）。
- スキーマ検証失敗は通信可否に関わらず失敗扱い（品質ゲート優先）。

---

## 6. 実装に渡す拘束条件

- プロバイダ実装は transport を抽象化し、上位ロジックにHTTP依存を漏らさない。
- テストは transport差し替え可能であること（in-process / IPC / fixture）。
- 監査ログには「どの通信経路を使用したか」を記録する。

