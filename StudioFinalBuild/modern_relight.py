import bpy
import math
import os
from mathutils import Vector

OUT_DIR = r"C:\Users\frank\Documents\Gavins Files\Gavin Studio Project\StudioFinalBuild"

sun = bpy.data.objects["Light"]
sun.data.energy = 6.5
sun.data.color = (1.0, 0.96, 0.88)
sun.rotation_euler = (math.radians(55), 0, math.radians(38))

fill = bpy.data.objects.get("Fill")
fill.data.energy = 0.9

world = bpy.data.worlds["World"]
wbg = world.node_tree.nodes.get("Background")
wbg.inputs[0].default_value = (0.55, 0.68, 0.85, 1)
wbg.inputs[1].default_value = 0.55

glass = bpy.data.materials["Glass"]
gb = glass.node_tree.nodes["Principled BSDF"]
gb.inputs["Base Color"].default_value = (0.13, 0.20, 0.28, 1)
gb.inputs["Roughness"].default_value = 0.05

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
print("RELIT DONE")
