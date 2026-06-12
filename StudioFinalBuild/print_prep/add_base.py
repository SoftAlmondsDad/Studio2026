import bpy, bmesh, json, mathutils
from mathutils import Vector

STL_IN = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\Studio2026\towerofpiza_printable.stl"
STL_OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\Studio2026\towerofpiza_printable_with_base.stl"
BLEND_OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild\print_prep\towerofpisa_printable.blend"
REPORT_OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild\print_prep\base_report.json"

report = {}

# ---- 1. verify the STL as a slicer sees it ----
before = set(bpy.context.scene.objects)
bpy.ops.wm.stl_import(filepath=STL_IN)
imported = [o for o in bpy.context.scene.objects if o not in before]
mins = [float("inf")] * 3
maxs = [float("-inf")] * 3
for o in imported:
    for corner in o.bound_box:
        wc = o.matrix_world @ Vector(corner)
        for i in range(3):
            mins[i] = min(mins[i], wc[i])
            maxs[i] = max(maxs[i], wc[i])
report["stl_size_xyz_mm"] = [round(maxs[i] - mins[i], 2) for i in range(3)]
report["stl_min_z"] = round(mins[2], 3)
for o in imported:
    bpy.data.objects.remove(o, do_unlink=True)

# ---- 2. center of mass of the tower (signed tetrahedron method) ----
tower = bpy.context.scene.objects["TowerOfPisa"]
bm = bmesh.new()
bm.from_mesh(tower.data)
bmesh.ops.triangulate(bm, faces=bm.faces)
vol6_total = 0.0
moment = Vector((0.0, 0.0, 0.0))
for f in bm.faces:
    a, b, c = (v.co for v in f.verts)
    vol6 = a.dot(b.cross(c))
    vol6_total += vol6
    moment += (a + b + c) / 4.0 * vol6
com = moment / vol6_total
bm.free()
report["center_of_mass_mm"] = [round(v, 2) for v in com]

# ---- 3. pedestal base: 80mm dia x 5mm cylinder fused under the tower ----
bpy.ops.mesh.primitive_cylinder_add(radius=40, depth=5, vertices=128, location=(0, 0, 2.5))
base = bpy.context.view_layer.objects.active
base.name = "PedestalBase"
# small bevel on the top rim so it looks intentional
bev = base.modifiers.new("Bevel", 'BEVEL')
bev.width = 1.0
bev.segments = 3
bpy.ops.object.modifier_apply(modifier=bev.name)

boo = tower.modifiers.new("UnionBase", 'BOOLEAN')
boo.operation = 'UNION'
boo.object = base
boo.solver = 'EXACT'
bpy.context.view_layer.objects.active = tower
bpy.ops.object.modifier_apply(modifier=boo.name)
bpy.data.objects.remove(base, do_unlink=True)

# ---- 4. verify single island + manifold ----
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

# ---- 5. export ----
for o in bpy.context.scene.objects:
    o.select_set(False)
tower.select_set(True)
bpy.ops.wm.stl_export(filepath=STL_OUT, export_selected_objects=True, ascii_format=False)
bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)

with open(REPORT_OUT, "w") as f:
    json.dump(report, f, indent=1)
print("BASE_REPORT", json.dumps(report))
