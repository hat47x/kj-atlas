import React from "react";
import { describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { setActiveLocale } from "../i18n/translate";
import {
  ModelSelector,
  reconcileModelSelection,
  resolveUnavailableReasonTranslationKey,
} from "./ModelSelector";

// AI-MODEL-GOVERNANCE-01 (R2): the selector is presentational (App owns the
// guarded fetch). It must never block the operation and always expose the
// "auto / default" fallback.

describe("ModelSelector", () => {
  it("clears a selected model that disappeared after an administrator change", () => {
    expect(reconcileModelSelection("disabled-model", [])).toBe("");
    expect(reconcileModelSelection("active-model", [
      { id: "active-model", displayName: "Active", providerId: "local" },
    ])).toBe("active-model");
    expect(reconcileModelSelection("loading-model", null)).toBe("loading-model");
  });

  it("renders a disabled auto-select while models are loading (null)", () => {
    setActiveLocale("ja");
    const html = renderToStaticMarkup(
      React.createElement(ModelSelector, {
        label: "モデル",
        value: "",
        onChange: vi.fn(),
        models: null,
      }),
    );
    expect(html).toContain("自動（既定）");
    expect(html).toContain("disabled");
  });

  it("renders an accessible labelled select with the allowed models", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(
      React.createElement(ModelSelector, {
        label: "Model",
        value: "",
        onChange: vi.fn(),
        dataUiRegion: "model-selector",
        models: [
          { id: "deepseek-chat", displayName: "DeepSeek Chat", providerId: "deepseek" },
          { id: "local-model", displayName: "Local Model", providerId: "local" },
        ],
      }),
    );
    expect(html).toContain("data-ui-region=\"model-selector\"");
    expect(html).toContain("Auto (default)");
    expect(html).toContain("DeepSeek Chat");
    expect(html).toContain("Local Model");
  });

  it("shows an actionable disabled state when the tenant has no available models", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(
      React.createElement(ModelSelector, {
        label: "Model",
        value: "",
        onChange: vi.fn(),
        models: [],
      }),
    );
    expect(html).toContain("No models available");
    expect(html).toContain("Check the administrator model policy or AI connection settings");
    expect(html).toContain("disabled");
    expect(html).toContain("aria-label=\"Model\"");
    expect(html).toContain("role=\"status\"");
  });

  it("explains the safe administrator action for a tenant policy empty state", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(
      React.createElement(ModelSelector, {
        label: "Model",
        value: "",
        onChange: vi.fn(),
        models: [],
        unavailableReason: "tenant_policy_excludes_all",
      }),
    );
    expect(html).toContain("This tenant&#x27;s model policy currently excludes every executable model");
    expect(html).not.toContain("providerId");
  });

  it("falls back safely when the API deploys an unknown reason code first", () => {
    expect(resolveUnavailableReasonTranslationKey("future_reason")).toBe(
      "model_selector.none_available_help",
    );
    expect(resolveUnavailableReasonTranslationKey(null)).toBe(
      "model_selector.none_available_help",
    );
  });
});
