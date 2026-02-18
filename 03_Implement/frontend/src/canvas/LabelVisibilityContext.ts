import { createContext } from "react";

export type LabelVisibilityState = {
  acceptedLabelIds: Set<string> | null;
};

export const LabelVisibilityContext = createContext<LabelVisibilityState>({
  acceptedLabelIds: null,
});
