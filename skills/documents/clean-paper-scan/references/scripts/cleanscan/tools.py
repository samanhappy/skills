"""Low-level image helpers for clean-paper-scan.

Deliberately depends on Pillow + numpy only: the bundled Python runtime used by
many agents has no OpenCV/scipy, so connected components, morphology and
resampling are implemented here with plain numpy.
"""

import numpy as np
from PIL import Image, ImageFilter


# --------------------------------------------------------------------------- io

def load_gray(path):
    """Open an image as 8-bit grayscale."""
    return Image.open(path).convert('L')


def load_rgb(path):
    return Image.open(path).convert('RGB')


def as_float(img):
    return np.asarray(img).astype(np.float32)


def blur(a, radius):
    """Gaussian blur of a float array (returns float array)."""
    return np.asarray(
        Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius))
    ).astype(np.float32)


# --------------------------------------------------------------- connected parts

def components(mask):
    """8-connected component labeling: run-length encoding + union-find.

    Returns (labels, n). ``labels`` is int32 with 0 = background. Labels are
    remapped to their union-find root, so ids in 1..n are not guaranteed to be
    contiguous or non-empty: always guard ``if len(xs) == 0: continue``.
    """
    H, W = mask.shape
    parent = [0]

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    labels = np.zeros((H, W), dtype=np.int32)
    prev_runs = []
    nxt = 1
    for y in range(H):
        row = mask[y]
        if not row.any():
            prev_runs = []
            continue
        edges = np.flatnonzero(np.diff(np.concatenate(([0], row.view(np.int8), [0]))))
        starts, ends = edges[0::2], edges[1::2]
        runs = []
        for s, e in zip(starts, ends):
            lab = 0
            for (ps, pe, pl) in prev_runs:
                if ps <= e and s <= pe:          # 8-connectivity via 1px slack
                    if lab == 0:
                        lab = pl
                    else:
                        union(lab, pl)
            if lab == 0:
                lab = nxt
                parent.append(nxt)
                nxt += 1
            runs.append((s, e, lab))
        for (s, e, lab) in runs:
            labels[y, s:e] = lab
        prev_runs = runs
    root = np.array([find(i) for i in range(nxt)], dtype=np.int32)
    return root[labels], nxt


def component_stats(labels, n):
    """Yield dicts with bbox/area for every non-empty label."""
    out = []
    for c in range(1, n + 1):
        ys, xs = np.where(labels == c)
        if len(xs) == 0:
            continue
        out.append(dict(
            c=c, area=int(len(xs)),
            x0=int(xs.min()), x1=int(xs.max()) + 1,
            y0=int(ys.min()), y1=int(ys.max()) + 1,
            w=int(xs.max() - xs.min() + 1), h=int(ys.max() - ys.min() + 1),
        ))
    return out


# ------------------------------------------------------------------- morphology

def dilate(mask, r=1):
    """Square-kernel binary dilation via shifted ORs."""
    out = mask.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dy == 0 and dx == 0:
                continue
            sh = np.zeros_like(mask)
            ys0, ys1 = max(0, dy), mask.shape[0] + min(0, dy)
            xs0, xs1 = max(0, dx), mask.shape[1] + min(0, dx)
            sh[ys0:ys1, xs0:xs1] = mask[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
            out |= sh
    return out


def erode(mask, r=1):
    return ~dilate(~mask, r)


def close_h(mask, k):
    """Horizontal closing: bridge gaps between glyphs of one text line."""
    return erode_h(dilate_h(mask, k), k)


def dilate_h(mask, k):
    out = mask.copy()
    r = k // 2
    for d in range(1, r + 1):
        out[:, d:] |= mask[:, :-d]
        out[:, :-d] |= mask[:, d:]
    return out


def erode_h(mask, k):
    out = mask.copy()
    r = k // 2
    for d in range(1, r + 1):
        out[:, d:] &= mask[:, :-d]
        out[:, :-d] &= mask[:, d:]
    return out


def long_runs(mask, minlen=150):
    """Mask of pixels that belong to a horizontal True-run of >= minlen.

    Used to protect printed rules (class/name underlines, table borders).
    """
    prot = np.zeros_like(mask)
    H, W = mask.shape
    for y in range(H):
        row = mask[y]
        if not row.any():
            continue
        edges = np.flatnonzero(np.diff(np.concatenate(([0], row.view(np.int8), [0]))))
        for s, e in zip(edges[0::2], edges[1::2]):
            if e - s >= minlen:
                prot[y, s:e] = True
    return prot
