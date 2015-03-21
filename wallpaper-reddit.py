#! /usr/bin/env python3

#Dependencies:
#- imagemagick (only 'convert' and 'identify')

#import libs
import argparse
import configparser
import ctypes
import json
import os
import platform
import subprocess
import random
import re
import shutil
import sys
import tempfile
import time
import urllib.request
from collections import OrderedDict
from distutils import spawn
from random import randint
from socket import timeout
from urllib.error import HTTPError,URLError

#global vars
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

def main():
  try:
    check_requirements()
    #create directories and files that don't exist and init directories based on OS
    make_dirs()
    #read arguments and configs
    parse_config()
    parse_args()
    #now create save directory, as that has to be loaded from conf
    make_save_dirs()
    #check to make sure the user has actually configged the program
    if setcmd == '' and opsys == 'Linux':
      print('It appears you have not set the command to set wallpaper from your DE.  Check the config file at ~/.config/wallpaper-reddit')
      sys.exit(1)
    #blacklist the current wallpaper if requested
    if blacklistcurrent:
      blacklist_current()
    #check if the program is run in a special case (save or startup)
    if save:
      save_wallpaper()
      sys.exit(0)
    if startup:
      wait_for_connection(startupattempts, startupinterval)
    #make sure you're actually connected to reddit
    if not connected('http://www.reddit.com'):
      print("ERROR: You do not appear to be connected to Reddit. Exiting")
      sys.exit(1)
    #download the image
    links = get_links()
    imgurls = links[0]
    titles = links[1]
    valid = choose_valid(links[0])
    valid_url = valid[0]
    title_index = valid[1]
    title = titles[title_index]
    #prepare a temp file to downlad the wallpaper to
    tempimage = tempfile.NamedTemporaryFile(delete=False)
    tempimage.close()
    download_image(valid_url, tempimage.name)
    #resize image if need be
    if resize:
      resize_image(tempimage.name)
    if settitle:
      set_image_title(tempimage.name, title)
    #move and set the wallpaper
    if opsys == "Windows":
      shutil.copyfile(tempimage.name, walldir + '\\wallpaper.bmp')
      os.unlink(tempimage.name + ".bmp")
    else:
      shutil.copyfile(tempimage.name, walldir + '/wallpaper.jpg')
      os.unlink(tempimage.name + ".jpg")
    os.unlink(tempimage.name)
    #save link of original image for reference and set the wallpaper
    save_info(valid_url, title)
    set_wallpaper(setcmd)
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

#checks that all required commands can be found
def check_requirements():
  for cmd in (('convert','imagemagick'),('identify','imagemagick'),('mogrify','imagemagick')):
    if not spawn.find_executable(cmd[0]):
      print("Missing required program '%s'." %cmd[1])
      if opsys == "Linux":
        print("Please install from the package package manager and try again")
      else:
        print("Please install the imagemagick suite from http://imagemagick.org/script/binary-releases.php#windows and try again")
      sys.exit(1)

#creates directories and files if they do not exist
def make_dirs():
  global walldir
  global confdir
  global tmpdir
  if opsys == "Linux":
    walldir = os.path.expanduser("~/.wallpaper")
    confdir = os.path.expanduser("~/.config/wallpaper-reddit")
  else:
    walldir = os.path.expanduser("~/Wallpaper-Reddit")
    confdir = os.path.expanduser("~/Wallpaper-Reddit/Config")
  if not os.path.exists(walldir):
    os.makedirs(walldir)
    log(walldir + " created")
  if not os.path.exists(walldir + '/blacklist.txt'):
    with open(walldir + '/blacklist.txt', 'w') as blacklist:
      blacklist.write('')
  if not os.path.exists(walldir + '/url.txt'):
    with open(walldir + '/url.txt', 'w') as urlfile:
      urlfile.write('')
  if not os.path.exists(confdir):
    os.makedirs(confdir)
    log(confdir + " created")
  if not os.path.isfile(confdir + '/wallpaper-reddit.conf'):
    make_config()
    print("default config file created at " + confdir + "/wallpaper-reddit.conf. You need to do some minimal configuration before the program will work")
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
    uaurl = urllib.request.Request(url, headers={'User-Agent' : 'wallpaper-reddit python script by /u/MarcusTheGreat7'})
    url = urllib.request.urlopen(uaurl,timeout=3)
    url.close()
    return True
  except (HTTPError, URLError, timeout):
    return False

#out - boolean - connection status
#checks whether the program can connect to reddit and is not being redirected
def check_not_redirected():
  try:
    #Not reloading /etc/resolv.conf, since it will have to be reloaded for the function right before this is called
    uaurl = urllib.request.Request('http://www.reddit.com/.json', headers={ 'User-Agent' : 'wallpaper-reddit python script by /u/MarcusTheGreat7'})
    url = urllib.request.urlopen(uaurl,timeout=3)
    json.loads(url.read().decode('utf8'))
    url.close()
    return True
  except (HTTPError, URLError, timeout, AttributeError, ValueError):
    return False

#in - string, int, int - url to check for connection, how many attempts and at what interval to retry until connected
#out - boolean - whether the connection was successfully establised
#waits for a connection to the specified url, or returns False if no connection could be made in the time frame
def wait_for_connection(tries, interval):
  log('Waiting for a connection...')
  for i in range(tries):
    if opsys == "Linux":
      #Reloads /etc/resolv.conf
      #credit: http://stackoverflow.com/questions/21356781/urrlib2-urlopen-name-or-service-not-known-persists-when-starting-script-witho
      libc = ctypes.cdll.LoadLibrary('libc.so.6')
      res_init = libc.__res_init
      res_init()
    log('Attempt #' + str(i + 1) + ' to connect...')
    if connected('http://www.reddit.com'):
      log('Connected to the internet, checking if you\'re being redirectied...')
      if check_not_redirected():
        log('No redirection.  Starting the main script...')
        return True
      log('Redirected.  Trying again...')
    time.sleep(interval)
  return False

#creates a default config file with examples in ~/.config/wallpaper-reddit
def make_config():
  config = configparser.ConfigParser()
  config['SetCommand'] = OrderedDict([('setcommand', '')])
  config['SetCommandExamples'] = OrderedDict([('examples', 'feel free to delete these, wallpaper will be ~/.wallpaper/wallpaper'),
                                              ('example_gnome3: gnome3 (Unity, Cinnamon, Gnome 3)', 'gsettings set org.gnome.desktop.background picture-uri file:///home/user/.wallpaper/wallpaper'),
                                              ('example_gnome2: gnome2 (Metacity, MATE)', 'gconftool-2 -t string -s /desktop/gnome/background/picture_filename "/home/user/.wallpaper/wallpaper"'),
                                              ('example_xfce4', 'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/image-path -s "" && xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/image-path -s "/home/user/.wallpaper/wallpaper"'),
                                              ('example_bash', 'bash /home/user/.config/wallpaper-reddit/some-script.sh'),
                                              ('example_windows', 'Can be blank, unused for Windows operating systems')])
  config['Options'] = OrderedDict([('subs', 'earthporn,spaceporn,skyporn,technologyporn,imaginarystarscapes'),
                        ('minwidth', '1024'),
                        ('minheight', '768'),
                        ('maxlinks', '15'),
                        ('resize', 'False'),
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

#reads the configuration at ~/.config/wallpaper-reddit
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

#parses command-line arguments and stores them to proper global variables
def parse_args():
  parser = argparse.ArgumentParser(description="Pulls wallpapers from specified subreddits in reddit.com")
  parser.add_argument("subreddits", help="subreddits to check for wallpapers", nargs="*")
  parser.add_argument("-v", "--verbose", help="increases program verbosity", action="store_true")
  parser.add_argument("-f", "--force", help="forces wallpapers to re-download even if it has the same url as the current wallpaper", action="store_true")
  parser.add_argument("--height", type=int, help='minimum height of the image in pixels')
  parser.add_argument("--width", type=int, help='minimum width of the image in pixels')
  parser.add_argument("--maxlinks", type=int, help="maximum amount of links to check before giving up")
  parser.add_argument("--startup", help="runs the program as a startup application, waiting on internet connection", action="store_true")
  parser.add_argument("--save", help='saves the current wallpaper (requires a subreddit, but does not use it or download wallpaper)', action="store_true")
  parser.add_argument("--resize", help="resizes the image to the specified height and width after wallpaper is set", action="store_true")
  parser.add_argument("--blacklist", help="blacklists the current wallpaper and redownloads a new wallpaper", action="store_true")
  parser.add_argument("--random", help="will pick a random subreddit from the ones provided instead of turning them into a multireddit", action="store_true")
  parser.add_argument("--settitle", help="write title over the image", action="store_true")
  parser.add_argument("--titlesize", type=int, help='font size of title in pixels')
  parser.add_argument("--titlegravity", help='corner of title, follows imagemagick compass directions (south, north, northeast, etc.)')
  parser.add_argument("--titlefont", help="font of the title overlay, use 'convert -list font' to get the list of valid fonts")
  parser.add_argument("--nocleanup", help="does not remove the original downloaded image from the /tmp directory after wallpaper is set", action="store_false")
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
  log("config and args parsed")

#in - string[] - list of subreddits to get links from
#out - string[], string[] - a list of links from the subreddits and their respective titles
#takes in subreddits, converts them to a reddit json url, and then picks out urls and their titles
def get_links():
  print("searching for valid images...")
  if randomsub:
    parsedsubs = pick_random(subreddits)
  else:
    parsedsubs = subs[0]
    for sub in subs[1:]:
      parsedsubs = parsedsubs + '+' + sub
  url = "http://www.reddit.com/r/" + parsedsubs + ".json?limit=" + str(maxlinks)
  log("Grabbing json file " + url)
  uaurl = urllib.request.Request(url, headers={ 'User-Agent' : 'wallpaper-reddit python script, github.com/markubiak/wallpaper-reddit' })
  response = urllib.request.urlopen(uaurl)
  content = response.read().decode('utf-8')
  try:
    data = json.loads(content)
  except (AttributeError, ValueError):
    print('Was redirected from valid Reddit formatting.  Likely a router redirect, such as a hotel or airport.  Exiting...')
    sys.exit(0)
  response.close()
  links = []
  titles = []
  for i in data["data"]["children"]:
    links.append(i["data"]["url"])
    titles.append(i["data"]["title"])
  return links, titles

#in - string[] - list of links to check
#out - string, int - first link to match all criteria and its index (for matching it with a title)
#takes in a list of links and attempts to find the first one that is a direct image link, is within the proper dimensions, and is not blacklisted
def choose_valid(links):
  if len(links) == 0:
    print("No links were returned from any of those subreddits. Are they valid?")
    sys.exit(1)
  for i, origlink in enumerate(links):
    log("checking link #{0}: {1}".format(i, origlink))
    link = origlink
    if not(link[-4:] == '.png' or link[-4:] == '.jpg' or link[-5:] == '.jpeg'):
      if re.search('(imgur\.com)(?!/a/)', link):
        link = link.replace("/gallery", "")
        link += ".jpg"
      else:
        continue
    if not (connected(link) and check_dimensions(link) and check_blacklist(link)):
      continue
    def check_same_url(link):
      with open(walldir + '/url.txt', 'r') as f:
        currlink = f.read()
        if currlink == link:
          print("current wallpaper is the most recent, will not re-download the same wallpaper.")
          sys.exit(0)
        else:
          return True
    if force_dl or not(os.path.isfile(walldir + '/url.txt')) or check_same_url(link):
      return link, i
  print("No valid links were found from any of those subreddits.  Try increasing the maxlink parameter.")
  sys.exit(0)

#in - string - link to check dimensions of
#out - boolean - if the link fits the proper dimensions
#takes a link and checks to see if the link will match the minimum dimensions
def check_dimensions(url):
  resp = urllib.request.urlopen(urllib.request.Request(url, headers={
      'User-Agent' : 'wallpaper-reddit python script by /u/MarcusTheGreat7',
      'Range': 'bytes=0-1000'
  }))
  header = tempfile.NamedTemporaryFile(delete=False)
  header.write(resp.read())
  header.close()
  identifyinfo = tempfile.NamedTemporaryFile(delete=False)
  identifyinfo.close()
  if opsys == "Linux":
    os.system("identify -format %[fx:w]x%[fx:h] " + header.name + " > " + identifyinfo.name + " 2> /dev/null")
  else:
    os.system("identify -format %[fx:w]x%[fx:h] " + header.name + " > " + identifyinfo.name + " 2> nul")
  with open(identifyinfo.name, 'rb') as f:
    info = f.read().decode("utf-8")
  if info != '' and info != 'x':
    dimensions = info.split('x') #picks out the dimensions
    if int(dimensions[0]) >= minwidth and int(dimensions[1]) >= minheight:
      log(url + " fits minimum dimensions by identify test")
      os.unlink(header.name)
      os.unlink(identifyinfo.name)
      return True
    else:
      log(url + " is too small by identify test")
      os.unlink(header.name)
      os.unlink(identifyinfo.name)
      return False
  os.unlink(identifyinfo.name)
  if opsys != "Linux":
    os.unlink(header.name)
    log("dimensions of image could not be read")
    return False
  fileinfo = tempfile.NamedTemporaryFile(delete=False)
  fileinfo.close()
  os.system("file " + header.name + " > " + fileinfo.name + " 2>/dev/null")
  with open(fileinfo.name, 'rb') as f:
    info = f.read().decode("utf-8")
  if info != '':
    dimsearch = re.search('([5-9]{1}[0-9]{2}|[1-9]{1}[0-9]{3,})x([5-9]{1}[0-9]{2}|[1-9]{1}[0-9]{3,})', info)
    if dimsearch is not None:
      dimensions = dimsearch.group().split('x')
      if int(dimensions[0]) >= minwidth and int(dimensions[1]) >= minheight:
        log(url + " fits minimum dimensions by regex test 1")
        os.unlink(header.name)
        os.unlink(fileinfo.name)
        return True
      else:
        log(url + " is too small by regex test 1")
        os.unlink(header.name)
        os.unlink(fileinfo.name)
        return False
    heightsearch = re.search('width=([5-9]{1}[0-9]{2}|[1-9]{1}[0-9]{3,})', info)
    widthsearch = re.search('([5-9]{1}[0-9]{2}|[1-9]{1}[0-9]{3,})', info)
    if heightsearch is not None and widthsearch is not None:
      height = heightsearch.group(1)[7:]
      width = widthsearch.group(1)[6:]
      if int(width) >= minwidth and int(height) >= minheight:
        log(url + " fits minimum dimensions by regex test 2")
        os.unlink(header.name)
        os.unlink(fileinfo.name)
        return True
      else:
        log(url + " is too small bby regex test 2")
        os.unlink(header.name)
        os.unlink(fileinfo.name)
        return False
  log("dimensions of image could not be read")
  os.unlink(header.name)
  os.unlink(fileinfo.name)
  return False

#credit: http://www.techniqal.com/blog/2011/01/18/python-3-file-read-write-with-urllib/
#in - string - direct url of the image to download
#downloads the specified image to /tmp/wallpaper-reddit/download
def download_image(url, path):
  uaurl = urllib.request.Request(url, headers={ 'User-Agent' : 'wallpaper-reddit python script by /u/MarcusTheGreat7'})
  f = urllib.request.urlopen(uaurl)
  print("downloading " + url)
  with open(path, "wb") as local_file:
    local_file.write(f.read())
  f.close()
  if opsys == "Windows":
    os.system("mogrify -format bmp " + path)
  else:
    os.system("mogrify -format jpg " + path)

#in - string - command to set the wallpaper from ~/.wallpaper/wallpaper (or ~/Wallpaper-Reddit/wallpaper for Win)
#uses the user-specified command to set the downloaded-then-moved wallpaper
def set_wallpaper(wpsetcommand):
  if opsys == "Windows":
    ctypes.windll.user32.SystemParametersInfoW(0x14, 0, walldir + "\\wallpaper.bmp", 0x3)
  else:
    os.system(wpsetcommand)
  print("wallpaper set command was run")

#in - string - path of the image to resize
#resizes the image to the minimum width and height from the config/args
def resize_image(path):
  log("resizing the downloaded wallpaper")
  #uses the imagemagick 'convert' command to resize the image
  command = [spawn.find_executable("convert"), path, "-resize", str(minwidth) + "x" + str(minheight)]
  if opsys == "Windows":
    command = [spawn.find_executable("convert"), path, "-resize", str(minwidth) + "x" + str(minheight) + "^^",
               "-gravity", "center", "-extent", str(minwidth) + "x" + str(minheight), path]
  else:
    command = [spawn.find_executable("convert"), path, "-resize", str(minwidth) + "x" + str(minheight) + "^",
               "-gravity", "center", "-extent", str(minwidth) + "x" + str(minheight), path]
  subprocess.call(command)

#in - string, string - path of the image to set title on, title for image
def set_image_title(path, title):
  log("setting title")
  newtitle = remove_tags(title)
  if titlefont == "":
    subprocess.call([spawn.find_executable("convert"), path, "-pointsize", str(titlesize), "-gravity", titlegravity,
                     "-fill", "#00000080", "-annotate", "+7+7", newtitle,
                     "-fill", "white", "-annotate", "+5+5", newtitle, path])
  else:
    subprocess.call([spawn.find_executable("convert"), path, "-pointsize", str(titlesize), "-gravity", titlegravity, "-font", titlefont,
                     "-fill", "#00000080", "-annotate", "+7+7", newtitle,
                     "-fill", "white", "-annotate", "+5+5", newtitle, path])

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
    print('ERROR: ~/.wallpaper/url.txt does not exist.  wallpaper-reddit must run once before you can blacklist a wallpaper.')
    sys.exit(1)
  with open(walldir + '/url.txt', 'r') as urlfile:
    url = urlfile.read()
  with open(walldir + '/blacklist.txt', 'a') as blacklist:
    blacklist.write(url + '\n')

#in - string, string, - a url and a title
#saves the url of the image to ~/.wallpaper/url.txt and the title of the image to ~/.wallpaper/title.txt, just for reference
def save_info(url, title):
  #Reddit escapes the unicode in json, so when the json is downloaded, the info has to be manually re-encoded
  #and have the unicode characters reprocessed
  title = title.encode('utf-8').decode('unicode-escape')
  with open(walldir + '/url.txt', 'w') as urlinfo:
    urlinfo.write(url)
  with open(walldir + '/title.txt', 'w') as titleinfo:
    titleinfo.write(remove_tags(title))

#in - string - title of the picture
#out - string - title without any annoying tags
#removes the [tags] throughout the image
def remove_tags(str):
  return re.sub(' +', ' ', re.sub("[\[\(\<].*?[\]\)\>]", "", str)).strip()

#saves the wallpaper in the save directory from the config
#naming scheme is wallpaperN
def save_wallpaper():
  i = 0
  while os.path.isfile(savedir + '/wallpaper' + str(i)):
    i = i + 1
  if opsys == "Windows":
    shutil.copyfile(walldir + '\\wallpaper.bmp', savedir + '\\wallpaper' + str(i))
  else:
    shutil.copyfile(walldir + '/wallpaper.jpg', savedir + '/wallpaper' + str(i))
  with open(walldir + '/title.txt', 'r') as f:
    title = f.read()
  with open(savedir + '/titles.txt', 'a') as f:
    f.write('\n' + 'wallpaper' + str(i) + ': ' + title)
  print("current wallpaper saved to " + savedir + '/wallpaper' + str(i))

#creates and runs the ~/.wallpaper/external.sh script
def external_script():
  if opsys == 'Linux':
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
