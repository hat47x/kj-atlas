# 第三者価値検証 — 公開・データ境界

- 状態: 最初の第三者session開始前に準備済み
- 日付: 2026-08-30
- 関連文書: `VALUE-REALNESS-01`, `PRACTICE-CULTURE-01`, `third-party-value-validation-execution-plan.md`, `third-party-value-session-record-template.md`

## 1. 目的

第三者価値検証では、KJ Atlasの価値を確かめるために、本人の実資料や仕事上の文脈を扱う。

一方、このrepositoryはpublic OSSである。Gitへ入った情報は、後からrepository上で削除しても、fork、clone、cache、引用等から完全には回収できない可能性がある。

そのため、**検証に必要な証拠と、public Gitへ置いてよい証拠を同一視しない。**

本書は、第三者sessionで扱うraw materialと、public repositoryへ残せるsanitized evidenceとの境界を定める。法的な同意書の代わりではなく、保守者・操作者が実務上守るfail-closedの規則である。

## 2. 既定の境界

既定では、**第三者のraw material、raw transcript、識別可能なartifactはpublic repositoryへcommitしない。**

public repositoryへ置けるのは、本人と操作者が公開範囲を確認した**sanitized validation evidence**だけとする。

公開することは価値検証の成立条件ではない。十分に匿名化できない場合は、public evidenceの粒度を粗くする、存在だけを記録する、またはpublic repositoryへ何も残さないことを許容する。

## 3. Public repositoryへ原則として入れないもの

- 参加者の氏名、連絡先、アカウント識別子。
- 明示的な許可のない所属、顧客名、案件名、取引先名。
- raw interview / meeting transcript。
- raw audio / video。
- 元の業務文書、調査票、顧客発言、自由記述データ。
- 識別可能なscreen shot / export。
- 契約、営業秘密、未公開企画、内部URL、ticket ID等。
- 参加者本人ではない第三者の個人情報。
- consent / withdrawal連絡に必要な個人連絡情報。
- 複数の文脈を組み合わせることで本人や組織を推定できるquasi-identifier。

名前を消しただけでは、匿名化済みとは扱わない。

## 4. Public repositoryへ残してよい候補

必要最小限であり、公開範囲を確認できた場合に限る。

- 個人を識別しないSession ID。
- 粗いpractice context。
- 参加者が公開可能と確認したparaphrase。
- 元資料を復元できない粒度の観察記録。
- value moment / friction / no-use reason / stop reasonの要旨。
- 公開可能なKJ Atlas documentのsanitized derivative。
- 「証拠はprivate materialに存在するがpublicには保持しない」というexistence note。
- findingの振り分け結果。

public evidenceは、第三者が言ったことを証明するために最大量を残すのではなく、**判断を監査できる最小量**を目標とする。

## 5. Raw working materialの扱い

raw materialの具体的な保存先は、本repositoryでは規定しない。ただし、最低限次を守る。

- 参加者または操作者が管理できる場所で扱う。
- public Gitへ自動同期されるdirectoryをraw materialの保管場所にしない。
- session開始前に、保存するか、終了後に破棄するかを決める。
- 保存する場合は、用途と保持期間を参加者へ説明する。
- KJ Atlas自体にraw materialを保存した場合、そのdocument / exportをpublic dogfood fixtureへ流用しない。

安全な保存先を用意できない場合は、raw materialを保存しない運用を選ぶ。

## 6. Session IDとalias

- Session IDを本人名、会社名、メールアドレス等から生成しない。
- aliasには、本人が公開を望まない限り識別情報を含めない。
- session間のlinkabilityが不要であれば、同一人物を追跡できる共通IDを作らない。
- 実践文脈の説明は、価値解釈に必要な粒度を超えて細かくしない。

## 7. 公開前の確認

public repositoryへsession由来のartifactをcommitする前に、最低限次を確認する。

- [ ] raw materialではなくsanitized derivativeである。
- [ ] participant identity / organizationを不要に推定できない。
- [ ] confidential / contractual / third-party materialを含んでいない。
- [ ] screenshot / exportのmetadataや画面端に識別情報が残っていない。
- [ ] 参加者が合意した公開範囲を超えていない。
- [ ] publicに残さなくても検証が成立する情報を、過剰に公開していない。
- [ ] withdrawal / deletionについて、Git公開後の回収不能性を誤解させていない。

**1項目でも不明ならcommitしない。**

## 8. 撤回・削除

### Public commit前

参加者が撤回した場合は、事前に合意した範囲に従い、raw working material / draft evidenceを削除するか、以後利用しない状態にする。

### Public commit後

public Gitへ公開した情報は、repositoryから削除できても、すでに取得されたclone / fork / cache / 引用まで完全には回収できない可能性がある。

そのため、**撤回可能性を担保する方法として、後からGit履歴を消すことに依存しない。**

この制約はsession開始前に説明し、public commitはsanitizationと公開範囲の確認を終えた後にだけ行う。

## 9. Evidenceの強さとprivacy

privacyを守るためpublic evidenceを粗くした場合、そのことを隠して強い証拠のように扱わない。

たとえば、次のように制約を明示する。

- `private evidence verified by operator; not public`。
- `participant wording paraphrased for privacy`。
- `artifact exists but was not retained`。

公開できないこと自体を欠陥とはみなさない。一方で、第三者が同じ証拠を再確認できないというepistemic limitationは明示する。

## 10. Findingの振り分けとの関係

- privacy / publicationだけに関する摩擦は、まず`VALUE-REALNESS-01`の実行観察として保持する。
- 1回のsession固有の保存事情を、すぐに一般的な製品要求へ変換しない。
- 複数の実利用で、KJ Atlas自身のdata boundary / sharing / AI送信契約によって仕事が成立しないことが再現した場合は、F2候補を検討する。
- 権限、安全、共有意味論等にまたがるcontract変更が必要だと実証された場合だけ、`ADR-0047`に従ってADR候補とする。

本書そのものを、新しい製品ADRとして扱わない。