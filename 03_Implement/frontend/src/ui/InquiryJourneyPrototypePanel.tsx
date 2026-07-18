import { useEffect, useMemo, useRef, useState, type ChangeEvent } from "react";

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

type InquiryJourneyPrototypePanelProps = {
  document: DocumentV1 | null;
  onRestoreDocument: (document: DocumentV1) => boolean;
  onDiscardRestoredDocument: () => boolean;
};

type BranchUndoCheckpoint = {
  bundle: InquiryBundleV1;
  restoredDocument: DocumentV1;
};

function stageLabel(stage: RoundStage): string {
  return t(`inquiry_journey.stage.${stage}`);
}

function fileStem(value: string): string {
  const sanitized = value.trim().replace(/[\\/:*?"<>|]+/g, "-").replace(/\s+/g, "-");
  return sanitized || "inquiry";
}

export function InquiryJourneyPrototypePanel({
  document,
  onRestoreDocument,
  onDiscardRestoredDocument,
}: InquiryJourneyPrototypePanelProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const importClientRef = useRef<InquiryBundleWorkerClient | null>(null);
  const importAbortRef = useRef<AbortController | null>(null);
  const resumePreviewRef = useRef<HTMLElement | null>(null);
  const [bundle, setBundle] = useState<InquiryBundleV1 | null>(null);
  const [selectedStage, setSelectedStage] = useState<RoundStage>("r1_problem_setting");
  const [isBusy, setIsBusy] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [isConfirmingEnd, setIsConfirmingEnd] = useState(false);
  const [recordParentRoundId, setRecordParentRoundId] = useState("");
  const [comparisonFromRoundId, setComparisonFromRoundId] = useState("");
  const [comparisonToRoundId, setComparisonToRoundId] = useState("");
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

  const handleExport = async () => {
    if (!bundle) return;
    setIsBusy(true);
    setMessage(null);
    try {
      const serialized = await serializeInquiryBundle(bundle);
      if (!serialized.ok) {
        setMessage({
          kind: "error",
          text: t(
            serialized.errors.some((error) => error.code === "payload_too_large")
              ? "inquiry_journey.prototype.export_too_large"
              : "inquiry_journey.prototype.export_error"
          ),
        });
        return;
      }
      downloadTextFile(
        `${fileStem(bundle.journey.title)}.kj-atlas-inquiry.json`,
        "application/json",
        serialized.json
      );
      setMessage({ kind: "status", text: t("inquiry_journey.prototype.exported") });
    } finally {
      setIsBusy(false);
    }
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
      const outcome = await importClientRef.current.parse(await file.text(), { signal: controller.signal });
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

          <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 8 }}>
            <button type="button" disabled={isBusy} onClick={() => void handleExport()} style={{ whiteSpace: "normal" }}>
              {t("inquiry_journey.prototype.export")}
            </button>
            <button type="button" disabled={isBusy} onClick={() => inputRef.current?.click()} style={{ whiteSpace: "normal" }}>
              {t("inquiry_journey.prototype.import")}
            </button>
          </div>
          {!isConfirmingEnd ? (
            <button type="button" onClick={() => setIsConfirmingEnd(true)}>
              {t("inquiry_journey.prototype.end")}
            </button>
          ) : (
            <div role="group" aria-label={t("inquiry_journey.prototype.end_confirm")} style={{ display: "grid", gap: 6 }}>
              <div style={{ fontSize: 12, color: "#92400e" }}>{t("inquiry_journey.prototype.end_confirm")}</div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 8 }}>
                <button
                  type="button"
                  onClick={() => {
                    setBundle(null);
                    setBranchUndoCheckpoint(null);
                    setMessage(null);
                    setIsConfirmingEnd(false);
                    setRecordParentRoundId("");
                    setComparisonFromRoundId("");
                    setComparisonToRoundId("");
                    setLineageCardId("");
                    setResumePreviewSnapshotId("");
                  }}
                  style={{ whiteSpace: "normal" }}
                >
                  {t("inquiry_journey.prototype.end_confirm_action")}
                </button>
                <button type="button" onClick={() => setIsConfirmingEnd(false)}>
                  {t("inquiry_journey.prototype.end_cancel")}
                </button>
              </div>
            </div>
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
      {isImporting ? (
        <button type="button" onClick={() => importAbortRef.current?.abort()}>
          {t("inquiry_journey.prototype.cancel_import")}
        </button>
      ) : null}
    </section>
  );
}
