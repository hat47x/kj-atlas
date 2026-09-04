import { useMemo, useState, type FormEvent } from "react";

import {
  AdminModelApiError,
  getTenantModelAllowlist,
  modelAllowlistApi,
  type ModelAllowlistSnapshot,
} from "./model_allowlist_api";
import {
  duplicateModelIds,
  parseModelIdDraft,
  saveAllowlistDraft,
  type SaveAllowlistOutcome,
} from "./model_allowlist_admin";

type ConflictOutcome = Extract<SaveAllowlistOutcome, { kind: "conflict" }>;

function formatError(error: unknown): string {
  if (error instanceof AdminModelApiError) {
    const code = error.code ? ` (${error.code})` : "";
    return `${error.message}${code}`;
  }
  return error instanceof Error ? error.message : "管理APIの呼び出しに失敗しました。";
}

function ModelList({ values, emptyLabel }: { values: string[]; emptyLabel: string }) {
  if (values.length === 0) {
    return <p style={{ margin: 0 }}>{emptyLabel}</p>;
  }
  return (
    <ul style={{ margin: "0.4rem 0 0", paddingLeft: "1.4rem" }}>
      {values.map((value) => <li key={value}><code>{value}</code></li>)}
    </ul>
  );
}

export function ModelAllowlistAdminConsole() {
  const [tenantId, setTenantId] = useState("");
  const [adminApiKey, setAdminApiKey] = useState("");
  const [baseline, setBaseline] = useState<ModelAllowlistSnapshot | null>(null);
  const [draft, setDraft] = useState("");
  const [conflict, setConflict] = useState<ConflictOutcome | null>(null);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const credential = useMemo(
    () => ({ adminApiKey: adminApiKey.trim() || undefined }),
    [adminApiKey],
  );

  async function loadCurrent(event?: FormEvent) {
    event?.preventDefault();
    const requestedTenantId = tenantId.trim();
    if (!requestedTenantId) {
      setError("tenant IDを入力してください。");
      return;
    }
    setBusy(true);
    setError("");
    setStatus("");
    try {
      const current = await getTenantModelAllowlist(requestedTenantId, credential);
      setBaseline(current);
      setDraft(current.modelIds.join("\n"));
      setConflict(null);
      setStatus("現在のallowlistを読み込みました。");
    } catch (loadError) {
      setError(formatError(loadError));
    } finally {
      setBusy(false);
    }
  }

  async function saveDraft() {
    const requestedTenantId = tenantId.trim();
    if (!baseline || baseline.tenantId !== requestedTenantId) {
      setError("保存前に対象tenantの現在値を読み込んでください。");
      return;
    }
    if (conflict) {
      setError("競合差分を確認し、新しい編集基準を選んでから保存してください。");
      return;
    }
    const modelIds = parseModelIdDraft(draft);
    const duplicates = duplicateModelIds(modelIds);
    if (duplicates.length > 0) {
      setError(`重複したmodel IDがあります: ${duplicates.join(", ")}`);
      return;
    }

    setBusy(true);
    setError("");
    setStatus("");
    try {
      const outcome = await saveAllowlistDraft(
        modelAllowlistApi,
        requestedTenantId,
        modelIds,
        baseline.revision,
        credential,
      );
      if (outcome.kind === "saved") {
        setBaseline(outcome.snapshot);
        setDraft(outcome.snapshot.modelIds.join("\n"));
        setStatus("allowlistを保存しました。");
        return;
      }
      setConflict(outcome);
      setStatus("別の管理者による更新を検出しました。現在値を再読込し、差分を表示しています。自動再送はしていません。");
    } catch (saveError) {
      setError(formatError(saveError));
    } finally {
      setBusy(false);
    }
  }

  function adoptCurrent() {
    if (!conflict) {
      return;
    }
    setBaseline(conflict.current);
    setDraft(conflict.current.modelIds.join("\n"));
    setConflict(null);
    setError("");
    setStatus("サーバーの現在値を編集内容として採用しました。");
  }

  function continueDraftFromCurrentRevision() {
    if (!conflict) {
      return;
    }
    setBaseline(conflict.current);
    setDraft(conflict.attemptedModelIds.join("\n"));
    setConflict(null);
    setError("");
    setStatus("現在revisionを新しい編集基準にしました。内容をもう一度確認し、保存する場合はSaveを押してください。");
  }

  return (
    <main style={{ maxWidth: 880, margin: "0 auto", padding: "2rem", fontFamily: "system-ui, sans-serif", lineHeight: 1.6 }}>
      <header>
        <p style={{ margin: 0, fontSize: "0.9rem" }}>KJ Atlas control plane</p>
        <h1 style={{ marginTop: "0.2rem" }}>Tenant model allowlist 管理</h1>
        <p>
          主キャンバスとは独立した管理画面です。保存は読み込んだrevisionに対してのみ行い、
          競合時は現在値を再読込して差分を確認するまで再送しません。
        </p>
      </header>

      <section aria-labelledby="target-heading" style={{ borderTop: "1px solid #bbb", paddingTop: "1rem" }}>
        <h2 id="target-heading">対象と認証</h2>
        <form onSubmit={loadCurrent}>
          <label style={{ display: "block", marginBottom: "0.8rem" }}>
            Tenant ID
            <input
              value={tenantId}
              onChange={(event) => {
                setTenantId(event.target.value);
                setBaseline(null);
                setConflict(null);
                setStatus("");
              }}
              style={{ display: "block", width: "100%", maxWidth: 560, padding: "0.5rem" }}
              autoComplete="off"
              data-testid="tenant-id"
            />
          </label>
          <label style={{ display: "block", marginBottom: "0.4rem" }}>
            Admin API key（Stage Aを使う場合のみ）
            <input
              type="password"
              value={adminApiKey}
              onChange={(event) => setAdminApiKey(event.target.value)}
              style={{ display: "block", width: "100%", maxWidth: 560, padding: "0.5rem" }}
              autoComplete="new-password"
              data-testid="admin-api-key"
            />
          </label>
          <p style={{ marginTop: 0, fontSize: "0.9rem" }}>
            Stage Bのtrusted sessionが使える場合は空欄で構いません。入力したkeyはアプリ側の永続ストレージへ保存しません。
          </p>
          <button type="submit" disabled={busy} data-testid="load-current">現在値を読み込む</button>
        </form>
      </section>

      {baseline && (
        <section aria-labelledby="edit-heading" style={{ borderTop: "1px solid #bbb", marginTop: "1.5rem", paddingTop: "1rem" }}>
          <h2 id="edit-heading">Allowlist編集</h2>
          <p>
            編集基準 revision: <code data-testid="baseline-revision">{baseline.revision}</code>
          </p>
          <label style={{ display: "block" }}>
            Model ID（1行に1件）
            <textarea
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              rows={12}
              style={{ display: "block", width: "100%", fontFamily: "ui-monospace, monospace", padding: "0.6rem" }}
              disabled={busy}
              data-testid="model-ids"
            />
          </label>
          <div style={{ marginTop: "0.8rem" }}>
            <button
              type="button"
              onClick={saveDraft}
              disabled={busy || conflict !== null}
              data-testid="save-allowlist"
            >
              Save
            </button>
          </div>
        </section>
      )}

      {conflict && (
        <section
          aria-labelledby="conflict-heading"
          role="alert"
          style={{ border: "2px solid currentColor", marginTop: "1.5rem", padding: "1rem" }}
          data-testid="conflict-panel"
        >
          <h2 id="conflict-heading">競合を検出しました</h2>
          <p>
            保存要求は再送していません。サーバーの現在revisionは
            <code data-testid="current-revision"> {conflict.current.revision}</code> です。
          </p>
          <div style={{ display: "grid", gap: "1rem", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
            <div data-testid="only-in-draft">
              <h3>自分のdraftだけにあるModel ID</h3>
              <ModelList values={conflict.diff.onlyInDraft} emptyLabel="差分はありません。" />
            </div>
            <div data-testid="only-on-server">
              <h3>現在のサーバーだけにあるModel ID</h3>
              <ModelList values={conflict.diff.onlyOnServer} emptyLabel="差分はありません。" />
            </div>
          </div>
          <p>どちらかを明示的に選ぶまでSaveは無効です。</p>
          <div style={{ display: "flex", gap: "0.8rem", flexWrap: "wrap" }}>
            <button type="button" onClick={adoptCurrent} data-testid="adopt-current">
              現在値を採用する
            </button>
            <button type="button" onClick={continueDraftFromCurrentRevision} data-testid="continue-draft">
              差分を確認し、現在revisionで編集を続ける
            </button>
          </div>
        </section>
      )}

      {status && <p role="status" data-testid="status-message">{status}</p>}
      {error && <p role="alert" data-testid="error-message">{error}</p>}
    </main>
  );
}
