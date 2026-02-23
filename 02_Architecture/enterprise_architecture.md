# Enterprise / Government Deployment Architecture

**English summary**  
This document defines the minimum OSS-level capabilities required for kj-atlas to be deployable in enterprise and government environments.  
The focus is integration readiness, not SaaS transformation.

---

# 基本方針

本アプリケーションは以下を維持する：

- OSSとしての軽量性
- ローカルファースト設計
- SafeMode既定ON
- 文書構造と表示状態の分離（document.json / view.json）

企業・行政運用において必要なのは「アプリの肥大化」ではなく、
**外部基盤との安全な接続点の整備**である。

---

# 1. 統合認証（SSO / IdP連携）

## 目的

- 組織内ユーザ識別
- レビュー責任所在の明確化
- アクセス制御との連動

## 方針

本アプリケーション自体は認証を実装しない。

代わりに：

- 認証はリバースプロキシまたはバックエンド層で処理
- アプリは「署名済みユーザコンテキスト」を受け取る

## 最低限必要な拡張

### 1. AuthContext抽象

- userId: string（必須）
- displayName?: string
- roles?: string[]
- groups?: string[]

これをフロントに渡すだけでよい。

対応可能なIdP例（実装は外部責務）：

- OIDC
- SAML
- LDAP（間接連携）

---

# 2. ユーザ管理

## 方針

ユーザ管理機能はアプリ内に持たない。

理由：
- 組織基盤と重複する
- セキュリティ責任が過大になる

## 必要最低限

- reviewerRef を AuthContext.userId にマッピング
- view.json に reviewerRef を保持（PII非保存）
- 表示名は揮発的に扱う（保存しない）

---

# 3. 文書管理（Document Governance）

## 目的

- 文書の所有権
- 版管理
- 承認フロー

## 最小OSS対応範囲

### A. バージョンメタデータ

view.json に保持可能：

- versionTag: string
- createdAt
- updatedAt
- ownerRef

### B. 外部ストレージ前提

文書保管は以下に委譲可能：

- 既存RDBMS
- オブジェクトストレージ
- Git管理
- DMS（Document Management System）

本アプリケーションは：
- JSON構造が安定
- スキーマ後方互換

これを保証するのみ。

---

# 4. 公開範囲とアクセス制御（重要）

企業・行政用途では「未ログイン（市民・一般職員）への公開可否」と「組織内の厳格な限定公開」が同時に求められる。
本アプリケーションはアプリ内で巨大な認可基盤を抱えず、**運用方式を複数用意して“選べる”こと**を最低ラインとする。

## 4.1 公開クラス（ドキュメント単位）

文書（Document/Pack）ごとに、次の公開クラスを持てる設計とする。

- **Public**：未ログインでも閲覧可能（広域公開）
- **Unlisted**：URLを知る者のみ（リンク共有）
- **Org**：組織内（SSO必須）
- **Restricted**：ロール/グループ単位で厳格に制御（SSO必須）

MVPでは、まず view.json（または pack manifest）に **visibility** フィールドを追加し、UIはその状態を表示する。

## 4.2 方式A：静的配信（広域公開向け）

### 背景

- 認証運用の負担を避けたい
- インフラ費用を最小化したい
- “閲覧だけ” を大量配布したい

### 方針

- 本アプリケーションの **Export（Bundle/Review Pack）** を定期連携し、
  - S3 + CloudFront
  - もしくは社内静的Webサーバ
  に配置して静的配信に載せる。

### 必要なOSS整備（最低限）

- Export を **静的サイト向け** に整形するモード
  - index.html + assets + packs
- SafeMode を強制（既定ON、解除不可を選択可能）
- “公開に必要な最小ファイル” のみ出力
- 署名/ハッシュ（将来）で改ざん検知

## 4.3 方式B：認証付き配信（限定公開向け）

### 背景

- 秘匿性が高い
- 文書ごとにロール/グループで閲覧制御が必要
- 監査・証跡が必須

### 方針

- 認証（SSO）は外部（OIDC/SAML）
- 認可（RBAC/ABAC）はAPI層で実装
- 本アプリケーションは AuthContext + isReadOnly + visibility を受け取りUI制御

### 最低限必要な拡張

- DocumentACL 抽象（アプリ内実装ではなく **I/F定義**）
  - allowedRoles / allowedGroups / policyRef
- APIのガード
  - read / write / export / share の権限制御
- 監査ログ連動
  - 「誰が何を閲覧/エクスポートしたか」を外部ログ基盤に送れる導線（オプション）

## 4.4 方式C：ハイブリッド（現実解）

- 内部は方式B（厳格管理）
- 市民向け公開は方式A（静的配信）
- “公開版” 生成はエクスポートパイプラインで担保
  - SafeMode強制
  - 伏字/匿名化ポリシー
  - 公開クラスを Public に変換

---

# 5. 監査・証跡

既存の：

- Merge Audit Log
- ReviewEvent

を活用。

拡張可能領域：

- 署名付きハッシュ保存（将来）
- 外部ログ基盤への送信（オプション）

---

# 6. データ保護

## 既定

- SafeMode ON
- PII保存しない

## 組織向け追加検討

- 暗号化保存（DB側責務）
- バックアップ戦略
- データ保持ポリシー

---

# 7. 推奨デプロイ構成

## 小規模

Browser → Reverse Proxy → Static Frontend + API → DB

## 中規模

Browser → SSO Gateway → API Layer → Postgres → Object Storage

## 行政用途

Browser → Internal IdP → Hardened API → RDBMS（オンプレ）


---

# 8. OSSとして整備すべき最低ライン

1. AuthContext抽象インタフェース
2. reviewerRef外部マッピング対応
3. readOnlyモード対応
4. versionメタデータ構造
5. スキーマ安定性保証（後方互換）
6. データ移行ガイド

---

# 非目標

- 内蔵ユーザ管理画面
- 独自認証基盤
- SaaSマルチテナント管理

---

# 結論

企業・行政レベル運用に必要なのは、

「機能の追加」ではなく
「接続点の抽象化と責任分離」である。

本アプリケーションは、

- 認証は外部
- 保存は外部
- 統治は外部

という前提を明確にし、

“組み込まれるOSS” として成立させる。

