import type { DocumentV1 } from "../types";
import type { FindingEntityRef, OutlineQualityReport } from "./outline_quality";
import type { ReadingPathViewState } from "./reading_path";

export type RecommendationCategory = "structure" | "review" | "relation" | "clarity";
export type RecommendationImpactLevel = "high" | "medium" | "low";

export type Recommendation = {
  id: string;
  priority: number;
  category: RecommendationCategory;
  title: string;
  description: string;
  targetEntities?: { kind: "island" | "card"; id: string }[];
  rationaleCodes: string[];
  suggestedActions: string[];
  impactLevel: RecommendationImpactLevel;
};

function isEmptyText(value: string | undefined): boolean {
  return (value ?? "").trim().length === 0;
}

function getImpactRank(level: RecommendationImpactLevel): number {
  if (level === "high") {
    return 0;
  }
  if (level === "medium") {
    return 1;
  }
  return 2;
}

function hasFinding(report: OutlineQualityReport, code: string): boolean {
  return report.findings.some((finding) => finding.code === code);
}

function getFindingEntityRefs(report: OutlineQualityReport, code: string): FindingEntityRef[] {
  return report.findings
    .filter((finding) => finding.code === code)
    .flatMap((finding) => finding.entityRefs ?? [])
    .slice(0, 10);
}

function pickTargets(report: OutlineQualityReport, code: string, fallback: FindingEntityRef[]): FindingEntityRef[] | undefined {
  const refs = getFindingEntityRefs(report, code);
  if (refs.length > 0) {
    return refs;
  }

  if (fallback.length > 0) {
    return fallback.slice(0, 10);
  }

  return undefined;
}

function byTitle(a: string, b: string): number {
  if (a === b) {
    return 0;
  }

  return a < b ? -1 : 1;
}

export function generateRecommendations(
  report: OutlineQualityReport,
  doc: DocumentV1,
  readingState: ReadingPathViewState,
): Recommendation[] {
  const recommendations: Recommendation[] = [];
  const untitledIslands = doc.islands.filter((island) => isEmptyText(island.title)).map((island) => ({ kind: "island" as const, id: island.id }));
  const unreviewedIslands = doc.islands.filter((island) => island.summaryReviewed !== true).map((island) => ({ kind: "island" as const, id: island.id }));
  const islandCardIds = new Set(doc.islands.flatMap((island) => island.cardIds));
  const loneCards = doc.cards.filter((card) => !islandCardIds.has(card.id)).map((card) => ({ kind: "card" as const, id: card.id }));

  if (hasFinding(report, "Q001")) {
    recommendations.push({
      id: "rec-q001-missing-island-titles",
      priority: 1,
      category: "clarity",
      title: "島タイトルを整理する",
      description: "多くの島にタイトルが無く、読解の起点が不明確です。",
      targetEntities: pickTargets(report, "Q001", untitledIslands),
      rationaleCodes: ["Q001"],
      suggestedActions: [
        "各島に1行の要約タイトルを付与する",
        "冗長なタイトルは15文字以内に整理する",
      ],
      impactLevel: "high",
    });
  }

  if (hasFinding(report, "Q003")) {
    recommendations.push({
      id: "rec-q003-review-unreviewed-summaries",
      priority: readingState.reviewedOnly ? 2 : 1,
      category: "review",
      title: "未承認サマリのレビューを優先する",
      description: "読解の大部分が未承認状態です。",
      targetEntities: pickTargets(report, "Q003", unreviewedIslands),
      rationaleCodes: ["Q003"],
      suggestedActions: [
        "各島サマリを確認し、reviewed=trueにする",
        "誤解の恐れがある表現を修正する",
      ],
      impactLevel: "high",
    });
  }

  if (hasFinding(report, "Q005")) {
    recommendations.push({
      id: "rec-q005-reconnect-islands",
      priority: 2,
      category: "structure",
      title: "島間の関係を再検討する",
      description: "孤立島が多く、全体構造が断片化しています。",
      targetEntities: pickTargets(report, "Q005", []),
      rationaleCodes: ["Q005"],
      suggestedActions: [
        "関連する島同士に関係線を追加する",
        "不要な島は統合を検討する",
      ],
      impactLevel: "high",
    });
  }

  if (hasFinding(report, "Q004")) {
    recommendations.push({
      id: "rec-q004-add-relation-summaries",
      priority: 3,
      category: "relation",
      title: "島間関係の説明を補強する",
      description: "島間関係の要約が不足しており、接続理由の把握が難しい状態です。",
      rationaleCodes: ["Q004"],
      suggestedActions: ["主要な島間にrelation summaryを追加する"],
      impactLevel: "medium",
    });
  }

  if (hasFinding(report, "Q006")) {
    recommendations.push({
      id: "rec-q006-reduce-path-length",
      priority: 3,
      category: "structure",
      title: "階層化または統合を検討する",
      description: "読解パスが長く、全体把握に時間がかかります。",
      rationaleCodes: ["Q006"],
      suggestedActions: [
        "代表カードを作成して類似カードを統合する",
        "島を上位/下位構造に分ける",
      ],
      impactLevel: "medium",
    });
  }

  if (hasFinding(report, "Q007")) {
    recommendations.push({
      id: "rec-q007-handle-lone-cards",
      priority: 4,
      category: "structure",
      title: "孤立カードの扱いを明確にする",
      description: "島に属していないカードが存在し、読解導線が分断されています。",
      targetEntities: pickTargets(report, "Q007", loneCards),
      rationaleCodes: ["Q007"],
      suggestedActions: ["島へ編入する", "不要なら削除する"],
      impactLevel: "medium",
    });
  }

  return recommendations.sort((a, b) => {
    if (a.priority !== b.priority) {
      return a.priority - b.priority;
    }

    const impactDiff = getImpactRank(a.impactLevel) - getImpactRank(b.impactLevel);
    if (impactDiff !== 0) {
      return impactDiff;
    }

    return byTitle(a.title, b.title);
  });
}
