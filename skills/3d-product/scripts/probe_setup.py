#!/usr/bin/env python3
"""probe_setup.py - Step 0.5 of the /3d-product pipeline: find out what this setup can do, read-only.

    python3 probe_setup.py [--site ~/.config/3d-product/site.json] [--node ALIAS ...] [--out setup.json]
                           [--deep] [--bench] [--priority realism|speed] [--timeout 25]

Probes the local machine and every render node named in the site config (or with --node, an ssh alias), then writes a
setup profile (JSON) with a recommendation: the render path for finals (Octane or Cycles), where previews and finals
run, one GPU per frame or all GPUs per frame, the finishing host and the preview ladder.

Read-only by design: it never installs, restarts, kills or configures anything, and it writes only --out (plus a
temporary render in the system temp dir with --bench). Remote probes are plain queries over ssh (uname, nvidia-smi,
file listings, tasklist / ps, netstat, `blender --version`). --deep also asks each node's Blender for its Cycles
devices (starts Blender headless with --factory-startup and preference saving off). --bench renders one small
synthetic frame locally (never remotely) to measure the preview device.

Site config (JSON; default ~/.config/3d-product/site.json if it exists; example: site.example.json next to this file):
  {"nodes": [{"name": "node1", "ssh": "node1"}],
   "shares": [{"name": "Render", "local": "/Volumes/Render", "remote": {"node1": "E:/Render"}}],
   "python": "~/venvs/3d-product/bin/python"}
Output schema: see references/site-profile-example.md ("setup.json").
"""
import argparse, base64, json, os, platform, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

TIMEOUT = 25


def run(cmd, timeout=None, stdin=None):
    """run a command, never raise: (returncode, stdout, stderr)"""
    try:
        p = subprocess.run(cmd, input=stdin, capture_output=True, text=True, timeout=timeout or TIMEOUT)
        return p.returncode, p.stdout, p.stderr
    except FileNotFoundError:
        return 127, "", "not found"
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except Exception as e:  # noqa: BLE001
        return 1, "", repr(e)


# ------------------------------------------------------------------ Blender helpers (programs passed base64-encoded)
DEVICES_PY = r"""
import bpy, json
P = bpy.context.preferences
P.use_preferences_save = False
p = P.addons['cycles'].preferences
out = {}
for t in ('OPTIX', 'CUDA', 'HIP', 'METAL', 'ONEAPI'):   # a dynamic enum: its items can't be listed, so try each
    try:
        p.compute_device_type = t
        p.get_devices()
        out[t] = [[d.name, d.type] for d in p.devices if d.type == t]
    except Exception as e:
        out[t] = 'unsupported' if 'not found' in str(e) else 'error: %s' % e
print('@@cycles ' + json.dumps(out))
"""

BENCH_PY = r"""
import bpy, json, time, os, sys
P = bpy.context.preferences
P.use_preferences_save = False
p = P.addons['cycles'].preferences
best = None
for t in ('OPTIX', 'CUDA', 'HIP', 'METAL', 'ONEAPI'):
    try:
        p.compute_device_type = t
        p.get_devices()
        devs = [d for d in p.devices if d.type == t]
        if devs:
            best = t
            for d in p.devices:
                d.use = (d.type == t)
            break
    except Exception:
        pass
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'GPU' if best else 'CPU'
sc.cycles.samples = 128
sc.cycles.use_adaptive_sampling = False
sc.cycles.use_denoising = False
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 640, 360, 100
bpy.ops.mesh.primitive_monkey_add(location=(2.2, 0, 0.5))
m = bpy.context.object
mod = m.modifiers.new('s', 'SUBSURF'); mod.levels = mod.render_levels = 2
mat = bpy.data.materials.new('g'); mat.use_nodes = True
b = mat.node_tree.nodes.get('Principled BSDF'); b.inputs['Roughness'].default_value = 0.15; b.inputs['Metallic'].default_value = 1.0
m.data.materials.append(mat)
bpy.ops.object.light_add(type='AREA', location=(0, -3, 4)); bpy.context.object.data.energy = 800; bpy.context.object.data.size = 1.5
sc.render.filepath = os.path.join(%r, 'bench.png')
t0 = time.time(); bpy.ops.render.render(write_still=True); t1 = time.time()
print('@@bench ' + json.dumps({'backend': best or 'CPU', 'res': [640, 360], 'spp': 128, 'seconds': round(t1 - t0, 2)}))
"""


def b64expr(prog):
    return "import base64;exec(base64.b64decode('%s').decode())" % base64.b64encode(prog.encode()).decode()


def parse_tag(text, tag):
    for line in text.splitlines():
        if line.startswith("@@" + tag + " "):
            try:
                return json.loads(line[len(tag) + 3:])
            except ValueError:
                return line[len(tag) + 3:]
    return None


# ------------------------------------------------------------------ local probes
def local_blender():
    cands = ["/Applications/Blender.app/Contents/MacOS/Blender", shutil.which("blender") or ""]
    cands += sorted(str(p) for p in Path("C:/Program Files/Blender Foundation").glob("Blender*/blender.exe"))
    for c in cands:
        if c and os.path.exists(c):
            rc, out, _ = run([c, "--version"], timeout=30)
            ver = out.splitlines()[0].strip() if rc == 0 and out else None
            return {"path": c, "version": ver}
    return None


def blender_program(path, prog, timeout=90):
    rc, out, err = run([path, "-b", "--factory-startup", "--python-expr", b64expr(prog)], timeout=timeout)
    return out + err


def local_gpus():
    gpus, backend, mem = [], None, None
    sysname = platform.system()
    if sysname == "Darwin":
        rc, out, _ = run(["sysctl", "-n", "hw.memsize"])
        mem = round(int(out.strip()) / 2**30, 1) if rc == 0 and out.strip().isdigit() else None
        rc, out, _ = run(["system_profiler", "SPDisplaysDataType", "-json"], timeout=30)
        try:
            for g in json.loads(out).get("SPDisplaysDataType", []):
                gpus.append({"name": g.get("sppci_model") or g.get("_name"), "cores": g.get("sppci_cores"),
                             "memory_gb": mem, "memory_kind": "unified"})
        except ValueError:
            pass
        backend = "METAL" if gpus else None
    rc, out, _ = run(["nvidia-smi", "--query-gpu=index,name,memory.total,utilization.gpu,pci.bus_id,driver_version,"
                      "power.limit", "--format=csv,noheader,nounits"])
    if rc == 0:
        for line in out.strip().splitlines():
            f = [x.strip() for x in line.split(",")]
            if len(f) >= 7:
                gpus.append({"index": int(f[0]), "name": f[1], "memory_gb": round(float(f[2]) / 1024, 1),
                             "memory_kind": "vram", "util_pct": _num(f[3]), "bus": f[4], "driver": f[5],
                             "power_limit_w": _num(f[6])})
        backend = "OPTIX" if any("RTX" in g["name"] for g in gpus) else ("CUDA" if gpus else backend)
    if sysname == "Linux" and mem is None:
        try:
            kb = int(re.search(r"MemTotal:\s+(\d+)", Path("/proc/meminfo").read_text()).group(1))
            mem = round(kb / 2**20, 1)
        except Exception:  # noqa: BLE001
            pass
    return gpus, backend, mem


def _num(s):
    try:
        return float(s)
    except ValueError:
        return None


def local_octane():
    homes = [Path.home() / "Library/Application Support/Blender", Path.home() / ".config/blender",
             Path(os.environ.get("APPDATA", "/nonexistent")) / "Blender Foundation/Blender"]
    addon = [str(p) for h in homes if h.exists() for p in h.glob("*/scripts/addons/octane")]
    procs = _proc_list()
    return {"addon": addon, "server_running": any("octaneserver" in p.lower() for p in procs),
            "server_exe": [str(p) for p in Path("C:/Program Files").glob("OctaneServer*/OctaneServer.exe")]
            if platform.system() == "Windows" else [], "listening_50051": _listening(50051),
            "licence": "not probed (read-only): check the server's own status"}


def _proc_list():
    if platform.system() == "Windows":
        rc, out, _ = run(["tasklist"])
    else:
        rc, out, _ = run(["ps", "-axo", "comm"])
    return out.splitlines() if rc == 0 else []


def _listening(port):
    rc, out, _ = run(["netstat", "-an"], timeout=15)
    return any(re.search(r"[.:]%d\s" % port, l) and "LISTEN" in l.upper() for l in out.splitlines()) if rc == 0 else None


def local_resolve():
    info = {"installed": False}
    app = Path("/Applications/DaVinci Resolve/DaVinci Resolve.app")
    win = Path("C:/Program Files/Blackmagic Design/DaVinci Resolve/Resolve.exe")
    lin = Path("/opt/resolve/bin/resolve")
    for p in (app, win, lin):
        if p.exists():
            info.update(installed=True, path=str(p))
    if app.exists():
        rc, out, _ = run(["/usr/libexec/PlistBuddy", "-c", "Print :CFBundleShortVersionString", str(app / "Contents/Info.plist")])
        info["version"] = out.strip() if rc == 0 else None
    mod = Path("/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules")
    info["scripting_module"] = str(mod) if mod.exists() else None
    info["running"] = any("resolve" in p.lower() for p in _proc_list())
    info["product"] = None
    if info["running"] and info["scripting_module"]:
        # a read-only query of the running app: the product name tells Studio (scriptable) from the free version
        lib = app / "Contents/Libraries/Fusion/fusionscript.so"
        env = dict(os.environ, RESOLVE_SCRIPT_API=str(mod.parent), RESOLVE_SCRIPT_LIB=str(lib),
                   PYTHONPATH=str(mod))
        prog = ("import DaVinciResolveScript as d; r=d.scriptapp('Resolve'); "
                "print('@@resolve', (r.GetProductName() if r else 'no connection'), '|', (r.GetVersionString() if r else ''))")
        try:
            p = subprocess.run([sys.executable, "-c", prog], capture_output=True, text=True, timeout=20, env=env)
            m = re.search(r"@@resolve (.*)", p.stdout)
            info["product"] = m.group(1).strip() if m else ("query failed: " + p.stderr.strip()[-200:])
        except Exception as e:  # noqa: BLE001
            info["product"] = "query failed: %r" % e
    info["studio"] = (None if not info["product"] else "studio" in info["product"].lower())
    return info


def local_python(site):
    py = os.path.expanduser(site.get("python", "")) or sys.executable
    rc, out, _ = run([py, "-c", "import numpy, OpenEXR; print(numpy.__version__)"])
    return {"python": py, "numpy_openexr": rc == 0, "numpy": out.strip() if rc == 0 else None}


# ------------------------------------------------------------------ remote probes (one bash script over ssh)
REMOTE_SH = r"""
echo "@@uname $(uname -s 2>/dev/null) $(uname -r 2>/dev/null) $(uname -m 2>/dev/null)"
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=index,name,memory.total,utilization.gpu,pci.bus_id,driver_version,power.limit --format=csv,noheader,nounits | sed 's/^/@@gpu /'
fi
AD=$( (command -v cygpath >/dev/null && cygpath -u "$APPDATA") 2>/dev/null || echo "$APPDATA")
for b in "/c/Program Files/Blender Foundation"/Blender*/blender.exe /usr/bin/blender /usr/local/bin/blender /Applications/Blender.app/Contents/MacOS/Blender; do
  [ -f "$b" ] && echo "@@blender $b"
done
for d in "$AD/Blender Foundation/Blender"/*/scripts/addons/octane "$HOME/.config/blender"/*/scripts/addons/octane "$HOME/Library/Application Support/Blender"/*/scripts/addons/octane; do
  [ -d "$d" ] && echo "@@octane_addon $d"
done
for s in "/c/Program Files"/OctaneServer*/OctaneServer.exe; do [ -f "$s" ] && echo "@@octane_server_exe $s"; done
if command -v tasklist >/dev/null 2>&1; then
  tasklist 2>/dev/null | grep -i -E "octaneserver|blender|resolve" | sed 's/^/@@proc /'
  command -v powershell >/dev/null 2>&1 && echo "@@ssh_session $(powershell -NoProfile -Command '(Get-Process -Id $PID).SessionId' 2>/dev/null | tr -d '\r')"
else
  ps -axo comm 2>/dev/null | grep -i -E "octaneserver|blender|resolve" | sed 's/^/@@proc /'
fi
netstat -an 2>/dev/null | grep -E "[:.]50051 " | grep -i listen | head -1 | sed 's/^/@@listen50051 /'
for r in "/c/Program Files/Blackmagic Design/DaVinci Resolve/Resolve.exe" /opt/resolve/bin/resolve "/Applications/DaVinci Resolve/DaVinci Resolve.app"; do
  [ -e "$r" ] && echo "@@resolve $r"
done
"""


def probe_node(alias, deep=False):
    t0 = time.time()
    node = {"name": alias, "ssh": alias, "reachable": False}
    rc, out, err = run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=6", alias, "bash", "-s"], stdin=REMOTE_SH,
                       timeout=60)
    if rc != 0 and "@@uname" not in out:
        node["error"] = (err or out).strip()[-300:]
        return node
    node["reachable"] = True
    lines = out.splitlines()
    val = lambda tag: [l[len(tag) + 3:].strip() for l in lines if l.startswith("@@" + tag + " ")]  # noqa: E731
    uname = (val("uname") or [""])[0]
    node["os"] = uname
    node["windows"] = bool(re.search(r"MINGW|MSYS|CYGWIN|Windows", uname, re.I))
    gpus = []
    for g in val("gpu"):
        f = [x.strip() for x in g.split(",")]
        if len(f) >= 7:
            gpus.append({"index": int(f[0]), "name": f[1], "memory_gb": round(float(f[2]) / 1024, 1),
                         "memory_kind": "vram", "util_pct": _num(f[3]), "bus": f[4], "driver": f[5],
                         "power_limit_w": _num(f[6])})
    node["gpus"] = gpus
    node["backend"] = "OPTIX" if any("RTX" in g["name"] for g in gpus) else ("CUDA" if gpus else None)
    bl = val("blender")
    node["blender"] = {"path": bl[-1]} if bl else None
    if bl:
        rc2, o2, _ = run(["ssh", "-o", "BatchMode=yes", alias, "bash", "-s"], stdin='"%s" --version | head -1\n' % bl[-1],
                         timeout=60)
        node["blender"]["version"] = o2.strip().splitlines()[0] if rc2 == 0 and o2.strip() else None
        if deep:
            prog = b64expr(DEVICES_PY)
            rc3, o3, _ = run(["ssh", "-o", "BatchMode=yes", alias, "bash", "-s"],
                             stdin='"%s" -b --factory-startup --python-expr "%s" 2>&1 | grep "@@cycles"\n' % (bl[-1], prog),
                             timeout=120)
            node["blender"]["cycles_devices"] = parse_tag(o3, "cycles")
    procs = val("proc")
    srv = [p for p in procs if "octaneserver" in p.lower()]
    node["octane"] = {"addon": val("octane_addon"), "server_exe": val("octane_server_exe"),
                      "server_running": bool(srv), "server_process": srv[:1],
                      "listening_50051": bool(val("listen50051")),
                      "licence": "not probed (read-only): check the server's own status"}
    sess = (val("ssh_session") or [None])[0]
    node["ssh_session_id"] = int(sess) if sess and sess.isdigit() else None
    srv_console = any(re.search(r"\bConsole\b", p) for p in srv)
    node["octane"]["needs_interactive_session"] = bool(node["windows"] and srv_console and node["ssh_session_id"] == 0)
    node["resolve"] = {"installed": bool(val("resolve")), "path": (val("resolve") or [None])[0],
                       "running": any("resolve" in p.lower() for p in procs)}
    node["probe_s"] = round(time.time() - t0, 1)
    return node


# ------------------------------------------------------------------ shares and links
def ssh_host(alias):
    rc, out, _ = run(["ssh", "-G", alias], timeout=15)
    for l in out.splitlines():
        if l.startswith("hostname "):
            return l.split()[1]
    return None


def link_to(host):
    if not host:
        return None
    if platform.system() == "Darwin":
        rc, out, _ = run(["route", "-n", "get", host], timeout=10)
        m = re.search(r"interface:\s+(\S+)", out)
        if not m:
            return None
        iface = m.group(1)
        rc, out, _ = run(["ifconfig", iface], timeout=10)
        media = re.search(r"media:\s+(.*)", out)
        return {"host": host, "interface": iface, "media": media.group(1).strip() if media else None}
    if platform.system() == "Linux":
        rc, out, _ = run(["ip", "route", "get", host], timeout=10)
        m = re.search(r"dev\s+(\S+)", out)
        if m:
            sp = Path("/sys/class/net/%s/speed" % m.group(1))
            return {"host": host, "interface": m.group(1), "speed_mbps": sp.read_text().strip() if sp.exists() else None}
    return {"host": host}


def probe_shares(site):
    res = []
    for s in site.get("shares", []):
        loc = os.path.expanduser(s.get("local", ""))
        e = {"name": s.get("name"), "local": loc, "remote": s.get("remote", {}), "mounted": os.path.ismount(loc)}
        if os.path.exists(loc):
            try:
                du = shutil.disk_usage(loc)
                e["free_tb"] = round(du.free / 1e12, 2)
            except OSError:
                pass
            rc, out, _ = run(["mount"], timeout=10)
            line = next((l for l in out.splitlines() if (" on %s " % loc) in l), None)
            e["mount"] = line
        res.append(e)
    return res


# ------------------------------------------------------------------ recommendation
def gpu_score(n):
    s = 0.0
    for g in n.get("gpus", []):
        if g.get("memory_kind") == "vram":
            s += 10 + g.get("memory_gb", 0) / 4
        else:
            s += 2  # an integrated / unified-memory GPU: fine for previews, slow for finals
    return s


def recommend(local, nodes, shares, priority):
    everyone = [local] + [n for n in nodes if n.get("reachable")]
    cyc = [n for n in everyone if n.get("blender")]
    octa = [n for n in everyone if n.get("octane", {}).get("addon") and n["octane"].get("server_running")]
    best = max(cyc, key=gpu_score) if cyc else None
    rec = {"notes": []}
    if priority == "realism" and octa:
        fin = max(octa, key=gpu_score)
        rec["finals"] = {"path": "octane", "node": fin["name"],
                         "why": "Octane is available: it carries light through glass, smoked acrylic and chrome cleanly "
                                "(measured in a Cycles vs Octane study); Cycles stays for previews"}
        if fin.get("octane", {}).get("needs_interactive_session"):
            rec["notes"].append("%s: OctaneServer runs in the console session and ssh lands in session 0: launch Octane "
                                "jobs through an interactive-session task (one-off schtasks /it), never plain ssh" % fin["name"])
        if not fin.get("octane", {}).get("listening_50051"):
            rec["notes"].append("%s: OctaneServer isn't listening on 50051: start it in the logged-in session first "
                                "(ask the user)" % fin["name"])
    else:
        rec["finals"] = {"path": "cycles", "node": best["name"] if best else None,
                         "why": ("speed priority" if priority == "speed" else "no Octane add-on + running server found")
                         + ": the Cycles production path"}
    fin_node = next((n for n in everyone if n["name"] == rec["finals"]["node"]), None)
    ngpu = len([g for g in (fin_node or {}).get("gpus", []) if g.get("memory_kind") == "vram"])
    if rec["finals"]["path"] == "cycles":
        rec["gpu_per_frame"] = ("one GPU per frame, one Blender per GPU (multi-GPU on one frame was slower on a 16 GB "
                                "scene: per-device upload)" if ngpu > 1 else "all devices on one frame")
    else:
        rec["gpu_per_frame"] = "all GPUs per frame (the Octane server picks its devices); one kept-alive session per node"
    lg = local.get("gpus")
    rec["previews"] = {"node": local["name"] if (local.get("blender") and lg) else (best["name"] if best else None),
                       "engine": "cycles",
                       "ladder": {"composition_motion": "640x360, 16 spp + OIDN (clay or final look)",
                                  "look_light_engine": "960x540, 64-256 spp + OIDN",
                                  "detail_noise": "1:1 border-render crops at full resolution",
                                  "confirm_deliver": "1920x1080 at production settings"}}
    if local.get("bench"):
        rec["previews"]["bench"] = local["bench"]
    rs = [n for n in everyone if n.get("resolve", {}).get("installed")]
    studio_local = local.get("resolve", {}).get("studio")
    rec["finishing"] = {"look_chain": "numpy (the frozen look + mist + grain) on any host with numpy + OpenEXR",
                        "resolve_host": (local["name"] if local.get("resolve", {}).get("installed") else
                                         (rs[0]["name"] if rs else None)),
                        "resolve_scriptable": studio_local}
    if local.get("resolve", {}).get("installed") and studio_local is None:
        rec["notes"].append("Resolve found but not running: Studio (scriptable) can't be confirmed read-only; start it "
                            "and re-probe, or check the About box")
    rec["storage"] = ([{"share": s["name"], "mounted": s.get("mounted")} for s in shares] or
                      "no shared storage configured: copy job files to the render node (scp is CPU-bound on Windows "
                      "OpenSSH, ~130 MB/s)")
    return rec


# ------------------------------------------------------------------ main
def main():
    global TIMEOUT
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--site", default=None)
    ap.add_argument("--node", action="append", default=[])
    ap.add_argument("--out", default=None)
    ap.add_argument("--deep", action="store_true")
    ap.add_argument("--bench", action="store_true")
    ap.add_argument("--priority", choices=["realism", "speed"], default="realism")
    ap.add_argument("--timeout", type=int, default=25)
    a = ap.parse_args()
    TIMEOUT = a.timeout
    site_path = a.site or os.path.expanduser("~/.config/3d-product/site.json")
    site = json.loads(Path(os.path.expanduser(site_path)).read_text()) if os.path.exists(os.path.expanduser(site_path)) else {}
    t0 = time.time()
    gpus, backend, mem = local_gpus()
    local = {"name": "local", "host": platform.node(), "os": "%s %s %s" % (platform.system(), platform.release(),
             platform.machine()), "memory_gb": mem, "gpus": gpus, "backend": backend, "blender": local_blender()}
    if platform.system() == "Darwin":
        rc, out, _ = run(["sw_vers", "-productVersion"])
        local["os"] += " (macOS %s)" % out.strip()
    if local["blender"]:
        o = blender_program(local["blender"]["path"], DEVICES_PY)
        local["blender"]["cycles_devices"] = parse_tag(o, "cycles")
        if a.bench:
            tmp = tempfile.mkdtemp(prefix="probe_bench_")
            o = blender_program(local["blender"]["path"], BENCH_PY % tmp, timeout=300)
            local["bench"] = parse_tag(o, "bench")
    local["octane"] = local_octane()
    local["resolve"] = local_resolve()
    local["python"] = local_python(site)
    local["ffmpeg"] = shutil.which("ffmpeg")
    aliases = [n.get("ssh") or n.get("name") for n in site.get("nodes", [])] + a.node
    nodes = []
    for al in dict.fromkeys(aliases):
        n = probe_node(al, deep=a.deep)
        n["link"] = link_to(ssh_host(al))
        nodes.append(n)
    shares = probe_shares(site)
    prof = {"probed_at": time.strftime("%Y-%m-%d %H:%M:%S"), "probe_s": None, "site_config": site_path if site else None,
            "local": local, "nodes": nodes, "shares": shares}
    prof["recommendation"] = recommend(local, nodes, shares, a.priority)
    prof["probe_s"] = round(time.time() - t0, 1)
    js = json.dumps(prof, indent=1)
    if a.out:
        Path(a.out).write_text(js)
        print("wrote", a.out)
    print(js)


if __name__ == "__main__":
    main()
