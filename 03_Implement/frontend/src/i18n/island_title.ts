import type { Island } from "../domain/types";
import { t } from "./translate";

export function resolveIslandDisplayTitle(island: Island, islands: Island[]): string {
  const authoredTitle = island.title?.trim();
  if (authoredTitle) {
    return authoredTitle;
  }

  const islandIndex = islands.findIndex((candidate) => candidate.id === island.id);
  if (islandIndex < 0) {
    return t("canvas.island.default_title");
  }

  return t("canvas.island.default_title_numbered", { number: islandIndex + 1 });
}
