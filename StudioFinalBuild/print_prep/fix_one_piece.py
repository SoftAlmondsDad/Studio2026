import bpy, bmesh, json, mathutils
from mathutils import Vector, kdtree

BLEND_OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild\print_prep\towerofpisa_printable.blend"
STL_OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\Studio2026\towerofpiza_printable.stl"
REPORT_OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild\print_prep\fix_report.json"

DEBRIS_MAX_VERTS = 50
PENETRATION = 2.0  # mm each end of connector embedded into the parts

tower = bpy.context.scene.objects["TowerOfPisa"]
bpy.context.view_layer.objects.active = tower

# ---- find islands ----
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
main = islands[0]
report = {"islands_before": len(islands), "connectors": [], "debris_deleted": 0}

# ---- delete debris islands ----
debris_idx = set()
for comp in islands[1:]:
    if len(comp) <= DEBRIS_MAX_VERTS:
        debris_idx.update(comp)
        report["debris_deleted"] += 1

# ---- closest-pair connectors for real secondary islands ----
main_kd = kdtree.KDTree(len(main))
for i, vi in enumerate(main):
    main_kd.insert(bm.verts[vi].co, vi)
main_kd.balance()

connectors = []  # (midpoint, direction, length, cross_size)
for comp in islands[1:]:
    if len(comp) <= DEBRIS_MAX_VERTS:
        continue
    best = (None, None, float("inf"))
    for vi in comp:
        co = bm.verts[vi].co
        loc, idx, dist = main_kd.find(co)
        if dist < best[2]:
            best = (co.copy(), loc.copy(), dist)
    p_island, p_main, gap = best
    # island thickness to size the strut
    xs = [bm.verts[vi].co for vi in comp]
    bb_min = Vector((min(c.x for c in xs), min(c.y for c in xs), min(c.z for c in xs)))
    bb_max = Vector((max(c.x for c in xs), max(c.y for c in xs), max(c.z for c in xs)))
    min_dim = min(bb_max - bb_min)
    cross = max(1.2, min(6.0, min_dim * 0.9, len(comp) ** 0.5 / 4))
    direction = (p_main - p_island)
    length = direction.length + 2 * PENETRATION
    mid = (p_main + p_island) / 2
    connectors.append((mid, direction.normalized() if direction.length > 1e-6 else Vector((0, 0, 1)), length, cross))
    report["connectors"].append({
        "island_verts": len(comp),
        "gap_mm": round(gap, 3),
        "at": [round(v, 2) for v in mid],
        "cross_mm": round(cross, 2),
    })

# apply debris deletion
if debris_idx:
    del_verts = [bm.verts[i] for i in debris_idx]
    bmesh.ops.delete(bm, geom=del_verts, context='VERTS')
bm.to_mesh(tower.data)
bm.free()
tower.data.update()

# ---- build connector struts and union ----
if connectors:
    strut_objs = []
    for n, (mid, d, length, cross) in enumerate(connectors):
        bpy.ops.mesh.primitive_cube_add(size=1, location=mid)
        cube = bpy.context.view_layer.objects.active
        cube.scale = (cross, cross, length)
        q = Vector((0, 0, 1)).rotation_difference(d)
        cube.rotation_mode = 'QUATERNION'
        cube.rotation_quaternion = q
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        strut_objs.append(cube)
    # join struts into one object
    for o in bpy.context.scene.objects:
        o.select_set(False)
    for o in strut_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = strut_objs[0]
    if len(strut_objs) > 1:
        bpy.ops.object.join()
    struts = bpy.context.view_layer.objects.active
    struts.name = "Connectors"

    boo = tower.modifiers.new("UnionStruts", 'BOOLEAN')
    boo.operation = 'UNION'
    boo.object = struts
    try:
        boo.solver = 'EXACT'
    except TypeError:
        pass
    bpy.context.view_layer.objects.active = tower
    bpy.ops.object.modifier_apply(modifier=boo.name)
    bpy.data.objects.remove(struts, do_unlink=True)

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
report["islands_after"] = n_islands
report["non_manifold_edges"] = sum(1 for e in bm.edges if not e.is_manifold)
report["volume_cm3"] = round(bm.calc_volume(signed=True) / 1000.0, 2)
report["verts"] = len(bm.verts)
report["faces"] = len(bm.faces)
bm.free()

# ---- export ----
for o in bpy.context.scene.objects:
    o.select_set(False)
tower.select_set(True)
bpy.context.view_layer.objects.active = tower
bpy.ops.wm.stl_export(filepath=STL_OUT, export_selected_objects=True, ascii_format=False)
bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)

with open(REPORT_OUT, "w") as f:
    json.dump(report, f, indent=1)
print("FIX_REPORT", json.dumps(report))
