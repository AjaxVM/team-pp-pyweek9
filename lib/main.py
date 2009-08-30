
import pyggel
from pyggel import *

import data


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

##    commands = [i.strip() for i in _data.split()]
    commands = _data.split(":")
    commands = [i.strip() for i in commands if i]
    tile_set = "dungeon"
    fog_color = (1,1,1)

    for i in xrange(0, len(commands), 2):
        com = commands[i]
        val = commands[i+1]
        if com == "tile_set":
            tile_set = val
        if com == "fog_color":
            fog_color = tuple(map(float, val.split(",")))
        if com == "map":
            GRID = []
            val = val.split()
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
                    if cur == "#":
                        cube = pyggel.geometry.Cube(tsize,
                                                    texture=wall_tex,
                                                    pos=(x*tsize,0,y*tsize))
                        static.append(cube)
    return pyggel.misc.StaticObjectGroup(static), fog_color, tile_set

def main():
    pyggel.init()

    camera = pyggel.camera.LookFromCamera((10,0,10))
    light = pyggel.light.Light((0,100,0), (0.5,0.5,0.5,1),
                                  (1,1,1,1), (50,50,50,10),
                                  (0,0,0), True)

    scene = pyggel.scene.Scene()
    scene.add_light(light)

    static, fog_color, tile_set = get_geoms("level1.txt")
    pyggel.view.set_fog_color(fog_color)
    pyggel.view.set_fog_depth(5, 60)
    pyggel.view.set_background_color(fog_color[:3])
    scene.add_3d(static)

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
        scene.render(camera)
        pyggel.view.refresh_screen()
