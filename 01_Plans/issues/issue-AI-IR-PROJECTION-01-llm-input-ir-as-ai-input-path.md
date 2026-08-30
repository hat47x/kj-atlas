# Issue: AI-IR-PROJECTION-01 LLM投入IRをAI入力の実経路として実装する

- Type: Architecture / AI Integration
- Status: In Progress
- Source Issue: N/A
- Priority: P1
- Owner: Unassigned
- Scope: `03_Implement/backend/src/kj_atlas_api/llm_input_ir.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/models_ai.py`, `03_Implement/backend/src/kj_atlas_api/models_context.py`, `03_Implement/backend/src/kj_atlas_api/llm/provider.py`, `02_Architecture/llm_input_ir_spec.md`, `02_Architecture/api.md`, `03_Implement/backend/tests/test_ts_python_contract_drift.py`
- Related ADR/Spec: `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`, `02_Architecture/llm_input_ir_spec.md`, `01_Plans/adr/ADR-0009-local-llm-integration.md`, `02_Architecture/canvas-projection-asymmetry-2026-08-09.html`
- Expected verification level: `integration`

> **進捗（2026-08-30）: 段階適用の Stage 1〜3 / 5 完了（`detect-contradiction`・`suggest-card-groups`・`generate-narrative`）。** 残り2段階（`suggest-layout` → その他）は未着手。AC-10 は未着手、AC-7 は範囲を分離。詳細は末尾の「結果（Stage 1）」「結果（Stage 2）」「結果（Stage 3）」節を参照。`Status` メタデータの語彙は `Draft` / `Open` / `In Progress` / `Done` に固定されている（`01_Plans/issues/issue_memo_status.py`）ため、段階情報はここに書く。

> **本issueは `ADR-0069` の採択を前提とする。** ADR が Proposed の間は着手しないこと。D1〜D4 が未決のまま実装すると、凍結仕様（`llm_input_ir_spec.md`）への非互換な改変が入る。**（2026-08-29 に Accepted・仮承認となり、この前提は解消済み。）**

## 課題

> 以下は起票時（2026-08-09）の実測である。**Stage 1 で解消した範囲は「結果（Stage 1）」節を参照**（`llm_input_ir.py` が実装され、`detect-contradiction` が IR 経由になった）。残り8つのプロンプト構築関数については、下記の記述は現在も有効である。

`02_Architecture/llm_input_ir_spec.md` は「LLMへ渡す前段データ」の正本であり、`ADR-0009`（Accepted）Phase B を完了させる凍結仕様である。**この仕様の実装は存在しない。**

```
$ grep -rn "ir_version\|graph_summary\|cluster_candidates" --include=*.py --include=*.ts --include=*.tsx 03_Implement
（0件）
```

出荷済みの `/ai/*` は `DocumentV1` を直接プロンプト文字列へ変換している。その結果、**論理構造がAIへほとんど渡っていない**。

### 実測（`routes/ai.py` の全プロンプト構築関数9件を走査）

| 渡されていないもの | 該当 |
|---|---|
| `edges`（関係） | **全9関数** |
| `evidenceLinks` | 全9関数 |
| `relationSummaries` | 全9関数 |
| `claimType` | 全9関数 |
| `parentIslandId`（島階層） | 全9関数 |
| `placardCardId`（表札） | 全9関数 |

`ADR-0048` D3 で固定した関係語彙（`related`/`negate`/`causal`/`mutual`/`equivalence`、`types.ts:78`）は、AIに一度も届いていない。

具体的な症状:

- `POST /ai/detect-contradiction`（`ai.py:746-752`）: 矛盾を扱うAPIが、人間が既に記録した矛盾（`EvidenceLink.type="contradicts"`、`contradictionState`）を見ていない。確定・保留済みの矛盾を再提示しうる。
- `POST /ai/suggest-card-groups`（`ai.py:725-731`）: グルーピング提案が既存の島・階層・`holdState` を見ていない。人間の既決と衝突する候補を出しうる。
- `POST /ai/generate-narrative`: `readingOrder` は渡るが `edges` は渡らない。因果・対立という叙述の骨格が使えない。
- `POST /ai/suggest-layout`（`ai.py:317-336`）: 生の絶対座標 `x`/`y` と島の `bounds`/`anchor` のみ。関係を渡していないため「関係の近さを配置へ反映する」根拠を欠く。

### 使われていない投影層

座標非依存ないし座標正規化済みの投影が、既に4層設計されている。AI入力経路はそのすべてを迂回している。

| 投影層 | 状態 |
|---|---|
| `getDerivedIslandEdges()`（`island_edge_aggregate.ts:78`） | 実装済み・呼出5箇所・AI未使用 |
| `buildAbstractMapExport()`（`abstract_map_export.ts`） | 実装済み・座標参照ゼロ・SafeMode実装済み・AI未使用 |
| `ContextBundleResponse`（`models_context.py:89`） | `build_bundle()` が `_STUB_DATASET` を返す（`:263`）・未接続 |
| `LLMRequest.inputs` IR（`llm_input_ir_spec.md` §4） | 凍結仕様・実装ゼロ |

背景と分析の全文は `02_Architecture/canvas-projection-asymmetry-2026-08-09.html` を参照。

## 対応方針（実装者向け）

`ADR-0069` の D1〜D4 の**採択された決定に従う**。ADR の推奨は D1=B（`coordinates` を任意化しエンドポイントごとに要否宣言）、D2=A（IR の関係語彙をキャンバス5値へ拡張）、D3=A（`islands` を追加し `cluster_candidates` と型で分ける）、D4=A（サーバ側 Python 実装＋TS との同値テスト）。

### 実装順序（推奨）

論理関係が効く順に段階適用する。全エンドポイント一括より回帰リスクが小さい。

1. `detect-contradiction` — `evidenceLinks` / `contradictionState` を渡す効果が最も直接的
2. `suggest-card-groups` — 既存の島・階層・`holdState` を渡す
3. `generate-narrative` — `edges`（`causal`/`negate`）を渡す
4. `suggest-layout` — 座標を渡す唯一の例外として契約へ明記し、あわせて `edges` を渡す
5. 残りのエンドポイント

### 注意事項

- **`ir_version` を繰り上げること。** 現スキーマは `ir_version: {"const": "1.0"}` かつ `additionalProperties: false`。D1〜D3 のいずれもスキーマ変更を伴う。
- **`llm_input_ir_spec.md` §6 の FixtureProvider 回帰データを再生成すること。** IR 仕様のみから決定論的に生成できること（AC-1 / AC-4）が仕様の受入条件である。
- **フロントエンドの既存 SafeMode 実装を削除しないこと。** 二重防御として残す。
- **既存の外部送出ガードを変更しないこと** — 二段 opt-in（`settings.py:473-481`）、ホスト allowlist（`:504-520`）、trusted-HTTP エンドポイント検証。これらは妥当であり本issueの対象外。

### 前提条件（着手前に解消または回避すること）

`02_Architecture/functional-dependency-integrity-2026-08-06.html` の **F-5「島所属の関数従属性が強制されていない」が未解消**である。カード→島の所属が一意に定まらない状態では、`islands` を含む IR の構築結果が一意にならない。F-5 を解消するか、投影側で一意化規則（先勝ち／後勝ち／全列挙）を明示すること。後者を選ぶ場合は決定を仕様へ記載する。

**解消（2026-08-30）**: 後者（投影側での一意化規則の明示）を採った。`issue-DOMAIN-ISLAND-MEMBERSHIP-01`（Done）が暫定規則を**先勝ち**（`getIslandsForCard()` / `islands.find()` が既に実装している挙動）と定め、`ADR-0069`「前提条件」節がこれを採択している。IRビルダーはこの規則で単一の島を選び、規則は `llm_input_ir_spec.md` §2.2A 規則3 に明記した。F-5 の書込み側の強制自体は依然として未解決だが、**読み取り側の投影が一意になることは保証されている**ため、本issueの着手ゲートは解除済みである。

## 受入条件

- [x] AC-1（detect-contradiction のみ）: `detect-contradiction` が `evidenceLinks` と `contradictionState` を受け取り、`confirmed` / `held` の矛盾を再提示しないことを integration テストで固定する。— `tests/test_ai_detect_contradiction_ir.py`。抑止は決定論（LLMを呼ばない）。
- [x] AC-2（suggest-card-groups only）: `suggest-card-groups` が既存の島・`parentIslandId`・`holdState` を受け取り、`holdState` が保留中のカードを新規グループへ含めないことをテストで固定する。— `tests/test_ai_suggest_card_groups_ir.py`。抑止は決定論（候補集合から除外＋応答からも除去。プロンプト依存にしない）。`held` / `pending` / `shelved` の3値すべてを対象とした。
- [x] AC-3（generate-narrative only）: `generate-narrative` が `edges` を受け取り、`causal` / `negate` が入力に含まれることをテストで固定する。— `tests/test_ai_generate_narrative_ir.py`。IR（`LLMRequest.inputs`）側とプロンプト側の両方で固定し、あわせて読み順上のどこで効くかの写像も固定した。
- [x] AC-4（detect-contradiction / suggest-card-groups / generate-narrative）: 全対象エンドポイントで、IR が `constraints.safe_mode == true` を満たさない場合に IR 生成が失敗すること（仕様 §7.1）をテストで固定する。— `build_llm_input_ir(safe_mode=False)` が `safe_mode_required` を送出。あわせて既存の `_reject_unreviewed_cards` 422 が**無変更**であることの回帰テストを、移行済みの各エンドポイントで追加（第二層であって置換でないことの証明）。Stage 3 では `_reject_unreviewed_text`（文書経路）について同じ回帰を追加した。Stage 4 以降の対象エンドポイントでは未実施。
- [x] AC-5（detect-contradiction のみ）: PII最小化チェック（§7.2）と構造化テキスト限定チェック（§7.3）が入力側で機能することをテストで固定する。— メール／電話／URLトークンの3パターンと、base64疑似バイナリ・禁止キー名を `tests/test_llm_input_ir.py` で固定。拒否応答が該当文字列を反射しないことも固定。
- [x] AC-6: 上限超過時の切り詰めが決定論的であること（同一入力→同一出力、§5）をテストで固定する。— 同一入力2回で `llm_ir.json` のSHA-256一致、入力配列順を反転しても一致、参照整合が保たれることを固定。IRビルダー全体の性質のため段階に依存しない。
- [ ] AC-7: `test_ts_python_contract_drift.py` を投影ロジックへ拡張し、TS 実装（`buildAbstractMapExport` / `getDerivedIslandEdges`）と Python 実装の同値性を検査する。— **未着手**。狭いスポットチェックも実施していない。現行の `test_ts_python_contract_drift.py` は TS ソースからフィールド集合を抽出して突き合わせる**静的な**ドリフト検出であり、挙動同値性の検査基盤ではない。TS を実行して結果を突き合わせる仕組みは新規構築が必要で、本Stageの範囲を超える。また今回のIRビルダーは `getDerivedIslandEdges()`（島間派生辺）も `buildAbstractMapExport()` も再実装しておらず（`islands` は確定済み島をそのまま投影する）、対応する関数対が現時点で存在しない。**Stage 4（`suggest-layout`）で派生辺・座標投影を扱う段階で再評価すること。**
- [x] AC-8（D1/D3のスキーマ変更範囲のみ）: `ir_version` が繰り上がり、`llm_input_ir_spec.md` が採択された D1〜D3 と一致している。— `1.0` → `1.1`（Stage 1）→ `1.2`（Stage 2 で `cards[*].hold_state` を加算）。版数判断の根拠は仕様 §7.4。§6 の FixtureProvider 生成手順は `scripts/generate_llm_input_ir_fixture.py` で end-to-end に再現でき、`--check` によるドリフト検出をテストに含めた。「全エンドポイントが IR 経由」の確認は Stage 5 まで持ち越し。
- [x] AC-9（detect-contradiction / suggest-card-groups / generate-narrative）: `02_Architecture/api.md` のリクエスト契約が実装と同期している。— Stage 1 で `/ai/detect-contradiction`、Stage 2 で `/ai/suggest-card-groups`、Stage 3 で `/ai/generate-narrative` の項を更新。Stage 3 はリクエスト／レスポンスの**形が変わっていない**ため、追記したのは IR 経由化・二層 SafeMode・IR 由来の 422 コード（`empty_cards` の挙動変更を含む）である。他エンドポイントは未変更（未変更であることが正しい）。
- [ ] AC-10: 代表規模（カード300・島30程度）で入力トークン量を計測し、変化を記録する。上限値（`MAX_CARDS=200` 等、§5.1）が現行規模に合わない場合は別issueへ切り出す。— **意図的に延期**。1エンドポイントだけの計測は代表性を持たない（IRの `graph_summary` / `islands` は文書単位のコストであり、複数エンドポイントで償却される前提で設計されている）。移行エンドポイントが増えた段階でまとめて計測する。
- [x] AC-11（detect-contradiction / suggest-card-groups）: 既存フロントエンドが動作する（後方互換）。または必要な改修を同一 PR に含める。`03_Implement/deploy/tools/kj_canvas_demo.py` も追随させる。— **改修不要を確認**。`/ai/detect-contradiction` を呼ぶフロントエンドコードは存在しない（`grep -rn "detect-contradiction\|detectContradiction" 03_Implement/frontend/src` は0件）。`kj_canvas_demo.py` はAPIではなくモックLLMアダプタ（`http://localhost:8001/generate`）を直接叩いており、本エンドポイントの契約に依存しない。追加した `doc` はリクエストの任意フィールド、`alreadyRecorded` / `existingContradictionState` はレスポンスの追加フィールドであり、いずれも破壊的ではない。`verify_business_flow_e2e.sh` の2箇所の呼び出しも従来形のまま通る。**Stage 2 追記**: `/ai/suggest-card-groups` にもフロントエンドの呼び出し元は存在しない（`grep -rn "suggest-card-groups\|suggestCardGroups" 03_Implement/frontend` は0件。`03_Implement/deploy/tools/` の2件はいずれもモックLLMアダプタ側で、APIの契約に依存しない）。追加した `doc` はリクエストの任意フィールド、`excludedCardIds` / `truncated` はレスポンスの追加フィールドである。`verify_business_flow_e2e.sh` の呼び出し（27箇所）は `doc` を渡さない従来形であり、候補カード行の書式 `  - id="...", text="..."` を IR 経路でも維持したため `mock_local_llm.py` のプロンプト解析（`_CARD_LINE_ID_TEXT`）もそのまま一致する。**Stage 3 追記**: `/ai/generate-narrative` は**移行済みエンドポイントで初めて実フロントエンド呼出元を持つ**（`frontend/src/api/client.ts` の `generateNarrative`、`App.tsx` から使用）。このためリクエスト／レスポンスの形を一切変えない方針を採り、フロントエンドは無改修（`03_Implement/frontend` の変更ゼロ）。読み順行の書式 `- <n>. island id="..."` / `- <n>. card id="..."` も維持したため `mock_local_llm.py` の `_READING_ORDER_LINE`（`^- \d+\. \w+ id="([^"]+)"`）はそのまま一致する。新たに加えた行（`- reading-order 1 -> reading-order 2: ...` 等の背骨行、切り詰め注記）はいずれもこの正規表現に一致しない（`- ` の直後が数字＋`.` ではない）ことをテストで固定した。`verify_business_flow_e2e.sh` からの呼び出しは**144箇所**あり（当初「2箇所」と記載していたのは誤り。`grep -c 'X POST "$BASE_URL/ai/generate-narrative"'` で確認）、IR経路化で新設された 422（`pii_detected` §7.2 / `structured_text_only_violation` §7.3）に触れる fixture が無いことを静的に確認した（同スクリプト中の `text` / `title` / `summary` / `note` 値 1463件に対し §7.2 の3パターンと §7.3 の禁止キーを走査、ヒット0件）。

## 依存関係

- `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`（採択が前提）
- `01_Plans/issues/done/issue-AI-REL-VOCAB-DRIFT-01-ir-canvas-relation-type-mismatch.md`（D2 の決定で同時に解消される。本issueと同一PRで実施してよい）

### 連携（依存ではない）

`SEC-AI-SAFEMODE-01` / `ADR-0068` は**同じ境界を対象としており、独立に実装すると衝突する**。`ADR-0068` は `/ai/*` の各リクエストモデルへ `safeMode` を追加する方向、本issueは IR §7.1 でサーバ側強制する方向である。**両者を並行実装しないこと。** 採択順序を保守者に確認してから着手すること。

**決着（2026-08-30）**: `ADR-0068` が先に Accepted となり `SEC-AI-SAFEMODE-01` が Done で出荷済みであるため、順序の問題は解消した。`ADR-0069` の「ADR-0068 との関係」節が定めるとおり、**併用（defense-in-depth）**とする。本issueの実装は `_reject_unreviewed_cards` / `_reject_unreviewed_text` を除去・弱化せず、IR §7.1 のレビュー状態再検査を第二層として**追加**する。両者の同時成立は `tests/test_ai_detect_contradiction_ir.py` が固定している。

## 検証

- `python -m pytest tests/ -k "ai or llm or ir" -q`
- `python -m pytest tests/ -q`（backend 全体回帰）
- frontend: `npx vitest run` および `npx tsc --noEmit -p .`
- `python 01_Plans/docs_check.py`

## 結果（Stage 1: detect-contradiction）

### 何を作ったか

| 成果物 | パス | 役割 |
|---|---|---|
| IRビルダー | `03_Implement/backend/src/kj_atlas_api/llm_input_ir.py` | `llm_input_ir_spec.md` §2〜§7 の決定論的実装。FastAPI・SQLAlchemy・時計・LLM のいずれにも依存しない純関数群 |
| 仕様改訂 | `02_Architecture/llm_input_ir_spec.md` | `ir_version` 1.0 → 1.1（D1・D3・`evidence_links`・`meta` 是正・§3/§5 の曖昧語解消） |
| ルート配線 | `03_Implement/backend/src/kj_atlas_api/routes/ai.py` | `detect_contradiction` が IR 経由になり、プロンプトを IR から描画する |
| リクエスト/レスポンス契約 | `03_Implement/backend/src/kj_atlas_api/models_ai.py` | `DetectContradictionRequest.doc`（任意）、`DetectContradictionResponse.alreadyRecorded` / `.existingContradictionState`（追加） |
| LLM境界 | `03_Implement/backend/src/kj_atlas_api/llm/provider.py` | `LLMRequest.inputs`（任意）。transport は従来どおり `prompt` のみを送る |
| 回帰データ | `03_Implement/backend/tests/fixtures/llm_input_ir_document.json`, `..._expected.json` | 仕様 §6 の `document.json` → `llm_ir.json` ＋ SHA-256。Stage 1 当時の名は `..._v1_1.json` で、Stage 2 で版数を落として改名した（下の Stage 2 の表と仕様 §6.1 を参照） |
| 再生成スクリプト | `03_Implement/backend/scripts/generate_llm_input_ir_fixture.py` | `--check` でドリフト検出。LLM も外部 provider も呼ばない |
| ユニットテスト | `03_Implement/backend/tests/test_llm_input_ir.py` | AC-4 / AC-5 / AC-6 / AC-8 |
| 統合テスト | `03_Implement/backend/tests/test_ai_detect_contradiction_ir.py` | AC-1、SafeMode 二層の同時成立、後方互換 |

### `ir_version` を 1.1 とした理由

`ADR-0069` は「D1〜D3 のいずれを採ってもスキーマ変更を伴うため繰り上げが必要」とだけ述べ、版数は実装時判断とした。**1.1（マイナー、加算的）**を選んだ根拠は仕様 §7.4 に記録した。要約:

- **必須フィールドを増やしていない。** `meta` を §4 の必須へ加えたのは新要求ではなく、§2.4 と §7.1 が既に必須と定めていたものが §4 のスキーマ本文から抜けていた自己矛盾の是正である（1.0 は `additionalProperties: false` と併せて字義どおりには実装不能だった）。
- `coordinates` は必須→**任意への緩和**であり、1.0 の妥当な IR は 1.1 でも妥当。
- `islands` / `evidence_links` は任意フィールドの追加。
- 既存フィールドの意味・列挙値・計算規則を変更していない。§3 / §5 への追記は 1.0 が定義していなかった箇所（`density` / `cohesion`、採番順、切り詰めの参照整合）を一意に埋めたもので、1.0 で一意に定まっていた結果を別の値へ変えてはいない。

破壊的変更を示す 2.0 は当たらないと判断した。ただし `additionalProperties: false` を維持しているため、1.0 想定の消費側は新フィールドを未知キーとして扱う。消費側は `ir_version` で分岐すること（§7.4 に明記）。

### 設計上の判断（実装時に決めたこと）

1. **「再提示しない」を決定論で実現した。** `confirmed` / `held` の矛盾リンクが IR にある場合、ルートは **LLM を呼ばずに** `hasContradiction=false` ＋ `alreadyRecorded=true` を返す。プロンプトで「再提示するな」と指示するだけでは不変条件にならない。`hasContradiction=false` は「矛盾が無い」の主張ではなく「新規の発見は無い」の意味であり、区別できるよう `alreadyRecorded` / `existingContradictionState` を追加した（api.md に明記）。`unconfirmed` / `resolved` は抑止対象外。
2. **`doc` は任意フィールドにした。** カード2枚だけの既存契約を壊さないため（AC-11）。`doc` 無しでも IR 経路を通る（カード2枚のみの IR を組む）ので、「IR が実経路である」という本ADRの主張はどちらの形でも成立する。
3. **SafeMode は二層。** ルートの `_reject_unreviewed_cards` は無変更でそのまま先に走る。IRビルダーは投影対象カードのレビュー状態を独立に再検査する。後者は前者が**構造的に見られないもの**を捕まえる ── `_reject_unreviewed_cards` は `cardA` / `cardB` しか検査しないが、`doc` 側の未レビューカードは IR 層でのみ検出できる。この非重複性をテストで固定した。
4. **PII 検査は ID とタイムスタンプを除外した。** 仕様 §7.2 の電話パターン `\+?[0-9][0-9\- ]{8,}[0-9]` は実質「長い数字列」の検出器で、ISO-8601 タイムスタンプ（`2026-01-01T00:00:00Z`）が必ず一致する。除外しないと**あらゆる文書が投影不能**になる。自由記述本文には3パターンすべてを適用する（日付を含むカード本文が偽陽性で弾かれうる点は仕様 §7.2 に既知の偽陽性として明記し、fail-closed 側に倒すことを意図的な選択として記録した）。
5. **`graph_summary` は切り詰め後の集合で算出する。** 除外順の根拠に使う `rank` は切り詰め前に1度だけ算出し、出力する `centrality` は切り詰め後に再算出する。そうしないと `graph_summary` が IR に存在しないカードを参照し、IR が参照的に閉じない。
6. **カードは `id` 昇順に正規化する。** 入力配列の並びだけが違う文書から同一の `llm_ir.json` が得られるようにするため（仕様 §6 の検証成功条件を些末な差分に対しても成立させる）。

### テスト結果

| 対象 | 結果 |
|---|---|
| `pytest tests/test_llm_input_ir.py -q` | 37 passed |
| `pytest tests/test_ai_detect_contradiction_ir.py -q` | 16 passed |
| `pytest tests/ -k "contradiction or ir or safe_mode" -q` | 163 passed, 3 skipped, 1225 deselected |
| `pytest tests/ -q`（backend 全体回帰） | **1346 passed, 39 skipped, 8 deselected**（変更前ベースライン: 1293 passed, 39 skipped, 8 deselected。差分 +53 は本Stageの新規テストのみで、既存テストの failed / skipped / deselected は1件も増減していない） |
| `pytest tests/test_ai_safemode.py -q` | 20 passed（SafeMode の既存 suite。**無変更で全通過** = 第一層を弱化していないことの直接証拠） |
| `ruff check`（変更した src / tests / scripts） | All checks passed |
| `scripts/check_design_consistency.py` | PASSED（0 errors, 0 warnings） |
| `scripts/check_contract_drift.py` | OK（0 errors, 2 warnings。いずれも本変更以前から存在する Pydantic↔TS の既知差分） |
| `python3 01_Plans/docs_check.py` | passed（active_memos=45, tracked_markdown=683） |

frontend は**変更していない**（`/ai/detect-contradiction` の呼び出し元が存在しないため）。したがって `npm run typecheck` / `vitest` は本変更の検証対象外。

環境注記: このリポジトリの backend テストは `03_Implement/backend/.venv` の Python で実行する必要がある（システムの `python3` には `alembic` が入っておらず、`kj_atlas_api.main` の import で 110 件の collection error になる）。

### Stage 2〜5 に残っていること

| Stage | 対象 | 主な作業 |
|---|---|---|
| 2 | `suggest-card-groups` | AC-2。既存の島・`parentIslandId`・`holdState` を IR 経由で渡す。`holdState` は現在 IR に無いため、フィールド追加の要否判断（`ir_version` 1.2 の候補）から始まる |
| 3 | `generate-narrative` | AC-3。`edges`（`causal` / `negate`）を渡す。`readingOrder` と IR の関係を決める必要がある |
| 4 | `suggest-layout` | 座標を渡す唯一のエンドポイント（`include_coordinates=True`）。ここで初めて `getDerivedIslandEdges()` 相当が必要になる見込みで、**AC-7 の再評価点**でもある |
| 5 | 残りのエンドポイント | `refine-card-text` / `suggest-document-title` / `check-narrative` / `suggest-island-summary` / `summarize-island-relation` ほか |
| 全Stage完了後 | AC-10 | 代表規模（カード300・島30）でのトークン量計測。1エンドポイントだけでは代表性が無いため延期した |
| 全Stage完了後 | `ADR-0068` の退役判断 | IR 経路が全 `/ai/*` を覆った時点で判断する（`ADR-0069` が「本ADRの実装時点では判断しない」と明記。**本Stageでも判断していない**） |

`MAX_CARDS=200` 等の上限値が現行規模に妥当かの再検討（`ADR-0069` 非目標の4番目）も AC-10 と同じタイミングで扱う。

### 本Stageで意図的に触れなかったもの

- `models_context.py` の `ContextBundleResponse` / `build_bundle()` / `_STUB_DATASET`（`CE1-CTX-IF`）。Scope に挙がっているが、IRビルダーとは別の投影層であり、本Stageでは接続しない。
- `_reject_unreviewed_cards` / `_reject_unreviewed_text` の呼び出し箇所（12箇所すべて）。1行も変更していない（`git diff` で確認済み）。
- 他8つのプロンプト構築関数。`ADR-0069` の段階適用順に従い、Stage 2 以降で扱う。

## 結果（Stage 2: suggest-card-groups）

AC-2 を `suggest-card-groups` に限定して実装した。Stage 1 の配線パターン（IRビルダーを消費し、プロンプトをIRから描画し、人間の既決は決定論で守る）をそのまま踏襲している。

### 何を作ったか

| 成果物 | パス | 変更内容 |
|---|---|---|
| IRビルダー（加算） | `03_Implement/backend/src/kj_atlas_api/llm_input_ir.py` | `HOLD_STATES` 定数、`SourceCard.hold_state`、`_card_to_ir()`、消費側ヘルパ `held_card_ids()`、`validate_llm_input_ir()` の hold_state 検査。`IR_VERSION` 1.1 → 1.2 |
| 仕様改訂 | `02_Architecture/llm_input_ir_spec.md` | §2.1 規則8（`hold_state`）、§4.1 / §4.2 スキーマ、§6.1 の fixture 名、§7.4 に 1.2 の行と版数根拠 |
| ルート配線 | `03_Implement/backend/src/kj_atlas_api/routes/ai.py` | `_suggest_card_groups_ir()`（新規）、`_card_group_candidates()`（新規）、`_build_suggest_card_groups_prompt()` をIR描画へ、`_parse_suggest_card_groups_response()` に候補集合フィルタ、`suggest_card_groups()` 本体 |
| リクエスト/レスポンス契約 | `03_Implement/backend/src/kj_atlas_api/models_ai.py` | `SuggestCardGroupsRequest.doc`（任意）、`SuggestCardGroupsResponse.excludedCardIds` / `.truncated`（追加） |
| API契約 | `02_Architecture/api.md` | `/ai/suggest-card-groups` の項のみ。あわせて `cards` の上限記述の陳腐化（「最大100件」→ 実装は 2〜1000件、`DOGFOOD-31` で引き上げ済み）を是正 |
| 回帰データ | `tests/fixtures/llm_input_ir_document.json`, `..._expected.json` | 版数入りの旧名から改名（§6.1 に理由を明記）。`c-isolated` に `holdState: "held"` を追加して新フィールドを回帰データで覆う |
| ユニットテスト | `tests/test_llm_input_ir.py` | `hold_state` の投影・省略・未知値・派生構造への非影響を追加（37 → 46件） |
| 統合テスト | `tests/test_ai_suggest_card_groups_ir.py`（新規） | AC-2、SafeMode 二層の同時成立、後方互換、切り詰めの可視化（18件） |

### 仕様改訂は必要だったか — 必要だった（`ir_version` 1.2）

**必要だった。** 1.1 の IR にはカードの hold 状態を置く場所が無く、既存フィールドで代替できない（`islands` は確定した所属、`evidence_links` は根拠・矛盾、`relations` はカード間の論理関係を表し、いずれも「このカードの扱いを人間が保留している」という単項の状態を表現できない）。IR を迂回して `DocumentV1.cards[*].holdState` を直接読めば実装自体は可能だが、それは `ADR-0069` の主張（IR がAI入力の実経路である）を崩す。

**島・`parentIslandId` は 1.1 で足りていた。** `islands[*].parent_island_id`（§2.2A）をそのまま使っており、この部分の仕様改訂は不要だった。改訂は `cards[*].hold_state` の1フィールドのみ、加算的（`required` 不変・値を持たないカードではキーごと省略）で、hold 状態を使っていない文書の IR は 1.1 とバイト単位で同一である。根拠は仕様 §7.4。

### 設計上の判断（実装時に決めたこと）

1. **3値すべてを除外対象にした。** `held`（判断を保留）/ `pending`（未着手）/ `shelved`（Shelfへ退避）はいずれも `schemas.md` §14.1 で「人間が意図的に扱いを決めていない」状態であり、新しい島の構成員として提案することはその判断の上書きになる。AC-2 の「保留中」を「`holdState` が付いている＝非 active」と読んだ。3値のいずれかだけを対象にする読み方を採らなかった理由は、`pending` を候補に残すと「未着手だから束ねてよい」という解釈をコードが採ることになり、その判断は人間の側にあるためである。狭める必要が生じた場合は `held_card_ids()` の1箇所で変えられる。
2. **抑止は二重にコードで行う。** (a) 候補集合から除外してプロンプトに載せない、(b) LLM応答の `cardIds` を候補集合へフィルタする。(b) が必要なのは、プロンプトの遵守が不変条件にならないため（Stage 1 の「再提示しない」を決定論で実現したのと同じ理由）。(b) は同時にID捏造の防御にもなる。フィルタで空になったグループは返さない。
3. **候補が2枚未満なら LLM を呼ばない。** 1枚だけの「束」は KJ の束ではない（`ai_kj_execution_procedures.md` §2）。`groups: []` と `excludedCardIds` を決定論で返す。
4. **`doc` は任意フィールドにした。** フラットなカード配列だけの既存契約を壊さないため（AC-11）。`doc` 無しでも IR 経路を通る。ただし `doc` が無ければ hold 状態は入力に存在しないため、AC-2 の抑止が働くのは `doc` を渡した場合のみである（カード配列側に `holdState` を追加する案は採らなかった。`_CardRef` は `detect-contradiction` と共有しており、そちらの契約まで動かすことになるため）。
5. **候補カード行の書式を維持した。** `  - id="...", text="..."` は `03_Implement/deploy/tools/mock_local_llm.py` のプロンプト解析（`_CARD_LINE_ID_TEXT`）との事実上の契約であり、business-flow E2E の27箇所がこれに依存する。IR から描画する形に変えても書式は同一に保ち、テストで固定した。並び順のみ IR の `id` 昇順になる（決定論のため）。
6. **切り詰めを可視化した（`truncated`）。** リクエストは最大1000枚を受け付ける（`DOGFOOD-31`）のに対し、IR は `MAX_CARDS=200` / `MAX_TEXT_CHARS=12000`（仕様 §5.1）で切り詰める。IR 経路化により、**200枚超の束ね依頼では一部のカードがモデルへ届かなくなる**。上限値の妥当性は AC-10（延期中）の主題だが、黙って落とすことは避け、レスポンスに `truncated` を追加した。切り詰めで落ちたカードは `excludedCardIds`（人間が保留したもの）とは区別している。

### テスト結果

| 対象 | 結果 |
|---|---|
| `pytest tests/test_ai_suggest_card_groups_ir.py -q` | 18 passed |
| `pytest tests/test_llm_input_ir.py -q` | 46 passed（Stage 1 の 37 + 本Stageの9） |
| `pytest tests/ -k "card_groups or ir or safe_mode" -q` | 189 passed, 2 skipped, 1229 deselected |
| `pytest tests/ -q`（backend 全体回帰） | **1373 passed, 39 skipped, 8 deselected**（Stage 1 のベースライン: 1346 passed, 39 skipped, 8 deselected。差分 +27 は本Stageの新規テストのみで、既存テストの failed / skipped / deselected は1件も増減していない） |
| `pytest tests/test_ai_safemode.py -q` | 20 passed（**無変更で全通過** = 第一層を弱化していないことの直接証拠） |
| `ruff check`（変更した src / tests / scripts） | All checks passed |
| `scripts/check_design_consistency.py` | PASSED（0 errors, 0 warnings） |
| `scripts/check_contract_drift.py` | OK（0 errors, 2 warnings。いずれも本変更以前から存在する Pydantic↔TS の既知差分） |
| `python3 01_Plans/docs_check.py` | passed（active_memos=45, tracked_markdown=683） |

frontend は**変更していない**（`/ai/suggest-card-groups` の呼び出し元が存在しないため。AC-11 参照）。したがって `npm run typecheck` / `vitest` は本変更の検証対象外。

### Stage 3〜5 に残っていること（Stage 1 の表の更新）

| Stage | 対象 | 主な作業 |
|---|---|---|
| 3 | `generate-narrative` | AC-3。`edges`（`causal` / `negate`）を渡す。`readingOrder` と IR の関係を決める必要がある |
| 4 | `suggest-layout` | 座標を渡す唯一のエンドポイント（`include_coordinates=True`）。`getDerivedIslandEdges()` 相当が必要になる見込みで、**AC-7 の再評価点** |
| 5 | 残りのエンドポイント | `refine-card-text` / `suggest-document-title` / `check-narrative` / `suggest-island-summary` / `summarize-island-relation` ほか |
| 全Stage完了後 | AC-10 | 代表規模（カード300・島30）でのトークン量計測。**本Stageで `MAX_CARDS=200` が実運用規模（`DOGFOOD-31` の200〜300枚）と衝突することが具体化した**（上記 設計判断6）。AC-10 では計測に加えて上限値の見直し要否を判断すること |
| 全Stage完了後 | `ADR-0068` の退役判断 | IR 経路が全 `/ai/*` を覆った時点で判断する（**本Stageでも判断していない**） |

### 本Stageで意図的に触れなかったもの

- `_reject_unreviewed_cards` / `_reject_unreviewed_text` の呼び出し箇所（12箇所すべて）。1行も変更していない（`git diff` で確認済み。`suggest_card_groups` の呼び出しはコメントを添えたのみで、引数も位置も同一）。
- `detect-contradiction` / `generate-narrative` / `suggest-layout` ほかのエンドポイントとそのプロンプト構築関数。
- `models_context.py` の `ContextBundleResponse` / `build_bundle()` / `_STUB_DATASET`（`CE1-CTX-IF`）。
- `_CardRef`（`detect-contradiction` と共有のリクエスト型）。hold 状態は `doc` 経由でのみ受け取る（上記 設計判断4）。

### 事後検証で見つかった不備と是正（2026-08-30）

Stage 2 の変更に独立レビューを掛け、指摘3件のうち1件を是正した。

| 指摘 | 判定 | 対応 |
|---|---|---|
| Stage 1 の「何を作ったか」表（本issue上部）の回帰データ行が、改名前の `llm_input_ir_document_v1_1.json` / `..._expected_v1_1.json` を指したまま残っていた | **是正した。** リポジトリ内で `_v1_1.json` を指す参照はこの1行のみで（他は仕様 §6.1・`generate_llm_input_ir_fixture.py`・`test_llm_input_ir.py` とも改名済み）、`docs_check.py` は markdown 追跡を検査するのでこの種の fixture パス腐りを捕捉しない | 現行名へ更新し、Stage 1 当時の名と改名の経緯を同じ行に注記した |
| fixture の改名自体（`..._v1_1.json` → `....json` と、それに伴う `generate_llm_input_ir_fixture.py` / 仕様 §6.1 の追随）は AC-2 が要求したものではなく、Stage 1 成果物への便宜的変更である | **差し戻さない。** 版数を落とす根拠は仕様 §6.1・§7.4 と `512cd75d` のコミットメッセージに記録済みで、ドリフト検査も通っている。ここで再改名すると仕様・スクリプト・テストを再び動かすことになり、そちらの方が変更範囲を広げる | 対応なし（記録のみ） |
| IR 経路化により `SuggestCardGroupsRequest.cards`（上限1000枚、`models_ai.py:388`）に対し IR 側が `MAX_CARDS=200` / `MAX_TEXT_CHARS=12000`（`llm_input_ir.py:35,37`）で切り詰めるため、200枚超ではモデルへ届かないカードが出る | **不備ではない。** 上記 設計判断6 の記載どおりで、黙って落とさず `truncated` で可視化しており、上限値の妥当性は AC-10 の主題として明示的に繰り延べている。数値・契約上限とも再確認して相違なし | 対応なし（AC-10 で扱う） |

是正は本issueの文言1行のみで、`03_Implement/` 配下のコード・テスト・fixture は変更していない。是正後に backend 全体回帰を再実行し **1373 passed, 39 skipped, 8 deselected**（Stage 2 完了時と同一）、`python3 01_Plans/docs_check.py` も passed を確認した。

## 結果（Stage 3: generate-narrative）

AC-3 を `generate-narrative` に限定して実装した。Stage 1〜2 の配線パターン（IRビルダーを消費し、プロンプトをIRから描画する）を踏襲しているが、**移行済みエンドポイントで初めて実フロントエンド呼出元を持つ**点が前2段階と異なる（`frontend/src/api/client.ts` の `generateNarrative`、`App.tsx` から使用）。このためリクエスト／レスポンスの形を一切変えない方針を採った。

### 何を作ったか

| 成果物 | パス | 変更内容 |
|---|---|---|
| ルート配線 | `03_Implement/backend/src/kj_atlas_api/routes/ai.py` | `_generate_narrative_ir()` / `_reading_order_slots()` / `_narrative_relation_lines()` / `_narrative_spine_lines()`（いずれも新規）、`_build_generate_narrative_prompt()` に `ir` 引数を追加してIR描画へ、`generate_narrative()` 本体で `LLMRequest.inputs` にIRを載せる |
| API契約 | `02_Architecture/api.md` | `/ai/generate-narrative` の項のみ。形は不変のため、追記したのは IR経由化・二層SafeMode・IR由来の422コード（`empty_cards` の挙動変更を含む）・座標非投影・切り詰めの扱い |
| 統合テスト | `03_Implement/backend/tests/test_ai_generate_narrative_ir.py`（新規） | AC-3、読み順への写像、SafeMode二層の同時成立、後方互換、切り詰めの可視化（17件） |

**IRビルダー（`llm_input_ir.py`）と仕様（`llm_input_ir_spec.md`）は変更していない。** 本Stageが消費する `relations`（5語彙）と `evidence_links` は Stage 1（`ir_version` 1.1）までに揃っており、`ir_version` は 1.2 のまま据え置きである。**仕様改訂を必要としなかった最初の段階**であり、これは投影層が段階を跨いで償却され始めた最初の証拠でもある（ADR-0069 が想定した「文書単位のコストを複数エンドポイントで償却する」構造）。

### 設計上の判断（実装時に決めたこと）

1. **リクエスト／レスポンスの形を一切変えなかった。** Stage 1・2 は `doc` を任意フィールドとして加え、レスポンスにも観測用フィールド（`alreadyRecorded` / `excludedCardIds` / `truncated`）を足したが、本エンドポイントは `doc` が既に必須であり、かつ実フロントエンド呼出元がある。`truncated` 相当を足せばフロントエンドの型（`GenerateNarrativeResult`）へ波及する。IR経由化はAI入力の質の問題であって契約の問題ではないため、**frontend の変更ゼロ**（`git status --short -- 03_Implement/frontend` が空）で完了させた。
2. **読み順はIRから描かない。** `llm_input_ir_spec.md` §4 は `additionalProperties: false` の閉じたスキーマであり `reading_order` を定義しない。読み順をIRへ入れるには仕様改訂が要るが、読み順は「この文書のこの瞬間の叙述の並び」であって投影すべき構造ではない（Stage 4 の座標と同じく、必要なエンドポイントだけが受け取ればよい）。したがって**IRは骨格（関係）を供給し、背骨（読み順）は従来どおり `doc.readingOrder` から描く**という分担にした。副次的に `mock_local_llm.py` の `_READING_ORDER_LINE` との事実上の契約も自動的に維持される。
3. **関係を読み順の上に写像した（`_narrative_spine_lines`）。** 「`c1 --causal--> c2`」とだけ渡すと、その因果が叙述のどこで効くのかをモデルが再発見する必要がある。それは投影層が肩代わりすべき作業である。島の読み順項目は構成カードへ位置を配り（`_reading_order_slots`）、`causal` / `negate` の2種別に限って `reading-order 1 -> reading-order 2` / `within reading-order 2` / `reading-order 1 <-> outside the reading order` / `outside the reading order` の4形で位置を明示する。`related` 等は文脈として一覧には出すが背骨には載せない。
4. **島間の辺はIRを通さない。** 仕様 §2.3 規則6 が島間辺をIRの対象外としており（派生辺は Stage 4 の `getDerivedIslandEdges()` の主題）、従来どおり `doc.edges` から描く。IR経由化で**従来届いていた文脈を失わない**ことを回帰テストで固定した。
5. **SafeMode の第一層はコメント追加のみ。** `_reject_unreviewed_text(payload.doc, payload.allowUnreviewedText)` の行は1文字も変えず、上に由来コメント（DO NOT REMOVE）を添えただけである。`_reject_unreviewed_*` の呼び出しは変更前後とも12箇所で同一。IR層の `allow_unreviewed_text` は第一層と同じ述語（`allowUnreviewedText is True and settings.allow_unreviewed_ai_text`）を再現しており、緩和プロファイル下で両層が食い違わない（片開きにならない）ことをテストで固定した。
6. **`empty_cards` の挙動変更は受け入れた。** カード0枚の文書は 200（空のプロンプトから叙述を書かせる）ではなく 422 になる。叙述の対象が存在しない以上、草稿を返すことに価値がない。api.md に挙動変更として明記した。フロントエンドは `parseErrorDetail` が `{code, message}` 形の detail を解釈するため `ApiError` としてメッセージが表示され、クラッシュしない（`client.ts` で確認）。
7. **切り詰めはプロンプトに明記した。** レスポンスへ `truncated` を足さない方針（上記1）の代わりに、`MAX_CARDS=200` 超で投影が切り詰められた場合はプロンプト本文へ注記を出す。Stage 2 で立てた「黙って落とさない」原則を、契約を変えずに満たせる範囲で維持したもの。API利用者から観測できない点は api.md に限界として明記した。

### テスト結果

| 対象 | 結果 |
|---|---|
| `pytest tests/test_ai_generate_narrative_ir.py -v` | 17 passed |
| `pytest tests/ -k "narrative or ir or safe_mode" -q` | 228 passed, 2 skipped, 1207 deselected |
| `pytest tests/ -q`（backend 全体回帰） | **1390 passed, 39 skipped, 8 deselected**（Stage 2 のベースライン: 1373 passed, 39 skipped, 8 deselected。差分 +17 は本Stageの新規テストのみで、既存テストの failed / skipped / deselected は1件も増減していない） |
| `pytest tests/test_ai_safemode.py -q` | 20 passed（**無変更で全通過** = 第一層を弱化していないことの直接証拠） |
| `pytest tests/test_ai_prompt.py -q` | 30 passed（`_build_generate_narrative_prompt()` を `ir` 無しで直接呼ぶ既存テストを含む。既定引数 `ir=None` で従来描画に落ちることを担保している） |
| `ruff check`（変更した src / tests） | All checks passed |
| `scripts/check_design_consistency.py` | PASSED（0 errors, 0 warnings） |
| `scripts/check_contract_drift.py` | OK（0 errors, 2 warnings。いずれも本変更以前から存在する Pydantic↔TS の既知差分） |
| `scripts/generate_llm_input_ir_fixture.py --check` | up to date（IRビルダー無変更であることの確認として実行） |
| `python3 01_Plans/docs_check.py` | passed（active_memos=45, tracked_markdown=683） |

frontend は**変更していない**（`git status --short -- 03_Implement/frontend` が空）。リクエスト／レスポンスの形が不変であるため `npm run typecheck` / `vitest` は本変更の検証対象外。

`verify_business_flow_e2e.sh`（実サーバ＋モックLLMを要するため本セッションでは未実行）については、静的確認のみ行った: 呼び出し144箇所、IR経由化で新設された 422（§7.2 `pii_detected` / §7.3 `structured_text_only_violation`）に触れる fixture は無し（`text` / `title` / `summary` / `note` 値1463件を走査、ヒット0件）。**実行は未実施であり、残作業として明記する。**

### Stage 4〜5 に残っていること（Stage 2 の表の更新）

| Stage | 対象 | 主な作業 |
|---|---|---|
| 4 | `suggest-layout` | 座標を渡す唯一のエンドポイント（`include_coordinates=True`）。`getDerivedIslandEdges()` 相当（島間派生辺）が必要になる見込みで、**AC-7 の再評価点**。本Stageで島間辺をIR外に留め置いたため、その判断は Stage 4 へそのまま持ち越されている |
| 5 | 残りのエンドポイント | `refine-card-text` / `suggest-document-title` / `check-narrative` / `suggest-island-summary` / `summarize-island-relation` ほか |
| 全Stage完了後 | AC-10 | 代表規模でのトークン量計測。`MAX_CARDS=200` の影響が本Stageで2エンドポイント目に及んだ（200枚超では叙述の骨格から関係が落ちる）。AC-10 では上限値の見直し要否を判断すること |
| 全Stage完了後 | `ADR-0068` の退役判断 | IR経路が全 `/ai/*` を覆った時点で判断する（**本Stageでも判断していない**） |

### 本Stageで意図的に触れなかったもの

- `llm_input_ir.py` と `llm_input_ir_spec.md`。本Stageは既存の `relations` / `evidence_links` を消費するだけで、仕様改訂を要さない。
- `_reject_unreviewed_cards` / `_reject_unreviewed_text` の呼び出し箇所（12箇所すべて）。1行も変更していない。
- `detect-contradiction` / `suggest-card-groups` / `suggest-layout` ほかのエンドポイントとそのプロンプト構築関数。
- `03_Implement/frontend` 全体（上記 設計判断1）。
- AC-7（TS同値性の検査基盤）と AC-10（トークン量計測）。いずれも Stage 4 以降の主題として据え置き。
