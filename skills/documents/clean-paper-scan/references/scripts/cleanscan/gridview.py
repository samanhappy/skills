"""Coordinate-grid inspection views.

Erase boxes have to be defined by looking at the actual page. These helpers
render a page (or a crop) with a labelled coordinate grid so the numbers read
off the image can be typed straight into the box list.
"""

from PIL import Image, ImageDraw


def gridded(im, scale=1.0, step=100, label=True):
    if scale != 1.0:
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    im = im.convert('RGB').copy()
    d = ImageDraw.Draw(im)
    W, H = im.size
    for x in range(0, W, int(step * scale)):
        d.line([(x, 0), (x, H)], fill=(255, 120, 120), width=1)
        if label:
            d.text((x + 2, 2), str(int(x / scale)), fill=(255, 0, 0))
            d.text((x + 2, H - 12), str(int(x / scale)), fill=(255, 0, 0))
    for y in range(0, H, int(step * scale)):
        d.line([(0, y), (W, y)], fill=(120, 120, 255), width=1)
        if label:
            d.text((2, y + 2), str(int(y / scale)), fill=(0, 0, 255))
            d.text((W - 46, y + 2), str(int(y / scale)), fill=(0, 0, 255))
    return im


def zoom(im, box, path, scale=3, step=20):
    """Crop ``box`` = (x0, y0, x1, y1), upscale, overlay a fine grid, save."""
    c = im.crop(box).convert('RGB')
    c = c.resize((c.width * scale, c.height * scale), Image.LANCZOS)
    d = ImageDraw.Draw(c)
    x0, y0, bx2, by2 = box
    gx = (int(x0) // step + 1) * step
    while gx < bx2:
        X = (gx - x0) * scale
        d.line([(X, 0), (X, c.height)], fill=(255, 0, 0))
        d.text((X + 2, 2), str(gx), fill=(255, 0, 0))
        gx += step
    gy = (int(y0) // step + 1) * step
    while gy < by2:
        Y = (gy - y0) * scale
        d.line([(0, Y), (c.width, Y)], fill=(0, 0, 255))
        d.text((2, Y + 2), str(gy), fill=(0, 0, 255))
        gy += step
    c.save(path)
    return c


def draw_quad(im, quad, width=5, color=(255, 0, 0)):
    """Overlay the detected sheet quad - always eyeball this before trusting it."""
    im = im.convert('RGB').copy()
    d = ImageDraw.Draw(im)
    pts = [quad['TL'], quad['TR'], quad['BR'], quad['BL'], quad['TL']]
    d.line([tuple(map(float, p)) for p in pts], fill=color, width=width)
    return im


def draw_boxes(im, boxes, width=3):
    """Overlay erase boxes for a pre-flight check before erasing anything."""
    im = im.convert('RGB').copy()
    d = ImageDraw.Draw(im)
    for _name, (x0, y0, x1, y1) in boxes:
        d.rectangle([x0, y0, x1, y1], outline=(255, 0, 0), width=width)
    return im
