"""Illumination normalization: white paper, black ink, no show-through.

Divide the page by a heavily blurred version of itself (background estimate),
then push everything above ``t_hi`` to white and everything below ``t_lo`` to
black. That single step removes uneven lighting, fold shadows, the gray paper
tint and the faint ghost of the reverse side, while keeping antialiased edges.
"""

import numpy as np
from PIL import Image

from .tools import blur


def normalize(img, blur_r=55, t_hi=0.86, t_lo=0.50):
    """img: grayscale PIL image -> normalized grayscale PIL image."""
    a = np.asarray(img.convert('L')).astype(np.float32)
    bg = np.maximum(blur(a, blur_r), 1.0)
    v = a / bg
    out = np.clip((t_hi - v) / (t_hi - t_lo), 0.0, 1.0)
    return Image.fromarray((255 * (1 - out)).astype(np.uint8))


def auto_tune(img, blur_r=55, sample=0.02):
    """Suggest (t_hi, t_lo) from the image histogram; a sanity hint, not a rule.

    Returns thresholds that put ``sample`` of the paper area at white and keep
    real ink dark. Print is usually far darker than show-through, so the gap
    between the two thresholds is what matters.
    """
    a = np.asarray(img.convert('L')).astype(np.float32)
    bg = np.maximum(blur(a, blur_r), 1.0)
    v = (a / bg).ravel()
    v.sort()
    n = len(v)
    t_hi = float(np.quantile(v, 1 - sample))
    t_lo = float(np.quantile(v, 0.004)) + 0.05
    return max(0.70, min(0.95, t_hi)), max(0.30, min(0.70, t_lo))
