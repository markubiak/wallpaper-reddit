import os
import sys
from pkg_resources import resource_string

from wpreddit import config, connection, download, reddit, wallpaper


def run():
    try:
        config.init_config()
        # blacklist the current wallpaper if requested
        if config.blacklistcurrent:
            reddit.blacklist_current()
        # check if the program is run in a special case (save or startup)
        if config.save:
            wallpaper.save_wallpaper()
            sys.exit(0)
        if config.autostartup:
            if config.opsys == "Linux":
                dfile = resource_string(__name__, 'conf_files/linux-autostart.desktop')
                path = os.path.expanduser("~/.config") + "/autostart/wallpaper-reddit.desktop"
                with open(path, "wb") as f:
                    f.write(dfile)
                print("Autostart file created at " + path)
                sys.exit(0)
            else:
                print("Automatic startup creation only currently supported on Linux")
                sys.exit(1)
        if config.startup:
            connection.wait_for_connection(config.startupattempts, config.startupinterval)
        # make sure you're actually connected to reddit
        if not connection.connected("http://www.reddit.com"):
            print("ERROR: You do not appear to be connected to Reddit. Exiting")
            sys.exit(1)
        links = reddit.get_links()
        titles = links[1]
        valid = reddit.choose_valid(links[0])
        valid_url = valid[0]
        title = titles[valid[1]]
        download.download_image(valid_url, title)
        download.save_info(valid_url, title)
        wallpaper.set_wallpaper()
        external_script()
    except KeyboardInterrupt:
        sys.exit(1)


# creates and runs the ~/.wallpaper/external.sh script
def external_script():
    if config.opsys == 'Linux' or config.opsys == 'Darwin':
        return_value = 0
        if not os.path.isfile(config.walldir + '/external.sh'):
            with open(config.walldir + '/external.sh', 'w') as external:
                external.write(
                    '# ! /bin/bash\n\n# You can enter custom commands here that will execute after the main program is finished')
            return_value += os.system('chmod +x ' + config.walldir + '/external.sh')
        return_value += os.system('bash ' + config.walldir + '/external.sh')
        if return_value != 0:
            print("external.sh returned a non-zero exit code.  Check for errors.")
