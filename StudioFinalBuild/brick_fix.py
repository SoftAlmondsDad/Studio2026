import bpy
import bmesh
import os
from mathutils import Vector

OUT_DIR = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild"
bld = bpy.data.objects["ApartmentBuilding"]

def set_mat(name, color, rough, metal):
    b = bpy.data.materials[name].node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = color
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal

set_mat("TankWood",  (0.19, 0.105, 0.055, 1), 0.8, 0.0)
set_mat("SteelDark", (0.025, 0.025, 0.03, 1), 0.7, 0.0)
set_mat("ZincRoof",  (0.15, 0.17, 0.20, 1), 0.5, 0.3)
set_mat("Limestone", (0.52, 0.48, 0.40, 1), 0.8, 0.0)

bpy.data.objects["FillSun"].data.energy = 0.7

# full stone arch surrounds on the storefronts
XH, YH = 20.0, 15.0
ns_c = [-16.5, -11, -5.5, 0, 5.5, 11, 16.5]
ew_c = [-11.5, -6.5, 6.5, 11.5]
I_STONE = 1
boxes = []
for c in ns_c:
    boxes.append((c-2.05, c+2.05,  YH-0.30,  YH+0.35, 0.25, 4.05))
    boxes.append((c-2.05, c+2.05, -YH-0.35, -YH+0.30, 0.25, 4.05))
for c in ew_c:
    boxes.append(( XH-0.30,  XH+0.35, c-2.05, c+2.05, 0.25, 4.05))
    boxes.append((-XH-0.35, -XH+0.30, c-2.05, c+2.05, 0.25, 4.05))

bm = bmesh.new()
bm.from_mesh(bld.data)
n = 0
for f in bm.faces:
    c = f.calc_center_median()
    for (x0, x1, y0, y1, z0, z1) in boxes:
        if x0 <= c.x <= x1 and y0 <= c.y <= y1 and z0 <= c.z <= z1:
            f.material_index = I_STONE
            n += 1
            break
bm.to_mesh(bld.data)
bm.free()
print("ARCH SURROUND FACES", n)

bpy.ops.wm.save_mainfile()

# re-export STL (shell now includes quoins)
bpy.ops.object.select_all(action='DESELECT')
bld.select_set(True)
bpy.context.view_layer.objects.active = bld
bpy.ops.wm.stl_export(filepath=os.path.join(OUT_DIR, "ApartmentBuilding.stl"),
                      export_selected_objects=True)

scene = bpy.context.scene
scene.render.resolution_x = 1600
scene.render.resolution_y = 1000
scene.render.image_settings.file_format = 'PNG'
cam = bpy.data.objects["Camera"]

def shoot(loc, target, path):
    cam.location = loc
    d = Vector(target) - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)

shoot((62, -54, 36), (0, 0, 8), os.path.join(OUT_DIR, "brick-upgraded-hero.png"))
shoot((26, -14, 24), (13.5, 0, 22.5), os.path.join(OUT_DIR, "brick-upgraded-tower.png"))
shoot((33, -31, 5), (17, -13, 5), os.path.join(OUT_DIR, "brick-upgraded-corner.png"))
print("FIX DONE")
