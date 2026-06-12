import bpy
import bmesh
import math
import os

OUT_DIR = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild"

# ---------- scene reset ----------
cube = bpy.data.objects.get("Cube")
if cube:
    bpy.data.objects.remove(cube, do_unlink=True)
col = bpy.context.collection

# ---------- helpers ----------
def new_obj_from_bm(bm, name):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    o = bpy.data.objects.new(name, mesh)
    col.objects.link(o)
    return o

def bm_box(bm, cx, cy, cz, sx, sy, sz):
    ret = bmesh.ops.create_cube(bm, size=1.0)
    vs = ret['verts']
    bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=vs)
    bmesh.ops.translate(bm, vec=(cx, cy, cz), verts=vs)

def bm_ring(bm, oxh, oyh, t, z0, z1):
    oc = [( oxh, oyh), (-oxh, oyh), (-oxh, -oyh), ( oxh, -oyh)]
    ic = [( oxh-t, oyh-t), (-(oxh-t), oyh-t), (-(oxh-t), -(oyh-t)), ( oxh-t, -(oyh-t))]
    O0 = [bm.verts.new((x, y, z0)) for x, y in oc]
    I0 = [bm.verts.new((x, y, z0)) for x, y in ic]
    O1 = [bm.verts.new((x, y, z1)) for x, y in oc]
    I1 = [bm.verts.new((x, y, z1)) for x, y in ic]
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new([O0[i], O0[j], O1[j], O1[i]])
        bm.faces.new([I1[i], I1[j], I0[j], I0[i]])
        bm.faces.new([O1[i], O1[j], I1[j], I1[i]])
        bm.faces.new([I0[i], I0[j], O0[j], O0[i]])

def solo_box(name, cx, cy, cz, sx, sy, sz):
    bm = bmesh.new()
    bm_box(bm, cx, cy, cz, sx, sy, sz)
    return new_obj_from_bm(bm, name)

def apply_bool(target, cutter, op):
    mod = target.modifiers.new("b", 'BOOLEAN')
    mod.operation = op
    mod.solver = 'EXACT'
    mod.object = cutter
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    zs = [v.co.z for v in target.data.vertices]
    print("STAGE zmin=%.2f zmax=%.2f verts=%d" % (min(zs), max(zs), len(target.data.vertices)))

# ---------- dimensions ----------
XH, YH = 20.0, 15.0
CXH, CYH = 10.0, 7.0
Z2, Z3, Z4, Z5, Z6, ZTOP = 4.5, 7.5, 10.5, 13.5, 16.5, 19.5
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

BW, BD, BH = 2.4, 1.6, 2.7      # balcony recess
BOFF, WOFF = -1.1, 1.3
WW, WH = 1.8, 2.55              # floor-to-ceiling window opening
CW, CH, CSILL = 1.8, 2.4, 0.3   # courtyard window
SW, SH = 4.2, 3.8               # storefront opening (z 0.3 .. 4.1)

# ---------- shell: massing ----------
m1 = solo_box("Mass1", 0, 0, Z5/2, 2*XH, 2*YH, Z5)
m2 = solo_box("Mass2", 0, 0, (Z5-0.1+Z6)/2, 2*(XH-S5), 2*(YH-S5), Z6-Z5+0.1)
m3 = solo_box("Mass3", 0, 0, (Z6-0.1+ZTOP)/2, 2*(XH-S6), 2*(YH-S6), ZTOP-Z6+0.1)
apply_bool(m1, m2, 'UNION')
apply_bool(m1, m3, 'UNION')
shell = m1
shell.name = "ModernBuilding"

# courtyard
apply_bool(shell, solo_box("Court", 0, 0, (0.3+25.0)/2, 2*CXH, 2*CYH, 25.0-0.3), 'DIFFERENCE')

# rectangular tunnels through both ends
bm = bmesh.new()
bm_box(bm,  15, 0, (0.3+4.1)/2, 12.4, 4.2, 4.1-0.3)
bm_box(bm, -15, 0, (0.3+4.1)/2, 12.4, 4.2, 4.1-0.3)
apply_bool(shell, new_obj_from_bm(bm, "Tunnels"), 'DIFFERENCE')

# balcony recesses
bm = bmesh.new()
for zf, xh, yh, xcs, ycs in floors:
    cz = zf + 0.15 + BH/2
    for c in xcs:
        bm_box(bm, c+BOFF,  yh-BD/2+0.1, cz, BW, BD+0.2, BH)
        bm_box(bm, c+BOFF, -(yh-BD/2+0.1), cz, BW, BD+0.2, BH)
    for c in ycs:
        bm_box(bm,  xh-BD/2+0.1, c+BOFF, cz, BD+0.2, BW, BH)
        bm_box(bm, -(xh-BD/2+0.1), c+BOFF, cz, BD+0.2, BW, BH)
apply_bool(shell, new_obj_from_bm(bm, "BalCut"), 'DIFFERENCE')

# exterior window openings (floor-to-ceiling)
bm = bmesh.new()
for zf, xh, yh, xcs, ycs in floors:
    cz = zf + 0.15 + WH/2
    for c in xcs:
        bm_box(bm, c+WOFF,  yh-0.15+0.1, cz, WW, 0.5, WH)
        bm_box(bm, c+WOFF, -(yh-0.15+0.1), cz, WW, 0.5, WH)
    for c in ycs:
        bm_box(bm,  xh-0.15+0.1, c+WOFF, cz, 0.5, WW, WH)
        bm_box(bm, -(xh-0.15+0.1), c+WOFF, cz, 0.5, WW, WH)
apply_bool(shell, new_obj_from_bm(bm, "WinCut"), 'DIFFERENCE')

# courtyard window openings
bm = bmesh.new()
for zf, _, _, _, _ in floors:
    cz = zf + CSILL + CH/2
    for y in [-5, -2.5, 0, 2.5, 5]:
        bm_box(bm,  CXH+0.05, y, cz, 0.5, CW, CH)
        bm_box(bm, -(CXH+0.05), y, cz, 0.5, CW, CH)
    for x in [-7.5, -5, -2.5, 0, 2.5, 5, 7.5]:
        bm_box(bm, x,  CYH+0.05, cz, CW, 0.5, CH)
        bm_box(bm, x, -(CYH+0.05), cz, CW, 0.5, CH)
apply_bool(shell, new_obj_from_bm(bm, "CourtWinCut"), 'DIFFERENCE')

# storefront openings
ns_c = [-16.5, -11, -5.5, 0, 5.5, 11, 16.5]
ew_c = [-11.5, -6.5, 6.5, 11.5]
bm = bmesh.new()
for c in ns_c:
    bm_box(bm, c,  YH-0.2, (0.3+4.1)/2, SW, 1.2, SH)
    bm_box(bm, c, -(YH-0.2), (0.3+4.1)/2, SW, 1.2, SH)
for c in ew_c:
    bm_box(bm,  XH-0.2, c, (0.3+4.1)/2, 1.2, SW, SH)
    bm_box(bm, -(XH-0.2), c, (0.3+4.1)/2, 1.2, SW, SH)
apply_bool(shell, new_obj_from_bm(bm, "ShopCut"), 'DIFFERENCE')

# expressed slab bands (modern stacked-slab look)
bm = bmesh.new()
for z in (Z2, Z3, Z4):
    bm_ring(bm, XH+0.12, YH+0.12, 0.5, z-0.18, z+0.18)
apply_bool(shell, new_obj_from_bm(bm, "SlabBands"), 'UNION')

# slim parapets (terraces, roof, courtyard edge)
bm = bmesh.new()
bm_ring(bm, XH+0.06,    YH+0.06,    0.25, 13.45, 14.15)
bm_ring(bm, XH-S5+0.06, YH-S5+0.06, 0.25, 16.45, 17.15)
bm_ring(bm, XH-S6+0.06, YH-S6+0.06, 0.25, 19.45, 20.15)
bm_ring(bm, CXH+0.3,    CYH+0.3,    0.3,  19.45, 20.15)
apply_bool(shell, new_obj_from_bm(bm, "Parapets"), 'UNION')

# solid white balcony upstands (printable railings)
bm = bmesh.new()
for zf, xh, yh, xcs, ycs in floors:
    cz = zf + 0.13 + 0.525
    for c in xcs:
        bm_box(bm, c+BOFF,  yh-0.16, cz, BW+0.04, 0.18, 1.05)
        bm_box(bm, c+BOFF, -(yh-0.16), cz, BW+0.04, 0.18, 1.05)
    for c in ycs:
        bm_box(bm,  xh-0.16, c+BOFF, cz, 0.18, BW+0.04, 1.05)
        bm_box(bm, -(xh-0.16), c+BOFF, cz, 0.18, BW+0.04, 1.05)
apply_bool(shell, new_obj_from_bm(bm, "Upstands"), 'UNION')

# ---------- cleanup + manifold check ----------
bpy.ops.object.select_all(action='DESELECT')
shell.select_set(True)
bpy.context.view_layer.objects.active = shell
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles(threshold=0.0005)
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

bmc = bmesh.new()
bmc.from_mesh(shell.data)
for e in [e for e in bmc.edges if len(e.link_faces) == 0]:
    bmc.edges.remove(e)
for v in [v for v in bmc.verts if len(v.link_faces) == 0]:
    bmc.verts.remove(v)
nonman = sum(1 for e in bmc.edges if not e.is_manifold)
print("MANIFOLD non_manifold_edges=%d verts=%d faces=%d" %
      (nonman, len(bmc.verts), len(bmc.faces)))
bmc.to_mesh(shell.data)
bmc.free()

# ---------- glass + dark frames + wood accents (render-only objects) ----------
glass_bm = bmesh.new()
dark_bm = bmesh.new()
wood_bm = bmesh.new()

def glazed(axis, sign, wall, u, cz, w, h):
    """glass pane + dark backing in an opening on a facade plane."""
    if axis == 'y':
        glass_bm and bm_box(glass_bm, u, sign*(wall-0.18), cz, w-0.12, 0.05, h-0.12)
        bm_box(dark_bm, u, sign*(wall-0.24), cz, w, 0.04, h)
    else:
        bm_box(glass_bm, sign*(wall-0.18), u, cz, 0.05, w-0.12, h-0.12)
        bm_box(dark_bm, sign*(wall-0.24), u, cz, 0.04, w, h)

for zf, xh, yh, xcs, ycs in floors:
    cz = zf + 0.15 + WH/2
    for c in xcs:
        glazed('y',  1, yh, c+WOFF, cz, WW, WH)
        glazed('y', -1, yh, c+WOFF, cz, WW, WH)
        # balcony glass door behind recess
        if True:
            bm_box(glass_bm, c+BOFF,  yh-BD+0.06, zf+0.15+(BH-0.2)/2, BW-0.3, 0.05, BH-0.2)
            bm_box(glass_bm, c+BOFF, -(yh-BD+0.06), zf+0.15+(BH-0.2)/2, BW-0.3, 0.05, BH-0.2)
    for c in ycs:
        glazed('x',  1, xh, c+WOFF, cz, WW, WH)
        glazed('x', -1, xh, c+WOFF, cz, WW, WH)
        bm_box(glass_bm,  xh-BD+0.06, c+BOFF, zf+0.15+(BH-0.2)/2, 0.05, BW-0.3, BH-0.2)
        bm_box(glass_bm, -(xh-BD+0.06), c+BOFF, zf+0.15+(BH-0.2)/2, 0.05, BW-0.3, BH-0.2)
    # wood soffit panel at balcony recess back wall
    for c in xcs:
        wood_z = zf + 0.15 + (BH-0.1)/2
        bm_box(wood_bm, c+BOFF,  yh-BD+0.02, wood_z, BW-0.06, 0.06, BH-0.1)
        bm_box(wood_bm, c+BOFF, -(yh-BD+0.02), wood_z, BW-0.06, 0.06, BH-0.1)
    for c in ycs:
        wood_z = zf + 0.15 + (BH-0.1)/2
        bm_box(wood_bm,  xh-BD+0.02, c+BOFF, wood_z, 0.06, BW-0.06, BH-0.1)
        bm_box(wood_bm, -(xh-BD+0.02), c+BOFF, wood_z, 0.06, BW-0.06, BH-0.1)

# courtyard glazing
for zf, _, _, _, _ in floors:
    cz = zf + CSILL + CH/2
    for y in [-5, -2.5, 0, 2.5, 5]:
        glazed('x',  1, CXH+0.3, y, cz, CW, CH)
        glazed('x', -1, CXH+0.3, y, cz, CW, CH)
    for x in [-7.5, -5, -2.5, 0, 2.5, 5, 7.5]:
        glazed('y',  1, CYH+0.3, x, cz, CW, CH)
        glazed('y', -1, CYH+0.3, x, cz, CW, CH)

# storefront glazing with center mullion
cz_s = (0.3+4.1)/2
for c in ns_c:
    for sgn in (1, -1):
        bm_box(glass_bm, c, sgn*(YH-0.45), cz_s, SW-0.15, 0.05, SH-0.15)
        bm_box(dark_bm,  c, sgn*(YH-0.52), cz_s, SW, 0.04, SH)
        bm_box(dark_bm,  c, sgn*(YH-0.40), cz_s, 0.1, 0.08, SH-0.1)
for c in ew_c:
    for sgn in (1, -1):
        bm_box(glass_bm, sgn*(XH-0.45), c, cz_s, 0.05, SW-0.15, SH-0.15)
        bm_box(dark_bm,  sgn*(XH-0.52), c, cz_s, 0.04, SW, SH)
        bm_box(dark_bm,  sgn*(XH-0.40), c, cz_s, 0.08, 0.1, SH-0.1)

glass = new_obj_from_bm(glass_bm, "Glazing")
dark = new_obj_from_bm(dark_bm, "DarkFrames")
wood = new_obj_from_bm(wood_bm, "WoodAccents")

# ground plane
ground = solo_box("Ground", 0, 0, -0.05, 300, 300, 0.1)

# ---------- materials ----------
def simple_mat(name, color, rough, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = color
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m

shell.data.materials.append(simple_mat("WhiteRender", (0.85, 0.84, 0.81, 1), 0.6))
glass.data.materials.append(simple_mat("Glass", (0.22, 0.31, 0.38, 1), 0.08, 0.85))
dark.data.materials.append(simple_mat("Charcoal", (0.045, 0.045, 0.05, 1), 0.5))
wood.data.materials.append(simple_mat("WarmWood", (0.43, 0.25, 0.12, 1), 0.65))
ground.data.materials.append(simple_mat("Pavement", (0.52, 0.52, 0.50, 1), 0.9))

# ---------- lighting / world / camera ----------
sun = bpy.data.objects.get("Light")
sun.data.type = 'SUN'
sun.data.energy = 4.0
sun.rotation_euler = (math.radians(50), 0, math.radians(30))

fill_data = bpy.data.lights.new("Fill", 'SUN')
fill_data.energy = 1.2
fill_data.color = (0.75, 0.82, 1.0)
fill = bpy.data.objects.new("Fill", fill_data)
col.objects.link(fill)
fill.rotation_euler = (math.radians(60), 0, math.radians(-130))

world = bpy.data.worlds["World"]
world.use_nodes = True
wbg = world.node_tree.nodes.get("Background")
wbg.inputs[0].default_value = (0.72, 0.80, 0.92, 1)
wbg.inputs[1].default_value = 1.0

scene = bpy.context.scene
for engine in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
    try:
        scene.render.engine = engine
        break
    except TypeError:
        continue
scene.eevee.taa_render_samples = 64
scene.render.resolution_x = 1600
scene.render.resolution_y = 1000
scene.render.image_settings.file_format = 'PNG'

from mathutils import Vector
cam = bpy.data.objects["Camera"]
cam.data.clip_end = 1000

def shoot(loc, target, path):
    cam.location = loc
    d = Vector(target) - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)

shoot((62, -54, 36), (0, 0, 8),  os.path.join(OUT_DIR, "modern-hero.png"))
shoot((34, -44, 2.0), (0, -8, 11), os.path.join(OUT_DIR, "modern-street.png"))

# ---------- save + export ----------
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "ModernApartmentBuilding.blend"))
bpy.ops.object.select_all(action='DESELECT')
shell.select_set(True)
bpy.context.view_layer.objects.active = shell
bpy.ops.wm.stl_export(filepath=os.path.join(OUT_DIR, "ModernApartmentBuilding.stl"),
                      export_selected_objects=True)
print("ALL DONE")
