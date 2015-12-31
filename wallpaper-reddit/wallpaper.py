import ctypes
import os
import shutil

import config
# in - string - command to set the wallpaper from ~/.wallpaper/wallpaper (or ~/Wallpaper-Reddit/wallpaper for Win)
# uses the user-specified command to set the downloaded-then-moved wallpaper
import main


def set_wallpaper():
    if config.opsys == "Windows":
        ctypes.windll.user32.SystemParametersInfoW(0x14, 0, config.walldir + "\\wallpaper.bmp", 0x3)
    else:
        os.system(config.setcmd)
    print("wallpaper set command was run")


# saves the wallpaper in the save directory from the config
# naming scheme is wallpaperN
def save_wallpaper():
    i = 0
    while os.path.isfile(config.savedir + '/wallpaper' + str(i)):
        i += 1
    if config.opsys == "Windows":
        shutil.copyfile(config.walldir + '\\wallpaper.bmp', config.savedir + '\\wallpaper' + str(i))
    else:
        shutil.copyfile(config.walldir + '/wallpaper.jpg', config.savedir + '/wallpaper' + str(i))
    with open(config.walldir + '/title.txt', 'r') as f:
        title = f.read()
    with open(config.savedir + '/titles.txt', 'a') as f:
        f.write('\n' + 'wallpaper' + str(i) + ': ' + title)
    print("current wallpaper saved to " + config.savedir + '/wallpaper' + str(i))


# creates directories for the saved images, as that directory has to be loaded from the config file
def make_save_dirs():
    if not os.path.exists(config.savedir):
        os.makedirs(config.savedir)
        main.log(config.savedir + " created")
    if not os.path.isfile(config.savedir + '/titles.txt'):
        with open(config.savedir + '/titles.txt', 'w') as f:
            f.write('Titles of the saved wallpapers:')
        main.log(config.savedir + "/titles.txt created")
