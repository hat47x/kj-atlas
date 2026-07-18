import { useMemo, useState } from "react";

import {
  completeVisualCueTrial,
  VISUAL_CUE_CONDITIONS,
  VISUAL_CUE_PROTOTYPE_SCENARIOS,
  withVisualCueEaseRating,
  type VisualCueConditionId,
  type VisualCueTrialResult,
} from "../domain/representative_visual_cue_prototype";
import { t } from "../i18n/translate";

type TrialState =
  | { kind: "idle" }
  | { kind: "active"; startedAt: number; mistakes: number }
  | { kind: "complete"; result: VisualCueTrialResult };

const EMOJI_CUES = ["📍", "🔎", "⏳", "✍️", "🪪", "↗️", "💻", "⚠️"];
const HAND_CUES = ["○", "△", "≈", "□", "＋", "↗", "⌁", "!"];

function cueIndex(title: string): number {
  return Array.from(title).reduce((sum, character) => sum + (character.codePointAt(0) ?? 0), 0);
}

function VisualCue({ condition, title, photoPath }: { condition: VisualCueConditionId; title: string; photoPath?: string }) {
  const index = cueIndex(title);
  const frameStyle = {
    width: 36,
    height: 36,
    flex: "0 0 36px",
    display: "grid",
    placeItems: "center",
    overflow: "hidden",
  } as const;

  if (condition === "C0") return <span aria-hidden="true" style={frameStyle} />;
  if (condition === "C1") {
    return (
      <span aria-hidden="true" style={{ ...frameStyle, fontSize: 25, fontFamily: "cursive", transform: `rotate(${(index % 9) - 4}deg)` }}>
        {HAND_CUES[index % HAND_CUES.length]}
      </span>
    );
  }
  if (condition === "C2") {
    const shape = index % 3;
    return (
      <span aria-hidden="true" style={frameStyle}>
        <span
          style={{
            width: shape === 1 ? 22 : 19,
            height: shape === 2 ? 13 : 19,
            border: "2px solid #0f766e",
            borderRadius: shape === 0 ? "50%" : 2,
            transform: shape === 2 ? "rotate(45deg)" : undefined,
            boxSizing: "border-box",
          }}
        />
      </span>
    );
  }
  if (condition === "C3" && photoPath) {
    return <img aria-hidden="true" src={photoPath} alt="" style={{ ...frameStyle, objectFit: "cover", borderRadius: 4 }} />;
  }
  if (condition === "C4") {
    return <span aria-hidden="true" style={{ ...frameStyle, fontSize: 24 }}>{EMOJI_CUES[index % EMOJI_CUES.length]}</span>;
  }
  return <span aria-hidden="true" style={frameStyle} />;
}

export function RepresentativeVisualCuePrototypePanel() {
  const [scenarioId, setScenarioId] = useState(VISUAL_CUE_PROTOTYPE_SCENARIOS[0].id);
  const [conditionId, setConditionId] = useState<VisualCueConditionId>("C0");
  const [targetIndex, setTargetIndex] = useState(0);
  const [trial, setTrial] = useState<TrialState>({ kind: "idle" });
  const [results, setResults] = useState<VisualCueTrialResult[]>([]);
  const [showSource, setShowSource] = useState(false);

  const scenario = useMemo(
    () => VISUAL_CUE_PROTOTYPE_SCENARIOS.find((candidate) => candidate.id === scenarioId) ?? VISUAL_CUE_PROTOTYPE_SCENARIOS[0],
    [scenarioId],
  );
  const target = scenario.targetSequence[targetIndex] ?? scenario.targetSequence[0];

  const resetTrial = (nextScenarioId = scenarioId, nextCondition = conditionId) => {
    const nextScenario = VISUAL_CUE_PROTOTYPE_SCENARIOS.find((candidate) => candidate.id === nextScenarioId)
      ?? VISUAL_CUE_PROTOTYPE_SCENARIOS[0];
    setTargetIndex(0);
    setTrial({ kind: "idle" });
    setShowSource(false);
    if (!nextScenario.availableConditions.includes(nextCondition)) setConditionId("C0");
  };

  const handleIslandSelect = (selectedTitle: string) => {
    if (trial.kind !== "active") return;
    if (selectedTitle !== target) {
      setTrial({ ...trial, mistakes: trial.mistakes + 1 });
      return;
    }
    setTrial({
      kind: "complete",
      result: completeVisualCueTrial({
        scenarioId: scenario.id,
        conditionId,
        target,
        startedAt: trial.startedAt,
        completedAt: performance.now(),
        mistakes: trial.mistakes,
      }),
    });
  };

  const handleRating = (rating: number) => {
    if (trial.kind !== "complete") return;
    const rated = withVisualCueEaseRating(trial.result, rating);
    setTrial({ kind: "complete", result: rated });
  };

  const handleNext = () => {
    if (trial.kind !== "complete" || trial.result.easeRating === undefined) return;
    setResults((current) => [...current, trial.result]);
    if (targetIndex + 1 < scenario.targetSequence.length) {
      setTargetIndex((current) => current + 1);
      setTrial({ kind: "idle" });
    } else {
      setTargetIndex(0);
      setTrial({ kind: "idle" });
    }
    setShowSource(false);
  };

  return (
    <section data-panel="representative-visual-cue-prototype" style={{ display: "grid", gap: 12 }}>
      <header style={{ display: "grid", gap: 4 }}>
        <div style={{ fontSize: 13, fontWeight: 700 }}>{t("visual_cue.prototype.title")}</div>
        <div role="status" style={{ fontSize: 11, color: "#92400e" }}>{t("visual_cue.prototype.session_only")}</div>
      </header>

      <label style={{ display: "grid", gap: 4, fontSize: 12 }}>
        {t("visual_cue.prototype.scenario")}
        <select
          value={scenarioId}
          onChange={(event) => {
            const nextId = event.currentTarget.value;
            setScenarioId(nextId);
            resetTrial(nextId, conditionId);
          }}
        >
          {VISUAL_CUE_PROTOTYPE_SCENARIOS.map((candidate) => (
            <option key={candidate.id} value={candidate.id}>{candidate.id}: {candidate.title}</option>
          ))}
        </select>
      </label>

      <div role="group" aria-label={t("visual_cue.prototype.condition")} style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
        {VISUAL_CUE_CONDITIONS.map((candidate) => {
          const available = scenario.availableConditions.includes(candidate);
          return (
            <button
              key={candidate}
              type="button"
              aria-label={`${candidate}: ${t(`visual_cue.prototype.condition.${candidate}`)}`}
              aria-pressed={conditionId === candidate}
              disabled={!available || trial.kind === "active"}
              onClick={() => {
                setConditionId(candidate);
                resetTrial(scenarioId, candidate);
              }}
              style={{
                minWidth: 128,
                border: "1px solid #cbd5e1",
                borderRadius: 6,
                padding: "6px 8px",
                backgroundColor: conditionId === candidate ? "#e0f2fe" : "#ffffff",
                color: available ? "#0f172a" : "#94a3b8",
                fontWeight: 700,
              }}
            >
              {candidate}: {t(`visual_cue.prototype.condition.${candidate}`)}
            </button>
          );
        })}
      </div>
      {scenario.availableConditions.length < VISUAL_CUE_CONDITIONS.length ? (
        <div style={{ fontSize: 11, color: "#64748b" }}>{t("visual_cue.prototype.unavailable_note")}</div>
      ) : null}
      <div style={{ fontSize: 11, color: "#475569" }}>{t(`visual_cue.prototype.condition.${conditionId}`)}</div>

      <div style={{ borderTop: "1px solid #e2e8f0", paddingTop: 12, display: "grid", gap: 10 }}>
        <div style={{ fontSize: 12, color: "#334155" }}>{t("visual_cue.prototype.critical_check", { value: scenario.criticalCheck })}</div>
        <div style={{ fontSize: 14, fontWeight: 700 }}>{t("visual_cue.prototype.target", { value: target })}</div>

        {trial.kind === "idle" ? (
          <button type="button" onClick={() => setTrial({ kind: "active", startedAt: performance.now(), mistakes: 0 })}>
            {t("visual_cue.prototype.start")}
          </button>
        ) : null}

        <div
          aria-label={t("visual_cue.prototype.islands")}
          style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 8 }}
        >
          {scenario.islandTitles.map((title) => (
            <button
              key={title}
              type="button"
              disabled={trial.kind !== "active"}
              onClick={() => handleIslandSelect(title)}
              style={{
                minHeight: 92,
                minWidth: 0,
                border: "1px solid #94a3b8",
                borderRadius: 6,
                backgroundColor: "#ffffff",
                color: "#0f172a",
                display: "flex",
                alignItems: "flex-start",
                gap: 8,
                padding: 10,
                textAlign: "left",
                fontSize: 12,
                lineHeight: 1.5,
              }}
            >
              <VisualCue
                condition={conditionId}
                title={title}
                photoPath={title === scenario.targetSequence[0] ? scenario.sourceVisual?.assetPath : undefined}
              />
              <span style={{ minWidth: 0, overflowWrap: "anywhere" }}>{title}</span>
            </button>
          ))}
        </div>

        {trial.kind === "active" ? (
          <div role="status" aria-live="polite" style={{ fontSize: 12, color: "#475569" }}>
            {t("visual_cue.prototype.mistakes", { count: trial.mistakes })}
          </div>
        ) : null}

        {trial.kind === "complete" ? (
          <div style={{ display: "grid", gap: 10, border: "1px solid #cbd5e1", borderRadius: 6, padding: 10 }}>
            <div role="status" style={{ fontSize: 12, color: "#166534" }}>
              {t("visual_cue.prototype.result", {
                time: trial.result.elapsedMs,
                mistakes: trial.result.mistakes,
              })}
            </div>
            <div role="group" aria-label={t("visual_cue.prototype.ease")} style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
              {[1, 2, 3, 4, 5].map((rating) => (
                <button
                  key={rating}
                  type="button"
                  aria-pressed={trial.result.easeRating === rating}
                  onClick={() => handleRating(rating)}
                  style={{ width: 36, height: 36 }}
                >
                  {rating}
                </button>
              ))}
            </div>
            {scenario.sourceVisual && conditionId === "C3" ? (
              <button type="button" onClick={() => setShowSource((current) => !current)} aria-expanded={showSource}>
                {t("visual_cue.prototype.source_open")}
              </button>
            ) : null}
            <button type="button" disabled={trial.result.easeRating === undefined} onClick={handleNext}>
              {t("visual_cue.prototype.next")}
            </button>
          </div>
        ) : null}

        {showSource && scenario.sourceVisual ? (
          <figure style={{ margin: 0, display: "grid", gap: 8 }}>
            <img
              src={scenario.sourceVisual.assetPath}
              alt={t("visual_cue.prototype.source_alt")}
              style={{ width: "100%", maxHeight: 300, objectFit: "contain", backgroundColor: "#f8fafc" }}
            />
            <figcaption style={{ display: "grid", gap: 4, fontSize: 12, color: "#334155" }}>
              <strong>{t("visual_cue.prototype.synthetic")}</strong>
              <span>{t("visual_cue.prototype.capture_context", { value: scenario.sourceVisual.captureContext })}</span>
              <span>{t("visual_cue.prototype.linked_card", { value: scenario.sourceVisual.linkedCard })}</span>
            </figcaption>
          </figure>
        ) : null}
      </div>

      {results.length > 0 ? (
        <details>
          <summary>{t("visual_cue.prototype.records", { count: results.length })}</summary>
          <ol aria-label={t("visual_cue.prototype.records_label")} style={{ margin: "8px 0 0", paddingInlineStart: 24, fontSize: 11 }}>
            {results.map((result, index) => (
              <li key={`${result.scenarioId}-${result.conditionId}-${result.target}-${index}`}>
                {t("visual_cue.prototype.record", {
                  scenario: result.scenarioId,
                  condition: result.conditionId,
                  time: result.elapsedMs,
                  mistakes: result.mistakes,
                  ease: result.easeRating ?? "-",
                })}
              </li>
            ))}
          </ol>
        </details>
      ) : null}
    </section>
  );
}
