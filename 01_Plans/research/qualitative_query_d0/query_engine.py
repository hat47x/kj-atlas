#!/usr/bin/env python3
"""Deterministic qualitative query engine for synthetic research networks.

D0 intentionally performs no semantic inference and emits no importance,
confidence, or truth score. Query results are derived read-only views.
"""

from __future__ import annotations

import copy
from collections import defaultdict, deque
from typing import Any, Iterable


class D0QueryError(ValueError):
    pass


class D0Network:
    def __init__(self, data: dict[str, Any]):
        if not isinstance(data, dict):
            raise D0QueryError("network must be an object")
        self._data = copy.deepcopy(data)
        self.network_id = self._require_string(data.get("networkId"), "networkId")
        self.nodes = self._index(data.get("nodes"), "nodes")
        self.edges = self._index(data.get("edges"), "edges")
        self.critiques = self._index(data.get("critiques", []), "critiques")
        self.contradictions = self._index(data.get("contradictions", []), "contradictions")
        self.events = self._index(data.get("events", []), "events")
        self.sources = self._index(data.get("sources", []), "sources")
        self._validate_refs()
        self._adjacency = self._build_adjacency()
        self._incident_edges = self._build_incident_edges()
        self._island_members = self._build_island_members()
        self._critique_by_target = self._build_critique_by_target()
        self._contradiction_by_target = self._build_contradiction_by_target()

    @staticmethod
    def _require_string(value: Any, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise D0QueryError(f"{field} must be a non-empty string")
        return value.strip()

    def _index(self, value: Any, field: str) -> dict[str, dict[str, Any]]:
        if not isinstance(value, list):
            raise D0QueryError(f"{field} must be a list")
        out: dict[str, dict[str, Any]] = {}
        for item in value:
            if not isinstance(item, dict):
                raise D0QueryError(f"{field} items must be objects")
            item_id = self._require_string(item.get("id"), f"{field}.id")
            if item_id in out:
                raise D0QueryError(f"duplicate {field} id: {item_id}")
            out[item_id] = copy.deepcopy(item)
        return out

    def _validate_refs(self) -> None:
        for edge in self.edges.values():
            for key in ("fromId", "toId"):
                ref = self._require_string(edge.get(key), f"edge.{key}")
                if ref not in self.nodes:
                    raise D0QueryError(f"edge references unknown node: {ref}")
            if not isinstance(edge.get("directed"), bool):
                raise D0QueryError("edge.directed must be boolean")
        for critique in self.critiques.values():
            ref = self._require_string(critique.get("targetRef"), "critique.targetRef")
            if ref not in self.nodes:
                raise D0QueryError(f"critique references unknown node: {ref}")
        for contradiction in self.contradictions.values():
            for key in ("fromId", "toId"):
                ref = self._require_string(contradiction.get(key), f"contradiction.{key}")
                if ref not in self.nodes:
                    raise D0QueryError(f"contradiction references unknown node: {ref}")
        for node in self.nodes.values():
            for source_ref in node.get("sourceRefs", []):
                if source_ref not in self.sources:
                    raise D0QueryError(f"node references unknown source: {source_ref}")

    def _build_adjacency(self) -> dict[str, list[str]]:
        adjacency: dict[str, set[str]] = {node_id: set() for node_id in self.nodes}
        for edge in self.edges.values():
            a, b = edge["fromId"], edge["toId"]
            adjacency[a].add(b)
            if not edge["directed"]:
                adjacency[b].add(a)
        return {node_id: sorted(values) for node_id, values in adjacency.items()}

    def _build_incident_edges(self) -> dict[str, list[str]]:
        incident: dict[str, list[str]] = {node_id: [] for node_id in self.nodes}
        for edge_id, edge in self.edges.items():
            incident[edge["fromId"]].append(edge_id)
            incident[edge["toId"]].append(edge_id)
        return {node_id: sorted(values) for node_id, values in incident.items()}

    def _build_island_members(self) -> dict[str, list[str]]:
        groups: dict[str, list[str]] = defaultdict(list)
        for node_id, node in self.nodes.items():
            island_id = node.get("islandId")
            if isinstance(island_id, str) and island_id:
                groups[island_id].append(node_id)
        return {key: sorted(values) for key, values in groups.items()}

    def _build_critique_by_target(self) -> dict[str, list[str]]:
        values: dict[str, list[str]] = defaultdict(list)
        for critique_id, critique in self.critiques.items():
            values[critique["targetRef"]].append(critique_id)
        return {key: sorted(items) for key, items in values.items()}

    def _build_contradiction_by_target(self) -> dict[str, list[str]]:
        values: dict[str, list[str]] = defaultdict(list)
        for contradiction_id, contradiction in self.contradictions.items():
            values[contradiction["fromId"]].append(contradiction_id)
            values[contradiction["toId"]].append(contradiction_id)
        return {key: sorted(items) for key, items in values.items()}

    def snapshot(self) -> dict[str, Any]:
        return copy.deepcopy(self._data)

    def _require_node_refs(self, refs: Iterable[str], field: str) -> list[str]:
        result = sorted(set(refs))
        if not result:
            raise D0QueryError(f"{field} must not be empty")
        unknown = [ref for ref in result if ref not in self.nodes]
        if unknown:
            raise D0QueryError(f"{field} contains unknown node refs: {unknown}")
        return result

    def _induced_edge_refs(self, node_refs: Iterable[str]) -> list[str]:
        selected = set(node_refs)
        return sorted(
            edge_id
            for edge_id, edge in self.edges.items()
            if edge["fromId"] in selected and edge["toId"] in selected
        )

    def neighborhood(self, focus_refs: Iterable[str], depth: int = 1) -> dict[str, Any]:
        focus = self._require_node_refs(focus_refs, "focusRefs")
        if not isinstance(depth, int) or depth < 0 or depth > 5:
            raise D0QueryError("depth must be an integer from 0 to 5")

        distance: dict[str, int] = {ref: 0 for ref in focus}
        queue = deque(focus)
        while queue:
            current = queue.popleft()
            if distance[current] >= depth:
                continue
            for neighbor in self._adjacency[current]:
                next_distance = distance[current] + 1
                if neighbor not in distance or next_distance < distance[neighbor]:
                    distance[neighbor] = next_distance
                    queue.append(neighbor)

        selected_nodes = sorted(distance)
        return {
            "intent": "neighborhood",
            "focusRefs": focus,
            "selectedNodeRefs": selected_nodes,
            "selectedEdgeRefs": self._induced_edge_refs(selected_nodes),
            "distanceByRef": {ref: distance[ref] for ref in selected_nodes},
            "trace": {"networkId": self.network_id, "method": "explicit_relation_bfs"},
        }

    def _facet_values(self, refs: list[str]) -> dict[str, set[str]]:
        facets: dict[str, set[str]] = {
            "sources": set(),
            "actors": set(),
            "islands": set(),
            "holdStates": set(),
            "reviewStates": set(),
            "edgeTypes": set(),
        }
        for ref in refs:
            node = self.nodes[ref]
            facets["sources"].update(node.get("sourceRefs", []))
            facets["actors"].update(node.get("actorRefs", []))
            if node.get("islandId"):
                facets["islands"].add(node["islandId"])
            if node.get("holdState"):
                facets["holdStates"].add(node["holdState"])
            if node.get("reviewState"):
                facets["reviewStates"].add(node["reviewState"])
            for edge_id in self._incident_edges[ref]:
                edge_type = self.edges[edge_id].get("type")
                if isinstance(edge_type, str) and edge_type:
                    facets["edgeTypes"].add(edge_type)
        return facets

    def contrast(self, left_refs: Iterable[str], right_refs: Iterable[str]) -> dict[str, Any]:
        left = self._require_node_refs(left_refs, "leftRefs")
        right = self._require_node_refs(right_refs, "rightRefs")
        left_facets = self._facet_values(left)
        right_facets = self._facet_values(right)
        facets: dict[str, dict[str, list[str]]] = {}
        for facet in sorted(left_facets):
            a, b = left_facets[facet], right_facets[facet]
            facets[facet] = {
                "shared": sorted(a & b),
                "leftOnly": sorted(a - b),
                "rightOnly": sorted(b - a),
            }

        left_set, right_set = set(left), set(right)
        cross_contradictions = sorted(
            contradiction_id
            for contradiction_id, item in self.contradictions.items()
            if (
                item["fromId"] in left_set and item["toId"] in right_set
            )
            or (
                item["toId"] in left_set and item["fromId"] in right_set
            )
        )
        selected_nodes = sorted(left_set | right_set)
        return {
            "intent": "contrast",
            "leftRefs": left,
            "rightRefs": right,
            "selectedNodeRefs": selected_nodes,
            "selectedEdgeRefs": self._induced_edge_refs(selected_nodes),
            "facets": facets,
            "crossContradictionRefs": cross_contradictions,
            "trace": {"networkId": self.network_id, "method": "set_and_structural_difference"},
        }

    def _shortest_distances(self, start: str, max_depth: int) -> dict[str, int]:
        distance = {start: 0}
        queue = deque([start])
        while queue:
            current = queue.popleft()
            if distance[current] >= max_depth:
                continue
            for neighbor in self._adjacency[current]:
                if neighbor not in distance:
                    distance[neighbor] = distance[current] + 1
                    queue.append(neighbor)
        return distance

    def _edge_ref_between(self, a: str, b: str) -> str:
        candidates = []
        for edge_id in self._incident_edges[a]:
            edge = self.edges[edge_id]
            if edge["fromId"] == a and edge["toId"] == b:
                candidates.append(edge_id)
            elif not edge["directed"] and edge["fromId"] == b and edge["toId"] == a:
                candidates.append(edge_id)
        if not candidates:
            raise D0QueryError(f"no traversable edge between {a} and {b}")
        return sorted(candidates)[0]

    def bridge(self, from_ref: str, to_ref: str, max_depth: int = 5, max_paths: int = 8) -> dict[str, Any]:
        start = self._require_node_refs([from_ref], "fromRef")[0]
        goal = self._require_node_refs([to_ref], "toRef")[0]
        if start == goal:
            paths = [[start]]
        else:
            if not isinstance(max_depth, int) or max_depth < 1 or max_depth > 8:
                raise D0QueryError("maxDepth must be an integer from 1 to 8")
            if not isinstance(max_paths, int) or max_paths < 1 or max_paths > 32:
                raise D0QueryError("maxPaths must be an integer from 1 to 32")
            distance = self._shortest_distances(start, max_depth)
            if goal not in distance:
                paths = []
            else:
                target_distance = distance[goal]
                paths: list[list[str]] = []

                def walk(path: list[str]) -> None:
                    if len(paths) >= max_paths:
                        return
                    current = path[-1]
                    if current == goal:
                        paths.append(path[:])
                        return
                    for neighbor in self._adjacency[current]:
                        if distance.get(neighbor) != distance[current] + 1:
                            continue
                        if distance[neighbor] > target_distance or neighbor in path:
                            continue
                        walk(path + [neighbor])

                walk([start])
                paths.sort()

        edge_paths = [
            [self._edge_ref_between(path[i], path[i + 1]) for i in range(len(path) - 1)]
            for path in paths
        ]
        selected_nodes = sorted({ref for path in paths for ref in path})
        selected_edges = sorted({ref for path in edge_paths for ref in path})
        return {
            "intent": "bridge",
            "fromRef": start,
            "toRef": goal,
            "status": "explicit_paths_found" if paths else "no_explicit_path",
            "nodePaths": paths,
            "edgePaths": edge_paths,
            "selectedNodeRefs": selected_nodes,
            "selectedEdgeRefs": selected_edges,
            "trace": {"networkId": self.network_id, "method": "explicit_shortest_paths"},
        }

    def residual(self, scope_refs: Iterable[str] | None = None) -> dict[str, Any]:
        scope = sorted(self.nodes) if scope_refs is None else self._require_node_refs(scope_refs, "scopeRefs")
        items = []
        for ref in scope:
            node = self.nodes[ref]
            reasons: list[str] = []
            island_id = node.get("islandId")
            if island_id and len(self._island_members.get(island_id, [])) == 1:
                reasons.append("singleton_island")
            if node.get("holdState") in {"held", "pending", "shelved"}:
                reasons.append("held_or_pending")
            if any(self.critiques[cid].get("state") != "resolved" for cid in self._critique_by_target.get(ref, [])):
                reasons.append("has_critique")
            if not self._incident_edges[ref]:
                reasons.append("unconnected")
            if any(
                self.contradictions[cid].get("state") != "resolved"
                for cid in self._contradiction_by_target.get(ref, [])
            ):
                reasons.append("unresolved_contradiction")
            if not node.get("sourceRefs"):
                reasons.append("missing_provenance")
            if reasons:
                items.append({"ref": ref, "reasons": sorted(reasons)})
        selected_nodes = [item["ref"] for item in items]
        return {
            "intent": "residual",
            "selectedNodeRefs": selected_nodes,
            "selectedEdgeRefs": self._induced_edge_refs(selected_nodes),
            "items": items,
            "trace": {"networkId": self.network_id, "method": "explicit_residual_reasons"},
        }

    def unresolved(self, scope_refs: Iterable[str] | None = None) -> dict[str, Any]:
        scope = sorted(self.nodes) if scope_refs is None else self._require_node_refs(scope_refs, "scopeRefs")
        scope_set = set(scope)
        items: list[dict[str, Any]] = []
        for ref in scope:
            node = self.nodes[ref]
            reasons: list[str] = []
            if node.get("holdState") in {"held", "pending", "shelved"}:
                reasons.append(f"hold:{node['holdState']}")
            if node.get("reviewState") == "unreviewed":
                reasons.append("review:unreviewed")
            open_critiques = sorted(
                cid
                for cid in self._critique_by_target.get(ref, [])
                if self.critiques[cid].get("state") != "resolved"
            )
            if open_critiques:
                reasons.append("critique:open")
            if reasons:
                items.append({"ref": ref, "reasons": sorted(reasons), "critiqueRefs": open_critiques})

        contradiction_refs = sorted(
            cid
            for cid, item in self.contradictions.items()
            if item.get("state") != "resolved"
            and item["fromId"] in scope_set
            and item["toId"] in scope_set
        )
        selected_nodes = sorted(
            set(item["ref"] for item in items)
            | {
                endpoint
                for cid in contradiction_refs
                for endpoint in (self.contradictions[cid]["fromId"], self.contradictions[cid]["toId"])
            }
        )
        return {
            "intent": "unresolved",
            "selectedNodeRefs": selected_nodes,
            "selectedEdgeRefs": self._induced_edge_refs(selected_nodes),
            "items": items,
            "contradictionRefs": contradiction_refs,
            "trace": {"networkId": self.network_id, "method": "explicit_unresolved_states"},
        }

    def temporal(self, scope_refs: Iterable[str] | None = None) -> dict[str, Any]:
        scope = set(self.nodes if scope_refs is None else self._require_node_refs(scope_refs, "scopeRefs"))
        records: list[dict[str, Any]] = []
        for ref in sorted(scope):
            node = self.nodes[ref]
            if node.get("observedAt"):
                records.append({"at": node["observedAt"], "kind": "node_observed", "ref": ref})
        for edge_id, edge in self.edges.items():
            if edge["fromId"] in scope and edge["toId"] in scope and edge.get("createdAt"):
                records.append({"at": edge["createdAt"], "kind": "edge_created", "ref": edge_id})
        for critique_id, critique in self.critiques.items():
            if critique["targetRef"] in scope and critique.get("createdAt"):
                records.append({"at": critique["createdAt"], "kind": "critique_recorded", "ref": critique_id})
        for contradiction_id, item in self.contradictions.items():
            if item["fromId"] in scope and item["toId"] in scope and item.get("createdAt"):
                records.append({"at": item["createdAt"], "kind": "contradiction_recorded", "ref": contradiction_id})
        for event_id, event in self.events.items():
            targets = set(event.get("targetRefs", []))
            if targets & scope:
                records.append({
                    "at": event.get("at", ""),
                    "kind": event.get("kind", "event"),
                    "ref": event_id,
                    "targetRefs": sorted(targets),
                    "actorRef": event.get("actorRef"),
                    "sourceRef": event.get("sourceRef"),
                })
        records.sort(key=lambda item: (item.get("at", ""), item.get("kind", ""), item.get("ref", "")))
        selected_nodes = sorted(scope)
        return {
            "intent": "temporal",
            "selectedNodeRefs": selected_nodes,
            "selectedEdgeRefs": self._induced_edge_refs(selected_nodes),
            "records": records,
            "trace": {"networkId": self.network_id, "method": "explicit_timestamp_order"},
        }

    def provenance(self, scope_refs: Iterable[str] | None = None) -> dict[str, Any]:
        scope = sorted(self.nodes) if scope_refs is None else self._require_node_refs(scope_refs, "scopeRefs")
        by_source: dict[str, list[str]] = defaultdict(list)
        by_actor: dict[str, list[str]] = defaultdict(list)
        missing_source_refs: list[str] = []
        for ref in scope:
            node = self.nodes[ref]
            sources = sorted(set(node.get("sourceRefs", [])))
            actors = sorted(set(node.get("actorRefs", [])))
            if not sources:
                missing_source_refs.append(ref)
            for source_ref in sources:
                by_source[source_ref].append(ref)
            for actor_ref in actors:
                by_actor[actor_ref].append(ref)
        return {
            "intent": "provenance",
            "selectedNodeRefs": scope,
            "selectedEdgeRefs": self._induced_edge_refs(scope),
            "bySource": {key: sorted(values) for key, values in sorted(by_source.items())},
            "byActor": {key: sorted(values) for key, values in sorted(by_actor.items())},
            "missingSourceRefs": sorted(missing_source_refs),
            "sourceMeta": {key: copy.deepcopy(self.sources[key]) for key in sorted(by_source)},
            "trace": {"networkId": self.network_id, "method": "explicit_provenance_grouping"},
        }

    def subgraph(self, node_refs: Iterable[str]) -> dict[str, Any]:
        refs = self._require_node_refs(node_refs, "nodeRefs")
        edge_refs = self._induced_edge_refs(refs)
        return {
            "nodes": [copy.deepcopy(self.nodes[ref]) for ref in refs],
            "edges": [copy.deepcopy(self.edges[ref]) for ref in edge_refs],
        }
