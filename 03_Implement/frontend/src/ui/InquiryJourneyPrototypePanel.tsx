import { useEffect, useMemo, useState } from "react";

import { ROUND_STAGES, type RoundStage } from "../domain/inquiry_journey";
import type { DocumentV1 } from "../domain/types";
import { t } from "../i18n/translate";

type PrototypeRecord = {
  id: string;
  stage: RoundStage;
  iteration: number;
};

type InquiryJourneyPrototypePanelProps = {
  document: DocumentV1 | null;
};

function stageLabel(stage: RoundStage): string {
  return t(`inquiry_journey.stage.${stage}`);
}

export function InquiryJourneyPrototypePanel({ document }: InquiryJourneyPrototypePanelProps) {
  const [originDocumentId, setOriginDocumentId] = useState<string | null>(null);
  const [selectedStage, setSelectedStage] = useState<RoundStage>("r1_problem_setting");
  const [records, setRecords] = useState<PrototypeRecord[]>([]);

  useEffect(() => {
    setOriginDocumentId(null);
    setSelectedStage("r1_problem_setting");
    setRecords([]);
  }, [document?.id]);

  const documentLabel = document?.title?.trim() || document?.id || t("inquiry_journey.prototype.no_document");
  const nextIteration = useMemo(
    () => records.filter((record) => record.stage === selectedStage).length + 1,
    [records, selectedStage]
  );
  const isStarted = originDocumentId === document?.id;

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
        <button
          type="button"
          data-domain-action="start-inquiry-journey-prototype"
          disabled={!document}
          onClick={() => setOriginDocumentId(document?.id ?? null)}
        >
          {t("inquiry_journey.prototype.start")}
        </button>
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
            onClick={() => {
              setRecords((previous) => [
                ...previous,
                {
                  id: `prototype-round-${previous.length + 1}`,
                  stage: selectedStage,
                  iteration: nextIteration,
                },
              ]);
            }}
          >
            {t("inquiry_journey.prototype.record", {
              stage: stageLabel(selectedStage),
              iteration: nextIteration,
            })}
          </button>

          {records.length > 0 ? (
            <ol aria-label={t("inquiry_journey.prototype.history")} style={{ margin: 0, paddingInlineStart: 24, fontSize: 12 }}>
              {records.map((record) => (
                <li key={record.id}>
                  {t("inquiry_journey.prototype.recorded", {
                    stage: stageLabel(record.stage),
                    iteration: record.iteration,
                  })}
                </li>
              ))}
            </ol>
          ) : null}

          <button
            type="button"
            onClick={() => {
              setOriginDocumentId(null);
              setRecords([]);
            }}
          >
            {t("inquiry_journey.prototype.end")}
          </button>
        </>
      )}
    </section>
  );
}
