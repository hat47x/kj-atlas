# Review Attribution (Design)

## Purpose
kj-atlas は「曖昧さを保留したまま思考を進める」ための図解ツールであり、成果物は共有・レビューされることを前提とする。  
本ドキュメントは、図解内の要素（島・カード・関係・要約等）について「レビュー済みかどうか」および（任意で）「誰が・いつ」レビューしたかを記録するための設計方針を示す。

本機能は **設計のみ**とし、MVPには実装しない。

## Non-goals
- 本機能で「改ざん不可能な監査証跡」を提供しない（署名・証明は将来拡張）。
- 認証・認可・IDプロバイダ（SSO等）を必須要件にしない。
- 個人情報（実名、メール等）の保存をデフォルトで行わない。
- レビュー行為の“正しさ”を自動判定しない。

## Why view-scoped (privacy-first)
kj-atlas は OSS として、多様な環境で利用される：
- ローカル個人利用（ログイン無し）
- 企業/行政のイントラ（SSOやアカウント管理あり）
- 自前ホスティング（最小構成）

この前提では、レビュー情報を document.json（内容そのもの）に埋め込むと、共有時に個人情報や組織内情報が意図せず外へ流出する危険が高い。  
よってレビューの帰属（attribution）は **view.json 側（ビュー・メタデータ）に保持**するのを基本方針とする。

## Data Model Options
### Option A: View-scoped attribution (Recommended default)
- view.json に reviewEvents / reviewers を保持する
- document.json は「内容」のみに限定する

**Pros**
- 共有物（document.json）の安全性が高い
- レビュー情報を必要に応じて “同梱/削除” できる（export redaction）
- 認証不要で成立する

**Cons**
- view.json を共有しない場合、レビュー情報が伝播しない

### Option B: Doc-scoped attribution (Not default)
- document.json に要素単位の reviewedBy / reviewedAt 等を持たせる

**Pros**
- ドキュメント単体でレビュー状態が完結する

**Cons**
- 個人情報/組織情報がコンテンツと一体化し、削除しづらい
- 公開や外部共有で事故りやすい

### Option C: Hybrid (Possible future)
- document.json に reviewerRef（匿名ID）のみ保持し、
- view.json で reviewerRef→表示名のマッピングを保持する

**Pros**
- コンテンツ側で最低限の帰属が持てる
- 表示名は view 側で削除可能

**Cons**
- 運用が複雑化しやすい
- “匿名ID” でも組織内では個人特定されうる（扱い注意）

## Recommended Approach
### Default
- **Option A（view-scoped）を採用**
- レビューの記録は **reviewEvents** として append-only に近い形で残す
- “誰が”は **ReviewerRef（匿名ID）** とし、実名等はオプトイン

### Concepts
- **ReviewerRef**: 文字列ID（例: `user:local:4f9c...` / `user:sso:sub:...`）
- **ReviewEvent**: いつ、何に対して、どんなレビューアクションが起きたか
- **ReviewContext**: 内部レビュー/外部レビュー/セルフチェック等、出力時の扱いに影響する文脈
- **Attribution Policy**: 個人情報の保存可否、エクスポート時の削除方針、保持期間等

## Interoperability & Identity
- ローカル利用:
  - ランダム生成した ReviewerRef を使う
  - displayName は保存しない（必要ならユーザが任意に付ける）
- 組織利用（SSO等）:
  - 安定した subject id を ReviewerRef として利用可能
  - displayName は “ビュー側”にのみ保持し、エクスポート時に削除できること
- 認証無しでも動作し続けること（必須）

## Export & Redaction Policy
レビュー情報は共有時に事故の原因になりやすい。  
よって view.json には以下の “削除モード” を持たせる。

- `none`: すべて含める（組織内運用向け）
- `strip-identities`: reviewerRef を残すが、displayName 等PIIを除去
- `strip-all`: reviewEvents / reviewers 自体を出力しない（公開向け）

※MVP外だが、I25 review pack の既定は `strip-identities` が妥当。

## Threat Model (Abuse Cases)
- **Doxxing**: 実名やメールが成果物に残り外部流出
- **Tampering**: reviewEvents は編集可能であり、監査証跡としては不完全
- **Over-collection**: 不要な個人属性を収集しがち

対策（設計方針）:
- デフォルト storePII=false
- 表示名はオプトイン
- “証拠”ではなく“主張（claim）”として扱う
- 将来拡張で署名（detached signature）を検討

## Optional signing (Phase3 M6, non-MVP)

### Scope and goals
- detached signature は **review attribution を含む配布単位の完全性確認** を目的とする。
- 署名はオプションであり、未署名データでも既存の閲覧・編集・レビュー運用は継続できる。
- SafeMode と PII 最小化（`storePII=false` 既定、redaction 既定 `strip-identities`）を優先し、署名導入で既定値を緩めない。

### Signing target
- 対象は `view.json` 単体ではなく、`document.json` + `view.json` の組み合わせを表す `review-attribution digest` とする。
- digest 生成時は次を必須入力にする。
  - `documentDigest`（`document.json` の SHA-256）
  - `viewDigest`（`view.json` の SHA-256。redaction 後の実ファイルを対象）
  - `reviewEventDigest`（`reviewEvents` 正規化 JSON の SHA-256）
  - `attributionPolicyDigest`（`reviewAttributionPolicy` 正規化 JSON の SHA-256）
- 署名対象は上記 digest 群を含む `ReviewSignatureEnvelope` の canonical JSON とし、署名方式は `detached` を前提にする。

### Verification flow
1. 署名ファイル（例: `review-signature.json`）がある場合のみ検証処理を開始する。
2. `document.json` / `view.json` から digest を再計算し、envelope 内の値と比較する。
3. `keyId` で公開鍵を解決し、`signature` を検証する。
4. 成功時は監査ログに `verification=passed` を追記する。
5. 失敗時は監査ログに失敗理由（`digest_mismatch` / `key_not_found` / `signature_invalid`）を残す。

### Failure behavior (non-blocking default)
- **署名がない場合**: `verification=not_provided` として扱い、通常利用は継続する。
- **署名検証失敗**: 既定では read-only で継続可能とし、破壊的操作（share/export）のみ追加確認を要求する。
- 組織運用で fail-closed が必要な場合は policy で `requireSignature=true` を明示し、未署名/失敗を拒否できる。
- 既定値は `requireSignature=false` とし、ローカル利用・OSS利用を阻害しない。

### UI / operations policy
- UI には「署名状態」を 3 値で表示する。
  - `Unsigned`（未署名）
  - `Verified`（署名検証成功）
  - `Verification failed`（署名不正または鍵不一致）
- 未署名は warning ではなく info 扱いにし、通常フローをブロックしない。
- `Verification failed` では操作を即時停止せず、share/export 前に確認ダイアログを出す。
- 運用では「公開配布時のみ署名必須」「内部下書きは任意」を標準とし、署名必須範囲を deployment policy で管理する。

### Audit log relation
- 署名検証結果は review attribution 本体（`reviewEvents`）とは別系列で記録する。
- 監査ログには以下を残す。
  - `verifiedAt`
  - `result`（`passed` / `not_provided` / `failed`）
  - `reasonCode`（失敗時のみ）
  - `keyId`（解決できた場合）
- `reviewEvents` の意味を変更しない（レビュー操作ログと検証ログを混在させない）。

### Key management policy
- private key はアプリ実行環境に持ち込まず、CI/CD か専用署名基盤で管理する。
- key rotation を前提に `keyId` 必須、検証側は複数公開鍵を保持可能にする。
- 失効した鍵は deny-list で明示し、過去成果物再検証時は「当時有効だった鍵」を参照できる運用記録を残す。

### Backward compatibility policy
- `review-signature.json` は追加ファイル扱いとし、既存の `document.json` / `view.json` 形式を変更しない。
- 未対応クライアントは署名ファイルを無視して従来通り動作できることを互換要件とする。
- 将来アルゴリズム追加時は `algorithm` 列挙を拡張し、既存 `rsa-sha256`（初期値）を後方互換で維持する。

## Future Milestones (Phase 3+)
- M1: “現在のレビュア”設定（ローカルID発行）
- M2: reviewedフラグ変更時に ReviewEvent を追記
- M3: エクスポート時の redaction 実装（strip-identities / strip-all）
- M4: Merge audit log integration
- M5: SSOアダプタ（ReviewerRef生成規約の差し替え）
- M6: Optional signing（detached signature + verification UI）

## Notes
- 本機能は「責任所在を明確化し、レビュー運用を回す」ための補助である。
- 生成AIの要約/文章化が入る場合でも、“人間がレビューしたか”の区別ができることを優先する。

## 8. AUTH-ARCH-01: AuthContext/JIT 境界と表示責務

- 永続境界（review attribution 観点）:
  - 永続化: `userId`, `reviewerRef=user:<userId>`, `ownerRef=user:<userId>`
  - 非永続（揮発）: `amr/acr/aal/auth_time`, `roles/groups`, `trace_id`
  - 例外（identity台帳のみ保存可）: `display_name`, `email`
- PII最小化:
  - document/view/review event には `reviewerRef` のみ残す。
  - 表示名/メールは review event へ複写しない。必要時のみ identity台帳または外部ディレクトリ照会で補完する。
- 監査出力制約:
  - `amr/acr/aal/auth_time` は監査イベントの最小属性として任意出力可（欠損許容）。
  - `roles/groups` と `policyRef` は生値出力禁止。`rolesPresent/groupsPresent/policyRefPresent` のフラグと理由コードのみ許可。
  - トークン原文・WebAuthn credential id・IdP assertion 本文の出力は禁止。
- strict mode:
  - `ALLOW_JIT_PROVISIONING=false` では未登録 subject を `403` 拒否し、`POST /admin/provision/users` を唯一の事前登録導線とする。
  - strict mode の例外承認者は Platform Architecture Owner、審査責任は Compliance/Security Officer と Auth Architecture Lead。
