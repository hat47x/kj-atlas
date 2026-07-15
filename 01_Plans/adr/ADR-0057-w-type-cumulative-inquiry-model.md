# ADR-0057: W型累積KJ法の反復的探究モデル

- Status: Proposed
- Date: 2026-07-15
- Deciders: Project Maintainers / UX Lead / Domain Expert / Productization Program Owner
- Scope: `00_Prompt/w_type_iterative_inquiry_requirements.md`, `02_Architecture/schemas.md`, `02_Architecture/data_model_operations_overview.md`, `03_Implement/frontend/src/domain/`, `03_Implement/frontend/src/ui/`

## 背景

現行kj-atlasは、一つの文書内でカード化、グループ編成、図解、文章化、保留、違和感、根拠を扱える。しかし、6ラウンド累積KJ法のように、問題提起から手順化まで異なる姿勢でKJ法を繰り返し、現場での経験と思考を往復する長期的な探究は第一級の概念として持たない。

単純にR1からR6のタブを追加すると、次の問題が起きる。

- 固定順の完了ウィザードとなり、後の知見から前の問いへ戻れない。
- ラウンド移行時に前のカードや配置を上書きし、思考の変化を辿れない。
- 段階番号と同じ段階の再試行を混同する。
- 長期間の中断後に、問い、未解決点、次に確かめることを再構成できない。
- 6段階が通常利用者の初期画面と認知負荷を増やす。

一方、ラウンド成果の非破壊保存は、現行の単一 `DocumentV2` スナップショット運用を越える。空間配置を含む中間成果、分岐、カード系譜、部分共有をどの単位で永続化するかは、容量、可搬性、後方互換、安全共有に影響する。

## ADR再起票基準

本提案は `ADR-0047` の次の基準に該当する。

- R-1: 利用者指摘により、一ラウンド中心の現行モデルでは高度な反復実務を表現できない摩擦が明示された。
- R-3: ラウンド履歴の常設は複雑性予算、性能予算、SafeMode、UI/UX品質境界を横断する。
- R-4候補: 永続方式によっては `DocumentV2` の意味またはversion gateへ影響する。optional加算で済むかを受理前に判断する必要がある。

## 決定案

1. **探究を任意の高度機能として導入する。** 通常の一ラウンド利用と初期画面は変更しない。
2. **R1問題提起、R2現状把握、R3本質追求、R4構想計画、R5具体策、R6手順化を段階の意味として固定する。** ただし固定順の完了を強制しない。
3. **ラウンド段階と反復番号を分離する。** 同じ段階の追加取材・再統合は新しい `RoundRecord` として扱う。
4. **ラウンド成果を非破壊の `RoundSnapshot` として扱う。** 後続編集は過去成果を上書きせず、差し戻しは分岐として表す。
5. **ラウンド間を `RoundHandoff` で接続する。** 持ち越し、保留、未解決点、現場への問い、理解の変化を人が確認する。
6. **カード本文の正本とラウンド上の役割を分離する。** 段階や持ち越し状態をカードの固有属性として上書きしない。
7. **AIは段階別の問い、引継ぎ、差分、反証候補を提案できるが、自動移行・過去成果の書換え・仮説の自動決定をしない。** `provider=none` で中核操作を成立させる。
8. **永続化実装は本ADR受理後も、データ契約の比較を完了するまで開始しない。** UIプロトタイプは固定fixtureとメモリ内状態で検証できるが、現行文書へ未知キーを保存しない。

## 永続化候補

### A. `DocumentV2` のoptional入れ子構造

`inquiryJourneys?: InquiryJourney[]` を加え、ラウンド記録と最小成果を文書と一緒に保存する。

- 利点: import/exportが一体で、ローカル利用と可搬性が分かりやすい。
- 欠点: 文書サイズが増え、closed-world validation、共有、部分削除、過去成果の重複を広く変更する。

### B. 独立した `InquiryJourneyV1` 成果物

文書スナップショットを参照する独立成果物として探究とラウンドを保存する。

- 利点: 現行 `DocumentV2` の日常操作と履歴容量を分離し、ラウンド単位の共有・保持を扱いやすい。
- 欠点: 参照切れ、複数ファイル管理、バックエンドAPI、export bundleの設計が必要になる。

### C. ラウンドごとに独立文書を複製する

- 利点: 現行文書保存を流用しやすい。
- 欠点: カード系譜、引継ぎ、分岐、全体再開が命名規則頼みになるため、標準方式としては採用しない。

受理時はAまたはBを選び、スナップショット最小内容、参照整合、容量上限、削除、部分共有、SafeModeを同時に固定する。

## UI方針案

- 高度機能の作業モード内に「探究」を置き、コアツールバーへ6段階を常設しない。
- 現在位置は「現状把握・2回目」のように一行で示す。
- 全履歴は要求時に開き、次段階を直線的な進捗バーで表さない。
- ラウンド移行は一つずつ確認する引継ぎフローとし、保存を先に完了できる。
- 前へ戻る操作は、破壊的巻き戻しではなく「この成果から分岐」と表示する。
- 再開時は、問い、前回の変化、未解決点、次の行動を短いブリーフとして表示する。

## 影響

- 長期間にわたるKJ法実務で、問いと理解がどう変化したかを説明できる。
- 現場へ戻って追加情報を集める行為を、キャンバス外の断絶ではなく探究の一部として保持できる。
- 過去の仮説や少数意見を後の結論に合わせて消さず、分岐比較できる。
- 新しいドメイン型、履歴容量、共有範囲、操作面が増えるため、通常利用からの段階的開示が不可欠になる。
- 完全な永続化には、現行の文書単位CRUDを越える設計が必要になる可能性がある。

## 対象外

- 本ADRのProposed段階で `DocumentV2` またはbackend APIを変更すること。
- 6ラウンドをすべての文書へ必須化すること。
- プロジェクト管理、承認ワークフロー、担当者管理を同時導入すること。
- KJ法の実施品質や研究の妥当性を認定すること。
- AIがラウンド移行、仮説採用、具体策決定を自動化すること。

## 受理に必要な確認

- [ ] 6ラウンドを固定ウィザードではなく、反復・分岐可能な探究として扱うことを確認する。
- [ ] `RoundStage` と `RoundIteration` の分離を確認する。
- [ ] `RoundSnapshot` の最小内容と、空間配置を保存する境界を決める。
- [ ] 永続化候補A/Bを比較し、後方互換、容量、削除、共有、SafeModeを確認する。
- [ ] 通常利用の初期表示を増やさず、高度機能へ置くことをUXプロトタイプで確認する。
- [ ] `DOMAIN-W-ITERATION-01` の代表シナリオをマウス・キーボード・390pxで検証できる状態にする。

## 追跡関係

- Requirements: `00_Prompt/w_type_iterative_inquiry_requirements.md`
- Source issue: `01_Plans/issues/issue-DOMAIN-W-ITERATION-01-w-type-cumulative-inquiry-support.md`
- Related: `00_Prompt/qualitative_card_quality_requirements.md`
- Related: `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`
- Related: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`
- Related: `01_Plans/adr/ADR-0046-responsiveness-performance-budget.md`
- Related: `01_Plans/adr/ADR-0047-design-decision-adr-saturation-and-execution-first.md`
- Related: `02_Architecture/schemas.md`
- Related: `02_Architecture/data_model_operations_overview.md`
- Derived-from: 2026-07-15 ユーザー提案「6ラウンドのW型進行に見られる、イテレーションで思考を深める高度実務を支援する要件」
