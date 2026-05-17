# ADR-0030: UI操作モデルの段階的開示とキーボードスコープ

- Status: Proposed
- Date: 2026-05-17
- Deciders: Project Maintainers
- Scope: `01_Plans/adr/`, `01_Plans/issues/`, `04_Documentation/acceptance_check.md`, `03_Implement/frontend/docs/e2e_testing.md`

## Context

- 2026-05-14 の代表操作検証で、次の課題が確認された。
  - **到達性**: キーボードでカード選択に到達できない。
  - **フォーカススコープ**: カード/島を選択しても、選択文脈の確認領域が現在視界に現れにくい。
  - **段階的開示**: 高度機能が初期表示で密集し、主要操作の認知負荷を上げる。
  - **閉じる/復帰**: `表示` / `共有と再現` パネルを `Escape` で閉じられず、起点フォーカス復帰方針も未固定。
- これらは単発UI調整ではなく、UI操作モデル（主要対象・文脈優先・閉じる挙動・Tab優先度）の仕様化が必要である。

## Decision

kj-atlas の UI操作モデルとして、次を確定方針とする（**仕様決定。実装は別Issueで管理**）。

1. **キーボード到達可能な主要操作対象**
   - カード・島・主要ツールバー・右側パネル主要導線を、キーボード到達の対象として扱う。
   - 少なくとも「選択」「確認」「次操作への移動」がキーボードで成立することを必須要件にする。

2. **段階的開示（Progressive Disclosure）**
   - 選択直後は「選択対象の確認・編集・レビュー導線」を文脈先頭に提示する。
   - 高度機能（差分、パッチ、文章化、診断など）は初期状態で全展開せず、明示操作で段階的に開示する。

3. **Escapeで閉じる + 起点フォーカス復帰**
   - `表示` / `共有と再現` の一時パネルは `Escape` で閉じる。
   - 閉じた後は、開く操作を行った起点ボタンへフォーカスを戻す。

4. **Tab順序の文脈優先**
   - 起動直後および選択直後の `Tab` 順序は、現在作業中の文脈（選択対象・関連操作）を優先する。
   - 文脈外の高度操作へ長距離巡回を強制しない。

### Non-goals

- 本ADRでは実装方式、コンポーネント分割、最終UIデザインを確定しない。
- 本ADRでは frontend/backend/deploy のコード変更を行わない。
- 本ADRでは CE/HIL/ENV/PRODUCT-VALUE/DATA ストリーム要件を再定義しない。

## Consequences

- **E2E観点の固定化**
  - 「開始 → 選択 → 表示 → 閉じる → 復帰」の検証軸を固定し、UI回帰判定を明確化できる。
- **既存UIとの移行コスト**
  - 右側パネル情報設計やフォーカス順序の再編が必要になり、既存利用者の操作位置が変わる可能性がある。
- **リグレッション観点の明確化**
  - マウス操作とキーボード操作の同等性、SafeMode/share-export への到達性、閉じる/戻るの可逆性を回帰対象として固定できる。

## Implementation boundary (I/F level)

- `UX-OPERABILITY-01`〜`04` は次の直列で実施する。
  1. 01: 操作動線レビューと仕様観点固定
  2. 02: カード選択のキーボード到達性
  3. 03: 選択文脈優先パネル
  4. 04: パネル閉じる/復帰フォーカス
- 各Issueは AC/DoD/Validation を仕様として定義し、実装作業は別PRで実施する。

## Traceability

- Related: `01_Plans/adr/ADR-0001-value-to-requirements.md`
- Related: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Related: `02_Architecture/architecture.md`
- Related: `01_Plans/issues/issue-UX-OPERABILITY-01-pointer-keyboard-flow-review.md`
- Related: `01_Plans/issues/issue-UX-OPERABILITY-02-keyboard-card-selection.md`
- Related: `01_Plans/issues/issue-UX-OPERABILITY-03-contextual-selection-panel.md`
- Related: `01_Plans/issues/issue-UX-OPERABILITY-04-panel-dismissal-focus-scope.md`
