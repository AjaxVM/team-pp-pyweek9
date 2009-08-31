
import pyggel
from pyggel import *

import data

class Hud(pyggel.scene.BaseSceneObject):
    def __init__(self):
        pyggel.scene.BaseSceneObject.__init__(self)

        self.font = pyggel.font.Font()

        self.hover_status = {}
        self.hover_status["door"] = self.font.make_text_image("Door - face and move next to it to open")
        self.hover_status["feather"] = self.font.make_text_image("A feather! Get close to it and Right-click to pick it up")
        self.hover_status["shotgun"] = self.font.make_text_image("A shotgun! Better grab that, Right-click to pick it up")

        self.cur_text = None

        self.feathers = self.font.make_text_image("Feathers: 0/3")
        self.feathers.pos = (10, 50)

    def set_hover_status(self, text):
        self.cur_text = text

    def update_feathers(self, have, max):
        text = "Feathers: %s/%s"%(have, max)
        if not self.feathers.text == text:
            self.feathers.text = text

    def render(self):
        if self.cur_text:
            img = self.hover_status[self.cur_text]
            x,y = 320, 25
            w,h = img.get_size()
            img.pos = x-w/2, y-h/2
            img.render()
            img.pos = x,y

        self.feathers.render()
