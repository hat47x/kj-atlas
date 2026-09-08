# 継続dogfood R41 — 確認手順を主張対象を証明できる観測面へ結ぶ

Date: 2026-09-07
Canvas: `doc_kj_atlas_dogfood_r41.json`

## 1. Trigger

R40統合後、Lane B2 の public configuration 監査を振り返ると、設定値やruntime実装そのものではなく、**運用者向けの確認手順が、その主張を実際には証明しない近傍surfaceを指していた**実陽性が複数続いていた。

代表例は次である。

### PR #3068 — adapter / resolver probe

access-control / document-binding / tenant-capability の3設定で、実装上は存在しない「adapter / resolver名の起動ログ確認」を案内していた。

修正後は、実在する SaaS preflight のconcrete-component検査と、external test-doubleへの到達確認へ戻した。

### PR #3071 — runtime profile

`KJ_ATLAS_RUNTIME_PROFILE` の確認先として `/healthz` を案内していたが、`/healthz` はliveness-onlyでprofileを返さない。

修正後は、validated profileを `runtimeProfile` として返す `GET /version` をprobe surfaceとした。

### PR #3073 — LLM provider

`KJ_ATLAS_LLM_PROVIDER` の確認先も `/healthz` だったが、provider kindを返さないため、設定されたproviderを証明できなかった。

修正後は `GET /ai/provider-status.providerKind` へ戻し、runtime registryのalias解決もfocused contractで固定した。

### PR #3074 — database readiness

`KJ_ATLAS_DATABASE_URL` の確認先として `/healthz` を使っていたが、liveness-only surfaceはDatabase到達性やschema headを検査しない。

修正後は、Database到達性とAlembic schema headを検査する `GET /readyz` をprobe surfaceとした。

4件ともruntime変更ではなく、**「確認できる」と公開していたEvidence pathの意味を実装へ戻した修正**だった。

## 2. KJで分けて見えたもの

### A. surfaceが実在することと、主張対象を証明できることは別である

`/healthz` は実在し、正常応答する有効なsurfaceである。

しかし、

```text
service is alive
```

を証明できることは、

```text
runtime profile is X
LLM provider kind is Y
Database is reachable and schema-ready
```

を証明できることを意味しない。

同様に「それらしい起動ログ」が近くに存在しそうでも、実装がそのcomponent名を出していなければ確認手順にはならない。

### B. 同じendpointでも、証明責務が違えば使い回せない

health / version / readiness / provider-status は、いずれもruntimeの状態を観測するsurfaceではある。

しかし責務は異なる。

```text
/healthz
  -> process/service liveness

/version
  -> build / runtime profile等のversion surface

/readyz
  -> service dependency readiness

/ai/provider-status
  -> provider registration / provider kind status
```

「HTTPで200が返る」「runtime情報っぽい」という近さだけでprobeを共用すると、確認手順が主張範囲を越える。

### C. positive probeだけでなく、negative meaningも明示する

有効なprobeは「何を確認できるか」だけでなく「何を確認していないか」も持つ。

```text
/healthz success
  != runtime profile verified
  != provider kind verified
  != Database readiness verified
```

このnegative boundaryがあることで、liveness成功をreadinessやconfiguration成功へ誤昇格させない。

### D. operator probeはEvidence contractである

configuration文書の「確認方法」は単なる便利な例ではない。

利用者がその結果を見て「設定が効いた」「依存先へ到達した」「runtimeがこのprofileで動いている」と判断するなら、そのprobeは実質的にEvidence contractになる。

したがって確認手順には、少なくとも次が必要である。

1. surfaceが実在する。
2. surfaceが対象propertyを実際に返す／検査する。
3. startup / request-time / readiness等のscopeが主張と一致する。
4. successが証明しない範囲も過大解釈しない。

## 3. 中心所見

**運用上のprobeは、近くにあるhealth/status surfaceではなく、主張対象を実際に返す、またはその条件を検査するEvidence surfaceへ結ぶ。surfaceの存在と、主張に対する証明能力は別契約である。**

短くすると、

```text
nearby observable surface
  != evidence for the target claim

operator probe
  = claim-specific evidence surface
```

である。

## 4. R33 / R34 / R39との関係

R41は既存dogfoodを置き換えない。

### R33 — canonical意味と観測surfaceへの伝播

R33は、APP_REVISIONのcanonical意味が正しいだけでなく、必要なstructured log surfaceへ値が届くことを分離した。

R41はその一段外側で、**運用手順がどのsurfaceをEvidenceとして読むか**を扱う。

```text
R33
  value reaches required observation surface

R41
  operator is directed to the surface that can prove the claim
```

### R34 — shape-aware current-contract conformance

R34は、scalar/default、finite enum、delivery surface、wiring state、ADR factual premiseを同じ文字列guardへ潰さず、shapeごとの実行可能な正本照合へ戻した。

R41も同じ方向を支持するが、新しい万能probe registryは作らない。

HTTP JSON field、readiness検査、preflight component、test-double到達など、証明shapeが違うからである。

### R39 — assertionが所有するsemantic surface

R39はDOM locatorが別の正当なstatus surfaceまで拾ったtest defectから、assertionの意味境界へlocator scopeを合わせた。

R41はUI locatorではなくoperator verificationのEvidence scopeを扱う。

両者に共通するのは、

```text
observable nearby thing
  != assertion / claimが所有するsurface
```

という点である。

## 5. 今回の設計判断

### 新しいgeneric checkerは追加しない

4件の実陽性は同じ中心所見を持つが、probe shapeは異なる。

- preflight component check
- external test-double reachability
- JSON field (`runtimeProfile`)
- JSON field (`providerKind`)
- dependency readiness (`/readyz`)

したがって、この段階で全configuration probeを一つのschemaやparserへ押し込まない。

既存の各focused contractが、対象keyと実装surfaceの関係を狭く固定する方がR34の方針とも整合する。

### 文書の確認手順を「例」扱いしない

確認手順がcurrent runtime factを主張するなら、文書レビューでは次を問う。

```text
このprobeは存在するか
このprobeは対象propertyを本当に返す／検査するか
このprobeのscopeは主張scopeと一致するか
成功から余計な事実を推論していないか
```

ただし、すべての運用例やトラブルシュート文をmachine contractへ昇格させるわけではない。

## 6. Finding triage

- F0: PR #3068 / #3071 / #3073 / #3074 の複数実陽性。いずれも「近傍surfaceは実在するが対象claimを証明しない」または「案内したsurface自体が実装上存在しない」確認手順driftだった。
- F1: 各PRでfocused contractへ戻して再発防止済み。R41として追加runtime修正は不要。
- F2: 新Issueなし。現時点ではpublic-config/doc conformance workstream内で閉じる。
- F3: 新ADRなし。architecture decisionではなくEvidence/probe選択の監査原則である。

## 7. 境界

R41は次を主張しない。

- `/healthz` を弱いendpointとして廃止すべき。
- health endpointは一つのpropertyしか返してはいけない。
- すべての確認手順を自動テスト化すべき。
- 全設定keyへ専用endpointが必要。
- HTTP endpointがlog / preflight / test-doubleより常に優れている。

重要なのはsurface種別ではなく、**そのsurfaceが対象claimの証明責務を実際に持つか**である。

また、R41を恒久required checkへ単独昇格しない。現在は実陽性ごとにfocused contractで閉じられており、generic automationの追加価値はまだ証明されていない。

## 8. 非主張

R41はcontinuous/internal dogfoodであり、Case 001〜003のformal cognitive comparison、第三者product-value validation、AI-IR named-provider evidenceを代替しない。

formal P1の現在地も変わらない。次の正式工程はfresh isolated context + frozen KJ Atlas UIでのCase 001 Arm C実走である。
