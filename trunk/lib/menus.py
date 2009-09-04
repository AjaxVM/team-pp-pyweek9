import pyggel
from pyggel import *

import data


class Menu(pyggel.scene.BaseSceneObject):
    def __init__(self):
        pyggel.scene.BaseSceneObject.__init__(self)

        self.event_handler = pyggel.event.Handler()

        self.app = pyggel.gui.App(self.event_handler)
        self.app.theme.load(data.gui_path("theme.py"))
        frame = pyggel.gui.Frame(self.app, pos=(500,350), size=(100,100))
        frame.packer.packtype = "center"
        pyggel.gui.Button(frame, "play", callbacks=[self.set_play])
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

            
