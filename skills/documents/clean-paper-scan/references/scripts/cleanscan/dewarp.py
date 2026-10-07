"""De-warping for curled / wavy pages.

A four-point perspective transform makes the sheet rectangular but cannot undo
the curl of the paper: text baselines come out slanted at the top and slanted
the other way at the bottom, and table rules look like bananas.

Method: detect every text line and printed rule, measure how much each one bends,
fit a smooth 2-D displacement field to those measurements, and resample the page
along that field. Iterating 2-3 times removes what a single polynomial cannot.
"""

import numpy as np
from PIL import Image

from .tools import blur, close_h, components, long_runs


def line_samples(ink, min_w=140, max_h=64, close_k=23, rule_len=60, min_pts=8):
    """Collect (xs, ys) center-line samples: one array per text line / rule."""
    m = close_h(ink, close_k)
    lab, n = components(m)
    pts = []
    for c in range(1, n + 1):
        ys, xs = np.where(lab == c)
        if len(xs) == 0:
            continue
        x0, x1 = int(xs.min()), int(xs.max())
        h = int(ys.max() - ys.min()) + 1
        if (x1 - x0 + 1) < min_w or h > max_h:
            continue
        cols = {}
        for x, y in zip(xs, ys):
            cols.setdefault(int(x), []).append(int(y))
        xs_s = np.array(sorted(cols), dtype=np.float64)
        ys_s = np.array([np.mean(cols[x]) for x in xs_s], dtype=np.float64)
        if len(xs_s) >= min_pts:
            pts.append((xs_s, ys_s))

    rules = long_runs(ink, rule_len)
    lab2, n2 = components(rules)
    for c in range(1, n2 + 1):
        ys, xs = np.where(lab2 == c)
        if len(xs) == 0 or (xs.max() - xs.min() + 1) < 200:
            continue
        cols = {}
        for x, y in zip(xs, ys):
            cols.setdefault(int(x), []).append(int(y))
        xs_s = np.array(sorted(cols), dtype=np.float64)
        ys_s = np.array([np.mean(cols[x]) for x in xs_s], dtype=np.float64)
        if len(xs_s) >= 20:
            pts.append((xs_s, ys_s))
    return pts


def fit_field(pts, W, H, deg=3, iters=4):
    """Least-squares smooth field D(x, y) from per-line bend measurements."""
    X, Y, R = [], [], []
    for xs, ys in pts:
        r = ys - np.median(ys)
        keep = np.abs(r) < 45                     # drop merged/odd line samples
        xs, ys, r = xs[keep], ys[keep], r[keep]
        if len(xs) < 8:
            continue
        X.append(xs); Y.append(ys); R.append(r)
    if not X:
        raise RuntimeError('no usable text lines: page too empty for de-warp')
    X = np.concatenate(X); Y = np.concatenate(Y); R = np.concatenate(R)
    xn = (X - W / 2) / (W / 2)
    yn = (Y - H / 2) / (H / 2)
    terms = [(p, q) for p in range(deg + 1) for q in range(deg + 1) if p + q <= deg]
    A = np.stack([(xn ** p) * (yn ** q) for (p, q) in terms], axis=1)
    w = np.ones(len(R), bool)
    coef = np.zeros(len(terms))
    for _ in range(iters):
        coef, *_ = np.linalg.lstsq(A[w], R[w], rcond=None)
        res = A @ coef - R
        s = np.median(np.abs(res[w])) * 1.4826 + 1e-6
        w = np.abs(res) < max(2.0, 2.5 * s)
    stats = dict(n=int(len(R)), kept=int(w.sum()),
                 rms=float(np.sqrt((res[w] ** 2).mean())))
    return coef, terms, stats


def field_image(coef, terms, W, H):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    xn = (xx - W / 2) / (W / 2)
    yn = (yy - H / 2) / (H / 2)
    D = np.zeros((H, W), np.float32)
    for c, (p, q) in zip(coef, terms):
        D += c * (xn ** p) * (yn ** q)
    return D


def _sample_field(D, xs, ys):
    H, W = D.shape
    xi = np.clip(xs, 0, W - 1); yi = np.clip(ys, 0, H - 1)
    x0 = np.floor(xi).astype(int); y0 = np.floor(yi).astype(int)
    x1 = np.clip(x0 + 1, 0, W - 1); y1 = np.clip(y0 + 1, 0, H - 1)
    wx = xi - x0; wy = yi - y0
    return (D[y0, x0] * (1 - wx) * (1 - wy) + D[y0, x1] * wx * (1 - wy) +
            D[y1, x0] * (1 - wx) * wy + D[y1, x1] * wx * wy)


def apply_field(img, D):
    """out(x, y) = in(x, y + D(x, y)) with bilinear sampling."""
    a = np.asarray(img.convert('L')).astype(np.float32)
    H, W = a.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ys = np.clip(yy + D, 0, H - 1)
    y0 = np.floor(ys).astype(np.int32)
    y1 = np.clip(y0 + 1, 0, H - 1)
    wy = ys - y0
    cols = np.broadcast_to(np.arange(W, dtype=np.int32), (H, W))
    out = a[y0, cols] * (1 - wy) + a[y1, cols] * wy
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def estimate(img, iters=3, deg=3, thr=150, verbose=False,
             min_samples=400, max_field_frac=0.04):
    """Iterative de-warp. Returns (image, total_field, per-iteration stats).

    Refuses to run when the page has too few line samples or when a fitted field
    exceeds ``max_field_frac`` of the page height: that means the fit degenerated
    (usually a nearly empty page), and applying it would shred the layout.
    """
    H, W = img.height, img.width
    total = np.zeros((H, W), np.float32)
    cur = img.convert('L')
    info = []
    limit = max_field_frac * H
    for _ in range(iters):
        ink = np.asarray(cur).astype(np.float32) < thr
        pts = line_samples(ink)
        coef, terms, st = fit_field(pts, W, H, deg=deg)
        if st['n'] < min_samples:
            raise RuntimeError('de-warp needs more text lines (%d samples found)'
                               % st['n'])
        D = field_image(coef, terms, W, H)
        if float(np.abs(D).max()) > limit:
            raise RuntimeError('de-warp field unstable (|D|max=%.0f px > %.0f)'
                               % (float(np.abs(D).max()), limit))
        info.append(dict(lines=len(pts), **st, dmax=float(np.abs(D).max())))
        yy, xx = np.mgrid[0:H, 0:W]
        total = _sample_field(total, xx, yy + D) + D
        cur = apply_field(cur, D)
        if verbose:
            print('   dewarp iter: lines=%d rms=%.2f |D|max=%.1f' %
                  (len(pts), st['rms'], np.abs(D).max()))
    return cur, total, info
