import bpy
import math
import os

OUT_DIR = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild"
scene = bpy.context.scene
col = bpy.context.collection
cam = bpy.data.objects["Camera"]

# aim target
aim = bpy.data.objects.new("Aim", None)
col.objects.link(aim)
aim.location = (0.0, 0.0, 9.0)

# orbit pivot
pivot = bpy.data.objects.new("FlyPivot", None)
col.objects.link(pivot)
pivot.location = (0.0, 0.0, 0.0)

cam.parent = pivot
cam.matrix_parent_inverse = pivot.matrix_world.inverted()
tc = cam.constraints.new('TRACK_TO')
tc.target = aim
tc.track_axis = 'TRACK_NEGATIVE_Z'
tc.up_axis = 'UP_Y'

FRAMES = 192  # 8 s @ 24 fps
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
pivot.rotation_euler = (0, 0, 0)
pivot.keyframe_insert(data_path="rotation_euler", frame=1)
pivot.rotation_euler = (0, 0, math.radians(360.0))
pivot.keyframe_insert(data_path="rotation_euler", frame=FRAMES + 1)

# camera rises over the roof mid-orbit, then settles back — smooth ease
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'BEZIER'
cam.location = (72, -62, 14)
cam.keyframe_insert(data_path="location", frame=1)
cam.location = (40, -34, 52)
cam.keyframe_insert(data_path="location", frame=FRAMES // 2 + 1)
cam.location = (72, -62, 14)
cam.keyframe_insert(data_path="location", frame=FRAMES + 1)

scene.frame_start = 1
scene.frame_end = FRAMES
scene.render.fps = 24
for engine in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
    try:
        scene.render.engine = engine
        break
    except TypeError:
        continue
scene.eevee.taa_render_samples = 32
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = os.path.join(OUT_DIR, "flyover_frames", "frame_####")

bpy.ops.render.render(animation=True)
print("FLYOVER FRAMES DONE")
