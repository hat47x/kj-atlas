# Schemas: Review Attribution (Proposal)

本ファイルは review attribution を view.json 側へ追加するためのスキーマ提案である。  
MVPでは未実装だが、将来の互換性のため設計段階で固定する。

## Location
- view.json (view metadata) に追加
- document.json には追加しない（default）

## Top-level additions to view.json

```ts
type ReviewAttributionPolicy = {
  storePII: boolean; // default false
  exportRedactionMode: "none" | "strip-identities" | "strip-all"; // default "strip-identities"
  retention?: {
    maxEvents: number; // default 2000
    maxDays?: number;  // optional
  };
};

type ReviewerProfile = {
  reviewerRef: string;       // opaque stable id (non-empty)
  displayName?: string;      // optional; only allowed when storePII=true
  contact?: string;          // optional; discouraged
  role?: string;             // optional
};

type ReviewTargetKind = "island" | "card" | "relation" | "summary";

type ReviewTargetRef = {
  kind: ReviewTargetKind;
  id: string; // entity id
};

type ReviewAction =
  | "markReviewed"
  | "unreview"
  | "approve"
  | "requestChange";

type ReviewEvent = {
  id: string;                 // unique
  target: ReviewTargetRef;
  action: ReviewAction;
  reviewerRef?: string;       // optional; recommended
  createdAt: string;          // ISO
  contextLabel?: string;      // e.g., "internal"|"external"|"self"
  reasonCode?: string;        // optional enumerated codes
  note?: string;              // optional; discouraged by default
};

type ViewMetadata = {
  // ...existing fields...
  reviewAttributionPolicy?: ReviewAttributionPolicy;
  reviewers?: ReviewerProfile[];
  reviewEvents?: ReviewEvent[];
};

type ReviewSignatureEnvelope = {
  version: "1";
  keyId: string;
  algorithm: "rsa-sha256";
  signedAt: string; // ISO
  payload: {
    documentDigest: string; // sha256:<hex>
    viewDigest: string; // sha256:<hex>
    reviewEventDigest: string; // sha256:<hex>
    attributionPolicyDigest: string; // sha256:<hex>
  };
  signature: string; // base64 detached signature
};

type ReviewSignatureVerification = {
  verifiedAt: string; // ISO
  result: "passed" | "not_provided" | "failed";
  reasonCode?: "digest_mismatch" | "key_not_found" | "signature_invalid";
  keyId?: string;
};
```

## Defaults
- reviewAttributionPolicy.storePII = false
- reviewAttributionPolicy.exportRedactionMode = "strip-identities"
- reviewAttributionPolicy.retention.maxEvents = 2000
- reviewEvents / reviewers 欠如は「履歴なし」として扱う

## Validation rules
- reviewerRef は空文字不可
- storePII=false の場合:
  - reviewers[].displayName / reviewers[].contact は保存しない（読み込み時に破棄、または無視）
- reviewEvents は以下を満たす:
  - id 重複なし
  - target.id は既存要素IDであることが望ましい
    - ただし過去イベントの再現のため、参照先欠落は 読み込み時にエラーにしない（警告扱い）
  - createdAt は ISO 文字列
- retention:
  - export/import 時に maxEvents を超える場合は古い順に削除してよい
  - details の肥大化を避けるため、必要なら event ごとの note 長を制限してよい（例: 500 chars）

## Export redaction behavior
- none:
  - reviewers / reviewEvents をそのまま出力
- strip-identities:
  - reviewers[].displayName / reviewers[].contact を除去
  - reviewEvents[].reviewerRef は残す（匿名ID）
- strip-all:
  - reviewers / reviewEvents を出力しない
  - policy 自体は残してよい

## Interoperability guidance
ReviewerRef 推奨フォーマット（例）:
- ローカル: user:local:<random>
- SSO: user:sso:sub:<subject>
- 組織独自: user:org:<opaque>

重要:
- reviewEvents は暗号署名されない前提であり、監査証跡としての強度は限定的。
- 将来拡張で detached signature を追加する場合も、上記構造を壊さず付加情報として実装する。

## Optional signing additions (Phase3 M6)

### File placement
- `review-signature.json`（新規、任意）
  - `ReviewSignatureEnvelope` を保存する detached signature ファイル
  - `document.json` / `view.json` を変更せず同梱する

### Verification status model
- 署名検証結果は監査ログ側で `ReviewSignatureVerification` として扱う。
- `reviewEvents` へ混在させない（レビュー操作ログの意味境界を維持）。

### Validation rules for envelope
- `keyId` は空文字不可
- `algorithm` は当面 `rsa-sha256` のみ許可（将来列挙拡張）
- `payload.*Digest` は `sha256:<hex>` 形式
- `signedAt` は ISO 8601 文字列
- `signature` は base64 文字列（空文字不可）

### Verification behavior
- 署名ファイル欠損:
  - `result=not_provided`
  - import / view / review 操作は継続（non-blocking default）
- 署名ファイルあり + 検証成功:
  - `result=passed`
- 署名ファイルあり + 検証失敗:
  - `result=failed` + `reasonCode`
  - 既定では read-only で閲覧継続可、share/export で追加確認

### Policy override (org optional)
- 組織運用で fail-closed が必要な場合のみ `requireSignature=true` を別途 policy で指定する。
- 既定は `requireSignature=false` とし、無署名をエラー扱いにしない。

### Backward compatibility
- 署名情報は sidecar 追加のため、既存 `ViewMetadata` スキーマ version を変更しない。
- 旧クライアントは `review-signature.json` を読まなくても動作可能。

