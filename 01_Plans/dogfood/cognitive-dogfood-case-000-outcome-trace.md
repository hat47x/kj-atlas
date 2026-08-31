# Cognitive Dogfood Case 000 — R1–R5 outcome trace

- Status: Completed retrospective supplement / exploratory only
- Audit date: 2026-08-30
- Parent audit: `cognitive-dogfood-case-000-r1-r5-audit.md`
- Source artifacts: `doc_kj_atlas_dogfood_r1.json` ... `doc_kj_atlas_dogfood_r5.json`
- Related: `COGNITIVE-DOGFOOD-01`, `COGNITIVE-EVAL-01`, `DOMAIN-W-ITERATION-01`

## 1. この補遺の役割

親監査は、R1〜R5を認知dogfoodの比較前観察として扱える理由と、対照条件・AI提案履歴・認知摩擦等が欠ける限界を整理した。本補遺はそこへ、**R1〜R5の論点が後続のrepository contract・実装・dogfood運用へどのように着地したか**の代表的な追跡を追加する。

これはKJ Atlasの認知増分を証明する文書ではない。観察できるのは「当時の問題・理解・具体策と、後の実装状態の間に対応する変換経路があること」であり、「KJ Atlasを使ったから変更が起きた」という因果帰属ではない。

また、本書はCase 001のanswer keyとして使用しない。Case 001 Round 1のarmには本書を入力しない。

## 2. 監査方法

### 2.1 lineageの強さを区別する

R1〜R5には現行InquiryJourneyのような完全な機械可読lineageがない。ただし、すべてを監査者が後付けで結びつける必要があるわけでもない。

R2以降には `R1-cXX`、`R2-cXX` のような前ラウンド参照があり、R5の `meta.source` には次のような明示的な意味来歴が保存されている。

```text
R3-c01 → R4-i1 → 即時実行可能
R3-c04 → テンプレート強制の実効性確認
R2-c12 + DOMAIN-TITLE-01 Draft
R2-c13 + R4-c07 → 段階的分離
R4-c08 → 運用化
```

したがって本監査では、次の順に証拠強度を扱う。

1. **explicit lineage**: R2〜R5自身が前ラウンドcard/islandを明記している。
2. **downstream repository trace**: 現在のissue、template、CI、code、E2E等が具体策と対応する。
3. **analyst reconstruction**: 文面上は近いが明示参照がない。これは補助仮説に留める。

### 2.2 outcome state

代表論点を次で記録する。

- `resolved/implemented`: 当時の具体策と対応する実装・検証が現在確認できる。
- `transformed/partial`: 対応する変更は起きたが、元の問題全体は残る。
- `corrected`: 後ラウンドで初期認識が訂正・限定された。
- `surviving/open`: 後続でも未解決論点として残る。
- `untraceable`: artifactだけでは後続状態を安全に結べない。

`resolved` は「KJ Atlasが解決を生んだ」という意味ではない。

## 3. 代表的な意味チェーン

| Chain | R1/R2の観察 | R3/R4/R5での変換 | 現在のrepository evidence | State | 主に関係するM |
|---|---|---|---|---|---|
| C0-1 文書ドリフト | R1-c05/c06: 不整合検出不足、二重管理。R2-c07/c08: 検出器はできたが警告ノイズが大きい | R3-c01/c02: 人の記憶依存とfail-closed化不能を構造問題化。R4/R5: baseline化して既存負債と新規流入を分離 | CIは `check_design_consistency.py --baseline ...` と `check_contract_drift.py --baseline ...` を必須実行。現在baselineはdesign consistency 0 warnings、contract drift 2 warningsまで縮退 | resolved/implemented as contract; residual warnings remain | M4, M6, M8 |
| C0-2 三要素整合 | R1-c04: 三要素設計法が明確でない | R3-c04: 方法があってもissue workflowへ出てこない問題へ変化。R4-c01/R5-c03: template/CIへ接続する具体策 | 現在の `01_Plans/issues/TEMPLATE.md` は新規設計判断向けに Business/Data/Function の三要素整合欄を持つ | transformed/implemented | M8 |
| C0-3 文書タイトル | R1-c12: AIタイトル提案なし。R2-c12: `DocumentTitleEditor` は実装されたが実機/E2E未完了 | R5-c04: 新規文書→編集→AI提案→Adoptの一連フローを実機確認する具体策 | `DocumentTitleEditor.tsx` は手動編集、AI候補、明示Adoptを実装。`document-title-editor.spec.ts` は表示・編集・proposal-only・keyboard・Adopt・provider noneを検証 | resolved/implemented for the described flow | M6, M8 |
| C0-4 App.tsx分離 | R1-c16: 約12,200行。R2-c13: 12,252行で分離判断未解決 | R3-c06: 分離コスト認知の偏りという仮説。R4-c07/R5-c11: `DocumentTitleEditor`→`Shell`/`SidePanel`/`WorkModePanel`を段階分離 | 現在これらの独立componentは存在する一方、`App.tsx` 自体も約478KBあり依然大きい | transformed/partial | M4, M8 |
| C0-5 dogfood運用 | R1-c10: dogfood必須なのに具体計画なし。R2-c10: R1/R2成果はあるが運用未成熟 | R3-c10: R1→R2を初の構造的feedback attemptとして認識。R4-c08/R5-c09: KJ Atlas自身を継続dogfoodする運用へ | `DOGFOODING_MANIFEST.md` は再検証可能なdogfood集約を持ち、iteration 240時点で170 scenarios / business-flow 1026 checks / total 1084 checks / dogfood由来Done issue群を記録 | resolved/implemented as verification program; cognitive/value validation remains open | M6, M8 |

## 4. 各チェーンの読み解き

### C0-1 文書ドリフト: 「検出できる」から「新規悪化を止める」へ

このチェーンはCase 0で最も強いM8の観察例である。

R1では不整合検出そのものの不足が問題だった。R2では検出器ができたため、問題は「検出できない」から「警告が多く、運用上fail-closedにできない」へ変わっている。これは初期問題を固定せず、対象側の変化に応じて問いを更新した例でもある。

R3では、人間の記憶や善意に頼る文書同期と、既存warning負債のため新規warningを止められないことが別々の構造問題として表現される。R4/R5では、既存負債をbaselineとして凍結し、新規流入だけをfailさせる方向へ具体化された。

現在のCIはdesign-consistencyとcontract-driftの双方をbaseline付きで実行する。さらにbaseline実体も、design-consistency 0 warnings、contract-drift 2 warningsまで縮退している。

ここから言えるのは、**dogfood上の問題がrepository contractへ変換された**ことである。KJキャンバスがなければこの変更が発見されなかった、という反実仮想までは測れない。

### C0-2 三要素整合: 「方法がある」だけでは実行されない

R3-c04の重要点は、三要素設計法そのものの存在ではなく、日々のissue作成時にその視点が前景化されないことだった。

現在のissue templateには、ADR-0067を参照する `三要素整合（Business/Data/Function）` が存在する。ただしこれは「新規設計判断を含む場合のみ、任意」と明記されている。

したがって、Case 0から現在への正確な変換は「すべてのissueへ強制された」ではなく、**新規設計判断時に三要素を確認できるworkflow contractとして前景化された**である。この限定は保持する。

### C0-3 DocumentTitleEditor: 問題→部分実装→具体的受入フロー

このチェーンは時間状態の変化が明瞭である。

- R1: タイトルAI提案がない。
- R2: editorはできたがE2E/実使用確認が足りない。
- R5: 新規文書→タイトル編集→AI提案→Adoptを明示的な具体策にする。
- 現在: componentとE2Eの双方でproposal-only adoptionまで検証されている。

特に現在のE2Eは、AI候補が出てもcurrent titleを自動変更せず、人間が `Adopt` して初めて変えることを固定している。これはKJ Atlasの「AIはproposal、人間が決定」という価値境界が、抽象原則から具体UI contractへ変換された例でもある。

### C0-4 App.tsx: 成功例だけで監査しない

App.tsx論点は、Case 0を成功物語にしないための重要な反例である。

R5で予告された `DocumentTitleEditor`、`Shell`、`SidePanel`、`WorkModePanel` は現在独立componentとして存在する。したがって「何も進まなかった」ではない。

一方、現在の `App.tsx` はなお約478KBあり、大規模な統合責務を保持している。元の「巨大App.tsx」という問題全体が解決済みとは判定できない。

したがってstateは `transformed/partial` とする。M8は「具体策が何らかの実装へ移った」ことを捉えるが、「問題が解決した」へ自動昇格させない。

### C0-5 dogfood運用: 検証基盤化は進んだが、認知価値とは別

R1の「具体dogfood planがない」は、現在では明確に古い状態である。`DOGFOODING_MANIFEST.md` は、別の生成AIが構造照合と再現実行をできることを目的に掲げ、業務フローE2E、CIハーネス、unit/UI E2E、計画文書整合を集約している。

これはdogfoodが単発観察から継続verification programへ変換された強い証拠である。

ただし、その大部分は実装correctness・回帰・契約検証である。本プロジェクトが新たに測ろうとしている「複雑な開発問題について、AIチャット単独よりも異論・根拠・空白を保持して考えられるか」や、第三者にとっての価値実在性は別問題である。

Case 001以降はこの差を埋めるためにある。

## 5. M1–M9への補正

| Metric | Case 0 outcome traceから言えること | 言えないこと |
|---|---|---|
| M1 生存所見 | 複数論点がR5具体策や現在contractへ生存した | baselineとの差、純粋なKJ増分 |
| M2 根拠接地 | R5には前round IDを含む手書きsemantic provenanceが一部ある | 全カードの不変・完全lineage |
| M3 異論・残差保持 | App.tsx等の未解決/部分解決を後から残せる | 最終成果から消えた全異論を復元できること |
| M4 早期収束耐性 | R1問題がR2で「部分解決」へ訂正され、問題定義が変化した例がある | 段階質問自体の効果との分離 |
| M5 AI依存校正 | not measurable | rejected/modified proposal ledgerが不足 |
| M6 再訪・訂正可能性 | round別artifactとexplicit source refsにより時間変化を再監査できる | 現行InquiryJourneyと同水準の完全revisit性 |
| M7 注意・探索制御 | bugだけでなく設計・process・human cognitionへ観察対象が広がった | 通常chatより広がったという因果比較 |
| M8 決定への変換品質 | docs drift、title、template、dogfoodでdownstream implementation/contractを確認。App分離はpartial | KJ Atlasが変更の原因だったという主張 |
| M9 認知摩擦 | not measurable | useful/waste frictionの比較 |

Case 0のM8は従来より強く評価できる。ただし名称は **transformation evidence** とし、`causal cognitive benefit` へ読み替えない。

## 6. 現行InquiryJourneyとの時点差

R1〜R5は、現在の `InquiryJourneyV1` 手動中核が整う前のartifactである。そのため、個別JSONとfree-text sourceでroundをまたいでいる。

現在の `DOMAIN-W-ITERATION-01` は、既存documentからの探究開始、round記録、比較、非破壊branch、lineage、resume brief、handoff、AIなしの完遂等を受入条件として完了済みにしている。support level全体がなお `L0: Planned` 扱いなのは、単純に「実装されていない」ためではなく、T9の実使用feedbackとT10の外部design trigger等が残るためである。

したがってCase 0から見つかったhistorical lineage gapだけを根拠に、新しい履歴/lineage機能issueを起票しない。Case 001 C/Dで現行InquiryJourneyを実際に使い、それでも再現する不足だけを評価する。

## 7. Finding triage

### F0 — 記録するが新issueにしない

- R1〜R5には完全なrejected/modified AI proposal ledgerがなく、M5は回顧測定不能。
- useful/waste cognitive frictionの記録がなく、M9は回顧測定不能。
- provenanceは一部explicitだが、全カードの不変snapshot/lineageではない。
- App.tsx分離は進展したがpartialであり、Case 0単独では新しい分離issueを追加しない。

### F1 — 既存issueへ返す可能性がある

Case 001 C/DでInquiryJourney手動中核を実利用して、問い・handoff・compare・lineage・resume等に反復摩擦が観測された場合は `DOMAIN-W-ITERATION-01` T9へ返す。

### F2 — 新issue memo

**なし。** Case 0は回顧監査であり、新しい再現可能な機能欠陥を発見していない。

### F3 — ADR候補

**なし。** 長期・横断・破壊的contract変更を要求する新証拠はない。

## 8. Case 001へ渡すもの / 渡さないもの

Case 001の**実験設計者/operator**は、この監査から次を学習してよい。

- 時点差を明示して評価する必要がある。
- `resolved` と `transformed/partial` を分ける必要がある。
- downstream actionを確認しても因果帰属しない。
- M5/M9は測定不能を0点にしない。

一方、Case 001の**各arm分析者**へ、この補遺のchain、current-state判定、M評価、F0〜F3判定を渡さない。arm自身が同じ資料から何を見つけるかを比較するためである。

## 9. 結論

Case 0を深く追うと、R1〜R5は単なる「考えて終わったキャンバス」ではなく、少なくとも複数の論点で、

```text
問題提起
→ 現状更新/部分訂正
→ 構造化された問題
→ 理想状態
→ 具体策
→ repository contract / implementation / verification
```

という変換経路を持つことが確認できる。

とくに文書ドリフト、DocumentTitleEditor、三要素整合、dogfood運用は下流証拠が強い。一方App.tsxはpartialであり、すべてが解決したわけではない。

この結果はM8の**決定・行動への変換可能性**を支持する探索的証拠にはなるが、KJ Atlasの認知優位性を証明しない。次に必要なのは、同じ問い・同じsource snapshotをA〜Dへ与えたprospective comparisonである。