# Canonicalization

対象読者: import/export、差分比較、AI 提案の根拠確認を行う利用者、開発者、QA。

目的: kj-atlas でいう canonicalization の考え方と、利用者が確認すべき境界を説明します。

範囲外: 内部アルゴリズムの完全仕様、未公開のレビュー手順、設計判断ログ。

## 概要

canonicalization は、同じ意味のデータを同じ形にそろえるための正規化です。カード、島、関係、レビュー状態、bundle hash などを比較するとき、順序や一時的なメタ情報に左右されない判断をしやすくします。

## 使われる場面

- import した JSON の検証。
- export したファイルの再読み込み。
- AI 提案の `sourceBundleHash` 確認。
- E2E や回帰テストでの差分比較。
- review 済み、未レビューの境界確認。

## 利用者が意識すること

- 同じ入力から同じ結果になることが重要です。
- 生成時刻、trace id、provider latency などの一時情報は、比較の主根拠にしません。
- AI 提案は canonical な根拠を持っていても、自動採用しません。
- SafeMode の安全境界を canonicalization で緩和しません。

## import/export の確認

1. export したファイルを保管する。
2. 同じファイルを import する。
3. カード、島、関係、レビュー状態が意図どおり復元されるか確認する。
4. 不要な内部メモや秘密情報が含まれていないか確認する。

## AI 提案との関係

AI 提案では、提案の根拠になった bundle と提案が一致しているかを確認するために hash を使います。hash が一致しない場合は、提案を採用せず保留します。

## 正本

詳細な schema と設計上の規則は、次の文書を参照してください。

- [schemas.md](../02_Architecture/schemas.md)
- [architecture.md](../02_Architecture/architecture.md)
- [ce2_low_risk_ai_assist.md](ce2_low_risk_ai_assist.md)

## 関連文書

- [diagnostics.md](diagnostics.md)
- [e2e_testing.md](e2e_testing.md)
- [narratives.md](narratives.md)
