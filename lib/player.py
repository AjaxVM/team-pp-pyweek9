import pyggel
from pyggel import *

from weapons import *

class PlayerData(object):
    def __init__(self):
        self.max_hp = 100
        self.cur_hp = 100
        self.max_ammo = 100

        self.weapons = {}
        self.ammos = {"shotgun":25,
                      "handgun":50}
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

        self.collision_body = pyggel.math3d.Sphere((0,0,0), 1)

    def add_weapon(self, scene, wep_type, mesh):
        self.weapons[wep_type] = mesh
        self.swap_weapon(scene, wep_type)

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

    def move(self, camera):
        self.collision_body.set_pos(camera.get_pos())
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
                if self.cur_weapon == "handgun" and x >= self.weapon_buck_back*3:
                    x = self.weapon_buck_back * 3
                    y = self.weapon_buck_twist * 3
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
        if self.cur_weapon == "handgun":
            if self.weapon_buck_done:
                if self.ammos[self.cur_weapon]:
                    self.ammos[self.cur_weapon] -= 1
                    self.weapon_bucked = True
                    self.weapon_buck_back = 0.2
                    self.weapon_buck_twist = -4
                    self.weapon_buck_done = False
                    self.game_hud.update_ammo(self.ammos[self.cur_weapon])
                    return HandgunShot(self.weapons[self.cur_weapon].pos,
                                       self.weapons[self.cur_weapon].rotation,
                                       level_data, scene)