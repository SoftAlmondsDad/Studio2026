import bpy, bmesh, json, mathutils

OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild\print_prep\inspect_report.json"

report = {"objects": []}
for obj in bpy.context.scene.objects:
    entry = {
        "name": obj.name,
        "type": obj.type,
        "scale": [round(v, 4) for v in obj.scale],
        "dimensions": [round(v, 4) for v in obj.dimensions],
    }
    if obj.type == 'MESH':
        me = obj.data
        entry["verts"] = len(me.vertices)
        entry["faces"] = len(me.polygons)
        bm = bmesh.new()
        bm.from_mesh(me)
        entry["non_manifold_edges"] = sum(1 for e in bm.edges if not e.is_manifold)
        bm.free()
    report["objects"].append(entry)

mins = [float("inf")] * 3
maxs = [float("-inf")] * 3
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        for corner in obj.bound_box:
            wc = obj.matrix_world @ mathutils.Vector(corner)
            for i in range(3):
                mins[i] = min(mins[i], wc[i])
                maxs[i] = max(maxs[i], wc[i])
report["scene_bbox_min"] = [round(v, 4) for v in mins]
report["scene_bbox_max"] = [round(v, 4) for v in maxs]
report["scene_size"] = [round(maxs[i] - mins[i], 4) for i in range(3)]

with open(OUT, "w") as f:
    json.dump(report, f, indent=1)
print("WROTE", OUT)
