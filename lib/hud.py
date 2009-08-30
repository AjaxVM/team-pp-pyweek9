
import pyggel
from pyggel import *

import data

class Hud(pyggel.scene.BaseSceneObject):
    def __init__(self):
        pyggel.scene.BaseSceneObject.__init__(self)

        self.font = pyggel.font.Font()

        self.hover_status = {}
        self.hover_status["door"] = self.font.make_text_image("Door - face and move next to it to open")

        self.cur_text = None

    def set_hover_status(self, text):
        self.cur_text = text

    def render(self):
        if self.cur_text:
            img = self.hover_status[self.cur_text]
            x,y = 320, 50
            w,h = img.get_size()
            img.pos = x-w/2, y-h/2
            img.render()
            img.pos = x,y
