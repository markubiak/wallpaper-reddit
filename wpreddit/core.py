import os
import random
import sys
from pkg_resources import resource_string
from subprocess import check_call, CalledProcessError
from wpreddit import config, connection, download, reddit, wallpaper
from wpreddit.common import log


def run():
    try:
        cfg = config.init_config()
        # switch based on action
        if cfg.action == 'blacklist':
            # blacklist the current wallpaper if requested
            reddit.blacklist_current()
            sys.exit(0)
        elif cfg.action == 'save':
            # check if the program is run in a special case (save or startup)
            wallpaper.save_wallpaper()
            sys.exit(0)
        elif cfg.action == 'autostartup':
            # generate file for autostart on login and exit
            if config.opsys == "Linux":
                dfile = resource_string(__name__, 'conf_files/linux-autostart.desktop')
                path = os.path.expanduser("~/.config/autostart")
                if not os.path.exists(path):
                    os.makedirs(path)
                    log(path + " created")
                with open(path + "/wallpaper-reddit.desktop", "wb") as f:
                    f.write(dfile)
                print("Autostart file created at " + path)
                sys.exit(0)
            else:
                print("Automatic startup creation only currently supported on Linux")
                sys.exit(1)
        # normal mode
        if cfg.action == 'startup':
            # give it a bit to connect to wifi
            connection.wait_for_connection(cfg.startup.attempts, cfg.startup.interval)
        else:
            # exit if no internet connection
            if not connection.connected("http://www.reddit.com"):
                print("ERROR: You do not appear to be connected to Reddit. Exiting")
                sys.exit(1)
        links = reddit.get_links()
        valid = reddit.choose_valid(links)
        download.download_image(valid[0], valid[1])
        if platform.system() == "Windows":
            img.save(config.walldir + '\\wallpaper.bmp', "BMP")
        else:
            img.save(config.walldir + '/wallpaper.jpg', "JPEG")
        download.save_info(valid)
        wallpaper.set_wallpaper()
        external_script(cfg.path.external)
    except KeyboardInterrupt:
        sys.exit(1)


# creates and runs the ~/.local/share/wallpaper-reddit/external.sh script
def external_script(path):
    if config.opsys == 'Linux' or config.opsys == 'Darwin':
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


