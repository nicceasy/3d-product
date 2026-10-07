"""scene_weight.py - how heavy is this Blender scene, and where is the weight?  (read-only; changes nothing)

Run at the END of every 3D stage (modelling, materials, environment, lighting) and before production, so the scene stays
light from the first file instead of being trimmed at the end:

    blender -b scene.blend --python scene_weight.py -- --out weight.json [--budget budget.json] [--top 15] [--card-gb 24]

It reports, from the evaluated scene (modifiers applied, instances counted):
  geometry   triangles in total and per object (instanced copies counted once as data, N times as render load),
             the heaviest objects and their share, live modifiers that multiply geometry (subdivision, booleans, arrays)
  objects    counts by type, render-visible, separate objects (each costs session start/stop time in some renderers)
  materials  materials, distinct shader programs (node-graph signatures), procedural texture nodes, script (OSL) nodes
  images     count, pixels, estimated GPU bytes (8-bit RGBA 4 B/px, float 16 B/px), the largest, those over the cap
  light      lights by type, emissive materials, mesh emitters, volumes (world and object)
  estimate   a rough VRAM need (triangles x bytes per triangle + image bytes) against the card

With --budget it prints PASS / FAIL per line (keys: max_triangles, max_object_triangles, max_object_share, max_objects,
max_image_px, max_image_gb, max_shader_programs, max_procedural_nodes, max_script_nodes, max_mesh_emitters,
max_sampled_mesh_emitters, max_vram_share; example and meanings: scripts/budget.example.json, scene-optimisation.md
section 0). The budget may also carry card_gb (the smallest render card; --card-gb overrides it) and hero_collections:
objects in those collections (nested included), and the images their materials or the world use, are exempt from the
per-object and per-image lines (the product, its prints and labels, the HDRI keep full size). Other keys (time budgets)
are ignored here. Numbers are estimates for trend and triage; the renderer's own memory stats are the final word.
"""
import bpy, json, sys, hashlib, argparse
from collections import Counter, defaultdict

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--out", default="")
ap.add_argument("--budget", default="")
ap.add_argument("--top", type=int, default=15)
ap.add_argument("--card-gb", type=float, default=None, help="card memory in GB (default: the budget's card_gb, else 24)")
ap.add_argument("--bytes-per-tri", type=float, default=185.0, help="GPU bytes per triangle (measured guide: ~0.185 GB per million triangles)")
ap.add_argument("--image-cap", type=int, default=2048, help="flag set textures whose long side exceeds this")
a = ap.parse_args(argv)
B = json.load(open(a.budget)) if a.budget else {}
if a.card_gb is None:
    a.card_gb = float(B.get("card_gb", 24.0))

sc = bpy.context.scene
hero_objs = set()                                                # objects under the budget's hero collections
for cn in B.get("hero_collections", []):
    col = bpy.data.collections.get(cn)
    if col:
        hero_objs |= {o.name for o in col.all_objects}
hero_imgs = set()                                                # images used by hero materials or the world
def _imgs_of(tree):
    return {nd.image.name for nd in tree.nodes
            if nd.bl_idname in ("ShaderNodeTexImage", "ShaderNodeTexEnvironment") and nd.image} if tree else set()
for on in hero_objs:
    for ms in getattr(bpy.data.objects[on], "material_slots", []):
        if ms.material and ms.material.use_nodes:
            hero_imgs |= _imgs_of(ms.material.node_tree)
if "hero_collections" in B and sc.world and sc.world.use_nodes:
    hero_imgs |= _imgs_of(sc.world.node_tree)
dg = bpy.context.evaluated_depsgraph_get()
PROC = {"ShaderNodeTexNoise", "ShaderNodeTexVoronoi", "ShaderNodeTexWave", "ShaderNodeTexMusgrave", "ShaderNodeTexMagic",
        "ShaderNodeTexBrick", "ShaderNodeTexChecker", "ShaderNodeTexGradient", "ShaderNodeTexWhiteNoise", "ShaderNodeTexGabor"}

# ---------------- geometry (evaluated; instances counted)
tri_data = {}
def tris_of(obj_eval):
    key = obj_eval.data.name if obj_eval.data else obj_eval.name
    if key in tri_data:
        return tri_data[key]
    n = 0
    try:
        me = obj_eval.to_mesh()
        me.calc_loop_triangles(); n = len(me.loop_triangles)
        obj_eval.to_mesh_clear()
    except Exception:
        n = 0
    tri_data[key] = n
    return n

per_obj = defaultdict(int); inst_count = Counter(); total_tris = 0
for inst in dg.object_instances:
    ob = inst.object
    if ob.type not in ("MESH", "CURVE", "SURFACE", "META", "FONT"):
        continue
    src = inst.instance_object.original.name if inst.is_instance and inst.instance_object else ob.original.name
    n = tris_of(ob)
    per_obj[src] += n; total_tris += n
    if inst.is_instance:
        inst_count[src] += 1

types = Counter(o.type for o in sc.objects)
heavy = sorted(per_obj.items(), key=lambda kv: -kv[1])[:a.top]
heavy_set = next(((n, t) for n, t in sorted(per_obj.items(), key=lambda kv: -kv[1]) if n not in hero_objs), ("", 0))
mods = Counter()
for o in sc.objects:
    for m in getattr(o, "modifiers", []):
        if m.type == "SUBSURF" and m.render_levels > 0:
            mods[f"SUBSURF render>{m.render_levels - 1}"] += 1
        elif m.type in ("BOOLEAN", "ARRAY", "MULTIRES", "REMESH", "GEOMETRY_NODES", "PARTICLE_SYSTEM", "SCREW", "SOLIDIFY"):
            mods[m.type] += 1
shape_keyed = sum(1 for o in sc.objects if o.type == "MESH" and o.data.shape_keys)
animated = sum(1 for o in sc.objects if o.animation_data and o.animation_data.action)

# ---------------- materials and shaders
mats = [m for m in bpy.data.materials if m.users]
sigs = set(); proc_nodes = 0; script_nodes = 0; undefined = 0
for m in mats:
    if not m.use_nodes or not m.node_tree:
        continue
    names = []
    for nd in m.node_tree.nodes:
        names.append(nd.bl_idname)
        if nd.bl_idname in PROC:
            proc_nodes += 1
        if nd.bl_idname == "ShaderNodeScript" or "OSL" in nd.name:
            script_nodes += 1
        if nd.bl_idname == "NodeUndefined":
            undefined += 1
    links = sorted(f"{l.from_node.bl_idname}.{l.from_socket.identifier}>{l.to_node.bl_idname}.{l.to_socket.identifier}" for l in m.node_tree.links)
    sigs.add(hashlib.md5(("|".join(sorted(names)) + "#" + "|".join(links)).encode()).hexdigest())

# ---------------- images
imgs = []
for im in bpy.data.images:
    if not im.users or im.type not in ("IMAGE", "MULTILAYER"):
        continue
    w, h = im.size[0], im.size[1]
    if w == 0 and im.filepath:                                   # not loaded yet: read the header
        try:
            im.reload(); w, h = im.size[0], im.size[1]
        except Exception:
            pass
    flt = im.is_float or im.filepath.lower().endswith((".exr", ".hdr"))
    imgs.append(dict(name=im.name, w=w, h=h, px=w * h, float=bool(flt), bytes=w * h * (16 if flt else 4), hero=im.name in hero_imgs))
unresolved = [i["name"] for i in imgs if i["px"] == 0]            # path not readable on this host (e.g. a render node's drive)
img_px = sum(i["px"] for i in imgs); img_bytes = sum(i["bytes"] for i in imgs)
over_cap = [i for i in imgs if max(i["w"], i["h"]) > a.image_cap and not i["hero"]]
set_img_px = max([max(i["w"], i["h"]) for i in imgs if not i["hero"]] or [0])   # longest side of any non-hero image

# ---------------- light
lights = Counter(o.data.type for o in sc.objects if o.type == "LIGHT" and not o.hide_render)
emissive = []
for m in mats:
    if not m.use_nodes or not m.node_tree:
        continue
    for nd in m.node_tree.nodes:
        s = None
        if nd.bl_idname == "ShaderNodeEmission":
            s = nd.inputs["Strength"]
        elif nd.bl_idname == "ShaderNodeBsdfPrincipled" and "Emission Strength" in nd.inputs:
            s = nd.inputs["Emission Strength"]
        if s is not None and (s.is_linked or s.default_value > 0):
            emissive.append(m.name); break
mesh_emitters = sum(1 for o in sc.objects if o.type == "MESH" and not o.hide_render and any(ms.material and ms.material.name in emissive for ms in o.material_slots))
def _sampled(m):                                                 # Cycles: Emission Sampling not None (other engines: own setting)
    return getattr(getattr(m, "cycles", None), "emission_sampling", "AUTO") != "NONE"
sampled_emitters = sum(1 for o in sc.objects if o.type == "MESH" and not o.hide_render and any(
    ms.material and ms.material.name in emissive and _sampled(ms.material) for ms in o.material_slots))
volumes = sum(1 for m in mats if m.use_nodes and m.node_tree and any(l.to_socket.name == "Volume" for l in m.node_tree.links))
world_vol = bool(sc.world and sc.world.use_nodes and sc.world.node_tree and any(l.to_socket.name == "Volume" for l in sc.world.node_tree.links))

geo_gb = total_tris * a.bytes_per_tri / 1e9; img_gb = img_bytes / 1e9; vram_gb = geo_gb + img_gb
R = dict(
    file=bpy.data.filepath,
    geometry=dict(triangles=total_tris, unique_mesh_data=len(tri_data), heaviest=[[n, t, round(100 * t / max(total_tris, 1), 1), inst_count.get(n, 0)] for n, t in heavy],
                  over_1M=[n for n, t in per_obj.items() if t > 1_000_000], multiplying_modifiers=dict(mods), shape_keyed=shape_keyed, animated=animated,
                  heaviest_non_hero=[heavy_set[0], heavy_set[1], round(heavy_set[1] / max(total_tris, 1), 3)], hero_objects=len(hero_objs)),
    objects=dict(total=len(sc.objects), by_type=dict(types), render_visible=sum(1 for o in sc.objects if not o.hide_render)),
    materials=dict(used=len(mats), shader_programs=len(sigs), procedural_nodes=proc_nodes, script_nodes=script_nodes, undefined_nodes=undefined),
    images=dict(count=len(imgs), megapixels=round(img_px / 1e6, 1), gpu_gb=round(img_gb, 2),
                largest=[[i["name"], i["w"], i["h"], i["float"]] for i in sorted(imgs, key=lambda i: -i["bytes"])[:a.top]],
                over_cap=len(over_cap), longest_non_hero_px=set_img_px, hero_images=len(hero_imgs), unresolved=len(unresolved)),
    light=dict(lights=dict(lights), emissive_materials=len(emissive), mesh_emitters=mesh_emitters, sampled_mesh_emitters=sampled_emitters, volume_materials=volumes, world_volume=world_vol),
    estimate=dict(geometry_gb=round(geo_gb, 2), images_gb=round(img_gb, 2), vram_gb=round(vram_gb, 2), card_gb=a.card_gb, vram_share=round(vram_gb / a.card_gb, 3)),
)

print("\nSCENE WEIGHT  %s" % (bpy.data.filepath or "(unsaved)"))
g = R["geometry"]; print("  triangles %s  (unique mesh data %d, objects >1M tris: %d)" % (f"{total_tris:,}", g["unique_mesh_data"], len(g["over_1M"])))
for n, t, pct, ic in g["heaviest"][:10]:
    print("    %-48s %12s  %5.1f %%%s" % (n[:48], f"{t:,}", pct, f"  x{ic} instances" if ic else ""))
if hero_objs: print("  heaviest non-hero object: %s  %s tris = %.1f %% of the scene  (%d hero objects exempt)" % (heavy_set[0][:48], f"{heavy_set[1]:,}", 100 * heavy_set[1] / max(total_tris, 1), len(hero_objs)))
if mods: print("  multiplying modifiers:", dict(mods))
o = R["objects"]; print("  objects %d (render-visible %d)  %s" % (o["total"], o["render_visible"], dict(types)))
m = R["materials"]; print("  materials %d, distinct shader programs %d, procedural nodes %d, script/OSL nodes %d" % (m["used"], m["shader_programs"], m["procedural_nodes"], m["script_nodes"]))
i = R["images"]; print("  images %d, %.1f MP, ~%.2f GB on the GPU, %d over %d px%s" % (i["count"], i["megapixels"], i["gpu_gb"], i["over_cap"], a.image_cap, ("  [%d UNRESOLVED: sizes unknown on this host - run where the textures live]" % i["unresolved"]) if i["unresolved"] else ""))
l = R["light"]; print("  lights %s, emissive materials %d, mesh emitters %d (%d in light sampling), volumes %d%s" % (dict(lights), l["emissive_materials"], l["mesh_emitters"], l["sampled_mesh_emitters"], l["volume_materials"], " + world volume" if world_vol else ""))
e = R["estimate"]; print("  VRAM estimate ~%.1f GB (geometry %.1f + images %.1f) = %.0f %% of a %.0f GB card" % (e["vram_gb"], e["geometry_gb"], e["images_gb"], 100 * e["vram_share"], a.card_gb))

if a.budget:
    checks = []
    def chk(key, val):
        if key in B:
            ok = val <= B[key]; checks.append([key, val, B[key], ok]); print("  %-4s %-22s %s <= %s" % ("PASS" if ok else "FAIL", key, val, B[key]))
    chk("max_triangles", total_tris); chk("max_object_triangles", heavy_set[1]); chk("max_objects", len(sc.objects))
    chk("max_object_share", round(heavy_set[1] / max(total_tris, 1), 3))
    chk("max_image_px", set_img_px); chk("max_image_gb", round(img_gb, 2))
    chk("max_shader_programs", len(sigs)); chk("max_procedural_nodes", proc_nodes); chk("max_script_nodes", script_nodes)
    chk("max_mesh_emitters", mesh_emitters); chk("max_sampled_mesh_emitters", sampled_emitters)
    chk("max_vram_share", round(vram_gb / a.card_gb, 3))
    R["budget"] = checks
if a.out:
    json.dump(R, open(a.out, "w"), indent=1); print("  wrote", a.out)
