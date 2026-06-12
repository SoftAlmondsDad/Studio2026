import bpy, bmesh, json
from mathutils import Vector

STL_OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\Studio2026\towerofpiza_FAST_PRINT_113mm.stl"
REPORT_OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild\print_prep\fast_report.json"
SCALE = 0.75

report = {}
tower = bpy.context.scene.objects["TowerOfPisa"]
bpy.context.view_layer.objects.active = tower
for o in bpy.context.scene.objects:
    o.select_set(False)
tower.select_set(True)

tower.scale = (SCALE, SCALE, SCALE)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
min_z = min((tower.matrix_world @ Vector(c)).z for c in tower.bound_box)
tower.location.z -= min_z
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# thinnest-feature check in the railing zone (scaled: ~106-113mm)
def thickness_stats(obj, zlo, zhi, samples=400):
    verts = [v for v in obj.data.vertices if zlo <= v.co.z <= zhi]
    step = max(1, len(verts) // samples)
    vals = []
    for v in verts[::step]:
        origin = v.co - v.normal * 0.01
        hit, loc, nrm, idx = obj.ray_cast(origin, -v.normal, distance=20.0)
        if hit:
            vals.append((loc - v.co).length)
    vals.sort()
    return {"samples": len(vals), "min_mm": round(vals[0], 3),
            "median_mm": round(vals[len(vals) // 2], 3)} if vals else None

report["railing_zone_thickness"] = thickness_stats(tower, 105.0, 113.5)

# empty-layer check at 0.75mm steps
bm = bmesh.new()
bm.from_mesh(tower.data)
zs = sorted(v.co.z for v in bm.verts)
zmin, zmax = zs[0], zs[-1]
empty = []
z = zmin + 0.4
while z < zmax - 0.4:
    if not any(min(e.verts[0].co.z, e.verts[1].co.z) <= z <= max(e.verts[0].co.z, e.verts[1].co.z) for e in bm.edges):
        empty.append(round(z, 1))
    z += 0.75
report["empty_layer_bands"] = empty

# island + manifold check
bm.verts.ensure_lookup_table()
visited = [False] * len(bm.verts)
n_islands = 0
for seed in range(len(bm.verts)):
    if visited[seed]:
        continue
    n_islands += 1
    stack = [bm.verts[seed]]
    visited[seed] = True
    while stack:
        v = stack.pop()
        for e in v.link_edges:
            o = e.other_vert(v)
            if not visited[o.index]:
                visited[o.index] = True
                stack.append(o)
report["islands"] = n_islands
report["non_manifold_edges"] = sum(1 for e in bm.edges if not e.is_manifold)
report["volume_cm3"] = round(bm.calc_volume(signed=True) / 1000.0, 2)
bm.free()

mins = [float("inf")] * 3
maxs = [float("-inf")] * 3
for corner in tower.bound_box:
    wc = tower.matrix_world @ Vector(corner)
    for i in range(3):
        mins[i] = min(mins[i], wc[i])
        maxs[i] = max(maxs[i], wc[i])
report["size_mm"] = [round(maxs[i] - mins[i], 2) for i in range(3)]
report["base_z"] = round(mins[2], 4)

bpy.ops.wm.stl_export(filepath=STL_OUT, export_selected_objects=True, ascii_format=False)
# NOTE: intentionally not saving the blend — keep the 150mm master intact
with open(REPORT_OUT, "w") as f:
    json.dump(report, f, indent=1)
print("FAST_REPORT", json.dumps(report))
