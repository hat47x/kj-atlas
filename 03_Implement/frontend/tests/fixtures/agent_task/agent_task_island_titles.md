## 依頼

文脈に含まれるカード群から、島（まとまり）のタイトル候補を3件程度、提案してください。対象範囲: カード3枚。

## ガードレール

「あなたの出力は提案であり確定しません／点数・順位・％・優先度の数値を付けないでください／曖昧・対立・未確定はそのまま保持して提示してください／出典のない断定をしないでください／応答は§4の JSON のみで返してください（前後の説明文は不要）」

## 文脈

（未レビューのカード 1件は本文を除外しています）

カード: 3枚（レビュー済み 2・未レビュー 1）
- [claim] 雨が降ると来場者が減る
- [fact] 駐車場が濡れて滑りやすくなる
- [unknown] [REDACTED]:h4f36d401

関係線: 1件
- c1 → c2 (causal)

根拠リンク: 1件
- c2 ⇒ c1

## 応答契約

以下のJSON Schemaの形式で応答してください。

```json
{
  "schemaVersion": "agent-response.v1",
  "taskId": "uuid (依頼のエコーバック・必須)",
  "correlation": {
    "schemaVersion": "agent-task.v1",
    "taskId": "相関ブロックの値",
    "createdAt": "相関ブロックの値",
    "docId": "相関ブロックの値",
    "baseDocSignature": "相関ブロックの値",
    "bundleHash": "相関ブロックの値",
    "queryCanonicalHash": "相関ブロックの値",
    "taskKind": "相関ブロックの値",
    "locale": "ja"
  },
  "respondedAt": "ISO8601 (任意)",
  "agent": "string (例: copilot-studio:<agent名> / m365-copilot。自由記述)",
  "proposals": [
    {
      "proposalId": "string (応答内一意)",
      "kind": "island_title | merge_candidate | narrative_draft | opposing_viewpoint | critique | patch",
      "targetRef": {
        "islandId": "string?",
        "cardIds": [
          "string"
        ]
      },
      "content": {
        "title": "string?",
        "text": "string?",
        "mergedText": "string?",
        "mergeMethod": "near_duplicate | kernel_fusion (kind=merge_candidate のとき必須)"
      },
      "rationale": "string (必須・なぜそう考えたか)",
      "patch": "PatchV1? (kind=patch のときのみ。baseDocSignature は依頼と一致必須)"
    }
  ]
}
```

最小記入例:

```json
{
  "schemaVersion": "agent-response.v1",
  "taskId": "<correlation.taskId をそのまま記入>",
  "correlation": "<依頼の相関ブロックをオブジェクトとしてそのまま記入>",
  "proposals": [
    {
      "proposalId": "p1",
      "kind": "critique",
      "targetRef": {
        "cardIds": [
          "<card-id>"
        ]
      },
      "content": {
        "text": "..."
      },
      "rationale": "..."
    }
  ]
}
```

## 相関ブロック

以下のJSONを、応答の correlation にそのまま echo-back してください（taskId も必ず一致させてください）。

```json
{
  "schemaVersion": "agent-task.v1",
  "taskId": "11111111-1111-1111-1111-111111111111",
  "createdAt": "2026-07-09T00:00:00.000Z",
  "docId": "doc_agent_task_fixture",
  "baseDocSignature": "doc_agent_task_fixture:2026-07-09T00:00:00.000Z",
  "bundleHash": "46adc0a065b03c896f5e87ca5af8a18a325f1045f9a88a00effa1a8332c29bfa",
  "queryCanonicalHash": "0167758da4364dde29fd4848bbef0a7c13496d08a258aa11d99a4f3ef55d4585",
  "taskKind": "island_titles",
  "locale": "ja"
}
```
