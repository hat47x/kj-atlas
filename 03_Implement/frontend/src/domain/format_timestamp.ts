import { getActiveLocale } from "../i18n/translate";

export const formatTimestamp = (createdAt: string): string => {
  const parsedDate = new Date(createdAt);
  if (Number.isNaN(parsedDate.getTime())) {
    return createdAt;
  }

  return parsedDate.toLocaleString(getActiveLocale() === "ja" ? "ja-JP" : "en-US");
};
