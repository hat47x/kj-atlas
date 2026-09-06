# Issue Draft: AI-ROUTE-HELD-LINKAGE-01 Final Judgement失敗とproposal held遷移の明示的linkage

- Type: Architecture / Safety contract
- Status: Draft
- Source Issue: `AI-ROUTE-01` MMR-06
- Priority: P2
- Owner: Maintainer
- Scope: `00_Prompt/ai_cognitive_externalization_requirements.md` §7.1a, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/proposal_decision_repository.py`, `03_Implement/backend/src/kj_atlas_api/models_ai.py`, `02_Architecture/api.md`, `02_Architecture/schemas.md`
- Related ADR/Spec: `AI-ROUTE-01`, `00_Prompt/ai_cognitive_externalization_requirements.md` MMR-06
- Expected verification level: `integration`

## 課題

`AI-ROUTE-01` MMR-06 は、`final_judgement` を利用できない場合に auto-publish へフォールバックせず、**当該外部エージェントproposalを `held` へ遷移させる**ことを要求している。

現行実装には `ExternalAgentProposalRecord.status = proposed | accepted | rejected | held` と、人間のdecision endpointによる `proposed -> held` が存在し、`held` proposalはapplyできない。一方、`final_judgement` に分類される `check_narrative` / `detect_contradiction` route はproposal識別子を受け取らず、どのexternal proposalに対する最終判断なのかをserverが一意に特定する契約がない。

したがって、provider/model利用不能時に「最新proposal」「同じdocumentのproposal」等を推測してholdすると、無関係なproposalを停止させる危険がある。また、既存の `decision=hold` は人間decisionとして記録されるため、system/provider failureによるholdへそのまま流用すると監査上の意味も混同する。さらに現行repositoryではdecision可能なのは `proposed` のみで、`held` 後の再試行・解除経路も別途固定されていない。

MMR-06を実装する前に、**proposal identity / system hold / recovery** の三点を明示的な契約として固定する必要がある。

## 非目標

- proposalをdocument ID、作成時刻、最新順、内容類似度等から推測しない。
- provider failureを成功したfinal judgementとして扱わない。
- system holdを人間の `accept/reject/hold` decisionとして偽装しない。
- `held` からの回復を暗黙のauto-accept / auto-publishにしない。
- MMR-06を理由にintermediate taskのrouting/fallback契約を変更しない。

## 決める契約

### 1. proposal identity linkage

external-agent proposal flowの一部としてfinal judgementを呼ぶ場合、対象proposalをserverが一意に識別できる**明示的なproposal reference**を持たせる。候補はorchestration requestの `proposalId`、または同等のserver-side typed referenceとする。

- referenceはclient入力をそのまま信用せず、対象proposalの存在・document/source整合をserver側で検証する。
- `check_narrative` / `detect_contradiction` の一般利用までproposal必須にはしない。MMR-06のstate transitionは「external proposal flowに明示的にlinkされたfinal judgement」に限定する。
- linkageがないstandalone final-judgement callではprovider failureを通常どおりfail-closedで返し、任意proposalを変更しない。

### 2. availability failure -> system held

明示的にlinkされたproposalが `proposed` で、final-judgement model/providerを利用できず有効な判断を得られなかった場合だけ、server-side transitionで `held` にする。

最低限、実装時に以下のfailure classを列挙して固定する。

- provider/model unavailable
- timeout
- model-governance / routing上、eligible final-judgement modelを解決できない状態

`provider_validation`、parse failure、policy rejection等を同じ「利用不能」に含めるかは、実装前にAPI/error contractと合わせて明示する。曖昧なcatch-allで全失敗をholdしない。

### 3. system hold audit semantics

system/provider failureによるholdは、人間decision endpointとは別の意味として監査可能にする。

記録には少なくとも次を含める。

- proposal ID
- previous/new status
- transition source = `final_judgement_unavailable` 等のmachine-readable reason
- routing stage = `final_judgement`
- provider/model/trace ID（取得できた範囲。secretは含めない）
- timestamp

既存human decision eventのactorを架空のユーザーにして代用しない。

### 4. state/race contract

- 自動遷移対象は原則 `proposed -> held` のみとする。
- 既に `accepted` / `rejected` のproposalをprovider failureで巻き戻さない。
- 既に `held` の場合の同一failureはidempotentに扱い、重複イベントの扱いを固定する。
- final judgementとhuman decisionが競合する場合、repositoryのatomic state transitionで誤上書きを防ぐ。

### 5. recovery contract

現行repositoryでは `held` がhuman decision上ほぼ終端状態であるため、system holdを導入する前に回復経路を明示する。

最低限、次のいずれかを仕様として選び、integration testで固定する。

- 明示的retryでfinal judgementを再実行し、成功時に `held -> proposed` へ戻して人間decisionを待つ。
- 人間が明示的にrelease/reopenし `held -> proposed` とした後に再試行する。
- `held` を終端として新proposalを作り直す。

どの方式でも、再利用可能になっただけで `accepted` / publishへ自動遷移させない。

## 受入条件

- [x] external proposal flowとfinal judgementの対象proposalを、推測なしで一意に結ぶtyped linkageをAPI/schemaへ固定する。— R1: optional `externalProposalRef` + server-side `(tenant, doc, proposal, sourceBundleHash, origin)` validationを追加。
- [ ] linkageなしのstandalone `check_narrative` / `detect_contradiction` failureがproposal stateを変更しないことを固定する。
- [ ] MMR-06対象failure classを列挙し、明示的にlinkされた `proposed` proposalだけをsystem `held` へatomic遷移させる。
- [ ] system holdがhuman decisionと区別できるaudit/event contractを持つ。
- [ ] `accepted` / `rejected` を巻き戻さず、既存 `held` / concurrent decisionを安全に扱う。
- [ ] `held` 後の明示的recovery contractを選択・実装し、成功してもauto-accept / auto-publishしない。
- [ ] integration testで少なくとも provider unavailable、timeout、standalone call、already-decided race、recoveryを検証する。
- [ ] `AI-ROUTE-01` MMR-06は上記integration evidenceが揃うまで未完了のままとする。

## 検証計画

- proposal repositoryのatomic transition unit test
- final judgement orchestration integration test
- `held` proposalのapply拒否回帰
- routing/audit eventのsource/reason/trace検証
- `python 01_Plans/docs_check.py`

## 補足

このissueはMMR-06を遅らせるための抽象化ではなく、現行routeがproposal IDを持たない状態で誤proposalをholdすることを防ぐための安全境界である。実装時は、この契約を満たす最小のorchestration/linkageを選び、一般AI routeへ不要なproposal stateを持ち込まない。

## R1 実装履歴（2026-09-06）

- `ExternalProposalReference` (`proposalId` + `sourceBundleHash`) を追加し、`check-narrative` / `detect-contradiction` に optional linkage として接続。
- serverはrequestの `doc.id` と登録済みproposal rowを照合し、external-agent origin / source hashまで一致した場合だけprovider処理へ進む。
- `detect-contradiction` でlinkageだけを渡してdocumentを省略することは禁止（422）。proposal IDからdocumentを逆引きしない。
- standalone呼出しのrequest shape/処理は維持。
- 本R1はread-only identity gateのみ。system `held` 遷移、failure class、system audit、recoveryは未実装であり、MMR-06は未完了のまま。
