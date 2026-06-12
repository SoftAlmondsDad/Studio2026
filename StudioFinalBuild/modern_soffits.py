import bpy
import bmesh
import os
from mathutils import Vector

OUT_DIR = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild"

# rebuild WoodAccents as balcony ceiling soffits
old = bpy.data.objects.get("WoodAccents")
wood_mat = old.data.materials[0]
bpy.data.objects.remove(old, do_unlink=True)

XH, YH = 20.0, 15.0
Z2, Z3, Z4, Z5, Z6 = 4.5, 7.5, 10.5, 13.5, 16.5
S5, S6 = 1.5, 3.0
xc_main = [-15, -10, -5, 0, 5, 10, 15]
yc_main = [-12.5, -7.5, -2.5, 2.5, 7.5, 12.5]
yc_step = [-10, -5, 0, 5, 10]
xc6 = [-12.5, -7.5, -2.5, 2.5, 7.5, 12.5]
yc6 = [-7.5, -2.5, 2.5, 7.5]
floors = [
    (Z2, XH,    YH,    xc_main, yc_main),
    (Z3, XH,    YH,    xc_main, yc_main),
    (Z4, XH,    YH,    xc_main, yc_main),
    (Z5, XH-S5, YH-S5, xc_main, yc_step),
    (Z6, XH-S6, YH-S6, xc6,     yc6),
]
BW, BD, BH, BOFF = 2.4, 1.6, 2.7, -1.1

bm = bmesh.new()

def box(cx, cy, cz, sx, sy, sz):
    ret = bmesh.ops.create_cube(bm, size=1.0)
    vs = ret['verts']
    bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=vs)
    bmesh.ops.translate(bm, vec=(cx, cy, cz), verts=vs)

for zf, xh, yh, xcs, ycs in floors:
    cz = zf + 0.15 + BH - 0.04   # flush against recess ceiling
    for c in xcs:
        box(c+BOFF,  yh-BD/2-0.02, cz, BW-0.04, BD-0.08, 0.08)
        box(c+BOFF, -(yh-BD/2-0.02), cz, BW-0.04, BD-0.08, 0.08)
    for c in ycs:
        box( xh-BD/2-0.02, c+BOFF, cz, BD-0.08, BW-0.04, 0.08)
        box(-(xh-BD/2-0.02), c+BOFF, cz, BD-0.08, BW-0.04, 0.08)

bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
mesh = bpy.data.meshes.new("WoodAccents")
bm.to_mesh(mesh)
bm.free()
o = bpy.data.objects.new("WoodAccents", mesh)
bpy.context.collection.objects.link(o)
o.data.materials.append(wood_mat)

# brighter, warmer wood so it reads at distance
wb = wood_mat.node_tree.nodes["Principled BSDF"]
wb.inputs["Base Color"].default_value = (0.55, 0.33, 0.16, 1)

scene = bpy.context.scene
cam = bpy.data.objects["Camera"]

def shoot(loc, target, path):
    cam.location = loc
    d = Vector(target) - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)

shoot((62, -54, 36), (0, 0, 8),   os.path.join(OUT_DIR, "modern-hero.png"))
shoot((34, -44, 2.0), (0, -8, 11), os.path.join(OUT_DIR, "modern-street.png"))

bpy.ops.wm.save_mainfile()
print("SOFFITS DONE")
