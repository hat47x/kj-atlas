#!/usr/bin/env python3
"""Deterministic projection formatters for D0 query selections."""

from __future__ import annotations

import copy
from typing import Any

from query_engine import D0Network


class D0ProjectionError(ValueError):
    pass


D0_FORMS = {
    "subgraph",
    "path_list",
    "card_stack",
    "comparison_table",
    "spatial_layout",
    "timeline",
    "provenance_matrix",
}


def _base(result: dict[str, Any], form: str) -> dict[str, Any]:
    return {
        "queryIntent": result.get("intent"),
        "projectionForm": form,
        "selectedNodeRefs": list(result.get("selectedNodeRefs", [])),
        "selectedEdgeRefs": list(result.get("selectedEdgeRefs", [])),
        "selectionTrace": copy.deepcopy(result.get("trace", {})),
    }


def project(network: D0Network, result: dict[str, Any], form: str) -> dict[str, Any]:
    if form == "compact_narrative":
        raise D0ProjectionError("compact_narrative belongs to D4, not deterministic D0")
    if form not in D0_FORMS:
        raise D0ProjectionError(f"unsupported D0 projection form: {form}")
    if not isinstance(result, dict) or not result.get("intent"):
        raise D0ProjectionError("result must be a D0 query result")

    output = _base(result, form)
    selected = result.get("selectedNodeRefs", [])

    if form == "subgraph":
        output["payload"] = network.subgraph(selected) if selected else {"nodes": [], "edges": []}
        return output

    if form == "card_stack":
        output["payload"] = {
            "cards": [copy.deepcopy(network.nodes[ref]) for ref in selected]
        }
        return output

    if form == "spatial_layout":
        items = []
        for ref in selected:
            node = network.nodes[ref]
            if "x" in node and "y" in node:
                items.append({"ref": ref, "x": node["x"], "y": node["y"]})
        output["payload"] = {
            "items": items,
            "edgeRefs": list(result.get("selectedEdgeRefs", [])),
        }
        return output

    if form == "path_list":
        if result.get("intent") != "bridge":
            raise D0ProjectionError("path_list requires a bridge result")
        output["payload"] = {
            "status": result.get("status"),
            "nodePaths": copy.deepcopy(result.get("nodePaths", [])),
            "edgePaths": copy.deepcopy(result.get("edgePaths", [])),
        }
        return output

    if form == "comparison_table":
        if result.get("intent") != "contrast":
            raise D0ProjectionError("comparison_table requires a contrast result")
        rows = []
        for facet, values in sorted(result.get("facets", {}).items()):
            rows.append(
                {
                    "facet": facet,
                    "shared": list(values.get("shared", [])),
                    "leftOnly": list(values.get("leftOnly", [])),
                    "rightOnly": list(values.get("rightOnly", [])),
                }
            )
        output["payload"] = {
            "leftRefs": list(result.get("leftRefs", [])),
            "rightRefs": list(result.get("rightRefs", [])),
            "rows": rows,
            "crossContradictionRefs": list(result.get("crossContradictionRefs", [])),
        }
        return output

    if form == "timeline":
        if result.get("intent") != "temporal":
            raise D0ProjectionError("timeline requires a temporal result")
        output["payload"] = {"records": copy.deepcopy(result.get("records", []))}
        return output

    if form == "provenance_matrix":
        if result.get("intent") != "provenance":
            raise D0ProjectionError("provenance_matrix requires a provenance result")
        output["payload"] = {
            "bySource": copy.deepcopy(result.get("bySource", {})),
            "byActor": copy.deepcopy(result.get("byActor", {})),
            "missingSourceRefs": list(result.get("missingSourceRefs", [])),
            "sourceMeta": copy.deepcopy(result.get("sourceMeta", {})),
        }
        return output

    raise AssertionError("unreachable projection form")
