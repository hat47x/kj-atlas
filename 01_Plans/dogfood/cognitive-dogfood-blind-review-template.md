# 認知dogfood ブラインドレビュー記録テンプレート

> Armや使用したmethodを知らない状態で、成果物そのものをsourceへ戻して評価する。
> 単一の総合点やreviewerの好みで順位付けしない。
> Case 001〜003で共通して使用し、それぞれのfixed questionに対応した境界回答を評価する。

## 0. Review情報

- Case ID:
- Round:
- Blind alias:
- Review stage: BR1 / BR2
- Reviewer / run ID:
- Date:
- Reviewer context started fresh: yes / no
- このreviewより前に見た他package: none / <aliases>
- Arm mappingを知っているか: no / yes
- Common source snapshot:
- Package digest:
- Blind status: blind / partial blind / unblinded
- Known limitation:

## 1. Review対象

### BR1

- Package artifact:
- Common source bundle / reference:

### BR2

- 比較するpackages:
- 比較するBR1 artifacts:
- Package presentation order:

## 2. 根拠の正確さ

主要な主張をsourceへ戻して確認する。

| Claim / finding | 使用したsource | Sourceは主張を支えるか | 時点・契約状態を適切に扱ったか | Counterevidenceを扱ったか | Review |
|---|---|---|---|---|---|
|  |  | yes / partial / no | yes / partial / no | yes / partial / no |  |

- 根拠を越えた飛躍:
- Sourceの読み違い:
- 古い状態、条件付き状態、未実装状態を現在状態として扱った箇所:
- 重要なevidenceを適切に使えている箇所:

## 3. 中核回答とCaseの境界

fixed questionへの回答を、機能一覧ではなく、条件を伴う製品・判断境界として読めているかを確認する。

- Packageから読み取れる中核回答・境界:
- Fixed questionへ直接答えているか:
- その回答を支えるevidence:
- その回答を弱めるevidence:
- 提案された境界を適用すべきでない条件:
- 既存手段や代替手段で十分だと適切に扱っている領域:
- 既存手段や代替手段を不当に弱く扱っている可能性:
- まだ不明確な境界:

Caseごとの着眼点は次の範囲に留め、特定の結論を「正解」として与えない。

- Case 001: 利用者の一次仕事と、KJ Atlasが必要・不要になる製品境界。
- Case 002: AIの自律実行、proposal、human confirmation、useful frictionの境界。
- Case 003: local / offline / self-host / data-control と server / collaboration の境界。

## 4. 反証の質

- Package内で最も強いcounter-hypothesis:
- そのevidenceは中核回答を実際に覆す、または修正し得るか:
- 提案された境界が不要になる、または逆転すべき条件:
- 形式的に置かれただけで弱いcounterargument:
- 欠けているdisconfirming evidence:

## 5. 不確実性・異論・残差

- 保持されている重要な不確実性:
- 保持されている重要なdefer:
- 保持されているdissent / counterevidence:
- 目立ちにくい、または孤立したまま残っている重要資料:
- 一般論的な折衷へ平板化された材料:
- uncertain / inference / conditionalからfactへ不当に昇格した材料:

## 6. Sourceの訂正・時点差

package内で中立化された`source-check-N`をすべて確認する。事前登録時の「正解語」を探すのではなく、古い記述、訂正、条件付き設計、未実装契約と現在状態との関係を評価する。

| Check | 検出した関係 | 過去・条件付きの状態を現在状態として誤用したか | Review |
|---|---|---|---|
| source-check-1 |  | yes / no / unclear |  |
| source-check-2 |  | yes / no / unclear |  |
| source-check-3 |  | yes / no / unclear |  |
| source-check-4 | N/A if absent | yes / no / unclear / N/A |  |
| source-check-5 | N/A if absent | yes / no / unclear / N/A |  |

## 7. 意思決定へのつながり

- 具体的な次のvalidation / issue / defer / reject action:
- そのactionは、不足しているevidenceに対応しているか:
- 後のmaintainerが、何のevidenceによって判断が変わるかを理解できるか:
- 不要に新しいADRを求めていないか:
- すべての観察をfeature requestへ変換していないか:
- issue / ADRへ上げず、F0のまま保持すべきもの:

## 8. 成果物からの再訪可能性

ここでは成果物だけを見る。どのmethodを使ったかは推測しない。

- 主要主張を、引用されたevidenceから後で再構成できるか:
- 後のreviewerが、何がuncertain / conditional / unimplementedだったかを識別できるか:
- counter-hypothesisを棄却・保留した理由を後から確認できるか:
- 後から辿るのが難しい部分:

## 9. 重要な見落とし

- 欠落した影響の大きいevidence:
- 欠落した重要な矛盾・状態遷移:
- 欠落した重要な代替手段・既存手段で十分な条件:
- 欠落した重要な未実証仮定:
- Packageにはないがsourceに支えられるcandidate finding:

## 10. BR1 verdict

BR1では他packageとの順位付けを行わない。

- Evidenceに支えられた強み:
- Evidenceに基づく弱み:
- 影響の大きい、生き残ったfinding:
- 影響の大きい、根拠不足のfinding:
- 最も重要な修正点:
- Overall evidence status: robust / usable-with-corrections / weak / invalid
- このreviewへのconfidence: high / medium / low
- Confidenceへ影響するblind上の制約:

---

## 11. BR2 — Package間の統合

BR2でだけ記入する。Arm mappingを見ない状態で行う。

### 11.1 意味上の重複整理

表現だけが違うものを、別findingとして数えない。

| Semantic finding | 含むpackages | Source確認後も生き残るか | Package間の実質的な違い |
|---|---|---|---|
|  |  | yes / partial / no |  |

### 11.2 特定packageでのみ生き残ったfinding

| Finding | 特に強いalias | Source確認 | Decision impact | 他packageで欠落しているか、単なる表現差か |
|---|---|---|---|---|
|  |  |  |  |  |

### 11.3 Package固有の失敗

| Failure | Alias | Evidence | Severity | 結論を変え得るか |
|---|---|---|---|---|
|  |  |  |  |  |

### 11.4 勝者スコアを作らない比較

- 全packageに共通するfinding:
- 一部packageにだけ存在し、source確認後も生き残るfinding:
- 一部packageにだけ存在するunsupported / overclaimed finding:
- Sourceの時点・訂正状態を最も適切に扱っているpackageと、その理由:
- Dissent / uncertaintyを最も適切に保持しているpackageと、その理由:
- Falsificationを最も実質的に扱っているpackageと、その理由:
- Decision / revisitを最も支えているpackageと、その理由:
- 意味上の重複を除くと実質同等に見えるpackages:
- 工程が増えていても成果物上の増分が確認できないcases:
- 成果物が詳しくなっていても、かえって質が下がっているcases:

### 11.5 Unblind前に凍結するverdict

- Unblind後も検討に値する実質的な差:
- 文体やverbosityの違いに過ぎない可能性が高い差:
- 比較を妨げるevidence gap:
- Invalid / partial-blind package:
- Arm mappingを開示した後に確認すべきこと:
- Verdict frozen at:

> このsectionを保存した後でArm mappingを開示する。unblind後の解釈に合わせて、この記録を書き換えない。

## 12. Post-unblind synthesis — 別のpassとして記録

blind verdictを凍結した後でのみ記入する。

- Alias → Arm mapping:
- KJ Atlas incrementのcandidate:
- cultural-substrate-weaving incrementのcandidate:
- Arm D interactionのcandidate:
- Method-induced harmのcandidate:
- M1〜M9 run-record evidenceとの一致・不一致:
- M9 / T9とのtrade-off:
- F0 / F1 / F2 / F3のcandidate:
- まだ必要なcross-case evidence:

単一Caseの結果だけで、product / skillに関する恒久的な判断を確定しない。