#! /usr/bin/env python

#Dependencies:
#- imagemagick (only 'convert' and 'identify')
#- curl
#- ping

#import libs
import argparse
import configparser
import os
import urllib.request
import json
import shutil
import sys
import time
import random
from socket import timeout
from urllib.error import HTTPError,URLError

#global vars
verbose = False
startup = False
startupinterval = 0
startupattempts = 0
save = False
subs = []
minwidth = 0
minheight = 0
maxlinks = 0
resize = False
cleanup = False
randomsub = False
blacklistcurrent = False
setcmd = ''
walldir = os.getenv("HOME") + '/.wallpaper'
confdir = os.getenv("HOME") + '/.config/wallpaper-reddit'
tmpdir = '/tmp/wallpaper-reddit'
savedir = ''
    
def main():
  try:
    #create directories and files that don't exist
    make_dirs()
    #read arguments and configs
    parse_config()
    parse_args()
    #now create save directory, as that has to be loaded from conf
    make_save_dirs()
    #check to make sure the user has actually configged the program
    if setcmd == '':
      print('It appears you have not set the command to set wallpaper from your DE.  Check the config file at ~/.config/wallpaper-reddit')
      sys.exit(1)
    #blacklist the current wallpaper if requested
    if blacklistcurrent:
      blacklist_current()
    #check if the program is run in a special case (save or startup)
    if save:
      save_wallpaper()
      sys.exit(0)
    #check to make sure the user provided subreddits (checking now so that the user doesn't have to provide a sub to save their wallpaper)
    if startup:
      wait_for_connection('www.reddit.com', startupattempts, startupinterval)
    #make sure you're actually connected to reddit
    if not connected('http://www.reddit.com'):
      print("ERROR: You do not appear to be connected to Reddit. Exiting")
      sys.exit(1)
    #download the image
    links = get_links(subs)
    imgurls = links[0]
    titles = links[1]
    valid = choose_valid(links[0])
    valid_url = valid[0]
    title_index = valid[1]
    download_image(valid_url)
    #resize image if need be
    if resize:
      resize_image(tmpdir + '/download')
    #move and set the wallpaper
    shutil.copyfile(tmpdir + '/download', walldir + '/wallpaper')
    #save link of original image for reference and set the wallpaper
    save_info(valid_url, titles, title_index)
    set_wallpaper(setcmd)
    #cleanup
    if cleanup:
      shutil.rmtree(tmpdir)
      log(tmpdir + " cleaned out")
    external_script()
  except KeyboardInterrupt:
    sys.exit(1)
  except timeout:
    print('Connection timed out')
    sys.exit(1)
  except (HTTPError, URLError):
    print('Connection error, exiting')
    sys.exit(1)

#in - string - messages to print
#takes a string and will print it as output if verbose
def log(info):
  if verbose:
    print(info)

#creates directories and files if they do not exist
def make_dirs():
  if not os.path.exists(walldir):
    os.makedirs(walldir)
    log("~/.wallpaper created")
  if not os.path.exists(walldir + '/blacklist.txt'):
    with open(walldir + '/blacklist.txt', 'w') as blacklist:
      blacklist.write('')
  if not os.path.exists(tmpdir):
    os.makedirs(tmpdir)
    log("/tmp/wallpaper-reddit created")
  if not os.path.exists(confdir):
    os.makedirs(confdir)
    log("~/.config/wallpaper-reddit created")
  if not os.path.isfile(confdir + '/wallpaper-reddit.conf'):
    make_config()
    print("default config file created at ~/.config/wallpaper-reddit/wallpaper-reddit.conf. You need to do some minimal configuration before the program will work")
    sys.exit(0)

#creates directories for the saved images, as that directory has to be loaded from the config file
def make_save_dirs():
  if not os.path.exists(savedir):
    os.makedirs(savedir)
    log(savedir + " created")
  if not os.path.isfile(savedir + '/titles.txt'):
    with open(savedir + '/titles.txt', 'w') as f:
      f.write('Titles of the saved wallpapers:')
    log(savedir + "/titles.txt created")
#in - string - web page url
#out - boolean - connection status
#checks whether the program can connect to the specified url
def connected(url):
  try:
    uaurl = urllib.request.Request(url, headers={ 'User-Agent' : 'wallpaper-reddit python script by /u/MarcusTheGreat7'})
    urllib.request.urlopen(uaurl,timeout=3)
    return True
  except (HTTPError, URLError, timeout):
    return False

#in - string, int, int - url to check for connection, how many attempts and at what interval to retry until connected
#out - boolean - whether the connection was successfully establised
#waits for a connection to the specified url, or returns False if no connection could be made in the time frame
def wait_for_connection(url, tries, interval):
  #For some reason, urllib wouldn't connect to the web if I connected to wifi while it was running.  The ping command is a workaround.
  for i in range(tries):
    status = os.system('ping -c 1 ' + url + ' >/dev/null 2>&1')
    #catches the exit code of the ping command.  returning 0 mens ping made a connection
    if status == 0:
      return True
    else:
      time.sleep(interval)
  return False

#creates a default config file with examples in ~/.config/wallpaper-reddit
def make_config():
  config = configparser.ConfigParser()
  config['SetCommand'] = { 'setcommand': '' }
  config['SetCommandExamples'] = { 'examples': 'feel free to delete these, wallpaper will be ~/.wallpaper/wallpaper',
                           'example_gnome3: gnome3 (Unity, Cinnamon, Gnome 3)': 'gsettings set org.gnome.desktop.background picture-uri file:///home/user/.wallpaper/wallpaper',
                           'example_gnome2: gnome2 (Metacity, MATE)': 'gconftool-2 -t string -s /desktop/gnome/background/picture_filename "/home/user/.wallpaper/wallpaper"',
                           'example_xfce4': 'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/image-path -s "" && xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/image-path -s "/home/user/.wallpaper/wallpaper"',
                           'example_bash': 'bash /home/user/.config/wallpaper-reddit/some-script.sh' }
  config['Options'] = { 'subs': 'earthporn,spaceporn,skyporn,technologyporn,imaginarystarscapes',
                        'minwidth': '1024',
                        'minheight': '768',
                        'maxlinks': '15',
                        'resize': 'False',
                        'cleanup': 'True',
                        'random': 'False' }
  config['Startup'] = { 'attempts': '10',
                        'interval': '3' }
  config['Save'] = { 'directory': '~/Pictures/Wallpapers' }
  with open(confdir + '/wallpaper-reddit.conf', 'w') as configfile:
    config.write(configfile)

#reads the configuration at ~/.config/wallpaper-reddit
def parse_config():
  config = configparser.ConfigParser()
  config.read(confdir + '/wallpaper-reddit.conf')
  global subs
  global maxlinks
  global minheight
  global minwidth
  global resize
  global cleanup
  global setcmd
  global startupinterval
  global startupattempts
  global savedir
  global randomsub
  subs = config.get('Options', 'subs', fallback='earthporn,spaceporn,skyporn,technologyporn,imaginarystarscapes')
  subs = subs.split(',')
  maxlinks = config.getint('Options', 'maxlinks', fallback=15)
  minwidth = config.getint('Options', 'minwidth', fallback=1024)
  minheight = config.getint('Options', 'minheight', fallback=768)
  resize = config.getboolean('Options', 'resize', fallback=False)
  cleanup = config.getboolean('Options', 'cleanup', fallback=True)
  randomsub = config.getboolean('Options', 'random', fallback=False)
  setcmd = config.get('SetCommand', 'setcommand', fallback='')
  startupinterval = config.getint('Startup', 'interval', fallback=3)
  startupattempts = config.getint('Startup', 'attempts', fallback=10)
  savedir = config.get('Save', 'directory', fallback=os.getenv("HOME") + '/Pictures/Wallpapers').replace('~', os.getenv("HOME"))
  
#parses command-line arguments and stores them to proper global variables  
def parse_args():
  parser = argparse.ArgumentParser(description="Pulls wallpapers from specified subreddits in reddit.com")
  parser.add_argument("subreddits", help="subreddits to check for wallpapers", nargs="*")
  parser.add_argument("-v", "--verbose", help="increases program verbosity", action="store_true")
  parser.add_argument("--maxlinks", type=int, help="maximum amount of links to check before giving up")
  parser.add_argument("--height", type=int, help='minimum height of the image in pixels')
  parser.add_argument("--width", type=int, help='minimum width of the image in pixels')
  parser.add_argument("--startup", help="runs the program as a startup application, waiting on internet connection", action="store_true")
  parser.add_argument("--save", help='saves the current wallpaper (requires a subreddit, but does not use it or download wallpaper)', action="store_true")
  parser.add_argument("--resize", help="resizes the image to the specified height and width after wallpaper is set", action="store_true")
  parser.add_argument("--nocleanup", help="does not remove the original downloaded image from the /tmp directory after wallpaper is set", action="store_false")
  parser.add_argument("--blacklist", help="blacklists the current wallpaper and redownloads a new wallpaper", action="store_true")
  parser.add_argument("--random", help="will pick a random subreddit from the ones provided instead of turning them into a multireddit", action="store_true")
  args = parser.parse_args()
  global subs
  global verbose
  global save
  global startup
  global maxlinks
  global minheight
  global minwidth
  global resize
  global cleanup
  global randomsub
  global blacklistcurrent
  if not args.subreddits == []:
    subs = args.subreddits
  verbose = args.verbose
  save = args.save
  startup = args.startup
  if args.maxlinks:
    maxlinks = args.maxlinks
  if args.height:
    minheight = args.height
  if args.width:
    minwidth = args.width
  if args.resize:
    resize = True
  if not args.nocleanup:
    cleanup = False
  if args.random:
    randomsub = True
  if args.blacklist:
    blacklistcurrent = True
  log("config and args parsed")

#in - string[] - list of subreddits to get links from
#out - string[], string[] - a list of links from the subreddits and their respective titles
#takes in subreddits, converts them to a reddit json url, and then picks out urls and their titles
def get_links(subreddits):
  if randomsub:
    parsedsubs = pick_random(subreddits)
  else:
    parsedsubs = subreddits[0]
    for sub in subs[1:]:
      parsedsubs = parsedsubs + '+' + sub
  url = "http://www.reddit.com/r/" + parsedsubs + ".json?limit=" + str(maxlinks)
  log("Grabbing json file " + url)
  uaurl = urllib.request.Request(url, headers={ 'User-Agent' : 'wallpaper-reddit python script by /u/MarcusTheGreat7' })
  response = urllib.request.urlopen(uaurl)
  content = response.read()
  data = json.loads(content.decode("utf8"))
  dump = json.dumps(data, sort_keys=True, indent=0)
  links = []
  titles = []
  for ln in dump.split('\n'):
    if ln[0:6] == '"url":':
      links.append(ln[8:len(ln) - 2])
    if ln[0:8] == '"title":':
      titles.append(ln[10:len(ln) - 2])
  return links, titles

#in - string[] - list of links to check
#out - string, int - first link to match all criteria and its index (for matching it with a title)
#takes in a list of links and attempts to find the first one that is a direct image link, is within the proper dimensions, and is not blacklisted
def choose_valid(links):
  #checks that there are subreddits to check
  if len(links) == 0:
    print("No links were returned from any of those subreddits. Are they valid?")
    sys.exit(1)
  index = 0
  for link in links:
    log("checking url " + link)
    #checks for direct image links
    if link[len(link)-4:len(link)] == '.png' or link[len(link)-4:len(link)] == '.jpg' or link[len(link)-5:len(link)] == '.jpeg':
      log(link + " appears to be an image")
      #if links is direct image, make sure the porgram can get the link, that it fits the minimum dimensions, and that it's not blacklisted
      if connected(link) and check_dimensions(link) and check_blacklist(link):
        return link, index
    else:
      log(link + " was not a valid image")
    index = index + 1
  print("No valid links found.  Exiting")
  sys.exit(1)
      
#in - string - link to check dimensions of
#out - boolean - if the link fits the proper dimensions
#takes a link and checks to see if the link will match the minimum dimensions
def check_dimensions(url):
  #this is a very odd function, and super hack-y.  Python's urllib libraries would not partially download images.
  #in addition, python3 has no built-in libs to check images, and I didn't feel like making this a huge program, so I used imagemagicks's identify command
  os.system("curl --post301 --location -so " + tmpdir + "/header -r0-10000 " + url) #downloads only the first 10k of the image (for the headers)
  os.system("identify /tmp/wallpaper-reddit/header >" + tmpdir + "/headernew 2>/dev/null") #the ending saves the dimensions in /tmp, but ignores errors
  with open(tmpdir + "/headernew", 'r') as headfile:
    info = headfile.read()
  if info != '':
    dimensions = info.split(' ')[2].split('x') #picks out the dimensions
    if int(dimensions[0]) >= minwidth and int(dimensions[1]) >= minheight:
      log(url + " fits minimum dimensions")
      return True
  log(url + " is too small")
  return False

#credit: http://www.techniqal.com/blog/2011/01/18/python-3-file-read-write-with-urllib/
#in - string - direct url of the image to download
#downloads the specified image to /tmp/wallpaper-reddit/download
def download_image(url):
  uaurl = urllib.request.Request(url, headers={ 'User-Agent' : 'wallpaper-reddit python script by /u/MarcusTheGreat7'})
  f = urllib.request.urlopen(uaurl)
  log("downloading " + url)
  with open(tmpdir + "/download", "wb") as local_file:
    local_file.write(f.read())
  
#in - string - command to set the wallpaper from ~/.wallpaper/wallpaper
#uses the user-specified command to set the downloaded-then-moved wallpaper
def set_wallpaper(wpsetcommand):
  os.system(wpsetcommand)
  log(walldir + "/wallpaper was set as the wallpaper")

#in - string - path of the image to resize
#resizes the image to the minimum width and height from the config/args
def resize_image(path):
  log("resizing the downloaded wallpaper")
  #uses the imagemagick 'convert' command to resize the image
  command = 'convert ' + path + ' -resize ' + str(minwidth) + 'x' + str(minheight) + '^ -gravity center -extent ' + str(minwidth) + 'x' + str(minheight) + ' ' + path
  os.system(command)

#in - string - a url to match against the blacklist
#out - boolean - whether the url is blacklisted
#checks to see if the url is on the blacklist or not (True means the link is good)
def check_blacklist(url):
  with open(walldir + '/blacklist.txt', 'r') as blacklist:
    bl_links = blacklist.read().split('\n')
  for link in bl_links:
    if link == url:
      return False
  return True

#blacklists the current wallpaper, as listed in the ~/.wallpaper/url.txt file
def blacklist_current():
  if not os.path.isfile(walldir + '/url.txt'):
    print('ERROR: ~/.wallpaper/url.txt does not exist.  wallpaper-reddit must run oncce before you can blacklist a wallpaper.')
    sys.exit(1)
  with open(walldir + '/url.txt', 'r') as urlfile:
    url = urlfile.read()
  with open(walldir + '/blacklist.txt', 'a') as blacklist:
    blacklist.write(url + '\n')

#in - string, string[], int - a url, a list of titles, and the index of the correct title of the picture
#saves the url of the image to ~/.wallpaper/url.txt and the title of the image to ~/.wallpaper/title.txt, just for reference
def save_info(url, titles, title_index):
  title = titles[title_index].replace('\\"', '"')
  with open(walldir + '/url.txt', 'w') as urlinfo:
    urlinfo.write(url)
  with open(walldir + '/title.txt', 'w') as titleinfo:
    titleinfo.write(remove_tags(title))

#in - string - title of the picture
#out - string - title without any annoying tags
#removes the [tags] throughout the image
def remove_tags(str):
  tag = False
  title = ''
  for i in str:
    if i == '[':
      tag = True
    if not tag:
      title = title + i
    if i == ']':
      tag = False
  return title.strip()

#saves the wallpaper in the save directory from the config
#naming scheme is wallpaperN
def save_wallpaper():
  i = 0
  while os.path.isfile(savedir + '/wallpaper' + str(i)):
    i = i + 1
  shutil.copyfile(walldir + '/wallpaper', savedir + '/wallpaper' + str(i))
  with open(walldir + '/title.txt', 'r') as f:
    title = f.read()
  with open(savedir + '/titles.txt', 'a') as f:
    f.write('\n' + 'wallpaper' + str(i) + ': ' + title)
  log("current wallpaper saved to " + savedir + '/wallpaper' + str(i))

#creates and runs the ~/.wallpaper/external.sh script
def external_script():
  if not os.path.isfile(walldir + '/external.sh'):
    with open(walldir + '/external.sh', 'w') as external:
      external.write('#! /bin/bash\n\n#You can enter custom commands here that will execute after the main program is finished')
    os.system('chmod +x ' + walldir + '/external.sh')
  os.system('bash ' + walldir + '/external.sh')
  
#in: a list of subreddits
#out: the name of a random subreddit
#will pick a random sub from a list of subreddits
def pick_random(subreddits):
  rand = random.randint(0, len(subreddits) - 1)
  return subreddits[rand]

main()
