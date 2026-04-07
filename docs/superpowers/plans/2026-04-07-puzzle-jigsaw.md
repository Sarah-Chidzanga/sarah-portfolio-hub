# Puzzle Jigsaw Piece Shapes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace flat rectangular puzzle tiles with real curved jigsaw piece shapes (tab-and-blank edges) while keeping the existing drag-to-swap mechanic.

**Architecture:** All changes are client-side JS inside `templates/puzzle_play.html`. At init, an edge map is generated (random tab/blank per internal edge), SVG `<clipPath>` elements are injected for every tile, and each tile `div` is absolutely positioned and sized to accommodate tab protrusion.

**Tech Stack:** Vanilla JS, SVG clip-path, CSS background-position, existing Flask/Jinja2 template.

---

## File Map

| File | Change |
|------|--------|
| `templates/puzzle_play.html` | All changes live here — board HTML + `<script>` block |
| `tests/test_puzzle.py` | Run only — no changes needed |

---

### Task 1: Add `generateEdges` and `getTileEdges` helpers

**Files:**
- Modify: `templates/puzzle_play.html` — inside the `<script>` block, after the existing variable declarations

- [ ] **Step 1: Run existing tests to establish baseline**

```bash
pytest tests/test_puzzle.py -v
```
Expected: all 6 tests pass.

- [ ] **Step 2: Add `generateEdges` and `getTileEdges` after `var tiles = [];`**

Open `templates/puzzle_play.html`. Find this line (around line 57):
```javascript
  var tiles = [];
```

Insert the following two functions immediately after it:

```javascript
  var tiles = [];

  // Returns an object of edge keys → 'tab' or 'blank'.
  // 'h-R-C' = horizontal edge between row R and row R+1, at column C.
  // 'v-R-C' = vertical edge between col C and col C+1, at row R.
  // The tile ABOVE/LEFT of each internal edge is 'tab-out' when value='tab',
  // the tile BELOW/RIGHT is 'blank-in' (and vice-versa when value='blank').
  function generateEdges(rows, cols) {
    var edges = {};
    for (var r = 0; r < rows - 1; r++) {
      for (var c = 0; c < cols; c++) {
        edges['h-' + r + '-' + c] = Math.random() < 0.5 ? 'tab' : 'blank';
      }
    }
    for (var r = 0; r < rows; r++) {
      for (var c = 0; c < cols - 1; c++) {
        edges['v-' + r + '-' + c] = Math.random() < 0.5 ? 'tab' : 'blank';
      }
    }
    return edges;
  }

  // Returns {top, right, bottom, left} each = 'straight' | 'tab-out' | 'blank-in'.
  function getTileEdges(row, col, rows, cols, edges) {
    return {
      top:    row === 0      ? 'straight' : (edges['h-'+(row-1)+'-'+col]  === 'tab' ? 'blank-in' : 'tab-out'),
      bottom: row === rows-1 ? 'straight' : (edges['h-'+row+'-'+col]      === 'tab' ? 'tab-out'  : 'blank-in'),
      left:   col === 0      ? 'straight' : (edges['v-'+row+'-'+(col-1)]  === 'tab' ? 'blank-in' : 'tab-out'),
      right:  col === cols-1 ? 'straight' : (edges['v-'+row+'-'+col]      === 'tab' ? 'tab-out'  : 'blank-in')
    };
  }
```

- [ ] **Step 3: Run tests to confirm no breakage**

```bash
pytest tests/test_puzzle.py -v
```
Expected: all 6 tests still pass (no logic changed yet).

- [ ] **Step 4: Commit**

```bash
git add templates/puzzle_play.html
git commit -m "feat: add generateEdges and getTileEdges helpers for jigsaw shapes"
```

---

### Task 2: Add `tilePathData` function

**Files:**
- Modify: `templates/puzzle_play.html` — `<script>` block, after `getTileEdges`

`tilePathData` returns an SVG path `d` string for a single jigsaw piece. Each tile div is `(cs + 2s) × (cs + 2s)` where `cs = cellSize` and `s = tabSize`. The cell area starts at `(s, s)` inside the div. Tabs protrude outside the cell area.

- [ ] **Step 1: Add `tilePathData` immediately after `getTileEdges`**

```javascript
  // Returns SVG path 'd' string for the jigsaw piece at (row, col).
  // cs = cellSize (px), s = tabSize (px, = cs * 0.18).
  // Tile div is (cs+2s) × (cs+2s). Cell area corners: TL=(s,s), TR=(s+cs,s), BR=(s+cs,s+cs), BL=(s,s+cs).
  // tab-out protrudes AWAY from the cell centre; blank-in cuts INTO it.
  function tilePathData(row, col, rows, cols, edges, cs, s) {
    var te  = getTileEdges(row, col, rows, cols, edges);
    var hw  = cs * 0.15;          // half-tab-width  (tab width = cs*0.3)
    var midX = s + cs / 2;
    var midY = s + cs / 2;
    var d = 'M ' + s + ',' + s + ' ';

    // Top edge — left to right at y=s
    if (te.top === 'straight') {
      d += 'L ' + (s + cs) + ',' + s + ' ';
    } else {
      var depth = te.top === 'tab-out' ? -s : s;  // negative = up (outward)
      d += 'L ' + (midX - hw) + ',' + s + ' ';
      d += 'C ' + (midX - hw) + ',' + (s + depth) + ' '
               + (midX + hw) + ',' + (s + depth) + ' '
               + (midX + hw) + ',' + s + ' ';
      d += 'L ' + (s + cs) + ',' + s + ' ';
    }

    // Right edge — top to bottom at x=s+cs
    if (te.right === 'straight') {
      d += 'L ' + (s + cs) + ',' + (s + cs) + ' ';
    } else {
      var depth = te.right === 'tab-out' ? s : -s;  // positive = right (outward)
      d += 'L ' + (s + cs) + ',' + (midY - hw) + ' ';
      d += 'C ' + (s + cs + depth) + ',' + (midY - hw) + ' '
               + (s + cs + depth) + ',' + (midY + hw) + ' '
               + (s + cs) + ',' + (midY + hw) + ' ';
      d += 'L ' + (s + cs) + ',' + (s + cs) + ' ';
    }

    // Bottom edge — right to left at y=s+cs
    if (te.bottom === 'straight') {
      d += 'L ' + s + ',' + (s + cs) + ' ';
    } else {
      var depth = te.bottom === 'tab-out' ? s : -s;  // positive = down (outward)
      d += 'L ' + (midX + hw) + ',' + (s + cs) + ' ';
      d += 'C ' + (midX + hw) + ',' + (s + cs + depth) + ' '
               + (midX - hw) + ',' + (s + cs + depth) + ' '
               + (midX - hw) + ',' + (s + cs) + ' ';
      d += 'L ' + s + ',' + (s + cs) + ' ';
    }

    // Left edge — bottom to top at x=s
    if (te.left === 'straight') {
      d += 'L ' + s + ',' + s + ' ';
    } else {
      var depth = te.left === 'tab-out' ? -s : s;  // negative = left (outward)
      d += 'L ' + s + ',' + (midY + hw) + ' ';
      d += 'C ' + (s + depth) + ',' + (midY + hw) + ' '
               + (s + depth) + ',' + (midY - hw) + ' '
               + s + ',' + (midY - hw) + ' ';
      d += 'L ' + s + ',' + s + ' ';
    }

    d += 'Z';
    return d;
  }
```

- [ ] **Step 2: Run tests**

```bash
pytest tests/test_puzzle.py -v
```
Expected: all 6 pass.

- [ ] **Step 3: Commit**

```bash
git add templates/puzzle_play.html
git commit -m "feat: add tilePathData SVG path generator for jigsaw piece shapes"
```

---

### Task 3: Add `injectClipPaths` function

**Files:**
- Modify: `templates/puzzle_play.html` — `<script>` block, after `tilePathData`

- [ ] **Step 1: Add `injectClipPaths` immediately after `tilePathData`**

```javascript
  // Builds one SVG <clipPath> per tile and appends them to <body>.
  // IDs are 'jigsaw-R-C' based on solved position (row, col).
  // clipPathUnits="userSpaceOnUse" means coordinates are in the tile div's own space.
  function injectClipPaths(rows, cols, edges, cs, s) {
    var existing = document.getElementById('jigsaw-clips');
    if (existing) existing.parentNode.removeChild(existing);

    var ns   = 'http://www.w3.org/2000/svg';
    var svg  = document.createElementNS(ns, 'svg');
    svg.id   = 'jigsaw-clips';
    svg.setAttribute('style', 'position:absolute;width:0;height:0;overflow:hidden');
    var defs = document.createElementNS(ns, 'defs');

    for (var r = 0; r < rows; r++) {
      for (var c = 0; c < cols; c++) {
        var cp   = document.createElementNS(ns, 'clipPath');
        cp.setAttribute('id', 'jigsaw-' + r + '-' + c);
        cp.setAttribute('clipPathUnits', 'userSpaceOnUse');
        var path = document.createElementNS(ns, 'path');
        path.setAttribute('d', tilePathData(r, c, rows, cols, edges, cs, s));
        cp.appendChild(path);
        defs.appendChild(cp);
      }
    }

    svg.appendChild(defs);
    document.body.appendChild(svg);
  }
```

- [ ] **Step 2: Run tests**

```bash
pytest tests/test_puzzle.py -v
```
Expected: all 6 pass.

- [ ] **Step 3: Commit**

```bash
git add templates/puzzle_play.html
git commit -m "feat: add injectClipPaths to create SVG clip-path defs for all tiles"
```

---

### Task 4: Update board container HTML and init constants

**Files:**
- Modify: `templates/puzzle_play.html` — board `<div>` inline style + bottom of `<script>` init block

The board switches from `display:grid` to `position:relative` with explicit px dimensions. Three new constants (`CELL_SIZE`, `TAB_SIZE`, `EDGES`) are computed at init.

- [ ] **Step 1: Replace the board div inline style**

Find:
```html
    <div id="puzzle-board"
         style="
           display: grid;
           grid-template-columns: repeat({{ cols }}, 1fr);
           gap: 3px;
           width: min(480px, 90vw);
           aspect-ratio: 1;
           background: var(--bg-secondary);
           border-radius: 8px;
           padding: 3px;
         ">
    </div>
```

Replace with:
```html
    <div id="puzzle-board"
         style="
           position: relative;
           width: min(480px, 90vw);
           background: var(--bg-secondary);
           border-radius: 8px;
           overflow: visible;
         "></div>
```

- [ ] **Step 2: Add constants and board-size init at the bottom of the script, replacing the existing init block**

Find (near the bottom of the `<script>` block):
```javascript
  // Initialise
  for (var i = 0; i < ROWS * COLS; i++) { tiles.push(i); }
  shufflePuzzle();
```

Replace with:
```javascript
  // Initialise
  var board       = document.getElementById('puzzle-board');
  var BOARD_SIZE  = Math.min(480, Math.floor(window.innerWidth * 0.9));
  var CELL_SIZE   = Math.floor(BOARD_SIZE / COLS);
  var TAB_SIZE    = Math.round(CELL_SIZE * 0.18);
  var EDGES       = generateEdges(ROWS, COLS);

  board.style.width  = (COLS * CELL_SIZE) + 'px';
  board.style.height = (ROWS * CELL_SIZE) + 'px';

  injectClipPaths(ROWS, COLS, EDGES, CELL_SIZE, TAB_SIZE);

  for (var i = 0; i < ROWS * COLS; i++) { tiles.push(i); }
  shufflePuzzle();
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_puzzle.py -v
```
Expected: all 6 pass (template renders; route logic unchanged).

- [ ] **Step 4: Commit**

```bash
git add templates/puzzle_play.html
git commit -m "feat: switch puzzle board to position:relative with px dimensions for jigsaw tiles"
```

---

### Task 5: Update `makeTile()` for absolute positioning and clip-path

**Files:**
- Modify: `templates/puzzle_play.html` — replace the `makeTile` function body

Each tile is now absolutely positioned at its slot, sized to include tab overflow, and clipped to its jigsaw shape.

- [ ] **Step 1: Replace the entire `makeTile` function**

Find the existing `makeTile` function:
```javascript
  function makeTile(solvedIdx, slotIdx) {
    var tileW = 100 / COLS;
    var tileH = 100 / ROWS;
    var col = solvedIdx % COLS;
    var row = Math.floor(solvedIdx / COLS);

    var div = document.createElement('div');
    div.dataset.slotIndex = slotIdx;
    div.dataset.solvedIndex = solvedIdx;
    div.draggable = true;
    div.style.cssText = [
      'background-image: url(' + PHOTO_URL + ');',
      'background-size: ' + (COLS * 100) + '% ' + (ROWS * 100) + '%;',
      'background-position: ' + (col * 100 / (COLS - 1 || 1)) + '% ' + (row * 100 / (ROWS - 1 || 1)) + '%;',
      'border-radius: 4px;',
      'cursor: grab;',
      'transition: opacity 0.15s, transform 0.1s;',
      'aspect-ratio: 1;',
    ].join('');

    div.addEventListener('dragstart', onDragStart);
    div.addEventListener('dragover',  onDragOver);
    div.addEventListener('drop',      onDrop);
    div.addEventListener('dragend',   onDragEnd);
    return div;
  }
```

Replace with:
```javascript
  function makeTile(solvedIdx, slotIdx) {
    var cs       = CELL_SIZE;
    var s        = TAB_SIZE;
    var col      = solvedIdx % COLS;
    var row      = Math.floor(solvedIdx / COLS);
    var slotCol  = slotIdx % COLS;
    var slotRow  = Math.floor(slotIdx / COLS);
    var tileSize = cs + 2 * s;

    var div = document.createElement('div');
    div.dataset.slotIndex  = slotIdx;
    div.dataset.solvedIndex = solvedIdx;
    div.draggable = true;

    // background-position: shift the full photo so the correct region
    // appears inside the tile's cell area (which starts at offset s,s within the div).
    var bgX = s - col * cs;
    var bgY = s - row * cs;

    div.style.cssText = [
      'position: absolute;',
      'left: '   + (slotCol * cs - s) + 'px;',
      'top: '    + (slotRow * cs - s) + 'px;',
      'width: '  + tileSize + 'px;',
      'height: ' + tileSize + 'px;',
      'background-image: url(' + PHOTO_URL + ');',
      'background-size: ' + (COLS * cs) + 'px ' + (ROWS * cs) + 'px;',
      'background-position: ' + bgX + 'px ' + bgY + 'px;',
      'clip-path: url(#jigsaw-' + row + '-' + col + ');',
      '-webkit-clip-path: url(#jigsaw-' + row + '-' + col + ');',
      'cursor: grab;',
      'z-index: 1;',
      'transition: opacity 0.15s;',
    ].join('');

    div.addEventListener('dragstart', onDragStart);
    div.addEventListener('dragover',  onDragOver);
    div.addEventListener('drop',      onDrop);
    div.addEventListener('dragend',   onDragEnd);
    return div;
  }
```

- [ ] **Step 2: Run tests**

```bash
pytest tests/test_puzzle.py -v
```
Expected: all 6 pass.

- [ ] **Step 3: Commit**

```bash
git add templates/puzzle_play.html
git commit -m "feat: update makeTile to use absolute positioning and SVG clip-path jigsaw shapes"
```

---

### Task 6: Update drag handlers — z-index and remove stale transform resets

**Files:**
- Modify: `templates/puzzle_play.html` — `onDragStart`, `onDragOver`, `onDragEnd`

The dragged tile needs `z-index: 10` so its tab renders above neighbours. The old `transform: scale(1.05)` on hover is removed (incompatible with absolute positioning + clip-path).

- [ ] **Step 1: Replace `onDragStart`**

Find:
```javascript
  function onDragStart(e) {
    dragSourceIndex = parseInt(e.currentTarget.dataset.slotIndex);
    e.currentTarget.style.opacity = '0.45';
    e.dataTransfer.effectAllowed = 'move';
  }
```

Replace with:
```javascript
  function onDragStart(e) {
    dragSourceIndex = parseInt(e.currentTarget.dataset.slotIndex);
    e.currentTarget.style.opacity = '0.45';
    e.currentTarget.style.zIndex  = '10';
    e.dataTransfer.effectAllowed  = 'move';
  }
```

- [ ] **Step 2: Replace `onDragOver`**

Find:
```javascript
  function onDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    e.currentTarget.style.transform = 'scale(1.05)';
  }
```

Replace with:
```javascript
  function onDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  }
```

- [ ] **Step 3: Replace `onDragEnd`**

Find:
```javascript
  function onDragEnd(e) {
    e.currentTarget.style.opacity = '1';
    e.currentTarget.style.transform = '';
    dragSourceIndex = null;
    // Reset all scale transforms in case dragend fires before buildBoard
    document.querySelectorAll('#puzzle-board > div').forEach(function(t) {
      t.style.transform = '';
    });
  }
```

Replace with:
```javascript
  function onDragEnd(e) {
    e.currentTarget.style.opacity = '1';
    e.currentTarget.style.zIndex  = '1';
    dragSourceIndex = null;
  }
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_puzzle.py -v
```
Expected: all 6 pass.

- [ ] **Step 5: Commit**

```bash
git add templates/puzzle_play.html
git commit -m "feat: update drag handlers — z-index lift on drag, remove stale transform resets"
```

---

### Task 7: Browser verification across all difficulty levels

**Files:** No code changes — visual verification only.

- [ ] **Step 1: Start the app**

```bash
python app.py
```

- [ ] **Step 2: Verify Easy (3×3)**

Open: `http://localhost:5000/puzzle` → pick any photo → choose **Easy**.

Check:
- 9 tiles visible, each shaped like a real jigsaw piece with curved tabs/blanks
- The photo is correctly aligned across all tiles (no offset mismatches)
- Dragging a tile swaps it with the target; pieces re-render in their new slots with correct shapes
- Shuffle scrambles tiles; Peek solution restores order
- Solving triggers the "🎉 Solved!" panel

- [ ] **Step 3: Verify Medium (4×4) and Hard (5×5)**

Repeat the above checks for Medium and Hard difficulty levels.

- [ ] **Step 4: Commit**

```bash
git add templates/puzzle_play.html
git commit -m "feat: real jigsaw piece shapes with curved tabs — all difficulties working"
```
