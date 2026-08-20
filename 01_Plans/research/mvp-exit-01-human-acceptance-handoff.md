# MVP-EXIT-01 残る人間確認4項目 — Cowork向けハンドオフ

- 目的: `01_Plans/issues/issue-MVP-EXIT-01-productization-readiness.md` の完了条件に残る4件の人間確認を、実機・実際の支援技術・人の目が必要な作業として、Claude Cowork（または担当者）に引き渡す。
- 前提: 2026-07-15時点で、frontend typecheck、Vitest 1,034件、Playwright 165件、accessibility自動検査、Compose構築、保存往復、backup/restore、代表障害からの復旧はすべて成功済み。**製品機能と自動検証はConditional Go、正式な出荷はNo-Go**。この文書はNo-GoをGoへ動かすための残作業だけを扱う。
- 非目標: この文書は個別のUI欠陥修正やテストコード追加を扱わない。実施中に見つかった欠陥は、再現条件と受入条件を持つ個別issue（`PRODUCT-UX-*` 等）へ切り出す。本文書やMVP-EXIT-01へ詳細ログを積み上げない。

## 4項目の全体像

| # | 項目 | 何が必要か | 誰が/何で確認するか |
|---|---|---|---|
| 1 | 物理キーボード操作確認 | 実機の物理キーボード（自動テストのキーイベント送出では代替不可） | 人が実機で操作 |
| 2 | スクリーンリーダー確認 | 実際の支援技術（NVDA/JAWS/VoiceOver等） | 人が支援技術を起動して操作 |
| 3 | リリース候補画面の確認 | 公開文書へ載せる画像そのものの目視 | 人が画像を見て判断 |
| 4 | 最終出荷判断 | 1〜3の結果とCIを踏まえた人間の承認 | Maintainer/Productization owner |

いずれも自動テストでは代替できないため、`Execution` を人間に委譲する。

---

## タスク1: 物理キーボード操作確認

### 何を確認するか
`04_Documentation/acceptance_check.md` の「キーボードで確認すること」章に記載の手順（Tab移動、Enter/Spaceでの実行、パネル遷移、入力欄操作、Escでの復帰）を、**キーボードイベントを自動送出するE2Eではなく、実機の物理キーボードで**実施する。Playwrightの165件はすでに自動検証済みのため、ここで確認すべきは「実際の指の動き・キー配列・OS/IME挙動を含めても迷わず操作できるか」という体感面である。

### 実施手順
1. `03_Implement/deploy` で `docker compose up --build -d` し、`http://localhost:8080` を実機ブラウザで開く。
2. マウスに触れず、`Tab` / `Shift+Tab` / `Enter` / `Space` / `Escape` / 矢印キーのみで次を行う。
   - カード新規作成 → 本文入力 → 確定（Enter）→ 別カードへフォーカス移動。
   - 「表示」パネル・「共有と再現」パネルを開き、次に操作すべき項目へ迷わず移動できるか。
   - 保存操作、ページ再読み込み後の状態確認。
   - 「詳細」トグルの表示/非表示切り替え。
3. フォーカスが「見えなくなる」「どこにあるか分からなくなる」瞬間があれば記録する。
4. IME入力（日本語変換）を使った本文入力で、確定・変換中のEnterが誤操作にならないか確認する。

### 合格基準
- マウスなしで「書く・並べる・束ねる・つなぐ・保存する」の主要操作が完結する。
- フォーカスが常に視認可能で、次にどこへ移動するか予測できる。
- IME入力中のEnterがカード確定と競合しない。

### 記録先
確認結果は本文書に追記せず、`issue-MVP-EXIT-01-productization-readiness.md` の該当ACに「実施日・環境・結果（問題なし/注意あり/停止）」を1行で追記する。「停止」または重大な「注意あり」が出た場合は、個別issueを起票してこの文書からリンクする。

---

## タスク2: スクリーンリーダー確認

### 何を確認するか
MVP-EXIT-01は「開始、編集、保存、共有前確認」の4操作をスクリーンリーダーで確認することを要求している。自動axe検査（accessibility自動検査）は既に成功済みだが、axeは静的なDOM/ARIA違反しか検出できず、実際の読み上げ順序・フォーカス移動・状態変化の音声通知は検出できない。

### 環境選択（いずれか1つで可）
- Windows: NVDA（無料）または JAWS。
- macOS: VoiceOver（標準搭載、`Cmd+F5`で起動）。

### 実施手順
1. スクリーンリーダーを起動し、`http://localhost:8080` を開く。
2. 「開始」: ページ読み込み時に何が読み上げられるか、主要な操作（新規カード、保存、共有と再現）にランドマークやラベルで到達できるか確認する。
3. 「編集」: カードを選択・編集する操作が、選択状態・編集モード・確定を音声で判別できるか確認する。
4. 「保存」: 保存操作の完了が音声で通知されるか（無音のまま完了する場合は問題として記録）確認する。
5. 「共有前確認」: 「共有と再現」パネルの共有前チェック（SafeMode、公開範囲、未レビュー情報件数）が読み上げられ、内容を判断できるか確認する。

### 合格基準
- 4操作それぞれで、次に何をすべきかが音声だけで分かる。
- ボタン・トグル・パネルにアクセシブルな名前がなく「ボタン」「リンク」としか読まれない箇所がない。
- 共有前チェックの内容（SafeMode状態、件数）が音声で読み取れる。

### 記録先
タスク1と同様、`issue-MVP-EXIT-01-productization-readiness.md` の該当ACへ結果を追記する。

---

## タスク3: リリース候補画面の確認

### 何を確認するか
`04_Documentation/` 配下（`assets/screenshots/`、`ui_catalog.md`、`acceptance_check.md` 掲載の画像群）が、公開文書として掲載してよい状態かを目視確認する。

### 確認観点
1. 画面に開発者向け内部情報（内部ID、デバッグ表示、未実装ラベル、Console出力）が写り込んでいないか。
2. 画面の内容が現行UIと一致しているか（古いスクリーンショットが残っていないか）。
3. サンプルカードの本文に、実在の個人情報や機微情報が使われていないか（`data_handling.md` のチェックリストに準拠）。
4. 日本語UIとして、未翻訳・内部都合の語（英語の変数名がそのまま出ている等）が写っていないか。

### 実施手順
1. `04_Documentation/ui_catalog.md` と `acceptance_check.md` に掲載中の全画像を一覧する。
2. 各画像を開き、上記4観点を確認する。
3. 古い・不適切な画像があれば、`PROJECT-GOV-01` 等で言及されている再撮影スクリプト（release-screenshot-capture系）を使って再生成するか、担当者へ差し戻す。

### 合格基準
- 掲載中の全画像が上記4観点をすべて満たす。

### 記録先
`issue-MVP-EXIT-01-productization-readiness.md` の該当ACへ「確認日・確認枚数・問題件数」を追記する。

---

## タスク4: 最終出荷判断

### 何を確認するか
タスク1〜3の結果と、候補commitの必須CI（`.github/workflows/ci.yml`）を確認し、最終出荷（Go/No-Go）を記録する。

### 実施手順
1. タスク1〜3が「問題なし」または「注意あり（Blocker/未解消Majorではない）」で完了していることを確認する。
2. 候補commitのCI（frontend/backend/E2E/docs contract）が全green であることを確認する。
3. `issue-PRODUCT-QA-01-release-readiness-quality-gates.md` のG0〜G7と価値ゲートに未解消のBlockerがないことを確認する。
4. 上記が揃った場合、`issue-MVP-EXIT-01-productization-readiness.md` の完了条件チェックボックスを埋め、Go/No-Go判断と根拠（候補commit SHA、確認日、承認者）を記録する。組織内の正式承認は、導入組織が存在し要求する場合のみ追加する。

### 合格基準（Done条件）
- 残る4つの人間確認が候補commitに対して完了している。
- 重大なBlockerまたは未解消Majorがない。
- 最終出荷判断が記録されている。

---

## Claude Coworkへの依頼プロンプト（コピペ用）

以下をそのまま新しいCowork/Claude Codeセッションの最初のメッセージとして貼り付けて使う。

```
kj-atlasリポジトリ（C:/GIT/kj-atlas）のMVP-EXIT-01（製品化準備）に残る、自動テストでは代替できない4つの人間確認を進めたいです。

参照文書:
- 01_Plans/mvp-exit-01-human-acceptance-handoff.md（この文書。各タスクの手順・合格基準・記録先が書かれています）
- 01_Plans/issues/issue-MVP-EXIT-01-productization-readiness.md（親issue、完了条件）
- 04_Documentation/acceptance_check.md（既存の手動smoke test手順、キーボード確認の土台）

進め方:
1. まず docker compose（03_Implement/deploy）でアプリを起動し、私（人間）が実機で操作できる状態にしてください。
2. ハンドオフ文書のタスク1（物理キーボード）→タスク2（スクリーンリーダー）→タスク3（リリース候補画面）→タスク4（最終出荷判断）の順に、各タスクの「実施手順」を私と一緒に一つずつ進めてください。タスク1・2は実機での物理操作が必要なので、私が実際に操作し、あなたは手順の読み上げ・チェック項目の提示・結果の記録を担当してください。
3. 各タスクが終わったら、「記録先」に指示された場所（issue-MVP-EXIT-01-productization-readiness.mdの該当AC）へ、実施日・環境・結果（問題なし/注意あり/停止）を追記してください。
4. 「停止」または重大な「注意あり」が見つかった場合は、そこで先に進まず、再現手順を個別issueとして起票する準備をしてから、次に進むか判断させてください。
5. 全タスク完了後、タスク4の手順に従って最終出荷判断（Go/No-Go）の記録を私に確認してから issue へ反映してください。最終判断そのものは私が行います。
```

## Traceability

- Source: `01_Plans/issues/issue-MVP-EXIT-01-productization-readiness.md`
- Related: `04_Documentation/acceptance_check.md`, `04_Documentation/ui_catalog.md`, `04_Documentation/data_handling.md`
- Related: `01_Plans/issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`
- Derived-from: 2026-07-16 チャットでの明示的な移譲依頼
