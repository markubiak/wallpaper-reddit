import argparse
import configparser
import os
import platform
from pkg_resources import resource_string
from wpreddit.common import log, exit_msg, set_verbose

# global config dictionary, init to working defaults
cfg = {
    'mode': "normal",
    'subs': ["earthporn", "spaceporn", "skyporn", "imaginarystarscapes"],
    'sorting_alg': "hot",
    'random_sub': False,
    'force_download': False,
    'max_links': 20,
    'resize': False,
    'os': "",
    'set_command': "",
    'external_script': "/external.sh",
    'dirs': {
        'data': "",
        'config': "",
        'save': ""
    },
    'startup': {
        'interval': 3,
        'attempts': 10
    },
    'min_dimensions': {
        'width': 1920,
        'height': 1080,
        'ratio': 0.0
    },
    'title': {
        'set': False,
        'size_px': 24,
        'align_x': "right",
        'align_y': "top",
        'offset_x_px': 5,
        'offset_y_px': 5
    }
}


def init_config():

    cfg['os'] = platform.system()

    # Get the full path of the directory per platform
    if cfg['os'] == "Linux":
        xdg_config = os.getenv('XDG_CONFIG_HOME')
        xdg_data = os.getenv('XDG_DATA_HOME')
        if xdg_config is not None:
            cfg['dirs']['config'] = os.path.expanduser(xdg_config + "/wallpaper-reddit")
        else:
            cfg['dirs']['config'] = os.path.expanduser("~/.config/wallpaper-reddit")
        if xdg_data is not None:
            cfg['dirs']['data'] =  os.path.expanduser(xdg_data + "/wallpaper-reddit")
        else:
            cfg['dirs']['data'] = os.path.expanduser("~/.local/share/wallpaper-reddit")
    elif cfg['os'] == "Windows":
        appdata = os.getenv("APPDATA")
        cfg['dirs']['config'] = os.path.expanduser(appdata + "/wallpaper-reddit/config")
        cfg['dirs']['data'] = os.path.expanduser(appdata + "/wallpaper-reddit/data")
    elif cfg['os'] == "Darwin":
        cfg['dirs']['config'] = os.path.expanduser("~/Library/Preferences/wallpaper-reddit")
        cfg['dirs']['data'] = os.path.expanduser("~/Library/Application Support/wallpaper-reddit")
    else:
        exit_msg("Operating system \"" + cfg['os'] + "\" incorrectly identified or unsupported.")

    # Make the paths if they are nonexistent
    if not os.path.exists(cfg['dirs']['data']):
        os.makedirs(cfg['dirs']['data'])
        log(cfg['dirs']['data'] + " created")
    if not os.path.exists(cfg['dirs']['config']):
        os.makedirs(cfg['dirs']['config'])
        log(cfg['dirs']['config'] + " created")

    # Create empty versions of specific files if necessary
    if not os.path.exists(cfg['dirs']['data'] + '/blacklist.txt'):
        with open(cfg['dirs']['data'] + '/blacklist.txt', 'w') as blacklist:
            blacklist.write('')
    if not os.path.exists(cfg['dirs']['data'] + '/url.txt'):
        with open(cfg['dirs']['data'] + '/url.txt', 'w') as urlfile:
            urlfile.write('')
    if not os.path.exists(cfg['dirs']['data'] + '/fonts'):
        os.makedirs(cfg['dirs']['data'] + '/fonts')
    if not os.path.exists(cfg['dirs']['data'] + '/fonts/Cantarell-Regular.otf'):
        with open(cfg['dirs']['data'] + '/fonts/Cantarell-Regular.otf', 'wb') as font:
            font.write(resource_string(__name__, 'fonts/Cantarell-Regular.otf'))
    if not os.path.isfile(cfg['dirs']['config'] + '/wallpaper-reddit.conf'):
        if cfg['os'] == 'Windows':
            cfile = resource_string(__name__, 'conf_files/windows.conf')
        else:
            cfile = resource_string(__name__, 'conf_files/unix.conf')
        with open(cfg['dirs']['config'] + '/wallpaper-reddit.conf', 'wb') as f:
            f.write(cfile)

    # Get the configuration, start with cfg files and use args as overrides
    parse_config()
    parse_args()
    log("config and args parsed")


# reads the configuration file
def parse_config():

    # read the config and check the version
    config = configparser.ConfigParser()
    config.read(cfg['dirs']['config'] + '/wallpaper-reddit.conf')
    if config.get('misc', 'version', fallback="0") is not "4":
        exit_msg("You are using an old configuration file.  Please delete your config file in " +
                 cfg['dirs']['config'] + " and let the program create a new one.")

    # core
    subs = [x.strip() for x in config.get('core', 'subs').split(',')]
    random_sub = config.getboolean('core', 'random_sub')
    sorting_alg = config.get('core', 'sorting_alg')
    max_links = config.getint('core', 'max_links')
    resize = config.getboolean('core', 'resize')
    set_command = config.get('core', 'set_command')
    if subs is not None:
        cfg['subs'] = subs
    if random_sub is not None:
        cfg['random_sub'] = random_sub
    if sorting_alg is not None:
        cfg['sorting_alg'] = sorting_alg
    if max_links is not None:
        cfg['max_links'] = max_links
    if resize is not None:
        cfg['resize'] = resize
    if set_command is not None:
        cfg['set_command'] = set_command

    # min dimensions
    min_width = config.getint('min_dimensions', 'width')
    min_height = config.getint('min_dimensions', 'height')
    min_ratio = config.getfloat('min_dimensions', 'ratio')
    if min_width is not None:
        cfg['min_dimensions']['width'] = min_width
    if min_height is not None:
        cfg['min_dimensions']['height'] = min_height
    if min_ratio is not None:
        cfg['min_dimensions']['ratio'] = min_ratio

    # title overlay
    set_title = config.getboolean('title', 'set')
    size_px = config.getint('title', 'size_px')
    align_x = config.get('title', 'align_x')
    align_y = config.get('title', 'align_y')
    offset_x_px = config.getint('title', 'offset_x_px')
    offset_y_px = config.getint('title', 'offset_y_px')
    if set_title is not None:
        cfg['title']['set'] = set_title
    if size_px is not None:
        cfg['title']['size_px'] = size_px
    if align_x is not None:
        cfg['title']['align_x'] = align_x
    if align_y is not None:
        cfg['title']['align_y'] = align_y
    if offset_x_px is not None:
        cfg['title']['offset_x_px'] = offset_x_px
    if offset_y_px is not None:
        cfg['title']['offset_y_px'] = offset_y_px

    # startup
    interval = config.getint('startup', 'interval')
    attempts = config.getint('startup', 'attempts')
    if interval is not None:
        cfg['startup']['interval'] = interval
    if attempts is not None:
        cfg['startup']['attempts'] = attempts

    # save
    if cfg['os'] == 'Windows':
        default_save_dir = "~/My Pictures/Wallpapers"
    else:
        default_save_dir = "~/Pictures/Wallpapers"
    cfg['dirs']['save'] = os.path.expanduser(config.get(
        'Save', 'directory', fallback=default_save_dir))


# parses command-line arguments and stores them to proper global variables
def parse_args():
    # parsing configuration
    sort_alg_values = ["hot", "new", "controversial", "top", "rising"]
    parser = argparse.ArgumentParser(description="Pulls wallpapers from subreddits of reddit.com")
    parser.add_argument("subreddits",
                        help="subreddits to check for wallpapers",
                        nargs="*")
    parser.add_argument("-v", "--verbose",
                        help="increases program verbosity",
                        action="store_true")
    parser.add_argument("-f", "--force",
                        help="forces wallpapers to re-download and ignores optimizations",
                        action="store_true")
    parser.add_argument("--startup",
                        help="runs the program as a startup application, waiting on internet connection",
                        action="store_true")
    parser.add_argument("--autostart",
                        help="sets the program to automatically run on every desktop login (Linux only)",
                        action="store_true")
    parser.add_argument("--save",
                        help='saves the current wallpaper to ' + cfg['dirs']['save'],
                        action="store_true")
    parser.add_argument("--resize",
                        help="resizes the image to the height and width specified in the config after "
                                         "wallpaper is set.  Enabled by default in the configuration file,",
                        action="store_true")
    parser.add_argument("--blacklist",
                        help="blacklists the current wallpaper and downloads a new wallpaper",
                        action="store_true")
    parser.add_argument("-s", "--sort-alg",
                        help="choose Reddit's sorting algorithm from {} (default=hot)".format(sort_alg_values))
    parser.add_argument("--random",
                        help="will pick a random subreddit instead of turning them into a multireddit",
                        action="store_true")
    parser.add_argument("--set-title",
                        help="write title over the image",
                        action="store_true")

    args = parser.parse_args()
    if not args.subreddits == []:
        cfg['subs'] = args.subreddits
    set_verbose(args.verbose)
    cfg['force_download'] = args.force
    # mode switch
    if args.save:
        cfg['mode'] = "save_current"
    elif args.startup:
        cfg['mode'] = "startup"
    elif args.autostart:
        cfg['mode'] = "gen_autostart"
    elif args.blacklist:
        cfg['mode'] = "blacklist_current"
    if args.resize:
        cfg['resize'] = True
    if args.set_title:
        cfg['title']['set'] = True
    if args.random:
        cfg['random_sub'] = True
    if args.sort_alg in sort_alg_values:
        cfg['sorting_alg'] = args.sort_alg
