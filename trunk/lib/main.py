
import pyggel
from pyggel import *

import data, hud

class LevelData(object):
    """WIP - for pathfinding and such later!"""
    def __init__(self, data):
        self.data = data

    def get_data_at(self, x, y):
        return self.data[y][len(self.data[y])-1-x]

class VertDoor(pyggel.geometry.Cube):
    def __init__(self, size, _tex, _pos):
        pyggel.geometry.Cube.__init__(self, size, texture=_tex, pos=_pos)
        self.scale = (0.25, 0.8, 1)
        x, y, z = _pos
        self.sphere = pyggel.geometry.Sphere(1, (x,size/2,z),
                                             colorize=(0,1,0,1))
        self.band = pyggel.geometry.Cube(size/5, pos=(x,size/2,z),
                                         colorize=(0.75,0,0.75,1))
        self.band.scale = (1.5,2,5)
        self.hide = False

        self.off_height = 0
        self.orig_pos = _pos

    def picked(self):
        self.hide = True
        self.game_hud.set_hover_status("door")

    def render(self, camera=None):
        if self.hide:
            self.sphere.colorize = (0,1,0,1)
            self.band.colorize = (0.75,0,0.75,1)
            if abs(camera.posx-self.pos[0]) + abs(camera.posz-self.pos[2]) > 15:
                self.hide = False
                self.sphere.colorize = (0.25,0.25,0.25,1)
                self.band.colorize = (0.2,0.2,0.2,1)
                self.off_height -= 0.1
            else:
                self.off_height += 0.1
        else:
            self.sphere.colorize = (0.25,0.25,0.25,1)
            self.band.colorize = (0.2,0.2,0.2,1)
            self.off_height -= 0.1
        if self.off_height < 0:
            self.off_height = 0
        if self.off_height > self.size:
            self.off_height = self.size

        self.pos = self.orig_pos[0], self.orig_pos[1]+self.off_height, self.orig_pos[2]
        pyggel.geometry.Cube.render(self, camera)
        self.sphere.render(camera)
        self.band.render(camera)

class HorzDoor(VertDoor, pyggel.geometry.Cube):
    def __init__(self, size, _tex, _pos):
        pyggel.geometry.Cube.__init__(self, size, texture=_tex, pos=_pos)
        self.scale = (1, 0.8, 0.25)
        x, y, z = _pos
        self.sphere = pyggel.geometry.Sphere(1, (x,size/2,z),
                                             colorize=(0,1,0,1))
        self.band = pyggel.geometry.Cube(size/5, pos=(x,size/2,z),
                                         colorize=(0.75,0,0.75,1))
        self.band.scale = (5,2,1.5)
        self.hide = False

        self.off_height = 0
        self.orig_pos = _pos

def get_geoms(level):
    tsize = 5.0
    fname = data.level_path(level)

    _data = []
    for line in open(fname):
        if not line.split(): #if it's blank:
            continue
        if line.startswith("//"):
            continue

        _data.append(line.strip())

    _data = "\n".join(_data)

    static = []
    dynamic = []

    commands = _data.split(":")
    commands = [i.strip() for i in commands if i]
    tile_set = "dungeon"
    fog_color = (1,1,1)
    map_grid = None

    for i in xrange(0, len(commands), 2):
        com = commands[i]
        val = commands[i+1]
        if com == "tile_set":
            tile_set = val
        if com == "fog_color":
            fog_color = tuple(map(float, val.split(",")))
        if com == "map":
            val = val.split()
            map_grid = val
            height = len(val)
            width = len(val[0])
            mwh = max((width, height))
            floor = pyggel.geometry.Plane(mwh*tsize, pos=(width*tsize/2,-tsize/2,height*tsize/2),
                                          texture=pyggel.data.Texture(data.image_path(tile_set+"_"+"floor.png")),
                                          tile=mwh*tsize)
            ceiling = pyggel.geometry.Plane(mwh*tsize, pos=(width*tsize/2,tsize/2,height*tsize/2),
                                          texture=pyggel.data.Texture(data.image_path(tile_set+"_"+"ceiling.png")),
                                          tile=mwh*tsize)
            static.append(floor)
            static.append(ceiling)
            for y in xrange(height):
                for x in xrange(width):
                    cur = val[height-1-y][x]
                    wall_tex = pyggel.data.Texture(data.image_path(tile_set+"_"+"wall.png")) #will want a few different later!
                    door_tex = pyggel.data.Texture(data.image_path(tile_set+"_"+"door.png"))
                    if cur == "#":
                        cube = pyggel.geometry.Cube(tsize,
                                                    texture=wall_tex,
                                                    pos=(x*tsize,0,y*tsize))
                        static.append(cube)
                    if cur == "|":
                        dynamic.append(VertDoor(tsize, door_tex, (x*tsize, -tsize/11, y*tsize)))
                    if cur == "_":
                        dynamic.append(HorzDoor(tsize, door_tex, (x*tsize, -tsize/11, y*tsize)))
    return (pyggel.misc.StaticObjectGroup(static), dynamic,
            fog_color, tile_set,
            LevelData(map_grid))

def main():
    pyggel.init()

    camera = pyggel.camera.LookFromCamera((10,0,10))
    light = pyggel.light.Light((0,100,0), (0.5,0.5,0.5,1),
                                  (1,1,1,1), (50,50,50,10),
                                  (0,0,0), True)

    scene = pyggel.scene.Scene()
    scene.pick = True
    scene.add_light(light)

    static, dynamic, fog_color, tile_set, level_data = get_geoms("level1.txt")
    pyggel.view.set_fog_color(fog_color)
    pyggel.view.set_fog_depth(5, 60)
    pyggel.view.set_background_color(fog_color[:3])
    static.pickable = True
    scene.add_3d(static)
    scene.add_3d(dynamic)

    game_hud = hud.Hud()
    scene.add_2d(game_hud)
    for i in dynamic:
        i.game_hud = game_hud

    clock = pygame.time.Clock()
    event = pyggel.event.Handler()

    while 1:
        clock.tick(999)
        pyggel.view.set_title("FPS: %s"%clock.get_fps())

        event.update()
        if event.quit:
            pyggel.quit()
            return None

        if K_LEFT in event.keyboard.active:
            camera.roty -= .5
        if K_RIGHT in event.keyboard.active:
            camera.roty += .5
        if K_UP in event.keyboard.active:
            camera.roty *= -1
            camera.set_pos(pyggel.math3d.move_with_rotation(camera.get_pos(),
                                                            camera.get_rotation(),
                                                            0.05))
            camera.roty *= -1
        if K_DOWN in event.keyboard.active:
            camera.roty *= -1
            camera.set_pos(pyggel.math3d.move_with_rotation(camera.get_pos(),
                                                            camera.get_rotation(),
                                                            -0.05))
            camera.roty *= -1

        pyggel.view.clear_screen()

        pick = scene.render(camera)
        if hasattr(pick, "picked"):
            pick.picked()
        else:
            game_hud.set_hover_status(None)

        pyggel.view.refresh_screen()
