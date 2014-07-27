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
  
If no subreddits are specified, the script will default to the top image from the /r/earthporn, /r/spaceporn, /r/skyporn, /r/technologyporn, and /r/imaginarystarscapes.  There are many, many more options, all of which you can see by typing:

  wallpaper-reddit -h
  
Now, the script will throw errors until you properly configure it.  The config file is in ~/.config/wallpaper-reddit, and will be created automatically.  Due to the varying nature of window managers, every user will have to set a command to set the wallpaper.  This can be researched per desktop environment, although the provided (deleteable) examples should cover a large portion of window managers.  Changing the other options in the config file is optional, but recommended.
