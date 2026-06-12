import bpy, bmesh, json

STL_OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\Studio2026\towerofpiza_printable_with_base.stl"
BLEND_OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild\print_prep\towerofpisa_printable.blend"

tower = bpy.context.scene.objects["TowerOfPisa"]
bpy.context.view_layer.objects.active = tower

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

debris = [i for comp in islands[1:] for i in comp if len(comp) <= 50]
if debris:
    bmesh.ops.delete(bm, geom=[bm.verts[i] for i in debris], context='VERTS')

n_islands = len([c for c in islands if len(c) > 50])
non_manifold = sum(1 for e in bm.edges if not e.is_manifold)
vol = bm.calc_volume(signed=True) / 1000.0
bm.to_mesh(tower.data)
bm.free()
tower.data.update()

for o in bpy.context.scene.objects:
    o.select_set(False)
tower.select_set(True)
bpy.ops.wm.stl_export(filepath=STL_OUT, export_selected_objects=True, ascii_format=False)
bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
print("DEBRIS_REPORT", json.dumps({
    "debris_removed": len(islands) - n_islands,
    "islands_after": n_islands,
    "non_manifold_edges": non_manifold,
    "volume_cm3": round(vol, 2),
}))
