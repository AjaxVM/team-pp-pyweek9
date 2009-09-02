
import pyggel
from pyggel import *

import data, hud
import random, math

class LevelData(object):
    """WIP - for pathfinding and such later!"""
    def __init__(self, data, tsize):
        self.data = data
        self.height = len(data)
        self.width = len(data[0])
        self.tsize = tsize

        self.collidable = ["#"]

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
            self.objs.append(pyggel.misc.StaticObjectGroup(pyggel.mesh.OBJ(data.mesh_path("feather_test.obj"))))
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
            self.objs["shotgun"] = pyggel.misc.StaticObjectGroup([pyggel.mesh.OBJ(data.mesh_path("shotgun_OLD.obj"))])
            self.objs["shotgun"].pickable = True
        pyggel.scene.BaseSceneObject.__init__(self)
        self.pos = pos

        self.obj = self.objs[name]
        self.rotation = 25, 0, 0
        self.name = name

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

class HPBuff(pyggel.scene.BaseSceneObject):
    obj = None
    def __init__(self, pos):
        if not HPBuff.obj:
            HPBuff.obj = pyggel.geometry.Cube(2, texture=pyggel.data.Texture(data.image_path("hp_tex.png")), mirror=True)
        pyggel.scene.BaseSceneObject.__init__(self)
        self.pos = pos

        self.rotation = 25, 0, 0

    def picked(self):
        self.game_hud.set_hover_status("hp")

    def update(self):
        x, y, z = self.rotation
        y += 2
        self.rotation = x, y, z

    def render(self, camera=None):
        self.update()
        self.obj.pos = self.pos
        self.obj.rotation = self.rotation
        self.obj.render(camera)

class AmmoBuff(pyggel.scene.BaseSceneObject):
    obj = None
    def __init__(self, pos):
        if not AmmoBuff.obj:
            AmmoBuff.obj = pyggel.geometry.Cube(2, texture=pyggel.data.Texture(data.image_path("ammo_tex.png")), mirror=True)
        pyggel.scene.BaseSceneObject.__init__(self)
        self.pos = pos

        self.rotation = 25, 0, 0

    def picked(self):
        self.game_hud.set_hover_status("ammo")

    def update(self):
        x, y, z = self.rotation
        y += 2
        self.rotation = x, y, z

    def render(self, camera=None):
        self.update()
        self.obj.pos = self.pos
        self.obj.rotation = self.rotation
        self.obj.render(camera)

class ShotgunShot(pyggel.scene.BaseSceneObject):
    obj = None
    def __init__(self, pos, rotation, level_data, scene):
        if not ShotgunShot.obj:
            ShotgunShot.obj = pyggel.geometry.Sphere(0.1)
            ShotgunShot.obj.scale = (1,1,4)
            ShotgunShot.obj.colorize = (0.2,0.2,0.25)
        pyggel.scene.BaseSceneObject.__init__(self)

        self.scene = scene

        self.collision_body = pyggel.math3d.AABox(pos, 0.15)

        self.pos = pos
        self.rotation = rotation
        self.level_data = level_data
        self.puff_tick = 1
        self.damage = 4

    def render(self, camera=None):
        if self.dead_remove_from_scene:
            return
        self.pos = pyggel.math3d.move_with_rotation(self.pos, self.rotation, -.75)
        self.collision_body.set_pos(self.pos)
        if self.level_data.get_at_uncon(self.pos[0], self.pos[2]) in self.level_data.collidable:
            self.dead_remove_from_scene = True #kills object
        self.obj.pos = self.pos
        self.obj.rotation = self.rotation
        self.obj.render(camera)

        if self.puff_tick <= 20:
            self.scene.add_3d_blend(ShotgunPuff(self.pos, self.rotation, self.puff_tick))
            self.puff_tick += 1

class ShotgunPuff(pyggel.scene.BaseSceneObject):
    obj = None
    def __init__(self, pos, rotation, size=1):
        if not ShotgunPuff.obj:
            ShotgunPuff.obj = pyggel.image.Image3D(data.image_path("shotgun_puff.png"))
        pyggel.scene.BaseSceneObject.__init__(self)

        self.pos = pos
        self.rotation = rotation

        self.pos = pyggel.math3d.move_with_rotation(self.pos, self.rotation, -1)

        self.puff_scale = 0.075 * size
        self.puff_rotate = size*3
        self.puff_alpha = 0.5 - size*0.025

    def render(self, camera=None):
        self.obj.pos = self.pos
        self.obj.scale  = self.puff_scale
        self.obj.rotation = (0,0,self.puff_rotate)
        self.obj.colorize = (1,1,1,self.puff_alpha)
        self.obj.render(camera)

        self.dead_remove_from_scene = True

class Alien(pyggel.scene.BaseSceneObject):
    objs = {}
    texs = []
    def __init__(self, pos, kind="quad"):
        if not Alien.objs:
            Alien.objs["quad"] = pyggel.geometry.Quad(1)
            Alien.objs["cube"] = pyggel.geometry.Cube(1, mirror=True)
            Alien.objs["sphere"] = pyggel.geometry.Sphere(1)
            Alien.objs["ellipsoid"] = pyggel.geometry.Sphere(1)
            Alien.objs["ellipsoid"].scale = 1,2,1
            Alien.objs["pyramid"] = pyggel.geometry.Pyramid(2)
            Alien.objs["dpyramid"] = pyggel.geometry.DoublePyramid(2)
            Alien.texs.append(pyggel.data.Texture(data.image_path("alien_face1.png")))
        pyggel.scene.BaseSceneObject.__init__(self)

        self.pos = pos
        self.rotation = (0,0,0)
        self.obj = self.objs[kind]
        self.tex = random.choice(self.texs)
        self.kind = kind
        self.color = random.choice(((1,1,0.25,1), (0,1,0,1), (0,0,1,1)))

        self.collision_body = pyggel.math3d.AABox(self.pos, 1.5)

        self.got_hit = False
        self.hit_grow = True
        self.hit_scale = 0
        self.hit_scale_inc = 0.1
        all_hp = {"quad":4,
                  "pyramid":6,
                  "dpyramid":9,
                  "cube":14,
                  "sphere":30,
                  "ellipsoid":40}

        self.hp = all_hp[self.kind]
        self.dead = False
        if kind == "ellpisoid":
            self.dead_scale = 2
            self.dead_scale_dec = 0.2
        else:
            self.dead_scale = 1
            self.dead_scale_dec = 0.1

    def update(self, player_pos, scene):
##        x = player_pos[0] - self.pos[0]
##        y = player_pos[2] - self.pos[2]
##        angle = math.atan2(-y, x)
##        angle = 90-(angle * 180.0)/math.pi
##        self.rotation = (self.rotation[0], angle, self.rotation[2])

        x, y, z = self.rotation
        y += 5
        self.rotation = x,y,z
        self.collision_body.set_pos(self.pos)

    def hit(self, damage):
        self.got_hit = True
        self.hp -= damage
        if self.hp <= 0:
            self.dead = True

    def render(self, camera=None):
        if self.dead:
            self.dead_scale -= self.dead_scale_dec
            if self.dead_scale <= 0:
                self.dead_remove_from_scene = True
                return
            oscale = self.dead_scale
        elif self.got_hit:
            self.obj.outline = True
            if self.hit_grow:
                self.hit_scale += self.hit_scale_inc
                if self.hit_scale >= 1:
                    self.hit_scale = 1
                    self.hit_grow = False
            else:
                self.hit_scale -= self.hit_scale_inc*2
                if self.hit_scale <= 0:
                    self.hit_scale = 0
                    self.got_hit = False
                    self.hit_grow = True
        else:
            self.obj.outline = False
        self.obj.pos = self.pos
        x, y, z = self.rotation
        self.obj.rotation = x, y, z
        self.obj.texture = self.tex
        self.obj.colorize = self.color

        oscale = self.dead_scale
        if self.kind == "quad": oscale += self.hit_scale
        self.obj.scale = 1+self.hit_scale, oscale, 1+self.hit_scale
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
    possible_boost_locations = []

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
                    if cur == "$":
                        possible_boost_locations.append((x, y))
                    if cur == "1":
                        baddies.append(Alien((x*tsize, 0, y*tsize), random.choice(["quad", "cube", "sphere",
                                                                                   "ellipsoid", "pyramid", "dpyramid"])))

    if possible_gun_locations:
        pick = random.choice(possible_gun_locations)
        dynamic.append(Weapon((pick[0]*tsize, 0, pick[1]*tsize), weps_per_level[level]))
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
        self.max_ammo = 100

        self.weapons = {}
        self.ammos = {"shotgun":20}
        self.kills = 0
        self.cur_weapon = None

        self.weapon_bucked = False
        self.weapon_buck_back = 0
        self.weapon_buck_twist = 0
        self.weapon_changes = (0,0)
        self.weapon_buck_done = True

        self.weapon_bob_d = 0.002
        self.weapon_bob_up = 0
        self.weapon_bob_rd = -0.2
        self.weapon_bob_rot = 0
        self.weapon_bob_count = 20

        self.game_hud = None

    def add_weapon(self, wep_type, mesh):
        self.weapons[wep_type] = mesh
        self.cur_weapon = wep_type

    def hit(self, damage):
        self.cur_hp -= damage
        self.game_hud.update_hp(self.cur_hp)

    def boost_hp(self, amount):
        self.cur_hp += amount
        if self.cur_hp >= self.max_hp:
            self.cur_hp = self.max_hp
        self.game_hud.update_hp(self.cur_hp)

    def boost_ammo(self, amount):
        for i in self.ammos:
            self.ammos[i] += amount
            if self.ammos[i] > self.max_ammo:
                self.ammos[i] = self.max_ammo
        if self.cur_weapon:
            self.game_hud.update_ammo(self.ammos[self.cur_weapon])

    def swap_weapon(self, scene, new):
        try:
            scene.remove_3d_after(self.weapons[self.cur_weapon])
        except:
            pass

        self.cur_weapon = new
        self.game_hud.update_weapon(new)
        if new:
            scene.add_3d_after(self.weapons[new])
            self.weapons[new].pickable = False
            self.game_hud.update_ammo(self.ammos[new])
        else:
            self.game_hud.update_ammo(0)

    def move(self):
        if self.cur_weapon:
            self.weapon_bob_up += self.weapon_bob_d
            self.weapon_bob_rot += self.weapon_bob_rd
            self.weapon_bob_count += 1
            if abs(self.weapon_bob_count) > 40:
                self.weapon_bob_d *= -1
                self.weapon_bob_rd *= -1
                self.weapon_bob_count = 0
        else:
            self.reset_move()
    def reset_move(self):
        self.weapon_bob_up = 0
        self.weapon_bob_rot = 0
        self.weapon_bob_count = 20

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
            obj = self.weapons[self.cur_weapon]
            obj.scale = 0.5
            x, y, z = camera.get_pos()
            roty = camera.roty
            x, y, z = pyggel.math3d.move_with_rotation((x, y, z), (0,-roty,0), 2.25-self.weapon_changes[0])
            x, y, z = pyggel.math3d.move_with_rotation((x, y, z), (0,-roty+45,0), -.75)
            y -= 0.25
            obj.pos = x, y+self.weapon_bob_up, z
            obj.rotation = (0,180-roty+self.weapon_changes[1]-self.weapon_bob_rot*0.2,
                            -20-self.weapon_changes[1]+self.weapon_bob_rot)

    def fire(self, scene, level_data):
        if self.cur_weapon == "shotgun":
            if self.weapon_buck_done: #other types maybe don't need this
                if self.ammos[self.cur_weapon]:
                    self.ammos[self.cur_weapon] -= 1
                    self.weapon_bucked = True
                    self.weapon_buck_back = 0.1
                    self.weapon_buck_twist = -3
                    self.weapon_buck_done = False
                    self.game_hud.update_ammo(self.ammos[self.cur_weapon])
                    return ShotgunShot(self.weapons[self.cur_weapon].pos,
                                       self.weapons[self.cur_weapon].rotation,
                                       level_data, scene)

def play_level(level, player_data):
    camera = pyggel.camera.LookFromCamera((10,0,10))
    light = pyggel.light.Light((0,100,0), (0.5,0.5,0.5,1),
                                  (1,1,1,1), (50,50,50,10),
                                  (0,0,0), True)

    scene = pyggel.scene.Scene()
    scene.pick = True
    scene.add_light(light)

    static, dynamic, baddies, bosses, feathers, camera_pos, fog_color, tile_set, level_data, tsize = get_geoms(level)
    shots = []
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
        new = (0,0,0)
        future = (0,0,0)
        if "w" in event.keyboard.active:
            new = pyggel.math3d.move_with_rotation(new,
                                                   (camera.rotx,camera.roty*-1, camera.rotz), 0.15)
            future = pyggel.math3d.move_with_rotation(future,
                                                      (camera.rotx,camera.roty*-1, camera.rotz), 1.25)
            do_move = True
        if "s" in event.keyboard.active:
            new = pyggel.math3d.move_with_rotation(new,
                                                   (camera.rotx,camera.roty*-1, camera.rotz), -0.15)
            future = pyggel.math3d.move_with_rotation(future,
                                                      (camera.rotx,camera.roty*-1, camera.rotz), -1.25)
            do_move = True

        if "a" in event.keyboard.active:
            new = pyggel.math3d.move_with_rotation(new,
                                                   (camera.rotx,camera.roty*-1+90, camera.rotz),
                                                   0.15)
            future = pyggel.math3d.move_with_rotation(future,
                                                   (camera.rotx,camera.roty*-1+90, camera.rotz),
                                                   1.25)
            do_move = True
        if "d" in event.keyboard.active:
            new = pyggel.math3d.move_with_rotation(new,
                                                   (camera.rotx,camera.roty*-1-90, camera.rotz),
                                                   0.15)
            future = pyggel.math3d.move_with_rotation(future,
                                                   (camera.rotx,camera.roty*-1-90, camera.rotz),
                                                   1.25)
            do_move = True

        if do_move:
            player_data.move()
            x = camera.posx + future[0]
            y = camera.posz + future[2]
            if not level_data.get_at_uncon(x, camera.posz) in level_data.collidable:
                camera.set_pos((camera.posx+new[0], camera.posy, camera.posz))
            if not level_data.get_at_uncon(camera.posx, y) in level_data.collidable:
                camera.set_pos((camera.posx, camera.posy, camera.posz+new[2]))
        else:
            player_data.reset_move()

        player_data.update_weapon(camera)

        for i in shots:
            if i.dead_remove_from_scene:
                shots.remove(i)
            else:
                for x in baddies:
                    if i.collision_body.collide(x.collision_body):
                        i.dead_remove_from_scene = True
                        x.hit(i.damage)
                        break

        for i in baddies:
            i.update(camera.get_pos(), scene)

        if "right" in event.mouse.hit:
            if pick and pyggel.math3d.get_distance(camera.get_pos(), pick.pos) < tsize*3:
                if isinstance(pick, Feather):
                    have_feathers += 1
                    scene.remove_3d(pick)
                    game_hud.update_feathers(have_feathers, len(feathers))
                if isinstance(pick, Weapon):
                    scene.remove_3d(pick)
                    player_data.add_weapon(pick.name, pick.obj)
                    player_data.swap_weapon(scene, pick.name)
                if isinstance(pick, HPBuff):
                    scene.remove_3d(pick)
                    player_data.boost_hp(20)
                if isinstance(pick, AmmoBuff):
                    scene.remove_3d(pick)
                    player_data.boost_ammo(25)
        if "left" in event.mouse.hit:
            shot = player_data.fire(scene, level_data)
            if shot:
                scene.add_3d(shot)
                shots.append(shot)

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
    pyggel.view.set_debug(False)

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
