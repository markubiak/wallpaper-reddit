# About
wallpaper-reddit is a Python 3 program that sets your wallpaper to the top image of one or multiple subreddits.  Version 3 has introduced many changes, such as the removal of all external dependencies, automatic DE detection for wallpaper setting, and proper setup using setuptools.

# Installation
RPMs for Fedora 23, Fedora 24, Ubuntu 16.04/Linux Mint 18 can be found on the [Releases Page] (https://github.com/markubiak/wallpaper-reddit/releases)
Users of Ubuntu derivatives <16.04 will have to build from source, as the version of PIL shipped with those versions of Ubuntu is outdated.
Arch users can get the package from the [AUR](https://aur.archlinux.org/packages/wallpaper-reddit-git/)  

From Source:
1. Install Pillow 3.x or the libraries necessary to compile it from scratch if the distribution you're using does not package it:  
  - Ubuntu <16.04/Linux Mint 17/ElementaryOS: `sudo apt-get install python3-dev python3-setuptools libjpeg8-dev zlib1g-dev libfreetype6-dev`
  - Fedora: `sudo dnf install python3-imaging` (installed by default)  
  - Arch: `sudo pacman -S python-pillow`  
  - Mac OS X El Capitan: 
    * `xcode-select --install`
    * `pip install pillow`
2. Clone the repository and navigate into the directory with the setup.py file.  
3. Run `sudo python3 setup.py install`  

# Usage
The script is very simple to use.  Simply type:

  `wallpaper-reddit [subreddits]`
  
If no subreddits are specified, the script will default to the top image from the subs section of the config file.  There are many, many more options, all of which you can see by typing:

  `wallpaper-reddit --help`

# Configuration
The config file is in `~/.config/wallpaper-reddit`, and will be created automatically.  Currently, the GNOME, XFCE, MATE, Unity, and Cinnamon Desktop Environments should be automatically detected and the program should set the wallpaper without any extra work.  However, due to the varying nature of window managers, it is possible, even likely, that you may have to specify a custom command to set your wallpaper.  The program will prompt you for this if this is the case; the exact command can be researched per desktop environment.  If your desktop environment is not supported, please file an issue so that automatic support can be implemented for others.  
### Config Options:  
- `minwidth` and `minheight` set the minimum dimensions the program will consider a valid candidate for a wallpaper.  If `--resize` is enabled, the script will resize the image to those dimensions before setting the wallpaper.
- `maxlinks` is the maximum number of links the script will go through before giving up.
- `resize` does the same thing as the `--resize` flag.  It is enabled by default.
- `random` does the same thing as the `--random` flag.

# Overlay Titles
The program has an option to overlay the title of the image directly onto the image itself, so using conky to constantly read the title of the image from `~/.wallpaper/title.txt` is no longer necessary (although it still works, and is recommended if not using the "resize" option).  This function is not enabled by default, but it can be enabled with either the `--settitle` command line flag or more permanently in the config under the `[Title Overlay]` section. There are five options for setting titles: size, x/y alignment, and x/y offset.  

### Overlay Title Configuration Options
Options for the overlay title can only be set in the config file.  They are under the [Title Overlay] section.
 - `titlesize` sets the font height at which the title will be rendered, in pixels.
 - `titlealignx` sets the horizontal alignment of the title, and can be either `left`, `center` or `right`.
 - `titlealigny` sets the vertical alignment, and can be `top` or `bottom`.
 - `titleoffsetx` and `titleoffsety` allow you to set an additional offset from the edge of the image, in pixels.

# Startup
If wallpaper-reddit is run with the `--startup` flag, the program will wait on an internet connection.   Once startup is activated, the script will try to connect to Reddit to download new wallpaper upon startup.  The default setting is an interval of 3 and 10 attempts, which means that the script will try to connect to Reddit every 3 seconds for up to 10 tries, giving a total of 30 seconds before the script gives up.

### Startup Configuration Options
Options for the startup can only be set in the config file.  They are under the [Startup] section.
-  `interval` describes the amount of time, in seconds, between wallpaper-reddit's attempts to procure new wallpaper.
 - `attempts` describes the number of attempts that will be made to connect to Reddit. After this number of attempts has failed, wallpaper-reddit will cease to try downloading wallpaper during the current startup.

# Saving
If wallpaper-reddit is run with the `--save` flag, no wallpaper will be downloaded.  The current wallpaper will be copied to the save directory, as specified in the config file (default is `~/Pictures/Wallpapers` on Linux, `~/My Pictures/Wallpapers` on Windows), and its title will be put into a titles.txt file inside the same directory.

# Blacklists
There is a function to blacklist a certain wallpaper from the script if it is particularly ugly.  Simply run the script with the `--blacklist` flag.  The script will run as usual, but additionally blacklist your current wallpaper.  You'll get a new wallpaper and never see the old one again.

# External commands and wallpaper info
Because more information is always better, much more than the wallpaper itself exists in `~/.wallpaper`.
- `blacklist.txt` contains the urls of blacklisted wallpapers, one can manually add urls without issue.
- `url.txt` is the url of the current wallpaper
- `title.txt` is the title of the current wallpaper (useful if you want to put the title into conky)
- `external.sh` is a bash script that is run at the end of every execution of the script (Linux only).  Any extra commands to deal with the wallpaper can be safely placed in this bash script.  I personally have mine darken my xfce4-panel if the wallpaper is too bright at the top, and set the wallpaper as my SLiM/xscreensaver background.

# Contact
If there is an issue with the program, please file a GitHub issue.  If you need more specific help troubleshooting a specific desktop or have an issue that isn't worthy of GitHub, feel free to reach out to me on Reddit: [/u/wallpaper-reddit](https://www.reddit.com/u/wallpaper-reddit)
