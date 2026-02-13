# Canonicalization Workflow

本ドキュメントは、`P-05: カード数の可管理性（merge提案 + canonical化）` を満たすための、
**canonicalization の運用手順**を定義する。

- canonicalization は、類似カードを「同一視可能な代表（canonical card）」へ束ねるための人間主導フローである。
- AI は候補提案のみを担当し、確定判断は人間が行う。

---

## 1. なぜ canonicalization が必要か

canonicalization の目的は次の2点に限定する。

1. **カード数の可管理性を維持すること**
   - 類似カードの増殖を抑え、キャンバス上の認知負荷を下げる。
2. **トレーサビリティを保持すること**
   - canonical 化後も source card への参照経路を保持し、意味差分を追跡できる状態を維持する。

加えて、canonicalization では以下を最低条件とする。

- canonical と source の**双方向参照**（canonical→source / source→canonical）を保持する。
- source の visibility 状態（visible / hidden / collapsed）を復元可能な形で保持する。

---

## 2. canonicalization workflow

canonicalization は、以下の順序で運用する。

### 2.1 Suggest merges（統合候補の提示）

- AI は類似カードの統合候補（merge suggestion）を提示する。
- この段階の候補はすべて **unreviewed** として扱う。
- 自動確定は行わない。

### 2.2 Review candidates（候補レビュー）

- 利用者は候補ごとに採否を判断する。
- レビュー時は、意味差分が失われないかを確認する。
- 必要に応じて候補を却下し、source を独立維持する。

### 2.3 Adopt as canonical（canonical へ採用）

- 採用された候補のみ、canonical/source 対応を確定する。
- 確定後も source 情報は保持する（削除しない）。
- canonical への採用は、常に人間操作でのみ確定する。
- 対応確定時は、canonical→source と source→canonical の参照整合を確認する。

### 2.4 View controls: hide/show sources（表示制御）

- canonical 化後は source の表示状態を切り替える。
  - visible: source を明示表示する。
  - hidden: source を非表示化する（データは保持する）。
  - collapsed: source を折りたたみ表示する。
- 表示状態は操作で復元できる状態として保持する。

### 2.5 Inspect sources when needed（必要時の出典確認）

- 差分確認や解釈の再検討が必要なときは、source を再表示して参照する。
- canonical のみを見て判断が難しい場合、source を確認して意味の取り違えを防ぐ。

---

## 3. Notes

### 3.1 AI suggestions are unreviewed

- AI が提示した merge suggestion は、既定で **未レビュー（unreviewed）** とする。
- AI はレビュー状態を自律変更しない。
- AI 提案は判断材料であり、結論ではない。

### 3.2 canonicalization は手動編集で可逆

canonicalization は手動操作で巻き戻せる。最小手順は次のとおり。

1. 対象 canonical card を開き、紐づく source card 一覧を表示する。
2. source の visibility を show に切り替え、差分を確認する。
3. 不適切な canonical/source 対応を解除する（双方向リンクを両方外す）。
4. 必要なら source card を独立カードとして再配置・再編集する。
5. 関係線（edge）が必要な場合は、人間が手動で再接続する。
6. canonical 側の内容を更新し、再レビュー状態を明示する。

この手順により、誤統合が起きても意味の回復経路を維持できる。

---

## 4. Non-goals

以下は本 workflow の対象外（将来課題または既定で禁止）とする。

- **automatic rerouting of edges**
  - canonical 採用時に、既存エッジを自動で付け替える処理は行わない（future）。
- **auto-deletion of sources**
  - source card の自動削除は既定で行わない（never by default）。

---

## 5. 要件トレーサビリティ（参照）

本ドキュメントは以下の要求と整合する。

- `P-05`: カード数の可管理性（merge提案 + canonical化）
- `AI-05-1`: AI は統合候補を提案できるが自動確定しない
- `AI-05-3`: canonical への採用可否は人間操作でのみ確定される
- `DATA-05-3`: canonical 化後も source card の参照経路を欠落なく保持する
- canonical cards 必須条件: 双方向参照（canonical→source / source→canonical）を保持
- source visibility 必須条件: visible / hidden / collapsed を保持し復元可能であること
