"""Paper-quad detection and perspective rectification.

The sheet is a bright quad on a darker/uneven background photographed at an
angle. We threshold, keep the largest blob, scan row/column boundaries, fit the
four edges robustly and intersect them. Then PIL's QUAD transform maps the quad
to a rectangle (no manual homography needed).
"""

import numpy as np
from PIL import Image

from .tools import blur, components


def _robust_fit(vals, base, iters=3):
    """Least squares fit ``vals = a*base + b`` with iterative outlier rejection."""
    vals = np.asarray(vals, np.float64)
    base = np.asarray(base, np.float64)
    keep = np.ones(len(vals), bool)
    coef = (0.0, 0.0)
    for _ in range(iters):
        A = np.vstack([base[keep], np.ones(int(keep.sum()))]).T
        coef, *_ = np.linalg.lstsq(A, vals[keep], rcond=None)
        res = np.abs(coef[0] * base + coef[1] - vals)
        thr = max(3.0, np.percentile(res, 70) * 2.5)
        keep = res < thr
    return coef


def detect_quad(gray_arr, thr=152, runlen=18, min_span=0.3):
    """Return {'TL','TR','BR','BL'} corners of the sheet in source pixels.

    gray_arr: float grayscale array. Assumes a single sheet filling most of the
    frame; if detection looks wrong, set the corners by hand instead.
    """
    H, W = gray_arr.shape
    m = blur(gray_arr, 4) > thr
    lab, n = components(m)
    if n <= 1:
        raise RuntimeError('no paper found: try another threshold')
    sizes = np.bincount(lab.ravel(), minlength=n + 1)
    best = int(np.argmax(sizes[1:])) + 1
    m = lab == best

    # left/right boundary per row, top/bottom per column
    left, right, top, bot = {}, {}, {}, {}
    for y in range(H):
        edges = np.flatnonzero(np.diff(np.concatenate(([0], m[y].view(np.int8), [0]))))
        st, en = edges[0::2], edges[1::2]
        ok = (en - st) >= runlen
        if not ok.any():
            continue
        st, en = st[ok], en[ok]
        if en[-1] - st[0] > W * min_span:
            left[y], right[y] = int(st[0]), int(en[-1] - 1)
    for x in range(W):
        col = m[:, x]
        edges = np.flatnonzero(np.diff(np.concatenate(([0], col.view(np.int8), [0]))))
        st, en = edges[0::2], edges[1::2]
        ok = (en - st) >= runlen
        if not ok.any():
            continue
        st, en = st[ok], en[ok]
        if en[-1] - st[0] > H * min_span:
            top[x], bot[x] = int(st[0]), int(en[-1] - 1)

    rows = [y for y in left if H * 0.06 < y < H * 0.94]
    cols = [x for x in top if W * 0.06 < x < W * 0.94]
    if len(rows) < 20 or len(cols) < 20:
        raise RuntimeError('paper quad not found; pass corners explicitly')
    a_l, b_l = _robust_fit([left[y] for y in rows], rows)      # x = a*y + b
    a_r, b_r = _robust_fit([right[y] for y in rows], rows)
    c_t, d_t = _robust_fit([top[x] for x in cols], cols)       # y = c*x + d
    c_b, d_b = _robust_fit([bot[x] for x in cols], cols)

    def inter(ab, cd):
        a, b = ab
        c, d = cd
        y = (c * b + d) / (1 - a * c)
        return (a * y + b, y)

    quad = {'TL': inter((a_l, b_l), (c_t, d_t)), 'TR': inter((a_r, b_r), (c_t, d_t)),
            'BR': inter((a_r, b_r), (c_b, d_b)), 'BL': inter((a_l, b_l), (c_b, d_b))}
    return {k: (float(v[0]), float(v[1])) for k, v in quad.items()}


def expand_quad(quad, factor=1.002):
    """Scale corners away from the centroid so no paper edge is clipped."""
    cx = np.mean([quad[k][0] for k in quad])
    cy = np.mean([quad[k][1] for k in quad])
    return {k: (cx + (quad[k][0] - cx) * factor, cy + (quad[k][1] - cy) * factor)
            for k in quad}


def warp_to_rect(img, quad, target_h=2339, border=45, fill=255):
    """Perspective-rectify the quad; paint a white ``border`` to drop desk edges.

    Aspect ratio is preserved (derived from the quad's mean side lengths), so the
    result is never stretched. 2339 px tall ~= A4 at 200 dpi.
    """
    TL, TR, BR, BL = quad['TL'], quad['TR'], quad['BR'], quad['BL']
    w_top = np.hypot(TR[0] - TL[0], TR[1] - TL[1])
    w_bot = np.hypot(BR[0] - BL[0], BR[1] - BL[1])
    h_l = np.hypot(BL[0] - TL[0], BL[1] - TL[1])
    h_r = np.hypot(BR[0] - TR[0], BR[1] - TR[1])
    aw, ah = (w_top + w_bot) / 2.0, (h_l + h_r) / 2.0
    sc = target_h / ah
    W, H = int(round(aw * sc)), int(round(ah * sc))
    data = (TL[0], TL[1], BL[0], BL[1], BR[0], BR[1], TR[0], TR[1])
    out = img.convert('RGB').transform((W, H), Image.QUAD, data, resample=Image.BICUBIC)
    arr = np.asarray(out).copy()
    b = int(border)
    if b > 0:
        arr[:b, :, :] = fill
        arr[-b:, :, :] = fill
        arr[:, :b, :] = fill
        arr[:, -b:, :] = fill
    return Image.fromarray(arr)
