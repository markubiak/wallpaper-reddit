import json
import os
import random
import re
import requests
import sys
from PIL import Image

from wpreddit import connection
from wpreddit.config import cfg
from wpreddit.common import log, exit_msg


# in - string[] - list of subreddits to get links from
# out - [string, string, string][] - a list of links from the subreddits and their respective titles and permalinks
def get_links():
    """Takes in subreddits, converts them to a reddit json url, and then picks out urls and their titles"""
    print("searching for valid images...")
    if cfg['random_sub']:
        parsed_subs = pick_random(cfg['subs'])
    else:
        parsed_subs = '+'.join(cfg['subs'])
    url = "http://www.reddit.com/r/" + parsed_subs + "/" + cfg['sorting_alg'] + \
          ".json?limit=" + str(cfg['max_links'])
    log("Grabbing json file " + url)
    r = requests.get(url, headers={'User-Agent': 'wallpaper-reddit python script: ' +
                                                 'github.com/markubiak/wallpaper-reddit'})
    data = json.loads("{}")  # warning suppression
    try:
        data = json.loads(r.text)
    except (AttributeError, ValueError):
        exit_msg("Was redirected from valid Reddit formatting. Likely a router redirect, "
                 "such as a hotel or airport. Exiting...")
    links = []
    for i in data["data"]["children"]:
        links.append([i["data"]["url"],
                      i["data"]["title"],
                      "http://reddit.com" + i["data"]["permalink"]])
    return links


# in - [string, string, string][] - list of links to check
# out - [string, string, string] - first link to match all criteria with title and permalink
def choose_valid(links):
    """takes in a list of links and attempts to find the first one that is a direct image link,
    is within the proper dimensions, and is not blacklisted"""
    if len(links) == 0:
        exit_msg("No links were returned from any of those subreddits. Are they valid?")
    for i, origlink in enumerate(links):
        link = origlink[0]
        log("checking link # {0}: {1}".format(i, link))
        if not (link[-4:] == '.png' or link[-4:] == '.jpg' or link[-5:] == '.jpeg'):
            if re.search('(imgur\.com)(?!/a/)', link):
                link = link.replace("/gallery", "")
                link += ".jpg"
            else:
                continue
        if not connection.connected(link) and check_dimensions(link) and check_blacklist(link):
            continue

        def check_same_url(link):
            with open(cfg['dirs']['data'] + '/url.txt', 'r') as f:
                curr_link = f.read()
                if curr_link == link:
                    exit_msg("current wallpaper is the most recent, will not re-download the same wallpaper.", code=0)
                else:
                    return True

        if cfg['force_download'] or not (os.path.isfile(cfg['dirs']['data'] + '/url.txt')) or check_same_url(link):
            return [link, origlink[1], origlink[2]]
    exit_msg("No valid links were found from any of those subreddits.  Try increasing the maxlink parameter.")


# in - string - link to check dimensions of
# out - boolean - if the link fits the proper dimensions
def check_dimensions(url):
    """Takes a link and checks to see if the link will match the minimum dimensions"""
    r = requests.get(url, headers={'User-Agent': 'wallpaper-reddit python script by /u/MarcusTheGreat7',
                                                 'Range': 'bytes=0-16384'
                                   },
                     stream=True)
    try:
        with Image.open(r.raw) as img:
            dimensions = img.size
            if (dimensions[0] / dimensions[1]) >= cfg['min_dimensions']['ratio'] and \
                    dimensions[0] >= cfg['min_dimensions']['width'] and \
                    dimensions[1] >= cfg['min_dimensions']['height']:
                        log("Size checks out")
                        return True
    except IOError:
        log("Image dimensions could not be read")
    return False


# in: a list of subreddits
# out: the name of a random subreddit
def pick_random(subreddits):
    """Will pick a random sub from a list of subreddits"""
    rand = random.randint(0, len(subreddits) - 1)
    return subreddits[rand]


# in - string - a url to match against the blacklist
# out - boolean - whether the url is blacklisted
def check_blacklist(url):
    """Checks to see if the url is on the blacklist or not (True means the link is good)"""
    with open(cfg['dirs']['data'] + '/blacklist.txt', 'r') as blacklist:
        bl_links = blacklist.read().split('\n')
    for link in bl_links:
        if link == url:
            return False
    return True


def blacklist_current():
    """Blacklists the current wallpaper, as listed in the ~/.wallpaper/url.txt file"""
    if not os.path.isfile(cfg['dirs']['data'] + '/url.txt'):
        exit_msg("ERROR: " + cfg['dirs']['data'] + "/url.txt does not exist. "
                 "wallpaper-reddit must run once before you can blacklist a wallpaper.")
    with open(cfg['dirs']['data'] + '/url.txt', 'r') as urlfile:
        url = urlfile.read()
    with open(cfg['dirs']['data'] + '/blacklist.txt', 'a') as blacklist:
        blacklist.write(url + '\n')
