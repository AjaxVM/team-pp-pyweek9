
import pyggel
from pyggel import *

import data, hud
import random

class LevelData(object):
    """WIP - for pathfinding and such later!"""
    def __init__(self, data, tsize):
        self.data = data
        self.height = len(data)
        self.width = len(data[0])
        self.tsize = tsize

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
            if pyggel.math3d.get_distance((camera.posx, 0, camera.posz), (self.pos[0], 0, self.pos[2])) > self.size*2:
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
        self.sphere = pyggel.geometry.Sphere(1, (x,size/2,z),
                                             colorize=(0,1,0,1))
        self.band = pyggel.geometry.Cube(size/5, pos=(x,size/2,z),
                                         colorize=(0.75,0,0.75,1))
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

    def picked(self):
        self.game_hud.set_hover_status("feather")

    def update(self):
        x, y, z = self.rotation
        y += 0.5
        self.rotation = x, y, z

    def render(self, camera=None):
        self.update()
        self.obj.pos = self.pos
        self.obj.rotation = self.rotation
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

    camera_pos = (2,0,2)

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
                    if cur == "*":
                        camera_pos = x*tsize, 0, y*tsize
                    if cur == "~":
                        feathers.append(Feather((x*tsize, 0, y*tsize)))
    return (pyggel.misc.StaticObjectGroup(static), dynamic,
            baddies, feathers,
            camera_pos,
            fog_color, tile_set,
            LevelData(map_grid, tsize),
            tsize)

class PlayerData(object):
    def __init__(self):
        self.max_hp = 100
        self.cur_hp = 100

        self.weapons = {}
        self.kills = 0
        self.cur_weapon = None

    def add_weapon(self, wep_type, ammo=100):
        self.weapons[wep_type] = ammo
        self.cur_weapon = wep_type

def play_level(level, player_data): #TODO: add controls for player data, like weapon, stats, etc.!
    camera = pyggel.camera.LookFromCamera((10,0,10))
    light = pyggel.light.Light((0,100,0), (0.5,0.5,0.5,1),
                                  (1,1,1,1), (50,50,50,10),
                                  (0,0,0), True)

    scene = pyggel.scene.Scene()
    scene.pick = True
    scene.add_light(light)

    collidable = ["#"] #TODO: add other collidables!

    static, dynamic, baddies, feathers, camera_pos, fog_color, tile_set, level_data, tsize = get_geoms(1)
    camera.set_pos(camera_pos)
    pyggel.view.set_fog_color(fog_color)
    pyggel.view.set_fog_depth(5, 60)
    pyggel.view.set_background_color(fog_color[:3])
    static.pickable = True
    scene.add_3d(static)
    scene.add_3d(dynamic)
    scene.add_3d(baddies)
    scene.add_3d(feathers)

    game_hud = hud.Hud()
    scene.add_2d(game_hud)
    for i in dynamic + feathers + baddies:
        i.game_hud = game_hud

    game_hud.update_feathers(0, len(feathers))
    have_feathers = 0

    clock = pygame.time.Clock()
    event = pyggel.event.Handler()

    #set up target:
    pygame.event.set_grab(1)
    pygame.mouse.set_visible(0)

    target = pyggel.image.Image(data.image_path("target.png"), pos=(320-32, 240-32))
    scene.add_2d(target)

    event.update() #so the camera doesn't wig out the first time...

    while 1:
        clock.tick(999)
        pyggel.view.set_title("FPS: %s"%clock.get_fps())

        #Render first, since picking is done at this time, and we need that later!

        pyggel.view.clear_screen()

        pick = scene.render(camera, (320,240)) #make sure we only pick the center!
        if hasattr(pick, "picked"):
            pick.picked()
        else:
            game_hud.set_hover_status(None)

        pyggel.view.refresh_screen()


        #Now events!
        event.update()
        if K_ESCAPE in event.keyboard.hit:
            return "back"

        if event.mouse.motion[0]:
            camera.roty += event.mouse.motion[0] * 0.1

        do_move = False
        if "w" in event.keyboard.active:
            camera.roty *= -1
            new = pyggel.math3d.move_with_rotation((0,0,0), camera.get_rotation(), 0.05)
            future = pyggel.math3d.move_with_rotation((0,0,0), camera.get_rotation(), 1.25)
            do_move = True
        if "s" in event.keyboard.active:
            camera.roty *= -1
            new = pyggel.math3d.move_with_rotation((0,0,0), camera.get_rotation(), -0.05)
            future = pyggel.math3d.move_with_rotation((0,0,0), camera.get_rotation(), -1.25)
            do_move = True

        if do_move:
            x = camera.posx + future[0]
            y = camera.posz + future[2]
            if not level_data.get_at_uncon(x, camera.posz) in collidable:
                camera.set_pos((camera.posx+new[0], camera.posy, camera.posz))
            if not level_data.get_at_uncon(camera.posx, y) in collidable:
                camera.set_pos((camera.posx, camera.posy, camera.posz+new[2]))
            camera.roty *= -1

        if "right" in event.mouse.hit:
            if pick and isinstance(pick, Feather) and\
               pyggel.math3d.get_distance(camera.get_pos(), pick.pos) < tsize*3:
                have_feathers += 1
                scene.remove_3d(pick)
                game_hud.update_feathers(have_feathers, len(feathers))

def main():
    pyggel.init()

    pData = PlayerData()

    retval = play_level(1, pData)
    if retval == "back":
        pyggel.quit()
        return None
