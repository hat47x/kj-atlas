import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import {
  completeVisualCueTrial,
  VISUAL_CUE_PROTOTYPE_SCENARIOS,
  withVisualCueEaseRating,
} from "./representative_visual_cue_prototype";

describe("representative visual cue Phase 0 prototype", () => {
  it("keeps the displayed scenarios aligned with the architecture fixture", () => {
    const fixturePath = resolve(
      process.cwd(),
      "../../02_Architecture/design/representative_visual_cue/phase0_scenarios.json",
    );
    const fixture = JSON.parse(readFileSync(fixturePath, "utf8")) as {
      scenarios: Array<{
        id: string;
        title: string;
        islandTitles: string[];
        targetSequence: string[];
        criticalCheck: string;
      }>;
    };

    expect(VISUAL_CUE_PROTOTYPE_SCENARIOS.map(({ id, title, islandTitles, targetSequence, criticalCheck }) => ({
      id,
      title,
      islandTitles,
      targetSequence,
      criticalCheck,
    }))).toEqual(fixture.scenarios.map(({ id, title, islandTitles, targetSequence, criticalCheck }) => ({
      id,
      title,
      islandTitles,
      targetSequence,
      criticalCheck,
    })));
  });

  it("keeps all five evaluation scenarios and condition restrictions", () => {
    expect(VISUAL_CUE_PROTOTYPE_SCENARIOS.map((scenario) => scenario.id)).toEqual([
      "VC-S1",
      "VC-S2",
      "VC-S3",
      "VC-S4",
      "VC-S5",
    ]);
    expect(VISUAL_CUE_PROTOTYPE_SCENARIOS.find((scenario) => scenario.id === "VC-S3")?.availableConditions)
      .toEqual(["C0", "C3"]);
  });

  it("records elapsed time and mistakes without ranking participants", () => {
    const result = completeVisualCueTrial({
      scenarioId: "VC-S1",
      conditionId: "C2",
      target: "本人確認",
      startedAt: 100.4,
      completedAt: 935.8,
      mistakes: 2.9,
    });

    expect(result).toEqual({
      scenarioId: "VC-S1",
      conditionId: "C2",
      target: "本人確認",
      elapsedMs: 835,
      mistakes: 2,
    });
    expect(withVisualCueEaseRating(result, 7).easeRating).toBe(5);
    expect(withVisualCueEaseRating(result, -1).easeRating).toBe(1);
  });
});
