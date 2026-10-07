"""Handwriting removal that never eats printed glyphs.

Two invariants do the work:

1. **Long horizontal runs are sacred.** Class/name underlines and table rules
   are the only long horizontal printed structures. Mark every pixel that sits
   in a horizontal ink run >= ``protect_len`` and never erase it.
2. **Majority vote per connected component.** A component is erased only when
   >= ``frac`` of its pixels fall inside an erase box. Handwriting sits fully
   inside its box; the printed parenthesis or neighbour glyph next to it pokes
   out of the box, so it survives.

After erasing, underlines are restored from the original pixels so they do not
end up dashed where handwriting crossed them.
"""

import numpy as np
from PIL import Image

from .tools import components, dilate, long_runs


def line_mask(shape, x0, x1, yc0, yc1, half=3):
    """A thin, optionally tilted horizontal band - used to restore a rule."""
    H, W = shape
    m = np.zeros((H, W), bool)
    for x in range(max(0, x0), min(W, x1 + 1)):
        t = (x - x0) / max(1, (x1 - x0))
        yc = yc0 + t * (yc1 - yc0)
        y0, y1 = int(round(yc)) - half, int(round(yc)) + half
        m[max(0, y0):min(H, y1 + 1), x] = True
    return m


def erase_boxes(img, boxes, thr=170, frac=0.5, grow=2, restore_lines=None,
                protect_len=150):
    """Erase handwriting inside ``boxes``.

    img     : normalized grayscale PIL image
    boxes   : [ (name, (x0, y0, x1, y1)), ... ] in img coordinates
    thr     : ink threshold (pixels darker than this count as ink)
    frac    : component is erased when this share of it lies inside a box
    grow    : dilate the erase mask by this many px to kill antialias halos
    restore_lines : [ (x0, x1, y_top, y_bottom), ... ] rules to repaint from the
              original image after erasing (keeps underlines continuous)
    protect_len   : horizontal run length that marks printed rules

    Returns (image, report, removed_mask).
    """
    a = np.asarray(img.convert('L')).astype(np.float32)
    H, W = a.shape
    ink = a < thr
    protected = long_runs(ink, protect_len)
    removable = ink & ~protected
    lab, n = components(removable)
    sizes = np.bincount(lab.ravel(), minlength=n + 1)

    kill = np.zeros_like(ink)
    report = []
    for name, (x0, y0, x1, y1) in boxes:
        x0, y0 = max(0, int(x0)), max(0, int(y0))
        x1, y1 = min(W, int(x1)), min(H, int(y1))
        sub = lab[y0:y1, x0:x1]
        ids = np.unique(sub)
        ids = ids[ids > 0]
        killed = 0
        for c in ids:
            inside = int((sub == c).sum())
            if inside / sizes[c] >= frac:
                kill |= (lab == c)
                killed += int(sizes[c])
        report.append((name, int(len(ids)), killed, (x1 - x0) * (y1 - y0)))

    kill = dilate(kill, grow)
    out = a.copy()
    out[kill] = 255
    if restore_lines:
        orig = a.copy()
        lm = np.zeros((H, W), bool)
        for (lx0, lx1, ly0, ly1) in restore_lines:
            lm |= line_mask(a.shape, lx0, lx1, ly0, ly1, half=3)
        out[lm] = orig[lm]
    return Image.fromarray(out.astype(np.uint8)), report, kill


def removed_overlay(before, after, thr=170, delta=40):
    """RGB image with every erased pixel painted red - the verification view."""
    a = np.asarray(before.convert('L')).astype(np.int16)
    b = np.asarray(after.convert('L')).astype(np.int16)
    removed = (b > a + delta) & (a < thr)
    rgb = np.stack([b, b, b], -1).astype(np.uint8)
    rgb[removed] = [255, 0, 0]
    return Image.fromarray(rgb), removed
