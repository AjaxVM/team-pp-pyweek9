import pyggel
from pyggel import *

import data, hud
import random, math

class Weapon(pyggel.scene.BaseSceneObject):
    objs = {}
    def __init__(self, pos, name):
        if not self.objs:
            self.objs["shotgun"] = pyggel.mesh.OBJ(data.mesh_path("shotgun.obj"))
            self.objs["handgun"] = pyggel.mesh.OBJ(data.mesh_path("handgun.obj"))
        pyggel.scene.BaseSceneObject.__init__(self)
        self.pos = pos

        self.obj = self.objs[name]
        self.rotation = 25, 0, 0
        self.name = name

    def picked(self):
        self.game_hud.set_hover_status(self.name)

    def update(self):
        x, y, z = self.rotation
        y += 2
        self.rotation = x, y, z

    def render(self, camera=None):
        self.update()
        self.obj.pos = self.pos
        self.obj.rotation = self.rotation
        self.obj.render(camera)

class ShotgunShot(pyggel.scene.BaseSceneObject):
    obj = None
    def __init__(self, pos, rotation, level_data, scene):
        if not ShotgunShot.obj:
            ShotgunShot.obj = pyggel.geometry.Sphere(0.1)
            ShotgunShot.obj.scale = (1,1,4)
            ShotgunShot.obj.colorize = (0.2,0.2,0.25)
        pyggel.scene.BaseSceneObject.__init__(self)

        self.scene = scene

        self.collision_body = pyggel.math3d.AABox(pos, 0.15)

        self.pos = pos
        self.rotation = rotation
        self.level_data = level_data
        self.puff_tick = 1
        self.damage = 5

    def render(self, camera=None):
        if self.dead_remove_from_scene:
            return
        self.pos = pyggel.math3d.move_with_rotation(self.pos, self.rotation, -.75)
        self.collision_body.set_pos(self.pos)
        if self.level_data.get_at_uncon(self.pos[0], self.pos[2]) in self.level_data.collidable:
            self.dead_remove_from_scene = True #kills object
        self.obj.pos = self.pos
        self.obj.rotation = self.rotation
        self.obj.render(camera)

        if self.puff_tick <= 20:
            self.scene.add_3d_blend(ShotgunPuff(self.pos, self.rotation, self.puff_tick))
            self.puff_tick += 1

class ShotgunPuff(pyggel.scene.BaseSceneObject):
    obj = None
    def __init__(self, pos, rotation, size=1):
        if not ShotgunPuff.obj:
            ShotgunPuff.obj = pyggel.image.Image3D(data.image_path("shotgun_puff.png"))
        pyggel.scene.BaseSceneObject.__init__(self)

        self.pos = pos
        self.rotation = rotation

        self.pos = pyggel.math3d.move_with_rotation(self.pos, self.rotation, -1)

        self.puff_scale = 0.075 * size
        self.puff_rotate = size*3
        self.puff_alpha = 0.5 - size*0.025

    def render(self, camera=None):
        self.obj.pos = self.pos
        self.obj.scale  = self.puff_scale
        self.obj.rotation = (0,0,self.puff_rotate)
        self.obj.colorize = (1,1,1,self.puff_alpha)
        self.obj.render(camera)

        self.dead_remove_from_scene = True

class HandgunShot(pyggel.scene.BaseSceneObject):
    obj = None
    def __init__(self, pos, rotation, level_data, scene):
        if not HandgunShot.obj:
            HandgunShot.obj = pyggel.geometry.Sphere(0.1)
            HandgunShot.obj.colorize = (0,0,0)
        pyggel.scene.BaseSceneObject.__init__(self)

        self.scene = scene

        self.collision_body = pyggel.math3d.Sphere(pos, 0.1)

        self.pos = pos
        self.rotation = rotation
        self.level_data = level_data
        self.puff_tick = 1
        self.damage = 2

    def render(self, camera=None):
        if self.dead_remove_from_scene:
            return
        self.pos = pyggel.math3d.move_with_rotation(self.pos, self.rotation, -.5)
        self.collision_body.set_pos(self.pos)
        if self.level_data.get_at_uncon(self.pos[0], self.pos[2]) in self.level_data.collidable:
            self.dead_remove_from_scene = True #kills object
        self.obj.pos = self.pos
        self.obj.rotation = self.rotation
        self.obj.render(camera)

        if self.puff_tick <= 10:
            self.scene.add_3d_blend(HandgunPuff(self.pos, self.rotation, self.puff_tick))
            self.puff_tick += 1

class HandgunPuff(pyggel.scene.BaseSceneObject):
    obj = None
    def __init__(self, pos, rotation, size=1):
        if not HandgunPuff.obj:
            HandgunPuff.obj = pyggel.image.Image3D(data.image_path("shotgun_puff.png"))
        pyggel.scene.BaseSceneObject.__init__(self)

        self.pos = pos
        self.rotation = rotation

        self.pos = pyggel.math3d.move_with_rotation(self.pos, self.rotation, -1)

        self.puff_scale = 0.1 * size
        self.puff_rotate = size * 3
        self.puff_alpha = 0.5 - size*0.025

    def render(self, camera=None):
        self.obj.pos = self.pos
        self.obj.scale  = self.puff_scale
        self.obj.rotation = (0,0,self.puff_rotate)
        self.obj.colorize = (1,1,1,self.puff_alpha)
        self.obj.render(camera)

        self.dead_remove_from_scene = True
