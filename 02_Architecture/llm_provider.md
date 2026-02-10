# LLM Provider 抽象

本ドキュメントは、kj-atlas が将来AI機能（Draft生成・再配置・類似統合・画像生成）を追加する際に、
**外部API依存を固定せず、設定で切替できるようにするための Provider 抽象**を定義します。

MVPでは AI機能を必須としません。
ここでは **枠（Interfaceと設定）だけ**を定義します。

---

## 1. 目的

- イントラ／自前ホストで **Local LLM（社内サーバ）** を利用できる
- 必要に応じて外部API（OpenAI等）も利用できるが、デフォルト依存しない
- LLMの切替は **設定ファイル／環境変数** で行う

---

## 2. Provider の責務境界

Provider は「LLMへ問い合わせる」ことに責務を限定します。

- ルーティング（どのモデル・どのURLに投げるか）
- 認証情報の適用（API key等）
- タイムアウト・リトライ（最小）

プロンプト設計・業務ルール・評価は上位の Use Case 層で行います。

---

## 3. 設定（環境変数）

MVPの段階では、以下の最小セットを想定します。

- `LLM_PROVIDER`：`none | local_http | external`

### 3.1 local_http

- `LOCAL_LLM_BASE_URL`：例 `http://llm.internal:8000`
- `LOCAL_LLM_MODEL`：例 `qwen2.5:32b`
- `LOCAL_LLM_ENDPOINT_STYLE`：`openai_compatible | custom`

### 3.2 external（将来）

- `EXTERNAL_LLM_VENDOR`：`openai | ...`
- `EXTERNAL_LLM_API_KEY`
- `EXTERNAL_LLM_MODEL`

---

## 4. Provider Interface（Python）

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Optional


@dataclass
class LLMRequest:
    task: str  # e.g. "draft_clusters" / "re_layout" / "merge_cards" / "image_prompt"
    prompt: str
    temperature: float = 0.2
    max_tokens: int = 2000


@dataclass
class LLMResponse:
    raw_text: str


class LLMProvider(Protocol):
    async def generate(self, req: LLMRequest) -> LLMResponse:
        ...
```

> 備考：MVPではこのInterface自体を未使用でもよい。

---

## 5. 最小実装方針（非MVPだが設計指針）

### 5.1 NoneProvider

- 例外を返すだけ（"AI is disabled"）

### 5.2 LocalHTTPProvider

- `LOCAL_LLM_ENDPOINT_STYLE=openai_compatible` の場合
  - `/v1/chat/completions` に投げる
- `custom` の場合
  - `POST /generate` 等に投げる

### 5.3 ExternalProvider

- OpenAI等のSDKを使うか、HTTP直叩き

---

## 6. セキュリティ方針

- デフォルトは `LLM_PROVIDER=none`
- 外部送信は明示的な設定が必要
- イントラでは、Base URLを社内ドメインに固定する運用が望ましい

---

## 7. 次に作るもの

- `02_Architecture/deployment.md`：Docker Compose案

