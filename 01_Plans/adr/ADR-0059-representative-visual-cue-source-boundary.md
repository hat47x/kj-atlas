# ADR-0059: 代表視覚手掛かりの供給経路と意味境界

- Status: Proposed
- Date: 2026-07-18
- Deciders: Product Owner / UX Lead / Security Officer / Project Maintainers
- Scope: `00_Prompt/representative_visual_cue_requirements.md`, `02_Architecture/schemas.md`, `02_Architecture/data_model_operations_overview.md`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/export/`, `03_Implement/frontend/src/import/`

## 背景

島や情報集合を小さな画像で見分けられると、カード数が増えたときの再発見を助ける可能性がある。しかし、「画像生成」という単一機能として設計すると、外部通信を必要としない絵文字、同梱画像、外部素材、生成画像の異なる安全・権利・運用境界が混ざる。また、画像を要約や分類の正解として扱うと、KJ法が保持すべき曖昧さ、少数意見、対立を一枚の具体像へ早く収束させるおそれがある。

## 選択肢

1. 画像機能を持たない。UIと権利管理は単純だが、視覚的な再認識を支援できない。
2. 島ごとに生成AIが画像を自動生成する。個別性は高いが、通信、費用、待ち時間、誤った具体化、AI無効構成との格差が大きい。
3. 絵文字または単一の画像集だけを採用する。実装は小さいが、表現範囲とライセンス条件が一つの供給元に固定される。
4. 共通の意味境界の下で、手描き・利用者画像、同梱素材、外部素材、生成画像を段階導入する。実装は段階ごとに増えるが、従来実践との連続性を保ち、利用者が負担とリスクに応じて選べる。

## 提案する決定

選択肢4を採用候補とし、次を固定する。

1. 機能の正本語彙は「代表視覚手掛かり」とする。画像は島の表札・要約・本文・根拠を置き換えず、再認識を助ける任意の補助である。
2. 供給経路を A: 手描き/基本図形/利用者画像、B: Unicode絵文字/同梱プリセット、C: 権利確認済み外部素材、D: proposal-only画像生成に分ける。A/Bから順に検証し、後の経路を前提にしない。
3. どの経路も明示操作、候補確認、人間による採用、削除・取り消し、非表示を共通条件とする。島作成時の自動生成と自動採用は禁止する。
4. B/Cは外部通信前に接続先と共有内容を確認し、SafeMode、provider固定、暗黙切替禁止を守る。
5. 外部素材は、原典、作者、ライセンス、取得時点、改変、クレジット要件を採用参照と一緒に保持する。検索集約サービスのライセンス表示だけで利用可能と判断しない。
6. Cは生成物であること、provider/model、生成日時、対象参照、入力投影digest、人間の採用状態を保持する。生成画像を事実や根拠として表示しない。
7. 写真・図が観察データや根拠である場合、識別用の手掛かりとは別の一次視覚資料として保持し、元資料、撮影文脈、出典へ戻れるようにする。島どり線・関係線などの図解記号も、代表手掛かりと混同しない。
8. 採用済み手掛かりと一次視覚資料の保存先、画像バイナリの保持方式、容量上限、許容ライセンスallowlist、外部providerは本ADR受理後のfixture検証で決める。決定前に `DocumentV1` やDBへフィールド・テーブルを追加しない。

## 複雑性予算

既定画面の常設操作は増やさず、島または選択集合の詳細から一段深く開く任意操作にする。画像なしの既存操作を変えず、外部経路は高度機能として段階的に開示する。

## 影響

- AIを使えない環境でも、小さな視覚支援を先に提供できる。
- 紙上のシンボルマーク、簡単な手描き、汎用図形、撮影写真から自然に移行できる。
- 特定素材集を採用する前に、表示義務や継承条件を製品配布と照合する作業が必要になる。
- 候補・採用済み参照・画像本体・サムネイルを分けたデータ設計が必要になる可能性がある。
- 公開/exportでクレジットを表示できない形式は、該当素材を含められない。
- 画像の有無による探索性能を比較し、効果が確認できない供給経路は標準機能へ昇格させない。

## 受理に必要な確認

- [ ] 絵文字をOS依存のUnicode表示とするか、固定画像セットとして同梱するかを比較する。
- [ ] 手描きの最小機能と、写真・図を一次資料として保持する境界をfixtureで確認する。
- [ ] 同梱候補のライセンス、帰属表示、派生物の継承条件を配布形態と照合する。
- [ ] 外部素材providerのAPI利用条件、検索語の扱い、キャッシュ、削除、クレジットを確認する。
- [ ] 画像保存先、容量上限、削除、import/export、オフライン表示をfixtureで比較する。
- [ ] 画像なし・手描き・基本図形・撮影写真・絵文字・プリセット・外部素材・生成画像の代表タスク評価計画をUX Leadが確認する。
- [ ] SafeModeと共有前確認をSecurity Officerが確認する。

## 追跡関係

- Source: `01_Plans/issues/issue-DOMAIN-VISUAL-CUE-01-representative-visual-cues.md`
- Requirements: `00_Prompt/representative_visual_cue_requirements.md`
- Evaluation: `02_Architecture/representative_visual_cue_evaluation.md`
- Related: `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`
- Related: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`
- Related: `01_Plans/adr/ADR-0049-external-agent-collaboration-boundary.md`
