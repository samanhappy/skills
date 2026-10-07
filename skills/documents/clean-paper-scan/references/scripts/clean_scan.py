#!/usr/bin/env python3
"""Photo(s) of paper documents -> clean printable A4 PDF.

    python clean_scan.py page1.jpg page2.jpg --work work/ --out clean.pdf

Stage outputs land in --work so every step can be inspected:
    01_warp_*.png   perspective-corrected
    02_norm_*.png   lighting/show-through removed
    03_dewarp_*.png text lines straightened (only when needed)
    04_erased_*.png handwriting removed (only when boxes are supplied)
    05_final_*.png  edge grime removed
    inspect/        quad overlay, coordinate grids, box pre-flight, removal overlay

Erase boxes are authored by looking at 03_dewarp_*.png (or 02_norm_*.png when the
page was not de-warped) through the grid overlay in inspect/, then passed as JSON:

    {
      "page1": {
        "boxes": [["name", 528, 194, 736, 282], ...],
        "restore_lines": [[515, 785, 263.5, 265.5]]
      }
    }

Run once without --erase, define the boxes, run again with --erase.
"""

import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cleanscan import dewarp as dewarp_mod           # noqa: E402
from cleanscan import gridview, margins as margins_mod, normalize as norm_mod  # noqa: E402
from cleanscan import pdf as pdf_mod                 # noqa: E402
from cleanscan import quad as quad_mod               # noqa: E402
from cleanscan.erase import erase_boxes, removed_overlay  # noqa: E402
from cleanscan.tools import load_gray                 # noqa: E402


def stage_dir(work):
    os.makedirs(os.path.join(work, 'inspect'), exist_ok=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('sources', nargs='+', help='source photos, in page order')
    ap.add_argument('--work', default='work', help='scratch dir for stage outputs')
    ap.add_argument('--out', required=True, help='output PDF path')
    ap.add_argument('--erase', help='JSON file with per-page erase boxes')
    ap.add_argument('--dewarp', choices=['auto', 'always', 'never'], default='auto',
                    help='auto = de-warp pages whose lines bend more than 6 px (default)')
    ap.add_argument('--dewarp-threshold', type=float, default=6.0,
                    help='auto mode: max |displacement| in px that triggers de-warp')
    ap.add_argument('--order', help='comma separated 1-based page order for the PDF, '
                                   'e.g. 2,3,4,1 to move the first page last')
    ap.add_argument('--no-margins', action='store_true', help='skip edge-grime cleanup')
    ap.add_argument('--target-height', type=int, default=2339,
                    help='rectified page height in px (2339 ~= A4 at 200 dpi)')
    ap.add_argument('--border', type=int, default=45,
                    help='white border painted after rectification, px')
    args = ap.parse_args(argv)

    stage_dir(args.work)
    boxes_cfg = {}
    if args.erase:
        boxes_cfg = json.load(open(args.erase, encoding='utf-8'))

    finals, names = [], []
    for src in args.sources:
        key = os.path.splitext(os.path.basename(src))[0]
        names.append(key)
        print('== %s' % src)

        # 1. perspective rectification ------------------------------------
        g = np.asarray(load_gray(src)).astype(np.float32)
        try:
            q = quad_mod.expand_quad(quad_mod.detect_quad(g))
        except RuntimeError as exc:
            print('   !! %s' % exc)
            sys.exit(2)
        rgb = Image.open(src).convert('RGB')
        gridview.draw_quad(rgb, q).save(
            os.path.join(args.work, 'inspect', 'quad_%s.jpg' % key), quality=88)
        warped = quad_mod.warp_to_rect(rgb, q, target_h=args.target_height,
                                       border=args.border)
        warped.save(os.path.join(args.work, '01_warp_%s.png' % key))

        # 2. lighting / show-through --------------------------------------
        norm = norm_mod.normalize(warped.convert('L'))
        norm.save(os.path.join(args.work, '02_norm_%s.png' % key))

        # 3. de-warp -------------------------------------------------------
        out = norm
        if args.dewarp != 'never':
            try:
                dw, field, info = dewarp_mod.estimate(norm, iters=3, deg=3,
                                                      verbose=True)
                dmax = float(np.abs(field).max())
                if args.dewarp == 'always' or dmax > args.dewarp_threshold:
                    out = dw
                    out.save(os.path.join(args.work, '03_dewarp_%s.png' % key))
                    print('   de-warped (field max %.1f px)' % dmax)
                else:
                    print('   lines already straight (field max %.1f px), skipped' % dmax)
            except RuntimeError as exc:
                print('   de-warp skipped: %s' % exc)

        # inspection grid for authoring boxes -----------------------------
        gridview.gridded(out, 0.62, 100).save(
            os.path.join(args.work, 'inspect', 'grid_%s.png' % key))

        # 4. erase handwriting --------------------------------------------
        cfg = boxes_cfg.get(key, {})
        boxes = [tuple([b[0], tuple(b[1:5])]) for b in cfg.get('boxes', [])]
        if boxes:
            pre = out
            gridview.draw_boxes(pre, boxes).save(
                os.path.join(args.work, 'inspect', 'boxes_%s.png' % key))
            out, report, _ = erase_boxes(pre, boxes,
                                         restore_lines=cfg.get('restore_lines'))
            ov_img, _ = removed_overlay(pre, out)
            ov_img.save(os.path.join(args.work, 'inspect', 'removed_%s.png' % key))
            out.save(os.path.join(args.work, '04_erased_%s.png' % key))
            for r in report:
                print('   erase %-14s comps=%2d killed_px=%-6d box_area=%d'
                      % (r[0], r[1], r[2], r[3]))
        elif boxes_cfg:
            print('   no boxes for %s' % key)

        # 5. edge grime ----------------------------------------------------
        if not args.no_margins:
            out, bb = margins_mod.clean_margins(out)
            print('   content box %s' % (bb,))
        final = os.path.join(args.work, '05_final_%s.png' % key)
        out.save(final)
        finals.append(final)

    # 6. assemble ----------------------------------------------------------
    if args.order:
        idx = [int(x) - 1 for x in args.order.split(',')]
        finals = [finals[i] for i in idx]
        names = [names[i] for i in idx]
    pdf_mod.build_pdf(finals, args.out)
    rep = pdf_mod.verify_pdf(args.out, expected_names=finals)
    print('== %s: pages=%s mediabox=%s bytes=%s' %
          (args.out, rep['pages'], rep['mediabox'], rep['bytes']))
    if rep['order']:
        for i, (path, diff) in enumerate(rep['order'], 1):
            print('   pdf page %d -> %s (diff %.2f)' % (i, os.path.basename(path), diff))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
