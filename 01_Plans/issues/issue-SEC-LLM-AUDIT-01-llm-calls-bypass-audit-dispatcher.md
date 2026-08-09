# Issue: SEC-LLM-AUDIT-01 LLM呼び出しが監査ディスパッチャを経由せず外部監査基盤へ届かない

- Type: Security / Operations
- Status: Open
- Source Issue: N/A
- Priority: P2
- Owner: Unassigned
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/audit.py`, `02_Architecture/enterprise_architecture.html`, `02_Architecture/llm_escalation_policy.html`, `04_Documentation/security.md`
- Related ADR/Spec: `02_Architecture/enterprise_architecture.html` §04.6, `02_Architecture/llm_escalation_policy.html` §04（CE2-C5）, `01_Plans/adr/ADR-0062-explicit-http-integration-fail-fast.md`
- Expected verification level: `unit`

## 課題

`routes/ai.py:56-60` は LLM 呼び出しをローカルロガーへ出すだけである。

```python
def _audit_llm_trace(task: str, llm_response) -> None:
    logger.info(
        "llm_generate",
        extra={"task": task, **build_audit_fields(llm_response)},
    )
```

監査ディスパッチャ（`audit.py` の `build_audit_dispatcher()`、`main.py:89` で `app.state.audit_dispatcher` へ設定）を使うのは `routes/docs.py` のみである。

```
$ grep -rln "audit_dispatcher" --include="*.py" 03_Implement/backend/src/kj_atlas_api/
audit.py
main.py
routes/docs.py
```

つまり **LLM 呼び出しは外部監査基盤へ送出されない**。`KJ_ATLAS_AUDIT_TRANSPORT=http` を設定した組織でも、AI 関連イベントは届かず、アプリのローカルログにしか残らない。

### 契約との乖離

`02_Architecture/llm_escalation_policy.html` §04（CE2-C5 監査必須項目）:

> CE2/CE4 で生成される監査イベントには、少なくとも以下を含める。`routingStage` / `provider` / `model` / `sourceBundleHash` / `proposalId`

`02_Architecture/enterprise_architecture.html` §04.6 は監査イベントの最小情報（`eventType` / `occurredAt` / `docId` / `action` / `traceId` 等）と PII 非保存を定めている。

外部LLMへ文書内容を送出する行為は、企業・行政の観点では**最も監査すべき事象**である。それが監査証跡へ載らない。

## 付随: 認証エッジのログに含まれる識別子

`trusted_auth_edge.py` は認証失敗時に `subject`（IdP 側の主体識別子）と `external_tenant_ref` を INFO で出力する（`320-323`, `336-339`, `428-431`）。

```python
logger.info("auth edge: unknown tenant provider=%s ref=%s subject=%s",
            provider.id, external_tenant_ref, subject)
```

本プロジェクトは監査イベントについて PII 最小化・生値非保存を明文化している（`enterprise_architecture.html` §04.6）。アプリケーションログが同じ方針の対象かどうかは未定義である。**方針を決めて明文化すること**。`SEC-AUTH-REPLAY-01` AC-5 と重複するため、どちらか一方で対応すればよい。

## 対応方針（実装者向け）

- LLM 呼び出しを `app.state.audit_dispatcher` 経由へ移す。`routes/docs.py` の既存呼び出しを参照実装とすること。
- 記録項目は `llm_escalation_policy` CE2-C5 と `enterprise_architecture` §04.6 の**両方**を満たすこと。少なくとも `provider` / `model` / `task`（routingStage 相当）/ `occurredAt` / `traceId`。
- **プロンプト本文・カード本文を監査イベントへ含めないこと。** `enterprise_architecture` §04.6 は本文非保存を定めている。送出した事実とメタデータのみ記録する。
- 監査送信失敗はアプリ機能を止めない（既存の fail-open 方針を維持、`enterprise_architecture` §04.3）。ただし失敗件数が観測可能であること。
- `ADR-0068`（SafeMode）が採択された場合、SafeMode 緩和が適用された事実も記録対象へ含めること。

## 受入条件

- [ ] AC-1: LLM 呼び出しが `audit_dispatcher` 経由で記録され、`KJ_ATLAS_AUDIT_TRANSPORT=http` 構成で外部へ送出されることを unit テストで固定する。
- [ ] AC-2: 監査イベントの項目が CE2-C5 と `enterprise_architecture` §04.6 の双方を満たす。
- [ ] AC-3: プロンプト本文・カード本文・未レビュー情報が監査イベントに含まれないことをテストで固定する。
- [ ] AC-4: 監査送信失敗時にAI機能が停止しない（fail-open 維持）ことと、失敗が観測可能であることを確認する。
- [ ] AC-5: アプリケーションログにおける主体識別子（`subject` 等）の取り扱い方針を決定し、`04_Documentation/security.md` または `THREAT_MODEL.md` へ明記する。

## 依存関係

- `01_Plans/issues/issue-SEC-AI-SAFEMODE-01-safemode-not-enforced-at-api-boundary.md`（SafeMode 緩和の記録項目が関係する）
- `01_Plans/issues/issue-SEC-AUTH-REPLAY-01-jwt-replay-defence-effectiveness.md`（AC-5 は同issueのAC-5と重複。一方で対応すればよい）

## 検証

- `python -m pytest tests/test_audit.py -q`
- `python -m pytest tests/ -k "ai or audit" -q`
- `python 01_Plans/docs_check.py`
