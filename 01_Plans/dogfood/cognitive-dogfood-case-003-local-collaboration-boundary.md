# 認知dogfood Case 003 — local / offline / self-hostとcollaborationの製品境界

- 状態: 準備済み / 最初の有効なCase 001 Arm実行より前にsourceを凍結済み
- Portfolio: `cognitive-dogfood-case-portfolio-preregistration.md`
- Product snapshot: `hat47x/kj-atlas@2232b3bb26647e5c4a083f55bdbf83c161698649`
- B/D用Skill snapshot: `hat47x/cultural-substrate-weaving@3988e12e5f7f316f377d3391e9486c8467a111d5`
- Round 1 source manifest: `cognitive-dogfood-case-003-round1-source-manifest.json`

## 1. 固定する問い

> KJ Atlasはoffline/local/self-hostによるデータ統制と、共同分析・共有・組織導入に必要な同期/collaborationをどの境界で両立するべきか。local-firstを中核価値、配備オプション、安全境界、または特定利用ケース向け要件のどれとして扱うべきか。

この問いは、Case 001 / 002の結果にかかわらず変更しない。

## 2. 主な不確実性

- offline / self-hostは、利用者がKJ Atlasへ切り替える理由なのか。それとも、機微な資料を扱う一部環境の必要条件なのか。
- unfinished / sensitiveな定性資料を利用者が統制することと、複数人による共同作業・共有・組織管理をどう両立するか。
- local-first / CRDT等の技術方向が、実利用要求より先に価値語として過大化していないか。
- server-authoritative / SaaS / tenantモデルは利用者主体性と衝突するのか。それとも、データ統制を別の形で実現し得るのか。
- 個人・小規模チームの簡便さと、enterprise / public-sectorにおけるself-host、identity、audit要求を、一つの製品境界で扱うべきか。

## 3. Round 1で使用する証拠の境界

全Armへ、manifestに固定した同じproduct sourceだけを与える。Round 1では、外部のlocal-first研究、CRDT研究、競合製品比較を新たに検索しない。これらはRound 2の候補とする。

資料には、意図的に次の異なる設計・実装状態を共存させる。

1. 公開README / ROADMAP上のローカル評価、人間レビュー、共有方針。
2. MVPのDocument JSON snapshotと運用サポート境界。
3. privileged data / diagnostics / external connectionの安全境界。
4. SaaS tenant / auth / ownership / DB portabilityの組織運用設計。
5. server-authoritative CASを採択した共同編集モデルと、offline / P2P / E2EE要件が生じた場合だけCRDTを再検討する判断。
6. 社会的共有・複数reviewerの価値が、まだreal-user条件待ちである証拠。

## 4. 自然発生した矛盾・訂正を使う確認項目

以下は評価者側の事前登録であり、Armへ答えとして教えない。

### C3-T1 — 「ローカルで使える」と「local-first」は同義ではない

READMEの標準構成は、loopback限定の同一ホスト評価から始まる。一方、後段ではSaaS tenant境界、server-owned auth / session、組織所有、共同編集を具体化している。

単に「ローカル起動できる」という事実から、offline-first同期、local source of truth、P2Pを中核価値だと飛躍しないかを見る。

### C3-T2 — CRDTは将来性の象徴ではなく、条件付きの代替案

`ADR-0076`は、共同編集にserver-authoritative LWW + existing CASを採択し、CRDTはoffline / P2P / E2EEが必要になった場合だけ再検討するとしている。

「collaborationならCRDT」「local-firstならCRDT」という技術連想で判断せず、現行SafeMode、tenant guard、single source of truthとの制約関係まで戻れるかを見る。

### C3-T3 — データ統制は保存場所だけでは決まらない

`ADR-0059` / `ADR-0073`等では、tenant境界、document ownership、capability、control plane separationを通じて、shared serverであっても管理者を暗黙のsuper-readerにしない設計を進めている。

local storageを利用者主体性、server storageを運営者支配と単純に対応させないかを見る。

### C3-T4 — schemaやarchitectureの存在を、運用実現と誤認しない

`ADR-0033`は、schemaに型があることと、標準運用・保守・復旧が可能であることを明確に分ける。SaaS / collaboration設計についても、Accepted ADRが存在するだけで実利用可能だとみなしてはならない。

### C3-T5 — collaboration / social diffusionの価値実在は未確認

`SOCIAL-DIFFUSION-01`は、複数reviewerによる再現性を価値として保持しつつ、real-user / cooperator等がいない段階ではdeferred-open-readyとしている。

「共同編集機能を増やせば社会的価値が増える」と先取りせず、共有、共同分析、普及のどこに実利用証拠が不足しているかを保持できるかを見る。

## 5. 全Arm共通の成果物

全Armは少なくとも次を返す。

1. KJ Atlasにとってのlocal / offline / self-host / data-controlを分解し、同義語として扱わない境界案。
2. 個人・小規模チーム・組織・相互に信頼しないSaaS tenant等、利用形態ごとの必要条件と不要条件。
3. 現行server-authoritative / snapshot / tenant / ownership / sharing設計が既に解いている問題。
4. 現行設計では満たせない可能性が高いoffline、network partition、P2P、E2EE、portable ownership等の要求。
5. CRDT / local-first等へ進む前に、実利用で観測されるべきトリガー。
6. self-host / localがKJ Atlasのswitch reasonではなく、deployment optionで十分かもしれないという最も強い反証。
7. 逆に、cloud / SaaS中心では失う可能性がある中核価値または利用ケース。
8. collaborationを増やすことで、保留、違和感、少数意見、provenance、SafeModeが失われる失敗モード。
9. 次に実施すべき検証/issue。技術方式の採択より、利用要求、運用摩擦、データ境界の観測を優先する。
10. 主要主張ごとのsource path / stable identifier / evidence time、判断保留、追加証拠。

## 6. Case 003として不十分な結果

次のような結果では、Case 003における方法上の増分は弱いと判断する。

- 「local-firstはユーザー主体で良い」「クラウドは便利」といった価値一般論で終わる。
- local execution / self-host / offline-first / local source of truth / P2Pを区別しない。
- CRDTをcollaborationの当然の到達点として扱う。
- SaaS / tenant ADRが存在することを、共有SaaSや共同編集の実利用価値が証明されたこととみなす。
- 運用コスト、同期競合、権限、障害、migration、backup / restore、share / exportを扱わない。
- cloud-firstが一部利用者には明確に優れる可能性を落とす。
- 未完成・機微な定性資料のcontrolを、暗号化や保存場所だけへ還元する。

## 7. 方法上の境界

4Arm、M1〜M9、blind review、contamination、skill attributionには、`COGNITIVE-EVAL-01`とCase 001で固定した共通契約を再利用する。

Case 003を理由にcultural-substrate-weavingの正本を変更しない。B/DはCase 001 / 002と同じfrozen skill snapshotを使う。

C/DではInquiryJourneyを実際の外部認知状態として使用し、architecture、data、operations、adoptionという異なる材料を、あらかじめ用意した一つのカテゴリへ押し込まない。T9へ返すのは、実際に反復した手動摩擦だけとする。

## 8. 完了条件

Case 003 Round 1は、次を満たすまで結論として扱わない。

- A〜Dを、それぞれ独立したfresh contextで実行する。
- 同じfrozen source snapshotを使う。
- raw artifactを評価より先に固定する。
- blind reviewをunblindより前に完了する。
- C3-T1〜T5は答え合わせに使わず、概念分解、時点差の理解、条件付き設計を保持できたかを観察する材料として使う。
- negative / no-incrementな結果も削除しない。