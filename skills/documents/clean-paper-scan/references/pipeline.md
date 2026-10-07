# Pipeline details

Concrete algorithms, parameters and conventions for each stage. Values in
parentheses are what worked on real worksheets photographed with a phone
(1773×2364 px JPEG, A4/16K sheet on a stone floor, hard overhead light).

## Coordinate conventions

- Stage 1 output ("rectified page") is the working coordinate system for
  everything after it: `target_h=2339` px tall (≈A4 at 200 dpi), width derived
  from the sheet aspect (typically 1670–1700 px).
- Erase boxes in `boxes.json` are `[name, x0, y0, x1, y1]` in *that* system, half
  open in x/y (PIL-style: `x0 <= x < x1` is not required — the code slices
  `[y0:y1, x0:x1]`, so x1/y1 are exclusive). Read them off the `inspect/grid_*.png`
  overlay, which is rendered at 0.62× with 100 px labels: the labels always show
  rectified-page coordinates, never display coordinates.
- Because de-warp runs before erase, author boxes on `03_dewarp_*.png` (or on
  `02_norm_*.png` when that page was not de-warped). Running the CLI twice is the
  intended loop: run once, read the grids, fill in boxes, run again.

## Stage 1 — paper quad + perspective warp

1. Blur the grayscale photo (r=4), threshold at 152, keep the largest connected
   component. That is the sheet.
2. Scan every row for the first/last run of `True` of length ≥18 px; keep rows
   whose ink span exceeds 30 % of the width. Same for every column.
3. Fit `x = a·y + b` (left/right edges) and `y = c·x + d` (top/bottom) by least
   squares with 3 rounds of outlier rejection (`thr = max(3, p70·2.5)`).
4. Intersect the four lines → corners. Expand 0.2 % away from the centroid so no
   paper edge is clipped.
5. `PIL.Image.transform(size, Image.QUAD, data)` maps the quad to a rectangle —
   no hand-rolled homography needed. Output height 2339 px; width from the mean
   side lengths so the aspect ratio is never stretched.
6. Paint a white border (45 px) around the rectified page; it removes the desk
   sliver and gives the later stages clean edges.

Always eyeball `inspect/quad_*.jpg` once. A wrong quad is the one failure that
silently corrupts every later stage.

## Stage 2 — illumination normalization

```
bg  = gaussian_blur(gray, r=55)          # background illumination estimate
v   = gray / bg                          # flat-field
out = clip((t_hi - v) / (t_hi - t_lo))   # t_hi = 0.86, t_lo = 0.50
```

- Paper ≈ 1.0 → white; ink ≈ 0.2–0.5 → black; the reverse side's show-through
  usually sits at 0.8–0.9 → white.
- The gap `t_hi - t_lo` is the real control: too wide and faint print survives as
  gray mush, too narrow and thin strokes break up. Verify by zooming into the
  lightest printed text, not the darkest.
- `normalize.auto_tune()` prints data-driven thresholds as a sanity hint only.

## Stage 3 — handwriting erase

```
ink       = gray < 170
protected = pixels in horizontal ink runs >= 150 px     # rules & underlines
lab       = connected_components(ink & ~protected)      # 8-connected
kill      = union of components with >=50 % of their pixels inside a box
out       = gray; out[dilate(kill, 2)] = 255            # dilation kills halos
out[rule_mask] = original[rule_mask]                    # restore rules
```

- Ink threshold 170 (on the normalized image) is deliberately generous: it must
  catch the dry-ballpoint halo. Printing is far darker, so a generous threshold
  costs nothing.
- `grow=2` px of dilation removes the antialiased fringe of the pen stroke.
- Rule restoration takes an explicit `restore_lines` list, `[x0, x1, y_top, y_bottom]`
  per rule, because the rules are slightly tilted after rectification. Measure
  the rule's centre row at both ends (see the example below) and let
  `line_mask` interpolate; half-thickness 3 px is right for a 2–3 px printed line.
- Boxes that contain a *handwritten* pair of parentheses (some students draw the
  brackets themselves) legitimately leave a blank without brackets. Do not
  "repair" it by inventing printed brackets; report it instead.

Example (`boxes.json`):

```json
{
  "p2_shuxue1": {
    "boxes": [
      ["class",  528, 194, 736, 282],
      ["name",   918, 198, 1235, 282],
      ["i2_30",  528, 1592, 616, 1660]
    ],
    "restore_lines": [[515, 785, 263.5, 265.5], [918, 1152, 268.0, 270.5]]
  }
}
```

## Stage 4 — de-warp a curled sheet

A four-point transform cannot undo paper curl. Symptom: text lines slope
down-right in the upper half and up-right in the lower half; table rules bow.

1. **Line samples.** Horizontally close the ink mask (bridge k=23 px) so a row of
   glyphs becomes one blob; keep blobs with width ≥140 px and height ≤64 px —
   those are text lines. Separately, collect horizontal runs ≥60 px as rules.
   For each line, per column take the mean y of ink pixels → centre line `y(x)`.
2. **Bend measurement.** `r(x) = y(x) - median(y)`. Per-line medians are removed
   because a line's absolute position is not a defect.
3. **Field fit.** Model `D(x,y) = Σ a_pq · x'^p · y'^q` with `x',y' ∈ [-1,1]`,
   `p+q ≤ 3`, by least squares with iteratively reweighted outlier rejection.
   ~9 coefficients absorb fan/keystone/curl without inventing wiggles.
4. **Resample.** `out(x,y) = in(x, y + D(x,y))`, bilinear. Iterate 2–3 times,
   accumulating the field (`T ← T(x, y+D) + D`); the fit residual should fall
   each round (observed 2.18 → 1.79 → 1.47 px RMS).
5. **Guards.** Refuse when fewer than 400 samples exist, or when `|D|max`
   exceeds 4 % of the page height — that means the fit degenerated (nearly empty
   page) and applying it would shred the layout.

Apply it only when it is needed: `clean_scan.py --dewarp auto` compares
`|T|max` against 6 px and skips straight pages. Pages with handwriting should be
de-warped *before* boxes are authored, never after.

## Stage 5 — edge-grime cleanup

Cropping by a fixed margin either leaves grime or cuts text. Instead:

1. Deep-ink mask `gray < 110` (shadows are mid-gray, real print is near black).
2. Keep components with area ≥120.
3. Discard components that touch the outer 70 px band — that is the paper edge
   shadow, desk and specks.
4. The remaining bbox is the content box; paint everything outside it white with
   a 12 px buffer.

On the sample pages this yielded content boxes such as `(137,145)-(1488,2144)` on
a 1696×2339 page, i.e. 125 px of left grime and 200 px of right grime removed
without losing a single printed character.

## Stage 6 — A4 assembly

- Render each page onto a white A4 canvas at 254 dpi (2100×2970), uniform scale,
  centered. No stretching, no upscaling to a "nicer" dpi.
- Grayscale, JPEG-compressed inside the PDF (PIL `save(..., save_all=True,
  resolution=254)`).
- Page order is an explicit list; reordering the output (e.g. "move page 1 last")
  is a list permutation, not a re-render.
- Verify with `pdf.verify_pdf`: page count, MediaBox, and per-page matching of
  the embedded images against the built canvases (a mean absolute difference of
  ~0.1 means a match; >10 means a different page).
