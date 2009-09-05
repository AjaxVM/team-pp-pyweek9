import pyggel
from pyggel import *

from weapons import *

class PlayerData(object):
    def __init__(self, hud):
        self.max_hp = 100
        self.cur_hp = 100

        self.game_hud = hud

        self.weapons = {}
        self.ammos = {"shotgun":25,
                      "handgun":50,
                      "plasma gun":25,
                      "chaingun":150}
        self.max_ammos = {"shotgun":50,
                          "handgun":75,
                          "plasma gun":40,
                          "chaingun":500}

        self.weapon_scroll_list = ["handgun", "shotgun", "chaingun", "plasma gun"]
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

        self.collision_body = pyggel.math3d.Sphere((0,0,0), 2)

    def next_weapon(self, scene):
        if self.weapons:
            cur = self.weapon_scroll_list.index(self.cur_weapon)
            cur += 1
            if cur >= 4:
                cur = 0
            while not self.weapon_scroll_list[cur] in self.weapons:
                cur += 1
                if cur >= 4:
                    cur = 0
            self.swap_weapon(scene, self.weapon_scroll_list[cur])

    def prev_weapon(self, scene):
        if self.weapons:
            cur = self.weapon_scroll_list.index(self.cur_weapon)
            cur -= 1
            if cur < 0:
                cur = 3
            while not self.weapon_scroll_list[cur] in self.weapons:
                cur -= 1
                if cur < 0:
                    cur = 3
            self.swap_weapon(scene, self.weapon_scroll_list[cur])

    def reset(self):
        self.cur_hp = 100
        self.weapons = {}
        self.ammos = {"shotgun":25,
                      "handgun":50,
                      "plasma gun":25,
                      "chaingun":150}
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

        self.game_hud.update_ammo(0)
        self.game_hud.update_weapon("None")
        self.game_hud.update_hp(100)

    def add_weapon(self, scene, wep_type, mesh):
        self.weapons[wep_type] = mesh
        if scene:
            self.swap_weapon(scene, wep_type)
        else:
            self.cur_weapon = wep_type

    def hit(self, damage):
        self.game_hud.sfx.play_player_hit()
        self.cur_hp -= damage
        self.game_hud.update_hp(self.cur_hp)
        self.game_hud.got_hit()

    def boost_hp(self, amount):
        self.cur_hp += amount
        if self.cur_hp >= self.max_hp:
            self.cur_hp = self.max_hp
        self.game_hud.update_hp(self.cur_hp)

    def boost_ammo(self):
        for i in self.ammos:
            if i == "handgun":
                amount = 25
            if i == "shotgun":
                amount = 25
            if i == "chaingun":
                amount = 75
            if i == "plasma gun":
                amount = 15
            self.ammos[i] += amount
            if self.ammos[i] > self.max_ammos[i]:
                self.ammos[i] = self.max_ammos[i]
        if self.cur_weapon:
            self.game_hud.update_ammo(self.ammos[self.cur_weapon])

    def swap_weapon(self, scene, new):
        try:
            scene.remove_3d_after(self.weapons[self.cur_weapon])
        except:
            pass

        if "left" in self.game_hud.event_handler.mouse.active:
            self.game_hud.event_handler.mouse.active.remove("left")

        self.cur_weapon = new
        self.game_hud.update_weapon(new)
        if new:
            scene.add_3d_after(self.weapons[new])
            self.weapons[new].pickable = False
            self.game_hud.update_ammo(self.ammos[new])
        else:
            self.game_hud.update_ammo(0)

    def move(self, camera):
        self.game_hud.sfx.play_walk()
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
            self.reset_move(False)

    def reset_move(self, b=True):
        if b:
            self.game_hud.sfx.stop_walk()
        self.weapon_bob_up = 0
        self.weapon_bob_rot = 0
        self.weapon_bob_count = 20

    def update_weapon(self, camera):
        if self.cur_weapon:
            if self.weapon_bucked:
                x, y = self.weapon_changes
                x += self.weapon_buck_back
                y += self.weapon_buck_twist
                if self.cur_weapon == "shotgun" and x >= self.weapon_buck_back*5:
                    x = self.weapon_buck_back * 5
                    y = self.weapon_buck_twist * 5
                    self.weapon_bucked = False
                if self.cur_weapon == "handgun" and x >= self.weapon_buck_back*3:
                    x = self.weapon_buck_back * 3
                    y = self.weapon_buck_twist * 3
                    self.weapon_bucked = False
                if self.cur_weapon == "plasma gun" and x >= self.weapon_buck_back*8:
                    x = self.weapon_buck_back * 8
                    y = self.weapon_buck_twist * 8
                    self.weapon_bucked = False
                if self.cur_weapon == "chaingun" and x >= self.weapon_buck_back:
                    x = self.weapon_buck_back
                    y = self.weapon_buck_twist
                    self.weapon_bucked = False
                self.weapon_changes = x, y
            elif not self.weapon_buck_done:
                x, y = self.weapon_changes
                if x:
                    x -= self.weapon_buck_back/2
                    if x <= 0:
                        x = 0
                    y -= self.weapon_buck_twist/2
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
            y -= 0.5
            obj.pos = x, y+self.weapon_bob_up, z
            obj.rotation = (0,180-roty+self.weapon_changes[1]-self.weapon_bob_rot*0.2,
                            -20-self.weapon_changes[1]+self.weapon_bob_rot)

    def fire(self, scene, level_data):
        if not self.cur_weapon:
            return
        if self.ammos[self.cur_weapon]:
            if self.cur_weapon == "shotgun":
                if self.weapon_buck_done: #other types maybe don't need this
                    self.game_hud.sfx.player_shoot(self.cur_weapon)
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
                    self.game_hud.sfx.player_shoot(self.cur_weapon)
                    self.ammos[self.cur_weapon] -= 1
                    self.weapon_bucked = True
                    self.weapon_buck_back = 0.2
                    self.weapon_buck_twist = -4
                    self.weapon_buck_done = False
                    self.game_hud.update_ammo(self.ammos[self.cur_weapon])
                    return HandgunShot(self.weapons[self.cur_weapon].pos,
                                       self.weapons[self.cur_weapon].rotation,
                                       level_data, scene)
            if self.cur_weapon == "plasma gun":
                if self.weapon_buck_done:
                    self.game_hud.sfx.player_shoot(self.cur_weapon) #since it is same kind of weapon...
                    self.ammos[self.cur_weapon] -= 1
                    self.weapon_bucked = True
                    self.weapon_buck_back = 0.2
                    self.weapon_buck_twist = -4
                    self.weapon_buck_done = False
                    self.game_hud.update_ammo(self.ammos[self.cur_weapon])
                    return PlasmaShot(self.weapons[self.cur_weapon].pos,
                                       self.weapons[self.cur_weapon].rotation,
                                       level_data, scene)
            if self.cur_weapon == "chaingun":
                if self.weapon_buck_done:
                    self.game_hud.sfx.player_shoot(self.cur_weapon) #since it is same kind of weapon...
                    self.ammos[self.cur_weapon] -= 1
                    self.weapon_bucked = True
                    self.weapon_buck_back = 0.1
                    self.weapon_buck_twist = -1
                    self.weapon_buck_done = False
                    self.game_hud.update_ammo(self.ammos[self.cur_weapon])
                    return ChaingunShot(self.weapons[self.cur_weapon].pos,
                                       self.weapons[self.cur_weapon].rotation,
                                       level_data, scene)
        else:
            self.game_hud.sfx.play_no_ammo()
