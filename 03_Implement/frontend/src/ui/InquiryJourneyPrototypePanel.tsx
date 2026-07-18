import { useEffect, useMemo, useRef, useState, type ChangeEvent } from "react";

import { ROUND_STAGES, type InquiryBundleV1, type RoundStage } from "../domain/inquiry_journey";
import { parseInquiryBundleJson, serializeInquiryBundle } from "../domain/inquiry_bundle_io";
import {
  inquiryBundleOriginatesFromDocument,
  recordInquiryRound,
  startInquiryJourney,
} from "../domain/inquiry_journey_session";
import type { DocumentV1 } from "../domain/types";
import { downloadTextFile } from "../export/narrative_export";
import { t } from "../i18n/translate";

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
  const [bundle, setBundle] = useState<InquiryBundleV1 | null>(null);
  const [selectedStage, setSelectedStage] = useState<RoundStage>("r1_problem_setting");
  const [isBusy, setIsBusy] = useState(false);
  const [isConfirmingEnd, setIsConfirmingEnd] = useState(false);
  const [message, setMessage] = useState<{ kind: "status" | "error"; text: string } | null>(null);

  useEffect(() => {
    setBundle(null);
    setSelectedStage("r1_problem_setting");
    setIsConfirmingEnd(false);
    setMessage(null);
  }, [document?.id]);

  const records = bundle?.journey.roundRecords ?? [];
  const documentLabel = document?.title?.trim() || document?.id || t("inquiry_journey.prototype.no_document");
  const nextIteration = useMemo(
    () => records.filter((record) => record.stage === selectedStage).length + 1,
    [records, selectedStage]
  );
  const isStarted = bundle !== null;

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
        setMessage({ kind: "error", text: t("inquiry_journey.prototype.export_error") });
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
    setIsBusy(true);
    setMessage(null);
    try {
      const parsed = await parseInquiryBundleJson(await file.text());
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
      setSelectedStage(parsed.bundle.journey.roundRecords.at(-1)?.stage ?? "r1_problem_setting");
      setMessage({ kind: "status", text: t("inquiry_journey.prototype.imported") });
    } finally {
      setIsBusy(false);
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
    </section>
  );
}
