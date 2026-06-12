import bpy
import bmesh
import math
import os
from mathutils import Vector

OUT_DIR = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild"
col = bpy.context.collection
bld = bpy.data.objects["ApartmentBuilding"]

# ---------------- layout (must match build) ----------------
XH, YH = 20.0, 15.0
CXH, CYH = 10.0, 7.0
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
BOFF, WOFF = -1.15, 1.25
WW, WSILLH = 1.2, 0.9
ns_c = [-16.5, -11, -5.5, 0, 5.5, 11, 16.5]
ew_c = [-11.5, -6.5, 6.5, 11.5]
TX = 13.5

# ---------------- quoins: concrete corner blocks ----------------
course_z = [(4.3, 4.8), (7.3, 7.7), (10.3, 10.7)]
quoin_boxes = []
bm = bmesh.new()

def bm_box(b, cx, cy, cz, sx, sy, sz):
    ret = bmesh.ops.create_cube(b, size=1.0)
    vs = ret['verts']
    bmesh.ops.scale(b, vec=(sx, sy, sz), verts=vs)
    bmesh.ops.translate(b, vec=(cx, cy, cz), verts=vs)

for sx_ in (1, -1):
    for sy_ in (1, -1):
        for k in range(16):
            z0 = 0.3 + 0.78 * k
            z1 = z0 + 0.7
            if z1 > 13.4:
                continue
            if any(z0 < b and z1 > a for a, b in course_z):
                continue
            if k % 2 == 0:
                lx, ly = 1.4, 0.7
            else:
                lx, ly = 0.7, 1.4
            cx = sx_ * (XH + 0.12 - lx/2)
            cy = sy_ * (YH + 0.12 - ly/2)
            bm_box(bm, cx, cy, (z0+z1)/2, lx, ly, 0.7)
            quoin_boxes.append((cx-lx/2-0.03, cx+lx/2+0.03,
                                cy-ly/2-0.03, cy+ly/2+0.03,
                                z0-0.03, z1+0.03))

bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
qmesh = bpy.data.meshes.new("Quoins")
bm.to_mesh(qmesh)
bm.free()
qob = bpy.data.objects.new("Quoins", qmesh)
col.objects.link(qob)

mod = bld.modifiers.new("b", 'BOOLEAN')
mod.operation = 'UNION'
mod.solver = 'EXACT'
mod.object = qob
bpy.context.view_layer.objects.active = bld
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(qob, do_unlink=True)

# ---------------- materials ----------------
def simple_mat(name, color, rough, metal=0.0):
    m = bpy.data.materials.get(name)
    if m:
        bpy.data.materials.remove(m)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = color
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m

stone = simple_mat("Limestone", (0.58, 0.54, 0.46, 1), 0.8)
wood = simple_mat("TankWood", (0.30, 0.20, 0.13, 1), 0.85)
steel = simple_mat("SteelDark", (0.055, 0.055, 0.065, 1), 0.55, 0.4)
zinc = simple_mat("ZincRoof", (0.32, 0.34, 0.37, 1), 0.45, 0.7)

mats = bld.data.materials
# slot 0 already ReclaimedBrick
for m in (stone, wood, steel, zinc):
    mats.append(m)
I_STONE, I_WOOD, I_STEEL, I_ZINC = 1, 2, 3, 4

# ---------------- stone zone boxes ----------------
stone_boxes = list(quoin_boxes)
for zf, xh, yh, xcs, ycs in floors:
    cz = zf + WSILLH - 0.08
    for c in xcs:  # exterior sills N/S
        stone_boxes.append((c+WOFF-0.8, c+WOFF+0.8,  yh-0.15,  yh+0.16, cz-0.14, cz+0.14))
        stone_boxes.append((c+WOFF-0.8, c+WOFF+0.8, -yh-0.16, -yh+0.15, cz-0.14, cz+0.14))
    for c in ycs:  # exterior sills E/W
        stone_boxes.append(( xh-0.15,  xh+0.16, c+WOFF-0.8, c+WOFF+0.8, cz-0.14, cz+0.14))
        stone_boxes.append((-xh-0.16, -xh+0.15, c+WOFF-0.8, c+WOFF+0.8, cz-0.14, cz+0.14))
for zf, _, _, _, _ in floors:  # courtyard sills
    cz = zf + 0.72
    for y in [-5, -2.5, 0, 2.5, 5]:
        stone_boxes.append(( CXH-0.16,  CXH+0.15, y-0.85, y+0.85, cz-0.14, cz+0.14))
        stone_boxes.append((-CXH-0.15, -CXH+0.16, y-0.85, y+0.85, cz-0.14, cz+0.14))
    for x in [-7.5, -5, -2.5, 0, 2.5, 5, 7.5]:
        stone_boxes.append((x-0.85, x+0.85,  CYH-0.16,  CYH+0.15, cz-0.14, cz+0.14))
        stone_boxes.append((x-0.85, x+0.85, -CYH-0.15, -CYH+0.16, cz-0.14, cz+0.14))
# keystones + imposts (storefronts)
for c in ns_c:
    stone_boxes.append((c-0.27, c+0.27,  YH-0.25,  YH+0.32, 3.1, 4.0))
    stone_boxes.append((c-0.27, c+0.27, -YH-0.32, -YH+0.25, 3.1, 4.0))
    for s in (-1, 1):
        stone_boxes.append((c+s*1.8-0.27, c+s*1.8+0.27,  YH-0.25,  YH+0.27, 2.3, 2.8))
        stone_boxes.append((c+s*1.8-0.27, c+s*1.8+0.27, -YH-0.27, -YH+0.25, 2.3, 2.8))
for c in ew_c:
    stone_boxes.append(( XH-0.25,  XH+0.32, c-0.27, c+0.27, 3.1, 4.0))
    stone_boxes.append((-XH-0.32, -XH+0.25, c-0.27, c+0.27, 3.1, 4.0))
    for s in (-1, 1):
        stone_boxes.append(( XH-0.25,  XH+0.27, c+s*1.8-0.27, c+s*1.8+0.27, 2.3, 2.8))
        stone_boxes.append((-XH-0.27, -XH+0.25, c+s*1.8-0.27, c+s*1.8+0.27, 2.3, 2.8))
# string courses (visible proud part)
for oxh, oyh, zr0, zr1 in ((XH+0.2, YH+0.2, 4.35, 4.75),
                           (XH+0.1, YH+0.1, 7.35, 7.65),
                           (XH+0.1, YH+0.1, 10.35, 10.65)):
    stone_boxes.append((-oxh-0.05, oxh+0.05,  YH-0.07,  oyh+0.05, zr0, zr1))
    stone_boxes.append((-oxh-0.05, oxh+0.05, -oyh-0.05, -YH+0.07, zr0, zr1))
    stone_boxes.append(( XH-0.07,  oxh+0.05, -oyh-0.05, oyh+0.05, zr0, zr1))
    stone_boxes.append((-oxh-0.05, -XH+0.07, -oyh-0.05, oyh+0.05, zr0, zr1))
# parapet copings (top 0.3 of each parapet, all four rings)
for oxh, oyh, t, ztop in ((XH+0.05, YH+0.05, 0.35, 14.0),
                          (XH-S5+0.05, YH-S5+0.05, 0.35, 17.0),
                          (XH-S6+0.05, YH-S6+0.05, 0.35, 20.0),
                          (CXH+0.35, CYH+0.35, 0.35, 20.0)):
    zr = (ztop-0.3, ztop+0.05)
    stone_boxes.append((-oxh-0.05, oxh+0.05,  oyh-t-0.05,  oyh+0.05) + zr)
    stone_boxes.append((-oxh-0.05, oxh+0.05, -oyh-0.05, -(oyh-t)+0.05) + zr)
    stone_boxes.append(( oxh-t-0.05,  oxh+0.05, -oyh-0.05, oyh+0.05) + zr)
    stone_boxes.append((-oxh-0.05, -(oxh-t)+0.05, -oyh-0.05, oyh+0.05) + zr)

# ---------------- assign materials by face center ----------------
bmm = bmesh.new()
bmm.from_mesh(bld.data)
counts = {"stone": 0, "wood": 0, "steel": 0, "zinc": 0}
for f in bmm.faces:
    c = f.calc_center_median()
    x, y, z = c.x, c.y, c.z
    # water tower region
    if 10.5 < x < 16.5 and -2.5 < y < 2.5 and z > 19.42:
        r = math.hypot(x - TX, y)
        if z > 24.08:
            f.material_index = I_ZINC; counts["zinc"] += 1
        elif (21.55 < z < 21.85 or 22.95 < z < 23.25) and r > 1.72:
            f.material_index = I_STEEL; counts["steel"] += 1
        elif z > 20.93:
            f.material_index = I_WOOD; counts["wood"] += 1
        else:
            f.material_index = I_STEEL; counts["steel"] += 1
        continue
    for (x0, x1, y0, y1, z0, z1) in stone_boxes:
        if x0 <= x <= x1 and y0 <= y <= y1 and z0 <= z <= z1:
            f.material_index = I_STONE; counts["stone"] += 1
            break
nonman = sum(1 for e in bmm.edges if not e.is_manifold)
bmm.to_mesh(bld.data)
bmm.free()
print("ASSIGN", counts, "nonman", nonman)

# ---------------- glazing (render-only) ----------------
gbm = bmesh.new()
dbm = bmesh.new()
for zf, xh, yh, xcs, ycs in floors:
    cz = zf + 1.82
    for c in xcs:
        bm_box(gbm, c+WOFF,  yh-0.20, cz, 1.35, 0.05, 2.0)
        bm_box(gbm, c+WOFF, -(yh-0.20), cz, 1.35, 0.05, 2.0)
        bm_box(dbm, c+WOFF,  yh-0.29, cz, 1.35, 0.04, 2.0)
        bm_box(dbm, c+WOFF, -(yh-0.29), cz, 1.35, 0.04, 2.0)
        # balcony door glass at recess back
        bm_box(gbm, c+BOFF,  yh-1.44, zf+1.35, 2.0, 0.05, 2.3)
        bm_box(gbm, c+BOFF, -(yh-1.44), zf+1.35, 2.0, 0.05, 2.3)
    for c in ycs:
        bm_box(gbm,  xh-0.20, c+WOFF, cz, 0.05, 1.35, 2.0)
        bm_box(gbm, -(xh-0.20), c+WOFF, cz, 0.05, 1.35, 2.0)
        bm_box(dbm,  xh-0.29, c+WOFF, cz, 0.04, 1.35, 2.0)
        bm_box(dbm, -(xh-0.29), c+WOFF, cz, 0.04, 1.35, 2.0)
        bm_box(gbm,  xh-1.44, c+BOFF, zf+1.35, 0.05, 2.0, 2.3)
        bm_box(gbm, -(xh-1.44), c+BOFF, zf+1.35, 0.05, 2.0, 2.3)
for zf, _, _, _, _ in floors:  # courtyard windows
    cz = zf + 1.65
    for y in [-5, -2.5, 0, 2.5, 5]:
        bm_box(gbm,  CXH+0.18, y, cz, 0.05, 1.45, 1.85)
        bm_box(gbm, -(CXH+0.18), y, cz, 0.05, 1.45, 1.85)
        bm_box(dbm,  CXH+0.26, y, cz, 0.04, 1.45, 1.85)
        bm_box(dbm, -(CXH+0.26), y, cz, 0.04, 1.45, 1.85)
    for x in [-7.5, -5, -2.5, 0, 2.5, 5, 7.5]:
        bm_box(gbm, x,  CYH+0.18, cz, 1.45, 0.05, 1.85)
        bm_box(gbm, x, -(CYH+0.18), cz, 1.45, 0.05, 1.85)
        bm_box(dbm, x,  CYH+0.26, cz, 1.45, 0.04, 1.85)
        bm_box(dbm, x, -(CYH+0.26), cz, 1.45, 0.04, 1.85)
for c in ns_c:  # storefront glass
    bm_box(gbm, c,  YH-0.22, 2.05, 3.35, 0.05, 3.5)
    bm_box(gbm, c, -(YH-0.22), 2.05, 3.35, 0.05, 3.5)
    bm_box(dbm, c,  YH-0.31, 2.05, 3.35, 0.04, 3.5)
    bm_box(dbm, c, -(YH-0.31), 2.05, 3.35, 0.04, 3.5)
for c in ew_c:
    bm_box(gbm,  XH-0.22, c, 2.05, 0.05, 3.35, 3.5)
    bm_box(gbm, -(XH-0.22), c, 2.05, 0.05, 3.35, 3.5)
    bm_box(dbm,  XH-0.31, c, 2.05, 0.04, 3.35, 3.5)
    bm_box(dbm, -(XH-0.31), c, 2.05, 0.04, 3.35, 3.5)

def finish(b, name, mat):
    bmesh.ops.recalc_face_normals(b, faces=b.faces)
    me = bpy.data.meshes.new(name)
    b.to_mesh(me)
    b.free()
    o = bpy.data.objects.new(name, me)
    col.objects.link(o)
    o.data.materials.append(mat)
    return o

glass_mat = simple_mat("WindowGlass", (0.14, 0.19, 0.26, 1), 0.06, 0.85)
dark_mat = simple_mat("DarkInterior", (0.02, 0.02, 0.025, 1), 0.9)
finish(gbm, "Glazing", glass_mat)
finish(dbm, "DarkBacking", dark_mat)

# ---------------- fill light so shadow sides aren't black ----------------
if not bpy.data.objects.get("FillSun"):
    fd = bpy.data.lights.new("FillSun", 'SUN')
    fd.energy = 1.4
    fd.color = (0.75, 0.82, 1.0)
    fo = bpy.data.objects.new("FillSun", fd)
    col.objects.link(fo)
    fo.rotation_euler = (math.radians(62), 0, math.radians(-150))

bpy.ops.wm.save_mainfile()

# ---------------- verification stills ----------------
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
print("UPGRADE DONE")
