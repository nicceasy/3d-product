#!/usr/bin/env python3
"""macro_focus.py - pick the f-number and focus offset that keep a close-up's named subject sharp (read-only maths).

Why: at macro magnification the depth of field is millimetres (total DoF ~ 2*N*c*(1+m)/m^2), so a subject with
depth (a front edge, a print behind it, a body behind that) goes soft at any "normal" stop. The fix is to stop down
within the diffraction limit and put the focus plane where it splits the subject's depth, not on its nearest point.
This scans f-numbers and focus offsets, adds diffraction (renderers don't), and prints the minimax choice plus the
engine settings. Formulas: fkl-frames.md section 2 and 2b.

Usage:
  python3 macro_focus.py --f 100 --W 60 --depths "front:0,logo:3,back:8" [--N 5.6,8,11,16,22,32]
        [--px 1920] [--sensor 36] [--gate 2.0] [--key front,logo]
  --f       real lens focal length, mm
  --W       frame width at the focus plane, mm (or --m magnification = sensor / W)
  --depths  named subject points as offsets along the view axis from a reference point, mm (+ = farther away)
  --key     the points that must pass the gate (default: all); the others are reported only
Output: per N, the best focus offset (minimax over the key points), the worst combined blur in px, the total DoF,
and the Blender and Octane camera values for the chosen N.

Blur model (thin lens, camera fixed, focus moved): aperture diameter A = f/N; a point at distance d with the focus
plane at S blurs to A*|d - S|/d on the focus plane; in pixels that is divided by the frame width at S over the image
width. Diffraction is a disc of N_eff/24 px at 1920 on a 36 mm frame (N_eff = N(1+m), the Airy MTF at 1080p
Nyquist), scaled by resolution and sensor width; the two add in quadrature. The gate is sqrt(blur^2 + diff^2) <= 2 px.
"""
import argparse
import math
import sys


def parse_depths(s):
    out = []
    for item in s.split(","):
        name, _, v = item.strip().partition(":")
        out.append((name.strip(), float(v)))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--f", type=float, required=True, help="real focal length, mm")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--W", type=float, help="frame width at the focus plane, mm")
    g.add_argument("--m", type=float, help="magnification (sensor width / frame width)")
    ap.add_argument("--depths", required=True)
    ap.add_argument("--key", default=None)
    ap.add_argument("--N", default="2.8,4,5.6,8,11,16,22,32")
    ap.add_argument("--px", type=float, default=1920.0)
    ap.add_argument("--sensor", type=float, default=36.0)
    ap.add_argument("--gate", type=float, default=2.0)
    a = ap.parse_args()

    m = a.m if a.m else a.sensor / a.W
    W = a.W if a.W else a.sensor / m
    s_ref = a.f * (1.0 + 1.0 / m)                     # working distance of the reference plane (entrance pupil), mm
    pts = parse_depths(a.depths)
    key = set(k.strip() for k in a.key.split(",")) if a.key else set(n for n, _ in pts)
    lo = min(v for n, v in pts if n in key)
    hi = max(v for n, v in pts if n in key)
    c_mm = a.gate * a.sensor / a.px                    # acceptable blur on the sensor for the DoF formula

    def blur_px(N, phi, delta):
        A = a.f / N
        S = s_ref + phi                                # focus distance
        d = s_ref + delta
        W_S = W * S / s_ref                            # frame width at the focus plane
        return A * abs(d - S) / d * a.px / W_S

    def diff_px(N):
        return N * (1.0 + m) / 24.0 * (a.px / 1920.0) * (36.0 / a.sensor)

    rows = []
    for N in (float(v) for v in a.N.split(",")):
        best = None
        steps = 400
        for i in range(steps + 1):
            phi = lo + (hi - lo) * i / steps
            worst = max(math.hypot(blur_px(N, phi, dl), diff_px(N)) for n, dl in pts if n in key)
            if best is None or worst < best[1]:
                best = (phi, worst)
        phi, worst = best
        dof_total = 2.0 * N * c_mm * (1.0 + m) / (m * m)
        per = {n: round(math.hypot(blur_px(N, phi, dl), diff_px(N)), 2) for n, dl in pts}
        rows.append({"N": N, "N_eff": round(N * (1 + m), 1), "focus_offset_mm": round(phi, 2),
                     "worst_key_px": round(worst, 2), "diffraction_px": round(diff_px(N), 2),
                     "dof_total_mm": round(dof_total, 2), "per_point_px": per, "pass": worst <= a.gate})

    floor = min(r["worst_key_px"] for r in rows)       # near-ties (within 0.1 px) go to the wider stop:
    best = min((r for r in rows if r["worst_key_px"] <= floor + 0.1), key=lambda r: r["N"])  # less diffraction
    print(f"magnification m = {m:.3f}, working distance {s_ref:.0f} mm, frame width {W:.1f} mm, "
          f"key points {sorted(key)} span {hi - lo:.2f} mm")
    print(f"{'N':>5} {'N_eff':>6} {'focus+mm':>9} {'worst px':>9} {'diffr px':>9} {'DoF mm':>7}  pass  per point px")
    for r in rows:
        print(f"{r['N']:>5g} {r['N_eff']:>6} {r['focus_offset_mm']:>9} {r['worst_key_px']:>9} {r['diffraction_px']:>9} "
              f"{r['dof_total_mm']:>7}  {'yes ' if r['pass'] else 'no  '}  {r['per_point_px']}")
    N = best["N"]
    print(f"\nchoice: f/{N:g} with the focus {best['focus_offset_mm']} mm behind the reference point "
          f"(worst key point {best['worst_key_px']} px; gate {a.gate} px: {'PASS' if best['pass'] else 'FAIL'})")
    if not best["pass"]:
        print("  no f-number passes: reframe a little wider (a bigger W), or name fewer key points; never stop down past "
              "the minimum of the curve above (diffraction then dominates)")
    print(f"  Blender camera: focal {a.f * (1 + m):.1f} mm, f-stop {N * (1 + m):.2f} (keeps the real pupil "
          f"{a.f / N:.2f} mm), focus distance {s_ref + best['focus_offset_mm']:.1f} mm from the pupil")
    print(f"  Octane thin lens: aperture = RADIUS in cm = f/(20 N) = {a.f / (20.0 * N):.4f} "
          f"(a diameter here would halve the depth of field; verify on your add-on version)")
    return 0 if best["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
