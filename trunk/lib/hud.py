
import pyggel
from pyggel import *

import data

class Hud(pyggel.scene.BaseSceneObject):
    def __init__(self):
        pyggel.scene.BaseSceneObject.__init__(self)

        self.font = pyggel.font.Font()
        self.font.add_image("{health}", pyggel.image.Image(data.image_path("hp.png")))
        self.font.add_image("{ammo}", pyggel.image.Image(data.image_path("ammo.png")))

        self.hover_status = {}
        self.hover_status["door"] = self.font.make_text_image("Door - face and move next to it to open")
        self.hover_status["feather"] = self.font.make_text_image("A feather! Get close to it and Right-click to pick it up")
        self.hover_status["shotgun"] = self.font.make_text_image("A shotgun! Better grab that, Right-click to pick it up")
        self.hover_status["hp"] = self.font.make_text_image("A health {health}+20 pack! Right-click to take it")
        self.hover_status["ammo"] = self.font.make_text_image("An ammo {ammo}+25 pack! Right-click to take it")

        self.cur_text = None

        self.feathers = self.font.make_text_image("Feathers: 0/3")
        self.feathers.pos = (10, 50)

        self.hp = self.font.make_text_image("{health} 100")
        self.hp.pos = (10, 85)
        self.weapon = self.font.make_text_image("Weapon: None")
        self.weapon.pos = (0, 145)
        self.ammo = self.font.make_text_image("{ammo} 100")
        self.ammo.pos = (10, 180)

    def set_hover_status(self, text):
        self.cur_text = text

    def update_feathers(self, have, max):
        text = "Feathers: %s/%s"%(have, max)
        if not self.feathers.text == text:
            self.feathers.text = text

    def update_hp(self, amount):
        text = "{health} %s"%amount
        if not self.hp.text == text:
            self.hp.text = text

    def update_ammo(self, amount):
        text = "{ammo} %s"%amount
        if not self.ammo.text == text:
            self.ammo.text = text

    def update_weapon(self, weapon):
        text = "Weapon: %s"%weapon
        if not self.weapon.text == text:
            self.weapon.text = text

    def render(self):
        if self.cur_text:
            img = self.hover_status[self.cur_text]
            x,y = 320, 10
            img.pos = x-img.get_width()/2, y
            img.render()
            img.pos = x,y

        self.feathers.render()
        self.hp.render()
        self.weapon.render()
        self.ammo.render()
