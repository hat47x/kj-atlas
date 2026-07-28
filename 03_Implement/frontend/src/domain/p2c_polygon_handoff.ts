import { fnv1aHash } from "../utils/fnv1a_hash";
import { padPolygonFromCentroid } from "./geometry/polygon_pad";
import { P2C_DETERMINISTIC_TIE_BREAK_ORDER, type P2CTieBreakKey } from "./merge/p2c_tie_break_contract";

export { P2C_DETERMINISTIC_TIE_BREAK_ORDER };

export type Point = { x: number; y: number };

export const P2C_A2_HANDOFF_ID = "A2-HANDOFF-FB-P2C-01-2026-03-14" as const;
export type P2CMockCaseId = "A" | "B" | "C";

export type P2CMockValidationLog = {
  handoffId: typeof P2C_A2_HANDOFF_ID;
  mockCaseId: P2CMockCaseId;
  inputHash: string;
  outputPolygonHash: string;
  paddingViolationCount: number;
  seed: number;
  tieBreakOrder: readonly P2CTieBreakKey[];
  validationResult: "pass" | "fail";
  ownerOfFix: "A2" | "A3";
  evidence: string;
};

function normalizePoints(points: readonly Point[]): Point[] {
  return points.map((point) => ({
    x: Number(point.x.toFixed(2)),
    y: Number(point.y.toFixed(2)),
  }));
}

export function toPolygonInputHash(points: readonly Point[], seed: number): string {
  return fnv1aHash(JSON.stringify({ seed, points: normalizePoints(points) }));
}

export function toPolygonOutputHash(points: readonly Point[]): string {
  return fnv1aHash(JSON.stringify(normalizePoints(points)));
}

export function countPaddingViolations(before: readonly Point[], after: readonly Point[], padding: number): number {
  const centroid = before.reduce(
    (acc, point) => ({ x: acc.x + point.x / before.length, y: acc.y + point.y / before.length }),
    { x: 0, y: 0 }
  );

  return before.reduce((count, sourcePoint, index) => {
    const targetPoint = after[index];
    if (!targetPoint) {
      return count + 1;
    }

    const beforeDistance = Math.hypot(sourcePoint.x - centroid.x, sourcePoint.y - centroid.y);
    const afterDistance = Math.hypot(targetPoint.x - centroid.x, targetPoint.y - centroid.y);
    return afterDistance - beforeDistance < padding - 1e-6 ? count + 1 : count;
  }, 0);
}

export function buildP2CMockValidationLog(
  mockCaseId: P2CMockCaseId,
  fixture: readonly Point[],
  seed: number,
  padding: number
): P2CMockValidationLog {
  const output = padPolygonFromCentroid([...fixture], padding);
  const paddingViolationCount = countPaddingViolations(fixture, output, padding);
  const isPass = paddingViolationCount === 0;

  return {
    handoffId: P2C_A2_HANDOFF_ID,
    mockCaseId,
    inputHash: toPolygonInputHash(fixture, seed),
    outputPolygonHash: toPolygonOutputHash(output),
    paddingViolationCount,
    seed,
    tieBreakOrder: P2C_DETERMINISTIC_TIE_BREAK_ORDER,
    validationResult: isPass ? "pass" : "fail",
    ownerOfFix: isPass ? "A3" : "A2",
    evidence: isPass ? "paddingViolationCount=0" : `paddingViolationCount=${paddingViolationCount}`,
  };
}

export function evaluateP2CA3StartCondition(
  logs: readonly P2CMockValidationLog[],
  options: { gateApproved: boolean; a2VerifyPass: boolean }
): { go: boolean; reason: string } {
  if (!options.gateApproved || !options.a2VerifyPass) {
    return { go: false, reason: "StartCondition requires Gate0=Approved and A2Verify=Pass" };
  }

  const requiredCases: P2CMockCaseId[] = ["A", "B", "C"];
  const seen = new Set<P2CMockCaseId>();
  for (const log of logs) {
    if (log.handoffId !== P2C_A2_HANDOFF_ID) {
      return { go: false, reason: `invalid handoffId: ${log.handoffId}` };
    }

    if (seen.has(log.mockCaseId)) {
      return { go: false, reason: `duplicate mock case: ${log.mockCaseId}` };
    }
    seen.add(log.mockCaseId);

    if (log.tieBreakOrder.join(",") !== P2C_DETERMINISTIC_TIE_BREAK_ORDER.join(",")) {
      return { go: false, reason: "tieBreakOrderChanged=true" };
    }

    if (log.paddingViolationCount > 0) {
      return { go: false, reason: "paddingViolationCount>0" };
    }

    if (log.validationResult !== "pass") {
      return { go: false, reason: `${log.mockCaseId} must be pass` };
    }
  }

  for (const requiredCase of requiredCases) {
    if (!seen.has(requiredCase)) {
      return { go: false, reason: `missing mock case: ${requiredCase}` };
    }
  }

  return { go: true, reason: "go" };
}
