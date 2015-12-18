import argparse
import configparser
import os
import platform
import sys
from collections import OrderedDict

import main

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
titlegravity = "south"
titlefont = ""
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


def create_config():
    global walldir
    global confdir
    if opsys == "Linux":
        walldir = os.path.expanduser("~/.wallpaper")
        confdir = os.path.expanduser("~/.config/wallpaper-reddit")
    else:
        walldir = os.path.expanduser("~/Wallpaper-Reddit")
        confdir = os.path.expanduser("~/Wallpaper-Reddit/Config")
    if not os.path.exists(walldir):
        os.makedirs(walldir)
        main.log(walldir + " created")
    if not os.path.exists(walldir + '/blacklist.txt'):
        with open(walldir + '/blacklist.txt', 'w') as blacklist:
            blacklist.write('')
    if not os.path.exists(walldir + '/url.txt'):
        with open(walldir + '/url.txt', 'w') as urlfile:
            urlfile.write('')
    if not os.path.exists(confdir):
        os.makedirs(confdir)
        main.log(confdir + " created")
    if not os.path.isfile(confdir + '/wallpaper-reddit.conf'):
        make_config()
        print(
            "default config file created at " + confdir +
            "/wallpaper-reddit.conf.  You need to do some minimal configuration before the program will work")
        sys.exit(0)
    parse_config()
    if setcmd == '' and opsys == 'Linux':
            print("It appears you have not set the command to set wallpaper from your DE."
                  "Check the config file at ~/.config/wallpaper-reddit")
            sys.exit(1)
    parse_args()


# creates a default config file with examples in ~/.config/wallpaper-reddit
def make_config():
    config = configparser.ConfigParser()
    config['SetCommand'] = OrderedDict([('setcommand', '')])
    config['SetCommandExamples'] = OrderedDict(
        [('examples', 'feel free to delete these, wallpaper will be ~/.wallpaper/wallpaper.jpg'),
         ('example_gnome3: gnome3 (Unity, Cinnamon, Gnome 3)',
          'gsettings set org.gnome.desktop.background picture-uri file:///home/user/.wallpaper/wallpaper.jpg'),
         ('example_gnome2: gnome2 (Metacity, MATE)',
          'gconftool-2 -t string -s /desktop/gnome/background/picture_filename "/home/user/.wallpaper/wallpaper.jpg"'),
         ('example_xfce4',
          'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/image-path -s "" && xfconf-query -c '
          'xfce4-desktop -p /backdrop/screen0/monitor0/image-path -s "/home/user/.wallpaper/wallpaper.jpg"'),
         ('example_bash', 'bash /home/user/.config/wallpaper-reddit/some-script.sh'),
         ('example_windows', 'Can be blank, unused for Windows operating systems')])
    config['Options'] = OrderedDict([('subs', 'earthporn,spaceporn,skyporn,technologyporn,imaginarystarscapes'),
                                     ('minwidth', '1920'),
                                     ('minheight', '1080'),
                                     ('maxlinks', '20'),
                                     ('resize', 'True'),
                                     ('random', 'False')])
    config['Title Overlay'] = OrderedDict([('settitle', 'False'),
                                           ('titlesize', '20'),
                                           ('titlegravity', 'south'),
                                           ('titlefont', '')])
    config['Startup'] = OrderedDict([('attempts', '10'),
                                     ('interval', '3')])
    if opsys == 'Linux':
        config['Save'] = {'directory': '~/Pictures/Wallpapers'}
    else:
        config['Save'] = {'directory': '~/My Pictures/Wallpapers'}
    with open(confdir + '/wallpaper-reddit.conf', 'w') as configfile:
        config.write(configfile)


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
    global titlegravity
    global titlefont
    global resize
    global setcmd
    global startupinterval
    global startupattempts
    global savedir
    global randomsub
    subs = config.get('Options', 'subs', fallback='earthporn,spaceporn,skyporn,technologyporn,imaginarystarscapes')
    subs = [x.strip() for x in subs.split(',')]
    maxlinks = config.getint('Options', 'maxlinks', fallback=15)
    minwidth = config.getint('Options', 'minwidth', fallback=1024)
    minheight = config.getint('Options', 'minheight', fallback=768)
    resize = config.getboolean('Options', 'resize', fallback=False)
    randomsub = config.getboolean('Options', 'random', fallback=False)
    setcmd = config.get('SetCommand', 'setcommand', fallback='')
    settitle = config.getboolean('Title Overlay', 'settitle', fallback=False)
    titlesize = config.getint('Title Overlay', 'titlesize', fallback=20)
    titlegravity = config.get('Title Overlay', 'titlegravity', fallback='south')
    titlefont = config.get('Title Overlay', 'titlefont', fallback='')
    startupinterval = config.getint('Startup', 'interval', fallback=3)
    startupattempts = config.getint('Startup', 'attempts', fallback=10)
    savedir = os.path.expanduser(config.get('Save', 'directory', fallback="~/Pictures/Wallpaper"))


# parses command-line arguments and stores them to proper global variables
def parse_args():
    parser = argparse.ArgumentParser(description="Pulls wallpapers from specified subreddits in reddit.com")
    parser.add_argument("subreddits", help="subreddits to check for wallpapers", nargs="*")
    parser.add_argument("-v", "--verbose", help="increases program verbosity", action="store_true")
    parser.add_argument("-f", "--force",
                        help="forces wallpapers to re-download even if it has the same url as the current wallpaper",
                        action="store_true")
    parser.add_argument("--height", type=int, help='minimum height of the image in pixels')
    parser.add_argument("--width", type=int, help='minimum width of the image in pixels')
    parser.add_argument("--maxlinks", type=int, help="maximum amount of links to check before giving up")
    parser.add_argument("--startup", help="runs the program as a startup application, waiting on internet connection",
                        action="store_true")
    parser.add_argument("--save",
                        help='saves the current wallpaper (requires a subreddit, but does not use it or download wallpaper)',
                        action="store_true")
    parser.add_argument("--resize", help="resizes the image to the specified height and width after wallpaper is set",
                        action="store_true")
    parser.add_argument("--blacklist", help="blacklists the current wallpaper and redownloads a new wallpaper",
                        action="store_true")
    parser.add_argument("--random",
                        help="will pick a random subreddit from the ones provided instead of turning them into a multireddit",
                        action="store_true")
    parser.add_argument("--settitle", help="write title over the image", action="store_true")
    parser.add_argument("--titlesize", type=int, help='font size of title in pixels')
    parser.add_argument("--titlegravity",
                        help='corner of title, follows imagemagick compass directions (south, north, northeast, etc.)')
    parser.add_argument("--titlefont",
                        help="font of the title overlay, use 'convert -list font' to get the list of valid fonts")
    parser.add_argument("--nocleanup",
                        help="does not remove the original downloaded image from the /tmp directory after wallpaper is set",
                        action="store_false")
    args = parser.parse_args()
    global subs
    global verbose
    global save
    global force_dl
    global startup
    global maxlinks
    global minheight
    global minwidth
    global titlesize
    global titlegravity
    global titlefont
    global resize
    global settitle
    global cleanup
    global randomsub
    global blacklistcurrent
    if not args.subreddits == []:
        subs = args.subreddits
    verbose = args.verbose
    save = args.save
    startup = args.startup
    force_dl = args.force
    if args.maxlinks:
        maxlinks = args.maxlinks
    if args.height:
        minheight = args.height
    if args.width:
        minwidth = args.width
    if args.titlesize:
        titlesize = args.titlesize
    if args.titlegravity:
        titlegravity = args.titlegravity
    if args.titlefont:
        titlefont = args.titlefont
    if args.resize:
        resize = True
    if args.settitle:
        settitle = True
    if not args.nocleanup:
        cleanup = False
    if args.random:
        randomsub = True
    if args.blacklist:
        blacklistcurrent = True
    main.log("config and args parsed")
