export type ViewPatch = {
  summaryView?: boolean;
  abstractMapView?: boolean;
  hideSourceCards?: boolean;
  maxDepth?: number | "all";
  focusIslandId?: string | null;
  showReadingOrder?: boolean;
  readingNavEnabled?: boolean;
  readingMode?: "islands" | "islands+cards";
  reviewedOnly?: boolean;
  collapsedIslandIds?: string[];
  safeMode?: boolean;
  lodEnabled?: boolean;
  perspectiveMode?: "default" | "facts" | "claims" | "hypotheses" | "unknown" | "evidence" | "contradiction" | "review";
  perspectiveStrictFilter?: boolean;
};

export type ViewPreset = {
  id: string;
  name: string;
  viewPatch: ViewPatch;
  createdAt: string;
  updatedAt: string;
};

export const DEFAULT_VIEW_PRESETS: ViewPreset[] = [
  {
    id: "default-explore",
    name: "Explore",
    createdAt: "1970-01-01T00:00:00.000Z",
    updatedAt: "1970-01-01T00:00:00.000Z",
    viewPatch: {
      summaryView: false,
      abstractMapView: false,
      maxDepth: "all",
      reviewedOnly: false,
      perspectiveMode: "default",
      perspectiveStrictFilter: false,
      showReadingOrder: false,
      safeMode: false,
      lodEnabled: false,
    },
  },
  {
    id: "default-review",
    name: "Review",
    createdAt: "1970-01-01T00:00:00.000Z",
    updatedAt: "1970-01-01T00:00:00.000Z",
    viewPatch: {
      perspectiveMode: "review",
      perspectiveStrictFilter: false,
      reviewedOnly: true,
      showReadingOrder: true,
      safeMode: true,
      lodEnabled: false,
    },
  },
  {
    id: "default-summary",
    name: "Summary",
    createdAt: "1970-01-01T00:00:00.000Z",
    updatedAt: "1970-01-01T00:00:00.000Z",
    viewPatch: {
      summaryView: true,
      abstractMapView: true,
      maxDepth: 1,
      showReadingOrder: false,
      reviewedOnly: false,
      focusIslandId: null,
      safeMode: true,
      lodEnabled: true,
      perspectiveMode: "default",
      perspectiveStrictFilter: false,
    },
  },
];

function sortPresets(presets: ViewPreset[]): ViewPreset[] {
  return [...presets].sort((a, b) => a.name.localeCompare(b.name) || a.id.localeCompare(b.id));
}

export function migrateViewPresets(presets: ViewPreset[]): ViewPreset[] {
  const byId = new Map<string, ViewPreset>();
  for (const preset of DEFAULT_VIEW_PRESETS) {
    byId.set(preset.id, preset);
  }
  for (const preset of presets) {
    byId.set(preset.id, preset);
  }
  return sortPresets([...byId.values()]);
}

export function replaceViewPreset(presets: ViewPreset[], preset: ViewPreset): ViewPreset[] {
  return sortPresets([...presets.filter((item) => item.id !== preset.id), preset]);
}

export function renameViewPreset(presets: ViewPreset[], presetId: string, name: string, updatedAt: string): ViewPreset[] {
  return sortPresets(presets.map((preset) => (preset.id === presetId ? { ...preset, name, updatedAt } : preset)));
}

export function removeViewPreset(presets: ViewPreset[], presetId: string): ViewPreset[] {
  return sortPresets(presets.filter((preset) => preset.id !== presetId));
}

export function resolveSummaryAbstractFromPatch(
  current: { summaryView: boolean; abstractMapView: boolean },
  patch: ViewPatch,
): { summaryView: boolean; abstractMapView: boolean } {
  const nextAbstract = patch.abstractMapView ?? current.abstractMapView;
  if (nextAbstract) {
    return { summaryView: true, abstractMapView: true };
  }

  return {
    abstractMapView: false,
    summaryView: patch.summaryView ?? current.summaryView,
  };
}
