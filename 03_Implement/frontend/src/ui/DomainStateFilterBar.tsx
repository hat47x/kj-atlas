import type { DomainStateFilter } from "../domain/domain_state_filter";
import { t } from "../i18n/translate";

type DomainStateFilterBarProps = {
  filter: DomainStateFilter;
  onFilterChange: (filter: DomainStateFilter) => void;
};

const chipStyle = (active: boolean): React.CSSProperties => ({
  border: active ? "2px solid #2563eb" : "1px solid #cbd5e1",
  borderRadius: 999,
  backgroundColor: active ? "#dbeafe" : "#ffffff",
  color: active ? "#1d4ed8" : "#475569",
  fontSize: 11,
  fontWeight: active ? 700 : 400,
  padding: "2px 8px",
  cursor: "pointer",
  whiteSpace: "nowrap",
  lineHeight: "18px",
});

export function DomainStateFilterBar({ filter, onFilterChange }: DomainStateFilterBarProps) {
  const claimTypeLabels = {
    fact: t("domain_filter.claim_type.fact"),
    claim: t("domain_filter.claim_type.claim"),
    hypothesis: t("domain_filter.claim_type.hypothesis"),
  };

  const toggleClaimType = (ct: "fact" | "claim" | "hypothesis") => {
    const current = filter.claimTypes ?? [];
    const next = current.includes(ct) ? current.filter((c) => c !== ct) : [...current, ct];
    onFilterChange({ ...filter, claimTypes: next.length > 0 ? next : undefined });
  };

  const toggleBool = (key: "unreviewedOnly" | "hasCritique") => {
    const current = filter[key] ?? false;
    onFilterChange({ ...filter, [key]: current ? undefined : true });
  };

  const hasActiveClaimFilter = (filter.claimTypes?.length ?? 0) > 0;

  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        gap: 4,
        padding: "6px 0",
        borderBottom: "1px solid #e2e8f0",
        marginBottom: 6,
      }}
    >
      <span style={{ fontSize: 10, fontWeight: 600, color: "#94a3b8", marginRight: 4, lineHeight: "20px" }}>
        {t("domain_filter.label")}
      </span>
      {(["fact", "claim", "hypothesis"] as const).map((ct) => (
        <button
          key={ct}
          type="button"
          onClick={() => toggleClaimType(ct)}
          style={chipStyle(filter.claimTypes?.includes(ct) ?? false)}
        >
          {claimTypeLabels[ct]}
        </button>
      ))}
      <button
        type="button"
        onClick={() => toggleBool("unreviewedOnly")}
        style={chipStyle(filter.unreviewedOnly ?? false)}
      >
        {t("domain_filter.unreviewed_only")}
      </button>
      <button
        type="button"
        onClick={() => toggleBool("hasCritique")}
        style={chipStyle(filter.hasCritique ?? false)}
      >
        {t("domain_filter.has_critique")}
      </button>
      {hasActiveClaimFilter || filter.unreviewedOnly || filter.hasCritique ? (
        <button
          type="button"
          onClick={() => onFilterChange({})}
          style={{
            border: "none",
            backgroundColor: "transparent",
            color: "#ef4444",
            fontSize: 10,
            cursor: "pointer",
            padding: "2px 4px",
          }}
        >
          {t("domain_filter.clear")}
        </button>
      ) : null}
    </div>
  );
}
