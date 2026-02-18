export type LODLevel = "close" | "mid" | "far";

export type LODThresholds = {
  close: number;
  mid: number;
};

export type LODConfig = {
  lodEnabled: boolean;
  lodThresholds?: LODThresholds;
  lodLevelOverride?: LODLevel | null;
  lodShowLoneWolvesWhenFar: boolean;
};

export type LODRules = {
  showCards: boolean;
  compactCards: boolean;
  showCardEdges: boolean;
  showIslandEdges: boolean;
};

export function isVirtualCollapsedByLOD(lodEnabled: boolean, lodLevel: LODLevel | null | undefined): boolean {
  return lodEnabled && lodLevel === "far";
}

export function isEffectivelyCollapsed(
  userCollapsed: boolean,
  lodEnabled: boolean,
  lodLevel: LODLevel | null | undefined
): boolean {
  return userCollapsed || isVirtualCollapsedByLOD(lodEnabled, lodLevel);
}

export const DEFAULT_LOD_THRESHOLDS: LODThresholds = {
  close: 1,
  mid: 0.5,
};

function normalizeThresholds(thresholds?: LODThresholds): LODThresholds {
  if (!thresholds) {
    return DEFAULT_LOD_THRESHOLDS;
  }

  const close = Number.isFinite(thresholds.close) ? thresholds.close : DEFAULT_LOD_THRESHOLDS.close;
  const mid = Number.isFinite(thresholds.mid) ? thresholds.mid : DEFAULT_LOD_THRESHOLDS.mid;

  if (close < mid) {
    return {
      close: mid,
      mid,
    };
  }

  return { close, mid };
}

export function getLODLevel(
  zoom: number,
  userConfig?: Pick<LODConfig, "lodThresholds" | "lodLevelOverride">
): { level: LODLevel; rules: LODRules } {
  const thresholds = normalizeThresholds(userConfig?.lodThresholds);

  const level: LODLevel = userConfig?.lodLevelOverride
    ? userConfig.lodLevelOverride
    : zoom >= thresholds.close
      ? "close"
      : zoom >= thresholds.mid
        ? "mid"
        : "far";

  if (level === "close") {
    return {
      level,
      rules: {
        showCards: true,
        compactCards: false,
        showCardEdges: true,
        showIslandEdges: true,
      },
    };
  }

  if (level === "mid") {
    return {
      level,
      rules: {
        showCards: true,
        compactCards: true,
        showCardEdges: false,
        showIslandEdges: true,
      },
    };
  }

  return {
    level,
    rules: {
      showCards: false,
      compactCards: true,
      showCardEdges: false,
      showIslandEdges: true,
    },
  };
}
