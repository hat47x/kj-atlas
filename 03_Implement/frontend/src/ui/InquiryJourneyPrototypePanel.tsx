import { useEffect, useMemo, useRef, useState, type ChangeEvent } from "react";

import { ApiError, getInquiryBundle, putInquiryBundle } from "../api/client";

import {
  ROUND_STAGES,
  nextRoundIteration,
  type InquiryBundleV1,
  type RoundStage,
} from "../domain/inquiry_journey";
import {
  INQUIRY_BUNDLE_MAX_BYTES,
  INQUIRY_BUNDLE_WARNING_BYTES,
  serializeInquiryBundle,
} from "../domain/inquiry_bundle_io";
import { deriveInquiryRoundBundle } from "../domain/inquiry_bundle_projection";
import { prepareInquiryBundleForShare } from "../domain/inquiry_bundle_share";
import {
  buildInquiryHandoffReview,
  saveInquiryRoundHandoff,
  type InquiryHandoffReviewCandidate,
  type InquiryHandoffReviewDecision,
} from "../domain/inquiry_handoff_review";
import {
  buildInquiryResumeBrief,
  compareInquiryRounds,
  inquiryBundleOriginatesFromDocument,
  recordInquiryRound,
  startInquiryJourney,
  traceInquiryCardLineage,
} from "../domain/inquiry_journey_session";
import type { DocumentV1 } from "../domain/types";
import { downloadTextFile } from "../export/narrative_export";
import { t } from "../i18n/translate";
import { InquiryBundleWorkerClient } from "../worker/inquiry_bundle_client";
import { InquiryEndConfirmationDialog, type InquiryEndDecision } from "./InquiryEndConfirmationDialog";
import type { TenantSessionContextV1 } from "../api/session_context";

type InquiryJourneyPrototypePanelProps = {
  document: DocumentV1 | null;
  onRestoreDocument: (document: DocumentV1) => boolean;
  onDiscardRestoredDocument: () => boolean;
  runTenantScopedOptionalTask?: <T>(task: () => Promise<T>) => Promise<T | undefined>;
  runTenantScopedApiRequest?: <T>(request: () => Promise<T>) => Promise<T>;
  verifiedTenantSession?: TenantSessionContextV1;
};

const runWithoutTenantScope = <T,>(task: () => Promise<T>): Promise<T> => task();

type BranchUndoCheckpoint = {
  bundle: InquiryBundleV1;
  restoredDocument: DocumentV1;
};

type InquiryHandoffReviewPanelProps = {
  candidates: InquiryHandoffReviewCandidate[];
  onSave: (candidates: InquiryHandoffReviewCandidate[]) => void;
};

function stageLabel(stage: RoundStage): string {
  return t(`inquiry_journey.stage.${stage}`);
}

function fileStem(value: string): string {
  const sanitized = value.trim().replace(/[\\/:*?"<>|]+/g, "-").replace(/\s+/g, "-");
  return sanitized || "inquiry";
}

function handoffCandidateQuestion(candidate: InquiryHandoffReviewCandidate): string {
  if (candidate.kind === "artifact") {
    return t("inquiry_journey.prototype.handoff_artifact_question", {
      kind: t(`inquiry_journey.prototype.handoff_artifact_kind.${candidate.artifactKind}`),
    });
  }
  return t(`inquiry_journey.prototype.handoff_question.${candidate.kind}`);
}

function InquiryHandoffReviewPanel({ candidates: initialCandidates, onSave }: InquiryHandoffReviewPanelProps) {
  const candidateRef = useRef<HTMLElement | null>(null);
  const addedCandidateCountRef = useRef(0);
  const [candidates, setCandidates] = useState(() => structuredClone(initialCandidates));
  const [currentIndex, setCurrentIndex] = useState(0);
  const current = candidates[currentIndex];

  useEffect(() => {
    candidateRef.current?.focus();
  }, [currentIndex]);

  if (!current) return null;

  const updateCurrent = (update: (candidate: InquiryHandoffReviewCandidate) => InquiryHandoffReviewCandidate) => {
    setCandidates((previous) => previous.map((candidate, index) => (
      index === currentIndex ? update(candidate) : candidate
    )));
  };
  const decide = (decision: InquiryHandoffReviewDecision) => {
    updateCurrent((candidate) => candidate.kind === "artifact"
      ? { ...candidate, decision }
      : { ...candidate, decision: decision === "held" ? "pending" : decision });
    if (currentIndex < candidates.length - 1) setCurrentIndex((index) => index + 1);
  };
  const addTextCandidate = (kind: "unresolved_question" | "fieldwork_request") => {
    addedCandidateCountRef.current += 1;
    const nextCandidate: InquiryHandoffReviewCandidate = {
      candidateId: `${kind}:added:${addedCandidateCountRef.current}`,
      kind,
      value: "",
      originalValue: "",
      decision: "pending",
    };
    setCandidates((previous) => [...previous, nextCandidate]);
    setCurrentIndex(candidates.length);
  };
  const isEdited = current.kind !== "artifact" && current.value !== current.originalValue;
  const canAdopt = current.kind === "artifact" || Boolean(current.value.trim());

  return (
    <details>
      <summary style={{ cursor: "pointer", fontSize: 12, fontWeight: 700 }}>
        {t("inquiry_journey.prototype.handoff_review")}
      </summary>
      <fieldset
        aria-label={t("inquiry_journey.prototype.handoff_review")}
        style={{ display: "grid", gap: 8, margin: "8px 0 0", padding: 10, border: "1px solid #cbd5e1", minWidth: 0 }}
      >
        <div style={{ fontSize: 11, color: "#475569" }}>
          {t("inquiry_journey.prototype.handoff_optional")}
        </div>
        <div style={{ fontSize: 11, color: "#475569" }}>
          {t("inquiry_journey.prototype.handoff_position", {
            current: currentIndex + 1,
            total: candidates.length,
          })}
        </div>
        <section
          ref={candidateRef}
          tabIndex={-1}
          aria-label={handoffCandidateQuestion(current)}
          style={{ display: "grid", gap: 8, minWidth: 0, padding: 8, borderInlineStart: "3px solid #64748b" }}
        >
          <strong style={{ fontSize: 12 }}>{handoffCandidateQuestion(current)}</strong>
          {current.kind === "artifact" ? (
            <div style={{ fontSize: 12, overflowWrap: "anywhere" }}>{current.label}</div>
          ) : (
            <label style={{ display: "grid", gap: 4, minWidth: 0, fontSize: 12 }}>
              {t(`inquiry_journey.prototype.handoff_input.${current.kind}`)}
              <textarea
                value={current.value}
                rows={3}
                onChange={(event) => {
                  const value = event.currentTarget.value;
                  updateCurrent((candidate) => candidate.kind === "artifact"
                    ? candidate
                    : { ...candidate, value, decision: "pending" });
                }}
                style={{ boxSizing: "border-box", width: "100%", minWidth: 0, resize: "vertical" }}
              />
            </label>
          )}
          <div role="status" aria-live="polite" style={{ fontSize: 11, color: "#475569" }}>
            {t(`inquiry_journey.prototype.handoff_decision.${current.decision}`)}
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            <button type="button" disabled={!canAdopt} onClick={() => decide("adopted")}>
              {t(isEdited
                ? "inquiry_journey.prototype.handoff_adopt_edited"
                : "inquiry_journey.prototype.handoff_adopt")}
            </button>
            {current.kind === "artifact" ? (
              <button type="button" onClick={() => decide("held")}>
                {t("inquiry_journey.prototype.handoff_hold")}
              </button>
            ) : null}
            <button type="button" onClick={() => decide("skipped")}>
              {t("inquiry_journey.prototype.handoff_skip")}
            </button>
          </div>
        </section>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 8 }}>
          <button
            type="button"
            disabled={currentIndex === 0}
            onClick={() => setCurrentIndex((index) => Math.max(0, index - 1))}
            style={{ whiteSpace: "normal" }}
          >
            {t("inquiry_journey.prototype.handoff_previous")}
          </button>
          <button
            type="button"
            disabled={currentIndex === candidates.length - 1}
            onClick={() => setCurrentIndex((index) => Math.min(candidates.length - 1, index + 1))}
            style={{ whiteSpace: "normal" }}
          >
            {t("inquiry_journey.prototype.handoff_next")}
          </button>
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
          <button type="button" onClick={() => addTextCandidate("unresolved_question")}>
            {t("inquiry_journey.prototype.handoff_add_unresolved")}
          </button>
          <button type="button" onClick={() => addTextCandidate("fieldwork_request")}>
            {t("inquiry_journey.prototype.handoff_add_fieldwork")}
          </button>
        </div>
        <button type="button" onClick={() => onSave(candidates)}>
          {t("inquiry_journey.prototype.handoff_save")}
        </button>
      </fieldset>
    </details>
  );
}

export function InquiryJourneyPrototypePanel({
  document,
  onRestoreDocument,
  onDiscardRestoredDocument,
  runTenantScopedOptionalTask = runWithoutTenantScope,
  runTenantScopedApiRequest = runWithoutTenantScope,
  verifiedTenantSession,
}: InquiryJourneyPrototypePanelProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const importClientRef = useRef<InquiryBundleWorkerClient | null>(null);
  const importAbortRef = useRef<AbortController | null>(null);
  // DATA-INQUIRY-CONCURRENCY-01 (案A): the server-owned revision observed on
  // the last load/save, sent back as If-Match on the next save.
  const backendEtagRef = useRef<string | undefined>(undefined);
  const resumePreviewRef = useRef<HTMLElement | null>(null);
  const [bundle, setBundle] = useState<InquiryBundleV1 | null>(null);
  const [selectedStage, setSelectedStage] = useState<RoundStage>("r1_problem_setting");
  const [isBusy, setIsBusy] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [isConfirmingEnd, setIsConfirmingEnd] = useState(false);
  const [recordParentRoundId, setRecordParentRoundId] = useState("");
  const [comparisonFromRoundId, setComparisonFromRoundId] = useState("");
  const [comparisonToRoundId, setComparisonToRoundId] = useState("");
  const [exportRoundId, setExportRoundId] = useState("");
  const [lineageCardId, setLineageCardId] = useState("");
  const [resumePreviewSnapshotId, setResumePreviewSnapshotId] = useState("");
  const [branchUndoCheckpoint, setBranchUndoCheckpoint] = useState<BranchUndoCheckpoint | null>(null);
  const [message, setMessage] = useState<{ kind: "status" | "error"; text: string } | null>(null);

  useEffect(() => {
    const activeImport = importAbortRef.current;
    importAbortRef.current = null;
    activeImport?.abort();
    setBundle(null);
    setSelectedStage("r1_problem_setting");
    setIsConfirmingEnd(false);
    setRecordParentRoundId("");
    setComparisonFromRoundId("");
    setComparisonToRoundId("");
    setExportRoundId("");
    setLineageCardId("");
    setResumePreviewSnapshotId("");
    setBranchUndoCheckpoint(null);
    setMessage(null);
  }, [document?.id]);

  useEffect(() => () => {
    const activeImport = importAbortRef.current;
    importAbortRef.current = null;
    activeImport?.abort();
    importClientRef.current?.dispose();
  }, []);

  useEffect(() => {
    if (!resumePreviewSnapshotId) return;
    resumePreviewRef.current?.focus();
  }, [resumePreviewSnapshotId]);

  const records = bundle?.journey.roundRecords ?? [];
  const documentLabel = document?.title?.trim() || document?.id || t("inquiry_journey.prototype.no_document");
  const effectiveRecordParentId = records.some((record) => record.roundId === recordParentRoundId)
    ? recordParentRoundId
    : bundle?.journey.defaultHeadRoundId ?? "";
  const nextIteration = useMemo(
    () => bundle
      ? nextRoundIteration(
          bundle.journey,
          selectedStage,
          effectiveRecordParentId ? [effectiveRecordParentId] : []
        )
      : 1,
    [bundle, effectiveRecordParentId, selectedStage]
  );
  const isStarted = bundle !== null;
  const isBranching = Boolean(
    effectiveRecordParentId && effectiveRecordParentId !== bundle?.journey.defaultHeadRoundId
  );
  const defaultComparisonFromId = records.at(-2)?.roundId ?? "";
  const defaultComparisonToId = records.at(-1)?.roundId ?? "";
  const effectiveComparisonFromId = records.some((record) => record.roundId === comparisonFromRoundId)
    ? comparisonFromRoundId
    : defaultComparisonFromId;
  const effectiveComparisonToId = records.some((record) => record.roundId === comparisonToRoundId)
    ? comparisonToRoundId
    : defaultComparisonToId;
  const effectiveExportRoundId = records.some((record) => record.roundId === exportRoundId)
    ? exportRoundId
    : "";
  const comparison = useMemo(
    () => bundle && effectiveComparisonFromId && effectiveComparisonToId
      ? compareInquiryRounds(bundle, effectiveComparisonFromId, effectiveComparisonToId)
      : null,
    [bundle, effectiveComparisonFromId, effectiveComparisonToId]
  );
  const resumeBrief = useMemo(
    () => bundle ? buildInquiryResumeBrief(bundle) : null,
    [bundle]
  );
  const handoffReview = useMemo(
    () => bundle ? buildInquiryHandoffReview(bundle) : null,
    [bundle]
  );
  const selectedResumeResult = resumeBrief?.ok
    ? resumeBrief.brief.previousResults.find((result) => result.snapshotId === resumePreviewSnapshotId)
    : undefined;
  const lineageRound = records.find((record) => record.roundId === bundle?.journey.defaultHeadRoundId);
  const lineageSnapshot = bundle?.snapshots.find((snapshot) => snapshot.snapshotId === lineageRound?.outputSnapshotId);
  const lineageCards = lineageSnapshot?.document.cards ?? [];
  const effectiveLineageCardId = lineageCards.some((card) => card.id === lineageCardId)
    ? lineageCardId
    : lineageCards.find((card) => card.claimType === "hypothesis")?.id ?? lineageCards[0]?.id ?? "";
  const lineageTrace = useMemo(
    () => bundle && lineageSnapshot && effectiveLineageCardId
      ? traceInquiryCardLineage(bundle, {
          snapshotId: lineageSnapshot.snapshotId,
          cardId: effectiveLineageCardId,
        })
      : null,
    [bundle, effectiveLineageCardId, lineageSnapshot]
  );
  const canUndoBranch = useMemo(
    () => Boolean(
      document
      && branchUndoCheckpoint
      && JSON.stringify(document) === JSON.stringify(branchUndoCheckpoint.restoredDocument)
    ),
    [branchUndoCheckpoint, document]
  );

  const recordLabel = (roundId: string): string => {
    const record = records.find((candidate) => candidate.roundId === roundId);
    return record
      ? t("inquiry_journey.prototype.recorded", {
          stage: stageLabel(record.stage),
          iteration: record.iteration,
        })
      : roundId;
  };

  const handleStart = async () => {
    if (!document) return;
    setIsBusy(true);
    setMessage(null);
    try {
      setBundle(await startInquiryJourney(document));
      setResumePreviewSnapshotId("");
      setBranchUndoCheckpoint(null);
    } finally {
      setIsBusy(false);
    }
  };

  const handleRecord = async () => {
    if (!bundle || !document) return;
    setIsBusy(true);
    setMessage(null);
    try {
      const branchParent = isBranching
        ? bundle.journey.roundRecords.find((record) => record.roundId === effectiveRecordParentId)
        : undefined;
      const branchSnapshot = branchParent
        ? bundle.snapshots.find((snapshot) => snapshot.snapshotId === branchParent.outputSnapshotId)
        : undefined;
      if (isBranching && !branchSnapshot) {
        setMessage({ kind: "error", text: t("inquiry_journey.prototype.branch_error") });
        return;
      }
      const result = await recordInquiryRound(
        bundle,
        branchSnapshot?.document ?? document,
        selectedStage,
        effectiveRecordParentId ? { parentRoundId: effectiveRecordParentId } : {}
      );
      if (!result.ok) {
        setMessage({ kind: "error", text: t("inquiry_journey.prototype.record_error") });
        return;
      }
      if (branchSnapshot && !onRestoreDocument(structuredClone(branchSnapshot.document))) {
        setMessage({ kind: "error", text: t("inquiry_journey.prototype.branch_error") });
        return;
      }
      if (branchSnapshot) {
        setBranchUndoCheckpoint({
          bundle,
          restoredDocument: structuredClone(branchSnapshot.document),
        });
      }
      setBundle(result.bundle);
      setRecordParentRoundId("");
      if (branchSnapshot) {
        setMessage({ kind: "status", text: t("inquiry_journey.prototype.branch_created") });
      }
    } finally {
      setIsBusy(false);
    }
  };

  const handleUndoBranch = () => {
    if (!branchUndoCheckpoint || !canUndoBranch) return;
    if (!onDiscardRestoredDocument()) {
      setMessage({ kind: "error", text: t("inquiry_journey.prototype.branch_undo_error") });
      return;
    }
    setBundle(branchUndoCheckpoint.bundle);
    setBranchUndoCheckpoint(null);
    setRecordParentRoundId("");
    setComparisonFromRoundId("");
    setComparisonToRoundId("");
    setResumePreviewSnapshotId("");
    setMessage({ kind: "status", text: t("inquiry_journey.prototype.branch_undone") });
  };

  const handleSaveHandoff = (candidates: InquiryHandoffReviewCandidate[]) => {
    if (!bundle || !handoffReview?.ok) return;
    const result = saveInquiryRoundHandoff(bundle, handoffReview.roundId, candidates);
    if (!result.ok) {
      setMessage({ kind: "error", text: t("inquiry_journey.prototype.handoff_save_error") });
      return;
    }
    setBundle(result.bundle);
    setMessage({
      kind: "status",
      text: t(result.unansweredCount > 0
        ? "inquiry_journey.prototype.handoff_saved_partial"
        : "inquiry_journey.prototype.handoff_saved"),
    });
  };

  const handleExport = async (): Promise<boolean> => {
    if (!bundle) return false;
    setIsBusy(true);
    setMessage(null);
    try {
      const projection = effectiveExportRoundId
        ? deriveInquiryRoundBundle(bundle, effectiveExportRoundId)
        : { ok: true as const, bundle };
      if (!projection.ok) {
        setMessage({
          kind: "error",
          text: t(
            projection.reason === "dependency_outside_scope"
              ? "inquiry_journey.prototype.export_scope_dependency"
              : "inquiry_journey.prototype.export_error"
          ),
        });
        return false;
      }
      const serialized = await serializeInquiryBundle(projection.bundle);
      if (!serialized.ok) {
        setMessage({
          kind: "error",
          text: t(
            serialized.errors.some((error) => error.code === "payload_too_large")
              ? "inquiry_journey.prototype.export_too_large"
              : "inquiry_journey.prototype.export_error"
          ),
        });
        return false;
      }
      const scopeSuffix = effectiveExportRoundId ? `-${fileStem(effectiveExportRoundId)}` : "";
      downloadTextFile(
        `${fileStem(bundle.journey.title)}${scopeSuffix}.kj-atlas-inquiry.json`,
        "application/json",
        serialized.json
      );
      setMessage({
        kind: "status",
        text: t(effectiveExportRoundId
          ? "inquiry_journey.prototype.exported_round"
          : "inquiry_journey.prototype.exported"),
      });
      return true;
    } finally {
      setIsBusy(false);
    }
  };

  // G5 (W型 single-tenant 化): persist the serialized inquiry bundle to the
  // backend, keyed by journey.journeyId, instead of only downloading a file.
  const handleSaveToBackend = async (): Promise<void> => {
    if (!bundle || !document) return;
    setIsBusy(true);
    setMessage({ kind: "status", text: t("inquiry_journey.prototype.saving_backend") });
    try {
      const serialized = await serializeInquiryBundle(bundle);
      if (!serialized.ok) {
        setMessage({ kind: "error", text: t("inquiry_journey.prototype.export_error") });
        return;
      }
      // DATA-INQUIRY-CONCURRENCY-01 (案A): save carries the last server-owned
      // revision as If-Match, or If-None-Match: * when this journey was never
      // persisted here, so a stale client can never overwrite newer work.
      const precondition = backendEtagRef.current
        ? { etag: backendEtagRef.current }
        : { createIfAbsent: true };
      const newEtag = await runTenantScopedApiRequest(() => putInquiryBundle(
        bundle.journey.journeyId,
        JSON.parse(serialized.json),
        { tenantSessionContext: verifiedTenantSession },
        precondition,
      ));
      if (newEtag) {
        backendEtagRef.current = newEtag;
      }
      setMessage({ kind: "status", text: t("inquiry_journey.prototype.saved_backend") });
    } catch (error) {
      // AC-6: a 409 is a real conflict — never auto-retry/merge into the newer
      // bundle and never treat the stale save as successful.
      if (error instanceof ApiError && error.status === 409) {
        setMessage({ kind: "error", text: t("inquiry_journey.prototype.conflict_backend") });
        return;
      }
      setMessage({ kind: "error", text: t("inquiry_journey.prototype.backend_error") });
    } finally {
      setIsBusy(false);
    }
  };

  const handleShareExport = async (): Promise<void> => {
    if (!bundle) return;
    setIsBusy(true);
    setMessage(null);
    try {
      const shared = await prepareInquiryBundleForShare(
        bundle,
        effectiveExportRoundId || undefined,
      );
      if (!shared.ok) {
        setMessage({
          kind: "error",
          text: t(
            shared.reason === "dependency_outside_scope"
              ? "inquiry_journey.prototype.export_scope_dependency"
              : "inquiry_journey.prototype.share_export_error",
          ),
        });
        return;
      }
      const scopeSuffix = effectiveExportRoundId ? `-${fileStem(effectiveExportRoundId)}` : "";
      downloadTextFile(
        `${fileStem(bundle.journey.title)}${scopeSuffix}.safe-share.kj-atlas-inquiry.json`,
        "application/json",
        shared.json,
      );
      setMessage({
        kind: "status",
        text: t(effectiveExportRoundId
          ? "inquiry_journey.prototype.share_exported_round"
          : "inquiry_journey.prototype.share_exported"),
      });
    } finally {
      setIsBusy(false);
    }
  };

  // DOMAIN-W-ITERATION-01 AC-13 / T10: 3-choice end confirmation (save/
  // discard/cancel), matching A-1's TenantChangeConfirmationDialog pattern.
  // "save" only clears the on-screen inquiry once export actually succeeds
  // (handleExport's own error message stays visible and the dialog remains
  // open otherwise, so a failed save never silently discards the bundle).
  const handleEndConfirmationDecision = async (decision: InquiryEndDecision) => {
    if (decision === "cancel") {
      setIsConfirmingEnd(false);
      return;
    }
    if (decision === "save") {
      const exported = await handleExport();
      if (!exported) return;
    }
    setBundle(null);
    setBranchUndoCheckpoint(null);
    setMessage(null);
    setIsConfirmingEnd(false);
    setRecordParentRoundId("");
    setComparisonFromRoundId("");
    setComparisonToRoundId("");
    setExportRoundId("");
    setLineageCardId("");
    setResumePreviewSnapshotId("");
  };

  const handleImport = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.currentTarget.files?.[0];
    event.currentTarget.value = "";
    if (!file || !document) return;
    if (file.size > INQUIRY_BUNDLE_MAX_BYTES) {
      setMessage({ kind: "error", text: t("inquiry_journey.prototype.import_too_large") });
      return;
    }
    const controller = new AbortController();
    importAbortRef.current = controller;
    setIsBusy(true);
    setIsImporting(true);
    setMessage({
      kind: "status",
      text: t(
        file.size > INQUIRY_BUNDLE_WARNING_BYTES
          ? "inquiry_journey.prototype.importing_large"
          : "inquiry_journey.prototype.importing"
      ),
    });
    try {
      importClientRef.current ??= new InquiryBundleWorkerClient();
      const importClient = importClientRef.current;
      const outcome = await runTenantScopedOptionalTask(async () => (
        importClient.parse(await file.text(), { signal: controller.signal })
      ));
      if (outcome === undefined) {
        return;
      }
      if (outcome.status === "cancelled") {
        if (importAbortRef.current === controller) {
          setMessage({ kind: "status", text: t("inquiry_journey.prototype.import_cancelled") });
        }
        return;
      }
      const parsed = outcome.result;
      if (!parsed.ok) {
        setMessage({ kind: "error", text: t("inquiry_journey.prototype.import_error") });
        return;
      }
      if (!inquiryBundleOriginatesFromDocument(parsed.bundle, document.id)) {
        setMessage({ kind: "error", text: t("inquiry_journey.prototype.origin_mismatch") });
        return;
      }
      setBundle(parsed.bundle);
      setIsConfirmingEnd(false);
      setRecordParentRoundId("");
      setComparisonFromRoundId("");
      setComparisonToRoundId("");
      setExportRoundId("");
      setLineageCardId("");
      setResumePreviewSnapshotId("");
      setBranchUndoCheckpoint(null);
      setSelectedStage(parsed.bundle.journey.roundRecords.at(-1)?.stage ?? "r1_problem_setting");
      setMessage({ kind: "status", text: t("inquiry_journey.prototype.imported") });
    } finally {
      if (importAbortRef.current === controller) importAbortRef.current = null;
      setIsBusy(false);
      setIsImporting(false);
    }
  };

  // G5: reload the current journey's bundle from the backend (same journeyId),
  // so a persisted journey survives a page reload / session restart.
  const handleLoadFromBackend = async (): Promise<void> => {
    if (!bundle || !document) return;
    setIsBusy(true);
    setIsImporting(true);
    setMessage({ kind: "status", text: t("inquiry_journey.prototype.loading_backend") });
    try {
      importClientRef.current ??= new InquiryBundleWorkerClient();
      const importClient = importClientRef.current;
      const stored = await runTenantScopedApiRequest(() => getInquiryBundle(
        bundle.journey.journeyId,
        { tenantSessionContext: verifiedTenantSession },
      ));
      // DATA-INQUIRY-CONCURRENCY-01 (案A): remember the server-owned revision
      // so the next save carries it back as If-Match.
      backendEtagRef.current = stored.etag;
      const parsed = await runTenantScopedOptionalTask(async () => (
        importClient.parse(JSON.stringify(stored.payload))
      ));
      if (parsed === undefined || parsed.status === "cancelled") {
        return;
      }
      if (!parsed.result.ok) {
        setMessage({ kind: "error", text: t("inquiry_journey.prototype.import_error") });
        return;
      }
      if (!inquiryBundleOriginatesFromDocument(parsed.result.bundle, document.id)) {
        setMessage({ kind: "error", text: t("inquiry_journey.prototype.origin_mismatch") });
        return;
      }
      setBundle(parsed.result.bundle);
      setMessage({ kind: "status", text: t("inquiry_journey.prototype.loaded_backend") });
    } catch {
      setMessage({ kind: "error", text: t("inquiry_journey.prototype.backend_error") });
    } finally {
      setIsBusy(false);
      setIsImporting(false);
    }
  };

  return (
    <section data-panel="inquiry-journey-prototype" style={{ display: "grid", gap: 10 }}>
      <div style={{ fontSize: 12, fontWeight: 700 }}>{t("inquiry_journey.prototype.title")}</div>
      <div style={{ fontSize: 12, color: "#334155" }}>
        {t("inquiry_journey.prototype.origin", {
          title: documentLabel,
          cards: document?.cards.length ?? 0,
        })}
      </div>

      {!isStarted ? (
        <div style={{ display: "grid", gap: 8 }}>
          <button
            type="button"
            data-domain-action="start-inquiry-journey-prototype"
            disabled={!document || isBusy}
            onClick={() => void handleStart()}
          >
            {t("inquiry_journey.prototype.start")}
          </button>
          <button type="button" disabled={!document || isBusy} onClick={() => inputRef.current?.click()}>
            {t("inquiry_journey.prototype.import")}
          </button>
        </div>
      ) : (
        <>
          <div role="status" style={{ fontSize: 11, color: "#92400e" }}>
            {t("inquiry_journey.prototype.session_only")}
          </div>
          {records.length > 0 ? (
            <>
              <label style={{ display: "grid", gap: 4, fontSize: 12 }}>
                {t("inquiry_journey.prototype.record_parent")}
                <select
                  data-domain-input="inquiry-journey-parent-round"
                  value={effectiveRecordParentId}
                  onChange={(event) => setRecordParentRoundId(event.currentTarget.value)}
                >
                  {records.map((record) => (
                    <option key={record.roundId} value={record.roundId}>
                      {record.roundId === bundle.journey.defaultHeadRoundId
                        ? t("inquiry_journey.prototype.record_parent_current", {
                            record: recordLabel(record.roundId),
                          })
                        : recordLabel(record.roundId)}
                    </option>
                  ))}
                </select>
              </label>
              {isBranching ? (
                <div role="status" aria-live="polite" style={{ fontSize: 11, color: "#92400e" }}>
                  {t("inquiry_journey.prototype.branch_notice")}
                </div>
              ) : null}
            </>
          ) : null}

          <label style={{ display: "grid", gap: 4, fontSize: 12 }}>
            {t("inquiry_journey.prototype.stage")}
            <select
              data-domain-input="inquiry-journey-stage"
              value={selectedStage}
              onChange={(event) => setSelectedStage(event.currentTarget.value as RoundStage)}
            >
              {ROUND_STAGES.map((stage) => (
                <option key={stage} value={stage}>{stageLabel(stage)}</option>
              ))}
            </select>
          </label>
          <button
            type="button"
            data-domain-action="record-inquiry-round-prototype"
            disabled={isBusy}
            onClick={() => void handleRecord()}
          >
            {t(isBranching
              ? "inquiry_journey.prototype.record_branch"
              : "inquiry_journey.prototype.record", {
              stage: stageLabel(selectedStage),
              iteration: nextIteration,
            })}
          </button>
          {canUndoBranch ? (
            <button
              type="button"
              data-domain-action="undo-inquiry-branch"
              disabled={isBusy}
              onClick={handleUndoBranch}
            >
              {t("inquiry_journey.prototype.branch_undo")}
            </button>
          ) : null}

          {records.length > 0 ? (
            <ol aria-label={t("inquiry_journey.prototype.history")} style={{ margin: 0, paddingInlineStart: 24, fontSize: 12 }}>
              {records.map((record) => (
                <li key={record.roundId}>
                  {t("inquiry_journey.prototype.recorded", {
                    stage: stageLabel(record.stage),
                    iteration: record.iteration,
                  })}
                </li>
              ))}
            </ol>
          ) : null}

          {handoffReview?.ok ? (
            <InquiryHandoffReviewPanel
              key={`${handoffReview.roundId}:${records.find((record) => record.roundId === handoffReview.roundId)?.updatedAt ?? ""}`}
              candidates={handoffReview.candidates}
              onSave={handleSaveHandoff}
            />
          ) : null}

          {resumeBrief?.ok ? (
            <details>
              <summary style={{ cursor: "pointer", fontSize: 12, fontWeight: 700 }}>
                {t("inquiry_journey.prototype.resume_brief")}
              </summary>
              <fieldset
                aria-label={t("inquiry_journey.prototype.resume_brief")}
                style={{ display: "grid", gap: 8, margin: "8px 0 0", padding: 10, border: "1px solid #cbd5e1", minWidth: 0 }}
              >
                <div style={{ fontSize: 12, overflowWrap: "anywhere" }}>
                  <strong>{t("inquiry_journey.prototype.resume_stage")}</strong>{" "}
                  {t("inquiry_journey.prototype.recorded", {
                    stage: stageLabel(resumeBrief.brief.round.stage),
                    iteration: resumeBrief.brief.round.iteration,
                  })}
                </div>
                <div style={{ fontSize: 12, overflowWrap: "anywhere" }}>
                  <strong>{t("inquiry_journey.prototype.resume_question")}</strong>{" "}
                  {resumeBrief.brief.question}
                </div>
                {resumeBrief.brief.understandingDelta ? (
                  <div style={{ fontSize: 12, overflowWrap: "anywhere" }}>
                    <strong>{t("inquiry_journey.prototype.resume_understanding")}</strong>{" "}
                    {resumeBrief.brief.understandingDelta}
                  </div>
                ) : null}
                {resumeBrief.brief.unresolvedQuestions.length > 0 ? (
                  <div style={{ display: "grid", gap: 4, minWidth: 0 }}>
                    <strong style={{ fontSize: 12 }}>{t("inquiry_journey.prototype.resume_unresolved")}</strong>
                    <ul style={{ margin: 0, paddingInlineStart: 24, fontSize: 12 }}>
                      {resumeBrief.brief.unresolvedQuestions.map((question, index) => (
                        <li key={`${index}:${question}`} style={{ overflowWrap: "anywhere" }}>{question}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}
                {resumeBrief.brief.nextActions.length > 0 ? (
                  <div style={{ display: "grid", gap: 4, minWidth: 0 }}>
                    <strong style={{ fontSize: 12 }}>{t("inquiry_journey.prototype.resume_next_actions")}</strong>
                    <ul style={{ margin: 0, paddingInlineStart: 24, fontSize: 12 }}>
                      {resumeBrief.brief.nextActions.map((action, index) => (
                        <li key={`${index}:${action}`} style={{ overflowWrap: "anywhere" }}>{action}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}
                {resumeBrief.brief.previousResults.map((result) => (
                  <button
                    key={result.snapshotId}
                    type="button"
                    onClick={() => setResumePreviewSnapshotId(result.snapshotId)}
                    style={{ minWidth: 0, whiteSpace: "normal", overflowWrap: "anywhere" }}
                  >
                    {t("inquiry_journey.prototype.resume_open_result", { title: result.title })}
                  </button>
                ))}
                {selectedResumeResult ? (
                  <section
                    ref={resumePreviewRef}
                    tabIndex={-1}
                    aria-label={t("inquiry_journey.prototype.resume_result_preview")}
                    style={{ display: "grid", gap: 6, minWidth: 0, padding: 8, borderInlineStart: "3px solid #64748b" }}
                  >
                    <strong style={{ fontSize: 12, overflowWrap: "anywhere" }}>
                      {t("inquiry_journey.prototype.resume_result_title", { title: selectedResumeResult.title })}
                    </strong>
                    <div style={{ fontSize: 11, color: "#475569" }}>
                      {t("inquiry_journey.prototype.resume_read_only")}
                    </div>
                    <ul style={{ display: "grid", gap: 4, margin: 0, paddingInlineStart: 24, fontSize: 12 }}>
                      {selectedResumeResult.cards.map((card) => (
                        <li key={card.id} style={{ overflowWrap: "anywhere" }}>
                          <div>{card.text}</div>
                          {card.source ? <div>{t("inquiry_journey.prototype.lineage_source", { source: card.source })}</div> : null}
                        </li>
                      ))}
                    </ul>
                  </section>
                ) : null}
              </fieldset>
            </details>
          ) : null}

          {lineageCards.length > 0 ? (
            <details>
              <summary style={{ cursor: "pointer", fontSize: 12, fontWeight: 700 }}>
                {t("inquiry_journey.prototype.lineage")}
              </summary>
              <fieldset
                aria-label={t("inquiry_journey.prototype.lineage")}
                style={{ display: "grid", gap: 8, margin: "8px 0 0", padding: 10, border: "1px solid #cbd5e1", minWidth: 0 }}
              >
                <label style={{ display: "grid", gap: 4, minWidth: 0, fontSize: 12 }}>
                  {t("inquiry_journey.prototype.lineage_card")}
                  <select value={effectiveLineageCardId} onChange={(event) => setLineageCardId(event.currentTarget.value)}>
                    {lineageCards.map((card) => <option key={card.id} value={card.id}>{card.text}</option>)}
                  </select>
                </label>
                {lineageTrace?.ok ? (
                  <>
                    <div style={{ fontSize: 12, overflowWrap: "anywhere" }}>
                      <strong>{t("inquiry_journey.prototype.lineage_selected")}</strong> {lineageTrace.target.text}
                      {lineageTrace.target.source ? (
                        <div>{t("inquiry_journey.prototype.lineage_source", { source: lineageTrace.target.source })}</div>
                      ) : null}
                    </div>
                    {lineageTrace.ancestors.length > 0 ? (
                      <ol aria-label={t("inquiry_journey.prototype.lineage_ancestors")} style={{ display: "grid", gap: 6, margin: 0, paddingInlineStart: 24, fontSize: 12 }}>
                        {lineageTrace.ancestors.map((node) => (
                          <li key={`${node.address.snapshotId}:${node.address.cardId}`} style={{ overflowWrap: "anywhere" }}>
                            <div>
                              {node.round
                                ? t("inquiry_journey.prototype.lineage_round", {
                                    record: t("inquiry_journey.prototype.recorded", {
                                      stage: stageLabel(node.round.stage),
                                      iteration: node.round.iteration,
                                    }),
                                  })
                                : t("inquiry_journey.prototype.lineage_origin")}
                              {node.viaKind ? ` / ${t(`inquiry_journey.prototype.lineage_kind.${node.viaKind}`)}` : ""}
                            </div>
                            <div>{node.text}</div>
                            {node.source ? <div>{t("inquiry_journey.prototype.lineage_source", { source: node.source })}</div> : null}
                          </li>
                        ))}
                      </ol>
                    ) : (
                      <div role="status" style={{ fontSize: 12 }}>{t("inquiry_journey.prototype.lineage_no_ancestors")}</div>
                    )}
                  </>
                ) : null}
              </fieldset>
            </details>
          ) : null}

          {records.length >= 2 ? (
            <fieldset style={{ display: "grid", gap: 8, margin: 0, padding: 10, border: "1px solid #cbd5e1" }}>
              <legend style={{ paddingInline: 4, fontSize: 12, fontWeight: 700 }}>
                {t("inquiry_journey.prototype.comparison")}
              </legend>
              <label style={{ display: "grid", gap: 4, fontSize: 12 }}>
                {t("inquiry_journey.prototype.comparison_from")}
                <select
                  value={effectiveComparisonFromId}
                  onChange={(event) => setComparisonFromRoundId(event.currentTarget.value)}
                >
                  {records.map((record) => (
                    <option key={record.roundId} value={record.roundId}>{recordLabel(record.roundId)}</option>
                  ))}
                </select>
              </label>
              <label style={{ display: "grid", gap: 4, fontSize: 12 }}>
                {t("inquiry_journey.prototype.comparison_to")}
                <select
                  value={effectiveComparisonToId}
                  onChange={(event) => setComparisonToRoundId(event.currentTarget.value)}
                >
                  {records.map((record) => (
                    <option key={record.roundId} value={record.roundId}>{recordLabel(record.roundId)}</option>
                  ))}
                </select>
              </label>
              <div role="status" aria-live="polite" style={{ fontSize: 12, color: "#334155" }}>
                {comparison?.ok
                  ? t("inquiry_journey.prototype.comparison_summary", {
                      cards: comparison.summary.cards,
                      islands: comparison.summary.islands,
                      relations: comparison.summary.relationSummaries,
                      readingOrder: t(
                        comparison.summary.readingOrderChanged
                          ? "inquiry_journey.prototype.comparison_changed"
                          : "inquiry_journey.prototype.comparison_unchanged"
                      ),
                    })
                  : t("inquiry_journey.prototype.comparison_error")}
              </div>
            </fieldset>
          ) : null}

          <fieldset
            data-testid="inquiry-export-scope"
            style={{ display: "grid", gap: 8, margin: 0, padding: 10, border: "1px solid #cbd5e1" }}
          >
            <legend style={{ paddingInline: 4, fontSize: 12, fontWeight: 700 }}>
              {t("inquiry_journey.prototype.export_scope")}
            </legend>
            <label style={{ display: "grid", gap: 4, fontSize: 12 }}>
              {t("inquiry_journey.prototype.export_scope_label")}
              <select
                value={effectiveExportRoundId}
                onChange={(event) => setExportRoundId(event.currentTarget.value)}
              >
                <option value="">{t("inquiry_journey.prototype.export_scope_all")}</option>
                {records.map((record) => (
                  <option key={record.roundId} value={record.roundId}>
                    {t("inquiry_journey.prototype.export_scope_through", { record: recordLabel(record.roundId) })}
                  </option>
                ))}
              </select>
            </label>
            <div style={{ fontSize: 12, color: "#475569" }}>
              {t(effectiveExportRoundId
                ? "inquiry_journey.prototype.export_scope_round_hint"
                : "inquiry_journey.prototype.export_scope_all_hint")}
            </div>
            <div style={{ fontSize: 12, color: "#92400e" }}>
              {t("inquiry_journey.prototype.export_scope_safety_hint")}
            </div>
            <div style={{ fontSize: 12, color: "#166534" }}>
              {t("inquiry_journey.prototype.share_export_hint")}
            </div>
            {bundle.exportInfo ? (
              <div
                data-testid="inquiry-export-info"
                style={{ fontSize: 12, color: "#334155", overflowWrap: "anywhere" }}
              >
                {t(
                  bundle.exportInfo.scope === "round"
                    ? "inquiry_journey.prototype.imported_share_info_round"
                    : "inquiry_journey.prototype.imported_share_info_full",
                  bundle.exportInfo.scope === "round"
                    ? { roundId: bundle.exportInfo.selectedRoundId }
                    : undefined,
                )}
              </div>
            ) : null}
          </fieldset>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 8 }}>
            <button type="button" disabled={isBusy} onClick={() => void handleExport()} style={{ whiteSpace: "normal" }}>
              {t("inquiry_journey.prototype.export")}
            </button>
            <button type="button" disabled={isBusy} onClick={() => void handleShareExport()} style={{ whiteSpace: "normal" }}>
              {t("inquiry_journey.prototype.share_export")}
            </button>
            <button type="button" disabled={isBusy} onClick={() => inputRef.current?.click()} style={{ whiteSpace: "normal" }}>
              {t("inquiry_journey.prototype.import")}
            </button>
            <button type="button" disabled={isBusy} onClick={() => void handleSaveToBackend()} style={{ whiteSpace: "normal" }}>
              {t("inquiry_journey.prototype.save_backend")}
            </button>
            <button type="button" disabled={isBusy} onClick={() => void handleLoadFromBackend()} style={{ whiteSpace: "normal" }}>
              {t("inquiry_journey.prototype.load_backend")}
            </button>
          </div>
          {!isConfirmingEnd ? (
            <button type="button" onClick={() => setIsConfirmingEnd(true)}>
              {t("inquiry_journey.prototype.end")}
            </button>
          ) : (
            <InquiryEndConfirmationDialog
              isProcessing={isBusy}
              onDecision={(decision) => void handleEndConfirmationDecision(decision)}
            />
          )}
        </>
      )}
      <input
        ref={inputRef}
        type="file"
        accept=".json,application/json"
        onChange={(event) => void handleImport(event)}
        style={{ display: "none" }}
      />
      {message ? (
        <div role={message.kind === "error" ? "alert" : "status"} style={{ fontSize: 12, color: message.kind === "error" ? "#b91c1c" : "#166534" }}>
          {message.text}
        </div>
      ) : null}
      <div style={{ fontSize: 11, color: "#64748b" }}>
        {t("inquiry_journey.prototype.retention_note")}
      </div>
      {isImporting ? (
        <button type="button" onClick={() => importAbortRef.current?.abort()}>
          {t("inquiry_journey.prototype.cancel_import")}
        </button>
      ) : null}
    </section>
  );
}
