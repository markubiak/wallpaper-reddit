import os
import random
import sys
from pkg_resources import resource_string
from subprocess import check_call, CalledProcessError
from wpreddit import config, connection, download, reddit, wallpaper
from wpreddit.blacklist import Blacklist
from wpreddit.common import log, exit_msg


def run():
    try:
        config.init_config()
        cfg = config.cfg
        # switch based on action
        if cfg['mode'] == "blacklist_current":
            blacklist_current()
            sys.exit(0)
        elif cfg['mode'] == "save_current":
            wallpaper.save_wallpaper()
            sys.exit(0)
        elif cfg['mode'] == "gen_autostart":
            if cfg['opsys'] == "Linux":
                dfile = resource_string(__name__, 'conf_files/linux-autostart.desktop')
                path = os.path.expanduser("~/.config/autostart")
                if not os.path.exists(path):
                    os.makedirs(path)
                    log(path + " created")
                with open(path + "/wallpaper-reddit.desktop", "wb") as f:
                    f.write(dfile)
                exit_msg("Autostart file created at " + path, code=0)
            else:
                exit_msg("Automatic startup creation only currently supported on Linux")
        # normal mode
        if cfg['mode'] == 'startup':
            # give it a bit to potentially connect to wifi
            connection.wait_for_connection(cfg.startup.attempts, cfg.startup.interval)
        else:
            # exit if no internet connection
            if not connection.connected_to_reddit():
                exit_msg("ERROR: You do not appear to be connected to Reddit. Exiting")
        links = reddit.get_links()
        valid = reddit.choose_valid(links)
        img = download.download_image(valid[0])
        if cfg['os'] == "Windows":
            img.save(cfg['dirs']['data'] + '\\wallpaper.bmp', "BMP")
        else:
            img.save(cfg['dirs']['data'] + '/wallpaper.jpg', "JPEG")
        download.save_info(cfg['dirs']['data'], valid[0], valid[1], valid[2])
        wallpaper.set_wallpaper()
        external_script(cfg['dirs']['data'] + cfg['external_script'])
    except KeyboardInterrupt:
        sys.exit(1)


def blacklist_current():

    """
    Reads URL of currently set wallpaper and adds it to the blacklist
    """

    # Sanity check
    if not os.path.isfile(cfg['dirs']['data'] + '/url.txt'):
        exit_msg("ERROR: " + cfg['dirs']['data'] + "/url.txt does not exist. "
                 "wallpaper-reddit must run once before you can blacklist a wallpaper.")
    
    # Setup the blacklist and append to it
    blacklist = Blacklist(cfg['dirs']['data'] + '/url.txt')
    with open(cfg['dirs']['data'] + '/url.txt', 'r') as urlfile:
        url = urlfile.read()
    blacklist.add(url)


# creates and runs the ~/.local/share/wallpaper-reddit/external.sh script
def external_script(path):
    cfg = config.cfg
    if cfg['os'] == 'Linux' or cfg['os'] == 'Darwin':
        try:
            if not os.path.isfile(path):
                with open(path, 'w') as external:
                    external.write(
                        '# ! /bin/bash\n\n# You can enter custom commands here that will execute after the main '
                        'program is finished')
                check_call(["chmod", "+x", path])
            check_call(["bash", path])
        except CalledProcessError or FileNotFoundError:
            print("%s did not execute successfully, check for errors." % path)

if __name__ == '__main__':
    run()

