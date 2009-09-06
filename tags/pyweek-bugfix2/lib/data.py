import os

def image_path(path):
    return os.path.join("data", "image", path)

def mesh_path(path):
    return os.path.join("data", "mesh", path)

def sound_path(path):
    return os.path.join("data", "sound", path)

def character_sound_path(char, path):
    return os.path.join(sound_path(char), path)

def level_path(path):
    return os.path.join("data", "level", path)

def gui_path(path):
    return os.path.join("data", "gui", path)

def misc_path(path):
    return os.path.join("data", "misc", path)
