#About
wallpaper-reddit is a Python 3.4.1 script that simply sets your wallpaper to the top image from (a) subreddit(s) on reddit.com.

This is my first foray into Python, as Java is the only language I "know."  I always thought it would be cool to have some of the images from /r/earthporn and /r/spaceporn as wallpapers, and now I've automated it.

#Dependencies
- imagemagick package (just convert and identify programs)
- curl

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

--random: will pick a random subreddit from the list instead of creating a multireddit.  The default can be set in the config file.

#Startup
If wallpaper-reddit is run with the --startup flag, the program will wait on an internet connection.  Options for the startup can only be set in the config file.  They are under the [Startup] section: interval and attempts.  The script will try to make a connection to reddit.com $attempts times at every $interval seconds.  For example, the default setting is an interval of 3 and 10 attempts, so the script will try to connect to reddit every 3 seconds for up to 10 tries, giving a total of 30 seconds before the scrpit gives up.  As of v1.2, it should also catch if it is being redirected by the router (IE hotel/airport WiFi) As a reminder, this feature is only activated by the --startup flag

#Saving
If wallpaper-reddit is run with the --save flag, no wallpaper will be downloaded.  The current wallpaper will be copied to the save directory, as specified in the config file (default is ~/Pictures/Wallpapers), and its title will be put into a titles.txt file inside the same directory.

#Blacklists
There is a function to blacklist a certain wallpaper from the script, if it is particularly ugly.  Simply run the script with the --blacklist flag.  The script will run as usual, but additionally blacklist your current wallpaper.  You'll get a new wallpaper and never see the old one again.

#External commands and wallpaper info
Because more information is always better, much more than the wallpaper exists in ~/.wallpaper.
- blacklist.txt contains the urls of blacklisted wallpapers, one can manually add urls without issue.
- url.txt is the url of the current wallpaper
- title.txt is the title of the current wallpaper (useful if you want to put the title into conky!)
- external.sh is a bash script that is run at the end of every execution of the script.  Any extra commands to deal with the wallpaper can be safely places in this bash script.  I personally have mine darken my xfce4-panel if the wallpaper is too bright at the top, and set the wallpaper as my SLiM/xscreensaver background.

#Hacks for window managers that refuse to change wallpaper
Some WMs (like Pantheon) will not detect when a wallpaper updates.  Some, like XFCE, only need to have the wallpaper set to something else, then reset (thus why there is an example for it in there that does so).  However, some WMs will cache the wallpaper, which makes downloading a new one pointless, as the old one will simply be used.  To get around this, one can utilize change the command to change the wallpaper to run a bash script.  Edit ~/.config/wallpaper-reddit/wallpaper-reddit.conf and change the line to:

  setcommand = bash /home/user/.wallpaper/setwallpaper.sh
  
Then, create a bash script, ~/.wallpaper/setwallpaper.sh, and copy-paste the following into it (make sure to change the dirs to your username!)

    #! /bin/bash
    RAND=$RANDOM  #Creates a random int
    cd /home/user/.wallpaper  #Navigate to the proper directory
    rm `ls | grep wallpaper[0-9]`  #Removes any old copied wallpaper files (to reduce clutter)
    cp wallpaper wallpaper$RAND  #Copies the wallpaper to the new file
    gsettings set org.gnome.desktop.background picture-uri file:///home/user/.wallpaper/wallpaper$RAND  #Sets the wallpaper to the new, uncached file
  
Set the script as executable and everything should work!

What this block of code does is generate a random int (0-32767) and copy the wallpaper to wallpaper(random int).  This creates a new file that the WM has not cached before, forcing it to reload the wallpaper.  Only a 1 in 2^16 chance of failure, good enough for me.  The second line also makes sure any previous wallpapers get cleaned up
