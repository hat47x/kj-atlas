# Issue Draft: DOC-ADR-02 ADR-0047モラトリアムの再起票条件を引用していないADRが9件

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `01_Plans/adr/ADR-0047-design-decision-adr-saturation-and-execution-first.md`, `01_Plans/adr/ADR-0051-bulk-critique-reason-recording.md`, `01_Plans/adr/ADR-0052-canvas-and-menu-aria-semantics.md`, `01_Plans/adr/ADR-0053-support-diagnostics-bundle-boundary.md`, `01_Plans/adr/ADR-0055-work-mode-navigation-semantics.md`, `01_Plans/adr/ADR-0056-card-provenance-metadata-boundary.md`, `01_Plans/adr/ADR-0058-document-contract-v1-rebaseline.md`, `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`, `01_Plans/adr/ADR-0060-representative-visual-cue-source-boundary.md`, `01_Plans/adr/ADR-0061-saas-active-tenant-session-concurrency.md`
- Related ADR/Spec: `ADR-0047`
- Expected verification level: `docs-check`

## 課題

`ADR-0047`（2026-06-10、Accepted）は新規の設計判断ADRにモラトリアムを宣言し、再起票基準 R-1（実使用の摩擦）/ R-2（段階遷移）/ R-3（非機能境界の超過）/ R-4（破壊的契約変更）のいずれかに該当する場合のみ新規ADRを認めている（`:37-40,48`）。

ADR-0047以降に起票された13件のADR（ADR-0048〜ADR-0061）のうち、`ADR-0047` またはR-1..R-4のいずれかを本文中で明示的に引用しているのは5件（ADR-0048, 0049, 0050, 0054, 0057）のみで、残り9件（ADR-0051, 0052, 0053, 0055, 0056, 0058, 0059, 0060, 0061）は本文中に `ADR-0047` への言及もR-トリガーへの言及も一切ない（grep確認、マッチ無し）。`ADR-0047` 自身にも、モラトリアムが実務上どう運用されているか（縮小・解除されたか）を示す改訂・"Superseded by"・注記は無い。

## 調査結果（2026-08-05）

9件それぞれの本文をR-1〜R-4に照らして精読した結果、(a)でも(b)でもなく**混在**であることが判明した。

**トリガーに実質的に合致（5件、遡及的に引用を追記済み）**
- ADR-0051（R-1）: 出荷済み一括批評機能の実利用で顕在化した具体的な摩擦（hold→reason→reviewループの破綻）。
- ADR-0053（R-3）: 新しい共有面（診断バンドル）が既存のSafeMode・共有抑制不変条件と衝突しうる境界判断。
- ADR-0056（R-3）: 新しいメタデータ区分が個人情報・監査不変条件と衝突しうる境界判断。
- ADR-0058（R-4）: `DocumentV1`/`DocumentV1 | DocumentV2` unionの削除・fail-closed拒否という、明確な破壊的契約変更。
- ADR-0060（R-3）: 外部画像取得・生成をADR-0043複雑性予算内に収める境界判断。

**トリガーに合致しない（2件、a11y詳細判断）**
- ADR-0052、ADR-0055: いずれも既存UI（カード、作業モードタブ）のARIA/キーボード意味論の詳細確定であり、axeスモークテストの自動検出結果が起点。実利用摩擦でも、非機能境界超過でも、破壊的変更でもない。ADR-0044のUQ方針という既存マンデート下の実装詳細判断。

**判定保留（2件、投機的なSaaS先行整備）**
- ADR-0059、ADR-0061: マルチテナントという主題はR-2（外部利用者の出現）に近いが、本文自体が「Acceptedは実装完了を意味しない」「実装ゲート未充足」「Claude Design Round 8は先行レッドラインとしてのみ扱う」と明記しており、実際の段階遷移が起きた証拠が本文にない。ADR-0047が名指しで戒める「念のため」の先行整備に近い。

## 対応

トリガーに実質合致する5件のADRへ、`## Traceability` / `## 追跡関係` セクションへ根拠を1行ずつ遡及的に追記した（本コミット）。

**未解決の論点として残す**: 9件中4件（ADR-0052/0055のa11y詳細判断、ADR-0059/0061の投機的SaaS整備）はR-1〜R-4のいずれにも実質的に合致しない。これは「ADR-0047のトリガー一覧が、プロジェクトが実際に続けている種類の作業（アクセシビリティ意味論の判断、確定利用者到来前の先行アーキテクチャ整備）を捕捉できていない」ことを示している可能性がある。トリガー一覧の拡張（例: a11y詳細判断やプロダクト先行整備を明示的に許容する第5トリガーの追加）は`ADR-0047`自体の実質改訂であり、モラトリアムの適用範囲を変える価値判断のため、メンテナの決定を要する。

## 影響

ドキュメントの整合性の問題であり、実行時の挙動には影響しない。ただし、`ADR-0047` のトリガー一覧が実際のADR起票実績の4/13を捕捉できていないため、プロセス文書としての完全性に既知のギャップがある。
