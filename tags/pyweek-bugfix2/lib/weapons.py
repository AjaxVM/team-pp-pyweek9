import pyggel
from pyggel import *

import data, hud
import random, math

class Weapon(pyggel.scene.BaseSceneObject):
    objs = {}
    def __init__(self, pos, name):
        for i in Weapon.objs:
            if Weapon.objs[i] == None:
                Weapon.objs = {}
                break
        if not Weapon.objs:
            Weapon.objs["shotgun"] = pyggel.mesh.OBJ(data.mesh_path("shotgun.obj"))
            Weapon.objs["handgun"] = pyggel.mesh.OBJ(data.mesh_path("handgun.obj"))
            Weapon.objs["plasma gun"] = pyggel.mesh.OBJ(data.mesh_path("PlasmaGun.obj"))
            Weapon.objs["chaingun"] = pyggel.mesh.OBJ(data.mesh_path("chaingun.obj"))
            Weapon.objs["chicken gun"] = pyggel.mesh.OBJ(data.mesh_path("chickenGun.obj"))
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
        if self.obj:
            self.obj.pos = self.pos
            self.obj.rotation = self.rotation
            self.obj.render(camera)
        else:
            self.dead_remove_from_scene = True

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

        self.pos = self.pos = pos
        self.rotation = rotation
        self.level_data = level_data
        self.puff_tick = 1
        self.damage = 4

    def render(self, camera=None):
        if self.dead_remove_from_scene:
            return
        self.pos = pyggel.math3d.move_with_rotation(self.pos, self.rotation, -1)
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

        self.pos = self.pos = pos
        self.rotation = rotation
        self.level_data = level_data
        self.puff_tick = 1
        self.damage = 2

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


class PlasmaShot(pyggel.scene.BaseSceneObject):
    obj = None
    def __init__(self, pos, rotation, level_data, scene):
        if not PlasmaShot.obj:
            PlasmaShot.obj = pyggel.image.Image3D(data.image_path("flash.png"))
            PlasmaShot.obj.colorize=(1,0,1,1)
        pyggel.scene.BaseSceneObject.__init__(self)

        self.collision_body = pyggel.math3d.AABox(pos, 0.5)

        self.pos = pyggel.math3d.move_with_rotation((pos[0], 0, pos[2]), rotation, -1.5)
        self.rotation = rotation
        self.level_data = level_data

        self.scale_up = True
        self.scale = 1
        self.twist = 0

        self.speed = 2
        self.damage = 8

    def render(self, camera=None):
        if self.scale_up:
            self.scale += 0.6
            if self.scale >= 3:
                self.scale = 3
                self.scale_up = False
        else:
            if self.scale > 0.25:
                self.scale -= 1
            else:
                self.scale = 0.25
                self.pos = pyggel.math3d.move_with_rotation(self.pos, self.rotation, -0.5*self.speed)
        if self.dead_remove_from_scene:
            return
        self.collision_body.set_pos(self.pos)
        if self.level_data.get_at_uncon(self.pos[0], self.pos[2]) in self.level_data.collidable:
            self.dead_remove_from_scene = True #kills object
        self.obj.pos = self.pos
        self.obj.scale = self.scale
        self.twist += 15
        self.obj.rotation = (0,0,self.twist)
        self.obj.render(camera)


class ChaingunShot(pyggel.scene.BaseSceneObject):
    obj = None
    def __init__(self, pos, rotation, level_data, scene):
        if not ChaingunShot.obj:
            ChaingunShot.obj = pyggel.geometry.Sphere(0.075)
            ChaingunShot.obj.colorize = (0.075,0.075,0.1)
        pyggel.scene.BaseSceneObject.__init__(self)

        self.scene = scene

        self.collision_body = pyggel.math3d.Sphere(pos, 0.10)

        self.pos = pos
        self.rotation = rotation
        self.level_data = level_data
        self.damage = 1.5
        self.scene.add_3d_blend(ChaingunPuff(self.pos, self.rotation))

    def render(self, camera=None):
        if self.dead_remove_from_scene:
            return
        self.pos = pyggel.math3d.move_with_rotation(self.pos, self.rotation, -1.25)
        self.collision_body.set_pos(self.pos)
        if self.level_data.get_at_uncon(self.pos[0], self.pos[2]) in self.level_data.collidable:
            self.dead_remove_from_scene = True #kills object
        self.obj.pos = self.pos
        self.obj.rotation = self.rotation
        self.obj.render(camera)

class ChaingunPuff(pyggel.scene.BaseSceneObject):
    obj = None
    def __init__(self, pos, rotation):
        if not ChaingunPuff.obj:
            ChaingunPuff.obj = pyggel.image.Image3D(data.image_path("flash.png"))
            ChaingunPuff.obj.colorize = 1,1,0.25,1
        pyggel.scene.BaseSceneObject.__init__(self)

        self.pos = pos
        self.rotation = rotation

        self.pos = pyggel.math3d.move_with_rotation(self.pos, self.rotation, -2)
        self.age = 0
        self.scale = 1.5

    def render(self, camera=None):
        self.scale -= 0.10
        self.obj.pos = self.pos
        self.obj.scale = self.scale
        self.obj.render(camera)

        self.age += 1
        if self.age >= 3:
            self.dead_remove_from_scene = True


class ChickenGunShot(pyggel.scene.BaseSceneObject):
    obj = None
    def __init__(self, pos, rotation, level_data, scene):
        if not PlasmaShot.obj:
            ChickenGunShot.obj = pyggel.geometry.Sphere(0.125)
            ChickenGunShot.obj.scale = (1,1,2)
            ChickenGunShot.obj.colorize = (0.85,0.8,0.7)
        pyggel.scene.BaseSceneObject.__init__(self)

        self.collision_body = pyggel.math3d.AABox(pos, 0.5)

        self.pos = pos
        self.rotation = rotation
        self.level_data = level_data

        self.rot_x = 0

        self.speed = 1.5
        self.damage = 12

    def render(self, camera=None):
        self.rot_x += 10
        self.pos = pyggel.math3d.move_with_rotation(self.pos, self.rotation, -0.5*self.speed)
        if self.dead_remove_from_scene:
            return
        self.collision_body.set_pos(self.pos)
        if self.level_data.get_at_uncon(self.pos[0], self.pos[2]) in self.level_data.collidable:
            self.dead_remove_from_scene = True #kills object
        self.obj.pos = self.pos
        self.obj.rotation = self.rotation[0]+self.rot_x, self.rotation[1], self.rotation[2]
        self.obj.render(camera)
