import pyggel
from pyggel import *

import data


class Menu(pyggel.scene.BaseSceneObject):
    def __init__(self):
        pyggel.scene.BaseSceneObject.__init__(self)

        self.event_handler = pyggel.event.Handler()

        self.app = pyggel.gui.App(self.event_handler)
        self.app.theme.load(data.gui_path("theme.py"))
        frame = pyggel.gui.Frame(self.app, pos=(500,300), size=(100,125), background_image=None)
        frame.packer.packtype = "center"
        pyggel.gui.Button(frame, "play", callbacks=[self.set_play])
        pyggel.gui.NewLine(frame)
        pyggel.gui.Button(frame, "story", callbacks=[self.set_story])
        pyggel.gui.NewLine(frame)
        pyggel.gui.Button(frame, "quit", callbacks=[self.set_quit])

        self.background_image = pyggel.image.Image(data.image_path("background_crop_circle.png"))

        self.scene = pyggel.scene.Scene()
        self.scene.add_2d(self.background_image)
        self.scene.add_2d(self.app)

        self.have_event = False
        self.event = None

    def set_play(self):
        self.have_event = True
        self.event = "play"

    def set_quit(self):
        self.have_event = True
        self.event = "quit"

    def set_story(self):
        self.have_event = True
        self.event = "story"

    def run(self):
        clock = pygame.time.Clock()
        self.have_event = False
        self.event = None
        pygame.event.set_grab(0)
        pygame.mouse.set_visible(1)
        while not self.have_event:
            clock.tick(30)

            self.event_handler.update()

            if self.event_handler.quit or K_ESCAPE in self.event_handler.keyboard.hit:
                return ["quit"]

            pyggel.view.clear_screen()
            self.scene.render()
            pyggel.view.refresh_screen()
        return [self.event]

class StoryMenu(pyggel.scene.BaseSceneObject):
    def __init__(self):
        pyggel.scene.BaseSceneObject.__init__(self)

        self.event_handler = pyggel.event.Handler()

        self.app = pyggel.gui.App(self.event_handler)
        self.app.theme.load(data.gui_path("theme.py"))
        frame = pyggel.gui.Frame(self.app, pos=(500,300), size=(100,125), background_image=None)
        frame.packer.packtype = "center"
        pyggel.gui.Button(frame, "Play", callbacks=[self.set_play])
        pyggel.gui.NewLine(frame)
        pyggel.gui.Button(frame, "Back", callbacks=[self.set_back])

        f = open(data.misc_path("intro_story.txt"), "rU")
        text = ""
        for line in f:
            text += line.strip() + "\n"

        pyggel.gui.Label(self.app, text, font_color=(0,0,0,1), font_color_inactive=(0,0,0,1),
                         font="default-small")

        self.background_image = pyggel.image.Image(data.image_path("background_crop_circle.png"))

        self.scene = pyggel.scene.Scene()
        self.scene.add_2d(self.background_image)
        self.scene.add_2d(self.app)

        self.have_event = False
        self.event = None

    def set_play(self):
        self.have_event = True
        self.event = "play"

    def set_back(self):
        self.have_event = True
        self.event = "menu"

    def run(self):
        clock = pygame.time.Clock()
        self.have_event = False
        self.event = None
        pygame.event.set_grab(0)
        pygame.mouse.set_visible(1)
        while not self.have_event:
            clock.tick(30)

            self.event_handler.update()

            if self.event_handler.quit or K_ESCAPE in self.event_handler.keyboard.hit:
                return ["quit"]

            pyggel.view.clear_screen()
            self.scene.render()
            pyggel.view.refresh_screen()
        return [self.event]

            
