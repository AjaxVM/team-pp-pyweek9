
import pyggel
from pyggel import *

import data, hud
import random, math

from level_data import *
from weapons import *
from buffs import *
from aliens import *
from player import *
from menus import *

def play_level(level, player_data):
    camera = pyggel.camera.LookFromCamera((10,0,10))
    light = pyggel.light.Light((0,100,0), (0.5,0.5,0.5,1),
                                  (1,1,1,1), (50,50,50,10),
                                  (0,0,0), True)

    scene = pyggel.scene.Scene()
    scene.pick = True
    scene.add_light(light)

    (static, dynamic, baddies, feathers, camera_pos,
     fog_color, tile_set, level_data, tsize, last_level) = get_geoms(level)
    shots = []
    badshots = []
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
    scene.add_3d(feathers)

    game_hud = player_data.game_hud
    game_hud.scene = scene
    game_hud.camera = camera
    scene.add_2d(game_hud)
    for i in dynamic + feathers + baddies:
        i.game_hud = game_hud

    game_hud.update_feathers(0, len(feathers))
    have_feathers = 0

    clock = pygame.time.Clock()
    event = game_hud.event_handler

    player_data.swap_weapon(scene, player_data.cur_weapon)
    player_data.update_weapon(camera)

    scene.render_buffer = transition_buffer
    scene.pick = False
    game_hud.visible = False
    scene.render(camera) #make sure we only pick the center!
    do_transition(transition_buffer, player_data, False)
    game_hud.visible = True
    scene.pick = True
    scene.render_buffer = None

    game_hud.reset()

    event.update() #so the camera doesn't wig out the first time...

    paused = False

    while 1:
        clock.tick(999)
        pyggel.view.set_title("Chickenstein - Team [insert name] - Pyweek #9 - FPS: %s"%clock.get_fps())

        #Render first, since picking is done at this time, and we need that later!

        if have_feathers == len(feathers): #next round
            good = True
            for i in baddies:
                if i.kind == "boss":
                    if i in scene.graph.render_3d:
                        good = False
                        break
            if good and (not last_level):
                scene.render_buffer = transition_buffer
                scene.pick = False
                game_hud.visible = False
                scene.render(camera) #make sure we only pick the center!
                return ["next", transition_buffer]
            else:
                #TODO: hack
                #this won't return win - only when you finish talking to chicken do you win!
                scene.render_buffer = transition_buffer
                scene.pick = False
                game_hud.visible = False
                scene.render(camera) #make sure we only pick the center!
                return ["win", transition_buffer]

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
            scene.render_buffer = transition_buffer
            scene.pick = False
            game_hud.visible = False
            scene.render(camera) #make sure we only pick the center!
            return ["menu", transition_buffer]
        if event.quit:
            return ["quit"]

        if "p" in event.keyboard.hit:
            paused = not paused
            game_hud.paused.visible = paused

        if paused:
            continue

        if not game_hud.grab_events:
            if "wheel-up" in event.mouse.hit:
                player_data.next_weapon(scene)
            if "wheel-down" in event.mouse.hit:
                player_data.prev_weapon(scene)
            if event.mouse.motion[0]:
                camera.roty += event.mouse.motion[0] * 0.2

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
                                                       0.10)
                future = pyggel.math3d.move_with_rotation(future,
                                                       (camera.rotx,camera.roty*-1+90, camera.rotz),
                                                       1.25)
                do_move = True
            if "d" in event.keyboard.active:
                new = pyggel.math3d.move_with_rotation(new,
                                                       (camera.rotx,camera.roty*-1-90, camera.rotz),
                                                       0.10)
                future = pyggel.math3d.move_with_rotation(future,
                                                       (camera.rotx,camera.roty*-1-90, camera.rotz),
                                                       1.25)
                do_move = True

            if do_move:
                player_data.move(camera)
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

        for i in badshots:
            if i.dead_remove_from_scene:
                badshots.remove(i)
            else:
                if i.collision_body.collide(player_data.collision_body):
                    i.dead_remove_from_scene = True
                    player_data.hit(i.damage)

        if player_data.cur_hp <= 0:
            scene.render_buffer = transition_buffer
            scene.pick = False
            game_hud.visible = False
            scene.render(camera) #make sure we only pick the center!
            return ["death", transition_buffer]

        for i in baddies:
            shot = i.update(camera.get_pos(), level_data)
            if i.dead_remove_from_scene:
                baddies.remove(i)
            if shot:
                for x in shot:
                    badshots.append(x)
                scene.add_3d_blend(shot)
            if i.collision_body.collide(player_data.collision_body):
                player_data.hit(1)
                i.hit(1)

        if not game_hud.grab_events:
            if "right" in event.mouse.hit:
                if pick and pyggel.math3d.get_distance(camera.get_pos(), pick.pos) < tsize*3:
                    if isinstance(pick, Feather):
                        have_feathers += 1
                        scene.remove_3d(pick)
                        game_hud.sfx.play_pickup_feather()
                        game_hud.update_feathers(have_feathers, len(feathers))
                    if isinstance(pick, Weapon):
                        scene.remove_3d(pick)
                        game_hud.sfx.play_pickup_ammo()
                        player_data.add_weapon(scene, pick.name, pick.obj)
                    if isinstance(pick, HPBuff):
                        scene.remove_3d(pick)
                        game_hud.sfx.play_pickup_hp()
                        player_data.boost_hp(20)
                    if isinstance(pick, AmmoBuff):
                        scene.remove_3d(pick)
                        game_hud.sfx.play_pickup_ammo()
                        player_data.boost_ammo(25)
                    if isinstance(pick, Console):
                        game_hud.set_gui_app("console")
            if "left" in event.mouse.active:
                shot = player_data.fire(scene, level_data)
                if shot:
                    scene.add_3d_blend(shot)
                    shots.append(shot)

def do_transition(buf, player_data, out=True):
    player_data.game_hud.sfx.play_level_warp()
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

    clock = pygame.time.Clock()
    duration = 1.25
    frames = 30
    dif = int(frames*duration)

    for i in xrange(dif):
        clock.tick(30)
        if out:
            scale -= 1.1/dif
            rot += 360.0/dif
        else:
            scale += 1.1/dif
            rot -= 360.0/dif
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
    try:
        pygame.mixer.pre_init(22050,-16,4,1024)
    except:
        pass
    pyggel.init()
    try:
        i = pygame.image.load(data.image_path("chickenstein_logo_small.png"))
        i.set_colorkey(i.get_at((0,0)), RLEACCEL)
        pygame.display.set_icon(i)
    except:
        pass
    try:
        pyggel.view.set_debug(False)
    except:
        print "Cannot disable debug, speed may be slower..."

    pData = PlayerData(hud.Hud())

    level = 1
    mode = "menu"

    core_menu = Menu()
    core_story_menu = StoryMenu()
    core_death_menu = DeathMenu()
    core_win_menu = WinMenu()

    while 1:
        pyggel.view.set_title("Chickenstein - Team [insert name] - Pyweek #9")
        if mode == "menu":
            level = 1
            pData.reset()
            retval = core_menu.run()
            command = retval[0]
        elif mode == "game":
            retval = play_level(level, pData)
            command = retval[0]
        elif mode == "story":
            retval = core_story_menu.run()
            command = retval[0]
        elif mode == "death":
            retval = core_death_menu.run()
            command = retval[0]
        elif mode == "win":
            retval = core_win_menu.run()
            command = retval[0]

        pData.game_hud.sfx.reset()

        if command == "menu":
            mode = "menu"
        if command == "story":
            mode = "story"
        if command == "quit":
            pyggel.quit()
            return None
        if command == "play":
            mode = "game"
            level = 1
            pData.reset()
        if command == "next":
            mode = "game"
            do_transition(retval[1], pData)
            level += 1
            continue
        if command == "win":
            mode = "win"
            do_transition(retval[1], pData)
            level = 1
            pData.reset()
        if command == "death":
            mode = "death"
            do_transition(retval[1], pData)
            level = 1
            pData.reset()
