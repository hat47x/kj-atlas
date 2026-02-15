export type TemporaryRevealEligibility = {
  isInFocusScope: boolean;
  isWithinDepth: boolean;
};

export function isTemporaryRevealEligible(eligibility: TemporaryRevealEligibility): boolean {
  return eligibility.isInFocusScope && eligibility.isWithinDepth;
}
