
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
        self.hover_status["feather"] = self.font.make_text_image("A feather! Get close to it and Right-click to take")
        self.hover_status["shotgun"] = self.font.make_text_image("A shotgun! Better grab that - Right-click to take")
        self.hover_status["handgun"] = self.font.make_text_image("A handgun, better than nothing - Right-click to take")
        self.hover_status["hp"] = self.font.make_text_image("A health {health}+20 pack! Right-click to take")
        self.hover_status["ammo"] = self.font.make_text_image("An ammo {ammo}+25 pack! Right-click to take")
        self.hover_status["starting_console"] = self.font.make_text_image("Alien Console - move to and Right-click to use!")

        colors = {"1//1//0.25":"fast",
                  "0//1//0":"high damage",
                  "0//0//1":"normal"}
        shapes = {"quad":("A badguy (Level 1)", "- shoot it!"),
                  "pyramid":("A badguy (Level 2)", "- shoot it!"),
                  "dpyramid":("A badguy (Level 3)", "- shoot it!"),
                  "cube":("A badguy (Level 4)", "- shoot it!"),
                  "sphere":("A boss (Level 10)", "- watch out O_O"),
                  "ellipsoid":("A boss (Level 15)", "- umm.. run?")}
        for i in colors:
            for x in shapes:
                self.hover_status[i+"//"+x] = self.font.make_text_image(shapes[x][0]+" ("+colors[i]+") "+shapes[x][1])

        self.cur_text = None

        self.feathers = self.font.make_text_image("Feathers: 0/3")
        self.feathers.pos = (10, 50)

        self.hp = self.font.make_text_image("{health} 100")
        self.hp.pos = (10, 85)
        self.weapon = self.font.make_text_image("Weapon: None")
        self.weapon.pos = (0, 145)
        self.ammo = self.font.make_text_image("{ammo} 100")
        self.ammo.pos = (10, 180)

        self.event_handler = pyggel.event.Handler()

        #create gui apps for various events!
        self.console_app = pyggel.gui.App(self.event_handler)
        self.console_app.theme.load(data.gui_path("theme.py"))
        self.console_app.packer.packtype="center"
        frame = pyggel.gui.Frame(self.console_app, size=(300,200), image_border=9)
        frame.packer.packtype="center"
        pyggel.gui.Button(frame, "click!", callbacks=[self.gui_inactive])


        #set up later theme/font usage
        theme = self.console_app.theme
        fonts = self.console_app.fonts
        #any apps that are created later:
        #   app.theme = theme
        #   app.update_fonts(fonts)

        self.active_app = None

        self.app_binding = {"console":self.console_app}
        self.grab_events = False


        #target image
        self.target = pyggel.image.Image(data.image_path("target.png"),
                                         pos=(320-32, 240-32))

    def gui_inactive(self):
        pygame.event.set_grab(1)
        pygame.mouse.set_visible(0)
        self.event_handler.gui = None #turn off all guis
        self.active_app = None
        self.grab_events = False

    def gui_active(self):
        pygame.event.set_grab(0)
        pygame.mouse.set_visible(1)
        self.active_app.activate()
        self.grab_events = True
        pygame.mouse.set_pos((320,240))

    def set_gui_app(self, name):
        if name in self.app_binding:
            self.active_app = self.app_binding[name]
            self.gui_active()
        else:
            print name, "not in bindings!"
            self.gui_inactive()

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
        if self.active_app:
            self.active_app.render()

        else:
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
            self.target.render()
