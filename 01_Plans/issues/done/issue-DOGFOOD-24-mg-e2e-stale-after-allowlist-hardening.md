# Issue: DOGFOOD-24 モデルガバナンス強化後、E2Eシナリオ47（MG）が未追従で4件失敗

- Type: Bug / Verification drift（並行編集由来）
- Status: Done
- Source Issue: iteration 188（2026-08-16）の業務フローE2E実走行で、シナリオ47（MG・モデル選択とテナント許容制限）が**4件失敗**（MG ③④⑤⑤b）。並行 `/loop` 編集者がコミットした `model_registry.py` の許容リスト強化（1fc48873）に、E2Eシナリオ47の期待値が未追従であるため。
- Priority: P2
- Owner: Maintainer（並行編集者＝モデルガバナンス強化の当事者と協調）
- Scope: `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（シナリオ47・MG）, `03_Implement/backend/src/kj_atlas_api/routes/model_registry.py`
- Related ADR/Spec: `01_Plans/issues/done/issue-AI-MODEL-GOVERNANCE-03-registry-provider-dispatch-drift.md`（並行編集者が起票）, `02_Architecture/api.md`（allowlist 契約）, `01_Plans/issues/done/issue-DOGFOOD-10-concurrent-iteration-edits-race-with-ci-harness.md`（並行レースの記録）
- Expected verification level: `e2e`

> 追記（iteration 188 検証時）: 本コミット `1fc48873` は **backend単体テストの `test_ai_safemode.py` にも10件の失敗**を引き起こしている（`assert 503 == 200`）。`KJ_ATLAS_LLM_PROVIDER=none`（project settings.json 既定）の環境で、AIルートのモデルプロバイダ解決（`ai.py` の `model_provider_unavailable` → 503）が `generate_with_fallback` スタブより先に発火するようになった。同じく並行編集者コミット由来であり、単体テストの追従も並行編集者の責務範囲。

## 課題

並行 `/loop` 編集者のコミット `1fc48873 fix(admin): harden auth and model governance UX` は、`model_registry.py` の `put_tenant_allowlist` を**強化**した:

1. テナントが活性（`_require_active_tenant`）でなければ拒否
2. 許容リストに**重複ID**があれば 422（`duplicate_model_ids`）
3. 許容リストの**モデルIDが未登録 or 非活性**なら 422（`invalid_model_allowlist`）

一方、E2Eシナリオ47（MG）は**旧挙動を前提**にしている:

```bash
# MG ③: 未登録IDで許容リストを制限
curl -X PUT .../tenants/local-default/allowlist -d '{"modelIds":["bogus-restricted-only"]}'
# → 新挙動では 422（bogus-restricted-only は未登録）
```

この結果、シナリオ47は以下の4件が失敗する（iteration 188 実走行で確認）:

```text
FAIL: MG ③テナント許容リスト設定(制限) (expected 200, got 422)
FAIL: MG ④制限反映（default が残存）
FAIL: MG ⑤非許容モデル -> 403 (model_not_allowed) (expected 403, got 200)
FAIL: MG ⑤b code=model_not_allowed
```

### なぜ問題か

- **凍結済みE2Eの検証ドリフト**: バックエンドの挙動変更（コミット済み）に対して、E2Eシナリオ47の期待値が更新されておらず、業務フローE2Eが **706/706 にならない**。
- **E2E環境に登録済みモデルが1つ（default）のみ**: 新挙動では許容リストに登録済み活性モデルしか指定できず、`default` を除外するには**2つ目のモデル登録**が必要。シナリオ47の「`bogus-restricted-only` で制限」は根本的に成立しない。

## 対応方針（案）

- **並行編集者（モデルガバナンス強化の当事者）と協調**して、シナリオ47を新挙動へ追従させる:
  - 案A: シナリオ47で**2つ目のモデルを admin API 経由で登録**し、許容リストを `[登録済みモデル]` に制限して `default` を除外 → MG ④⑤を成立させる。
  - 案B: シナリオ47の制限対象を「未登録ID」から「登録済みだが非許容のモデル」へ変更。
- 本issueは Open のまま記録し、並行編集者のモデルガバナンス強化（AI-MODEL-GOVERNANCE-03・ADMIN-UX-01）と併せて追従を進める。

## 受入条件

- [x] シナリオ47（MG）が新挙動（登録済み活性モデルのみ許容・未登録/重複/非活性は422）に追従し、業務フローE2E が pass（**749/749**）。
- [x] 単体テスト（`test_model_governance.py`）の新挙動と矛盾しない（**14 passed**）。

## 追記（iteration 194 時点・E2E追従を実施）

**対応方針 案A を実施**: シナリオ47（MG）を新挙動へ追従させた。

- ③を **2つ目のモデル登録**（`POST /admin/provision/models`・`id=restricted`・`providerId=local`）に変更（201 を検証）。
- ④で許容リストを `["restricted"]` に制限（default を除外・登録済み活性モデルのみ許容・未登録IDは 422）。
- ⑤で **default が選択候補から除外**され、⑤b で **default → 403 `model_not_allowed`** を確認。
- ⑥（許容リスト復元・空=既定）は従来どおり維持。
- チェック数は 748→749（モデル登録チェックを追加）。`verify_dogfood_records.sh`・`DOGFOODING_MANIFEST.md`・シナリオ文書の数値照合を **749/791** へ同期。

**検証実走行**: 業務フローE2E **749 passed, 0 failed**（シナリオ1〜124）。`tests/test_model_governance.py` **14 passed**。

**残件（本issueの範囲外・並行編集者領域）**: 追記で記録した `tests/test_ai_safemode.py` の10件失敗（`KJ_ATLAS_LLM_PROVIDER=none` でモデル解決が先に発火し `assert 503 == 200`）は、本issue（E2E追従）の対象外として残る。修正はモデルガバナンス強化の並行編集者の責務範囲。

## 追記2（iteration 195 時点・モデルガバナンスのテスト整合を完了）

- 並行編集者が `dbe8600c fix(ci)` で `test_ai_safemode.py`（10件）・`test_ai_eval_pipeline.py`・`test_ai_provider_status_route.py` に **fixture で `settings.llm_provider="local"`＋登録モデルのseed** を追加し、safemode 10件失敗を解消（commit 済み）。
- 残っていた `test_ce2_proposal_api.py` の **1件失敗**（同根: `_assert_model_allowed` の `model_provider_unavailable` がスタブより先に発火）を **fixture で `settings.llm_provider="local"` を設定・復元** して修正（`dddae039`）。CE2 proposal **12/12**・AI-route 統合 **79/79** pass。
- フルスイート: **1174 pass / 1 fail**（修正前）→ CE2修正後の再走行で **1175 pass 相当**を確認。

## 補足

## 補足

- 本issueは**私（ドッグフーディング）が観察した検証ドリフトの記録**であり、修正は並行編集者（モデルガバナンス強化の当事者）の責務範囲。iteration 188の私の成果物（シナリオ118・DOGFOOD-23）は独立に検証済み。
- DOGFOOD-10（並行イテレーションのレース）と同種の現象。


## 配置の整理（2026-09-05）

- 本Issue群は、並行開発・並行ドッグフーディングによって検証入力や期待値が実行中／変更後の実装とずれ、実回帰ではない失敗を生む verification drift を解消した完了系列として `Done` となっていた。
- `DOGFOOD-10` は E2E スクリプトを実行時スナップショットへコピーしてから走らせることで、`/loop` の並行追記と共有作業ツリー実行のraceを遮断した。
- `DOGFOOD-24` は model governance の allowlist 強化後に古いE2E期待値・テストfixtureが残ったdriftを、登録済み活性モデルを用いるシナリオとprovider設定fixtureへ追随させて解消した。
- いずれも並行編集そのものを禁止するのではなく、検証ハーネスと期待値を現在の実装契約へ整合させることで、検証結果の信頼性を回復した記録である。
- `LEGACY_DONE_AT_ROOT_BASELINE` は10から8へ縮小し、R18 identity manifestは不変の歴史境界として維持する。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
