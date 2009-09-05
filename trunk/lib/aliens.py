import pyggel
from pyggel import *

import data, hud
import random, math

class AlienShot(pyggel.scene.BaseSceneObject):
    obj = None
    def __init__(self, pos, rotation, color, level_data, far=False):
        if not AlienShot.obj:
            AlienShot.obj = pyggel.image.Image3D(data.image_path("flash.png"))
        pyggel.scene.BaseSceneObject.__init__(self)

        self.collision_body = pyggel.math3d.AABox(pos, 0.15)

        if far:
            dis = -3.5
        else:
            dis = -1.25
        self.pos = pyggel.math3d.move_with_rotation(pos, rotation, dis)
        self.rotation = rotation
        self.level_data = level_data
        self.color = color

        self.scale_up = True
        self.scale = 0.75
        self.twist = 0

        if self.color == (1,1,0.25,1):
            self.damage = 2
            self.speed = 8
        if self.color == (0,1,0,1):
            self.damage = 8
            self.speed = 4
        if self.color == (0,0,1,1):
            self.damage = 4
            self.speed = 6

    def render(self, camera=None):
        if self.scale_up:
            self.scale += 0.6
            if self.scale >= 4:
                self.scale = 4
                self.scale_up = False
        else:
            if self.scale > 0.25:
                self.scale -= 0.5
            else:
                self.scale = 0.25
                self.pos = pyggel.math3d.move_with_rotation(self.pos, self.rotation, -1*self.speed)
        if self.dead_remove_from_scene:
            return
        self.collision_body.set_pos(self.pos)
        if self.level_data.get_at_uncon(self.pos[0], self.pos[2]) in self.level_data.collidable:
            self.dead_remove_from_scene = True #kills object
        self.obj.pos = self.pos
        self.obj.scale = self.scale
        self.obj.colorize = self.color
        self.twist += 15
        self.obj.rotation = (0,0,self.twist)
        self.obj.render(camera)

class Alien(pyggel.scene.BaseSceneObject):
    objs = {}
    texs = []
    base_los_count = 0
    def __init__(self, pos, kind="quad"):
        if not Alien.objs:
            Alien.objs["quad"] = pyggel.geometry.Quad(1)
            Alien.objs["cube"] = pyggel.geometry.Cube(1, mirror=True)
            Alien.objs["sphere"] = pyggel.geometry.Sphere(1)
            Alien.objs["ellipsoid"] = pyggel.geometry.Sphere(1)
            Alien.objs["ellipsoid"].scale = 1,2,1
            Alien.objs["pyramid"] = pyggel.geometry.Pyramid(2)
            Alien.objs["dpyramid"] = pyggel.geometry.DoublePyramid(2)
            Alien.objs["boss"] = pyggel.geometry.DoublePyramid(5)
            Alien.objs["boss"].scale = 1,0.5,1
            Alien.texs.append(pyggel.data.Texture(data.image_path("alien_face1.png")))
        pyggel.scene.BaseSceneObject.__init__(self)

        self.pos = pos
        self.rotation = (0,0,0)
        self.obj = self.objs[kind]
        self.tex = random.choice(self.texs)
        self.kind = kind
        self.color = random.choice(((1,1,0.25,1), (0,1,0,1), (0,0,1,1)))

        if self.kind == "boss":
            self.collision_body = pyggel.math3d.AABox(self.pos, 3.5)
        else:
            self.collision_body = pyggel.math3d.AABox(self.pos, (1.5,5,1.5))

        self.got_hit = False
        self.hit_grow = True
        self.hit_scale = 0
        self.hit_scale_inc = 0.1
        all_hp = {"quad":4,
                  "pyramid":6,
                  "dpyramid":8,
                  "cube":10,
                  "sphere":15,
                  "ellipsoid":20,
                  "boss":200}

        self.hp = all_hp[self.kind]
        self.dead = False
        if kind == "ellipsoid":
            self.dead_scale = 2
            self.dead_scale_dec = 0.2
        else:
            self.dead_scale = 1
            self.dead_scale_dec = 0.1

        self.shot_count = 0
        self.noticed = False

        self.stored_LOS = False
        self.sLOS_count = Alien.base_los_count
        Alien.base_los_count += 1
        if Alien.base_los_count >= 25:
            Alien.base_los_count = 0
        self.connected_to = []

    def build_connections(self, others, level_data):
        for i in others:
            if not (i in self.connected_to or i == self):
                if abs(self.pos[0]-i.pos[0]) <= 8 and\
                   abs(self.pos[2]-i.pos[2]) <= 8: #one-ish tile
                    self.connected_to.append(i)
                    if not self in i.connected_to:
                        i.connected_to.append(self)

                    for x in i.connected_to:
                        if not (x in self.connected_to or x == self):
                            self.connected_to.append(x)
                    for x in self.connected_to:
                        if not (x in i.connected_to or x == i):
                            i.connected_to.append(x)

    def LOS_to(self, topos, level_data, angle):
        # this is probably issue 15 -- getting distance through the wall
        # easy fix is take this out,  'proper' fix is to use some pathing alg to see if
        # they are just around a corner or well beyond a wall
        #if pyggel.math3d.get_distance(topos, self.pos) <= 5:
        #    return True

        if pyggel.math3d.get_distance(topos, self.pos) >= 50:
            return False

        pos = self.pos
        see = True
        for i in xrange(50):
            pos = pyggel.math3d.move_with_rotation(pos, (0,angle,0), -4)
            if pyggel.math3d.get_distance(topos, pos) <= 5:
                return True
            if level_data.get_at_uncon(pos[0], pos[2]) in level_data.collidable:
                return False
        return False

    def make_aware(self):
        self.game_hud.sfx.play_alien_alert()
        self.noticed = True
        for i in self.connected_to:
            i.noticed = True

    def picked(self):
        self.game_hud.set_hover_status("%s//%s//%s//%s"%(self.color[0],self.color[1],self.color[2],self.kind))

    def update(self, player_pos, level_data):
        # disconnect with any killed peers -- probably to free up for garbage collection
        for i in self.connected_to:
            if i.dead_remove_from_scene:
                self.connected_to.remove(i)

        # spin model
        x, y, z = self.rotation
        y += 5
        self.rotation = x,y,z
        self.collision_body.set_pos(self.pos)

        # rotate toward player
        x = player_pos[0] - self.pos[0]
        y = player_pos[2] - self.pos[2]
        angle = math.atan2(-y, x)
        angle = 90-(angle * 180.0)/math.pi


        self.sLOS_count += 1
        if self.sLOS_count >= 30:
            self.stored_LOS = self.LOS_to(player_pos, level_data, angle)
            self.sLOS_count = 0
            if self.stored_LOS:
                if random.randint(0,1):
                    self.game_hud.sfx.play_alien_chatter()

        if (not self.noticed):
            if pyggel.math3d.get_distance(player_pos, self.pos) < level_data.tsize * 7:
                if self.stored_LOS:
                    self.make_aware()

        # if noticed and have a line of sight
        if self.noticed and self.stored_LOS:
            # increment shot counter
            self.shot_count += 1

            if not self.kind == "boss":
                # move toward the player every X ticks
                engage_distance = 15    # aliens stop moving toward you when they get this close
                movement = 0.5         # movement speed of the aliens
                if self.shot_count % 5 == 0 and math.hypot(player_pos[0]-self.pos[0], player_pos[2]-self.pos[2]) > engage_distance:
                    # move toward the player a little bit -- skip pathing  :)
                    # could inject bugs that get you stuck in walls though probably, depending
                    # on how the LOS raycast works
                    # should probably implement A* pathing when I have more time and have looked at how the level data works
            
                    x,y,z = self.pos
                    self.pos = x - (math.cos(math.radians(angle+90)) * movement), y, z - (math.sin(math.radians(angle+90)) * movement)
                    self.collision_body.set_pos(self.pos)
                
            # boss shoots a little faster
            if self.kind == "boss" and self.shot_count >= 50:
                self.shot_count = 0
                self.game_hud.sfx.alien_shoot()
                return [AlienShot(self.pos, (0,angle+random.randint(-4,4),0),
                                  random.choice(((1,1,0.25,1), (0,1,0,1), (0,0,1,1))),
                                  level_data, True) for i in xrange(5)]
            # regular alien shot
            elif self.shot_count >= 75:
                self.shot_count = 0
                self.game_hud.sfx.alien_shoot()
                return [AlienShot(self.pos, (0,angle,0), self.color, level_data)]

        else:
            self.shot_count = 45

    def hit(self, damage):
        self.game_hud.sfx.play_alien_hit()
        self.make_aware()
        self.stored_LOS = True
        self.got_hit = True
        self.hp -= damage
        if self.hp <= 0:
            self.game_hud.sfx.play_alien_die()
            if random.randint(0,1):
                self.game_hud.sfx.play_player_kill()
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
