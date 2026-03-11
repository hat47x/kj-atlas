# HIL-RS-01-A1: Architecture最小I/F契約（Critique / 再提案差分 / レビュー帰属）

- Contract ID: `HIL-RS-01-A1`
- Status: Fixed
- Owner: Architecture Owner
- Scope: `02_Architecture/`
- Upstream: `01_Plans/adr/ADR-0026-next-phase-human-in-the-loop-reversible-synthesis.md`, `01_Plans/adr/ADR-0001-value-to-requirements.md`, `00_Prompt/domain.md`
- Related: `02_Architecture/review_attribution.md`, `02_Architecture/schemas_review_attribution.md`

## 0. 目的

本契約は、`ADR-0026` D2（契約先行）に従い、A2（Frontend実装）/A3（Documentation同期）が契約参照のみで着手できる最小I/F境界を固定する。

## 1. 非目標

- Frontend実装詳細（UIコンポーネント、状態管理、イベント処理）を定義しない。
- LLM provider・推論実行制約の再設計を行わない。
- SafeMode既定ON、share/export漏えい防止契約を緩和しない。

## 2. 契約一覧（必須/任意/禁止）

### 2.1 Critique入力I/F（Contract Key: `A1-CRITIQUE-IF`）

#### 必須
- `critiqueId`: critiqueイベントを一意識別する opaque string。
- `targetRef`: critique対象（card/cluster/edge/proposal）を示す参照。
- `critiqueType`: `too_close | too_far | not_the_same | feels_off | no_articulable_reason`。
- `createdAt`: ISO-8601 timestamp。
- `iteration`: 再提案世代番号（1以上の整数）。

#### 任意
- `comment`: 補足テキスト（理由任意の原則を壊さない補助情報）。
- `constraintHints`: 再提案に渡す追加制約ヒント（順序・距離・分離など）。

#### 禁止
- critique入力をもって「唯一正解」や自動確定状態へ遷移させること。
- `reviewed` 状態の自動更新。
- PII（実名/メール/外部ID生値）を critique payload に保存すること。

### 2.2 再提案差分I/F（Contract Key: `A1-REDIFF-IF`）

#### 必須
- `proposalId`: 再提案案ID。
- `basedOnIteration`: 直前案のiteration参照。
- `diffOps[]`: 可逆差分操作の配列。
- `traceKey`: critique入力から再提案までの追跡キー（`critiqueId` と連結可能）。

#### diffOps最小単位
- `opId`: 差分操作ID（案内で一意）。
- `opType`: `add | remove | move | regroup | relabel`。
- `targetRef`: 変更対象参照。
- `before` / `after`: 適用前後スナップショット（remove/add の場合は片側null可）。

#### 任意
- `rationale`: 変更理由の短文（説明可能性補助）。

#### 禁止
- 片方向差分のみを保存して逆操作不能にすること。
- traceKey未設定で critique→再提案の因果を切断すること。
- SafeModeで禁止される share/export 操作を再提案適用時に暗黙実行すること。

### 2.3 レビュー帰属I/F（Contract Key: `A1-ATTR-IF`）

#### 必須
- `reviewState`: `unreviewed | human_reviewed`。
- `reviewedAt`: `human_reviewed` 遷移時の timestamp。
- `reviewerRef`: non-empty opaque string（`review_attribution` 契約に準拠）。

#### 任意
- `reviewContext`: `internal | external | self` などの文脈ラベル。
- `ownerRef`: 表示・責務トレース用の任意参照。

#### 禁止
- AI処理のみで `human_reviewed` に遷移すること。
- `provider` / `external_uid` / email 等の生IDを attribution payload に保存すること。
- `reviewEvents` 欠如をエラー化して閲覧不可にすること（互換性維持）。

## 3. 横断制約（安全・可逆・並列）

### 3.1 安全制約
- SafeMode既定ONを前提とし、契約でOFFを要求しない。
- share/export漏えい防止の後退を禁止する。
- 監査情報は最小化し、PIIは既定で保存しない。

### 3.2 可逆制約
- 再提案差分は必ず `before/after` を持ち、巻き戻し可能であること。
- critique は否定・留保データとして保持し、削除による履歴欠落を既定動作にしない。

### 3.3 A2/A3並列実行境界
- A2は `03_Implement/frontend/**` のみ編集し、契約本文は参照専用。
- A3は `04_Documentation/**` のみ編集し、実装コードを変更しない。
- 共有リソース（`01_Plans/issues/README.md`, `01_Plans/project-progress-dashboard.md`）更新は統合フェーズへ分離する。

## 4. ADR更新要否判定

- 判定: **ADR更新不要**。
- 理由:
  - 本書は `ADR-0026` D2で要求された「最小I/F契約の固定」を具体化する下位仕様であり、意思決定の追加・変更を含まない。
  - 既存 `review_attribution` 契約（opaque reviewerRef / PII最小化）を踏襲し、上位方針を変更しない。

## 5. 契約未固定箇所チェック（A1完了判定）

- `A1-CRITIQUE-IF`: 0件（固定済み）
- `A1-REDIFF-IF`: 0件（固定済み）
- `A1-ATTR-IF`: 0件（固定済み）
- A2/A3参照先未定: 0件（本ファイルを単一参照先として固定）


## 6. A2/A3 handoff固定情報（Proceed）

- Contract IDs（固定）:
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
- Single Reference（固定）:
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- 非目標（A2/A3共通）:
  - 単一スコア/ランキングによる自動確定を導入しない。
  - SafeMode既定ONとshare/export漏えい防止を弱めない。
  - provider/external_uid/email等の生IDをpayloadへ保存しない。
- 禁止事項（A2/A3共通）:
  - 契約本文を参照せず独自I/Fを追加すること。
  - 共有リソース（`01_Plans/issues/README.md`, `01_Plans/project-progress-dashboard.md`）をストリーム内で更新すること。
  - A2で`04_Documentation/**`、A3で`03_Implement/**`を同時に変更すること。

## 7. AC/DoD自己検証（Stream A）

- [x] `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` の3契約IDが固定されている。
- [x] A2/A3の単一参照先が本ファイルで固定されている。
- [x] SafeMode既定ON・share/export漏えい防止後退禁止が明記されている。
- [x] A2/A3の禁止境界（編集スコープ分離・共有リソース更新禁止）が明記されている。

