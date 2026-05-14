# Value Traceability

この文書は、kj-atlas の価値判断が、設計要素、受入条件、検証観点へどのように接続するかを示す対応表です。

`00_Prompt` は価値・用語・禁止事項の上流、`02_Architecture` は実装可能な構造と責務境界の層です。設計や実装が上流の価値からずれている場合は、文書だけで吸収せず、内部 issue または ADR で修正方針を起票します。

`02_Architecture` の各文書で、現行契約と履歴ログのどちらを読んでいるか迷った場合は [contract_reading_guide.md](contract_reading_guide.md) を参照します。

---

## 1. 読み方

- **価値判断**: プロジェクトが守りたい利用者価値や判断軸。
- **利用者に見える成果**: 一般利用者が体験として受け取る状態。
- **上流文書**: 価値・用語・要求の正本。
- **設計への落とし込み**: `02_Architecture` で固定する構造や境界。
- **検証観点**: 受入条件、レビュー、テストで確認する観点。

---

## 2. 価値トレーサビリティ

| 価値判断 | 利用者に見える成果 | 上流文書 | 設計への落とし込み | 検証観点 |
|---|---|---|---|---|
| 意味を急いで確定しない | 未整理・違和感・保留を失敗として扱わず、考え途中の状態を保存できる | `00_Prompt/domain.md`, `00_Prompt/ai_cognitive_externalization_requirements.md` | `WorkingGraph` と `ContextProjectionGraph` を `Consensus Graph` から分離する | AI提案や表示が `Consensus Graph` を直接更新しない |
| 人間の判断を優先する | AIは候補を出すが、採否やレビュー済み化は人間が決める | `00_Prompt/domain.md`, `01_Plans/adr/ADR-0001-value-to-requirements.md` | proposal-only、`patch + approval`、`human_reviewed` の人手昇格 | auto-apply、AIによる `human_reviewed` 自動付与がない |
| 可逆性を守る | 配置、分類、共有前確認をやり直せる | `00_Prompt/domain.md` | snapshot / diff / dry-run / readOnly 境界を維持する | `dryRun=true` で副作用が発生しない |
| 安全に共有できる | export/share 時に未レビュー本文や意図しない情報が混ざらない | `THREAT_MODEL.md`, `02_Architecture/schemas.md` | SafeMode既定ON、share/export policy、`visibility` はラベル用途に限定 | SafeMode / readOnly / visibility の優先順位が崩れない |
| Local-first で小さく始められる | LLMや外部サービスなしでも導入・検証できる | `02_Architecture/runtime_parameter_registry.md`, `02_Architecture/deployment.md` | `KJ_ATLAS_LLM_PROVIDER=none` を既定にし、SQLite / PostgreSQL を切替可能にする | 既定構成で外部 LLM にデータを渡さない |
| 企業・行政運用に接続できる | 組織の認証、認可、監査基盤へ安全に接続できる | `02_Architecture/enterprise_architecture.md` | AuthContext、AccessControlAdapter、audit transport をアプリ本体から分離する | アプリ本体に role/group 判定ロジックを持ち込まない |
| 環境変数の混乱を防ぐ | 利用者が設定すべきキーを迷わない | `02_Architecture/runtime_parameter_registry.md` | 公開設定キーは例外なく `KJ_ATLAS_*` に統一する | 04文書、Compose、runbook が正本と同期している |

---

## 2.1 プロダクト価値実現ループ

`ADR-0032-product-value-realization-model.md` は、上記の価値判断を製品化の実行単位へ落とすため、次の5ループを定義します。

| Loop | 利用者価値 | 02層で守る設計責務 | 主な検証観点 | 対応issue |
|---|---|---|---|---|
| V0: 開始 | 迷わず作業を始められる | 文書入口、SafeMode表示、import-sanitize境界をUI Shellの責務として扱う | 初回起動、サンプル、文書読み込み、SafeMode確認が同じ導線で説明できる | `PRODUCT-UX-01`, `PRODUCT-VALUE-01` |
| V1: 外在化 | メモや違和感を置ける | Raw Note、Card、Hold、Critiqueを削除や失敗ではなく作業状態として扱う | カード作成、保留、違和感が理由なしで記録できる | `PRODUCT-VALUE-01`, `PRODUCT-VALUE-02` |
| V2: 構造化 | まとまり、関係、未整理を同時に扱える | Island、Relation、Pending、View stateを内容削除と分離する | 俯瞰、詳細、保留、関係が往復可能で、表示制御がデータ破壊にならない | `PRODUCT-UX-02`, `PRODUCT-VALUE-02` |
| V3: レビュー | AI候補や要約を人間が採否判断できる | ContextProjectionGraph、proposal-only、patch + approval、reviewStateを分離する | auto-applyなし、`human_reviewed` 自動昇格なし、sourceBundleHash追跡あり | `PRODUCT-VALUE-02`, `CE-*` |
| V4: 共有と学習 | 読者が確定点、保留点、根拠を理解できる | Narrative、Review Pack、SafeMode、review attribution、source traceを共有前確認へ接続する | 共有物に未レビュー情報、保留点、根拠参照、安全状態が明示される | `PRODUCT-UX-03`, `PRODUCT-VALUE-03` |

### 2.1.1 現状不足している設計観点

| 不足観点 | 現状の偏り | 設計上の補強方針 | 起票先 |
|---|---|---|---|
| 初回価値実感 | 文書を開くことと価値を得ることが混同されやすい | 「最初の意味ある配置」をカード、まとまり、保留点を含む状態として定義する | `PRODUCT-VALUE-01` |
| 保留・違和感の日常操作 | 上流概念とAI IRにはあるが、UI作業語彙が不足している | Hold/Critique/Evidence/Contradictionを選択コンテキスト、絞り込み、共有前確認へ接続する | `PRODUCT-VALUE-02` |
| 根拠・主張・反対意見の追跡 | ContextBundleには含まれるが、利用者が見て操作する境界が弱い | EvidenceLink/ClaimType/contradictionを、AI入力だけでなく人間レビューの確認対象にする | `PRODUCT-VALUE-02` |
| 成果物化 | 安全な共有に寄っており、読者が判断できる成果物単位が未固定 | 確定点、保留点、未レビュー情報、根拠への戻り方を成果物パッケージに含める | `PRODUCT-VALUE-03` |
| 価値実現ゲート | UI/安全/文書/診断ゲートはあるが、価値ループ別の合否が薄い | V0〜V4の代表シナリオを `PRODUCT-QA-01` のGo/No-Goへ接続する | `PRODUCT-QA-01` |

---

## 3. 設計判断の扱い

設計文書は、価値判断を再定義する場所ではありません。新しい要件や価値判断が必要になった場合は、先に `00_Prompt` または ADR で扱います。

一方で、既存の設計や実装が上流の価値に合っていない場合は、次の順で扱います。

1. 乖離箇所を内部 issue に記録する。
2. 要件や大方針に影響する場合は ADR を起票する。
3. 文書修正だけで整合できる場合は、正本と参照先を同じ PR で同期する。

---

## 4. 更新ルール

- 新しい主要設計文書を追加した場合は、`AGENTS.md` と本表を同期します。
- 価値判断を変える変更は、`02_Architecture` だけで完結させません。
- 受入条件を追加した場合は、検証観点にも対応する行を追加します。
