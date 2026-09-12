# Actor / Role / Interest → Context Projection 設計根拠

- Status: Research rationale
- Date: 2026-09-12
- Formal contract: `02_Architecture/information_network_projection_contract.md`
- Parent: `multi-actor-cognitive-consensus-space-2026-09-12.md`

## 1. この文書の位置づけ

本書は、Actor-aware Context Projectionを正式契約へ至らせた設計理由だけを残す。

型、I/F、Query pipeline、Permission、SafeMode、Graph planeの正本はすべて `02_Architecture/information_network_projection_contract.md` とする。本書独自のR0型や旧Query contractは定義しない。

## 2. 根幹の趣旨

SUI Sensemakingでは、人間、生成AI、SEI Cognition、外部systemが同じ情報ネットワークへ参加するが、同じ情報を同じ形で見る必要はない。

Context Projectionは、現在の問いに必要な情報を、元情報・relation・provenanceへ戻れる形で構成した認知用Viewである。

ただしProjectionは次ではない。

- truth
- importance ranking
- consensus
- actor personality profile
- access-control bypass

Projection生成だけでSUI Information Networkを書き換えない。

## 3. Actor / Role / Interest / Inquiry / Permissionを分離する理由

### Actor

誰／何が問い合わせているかを表す。identityはopaque referenceでよい。Actor kindは権限を意味しない。

### Role

今回のinteractionでの責務を表す。`explore`、`compare`、`propose`、`review`、`approve`等を想定するが、Roleはpermissionを付与しない。

### Interest

その時点で何を見たいかを表す一時的な認知焦点である。恒久的なpersonaへ固定しない。

### Inquiry

今回考えたい具体的な問いである。

### Permission

authorization layerがserver-sideで解決したeffective permissionだけを用いる。requester自己申告、Role、Actor kindから推測しない。

## 4. SelectionとProjectionを分ける理由

Query Intentは「何を見るか」、Projection Formは「どう返すか」である。

同じselectionを、例えば次のように返せる。

```text
same selected evidence
  ├─ Human -> spatial layout + comparison table
  ├─ Generative AI -> bounded structured context
  ├─ SEI -> compact subgraph
  └─ External system -> typed machine-readable projection
```

Actorによる差は、まずPresentationの差として扱う。同一permission / scope / inquiryでactor identityだけが違う場合、selectionを恣意的に変えない。

## 5. Permission / SafeMode

未レビュー情報は、少なくとも次のAND条件を満たす場合だけQuery対象へ入れる。

1. server-resolved permissionが未レビュー閲覧を許可する
2. trusted runtimeのSafeMode policyが許可する

片方でも満たさなければ、selection前に除外する。Projection生成失敗時にraw full networkをfallback返却しない。

## 6. Consensusとの境界

次は同一ではない。

```text
observed
 != acknowledged
 != understood
 != accepted-for-working
 != approved
```

AI / SEI / external systemのproposalはapprovalではない。ConsensusGraphへの昇格はformal contractどおりhuman approvalを経る。

## 7. 最終判断

R0で検証していた「旧Queryへcompileできるか」は、最終設計上の要件から外した。

正式版では、

```text
SUI Information Network
 -> QualitativeNetworkSnapshot
 -> ContextProjectionRequest
 -> D0..D5 Selection / Analysis
 -> Context Projection
```

を直接実装する。

旧Document / Query / Bundleへの互換adapterは作らない。
