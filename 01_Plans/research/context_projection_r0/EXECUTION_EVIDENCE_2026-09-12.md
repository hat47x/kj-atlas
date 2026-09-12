# Context Projection R0 — Execution Evidence 2026-09-12

- Status: Executable research evidence
- Scope: synthetic fixtures only
- Production claim: none

## 1. 確認したこと

`compile_projection_request.py`のresearch compilerについて、Human / Generative AI / SEIのsynthetic fixtureを用いて境界を確認した。

確認項目:

1. Human / SEI / Generative AIのrequestが、現行`ContextQueryV1`と同じclosed-world top-level keyへcompileされる。
2. `safeModePolicy`は`strict`から変化しない。
3. opaque `actorRef`は下流`ContextQuery`へ混入しない。
4. `approve` Roleだけではapproval permissionを得ない。
5. `propose` Roleがあっても`canCreateProposal=false`なら`outputMode=proposal`へ昇格しない。`synthesize` Roleが残るfixtureでは`summary`となる。
6. Permissionの`resolutionSource`が`server_resolved`でなければfail-closedする。
7. 未レビュー情報は`canSeeUnreviewed=true`とtrusted SafeMode allowanceの両方がある場合だけ`includeUnreviewed`となる。
8. readable scopeを縮小するとcompiled constraintsも縮小する。
9. roles / intents / readable scopes等のset-like input順序を変えてもcanonical outputは変化しない。
10. 未知Actor kindや空のreadable scopeはfail-closedする。

上記10境界を同一compilerロジックでsynthetic実行し、すべて通過した。

## 2. このEvidenceが意味すること

- Actor / Role / Interestをproduction `ContextQueryV1`へ直接追加せず、research wrapperから既存query形へcompileする方式が実行可能である。
- RoleとPermissionを分離したまま、proposal / reviewFilter等の既存query semanticsへ落とせる。
- SafeModeとpermissionをAND条件として扱うfail-closed境界を維持できる。
- 同じ意味のset-like inputについて、query生成を決定論的にできる。

## 3. このEvidenceが意味しないこと

- Actor-aware projectionが実利用で認知品質を向上させること。
- `constraints.projectionResearchR0`がproduction契約として十分であること。
- Authorization layerが実装済みであること。
- ContextProjectionR0の返却形式が確定したこと。
- Consensus段階の新しいenumが必要であること。
- production API / schema v2へ進むべきであること。

次のEvidenceは、synthetic information network上でD0 deterministic qualitative queryを実行し、同一selectionをHuman / AI / SEIの異なるProjection Formへ返せるかを確認する。
