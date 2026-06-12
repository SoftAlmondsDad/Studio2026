import bpy, bmesh, json
from mathutils import Vector

STL_OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\Studio2026\towerofpiza_printable_with_base.stl"
BLEND_OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild\print_prep\towerofpisa_printable.blend"
REPORT_OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild\print_prep\thicken_report.json"

Z_LO, Z_HI = 143.2, 151.0   # region the slicer flagged (railing/flagpole zone)
FATTEN = 0.35               # mm pushed outward along normals on each side
VOXEL = 0.3                 # final remesh voxel size, mm

report = {}
tower = bpy.context.scene.objects["TowerOfPisa"]
bpy.context.view_layer.objects.active = tower

def thickness_stats(obj, zlo, zhi, samples=400):
    """ray-cast inward from surface verts to estimate local wall thickness"""
    me = obj.data
    verts = [v for v in me.vertices if zlo <= v.co.z <= zhi]
    step = max(1, len(verts) // samples)
    vals = []
    for v in verts[::step]:
        origin = v.co - v.normal * 0.01
        hit, loc, nrm, idx = obj.ray_cast(origin, -v.normal, distance=20.0)
        if hit:
            vals.append((loc - v.co).length)
    if not vals:
        return None
    vals.sort()
    return {
        "samples": len(vals),
        "min_mm": round(vals[0], 3),
        "median_mm": round(vals[len(vals) // 2], 3),
    }

report["thickness_before"] = thickness_stats(tower, Z_LO, Z_HI)

# ---- fatten the flagged region along vertex normals ----
bm = bmesh.new()
bm.from_mesh(tower.data)
bm.normal_update()
moved = 0
for v in bm.verts:
    if v.co.z >= Z_LO:
        v.co += v.normal * FATTEN
        moved += 1
bm.to_mesh(tower.data)
bm.free()
tower.data.update()
report["verts_fattened"] = moved

# ---- voxel remesh to clean self-intersections and re-union ----
remesh = tower.modifiers.new("Remesh", 'REMESH')
remesh.mode = 'VOXEL'
remesh.voxel_size = VOXEL
bpy.ops.object.modifier_apply(modifier=remesh.name)

# ---- re-flatten the base at z=0 ----
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(tower.data)
geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
res = bmesh.ops.bisect_plane(
    bm, geom=geom, plane_co=(0, 0, 0.05), plane_no=(0, 0, 1),
    clear_inner=True)
cut_edges = [e for e in res['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]
if cut_edges:
    bmesh.ops.holes_fill(bm, edges=cut_edges)
bmesh.update_edit_mesh(tower.data)
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

# drop so base sits at z=0
mins_z = min((tower.matrix_world @ Vector(c)).z for c in tower.bound_box)
tower.location.z -= mins_z
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

report["thickness_after"] = thickness_stats(tower, Z_LO, Z_HI)

# ---- verify ----
bm = bmesh.new()
bm.from_mesh(tower.data)
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
report["faces"] = len(bm.faces)
bm.free()

mins = [float("inf")] * 3
maxs = [float("-inf")] * 3
for corner in tower.bound_box:
    wc = tower.matrix_world @ Vector(corner)
    for i in range(3):
        mins[i] = min(mins[i], wc[i])
        maxs[i] = max(maxs[i], wc[i])
report["final_size_mm"] = [round(maxs[i] - mins[i], 2) for i in range(3)]
report["base_z"] = round(mins[2], 4)

# ---- export ----
for o in bpy.context.scene.objects:
    o.select_set(False)
tower.select_set(True)
bpy.ops.wm.stl_export(filepath=STL_OUT, export_selected_objects=True, ascii_format=False)
bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)

with open(REPORT_OUT, "w") as f:
    json.dump(report, f, indent=1)
print("THICKEN_REPORT", json.dumps(report))
