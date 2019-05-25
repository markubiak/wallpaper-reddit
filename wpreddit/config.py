import argparse
import configparser
import os
import platform
import sys
from pkg_resources import resource_string

# global vars
verbose = False
startup = False
autostartup = False
force_dl = False
startupinterval = 0
startupattempts = 0
save = False
subs = []
minwidth = 0
minheight = 0
minratio = 0.0
titlesize = 0
titlealign_x = ""
titlealign_y = ""
titleoffset_x = 0
titleoffset_y = 0
maxlinks = 0
resize = False
settitle = False
randomsub = False
blacklistcurrent = False
setcmd = ''
walldir = ''
confdir = ''
savedir = ''
sortby = ''
opsys = platform.system()


def init_config():
    global walldir
    global confdir

    # Get the full path of the directory per platform
    if opsys == "Linux":
        xdg_config = os.getenv('XDG_CONFIG_HOME')
        xdg_data = os.getenv('XDG_DATA_HOME')
        if xdg_config is not None:
            confdir = os.path.expanduser(xdg_config + "/wallpaper-reddit")
        else:
            confdir = os.path.expanduser("~/.config/wallpaper-reddit")
        if xdg_data is not None:
            walldir =  os.path.expanduser(xdg_data + "/wallpaper-reddit")
        else:
            walldir = os.path.expanduser("~/.local/share/wallpaper-reddit")
    elif opsys == "Windows":
        appdata = os.getenv("APPDATA")
        walldir = os.path.expanduser(appdata + "/wallpaper-reddit/data")
        confdir = os.path.expanduser(appdata + "/wallpaper-reddit/config")
    else:
        walldir = os.path.expanduser("~/Library/Application Support/wallpaper-reddit")
        confdir = os.path.expanduser("~/Library/Preferences/wallpaper-reddit")

    # Make the paths if they are nonexistent
    if not os.path.exists(walldir):
        os.makedirs(walldir)
        log(walldir + " created")
    if not os.path.exists(confdir):
        os.makedirs(confdir)
        log(confdir + " created")

    # Create empty versions of specific files if necessary
    if not os.path.exists(walldir + '/blacklist.txt'):
        with open(walldir + '/blacklist.txt', 'w') as blacklist:
            blacklist.write('')
    if not os.path.exists(walldir + '/url.txt'):
        with open(walldir + '/url.txt', 'w') as urlfile:
            urlfile.write('')
    if not os.path.exists(walldir + '/fonts'):
        os.makedirs(walldir + '/fonts')
    if not os.path.exists(walldir + '/fonts/Cantarell-Regular.otf'):
        with open(walldir + '/fonts/Cantarell-Regular.otf', 'wb') as font:
            font.write(resource_string(__name__, 'fonts/Cantarell-Regular.otf'))
    if not os.path.isfile(confdir + '/wallpaper-reddit.conf'):
        if opsys == 'Windows':
            cfile = resource_string(__name__, 'conf_files/windows.conf')
        else:
            cfile = resource_string(__name__, 'conf_files/unix.conf')
        with open(confdir + '/wallpaper-reddit.conf', 'wb') as f:
            f.write(cfile)

    # Get the configuration, start with cfg files and use args as overrides
    parse_config()
    parse_args()
    log("config and args parsed")

# reads the configuration file
def parse_config():
    # options to change
    global subs
    global maxlinks
    global minheight
    global minwidth
    global minratio
    global settitle
    global titlesize
    global titlealign_x
    global titlealign_y
    global titleoffset_x
    global titleoffset_y
    global resize
    global setcmd
    global startupinterval
    global startupattempts
    global savedir
    global randomsub
    global lottery
    global sortby

    # read the config and check the version
    config = configparser.ConfigParser()
    config.read(confdir + '/wallpaper-reddit.conf')
    if config.get('miscellaneous', 'version', fallback=0) is not 4:
        print("You are using an old configuration file.  Please delete your config file in " + confdir +
              " and let the program create a new one.")
        sys.exit(1)

    # core
    subs = config.get('core', 'subs', fallback='earthporn,spaceporn,skyporn,imaginarystarscapes')
    subs = [x.strip() for x in subs.split(',')]
    minwidth = config.getint('core', 'minwidth', fallback=1920)
    minheight = config.getint('core', 'minheight', fallback=1080)
    minratio = config.getfloat('core', 'minratio', fallback=0.0)
    resize = config.getboolean('core', 'resize', fallback=True)
    maxlinks = config.getint('core', 'maxlinks', fallback=20)
    setcmd = config.get('core', 'setcommand', fallback='')

    # extra
    randomsub = config.getboolean('extra', 'random', fallback=False)
    lottery = config.getboolean('extra', 'lottery', fallback=False)
    sortby = config.get('extra', 'sortby', fallback="hot")

    # title overlay
    settitle = config.getboolean('Title Overlay', 'settitle', fallback=False)
    titlesize = config.getint('Title Overlay', 'titlesize', fallback=24)
    titlealign_x = config.get('Title Overlay', 'titlealignx', fallback='right').lower()
    titlealign_y = config.get('Title Overlay', 'titlealigny', fallback='top').lower()
    titleoffset_x = config.getint('Title Overlay', 'titleoffsetx', fallback=5)
    titleoffset_y = config.getint('Title Overlay', 'titleoffsety', fallback=5)

    # startup
    startupinterval = config.getint('Startup', 'interval', fallback=3)
    startupattempts = config.getint('Startup', 'attempts', fallback=10)

    # save
    if opsys == 'Windows':
        default_savedir = "~/My Pictures/Wallpapers"
    else:
        default_savedir = "~/Pictures/Wallpapers"
    savedir = os.path.expanduser(config.get('Save', 'directory', fallback=default_savedir))


# parses command-line arguments and stores them to proper global variables
def parse_args():
    sort_by_values = ["hot", "new", "controversial", "top", "rising"]
    parser = argparse.ArgumentParser(description="Pulls wallpapers from specified subreddits in reddit.com")
    parser.add_argument("subreddits", help="subreddits to check for wallpapers", nargs="*")
    parser.add_argument("-v", "--verbose", help="increases program verbosity", action="store_true")
    parser.add_argument("-f", "--force",
                        help="forces wallpapers to re-download even if it has the same url as the current wallpaper",
                        action="store_true")
    parser.add_argument("--startup", help="runs the program as a startup application, waiting on internet connection",
                        action="store_true")
    parser.add_argument("--auto-startup", help="sets the program to automatically run on every login (Linux only)",
                        action="store_true")
    parser.add_argument("--save",
                        help='saves the current wallpaper (does not download a wallpaper)',
                        action="store_true")
    parser.add_argument("--resize", help="resizes the image to the height and width specified in the config after "
                                         "wallpaper is set.  Enabled by default in the configuration file,",
                        action="store_true")
    parser.add_argument("-b", "--blacklist", help="blacklists the current wallpaper and downloads a new wallpaper",
                        action="store_true")
    parser.add_argument("-s", "--sort-by", help="choose Reddit's sorting algorithm from {} (default=hot)".format(sort_by_values))
    parser.add_argument("--random",
                        help="will pick a random subreddit from the ones provided instead of turning them into a multireddit",
                        action="store_true")
    parser.add_argument("--settitle", help="write title over the image", action="store_true")
    parser.add_argument("--lottery", help="select a random image from a subreddit instead of the newest", action="store_true")
 
    args = parser.parse_args()
    global subs
    global verbose
    global save
    global force_dl
    global startup
    global autostartup
    global resize
    global settitle
    global randomsub
    global blacklistcurrent
    global lottery
    global sortby
    if not args.subreddits == []:
        subs = args.subreddits
    verbose = args.verbose
    save = args.save
    startup = args.startup
    autostartup = args.auto_startup
    force_dl = args.force
    if args.resize:
        resize = True
    if args.settitle:
        settitle = True
    if args.random:
        randomsub = True
    if args.blacklist:
        blacklistcurrent = True
    if args.lottery:
        lottery = True
    if args.sort_by in sort_by_values:
        sortby = args.sort_by
