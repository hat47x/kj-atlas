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
