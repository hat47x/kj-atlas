import { useEffect, useMemo, useRef, useState, type ChangeEvent } from "react";

import { ROUND_STAGES, type InquiryBundleV1, type RoundStage } from "../domain/inquiry_journey";
import {
  INQUIRY_BUNDLE_MAX_BYTES,
  INQUIRY_BUNDLE_WARNING_BYTES,
  serializeInquiryBundle,
} from "../domain/inquiry_bundle_io";
import {
  compareInquiryRounds,
  inquiryBundleOriginatesFromDocument,
  recordInquiryRound,
  startInquiryJourney,
} from "../domain/inquiry_journey_session";
import type { DocumentV1 } from "../domain/types";
import { downloadTextFile } from "../export/narrative_export";
import { t } from "../i18n/translate";
import { InquiryBundleWorkerClient } from "../worker/inquiry_bundle_client";

type InquiryJourneyPrototypePanelProps = {
  document: DocumentV1 | null;
};

function stageLabel(stage: RoundStage): string {
  return t(`inquiry_journey.stage.${stage}`);
}

function fileStem(value: string): string {
  const sanitized = value.trim().replace(/[\\/:*?"<>|]+/g, "-").replace(/\s+/g, "-");
  return sanitized || "inquiry";
}

export function InquiryJourneyPrototypePanel({ document }: InquiryJourneyPrototypePanelProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const importClientRef = useRef<InquiryBundleWorkerClient | null>(null);
  const importAbortRef = useRef<AbortController | null>(null);
  const [bundle, setBundle] = useState<InquiryBundleV1 | null>(null);
  const [selectedStage, setSelectedStage] = useState<RoundStage>("r1_problem_setting");
  const [isBusy, setIsBusy] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [isConfirmingEnd, setIsConfirmingEnd] = useState(false);
  const [comparisonFromRoundId, setComparisonFromRoundId] = useState("");
  const [comparisonToRoundId, setComparisonToRoundId] = useState("");
  const [message, setMessage] = useState<{ kind: "status" | "error"; text: string } | null>(null);

  useEffect(() => {
    const activeImport = importAbortRef.current;
    importAbortRef.current = null;
    activeImport?.abort();
    setBundle(null);
    setSelectedStage("r1_problem_setting");
    setIsConfirmingEnd(false);
    setComparisonFromRoundId("");
    setComparisonToRoundId("");
    setMessage(null);
  }, [document?.id]);

  useEffect(() => () => {
    const activeImport = importAbortRef.current;
    importAbortRef.current = null;
    activeImport?.abort();
    importClientRef.current?.dispose();
  }, []);

  const records = bundle?.journey.roundRecords ?? [];
  const documentLabel = document?.title?.trim() || document?.id || t("inquiry_journey.prototype.no_document");
  const nextIteration = useMemo(
    () => records.filter((record) => record.stage === selectedStage).length + 1,
    [records, selectedStage]
  );
  const isStarted = bundle !== null;
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
    } finally {
      setIsBusy(false);
    }
  };

  const handleRecord = async () => {
    if (!bundle || !document) return;
    setIsBusy(true);
    setMessage(null);
    try {
      const result = await recordInquiryRound(bundle, document, selectedStage);
      if (!result.ok) {
        setMessage({ kind: "error", text: t("inquiry_journey.prototype.record_error") });
        return;
      }
      setBundle(result.bundle);
    } finally {
      setIsBusy(false);
    }
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
      setComparisonFromRoundId("");
      setComparisonToRoundId("");
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
            {t("inquiry_journey.prototype.record", {
              stage: stageLabel(selectedStage),
              iteration: nextIteration,
            })}
          </button>

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
                    setMessage(null);
                    setIsConfirmingEnd(false);
                    setComparisonFromRoundId("");
                    setComparisonToRoundId("");
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
