# Issue: SEC-VISUAL-ASSET-01 旧式の島画像URLをSafeModeで自動取得しない

- Type: Bug / Security / Privacy / UX / Documentation
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `DOMAIN-VISUAL-CUE-01`
- Priority: P1
- Owner: Codex / Maintainer
- Scope: `03_Implement/frontend/src/canvas/IslandView.tsx`, `03_Implement/frontend/src/ui/SidePanel.tsx`, `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/domain/legacy_island_image.ts`, `02_Architecture/data_model_operations_overview.md`, `02_Architecture/schemas.md`
- Related Backlog: `SEC-VISUAL-ASSET-01`, `DOMAIN-VISUAL-CUE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0060-representative-visual-cue-source-boundary.md`, `00_Prompt/representative_visual_cue_requirements.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: SEC-VISUAL-ASSET-01
- RequirementStatement: SafeModeが有効な間は、既存文書に保存された島画像URLを画面表示のために自動取得せず、URLの変更を人間レビュー済み状態へ自動昇格させない。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=外部画像URLを含む既存文書をSafeModeで開く / 操作=キャンバスを表示し、島の詳細を開く / 期待結果=画像への通信は発生せず、遮断理由が表示され、URLは文書内に保持される / 除外=SafeModeを利用者が明示的に解除した後の旧式プレビュー、新しい代表視覚手掛かりの供給経路
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / import-sanitize
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: `ADR-0060`

## 1) 課題 / Problem statement

現行の`Island.imageUrl`は任意の文字列を保持でき、キャンバスのCSS背景とサイドパネルの`img`プレビューが文書表示だけでURLを解決する。SafeModeが有効でもこの二経路は抑止されていないため、外部ホストへIPアドレス、取得時刻、ブラウザー由来の通信情報が意図せず伝わる可能性がある。

また、画像URLを変更すると`imageReviewed`が自動的に`true`となる。URL入力と、内容・由来・権利を人が確認した判断は同一ではないため、レビュー状態の自動昇格に当たる。

この旧式フィールドは、`ADR-0060`で計画中の`RepresentativeVisualCue`ではない。代替テキスト、原典、作者、ライセンス、クレジット、画像本体の保存境界を持たず、島全体の薄い背景として表示するため、新モデルへそのまま昇格させない。

## 2) 提案する解決策 / Proposed solution

- SafeMode有効時は、キャンバスとサイドパネルの両方で`imageUrl`を描画資源として解決しない。
- URLを削除・改変せず、既存文書の往復互換性を保つ。パネルには「読み込まないがURLは保持する」と表示する。
- URL変更時は`imageReviewed=false`へ戻し、人間が別操作でレビュー済みにする。
- 読み込み判定を共通関数へ集約し、二つの表示経路が再び分岐しないようテストする。
- 設計文書には旧式フィールドの現状と制約を記載し、`RepresentativeVisualCue` / `SourceVisualMaterial`とは区別する。
- SafeMode解除後の外部画像取得、URL方式の廃止、代替テキスト・由来・権利情報の移行は`DOMAIN-VISUAL-CUE-01`と`ADR-0060`で決定する。

## 3) 受入条件 / Acceptance criteria

- [x] AC-1: SafeMode有効時、島背景のHTML/CSSに`imageUrl`が含まれない。
- [x] AC-2: SafeMode有効時、サイドパネルに`img src=imageUrl`を生成せず、遮断理由を表示する。
- [x] AC-3: SafeMode無効時は、互換期間中の旧式画像プレビューを維持する。
- [x] AC-4: URL変更時に`imageReviewed`が`false`になる。
- [x] AC-5: 日本語・英語カタログに遮断表示と入力例を定義し、翻訳キー整合テストを通す。
- [x] AC-6: SafeMode有効時に外部画像へのリクエストが0件であることをブラウザーE2Eで確認する。
- [x] AC-7: 旧式フィールドから新しい代表視覚手掛かりモデルへの移行・廃止条件の決定先を`ADR-0060`へ固定する。

## 4) タスク / Tasks

- [x] T1 既存の保存、入力、キャンバス描画、パネル描画経路を棚卸しする。
- [x] T2 SafeMode共通読み込みポリシーと単体テストを追加する。
- [x] T3 キャンバスとサイドパネルへポリシーを適用する。
- [x] T4 URL変更時のレビュー状態を未レビューへ戻す。
- [x] T5 現行データモデルと将来モデルの違いを設計文書へ反映する。
- [x] T6 PlaywrightでSafeMode中の通信遮断とURL変更時のレビュー解除を確認する。
- [x] T7 `ADR-0060`の決定に合わせて移行または除却issueへ引き継ぐことを追跡関係へ明記する。

## 5) 検証計画 / Validation plan

- `legacy_island_image.test.ts`でSafeMode共通判定を検証する。
- `IslandView.accessibility.test.ts`でSafeMode中の描画結果に外部ホスト名が含まれないことを検証する。
- i18nカタログ整合、frontend typecheck、関連unit testを実行する。
- Playwrightで外部画像URLを含むfixtureを開き、SafeMode中の該当URLリクエストが0件であることを確認する。

## 6) 依存関係 / Dependencies

- `DOMAIN-VISUAL-CUE-01`
- `ADR-0060`

## 7) ADR判定

今回のSafeMode遮断とレビュー自動昇格の廃止は、既存の安全方針と人間承認原則への適合修正であり、新規ADRは不要。旧式URL方式の廃止、新しい画像保存方式、外部素材の取得同意は複数モジュールと公開形式へ影響するため、`ADR-0060`で決定する。
