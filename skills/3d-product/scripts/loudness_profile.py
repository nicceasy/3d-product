#!/usr/bin/env python3
"""loudness_profile.py - check a film mix's loudness architecture (ITU-R BS.1770 / EBU R128 style), read-only.

Why: a film's sound is judged by how its loudness moves, not only by its integrated level. A mix can hit -16 LUFS-I and
still jump 20 LU between a quiet bed and a song, or fall into a hole at a quiet beat. This prints the numbers the
sound gates use (sound-design.md, "Loudness architecture") and draws the short-term curve with the film's marks.

Measures:
  integrated loudness (gated, LUFS-I), true peak (4x oversampled, dBTP), loudness range (EBU 3342 style, LU),
  short-term (3 s) and momentary (0.4 s) loudness at 10 Hz, each time-stamped at its window's centre,
  inside a body window: the short-term range (max - min, LU) and its p5-p95 spread,
  the largest change of short-term loudness over 1 s (LU/s), overall and around each mark,
  for each quiet range: its dip below the median of the 5 s on either side (a gentle dip, not a hole).

Usage:
  python3 loudness_profile.py mix.wav [--window 6,55] [--marks "12.0:music in,31.5:music out,58.0:end card"]
        [--quiet 36-38] [--target-i -16] [--tp-max -1.0] [--st-range 6.5] [--max-step 3.5] [--dip-max 4]
        [--json report.json] [--png profile.png]
Exit code: 0 when every gate passes, 1 when any fails, 2 on a read error.

Requires numpy and scipy; soundfile and matplotlib are optional (WAV via scipy otherwise; no PNG without matplotlib).
Defaults are rules of thumb from a calm product film ("avoid big changes in volume"); set your own per film.
"""
import argparse
import json
import math
import sys

import numpy as np

try:
    from scipy.signal import lfilter, resample_poly
except ImportError:  # pragma: no cover
    sys.exit("loudness_profile.py needs scipy (pip install scipy)")


# ---------------------------------------------------------------- audio in
def read_audio(path):
    """float64 array (samples, channels) in [-1, 1] and the sample rate."""
    try:
        import soundfile as sf
        x, fs = sf.read(path, dtype="float64", always_2d=True)
        return x, fs
    except ImportError:
        pass
    from scipy.io import wavfile
    fs, x = wavfile.read(path)
    if x.dtype.kind == "i":
        x = x.astype(np.float64) / float(np.iinfo(x.dtype).max + 1)
    elif x.dtype.kind == "u":
        x = (x.astype(np.float64) - 128.0) / 128.0
    else:
        x = x.astype(np.float64)
    if x.ndim == 1:
        x = x[:, None]
    return x, fs


# ---------------------------------------------------------------- BS.1770 K-weighting (any sample rate)
def k_weight(x, fs):
    """Stage 1 high shelf (+4 dB, ~1.68 kHz) then stage 2 RLB high-pass (~38 Hz), designed for fs."""
    def shelf(fc, gain_db, q):
        a = 10 ** (gain_db / 40.0)
        w0 = 2 * math.pi * fc / fs
        al = math.sin(w0) / (2 * q)
        c = math.cos(w0)
        b = [a * ((a + 1) + (a - 1) * c + 2 * math.sqrt(a) * al),
             -2 * a * ((a - 1) + (a + 1) * c),
             a * ((a + 1) + (a - 1) * c - 2 * math.sqrt(a) * al)]
        d = [(a + 1) - (a - 1) * c + 2 * math.sqrt(a) * al,
             2 * ((a - 1) - (a + 1) * c),
             (a + 1) - (a - 1) * c - 2 * math.sqrt(a) * al]
        return np.array(b) / d[0], np.array(d) / d[0]

    def highpass(fc, q):
        w0 = 2 * math.pi * fc / fs
        al = math.sin(w0) / (2 * q)
        c = math.cos(w0)
        b = [(1 + c) / 2, -(1 + c), (1 + c) / 2]
        d = [1 + al, -2 * c, 1 - al]
        return np.array(b) / d[0], np.array(d) / d[0]

    b1, a1 = shelf(1681.974450955533, 3.999843853973347, 0.7071752369554196)
    b2, a2 = highpass(38.13547087602444, 0.5003270373238773)
    y = lfilter(b1, a1, x, axis=0)
    return lfilter(b2, a2, y, axis=0)


def channel_weights(n):
    # L, R, C = 1.0; surrounds 1.41 (5.1 order L R C LFE Ls Rs: LFE excluded)
    if n == 6:
        return np.array([1.0, 1.0, 1.0, 0.0, 1.41, 1.41])
    return np.ones(n)


def windowed_loudness(z_cum, fs, win_s, hop_s, g, centred=False):
    """Loudness of windows of win_s every hop_s. Times are the window END (like a live meter), or its CENTRE with
    centred=True (offline analysis: a dip or a step then lines up with the picture mark that caused it)."""
    n = z_cum.shape[0] - 1
    win = int(round(win_s * fs))
    hop = int(round(hop_s * fs))
    ends = np.arange(win, n + 1, hop)
    ms = (z_cum[ends] - z_cum[ends - win]) / win          # mean square per channel
    p = (ms * g).sum(axis=1)
    with np.errstate(divide="ignore"):
        lufs = -0.691 + 10 * np.log10(np.maximum(p, 1e-20))
    t = (ends - (win / 2.0 if centred else 0)) / fs
    return t, lufs, p


def integrated(z_cum, fs, g):
    t, l, p = windowed_loudness(z_cum, fs, 0.4, 0.1, g)
    keep = l > -70.0
    if not keep.any():
        return float("-inf")
    rel = -0.691 + 10 * math.log10(p[keep].mean()) - 10.0
    keep2 = keep & (l > rel)
    return -0.691 + 10 * math.log10(p[keep2].mean())


def loudness_range(st):
    s = st[st > -70.0]
    if s.size == 0:
        return 0.0
    p = 10 ** ((s + 0.691) / 10.0)
    rel = -0.691 + 10 * math.log10(p.mean()) - 20.0
    s = s[s > rel]
    if s.size < 2:
        return 0.0
    return float(np.percentile(s, 95) - np.percentile(s, 10))


def true_peak_db(x):
    peak = 0.0
    for ch in range(x.shape[1]):
        up = resample_poly(x[:, ch], 4, 1)
        peak = max(peak, float(np.max(np.abs(up))))
    return 20 * math.log10(max(peak, 1e-12))


# ---------------------------------------------------------------- helpers
def parse_marks(s):
    out = []
    if not s:
        return out
    for item in s.split(","):
        item = item.strip()
        if not item:
            continue
        t, _, label = item.partition(":")
        out.append((float(t), label.strip() or t))
    return out


def parse_ranges(s):
    out = []
    if not s:
        return out
    for item in s.split(","):
        a, _, b = item.strip().partition("-")
        out.append((float(a), float(b)))
    return out


def step_per_s(t, v, hop_s):
    lag = int(round(1.0 / hop_s))
    d = np.full_like(v, np.nan)
    d[lag:] = np.abs(v[lag:] - v[:-lag])
    return d


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("wav")
    ap.add_argument("--window", default=None, help="t0,t1 in s for the range/step gates (default 6 s in, 6 s before the end)")
    ap.add_argument("--marks", default="", help='"t:label,t:label" (cuts, entries, the end card)')
    ap.add_argument("--quiet", default="", help='quiet ranges "t0-t1,t0-t1" that should dip gently, not fall into a hole')
    ap.add_argument("--target-i", type=float, default=-16.0)
    ap.add_argument("--i-tol", type=float, default=0.5)
    ap.add_argument("--tp-max", type=float, default=-1.0)
    ap.add_argument("--st-range", type=float, default=6.5, help="max short-term range in the window, LU (about 6)")
    ap.add_argument("--max-step", type=float, default=3.5, help="max change of short-term loudness over 1 s, LU (about 3)")
    ap.add_argument("--dip-max", type=float, default=4.0, help="max dip of a quiet range below its surroundings, LU")
    ap.add_argument("--json", default=None)
    ap.add_argument("--png", default=None)
    a = ap.parse_args()

    try:
        x, fs = read_audio(a.wav)
    except Exception as e:  # noqa: BLE001
        print(f"cannot read {a.wav}: {e}", file=sys.stderr)
        return 2
    dur = x.shape[0] / fs
    g = channel_weights(x.shape[1])
    y = k_weight(x, fs)
    z_cum = np.vstack([np.zeros((1, y.shape[1])), np.cumsum(y * y, axis=0)])

    hop = 0.1
    t_st, st, _ = windowed_loudness(z_cum, fs, 3.0, hop, g, centred=True)
    t_m, mo, _ = windowed_loudness(z_cum, fs, 0.4, hop, g, centred=True)
    i_lufs = integrated(z_cum, fs, g)
    lra = loudness_range(windowed_loudness(z_cum, fs, 3.0, hop, g)[1])
    tp = true_peak_db(x)

    if a.window:
        w0, w1 = (float(v) for v in a.window.split(","))
    else:
        w0, w1 = 6.0, max(6.0, dur - 6.0)
    inw = (t_st >= w0) & (t_st <= w1) & (st > -70)
    st_w = st[inw]
    st_range = float(st_w.max() - st_w.min()) if st_w.size else 0.0
    st_p5_p95 = float(np.percentile(st_w, 95) - np.percentile(st_w, 5)) if st_w.size else 0.0
    steps = step_per_s(t_st, st, hop)
    sw = steps[inw]
    max_step = float(np.nanmax(sw)) if np.isfinite(sw).any() else 0.0
    max_step_at = float(t_st[inw][int(np.nanargmax(sw))]) if np.isfinite(sw).any() else None

    marks = parse_marks(a.marks)
    mark_rows = []
    for tm, label in marks:
        near = (t_st >= tm - 1.5) & (t_st <= tm + 1.5)
        s_near = steps[near]
        mark_rows.append({"t": tm, "label": label,
                          "st_step_max_LU_per_s": round(float(np.nanmax(s_near)), 2) if np.isfinite(s_near).any() else None,
                          "st_at": round(float(np.interp(tm, t_st, st)), 1)})

    dips = []
    for q0, q1 in parse_ranges(a.quiet):
        inside = (t_st >= q0) & (t_st <= q1) & (st > -70)
        around = (((t_st >= q0 - 5) & (t_st < q0)) | ((t_st > q1) & (t_st <= q1 + 5))) & (st > -70)
        if inside.any() and around.any():
            dip = float(np.median(st[around]) - np.median(st[inside]))
            dips.append({"range": [q0, q1], "dip_LU": round(dip, 2), "pass": dip <= a.dip_max})

    gates = {
        "integrated": abs(i_lufs - a.target_i) <= a.i_tol,
        "true_peak": tp <= a.tp_max,
        "st_range": st_range <= a.st_range,
        "max_step": max_step <= a.max_step,
        "dips": all(d["pass"] for d in dips),
    }
    rep = {
        "file": a.wav, "fs": fs, "channels": int(x.shape[1]), "duration_s": round(dur, 3),
        "integrated_LUFS": round(i_lufs, 2), "true_peak_dBTP": round(tp, 2), "LRA_LU": round(lra, 2),
        "window_s": [w0, w1], "st_max": round(float(st_w.max()), 2) if st_w.size else None,
        "st_min": round(float(st_w.min()), 2) if st_w.size else None,
        "st_range_LU": round(st_range, 2), "st_p5_p95_LU": round(st_p5_p95, 2),
        "st_max_step_LU_per_s": round(max_step, 2), "st_max_step_at_s": max_step_at,
        "marks": mark_rows, "quiet_dips": dips,
        "limits": {"target_i": a.target_i, "i_tol": a.i_tol, "tp_max": a.tp_max, "st_range": a.st_range,
                   "max_step": a.max_step, "dip_max": a.dip_max},
        "gates": gates, "pass": all(gates.values()),
    }
    txt = json.dumps(rep, indent=1)
    print(txt)
    if a.json:
        with open(a.json, "w") as f:
            f.write(txt)

    if a.png:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib not available: no PNG", file=sys.stderr)
        else:
            fig, ax = plt.subplots(figsize=(14, 4.5), dpi=110)
            ax.plot(t_m, mo, color="0.75", lw=0.6, label="momentary (0.4 s)")
            ax.plot(t_st, st, color="tab:blue", lw=1.6, label="short-term (3 s)")
            ax.axvspan(w0, w1, color="tab:green", alpha=0.05, label="gate window")
            if st_w.size:
                ax.axhline(st_w.max(), color="tab:green", lw=0.6, ls=":")
                ax.axhline(st_w.max() - a.st_range, color="tab:red", lw=0.6, ls=":",
                           label=f"range limit {a.st_range:g} LU")
            for q0, q1 in parse_ranges(a.quiet):
                ax.axvspan(q0, q1, color="tab:orange", alpha=0.15)
            for tm, label in marks:
                ax.axvline(tm, color="0.3", lw=0.6)
                ax.text(tm, (st_w.max() + 3) if st_w.size else -10, label, rotation=90, va="bottom", ha="right",
                        fontsize=7)
            ax.set_ylim(max(-60, (st_w.min() - 12) if st_w.size else -60), (st_w.max() + 9) if st_w.size else 0)
            ax.set_xlim(0, dur)
            ax.set_xlabel("film time (s)")
            ax.set_ylabel("LUFS")
            ax.set_title(f"{a.wav.split('/')[-1]}  I {i_lufs:.1f} LUFS  TP {tp:.1f} dBTP  "
                         f"ST range {st_range:.1f} LU  max step {max_step:.1f} LU/s  "
                         f"{'PASS' if rep['pass'] else 'FAIL'}", fontsize=9)
            ax.legend(loc="lower left", fontsize=7)
            ax.grid(alpha=0.2)
            fig.tight_layout()
            fig.savefig(a.png)
    return 0 if rep["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
