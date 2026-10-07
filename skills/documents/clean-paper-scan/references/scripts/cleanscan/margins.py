"""Whiten the paper edge without clipping any content.

Photos carry the desk, the shadow under the sheet and edge grime. Cropping by a
fixed margin either leaves grime or cuts text, so instead: find the real content
box from *deep* ink components (very dark pixels only), discard components that
sit within ``edge_guard`` px of the sheet border (those are shadows/specks), and
paint everything outside the resulting box white with a small buffer.
"""

import numpy as np
from PIL import Image

from .tools import components


def content_bbox(a, core_thr=110, min_area=120, edge_guard=70):
    """Bounding box of genuine content in a normalized grayscale array."""
    H, W = a.shape
    lab, n = components(a < core_thr)
    sizes = np.bincount(lab.ravel(), minlength=n + 1)
    keep = np.flatnonzero(sizes >= min_area)
    keep = keep[keep > 0]
    if len(keep) == 0:
        raise RuntimeError('no content found: check the ink threshold')
    bad = np.zeros(int(sizes.max()) + 1, bool)
    for c in keep:
        ys, xs = np.where(lab == c)
        if len(xs) == 0:
            continue
        if (xs.min() < edge_guard or xs.max() >= W - edge_guard or
                ys.min() < edge_guard or ys.max() >= H - edge_guard):
            bad[c] = True
    good = np.isin(lab, keep) & ~bad[lab]
    ys, xs = np.where(good)
    if len(xs) == 0:
        raise RuntimeError('content box empty after removing edge-touching blobs')
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def clean_margins(img, pad=12, core_thr=110, min_area=120, edge_guard=70):
    """Returns (cleaned image, content bbox)."""
    a = np.asarray(img.convert('L')).astype(np.float32)
    H, W = a.shape
    X0, Y0, X1, Y1 = content_bbox(a, core_thr, min_area, edge_guard)
    out = a.copy()
    out[:max(0, Y0 - pad), :] = 255
    out[min(H, Y1 + pad + 1):, :] = 255
    out[:, :max(0, X0 - pad)] = 255
    out[:, min(W, X1 + pad + 1):] = 255
    return Image.fromarray(out.astype(np.uint8)), (X0, Y0, X1, Y1)
