import ctypes
import logging
import os
import random
import re
import shutil
from subprocess import check_call, check_output, CalledProcessError

from .common import exit_msg
from .config import cfg


def set_wallpaper():
    if cfg['os'] == "Windows":
        ctypes.windll.user32.SystemParametersInfoW(0x14, 0, cfg['dirs']['data'] + "\\wallpaper.bmp", 0x3)
    elif cfg['os'] == "Darwin":
        path = os.path.expanduser(cfg['dirs']['data'] + "/wallpaper.jpg")
        try:
            check_call(["sqlite3", "~/Library/Application Support/Dock/desktoppicture.db", "\"update",
                                   "data", "set", "value", "=", "'%s'\"" % path])
            check_call(["killall", "dock"])
        except CalledProcessError or FileNotFoundError:
            exit_msg("Setting wallpaper failed.  Ensure all dependencies listen in the README are installed.")
    else:
        linux_wallpaper()
    logging.info("Wallpaper set command was run.")


def check_de(current_de, list_of_de):
    """Check if any of the strings in ``list_of_de`` is contained in ``current_de``."""
    return any([de in current_de for de in list_of_de])


def linux_wallpaper():
    de = os.environ.get('DESKTOP_SESSION')
    path = os.path.expanduser(cfg['dirs']['data'] + "/wallpaper.jpg")
    try:
        if cfg['set_command'] != '':
            check_call(cfg['set_command'].split(" "))
        elif check_de(de, ["gnome", "gnome-xorg", "gnome-wayland", "unity", "ubuntu", "ubuntu-xorg", "budgie-desktop"]):
            check_call(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", "file://%s" % path])
        elif check_de(de, ["cinnamon"]):
            check_call(["gsettings", "set", "org.cinnamon.desktop.background", "picture-uri", "file://%s" % path])
        elif check_de(de, ["pantheon"]):
            # Some disgusting hacks so that Pantheon will update the wallpaper
            # If the filename isn't changed, the wallpaper doesn't either
            files = os.listdir(cfg['dirs']['data'])
            for file in files:
                if re.search('wallpaper[0-9]+\.jpg', file) is not None:
                    os.remove(cfg['dirs']['data'] + "/" + file)
            randint = random.randint(0, 65535)
            randpath = os.path.expanduser(cfg['dirs']['data'] + "/wallpaper%s.jpg" % randint)
            shutil.copyfile(path, randpath)
            check_call(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", "file://%s" % randpath])
        elif check_de(de, ["mate"]):
            check_call(["gsettings", "set", "org.mate.background", "picture-filename", "'%s'" % path])
        elif check_de(de, ["xfce", "xubuntu"]):
            # Light workaround here, just need to toggle the wallpaper from null to the original filename
            # xfconf props aren't 100% consistent so light workaround for that too
            props = check_output(['xfconf-query', '-c', 'xfce4-desktop', '-p', '/backdrop', '-l'])\
                    .decode("utf-8").split('\n')
            for prop in props:
                if "last-image" in prop or "image-path" in prop:
                    check_call(["xfconf-query", "-c", "xfce4-desktop", "-p", prop, "-s", "''"])
                    check_call(["xfconf-query", "-c", "xfce4-desktop", "-p", prop, "-s" "'%s'" % path])
                if "image-show" in prop:
                    check_call(["xfconf-query", "-c", "xfce4-desktop", "-p", prop, "-s", "'true'"])
        elif check_de(de, ["lubuntu", "Lubuntu"]):
            check_call(["pcmanfm", "-w", "%s" % path])
        elif check_de(de, ["i3", "bspwm"]):
            check_call(["feh", "--bg-fill", path])
        elif cfg['set_command'] == '':
            exit_msg("Your DE could not be detected to set the wallpaper. "
                    "You need to set the 'setcommand' paramter at ~/.config/wallpaper-reddit. "
                    "When you get it working, please file an issue.")
    except CalledProcessError or FileNotFoundError:
        exit_msg("Command to set wallpaper returned non-zero exit code.  Please file an issue or check your custom "
                "command if you have set one in the configuration file.")


# saves the wallpaper in the save directory from the config
# naming scheme is wallpaperN
def save_wallpaper():
    if not os.path.exists(cfg['dirs']['save']):
        os.makedirs(cfg['dirs']['save'])
        logging.warning(cfg['dirs']['save'] + " did not exist and was created")
    if not os.path.isfile(cfg['dirs']['save'] + '/titles.txt'):
        with open(cfg['dirs']['save'] + '/titles.txt', 'w') as f:
            f.write('Titles of the saved wallpapers:')
        logging.warning(cfg['dirs']['save'] + "/titles.txt did not exist and was created")

    wp_count = 0
    orig_path = cfg['dirs']['data']
    new_path = cfg['dirs']['save']

    if cfg['os'] == "Windows":
        orig_path = orig_path + '\\wallpaper.bmp'
        while os.path.isfile(cfg['dirs']['save'] + '\\wallpaper' + str(wp_count) + '.bmp'):
            wp_count += 1
        new_path = new_path + ('\\wallpaper' + str(wp_count) + '.bmp')
    else:
        orig_path = orig_path + '/wallpaper.jpg'
        while os.path.isfile(cfg['dirs']['save'] + '/wallpaper' + str(wp_count) + '.jpg'):
            wp_count += 1
        new_path = new_path + '/wallpaper' + str(wp_count) + '.jpg'
    shutil.copyfile(orig_path, new_path)

    with open(cfg['dirs']['data'] + '/title.txt', 'r') as f:
        title = f.read()
    with open(cfg['dirs']['save'] + '/titles.txt', 'a') as f:
        f.write('\n' + 'wallpaper' + str(wp_count) + ': ' + title)

    logging.info("Current wallpaper saved to " + new_path)
