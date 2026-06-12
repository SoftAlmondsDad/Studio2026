import bpy, bmesh, json

OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild\print_prep\island_report.json"

tower = bpy.context.scene.objects["TowerOfPisa"]
bm = bmesh.new()
bm.from_mesh(tower.data)
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()

# find connected components via flood fill over verts
visited = [False] * len(bm.verts)
islands = []
for seed in range(len(bm.verts)):
    if visited[seed]:
        continue
    stack = [bm.verts[seed]]
    visited[seed] = True
    comp_verts = []
    while stack:
        v = stack.pop()
        comp_verts.append(v)
        for e in v.link_edges:
            o = e.other_vert(v)
            if not visited[o.index]:
                visited[o.index] = True
                stack.append(o)
    islands.append(comp_verts)

report = {"island_count": len(islands), "islands": []}
for comp in islands:
    xs = [v.co.x for v in comp]
    ys = [v.co.y for v in comp]
    zs = [v.co.z for v in comp]
    report["islands"].append({
        "verts": len(comp),
        "bbox_min": [round(min(xs), 2), round(min(ys), 2), round(min(zs), 2)],
        "bbox_max": [round(max(xs), 2), round(max(ys), 2), round(max(zs), 2)],
    })
report["islands"].sort(key=lambda i: -i["verts"])
report["non_manifold_edges"] = sum(1 for e in bm.edges if not e.is_manifold)
report["total_verts"] = len(bm.verts)
bm.free()

with open(OUT, "w") as f:
    json.dump(report, f, indent=1)
print("ISLANDS", report["island_count"], "NONMANIFOLD", report["non_manifold_edges"])
