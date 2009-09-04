import pyggel
from pyggel import *

import data, hud
import random, math

from weapons import *
from buffs import *
from aliens import *

class LevelData(object):
    """WIP - for pathfinding and such later!"""
    def __init__(self, data, tsize):
        self.data = data
        self.height = len(data)
        self.width = len(data[0])
        self.tsize = tsize

        self.collidable = ["#", "@"]

    def get_data_at(self, x, y):
        try:
            return self.data[self.height-1-y][x]
        except:
            return ""

    def convert_pos(self, x, y):
        return (int(pyggel.math3d.safe_div(x+self.tsize/2, self.tsize)),
                int(pyggel.math3d.safe_div(y+self.tsize/2, self.tsize)))

    def get_at_uncon(self, x, y):
        return self.get_data_at(*self.convert_pos(x, y))

class VertDoor(pyggel.geometry.Cube):
    def __init__(self, size, _tex, _pos):
        pyggel.geometry.Cube.__init__(self, size, texture=_tex, pos=_pos)
        self.scale = (0.25, 0.8, 1)
        x, y, z = _pos
        bar_tex = pyggel.data.Texture(data.image_path("door_bar.png"))
        self.sphere = pyggel.geometry.Sphere(1, (x,size/2,z),
                                             colorize=(0,1,0,1),
                                             texture=bar_tex)
        self.band = pyggel.geometry.Cube(size/5, pos=(x,size/2,z),
                                         colorize=(0.75,0,0.75,1),
                                         texture=bar_tex,
                                         mirror=True)
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
            if pyggel.math3d.get_distance((camera.posx, 0, camera.posz), (self.pos[0], 0, self.pos[2])) > self.size*2:
                self.hide = False
                self.sphere.colorize = (0.25,0.25,0.25,1)
                self.band.colorize = (0.2,0.2,0.2,1)
                self.off_height -= 0.1
            else:
                if self.off_height < self.size-self.size/4:
                    self.game_hud.sfx.open_door()
                self.off_height += 0.1
        else:
            self.sphere.colorize = (0.25,0.25,0.25,1)
            self.band.colorize = (0.2,0.2,0.2,1)
            self.off_height -= 0.1
        if self.off_height < 0:
            self.off_height = 0
        if self.off_height > self.size-self.size/4:
            self.off_height = self.size-self.size/4

        self.pos = self.orig_pos[0], self.orig_pos[1]+self.off_height, self.orig_pos[2]
        pyggel.geometry.Cube.render(self, camera)
        self.sphere.render(camera)
        self.band.render(camera)

class HorzDoor(VertDoor, pyggel.geometry.Cube):
    def __init__(self, size, _tex, _pos):
        pyggel.geometry.Cube.__init__(self, size, texture=_tex, pos=_pos)
        self.scale = (1, 0.8, 0.25)
        x, y, z = _pos
        bar_tex = pyggel.data.Texture(data.image_path("door_bar.png"))
        self.sphere = pyggel.geometry.Sphere(1, (x,size/2,z),
                                             colorize=(0,1,0,1),
                                             texture=bar_tex)
        self.band = pyggel.geometry.Cube(size/5, pos=(x,size/2,z),
                                         colorize=(0.75,0,0.75,1),
                                         texture=bar_tex, mirror=True)
        self.band.scale = (5,2,1.5)
        self.hide = False

        self.off_height = 0
        self.orig_pos = _pos

class Feather(pyggel.scene.BaseSceneObject):
    objs = []
    def __init__(self, pos):
        if not self.objs:
            self.objs.append(pyggel.mesh.OBJ(data.mesh_path("feather_test.obj")))
        pyggel.scene.BaseSceneObject.__init__(self)
        self.pos = pos

        self.obj = random.choice(self.objs)
        self.rotation = 25,0,0

    def picked(self):
        self.game_hud.set_hover_status("feather")

    def update(self):
        x, y, z = self.rotation
        y += 2
        self.rotation = x, y, z

    def render(self, camera=None):
        self.update()
        self.obj.pos = self.pos
        self.obj.rotation = self.rotation
        self.obj.render(camera)

class Console(pyggel.scene.BaseSceneObject):
    obj = None
    def __init__(self, pos):
        if not Console.obj:
            Console.obj = pyggel.mesh.OBJ(data.mesh_path("alien_console.obj"))
            Console.obj.scale = 1.5,2,1 #tsize
            Console.obj.rotation = 0,180,0

        pyggel.scene.BaseSceneObject.__init__(self)

        x,y,z = pos
        z += 1.25
        self.pos = x, y, z

    def picked(self):
        self.game_hud.set_hover_status("starting_console")

    def render(self, camera=None):
        self.obj.pos = self.pos
        self.obj.render(camera)

def get_geoms(level):
    tsize = 5.0
    fname = data.level_path("level%s.txt"%level)

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

    baddies = []
    feathers = []

    commands = _data.split(":")
    commands = [i.strip() for i in commands if i]
    tile_set = "dungeon"
    fog_color = (1,1,1)
    map_grid = None
    last_level = False

    camera_pos = (2,0,2)

    possible_gun_locations = []
    possible_boost_locations = []

    for i in xrange(0, len(commands), 2):
        com = commands[i]
        val = commands[i+1]
        if com == "tile_set":
            tile_set = val
        if com == "fog_color":
            fog_color = tuple(map(float, val.split(",")))
        if com == "last_level":
            if val in ("True", "true"):
                last_level = True
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
                    if cur == "*":
                        camera_pos = x*tsize, 0, y*tsize
                    if cur == "~":
                        feathers.append(Feather((x*tsize, 0, y*tsize)))
                    if cur in ("a","b","c","d","e"):
                        weights = {"a":"handgun",
                                   "b":"shotgun",
                                   "c":"chaingun",
                                   "d":"lightning gun",
                                   "e":"plasma gun"}
                        possible_gun_locations.append((x, y, weights[cur]))
                    if cur == "$":
                        possible_boost_locations.append((x, y))
                    if cur in ("1", "2", "3", "4", "5", "6", "7"):
                        weights = {"1":"quad",
                                   "2":"pyramid",
                                   "3":"dpyramid",
                                   "4":"cube",
                                   "5":"sphere",
                                   "6":"ellipsoid",
                                   "7":"boss"}
                        baddies.append(Alien((x*tsize, 0, y*tsize), weights[cur]))
                    if cur == "@":
                        dynamic.append(Console((x*tsize, 0, y*tsize)))

    for i in possible_gun_locations:
        dynamic.append(Weapon((i[0]*tsize, 0, i[1]*tsize), i[2]))
    if possible_boost_locations:
        t = 0
        for i in xrange(len(possible_boost_locations)/2):
            pick = random.choice(possible_boost_locations)
            t = 1-t
            possible_boost_locations.remove(pick)
            if t == 0: #health
                dynamic.append(HPBuff((pick[0]*tsize, 0, pick[1]*tsize)))
            else:
                dynamic.append(AmmoBuff((pick[0]*tsize, 0, pick[1]*tsize)))
    l = LevelData(map_grid, tsize)
    for i in baddies:
        i.build_connections(baddies, l)
    return (pyggel.misc.StaticObjectGroup(static), dynamic,
            baddies, feathers,
            camera_pos,
            fog_color, tile_set,
            l, tsize, last_level)
