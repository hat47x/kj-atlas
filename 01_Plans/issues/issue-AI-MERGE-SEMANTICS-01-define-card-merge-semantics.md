# Issue: AI-MERGE-SEMANTICS-01 `suggest-merges` の意味境界と受入条件を定める

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Architecture / AI Integration
- Status: Open
- Source Issue: `AI-IR-STAGE5-SCOPE-01` Stage 5
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/src/kj_atlas_api/llm_input_ir.py`, `00_Prompt/domain.md`, `00_Prompt/kj_technique.md`, `00_Prompt/qualitative_card_quality_requirements.md`, `02_Architecture/api.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`, `AI-IR-PROJECTION-01`, `AI-IR-STAGE5-SCOPE-01`
- Expected verification level: integration

## 課題

`POST /ai/suggest-merges` は現在、文書内の全カードについて `id` と `text` を並べ、「similar cards」のmerge候補を最大10件返すようLLMへ依頼している。応答は `groupId`、2件以上の `cardIds`、`mergedTextDraft`、任意の `rationale` から成る。

しかし、現行契約には「似ている」と「統合してよい」の境界がない。実装上も、候補カードの `holdState`、`claimType`、島所属、直接の `negate` 関係、矛盾を表す `evidenceLinks`、既存のmerge系譜をAI入力や決定論的な後段検査に使っていない。そのため、語彙が近いだけの少数意見、反対意見、観察と仮説、保留中のカードまで一つへ丸める余地がある。

これはkj-atlasの目的と逆向きである。KJ法の束ねは、既存分類へ押し込む操作ではなく、カードが訴えている内容を聴きながら近いものを集め、まとまらない一枚を無理に入れない作業である。また、対立は対立として残す。`domain.md` も、保留を勝手に解消しないこと、統合結果を単一の正解として扱わないこと、少数意見や矛盾をノイズとして削除しないことを不変条件としている。

したがって `suggest-merges` をIRへ移行する前に、この経路が扱う「merge」をKJ法上のグループ編成や意味統合から明確に分離する。

## 決定する意味境界

### この経路でいうmerge

`suggest-merges` の仕事は、**実質的に同じ中心内容を重複して保持しているカードについて、冗長性を整理する候補を提示すること**とする。

候補に含めてよいのは、少なくとも次を満たす場合に限る。

- 各カードが同じ中心的な観察・発言・経験・主張を表している。
- 一方にしかない条件、主体、時点、確実さ、否定、例外を捨てずに一つの本文へ表現できる。
- 統合後の本文が、元カードの意味を広げたり狭めたりしない。
- 元カードと出典・系譜へ戻れることを前提にできる。

単なる語彙類似、同じテーマ、同じ島に属しそうであることは、mergeの十分条件ではない。

### この経路で扱わないもの

次は `suggest-merges` の仕事に含めない。

- **KJ法のグループ編成**: 近い訴えを束として並べる仕事は `suggest-card-groups` / Island側の責務とする。元カードを一枚へ畳まない。
- **表札生成**: 複数カードが言いたいことを代弁する上位文は、元カードを保持した表札として扱う。
- **核融合法・04ステップに相当する意味統合**: 複数の異なるカードから核を保った新しい意味単位を作る場合は、元カードを消すmergeとして実装しない。将来必要なら、source cardを保持した新規の統合カード／表札を提案する別契約として設計する。
- **多数派への吸収**: 少数意見、例外、矛盾、違和感を「似ているから」と多数派本文へ吸収しない。
- **自動適用・自動削除**: 本経路はproposal-onlyを維持し、人間承認なしにカード本文・所属・系譜を変更しない。

`MergeSuggestion.groupId` はKJ法のGroup/Clusterを意味しない。あくまで一つのmerge提案を識別するproposal-local IDである。将来の契約改訂では、誤解を避ける名前への変更も検討対象とする。

## merge候補を抑止する条件

次の条件は、LLMへの注意書きだけでなく、実装側の決定論的な検査で候補から除外する。

### 1. 保留状態

候補のいずれかに `holdState` (`held` / `pending` / `shelved`) がある場合、その組をmerge候補として返さない。

保留は「まだ畳まない」という人間の判断であり、類似判定より優先する。将来、人間が明示的に保留カードも比較したいという別操作を設ける場合は、その操作でのみ境界を開く。

### 2. 明示的な対立・矛盾

候補カード間に次が存在する場合、その組をmerge候補として返さない。

- card-to-card の `negate` relation
- `type=contradicts` の `evidenceLink`

`contradictionState` が `confirmed` / `held` ならなおさら統合しない。`unconfirmed` であっても、「同じ意味」と断定してmergeするより対立候補を残す側へ倒す。

### 3. 認識上の位置づけ

両方に `claimType` が設定され、その値が異なる場合はmerge候補として返さない。

観察・引用、解釈、仮説、問いなどの位置づけが異なる情報は、本文が似ていても同じ情報単位ではない。片方が未設定の場合は、それだけで自動的に同一とみなさず、本文と周辺文脈から同一性を判断する。

### 4. 既存merge系譜

`mergedIntoCardId`、`canonicalId`、`repOf` など既存の統合系譜を確認し、既に別カードへ統合済みのカードを新たな独立候補として再mergeしない。必要ならcanonicalな代表へ解決してから候補集合を作る。

### 5. 同一応答内の競合提案

一枚のカードを同じ応答内の複数merge候補へ重複して含めない。

同じカードについてA+BとA+Cを同時に「適用候補」とすると、どの統合を先に採るかで意味と系譜が変わる。複数の可能性を残したい場合は、相互排他的な代替案であることを表す別契約が必要であり、現行 `MergeSuggestion[]` では表現できない。現行契約では一枚につき最大一候補とする。

## mergeを禁止しないが、文脈として渡す情報

### 島所属

異なる島にあることだけをhard vetoにはしない。同じ観察が重複入力され、別々の島へ置かれている場合もあり得るためである。

一方、島の違いは「利用者が別の意味文脈で扱っている」可能性を示す。IR移行時には島所属をAIへ渡し、異なる島のカードを語彙類似だけで統合しないよう注意情報として使う。島所属そのものをmerge判定の正解ラベルにはしない。

### `equivalence` / `related`

既存relationの `equivalence` はmerge候補を支持する材料になり得るが、それだけでmergeを自動決定しない。`related` はさらに弱い補助情報に留める。人間が記録したrelationは判断材料であり、カード削除の許可ではない。

### 出典・sources

異なる出典から同じ内容が独立に観察されている場合、情報価値は「重複」ではなく裏付けの増加にあることがある。したがって出典差を理由に機械的にmerge禁止ともmerge推奨ともせず、提案時には出典差があることを失わない。

mergeを人間が採用した場合も、元カードの `sources`、`repOf`、canonical/merge lineageなど、元情報へ戻る経路を失ってはならない。`mergedTextDraft` に出典を創作して埋め込まない。

## AI入力契約

本経路は `DocumentV1` 由来の構造がmerge可否の判断に直接必要な **Document-backed structured task** である。ADR-0069 D5=Aに従い、generic Document IRまたはroute固有投影をprovider実入力の正本とする。

少なくとも次をprovider手前へ届ける。

- 候補対象カードの `id` / IR正規化後本文
- `holdState`
- `claimType`
- 人間が確定させた島所属
- 候補間のcard relation、特に `negate` / `equivalence`
- 候補へ接続する `evidenceLinks` と `contradictionState`
- merge済みカードを再候補化しないために必要な系譜情報

全Documentを同じ重要度でpromptへ列挙することを目的にしない。大規模文書では、まず安全に候補比較できる集合を決め、必要意味をroute-requiredとして保護する。IR上限により候補の意味判定に必要なカード本文・relation・evidenceが欠ける場合は、不完全な入力でmergeを提案せずfail-closedにする。

SafeModeは、既存のroute側検査を一次防御として残し、IRまたはroute固有入力ビルダー側の検査を第二層として維持する。

## promptと応答検査

promptには少なくとも次を明記する。

- similarity alone is not sufficient for merge
- same topic is not sufficient for merge
- merge only when the same central meaning can be retained without losing distinguishing context
- leave minority, contradictory, held, or materially different cards separate
- proposal only; do not apply, delete, or rewrite source cards

LLM応答は信用せず、後段で決定論的に検査する。

- 未知ID、重複ID、2件未満、上限超過は現行どおり拒否する。
- holdを含む候補を除外する。
- `negate` / contradiction evidenceを含む候補を除外する。
- 異なる既知 `claimType` を含む候補を除外する。
- merge済み系譜上の無効候補を除外する。
- 同じカードが複数候補に出た場合は、順序依存で黙って採用せず、応答全体を不正として扱うか、明示した決定論的規則で候補を除外する。実装時にどちらかをテストで固定する。推奨は**応答全体を不正として扱う**ことである。
- `mergedTextDraft` は提案本文に過ぎず、元カードを削除・上書きしない。

## 実装方針

1. route-required meaningを固定するintegration regressionを先に追加する。
2. `suggest-merges` 専用のIR投影または入力コンテキストビルダーを追加する。
3. promptを「similar cards」から上記の冗長性整理契約へ狭める。
4. LLM応答後の決定論的merge guardを追加する。
5. `LLMRequest.inputs` とprovider promptの双方が同じ正規化済み入力を使い、Document生本文から同じ意味を迂回送出しないことを回帰で固定する。
6. API文書と `AI-IR-STAGE5-SCOPE-01` を実装結果へ同期する。
7. 内容・構造を確定した後、意味を変えず自然な日本語として全文を読み直す。

## 受入条件

- [x] `suggest-merges` をKJ法のグループ編成・表札生成・意味統合から分離し、冗長性整理のproposal-only経路として定義する。
- [x] 核融合法・04ステップ相当の意味統合は元カードを消すmergeとして扱わないと明記する。
- [x] hold、明示的対立・矛盾、異なる既知claimType、既存merge系譜、同一応答内の候補競合を保護対象として定義する。
- [x] 島所属・equivalence・出典差は単純なhard veto/許可ではなく、意味文脈として扱うと定義する。
- [x] ADR-0069 D5=Aに基づき、本経路をDocument-backed structured taskとして分類する。
- [ ] 上記のroute-required meaningをintegration regressionとして固定する。
- [ ] `suggest-merges` のprovider実入力をgeneric Document IRまたはroute固有投影へ移す。
- [ ] promptを冗長性整理契約へ更新する。
- [ ] LLM応答後の決定論的merge guardを実装する。
- [ ] 同一カードが複数候補へ出た場合のfail-closed挙動をテストで固定する。
- [ ] 元カード・sources・merge/canonical系譜が採用後も追跡可能であることを、既存適用経路と統合テストで確認する。
- [ ] SafeMode二層、PII最小化、structured-text-only、IR上限のfail-closedを確認する。
- [ ] `02_Architecture/api.md` と `AI-IR-STAGE5-SCOPE-01` を実装結果へ同期する。
- [ ] 最終成果物を自然な日本語として全文ドラフトし直す。

## 完了境界

このIssueは、単に `suggest-merges` をIR経由へ変えた時点では完了しない。

**「同じ中心内容の冗長性整理」と「異なる意味を束ねるKJ上の統合」をコード上で取り違えず、保留・対立・少数意見・出典・系譜を失わないことをintegration regressionで固定し、provider実入力がその契約を迂回しないところまで**を完了条件とする。
