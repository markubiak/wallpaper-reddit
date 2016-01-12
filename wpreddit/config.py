import argparse
import configparser
import os
import platform

from pkg_resources import resource_string
from wpreddit import main

# global vars
verbose = False
startup = False
force_dl = False
startupinterval = 0
startupattempts = 0
save = False
subs = []
minwidth = 0
minheight = 0
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
opsys = platform.system()


def init_config():
    global walldir
    global confdir
    if opsys == "Linux":
        walldir = os.path.expanduser("~/.wallpaper")
        confdir = os.path.expanduser("~/.config/wallpaper-reddit")
    else:
        walldir = os.path.expanduser("~/Wallpaper-Reddit")
        confdir = os.path.expanduser("~/Wallpaper-Reddit/config")
    if not os.path.exists(walldir):
        os.makedirs(walldir)
        main.log(walldir + " created")
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
    if not os.path.exists(confdir):
        os.makedirs(confdir)
        main.log(confdir + " created")
    if not os.path.isfile(confdir + '/wallpaper-reddit.conf'):
        if opsys == 'Linux':
            cfile = resource_string(__name__, 'conf_files/linux.conf')
        else:
            cfile = resource_string(__name__, 'conf_files/windows.conf')
        with open(confdir + '/wallpaper-reddit.conf', 'wb') as f:
            f.write(cfile)
    parse_config()
    parse_args()
    main.log("config and args parsed")


# reads the configuration at ~/.config/wallpaper-reddit
def parse_config():
    config = configparser.ConfigParser()
    config.read(confdir + '/wallpaper-reddit.conf')
    global subs
    global maxlinks
    global minheight
    global minwidth
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
    subs = config.get('Options', 'subs', fallback='earthporn,spaceporn,skyporn,technologyporn,imaginarystarscapes')
    subs = [x.strip() for x in subs.split(',')]
    maxlinks = config.getint('Options', 'maxlinks', fallback=20)
    minwidth = config.getint('Options', 'minwidth', fallback=1920)
    minheight = config.getint('Options', 'minheight', fallback=1080)
    resize = config.getboolean('Options', 'resize', fallback=True)
    randomsub = config.getboolean('Options', 'random', fallback=False)
    setcmd = config.get('SetCommand', 'setcommand', fallback='')
    settitle = config.getboolean('Title Overlay', 'settitle', fallback=False)
    titlesize = config.getint('Title Overlay', 'titlesize', fallback=24)
    titlealign_x = config.get('Title Overlay', 'titlealignx', fallback='right').lower()
    titlealign_y = config.get('Title Overlay', 'titlealigny', fallback='top').lower()
    titleoffset_x = config.getint('Title Overlay', 'titleoffsetx', fallback=5)
    titleoffset_y = config.getint('Title Overlay', 'titleoffsety', fallback=5)
    startupinterval = config.getint('Startup', 'interval', fallback=3)
    startupattempts = config.getint('Startup', 'attempts', fallback=10)

    def get_default_savedir():
        if opsys == 'Linux':
            return "~/Pictures/Wallpapers"
        else:
            return "~/My Pictures/Wallpapers"

    savedir = os.path.expanduser(config.get('Save', 'directory', fallback=get_default_savedir()))


# parses command-line arguments and stores them to proper global variables
def parse_args():
    parser = argparse.ArgumentParser(description="Pulls wallpapers from specified subreddits in reddit.com")
    parser.add_argument("subreddits", help="subreddits to check for wallpapers", nargs="*")
    parser.add_argument("-v", "--verbose", help="increases program verbosity", action="store_true")
    parser.add_argument("-f", "--force",
                        help="forces wallpapers to re-download even if it has the same url as the current wallpaper",
                        action="store_true")
    parser.add_argument("--startup", help="runs the program as a startup application, waiting on internet connection",
                        action="store_true")
    parser.add_argument("--save",
                        help='saves the current wallpaper (does not download a wallpaper)',
                        action="store_true")
    parser.add_argument("--resize", help="resizes the image to the height and width"
                                         "specified in the config after wallpaper is set",
                        action="store_true")
    parser.add_argument("--blacklist", help="blacklists the current wallpaper and downloads a new wallpaper",
                        action="store_true")
    parser.add_argument("--random",
                        help="will pick a random subreddit from the ones provided instead of turning them into a multireddit",
                        action="store_true")
    parser.add_argument("--settitle", help="write title over the image", action="store_true")
    args = parser.parse_args()
    global subs
    global verbose
    global save
    global force_dl
    global startup
    global resize
    global settitle
    global randomsub
    global blacklistcurrent
    if not args.subreddits == []:
        subs = args.subreddits
    verbose = args.verbose
    save = args.save
    startup = args.startup
    force_dl = args.force
    if args.resize:
        resize = True
    if args.settitle:
        settitle = True
    if args.random:
        randomsub = True
    if args.blacklist:
        blacklistcurrent = True
