import bpy, bmesh, json, math, mathutils

BLEND_OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild\print_prep\towerofpisa_printable.blend"
STL_OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\Studio2026\towerofpiza_printable.stl"
REPORT_OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild\print_prep\final_report.json"
TARGET_HEIGHT_MM = 150.0

scene = bpy.context.scene

# 1. Remove non-printable objects: camera, flat ground plane, flat disc
for name in ("Camera", "Plane.001", "Circle"):
    obj = scene.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

meshes = [o for o in scene.objects if o.type == 'MESH']

# 2. Apply all transforms (fixes negative scale), then join
for o in scene.objects:
    o.select_set(False)
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.join()
tower = bpy.context.view_layer.objects.active
tower.name = "TowerOfPisa"

# 3. Clean: merge close verts, fill holes, recalc normals
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles(threshold=0.0005)
bpy.ops.mesh.fill_holes(sides=0)
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

# 4. Voxel remesh into a single watertight solid.
# Tower is ~24 scene units tall -> ~150mm, so 1u ~ 6.15mm.
# Voxel 0.06u ~ 0.37mm printed feature size.
remesh = tower.modifiers.new("Remesh", 'REMESH')
remesh.mode = 'VOXEL'
remesh.voxel_size = 0.06
bpy.ops.object.modifier_apply(modifier=remesh.name)

# 5. Cut everything below z=0 (buried foundation) for a flat base
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(tower.data)
geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
res = bmesh.ops.bisect_plane(
    bm, geom=geom,
    plane_co=(0, 0, 0.001), plane_no=(0, 0, 1),
    clear_inner=True, use_snap_center=False)
cut_edges = [e for e in res['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]
if cut_edges:
    bmesh.ops.holes_fill(bm, edges=cut_edges)
bmesh.update_edit_mesh(tower.data)
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

# 6. Decimate if very heavy
face_count = len(tower.data.polygons)
if face_count > 1_200_000:
    dec = tower.modifiers.new("Decimate", 'DECIMATE')
    dec.ratio = 1_000_000 / face_count
    bpy.ops.object.modifier_apply(modifier=dec.name)

# 7. Scale so height = TARGET_HEIGHT_MM (1 unit = 1 mm), base at z=0, centered XY
deps = bpy.context.evaluated_depsgraph_get()
mins = [float("inf")] * 3
maxs = [float("-inf")] * 3
for corner in tower.bound_box:
    wc = tower.matrix_world @ mathutils.Vector(corner)
    for i in range(3):
        mins[i] = min(mins[i], wc[i])
        maxs[i] = max(maxs[i], wc[i])
height = maxs[2] - mins[2]
s = TARGET_HEIGHT_MM / height
tower.scale = (s, s, s)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# recompute bbox, move base to z=0 and center XY
mins = [float("inf")] * 3
maxs = [float("-inf")] * 3
for corner in tower.bound_box:
    wc = tower.matrix_world @ mathutils.Vector(corner)
    for i in range(3):
        mins[i] = min(mins[i], wc[i])
        maxs[i] = max(maxs[i], wc[i])
tower.location.x -= (mins[0] + maxs[0]) / 2
tower.location.y -= (mins[1] + maxs[1]) / 2
tower.location.z -= mins[2]
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# 8. Final validation
bm = bmesh.new()
bm.from_mesh(tower.data)
non_manifold = sum(1 for e in bm.edges if not e.is_manifold)
volume_mm3 = bm.calc_volume(signed=True)
bm.free()

mins = [float("inf")] * 3
maxs = [float("-inf")] * 3
for corner in tower.bound_box:
    wc = tower.matrix_world @ mathutils.Vector(corner)
    for i in range(3):
        mins[i] = min(mins[i], wc[i])
        maxs[i] = max(maxs[i], wc[i])

report = {
    "verts": len(tower.data.vertices),
    "faces": len(tower.data.polygons),
    "non_manifold_edges": non_manifold,
    "volume_cm3": round(volume_mm3 / 1000.0, 2),
    "size_mm": [round(maxs[i] - mins[i], 2) for i in range(3)],
    "base_z": round(mins[2], 4),
}

# 9. Export STL (1 unit = 1 mm)
scene.unit_settings.system = 'METRIC'
scene.unit_settings.length_unit = 'MILLIMETERS'
scene.unit_settings.scale_length = 0.001
for o in scene.objects:
    o.select_set(False)
tower.select_set(True)
bpy.ops.wm.stl_export(filepath=STL_OUT, export_selected_objects=True, ascii_format=False)

bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
with open(REPORT_OUT, "w") as f:
    json.dump(report, f, indent=1)
print("FINAL_REPORT", json.dumps(report))
