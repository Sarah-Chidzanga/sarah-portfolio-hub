# Puzzle Jigsaw Piece Shapes — Design Spec
**Date:** 2026-04-07
**Status:** Approved

## Overview

Replace the current flat rectangular tiles in the photo puzzle with real curved jigsaw piece shapes. Each piece has smooth curved tabs (bumps) and blanks (indentations) on its edges, interlocking with neighbouring pieces like a real puzzle. The drag-to-swap mechanic, difficulty levels, and all other UI stays the same.

## Scope

**One file changes:** `templates/puzzle_play.html` only.
No backend changes. No new routes. No new static files.

## Design

### Edge Assignment

At puzzle init time, JS generates an edge map for all internal edges in the grid:

- **Horizontal edges** — the edge between row `r` and row `r+1`, for each column `c`. Key: `h-{r}-{c}`.
- **Vertical edges** — the edge between col `c` and col `c+1`, for each row `r`. Key: `v-{r}-{c}`.

Each edge is randomly assigned `tab` or `blank`. The tile above/left gets `tab-out` or `blank-in` on that edge; the tile below/right gets the opposite.

Border edges (outermost sides of the grid) are always straight.

### Tile Shape (SVG clip-path)

Each tile is clipped to a jigsaw shape using an inline SVG `<clipPath>`. The path is built from 4 edges:

- `straight` — a straight line across that side
- `tab-out` — a smooth rounded bump that sticks outward (into the neighbouring cell)
- `blank-in` — a smooth rounded indentation that cuts inward

Tab geometry (relative to a `size × size` tile coordinate space):
- Tab/blank width: 30% of cell size, centered on the edge midpoint
- Tab/blank depth: 18% of cell size, protruding outward or inward

The path is drawn clockwise starting from the top-left corner: top edge → right edge → bottom edge (reversed) → left edge (reversed).

### Tile Sizing and Positioning

Because tabs stick outside a tile's grid cell, each tile div is larger than the cell:

- **Rendered size:** `cellSize + 2×tabSize` on each axis (tabs can protrude on any side)
- **Tab size:** `cellSize × 0.18` (pixels)
- **Position:** absolutely placed at `(col × cellSize − tabSize, row × cellSize − tabSize)` within a `position:relative` board container
- **Board container size:** `cols × cellSize` × `rows × cellSize` (no padding for tabs — tabs overlap neighbouring cells)

The board switches from `display:grid` to `position:relative` with explicit `width` and `height`.

### Background Image Alignment

Each tile shows the correct slice of the photo via `background-image`:

- `background-size`: `(cols × cellSize) px  (rows × cellSize) px`  
  *(the photo fills the full puzzle area exactly — same scale for every tile)*
- `background-position`: `(tabSize − col × cellSize) px  (tabSize − row × cellSize) px`  
  *(the `+tabSize` offset accounts for the tab padding at the top-left of the div, so the correct photo region appears in the cell area)*

### Clip-path Application

All clip-paths are injected as a single hidden `<svg>` block at the top of the puzzle board on init:

```html
<svg style="position:absolute;width:0;height:0;overflow:hidden">
  <defs>
    <clipPath id="jigsaw-0-0" clipPathUnits="userSpaceOnUse"> ... </clipPath>
    <clipPath id="jigsaw-0-1" clipPathUnits="userSpaceOnUse"> ... </clipPath>
    ...
  </defs>
</svg>
```

Each tile div gets `clip-path: url(#jigsaw-{row}-{col})` in its inline style.

The clip-path IDs use the tile's **solved position** (row/col), not its current slot. When tiles are swapped, the `makeTile()` function already knows `solvedIdx` so it always applies the right shape for the content being shown.

### Z-index

Tiles get `z-index: 1` by default. The tile being dragged gets `z-index: 10` so its tab renders above neighbouring tiles.

### What Stays the Same

- Drag-to-swap logic (`onDragStart`, `onDragOver`, `onDrop`, `onDragEnd`)
- `shufflePuzzle()`, `solvePuzzle()`, `checkSolved()`
- Move counter, success panel, Peek/Shuffle buttons
- All 3 difficulty levels (3×3, 4×4, 5×5)
- Route, backend, DynamoDB — untouched

## Implementation Steps

| Step | Function / Change | Notes |
|------|-------------------|-------|
| 1 | `generateEdges(rows, cols)` | Returns object mapping edge keys to `'tab'` or `'blank'` |
| 2 | `tilePathData(row, col, edges, cellSize, tabSize)` | Returns SVG path `d` string for one piece |
| 3 | `injectClipPaths(rows, cols, edges, cellSize, tabSize)` | Builds and inserts the `<svg><defs>` block |
| 4 | Update `makeTile()` | Larger size, absolute position, `clip-path`, updated background math |
| 5 | Update board container | Switch to `position:relative`, explicit px dimensions |
| 6 | Test 3×3, 4×4, 5×5 | Verify shapes tile correctly and photo aligns |

## Out of Scope

- Free-placement / snap-to-slot mechanic
- Shape presets (diamond, hexagon)
- Mobile touch events (existing drag events handle touch via browser defaults)
