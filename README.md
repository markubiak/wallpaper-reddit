#About

wallpaper-reddit is a Python 3.4.1 script that simply sets your wallpaper to the top image from (a) subreddit(s) on reddit.com.

This is my first foray into Python, as Java is the only language I "know."  I always thought it would be cool to have some of the images from /r/earthporn and /r/spaceporn as wallpapers, and now I've automated it.

#Dependencies
- imagemagick package (just convert and identify programs)
- curl
- ping

#Usage

The script is very simple to use.  If you have not copied the script to a folder such as /usr/bin or /usr/local/bin, make sure to cd into the directory of the script.  Then, type:

  wallpaper-reddit [subreddits]
  
If no subreddits are specified, the script will default to the top image from the subs section of the config file.  There are many, many more options, all of which you can see by typing:

  wallpaper-reddit -h
  
Now, the script will throw errors until you properly configure it.  The config file is in ~/.config/wallpaper-reddit, and will be created automatically.  Due to the varying nature of window managers, every user will have to set a command to set the wallpaper.  This can be researched per desktop environment, although the provided (deleteable) examples should cover a large portion of window managers.  Changing the other options in the config file is optional, but recommended.

#Options

-v or --verbose:  tells you what the program is doing (useful if you're on dialup or the script isn't getting wallpapers)

--maxlinks:  specifies how many links to process from the specified subreddits.  More will take longer to get, but may help if the subreddit isn't image-centric.  The default can be specified in the config file.

--height and --width:  specifies the minimum dimensions (in pixels) for the wallpaper to be to be considered a valid wallpaper.  The defaults can be specified in the config file.

--resize:  will resize the image to the height and width as specified by the command-line options or the config file before it is moved from /tmp to your home directory.  Useful for space saving and desktops that won't auto resize.  The default can be set in the config file.

--nocleanup:  will not remove the wallpaper-reddit folder from /tmp upon the script's completion.  The default can be set in the config file.

#Startup

If wallpaper-reddit is run with the --startup flag, the program will wait on an internet connection.  Options for the startup can only be set in the config file.  They are under the [Startup] section: interval and attempts.  The script will try to make a connection to reddit.com $attempts times at every $interval seconds.  For example, the default setting is an interval of 3 and 10 attempts, so the script will try to connect to reddit every 3 seconds for up to 10 tries, giving a total of 30 seconds before the scrpit gives up.  As a reminder, this feature is only activated by the --startup flag

#Saving

If wallpaper-reddit is run with the --save flag, no wallpaper will be downloaded.  The current wallpaper will be copied to the save directory, as specified in the config file (default is ~/Pictures/Wallpapers), and its title will be put into a titles.txt file inside the same directory.
