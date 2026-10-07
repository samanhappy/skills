# Troubleshooting

Symptom → cause → fix. Everything here was hit on real pages while building this
skill; the removal overlay (`inspect/removed_*.png`) is what makes most of them
visible in seconds.

## Erasing

| Symptom | Cause | Fix |
| --- | --- | --- |
| A printed `（` or `）` disappeared | The erase box contained that glyph *entirely*, so the ≥50 % majority test kept nothing | Shrink the box so the glyph crosses the boundary (stop 4–8 px short of it), then re-run. Check with the removal overlay before delivering. |
| A box that looked right deleted a printed glyph anyway | The glyph was inside the box and happened to be a separate component | Same as above; never widen a box "to be safe" — widening is what kills glyphs. |
| Class/name underline or table rule now dashed | The run-length protector only covers runs ≥150 px, so faint or interrupted stretches were erased | Add the rule to `restore_lines` with its measured centre row at both ends; the code repaints it from the original pixels. |
| Faint gray halo left around erased strokes | Ink threshold too tight or dilation too small | Raise `thr` (170 → 180) and/or `grow` (2 → 3). Generous thresholds cost nothing: print is much darker than pen halo. |
| Handwriting survives inside a box | The stroke is connected to a protected rule, so its component mostly lies outside the box | Extend the box to cover the stroke and keep the rule in `restore_lines`; the rule is repainted, the stroke is not. |
| Handwriting erased on a page that had none | Box list copied from another page | Boxes are per-page; pass none for clean pages (the CLI reports `no boxes for <page>`). |
| Coordinates hit the wrong place after a re-run | Boxes were authored on `02_norm_*.png` but the page is now de-warped (or vice versa) | Author boxes on the stage image the pipeline will actually feed to the erase step: `03_dewarp_*.png` when de-warp ran, else `02_norm_*.png`. |

## Geometry

| Symptom | Cause | Fix |
| --- | --- | --- |
| Text lines slope down-right at the top and up-right at the bottom; table rules bow | Paper curl — a four-point perspective transform cannot undo it | Run stage 4 (de-warp). `--dewarp auto` triggers above 6 px of field. |
| Lines collide or spacing looks stretched after de-warp | Field too aggressive (large y-gradient) | Lower `deg` (3 → 2) or `iters` (3 → 2). The built-in guard already rejects fields larger than 4 % of page height. |
| De-warp refuses to run | Too few text lines (a nearly empty page, or a page that is mostly a form/table) | Expected: skip it for that page. Do not lower `min_samples` to force it. |
| Page still noticeably rotated | Quad detection locked onto the wrong blob (bright desk area merged with the sheet) | Inspect `inspect/quad_*.jpg`; raise the threshold in `detect_quad` or supply corners explicitly. |
| Desk or floor visible along one side | Quad slightly inside the sheet, or the sheet is cut off in the photo | Increase `--border`, or raise `expand_quad`'s factor (1.002 → 1.01). If the paper itself is out of frame, say so — it cannot be recovered. |
| Two sheets in one photo | `detect_quad` keeps the largest blob only | Split the photo per sheet, or run the pipeline per region of interest. |

## Tone

| Symptom | Cause | Fix |
| --- | --- | --- |
| Whole page looks gray / dirty | Background blur radius too small for large soft shadows, or `t_hi` too low | Raise `blur_r` (55 → 80–120) for big shadows; raise `t_hi` (0.86 → 0.90). |
| Reverse-side show-through still visible | `t_hi` below the ghost level | Raise `t_hi` slightly and re-check the lightest real print. |
| Thin printed strokes broke up / disappeared | `t_hi` too high or `t_lo` too high, so real ink was pushed to white | Lower `t_hi` or lower `t_lo` (widen the gap); verify on the faintest printed text, not on the title. |
| Text edges look crunchy / aliased | Gap too narrow, so antialiased edge pixels were pushed to pure black | Widen the gap slightly (`t_lo` down) instead of blurring the result. |
| Gray bands remain along the left/right edges | Stage 5 skipped or `edge_guard` too small, so edge shadow entered the content box | Re-run with margins enabled; raise `edge_guard` if the shadow extends further in. |
| Content touches the white cut | `pad` too small for that page | Raise `pad` (12 → 20) — the content box itself is measured, so this only affects the buffer. |

## Output

| Symptom | Cause | Fix |
| --- | --- | --- |
| Page order wrong | Order list not applied, or the sources were passed in the wrong sequence | Pass `--order` (1-based, comma-separated) or reorder the source arguments; `verify_pdf` matches every embedded image against its page, so this cannot slip through unnoticed. |
| `verify_pdf` reports diffs like 10–30 | Comparing embedded images against raw page files instead of the A4 canvases | `verify_pdf` builds the canvases itself; only pass files, not pre-resized images. ~0.1 means a match. |
| PDF is huge | Very high source resolution plus `optimize=True` off | Pages are already downscaled to ~254 dpi; a 4-page worksheet lands around 2 MB. Do not raise dpi for "quality" — it only upsamples. |

## When not to use this skill

- **Born-digital PDFs** (exported from Word/LaTeX): do not rasterize. Edit the
  text layer or the source document instead.
- **Effective resolution below ~150 dpi**: erasing leaves visible mush; report the
  limit rather than over-processing.
- **Colored pens on colored paper, or colored annotations you must keep**: the
  single-threshold ink model assumes dark ink on light paper. Separate channels
  first, or state that the automatic path does not apply.
