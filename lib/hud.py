
import pyggel
from pyggel import *

import data
import time

import sfx
        

class Hud(pyggel.scene.BaseSceneObject):
    def __init__(self):
        pyggel.scene.BaseSceneObject.__init__(self)

        self.font = pyggel.font.Font()
        self.big_font = pyggel.font.Font(None, 45)
        self.font.add_image("{health}", pyggel.image.Image(data.image_path("hp.png")))
        self.font.add_image("{ammo}", pyggel.image.Image(data.image_path("ammo.png")))
        self.font.add_image("{feather}", pyggel.image.Image(data.image_path("feather.png")))

        self.big_font.add_image("{health}", pyggel.image.Image(data.image_path("hp.png")))
        self.big_font.add_image("{ammo}", pyggel.image.Image(data.image_path("ammo.png")))
        self.big_font.add_image("{feather}", pyggel.image.Image(data.image_path("feather.png")))

        self.hover_status = {}
        self.hover_status["door"] = self.font.make_text_image("Door - face and move next to it to open", color=(0,0,0,1))
        self.hover_status["feather"] = self.font.make_text_image("A feather! Get close to it and Right-click to take", color=(0,0,0,1))
        self.hover_status["shotgun"] = self.font.make_text_image("A shotgun! Better grab that - Right-click to take", color=(0,0,0,1))
        self.hover_status["handgun"] = self.font.make_text_image("A handgun, better than nothing - Right-click to take", color=(0,0,0,1))
        self.hover_status["plasma gun"] = self.font.make_text_image("A plasma gun, same energy as the aliens use! - Right-click", color=(0,0,0,1))
        self.hover_status["hp"] = self.font.make_text_image("A +20 {health} pack! Right-click to take", color=(0,0,0,1))
        self.hover_status["ammo"] = self.font.make_text_image("A +25 {ammo} pack! Right-click to take", color=(0,0,0,1))
        self.hover_status["starting_console"] = self.font.make_text_image("Alien Console - move to and Right-click to use!", color=(0,0,0,1))

        colors = {"1//1//0.25":"fast",
                  "0//1//0":"high damage",
                  "0//0//1":"normal"}
        shapes = {"quad":("A badguy (Level 1)", "- shoot it!"),
                  "pyramid":("A badguy (Level 2)", "- shoot it!"),
                  "dpyramid":("A badguy (Level 3)", "- shoot it!"),
                  "cube":("A badguy (Level 4)", "- shoot it!"),
                  "sphere":("An enforcer (Level 5)", "- watch out O_O"),
                  "ellipsoid":("An enforcer (Level 6)", "careful there!"),
                  "boss":("A boss (Level 10)", "The Controller - kill him!")}
        for i in colors:
            for x in shapes:
                self.hover_status[i+"//"+x] = self.font.make_text_image(shapes[x][0]+" ("+colors[i]+") "+shapes[x][1])

        self.cur_text = None

        self.feathers = self.big_font.make_text_image("{feather} 0/3", color=(0,0,0,1))
        self.feathers.pos = (10, 5)

        self.hp = self.big_font.make_text_image("{health} 100", color=(0,0,0,1))
        self.hp.pos = (130, 5)
        self.weapon = self.font.make_text_image("Weapon: None", color=(0,0,0,1))
        self.weapon.pos = (260, 10)
        self.weapon.scale = (1,1.5,1)
        self.ammo = self.big_font.make_text_image("{ammo} 100", color=(0,0,0,1))
        self.ammo.pos = (505, 5)

        self.event_handler = pyggel.event.Handler()

        #create gui apps for various events!
        self.main_app = pyggel.gui.App(self.event_handler)
        self.main_app.theme.load(data.gui_path("theme.py"))

        #set up later theme/font usage
        self.core_theme = self.main_app.theme
        self.core_fonts = self.main_app.fonts
        #any apps that are created later:
        #   app.theme = self.core_theme
        #   app.update_fonts(self.core_fonts)

        intro_qa = [("Hmm, this looks like a radio...\nmy nerves are fried...\nmaybe they have country 122.3 here...","<Hit some buttons>"),
                   ("BZZT... Squad 4 to sector 12...\numm sir, there's someone else on the line!!\n"+\
                    "Communication is coming from the alien mother-ship!", "...uhm, oops... I'm not an alien..."),
                   ("Of course you're not an alien, they can't speak...\nidentify yourself then...", "I'm Farmer Bob"),
                   ("Oh. I see - is your chicken there?", "My chicken?!?! umm, no..."),
                   ("Ok, then I'd better explain.\nWe're at war with a race of extra-dimensional aliens.\n"+\
                    "These aliens can't completely fit into our dimension,\ninstead they have to confine themselves\nto geometric shapes.",
                    "<continue>"),
                   ("Your chicken is an advanced mutated commando,\nand was fowl-napped while investigating\nthat crop-circle.\n"+\
                    "Oh, btw - that crop circle was actually\nthe outline of the alien mothership.\n"+\
                    "Anyway, we lost communication with Chicken\nshortly after he got on board.\nok...\n"+\
                    "Now to explain your mission.",
                    "My WHAT?!?!"),
                   ("Your mission, please pay attention.", "*whispers* should have stayed in the house...")]
        cont_qa = [("Your objectives are simple, destroy the alien ship\nand rescue Chicken.",
                    "Blow the ship? How am I supposed to do that?"),
                   ("The ship is controlled by one very powerful alien,\nChicken will probably be kept near him.\n"+\
                    "Once the alien controller is dead,\nthe ship will lose control and start falling apart.",
                    "Wow, that sounds pretty easy..."),
                   ('"Easier said than done" could never be more true,\nthe controller is exceedinly strong.',
                    "Umm, then how am I supposed to kill it?"),
                   ("Chicken had several weapons when he entered the ship,\nand would not have gone down without a fight.\n"+\
                    "He probably dropped weapons throughout the ship.\nLuckily, the aliens don't understand\n"+\
                    "the concept of our weapons, and probably ignored them.",
                    "Nice, an enemy even dumber than me!\nSo how do I find Chicken and the controller?"),
                   ("Ahem, Chicken probably lost a few feathers\nfighting his captors.\nFollow and collect them.\n"+\
                    "Once you have all the feathers in an area\na teleporter chip will be activated\nto the next level.",
                    "Interesting... anything else I should know?"),
                   ("That should be plenty - good luck Farmer!", "Then let's do this!\n...\nhey! wait a second\nwhy do I have to do this?"),
                   ("Because, we haven't managed to get a single\nsoldier onto that mother ship yet!\n"+\
                    "So, we aren't gonna let this opportunity\nescape us!\n"+\
                    "Not to mention, you and Chicken\nare linked... somehow.\nGood luck soldier.", "ok... better get moving...")]

        self.console_app_discussions_intro = intro_qa + cont_qa
        self._console_swap_point = len(intro_qa)
        self.console_last_index = 0
        self._console_repeat_stor = {} #so we don't have this issue again!

        self.active_app = None

        self.app_binding = {"console":self.console_app_discussions_intro[0]}
        self.grab_events = False


        #target image
        self.target = pyggel.image.Image(data.image_path("target.png"),
                                         pos=(320-32, 240-32))
        self.target_active = pyggel.image.Image(data.image_path("target_over.png"),
                                                pos=(320-32,240-32))

        self.hud_image = pyggel.image.Image(data.image_path("hud1.png"))
        self.logo_image = pyggel.image.Image(data.image_path("chickenstein_logo.png"))
        self.logo_image.colorize = (1,1,1,0.5)

        self.ouch_image = pyggel.image.Image(data.image_path("ouch.png"))
        self.ouch_image.colorize = (1,1,1,0)

        self.paused = self.big_font.make_text_image("Paused - hit 'p' to start again...", color=(0,0,0,1))
        self.paused.pos = 320-self.paused.get_width()/2, 240-self.paused.get_height()/2
        self.paused.visible = False

        #for 3d sounds...
        self.sfx = sfx.SFX()

    def reset(self):
        self.ouch_image.colorize = (1,1,1,0)
        self.gui_inactive()

    def got_hit(self):
        self.ouch_image.colorize = 1,1,1,1

    def _set_active_app_internal_cadi_next(self):
        app = self.console_last_index
        if app < len(self.console_app_discussions_intro):
            self.console_last_index += 1

            if app in self._console_repeat_stor:
                app = self._console_repeat_stor[app]
            else:
                label = self.console_app_discussions_intro[app]

                app = pyggel.gui.App(self.event_handler)
                app.theme = self.core_theme
                app.update_fonts(self.core_fonts)
                app.packer.packtype = "center"
                pyggel.gui.Label(app, label[0], font_color=(0,0,0,1), font_color_inactive=(0,0,0,1))
                pyggel.gui.NewLine(app)

                pyggel.gui.Button(app, label[1], callbacks=[lambda:self._set_active_app_internal_cadi_next()])
                self._console_repeat_stor[self.console_last_index-1] = app

            self.active_app = app
            app.activate()
        else:
            self.console_last_index = self._console_swap_point
            self.gui_inactive()

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
            if name == "console":
                self._set_active_app_internal_cadi_next()
                self.gui_active()
            else:
                self.active_app = self.app_binding[name]
                self.gui_active()
        else:
            print name, "not in bindings!"
            self.gui_inactive()

    def set_hover_status(self, text):
        self.cur_text = text

    def update_feathers(self, have, max):
        text = "{feather} %s/%s"%(have, max)
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
        self.sfx.update()
        if self.active_app:
            self.active_app.render()

        else:
            a,b,c,d = self.ouch_image.colorize
            if d <= 0:
                d = 0

            if d:
                self.ouch_image.render()
                d -= 0.025
                self.ouch_image.colorize = a,b,c,d
            self.logo_image.render()
            self.hud_image.render()

            if self.cur_text:
                img = self.hover_status[self.cur_text]
                x,y = 320, 65
                img.pos = x-img.get_width()/2, y
                img.render()
                img.pos = x,y
                self.target_active.render()
            else:
                self.target.render()

            self.feathers.render()
            self.hp.render()
            self.weapon.render()
            self.ammo.render()

            if self.paused.visible:
                self.paused.render()
