import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DomainStateFilterBar } from "./DomainStateFilterBar";
import { setActiveLocale } from "../i18n/translate";

afterEach(() => {
  setActiveLocale("ja");
});

describe("DomainStateFilterBar", () => {
  it("renders filter label and toggle buttons", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(
      createElement(DomainStateFilterBar, {
        filter: {},
        onFilterChange: vi.fn(),
      })
    );
    expect(html).toContain("Filter:");
    expect(html).toContain("Fact");
    expect(html).toContain("Claim");
    expect(html).toContain("Hypothesis");
    expect(html).toContain("unreviewed");
    expect(html).toContain("critique");
  });

  it("renders Japanese claim-type labels without internal enum values", () => {
    setActiveLocale("ja");
    const html = renderToStaticMarkup(
      createElement(DomainStateFilterBar, {
        filter: {},
        onFilterChange: vi.fn(),
      })
    );

    expect(html).toContain("事実");
    expect(html).toContain("主張");
    expect(html).toContain("仮説");
    expect(html).not.toContain(">fact<");
    expect(html).not.toContain(">claim<");
    expect(html).not.toContain(">hypothesis<");
  });

  it("highlights active filter chips with blue border", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(
      createElement(DomainStateFilterBar, {
        filter: { claimTypes: ["fact"], unreviewedOnly: true },
        onFilterChange: vi.fn(),
      })
    );
    expect(html).toContain("2px solid #2563eb");
  });

  it("shows clear button when any filter is active", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(
      createElement(DomainStateFilterBar, {
        filter: { unreviewedOnly: true },
        onFilterChange: vi.fn(),
      })
    );
    expect(html).toContain("clear");
  });

  it("shows no clear button when no filter active", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(
      createElement(DomainStateFilterBar, {
        filter: {},
        onFilterChange: vi.fn(),
      })
    );
    expect(html).not.toContain("clear");
  });
});
