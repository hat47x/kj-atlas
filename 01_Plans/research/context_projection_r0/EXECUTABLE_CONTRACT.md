# Context Projection R0 — executable contract

この文書はresearch utilityが現在受け取るfieldを固定する。上位概念文書より実行寄りであり、production contractではない。

## Request

```json
{
  "requestId": "opaque query correlation id",
  "actor": {
    "actorRef": "opaque actor ref",
    "kind": "human | generative_ai | sei_cognition | external_system"
  },
  "roles": ["observe | explore | compare | critique | synthesize | propose | review | approve | publish"],
  "interest": {
    "focusRefs": [],
    "themes": [],
    "seek": ["neighborhood | contrast | bridge | residual | unresolved | temporal | provenance | affinity | readout"]
  },
  "inquiry": "current inquiry",
  "permission": {
    "resolutionSource": "server_resolved",
    "readableScopes": [],
    "canSeeUnreviewed": false,
    "canCreateProposal": false,
    "canReview": false,
    "canApprove": false,
    "canPublish": false
  },
  "sourceScope": "document | view | island",
  "desiredProjection": ["subgraph | path_list | card_stack | comparison_table | spatial_layout | timeline | provenance_matrix | compact_narrative"],
  "diversityNeed": "default | increase",
  "unresolvedNeed": "default | increase",
  "previewConfirmed": true
}
```

## Trust boundary

- `actor.actorRef`はopaque referenceであり、emailやprovider UIDを直接入れない。
- `permission.resolutionSource`はresearch utilityでは必ず`server_resolved`とする。
- utility自身はauthorizationを行わない。
- RoleはPermissionを付与しない。
- Actor kindはPermissionを付与しない。
- `previewConfirmed`は現行CE1 Preview gateを迂回するものではなく、その状態を既存`ContextQueryV1`へ渡すだけである。

## Output

compiler outputのtop-level keyは現行`ContextQueryV1`と完全一致させる。

```text
queryId
goal
scope
depth
constraints
reviewFilter
safeModePolicy
outputMode
previewConfirmed
```

R0固有のactorRefはoutputへ含めない。Actor kind、Role、Interest等、selectionに必要なresearch hintだけを`constraints.projectionResearchR0`へ置く。

## Determinism

同じ意味のset-like inputは、配列順が違ってもcanonical outputを同一にする。

対象:

- roles
- focusRefs
- themes
- seek
- desiredProjection
- readableScopes

## SafeMode

`reviewFilter=includeUnreviewed`になるには次の両方を必要とする。

1. server-resolved `canSeeUnreviewed=true`
2. trusted callerから`safe_mode_allows_unreviewed=true`

片方だけなら`reviewedOnly`へfail-closedする。
