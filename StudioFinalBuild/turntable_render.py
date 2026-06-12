import bpy
import math
import os

scene = bpy.context.scene
cam = bpy.data.objects["Camera"]

# pivot at world center; camera orbits it for a seamless 360 loop
pivot = bpy.data.objects.new("TurntablePivot", None)
scene.collection.objects.link(pivot)
pivot.location = (0.0, 0.0, 0.0)

cam.parent = pivot
cam.matrix_parent_inverse = pivot.matrix_world.inverted()

# keep the sun fixed relative to the camera so no part of the loop goes dark
sun = bpy.data.objects["Light"]
sun.parent = pivot
sun.matrix_parent_inverse = pivot.matrix_world.inverted()

FRAMES = 144  # 6 s @ 24 fps; frame FRAMES+1 == frame 1, so loop is seamless
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
pivot.rotation_euler = (0.0, 0.0, 0.0)
pivot.keyframe_insert(data_path="rotation_euler", frame=1)
pivot.rotation_euler = (0.0, 0.0, math.radians(360.0))
pivot.keyframe_insert(data_path="rotation_euler", frame=FRAMES + 1)

# render settings
for engine in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
    try:
        scene.render.engine = engine
        break
    except TypeError:
        continue
scene.eevee.taa_render_samples = 32
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = FRAMES

scene.render.image_settings.file_format = 'PNG'
out = os.path.join(os.path.dirname(bpy.data.filepath), "turntable_frames", "frame_####")
scene.render.filepath = out

bpy.ops.render.render(animation=True)
print("DONE:", out)
