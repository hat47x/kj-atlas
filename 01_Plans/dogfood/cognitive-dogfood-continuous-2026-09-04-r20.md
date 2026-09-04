# 継続dogfood R20 — merge方式をproviderから保存済みdecisionまで通す

- Date: 2026-09-04
- Scope: 日常開発の自己分析。Case 001〜003の統制比較には含めない。
- Question: R19で確定した `mergeMethod` 契約を、provider応答、frontend、fallback、人間の採否、Document保存まで一度も意味を落とさず通せるか。
- Canvas: `doc_kj_atlas_dogfood_r20.json`
- Result class: 継続dogfoodの内部実装記録。第三者価値実証や認知比較結果の代替証拠ではない。
- External LLM: 使用していない。
- CI: PR作成前。結果はGitHub Actionsを確認後に確定する。

## 1. 実装した契約

R20では、R19で定めた二値を共通の意味語彙として実装した。

- `near_duplicate`
- `kernel_fusion`

backendの `MergeSuggestion` は `mergeMethod` を必須とし、provider promptのJSON schemaも同じ値を要求する。欠落または未知値はfail-closedにする。

frontendのremote/common `MergeSuggestion` も同じ二値を必須にし、decoderで未知値を拒否する。R18で分離した決定論fallback固有metadataは再び共通契約へ混ぜていない。

## 2. fallbackとlocal mockは事実以上を主張しない

決定論fallbackは候補生成の性質に合わせ、常に `near_duplicate` を付ける。

GPUなしで利用経路を確認するlocal mockも、既存のカテゴリ一致による正のmerge候補へ `near_duplicate` を付ける。mockが核融合法を実行したことにはしない。

これにより、remote providerが `kernel_fusion` を返す経路と、決定論的な近接候補探索を同じ内部ロジックだと誤認せずに済む。

## 3. UIでは方式を理由から分離して見せる

提案パネルには、既存の代表カード、AI理由、人間の判断理由とは別に「統合方式」を表示する。

日本語表示は、実際の人間KJ手続を完全実施したと過剰に読めないよう、次の表現とした。

- `near_duplicate`: 「類似カードの整理（04ステップ型）」
- `kernel_fusion`: 「意味核の統合（核融合法型）」

英語でも `style` を用い、同じ境界を保つ。

方式ラベルは判断材料の一部だが、それだけで採否を確定しない。人間の判断理由は従来どおり別入力として必須である。

## 4. decision保存では新規厳格・旧記録寛容を維持する

`appendMergeSuggestionDecision()` の新規入力では `mergeMethod` を必須にし、Appの採否処理から現在のproposal値をそのまま渡す。

一方、保存済み `MergeSuggestionDecision` のschemaではoptionalとして読む。これにより、R20以前のDocumentを壊さず、欠落した方式を推測補完しない。

backendのDocument validationも同じ境界へ合わせた。新しいremote proposalは方式なしを拒否するが、古いDocument decisionは方式なしで読める。

## 5. 回帰テストで固定したこと

R20では次を個別に固定した。

- provider応答で `mergeMethod` が欠ければ拒否する。
- 未知の `mergeMethod` を拒否する。
- `near_duplicate` と `kernel_fusion` の双方を値のまま保持する。
- frontend decoderでも欠落・未知値を拒否する。
- deterministic fallbackは `near_duplicate` を付ける。
- 新規decisionは `kernel_fusion` も含め方式を保存する。
- 旧decisionは方式欠落のまま読め、勝手に推測されない。
- UIが方式をAI理由とは別に表示する。

既存の意味保存guard、acceptとapplyの分離、source lineage、保存・再読込E2Eは変更していない。

## 6. 実装中に守った変更境界

巨大な `App.tsx` へ必要なのは一行だけだった。全ファイル置換で改行を正規化すると、本質と無関係な差分が発生するため、ブランチ限定の一度きりworkflowでバイト列を厳密に1件置換し、そのworkflow自身も同じcommitで削除した。最終差分では `App.tsx` は1行追加だけである。

また、`domain/types.ts` の重複型へ手を広げると既知のF-7重複問題と改行差分が混ざるため、本R20では新しい意味経路に必要な正本側へ限定した。型重複の一般解消は今回の完了条件にしない。

## 7. 正本文書の同期

R20の実装により、API文書の「MergeSuggestionは4項目」「方式フィールドは後で判断」という記述は古くなった。実装と同じ5項目契約へ更新する。

`AI-MERGE-SEMANTICS-01` は、CI成功後に残る未完受入条件がなくなるためDoneへ移す。`AI-IR-STAGE5-SCOPE-01` では、merge方式追跡性を残差としていた一文だけを更新し、Stage 5固有の未完である `check-narrative` のscale境界はそのまま残す。

## 8. 今回完了したものと、別に残すもの

R20で完了させる範囲は、`mergeMethod` のproposal → decision追跡性である。

次は別境界として残る。

- `AI-IR-SCALE-01` と `check-narrative` の大規模文書投影。
- formal Case 001〜003の有効な生の実行記録。
- `VALUE-REALNESS-01` の第三者価値実証。
- 実使用証拠なしの `residuals` 追加や自動merge権限拡張。
- 既知の重複型F-7の一般整理。

R20の内部CIが成功しても、これらを完了した証拠にはしない。

## 9. dogfoodとして得たこと

R20では、新しいフィールドを足すこと自体より、**意味がどの境界で失われ得るかを一つずつ通すこと**を重視した。

provider schemaだけを変えるとfrontendで落ちる。frontendだけを変えるとlocal mockが壊れる。decision型だけを変えるとAppが値を渡さない。さらにDocument validatorがextra fieldを拒否すれば保存で止まる。

一つの意味属性は、型定義ではなく利用者の仕事の経路全体を通って初めて存在する。R18で見つかった契約境界のずれを、R20では新しい意味契約を導入するときの実装手順そのものへ反映した。
