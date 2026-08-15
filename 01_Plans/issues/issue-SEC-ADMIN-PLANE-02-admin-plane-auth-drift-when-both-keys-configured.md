# Issue: SEC-ADMIN-PLANE-02 両キー設定時に管理面が業務キーを前提とし、a2a3-gate:validate は control-plane 認可を持たない

- Type: Security
- Status: Done
- Source Issue: SEC-ADMIN-PLANE-01（分離の残余ギャップ。ドッグフーディングで実測）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/main.py`, `03_Implement/backend/src/kj_atlas_api/routes/admin.py`, `03_Implement/backend/tests/test_control_plane_authorization.py`, `03_Implement/backend/tests/test_a2_a3_gate_validation.py`
- Related ADR/Spec: `01_Plans/adr/ADR-0072-control-plane-authorization-separation.md`, `02_Architecture/runtime_parameter_registry.md`
- Expected verification level: `integration`

## 課題

`KJ_ATLAS_API_KEY` と `KJ_ATLAS_ADMIN_API_KEY` を**両方設定して実機走行**したとき、管理面の認可分離に2つのギャップを確認した。

### 事実1: 管理面（/admin/provision/*）が業務キーを前提とする

`main.py` のグローバル middleware `require_api_key` は `/healthz` を除く全パスに業務キー（`X-API-Key`）を要求する。管理面もこの middleware を通るため、`KJ_ATLAS_ADMIN_API_KEY` 設定時に **`X-Admin-Api-Key` のみでは 401** になる。

```text
=== provision/users — admin key ONLY ===  → 401（middleware が x-api-key 欠損で拒否）
=== provision/users — BOTH keys ===        → 201
```

`SEC-ADMIN-PLANE-01` の分離テスト（`test_control_plane_authorization.py`）は**常に `api_key=None` の状態で** admin キー単独を検証しており（`test_admin_credential_reaches_the_control_plane`）、両キー設定時の挙動は未テスト・未固定だった。

これは ADR-0072 の分離原則（「管理面の認可を業務面のAPIキーと未分離」の解消）に対して**不完全**である:
- 業務キー失効で管理運用が止まる（管理面が業務面に従属する）。
- admin キー保持者が業務キーも併せ持つ必要がある（資格情報の従属・乱用面の拡大）。
- registry の契約文言「正しい `X-Admin-Api-Key` が成功する」は、業務キー未設定時のみ成立する。

### 事実2: a2a3-gate:validate に control-plane 認可が無い

`POST /admin/provision/hil-rs/a2a3-gate:validate` は `/admin/provision/*` 配下だが `require_control_plane_authorization` を持たない（rate limit のみ）。`SEC-ADMIN-PLANE-01` AC-2 の対象は「3ルート」（users / identity-providers / tenant-identity-providers）で、本ルートは含まれない。

```text
=== a2a3-gate:validate — business key ONLY → 200（分離違反）
=== a2a3-gate:validate — admin key → 401（middleware が業務キー欠損で拒否）
```

業務キー単独で `/admin/provision/` 配下へ到達できる唯一の経路であり、AC-2 の「業務面の資格情報だけでは到達できない」に抵触する。

## 対応方針

- 実施すること（D-a）:
  1. **グローバル middleware の /admin/ バイパス**: `require_api_key` が `/admin/` で始まるパスを業務キー要求から除外し、管理面の認可を `require_control_plane_authorization` へ一本化する。
  2. **a2a3-gate:validate への control-plane 認可追加**: 残る1ルートに `require_control_plane_authorization` を付与し、/admin/provision/* 全4ルートで「業務キー単独では到達不可」を固定する。
  3. **テスト固定**: 「両キー設定時に admin キー単独で 201」と「業務キー単独で 401」を統合テストで固定する。`a2a3-gate:validate` を `_CONTROL_PLANE_ROUTES` へ追加する。tenant-session-precondition の exemption 分類を `_NO_TENANT_RESOURCE`（DB不使用）から `_CONTROL_PLANE_AUTHORIZED`（control-plane 認可必須）へ移す（control-plane 認可が DB 依存のため `test_no_tenant_resource_exemptions_cannot_reach_the_database` と整合させる）。
  4. **検証経路**: `verify_api_admin.sh`（CLI/API 管理面の検証）を追加し、DOGFOOD-06 規約（成功＋異常系）で固定する。
- 実施しないこと:
  1. 業務キー middleware を全廃する（非 /admin/ の業務面保護は維持）。
  2. admin キーで業務面へ到達可能にする（admin キーは /admin/* にスコープする。管理面資格情報の業務面への横滑りを許さない）。

## 受入条件

- [x] 両キー設定時に `X-Admin-Api-Key` 単独で /admin/provision/* へ到達できる（201）。→ 4ルート全て `require_control_plane_authorization`（`routes/admin.py:126/276/349/445`）。`verify_api_admin.sh` が admin key で a2a3-gate 200 を固定。
- [x] 業務キー単独では /admin/provision/* 全4ルートへ到達できない（401 `control_plane_unauthorized`）。→ `test_control_plane_authorization.py`（4ルート・業務キーのみ401・`control_plane_unauthorized`）。`verify_api_admin.sh` も業務キーのみ401を固定。
- [x] a2a3-gate:validate が control-plane 認可を要求し、`_CONTROL_PLANE_ROUTES` で分離テストの対象になる。→ `routes/admin.py:274` の `hil-rs/a2a3-gate:validate` が `require_control_plane_authorization` 配下（test 58行目が4ルートに含む）。
- [x] 業務面（非 /admin/）は従来どおり業務キーで保護される。→ `test_control_plane_authorization.py` が業務面の既存キー保護と分離を固定。
- [x] `verify_api_admin.sh` が DOGFOOD-06 規約（成功＋異常系）で管理面を検証する。→ 無key401・誤key401・業務キーのみ401・admin key 200・drift 409/422 を実走行（verify_all.sh 統合済み）。

## 対応記録（2026-08-15・iteration 40）

本issueはコード実装済みだった（AC全項目が既存テスト/スクリプトで満たされていることを本日再検証）。`test_control_plane_authorization.py` 31 tests pass・`verify_api_admin.sh` 実走行で管理面分離を確認したため、Status を Done へ更新（iteration 34の棚卸しの取りこぼし）。実装の実体は `SEC-ADMIN-PLANE-01`（P0・AC-1〜4,6,7）および `verify_api_admin.sh` の導入時に同時に成立していた。

## 検証計画

- `python -m pytest tests/test_control_plane_authorization.py tests/test_a2_a3_gate_validation.py -q`
- 両キー設定の実バックエンドで `bash 03_Implement/backend/scripts/verify_api_admin.sh`
- `python 01_Plans/docs_check.py`

## 補足

- 発見経緯: ドッグフーディングで「管理者が自前スクリプトで CLI/API を利用する」経路を検証すべく、両キー設定の実バックエンドで /admin/provision/* を実走行した際に検出（2026-08-14）。
- 三要素分析: **業務設計**（管理面は業務面と独立した制御プレーン）／**機能設計**（middleware と route dependency の二段が管理面に業務キーを要求）／**データ設計**（`KJ_ATLAS_ADMIN_API_KEY` は /admin/* 専用と registry に明記）のうち、機能設計が業務設計に追従していない実例。
