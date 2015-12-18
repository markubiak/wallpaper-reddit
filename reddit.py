import json
import os
import random
import urllib.request
from PIL import Image

import sys

import re

import config
import connection
import main


# in - string[] - list of subreddits to get links from
# out - string[], string[] - a list of links from the subreddits and their respective titles
# takes in subreddits, converts them to a reddit json url, and then picks out urls and their titles
def get_links():
    print("searching for valid images...")
    if config.randomsub:
        parsedsubs = pick_random(config.subs)
    else:
        parsedsubs = config.subs[0]
        for sub in config.subs[1:]:
            parsedsubs = parsedsubs + '+' + sub
    url = "http://www.reddit.com/r/" + parsedsubs + ".json?limit=" + str(config.maxlinks)
    main.log("Grabbing json file " + url)
    uaurl = urllib.request.Request(url, headers={
        'User-Agent': 'wallpaper-reddit python script, github.com/markubiak/wallpaper-reddit'})
    response = urllib.request.urlopen(uaurl)
    content = response.read().decode('utf-8')
    try:
        data = json.loads(content)
    except (AttributeError, ValueError):
        print(
            'Was redirected from valid Reddit formatting. Likely a router redirect, such as a hotel or airport.'
            'Exiting...')
        sys.exit(0)
    response.close()
    links = []
    titles = []
    for i in data["data"]["children"]:
        links.append(i["data"]["url"])
        titles.append(i["data"]["title"])
    return links, titles


# in - string[] - list of links to check
# out - string, int - first link to match all criteria and its index (for matching it with a title)
# takes in a list of links and attempts to find the first one that is a direct image link,
# is within the proper dimensions, and is not blacklisted
def choose_valid(links):
    if len(links) == 0:
        print("No links were returned from any of those subreddits. Are they valid?")
        sys.exit(1)
    for i, origlink in enumerate(links):
        main.log("checking link # {0}: {1}".format(i, origlink))
        link = origlink
        if not (link[-4:] == '.png' or link[-4:] == '.jpg' or link[-5:] == '.jpeg'):
            if re.search('(imgur\.com)(?!/a/)', link):
                link = link.replace("/gallery", "")
                link += ".jpg"
            else:
                continue
        if not (connection.connected(link) and check_dimensions(link) and check_blacklist(link)):
            continue

        def check_same_url(link):
            with open(config.walldir + '/url.txt', 'r') as f:
                currlink = f.read()
                if currlink == link:
                    print("current wallpaper is the most recent, will not re-download the same wallpaper.")
                    sys.exit(0)
                else:
                    return True

        if config.force_dl or not (os.path.isfile(config.walldir + '/url.txt')) or check_same_url(link):
            return link, i
    print("No valid links were found from any of those subreddits.  Try increasing the maxlink parameter.")
    sys.exit(0)


# in - string - link to check dimensions of
# out - boolean - if the link fits the proper dimensions
# takes a link and checks to see if the link will match the minimum dimensions
def check_dimensions(url):
    resp = urllib.request.urlopen(urllib.request.Request(url, headers={
        'User-Agent': 'wallpaper-reddit python script by /u/MarcusTheGreat7',
        'Range': 'bytes=0-16384'
    }))
    try:
        with Image.open(resp) as img:
            dimensions = img.size
            if dimensions[0] >= config.minwidth and dimensions[1] >= config.minheight:
                main.log("Size checks out")
                return True
    except IOError:
        print("IOError")
    return False


# in: a list of subreddits
# out: the name of a random subreddit
# will pick a random sub from a list of subreddits
def pick_random(subreddits):
    rand = random.randint(0, len(subreddits) - 1)
    return subreddits[rand]


# in - string - a url to match against the blacklist
# out - boolean - whether the url is blacklisted
# checks to see if the url is on the blacklist or not (True means the link is good)
def check_blacklist(url):
    with open(config.walldir + '/blacklist.txt', 'r') as blacklist:
        bl_links = blacklist.read().split('\n')
    for link in bl_links:
        if link == url:
            return False
    return True


# blacklists the current wallpaper, as listed in the ~/.wallpaper/url.txt file
def blacklist_current():
    if not os.path.isfile(config.walldir + '/url.txt'):
        print(
            'ERROR: ~/.wallpaper/url.txt does not exist.'
            'wallpaper-reddit must run once before you can blacklist a wallpaper.')
        sys.exit(1)
    with open(config.walldir + '/url.txt', 'r') as urlfile:
        url = urlfile.read()
    with open(config.walldir + '/blacklist.txt', 'a') as blacklist:
        blacklist.write(url + '\n')
