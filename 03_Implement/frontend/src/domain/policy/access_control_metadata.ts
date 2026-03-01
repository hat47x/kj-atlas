export type AccessControlMetadata = {
  roles?: string[];
  groups?: string[];
  policyRef?: string;
};

function normalizeList(values: unknown): string[] | undefined {
  if (!Array.isArray(values)) {
    return undefined;
  }
  const normalized = values
    .filter((value): value is string => typeof value === "string")
    .map((value) => value.trim())
    .filter((value) => value.length > 0)
    .filter((value) => value.toLowerCase() !== "null");

  return normalized.length > 0 ? normalized : undefined;
}

function normalizePolicyRef(value: unknown): string | undefined {
  if (typeof value !== "string") {
    return undefined;
  }
  const trimmed = value.trim();
  if (trimmed.length === 0 || trimmed.toLowerCase() === "null") {
    return undefined;
  }
  return trimmed;
}

export function normalizeAccessControlMetadata(value: unknown): AccessControlMetadata | undefined {
  if (typeof value !== "object" || value === null) {
    return undefined;
  }

  const raw = value as Record<string, unknown>;
  const roles = normalizeList(raw.roles);
  const groups = normalizeList(raw.groups);
  const policyRef = normalizePolicyRef(raw.policyRef);

  const normalized: AccessControlMetadata = {
    ...(roles ? { roles } : {}),
    ...(groups ? { groups } : {}),
    ...(policyRef ? { policyRef } : {}),
  };

  return Object.keys(normalized).length > 0 ? normalized : undefined;
}

export function validateAccessControlMetadata(value: unknown, path: string): string | null {
  if (value === undefined) {
    return null;
  }
  if (typeof value !== "object" || value === null) {
    return `${path} must be an object when present`;
  }

  const raw = value as Record<string, unknown>;

  if (raw.roles !== undefined && !Array.isArray(raw.roles)) {
    return `${path}.roles must be an array of strings when present`;
  }
  if (Array.isArray(raw.roles) && raw.roles.some((item) => typeof item !== "string")) {
    return `${path}.roles must be an array of strings when present`;
  }

  if (raw.groups !== undefined && !Array.isArray(raw.groups)) {
    return `${path}.groups must be an array of strings when present`;
  }
  if (Array.isArray(raw.groups) && raw.groups.some((item) => typeof item !== "string")) {
    return `${path}.groups must be an array of strings when present`;
  }

  if (raw.policyRef !== undefined && typeof raw.policyRef !== "string") {
    return `${path}.policyRef must be a string when present`;
  }

  return null;
}
