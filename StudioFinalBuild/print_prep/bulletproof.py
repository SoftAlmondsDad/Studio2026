import bpy, bmesh, json
from mathutils import Vector

STL_OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\Studio2026\towerofpiza_FINAL_PRINT.stl"
BLEND_OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild\print_prep\towerofpisa_bulletproof.blend"
REPORT_OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild\print_prep\bulletproof_report.json"

DILATE = 0.35       # mm outward on every surface -> min feature ~1mm+
VOXEL = 0.45        # coarse, bombproof remesh
TARGET_FACES = 500_000

report = {}
scene = bpy.context.scene
tower = scene.objects["TowerOfPisa"]
bpy.context.view_layer.objects.active = tower
for o in scene.objects:
    o.select_set(False)
tower.select_set(True)

# 1. dilate every surface outward
bm = bmesh.new()
bm.from_mesh(tower.data)
bm.normal_update()
for v in bm.verts:
    v.co += v.normal * DILATE
bm.to_mesh(tower.data)
bm.free()
tower.data.update()

# 2. coarse voxel remesh -> one watertight solid, fuses everything that touches
remesh = tower.modifiers.new("Remesh", 'REMESH')
remesh.mode = 'VOXEL'
remesh.voxel_size = VOXEL
bpy.ops.object.modifier_apply(modifier=remesh.name)

# 3. keep ONLY the largest connected component, delete everything else
bm = bmesh.new()
bm.from_mesh(tower.data)
bm.verts.ensure_lookup_table()
visited = [False] * len(bm.verts)
islands = []
for seed in range(len(bm.verts)):
    if visited[seed]:
        continue
    stack = [bm.verts[seed]]
    visited[seed] = True
    comp = []
    while stack:
        v = stack.pop()
        comp.append(v.index)
        for e in v.link_edges:
            o = e.other_vert(v)
            if not visited[o.index]:
                visited[o.index] = True
                stack.append(o)
    islands.append(comp)
islands.sort(key=len, reverse=True)
report["islands_found"] = len(islands)
report["islands_removed_verts"] = sum(len(c) for c in islands[1:])
if len(islands) > 1:
    doomed = [bm.verts[i] for comp in islands[1:] for i in comp]
    bmesh.ops.delete(bm, geom=doomed, context='VERTS')
bm.to_mesh(tower.data)
bm.free()
tower.data.update()

# 4. flat base: cut at z=0.05 and fill
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(tower.data)
geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
res = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, 0.05),
                             plane_no=(0, 0, 1), clear_inner=True)
cut_edges = [e for e in res['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]
if cut_edges:
    bmesh.ops.holes_fill(bm, edges=cut_edges)
bmesh.update_edit_mesh(tower.data)
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
min_z = min((tower.matrix_world @ Vector(c)).z for c in tower.bound_box)
tower.location.z -= min_z
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# 5. decimate to a sane face count
fc = len(tower.data.polygons)
if fc > TARGET_FACES:
    dec = tower.modifiers.new("Decimate", 'DECIMATE')
    dec.ratio = TARGET_FACES / fc
    bpy.ops.object.modifier_apply(modifier=dec.name)

# 6. layer-by-layer material check: every 1mm slice must contain geometry
bm = bmesh.new()
bm.from_mesh(tower.data)
zs = sorted(v.co.z for v in bm.verts)
zmin, zmax = zs[0], zs[-1]
empty_bands = []
z = zmin + 0.5
while z < zmax - 0.5:
    has = any(True for e in bm.edges
              if min(e.verts[0].co.z, e.verts[1].co.z) <= z <= max(e.verts[0].co.z, e.verts[1].co.z))
    if not has:
        empty_bands.append(round(z, 1))
    z += 1.0
report["empty_layer_bands"] = empty_bands

# 7. final validation
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
report["final_islands"] = n_islands
report["non_manifold_edges"] = sum(1 for e in bm.edges if not e.is_manifold)
report["zero_area_faces"] = sum(1 for f in bm.faces if f.calc_area() < 1e-8)
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
report["size_mm"] = [round(maxs[i] - mins[i], 2) for i in range(3)]
report["base_z"] = round(mins[2], 4)

# 8. export
for o in scene.objects:
    o.select_set(False)
tower.select_set(True)
bpy.ops.wm.stl_export(filepath=STL_OUT, export_selected_objects=True, ascii_format=False)
bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
with open(REPORT_OUT, "w") as f:
    json.dump(report, f, indent=1)
print("BULLETPROOF_REPORT", json.dumps(report))
