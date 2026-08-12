# Issue: UI-RESILIENCE-01 React error boundaryが皆無で、未捕捉の描画例外が未保存作業を復旧不能に破棄する

- Type: Bug
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/main.tsx`, `03_Implement/frontend/src/App.tsx`
- Related ADR/Spec: `02_Architecture/design/ui_design_handoff.md`（侵してはならない核）
- Expected verification level: `unit`

## 課題

- 現在の問題: `03_Implement/frontend/src`全体に React error boundary（`getDerivedStateFromError`/`componentDidCatch`、または`react-error-boundary`等の同等ライブラリ）が一つも存在しない。`main.tsx`のルート描画（`ReactDOM.createRoot(rootElement).render(<StrictMode>{renderRuntimeEntry()}</StrictMode>)`）も、`renderRuntimeEntry()`が返す3分岐（`App`/`TenantSessionRuntimeGate`/`TenantSessionBlockedView`）のいずれも、boundaryで囲われていない。`App.tsx`（約12,000行）は文書・選択・履歴（`history: {past, present, future}`という undo/redo スタック含む在庫状態）をほぼ単一コンポーネントのstateとして保持しており、内部の分割boundaryも存在しない。
- 具体的な影響: この状態でどこか1箇所でも未捕捉の描画時例外が発生すると、React 18の`createRoot`挙動により`App`ツリー全体がアンマウントされ、白紙画面になる。保存は完全に手動（ツールバー保存ボタン・ファイルメニュー・コマンドパレット、いずれも`isDirty`条件つき）であり、自動保存・`beforeunload`ガード・文書内容をローカル保存する仕組みは一切存在しない（`storage/*`はUI設定のみ永続化し、文書・カード本文は対象外）。つまり、未捕捉の描画例外が起きた瞬間、その時点までの未保存の思考過程がすべて復旧不能に失われる。
- 判断が必要な理由: 「捕捉して一般的なフォールバックメッセージを表示するだけの最小boundary」自体は機械的に追加できる（既存パターンなしの新規実装にはなるが判断を要さない）。しかし、この課題の本質的なリスク（未保存作業の消失）に本当に対処するには、(a) フォールバック表示前に`history.present`等の状態をlocalStorageへ緊急退避すべきか、(b) 退避する場合どの状態（文書本文のみか、選択・履歴も含むか）を対象にするか、(c) 次回起動時にどのような復旧UXを提示するか、(d) エラーテレメトリを送信するか、を設計判断する必要がある。最小boundaryだけを実装して「対応済み」とすると、実際のリスク（未保存作業の無言消失）が未解決のまま見た目だけ解消したことになりかねない。
- 発生可能性: 描画ホットパス（`CanvasShell.tsx`/`IslandView.tsx`/`SidePanel.tsx`/`App.tsx`）を精査した限り、non-null assertion（`!`）は8箇所存在するが全て実行時に安全（事前のガード条件、ref初期化直後の参照、同一の純粋関数を2回呼んで同じ結果を得る等）で、危険な`.find(...).property`連鎖や未ガードの配列アクセスも見つからず、現時点でこの手書きコードは「規律的」と評価できる。したがって今すぐ顕在化する具体的なバグの指摘ではないが、(1) `App.tsx`の規模・複雑度が今後も増える、(2) エージェント/外部生成の文書JSONインポート経路（`import/agent_response_import.ts`、`import/zip_import.ts`等）が手書きコードより予期しないデータ形状を描画へ届けやすい経路である、(3) `ResizeObserver`等ブラウザAPI由来の失敗は無防備、という点で潜在的リスクは非自明。

## 対応方針

- 実施すること: React error boundaryの導入要否・範囲（ルート全体を1枚で囲うか、キャンバス/パネル単位で分割するか）と、捕捉時の状態退避・復旧UX・テレメトリ方針をMaintainerが決定する。
- 実施しないこと: 状態退避・復旧UXの設計が定まる前に、フォールバック表示のみのboundaryを単独で実装すること（本質的リスクを未解決のまま「対応済み」に見せてしまうため）。

## 受入条件

- [x] error boundaryの導入範囲（ルート全体 / パネル単位分割）が決定される。— **App 内部のルート render を1枚の `AppErrorBoundary` で包む**（App の state へ到達できる位置。分割境界は任意の強化として据え置き）。
- [x] 捕捉時の状態退避方針（何を・どこへ・いつ）が決定される。— **`history.present`（現行文書）を例外捕捉時に `localStorage["kj-atlas/evicted-doc"]` へ退避**。マウント時に退避があれば復旧バナーを提示。
- [x] 決定に応じてboundaryが実装され、`domain/core_value_guard.test.ts`（CVI群）または同等の回帰テストに、描画例外からの復旧を検証する項目が追加される。— `src/ui/AppErrorBoundary.tsx` 実装＋`AppErrorBoundary.test.ts`（退避/破棄の roundtrip・正常render 3件）。※実DOMでの描画例外トリガーは jsdom 不在のため unit 化（helpers）で固定。

## 検証計画

- 実行する確認: 実装する場合、`cd 03_Implement/frontend && npm run typecheck && npm test`、および意図的に描画例外を発生させるテスト（例: 特定propsで例外を投げるテスト用コンポーネントをboundary配下に配置）でフォールバック表示と状態退避を確認するunit/e2eテスト。
- 期待結果: 描画例外発生時に白紙画面ではなくフォールバックが表示され、決定した範囲の状態が復旧可能な形で保持される。

## 補足

- 発見経緯: 第18ラウンドの「フロントエンドReact error boundary網羅性」観点監査で発見。2名の独立検証者がそれぞれ広範囲の反証探索（service worker・IndexedDB・sessionStorage・別entry point・router単位のerror handling等）を行ったが、代替の安全網は見つからなかった。
- 検証時の指摘: 元調査の「non-null assertion 4箇所」「e2e spec ~189ファイル」という数値はそれぞれ実際には8箇所・67ファイル（テストケース数では約192件）だった。結論（規律的なコード・error boundary皆無・復旧手段なし）自体への影響はない、数値の記録上の誤りとして本文で訂正済み。

## 判断支援（2026-08-12・L2 分析。最終判断は人間）

論点(a)〜(d)への推奨案（仮承認で実装可能な最小スコープの提案として）:

- **(a) 状態退避の要否**: 推奨「退避する」。`getDerivedStateFromError` で例外を捕捉した時点で、`history.present`（現行文書）を `localStorage`（または `sessionStorage`）へ同期退避する。保存は手動のみのため、boundary 捕捉が未保存作業を残す最後の機会。
- **(b) 退避対象**: 推奨「現行文書の `DocumentV1` のみ」。選択・undo履歴は復旧価値が低く、退避容量と複雑度に見合わない。文書本文（カード・島・辺）が思考過程の正体。
- **(c) 復旧UX**: 次回起動時に退避状態を検出し、「復旧する／破棄する」の選択を提示する（`storage/*` の既存UI設定パターンを踏襲）。復旧後は退避データを消去。
- **(d) テレメトリ**: 推奨「外部送信なし」。個人OSS・プライバシー第一の方針（`ADR-0039`・SafeMode思想）に合わせ、エラーは console + フォールバックUI にのみ表示する。
- **実装の配置**: `App.tsx` の state にアクセスできる場所（`App` 内部で render 出力を包む boundary）が必須。ルート境界のみでは `App` の state へ届かない。分割境界（Canvas/パネル単位）は任意の強化。

この判断支援を採択すれば、最小実装（root 内 boundary + 文書退避 + 復旧プロンプト）を仮承認で進められます。
