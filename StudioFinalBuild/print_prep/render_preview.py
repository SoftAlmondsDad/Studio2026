import bpy, math, mathutils

OUT_DIR = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild\print_prep"

scene = bpy.context.scene
tower = scene.objects["TowerOfPisa"]

# bbox center/size
mins = [float("inf")] * 3
maxs = [float("-inf")] * 3
for corner in tower.bound_box:
    wc = tower.matrix_world @ mathutils.Vector(corner)
    for i in range(3):
        mins[i] = min(mins[i], wc[i])
        maxs[i] = max(maxs[i], wc[i])
center = mathutils.Vector([(mins[i] + maxs[i]) / 2 for i in range(3)])
height = maxs[2] - mins[2]

cam_data = bpy.data.cameras.new("PreviewCam")
cam = bpy.data.objects.new("PreviewCam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

empty = bpy.data.objects.new("Target", None)
empty.location = center
scene.collection.objects.link(empty)
tr = cam.constraints.new('TRACK_TO')
tr.target = empty

scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'SINGLE'
scene.display.shading.single_color = (0.8, 0.75, 0.65)
scene.render.resolution_x = 800
scene.render.resolution_y = 1100
scene.render.film_transparent = False

dist = height * 1.5
for label, angle_deg in (("front", -90), ("three_quarter", -45), ("back", 90)):
    a = math.radians(angle_deg)
    cam.location = (center.x + dist * math.cos(a), center.y + dist * math.sin(a), center.z + height * 0.25)
    scene.render.filepath = OUT_DIR + "\\preview_" + label + ".png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)
