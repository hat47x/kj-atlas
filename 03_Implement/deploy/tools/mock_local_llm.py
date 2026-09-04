#!/usr/bin/env python3
"""Deterministic mock ``/generate`` server for kj-atlas local-LLM (GPU-free) demos.

kj-atlas's local provider (``KJ_ATLAS_LLM_PROVIDER=local``) POSTs to
``{base_url}/generate`` a body ``{"task","prompt","temperature","max_tokens","model"}``
and expects ``{"text": "<JSON>"}`` where ``<JSON>`` is a *string* whose contents match
the strict per-task schema the API then validates. Small CPU-only models rarely emit
that exact JSON reliably, so this stub returns minimal VALID responses per task — letting
you SEE the AI-assisted UI flow without a GPU or a real model.

This is NOT an LLM. Layout is a plain grid, summaries/narratives are canned drafts, and
merge/issue suggestions are empty. Use it only to demonstrate the operational feel.

Usage:
    python3 mock_local_llm.py                       # 127.0.0.1:8001
    python3 mock_local_llm.py --host 0.0.0.0 --port 8001

Then point kj-atlas at it:
    export KJ_ATLAS_LLM_PROVIDER=local
    export KJ_ATLAS_LOCAL_LLM_BASE_URL=http://localhost:8001
    export KJ_ATLAS_LOCAL_LLM_MODEL=mock
"""
from __future__ import annotations

import argparse
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Card lines in the layout / island-summary prompts:  - id="<id>", text=...
# (island lines use `, title=` instead of `, text=`, so they are not matched.)
_CARD_LINE = re.compile(r'^\s*- id="([^"]+)", text=', re.MULTILINE)
# Reading-order lines in the narrative prompt:  - 1. card id="<id>", ...
_READING_ORDER_LINE = re.compile(r'^- \d+\. \w+ id="([^"]+)"', re.MULTILINE)
# Reading-order island lines in the narrative prompt:  - 1. island id="<id>", ...
_READING_ORDER_ISLAND_LINE = re.compile(r'^- \d+\. island id="([^"]+)"', re.MULTILINE)
# Island section lines in the narrative prompt:  - id="<id>", title=..., ...
_ISLAND_LINE = re.compile(r'^- id="([^"]+)", title=', re.MULTILINE)
# Allowed grounding lists in the relation-summary prompt:
#   allowed groundingCardIds=["z4"]   /   allowed groundingEdgeIds=[]
_ALLOWED_GROUNDING_CARD_LIST = re.compile(r'^allowed groundingCardIds=(\[.*\])$', re.MULTILINE)
_ALLOWED_GROUNDING_EDGE_LIST = re.compile(r'^allowed groundingEdgeIds=(\[.*\])$', re.MULTILINE)
# Refine-card-text input line:  Card text: <text>  (context follows on its own line)
_CARD_TEXT_INPUT = re.compile(r'^Card text: (.*)$', re.MULTILINE)
# Opposing-viewpoint target card line:  Target card: {"id": "...", "text": "..."}
_OPPOSING_TARGET_CARD = re.compile(r'^Target card: (\{.*\})$', re.MULTILINE)
# First island-label line in the title-suggestion prompt:  Island labels:\n  - <label>
_TITLE_ISLAND_LINE = re.compile(r'^Island labels:\n  - (.+)$', re.MULTILINE)
# All island-label lines in the title-suggestion prompt:  Island labels:\n  - <label>...
_TITLE_ISLAND_SECTION = re.compile(r'^Island labels:\n((?:  - .+\n?)*)', re.MULTILINE)
# Detect-contradiction prompt card lines:  Card A (id=..): <text> / Card B (id=..): <text>
_CARD_A_TEXT = re.compile(r'^Card A \(id=[^)]+\): (.*)$', re.MULTILINE)
_CARD_B_TEXT = re.compile(r'^Card B \(id=[^)]+\): (.*)$', re.MULTILINE)
# Relation-summary prompt island ids:  islandAId="<id>", islandBId="<id>"
_ISLAND_A_ID = re.compile(r'islandAId="([^"]+)"')
_ISLAND_B_ID = re.compile(r'islandBId="([^"]+)"')
# Card lines with text in the merge prompt:  - id="<id>", text="<text>"
_CARD_LINE_ID_TEXT = re.compile(r'^\s*- id="([^"]+)", text="([^"]*)"', re.MULTILINE)

_GRID_COLUMNS = 4
_GRID_SPACING_X = 280
_GRID_SPACING_Y = 160


def build_text_for_task(task: str, prompt: str) -> str:
    """Return the stringified per-task JSON the kj-atlas API will ``json.loads(text)``."""
    if task == "re_layout":
        card_ids = _CARD_LINE.findall(prompt)
        cards = [
            {
                "id": card_id,
                "x": (index % _GRID_COLUMNS) * _GRID_SPACING_X,
                "y": (index // _GRID_COLUMNS) * _GRID_SPACING_Y,
            }
            for index, card_id in enumerate(card_ids)
        ]
        return json.dumps({"transform": {"panX": 0, "panY": 0, "zoom": 1}, "cards": cards})

    if task == "suggest_merges":
        # Deterministic merge positive path (iteration 184, DOGFOOD-19): cards
        # sharing a (カテゴリ) segment in their text are suggested as a merge.
        # Previously the mock always returned empty suggestions, so the E2E could
        # never freeze that merge candidates are ever produced.
        card_entries = _CARD_LINE_ID_TEXT.findall(prompt)
        by_category: dict[str, list[str]] = {}
        for card_id, text in card_entries:
            cats = re.findall(r"（([^（）]+)）", text)
            cat = cats[-1] if cats else "その他"
            by_category.setdefault(cat, []).append(card_id)
        suggestions = []
        for cat, ids in by_category.items():
            if len(ids) >= 2:
                suggestions.append(
                    {
                        "groupId": f"g-{cat}",
                        "cardIds": ids,
                        "mergedTextDraft": f"（モック）{cat}が共通するカードの統合案",
                        "mergeMethod": "near_duplicate",
                        "rationale": f"{cat}をテーマとするカードの統合を提案",
                    }
                )
        return json.dumps({"suggestions": suggestions[:10]})

    if task == "suggest_island_summary":
        member_ids = _CARD_LINE.findall(prompt)
        # Ground EVERY member card, not the first 3 — the prompt carries exactly
        # the target island's members, and a [:3] truncation silently caps the
        # E2E to 3-card islands, so realistic multi-card islands (4+ cards) could
        # never be frozen with full grounding assertions (iteration 178, DOGFOOD-13).
        # Cap at 10 to match the backend's groundingIds quality guard
        # (routes/ai.py: a placard grounds to a representative subset, not all
        # members of a very large island). Small islands (<=10) still ground all
        # members; large islands (>10) ground the first 10 as the representative
        # subset (iteration 240, DOGFOOD-31).
        grounding = member_ids[:10] if member_ids else []
        # Reference the member card themes in the placard text so the E2E can
        # freeze that the 表札 (island advocacy) is grounded in the island's
        # content, not just the groundingIds (iteration 193, DOGFOOD-29).
        member_entries = _CARD_LINE_ID_TEXT.findall(prompt)
        themes: list[str] = []
        for card_id, raw_text in member_entries:
            # The island-summary prompt JSON-encodes card texts (json.dumps →
            # \uXXXX escapes), so decode before extracting the (カテゴリ) theme.
            try:
                text = json.loads(f'"{raw_text}"')
            except ValueError:
                text = raw_text
            cats = re.findall(r"（([^（）]+)）", text)
            if cats and cats[-1] not in themes:
                themes.append(cats[-1])
        theme_text = ", ".join(themes)
        base = theme_text if theme_text else "メンバーカード"
        # DOGFOOD-34 (壁打ち): when the user supplied a 違和感, reflect that the
        # regenerated candidates ADDRESS it (deterministic marker for E2E).
        critique_suffix = ""
        if re.search(r"raised this objection \(違和感\) to the current placard", prompt):
            critique_suffix = "（違和感を反映）"
        # ADR-0077: return multiple placard candidates (1-3) so the E2E can
        # freeze the condensation layer (核融合法). candidates[0] keeps the
        # primary grounding (member_ids[:10], above) so the existing
        # `"groundingIds":[...]` assertions stay intact; alternatives ground to
        # a different representative subset.
        candidates = [
            {
                "summaryText": f"（モック）{base}をテーマとするメンバーカードに基づく下書き要約です。レビュー前の暫定です。{critique_suffix}",
                "groundingIds": grounding,
            },
            {
                "summaryText": f"（モック）{base}という共通の訴えを軸に志を汲み取った別案です。レビュー前の暫定です。{critique_suffix}",
                "groundingIds": member_ids[:3] if len(member_ids) >= 3 else member_ids,
            },
            {
                "summaryText": f"（モック）{base}の観点から島の訴えを一言で表す候補です。レビュー前の暫定です。{critique_suffix}",
                "groundingIds": member_ids[-3:] if len(member_ids) >= 3 else member_ids,
            },
        ]
        return json.dumps({"candidates": candidates, "warnings": []})

    if task == "summarize_island_relation":
        # Echo the allowed grounding ids (iteration 180, DOGFOOD-15): the mock
        # previously always returned empty grounding, so the business-flow E2E
        # could never freeze that a relation summary is grounded to its basis
        # cards/edges (a regression dropping grounding would pass every check).
        # Also reference the island A/B ids in the text so the E2E can freeze
        # that the summary names WHICH islands it relates (not just the grounding)
        # (iteration 192, DOGFOOD-28).
        grounding_cards: list[str] = []
        grounding_edges: list[str] = []
        card_match = _ALLOWED_GROUNDING_CARD_LIST.search(prompt)
        edge_match = _ALLOWED_GROUNDING_EDGE_LIST.search(prompt)
        if card_match:
            try:
                parsed = json.loads(card_match.group(1))
            except ValueError:
                parsed = []
            grounding_cards = parsed if isinstance(parsed, list) else []
        if edge_match:
            try:
                parsed = json.loads(edge_match.group(1))
            except ValueError:
                parsed = []
            grounding_edges = parsed if isinstance(parsed, list) else []
        island_a_match = _ISLAND_A_ID.search(prompt)
        island_b_match = _ISLAND_B_ID.search(prompt)
        island_a = island_a_match.group(1) if island_a_match else ""
        island_b = island_b_match.group(1) if island_b_match else ""
        return json.dumps(
            {
                "text": f"（モック）島{island_a}と島{island_b}の関係に関する下書きの示唆です。確証ではありません。",
                "groundingCardIds": grounding_cards,
                "groundingEdgeIds": grounding_edges,
                "warnings": [],
            }
        )

    if task == "generate_narrative":
        order_ids = _READING_ORDER_LINE.findall(prompt)
        # Name the reading-order islands inside the narrative text so the E2E can
        # freeze that the narrative actually covers its declared source islands
        # (not just the basedOnReadingOrder declaration). Previously the text was
        # the same generic string for every document (iteration 186, DOGFOOD-21).
        order_text = ", ".join(order_ids) if order_ids else "(none)"
        return json.dumps(
            {
                "text": f"（モック・未レビュー）読み順（{order_text}）に沿った解釈の下書きです。事実の主張ではありません。",
                "basedOnReadingOrder": order_ids,
                "warnings": [],
            }
        )

    if task == "check_narrative":
        # Deterministic A/B mismatch paths (iteration 99 / 179, DOGFOOD-14):
        # the narrative carries marker phrases that deterministically trigger the
        # b_missing_in_a / a_missing_in_b directions, so the business-flow E2E
        # freezes BOTH A/B cross-check directions (kj_technique.md §5) — not just
        # a_missing_in_b. Without the b_missing_in_a path the E2E could never
        # verify that narrative-claims-not-in-the-diagram are reported.
        if "根拠のない主張" in prompt:
            return json.dumps({
                "issues": [{
                    "severity": "info",
                    "message": "ナラティブがカードの根拠を欠く主張を含む（b_missing_in_a）",
                    "direction": "b_missing_in_a",
                }],
                "counts": {"bMissingInA": 1, "aMissingInB": 0},
            })
        if "未検証の主張" in prompt:
            # Reference EVERY reading-order island (falling back to the island
            # section) as a_missing_in_b — the narrative draft is free text and
            # never contains island ids, so a deterministic mock cannot know which
            # island the narrative mentions; reporting all islands lets the E2E
            # freeze that MULTI-island omissions (not just the first island) are
            # surfaced (iteration 189, DOGFOOD-25). Also keeps DOGFOOD-12's
            # island-id independence (no hardcoded "i1").
            island_ids = _READING_ORDER_ISLAND_LINE.findall(prompt) or _ISLAND_LINE.findall(prompt)
            if not island_ids:
                return json.dumps({"issues": []})
            references = [{"id": iid, "kind": "island"} for iid in island_ids]
            return json.dumps({
                "issues": [{
                    "severity": "info",
                    "message": f"ナラティブが島{', '.join(island_ids)}に触れていない（a_missing_in_b）",
                    "references": references,
                    "direction": "a_missing_in_b",
                }],
                "counts": {"bMissingInA": 0, "aMissingInB": len(island_ids)},
            })
        return json.dumps({"issues": []})

    # ADR-0064: KJ-method card-level operations
    if task == "refine_card_text":
        # Embed the input card text so the E2E can freeze that refinement
        # PRESERVES the original meaning (qualitative_card_quality_requirements).
        # Previously the mock returned the same canned text for every input, so
        # the business-flow E2E could never verify meaning preservation
        # (iteration 181, DOGFOOD-16).
        card_text = ""
        match = _CARD_TEXT_INPUT.search(prompt)
        if match:
            card_text = match.group(1).strip()
        return json.dumps({
            "refinedText": f"（モック）カード文面の改善提案です。元の意味（{card_text}）を保持しつつ明確化しています。",
            "reasoning": "同義語の選択と冗長表現の除去により可読性を向上。"})
    if task == "suggest_card_groups":
        card_entries = _CARD_LINE_ID_TEXT.findall(prompt)
        card_ids = [card_id for card_id, _ in card_entries]
        if len(card_ids) < 2:
            return json.dumps({"groups": []})
        # Group by the (カテゴリ) theme segment when 2+ themes exist, so the E2E
        # can freeze that bundling follows theme similarity (kj_technique.md §2),
        # not document position. Previously the mock split by position, so the
        # most-used operation's semantic grouping was never verifiable
        # (iteration 185, DOGFOOD-20).
        by_category: dict[str | None, list[str]] = {}
        for card_id, text in card_entries:
            cats = re.findall(r"（([^（）]+)）", text)
            cat = cats[-1] if cats else None
            by_category.setdefault(cat, []).append(card_id)
        if len(by_category) >= 2:
            groups = [
                {"label": f"グループ（{cat}）", "cardIds": ids,
                 "rationale": f"{cat}をテーマとするカードをグループ化"}
                for cat, ids in by_category.items()
            ]
        else:
            mid = len(card_ids) // 2
            groups = [
                {"label": "グループA（モック）", "cardIds": card_ids[:mid],
                 "rationale": "主題の類似性に基づく自動グループ化"},
                {"label": "グループB（モック）", "cardIds": card_ids[mid:],
                 "rationale": "残りのカードを補完グループとして分類"},
            ]
        return json.dumps({"groups": groups})
    if task == "detect_contradiction":
        # Deterministic positive path (iteration 176): when the prompt carries the
        # marker phrase, report a contradiction. Mirrors check_narrative's
        # "未検証の主張" marker so the business-flow E2E can freeze the
        # contradiction-detection semantics, not just the response schema.
        # Reference the card A/B texts so the E2E can freeze that the explanation
        # is grounded in the actual pair, not a generic string
        # (iteration 191, DOGFOOD-27).
        if "トレードオフ" in prompt:
            a_text = _CARD_A_TEXT.search(prompt)
            b_text = _CARD_B_TEXT.search(prompt)
            card_a = a_text.group(1).strip() if a_text else "(unknown)"
            card_b = b_text.group(1).strip() if b_text else "(unknown)"
            return json.dumps({
                "hasContradiction": True,
                "explanation": f"（モック）カードA「{card_a}」とカードB「{card_b}」は相反する優先事項（トレードオフ）の関係にあります。",
            })
        return json.dumps({
            "hasContradiction": False,
            "explanation": "（モック）2枚のカード間に明示的な矛盾は検出されませんでした。"})
    if task == "suggest_document_title":
        # Reference ALL island labels so the E2E can freeze that a title reflects
        # the OVERALL canvas theme. Previously only the first island label was
        # embedded, so a multi-island document could never verify that the title
        # reflects every island (iteration 190, DOGFOOD-26; extends DOGFOOD-18).
        labels: list[str] = []
        match = _TITLE_ISLAND_SECTION.search(prompt)
        if match:
            for line in match.group(1).splitlines():
                line = line.strip()
                if line.startswith("- "):
                    labels.append(line[2:].strip())
        label_text = ", ".join(labels)
        return json.dumps({"candidates": [{"title": f"（モック）{label_text}のタイトル候補"}]})
    if task == "propose_opposing_viewpoint":
        # Reference the TARGET card's claim so the E2E can freeze that an opposing
        # viewpoint actually responds to (is grounded in) the target card text.
        # Previously the mock returned scenario-1's canned "待ち時間" text for
        # every target, so opposing-viewpoint grounding was never verifiable
        # (iteration 182, DOGFOOD-17).
        target_text = ""
        match = _OPPOSING_TARGET_CARD.search(prompt)
        if match:
            try:
                target_text = json.loads(match.group(1)).get("text", "")
            except ValueError:
                target_text = ""
        return json.dumps({
            "opposingText": f"（モック）この主張（「{target_text}」）は、逆の状況でも同じ帰結が起きる可能性があり、根拠の一般性が不足しています。",
            "evidenceGap": True,
            "rationale": "（モック）主張の根拠となるカードに、反例・補強の証拠が接続されていません。",
            "warnings": [],
        })
    return json.dumps({})


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args) -> None:  # keep the console quiet
        return

    def do_GET(self) -> None:
        # Health probe. The unified OpenAI-compatible adapter answers GET with 200,
        # and CI's connectivity check (plus the readiness probes in the LLM test
        # modules) rely on that. Mirror it so the mock and the adapter are
        # interchangeable on the same port.
        self._send(200, {"status": "ok", "type": "mock-local-llm", "model": "mock"})

    def do_POST(self) -> None:
        if self.path.rstrip("/") != "/generate":
            self._send(404, {"error": "not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length) if length > 0 else b"{}"
            payload = json.loads(body.decode("utf-8"))
        except (ValueError, json.JSONDecodeError):
            self._send(400, {"error": "invalid JSON body"})
            return

        task = str(payload.get("task", ""))
        prompt = payload.get("prompt", "")
        if not isinstance(prompt, str):
            prompt = ""

        self._send(200, {"text": build_text_for_task(task, prompt)})

    def _send(self, status: int, obj: dict) -> None:
        data = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Deterministic mock /generate server for kj-atlas local-LLM demos."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), _Handler)
    print(f"kj-atlas mock /generate server listening on http://{args.host}:{args.port}")
    print("Set KJ_ATLAS_LLM_PROVIDER=local and KJ_ATLAS_LOCAL_LLM_BASE_URL to this URL.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
