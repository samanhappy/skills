"""Assemble flattened pages into a print-ready A4 PDF."""

from PIL import Image

DPI = 254                     # sheet photos are ~200-250 dpi; no fake upscaling
A4_W = round(210 / 25.4 * DPI)
A4_H = round(297 / 25.4 * DPI)


def fit_a4(img, dpi=DPI):
    """Center a page image on a white A4 canvas, uniform scale, no distortion."""
    page_w = round(210 / 25.4 * dpi)
    page_h = round(297 / 25.4 * dpi)
    im = img.convert('L')
    sc = min(page_w / im.width, page_h / im.height)
    w, h = int(im.width * sc), int(im.height * sc)
    canvas = Image.new('L', (page_w, page_h), 255)
    canvas.paste(im.resize((w, h), Image.LANCZOS), ((page_w - w) // 2, (page_h - h) // 2))
    return canvas


def build_pdf(paths, out_path, dpi=DPI):
    """paths: page images in final order -> multi-page A4 grayscale PDF."""
    if not paths:
        raise ValueError('no pages')
    pages = [fit_a4(Image.open(p) if isinstance(p, str) else p, dpi) for p in paths]
    pages[0].save(out_path, save_all=True, append_images=pages[1:],
                  resolution=dpi, optimize=True)
    return out_path


def verify_pdf(path, expected_names=None, dpi=DPI):
    """Parse the PDF and report page count, MediaBox and embedded-image order.

    When ``expected_names`` is a list of page-image paths, each embedded image is
    matched against the A4 canvas that ``build_pdf`` would produce from it, so a
    wrong page order cannot slip through. The reported diff is a mean absolute
    grayscale difference: ~0.1 means a match, >10 means a different page.
    """
    import io
    import re

    import numpy as np
    from PIL import Image as _Image

    data = open(path, 'rb').read()
    pages = data.count(b'/Type /Page') - data.count(b'/Type /Pages')
    box = re.search(rb'/MediaBox \[([^\]]+)\]', data)
    report = dict(bytes=len(data), pages=pages,
                  mediabox=box.group(1).decode() if box else None, order=None)
    if not expected_names:
        return report
    objs = {}
    for m in re.finditer(rb'(\d+) 0 obj(.*?)endobj', data, re.S):
        objs[int(m.group(1))] = m.group(2)
    imgs = []
    for num, body in objs.items():
        if b'/Subtype /Image' in body:
            s = re.search(rb'stream\r?\n', body).end()
            e = body.rfind(b'endstream')
            imgs.append((num, _Image.open(io.BytesIO(body[s:e].rstrip(b'\r\n'))).convert('L')))
    imgs.sort()
    refs = []
    for p in expected_names:
        canvas = fit_a4(_Image.open(p) if isinstance(p, str) else p, dpi)
        refs.append(np.asarray(canvas.resize((300, 424))).astype(np.float32))
    order = []
    for _, im in imgs:
        a = np.asarray(im.resize((300, 424))).astype(np.float32)
        diffs = [float(np.abs(a - r).mean()) for r in refs]
        order.append((expected_names[int(np.argmin(diffs))], min(diffs)))
    report['order'] = order
    return report
