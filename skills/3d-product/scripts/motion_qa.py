#!/usr/bin/env python3
"""motion_qa.py - measure a film's camera motion from per-frame cameras (stage 9 gate, camera-motion.md §7), read-only.

Why: the user judges motion by eye, but a number catches a fault in every frame of every shot. This reads the per-frame
cameras every consumer reads (the edit frames file, greybox-animation.md) and prints the measurable columns of the
stage-9 gate. The generator-increment and clearance checks need the rig's parameters and the set's geometry, so they
stay in the rig module.

Subcommands:
  shots   cams.json [--stills stills.json] [--exempt id,id] [--bg-mult 3]
          per shot: speed (relative %/s, world mm/s), aim rate (deg/s), image flow (px/frame at 1920) on the focus
          plane (ceiling ~11) and on a background plane at 3x the focus distance (2x the ceiling: it is defocused; an
          arc moves the background, not the focus plane), the speed's max/min over the shot (exempt: shots inside the
          ease budget or a named ride), lens/shift changes; with --stills, each FIRST/KEY/LAST against its approved
          still (subject shift in % W, view turn in deg, KEY exactness in mm/deg).
  compare a.json b.json [--mode operator|proof|changed]
          per shot, camera b against camera a frame by frame: matrix and focus differences, the KEY subject's offset
          in px (RMS, peak, velocity, high-frequency residual, largest step, at the KEY).
          operator: b is a's operator layer (gates of camera-motion.md §6).
          proof:    b must equal a at every frame (the camera proof: render packs vs the approved source).
          changed:  b's camera must differ from a's everywhere except the KEY (a new operator pass) and equal it at
                    the KEY (matrix and lens; the focus may lag there, as a focus puller does).
  cuts    cams.json   per cut (N's out frame -> N+1's in frame): the view directions' angle and the ratio of the
          frame widths at the focus distance; similar = angle < 30 deg AND ratio < 1.5 (editing.md §1). Image checks
          at the cut (eye jump, sameness) are comp_analysis.py's.
  regate  cams.json [--every 12]   the frames the composition re-gate checks per shot: FIRST, LAST, the edit's in
          and out frames, and every Nth frame between (camera-motion.md §7), as source frames and edit frames.
Run `shots` on the base cameras for the constant-speed gate; the operator layer varies speed on purpose and is gated
with `compare --mode operator`.
Common: [--json out.json] [--width 1920] [--height 1080] [--set "name=value,..."] (override a limit in LIM for one film).
Exit code 0 = every gate passes, 1 = a fail, 2 = bad input.

Input (JSON; aliases in brackets match the edit frames file):
  {"fps": 24, "sensor_mm": 36.0,
   "shots": [{"id" [edit]: ..., "key_f" [fkl_src_f.KEY]: f, "first_f" [fkl_src_f.FIRST], "last_f" [fkl_src_f.LAST],
              "in_f" [src_in_f], "out_f" [src_out_f], "eased": false,
              "frames": [{"f" [src_f]: f, "matrix": 4x4 world (Blender camera: looks down -Z, +Y up), "lens": mm
                          (the focal the renderer uses), "focus_m": m, "shift": [x, y] (optional)}]}]}
  stills.json: {"<shot id>": {"FIRST": {"matrix", "lens", "focus_m"}, "KEY": {...}, "LAST": {...}}}
The subject is the KEY frame's focus point: the KEY camera's position + focus_m along its view axis.

Requires numpy. Rules of thumb in the limits are judgement from simple-move product films; set your own per film.
"""
import argparse
import json
import math
import sys

import numpy as np

LIM = {"flow_ceiling_px": 11.0, "flow_bg_factor": 2.0, "speed_ratio_max": 1.10, "similar_deg": 30.0, "similar_ratio": 1.5,
       "outcome_shift_pct": 10.0, "key_mm": 0.5, "key_deg": 0.01,
       "op_rms_px": 3.0, "op_peak_px": 5.0, "op_vel_rms_px": 0.4, "op_hf_rms_px": 0.3, "op_step_px": 0.8,
       "proof_tol": 1e-6}


# ---------------------------------------------------------------- input
def load(path):
    with open(path) as f:
        d = json.load(f)
    fps = float(d.get("fps", 24))
    sensor = float(d.get("sensor_mm", 36.0))
    shots = []
    for s in d["shots"]:
        fkl = s.get("fkl_src_f", {}) or {}
        frames = sorted(s["frames"], key=lambda r: r.get("f", r.get("src_f")))
        fr = np.array([r.get("f", r.get("src_f")) for r in frames], float)
        shot = {
            "id": s.get("id", s.get("edit")),
            "key_f": s.get("key_f", fkl.get("KEY")),
            "first_f": s.get("first_f", fkl.get("FIRST")),
            "last_f": s.get("last_f", fkl.get("LAST")),
            "in_f": s.get("in_f", s.get("src_in_f", fr[0])),
            "out_f": s.get("out_f", s.get("src_out_f", fr[-1])),
            "edit_in_f": s.get("edit_in_f"),
            "eased": bool(s.get("eased", s.get("exempt", False))),
            "f": fr,
            "M": np.array([r["matrix"] for r in frames], float),
            "lens": np.array([r["lens"] for r in frames], float),
            "focus": np.array([r.get("focus_m", np.nan) for r in frames], float),
            "edit_f": [r.get("edit_f") for r in frames],
            "shift": np.array([r.get("shift", [0.0, 0.0]) for r in frames], float),
        }
        if shot["key_f"] is None:
            shot["key_f"] = fr[len(fr) // 2]
        shots.append(shot)
    return fps, sensor, shots


def idx(shot, f):
    i = np.nonzero(shot["f"] == f)[0]
    return int(i[0]) if i.size else None


# ---------------------------------------------------------------- geometry
def forward(M):
    v = -M[:3, 2]
    return v / np.linalg.norm(v)


def project(M, lens, shift, P, sensor, W, H):
    """world points P (n,3) -> px (n,2) for a Blender camera with a horizontal sensor fit"""
    Minv = np.linalg.inv(M)
    pc = (Minv[:3, :3] @ np.atleast_2d(P).T).T + Minv[:3, 3]
    k = lens / sensor * W
    x = W / 2 + k * pc[:, 0] / -pc[:, 2] + shift[0] * W
    y = H / 2 - k * pc[:, 1] / -pc[:, 2] - shift[1] * W
    return np.stack([x, y], 1)


def subject(shot):
    k = idx(shot, shot["key_f"])
    M = shot["M"][k]
    return M[:3, 3] + forward(M) * shot["focus"][k]


def plane_grid(M, lens, focus, sensor, W, H):
    """a 3x3 grid of world points on the focus plane, at 10/50/90 % of the frame"""
    pts = []
    for u in (0.1, 0.5, 0.9):
        for v in (0.1, 0.5, 0.9):
            xc = (u - 0.5) * sensor / lens
            yc = (0.5 - v) * sensor * H / W / lens
            pts.append(M[:3, :3] @ (np.array([xc, yc, -1.0]) * focus) + M[:3, 3])
    return np.array(pts)


def rot_deg(Ma, Mb):
    R = Ma[:3, :3].T @ Mb[:3, :3]
    return math.degrees(math.acos(float(np.clip((np.trace(R) - 1) / 2, -1, 1))))


# ---------------------------------------------------------------- shots
def cmd_shots(a):
    fps, sensor, shots = load(a.cams)
    W, H = a.width, a.height
    exempt = {str(v).strip() for v in a.exempt.split(",") if v.strip()}
    stills = json.load(open(a.stills)) if a.stills else {}
    rows, ok_all = [], True
    for s in shots:
        sel = (s["f"] >= s["in_f"]) & (s["f"] <= s["out_f"])
        ii = np.nonzero(sel)[0]
        A = subject(s)
        C = s["M"][:, :3, 3]
        dC = np.linalg.norm(np.diff(C, axis=0), axis=1)
        dist = np.linalg.norm(C[:-1] - A, axis=1)
        rel = dC / dist * fps * 100.0                                # %/s of the distance to the subject
        world = dC * fps * 1000.0                                    # mm/s
        aim = np.array([math.degrees(math.acos(float(np.clip(forward(s["M"][j]) @ forward(s["M"][j + 1]), -1, 1))))
                        for j in range(len(C) - 1)]) * fps          # deg/s
        flow, flow_bg = [], []
        for j in range(len(C) - 1):
            for depth, out in ((s["focus"][j], flow), (s["focus"][j] * a.bg_mult, flow_bg)):
                pts = plane_grid(s["M"][j], s["lens"][j], depth, sensor, W, H)
                p0 = project(s["M"][j], s["lens"][j], s["shift"][j], pts, sensor, W, H)
                p1 = project(s["M"][j + 1], s["lens"][j + 1], s["shift"][j + 1], pts, sensor, W, H)
                out.append(float(np.linalg.norm(p1 - p0, axis=1).mean()))
        flow, flow_bg = np.array(flow), np.array(flow_bg)
        jj = ii[ii < len(C) - 1]                                     # steps that start inside the shot
        r_in, a_in, f_in, fb_in = rel[jj], aim[jj], flow[jj], flow_bg[jj]
        moving = r_in.mean() > 0.2 or a_in.mean() > 0.05
        drive = r_in if r_in.mean() >= a_in.mean() * 1.745 else a_in   # the larger of the two (1 deg ~ 1.745 %)
        ratio = float(drive.max() / max(drive.min(), 1e-12)) if moving else None
        is_eased = s["eased"] or str(s["id"]) in exempt
        row = {"shot": s["id"], "frames": int(sel.sum()), "exempt": is_eased, "moving": bool(moving),
               "rel_speed_pct_s": [round(float(r_in.min()), 3), round(float(r_in.mean()), 3), round(float(r_in.max()), 3)],
               "world_mm_s_mean": round(float(world[jj].mean()), 2),
               "aim_deg_s": [round(float(a_in.min()), 3), round(float(a_in.mean()), 3), round(float(a_in.max()), 3)],
               "flow_px_f": [round(float(f_in.mean()), 2), round(float(f_in.max()), 2)],
               "flow_bg_px_f": [round(float(fb_in.mean()), 2), round(float(fb_in.max()), 2)],
               "speed_max_min": round(ratio, 3) if ratio is not None else None,
               "lens_changes": bool(np.ptp(s["lens"][ii]) > 1e-6),
               "shift_changes": bool(np.ptp(s["shift"][ii], axis=0).max() > 1e-9)}
        g = {"flow": row["flow_px_f"][1] <= LIM["flow_ceiling_px"],
             "flow_background": row["flow_bg_px_f"][1] <= LIM["flow_ceiling_px"] * LIM["flow_bg_factor"],
             "constant_speed": is_eased or ratio is None or ratio <= LIM["speed_ratio_max"],
             "lens_shift_constant": not (row["lens_changes"] or row["shift_changes"])}
        st = stills.get(str(s["id"]))
        if st:
            out = {}
            for tag, fkey in (("FIRST", "first_f"), ("KEY", "key_f"), ("LAST", "last_f")):
                if tag not in st or s[fkey] is None or idx(s, s[fkey]) is None:
                    continue
                j = idx(s, s[fkey])
                Ms = np.array(st[tag]["matrix"], float)
                Ps = Ms[:3, 3] + forward(Ms) * float(st[tag]["focus_m"])
                ps = project(Ms, float(st[tag]["lens"]), st[tag].get("shift", [0, 0]), Ps, sensor, W, H)[0]
                pm = project(s["M"][j], s["lens"][j], s["shift"][j], Ps, sensor, W, H)[0]
                rec = {"shift_pct_W": round(float(np.linalg.norm(pm - ps) / W * 100), 2),
                       "turn_deg": round(rot_deg(Ms, s["M"][j]), 3),
                       "pos_mm": round(float(np.linalg.norm(Ms[:3, 3] - s["M"][j][:3, 3]) * 1000), 3)}
                if tag == "KEY":
                    rec["exact"] = rec["pos_mm"] <= LIM["key_mm"] and rec["turn_deg"] <= LIM["key_deg"]
                    g["key_exact"] = rec["exact"]
                else:
                    rec["reshow"] = rec["shift_pct_W"] >= LIM["outcome_shift_pct"]
                out[tag] = rec
            row["vs_stills"] = out
        row["gates"] = g
        row["pass"] = all(g.values())
        ok_all &= row["pass"]
        rows.append(row)
    for r in rows:
        vs = r.get("vs_stills", {})
        extra = "  ".join(f"{t} {v['shift_pct_W']:.1f}%W {v['turn_deg']:.2f}deg" + (" RESHOW" if v.get("reshow") else "")
                          for t, v in vs.items())
        print(f"{str(r['shot']):>6} {'exempt' if r['exempt'] else '      '} rel {r['rel_speed_pct_s'][1]:6.2f}%/s "
              f"aim {r['aim_deg_s'][1]:5.2f}deg/s flow {r['flow_px_f'][1]:5.2f} bg {r['flow_bg_px_f'][1]:5.2f}px/f "
              f"max/min {r['speed_max_min'] if r['speed_max_min'] is not None else '-':>6} "
              f"{'PASS' if r['pass'] else 'FAIL ' + ','.join(k for k, v in r['gates'].items() if not v)}  {extra}")
    return {"shots": rows, "limits": LIM, "pass": bool(ok_all)}


# ---------------------------------------------------------------- compare
def cmd_compare(a):
    fps, sensor, sa = load(a.a)
    _, _, sb = load(a.b)
    W, H = a.width, a.height
    bmap = {str(s["id"]): s for s in sb}
    rows, ok_all = [], True
    for s in sa:
        t = bmap.get(str(s["id"]))
        if t is None:
            rows.append({"shot": s["id"], "error": "missing in b"})
            ok_all = False
            continue
        common = np.intersect1d(s["f"], t["f"])
        ia = np.array([idx(s, f) for f in common])
        ib = np.array([idx(t, f) for f in common])
        dM = np.abs(s["M"][ia] - t["M"][ib]).reshape(len(common), -1).max(axis=1)
        dF = np.abs(np.nan_to_num(s["focus"][ia]) - np.nan_to_num(t["focus"][ib]))
        dL = np.abs(s["lens"][ia] - t["lens"][ib])
        same_cam = (dM <= LIM["proof_tol"]) & (dL <= LIM["proof_tol"])     # matrix and lens
        same = same_cam & (dF <= LIM["proof_tol"])                         # ... and focus
        k = idx(s, s["key_f"])
        kc = np.nonzero(common == s["key_f"])[0]
        P = subject(s)
        pa = np.array([project(s["M"][i], s["lens"][i], s["shift"][i], P, sensor, W, H)[0] for i in ia])
        pb = np.array([project(t["M"][i], t["lens"][i], t["shift"][i], P, sensor, W, H)[0] for i in ib])
        d = pb - pa
        ins = (common >= s["in_f"]) & (common <= s["out_f"])
        di = d[ins]
        mag = np.linalg.norm(di, axis=1)
        vel = np.linalg.norm(np.diff(di, axis=0), axis=1) if len(di) > 1 else np.zeros(1)
        kk = 9
        if len(di) >= kk:
            ker = np.ones(kk) / kk
            hf = np.stack([di[:, c] - np.convolve(np.pad(di[:, c], kk // 2, mode="edge"), ker, "valid")
                           for c in (0, 1)], 1)
            hf_rms = float(np.sqrt((hf ** 2).sum(1).mean()))
        else:
            hf_rms = 0.0
        key_px = float(np.linalg.norm(d[kc[0]])) if kc.size else None
        row = {"shot": s["id"], "frames": int(len(common)), "identical_frames": int(same.sum()),
               "identical_camera_frames": int(same_cam.sum()),
               "max_matrix_diff": float(dM.max()), "max_focus_diff_m": float(dF.max()),
               "key_identical": bool(same_cam[kc[0]]) if kc.size else None,
               "subj_px_rms": round(float(np.sqrt((mag ** 2).mean())), 3) if mag.size else 0.0,
               "subj_px_peak": round(float(mag.max()), 3) if mag.size else 0.0,
               "vel_px_f_rms": round(float(np.sqrt((vel ** 2).mean())), 3),
               "step_px_max": round(float(vel.max()), 3),
               "hf_px_rms": round(hf_rms, 3),
               "key_px": round(key_px, 4) if key_px is not None else None,
               "rot_deg_peak": round(max(rot_deg(s["M"][i], t["M"][j]) for i, j in zip(ia, ib)), 4)}
        if a.mode == "proof":
            g = {"identical_everywhere": bool(same.all())}
        elif a.mode == "changed":
            g = {"key_identical": bool(row["key_identical"]),                # the focus may lag (a focus puller)
                 "differs_elsewhere": bool((~same_cam[np.arange(len(common)) != (kc[0] if kc.size else -1)]).all())}
        else:
            g = {"key_exact": key_px is not None and key_px <= 1e-3,
                 "rms": row["subj_px_rms"] <= LIM["op_rms_px"], "peak": row["subj_px_peak"] <= LIM["op_peak_px"],
                 "vel": row["vel_px_f_rms"] <= LIM["op_vel_rms_px"], "hf": row["hf_px_rms"] < LIM["op_hf_rms_px"],
                 "step": row["step_px_max"] <= LIM["op_step_px"]}
        row["gates"] = g
        row["pass"] = all(g.values())
        ok_all &= row["pass"]
        rows.append(row)
    for r in rows:
        if "error" in r:
            print(f"{str(r['shot']):>6} {r['error']}")
            continue
        print(f"{str(r['shot']):>6} frames {r['frames']:4d} identical {r['identical_frames']:4d} "
              f"(camera {r['identical_camera_frames']:4d}) "
              f"max dM {r['max_matrix_diff']:.2e} | subj rms {r['subj_px_rms']:.2f} pk {r['subj_px_peak']:.2f} px "
              f"vel {r['vel_px_f_rms']:.3f} hf {r['hf_px_rms']:.3f} step {r['step_px_max']:.3f} KEY {r['key_px']} "
              f"{'PASS' if r['pass'] else 'FAIL ' + ','.join(k for k, v in r['gates'].items() if not v)}")
    return {"mode": a.mode, "shots": rows, "limits": LIM, "pass": bool(ok_all)}


# ---------------------------------------------------------------- cuts
def cmd_cuts(a):
    fps, sensor, shots = load(a.cams)
    W, H = a.width, a.height
    order = sorted(shots, key=lambda s: (s["edit_in_f"] is None, s["edit_in_f"] or 0)) if all(
        s["edit_in_f"] is not None for s in shots) else shots
    rows, ok_all = [], True
    for s, t in zip(order[:-1], order[1:]):
        jo, ji = idx(s, s["out_f"]), idx(t, t["in_f"])
        Mo, Mi = s["M"][jo], t["M"][ji]
        ang = math.degrees(math.acos(float(np.clip(forward(Mo) @ forward(Mi), -1, 1))))
        wo = sensor * s["focus"][jo] / s["lens"][jo]
        wi = sensor * t["focus"][ji] / t["lens"][ji]
        ratio = max(wo, wi) / min(wo, wi)
        similar = ang < LIM["similar_deg"] and ratio < LIM["similar_ratio"]
        rows.append({"cut": f"{s['id']}->{t['id']}", "angle_deg": round(ang, 1), "width_ratio": round(ratio, 2),
                     "similar": similar, "pass": not similar})
        ok_all &= not similar
    for r in rows:
        print(f"{r['cut']:>10} angle {r['angle_deg']:6.1f} deg  width x{r['width_ratio']:5.2f}  "
              f"{'SIMILAR' if r['similar'] else 'ok'}")
    return {"cuts": rows, "limits": LIM, "pass": bool(ok_all)}


# ---------------------------------------------------------------- regate
def cmd_regate(a):
    fps, sensor, shots = load(a.cams)
    rows = []
    for s in shots:
        named = {"in": s["in_f"], "out": s["out_f"], "FIRST": s["first_f"], "LAST": s["last_f"]}
        frames = {int(v) for v in named.values() if v is not None}
        f = int(s["in_f"]) + a.every
        while f < s["out_f"]:
            frames.add(f)
            f += a.every
        frames = sorted(x for x in frames if idx(s, x) is not None)
        rows.append({"shot": s["id"], "named": {k: (int(v) if v is not None else None) for k, v in named.items()},
                     "frames": frames, "edit_frames": [s["edit_f"][idx(s, x)] for x in frames]})
        print(f"{str(s['id']):>6} {len(frames):3d} frames: {frames}")
    return {"every": a.every, "shots": rows, "pass": True}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("shots")
    p.add_argument("cams")
    p.add_argument("--stills", default=None)
    p.add_argument("--exempt", default="", help="ids of shots without the constant-speed gate: inside the ease budget, "
                   "or a named ride on a moving part")
    p.add_argument("--bg-mult", type=float, default=3.0, help="background plane depth as a multiple of the focus distance")
    p = sub.add_parser("compare")
    p.add_argument("a")
    p.add_argument("b")
    p.add_argument("--mode", choices=["operator", "proof", "changed"], default="operator")
    p = sub.add_parser("cuts")
    p.add_argument("cams")
    p = sub.add_parser("regate")
    p.add_argument("cams")
    p.add_argument("--every", type=int, default=12)
    for q in sub.choices.values():
        q.add_argument("--set", default="", help='override limits per film: "op_rms_px=3.2,flow_ceiling_px=9"')
        q.add_argument("--json", default=None)
        q.add_argument("--width", type=int, default=1920)
        q.add_argument("--height", type=int, default=1080)
    a = ap.parse_args()
    for item in a.set.split(","):
        if item.strip():
            k, _, v = item.partition("=")
            if k.strip() not in LIM:
                print(f"unknown limit {k!r}; known: {', '.join(LIM)}", file=sys.stderr)
                return 2
            LIM[k.strip()] = float(v)
    try:
        rep = {"shots": cmd_shots, "compare": cmd_compare, "cuts": cmd_cuts, "regate": cmd_regate}[a.cmd](a)
    except (OSError, KeyError, ValueError) as e:
        print(f"bad input: {e!r}", file=sys.stderr)
        return 2
    if a.json:
        with open(a.json, "w") as f:
            json.dump(rep, f, indent=1, default=float)
    return 0 if rep["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
