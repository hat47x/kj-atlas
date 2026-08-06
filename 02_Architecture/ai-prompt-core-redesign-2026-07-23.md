# kj-atlas AI プロンプト / 応答契約コア — 監査・再設計・評価ルーブリック

作成: 2026-07-23 / 対象コミット: `main`（origin と同期）
対象: `03_Implement/backend/src/kj_atlas_api/routes/ai.py` の 5 ビルダー
成果物種別: **ドラフトのみ（コード変更なし）**。以下の再設計文は「downstream エンジニアがそのまま差し込める」形で提示する。

---

## 0. スコープと前提（グラウンディング）

### 対象の 5 ビルダー（すべて `ai.py`）
| # | 関数 | 行 | ルート | 応答契約 | パーサ |
|---|---|---|---|---|---|
| 1 | `_build_narrative_check_prompt` | `ai.py:87-136` | `POST /ai/check-narrative` | `CheckNarrativeResponse` (`models_ai.py:46-49`) | `_parse_narrative_check_response` (`ai.py:139-165`) |
| 2 | `_build_island_summary_prompt` | `ai.py:170-197` | `POST /ai/suggest-island-summary` | `SuggestIslandSummaryResponse` (`models_ai.py:74-79`) | `_parse_island_summary_response` (`ai.py:200-233`) |
| 3 | `_build_generate_narrative_prompt` | `ai.py:236-273` | `POST /ai/generate-narrative` | `GenerateNarrativeResponse` (`models_ai.py:59-64`) | `_parse_generate_narrative_response` (`ai.py:276-306`) |
| 4 | `_build_prompt` (layout) | `ai.py:308-359` | `POST /ai/suggest-layout` | `SuggestLayoutResponse` (`models.py:855-858`) | `_parse_suggestion` (`ai.py:362-424`) |
| 5 | `_build_merge_prompt` | `ai.py:427-445` | `POST /ai/suggest-merges` | `SuggestMergesResponse` (`models.py:873-874`) | `_parse_merge_suggestions` (`ai.py:448-492`) |

> **隣接する 6 番目のビルダー**: `_build_relation_summary_prompt`（`ai_relations.py:55-85`, ルート `POST /ai/summarize-island-relation`）はスコープ外だが同じイディオムを共有する。本監査の横断的所見（言語指定・反スコアリング・憲章表現）はこのビルダーにも同様に当てはまる。実際 `ai_relations.py:64-71` は 5 ビルダーより一歩進んでおり（"Never present the output as authoritative"・"unsupported claims" 警告）、再設計時の内部整合の参照点になる。

### プロバイダの現実（再設計の制約条件）
`provider.py` を読むと、プロンプト設計上の前提が固定される:
- LLM へは **単一の `prompt` 文字列**しか渡らない（`LLMRequest`, `provider.py:27-32`）。system/user 分割はない。
- **ネイティブ JSON モード / structured output は未配線**（`llm_provider_spec.md:120-129` の Phase-2）。HTTP プロバイダは `{"text": string}` 単独オブジェクトしか返さず（`provider.py:278-289`）、ルート側が `raw_text` を `json.loads` してパースする。
  - **含意**: 「Return strict JSON only. No markdown.」系の出力形式制約は *over-prescription ではなく load-bearing* である。トリムしてはならない。削るべきは推論手順の逐次スクリプト（下記 G4）であって、出力形式の固定ではない。
- 既定 `temperature=0.2`, `max_tokens=2000`（`provider.py:31-32`）。5 ルートとも上書きしていない。narrative/merge のような発散的タスクに 0.2 はやや低い（付録 B で言及）。
- 既定プロバイダは `none`（LLM 無効, `llm_provider_spec.md:66`）。`large-scale`/`external` は明示 opt-in（`provider.py:204-220`）で、**信頼境界を越える outbound**（`llm_provider_spec.md:42-43`「local と external は outbound 制御・監査・safeMode 赤線化要件が異なる」）。

### 保持すべきハード不変条件（再設計で絶対に後退させない）
1. **応答スキーマ形状**: 各プロンプト内の schema リテラル文字列は、パーサ（`_parse_*`）が要求する形状と完全一致で維持する。キーは英語のまま。
2. **反スコアリング**: `ADR-0048:40`（設計憲章の反パターン「スコア・ランキング・準備度%等の単一正解誘導」）、`02_Architecture/external_agent_collaboration_spec.html`（§01 原則3・§04 禁止フィールド score/rank/confidence/priority）。フロントは既に強制（`agent_task_export.ts:72-73`）。
3. **SafeMode / 未レビュー保護**: `ADR-0028:57`（CE0-SAFEMODE-IF）, `:279`（Guard-01: SafeMode ON 時、未レビュー本文を AI 入力へ含めない）, `llm_provider_spec.md:16`（safeMode 既定 ON・漏えい防止）。
4. **提案のみ / 自動確定なし**: `ADR-0028:56`（AI は候補生成器・自動確定禁止）, `:132-137`（D5 Stop 条件）, `ADR-0057:38`（AI は自動移行・過去成果の書換え・仮説の自動決定をしない）。現行プロンプトの "advisory only / proposal only / never claim certainty"（`ai.py:118, 261-262, 434`）はこの不変条件の表現であり、**言い換えても意味を保持**する。

### 品質ゲートの正本（評価ルーブリックの基盤）
`llm_quality_strategy.md` が本プロダクト自身の品質戦略を定義しており、第3章のルーブリックはこれに整合させる:
- §2 Layer A（決定論・必須）: schema 検証 / 必須セクション存在 / citation カバレッジ / length 境界 / **safeMode 適合（禁止領域への生テキスト漏えいゼロ）** / escalation 無効時 external 不使用（`llm_quality_strategy.md:22-31`）。
- §3 Layer B（任意・LLM セルフチェック）: grounding / missing contradictions / over-assertion（`llm_quality_strategy.md:39-44`）。
- §5: KJ 法の要約は単一正解に収束しない → 「正しさ」より「業務で利用可能か」（`llm_quality_strategy.md:74-77`）。

---

## 1. 横断的所見（5 ビルダー共通の弱点）

個別監査の重複を避けるため、まず共通の欠陥を列挙する。第1章の各節はこれらを参照する。

- **G1 — 出力言語の指定が皆無（最大の user-facing 欠陥）。** `ai.py` を grep しても `日本語`/`Japanese`/`locale` は 0 件。カード本文は日本語（ja 既定）で、`summaryText`・narrative `text`・`message`・`mergedTextDraft` はそのまま UI に出る user-facing テキストなのに、どのプロンプトも日本語出力を指示していない。フロントのタスクシートは `locale: "ja"` を明示している（`agent_task_export.ts:40,297`）。言語ミラーリングへの暗黙依存は脆く、英語の指示プロンプト地の文は英語出力へバイアスをかけうる。**影響大**: #1/#2/#3/#5（#4 は `notes` のみ）。

- **G2 — 反スコアリング（ハード不変条件 #2）がバックエンド全プロンプトから欠落。** フロント（`agent_task_export.ts:72-73`）は「点数・順位・％・優先度の数値を付けない」を固定文で強制するのに、バックエンドの 5 プロンプトは一切言及なし。とくに #5 merge（`rationale` に確度スコアが混入しやすい）・#2 island_summary（`summaryText` がカードを順位付けしやすい）で危険。**イディオム不整合かつ価値整合の穴**。

- **G3 — KJ 法の設計憲章（`ADR-0048:40`）が未表現。** 「一枚一志（原文の声を勝手に要約しない）」「一匹狼を許す（未分類・少数意見は正規状態・保護対象, `ADR-0048:49`）」「己をむなしくする（事前カテゴリ枠を持ち込まない）」がプロンプトに無い。これが「良い KJ 出力（対立や少数意見を保持し、実カードに接地する）」と「凡庸な要約（面白い部分を均してしまう）」の分岐点。とくに #2 island_summary と #5 merge は voice を平均化するリスクが高い。

- **G4 — フロンティアモデルに対して過剰処方的な逐次スクリプト。** 例: `ai.py:263`「For each reading-order item, describe what it appears to contain and what it might mean.」、`ai.py:344-345` の if/then critique ルール。Sonnet-5/Opus 級では「ゴール＋制約」提示が逐次手順スクリプトより高品質で、マイクロ処方はむしろ機械的で literal な文章を誘発する。**注意**: これは G1 の但し書きと両立する — 削るのは *推論手順*、残すのは *出力形式制約*。

- **G5 — 文書が持つ豊かなドメイン信号が入力として未使用。** `DocumentV1` には `claimType`（fact/claim/hypothesis/unknown, `models.py:275`）、evidence links（supports/contradicts, `models.py:434-442`）、edges（関係語彙, `models.py:312-327`）、KA `voice`/`value`（`models.py:295-301`）があるのに、5 プロンプトのうち構造メタを渡すのは #4 layout の `critique` のみ。`ADR-0028:267,273`（構造化コンテキスト＝review flags/contradictions/evidence をメタ層として重畳・切詰め順序 reviewed evidence→contradiction→pending）と `llm_quality_strategy.md:43`（missing contradictions がルーブリック軸）は、矛盾・claimType を入力に含めることを明確に望んでいる。
  - **SafeMode 注意（重要）**: `claimType`・contradiction/evidence の *構造*（ラベル・グラフ辺）は redaction リスクが低い（本文ではない）。一方 KA `voice`/`value` は *散文*であり `card.text` と同じ漏えい面を持つ。**KA テキストや追加のカード本文を redaction ゲートなしに足してはならない**（G6）。本再設計では claimType と矛盾/根拠の構造を任意コンテキストとして推奨し、KA 本文は SafeMode 対応が入るまで見送る。

- **G6 — ビルダー自身に SafeMode ゲートが無い（後退させず「要検証」として旗立て）。** 5 ビルダーは `card.text` を無条件でシリアライズする（`ai.py:101,113,180,251,428`）。フロントは `SafeModePolicy.canExposeText`／`summarizeForSafeMode` でゲートする（`safe_mode.ts:17-51`, `agent_task_export.ts:144-145`）が、バックエンドのビルダーには相当物が無い。LLM 呼び出し（とくに `large-scale`/external）は信頼境界（`llm_provider_spec.md:42-43`, `ADR-0028:279`）。**これは既存のアーキ状態であり、地の文の書き換えでは変わらない** — 本再設計は現行ビルダーと *完全に同じデータ*だけをシリアライズし（新規テキストフィールドを足さない）、不変条件を保持する。ただし (a) ビルダーに redaction ゲートが無く上流依存であること、(b) G5 の追加提案は redaction ゲート無しに採用してはならないこと、(c) 未レビュー本文が external に到達しないことの専用検証が必要なこと、を明示的に旗立てする。

- **G7 — 再設計の共通構造をフロントの正本イディオムに合わせる。** `agent_task_export.ts:301-335` と `02_Architecture/external_agent_collaboration_spec.html`（§03 タスクシート構成）はセクション順を固定している（**依頼→ガードレール→文脈→応答契約→相関ブロック**）。バックエンドは単一文字列だが、この順序に寄せる: **目的（依頼）→ ガードレール（反スコアリング・advisory・KJ 憲章）→ 応答契約（schema）→ 文脈（データ）**。schema をデータ直前に置くことで、モデルが「何を返すか」を見た直後に入力を読む流れになる。

---

## 第1章: 個別プロンプト監査

### 1.1 `_build_narrative_check_prompt`（`ai.py:87-136`）

**現状の挙動.** narrativeText を、reading order・islands（title/cardIds/cardTexts）・cards（text）と突き合わせ、(1) reading order に基づく欠落島/カード、(2) 矛盾（順序不一致・カード本文で裏付けられない主張）、(3) 曖昧な遷移（指示語の参照先不明）を検出し、`{"issues":[{severity, message, references?}]}` を返す（`ai.py:117-135`）。データは全て `json.dumps` でエスケープ済み（`ai.py:97-113`）。パーサは未知の card/island 参照を 422 で拒否（`ai.py:160-163`）、`message` は `min_length=1`（`models_ai.py:34`）、`extra="forbid"`（`models_ai.py:31`）。

**良い KJ 出力が要求するもの.** 一貫性チェックは *advisory* な違和感の指摘であって採点ではない（`ADR-0028:56` proposal-only, `ADR-0057:38`）。良い出力は: 名指ししたカード/島に必ず `references` を付ける（`llm_quality_strategy.md:28` citation カバレッジ）；矛盾を自動解消せず「そう読める/対立がある」と提示する（`ADR-0048:40` 対立の自動解消は反パターン）；severity を一貫した基準で付す。

**不足点.**
- **G1**: `message` は user-facing なのに日本語指定なし。
- **severity の付与基準が無い**（`ai.py:125` は enum を示すのみ）。info/warn/error をいつ使うかの指針が無く、grade 付き契約フィールドが恣意的になる。
- **citation 弱**: schema で `references` は任意（`?`）。カード/島を名指ししたら参照を付ける、という指示が無く、`llm_quality_strategy.md:28` のカバレッジ要件を満たしにくい。
- **G4 微**: 3 カテゴリを固定チェックリスト風に列挙。ゴール化した方が発見漏れが減る。
- **advisory 表現は良好**（`ai.py:117-118`「best-effort」「Never claim certainty」）— 保持する。
- **注意**: `test_ai_prompt.py:85-88` が英語の substring を pin（付録 A）。

### 1.2 `_build_island_summary_prompt`（`ai.py:170-197`）

**現状の挙動.** 対象島の直接メンバーカードのみを使い（ネスト島は無視・MVP, `ai.py:185`）、カード本文を超えた事実を足さず、根拠が弱い/希薄/矛盾なら警告を含め、`{"summaryText, groundingIds, warnings?}` を返す（`ai.py:184-196`）。パーサは groundingIds を「1-10・一意・全てメンバー」で強制（`ai.py:222-231`）、`summaryText`/`groundingIds` は `min_length=1`（`models_ai.py:77-78`）。

**良い KJ 出力が要求するもの.** 島要約は KJ 法の核心。「一枚一志」＝各カードの声を潰さず束ねる（`ADR-0048:40`）；「一匹狼を許す」＝馴染まないカードを切り捨てず、両立しない主張は緊張のまま残す（`ADR-0048:49` 少数意見は保護対象）；実カードに接地し過剰断定しない（`llm_quality_strategy.md:43` grounding / over-assertion）。

**不足点.**
- **G1**: `summaryText` は最も user-facing なのに日本語指定なし。**最重要修正対象**。
- **G3**: 「一枚一志」「一匹狼/少数意見保護」が未表現 → カードを均した凡庸要約になりやすい。とくに矛盾するカードを 1 つの滑らかな要約に融かしてしまう（`ADR-0048:40` 対立の自動解消）。
- **G2**: `summaryText` 内でカードを順位付け/％化しない、の指示が無い。
- **G5**: `claimType`・contradiction を入力に渡していない。fact と hypothesis を区別せず要約すると過剰断定を生む。
- **register**: 断定 vs 推量の register 指針が無い。KJ の洞察文は推量寄り（〜と読める）が適切。
- **良好**: 「Do not add facts beyond the card texts」「Prefer the strongest supporting card ids」（`ai.py:186,192`）は grounding 意図として妥当 — 保持。

### 1.3 `_build_generate_narrative_prompt`（`ai.py:236-273`）

**現状の挙動.** reading order を物語の背骨として順序どおりに辿り、各項目が「何を含み何を意味しうるか」を記述、出力を draft/unreviewed と明示し、`{"text, basedOnReadingOrder, warnings?}` を返す（`ai.py:257-272`）。パーサは `text` 非空（`ai.py:292`）、そして **`basedOnReadingOrder` が元 reading order と完全一致**（要素・順序とも, `ai.py:300-304`）を強制。

**良い KJ 出力が要求するもの.** B 型文章化は reviewed-only 既定のドラフト（`ADR-0028:83,185`）。「これは解釈・可能性である」という認識論的謙抑（`ai.py:261-262` 保持）；読み順に忠実；少数意見・対立を平滑化しない。

**不足点（契約エリシテーションの穴・最重要）.**
- **contract gap**: パーサは basedOnReadingOrder の **完全一致（全件・同順）** を要求する（`ai.py:300-304`）のに、プロンプトは「provided reading order の ID のみを含め順序を保て」としか言わない（`ai.py:268`）。**「全件を省略せずそのままエコーバックせよ」とは言っていない**。部分的にしか言及しない/末尾を落とすと正当な物語でも 422。→ **回避可能な 422 を量産する contract 不整合**。
- **G1**: `text` は user-facing なのに日本語指定なし。
- **G4**: `ai.py:263`「For each reading-order item, describe...」は逐次スクリプト。ゴール（読み順に沿って解釈の草稿を編む）に置換した方が良い。
- **G2/G3**: 反スコアリング・少数意見保護が未表現。
- **empty reading order の扱いが未定義**: `ai.py:271` は "- (empty)" を出すが、その場合の期待出力（`basedOnReadingOrder: []` かつ text 非空）が指示されていない。
- **良好**: draft/unreviewed の明示（`ai.py:264`）は `ADR-0028` の未レビュー保持と整合 — 保持。

### 1.4 `_build_prompt`（layout, `ai.py:308-359`）

**現状の挙動.** カード（id/text/x/y/critique）と島（id/title/cardIds/bounds/anchor/critique）を渡し、「単一の正解を強制せず、もっともらしい代替レイアウトを 1 つ提案」、critique に応じて距離を増減、全 id/text を保持し位置と transform のみ提案、`{"transform, cards[], notes?}` を返す（`ai.py:341-357`）。パーサは transform 有限（`ai.py:387-388`）、**cards が元と同数・全 id 既知・重複なし**（`ai.py:391-407`）、x/y 有限数（`ai.py:411-414`）を強制し、出力カードは元の id/text を保持して x/y のみ採用（`ai.py:416-421`）。

**良い KJ 出力が要求するもの.** 「配置は意味（近接＝親近性・整列は強制せず提案に留める）」（`ADR-0048:40`）。レイアウトは *提案*であり単一正解を押しつけない（`ai.py:343` は既にこれを表現・良好）。critique（too_close/too_far/belongs together）を尊重。

**不足点.**
- **G4**: `ai.py:344-345` の if/then（"too close"→距離増, "belongs together"→近づける）は逐次スクリプト。critique の *意図* を尊重せよ、というゴール提示で十分。ただし critique 文言は自由記述（`models.py:282`）なので、例示は残しつつ「例」と明示するのが安全。
- **G1 軽微**: `notes` は user-facing だが日本語指定なし。
- **憲章接地が薄い**: 「近接＝親近性・整列を強制しない」という *なぜ* が無く、グリッド整列のような単一正解へ寄りやすい。`ADR-0048:40` を一句入れると質が上がる。
- **最も健全なプロンプト**: 「単一正解を強制しない」「id/text 保持」が明示済み（`ai.py:343,346`）。redesign は最小限。
- **注意**: `test_ai_prompt.py:48-51` が英語 substring を pin（付録 A）。データ行フォーマット（`id="c1"`, `bounds=(...)` 等, `test_ai_prompt.py:53-63`）も pin されているので **データ行は改変しない**。

### 1.5 `_build_merge_prompt`（`ai.py:427-445`）

**現状の挙動.** 類似カードの統合候補を提案（適用・削除はしない, `ai.py:434`）、最大 10 件、各 `{groupId, cardIds(>=2), mergedTextDraft, rationale?}` を返す（`ai.py:436-444`）。パーサは <=10・groupId 一意・cardIds>=2・重複なし・既知 id を強制（`ai.py:460-490`）。

**不足点（最も要修正のビルダー）.**
- **バグ級: 生 f-string 補間でエスケープしていない**（`ai.py:428`）:
  ```python
  card_lines = [f'- id="{card.id}", text="{card.text}"' for card in payload.doc.cards]
  ```
  他の全ビルダーは `json.dumps(card.text)` を使う（`ai.py:101,113,180,251`, `ai_relations.py:57`）。結果: (a) `"` や改行を含むカード本文が行構造を壊しプロンプト scaffolding に漏れ出す（`02_Architecture/external_agent_collaboration_spec.html` §04 が inbound 方向で警告するプロンプトインジェクション/構造混同面の outbound 版）；(b) イディオム不整合。**`json.dumps` への修正を推奨**（付録 B・データ形式変更なので地の文だけでなくコード修正として旗立て）。
- **G1**: `mergedTextDraft`・`rationale` は user-facing なのに日本語指定なし。
- **G2**: merge は「類似度スコア/確度」の誘惑が最大。反スコアリング未表現は最も危険。
- **G3（一枚一志）**: mergedTextDraft はカード本文の *統合*。異なる主張を均さず、区別すべき声は区別する、が未表現。統合＝声を潰す、になりやすい。
- **G5**: `claimType` を渡していない。fact と hypothesis の統合可否は claimType 依存。
- **rationale**: schema/パーサとも任意だが、`02_Architecture/external_agent_collaboration_spec.html`（§04 rationale） は rationale 欠落を「根拠未記載」ラベルで受理（保全）とする方針。rationale の記載を促す方が良い。
- **良好**: 「propose only, do not apply/delete」（`ai.py:434`）は自動確定なし不変条件の表現 — 保持。

---

## 第2章: 再設計ドラフト（drop-in）

**方針.** 各ドラフトは `_build_*` が返す `"\n".join([...])` の **命令文（地の文）部分の置換**として提示する。**JSON schema リテラルとデータ行構築は現行と完全一致で保持**（パーサ契約・SafeMode データ面を後退させない）。地の文は user-facing 4 件を日本語、layout は日本語で簡潔に。schema のキーは英語のまま。共通ガードレール文はフロント正本（`agent_task_export.ts:73`）と同一イディオムに揃える。

> **共通ガードレール断片（各プロンプトで再利用）** — フロント `AGENT_TASK_GUARDRAIL_TEXT` を単一プロンプト用に分解したもの:
> - `"これは提案であり、確定ではありません。"`
> - `"点数・順位・パーセント・優先度などの数値評価を付けないでください。"`（反スコアリング / G2 / 不変条件#2）
> - `"曖昧さ・対立・未確定はまとめたり解消したりせず、そのまま保持して提示してください。"`（対立の自動解消禁止 / 少数意見保護 / `ADR-0048:40,49`）
> - `"出典（入力に含まれるカード）で裏付けられない断定をしないでください。"`（grounding / over-assertion 抑制）

### 2.1 narrative check（置換: `ai.py:115-135` の地の文）

```python
return "\n".join(
    [
        # --- 目的 ---
        "あなたは図（ダイアグラム）に対する物語文の整合性を、best-effort で点検します。",
        "出力は助言であり、正しさや確実性を主張しません。",
        # --- ガードレール ---
        "これは提案であり、確定ではありません。",
        "点数・順位・パーセント・優先度などの数値評価を付けないでください。",
        "対立や曖昧さは解消せず、「そう読める」「対立がある」として提示してください。",
        "指摘文(message)は日本語で書いてください。",
        # --- 検出の観点（チェックリストではなく観点として）---
        "次の観点で気づいた点を issue として挙げてください：読み順から見て欠けている重要な島/カード、"
        "読み順と物語の食い違いやどのカード本文でも裏付けられない主張などの矛盾、"
        "参照先が不明な指示語(it/they/this/that/これ/それ 等)による曖昧な遷移。",
        "問題が無ければ {\"issues\":[]} を返してください。",
        # --- severity の基準（grade 付けを一貫させる）---
        "severity は次を目安にします：error=物語が図と矛盾/破綻、warn=誤解を招く/裏付け不足、info=軽微な気づき・改善余地。",
        # --- citation ---
        "特定のカードや島に言及するときは、その id を必ず references に含めてください。",
        "references には入力の図に実在する id だけを含めてください。",
        # --- 応答契約 ---
        "厳密な JSON のみを返してください。マークダウン不可。JSON の外にテキストを出さないでください。",
        "次のスキーマに正確に従ってください：",
        '{"issues":[{"severity":"info|warn|error","message":string,"references":[{"id":string,"kind":"card|island"}]?}]}',
        # --- 文脈（データ行は現行のまま）---
        "Narrative text:",
        payload.narrativeText,
        "Reading order:",
        *reading_order_lines,
        "Islands:",
        *island_lines,
        "Cards:",
        *card_lines,
    ]
)
```
不変条件チェック: schema リテラル維持 / severity enum 英語維持 / advisory 保持 / 反スコアリング追加 / データ行不変（SafeMode 面不変）。

### 2.2 island summary（置換: `ai.py:182-196` の地の文）

```python
return "\n".join(
    [
        # --- 目的 ---
        "あなたは、根拠となるカード群から島(まとまり)の要約ドラフトを作成します。",
        "下に示す直接メンバーのカードのみを使ってください。ネストした島は今回は無視します。",
        # --- ガードレール / KJ 憲章 ---
        "これは提案であり、確定ではありません。要約文(summaryText)は日本語で書いてください。",
        "カード本文にない事実を足さないでください。断定を避け、「〜と読める」「〜の可能性がある」など推量で書いてください。",
        "各カードの元の声を平均化・省略しすぎないでください。両立しない主張は一つにまとめず、対立や緊張はそのまま残してください。",
        "他と馴染まないカードや少数の声を、弱い・劣るものとして切り捨てないでください。",
        "点数・順位・パーセント・優先度などの数値評価を付けないでください。",
        "根拠が弱い・希薄・矛盾している場合は warnings に記してください。",
        "「重要な論点」「今後の課題」のように、他の島の要約としても成立してしまう一般的な文にしないでください。",
        # --- 応答契約 ---
        "厳密な JSON のみを返してください。マークダウン不可。余分なテキスト不可。",
        "次のスキーマに正確に従ってください：",
        '{"summaryText":string,"groundingIds":[string,...],"warnings":[string,...]?}',
        "groundingIds は入力カードから選んだ 1〜10 個の一意な card id にしてください。最も強く要約を支えるカードを選んでください。",
        # --- 文脈（データ行は現行のまま）---
        f'Island id="{island.id}", title={json.dumps(island.title or "")}',
        "Member cards:",
        *card_lines,
    ]
)
```
不変条件チェック: schema リテラル維持 / groundingIds 1-10・一意（パーサ `ai.py:222-231` と一致）/ 「カード本文を超えない」grounding 保持 / 一枚一志・一匹狼・反スコアリングを追加 / データ行不変。

### 2.3 generate narrative（置換: `ai.py:257-272` の地の文）

```python
return "\n".join(
    [
        # --- 目的 ---
        "あなたは、図の読み順(reading order)から物語文のドラフトを作成します。",
        "本文(text)は日本語で書いてください。",
        # --- ガードレール（認識論的謙抑）---
        "これは助言であり、事実・真実・確実性を主張しません。すべての記述を、図に基づく解釈や可能性として述べてください。",
        "点数・順位・パーセント・優先度などの数値評価を付けないでください。",
        "対立や少数意見を平滑化せず、そのまま示してください。出力はドラフトかつ未レビューであることが分かるようにしてください。",
        # --- タスク（逐次スクリプトを外しゴール化）---
        "読み順を物語の背骨とし、その順序に沿って、各項目が何を含み何を意味しうるかを解釈として綴ってください。",
        f'題材のヒント(任意): {json.dumps(instruction_title)}',
        # --- 応答契約（完全一致エコーバックを明示：contract gap 修正）---
        "厳密な JSON のみを返してください。マークダウン不可。余分なキー不可。",
        "次のスキーマに正確に従ってください：",
        '{"text":string,"basedOnReadingOrder":[string,...],"warnings":[string,...]?}',
        "basedOnReadingOrder には、下の Reading order を『一つも省略せず・順序も変えず』そのまま全て列挙してください。"
        "read order に無い id を足さないでください。",
        "読み順が空の場合は basedOnReadingOrder を空配列 [] とし、読み順が未定義である旨を短く述べた text を返してください。",
        # --- 文脈（データ行は現行のまま）---
        "Reading order:",
        *(reading_order_lines or ["- (empty)"]),
    ]
)
```
不変条件チェック: schema リテラル維持 / **完全一致エコーバックを明示**（パーサ `ai.py:300-304` の 422 を回避）/ empty 読み順の期待出力を明文化 / advisory・未レビュー明示保持 / データ行不変。

### 2.4 layout（置換: `ai.py:339-358` の地の文。**データ行 `ai.py:354-357` は pin テストのため不変**）

```python
return "\n".join(
    [
        # --- 目的 ---
        "あなたはレイアウトの提案ドラフトを作成します。",
        "厳密な JSON のみ。マークダウン不可。",
        # --- KJ 憲章（なぜ）+ 反・単一正解 ---
        "配置は意味を持ちます（近いほど親近性が高い）。整列を強制せず、もっともらしい代替レイアウトを一つ提案してください。",
        "id と text はすべて保持し、位置(x,y)と transform だけを提案してください。全カードをちょうど一度ずつ含めてください。",
        # --- critique の尊重（if/then スクリプトを意図の尊重に）---
        "各 critique の意図を尊重してください（例：『近すぎる/too close』なら離す、『まとめるべき/belongs together』なら近づける）。",
        "注記(notes)を付ける場合は日本語で、単一の正解ではなく提案である旨が伝わるようにしてください。",
        # --- 応答契約 ---
        "次のスキーマに正確に従ってください：",
        '{"transform":{"panX":number,"panY":number,"zoom":number},"cards":[{"id":string,"x":number,"y":number}],"notes":string?}',
        # --- 文脈（データ行は現行のまま：pin テスト・SafeMode 面を保持）---
        f"Instruction: {instruction}",
        (
            f"Current transform: panX={payload.doc.transform.panX}, "
            f"panY={payload.doc.transform.panY}, zoom={payload.doc.transform.zoom}"
        ),
        "Cards:",
        *card_lines,
        "Islands:",
        *island_lines,
    ]
)
```
不変条件チェック: schema リテラル維持 / 「全カードを一度ずつ」（パーサ `ai.py:391-392`）/ id・text 保持 / 単一正解を強制しない を保持・強化 / データ行不変。

### 2.5 merge（置換: `ai.py:431-444` の地の文。**付録 B のコード修正と併用推奨**）

```python
return "\n".join(
    [
        # --- 目的 ---
        "あなたは、似ているカードの統合(マージ)候補を提案します。",
        "提案のみを行い、統合の適用や削除は一切しないでください。",
        # --- ガードレール / 一枚一志 / 反スコアリング ---
        "これは提案であり、確定ではありません。統合ドラフト(mergedTextDraft)と根拠(rationale)は日本語で書いてください。",
        "点数・順位・類似度・確度・パーセントなどの数値評価を付けないでください。",
        "各カードの元の声を潰さないでください。区別すべき異なる主張は無理に一つへまとめないでください。",
        "統合しても意味が変わらない、明確に重複・言い換えのカードだけを候補にしてください。判断に迷うものは候補にしないでください。",
        # --- 応答契約 ---
        "厳密な JSON のみを返してください。マークダウン不可。JSON の外に説明文を出さないでください。",
        "候補は最大 10 件までにしてください。",
        "次のスキーマに正確に従ってください：",
        '{"suggestions":[{"groupId":string,"cardIds":[string,...],"mergedTextDraft":string,"rationale":string?}]}',
        "各候補は少なくとも 2 個の cardIds を含めてください。cardIds は入力のカード id だけを使ってください。",
        "なぜ統合できると考えたかを rationale に短く記してください。",
        # --- 文脈（付録 B 適用後は json.dumps でエスケープ）---
        f"Instruction: {instruction}",
        "Cards:",
        *card_lines,
    ]
)
```
不変条件チェック: schema リテラル維持 / <=10・cardIds>=2・入力 id のみ（パーサ `ai.py:460-490`）/ propose-only 保持 / 一枚一志・反スコアリング追加。

---

## 第3章: 評価ルーブリック定義

各ルーブリックは `llm_quality_strategy.md` の二層に整合させる: **Layer A = 決定論・機械判定（必須ゲート）**、**Layer B = 判定（LLM-judge/人手・品質監査）**。各基準は独立にチェック可能な形で記す。〔D〕=決定論、〔J〕=判定。

### 共通ゲート（全 5 プロンプトに適用 — `llm_quality_strategy.md:22-31`）
- **C1〔D〕** `raw_text` が単体で `json.loads` 可能（前後にマークダウン/散文が無い）。
- **C2〔D〕** ルート pydantic モデルで検証成功（`models_ai.py`/`models.py`・該当ルート）。`extra="forbid"` 対象は余分キーで fail。
- **C3〔D〕 反スコアリング**: 出力の全文字列フィールドに、数値スコア/順位/％/確度/優先度を表す表現（例: 正規表現 `\b\d{1,3}\s*%`、`スコア|順位|優先度|確度|信頼度`、`\b(rank|score|confidence|priority)\b`、`★|/5|点`）が **無い**。1 件でも fail-closed。
- **C4〔D〕 出力言語**: user-facing テキストフィールド（該当プロンプトの該当フィールド）が日本語（例: ひらがな/カタカナ/CJK を含む・ASCII のみでない）。
- **C5〔D〕 SafeMode**: 入力が「未レビュー本文除外」で構成されていた場合、出力に未レビュー生本文が復元されていない（`llm_quality_strategy.md:30`・`ADR-0028:279`）。
- **C6〔J〕 over-assertion 抑制**: 根拠に対して過剰な断定をしていない（`llm_quality_strategy.md:43`）。

### 3.1 narrative check
- **N1〔D〕** `issues` は配列。各要素 `severity ∈ {info,warn,error}`・`message` 非空（`models_ai.py:33-34`）。
- **N2〔D〕** すべての `references[].id` が入力の card/island に実在（`kind` と一致）— パーサ `ai.py:160-163` を独立再現。
- **N3〔D〕** 問題無し時に `{"issues":[]}` を返せる（誤検出を強要しない）。
- **N4〔J〕 citation カバレッジ**: message が特定カード/島を名指しする場合、対応する `references` が付いている（`llm_quality_strategy.md:28`）。
- **N5〔J〕 severity 一貫性**: 同種の指摘に一貫した severity が付く（2.1 の目安に沿う）。
- **N6〔J〕 対立の非解消**: 矛盾を「どちらが正しい」と裁定せず、対立として提示（`ADR-0048:40`）。
- **N7〔J〕 有用性**: 指摘が実際にレビュー価値のある違和感を突いている（`llm_quality_strategy.md:74-77`）。

### 3.2 island summary
- **I1〔D〕** `summaryText` 非空・`groundingIds` は 1〜10 個・一意・全て対象島のメンバー（パーサ `ai.py:222-231`）。
- **I2〔D〕 length 境界**: `summaryText` が下限〜上限内（例: 15〜400 字。`llm_quality_strategy.md:29`。上限はカード本文を丸写しさせない意図）。
- **I3〔J〕 grounding**: summaryText の各主張がメンバーカードから辿れる。カード本文にない事実の混入が無い（`ai.py:186` の意図・`llm_quality_strategy.md:42`）。
- **I4〔J〕 一枚一志**: 個々のカードの声を潰さず、異なる主張を平均化していない（`ADR-0048:40`）。
- **I5〔J〕 少数意見保護**: 馴染まないカード/少数の声が黙殺されていない（`ADR-0048:49`）。混在時は warnings か本文で緊張を提示。
- **I6〔J〕 矛盾の検出**: メンバー間に矛盾があるとき warnings に反映（`llm_quality_strategy.md:43` missing contradictions）。
- **I7〔J〕 register**: 推量寄りの日本語（断定しすぎない）。
- **I8〔J〕 転写検査**: `summaryText` が他の島の要約としても成立してしまわないか（分類名化していないか。`00_Prompt/kj_technique.md:3` 転写検査）。

### 3.3 generate narrative
- **G-N1〔D〕** `text` 非空（`ai.py:292`）。
- **G-N2〔D〕 完全一致エコーバック**: `basedOnReadingOrder == 入力 readingOrder`（要素・順序とも完全一致。空なら `[]`）— パーサ `ai.py:300-304` を独立再現。**回避可能 422 の主要因なので必須ゲート**。
- **G-N3〔D〕 未レビュー明示**: `text` にドラフト/未レビューを示す語がある（`ADR-0028` 未レビュー保持・`ai.py:264`）。
- **G-N4〔J〕 読み順忠実**: 物語が reading order の順に展開し、各項目に触れている。
- **G-N5〔J〕 認識論的謙抑**: 断定でなく解釈・可能性として述べている（`ai.py:261-262`）。
- **G-N6〔J〕 平滑化しない**: 対立・少数意見が均されていない（`ADR-0048:40,49`）。
- **G-N7〔J〕 grounding / 非捏造**: reading order 項目に無い事実を創作していない。

### 3.4 layout
- **L1〔D〕** `transform.{panX,panY,zoom}` が有限数（`ai.py:387-388`）。
- **L2〔D〕** `cards` が入力と同数・全 id が入力に実在・重複なし（パーサ `ai.py:391-407`）。
- **L3〔D〕** 各 `cards[].x,y` が有限数（`ai.py:411-414`）。
- **L4〔D〕** 出力は位置と transform のみを変更（id/text を書き換えていない — パーサは元 id/text を保持するが、モデルが別フィールドを足していないこと）。
- **L5〔J〕 critique 尊重**: critique がある対象で、その意図に沿う位置変更になっている（too_close→距離増 等。`models.py:602` の critiqueType 意味）。
- **L6〔J〕 近接＝意味**: 関連の強いカード/同一島のカードが空間的に近い（`ADR-0048:40`）。
- **L7〔J〕 非・単一正解**: グリッド一律整列などの強制正解化になっていない（`ai.py:343`）。`notes` があれば日本語で提案トーン。

### 3.5 merge
- **M1〔D〕** `suggestions` <=10・各 `groupId` 一意・`cardIds` >=2・重複なし・入力 id のみ（パーサ `ai.py:460-490`）。
- **M2〔D〕** `mergedTextDraft` 非空・日本語（C4）。
- **M3〔D〕 propose-only**: 出力に適用/削除を表す副作用フィールドが無い（schema は候補のみ・`ai.py:434`）。
- **M4〔J〕 統合妥当性**: 各 group のカードが実際に重複/言い換えで、統合しても意味が保たれる（誤統合でない）。
- **M5〔J〕 一枚一志**: mergedTextDraft が構成カードの区別すべき主張を潰していない（`ADR-0048:40`）。
- **M6〔J〕 保守性（過剰統合の抑制）**: 迷う程度の弱い類似を候補化していない（少数意見を統合で消さない・`ADR-0048:49`）。
- **M7〔J〕 rationale**: なぜ統合できるかが簡潔に述べられている（`02_Architecture/external_agent_collaboration_spec.html`（§04 rationale））。

---

## 付録 A: テスト影響（downstream エンジニア向け・必読）

`03_Implement/backend/tests/test_ai_prompt.py` は **プロンプトの英語 substring を厳密に pin している**。第2章のドラフトを適用すると以下が落ちる。差し替え時にアサーションの更新が必要:
- `test_build_prompt_includes_critique_constraints_and_context`（`test_ai_prompt.py:45-63`）: `"Do not force a single correct answer..."` 等の英語行を assert。→ 2.4 の日本語行に更新。**ただしデータ行アサーション（`id="c1"`, `text="alpha"`, `bounds=(...)`, `anchor=(...)`, `cardIds=[...]`, `test_ai_prompt.py:53-63`）はデータ行を不変に保つので通り続ける**。
- `test_build_prompt_omits_critique_when_absent`（`:66-74`）: データ行依存なので通る。
- `test_build_narrative_check_prompt_includes_required_checks`（`:76-90`）: `"best-effort narrative consistency check"`, `"Identify missing..."` 等を assert → 2.1 の日本語に更新。`island id="i1"` / `card id="c2"`（データ行）は通る。
- `test_build_generate_narrative_prompt_mentions_unreviewed_and_reading_order`（`:128-139`）: `"reading order as the narrative spine"`, `"draft and unreviewed"` を assert → 2.3 の日本語に更新。

パーサ系テスト（`_parse_*` を叩くもの）は **schema・契約を変えていないので全て通る**（例: `test_parse_generate_narrative_response_*` `:142-171`、`test_parse_narrative_check_response_*` `:93-126`）。island_summary/merge のビルダー地の文を pin するテストは現状存在しない（grep 済み）ので、それらは自由度が高い。

## 付録 B: 併用推奨のコード修正（プロンプト外・データ形式）

本成果物はドラフトのみだが、プロンプト品質と不可分な小修正を 2 点、明示的な *提案* として記す（実装判断は downstream）:

1. **merge のエスケープ修正（バグ級）** — `ai.py:428` を他ビルダーと揃える:
   ```python
   card_lines = [f'- id="{card.id}", text={json.dumps(card.text)}' for card in payload.doc.cards]
   ```
   理由: `"`/改行を含むカード本文による行構造破壊・outbound プロンプト構造混同の解消（`02_Architecture/external_agent_collaboration_spec.html` §04）。**データ形式変更なので、merge ビルダーの pin テストが将来足された場合は要同期**（現状は無し）。

2. **temperature の per-task 調整（任意・軽微）** — 全ルートが既定 `temperature=0.2`（`provider.py:31`）。発散が要る #3 narrative・#5 merge は `LLMRequest(..., temperature=0.4〜0.5)` 程度が妥当な一方、#1 check・#4 layout は 0.2 維持が良い。これはルート側 `LLMRequest` 生成箇所（`ai.py:511-514, 546-550, 653-657` 等）の変更であり、プロンプトではないので **flag に留める**。

## 付録 C: SafeMode / G5 に関する明示的注意（不変条件の保全宣言）

- 第2章のドラフトは **現行ビルダーと完全に同一のデータ行**（同じ `card.text`/`island.title`/reading order 行）だけをシリアライズする。新規テキストフィールドを追加していない。したがって SafeMode の漏えい面は **後退しない**（不変条件 #3 保持）。
- G5 で推奨した「`claimType`・矛盾/根拠の *構造* を任意コンテキストに追加」は、それ自体は散文ではなくラベル/グラフ辺なので低リスクだが、**採用する場合でも `card.text` 追加ではないことを確認**すること。KA `voice`/`value` の追加は `card.text` と同じ漏えい面を持つため、**SafeMode redaction ゲート（`safe_mode.ts` 相当のバックエンド版）が入るまで見送り**。
- 独立の要検証事項（本再設計の範囲外だが旗立て）: バックエンドの 5 ビルダーには `SafeModePolicy` 相当のゲートが無く（`ai.py` に safe_mode 参照なし）、未レビュー本文の redaction は上流（呼び出し側の doc 構成）に依存している。`large-scale`/external プロバイダ有効時に未レビュー本文が outbound しないことの専用テスト（`llm_quality_strategy.md:30`・`ADR-0028:279` Guard-01）を推奨する。
