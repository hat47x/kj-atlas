import type { Card, Point } from "../types";

const CARD_WIDTH = 220;
const CARD_HEIGHT = 80;
// Visual gap between adjacent grid cells (matches the existing
// ISLAND_PADDING/POLYGON_PADDING scale already used for island geometry).
const CELL_GAP = 24;

type GridPoint = { x: number; y: number };
type GridCell = { row: number; col: number };

function cellKey(cell: GridCell): string {
  return `${cell.row},${cell.col}`;
}

function pointKey(point: GridPoint): string {
  return `${point.x},${point.y}`;
}

// The 4 directed unit edges around a grid cell, clockwise (screen y-down).
function cellEdges(cell: GridCell): Array<[GridPoint, GridPoint]> {
  const topLeft = { x: cell.col, y: cell.row };
  const topRight = { x: cell.col + 1, y: cell.row };
  const bottomRight = { x: cell.col + 1, y: cell.row + 1 };
  const bottomLeft = { x: cell.col, y: cell.row + 1 };
  return [
    [topLeft, topRight],
    [topRight, bottomRight],
    [bottomRight, bottomLeft],
    [bottomLeft, topLeft],
  ];
}

function signedArea(points: GridPoint[]): number {
  let sum = 0;
  for (let index = 0; index < points.length; index += 1) {
    const current = points[index];
    const next = points[(index + 1) % points.length];
    sum += current.x * next.y - next.x * current.y;
  }
  return sum / 2;
}

/**
 * Traces the boundary of a set of unit grid cells via edge cancellation: an
 * edge shared by two occupied cells is contributed once by each cell but in
 * OPPOSITE directions, so it cancels; edges with no matching reverse are the
 * boundary. The surviving edges are chained into closed loop(s), and the
 * loop with the largest area (the outer contour) is returned. Any other
 * loops (interior holes, or a second disconnected cluster of cells) are
 * discarded — a deliberate simplification, since real card clusters are
 * expected to be simply-connected (see generateOrthogonalIslandOutline's
 * doc comment for the practical implication).
 */
export function traceGridBoundary(cells: GridCell[]): GridPoint[] {
  if (cells.length === 0) {
    return [];
  }

  const allEdges: Array<[GridPoint, GridPoint]> = [];
  const edgeKeySet = new Set<string>();
  for (const cell of cells) {
    for (const [from, to] of cellEdges(cell)) {
      allEdges.push([from, to]);
      edgeKeySet.add(`${pointKey(from)}|${pointKey(to)}`);
    }
  }

  const boundaryEdges = allEdges.filter(([from, to]) => !edgeKeySet.has(`${pointKey(to)}|${pointKey(from)}`));
  if (boundaryEdges.length === 0) {
    return [];
  }

  const nextPointByStart = new Map<string, GridPoint>();
  const startPointByKey = new Map<string, GridPoint>();
  for (const [from, to] of boundaryEdges) {
    nextPointByStart.set(pointKey(from), to);
    startPointByKey.set(pointKey(from), from);
  }

  const visited = new Set<string>();
  const loops: GridPoint[][] = [];
  for (const [from] of boundaryEdges) {
    const startKey = pointKey(from);
    if (visited.has(startKey)) {
      continue;
    }

    const loop: GridPoint[] = [];
    let currentKey = startKey;
    while (!visited.has(currentKey)) {
      const point = startPointByKey.get(currentKey);
      if (!point) {
        break;
      }
      loop.push(point);
      visited.add(currentKey);
      const next = nextPointByStart.get(currentKey);
      if (!next) {
        break;
      }
      currentKey = pointKey(next);
    }
    if (loop.length >= 4) {
      loops.push(loop);
    }
  }

  if (loops.length === 0) {
    return [];
  }

  loops.sort((a, b) => Math.abs(signedArea(b)) - Math.abs(signedArea(a)));
  return loops[0];
}

// Removes redundant vertices where three consecutive points are collinear
// (the middle point sits mid-edge rather than at an actual turn).
function simplifyCollinear(points: GridPoint[]): GridPoint[] {
  if (points.length < 3) {
    return points;
  }

  const count = points.length;
  return points.filter((current, index) => {
    const prev = points[(index - 1 + count) % count];
    const next = points[(index + 1) % count];
    const dx1 = current.x - prev.x;
    const dy1 = current.y - prev.y;
    const dx2 = next.x - current.x;
    const dy2 = next.y - current.y;
    return dx1 * dy2 - dy1 * dx2 !== 0;
  });
}

export type OrthogonalIslandOutline = {
  points: Point[];
  /** (vertexCount - 4) / 2 — the count of reflex ("concave") corners. 0 for a plain rectangle. */
  complexity: number;
};

/**
 * Generates an axis-aligned (no diagonal edges) polygon that follows the
 * member cards' grid occupancy, rather than a padded bounding box or convex
 * hull. Cards are clustered onto a uniform grid derived from their own
 * positions (round-to-nearest-cell), so minor manual-drag jitter around an
 * intended grid position is tolerated. ADR-0048 D2 (Round 5 redline).
 *
 * Known simplification: if the member cards form more than one orthogonally
 * -connected cluster (e.g. two separate sub-groups with a large gap, or a
 * diagonal-only arrangement with no shared cell edges), only the largest
 * cluster is reflected in the outline — the others are omitted rather than
 * drawn as a second, disconnected shape or a hole. Running "tidy" resolves
 * this by re-packing every member into one dense block.
 */
export function generateOrthogonalIslandOutline(cards: Card[]): OrthogonalIslandOutline | null {
  if (cards.length === 0) {
    return null;
  }

  const cellWidth = CARD_WIDTH + CELL_GAP;
  const cellHeight = CARD_HEIGHT + CELL_GAP;
  const minX = Math.min(...cards.map((card) => card.x));
  const minY = Math.min(...cards.map((card) => card.y));

  const cellsByKey = new Map<string, GridCell>();
  for (const card of cards) {
    const cell: GridCell = {
      row: Math.round((card.y - minY) / cellHeight),
      col: Math.round((card.x - minX) / cellWidth),
    };
    cellsByKey.set(cellKey(cell), cell);
  }

  const loop = traceGridBoundary(Array.from(cellsByKey.values()));
  if (loop.length < 4) {
    return null;
  }

  const simplified = simplifyCollinear(loop);
  const points: Point[] = simplified.map((gridPoint) => ({
    x: minX - CELL_GAP / 2 + gridPoint.x * cellWidth,
    y: minY - CELL_GAP / 2 + gridPoint.y * cellHeight,
  }));

  return {
    points,
    complexity: Math.max(0, (points.length - 4) / 2),
  };
}

/**
 * Computes the "tidy" target position for every member card: a dense,
 * gapless near-square grid (row-major, reading order = current top-to-
 * bottom/left-to-right position), which minimizes — and for a card count
 * that fills the grid exactly, eliminates — outline complexity. Human-
 * triggered only (never run automatically); the caller applies the result
 * as one document/history step so it is a single undo.
 */
export function computeTidyIslandLayout(cards: Card[]): Array<{ id: string; x: number; y: number }> {
  if (cards.length === 0) {
    return [];
  }

  const cellWidth = CARD_WIDTH + CELL_GAP;
  const cellHeight = CARD_HEIGHT + CELL_GAP;
  const minX = Math.min(...cards.map((card) => card.x));
  const minY = Math.min(...cards.map((card) => card.y));

  const orderedCards = [...cards].sort((a, b) => {
    const rowA = Math.round((a.y - minY) / cellHeight);
    const rowB = Math.round((b.y - minY) / cellHeight);
    if (rowA !== rowB) {
      return rowA - rowB;
    }
    return a.x - b.x;
  });

  const columnCount = Math.max(1, Math.ceil(Math.sqrt(orderedCards.length)));

  return orderedCards.map((card, index) => ({
    id: card.id,
    x: minX + (index % columnCount) * cellWidth,
    y: minY + Math.floor(index / columnCount) * cellHeight,
  }));
}
