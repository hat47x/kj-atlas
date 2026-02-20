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


