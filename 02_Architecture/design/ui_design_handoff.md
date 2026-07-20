# UI設計見直し・実装照合の受け渡し

区分: Internal / Normative constraints + Informative handoff procedure

対象読者: UI/UX設計担当、frontend実装者、実装照合レビュー担当、外部デザイン支援へ依頼する保守者。

目的: kj-atlasのUIを見直す際に、利用者向けの画面カタログへ内部課題や設計指示を混入させず、守るべき価値・安全境界・複雑性予算・受け渡し入力を1か所から辿れるようにする。

非目標: 利用者向け操作説明、個別issueの進捗台帳、新規設計判断の採択、document/view/pack契約の変更。

## 正本と役割

| 情報 | 正本 |
| --- | --- |
| 利用者が見る現行画面 | `04_Documentation/ui_catalog.md` |
| 価値と判断軸 | `01_Plans/adr/ADR-0001-value-to-requirements.md` |
| UI/UX品質基準 | `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`、`02_Architecture/value_traceability.md` §2.7 |
| 視覚言語・コマンド到達・KJ語彙 | `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md` |
| 複雑性予算 | `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md` |
| 実装照合手順 | `02_Architecture/design/design-qa-checklist.md` |
| 各設計依頼と回答の形成履歴 | `02_Architecture/design/design-request-2026-07-round*.md`、同ディレクトリの `.dc.html` |
| 公開画像の撮影・検証台帳 | `04_Documentation/assets/screenshots/README.md` |
| 管理面データ境界（文書一覧・View/Preset・エージェント登録）の正本・権限・本文非表示原則（`DATA-MODEL-OPS-02` D1〜D4、Round 8入力） | `02_Architecture/data_model_operations_overview.md` §4 CRUDサポート表（文書一覧/View・Perspective/QueryPreset/エージェント登録の各行）・§5.2（Workspace/Admin・Audit表示分離）、`02_Architecture/schemas.md` §3.4.1（`DocumentListItemV1`）、`02_Architecture/api.md` §2.4（List）・§9.5（エージェント登録API） |

本書は上記正本の索引と受け渡し境界であり、ADRやissueの決定内容を上書きしない。矛盾時は上流のAccepted ADRとvalue traceabilityを優先する。

## 侵してはならない核

- コア価値は「少ない操作で曖昧さを保持できること」であり、機能数の最大化ではない。
- 保留は意味を確定しない健全な状態、違和感は言語化前でも第一級データ、配置・分類・構造は可逆である。
- キャンバスを主、AIとの対話を従とする。AIは候補生成に留まり、確定しない。
- 単一正解、ランキング、採点、準備度スコアで結論を誘導しない。
- `KJ_ATLAS_LLM_PROVIDER=none` でも、書く・並べる・束ねる・つなぐ・保留する操作が完結する。
- SafeModeは既定ON、共有前確認を必須とし、未レビュー本文や出典参照を安全側に扱う。

## 出力を評価する5つの判断軸

1. 人間の思考を雑にしないか。
2. AIに早すぎる収束を与えないか。
3. 保留・対立・未レビューを保持できるか。
4. 差分・監査・レビューに載せられるか。
5. 人間向け文脈とAI向け文脈を混同していないか。

いずれかに強く反する案は採用しない。判断不能な場合は、見た目だけで決めず、根拠となるADRまたは専用issueへ戻す。

## 情報設計と複雑性予算

- 画面は、開始/入口、キャンバス、選択コンテキスト、作業モード面、共有前確認の5領域を基本とする。
- 既定表示は静かに保ち、保留操作を確定操作より遠くしない。
- 新しい操作を既定表示へ純増させない。置換・包含・モード分離で収める。
- 元に戻せる操作は取消方法を表示し、不可逆操作は実行前に影響を説明する。
- Escapeによる段階的な閉鎖、トリガへのfocus復帰、キーボード到達性を回帰させない。
- amberは保留・違和感の保持系に予約し、claimTypeや成功・警告の別意味へ流用しない。

詳細な判定項目は `design-qa-checklist.md` を使い、本書へ複製しない。

## 現行の設計上の注意点

- 作業モードは選択コンテキストと分離した独立領域で、既定OFFの段階開示とする。
- 右側パネルの詳細フィルタとGuided Flowは `詳細` ON時だけ表示する。
- 表示状態としての確認ビューと、データ状態としてのレビュー済み/未レビューを同じ「レビュー」語で曖昧にしない。
- provider無効状態を劣化フォールバックとして扱わず、第一級の利用状態として説明する。
- 新規操作は、既存のコマンドパレット、メニュー、ショートカット、キャンバス文脈操作のどこへ属するかを先に決める。

個別課題の完了/未完了や最新優先度は本書へ固定せず、`01_Plans/issues/` とtriage出力を参照する。

## 再設計の非目標

- document/view/packスキーマの暗黙変更。
- レガシーimport/exportの削除。
- 反スコアリング、キャンバス主従、SafeMode既定ONの方針転換。
- チャットUIを主役にする全面刷新。
- リアルタイム共同編集の追加。
- Pendingのアイデアを、判断記録なしに現行仕様として描くこと。

## 受け渡しパッケージ

外部デザイン支援または実装照合レビューへ渡す入力は、次に限定する。

1. `04_Documentation/ui_catalog.md` と、同書が参照する検証済みスクリーンショット。
2. 本書の「侵してはならない核」「5つの判断軸」「情報設計と複雑性予算」「非目標」。
3. 対象を限定したTask Brief。対象画面、解く問題、変更可能範囲、変更禁止範囲、期待する出力を明記する。
4. 対象issueと必要なADR anchor。内部リポジトリを渡せない場合は、確定済み制約だけを秘密情報なしで要約する。
5. `design-qa-checklist.md` の該当節と、比較対象revision・viewport・locale・fixtureが分かる画像台帳。

「白紙から全面刷新」では依頼しない。提案には、既存操作との置換関係、増える認知負荷、SafeMode/未レビュー/保留の見え方、キーボードとfocusへの影響を説明させる。

## 受領後の処理

1. 提案を5判断軸とdesign QA checklistで照合する。
2. 既存のAccepted ADRで決まる内容と、新しいDecisionが必要な内容を分ける。
3. 既存判断の実行はissueへ、新しい安全・契約・不可逆境界はADR-0047の再起票条件に該当する場合だけADRへ送る。
4. 実装後に同一fixture・locale・viewportで画像を再生成し、`04_Documentation/assets/screenshots/README.md`へprovenanceを記録する。
5. 利用者向けに必要な確定事項だけを、内部issue/ADR番号や進捗を除いて公開UIカタログへ反映する。

