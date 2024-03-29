import pygame
from pygame.locals import *
import time, random
import data

class SoundWrapper(object):
    def __init__(self, filename):
        self.obj = pygame.mixer.Sound(filename)
        self.length = self.obj.get_length()

        self.running = False
        self.play_start = 0

    def play(self):
        self.running = True
        self.play_start = time.time()
        self.obj.play()

    def update(self):
        if self.running:
            if time.time() - self.play_start >= self.length:
                self.stop()

    def stop(self):
        self.running = False
        self.obj.stop()
        

class SFX(object):
    def __init__(self):
        player_walk = "bob", "walk.wav"
        player_hit = ("bob", "bob-hit1.wav"), ("bob", "bob-hit2.wav"), ("bob", "bob-hit3.wav")
        player_kill = ("bob", "bob-insult1.wav"), ("bob", "bob-insult2.wav")

        alien_alert = (("alien", "alien-alert1.wav"), ("alien", "alien-alert2.wav"),
                       ("alien", "alien-alert3.wav"), ("alien", "alien-alert4.wav"))
        alien_chatter = (("alien", "alien1.wav"), ("alien", "alien3.wav"),
                         ("alien", "alien4.wav"), ("alien", "alien5.wav"))
        alien_boss = (("alien", "alien-sinister1.wav"), ("alien", "alien-sinister2.wav"),
                      ("alien", "alien-sinister3.wav"), ("alien", "alien-sinister4.wav"),
                      ("alien", "alien-sinister5.wav"))

        self.all_sounds = []

        self.player_walk = SoundWrapper(data.character_sound_path(*player_walk))
        self.all_sounds.append(self.player_walk)

        self.player_hit_sounds = []
        for i in player_hit:
            self.player_hit_sounds.append(SoundWrapper(data.character_sound_path(*i)))
            self.all_sounds.append(self.player_hit_sounds[-1])

        self.player_kill_sounds = []
        for i in player_kill:
            self.player_kill_sounds.append(SoundWrapper(data.character_sound_path(*i)))
            self.all_sounds.append(self.player_kill_sounds[-1])

        self.player_one_playing = None


        self.alien_alert_sounds = []
        for i in alien_alert:
            self.alien_alert_sounds.append(SoundWrapper(data.character_sound_path(*i)))
            self.all_sounds.append(self.alien_alert_sounds[-1])
        self.alien_chatter_sounds = []
        for i in alien_chatter:
            self.alien_chatter_sounds.append(SoundWrapper(data.character_sound_path(*i)))
            self.all_sounds.append(self.alien_chatter_sounds[-1])

        self.alien_boss_sounds = []
        for i in alien_boss:
            self.alien_boss_sounds.append(SoundWrapper(data.character_sound_path(*i)))
            self.all_sounds.append(self.alien_boss_sounds[-1])

        self.alien_one_playing = None

        human_weapons = {"shotgun":["shotgun1.wav"],
                         "handgun":["handgun2.wav"],
                         "plasma gun":["plasma.wav"],
                         "chaingun":["chain.wav"],
                         "chicken gun":["chicken-gun.wav"]}
        self.human_weapons = {}
        for i in human_weapons:
            xx = []
            for x in human_weapons[i]:
                xx.append(SoundWrapper(data.character_sound_path("gun", x)))
            self.human_weapons[i] = xx
            self.all_sounds.extend(xx)

        self.alien_shot = SoundWrapper(data.character_sound_path("gun", "alien-lazer.wav"))
        self.alien_hit = SoundWrapper(data.character_sound_path("alien", "alien-hit.wav"))
        self.alien_die = SoundWrapper(data.character_sound_path("alien", "alien-die.wav"))

        self.door_open = SoundWrapper(data.sound_path("door-open.wav"))
        self.level_warp = SoundWrapper(data.sound_path("levelwarp.wav"))

        self.pickup_ammo = SoundWrapper(data.sound_path("pickup-ammo.wav"))
        self.pickup_hp = SoundWrapper(data.sound_path("pickup-health.wav"))
        self.pickup_feather = SoundWrapper(data.sound_path("pickup-feather.wav"))
        self.no_ammo = SoundWrapper(data.sound_path("pickup-ammo.wav"))
        self.no_ammo.obj.set_volume(0.25)
        self.no_ammo.length *= 2

        self.loss_sound = SoundWrapper(data.character_sound_path("bob", "bob-fail.wav"))
        self.win_sound = SoundWrapper(data.character_sound_path("bob", "bob-win.wav"))

        self.all_sounds.append(self.alien_shot)
        self.all_sounds.append(self.alien_hit)
        self.all_sounds.append(self.alien_die)

        self.all_sounds.append(self.door_open)
        self.all_sounds.append(self.level_warp)

        self.all_sounds.append(self.pickup_ammo)
        self.all_sounds.append(self.no_ammo)
        self.all_sounds.append(self.pickup_hp)
        self.all_sounds.append(self.pickup_feather)

        self.all_sounds.append(self.loss_sound)
        self.all_sounds.append(self.win_sound)

        menu_track = data.character_sound_path("music", "menu.ogg")
        game_track = data.character_sound_path("music", "game.ogg")
        self.track_states = {"menu":menu_track,
                             "play":game_track}
        self.track_state = None

    def play_walk(self):
        if not self.player_walk.running:
            self.player_walk.play()
    def stop_walk(self):
        if self.player_walk.running:
            self.player_walk.stop()

    def play_no_ammo(self):
        if not self.no_ammo.running:
            self.no_ammo.play()

    def play_loss(self):
        self.loss_sound.play()
    def play_win(self):
        self.win_sound.play()

    def set_track(self, state):
        if state == None:
            self.track_state = None
            pygame.mixer.music.stop()
        elif state != self.track_state:
            self.track_state = state
            pygame.mixer.music.load(self.track_states[state])
            pygame.mixer.music.play(-1)

    def open_door(self):
        if not self.door_open.running:
            self.door_open.play()

    def play_level_warp(self):
        self.level_warp.play()

    def play_pickup_ammo(self):
        self.pickup_ammo.play()
    def play_pickup_hp(self):
        self.pickup_hp.play()
    def play_pickup_feather(self):
        self.pickup_feather.play()

    def play_player_hit(self):
        if self.player_one_playing and not self.player_one_playing.running:
            self.player_one_playing = None
        if not self.player_one_playing:
            self.player_one_playing = random.choice(self.player_hit_sounds)
            self.player_one_playing.play()

    def play_player_kill(self):
        if self.player_one_playing and not self.player_one_playing.running:
            self.player_one_playing = None
        if not self.player_one_playing:
            self.player_one_playing = random.choice(self.player_kill_sounds)
            self.player_one_playing.play()

    def play_alien_hit(self):
        self.alien_hit.play()
    def play_alien_die(self):
        self.alien_die.play()

    def play_alien_alert(self):
        if self.alien_one_playing and not self.alien_one_playing.running:
            self.alien_one_playing = None
        if self.alien_one_playing in self.alien_chatter_sounds:
            self.alien_one_playing.stop()
        if not self.alien_one_playing in self.alien_alert_sounds:
            self.alien_one_playing = random.choice(self.alien_alert_sounds)
            self.alien_one_playing.play()

    def play_alien_chatter(self):
        if self.alien_one_playing and not self.alien_one_playing.running:
            self.alien_one_playing = None
        if not self.alien_one_playing:
            self.alien_one_playing = random.choice(self.alien_chatter_sounds)
            self.alien_one_playing.play()

    def player_shoot(self, kind):
        s = random.choice(self.human_weapons[kind])
        for i in self.human_weapons[kind]:
            if i.running:
                if not i == s:
                    return
        s.stop()
        s.play()

    def alien_shoot(self):
        self.alien_shot.play()

    def reset(self):
        for i in self.all_sounds:
            if i.running:
                i.stop()

    def update(self):
        for i in self.all_sounds:
            i.update()

        
