import pyggel
from pyggel import *

import data, hud
import random, math

class HPBuff(pyggel.scene.BaseSceneObject):
    obj = None
    def __init__(self, pos):
        if not HPBuff.obj:
            HPBuff.obj = pyggel.geometry.Cube(2, texture=pyggel.data.Texture(data.image_path("hp_tex.png")), mirror=True)
        pyggel.scene.BaseSceneObject.__init__(self)
        self.pos = pos

        self.rotation = 25, 0, 0

    def picked(self):
        self.game_hud.set_hover_status("hp")

    def update(self):
        x, y, z = self.rotation
        y += 2
        self.rotation = x, y, z

    def render(self, camera=None):
        self.update()
        self.obj.pos = self.pos
        self.obj.rotation = self.rotation
        self.obj.render(camera)

class AmmoBuff(pyggel.scene.BaseSceneObject):
    obj = None
    def __init__(self, pos):
        if not AmmoBuff.obj:
            AmmoBuff.obj = pyggel.geometry.Cube(2, texture=pyggel.data.Texture(data.image_path("ammo_tex.png")), mirror=True)
        pyggel.scene.BaseSceneObject.__init__(self)
        self.pos = pos

        self.rotation = 25, 0, 0

    def picked(self):
        self.game_hud.set_hover_status("ammo")

    def update(self):
        x, y, z = self.rotation
        y += 2
        self.rotation = x, y, z

    def render(self, camera=None):
        self.update()
        self.obj.pos = self.pos
        self.obj.rotation = self.rotation
        self.obj.render(camera)
