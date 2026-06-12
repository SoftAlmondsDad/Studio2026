import bpy, bmesh, json, sys

FBX = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\Studio2026\towerofpiza.fbx"
BLEND_OUT = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild\print_prep\towerofpisa_imported.blend"

bpy.ops.wm.read_factory_settings(use_empty=True)

# Import FBX (operator name differs across versions)
try:
    bpy.ops.import_scene.fbx(filepath=FBX)
except AttributeError:
    bpy.ops.wm.fbx_import(filepath=FBX)

report = {"objects": []}
depsgraph = bpy.context.evaluated_depsgraph_get()

for obj in bpy.context.scene.objects:
    entry = {
        "name": obj.name,
        "type": obj.type,
        "location": [round(v, 4) for v in obj.location],
        "scale": [round(v, 4) for v in obj.scale],
        "dimensions": [round(v, 4) for v in obj.dimensions],
    }
    if obj.type == 'MESH':
        me = obj.data
        entry["verts"] = len(me.vertices)
        entry["faces"] = len(me.polygons)
        bm = bmesh.new()
        bm.from_mesh(me)
        non_manifold_edges = sum(1 for e in bm.edges if not e.is_manifold)
        boundary_edges = sum(1 for e in bm.edges if e.is_boundary)
        loose_verts = sum(1 for v in bm.verts if not v.link_edges)
        entry["non_manifold_edges"] = non_manifold_edges
        entry["boundary_edges"] = boundary_edges
        entry["loose_verts"] = loose_verts
        bm.free()
    report["objects"].append(entry)

# overall scene bounding box of mesh objects (world space)
import mathutils
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
report["unit_system"] = bpy.context.scene.unit_settings.system
report["unit_scale"] = bpy.context.scene.unit_settings.scale_length

bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
print("REPORT_JSON_START")
print(json.dumps(report, indent=1))
print("REPORT_JSON_END")
