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

---

# 企業・行政運用の公開要件（Publishing & Access Control）

## 背景
本アプリケーションは「市民・一般職員などの未ログインユーザへの公開」から、
「秘匿性が高く文書ごとにロール/グループ単位で厳格に制御」まで、両極の要件を想定する。

## 運用方式（選べることが重要）
### 方式A：静的配信（広域公開向け）
- Export（Bundle/Review Pack）を定期連携し、S3 + CDN 等の静的配信へ載せる
- SafeMode 強制（既定ON、解除不可の公開モードを用意）
- 公開に必要な最小ファイル（index + assets + packs）を生成する “Static Publish” モード

### 方式B：認証付き配信（限定公開向け）
- 統合認証（OIDC/SAML）でユーザ識別
- API層で認可（RBAC/ABAC）を実施し、文書単位の公開範囲を制御
- 監査ログと連動（閲覧/エクスポートのイベント記録は外部ログ基盤に送れる導線）

### 方式C：ハイブリッド（現実解）
- 内部は方式Bで厳格管理
- 市民向けは方式Aで低コスト公開
- “公開版生成”をエクスポートパイプラインで担保（匿名化・伏字・SafeMode強制）

## 優先実装（Mid-term）
- visibility（Public / Unlisted / Org / Restricted）を pack/view メタに導入
- isReadOnly を受け取ってUIを制御（アプリ内RBACは持たない）
- Static Publish 出力（S3/静的Web向け）を公式サポート
- DocumentACL 抽象I/F（roles/groups/policyRef）を定義し、実装は外部に委譲
