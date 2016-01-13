import ctypes
import json
import time
import urllib.request
from socket import timeout
from urllib.error import HTTPError, URLError

from wpreddit import config


# in - string - web page url
# out - boolean - connection status
# checks whether the program can connect to the specified url
def connected(url):
    try:
        uaurl = urllib.request.Request(url,
                                       headers={'User-Agent': 'wallpaper-reddit python script by /u/MarcusTheGreat7'})
        url = urllib.request.urlopen(uaurl, timeout=3)
        url.close()
        return True
    except (HTTPError, URLError, timeout):
        return False


# out - boolean - connection status
# checks whether the program can connect to reddit and is not being redirected
def check_not_redirected():
    try:
        # Not reloading /etc/resolv.conf, since it will have to be reloaded for the function right before this is called
        uaurl = urllib.request.Request('http://www.reddit.com/.json',
                                       headers={'User-Agent': 'wallpaper-reddit python script by /u/MarcusTheGreat7'})
        url = urllib.request.urlopen(uaurl, timeout=3)
        json.loads(url.read().decode('utf8'))
        url.close()
        return True
    except (HTTPError, URLError, timeout, AttributeError, ValueError):
        return False


# in - string, int, int - url to check for connection, how many attempts and at what interval to retry until connected
# out - boolean - whether the connection was successfully establised
# waits for a connection to the specified url, or returns False if no connection could be made in the time frame
def wait_for_connection(tries, interval):
    config.log('Waiting for a connection...')
    for i in range(tries):
        if config.opsys == "Linux":
            # Reloads /etc/resolv.conf
            # credit: http://stackoverflow.com/questions/21356781/urrlib2-urlopen-name-or-service-not-known-persists-when-starting-script-witho
            libc = ctypes.cdll.LoadLibrary('libc.so.6')
            res_init = libc.__res_init
            res_init()
        config.log('Attempt # ' + str(i + 1) + ' to connect...')
        if connected("http://www.reddit.com"):
            config.log('Connected to the internet, checking if you\'re being redirectied...')
            if check_not_redirected():
                config.log('No redirection.  Starting the main script...')
                return True
            config.log('Redirected.  Trying again...')
        time.sleep(interval)
    return False