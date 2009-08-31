
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

class Weapon(pyggel.scene.BaseSceneObject):
    objs = {}
    def __init__(self, pos, name):
        if not self.objs:
            self.objs["shotgun"] = pyggel.mesh.OBJ(data.mesh_path("shotgun.obj"))
        pyggel.scene.BaseSceneObject.__init__(self)
        self.pos = pos

        self.obj = self.objs[name]
        self.rotation = 25, 0, 0
        self.name = name
        if self.name == "shotgun":
            self.base_ammo = 20
        else:
            self.base_ammo = 100

    def picked(self):
        self.game_hud.set_hover_status("shotgun")

    def update(self):
        x, y, z = self.rotation
        y += 2
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
    bosses = []
    feathers = []

    weps_per_level = {1: "shotgun"}

    commands = _data.split(":")
    commands = [i.strip() for i in commands if i]
    tile_set = "dungeon"
    fog_color = (1,1,1)
    map_grid = None

    camera_pos = (2,0,2)

    possible_gun_locations = []

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
                    if cur == "&":
                        possible_gun_locations.append((x, y))

    if possible_gun_locations:
        pick = random.choice(possible_gun_locations)
        dynamic.append(Weapon((pick[0]*tsize, 0, pick[1]*tsize), weps_per_level[level]))
    return (pyggel.misc.StaticObjectGroup(static), dynamic,
            baddies, bosses, feathers,
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

        self.weapon_bucked = False
        self.weapon_buck_back = 0
        self.weapon_buck_twist = 0
        self.weapon_changes = (0,0)
        self.weapon_buck_done = True

        self.game_hud = None

    def add_weapon(self, wep_type, mesh, ammo=100):
        self.weapons[wep_type] = [mesh, ammo]
        self.cur_weapon = wep_type

    def hit(self, damage):
        self.cur_hp -= damage
        self.game_hud.update_hp(self.cur_hp)

    def boost_hp(self, amount):
        self.cur_hp += amount
        if self.cur_hp >= self.max_hp:
            self.cur_hp = self.max_hp
        self.game_hud.update_hp(self.cur_hp)

    def swap_weapon(self, scene, new):
        try:
            scene.remove_3d_after(self.weapons[self.cur_weapon][0])
        except:
            pass

        self.cur_weapon = new
        self.game_hud.update_weapon(new)
        if new:
            scene.add_3d_after(self.weapons[new][0])
            self.weapons[new][0].pickable = False
            self.game_hud.update_ammo(self.weapons[new][1])
        else:
            self.game_hud.update_ammo(0)

    def update_weapon(self, camera):
        if self.cur_weapon:
            if self.weapon_bucked:
                x, y = self.weapon_changes
                x += self.weapon_buck_back
                y += self.weapon_buck_twist
                if self.cur_weapon == "shotgun" and x >= self.weapon_buck_back*7:
                    x = self.weapon_buck_back * 7
                    y = self.weapon_buck_twist * 7
                    self.weapon_bucked = False
                self.weapon_changes = x, y
            elif not self.weapon_buck_done:
                x, y = self.weapon_changes
                if x:
                    x -= self.weapon_buck_back/4
                    if x <= 0:
                        x = 0
                    y -= self.weapon_buck_twist/4
                else:
                    y = 0
                    self.weapon_buck_done = True
                self.weapon_changes = x, y
            obj = self.weapons[self.cur_weapon][0]
            obj.scale = 0.5
            x, y, z = camera.get_pos()
            roty = camera.roty
            x, y, z = pyggel.math3d.move_with_rotation((x, y, z), (0,-roty,0), 2.25-self.weapon_changes[0])
            x, y, z = pyggel.math3d.move_with_rotation((x, y, z), (0,-roty+45,0), -.75)
            y -= 0.25
            obj.pos = x, y, z
            obj.rotation = (0,180-roty+self.weapon_changes[1],-20-self.weapon_changes[1])

    def fire(self, scene):
        if self.cur_weapon == "shotgun":
            if self.weapon_buck_done: #other types maybe don't need this
                if self.weapons[self.cur_weapon][1]:
                    self.weapons[self.cur_weapon][1] -= 1
                    self.weapon_bucked = True
                    self.weapon_buck_back = 0.1
                    self.weapon_buck_twist = -3
                    self.weapon_buck_done = False
                    self.game_hud.update_ammo(self.weapons[self.cur_weapon][1])

def play_level(level, player_data):
    camera = pyggel.camera.LookFromCamera((10,0,10))
    light = pyggel.light.Light((0,100,0), (0.5,0.5,0.5,1),
                                  (1,1,1,1), (50,50,50,10),
                                  (0,0,0), True)

    scene = pyggel.scene.Scene()
    scene.pick = True
    scene.add_light(light)

    collidable = ["#"] #TODO: add other collidables!

    static, dynamic, baddies, bosses, feathers, camera_pos, fog_color, tile_set, level_data, tsize = get_geoms(level)
    camera.set_pos(camera_pos)
    pyggel.view.set_fog_color(fog_color)
    pyggel.view.set_fog_depth(5, 60)
    pyggel.view.set_background_color(fog_color[:3])
    static.pickable = True

    transition_buffer = pyggel.data.TextureBuffer(clear_color=fog_color[:3])
    #This is for going to the next level...

    scene.add_3d(static)
    scene.add_3d(dynamic)
    scene.add_3d(baddies)
    scene.add_3d(bosses)
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

    player_data.game_hud = game_hud

    player_data.swap_weapon(scene, player_data.cur_weapon)
    player_data.update_weapon(camera)

    scene.render_buffer = transition_buffer
    scene.pick = False
    game_hud.visible = False
    scene.render(camera) #make sure we only pick the center!
    do_transition(transition_buffer, False)
    game_hud.visible = True
    scene.pick = True
    scene.render_buffer = None

    event.update() #so the camera doesn't wig out the first time...

    while 1:
        clock.tick(999)
        pyggel.view.set_title("FPS: %s"%clock.get_fps())

        #Render first, since picking is done at this time, and we need that later!

        if have_feathers == len(feathers): #next round
            good = True
            for i in baddies:
                if i in scene.graph.render_3d:
                    good = False
                    break
            if good:
                scene.render_buffer = transition_buffer
                scene.pick = False
                game_hud.visible = False
                scene.render(camera) #make sure we only pick the center!
                return ["next", transition_buffer]

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
            return ["back"]

        if event.mouse.motion[0]:
            camera.roty += event.mouse.motion[0] * 0.1

        do_move = False
        if "w" in event.keyboard.active:
            camera.roty *= -1
            new = pyggel.math3d.move_with_rotation((0,0,0), camera.get_rotation(), 0.15)
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

        player_data.update_weapon(camera)

        if "right" in event.mouse.hit:
            if pick and pyggel.math3d.get_distance(camera.get_pos(), pick.pos) < tsize*3:
                if isinstance(pick, Feather):
                    have_feathers += 1
                    scene.remove_3d(pick)
                    game_hud.update_feathers(have_feathers, len(feathers))
                if isinstance(pick, Weapon):
                    scene.remove_3d(pick)
                    player_data.add_weapon(pick.name, pick.obj, pick.base_ammo)
                    player_data.swap_weapon(scene, pick.name)
        if "left" in event.mouse.hit:
            player_data.fire(scene)

def do_transition(buf, out=True):
    pyggel.view.set_lighting(False) #for now...
    glClearColor(0,0,0,0)
    tex = buf.texture
    tex.bind()
    glPushMatrix()
    if out:
        scale = 1.1
    else:
        scale = 0
    rot = 0

    for i in xrange(500):
        if out:
            scale -= 1.1/500
            rot += 360.0/500
        else:
            scale += 1.1/500
            rot -= 360.0/500
        pyggel.view.set3d()
        pyggel.view.clear_screen()

        glRotatef(rot,0,0,1)

        glBegin(GL_QUADS)
        glTexCoord2f(0,1)
        glVertex3f(-1*scale, 1*scale, -2)
        glTexCoord2f(0,0)
        glVertex3f(-1*scale,-1*scale, -2)
        glTexCoord2f(1,0)
        glVertex3f( 1*scale,-1*scale, -2)
        glTexCoord2f(1,1)
        glVertex3f( 1*scale, 1*scale, -2)
        glEnd()

        pyggel.view.refresh_screen()
    glPopMatrix()
    pyggel.view.set_lighting(True)
    glClearColor(*pyggel.view.screen.clear_color)

def main():
    pyggel.init()

    pData = PlayerData()

    level = 1

    while 1:
        retval = play_level(level, pData)
        command = retval[0]
        if command == "back":
            pyggel.quit()
            return None
        if command == "next":
            do_transition(retval[1])
            level += 1
            continue
