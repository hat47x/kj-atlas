export type VisualCueConditionId = "C0" | "C1" | "C2" | "C3" | "C4";

export type VisualCuePrototypeScenario = {
  id: string;
  title: string;
  islandTitles: string[];
  targetSequence: string[];
  availableConditions: VisualCueConditionId[];
  criticalCheck: string;
  sourceVisual?: {
    assetPath: string;
    captureContext: string;
    linkedCard: string;
    syntheticFixture: true;
  };
};

export type VisualCueTrialResult = {
  scenarioId: string;
  conditionId: VisualCueConditionId;
  target: string;
  elapsedMs: number;
  mistakes: number;
  easeRating?: number;
};

export const VISUAL_CUE_CONDITIONS: VisualCueConditionId[] = ["C0", "C1", "C2", "C3", "C4"];

export const VISUAL_CUE_PROTOTYPE_SCENARIOS: VisualCuePrototypeScenario[] = [
  {
    id: "VC-S1",
    title: "具体的な窓口業務",
    islandTitles: [
      "受付前の準備",
      "入口の案内表示",
      "窓口での待ち",
      "申請書の記入",
      "本人確認",
      "職員の引継ぎ",
      "オンライン申請",
      "例外対応",
    ],
    targetSequence: ["入口の案内表示", "本人確認", "例外対応"],
    availableConditions: ["C0", "C1", "C2", "C4"],
    criticalCheck: "表札を確認して選択する",
  },
  {
    id: "VC-S2",
    title: "抽象的な対立",
    islandTitles: ["速さを優先したい", "丁寧さを守りたい", "判断が割れている", "まだ確かめていない"],
    targetSequence: ["判断が割れている"],
    availableConditions: ["C0", "C1", "C2"],
    criticalCheck: "中立的な手掛かりまたは画像なしを選べる",
  },
  {
    id: "VC-S3",
    title: "写真が一次資料",
    islandTitles: ["入口の案内板が反射して読めない", "案内板までの動線", "受付で尋ねた内容"],
    targetSequence: ["入口の案内板が反射して読めない"],
    availableConditions: ["C0", "C3"],
    criticalCheck: "切り抜きから元写真・撮影状況・観察カードへ戻れる",
    sourceVisual: {
      assetPath: "/evaluation/representative-visual-cue/source-photo-sign-glare-01.png",
      captureContext: "入口正面から照明の反射を観察",
      linkedCard: "照明の反射で文字の一部が読めなかった",
      syntheticFixture: true,
    },
  },
  {
    id: "VC-S4",
    title: "機微情報を含む未レビュー取材",
    islandTitles: ["相談時に話された生活上の困りごと", "本人へ確認できていない点", "支援者の仮説"],
    targetSequence: ["本人へ確認できていない点"],
    availableConditions: ["C0", "C1"],
    criticalCheck: "画像なしで完了でき、外部通信しない",
  },
  {
    id: "VC-S5",
    title: "似た記号の衝突",
    islandTitles: ["窓口で順番を待つ", "職員の確認結果を待つ", "利用者からの返信を待つ", "期限まで保留する"],
    targetSequence: ["職員の確認結果を待つ", "期限まで保留する"],
    availableConditions: ["C0", "C1", "C2", "C4"],
    criticalCheck: "似た記号でも表札を読み飛ばさず誤選択が増えない",
  },
];

export function completeVisualCueTrial(input: {
  scenarioId: string;
  conditionId: VisualCueConditionId;
  target: string;
  startedAt: number;
  completedAt: number;
  mistakes: number;
}): VisualCueTrialResult {
  return {
    scenarioId: input.scenarioId,
    conditionId: input.conditionId,
    target: input.target,
    elapsedMs: Math.max(0, Math.round(input.completedAt - input.startedAt)),
    mistakes: Math.max(0, Math.floor(input.mistakes)),
  };
}

export function withVisualCueEaseRating(result: VisualCueTrialResult, rating: number): VisualCueTrialResult {
  return { ...result, easeRating: Math.min(5, Math.max(1, Math.round(rating))) };
}
