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

## Future Milestones (Phase 3+)
- M1: “現在のレビュア”設定（ローカルID発行）
- M2: reviewedフラグ変更時に ReviewEvent を追記
- M3: エクスポート時の redaction 実装（strip-identities / strip-all）
- M4: 組織向け署名（オプション、detached）
- M5: SSOアダプタ（ReviewerRef生成規約の差し替え）

## Notes
- 本機能は「責任所在を明確化し、レビュー運用を回す」ための補助である。
- 生成AIの要約/文章化が入る場合でも、“人間がレビューしたか”の区別ができることを優先する。
