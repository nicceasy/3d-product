#!/usr/bin/env python3
"""comp_analysis.py - the measured compositional analysis for stage 7 and the FIRST/KEY/LAST frames of stage 8.
Read-only: measures pixels and render passes, never renders.

Why: every composition and every FIRST/KEY/LAST frame needs a measured analysis showing that the subject wins its
frame, the frame's geometry is deliberate and the scene supports the subject (it fits harmoniously, it doesn't
compete). Code measures, the eye decides: no image metric predicted the user's picks (AUC <= 0.65), but measurements
reliably catch the flaws (cut or cornered subjects, near-misses, near-level lines, rivals, merges, soft subjects, dead
zones) and order the eye pass. Thresholds: composition-analysis sections C (gates), D (composition), E (harmony).

Subcommands
  frame     one frame -> <out>.analysis.json + <out>_tile.jpg (gates G, composition D, scene-subject harmony E)
  sameness  a set of frames -> pairwise thumbnail similarity; pairs >= 0.72 flagged
  cuts      cut pairs (shot N's LAST -> shot N+1's FIRST) -> eye jump, angle or scale change, brightest-region jump

Usage
  <python> comp_analysis.py frame --image F.png [--depth F_z.exr] [--mask S.png | --index F_idx.exr --ids 3,25-31]
        [--product-mask P.png | --product-ids 1-100] [--glass-ids 28,29] [--prop-ids 101-120] [--camera cam.json]
        [--brief brief.json] [--lines lines.json] [--facing left|right] [--subject-xy U,V] [--out PREFIX] [--no-tile]
        [--quiet]
  <python> comp_analysis.py sameness DIR|IMAGE ... [--masks DIR] [--thr 0.72] [--adjacent] [--out sameness.json]
        [--sheet pairs.jpg]
  <python> comp_analysis.py cuts cuts.json [--out cuts.report.json]
  <python> = any Python with numpy, scipy and Pillow; scikit-image for the line items (without it they report n/a);
  OpenEXR for .exr inputs. Exit code 0 = PASS (or PASS with reasons owed), 1 = FAIL, 2 = bad input.

Inputs (frame)
  --image    the preview in the review look: PNG / JPG / TIFF (display-referred), or EXR (scene-linear Rec.709, sRGB-
             encoded unless --exr-encoding none). Analysed at <= 960 px wide; any aspect ratio.
  --depth    planar Z in metres (Blender's Depth pass): EXR (channel *Depth.Z, *.Z, Z or --depth-channel; multi-part
             multilayer EXRs are read part by part), .npy, or .npz (key "depth").
  --mask     the subject mask (white = subject). Or --index (object / part index: EXR *IndexOB / *Object Index, .npz key
             "index", .npy or an integer PNG) with --ids "3,25-31" naming the subject's ids. A subject must be named in
             <= 4 words (brief "subject") and masked; an element subject (reflection, light patch, shadow, accent) gets a
             derived mask made Blender-side.
  --product-mask / --product-ids  the product ("1-100", ">0"). --glass-ids: transparent product parts (left out of
             the outline separation, as reads_metric does with a smoked lid). Set props (cut, kiss, merge, rival checks)
             are --prop-ids, or by default every index id mostly outside the product and the subject that covers < 25 %
             of the frame (a wall, floor or backdrop is the ground).
  --camera   JSON (or a JSON holding a "camera" object): focal_mm (alias lens), fstop (the render camera's f-stop; with a
             physical-camera setup that is N_eff), focus_m, sensor_w_mm (36). Optional: roll_deg (exact roll; G7 uses
             it), coc_model "cycles" (default: Blender's thin lens, blur on the sensor = (F/N)(F/s)|z-s|/z) or "thinlens"
             (a physical lens, F^2/(N(s-F))|z-s|/z; over-reads Blender blur by s/(s-F), x3.7 at close-ups), n_eff
             (diffraction disc N_eff/24 px @1920; default fstop), depth "radial" (ray length, not planar Z), and
             Blender-side facts when known: subject_in_frame, subject_visible, product_in_frame; az, el, field_w_mm
             (cuts).
  --brief    JSON: subject (<= 4 words), role (wide|medium|hero|packshot|field|insert|macro), size_band [lo, hi],
             size_of (product|subject), size_measure (width|height|area), anchor ("anchor" | "centre"), anchor_system
             (thirds|phi|diagonal|centre) or anchor_uv [u, v], mode (calm|field|dynamic|macro|symmetric), facing
             (left|right), scope (whole|most|part), crop (a declared bold crop), dot (a dot subject), symmetric,
             rhythm_row, dutch, low_key (a declared black void: dead thirds report only), edge_pad (0.03), accent_max
             (0.04), accent_expected. Defaults: mode calm, anchor policy "anchor", no size band.
  --lines    optional projected 3D edges written Blender-side (exact, occlusion-aware is best): a list of
             {"kind": "product"|"set", "name": str, "pts": [[x, y], ...]} or [kind, name, pts], image pixels, or
             {"size": [W, H], "lines": [...]}; clipped to the frame. Used for G6 (parallels / continuations between
             product and set edges) and, when given, instead of the image's Hough lines for G7 and D3.

Outputs (frame)
  <out>.analysis.json  inputs, subject / product facts, items [{id, name, class, status, values, target, note}],
                       verdict (PASS | PASS-REASONS | FAIL), fails, reasons_owed, notes, timing. --out defaults to the
                       image path without its extension.
  <out>_tile.jpg       the frame dimmed; thirds (white) and phi (amber, dashed) grid, diagonal nodes (violet), centre;
                       subject outline (red), its centroid and a line to its anchor (yellow); product outline (white);
                       lines that lead to the subject (green), strong lines leading elsewhere (yellow), G7 dead-band
                       lines (pink, labelled), other long lines (grey);
                       rivals (orange boxes), accent pixels (cyan), the weight centroid (blue), flagged edges (red bars)
                       and the key numbers. Read the clean frame first, then the tile.

Classes (C / D / E of the composition analysis; status pass | warn | fail | n/a)
  gate    a fail repairs or rejects the frame: G1 subject defined (mask >= 0.3 %, a dot >= 0.02 %), G2 in frame, G3 focus
          (depth + camera), G4 the subject wins + no rival, G5 edges (near-miss, nick, whole clearance, edge band, a
          contrasty line hugging an edge, prop sliver or kiss), G6 tangents (index props; projected lines), G7 dominant
          lines + roll, DZ dead thirds, E1a the subject separates (by tone, or at least by focus), E1b outline separation
          (when the product is the main shape), E1c background >= 1 EV or a distinct hue, E2a prop rivals, E3 colour
          (field chroma, hue clusters, accent size).
  +R      (the dagger in the docs) a fail passes only with a written reason; warn is a note: G1b a dot's 4 of 6
          conditions, G5b highlights / colour pops at an edge, G5p product parts kissing an edge, D1 placement and D1b
          lead room, D3 divisions, D7 size + figure-ground, DZb dead band, E1d a dark product's ground, E2b image-region
          rivals, E2c masses <= 7, E2d a set object sharper than the subject, E3b the accent off the subject.
  report  ranks and informs the eye pass: D2 eye path, D4 negative space, D5 masses, D6 balance, D8 thumbnail + crop,
          G3 sharpness when there is no depth + camera.
  Calibration: E1a by tone alone, E2c, E3b, G1b, G5b and G5p are written as gates in the rubric but failed many
  accepted frames of an audited film, so they owe a reason instead (E1a still gates when neither tone nor focus
  separates the subject). G3, G7, E1b, sameness and the cut numbers reproduce the tools they were generalised from.
  Pixel thresholds are written for 1920 px wide (scaled by width/1920); the 960-px ones scale by width/960.

Not measured here (Blender side): the geometric pre-gate (camera clearance, foreground occluders by ray grid, set
hiding the product, projected hull in frame, occlusion-aware projected edges for G6/G7, glass-cover azimuth,
intersections); G8 technical + reads (scripts/reads_metric.py is the calibrated reads gate); G9 glossy black (mirror
probe); E4 light (source, key side continuity, bounded light shape); E5 depth layers and scale beyond the depth pass;
E6 set continuity and logged dressing moves.

Sameness  similarity = (squint correlation + 3-level Notan agreement + subject-box IoU) / 3 on 32x18 thumbnails (CIE L*,
  Gaussian sigma 1 % W). --masks DIR (<stem>.png or <stem>_mask.png per image) measures the box IoU; without masks the
  term is 0.5, as calibrated. Pairs >= --thr are flagged; --adjacent also reports consecutive pairs (the edit order).

Cuts  cuts.json = [{"name": "01-02", "light_cut": false,
                    "out": {"image": p, "mask": p | "index": p, "ids": "3,25" | "eye": [u, v], "camera": {...} | path},
                    "in":  {... the same ...}}, ...]   (relative paths resolve against the JSON's folder)
  camera: az, el (deg) and field_w_mm (field width at the subject), or focal_mm + focus_m (+ sensor_w_mm) to derive it.
  Per cut: eye jump between subject centroids <= 25 % W; angle sqrt(daz^2 + del^2) >= 30 deg or field ratio >= x1.5;
  brightest-region jump <= 50 % W unless light_cut.
"""
import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

try:
    from skimage.feature import canny as _sk_canny
    from skimage.transform import probabilistic_hough_line as _sk_hough
    HAVE_SK = True
except Exception:  # noqa: BLE001
    HAVE_SK = False

VERSION = "1.0"
PHI = (1 + 5 ** 0.5) / 2
AW = 960                                   # analysis width (px)
SQ_W = 96                                  # squint / thumbnail width (px)
LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)
NEG_BAND = {"calm": (0.40, 0.70), "field": (0.55, 0.85), "dynamic": (0.30, 0.60), "macro": (0.25, 0.60),
            "symmetric": (0.35, 0.70)}
ROLE_SIZE = {"wide": ("width", 0.08, 0.12), "medium": ("width", 0.12, 0.25), "hero": ("width", 0.20, 0.32),
             "packshot": ("height", 0.55, 0.78), "field": ("area", 0.03, 0.15)}
IMG_EXT = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".exr", ".webp", ".bmp"}


# ================================================================================================================ I/O
_EXR_CACHE = {}


def _exr_channels(path):
    """{full channel name: 2-D array} from a (multi-part) EXR; decoded once per path (image, depth and index are often
    passes of one multilayer file)"""
    key = str(Path(path).resolve())
    if key in _EXR_CACHE:
        return _EXR_CACHE[key]
    import OpenEXR
    out = {}
    if hasattr(OpenEXR, "File"):
        with OpenEXR.File(str(path), separate_channels=True) as f:
            for p in f.parts:
                for k, v in p.channels.items():
                    a = np.asarray(v.pixels)
                    if a.ndim == 2:
                        out[k] = a
                    else:
                        for i in range(a.shape[2]):
                            out[f"{k}.{'RGBA'[i] if i < 4 else i}"] = a[..., i]
        _EXR_CACHE[key] = out
        return out
    import Imath
    f = OpenEXR.InputFile(str(path))
    dw = f.header()["dataWindow"]
    w, h = dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1
    pt = Imath.PixelType(Imath.PixelType.FLOAT)
    for k in f.header()["channels"]:
        out[k] = np.frombuffer(f.channel(k, pt), np.float32).reshape(h, w)
    _EXR_CACHE[key] = out
    return out


def _pick_channel(chans, kind, prefer=None, path=""):
    names = list(chans)
    if prefer:
        hit = [n for n in names if prefer.lower() in n.lower()]
        if not hit:
            raise SystemExit(f"channel '{prefer}' not found in {path}: {names}")
        return chans[hit[0]]
    if len(names) == 1:
        return chans[names[0]]
    low = {n: n.lower() for n in names}
    if kind == "depth":
        tests = (lambda s: s.endswith("depth.z"), lambda s: s == "z" or s.endswith(".z"), lambda s: "depth" in s)
    elif kind == "index":
        tests = (lambda s: "indexob" in s or "object index" in s, lambda s: "index" in s)
    else:
        tests = (lambda s: s.endswith(".r") or s == "r",)
    for t in tests:
        hit = [n for n in names if t(low[n])]
        if hit:
            return chans[hit[0]]
    raise SystemExit(f"no {kind} channel in {path}: {names} (pass --{kind}-channel)")


def _rgb_from_exr(chans):
    groups = {}
    for n, a in chans.items():
        pre, _, c = n.rpartition(".")
        if c.upper() in "RGB" and len(c) == 1:
            groups.setdefault(pre, {})[c.upper()] = a
    full = {p: g for p, g in groups.items() if all(c in g for c in "RGB")}
    if not full:
        raise SystemExit(f"no RGB channels in the EXR: {list(chans)[:12]}")
    pref = sorted(full, key=lambda p: (0 if "combined" in p.lower() or p in ("", "rgba", "image") else 1, p))
    g = full[pref[0]]
    return np.dstack([g["R"], g["G"], g["B"]]).astype(np.float32, copy=False)


def load_image(path, exr_encoding="srgb"):
    """-> H x W x 3 float32 display-referred 0..1"""
    p = Path(path)
    if p.suffix.lower() == ".exr":
        rgb = _rgb_from_exr(_exr_channels(p))
        rgb = np.nan_to_num(rgb, nan=0.0, posinf=1.0, neginf=0.0)
        return lin_to_srgb(rgb) if exr_encoding == "srgb" else np.clip(rgb, 0, 1)
    if p.suffix.lower() in (".tif", ".tiff"):
        try:
            import imageio.v3 as iio
            a = np.asarray(iio.imread(p))
            if a.ndim == 2:
                a = np.dstack([a] * 3)
            a = a[..., :3]
            if a.dtype.kind in "ui":
                return a.astype(np.float32) / float(np.iinfo(a.dtype).max)
            return np.clip(a.astype(np.float32), 0, 1)
        except Exception:  # noqa: BLE001
            pass
    im = Image.open(p)
    if im.mode in ("I;16", "I;16B", "I;16L", "I"):
        a = np.asarray(im, np.float32) / (65535.0 if "16" in im.mode else max(1.0, float(np.asarray(im).max())))
        return np.dstack([a] * 3)
    if im.mode == "F":
        return np.dstack([np.clip(np.asarray(im, np.float32), 0, 1)] * 3)
    return np.asarray(im.convert("RGB"), np.float32) / 255.0


def load_array(path, kind, channel=None):
    """depth / index buffer -> 2-D float32"""
    p = Path(path)
    suf = p.suffix.lower()
    if suf == ".npy":
        a = np.load(p)
    elif suf == ".npz":
        z = np.load(p)
        key = channel or (kind if kind in z.files else z.files[0])
        a = z[key]
    elif suf == ".exr":
        a = _pick_channel(_exr_channels(p), kind, channel, p)
    else:
        a = np.asarray(Image.open(p))
        if a.ndim == 3:
            a = a[..., 0]
    a = np.asarray(a, np.float32)
    if a.ndim == 3:
        a = a[..., 0]
    return a


def load_mask(path):
    p = Path(path)
    if p.suffix.lower() == ".exr":
        ch = _exr_channels(p)
        a = ch.get(next((n for n in ch if n.upper().endswith(".A") or n.upper() == "A"), ""), None)
        if a is None or float(np.ptp(a)) == 0:
            a = ch[sorted(ch)[0]]
        return np.asarray(a, np.float32) > 0.5
    im = Image.open(p)
    a = np.asarray(im)
    if a.ndim == 3:
        if a.shape[2] == 4 and a[..., 3].min() < a[..., 3].max():
            a = a[..., 3]
        else:
            a = a[..., :3].max(axis=2)
    mx = float(np.iinfo(a.dtype).max) if a.dtype.kind in "ui" else 1.0
    return a.astype(np.float32) / mx > 0.5


def load_json_arg(s, what):
    if not s:
        return {}
    p = Path(s)
    try:
        d = json.loads(p.read_text()) if p.exists() else json.loads(s)
    except json.JSONDecodeError as e:
        raise SystemExit(f"--{what}: not a JSON file or JSON text ({e})")
    if not isinstance(d, dict):
        raise SystemExit(f"--{what}: expected a JSON object")
    return d


def norm_camera(d):
    """flatten {"camera": {...}} and map common aliases"""
    c = {k: v for k, v in d.items() if not isinstance(v, (dict, list))}
    if isinstance(d.get("camera"), dict):
        c.update({k: v for k, v in d["camera"].items() if not isinstance(v, dict)})
    alias = {"focal_mm": ("lens", "focal", "focal_length_mm", "lens_mm"), "fstop": ("N", "f_number", "fnumber", "f_stop"),
             "focus_m": ("focus_distance_m", "focus_dist_m", "focus_distance"),
             "sensor_w_mm": ("sensor_width_mm", "sensor_width", "sensor"), "field_w_mm": ("W", "field_width_mm")}
    for k, al in alias.items():
        if k not in c:
            for x in al:
                if isinstance(c.get(x), (int, float)):
                    c[k] = float(c[x])
                    break
    return c


def parse_ids(spec, index=None):
    spec = str(spec).strip()
    if spec in (">0", "all", "*"):
        return [int(v) for v in np.unique(index) if v > 0] if index is not None else []
    out = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part[1:]:
            a, b = part.split("-", 1)
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


# ================================================================================================================ maths
def rs(a, w, h, how="bilinear"):
    a = np.asarray(a, np.float32)
    if a.shape == (h, w):
        return a.copy()
    m = {"bilinear": Image.BILINEAR, "nearest": Image.NEAREST, "box": Image.BOX}[how]
    return np.asarray(Image.fromarray(a).resize((w, h), m), np.float32)


def rs_mask(m, w, h):
    if m is None:
        return None
    if m.shape == (h, w):
        return m.copy()
    f = rs(m.astype(np.float32), w, h, "box")
    out = f > 0.5
    if not out.any() and m.any():
        out = f >= 0.5 * f.max()
    return out


def srgb_to_lin(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4).astype(np.float32)


def lin_to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * np.power(c, 1 / 2.4) - 0.055).astype(np.float32)


_M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566],
                [0.0883024619, 0.2817188376, 0.6299787005]], np.float32)
_M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099],
                [0.0259040371, 0.7827717662, -0.8086757660]], np.float32)


def oklab(lin):
    lab = np.cbrt(np.maximum(lin @ _M1.T, 0)) @ _M2.T
    return lab[..., 0], lab[..., 1], lab[..., 2]


def lstar01(lin):
    """CIE L*/100 from linear Rec.709 (D65)"""
    Y = lin @ LUMA
    f = np.where(Y > 0.008856, np.cbrt(np.maximum(Y, 0)), 7.787 * Y + 16 / 116)
    return (116 * f - 16) / 100.0


def ramp(x, a, b):
    if b == a:
        return float(x >= b)
    return float(min(1.0, max(0.0, (x - a) / (b - a))))


def circ_dist(a, b):
    return np.abs((np.asarray(a) - b + 180.0) % 360.0 - 180.0)


def otsu(x, classes=3, bins=128):
    """multi-level Otsu thresholds (2 or 3 classes) in numpy; returns (thresholds, eta = between / total variance)"""
    v = np.asarray(x, np.float64).ravel()
    lo, hi = float(v.min()), float(v.max())
    if hi - lo < 1e-6:
        return np.array([lo] * (classes - 1)), 0.0
    hist, edges = np.histogram(v, bins=bins, range=(lo, hi))
    p = hist / hist.sum()
    c = (edges[:-1] + edges[1:]) / 2
    P, S = np.cumsum(p), np.cumsum(p * c)
    tot_m = S[-1]
    tot_var = float((p * (c - tot_m) ** 2).sum()) + 1e-12
    with np.errstate(divide="ignore", invalid="ignore"):
        if classes == 2:
            w0, m0 = P[:-1], S[:-1]
            w1, m1 = 1 - w0, tot_m - m0
            var = m0 ** 2 / w0 + m1 ** 2 / w1
            var[(w0 <= 0) | (w1 <= 0)] = -np.inf
            i = int(np.argmax(var))
            return np.array([edges[i + 1]]), float((var[i] - tot_m ** 2) / tot_var)
        i = np.arange(bins - 1)[:, None]
        j = np.arange(bins - 1)[None, :]
        w0, m0 = P[i], S[i]
        w1, m1 = P[j] - P[i], S[j] - S[i]
        w2, m2 = 1 - P[j], tot_m - S[j]
        var = m0 ** 2 / w0 + m1 ** 2 / w1 + m2 ** 2 / w2
        var[(j <= i) | (w0 <= 1e-9) | (w1 <= 1e-9) | (w2 <= 1e-9)] = -np.inf
    a, b = np.unravel_index(int(np.argmax(var)), var.shape)
    return np.array([edges[a + 1], edges[b + 1]]), float((var[a, b] - tot_m ** 2) / tot_var)


def spectral_residual(lum, w=128):
    """Hou & Zhang 2007 saliency at w px wide"""
    h = max(8, int(round(lum.shape[0] * w / lum.shape[1])))
    s = rs(lum, w, h)
    F = np.fft.fft2(s)
    A = np.log(np.abs(F) + 1e-6)
    R = A - ndi.uniform_filter(A, 3, mode="nearest")
    S = np.abs(np.fft.ifft2(np.exp(R + 1j * np.angle(F)))) ** 2
    S = ndi.gaussian_filter(S, 2.5)
    return S / (S.max() + 1e-12)


def band_mean(V, region, sigma):
    num = ndi.gaussian_filter(np.where(region, V, 0.0).astype(np.float32), sigma)
    den = ndi.gaussian_filter(region.astype(np.float32), sigma)
    return num / np.maximum(den, 1e-6)


def outline(m):
    return m & ~ndi.binary_erosion(m)


def mask_facts(m):
    """centroid (u, v), bbox (x0, y0, x1, y1 px), gaps per edge (fraction of that dimension), share"""
    H, W = m.shape
    ys, xs = np.nonzero(m)
    if xs.size == 0:
        return None
    x0, x1, y0, y1 = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
    return {"centroid_uv": [float(xs.mean() + 0.5) / W, float(ys.mean() + 0.5) / H], "bbox_px": [x0, y0, x1, y1],
            "gaps": {"left": x0 / W, "right": (W - 1 - x1) / W, "top": y0 / H, "bottom": (H - 1 - y1) / H},
            "share": float(xs.size) / m.size, "width_share": (x1 - x0 + 1) / W, "height_share": (y1 - y0 + 1) / H}


def largest_rect(grid):
    """largest all-True axis-aligned rectangle (cells) - histogram method"""
    hh, ww = grid.shape
    best = 0
    hgt = np.zeros(ww, int)
    for row in grid:
        hgt = np.where(row, hgt + 1, 0)
        st = []
        for i in range(ww + 1):
            cur = hgt[i] if i < ww else 0
            start = i
            while st and st[-1][1] >= cur:
                s0, h0 = st.pop()
                best = max(best, h0 * (i - s0))
                start = s0
            st.append((start, cur))
    return best / float(hh * ww)


def anchors(W, H):
    """placement systems, normalised (u, v)"""
    t, p = (1 / 3, 2 / 3), (1 - 1 / PHI, 1 / PHI)
    if W >= H:
        a = H / (2.0 * W)
        diag = [(a, 0.5), (1 - a, 0.5)]
    else:
        a = W / (2.0 * H)
        diag = [(0.5, a), (0.5, 1 - a)]
    return {"thirds": [(x, y) for x in t for y in t], "phi": [(x, y) for x in p for y in p], "diagonal": diag,
            "centre": [(0.5, 0.5)]}


def dist_w(u0, v0, u1, v1, A):
    """distance in fractions of the frame width (A = W/H)"""
    return math.hypot(u0 - u1, (v0 - v1) / A)


# ================================================================================================================ lines
def _segments(edges, min_len, gap):
    if not HAVE_SK or not edges.any():
        return np.zeros((0, 4), np.float32)
    segs = _sk_hough(edges, threshold=12, line_length=int(min_len), line_gap=int(gap), rng=np.random.default_rng(0))
    if not segs:
        return np.zeros((0, 4), np.float32)
    return np.array([(a[0], a[1], b[0], b[1]) for a, b in segs], np.float32)


def _seg_len(S):
    return np.hypot(S[:, 2] - S[:, 0], S[:, 3] - S[:, 1])


def refine_segments(S, edges, min_len):
    """least-squares (PCA) angle and extent from the edge pixels along each long segment"""
    if not len(S):
        return S
    ys, xs = np.nonzero(edges)
    P = np.stack([xs, ys], 1).astype(np.float32)
    out = S.copy()
    for i in np.nonzero(_seg_len(S) >= min_len)[0]:
        x0, y0, x1, y1 = S[i]
        d = np.array([x1 - x0, y1 - y0], np.float32)
        n_ = float(np.hypot(*d))
        d /= n_
        nrm = np.array([-d[1], d[0]], np.float32)
        q = P - (x0, y0)
        t = q @ d
        sel = (np.abs(q @ nrm) <= 1.5) & (t >= -2) & (t <= n_ + 2)
        if sel.sum() < 10:
            continue
        Q = P[sel]
        c = Q.mean(0)
        ev, vec = np.linalg.eigh(np.cov((Q - c).T))
        dd = vec[:, 1]
        tt = (Q - c) @ dd
        out[i] = (c[0] + dd[0] * tt.min(), c[1] + dd[1] * tt.min(), c[0] + dd[0] * tt.max(), c[1] + dd[1] * tt.max())
    return out


def merge_collinear(S, tol_deg, tol_px, gap_px):
    segs = [list(map(float, s)) for s in S[np.argsort(-_seg_len(S))]] if len(S) else []
    changed = True
    while changed:
        changed = False
        for i in range(len(segs)):
            ax0, ay0, ax1, ay1 = segs[i]
            la = math.hypot(ax1 - ax0, ay1 - ay0)
            if la < 1e-6:
                continue
            ux, uy = (ax1 - ax0) / la, (ay1 - ay0) / la
            for j in range(i + 1, len(segs)):
                bx0, by0, bx1, by1 = segs[j]
                lb = math.hypot(bx1 - bx0, by1 - by0)
                if lb < 1e-6:
                    continue
                cosang = abs(ux * (bx1 - bx0) / lb + uy * (by1 - by0) / lb)
                if cosang < math.cos(math.radians(tol_deg)):
                    continue
                d0 = abs(-(bx0 - ax0) * uy + (by0 - ay0) * ux)
                d1 = abs(-(bx1 - ax0) * uy + (by1 - ay0) * ux)
                if max(d0, d1) > tol_px:
                    continue
                t0 = (bx0 - ax0) * ux + (by0 - ay0) * uy
                t1 = (bx1 - ax0) * ux + (by1 - ay0) * uy
                gap = max(0.0, min(t0, t1) - la, -max(t0, t1))
                if gap > gap_px:
                    continue
                lo, hi = min(0.0, t0, t1), max(la, t0, t1)
                segs[i] = [ax0 + ux * lo, ay0 + uy * lo, ax0 + ux * hi, ay0 + uy * hi]
                del segs[j]
                changed = True
                break
            if changed:
                break
    return np.array(segs, np.float32).reshape(-1, 4)


def seg_angle_dev(S):
    """angle in [0, 180) (image coords, y down) and deviation from the nearest frame axis (deg)"""
    ang = np.degrees(np.arctan2(S[:, 3] - S[:, 1], S[:, 2] - S[:, 0])) % 180.0
    dev = np.minimum(ang % 90.0, 90.0 - ang % 90.0)
    return ang, dev


def line_dist_to_points(S, pts):
    """min distance from each (infinite) segment line to a set of points"""
    if not len(S) or not len(pts):
        return np.full(len(S), np.inf)
    d = np.stack([S[:, 2] - S[:, 0], S[:, 3] - S[:, 1]], 1)
    d /= np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)
    q = pts[None, :, :] - S[:, None, :2]
    perp = np.abs(q[..., 0] * d[:, None, 1] - q[..., 1] * d[:, None, 0])
    return perp.min(1)


def load_projected_lines(path, W, H):
    d = json.loads(Path(path).read_text())
    sx = sy = 1.0
    if isinstance(d, dict):
        if d.get("size"):
            sx, sy = W / float(d["size"][0]), H / float(d["size"][1])
        d = d.get("lines", [])
    out = []
    for e in d:
        if isinstance(e, dict):
            kind, name, pts = e.get("kind", "set"), e.get("name", "?"), e.get("pts", [])
        else:
            kind, name, pts = e[0], e[1], e[2]
        pts = np.asarray(pts, np.float32).reshape(-1, 2) * (sx, sy)
        inb = (pts[:, 0] >= 0) & (pts[:, 0] <= W - 1) & (pts[:, 1] >= 0) & (pts[:, 1] <= H - 1)
        pts = pts[inb]                                       # the visible run inside the frame
        if len(pts) >= 2:
            out.append((str(kind), str(name), pts))
    return out


def projected_tangents(lines, W, H):
    """G6 on projected edges: product/set parallels within 2 deg and <= 0.6 % H over >= 3 % W; continuations
    (collinear within 1 deg and 0.5 % H, end gap <= 3 % W)"""
    segs = []
    for kind, name, p in lines:
        (x0, y0), (x1, y1) = p[0], p[-1]
        L_ = math.hypot(x1 - x0, y1 - y0)
        if L_ >= 0.03 * W:
            segs.append((kind, name, (x0, y0, x1, y1), math.degrees(math.atan2(-(y1 - y0), x1 - x0)), L_))
    notes = []
    prod = [s for s in segs if s[0] == "product"]
    sets = [s for s in segs if s[0] != "product"]
    for a in prod:
        for b in sets:
            da = abs(((a[3] - b[3]) + 90) % 180 - 90)
            if da > 2.0:
                continue
            ax0, ay0, ax1, ay1 = a[2]
            n_ = math.hypot(ax1 - ax0, ay1 - ay0) or 1.0
            ux, uy = (ax1 - ax0) / n_, (ay1 - ay0) / n_
            t, dp = [], []
            for bx, by in ((b[2][0], b[2][1]), (b[2][2], b[2][3])):
                t.append((bx - ax0) * ux + (by - ay0) * uy)
                dp.append(abs(-(bx - ax0) * uy + (by - ay0) * ux))
            sep = min(dp)
            overlap = min(n_, max(t)) - max(0.0, min(t))
            if 0.0 < sep <= 0.006 * H and overlap >= 0.03 * W:
                notes.append(f"{a[1]} parallel to {b[1]} {sep:.1f} px apart")
            elif sep <= 0.005 * H and overlap <= 0 and min(abs(min(t) - n_), abs(max(t))) <= 0.03 * W and da <= 1.0:
                notes.append(f"{a[1]} continues into {b[1]}")
    return notes


# ================================================================================================================ frame
class Item:
    def __init__(self, id_, name, cls, status, values=None, target="", note=""):
        self.d = {"id": id_, "name": name, "class": cls, "status": status, "values": values or {}, "target": target,
                  "note": note}


def _r(x, n=3):
    if x is None:
        return None
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if isinstance(x, (int, np.integer)):
        return int(x)
    try:
        xf = float(x)
    except (TypeError, ValueError):
        return x
    return None if not math.isfinite(xf) else round(xf, n)


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return _r(o, 4)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return _clean(o.tolist())
    return o


def analyse_frame(a):
    t_start = time.time()
    cam = norm_camera(load_json_arg(a.camera, "camera"))
    brief = load_json_arg(a.brief, "brief")
    if a.facing:
        brief["facing"] = a.facing
    rgb = load_image(a.image, a.exr_encoding)
    H, W = rgb.shape[:2]
    A = W / H

    def fit(arr, nearest=True):
        if arr is None:
            return None
        if arr.shape[:2] != (H, W):
            arr = rs(arr, W, H, "nearest" if nearest else "bilinear")
        return arr

    depth = None
    if a.depth:
        depth = fit(load_array(a.depth, "depth", a.depth_channel))
        depth = np.where(np.isfinite(depth) & (depth > 0), depth, 1e5).astype(np.float32)
        depth = np.minimum(depth, 1e5)
        if str(cam.get("depth", "planar")).lower() == "radial" and cam.get("focal_mm"):
            fx = cam["focal_mm"] / cam.get("sensor_w_mm", 36.0) * W
            uu, vv = np.meshgrid(np.arange(W) + 0.5 - W / 2, np.arange(H) + 0.5 - H / 2)
            depth = depth / np.sqrt(1 + (uu / fx) ** 2 + (vv / fx) ** 2)
    index = None
    if a.index:
        index = np.rint(fit(load_array(a.index, "index", a.index_channel))).astype(np.int32)
    sub, sub_src = None, "none"
    sub_ids, prod_ids = [], []
    if a.mask:
        sub = fit(load_mask(a.mask).astype(np.float32)) > 0.5
        sub_src = "mask"
    elif index is not None and a.ids:
        sub_ids = parse_ids(a.ids, index)
        sub = np.isin(index, sub_ids)
        sub_src = "index"
    prod = None
    if a.product_mask:
        prod = fit(load_mask(a.product_mask).astype(np.float32)) > 0.5
    elif index is not None and a.product_ids:
        prod_ids = parse_ids(a.product_ids, index)
        prod = np.isin(index, prod_ids)
    if sub is None and a.subject_xy:
        su, sv = (float(x) for x in a.subject_xy.split(","))
        yy, xx = np.mgrid[0:H, 0:W]
        sub = np.hypot((xx + 0.5) / W - su, ((yy + 0.5) / H - sv) / A) * W < 0.035 * H
        sub_src = "point"
    if sub is None and prod is not None:
        sub, sub_src = prod.copy(), "product"
    notes = []
    if sub is not None and not sub.any():
        notes.append("subject mask is empty")
    has_sub = sub is not None and bool(sub.any())
    if prod is None and has_sub and sub_src in ("mask", "index"):
        prod = sub.copy()                         # no product mask: the subject stands in for it
    has_prod = prod is not None and bool(prod.any())
    glass = np.isin(index, parse_ids(a.glass_ids, index)) if (index is not None and a.glass_ids) else None

    # ------------------------------------------------------------------------------------------- analysis arrays
    w = min(AW, W)
    h = max(2, int(round(H * w / W)))
    k96 = w / 960.0                               # 960-px thresholds scale by this
    rgbA = np.dstack([rs(rgb[..., i], w, h) for i in range(3)]) if (w, h) != (W, H) else rgb
    rgbA = np.clip(rgbA, 0, 1)
    lin = srgb_to_lin(rgbA)
    L, oa, ob = oklab(lin)
    C = np.hypot(oa, ob)
    hue = np.degrees(np.arctan2(ob, oa)) % 360.0
    Ylin = lin @ LUMA
    Yd = rgbA @ LUMA
    subA = rs_mask(sub, w, h) if has_sub else None
    prodA = rs_mask(prod, w, h) if has_prod else None
    glassA = rs_mask(glass, w, h) if glass is not None and glass.any() else None
    idxA = rs(index, w, h, "nearest").astype(np.int32) if index is not None else None
    depA = rs(depth, w, h, "nearest") if depth is not None else None
    sfacts = mask_facts(sub) if has_sub else None
    pfacts = mask_facts(prod) if has_prod else None
    subj_name = brief.get("subject") or (f"ids {a.ids}" if sub_src == "index" else sub_src)

    # squint (OKLab L, sigma 1 % W, 96 px wide)
    hq = max(2, int(round(SQ_W * h / w)))
    Sq = rs(ndi.gaussian_filter(L, 0.01 * w), SQ_W, hq)
    subQ = rs_mask(subA, SQ_W, hq) if has_sub else None
    prodQ = rs_mask(prodA, SQ_W, hq) if has_prod else None

    def ringq(m, frac=0.04):
        return ndi.binary_dilation(m, iterations=max(1, int(round(frac * SQ_W)))) & ~m

    # sharpness
    lap = np.abs(ndi.laplace(ndi.gaussian_filter(L, 0.8)))
    T = max(4, int(round(16 * k96)))
    th_, tw_ = h // T, w // T
    log_ = np.abs(ndi.gaussian_laplace(Yd, 0.8))
    tiles = log_[:th_ * T, :tw_ * T].reshape(th_, T, tw_, T).transpose(0, 2, 1, 3).reshape(th_, tw_, -1)
    tile_s = np.percentile(tiles, 95, axis=2)
    tile_ref = float(np.percentile(tile_s, 95)) + 1e-6

    # saliency (spectral residual; x centre prior for the cue, without it for balance)
    Sal = rs(spectral_residual(L), w, h)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    prior = np.exp(-(((xx - w / 2) / w) ** 2 + ((yy - h / 2) / w) ** 2) / (2 * 0.3 ** 2))
    Sp = Sal * prior

    # field hue and accent (OKLCH)
    chrom = C >= 0.02
    hist, _ = np.histogram(hue[chrom], bins=36, range=(0, 360), weights=C[chrom])
    hs = hist + 0.5 * (np.roll(hist, 1) + np.roll(hist, -1))
    if hs.sum() > 0:
        pk = (int(np.argmax(hs)) + 0.5) * 10.0
        near = chrom & (circ_dist(hue, pk) <= 45)
        wts = C[near]
        field_hue = float(math.degrees(math.atan2((np.sin(np.radians(hue[near])) * wts).sum(),
                                                  (np.cos(np.radians(hue[near])) * wts).sum())) % 360)
    else:
        field_hue = float("nan")
    dh = circ_dist(hue, field_hue) if math.isfinite(field_hue) else np.zeros_like(hue)
    accent = ((C >= 0.07) & (dh >= 60)) | ((L >= 0.85) & (C >= 0.10))
    acc_n = int(accent.sum())
    acc_min = max(8, int(30 * k96 * k96))

    # CoC
    coc = None
    coc_info = {}
    if depA is not None and all(k in cam for k in ("focal_mm", "fstop", "focus_m")):
        F = cam["focal_mm"] / 1000.0
        N = float(cam["fstop"])
        s_ = float(cam["focus_m"])
        sw = cam.get("sensor_w_mm", 36.0) / 1000.0
        model = str(cam.get("coc_model", "cycles")).lower()
        denom = s_ if model == "cycles" else max(s_ - F, 1e-6)
        z = np.clip(depA, 1e-4, 1e5)
        coc = np.abs((F / N) * F * (z - s_) / (z * denom)) / sw * 1920.0          # px @1920
        n_eff = float(cam.get("n_eff", N))
        coc_info = {"model": model, "diffraction_px_1920": n_eff / 24.0 * (36.0 / (sw * 1000.0))}

    # lines: luminance edges + depth edges + mask / index boundaries, one Hough pass, refined and merged
    seg = np.zeros((0, 4), np.float32)
    con = np.zeros(0, np.float32)
    edges = None
    if HAVE_SK:
        e_lum = _sk_canny(L, sigma=2.0, low_threshold=0.80, high_threshold=0.92, use_quantiles=True)
        edges = e_lum.copy()
        if depA is not None:
            dl = np.log(np.clip(depA, 1e-3, 1e5))
            edges |= _sk_canny(dl, sigma=1.5, low_threshold=0.85, high_threshold=0.95, use_quantiles=True)
        bnd = np.zeros((h, w), bool)
        if idxA is not None:
            bnd[:, 1:] |= idxA[:, 1:] != idxA[:, :-1]
            bnd[1:, :] |= idxA[1:, :] != idxA[:-1, :]
        else:
            for m in (subA, prodA):
                if m is not None:
                    bnd |= outline(m)
        edges |= bnd
        bd = max(3, int(round(4 * k96)))
        edges[:bd] = edges[-bd:] = False
        edges[:, :bd] = edges[:, -bd:] = False
        seg = _segments(edges, max(24, int(0.05 * w)), max(3, int(round(5 * k96))))
        if len(seg) > 400:
            seg = seg[np.argsort(-_seg_len(seg))[:400]]
        seg = refine_segments(seg, edges, 0.10 * w)
        seg = merge_collinear(seg, 1.5, max(2.0, 3 * k96), 0.03 * w)
        G = ndi.gaussian_gradient_magnitude(L, 1.5)
        g99 = float(np.percentile(G, 99)) + 1e-6
        if len(seg):
            tt = np.linspace(0, 1, 24)[None, :]
            xs_ = np.clip(seg[:, :1] + (seg[:, 2:3] - seg[:, :1]) * tt, 0, w - 1).round().astype(int)
            ys_ = np.clip(seg[:, 1:2] + (seg[:, 3:4] - seg[:, 1:2]) * tt, 0, h - 1).round().astype(int)
            con = np.clip(G[ys_, xs_].mean(1) / g99, 0, 1).astype(np.float32)
    seg_len = _seg_len(seg) if len(seg) else np.zeros(0)
    seg_ang, seg_dev = seg_angle_dev(seg) if len(seg) else (np.zeros(0), np.zeros(0))
    plines = load_projected_lines(a.lines, W, H) if a.lines else []

    # squint classes (3-level Otsu) and masses
    thr3, _ = otsu(Sq, 3)
    cls = np.digitize(Sq, thr3)
    _, eta2 = otsu(Sq, 2)
    comps = []
    for c_ in range(3):
        lab_, n_ = ndi.label(cls == c_)
        for i in range(1, n_ + 1):
            mk = lab_ == i
            comps.append((float(mk.mean()), c_, mk))
    comps.sort(key=lambda t: -t[0])
    masses = [c_ for c_ in comps if c_[0] >= 0.02]

    # quiet (negative space)
    Lg = ndi.gaussian_filter(L, 3.0 * k96)
    sob = np.hypot(ndi.sobel(Lg, 0), ndi.sobel(Lg, 1))
    quiet = sob < 0.2 * float(np.percentile(sob, 99))
    if coc is not None:
        quiet |= coc >= 12.0
    if has_sub:
        quiet &= ~subA

    items = []
    add = items.append
    rivals = []                    # (bbox in analysis px, label) for the tile
    flagged_edges = set()

    # G1 is decided at the end (a dot subject needs the placement, line and space measurements); a placeholder keeps
    # it first in the list
    add(Item("G1", "subject defined", "gate", "n/a"))

    # ===================================================================================================== G2
    if has_sub:
        touch = {}
        for e, line_ in (("left", sub[:, 0]), ("right", sub[:, -1]), ("top", sub[0, :]), ("bottom", sub[-1, :])):
            n_t = int(line_.sum())
            ext = sfacts["height_share"] * H if e in ("left", "right") else sfacts["width_share"] * W
            if n_t >= 2:
                touch[e] = round(n_t / max(ext, 1), 3)
        crop = bool(brief.get("crop"))
        inf, vis = cam.get("subject_in_frame"), cam.get("subject_visible")
        if inf is not None:
            need = 0.6 if crop else 0.95
            ok = float(inf) >= need and (vis is None or float(vis) >= 0.8)
            st, note = ("pass" if ok else "fail"), f"in frame {float(inf):.2f}, visible {vis}"
        elif not touch:
            st, note = "pass", "not cut by the frame (image)"
        elif crop:
            st, note = "pass", (f"declared bold crop at {', '.join(touch)}; confirm >= 60 % in frame and >= 10 % cut "
                                f"Blender-side")
        else:
            st, note = "fail", f"subject cut at the {', '.join(touch)} edge(s); declare a bold crop or reframe"
        add(Item("G2", "subject in frame", "gate", st, {"touches": touch, "subject_in_frame": inf, "visible": vis},
                 ">= 95 % in frame and visibility >= 0.8; a declared bold crop >= 60 % in, >= 10 % cut", note))
    else:
        add(Item("G2", "subject in frame", "gate", "n/a", note="no subject"))

    # ===================================================================================================== G3
    sharp_rel = None
    if has_sub:
        mt = subA[:th_ * T, :tw_ * T].reshape(th_, T, tw_, T).mean((1, 3)) >= 0.3
        if mt.any():
            sharp_rel = [float(np.median(tile_s[mt])) / tile_ref, float(np.percentile(tile_s[mt], 90)) / tile_ref]
        else:
            md = ndi.binary_dilation(subA, iterations=3)
            v_ = float(np.percentile(log_[md], 95)) / tile_ref
            sharp_rel = [v_, v_]
    if coc is not None and has_sub:
        cs = coc[subA]
        med = float(np.median(cs))
        dif = coc_info["diffraction_px_1920"]
        comb = math.hypot(med, dif)
        st = "pass" if comb <= 2.0 else "fail"
        add(Item("G3", "subject in focus", "gate", st,
                 {"coc_median_px1920": _r(med, 2), "coc_p10": _r(np.percentile(cs, 10), 2),
                  "coc_p90": _r(np.percentile(cs, 90), 2), "diffraction_px1920": _r(dif, 2),
                  "combined_px1920": _r(comb, 2), "share_le_2px": _r(float((cs <= 2.0).mean())),
                  "model": coc_info["model"], "sharp_rel": [_r(x) for x in sharp_rel]},
                 "sqrt(CoC^2 + (N_eff/24)^2) <= 2 px @1920, median over the subject (its visible surface)",
                 "" if st == "pass" else f"subject soft: {comb:.2f} px @1920 (focus on the visible surface; "
                                         f"macro_focus.py for the stop and focus split)"))
    elif has_sub:
        st = "pass" if sharp_rel[0] >= 0.5 else "warn"
        add(Item("G3", "subject sharpness (image only)", "report", st, {"sharp_rel": [_r(x) for x in sharp_rel]},
                 "tile p95 |LoG| on the subject / the frame's p95 tile >= 0.5 reads sharp",
                 "no depth + camera: the CoC gate needs --depth and --camera"))
    else:
        add(Item("G3", "subject in focus", "gate", "n/a", note="no subject"))

    # ===================================================================================================== G4
    cue = {}
    sub_d = None
    if has_sub:
        sub_d = ndi.binary_dilation(subA, iterations=max(1, int(round(0.01 * w))))
        rq = ringq(subQ)
        dL_sq = abs(float(np.median(Sq[subQ])) - float(np.median(Sq[rq]))) if rq.any() else 0.0
        cue["a_contrast"] = dL_sq >= 0.10
        lap_sub = float(lap[subA].mean())
        lap_out = float(np.median(lap[~subA])) if (~subA).any() else 0.0
        cue["b_sharp"] = lap_sub >= 1.5 * lap_out + 1e-6
        sal_share = float(Sp[sub_d].sum() / (Sp.sum() + 1e-9))
        area_share = float(sub_d.mean())
        cue["c_saliency"] = sal_share >= min(1.5 * area_share, 0.75)
        acc_on = float((accent & sub_d).sum()) / max(1, acc_n)
        cue["d_colour"] = acc_n >= acc_min and acc_on >= 0.5
        ncue = int(sum(cue.values()))
        # rival: a connected squint mass of the brightest Otsu class, away from the product (3 % W), at least the
        # subject's size and 2 % of the frame, brighter than the subject by >= 0.25 (squint L), at least as salient per
        # pixel, and winning >= 2 of the 4 cues itself (the rubric's rival made practical: without the brightness and
        # saliency conditions every large lit backdrop counts as a rival)
        w2 = 240
        h2 = max(2, int(round(w2 * h / w)))
        lap2, Sp2 = rs(lap, w2, h2, "box"), rs(Sp, w2, h2, "box")
        acc2 = rs(accent.astype(np.float32), w2, h2, "box")
        sub2 = rs_mask(subA, w2, h2)
        sp_sub = float(Sp2[sub2].mean()) if sub2.any() else 0.0
        support = ndi.binary_dilation(prodQ if prodQ is not None else subQ, iterations=max(1, int(round(0.03 * SQ_W))))
        support |= ndi.binary_dilation(subQ, iterations=1)
        sub_Lq = float(np.median(Sq[subQ]))
        rival_g4 = []
        for area, c_, mk in comps:
            if c_ != 2 or mk.sum() < max(subQ.sum(), 0.02 * mk.size) or (mk & support).any():
                continue
            if float(Sq[mk].mean()) < sub_Lq + 0.25:
                continue
            r_ = ringq(mk)
            ca = r_.any() and abs(float(np.median(Sq[mk])) - float(np.median(Sq[r_]))) >= 0.10
            m2 = rs(mk.astype(np.float32), w2, h2, "nearest") > 0.5
            if not m2.any() or m2.all():
                continue
            cb = float(lap2[m2].mean()) >= 1.5 * float(np.median(lap2[~m2])) + 1e-6
            cc = float(Sp2[m2].sum() / (Sp2.sum() + 1e-9)) >= min(1.5 * float(m2.mean()), 0.75)
            cd = acc_n >= acc_min and float(acc2[m2].sum()) >= 0.5 * float(acc2.sum())
            wins = int(ca) + int(cb) + int(cc) + int(cd)
            dens = float(Sp2[m2].mean())
            if wins >= 2 and dens >= sp_sub:
                ys_, xs_ = np.nonzero(mk)
                box = [xs_.min() * w / SQ_W, ys_.min() * h / hq, (xs_.max() + 1) * w / SQ_W, (ys_.max() + 1) * h / hq]
                rival_g4.append({"share": _r(area), "cues": wins, "bbox_uv": [_r(box[0] / w), _r(box[1] / h),
                                                                             _r(box[2] / w), _r(box[3] / h)]})
                rivals.append((box, "G4 rival"))
        st = "pass" if ncue >= 2 and not rival_g4 else "fail"
        note = []
        if ncue < 2:
            note.append(f"wins {ncue}/4 cues")
        if rival_g4:
            note.append(f"{len(rival_g4)} rival region(s) win >= 2 cues")
        add(Item("G4", "subject wins", "gate", st,
                 {"cues": {k: bool(v) for k, v in cue.items()}, "n_cues": ncue, "squint_dL": _r(dL_sq),
                  "sharp_ratio": _r(lap_sub / (lap_out + 1e-6), 2), "saliency_share": _r(sal_share),
                  "area_share": _r(area_share), "accent_on_subject": _r(acc_on), "accent_px": acc_n,
                  "rivals": rival_g4},
                 ">= 2 of 4 cues (squint dL >= 0.10 vs a 4 % W ring; |Laplacian| >= 1.5x the frame median; saliency "
                 "share >= 1.5x area share; >= 50 % of the accent) and no rival", "; ".join(note)))
    else:
        add(Item("G4", "subject wins", "gate", "n/a", note="no subject"))

    # ===================================================================================================== G5
    g5_notes, g5_ok = [], True
    scope = brief.get("scope")
    pin = cam.get("product_in_frame")
    scope_src = "brief"
    if not scope and pin is not None:
        scope = "whole" if float(pin) >= 0.95 else ("most" if float(pin) >= 0.60 else "part")
        scope_src = "camera"
    if not scope and has_prod:
        n_touch = sum(1 for g in pfacts["gaps"].values() if g <= 0)
        scope = "whole" if n_touch == 0 else ("part" if n_touch >= 3 else "most")
        scope_src = "image"
    whole_req = bool(brief.get("whole")) or scope == "whole"
    pad = float(brief.get("edge_pad", 0.03))

    def edge_check(m, f, name, clear):
        nonlocal g5_ok
        Hm, Wm = m.shape
        for e, g in f["gaps"].items():
            if clear and g < pad:
                g5_ok = False
                g5_notes.append(f"{name} {g:.1%} from the {e} edge (whole needs {pad:.0%})")
                flagged_edges.add(e)
                continue
            if 0 < g < 0.015:
                g5_ok = False
                g5_notes.append(f"near-miss: {name} {g:.1%} from the {e} edge")
                flagged_edges.add(e)
            if g <= 0:
                t_ = {"left": m[:, 0], "right": m[:, -1], "top": m[0, :], "bottom": m[-1, :]}[e]
                ext = f["height_share"] * Hm if e in ("left", "right") else f["width_share"] * Wm
                along = float(t_.sum()) / max(ext, 1.0)
                if 0 < along < 0.03:
                    g5_ok = False
                    g5_notes.append(f"nick: {name} touches the {e} edge along {along:.1%} of its extent")
                    flagged_edges.add(e)

    if has_prod and (whole_req or scope in ("whole", "most")) and sub_src != "product":
        edge_check(prod, pfacts, "product", whole_req)
    same_as_prod = has_prod and sub_src != "product" and sfacts is not None and pfacts is not None and \
        sfacts["bbox_px"] == pfacts["bbox_px"] and abs(sfacts["share"] - pfacts["share"]) < 1e-6
    if has_sub and sfacts["share"] < 0.5 and not (same_as_prod and (whole_req or scope in ("whole", "most"))):
        edge_check(sub, sfacts, "subject", whole_req and sub_src == "product")
    # thin luminance bands hugging an edge
    bands = []
    nb = max(3, int(round(14 * k96)))
    for e in ("top", "bottom", "left", "right"):
        a_ = Yd if e in ("top", "bottom") else Yd.T
        if e in ("bottom", "right"):
            a_ = a_[::-1]
        strip = a_[:nb + 3]
        cs_ = np.cumsum(strip, axis=0)
        best = (0.0, 0)
        for kk in range(1, nb):
            band_m = cs_[kk - 1] / kk
            inner = (cs_[kk + 2] - cs_[kk - 1]) / 3.0
            fr = float((np.abs(band_m - inner) > 0.11).mean())
            if fr > best[0]:
                best = (fr, kk)
        if best[0] >= 0.55:
            bands.append({"edge": e, "depth_px": best[1], "along": round(best[0], 2)})
            g5_ok = False
            g5_notes.append(f"edge band: a luminance step {best[1]} px inside the {e} edge along {best[0]:.0%}")
            flagged_edges.add(e)
    # long contrasty lines running along a frame edge (a contour parked inside the frame edge: a tangent to the frame)
    hugs = []
    if len(seg):
        lim_px = 0.025 * w
        for i in np.nonzero(con >= 0.5)[0]:
            x0, y0, x1, y1 = (float(v) for v in seg[i])
            for e, d0, d1, along, edge_len in (("left", x0, x1, abs(y1 - y0), h), ("right", w - 1 - x0, w - 1 - x1, abs(y1 - y0), h),
                                              ("top", y0, y1, abs(x1 - x0), w), ("bottom", h - 1 - y0, h - 1 - y1, abs(x1 - x0), w)):
                if max(d0, d1) <= lim_px and along >= 0.20 * edge_len:
                    hugs.append({"edge": e, "len_of_edge": _r(along / edge_len), "max_dist_w": _r(max(d0, d1) / w, 4),
                                 "contrast": _r(con[i])})
                    flagged_edges.add(e)
    if hugs:
        g5_ok = False
        g5_notes += [f"a line runs along the {g['edge']} edge ({g['len_of_edge']:.0%} of it, <= {g['max_dist_w']:.1%} W "
                     f"inside)" for g in hugs[:3]]
    # small point-like highlights (a lit LED, a glint) or strong colour pops cut by an edge
    top3 = Ylin >= float(np.quantile(Ylin, 0.97))
    blob_src = (L >= max(0.85, float(np.quantile(L, 0.995)))) | (accent & (C >= 0.10))
    if has_sub:
        blob_src &= ~sub_d
    lab_b, nb_b = ndi.label(blob_src)
    cut_blobs = []
    if nb_b:
        objs = ndi.find_objects(lab_b)
        sizes = ndi.sum(np.ones_like(Ylin), lab_b, range(1, nb_b + 1))
        kiss = 6 * k96
        for i, sl in enumerate(objs):
            frac = float(sizes[i]) / (w * h)
            if frac < 0.0001 or frac >= 0.004:
                continue
            ys0, ys1, xs0, xs1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
            gaps_b = {"left": xs0, "right": w - xs1, "top": ys0, "bottom": h - ys1}
            e = [n for n, g in gaps_b.items() if g <= kiss]
            if e:
                cut_blobs.append({"edges": e, "gap_px960": _r(min(gaps_b[n] for n in e) / k96, 1), "share": _r(frac, 4),
                                  "bbox_uv": [_r(xs0 / w), _r(ys0 / h), _r(xs1 / w), _r(ys1 / h)]})
    # props from the index: slivers and kisses (thresholds at 960 px)
    props, prop_rows = [], []
    if idxA is not None and (has_prod or has_sub):
        supp = (prodA if prodA is not None else np.zeros((h, w), bool)) | (subA if subA is not None else False)
        ids_, counts_ = np.unique(idxA, return_counts=True)
        declared = set(parse_ids(a.prop_ids, index)) if a.prop_ids else None
        grounds = []
        for pid, n_ in zip(ids_, counts_):
            if pid == 0 or n_ < max(8, 30 * k96 * k96):
                continue
            if declared is not None and int(pid) not in declared:
                continue
            mk = idxA == pid
            if (mk & supp).sum() > 0.5 * n_:
                continue
            if declared is None and n_ >= 0.25 * w * h:          # a wall, floor or backdrop is the ground, not a prop
                grounds.append(int(pid))
                continue
            props.append((int(pid), mk))
        if grounds:
            notes.append(f"index ids {grounds} cover >= 25 % of the frame: treated as the ground, not props "
                         f"(--prop-ids to declare props explicitly)")
    prod_mean_Y = float(Ylin[prodA].mean()) if prodA is not None and prodA.any() else None
    top3_n = max(1, int(top3.sum()))
    prod_out = outline(prodA) if prodA is not None else None
    prod_near = ndi.binary_dilation(prod_out, iterations=max(1, int(round(3 * k96)))) if prod_out is not None else None
    for pid, mk in props:
        f = mask_facts(mk)
        row = {"id": pid, "share": _r(f["share"], 4), "issues": []}
        for e, g in f["gaps"].items():
            t_ = {"left": mk[:, 0], "right": mk[:, -1], "top": mk[0, :], "bottom": mk[-1, :]}[e]
            if t_.sum() >= 3 * k96:
                across = f["width_share"] if e in ("left", "right") else f["height_share"]
                if across < 0.04 or f["share"] < 0.004:
                    row["issues"].append(f"cut sliver at {e}")
                    flagged_edges.add(e)
            gap_px = g * (w if e in ("left", "right") else h)
            if 1 * k96 - 0.5 <= gap_px <= 6 * k96 + 0.5 and gap_px > 0:
                row["issues"].append(f"kiss {gap_px / k96:.0f} px@960 from {e}")
                flagged_edges.add(e)
        if prod_near is not None:
            pout = mk & ~ndi.binary_erosion(mk)
            bg_side = pout & ndi.binary_dilation(~mk & ~prodA)
            merge_px = int((bg_side & prod_near).sum())
            if merge_px >= 25 * k96:
                row["issues"].append(f"outline runs within 3 px@960 of the product's over {merge_px / k96:.0f} px")
                row["merge_px960"] = _r(merge_px / k96, 0)
        if prod_mean_Y is not None and f["share"] >= 0.015:
            lm = float(Ylin[mk].mean())
            t3 = float((top3 & mk).sum()) / top3_n
            row["L_vs_product"], row["top3_share"] = _r(lm / max(prod_mean_Y, 1e-6), 2), _r(t3)
            if lm >= 1.3 * prod_mean_Y or t3 >= 0.2:
                row["issues"].append("rival (brightness)")
                ys_, xs_ = np.nonzero(mk)
                rivals.append(([xs_.min(), ys_.min(), xs_.max(), ys_.max()], f"prop {pid}"))
        if coc is not None and has_sub and f["share"] >= 0.01:
            row["coc_median"] = _r(float(np.median(coc[mk])), 2)
        prop_rows.append(row)
    p_cut = [r for r in prop_rows if any(i.startswith(("cut", "kiss")) for i in r["issues"])]
    if p_cut:
        g5_ok = False
        g5_notes.append("props at the edge: " + "; ".join(f"{r['id']} " + ", ".join(i for i in r["issues"]
                                                          if i.startswith(("cut", "kiss"))) for r in p_cut))
    add(Item("G5", "frame edges", "gate", "pass" if g5_ok else "fail",
             {"scope": scope, "scope_source": scope_src, "subject_gaps": {k: _r(v) for k, v in sfacts["gaps"].items()}
              if sfacts else None, "product_gaps": {k: _r(v) for k, v in pfacts["gaps"].items()} if pfacts else None,
              "edge_bands": bands, "edge_hugging_lines": hugs},
             "no near-miss < 1.5 % of the dimension; no nick (< 3 % of its extent on the edge); whole >= 3 % clear; no "
             "edge band (a step within ~1.5 % of an edge along >= 55 %); no contrasty line within 2.5 % W of an edge "
             "along >= 20 % of it; no prop sliver < 0.4 % / < 4 % across, no prop kiss 1-6 px @960",
             "; ".join(g5_notes)))
    add(Item("G5b", "highlights at the edge", "+R", "fail" if cut_blobs else "pass", {"blobs": cut_blobs[:8]},
             "no small point highlight (L >= 0.85) or colour pop (accent with C >= 0.10), 0.01-0.4 % of the frame, cut by "
             "or within 6 px@960 of an edge (a glow cut by the frame pulls the eye out)",
             (f"{len(cut_blobs)} highlight / colour blob(s) at the " + ", ".join(sorted({e for b in cut_blobs for e in b['edges']}))
              + " edge") if cut_blobs else ""))
    for b in cut_blobs:
        flagged_edges.update(b["edges"])
    # product parts parked next to an edge (report: the eye decides)
    if idxA is not None and prodA is not None:
        near_parts = []
        for pid in np.unique(idxA[prodA]):
            if pid == 0 or pid in sub_ids:
                continue
            mk = idxA == pid
            if mk.sum() < max(8, 25 * k96 * k96):
                continue
            f = mask_facts(mk)
            for e, g in f["gaps"].items():
                gp = g * (w if e in ("left", "right") else h) / k96
                if 0 < gp <= 6.5:
                    near_parts.append(f"{int(pid)}@{e} {gp:.0f}px")
        add(Item("G5p", "product parts kissing an edge", "+R", "fail" if near_parts else "pass", {"parts": near_parts},
                 "no product part (index id) parked 1-6 px@960 inside an edge (a kiss to the frame); cut it boldly or "
                 "give it room", ", ".join(near_parts[:8])))

    # ===================================================================================================== G6
    g6_notes = [f"prop {r['id']}: {i}" for r in prop_rows for i in r["issues"] if i.startswith("outline")]
    g6_notes += projected_tangents(plines, W, H) if plines else []
    if props or plines:
        add(Item("G6", "tangents", "gate", "fail" if g6_notes else "pass",
                 {"sources": (["index props"] if props else []) + (["projected lines"] if plines else [])},
                 "no prop outline within 3 px@960 of the product's over >= 25 px; projected product/set edges not "
                 "parallel <= 0.6 % H apart over >= 3 % W, not continuing each other", "; ".join(g6_notes)))
    else:
        add(Item("G6", "tangents", "gate", "n/a", note="needs set props in --index or --lines; the full check runs on "
                                                       "occlusion-aware projected edges Blender-side"))

    # ===================================================================================================== G7
    cands = []
    for kind, name, p in plines:
        d_ = p[-1] - p[0]
        ln = float(np.hypot(*d_)) * w / W
        if ln >= 0.25 * w:
            ang = math.degrees(math.atan2(d_[1], d_[0])) % 180
            cands.append({"src": "projected", "name": name, "len_w": ln / w, "angle": ang,
                          "dev": min(ang % 90, 90 - ang % 90), "seg": (p[0][0] * w / W, p[0][1] * h / H,
                                                                       p[-1][0] * w / W, p[-1][1] * h / H)})
    if not plines and len(seg):
        for i in np.nonzero((seg_len >= 0.25 * w) & (con >= 0.15))[0]:
            cands.append({"src": "image", "name": f"line{i}", "len_w": float(seg_len[i]) / w,
                          "angle": float(seg_ang[i]), "dev": float(seg_dev[i]), "seg": tuple(map(float, seg[i]))})
    cands.sort(key=lambda c_: -c_["len_w"])
    dom = cands[:2]
    dead = [c_ for c_ in dom if 0.5 < c_["dev"] < 10.0]
    roll_img = float("nan")
    if len(seg):
        dx, dy = seg[:, 2] - seg[:, 0], seg[:, 3] - seg[:, 1]
        devv = (np.degrees(np.arctan2(dx, dy)) + 90) % 180 - 90
        sel = (np.abs(devv) < 20) & (con > 0.15) & (seg_len >= 0.05 * w)
        if sel.sum() >= 3:
            xm = ((seg[sel, 0] + seg[sel, 2]) / 2) / w - 0.5
            wv_ = np.sqrt(seg_len[sel] * con[sel])
            X = np.stack([np.ones_like(xm), xm], 1)
            coef, *_ = np.linalg.lstsq(X * wv_[:, None], devv[sel] * wv_, rcond=None)
            keep_ = np.abs(X @ coef - devv[sel]) < 1.5
            if keep_.sum() >= 3:
                coef, *_ = np.linalg.lstsq((X * wv_[:, None])[keep_], (devv[sel] * wv_)[keep_], rcond=None)
            roll_img = float(coef[0])
    roll_cam = cam.get("roll_deg")
    g7_notes = [f"{c_['name']} ({c_['src']}, {c_['len_w']:.0%} W) {c_['dev']:.1f} deg off the axes" for c_ in dead]
    if roll_cam is not None and abs(float(roll_cam)) > 0.2 and not brief.get("dutch"):
        g7_notes.append(f"camera roll {float(roll_cam):+.2f} deg")
    if not HAVE_SK and not plines:
        add(Item("G7", "dominant lines", "gate", "n/a", note="scikit-image missing (no Hough) and no --lines"))
    else:
        add(Item("G7", "dominant lines", "gate", "fail" if g7_notes else "pass",
                 {"dominant": [{"src": c_["src"], "len_w": _r(c_["len_w"]), "angle": _r(c_["angle"], 2),
                                "dev": _r(c_["dev"], 2)} for c_ in dom],
                  "roll_camera_deg": roll_cam, "roll_image_deg": _r(roll_img, 2)},
                 "the 1-2 longest straight contours >= 25 % W within 0.5 deg of the axes or >= 10 deg off; roll 0 +- 0.2 "
                 "deg (camera) unless dutch; the image roll estimate (+-0.55 deg noise) is a report",
                 "; ".join(g7_notes) or ("" if dom else "no straight contour >= 25 % W")))

    # ===================================================================================================== dead zones
    thirds = {"cols": [], "rows": [], "cols_std": [], "rows_std": []}
    dead3 = []
    for i in range(3):
        c_ = Yd[:, i * w // 3:(i + 1) * w // 3]
        r_ = Yd[i * h // 3:(i + 1) * h // 3, :]
        thirds["cols"].append(_r(c_.mean()))
        thirds["cols_std"].append(_r(c_.std()))
        thirds["rows"].append(_r(r_.mean()))
        thirds["rows_std"].append(_r(r_.std()))
        for nm, blk in ((f"col{i + 1}", c_), (f"row{i + 1}", r_)):
            if blk.mean() < 0.12 and blk.std() < 0.01:
                dead3.append(nm)
    low_key = bool(brief.get("low_key"))
    add(Item("DZ", "dead thirds", "report" if low_key else "gate", ("warn" if low_key else "fail") if dead3 else "pass",
             {"thirds_Y": thirds, "dead": dead3}, "no third at mean Y < 0.12 with std < 0.01 (measured dead third: "
             "0.07 / 0.002)", ("dead: " + ", ".join(dead3)) if dead3 else ""))
    m1 = ndi.uniform_filter(Yd, max(3, int(round(7 * k96))))
    m2 = ndi.uniform_filter(Yd * Yd, max(3, int(round(7 * k96))))
    flat_dark = (Yd < 0.10) & (np.sqrt(np.maximum(m2 - m1 * m1, 0)) < 0.01)
    rows_dead = flat_dark.mean(1) >= 0.5
    run, best_run = 0, 0
    for v_ in rows_dead:
        run = run + 1 if v_ else 0
        best_run = max(best_run, run)
    band_h = best_run / h
    st = "pass" if band_h <= 0.20 else ("warn" if band_h <= 0.30 else "fail")
    add(Item("DZb", "dead dark band", "report" if low_key else "+R", st,
             {"band_height": _r(band_h), "flat_dark_share": _r(flat_dark.mean())},
             "a shapeless dark face or band <= 20-30 % of the frame height (light it or aim up; never +EV)",
             f"a flat dark band {band_h:.0%} of the frame height" if st != "pass" else ""))

    # ===================================================================================================== D1
    anc = anchors(W, H)
    null_hit = None
    gu, gv = np.meshgrid((np.arange(64) + 0.5) / 64, (np.arange(36) + 0.5) / 36)
    dmin = np.full(gu.shape, np.inf)
    for pts in anc.values():
        for (x_, y_) in pts:
            dmin = np.minimum(dmin, np.hypot(gu - x_, (gv - y_) / A))
    null_hit = float((dmin <= 0.03).mean())
    if has_sub:
        su, sv = sfacts["centroid_uv"]
        per = {}
        for sys_, pts in anc.items():
            dd = [dist_w(su, sv, x_, y_, A) for x_, y_ in pts]
            j = int(np.argmin(dd))
            per[sys_] = {"dist_w": _r(dd[j]), "point": [_r(pts[j][0]), _r(pts[j][1])]}
        nearest = min(per, key=lambda k_: per[k_]["dist_w"])
        policy = str(brief.get("anchor", "anchor")).lower()
        if brief.get("anchor_uv"):
            ref_pt = tuple(brief["anchor_uv"])
            ref_name = "declared point"
            ref_d = dist_w(su, sv, ref_pt[0], ref_pt[1], A)
        elif policy.startswith("cent"):
            ref_name, ref_pt, ref_d = "centre", (0.5, 0.5), dist_w(su, sv, 0.5, 0.5, A)
        elif brief.get("anchor_system") in per:
            ref_name = brief["anchor_system"]
            ref_pt, ref_d = tuple(per[ref_name]["point"]), per[ref_name]["dist_w"]
        else:
            ref_name, ref_pt, ref_d = nearest, tuple(per[nearest]["point"]), per[nearest]["dist_w"]
        d_all = per[nearest]["dist_w"]
        on_line = [n for n, v_ in (("thirds-v", min(abs(su - 1 / 3), abs(su - 2 / 3))),
                                   ("phi-v", min(abs(su - 0.382), abs(su - 0.618))), ("centre-v", abs(su - 0.5)))
                   if v_ <= 0.03]
        declared = bool(brief.get("anchor_uv")) or policy.startswith("cent") or brief.get("anchor_system") in per
        if ref_d <= 0.03:
            st, note = "pass", f"on {ref_name} ({ref_d:.1%} W)"
        elif ref_d <= 0.06:
            st, note = "warn", f"near {ref_name} ({ref_d:.1%} W): place it on the anchor (lens shift)"
        elif declared:
            st, note = "fail", f"{ref_d:.1%} W from the declared {ref_name}"
        elif d_all <= 0.15:
            st, note = "fail", f"drifting: {d_all:.1%} W from every anchor (the 'almost' of placement)"
        else:
            st, note = "warn", f"{d_all:.1%} W from the nearest anchor (free placement)"
        add(Item("D1", "placement", "+R", st,
                 {"centroid_uv": [_r(su), _r(sv)], "systems": per, "nearest": nearest, "reference": ref_name,
                  "reference_uv": [_r(ref_pt[0]), _r(ref_pt[1])], "dist_to_reference_w": _r(ref_d),
                  "on_vertical_line": on_line, "null_hit_rate": _r(null_hit)},
                 "<= 3 % W from the declared anchor (or centre); 6-15 % W from every anchor = drifting (needs a reason or "
                 "a fix by lens shift); the grids cover ~half the frame, so a hit proves little", note))
        facing = brief.get("facing")
        if facing in ("left", "right"):
            free = (1 - su) if facing == "right" else su
            st = "pass" if 0.55 <= free <= 0.65 else ("fail" if free < 0.5 else "warn")
            add(Item("D1b", "lead room", "+R", st, {"facing": facing, "free_w": _r(free)},
                     "55-65 % of the width free on the side the subject faces",
                     "" if st == "pass" else f"{free:.0%} free on the {facing}"))
    else:
        add(Item("D1", "placement", "+R", "n/a", note="no subject"))

    # ===================================================================================================== D2
    d2_vals = {}
    lead_idx, out_idx = [], []
    if has_sub and len(seg):
        su, sv = sfacts["centroid_uv"]
        ys_, xs_ = np.nonzero(outline(subA) if subA.sum() > 50 else subA)
        pts = np.stack([xs_, ys_], 1).astype(np.float32)
        if len(pts) > 400:
            pts = pts[np.random.default_rng(0).choice(len(pts), 400, replace=False)]
        dist = line_dist_to_points(seg, pts)
        at_sub = np.zeros(len(seg), bool)
        sub_near = ndi.binary_dilation(subA, iterations=max(1, int(round(0.015 * w))))
        tt = np.linspace(0, 1, 16)[None, :]
        xs_s = np.clip(seg[:, :1] + (seg[:, 2:3] - seg[:, :1]) * tt, 0, w - 1).round().astype(int)
        ys_s = np.clip(seg[:, 1:2] + (seg[:, 3:4] - seg[:, 1:2]) * tt, 0, h - 1).round().astype(int)
        at_sub = sub_near[ys_s, xs_s].mean(1) >= 0.5
        long_ = seg_len >= 0.15 * w
        wgt = (seg_len / math.hypot(w, h)) * (0.25 + 0.75 * con)
        passes = long_ & ~at_sub & (dist <= 0.05 * w) & (con >= 0.2)
        edge_m = 0.03 * w
        from_edge = (np.minimum.reduce([seg[:, 0], seg[:, 2]]) <= edge_m) | \
                    (np.maximum.reduce([seg[:, 0], seg[:, 2]]) >= w - 1 - edge_m) | \
                    (np.minimum.reduce([seg[:, 1], seg[:, 3]]) <= edge_m) | \
                    (np.maximum.reduce([seg[:, 1], seg[:, 3]]) >= h - 1 - edge_m)
        lead_idx = list(np.nonzero(passes)[0])
        strong = [i for i in np.argsort(-wgt) if long_[i] and not at_sub[i]][:3]
        rival_pts = []
        for box, _ in rivals:
            rival_pts.append(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2))
        lead_to = []
        for i in strong:
            if passes[i] or dist[i] <= 0.05 * w:
                lead_to.append("subject")
            elif rival_pts and line_dist_to_points(seg[i:i + 1], np.array(rival_pts, np.float32))[0] <= 0.05 * w:
                lead_to.append("rival")
            else:
                lead_to.append("elsewhere")
                out_idx.append(i)
        # convergence (comp_score's lead map): weight of lines aimed at each point vs at the subject
        mx_, my_ = (seg[:, 0] + seg[:, 2]) / 2, (seg[:, 1] + seg[:, 3]) / 2
        dvec = np.stack([seg[:, 2] - seg[:, 0], seg[:, 3] - seg[:, 1]], 1)
        dvec /= np.maximum(np.linalg.norm(dvec, axis=1, keepdims=True), 1e-9)

        def conv(px, py):
            vx, vy = np.asarray(px)[..., None] - mx_, np.asarray(py)[..., None] - my_
            vn = np.hypot(vx, vy) + 1e-9
            al = np.degrees(np.arcsin(np.clip(np.abs(vx * dvec[:, 1] - vy * dvec[:, 0]) / vn, 0, 1)))
            return (wgt * np.clip(1 - al / 12.0, 0, 1) * (vn >= 0.03 * w)).sum(-1)
        Ms = float(conv(su * w, sv * h))
        Mg = conv(gu * w, gv * h)
        pk_ = np.unravel_index(int(np.argmax(Mg)), Mg.shape)
        bq = rs(ndi.gaussian_filter(Yd, 0.01 * w), SQ_W, hq)
        btop = bq >= np.quantile(bq, 0.97)
        lb, nb_ = ndi.label(btop)
        if nb_:
            big = int(np.argmax(ndi.sum(btop, lb, range(1, nb_ + 1)))) + 1
            by_, bx_ = ndi.center_of_mass(lb == big)
            entry = [float(bx_ + 0.5) / SQ_W, float(by_ + 0.5) / hq]
        else:
            entry = [0.5, 0.5]
        entry_on_sub = bool(subQ[min(hq - 1, int(entry[1] * hq)), min(SQ_W - 1, int(entry[0] * SQ_W))])
        n_lead = len(lead_idx)
        n_edge = int((passes & from_edge).sum())
        ok = n_lead >= 2 and n_edge >= 1 and (not lead_to or lead_to[0] != "rival")
        d2_vals = {"n_lines_to_subject": n_lead, "entering_from_edge": n_edge, "strongest_lead_to": lead_to,
                   "convergence_peak_uv": [_r(gu[pk_]), _r(gv[pk_])], "subject_convergence_ratio": _r(Ms / (Mg.max() + 1e-9)),
                   "entry_brightest_uv": [_r(entry[0]), _r(entry[1])], "entry_on_subject": entry_on_sub,
                   "n_lines_ge_15pct": int(long_.sum())}
        nt = []
        if n_lead < 2:
            nt.append(f"{n_lead} line(s) lead to the subject")
        if lead_to and lead_to[0] != "subject":
            nt.append("the strongest line leads " + ("to a rival" if lead_to[0] == "rival" else "elsewhere"))
        add(Item("D2", "eye path", "report", "pass" if ok else "warn", d2_vals,
                 ">= 2 lines >= 15 % W pass within 5 % W of the subject, one entering from an edge; nothing strong "
                 "leads out or to a rival (lines on luminance + depth edges, weighted by luminance contrast)",
                 "; ".join(nt)))
    else:
        add(Item("D2", "eye path", "report", "n/a", note="no subject" if not has_sub else "no lines (scikit-image?)"))

    # ===================================================================================================== D3
    divs = []
    for kind, name, p in plines:
        d_ = p[-1] - p[0]
        ln = float(np.hypot(*d_)) / W
        ang = math.degrees(math.atan2(d_[1], d_[0])) % 180
        dv = min(ang % 90, 90 - ang % 90)
        if ln >= 0.30 and dv < 3:
            hor = abs(math.sin(math.radians(ang))) < 0.5
            divs.append(("h" if hor else "v", float(p[:, 1].mean() / H if hor else p[:, 0].mean() / W), name))
    if not plines:
        for i in np.nonzero((seg_len >= 0.30 * w) & (seg_dev < 3) & (con >= 0.15))[0]:
            hor = abs(math.sin(math.radians(seg_ang[i]))) < 0.5
            pos = float((seg[i, 1] + seg[i, 3]) / 2 / h if hor else (seg[i, 0] + seg[i, 2]) / 2 / w)
            divs.append(("h" if hor else "v", pos, f"line{i}"))
    sym = bool(brief.get("symmetric")) or brief.get("mode") == "symmetric"
    halves = [d_ for d_ in divs if abs(d_[1] - 0.5) < 0.03]
    eq = []
    for kind in ("h", "v"):
        ps = sorted({0.0, 1.0} | {round(d_[1], 3) for d_ in divs if d_[0] == kind})
        ps2 = [ps[0]]
        for p_ in ps[1:]:
            if p_ - ps2[-1] >= 0.02:
                ps2.append(p_)
        iv = np.diff(ps2)
        for i in range(len(iv) - 1):
            if abs(iv[i] - iv[i + 1]) < 0.1 * max(iv[i], iv[i + 1]) and len(ps2) > 2:
                eq.append(f"{kind} intervals {iv[i]:.2f} / {iv[i + 1]:.2f}")
    bad_half = halves and not sym
    bad_eq = eq and not brief.get("rhythm_row")
    st = "fail" if bad_half else ("fail" if bad_eq else "pass")
    if not HAVE_SK and not plines:
        st = "n/a"
    add(Item("D3", "divisions", "+R", st,
             {"dominant": [{"axis": d_[0], "pos": _r(d_[1]), "name": d_[2]} for d_ in divs[:8]],
              "halving": [{"axis": d_[0], "pos": _r(d_[1])} for d_ in halves], "equal_intervals": eq},
             "no dominant horizontal / vertical (>= 30 % W, within 3 deg of the axes) within +-3 % of the 50 % line "
             "unless symmetric; adjacent intervals differ by > 10 % unless a rhythm row",
             "; ".join((["halves the frame"] if bad_half else []) + (eq if bad_eq else []))))

    # ===================================================================================================== D4
    mode = brief.get("mode") or "calm"
    qf = float(quiet.mean())
    ql, qn = ndi.label(quiet)
    coh = sol = erect = 0.0
    if qn:
        areas = ndi.sum(np.ones_like(L), ql, range(1, qn + 1))
        big = int(np.argmax(areas)) + 1
        coh = float(areas.max() / areas.sum())
        comp = ql == big
        sl = ndi.find_objects((comp).astype(np.int8))[0]
        sol = float(comp.sum()) / float((sl[0].stop - sl[0].start) * (sl[1].stop - sl[1].start))
        gh = max(4, int(round(64 * h / w)))
        erect = largest_rect(rs(comp.astype(np.float32), 64, gh, "box") > 0.5)
    lo, hi = NEG_BAND.get(mode, NEG_BAND["calm"])
    ok = lo <= qf <= hi and coh >= 0.6 and sol >= 0.8 and erect >= 0.12
    nt = []
    if not lo <= qf <= hi:
        nt.append(f"quiet {qf:.0%} outside {mode} {lo:.0%}-{hi:.0%}")
    if coh < 0.6:
        nt.append(f"quiet space split (coherence {coh:.2f})")
    if sol < 0.8:
        nt.append(f"ragged (solidity {sol:.2f})")
    if erect < 0.12:
        nt.append(f"no room for a line of type (largest rect {erect:.0%})")
    add(Item("D4", "negative space", "report", "pass" if ok else "warn",
             {"mode": mode + ("" if brief.get("mode") else " (default)"), "quiet_share": _r(qf), "band": [lo, hi],
              "coherence": _r(coh), "solidity": _r(sol), "empty_rect": _r(erect)},
             "quiet share in the mode band; one region >= 60 % of the quiet, solidity >= 0.8; empty rectangle >= 12 %",
             "; ".join(nt)))

    # ===================================================================================================== D5
    tgtQ = prodQ if (prodQ is not None and scope in ("whole", "most")) else subQ
    agree = 0.0
    if tgtQ is not None and tgtQ.any():
        agree = max(float((tgtQ & (cls == c_)).sum()) / max(1, float((tgtQ | (cls == c_)).sum())) for c_ in range(3))
    n_m = len(masses)
    m1_ = masses[0][0] if masses else 0.0
    m2_ = masses[1][0] if len(masses) > 1 else 1e-6
    ok = 2 <= n_m <= 7 and m1_ / max(m2_, 1e-6) >= 1.5 and agree >= 0.3
    add(Item("D5", "masses", "report", "pass" if ok else "warn",
             {"n_masses_ge_2pct": n_m, "largest_vs_next": _r(m1_ / max(m2_, 1e-6), 2), "iou_with_target": _r(agree),
              "target": "product" if tgtQ is prodQ else "subject", "eta2": _r(eta2),
              "crumbs": _r(sum(c_[0] for c_ in comps if c_[0] < 0.02))},
             "squint 96 px, 3-level Otsu: 2-7 masses >= 2 %; largest >= 1.5x the next; IoU with the product (whole / "
             "most) or the subject >= 0.3 (0.7 good)",
             "; ".join(x for x in (f"{n_m} masses" if not 2 <= n_m <= 7 else "",
                                   f"largest only {m1_ / max(m2_, 1e-6):.2f}x the next" if m1_ / max(m2_, 1e-6) < 1.5 else "",
                                   f"target matches no value mass (IoU {agree:.2f})" if agree < 0.3 else "") if x)))

    # ===================================================================================================== D6
    wmap = Sal * (1.0 / (1.0 + coc / 8.0) if coc is not None else 1.0) * (1 + 2 * accent)
    wsum = float(wmap.sum()) + 1e-12
    cu, cv = float((wmap * (xx + 0.5)).sum() / wsum) / w, float((wmap * (yy + 0.5)).sum() / wsum) / h
    dcm = math.hypot(cu - 0.5, cv - 0.5) / math.hypot(0.5, 0.5)
    Es = rs(np.hypot(ndi.sobel(L, 0), ndi.sobel(L, 1)), 96, max(2, int(round(96 * h / w))))
    symv = float(1 - np.abs(Es - Es[:, ::-1]).sum() / max((Es + Es[:, ::-1]).sum(), 1e-9))
    lim = 0.06 if mode == "calm" else 0.20
    almost = 0.60 <= symv < 0.80 and has_sub and abs(sfacts["centroid_uv"][0] - 0.5) < 0.05
    ok = (dcm <= lim or mode == "symmetric") and not almost and (symv >= 0.85 if mode == "symmetric" else True)
    add(Item("D6", "balance", "report", "pass" if ok else "warn",
             {"weight_centroid_uv": [_r(cu), _r(cv)], "dcm": _r(dcm), "dcm_limit": lim, "symmetry": _r(symv)},
             "DCM (weight centroid from the centre / half-diagonal) <= 0.06 calm, <= 0.20 otherwise; symmetric >= 0.85 "
             "or clearly asymmetric (an almost-symmetric 0.60-0.80 with a centred subject reads as an error)",
             "; ".join(x for x in (f"DCM {dcm:.2f} > {lim}" if dcm > lim and mode != "symmetric" else "",
                                   "almost symmetric" if almost else "") if x)))

    # ===================================================================================================== D7
    size_of = brief.get("size_of", "product")
    fct = pfacts if (size_of == "product" and pfacts) else sfacts
    band_ = None
    if brief.get("size_band"):
        band_ = (brief.get("size_measure", "width"), float(brief["size_band"][0]), float(brief["size_band"][1]))
    elif brief.get("role") in ROLE_SIZE:
        band_ = ROLE_SIZE[brief["role"]]
    vals = {}
    if fct:
        vals = {"of": size_of if fct is pfacts else "subject", "width_share": _r(fct["width_share"]),
                "height_share": _r(fct["height_share"]), "area_share": _r(fct["share"], 4)}
    figm = prodA if (prodA is not None and scope in ("whole", "most")) else subA
    if figm is not None and figm.any():
        bd_ = outline(figm)
        border = np.zeros_like(bd_)
        border[0, :] = border[-1, :] = border[:, 0] = border[:, -1] = True
        vals["silhouette_off_border"] = _r(1.0 - float((bd_ & border).sum()) / max(1, int(bd_.sum())))
        figq = rs_mask(figm, SQ_W, hq)
        if figq.any() and (~figq).any():
            k3 = np.ones((3, 3), np.float32)
            a_in = ndi.convolve(np.where(figq, Sq, 0), k3) / np.maximum(ndi.convolve(figq.astype(np.float32), k3), 1e-6)
            a_ou = ndi.convolve(np.where(~figq, Sq, 0), k3) / np.maximum(ndi.convolve((~figq).astype(np.float32), k3), 1e-6)
            bq_ = outline(figq)
            vals["silhouette_contrast"] = _r(float(np.median(np.abs(a_in[bq_] - a_ou[bq_]))) if bq_.any() else 0.0)
    if band_ and fct:
        meas, lo, hi = band_
        v_ = {"width": fct["width_share"], "height": fct["height_share"], "area": fct["share"]}[meas]
        st = "pass" if lo <= v_ <= hi else "fail"
        vals.update({"measure": meas, "band": [lo, hi], "value": _r(v_)})
        note = "" if st == "pass" else f"{vals['of']} {meas} {v_:.0%} outside {lo:.0%}-{hi:.0%} ({brief.get('role', 'brief')})"
    else:
        st, note = "n/a", "no size band (brief role or size_band)"
    if scope in ("whole", "most") and vals.get("silhouette_off_border") is not None and vals["silhouette_off_border"] < 0.3:
        st = "fail" if st != "n/a" else "warn"
        note = (note + "; " if note else "") + "the product reads as wallpaper (silhouette mostly on the border)"
    add(Item("D7", "size + figure-ground", "+R", st, vals,
             "in the brief's band for the role (defaults: wide 8-12 % W, medium 12-25 % W, hero 20-32 % W, packshot "
             "55-78 % H, field 3-15 % area); silhouette off the border >= 0.3 (0.7 good) for whole / most; silhouette "
             "contrast 0.04-0.18", note))

    # ===================================================================================================== D8
    thumb = rs(L, SQ_W, hq, "box")
    d8 = {}
    if has_sub:
        rq = ringq(subQ)
        d8["subject_dL_96"] = _r(abs(float(np.median(thumb[subQ])) - float(np.median(thumb[rq]))) if rq.any() else 0.0)
    if vals.get("silhouette_contrast") is not None:
        d8["silhouette_contrast_96"] = vals["silhouette_contrast"]
    # crop stability (proxy): placement + balance + edges on crops moving the edges inward 0-8 % at the frame's aspect
    crop = None
    if has_sub:
        w3 = 192
        h3 = max(2, int(round(w3 * h / w)))
        wm3 = rs(wmap, w3, h3, "box")
        y3, x3 = np.mgrid[0:h3, 0:w3].astype(np.float64)
        I0, Ix, Iy = (np.pad(np.cumsum(np.cumsum(q_, 0), 1), ((1, 0), (1, 0))) for q_ in (wm3, wm3 * (x3 + 0.5), wm3 * (y3 + 0.5)))
        su, sv = sfacts["centroid_uv"]
        sb = sfacts["bbox_px"]
        sbb = (sb[0] / W, sb[1] / H, (sb[2] + 1) / W, (sb[3] + 1) / H)
        pbb = None
        if pfacts and scope in ("whole", "most"):
            pb = pfacts["bbox_px"]
            pbb = (pb[0] / W, pb[1] / H, (pb[2] + 1) / W, (pb[3] + 1) / H)
        policy_c = str(brief.get("anchor", "anchor")).lower().startswith("cent")

        def crop_score(x0, y0, s):
            uc, vc = (su - x0) / s, (sv - y0) / s
            if policy_c:
                dp = dist_w(uc, vc, 0.5, 0.5, A)
            else:
                dp = min(dist_w(uc, vc, x_, y_, A) for pts in anc.values() for x_, y_ in pts)
            plc = math.exp(-dp * dp / (2 * 0.03 ** 2))
            X0, Y0 = int(round(x0 * w3)), int(round(y0 * h3))
            X1, Y1 = int(round((x0 + s) * w3)), int(round((y0 + s) * h3))
            tot = I0[Y1, X1] - I0[Y0, X1] - I0[Y1, X0] + I0[Y0, X0]
            if tot <= 0:
                return 0.0
            mxc = (Ix[Y1, X1] - Ix[Y0, X1] - Ix[Y1, X0] + Ix[Y0, X0]) / tot / w3
            myc = (Iy[Y1, X1] - Iy[Y0, X1] - Iy[Y1, X0] + Iy[Y0, X0]) / tot / h3
            dc = math.hypot((mxc - x0) / s - 0.5, (myc - y0) / s - 0.5) / math.hypot(0.5, 0.5)
            bal = ramp(dc, 0.20, 0.06)
            edge = 1.0
            for bb, need in ((sbb, 0.0), (pbb, pad if whole_req else 0.0)):
                if bb is None:
                    continue
                gl, gt = (bb[0] - x0) / s, (bb[1] - y0) / s
                gr, gb = 1 - (bb[2] - x0) / s, 1 - (bb[3] - y0) / s
                for g, g0 in ((gl, bb[0]), (gt, bb[1]), (gr, 1 - bb[2]), (gb, 1 - bb[3])):
                    if g0 > 0 and g <= 0:
                        edge -= 0.5                     # the crop cuts what the frame kept whole
                    elif 0 < g < 0.015 or (need and g < need):
                        edge -= 0.25
            return 18 * plc + 8 * bal + 6 * max(0.0, edge)        # the rubric weights of these three (of 100)
        base = crop_score(0.0, 0.0, 1.0)
        best_c = (base, 0.0, 0.0, 1.0)
        for s in (0.96, 0.92):
            for x0 in np.arange(0, 1 - s + 1e-9, 0.02):
                for y0 in np.arange(0, 1 - s + 1e-9, 0.02):
                    sc = crop_score(float(x0), float(y0), s)
                    if sc > best_c[0]:
                        best_c = (sc, float(x0), float(y0), s)
        crop = {"score": _r(base, 1), "best_score": _r(best_c[0], 1),
                "best_crop": {"left": _r(best_c[1]), "top": _r(best_c[2]), "right": _r(1 - best_c[1] - best_c[3]),
                              "bottom": _r(1 - best_c[2] - best_c[3])}}
        d8["crop"] = crop
    nt = []
    if d8.get("subject_dL_96") is not None and d8["subject_dL_96"] < 0.04:
        nt.append(f"subject lost at thumbnail size (dL {d8['subject_dL_96']:.2f})")
    if crop and crop["best_score"] - crop["score"] > 5:
        bc = crop["best_crop"]
        nt.append("a crop within 8 % scores +{:.0f} (edges in: L {:.0%} T {:.0%} R {:.0%} B {:.0%}): move the camera "
                  "there".format(crop["best_score"] - crop["score"], bc["left"], bc["top"], bc["right"], bc["bottom"]))
    add(Item("D8", "thumbnail + crop", "report", "warn" if nt else ("pass" if d8 else "n/a"), d8,
             "96 px: subject dL >= 0.04 (0.10 good), silhouette contrast >= 0.03 (0.12 good); no crop within 8 % gains "
             "> 5 points of the 100-point rank score (proxy: placement 18, balance 8, edges 6)", "; ".join(nt)))

    # ===================================================================================================== E1
    if has_sub:
        # calibration: on an audited film most accepted part subjects separated by focus, not tone (ring dL < 0.10),
        # so tone alone is a report; the gate fails when neither tone nor focus separates the subject
        if cue.get("a_contrast"):
            st, cls_, nt = "pass", "gate", ""
        elif cue.get("b_sharp"):
            st, cls_, nt = "warn", "report", f"separates by focus, not tone (dL {dL_sq:.2f})"
        else:
            st, cls_, nt = "fail", "gate", (f"subject merges with its surround: dL {dL_sq:.2f} and not sharper than the "
                                            f"frame; fix with light or camera, never exposure")
        add(Item("E1a", "tone: subject vs its ring", cls_, st, {"squint_dL": _r(dL_sq), "sharper": bool(cue.get("b_sharp"))},
                 "squint dL >= 0.10 vs a 4 % W ring (G4 cue a); else it must at least be the sharpest thing (cue b)", nt))
    figE = prodA if prodA is not None else subA
    if figE is not None and figE.any() and (~figE).any():
        setE = ~figE
        fo = outline(figE) & ndi.binary_dilation(setE)          # the outline where it meets the set
        sg = max(1.0, 2 * k96)
        dLo = np.abs(band_mean(L, figE, sg) - band_mean(L, setE, sg))
        sel_o = fo.copy()
        sel_o[0, :] = sel_o[-1, :] = sel_o[:, 0] = sel_o[:, -1] = False
        if depA is not None:                                     # contact edges (the set not behind) are excluded
            zin = band_mean(depA, figE, sg)
            zout = band_mean(depA, setE, sg)
            sel_o &= (zout - zin) >= np.maximum(0.05, 0.10 * zin)
        n_o = int(sel_o.sum())
        sep = float((dLo[sel_o] >= 0.08).mean()) if n_o >= 0.10 * w else None
        sep_body, basis = None, "outline"
        if sep is not None and glassA is not None:               # a transparent cover takes the value behind it
            sb = sel_o & ~glassA
            if sb.sum() >= 0.05 * w:
                sep_body, basis = float((dLo[sb] >= 0.08).mean()), "opaque body outline"
        sep_used = sep_body if sep_body is not None else sep
        main = scope == "whole" or (prodA is not None and prodA.mean() >= 0.50)
        if sep_used is None:
            st, cls_ = "n/a", "report"
        else:
            cls_ = "gate" if main else "report"
            st = "fail" if sep_used < 0.20 else ("warn" if sep_used < 0.40 else "pass")
        add(Item("E1b", "tone: outline separation", cls_, st,
                 {"sep_frac": _r(sep), "sep_frac_body": _r(sep_body), "basis": basis, "outline_px": n_o,
                  "behind_by_depth": depA is not None},
                 ">= 0.20 of the product outline where the set lies behind separates by dL >= 0.08 (warn < 0.40; the "
                 "opaque body when --glass-ids); a gate when the product is the main shape (whole, or >= 50 % of the "
                 "frame); scripts/reads_metric.py is the calibrated reads gate",
                 "" if st in ("pass", "n/a") else f"outline merges with what is behind ({sep_used:.0%} separates)"))
    if has_sub:
        part_subject = sub_src != "product" and prodA is not None and (prodA & ~subA).any()
        bg_desc = "non-product pixels"
        if depA is not None:
            zs = float(np.median(depA[subA]))
            bgm = (np.log2(np.clip(depA, 1e-3, 1e5) / max(zs, 1e-3)) > 0.5)
            bg_desc = "depth layer > +0.5 log2 behind the subject"
            if prodA is not None and not part_subject:
                bgm &= ~prodA                      # whole-product subject: the background is the set behind it
            if (bgm & ~subA).mean() < 0.05 and not part_subject:   # a close backdrop behind a whole product
                bgm = (depA > zs) & ~subA & (~prodA if prodA is not None else True)
                bg_desc = "the set behind the product (no layer beyond +0.5 log2)"
        else:
            bgm = ~(prodA if prodA is not None else subA)
            if bgm.mean() < 0.05:
                bgm = ~subA                        # macro: the product is the ground
        bgm &= ~subA
        if bgm.mean() >= 0.05:
            ys_sub = float(np.median(Ylin[subA]))
            ys_bg = float(np.median(Ylin[bgm]))
            ev = abs(math.log2(max(ys_sub, 1e-5) / max(ys_bg, 1e-5)))

            def mhue(m):
                ww_ = C[m]
                return float(math.degrees(math.atan2((np.sin(np.radians(hue[m])) * ww_).sum(),
                                                     (np.cos(np.radians(hue[m])) * ww_).sum())) % 360), float(np.median(C[m]))
            hs_, cs_s = mhue(subA)
            hb_, cs_b = mhue(bgm)
            hd = float(circ_dist(hs_, hb_))
            distinct = hd >= 60 and cs_s >= 0.03 and cs_b >= 0.03
            st = "pass" if ev >= 1.0 or distinct else "fail"
            add(Item("E1c", "tone: background", "gate", st,
                     {"ev_subject_vs_bg": _r(ev, 2), "hue_diff": _r(hd, 1), "chroma": [_r(cs_s), _r(cs_b)],
                      "bg": bg_desc,
                      "bg_share": _r(bgm.mean())},
                     "the background sits >= 1 EV from the subject or is a distinct hue (>= 60 deg, both C >= 0.03)",
                     "" if st == "pass" else f"background only {ev:.2f} EV from the subject and no hue contrast"))
        else:
            add(Item("E1c", "tone: background", "gate", "n/a", {"bg_share": _r(bgm.mean())},
                     note="background < 5 % of the frame"))
    if prodA is not None and prodA.any():
        ring_p = ndi.binary_dilation(prodA, iterations=max(2, int(round(0.04 * w)))) & ~prodA
        if ring_p.any():
            yp, yr = float(np.median(Ylin[prodA])), float(np.median(Ylin[ring_p]))
            stops = math.log2(max(yr, 1e-5) / max(yp, 1e-5))
            dark = float(np.median(L[prodA])) < 0.35
            fo = outline(prodA)
            Lin_ = band_mean(L, prodA, max(1.0, 2 * k96))
            Lout_ = band_mean(L, ~prodA, max(1.0, 2 * k96))
            rim = float(((Lin_ - Lout_)[fo] >= 0.08).mean()) if fo.any() else 0.0
            ok = (not dark) or stops >= 1.5 or rim >= 0.25
            add(Item("E1d", "tone: a dark product's ground", "+R", "pass" if ok else "fail",
                     {"product_dark": dark, "ground_stops_lighter": _r(stops, 2), "rim_share": _r(rim)},
                     "a dark product stands on / against a ground >= ~1.5 stops lighter, or carries a rim / reflection "
                     "line along >= 25 % of its silhouette", "" if ok else f"dark product, ground only {stops:.1f} stops "
                                                                          f"lighter, rim {rim:.0%}"))

    # ===================================================================================================== E2
    pr = [r for r in prop_rows if "rival (brightness)" in r["issues"]]
    if props:
        add(Item("E2a", "prop rivals", "gate", "fail" if pr else "pass",
                 {"rivals": [{k_: r[k_] for k_ in ("id", "share", "L_vs_product", "top3_share")} for r in pr],
                  "props": prop_rows},
                 "no set prop >= 1.5 % of the frame brighter than the product's mean x 1.3 or holding >= 20 % of the "
                 "brightest 3 %", "; ".join(f"prop {r['id']} x{r['L_vs_product']} / top3 {r['top3_share']}" for r in pr)))
    else:
        add(Item("E2a", "prop rivals", "gate", "n/a", note="no set props in the index"))
    reg_r = []
    if prod_mean_Y is not None and has_sub:
        sp_sub_d = float(Sp[subA].mean())
        lap_sub_m = float(lap[subA].mean())
        for area, c_, mk in comps:
            if area < 0.015 or area >= 0.25:                     # >= 25 % of the frame is the ground, not a rival
                continue
            m_ = rs(mk.astype(np.float32), w, h, "nearest") > 0.5
            if (m_ & (prodA | sub_d)).sum() > 0.3 * m_.sum():
                continue
            lm = float(Ylin[m_].mean())
            t3 = float((top3 & m_).sum()) / top3_n
            if (lm >= 1.3 * prod_mean_Y or t3 >= 0.2) and (float(Sp[m_].mean()) >= sp_sub_d or
                                                           float(lap[m_].mean()) >= lap_sub_m):
                ys_, xs_ = np.nonzero(m_)
                reg_r.append({"share": _r(area), "L_vs_product": _r(lm / max(prod_mean_Y, 1e-6), 2), "top3": _r(t3),
                              "bbox_uv": [_r(xs_.min() / w), _r(ys_.min() / h), _r(xs_.max() / w), _r(ys_.max() / h)]})
                rivals.append(([xs_.min(), ys_.min(), xs_.max(), ys_.max()], "region"))
        add(Item("E2b", "image-region rivals", "+R", "fail" if reg_r else "pass", {"regions": reg_r},
                 "no non-product region of 1.5-25 % of the frame brighter than the product mean x 1.3 or holding >= 20 % "
                 "of the brightest 3 %, AND as salient or as sharp as the subject (fix with camera, then light; never hide a "
                 "visible prop)", f"{len(reg_r)} bright region(s) compete" if reg_r else ""))
    add(Item("E2c", "clutter: masses", "+R", "pass" if n_m <= 7 else "fail", {"n_masses_ge_2pct": n_m},
             "<= 7 squint masses >= 2 %", "" if n_m <= 7 else f"{n_m} masses: the frame reads busy"))
    sharper = []
    if coc is not None and has_sub:
        cs_med = float(np.median(coc[subA]))
        for r in prop_rows:
            if r.get("coc_median") is not None and cs_med > 1.0 and r["coc_median"] < 0.5 * cs_med:
                sharper.append(r["id"])
        nonp = ~(prodA if prodA is not None else subA)
        sharp_out = float((coc[nonp] <= min(cs_med, 2.0)).mean()) if nonp.any() else 0.0
        add(Item("E2d", "set sharper than the subject", "+R", "fail" if sharper else "pass",
                 {"props_sharper": sharper, "subject_coc": _r(cs_med, 2), "set_share_as_sharp": _r(sharp_out)},
                 "no set object sharper than the subject",
                 f"props {sharper} sharper than the subject" if sharper else ""))

    # ===================================================================================================== E3
    nonacc = ~accent
    fc90 = float(np.percentile(C[nonacc], 90)) if nonacc.any() else 0.0
    cw = C >= 0.04
    hist2, _ = np.histogram(hue[cw], bins=36, range=(0, 360), weights=C[cw])
    hs2 = hist2 + 0.5 * (np.roll(hist2, 1) + np.roll(hist2, -1))
    peaks = []
    if hs2.sum() > 0:
        for i in range(36):
            if hs2[i] >= 0.15 * hs2.max() and hs2[i] >= hs2[i - 1] and hs2[i] >= hs2[(i + 1) % 36]:
                ang = (i + 0.5) * 10
                if all(circ_dist(ang, p_) >= 40 for p_ in peaks):
                    peaks.append(ang)
    acc_share = acc_n / float(w * h)
    amax = float(brief.get("accent_max", 0.04))
    e3 = []
    if fc90 > 0.08:
        e3.append(f"field chroma p90 {fc90:.3f} > 0.08")
    if len(peaks) > 2:
        e3.append(f"{len(peaks)} hue clusters")
    acc_vals = {}
    e3b = ""
    if acc_share >= 0.0005:                     # below 0.05 % a chromatic speck is noise, not an accent
        ys_a, xs_a = np.nonzero(accent)
        acc_c = (float(xs_a.mean()) / w, float(ys_a.mean()) / h)
        on = float((accent & sub_d).sum()) / acc_n if sub_d is not None else 0.0
        near_ = has_sub and dist_w(acc_c[0], acc_c[1], *sfacts["centroid_uv"], A) <= 0.10
        acc_vals = {"share": _r(acc_share, 4), "on_subject": _r(on), "centroid_uv": [_r(acc_c[0]), _r(acc_c[1])],
                    "near_subject": bool(near_), "hue": _r(float(np.median(hue[accent])), 1),
                    "chroma_p50": _r(float(np.median(C[accent])))}
        if acc_share > amax:
            e3.append(f"accent {acc_share:.2%} of the frame (> {amax:.0%}: it stops being an accent)")
        elif acc_share < 0.001:
            notes.append(f"E3 colour: a small accent ({acc_share:.2%} of the frame, < 0.1 %) may not read")
        if has_sub and on < 0.5 and not near_:
            e3b = (f"the accent ({acc_vals['hue']:.0f} deg, {acc_share:.2%}) sits away from the subject "
                   f"at ({acc_c[0]:.2f}, {acc_c[1]:.2f})")
    elif brief.get("accent_expected"):
        e3.append("no accent measured (C >= 0.07, >= 60 deg from the field) though the brief expects one: measure it "
                  "in the render under the shot's white balance")
    add(Item("E3", "colour", "gate", "fail" if e3 else "pass",
             {"field_hue": _r(field_hue, 1), "field_C_p90": _r(fc90), "hue_clusters": [_r(p_, 0) for p_ in peaks],
              "accent": acc_vals or None, "accent_px": acc_n},
             "OKLCH: field chroma p90 <= 0.08; <= 2 hue clusters (C >= 0.04, chroma-weighted); one accent C >= 0.07, "
             ">= 60 deg from the field hue, 0.1-4 % of the frame (accent_max)", "; ".join(e3)))
    if acc_vals:
        add(Item("E3b", "accent on the subject", "+R", "fail" if e3b else "pass",
                 {"on_subject": acc_vals["on_subject"], "near_subject": acc_vals["near_subject"]},
                 "the accent sits on the subject (>= 50 % of its pixels) or near it (<= 10 % W); elsewhere it is a colour "
                 "rival", e3b))

    # ===================================================================================================== G1
    dot_item = None
    if has_sub:
        share = sfacts["share"]
        vals = {"share": _r(share, 5), "named": subj_name, "source": sub_src}
        note = ""
        if sub_src == "point":
            st, note = "n/a", "a point subject (--subject-xy): mask it to gate G1"
        elif share >= 0.003:
            st = "pass"
        elif share >= 0.0002:
            # a dot subject (an LED, a key, a print): 4 of the 6 small-detail conditions
            dmeq = 2.0 * math.sqrt(max(float(subA.sum()), 1.0) / math.pi)          # equivalent diameter (px)
            ring3 = ndi.binary_dilation(subA, iterations=max(2, int(round(3 * dmeq)))) & ~subA
            ringl = ndi.binary_dilation(subA, iterations=max(2, int(round(dmeq)))) & ~subA
            dL_loc = abs(float(np.median(L[subA])) - float(np.median(L[ringl]))) if ringl.any() else 0.0
            top1 = L >= float(np.quantile(L, 0.99))
            d1v = next((it.d["values"] for it in items if it.d["id"] == "D1"), {})
            d2v = next((it.d["values"] for it in items if it.d["id"] == "D2"), {})
            cond = {"sharpest": bool(cue.get("b_sharp")),
                    "brightest_or_contrasty": dL_loc >= 0.10 or float((top1 & subA).sum()) >= 0.5 * float(subA.sum()),
                    "only_saturated_hue": bool(cue.get("d_colour")),
                    "on_an_anchor": (d1v.get("systems") is not None and
                                     min(v_["dist_w"] for v_ in d1v["systems"].values()) <= 0.03),
                    "lines_converge": (d2v.get("n_lines_to_subject") or 0) >= 2,
                    "clean_space_3x": bool(ring3.any()) and float(quiet[ring3].mean()) >= 0.8}
            n_ok = int(sum(cond.values()))
            vals.update({"dot": True, "conditions": cond, "n_conditions": n_ok, "local_dL": _r(dL_loc)})
            st, note = "pass", f"a dot subject ({share:.3%})"
            dot_item = Item("G1b", "dot subject conditions", "+R", "pass" if n_ok >= 4 else "fail",
                            {"conditions": cond, "n_conditions": n_ok},
                            ">= 4 of 6: sharpest, brightest / most contrasty, the only saturated hue, on an anchor, >= 2 "
                            "lines converge, clean space >= 3x its diameter",
                            "" if n_ok >= 4 else f"meets {n_ok}/6: " + ", ".join(k_ for k_, v_ in cond.items() if not v_)
                            + " missing")
        else:
            st, note = "fail", f"subject is {share:.4%} of the frame (< 0.02 %)"
        items[0] = Item("G1", "subject defined", "gate", st, vals,
                        ">= 0.3 % of the frame, or a dot subject >= 0.02 % (then G1b: 4 of 6 detail conditions)", note)
        if dot_item is not None:
            items.insert(1, dot_item)
    else:
        items[0] = Item("G1", "subject defined", "gate", "fail", {"source": sub_src}, ">= 0.3 % of the frame",
                        "no subject mask (--mask, --index + --ids, --product-*, or --subject-xy)")

    # ===================================================================================================== verdict
    D = [it.d for it in items]
    fails = [f"{d['id']} {d['name']}: {d['note'] or 'fail'}" for d in D if d["class"] == "gate" and d["status"] == "fail"]
    owed = [f"{d['id']} {d['name']}: {d['note'] or d['status']}" for d in D if d["class"] == "+R" and d["status"] == "fail"]
    rnotes = [f"{d['id']} {d['name']}: {d['note']}" for d in D if d["status"] == "warn" and d["note"]]
    verdict = "FAIL" if fails else ("PASS-REASONS" if owed else "PASS")
    res = {"tool": "comp_analysis.py frame", "version": VERSION, "image": str(a.image), "size": [W, H],
           "analysis_width": w,
           "inputs": {"depth": a.depth, "mask": a.mask, "index": a.index, "ids": a.ids, "product_mask": a.product_mask,
                      "product_ids": a.product_ids, "camera": cam or None, "brief": brief or None, "lines": a.lines,
                      "subject_xy": a.subject_xy},
           "subject": dict(name=subj_name, source=sub_src, **({k: _clean(v) for k, v in sfacts.items()} if sfacts else {})),
           "product": {k: _clean(v) for k, v in pfacts.items()} if pfacts else None,
           "scope": scope, "scope_source": scope_src, "mode": mode,
           "items": _clean(D), "verdict": verdict, "fails": fails, "reasons_owed": owed, "notes": notes + rnotes}
    ctx = dict(rgbA=rgbA, w=w, h=h, W=W, H=H, subA=subA, prodA=prodA, accent=accent if acc_n >= acc_min else None,
               seg=seg, con=con, seg_len=seg_len, lead_idx=lead_idx, out_idx=out_idx, dead=dead, rivals=rivals,
               flagged=flagged_edges, anc=anc, wc=(cu, cv), res=res)
    res["timing_s"] = round(time.time() - t_start, 3)
    return res, ctx


# ================================================================================================================ tile
def _font(sz):
    for p in ("/System/Library/Fonts/HelveticaNeue.ttc", "/System/Library/Fonts/Helvetica.ttc",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf"):
        try:
            return ImageFont.truetype(p, sz)
        except Exception:  # noqa: BLE001
            continue
    try:
        return ImageFont.load_default(size=sz)
    except TypeError:
        return ImageFont.load_default()


def _outline_px(m, ow, oh, wd=2):
    mm = rs(m.astype(np.float32), ow, oh, "nearest") > 0.5
    return mm & ~ndi.binary_erosion(mm, iterations=wd)


def draw_tile(ctx, path, tw=1280):
    res = ctx["res"]
    w, h = ctx["w"], ctx["h"]
    th = int(round(h * tw / w))
    k = tw / w
    base = Image.fromarray((ctx["rgbA"] * 255 + 0.5).astype(np.uint8)).resize((tw, th), Image.BILINEAR)
    base = Image.blend(base, Image.new("RGB", base.size, (0, 0, 0)), 0.30)
    arr = np.asarray(base).copy()
    if ctx["accent"] is not None:
        arr[_outline_px(ndi.binary_dilation(ctx["accent"]), tw, th, 1)] = (60, 220, 255)
    if ctx["prodA"] is not None:
        arr[_outline_px(ctx["prodA"], tw, th)] = (235, 235, 235)
    if ctx["subA"] is not None:
        arr[_outline_px(ctx["subA"], tw, th)] = (255, 70, 70)
    im = Image.fromarray(arr)
    dr = ImageDraw.Draw(im, "RGBA")
    for t in (1 / 3, 2 / 3):
        dr.line([(t * tw, 0), (t * tw, th)], fill=(255, 255, 255, 120), width=1)
        dr.line([(0, t * th), (tw, t * th)], fill=(255, 255, 255, 120), width=1)
    for t in (1 - 1 / PHI, 1 / PHI):
        for s in range(0, th, 10):
            dr.line([(t * tw, s), (t * tw, s + 5)], fill=(255, 180, 40, 170), width=1)
        for s in range(0, tw, 10):
            dr.line([(s, t * th), (s + 5, t * th)], fill=(255, 180, 40, 170), width=1)
    for (u, v) in ctx["anc"]["diagonal"]:
        x, y = u * tw, v * th
        dr.line([(x - 7, y - 7), (x + 7, y + 7)], fill=(180, 130, 255, 220), width=2)
        dr.line([(x - 7, y + 7), (x + 7, y - 7)], fill=(180, 130, 255, 220), width=2)
    dr.line([(tw / 2 - 8, th / 2), (tw / 2 + 8, th / 2)], fill=(255, 255, 255, 160))
    dr.line([(tw / 2, th / 2 - 8), (tw / 2, th / 2 + 8)], fill=(255, 255, 255, 160))
    seg, sl = ctx["seg"], ctx["seg_len"]
    lead, outs = set(int(i) for i in ctx["lead_idx"]), set(int(i) for i in ctx["out_idx"])
    for i in np.argsort(sl):
        if sl[i] < 0.15 * w:
            continue
        x0, y0, x1, y1 = (float(v) * k for v in seg[i])
        if i in lead:
            dr.line([(x0, y0), (x1, y1)], fill=(70, 255, 110, 235), width=3)
        elif i in outs:
            dr.line([(x0, y0), (x1, y1)], fill=(255, 225, 60, 210), width=2)
        else:
            dr.line([(x0, y0), (x1, y1)], fill=(170, 170, 170, 130), width=1)
    fnt_s = _font(max(11, int(tw / 95)))
    for c_ in ctx["dead"]:
        x0, y0, x1, y1 = (float(v) * k for v in c_["seg"]) if c_["src"] != "projected" else \
            (float(v) * k for v in c_["seg"])
        dr.line([(x0, y0), (x1, y1)], fill=(255, 0, 170, 255), width=4)
        dr.text(((x0 + x1) / 2 + 6, (y0 + y1) / 2 + 4), f"G7 {c_['dev']:.1f} deg", fill=(255, 80, 200, 255), font=fnt_s)
    for box, lab in ctx["rivals"]:
        dr.rectangle([box[0] * k, box[1] * k, box[2] * k, box[3] * k], outline=(255, 150, 30, 230), width=3)
        dr.text((box[0] * k + 4, box[1] * k + 2), lab, fill=(255, 170, 60, 255), font=fnt_s)
    cu, cv = ctx["wc"]
    dr.line([(tw / 2, th / 2), (cu * tw, cv * th)], fill=(90, 150, 255, 220), width=2)
    dr.ellipse([cu * tw - 6, cv * th - 6, cu * tw + 6, cv * th + 6], fill=(90, 150, 255, 255))
    d1 = next((d for d in res["items"] if d["id"] == "D1"), None)
    if res["subject"].get("centroid_uv"):
        su, sv = res["subject"]["centroid_uv"]
        x, y = su * tw, sv * th
        if d1 and d1["values"].get("reference_uv"):
            ru, rv = d1["values"]["reference_uv"]
            dr.line([(x, y), (ru * tw, rv * th)], fill=(255, 235, 60, 240), width=2)
            dr.ellipse([ru * tw - 4, rv * th - 4, ru * tw + 4, rv * th + 4], outline=(255, 235, 60, 255), width=2)
        dr.ellipse([x - 11, y - 11, x + 11, y + 11], outline=(255, 70, 70, 255), width=3)
        dr.line([(x - 18, y), (x + 18, y)], fill=(255, 70, 70, 255), width=1)
        dr.line([(x, y - 18), (x, y + 18)], fill=(255, 70, 70, 255), width=1)
    for e in ctx["flagged"]:
        box = {"left": [0, 0, 6, th], "right": [tw - 6, 0, tw, th], "top": [0, 0, tw, 6], "bottom": [0, th - 6, tw, th]}[e]
        dr.rectangle(box, fill=(255, 50, 50, 220))
    # readout
    it = {d["id"]: d for d in res["items"]}

    def v(i, key, default=None):
        return it.get(i, {}).get("values", {}).get(key, default)

    def st(i):
        s = it.get(i, {}).get("status", "n/a")
        return {"pass": "ok", "fail": "FAIL", "warn": "warn", "n/a": "-"}[s]
    bad_g = [d["id"] for d in res["items"] if d["class"] == "gate" and d["status"] == "fail"]
    owed = [d["id"] for d in res["items"] if d["class"] == "+R" and d["status"] == "fail"]
    rows = [f"{res['verdict']}   gates failed: {' '.join(bad_g) or '-'}   reasons owed: {' '.join(owed) or '-'}"]
    s = res["subject"]
    g3 = it.get("G3", {}).get("values", {})
    rows.append(f"subject '{s.get('name')}' {100 * (s.get('share') or 0):.2f}% [{st('G1')}]  in frame [{st('G2')}]  focus "
                + (f"{g3.get('combined_px1920')} px@1920" if g3.get("combined_px1920") is not None else
                   f"sharp {g3.get('sharp_rel', ['-'])[0]}") + f" [{st('G3')}]")
    rows.append(f"wins {v('G4', 'n_cues', '-')}/4 dL {v('G4', 'squint_dL', '-')} rivals {len(v('G4', 'rivals', []) or [])} "
                f"[{st('G4')}]  edges [{st('G5')}]  tangents [{st('G6')}]  lines [{st('G7')}]  dead [{st('DZ')}]")
    if d1 and d1["status"] != "n/a":
        rows.append(f"place {d1['values'].get('reference')} {100 * (d1['values'].get('dist_to_reference_w') or 0):.1f}% W "
                    f"[{st('D1')}]  null hit {100 * (d1['values'].get('null_hit_rate') or 0):.0f}%  eye "
                    f"{v('D2', 'n_lines_to_subject', '-')} lines -> subj [{st('D2')}]  divisions [{st('D3')}]")
    rows.append(f"space {v('D4', 'quiet_share', '-')} ({v('D4', 'mode', '')}) coh {v('D4', 'coherence', '-')} rect "
                f"{v('D4', 'empty_rect', '-')} [{st('D4')}]  masses {v('D5', 'n_masses_ge_2pct', '-')} "
                f"x{v('D5', 'largest_vs_next', '-')} IoU {v('D5', 'iou_with_target', '-')} [{st('D5')}]")
    rows.append(f"DCM {v('D6', 'dcm', '-')} sym {v('D6', 'symmetry', '-')} [{st('D6')}]  size w{v('D7', 'width_share', '-')} "
                f"[{st('D7')}]  thumb dL {v('D8', 'subject_dL_96', '-')} [{st('D8')}]")
    rows.append(f"tone ring [{st('E1a')}] outline {v('E1b', 'sep_frac', '-')} [{st('E1b')}] bg "
                f"{v('E1c', 'ev_subject_vs_bg', '-')} EV [{st('E1c')}]  rivals [{st('E2a')}/{st('E2b')}]  colour "
                f"fC90 {v('E3', 'field_C_p90', '-')} hues {len(v('E3', 'hue_clusters', []) or [])} [{st('E3')}]")
    fnt = _font(max(12, int(tw / 82)))
    lh = int(getattr(fnt, "size", 13) * 1.3)
    bw = int(max(dr.textlength(r_, font=fnt) for r_ in rows)) + 18
    bh = lh * len(rows) + 10
    y0 = th - bh - 8
    dr.rectangle([8, y0, 8 + bw, th - 8], fill=(0, 0, 0, 185))
    for i, r_ in enumerate(rows):
        col = (255, 110, 110, 255) if (i == 0 and res["verdict"] == "FAIL") else \
            ((255, 210, 90, 255) if i == 0 and res["verdict"] != "PASS" else (240, 240, 240, 255))
        dr.text((16, y0 + 5 + i * lh), r_, fill=col, font=fnt)
    im.save(path, quality=90)


def frame_main(a):
    res, ctx = analyse_frame(a)
    out = Path(a.out) if a.out else Path(a.image).with_suffix("")
    out.parent.mkdir(parents=True, exist_ok=True)
    jp = Path(str(out) + ".analysis.json")
    if not a.no_tile:
        tp = Path(str(out) + "_tile.jpg")
        draw_tile(ctx, tp)
        res["tile"] = str(tp)
    jp.write_text(json.dumps(res, indent=1, ensure_ascii=False))
    if not a.quiet:
        print(f"{res['verdict']}  {Path(a.image).name}  ({res['timing_s']} s)  -> {jp}")
        for f in res["fails"]:
            print(f"  FAIL  {f}")
        for f in res["reasons_owed"]:
            print(f"  +R    {f}")
        for f in res["notes"]:
            print(f"  note  {f}")
    return 1 if res["verdict"] == "FAIL" else 0


# ================================================================================================================ sameness
def _stems(paths):
    files = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            files += sorted(q for q in p.iterdir() if q.suffix.lower() in IMG_EXT and "_tile" not in q.stem)
        elif p.exists():
            files.append(p)
        else:
            raise SystemExit(f"not found: {p}")
    return files


def thumb_feat(path, mask_dir=None, exr_encoding="srgb"):
    rgb = load_image(path, exr_encoding)
    H, W = rgb.shape[:2]
    w = min(480, W)
    h = max(2, int(round(H * w / W)))
    small = np.dstack([rs(rgb[..., i], w, h) for i in range(3)])
    Ls = lstar01(srgb_to_lin(small))
    Lb = ndi.gaussian_filter(Ls, 0.01 * w)
    s = rs(Lb, 32, 18)
    z = (s - s.mean()) / (s.std() + 1e-6)
    thr, _ = otsu(s, 3)
    notan = np.digitize(s, thr)
    box = None
    if mask_dir:
        for cand in (Path(mask_dir) / f"{Path(path).stem}.png", Path(mask_dir) / f"{Path(path).stem}_mask.png"):
            if cand.exists():
                m = load_mask(cand)
                f = mask_facts(m)
                if f:
                    x0, y0, x1, y1 = f["bbox_px"]
                    mh, mw = m.shape
                    box = (x0 / mw, y0 / mh, (x1 + 1) / mw, (y1 + 1) / mh)
                break
    return z.ravel() / math.sqrt(z.size), notan, box


def _iou(a, b):
    if a is None or b is None:
        return 0.5
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / u if u > 0 else 0.0


def sim_parts(fa, fb):
    c = max(0.0, float(np.dot(fa[0], fb[0])))
    n = float((fa[1] == fb[1]).mean())
    i = _iou(fa[2], fb[2])
    return (c + n + i) / 3.0, c, n, i


def sameness_main(a):
    t0 = time.time()
    files = _stems(a.paths)
    if len(files) < 2:
        raise SystemExit("sameness needs >= 2 images")
    F = {}
    for f in files:
        F[f] = thumb_feat(f, a.masks, a.exr_encoding)
    pairs = []
    for i in range(len(files)):
        for j in range(i + 1, len(files)):
            s, c, n, io = sim_parts(F[files[i]], F[files[j]])
            pairs.append({"a": files[i].stem, "b": files[j].stem, "sim": round(s, 3), "squint_corr": round(c, 3),
                          "notan_agree": round(n, 3), "box_iou": round(io, 3)})
    pairs.sort(key=lambda p: -p["sim"])
    flagged = [p for p in pairs if p["sim"] >= a.thr]
    nn = {}
    for p in pairs:
        for x, y in ((p["a"], p["b"]), (p["b"], p["a"])):
            if x not in nn or p["sim"] > nn[x]["sim"]:
                nn[x] = {"nearest": y, "sim": p["sim"]}
    res = {"tool": "comp_analysis.py sameness", "version": VERSION, "n": len(files), "threshold": a.thr,
           "masks": bool(a.masks), "box_term": "measured" if a.masks else "0.5 (no masks, as calibrated)",
           "max": pairs[0]["sim"], "median": round(float(np.median([p["sim"] for p in pairs])), 3),
           "flagged": flagged, "nearest": nn, "pairs": pairs}
    if a.adjacent:
        lookup = {(p["a"], p["b"]): p for p in pairs}
        lookup.update({(p["b"], p["a"]): p for p in pairs})
        res["adjacent"] = [lookup[(files[i].stem, files[i + 1].stem)] for i in range(len(files) - 1)]
    res["timing_s"] = round(time.time() - t0, 2)
    out = Path(a.out) if a.out else Path("sameness.json")
    out.write_text(json.dumps(res, indent=1))
    print(f"sameness: {len(files)} frames, {len(pairs)} pairs, max {res['max']:.3f}, median {res['median']:.3f}; "
          f"{len(flagged)} pair(s) >= {a.thr}  ({res['timing_s']} s) -> {out}")
    for p in flagged[:20]:
        print(f"  {p['sim']:.3f}  {p['a']}  ~  {p['b']}   (squint {p['squint_corr']:.2f}, notan {p['notan_agree']:.2f}, "
              f"box {p['box_iou']:.2f})")
    if a.adjacent:
        adj_bad = [p for p in res["adjacent"] if p["sim"] >= a.thr]
        print(f"  adjacent pairs >= {a.thr}: {len(adj_bad)}" + "".join(f"\n    {p['sim']:.3f}  {p['a']} -> {p['b']}"
                                                                    for p in adj_bad))
    if a.sheet and flagged:
        tw, thh = 400, 225
        rows_ = flagged[:12]
        sheet = Image.new("RGB", (2 * tw + 10, len(rows_) * (thh + 24)), (0, 0, 0))
        dr = ImageDraw.Draw(sheet)
        fn = _font(14)
        byname = {f.stem: f for f in files}
        for r_, p in enumerate(rows_):
            for c_, nm in enumerate((p["a"], p["b"])):
                im = Image.fromarray((np.clip(load_image(byname[nm], a.exr_encoding), 0, 1) * 255).astype(np.uint8))
                sheet.paste(im.resize((tw, thh), Image.BILINEAR), (c_ * (tw + 10), r_ * (thh + 24) + 22))
                dr.text((c_ * (tw + 10) + 4, r_ * (thh + 24) + 3), (f"{p['sim']:.2f}  " if c_ == 0 else "") + nm,
                        fill=(255, 230, 80), font=fn)
        sheet.save(a.sheet, quality=88)
        print(f"  sheet -> {a.sheet}")
    return 0


# ================================================================================================================ cuts
def _side(spec, base):
    def P(p):
        q = Path(p)
        return q if q.is_absolute() else (base / q)
    img = P(spec["image"])
    rgb = load_image(img)
    H, W = rgb.shape[:2]
    eye, src = None, None
    m = None
    if spec.get("mask"):
        m = load_mask(P(spec["mask"]))
    elif spec.get("index") and spec.get("ids"):
        idx = np.rint(load_array(P(spec["index"]), "index", spec.get("index_channel"))).astype(np.int32)
        m = np.isin(idx, parse_ids(spec["ids"], idx))
    if m is not None and m.any():
        f = mask_facts(m)
        eye, src = f["centroid_uv"], "mask centroid"
    elif spec.get("eye"):
        eye, src = [float(spec["eye"][0]), float(spec["eye"][1])], "given"
    else:
        w = min(480, W)
        h = max(2, int(round(H * w / W)))
        Ls = oklab(srgb_to_lin(np.dstack([rs(rgb[..., i], w, h) for i in range(3)])))[0]
        S = rs(spectral_residual(Ls), w, h)
        y_, x_ = np.unravel_index(int(np.argmax(ndi.gaussian_filter(S, 0.03 * w))), S.shape)
        eye, src = [(x_ + 0.5) / w, (y_ + 0.5) / h], "saliency peak (no mask)"
    w = min(480, W)
    h = max(2, int(round(H * w / W)))
    Yd = np.dstack([rs(rgb[..., i], w, h) for i in range(3)]) @ LUMA
    Yb = ndi.gaussian_filter(Yd, 0.01 * w)
    top = Yb >= np.quantile(Yb, 0.97)
    lb, nb = ndi.label(top)
    big = int(np.argmax(ndi.sum(top, lb, range(1, nb + 1)))) + 1 if nb else 0
    by, bx = ndi.center_of_mass(lb == big) if nb else (h / 2, w / 2)
    cam = spec.get("camera") or {}
    if isinstance(cam, str):
        cam = load_json_arg(str(P(cam)), "camera")
    cam = norm_camera(cam)
    fw = cam.get("field_w_mm")
    if fw is None and all(k in cam for k in ("focal_mm", "focus_m")):
        fw = cam["focus_m"] * cam.get("sensor_w_mm", 36.0) / cam["focal_mm"] * 1000.0
    return {"image": str(img), "eye_uv": [round(eye[0], 4), round(eye[1], 4)], "eye_source": src,
            "bright_uv": [round(float(bx + 0.5) / w, 4), round(float(by + 0.5) / h, 4)], "mean_Y": round(float(Yd.mean()), 3),
            "az": cam.get("az"), "el": cam.get("el"), "field_w_mm": None if fw is None else round(float(fw), 1),
            "aspect": W / H}


def cuts_main(a):
    t0 = time.time()
    p = Path(a.cuts)
    spec = json.loads(p.read_text())
    if isinstance(spec, dict):
        spec = spec.get("cuts", [])
    rows = []
    n_fail = 0
    for i, c in enumerate(spec):
        o, n = _side(c["out"], p.parent), _side(c["in"], p.parent)
        A_ = o["aspect"]
        jump = math.hypot(o["eye_uv"][0] - n["eye_uv"][0], (o["eye_uv"][1] - n["eye_uv"][1]) / A_) * 100
        bj = math.hypot(o["bright_uv"][0] - n["bright_uv"][0], (o["bright_uv"][1] - n["bright_uv"][1]) / A_) * 100
        ang = None
        if o["az"] is not None and n["az"] is not None:
            daz = ((n["az"] - o["az"] + 180) % 360) - 180
            de = (n["el"] - o["el"]) if (o["el"] is not None and n["el"] is not None) else 0.0
            ang = math.hypot(daz, de)
        ratio = None
        if o["field_w_mm"] and n["field_w_mm"]:
            ratio = max(o["field_w_mm"], n["field_w_mm"]) / min(o["field_w_mm"], n["field_w_mm"])
        light_cut = bool(c.get("light_cut"))
        why = []
        if jump > 25:
            why.append(f"eye jumps {jump:.0f} % W")
        if ang is None and ratio is None:
            change_ok = None
        else:
            change_ok = (ang is not None and ang >= 30) or (ratio is not None and ratio >= 1.5)
            if not change_ok:
                why.append(f"too similar: {ang if ang is not None else float('nan'):.0f} deg, x{ratio or float('nan'):.2f}")
        if bj > 50 and not light_cut:
            why.append(f"brightest region jumps {bj:.0f} % W")
        verdict = "FAIL" if why else ("PASS" if change_ok is not None else "PASS (eye + light only; no camera)")
        n_fail += bool(why)
        rows.append({"name": c.get("name", str(i)), "verdict": verdict, "why": why, "eye_jump_pctW": round(jump, 1),
                     "angle_deg": None if ang is None else round(ang, 1), "field_ratio": None if ratio is None else round(ratio, 2),
                     "bright_jump_pctW": round(bj, 1), "light_cut": light_cut, "out": o, "in": n})
    res = {"tool": "comp_analysis.py cuts", "version": VERSION, "rules": "eye <= 25 % W; >= 30 deg or >= x1.5 field; "
           "brightest region <= 50 % W unless a light cut", "cuts": rows, "n_fail": n_fail,
           "timing_s": round(time.time() - t0, 2)}
    out = Path(a.out) if a.out else p.with_suffix(".report.json")
    out.write_text(json.dumps(res, indent=1))
    for r in rows:
        ang = "-" if r["angle_deg"] is None else f"{r['angle_deg']:.0f}deg"
        rat = "-" if r["field_ratio"] is None else f"x{r['field_ratio']:.2f}"
        print(f"{r['verdict']:5s} {r['name']:>10s}  eye {r['eye_jump_pctW']:5.1f}%W  {ang:>6s} {rat:>6s}  bright "
              f"{r['bright_jump_pctW']:5.1f}%W" + (f"   <- {'; '.join(r['why'])}" if r["why"] else ""))
    print(f"cuts: {len(rows)}, {n_fail} FAIL ({res['timing_s']} s) -> {out}")
    return 1 if n_fail else 0


# ================================================================================================================ main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("frame", help="analyse one frame")
    f.add_argument("--image", required=True)
    f.add_argument("--depth")
    f.add_argument("--depth-channel")
    f.add_argument("--mask")
    f.add_argument("--index")
    f.add_argument("--index-channel")
    f.add_argument("--ids", help="subject ids in --index, e.g. 3,25-31")
    f.add_argument("--product-mask")
    f.add_argument("--product-ids", help='product ids in --index, e.g. "1-40,42-100" or ">0"')
    f.add_argument("--glass-ids", help="transparent product parts (glass, acrylic covers) left out of the outline "
                                       "separation (E1b)")
    f.add_argument("--prop-ids", help="set props in --index (default: every id mostly outside the product and the "
                                      "subject, covering < 25 %% of the frame)")
    f.add_argument("--camera", help="camera JSON file (or JSON text)")
    f.add_argument("--brief", help="brief JSON file (or JSON text)")
    f.add_argument("--lines", help="projected 3D edges JSON")
    f.add_argument("--facing", choices=("left", "right"))
    f.add_argument("--subject-xy", help="U,V of the subject when no mask exists (a 3.5 %% H disc)")
    f.add_argument("--exr-encoding", choices=("srgb", "none"), default="srgb")
    f.add_argument("--out", help="output prefix (default: the image path without its extension)")
    f.add_argument("--no-tile", action="store_true")
    f.add_argument("--quiet", action="store_true")
    s = sub.add_parser("sameness", help="thumbnail sameness across a set")
    s.add_argument("paths", nargs="+")
    s.add_argument("--masks")
    s.add_argument("--thr", type=float, default=0.72)
    s.add_argument("--adjacent", action="store_true")
    s.add_argument("--exr-encoding", choices=("srgb", "none"), default="srgb")
    s.add_argument("--out")
    s.add_argument("--sheet")
    c = sub.add_parser("cuts", help="cut pairs")
    c.add_argument("cuts")
    c.add_argument("--out")
    a = ap.parse_args()
    try:
        if a.cmd == "frame":
            return frame_main(a)
        if a.cmd == "sameness":
            return sameness_main(a)
        return cuts_main(a)
    except SystemExit as e:
        if isinstance(e.code, str):
            print(f"comp_analysis: {e.code}", file=sys.stderr)
            return 2
        raise
    except (FileNotFoundError, KeyError, ValueError, ImportError) as e:
        print(f"comp_analysis: {type(e).__name__}: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
