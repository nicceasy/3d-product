"""The "product reads" metric (R1 void, R2 separation). Read-only: measures, never renders.

An example implementation from the project the skill was built on (a black glossy turntable under a smoked acrylic
cover). It runs on any shots folder laid out like this (previews/<id>.jpg, exr/<batch>/<id>.npz|.json|.exr|.png,
exr/<batch>/part_idx.json). Its masks assume that project's object-index naming (product parts > 0, set = 0, a cover
called `hood` and a record that has its own check): adapt `masks()` to your own parts. Defaults: --root = the current
folder, --rules = lighting_rules.json next to this file.

    <python with numpy, scipy, scikit-image, Pillow, OpenEXR> reads_metric.py [ids ...] [--root=<shots dir>]
        [--rules=lighting_rules.json] [--out=reads.json]

Per frame it reads what the viewer sees (previews/<id>.jpg, display-referred) plus the render's own buffers
(exr/<batch>/<id>.npz: IndexOB `index` + `depth`; <id>.json: the candidate + camera; part_idx.json; <id>.exr:
scene-linear Combined). The batch is the exr/<batch>/<id>.png closest to the preview (mean |dL*|), so a re-rendered
frame is matched to the buffers it was actually made from.

Masks: prod = IndexOB > 0 minus `leads` minus the record (vinyl, label, label_b: the record has its own check);
body = prod minus the smoked hood (hood, hood_pads); set = IndexOB == 0. Numbers are CIE L* (0-100) on the preview
unless named `stops_*` (scene-linear EXR).

GATES (thresholds in ../lighting_rules.json `reads_metric.thresholds`; verdict() names the decision-table rows)
R1 void       void_frac = share of the FRAME that is prod with L* < 10 and local sigma(L*) < 1.5 (7 px @960): a black,
              structureless hole. Split by world normals (depth + camera) into void_top / void_vert, plus void_hood
              (the deck seen through the smoked lid) -> which light to add.
R2 separation figure-ground: prod outline pixels next to set where the set lies BEHIND (depth step >= max(5 cm, 10 %));
              dL* = |mean L* inside - outside| in 5 px bands (sigma 2 px) @960; sep_frac = share with dL* >= 8;
              sep_frac_body = the same on the opaque body's outline (used when present). Contact edges excluded.
R3 subject    the named part (cand.cam.subject / subject_parts): ring dL* and internal RMS
              (warn only, uncalibrated)
DIAGNOSTICS   prod/body L* p50/p90, dark_frac, hl_frac (L* >= 50), faces {top,+x,+y,-x,-y} + face_sep,
              stops_body_set = log2(Y_body p50 / Y_set p50), stops_hl."""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.color import rgb2lab

ROOT = Path.cwd()                                                   # --root overrides
RULES = Path(__file__).resolve().parent / "lighting_rules.json"       # --rules overrides


def lstar(rgb01):
    return rgb2lab(rgb01)[..., 0]


def load_exr_Y(p):
    import OpenEXR
    import Imath
    f = OpenEXR.InputFile(str(p))
    dw = f.header()["dataWindow"]
    w, h = dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1
    ch = {c.split(".")[-1]: c for c in f.header()["channels"]}
    pt = Imath.PixelType(Imath.PixelType.FLOAT)
    rgb = [np.frombuffer(f.channel(ch[c], pt), np.float32).reshape(h, w) for c in "RGB"]
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def pick_batch(fid):
    """the exr/<batch> whose AgX png is closest to the preview jpg"""
    prev = ROOT / "previews" / f"{fid}.jpg"
    P = np.asarray(Image.open(prev).convert("RGB").resize((240, 135)), np.float32) / 255
    best = None
    for png in sorted(ROOT.glob(f"exr/*/{fid}.png")):
        Q = np.asarray(Image.open(png).convert("RGB").resize((240, 135)), np.float32) / 255
        d = float(np.abs(lstar(P) - lstar(Q)).mean())
        if best is None or d < best[1]:
            best = (png.parent, d)
    return best


def band_mean(L, region, sigma):
    num = ndi.gaussian_filter(np.where(region, L, 0.0), sigma)
    den = ndi.gaussian_filter(region.astype(np.float32), sigma)
    return num / np.maximum(den, 1e-6), den


def world_normals(depth, cam, W, H):
    fx = cam["lens"] / 36.0 * W
    sx, sy = (cam.get("shift") or [0.0, 0.0])[:2]
    cx, cy = W / 2 - sx * W, H / 2 + sy * W
    u, v = np.meshgrid(np.arange(W) + 0.5, np.arange(H) + 0.5)
    d = np.stack([(u - cx) / fx, -(v - cy) / fx, -np.ones_like(u)], -1)
    d /= np.linalg.norm(d, axis=-1, keepdims=True)          # Cycles' depth pass = distance along the ray
    P = d * depth[..., None]
    du = np.zeros_like(P); dv = np.zeros_like(P)
    du[:, 1:-1] = P[:, 2:] - P[:, :-2]
    dv[1:-1] = P[2:] - P[:-2]
    n = np.cross(du, dv)
    n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-12)
    flip = (n * P).sum(-1) > 0
    n[flip] *= -1
    R = np.asarray(cam["matrix_world"], np.float64)[:3, :3]
    return n @ R.T


def measure(fid, TH=None):
    b = pick_batch(fid)
    if b is None:
        return {"id": fid, "error": "no buffers"}
    bdir, match = b
    meta = json.loads((bdir / f"{fid}.json").read_text())
    PIDX = json.loads((bdir / "part_idx.json").read_text())
    z = np.load(bdir / f"{fid}.npz")
    idx = z["index"].astype(np.int32)
    depth = z["depth"].astype(np.float32)
    H, W = idx.shape
    img = np.asarray(Image.open(ROOT / "previews" / f"{fid}.jpg").convert("RGB").resize((W, H), Image.BILINEAR),
                     np.float32) / 255
    L = lstar(img)
    cand = meta["cand"]; cam = meta["camera"]
    leads = PIDX.get("leads", -1); hood = [PIDX.get("hood", -1), PIDX.get("hood_pads", -1)]
    record = [PIDX.get(k, -1) for k in ("vinyl", "label", "label_b")]
    prod = (idx > 0) & (idx != leads) & ~np.isin(idx, record)   # the turntable as seen (smoked hood included)
    body = prod & ~np.isin(idx, hood)                             # the opaque turntable
    setm = idx == 0
    k = W / 960.0
    out = {"id": fid, "batch": bdir.name, "match_dL": round(match, 2), "state": cand.get("light", {}).get("state"),
           "arch": cand.get("arch"), "whole": bool(cand.get("whole")), "prod_frac": round(float(prod.mean()), 3),
           "body_frac": round(float(body.mean()), 3)}
    if body.sum() < 200:
        out["error"] = "body too small"
        return out
    Lb = L[body]; Lp = L[prod]
    out["prod_L50"] = round(float(np.percentile(Lp, 50)), 1)
    out["prod_L90"] = round(float(np.percentile(Lp, 90)), 1)
    out["dark_frac"] = round(float((Lp < 10).mean()), 3)         # the product as seen, the smoked hood included
    out["hl_frac"] = round(float((Lp >= 50).mean()), 4)
    out["body_L50"] = round(float(np.percentile(Lb, 50)), 1)
    out["body_L90"] = round(float(np.percentile(Lb, 90)), 1)
    out["body_dark_frac"] = round(float((Lb < 10).mean()), 3)
    out["hl35_frac"] = round(float((Lp >= 35).mean()), 4)
    # M1b void: product pixels that are black AND structureless (local σ over 7 px @960 < 1.5 L*) — share of the frame
    kk = max(3, int(round(7 * k)) | 1)
    mu = ndi.uniform_filter(L, kk); sd = np.sqrt(np.maximum(ndi.uniform_filter(L * L, kk) - mu * mu, 0))
    void = prod & (L < 10) & (sd < 1.5)
    out["void_frac"] = round(float(void.mean()), 3)
    out["void_prod"] = round(float(void.sum() / max(1, prod.sum())), 3)
    hoodm = prod & np.isin(idx, hood)
    out["void_hood"] = round(float((void & hoodm).mean()), 3)      # the deck seen through the smoked hood, black
    out["hood_frac"] = round(float(hoodm.mean()), 3)
    out["hood_L50"] = round(float(np.median(L[hoodm])), 1) if hoodm.sum() > 200 else None
    out["frame_L50"] = round(float(np.median(L)), 1)
    out["set_L50"] = round(float(np.median(L[setm])), 1) if setm.sum() > 200 else None
    # M2 figure-ground separation: the product's outline (hood included) where the set lies well BEHIND it (depth step
    # ≥ max(5 cm, 10 %)); contact edges (the credenza under the feet, a dark contact line by nature) are excluded
    k2 = max(2, int(2 * k))
    edge = np.zeros_like(prod); edge[:k2] = edge[-k2:] = True; edge[:, :k2] = True; edge[:, -k2:] = True
    sil = prod & ndi.binary_dilation(setm, structure=np.ones((3, 3), bool)) & ~edge
    out["sil_px"] = 0; out["sep_med"] = None; out["sep_frac"] = None
    if sil.sum() >= 0.1 * W:
        bw = 5 * k
        dist_in = ndi.distance_transform_edt(prod); dist_out = ndi.distance_transform_edt(~prod)
        inner = prod & (dist_in <= bw); outer = setm & (dist_out <= bw)
        Li, _ = band_mean(L, inner, 2 * k); Lo, _ = band_mean(L, outer, 2 * k)
        Di, _ = band_mean(depth, inner, 2 * k); Do, _ = band_mean(depth, outer, 2 * k)
        fig = sil & ((Do - Di) >= np.maximum(0.05, 0.10 * Di))
        out["sil_px"] = int(fig.sum()); out["contact_px"] = int((sil & ~fig).sum())
        if fig.sum() >= 0.1 * W:
            dL = np.abs(Li - Lo)[fig]
            out["sep_med"] = round(float(np.median(dL)), 1)
            out["sep_frac"] = round(float((dL >= 8).mean()), 3)
            out["ring_L50"] = round(float(np.median(Lo[fig])), 1)        # the background just outside the outline
            fb = fig & ~np.isin(idx, hood)
            out["sep_frac_body"] = round(float((np.abs(Li - Lo)[fb] >= 8).mean()), 3) if fb.sum() >= 0.05 * W else None
            out["sep_frac_hood"] = round(float((np.abs(Li - Lo)[fig & np.isin(idx, hood)] >= 8).mean()), 3) \
                if (fig & np.isin(idx, hood)).sum() >= 0.05 * W else None
    # M3 form from world normals
    try:
        nw = world_normals(depth, cam, W, H)
        same = ndi.minimum_filter(idx, 3) == ndi.maximum_filter(idx, 3)
        dz = ndi.maximum_filter(depth, 3) - ndi.minimum_filter(depth, 3)
        ok = body & same & (dz < 0.02 * np.maximum(depth, 1e-3))
        rot = math.radians(float((cand.get("place") or {}).get("rot", 0.0)))
        az = (np.degrees(np.arctan2(nw[..., 1], nw[..., 0]) - rot) + 360 + 45) % 360 // 90
        cls = np.full(idx.shape, -1, np.int8)
        cls[ok & (nw[..., 2] >= 0.9)] = 0
        vert = ok & (np.abs(nw[..., 2]) <= 0.35)
        cls[vert] = 1 + az[vert].astype(np.int8)
        faces = {}
        for c in range(5):
            mk = cls == c
            if mk.sum() >= max(500 * k * k, 0.03 * body.sum()):
                faces[c] = mk
        names = {0: "top", 1: "+x", 2: "+y", 3: "-x", 4: "-y"}
        meds = {names[c]: round(float(np.median(L[mk])), 1) for c, mk in faces.items()}
        out["faces"] = meds
        out["face_sep"] = round(max(meds.values()) - min(meds.values()), 1) if len(meds) >= 2 else None
        # where the void sits: top-facing vs vertical (camera-facing) faces — picks the light (lighting_rules.json)
        vtop = void & (cls == 0); vvert = void & (cls >= 1)
        out["void_top"] = round(float(vtop.mean()), 3); out["void_vert"] = round(float(vvert.mean()), 3)
    except Exception as e:  # noqa: BLE001
        out["form_error"] = str(e)[:80]
    # M5 subject legibility
    parts = [p for p in cand.get("subject_parts", []) if p in PIDX]
    cs = cand.get("cam", {}).get("subject")
    if isinstance(cs, str) and cs in PIDX:
        parts = [cs] + [q for q in parts if q != cs]
    if not cand.get("whole") and parts:
        sub = idx == PIDX[parts[0]]
        if parts[0] == "vinyl":
            sub |= np.isin(idx, [PIDX.get("label", -1), PIDX.get("label_b", -1)])
        if sub.sum() >= 50:
            ring = ndi.binary_dilation(sub, iterations=max(2, int(0.03 * W))) & ~sub
            out["subject"] = parts[0]
            out["subj_L90"] = round(float(np.percentile(L[sub], 90)), 1)
            out["subj_ring_dL"] = round(abs(float(np.median(L[sub])) - float(np.median(L[ring]))), 1) if ring.any() else None
            out["subj_rms"] = round(float(L[sub].std()), 1)
    # M6 scene-linear
    exr = bdir / f"{fid}.exr"
    if exr.exists():
        Y = load_exr_Y(exr)
        if Y.shape == idx.shape:
            yb = Y[body]; ys = Y[setm] if setm.sum() > 200 else None
            p50 = float(np.percentile(yb, 50)); p90 = float(np.percentile(yb, 90))
            out["stops_hl"] = round(math.log2(max(p90, 1e-9) / max(p50, 1e-9)), 2)
            if ys is not None:
                out["stops_body_set"] = round(math.log2(max(p50, 1e-9) / max(float(np.percentile(ys, 50)), 1e-9)), 2)
    if TH:
        out.update(verdict(out, TH))
    return out


def verdict(m, TH):
    """the gate (lighting_rules.json reads_metric.thresholds). `fails` / `warns` are decision-table keys:
    R1_void (black, structureless product area), R2_merges (outline lost against the background), R3_subject (the named
    part lost in its surroundings; uncalibrated, so warn-only)"""
    fails, warns = [], []
    vf = m.get("void_frac")
    if vf is not None:
        if vf > TH["void_frac_fail"]:
            fails.append("R1_void")
        elif vf > TH["void_frac_warn"]:
            warns.append("R1_void")
    sep = m.get("sep_frac_body") if m.get("sep_frac_body") is not None else m.get("sep_frac")
    if sep is not None and m.get("sil_px", 0) >= TH["sil_px_min_frac_W"] * 960:
        major = m.get("whole") or (m.get("prod_frac") or 0) >= TH["merge_major_prod_frac"]
        if sep < TH["sep_frac_fail"]:
            (fails if major else warns).append("R2_merges")
        elif sep < TH["sep_frac_warn"]:
            warns.append("R2_merges")
    if m.get("subj_ring_dL") is not None and m["subj_ring_dL"] < TH["subj_ring_dL_min"] and \
            (m.get("subj_rms") or 0) < TH["subj_rms_min"]:
        warns.append("R3_subject")
    return {"reads": not fails, "fails": fails, "warns": warns}


def main():
    global ROOT, RULES
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    if opts.get("root"):
        ROOT = Path(opts["root"]).expanduser()
    if opts.get("rules"):
        RULES = Path(opts["rules"]).expanduser()
    ids = args or sorted(p.stem for p in (ROOT / "previews").glob("s*_*.jpg"))
    TH = None
    if RULES.exists():
        TH = json.loads(RULES.read_text())["reads_metric"]["thresholds"]
    res = [measure(i, TH) for i in ids]
    if opts.get("out"):
        Path(opts["out"]).write_text(json.dumps(res, indent=1))
    for r in res:
        print(json.dumps(r))


if __name__ == "__main__":
    main()
