# Third-Party Value Validation — Publication / Data Boundary

- Status: Prepared before first third-party session
- Date: 2026-08-30
- Related: `VALUE-REALNESS-01`, `PRACTICE-CULTURE-01`, `third-party-value-validation-execution-plan.md`, `third-party-value-session-record-template.md`

## 1. 目的

第三者価値検証では、KJ Atlasの価値を確かめるために本人の実資料や仕事上の文脈を扱う。

一方、このrepositoryはpublic OSSであり、Gitへ入った情報は後から削除してもfork、clone、cache、引用等から完全に回収できない可能性がある。

したがって、**「検証に必要な証拠」と「public Gitへ置いてよい証拠」を同一視しない。**

本書は、第三者sessionのraw materialとpublic repositoryに残すsanitized evidenceの境界を固定する。法的同意書の代替ではなく、maintainer/operatorの実務上のfail-closed規則である。

## 2. Default boundary

既定は次とする。

> **第三者のraw material、raw transcript、識別可能なartifactはpublic repositoryへcommitしない。**

public repoへ置けるのは、本人とoperatorが公開範囲を確認した**sanitized validation evidence**だけとする。

公開が価値検証の成立条件ではない。十分に匿名化できない場合は、public evidenceを粗くする、参照だけ残す、またはpublic repoへ何も残さないことを許容する。

## 3. Public repoへ原則入れないもの

- 参加者の氏名、連絡先、アカウント識別子。
- 明示許可のない所属、顧客名、案件名、取引先名。
- raw interview / meeting transcript。
- raw audio / video。
- 元の業務文書、調査票、顧客発言、自由記述データ。
- 識別可能なscreen shot / export。
- 契約、営業秘密、未公開企画、内部URL、ticket ID等。
- 第三者本人ではなく別人の個人情報。
- consent / withdrawal連絡に必要な個人連絡情報。
- 小さな文脈の組合せだけで本人や組織を推定できるquasi-identifier。

「名前を消した」だけで匿名化済みとは扱わない。

## 4. Public repoへ残してよい候補

必要最小限かつ確認済みの場合に限る。

- 非識別のSession ID。
- 粗いpractice context。
- 参加者が公開可能と確認したparaphrase。
- 元資料を復元できない粒度の観察記録。
- value moment / friction / no-use reason / stop reasonの要旨。
- 公開可能なKJ Atlas documentのsanitized derivative。
- 「証拠はprivate materialに存在するがpublicには保持しない」というexistence note。
- finding triage結果。

public evidenceは「第三者が言ったことを証明するための最大量」ではなく、**判断を監査するための最小量**を目標とする。

## 5. Raw working material

raw materialの保存先をこのrepositoryで規定しない。

最低限の規則だけを置く。

- 参加者/operatorが管理可能な場所で扱う。
- public Gitへ自動同期されるdirectoryをraw保管場所にしない。
- session開始前に、保存するか、session後に破棄するかを決める。
- 保存する場合は、用途と保存期間を参加者へ説明する。
- KJ Atlas自体にraw materialを保存した場合、そのdocument/exportをpublic dogfood fixtureへ流用しない。

安全な保存先が用意できない場合、raw materialを保存しない運用を選ぶ。

## 6. Session ID / pseudonym

- Session IDは本人名、会社名、メールアドレス等から生成しない。
- aliasは本人が公開を望まない限り識別情報を含めない。
- session間のlinkabilityが不要なら、同一人物を追跡可能な共通IDを作らない。
- 実践文脈の説明は、価値解釈に必要な粒度を超えて細かくしない。

## 7. Publication gate

public repoへsession-derived artifactをcommitする前に、最低限次を確認する。

- [ ] raw materialではなくsanitized derivativeである。
- [ ] participant identity / organizationを不要に推定できない。
- [ ] confidential / contractual / third-party materialが含まれない。
- [ ] screenshot / exportのmetadataや画面端に識別情報が残っていない。
- [ ] participantが合意した公開範囲を越えていない。
- [ ] publicに残さなくても検証が成立する情報を過剰に公開していない。
- [ ] withdrawal/deletionについて、Git公開後の回収不能性を誤解させていない。

1項目でも不明ならcommitしない。

## 8. Withdrawal / deletion

### Public commit前

参加者が撤回した場合、合意した範囲に従いraw working material / draft evidenceを削除または非利用化する。

### Public commit後

public Gitへ公開した情報はrepositoryから削除できても、既に取得されたclone / fork / cache /引用まで完全に回収できない可能性がある。

そのため、**撤回可能性を担保する手段として「後からGit履歴を消す」ことに依存しない。**

この制約はsession開始前に説明し、公開commitはsanitizationと確認後にのみ行う。

## 9. Evidence strength and privacy

privacyのためにpublic evidenceを粗くした場合、それを強い証拠であるかのように装わない。

例:

- `private evidence verified by operator; not public`。
- `participant wording paraphrased for privacy`。
- `artifact exists but was not retained`。

公開できないことを欠陥とみなさない一方、第三者が再検証できないというepistemic limitationは明示する。

## 10. Finding triageとの関係

- privacy / publicationだけの摩擦はまず `VALUE-REALNESS-01` の実行観察として保持する。
- 特定sessionだけの保存事情を製品要求へ一般化しない。
- 複数実利用で「KJ Atlas自身のdata boundary / sharing / AI送信契約が仕事を成立不能にする」ことが再現した場合はF2候補を検討する。
- 権限、安全、共有意味論等の横断的contract変更が必要と実証された場合だけ `ADR-0047` に従ってADR候補とする。

本書そのものを新しい製品ADRとはしない。
