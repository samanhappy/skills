---
name: clean-paper-scan
description: Turn phone photos of paper documents (worksheets, homework, test papers, notes, forms) into clean printable scans — correct perspective, normalize lighting, delete reverse-side show-through, erase handwriting and answer marks, de-warp curled pages, clear edge grime, and export a print-ready A4 PDF. Use when asked to 擦除笔迹 / 去掉手写答案 / 把照片转成可打印的 PDF / 试卷去答案做空白卷 / 扫描件美化 / 把歪的页面摆正 / clean up a photographed page / straighten a photographed page / make a blank copy of a worksheet.
argument-hint: '照片路径（可多张，按页序），是否需要擦笔迹、页序与输出格式'
---

# Clean Paper Scan

The deliverable is a clean **scan** of the original sheet: identical layout, intact printed text, no handwriting, no photo artifacts (shadow, show-through, curl, desk, edge grime).

Never re-typeset the page in HTML/LaTeX/Word unless the user asks for an editable document. Erasing ink on the image preserves layout exactly and cannot introduce transcription errors — it is both cheaper and safer, and it is what "擦除笔迹" actually asks for.

## 1. Clarify, then classify pages

- Which pages actually carry handwriting? Look at every page before promising work: worksheets often come in pairs where one is blank. Pages with handwriting need stage 3; blank pages must stay untouched beyond normalization.
- Confirm page order and output shape (single multi-page PDF vs per-page images). A "把第一页移到最后" style request is a page-order edit on the *output*, not a re-processing.
- Keep the source photos read-only. Do heavy work in a scratch dir (`work/`), put only deliverables in the user-facing output path.

## 2. Probe the environment before designing anything

Bundled agent runtimes frequently ship **Pillow + numpy only** — no OpenCV, no scipy. Check first:

```bash
python -c "import cv2" ; python -c "import scipy"
```

If they are missing, use [references/scripts](references/scripts/README.md): connected components (run-length + union-find), morphology (shift-based), and bilinear remapping are all implemented in pure numpy there. Do not `pip install` a CV stack for this job unless the user asks; the pure-numpy path is fast enough for a handful of pages (seconds per page).

## 3. Pipeline

Read [references/pipeline.md](references/pipeline.md) before writing code: it carries the parameters, the coordinate conventions and the arithmetic behind each step.

| # | Stage | Fixes | Entry point |
| --- | --- | --- | --- |
| 1 | Paper quad detection + perspective warp | angle, keystone, desk in frame | `cleanscan.quad` |
| 2 | Illumination normalization | uneven light, fold shadows, gray paper, reverse-side show-through | `cleanscan.normalize` |
| 3 | Handwriting erase (boxes + component majority vote) | pen/pencil answers, name, scribbles | `cleanscan.erase` |
| 4 | De-warp (text-line field) | curled sheet: lines that slope one way at the top and the other way at the bottom, banana-shaped table rules | `cleanscan.dewarp` |
| 5 | Edge-grime cleanup | desk shadow, paper-edge grime, specks | `cleanscan.margins` |
| 6 | A4 assembly + verification | page size, page order | `cleanscan.pdf` |

Order matters: de-warp **before** erasing, so erase boxes are authored on the final geometry. `clean_scan.py` does exactly this and refuses to de-warp pages that are already straight.

## 4. Two invariants that keep printed content alive

Erasing by rectangle is what damages documents. The erase step only works because of these two rules — keep them if you rewrite anything:

1. **Long horizontal runs are sacred.** Mark every pixel belonging to a horizontal ink run of ≥150 px and never erase it. Those runs are exactly the printed class/name underlines and table rules. Restore them from the original pixels after erasing, otherwise the surviving rule looks dashed where handwriting crossed it.
2. **Majority vote per connected component.** Erase a component only when ≥50% of its pixels fall inside an erase box. Handwriting sits fully inside its box; the printed parenthesis `（ ）` or the neighbouring glyph that the box touches pokes out of it and survives. This is why boxes may be authored loosely — but keep them tight enough that no printed glyph is *entirely* inside.

Consequently the erase boxes are defined **by looking at the page**, with the labelled coordinate grids in `work/inspect/`. That is expected work, not a shortcut to skip: print a grid, read the numbers, write them into `boxes.json`, re-run. If a page has no handwriting, pass no boxes for it.

## 5. Verify — never deliver from a single glance

Do all three, every time:

1. **Removal overlay** (`inspect/removed_*.png`): the pre-erase page with every erased pixel painted red. Red must cover handwriting *only*. This single check is what catches a deleted printed parenthesis or a chewed-off rule — it caught exactly that during development.
2. **Before/after crops** of each edited region at 2-4× zoom, not just the whole page.
3. **PDF introspection**: assert the page count, the A4 MediaBox, and match each embedded image against its source page so a wrong order cannot slip through (`verify_pdf`).

If an overlay shows printed damage, fix the box (shrink it, or split it around the glyph) and re-run; do not "touch up" the result by hand.

## 6. When something looks wrong

Use [references/troubleshooting.md](references/troubleshooting.md). The high-frequency cases: a missing parenthesis or a broken underline (erase-box geometry), text still wavy after rectification (sheet curl → stage 4), gray bands along the edges (stage 5), and residual gray mush around characters (normalization thresholds too aggressive/conservative).

## 7. Reporting back

State what changed per page (handwriting erased / straightened / edges cleaned), the output page order, and any place where the sheet itself limited quality (a genuinely faint print, deep fold through text, a torn edge). Offer the trade-offs you deliberately did not take — for example leaving faint paper grain instead of pushing the tone curve until thin strokes disappear.
