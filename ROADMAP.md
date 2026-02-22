# ROADMAP

**English summary (short):**
This roadmap shares public priorities for kj-atlas.
Near-term covers U1/U2/U3 and SafeMode hardening.
Mid-term targets consolidation, hierarchical synthesis, and an optional local LLM adapter.
Long-term explores advanced island shapes, collaboration, and optional signing/audit hardening.

このロードマップは、公開向けに優先度を短く共有するための文書です。
詳細な実装タスクは `01_Plans/` を参照してください。

## 近距離（次の 1〜2 リリース）

- **U1 presets**
  - 代表的な探索開始パターンをプリセットとして選べるようにする。
- **U2 collapse**
  - 情報密度が高い場面でも読みやすくするため、折りたたみ操作を強化する。
- **U3 polygon islands**
  - ポリゴン島を前提とした配置・編集体験を安定化する。
- **SafeMode enforcement hardening**
  - safeMode 制約の強制をより堅牢化し、共有時の安全性を高める。

## 中期

- **Similar-card consolidation support**
  - 類似カードの統合（consolidation）を支援する機能を追加する（既知の将来タスク）。
- **Hierarchical synthesis（質的統合）**
  - 複数クラスタを段階的に束ね、上位概念へ統合できる流れを整備する。
- **Local LLM adapter interface（任意）**
  - プライベート運用向けに、任意で使えるローカル LLM アダプタ I/F を整える。

## 長期

- **Non-rect island shapes beyond polygon（splines）**
  - ポリゴンを超える非矩形島（例: スプライン）を検討する。
- **Multi-user collaboration（現時点ではスコープ外）**
  - 複数人同時編集は将来候補とし、当面は単一ユーザー前提を維持する。
- **Optional signing/audit hardening**
  - 必要に応じて署名・監査の強化オプションを提供する。
