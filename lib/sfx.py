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

        self.alien_boss_sounds = []
        for i in alien_boss:
            self.alien_boss_sounds.append(SoundWrapper(data.character_sound_path(*i)))
            self.all_sounds.append(self.alien_boss_sounds[-1])

        self.alien_one_playing = None

        human_weapons = {"shotgun":["shotgun1.wav", "shotgun2.wav"],
                         "handgun":["handgun2.wav"]}
        self.human_weapons = {}
        for i in human_weapons:
            xx = []
            for x in human_weapons[i]:
                xx.append(SoundWrapper(data.character_sound_path("gun", x)))
            self.human_weapons[i] = xx
            self.all_sounds.extend(xx)

    def play_walk(self):
        if not self.player_walk.running:
            self.player_walk.play()
    def stop_walk(self):
        if self.player_walk.running:
            self.player_walk.stop()

    def play_player_hit(self):
        if self.player_one_playing and not self.player_one_playing.running:
            self.player_one_playing = None
        if self.player_one_playing in self.player_kill_sounds:
            self.player_one_playing.stop()
            self.player_one_playing = random.choice(self.player_hit_sounds)
            self.player_one_playing.play()
        elif self.player_one_playing in self.player_hit_sounds:
            pass
        else:
            self.player_one_playing = random.choice(self.player_hit_sounds)
            self.player_one_playing.play()

    def player_shoot(self, kind):
        s = random.choice(self.human_weapons[kind])
        if not s.running:
            s.play()

    def reset(self):
        for i in self.all_sounds:
            if i.running:
                i.stop()

    def update(self):
        for i in self.all_sounds:
            i.update()

        
