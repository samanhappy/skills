# scripts

Runnable implementation of the pipeline. Pillow + numpy only — no OpenCV, no
scipy, no network. A four-page A4 worksheet processes in a few seconds per page.

```bash
python clean_scan.py page1.jpg page2.jpg \
    --work work/ --out clean.pdf \
    --erase boxes.json --order 2,3,4,1
```

Run it once without `--erase`: it rectifies, normalizes, de-warps when needed and
writes labelled coordinate grids to `work/inspect/`. Read the boxes off those
grids, write `boxes.json`, run again.

## Stage outputs (all inspectable)

| File | Meaning |
| --- | --- |
| `01_warp_<key>.png` | perspective-rectified page |
| `02_norm_<key>.png` | lighting / show-through removed |
| `03_dewarp_<key>.png` | present only when the page was de-warped |
| `04_erased_<key>.png` | present only when boxes were supplied |
| `05_final_<key>.png` | final page (edge grime cleaned) |
| `inspect/quad_<key>.jpg` | detected sheet outline — always eyeball this |
| `inspect/grid_<key>.png` | coordinate grid for authoring erase boxes |
| `inspect/boxes_<key>.png` | erase boxes drawn before erasing (pre-flight) |
| `inspect/removed_<key>.png` | erased pixels painted red — the key verification view |

`<key>` is the source file stem, so `boxes.json` keys map 1:1 to photos.

## boxes.json

```json
{
  "<source stem>": {
    "boxes": [["label", x0, y0, x1, y1]],
    "restore_lines": [[x0, x1, y_top, y_bottom]]
  }
}
```

- Coordinates are in the stage image that feeds the erase step (`03_dewarp_*.png`
  when de-warp ran, otherwise `02_norm_*.png`).
- `restore_lines` repaints printed rules (class/name underlines, table rules) from
  the original pixels after erasing, so they stay continuous. `y_top`/`y_bottom`
  are the rule's centre row measured at `x0` and `x1`.

## Modules

| Module | API | Notes |
| --- | --- | --- |
| `cleanscan.tools` | `components`, `component_stats`, `dilate`, `erode`, `dilate_h`, `erode_h`, `close_h`, `long_runs`, `blur` | run-length + union-find labelling; shift-based morphology |
| `cleanscan.quad` | `detect_quad`, `expand_quad`, `warp_to_rect` | largest bright blob → robust edge fits → `PIL` `Image.QUAD` |
| `cleanscan.normalize` | `normalize`, `auto_tune` | flat-field divide + two-threshold curve |
| `cleanscan.erase` | `erase_boxes`, `removed_overlay`, `line_mask` | the two invariants (protected rules, component majority vote) |
| `cleanscan.dewarp` | `line_samples`, `fit_field`, `field_image`, `apply_field`, `estimate` | text-line bend → smooth 2-D field → iterative resample |
| `cleanscan.margins` | `content_bbox`, `clean_margins` | deep-ink content box; whitens edge grime safely |
| `cleanscan.pdf` | `fit_a4`, `build_pdf`, `verify_pdf` | A4 254 dpi assembly + page-order verification |
| `cleanscan.gridview` | `gridded`, `zoom`, `draw_quad`, `draw_boxes` | inspection views for authoring and review |

## Validation

These scripts are the distilled, re-tested version of a working session. Run on
the same four source photos, the CLI reproduces the delivered pages: mean absolute
grayscale difference vs. the original hand-run output was 0.005, 0.009, 0.000 and
0.463 (0–255 scale) across the four pages, with identical erase reports, identical
de-warp residuals (2.18 → 1.79 → 1.47 px on the curled page) and the same content
boxes. `verify_pdf` confirmed 4 pages, A4 MediaBox and the requested page order.
